# Aeron Chronicle 状态存储指南（aeron-chronicle）

> 适用模块：`aeron-chronicle`
> 依赖：`com.mcst:chronicle-map`（easyfk-component 的 Chronicle Map 封装，`aeron-chronicle` 以 `api` 传递）
> 配套手册：`easyfk-component/component-chronicle/chronicle-map` 的使用手册、`docs/跨语言互通指南.md`、`docs/序列化Codec接入指南.md`

---

## 1. 定位：事件流 → 本地 KV 状态视图

把 Aeron 订阅到的**事件流（changelog）**物化成本地 **Chronicle Map 状态表（materialized view）**，
供同机其他 Java 业务低延迟查询：

```
Go producer ──IPC──> AeronConsumer ──> StateMaterializer ──> ChronicleMap (quotes.dat)
                                                                  ▲
                                              同机其他 Java 进程用一致参数打开同一文件读取
```

典型场景：Go 行情/风控引擎持续推送状态变更事件，Java 侧把"每个 key 的最新状态"
落到持久化 Chronicle Map，查询方直接读本地 off-heap 内存（µs 级），不经过网络。

### 1.1 明确的能力边界

| 能力 | 是否提供 | 说明 |
|---|---|---|
| key 最新状态（last value cache） | ✅ | upsert / delete / LWW 防乱序 |
| 持久化 + 重启恢复 | ✅ | Chronicle Map mmap 文件，进程重启状态仍在 |
| 同机跨进程读 | ✅ | 其他 Java 进程一致参数打开同一 `.dat` 文件 |
| 历史事件回放 | ❌ | 只存最新值；需要全量历史请用 `aeron-store` WAL |
| 消费者宕机期间的事件 | ❌ **会丢** | Aeron 是流式传输非持久队列。接受边界：消费者重启后只能拿到重启后的新事件；Go 侧如需补偿，可在 Java 端上线后重发全量快照（snapshot + delta 模式） |

---

## 2. 快速开始（编程式，无 Spring）

```java
// 1. 打开/创建持久化 Chronicle Map（参数即跨进程契约，见 §5）
ChronicleMap<String, String> map = ChronicleMap.of(String.class, String.class)
        .entries(100_000)
        .averageKeySize(16)
        .averageValueSize(64)
        .putReturnsNull(true)       // 物化路径不读旧值：省一次旧值反序列化/堆分配（GC，强烈建议）
        .removeReturnsNull(true)
        .createPersistedTo(new File("/data/state/quotes.dat"));

// 2. 一行式绑定：topic 事件流 → 状态表
AeronStateBinding.<QuoteEvent, String, String>builder()
        .consumer(consumer)                     // 现有 AeronConsumer，需已注册事件类型的 codec
        .topic("md.quote")
        .eventType(QuoteEvent.class)
        .map(map)
        .key(QuoteEvent::symbol)                // 事件 → 状态表 key
        .value(e -> e.price() + ":" + e.version()) // 事件 → 存储值
        .tombstoneWhen(QuoteEvent::isDelete)    // 可选：delete 事件
        .versionedBy(v -> parseVersion(v))      // 可选：LWW 防乱序（版本号从存储值提取）
        .bind();                                // 内部 consumer.subscribe(...)

consumer.start();
```

要点：

- `bind()` 必须在 `consumer.start()` 之前调用（与所有订阅一致）；
- `StateMaterializer` 只要求目标表是 `ConcurrentMap`——单元测试可用 `ConcurrentHashMap`
  验证物化逻辑，不需要 Chronicle 的 JVM 参数；
- map 的生命周期归创建方管（手动 close 或交给 `ChronicleMapManager`），绑定不负责；
- **关闭顺序必须是先 close consumer、再 close map**：map 先关会解除 off-heap 内存映射，
  还在执行的 handler 触碰已 unmap 内存可能 SIGSEGV 崩掉 JVM。try-with-resources 把 map
  声明在 consumer 之前即可（关闭顺序与声明相反）；Spring 装配路径顺序天然正确；
- **投递模式建议 INLINE（consumer 默认是 RING_BUFFER_POOL，需显式配置 `delivery-mode: INLINE`）**：RING_BUFFER_POOL 下同 key 事件可能被多个 worker
  乱序处理，必须搭配 `versionedBy` 才安全；且 pool 队列满会丢消息（状态表缺更新），
  详见 §7。

### 2.1 事件语义

| 事件 | 行为 |
|---|---|
| 普通事件 | `map.put(key(e), value(e))` |
| tombstone（`tombstoneWhen` 命中） | `map.remove(key(e))`，不调用 value 提取 |
| 版本落后（开了 `versionedBy`） | 跳过，计 `onStaleSkipped`——at-least-once 重放 + 乱序不会把新状态回退成旧状态；**取等号允许**同版本重放幂等覆盖 |
| key/value 提取出 `null` | 按畸形事件丢弃，计 `onMalformed`（畸形事件重投也不会变好） |
| 提取函数抛异常 | 向上传播：consumer 计 `onError` 且不占去重槽位，重放可重试 |

`versionedBy` 的版本号从**存储值 V** 上提取（业务版本号 / 序列号 / 事件时间戳均可），
因此 V 必须携带版本字段。不开 `versionedBy` 则按到达顺序覆盖（适合 Go 端保证单调有序的场景）。

---

## 3. Spring Boot 接入（自动装配）

业务方只注册一个 `AeronChronicleBindingSpec` bean，启动期自动完成
map 创建 + consumer 订阅（先于 consumer 启动，不漏事件）：

```java
@Bean
AeronChronicleBindingSpec<QuoteEvent, String, Quote> quoteState() {
    return AeronChronicleBindingSpec.<QuoteEvent, String, Quote>builder()
            .topic("md.quote")
            .eventType(QuoteEvent.class)
            .mapName("quotes")                          // ChronicleMapManager 中的 map 名
            .keyType(String.class).valueType(Quote.class)
            .key(QuoteEvent::symbol)
            .value(e -> new Quote(e.symbol(), e.price(), e.version()))
            .versionedBy(Quote::version)
            .build();
}
```

YAML（map 本体配置走 chronicle-map 自己的前缀 `easyfk.config.chronicle.map`）：

```yaml
easyfk:
  config:
    aeron:
      driver:
        embedded: true
        consumer:
          channels: ["aeron:ipc"]
          base-stream-id: 1001
          delivery-mode: INLINE  # 状态物化建议 INLINE（默认 RING_BUFFER_POOL）
      chronicle:
        enabled: true            # 默认 true
    chronicle:
      map:
        default-path: /data/state
        put-returns-null: true   # 物化路径不读旧值，省一次旧值反序列化
        remove-returns-null: true
        maps:                    # 推荐：YAML 预配置 map，参数显式可审计
          - map-name: quotes
            key-type: java.lang.String
            value-type: com.example.Quote
            max-entries: 100000
            average-key-size: 16
            average-value-size: 128
```

装配规则：

- **map 来源（按序）**：① `ChronicleMapManager` 已注册同名 map（YAML 预配置，推荐）——
  复用时会校验已注册 K/V 类型与 spec 一致，不一致直接启动失败；
  ② 否则按 spec 的 `mapParams(...)` / 全局默认参数创建。自定义 POJO 值默认走 Fory
  Marshaller，原生类型（String/byte[]/包装类）用 `.plainMarshaller()`；
  `.filePath(...)` 必须与 `.mapParams(...)` 同时设置；
- **consumer 选择**：默认取容器唯一 `Consumer` bean；多 driver 用 `.driver("ipc-a")`
  （按 starter 命名约定 `aeronConsumer_ipcA` 解析）或 `.consumerBeanName(...)` 直接点名；
- **失败语义**：任一绑定失败直接中断启动（fail-fast）——状态表少订一个 topic 属于静默数据缺失；
- **生命周期**：绑定在 phase `Integer.MIN_VALUE + 500` 执行，早于 starter `AeronLifecycle`
  （`MIN_VALUE + 1000`，负责 `consumer.start()`）；map 关闭由 `ChronicleMapManager`
  （`DisposableBean`）统一处理。

---

## 4. Go 端对接 checklist（SBE 事件）

wire 字节布局即跨语言契约，Java 侧零特殊处理。完整协议见 `docs/跨语言互通指南.md`、
`docs/aeron协议说明.md`，黄金样本在 `docs/wire-samples/`。

1. **事件 schema**：用 sbe-tool 维护一份 schema XML（建议放公司 `sbe-schemas` repo），
   生成 Go encoder + Java decoder。事件至少包含：
   - 状态表 key 字段（如 `symbol`）；
   - 业务 payload 字段；
   - `op` 字段（uint8：0=upsert，1=delete）→ Java 侧 `tombstoneWhen(e -> e.op() == 1)`；
   - 单调 `version` 字段（序列号/时间戳）→ Java 侧 `versionedBy`，防 at-least-once 重放与乱序；
2. **帧头**：Go 端按本 SDK 帧协议封包（FrameHeader + codecId=SBE + 压缩 id 等，
   见协议契约文档），与现有 Go producer 路径完全一致；
3. **传输**：同机 `aeron:ipc`，Go/Java 连同一个 MediaDriver（standalone driver 或
   Java 侧 embedded driver 暴露 aeronDir）；
4. **快照补偿（推荐）**：Java 消费端重启会丢宕机窗口内的事件。Go 端实现
   "Java 上线信号 → 重发全量快照"（或定期全量快照 + 增量），即可把状态表收敛到最新；
5. **验证**：跑 `gradlew :aeron-examples:runChronicleStateDemo` 看 Java 端到端行为，
   Go 端对拍 `docs/wire-samples/` 黄金字节。

---

## 5. 跨进程读端注意事项（重要）

Chronicle Map 跨进程共享的前提是**所有打开方建表参数完全一致**：

- `entries / averageKeySize / averageValueSize / key,value 类型 / marshaller` 任一不一致，
  读出的就是错位垃圾数据（不会报错！）——参数就是文件格式的一部分；
- 推荐把建表参数收敛到一处（YAML `easyfk.config.chronicle.map.maps` 或共享常量类），
  读写两端引用同一份；
- 值用 Fory Marshaller 时，读端也必须用相同 Fory 配置注册相同值类型（见 ChronicleMap
  使用手册 Fory 一节）；跨进程读端若非公司框架应用，值类型建议用 String/byte[] 原生类型；
- 写端唯一：本组件是状态表的**唯一写入方**，其他进程只读。Chronicle Map 本身支持多写，
  但多写方会绕过 LWW 版本检查，破坏物化语义；
- 运行任何打开 Chronicle Map 的进程（JDK 21）都需要 JVM 参数（见 §6）。

写端进程崩溃（kill -9）时 mmap 已写入页由 OS 落盘，但 `createPersistedTo` **不会**自动修复
崩溃时正在写入的半截 entry——需要时用 `ChronicleMapBuilder.recoverPersistedTo(...)` 显式恢复，
且恢复期间必须确保**没有任何其他进程打开该文件**（Windows 上 Chronicle 文件锁不可用，
框架无法替你校验这一点）。更省事的兜底是 Go 端快照补偿（§4.4）：删掉文件重建 + 等一次全量快照。

---

## 6. JVM 参数（JDK 21）

在 SDK 既有 `--add-opens` 参数基础上，Chronicle Map 额外需要（与 component-chronicle 的要求一致）：

```
--add-exports java.base/jdk.internal.ref=ALL-UNNAMED
--add-exports java.base/sun.nio.ch=ALL-UNNAMED
--add-exports jdk.unsupported/sun.misc=ALL-UNNAMED
--add-exports jdk.compiler/com.sun.tools.javac.file=ALL-UNNAMED
--add-opens   jdk.compiler/com.sun.tools.javac=ALL-UNNAMED
--add-opens   java.base/java.util=ALL-UNNAMED
```

`aeron-examples` 的 `runChronicleStateDemo` 任务已内置；业务应用请加到启动脚本（Spring Boot 应用同样需要）。

---

## 7. 容量与性能定位

- 设计目标：**10 万级条目、小对象值**的状态表（已确认的业务规模）。Chronicle Map 在该规模
  下读写均为 µs 级，单文件几十 MB；
- `entries` 给真实上限的 1.5~2x 余量（Chronicle Map 超过 entries 会抛异常，不会自动扩容；
  满表后每条 upsert 都会失败并计入 consumer onError——状态表停止更新，必须按容量告警）；
- **GC / 热路径分配**：
  - 物化器本身热路径零分配（LWW 用显式 CAS 循环，无 lambda / 装箱 / 临时对象）；
  - `Map.put/remove` 按接口契约返回旧值，Chronicle Map 为此每次**反序列化一次旧值**——
    自建 map 务必 `putReturnsNull(true).removeReturnsNull(true)` 关掉（本组件从不读返回值）；
    经 `ChronicleMapManager` 创建的 map 用全局 `put-returns-null / remove-returns-null`
    开启，YAML 声明的 map 也可单独覆盖；
  - 开 `versionedBy` 后每条事件多一次 `get`（旧值反序列化）做版本比较，是 LWW 的固有成本；
- **投递模式与顺序**：INLINE（需显式配置，consumer 默认 RING_BUFFER_POOL）下单 partition 事件严格按接收序物化。
  RING_BUFFER_POOL 多 worker 抢占消费，同 key 事件完成顺序不确定——不开 `versionedBy`
  时最终状态由线程调度决定（可能停在旧值），**pool 模式必须搭配 `versionedBy`**；
  且 pool 队列满会丢消息（`onDispatchDropped`），状态表缺该次更新直到同 key 下一条事件；
- 监控：`StateStoreMetrics`（onUpsert / onDelete / onStaleSkipped / onMalformed）
  自行桥接到 Micrometer 即可；容量水位用 `map.size()` 定期采样对比 `entries`。

---

## 8. 测试与示例索引

`aeron-chronicle` 目前没有单元测试，端到端行为通过 demo 验证：

| 内容 | 位置 |
|---|---|
| 可运行 demo（SBE 事件流 → 持久化 Chronicle Map） | `gradlew :aeron-examples:runChronicleStateDemo` |
