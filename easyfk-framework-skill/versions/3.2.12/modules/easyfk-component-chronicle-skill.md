# easyfk-component-chronicle Skill 参考文档

> 模块：`easyfk-component/component-chronicle`（chronicle-map / chronicle-queue）
> 坐标：`com.mcst:chronicle-map`、`com.mcst:chronicle-queue`（catalog 别名 `componentChronicleMap` / `componentChronicleQueue`，也在 `storage` bundle 中）
> 依据：两个子模块源码（含 chronicle-queue 单元测试目录）+ `chronicle-map使用手册.md`、`chronicle-map技术特点.md`、`chronicle-queue-使用手册.md`、`chronicle-queue-项目特点介绍.md`
> 文档与源码不一致时 **以源码为准**，差异见文末「复查记录」。

---

## 1. 模块定位

| 子模块 | 底层 | 包名 | 作用 |
|---|---|---|---|
| chronicle-map | `net.openhft:chronicle-map:3.27ea1` + serializer-fory | `com.mcst.easyfk.chronicle.map` | 本机堆外、可持久化的 K-V 存储；`ChronicleMapManager` + `ChronicleMapTemplate`；Fory 值序列化；多进程伴生锁 |
| chronicle-queue | `net.openhft:chronicle-queue:5.27ea10`（排除 affinity / third-party-bom，另引 affinity 3.23.3）+ serializer-fory | `com.mcst.easyfk.chronicle.queue` | 本机持久化顺序日志队列；Publisher / Consumer / Template；`@ChronicleQueueListener` 注解消费；位点感知的文件清理 |

- 两者都只解决**单机（同一台机器上的多个进程）**内的低延迟存储与通信，不是分布式组件。
- 两个子模块对 `easyfk-core` 只是 `compileOnly`。
- 依赖版本由 easyfk-dependencies 统一管理，当前均为 OpenHFT 的 EA（early access）版本；离线仓库中没有对应的非 EA 版本，暂未升级。升级时 chronicle-map / chronicle-queue / chronicle-wire / chronicle-bytes 需成套升级。
- Chronicle 库在 Java 21 上需要额外 JVM 参数，按 Chronicle 官方要求配置，常用集合：
  ```
  --add-exports=java.base/jdk.internal.ref=ALL-UNNAMED
  --add-exports=java.base/sun.nio.ch=ALL-UNNAMED
  --add-exports=jdk.unsupported/sun.misc=ALL-UNNAMED
  --add-exports=jdk.compiler/com.sun.tools.javac.file=ALL-UNNAMED
  --add-opens=jdk.compiler/com.sun.tools.javac=ALL-UNNAMED
  --add-opens=java.base/java.lang=ALL-UNNAMED
  --add-opens=java.base/java.lang.reflect=ALL-UNNAMED
  --add-opens=java.base/java.io=ALL-UNNAMED
  --add-opens=java.base/java.util=ALL-UNNAMED
  --add-opens=java.base/java.nio=ALL-UNNAMED
  ```
  应用启动脚本与运行 Chronicle 的单元测试（`test { jvmArgs ... }`）都要配置。

---

## 2. chronicle-map

### 2.1 自动配置

`ChronicleMapAutoConfiguration`（无开关，引入即生效）：
- `ChronicleMapManager`（`@ConditionalOnMissingBean`，启动时创建，实现 `DisposableBean`，容器关闭时关闭所有 Map 并释放锁）。
- `ChronicleMapTemplate`（`@ConditionalOnMissingBean`）。
- 启动时按 `maps` 列表创建声明式 Map；任一失败则关闭 Manager 并抛 `IllegalStateException`，应用启动失败。

### 2.2 配置（前缀 `easyfk.config.chronicle.map`）

```yaml
easyfk:
  config:
    chronicle:
      map:
        default-path: ./chronicle-maps        # 持久化目录，文件为 <path>/<mapName><ext>
        default-max-entries: 100000
        default-average-key-size: 64.0
        default-average-value-size: 1024.0
        default-file-extension: .dat
        persistence-enabled: true             # 总开关；false 时所有 Map（含编程式显式 filePath）都是纯内存
        recover-on-startup: true
        apply-average-sizes: true
        fixed-size-optimization-enabled: true # Long/Integer/Double 等定长类型不设置平均大小
        fory-marshaller-enabled: true         # 未显式指定时按值类型自动识别是否用 Fory（默认 true）
        fory-schema-mode: COMPATIBLE          # 不配置则沿用 serializer-fory 全局默认（SCHEMA_CONSISTENT）
        put-returns-null: false               # true 时 put 返回 null，省一次旧值反序列化
        remove-returns-null: false
        maps:
          - map-name: userCache
            key-type: java.lang.String        # 默认 String
            value-type: com.biz.UserInfo      # 默认 Object
            max-entries: 1000000
            average-value-size: 800
            use-fory-marshaller: true         # 不配置则按全局开关自动识别
            fory-schema-mode: COMPATIBLE
            persistence-enabled: true         # 需全局也为 true
            file-path: /data/maps/user.dat    # 可选
```

### 2.3 ChronicleMapManager

| 方法 | 说明 |
|---|---|
| `getOrCreateMap(name, K.class, V.class)` | Fory：按全局开关 + 值类型自动识别 |
| `getOrCreateMap(name, K, V, maxEntries, avgKey, avgValue, filePath)` | Fory：同上，按全局开关 + 值类型自动识别 |
| `getOrCreateMap(name, K, V, Boolean useFory, maxEntries, avgKey, avgValue, filePath)` | Fory：`true` 强制开启 / `false` 强制关闭 / `null` 自动识别 |
| `getOrCreateForyMap(name, K, V)` / `(…, maxEntries, avgKey, avgValue, filePath)` | Fory：强制开启 |
| `registerMap(name, map[, K, V])` / `registerConfiguredMap(info)` | 注册已有实例 / 按配置创建；重名抛 `IllegalArgumentException` |
| `getMap(name)` | 不存在返回 null |
| `containsMap / getMapNames / getMapStats / removeMap / closeAll / close` | 管理 |

- 同名但 K/V 类型不同 → `IllegalArgumentException`（`registerMap(name, map)` 不带类型时不登记类型、不校验）。
- Fory 自动识别（`fory-marshaller-enabled=true`，默认）：基本类型及包装类、`String`/`CharSequence`、`byte[]`、`BytesMarshallable`、`java.*` 包下的 `Serializable` 走 Chronicle 原生序列化；`Object`、接口、抽象类也不自动用 Fory（Fory 按运行时类型写 typeId，重启/跨进程读取未预注册的类会失败）；其余具体业务类走 `ForyBytesMarshaller`。
- `fory-marshaller-enabled=false` 或值类型为 `Object`/接口/抽象类时，未显式启用 Fory 的类型由 Chronicle 自身处理，通常要求实现 `Serializable`（或 `BytesMarshallable`）。
- 持久化：`persistence-enabled` 是总开关。`false` 时所有 Map 均为纯内存（编程式传入的 `filePath` 被忽略并打 WARN）；`true` 时显式 `filePath` 优先，否则写 `<default-path>/<name><ext>`。
- 多进程协议：每个文件旁生成 `<file>.lck`，字节 0 为门锁（独占，等待上限 60s），字节 1 为使用锁（共享，打开期间持有）。文件存在、`recover-on-startup=true` 且没有其他活跃使用者时执行 `recoverPersistedTo(file, true)`；有其他使用者时直接 `createPersistedTo`。同一 JVM 内两个 Manager 打开同一文件会抛 `OverlappingFileLockException` 包装的 IOException。
- `put-returns-null / remove-returns-null` 只有声明式 Map 支持单 Map 覆盖，编程式创建只用全局值。

### 2.4 ChronicleMapTemplate

```java
@Resource
private ChronicleMapTemplate chronicleMapTemplate;

chronicleMapTemplate.initMap("userCache", String.class, UserInfo.class);              // 默认自动识别：POJO 用 Fory
chronicleMapTemplate.initForyMap("userCache", String.class, UserInfo.class);          // 强制 Fory；或 YAML 声明
chronicleMapTemplate.initForyMap("userCache", String.class, UserInfo.class, 1_000_000, 800); // avgKeySize 固定 64
chronicleMapTemplate.put("userCache", "UID001", user);
UserInfo u = chronicleMapTemplate.get("userCache", "UID001");
chronicleMapTemplate.updateWithLock("userCache", "UID001", (UserInfo v) -> v.setScore(v.getScore() + 1));
```
- **写入类**（`put` / `putIfAbsent` / `putAll` / `computeIfAbsent` / `putMarshallable` / `putWriteMarshallable`）：Map 不存在抛 `IllegalStateException`。
- **读取/作用于已有条目类**（`get` / `getAll` / `getOrDefault` / `containsKey` / `remove` / `replace` / `computeIfPresent` / `getUsing` / `size` / `isEmpty` / `clear` / `keySet`）：Map 不存在时返回 null / 空 / false / 0；`keySet` 返回 null。
- 批量：`getAll(name, keys)`（LinkedHashMap，跳过 null key 与未命中）、`getAll(name, keys, (k, v) -> …)`（流式）、`getAllParallel(name, keys, action)`（公共 ForkJoinPool，action 必须线程安全）。
- 锁：`getWithLock(name, key, action)`（读锁）、`updateWithLock(name, key, action)`（写锁内读-改-`doReplaceValue` 写回；key 不存在时不执行）。
- `getUsing` 只对 `BytesMarshallable` / value-interface 有零分配效果；Fory 值每次都会新建对象。
- 带 `Class<K>, Class<V>` 参数的旧方法全部 `@Deprecated`，直接委托给对应新方法（类型参数被忽略）；写入类旧方法与新方法一致，Map 不存在抛 `IllegalStateException`，不会自动创建。

---

## 3. chronicle-queue

### 3.1 自动配置

| 配置类 | 条件 | 内容 |
|---|---|---|
| `ChronicleQueueAutoConfiguration` | 无开关 | `ChronicleQueueManager`（启动时创建，并注册 JVM shutdown hook）、`ChronicleQueueTemplate`、`ChronicleQueueListenerErrorHandler`（默认 `LoggingChronicleQueueListenerErrorHandler`）、`ChronicleQueueListenerRegistry`、`ChronicleQueueListenerBeanPostProcessor`（static `@Bean`，只持有 `ObjectProvider<Registry>`，扫描结果在所有单例实例化后才注册，不会提前创建 Registry/Template/Manager），均 `@ConditionalOnMissingBean` |
| `ChronicleQueueCleanupAutoConfiguration` | 存在 Manager（不再依赖全局开关） | `ChronicleQueueCleanupTask` + 组件私有的单线程 `SmartLifecycle` 调度器（fixed-delay，不使用 `@EnableScheduling`，不影响业务 `@Scheduled`）；每个队列是否清理由单队列/全局 `cleanup.enabled` 决定 |

### 3.2 配置（前缀 **`easyfk.config.storage.queue`**）

```yaml
easyfk:
  config:
    storage:
      queue:
        default-path: ./chronicle-queues          # 队列目录为 <default-path>/<queueName>
        default-roll-cycle: FAST_DAILY            # RollCycles 枚举名（大小写不敏感），非法值回退 FAST_DAILY
        default-block-size: 0                     # 0 = Chronicle 默认
        create-directories-on-startup: true       # 启动时创建 queues 中声明的队列
        fory-schema-mode: COMPATIBLE              # Fory 消息默认模式（默认 COMPATIBLE），已有数据不可中途切换
        queues:
          - queue-name: trade
            path: ./chronicle-queues/trade
            roll-cycle: FAST_HOURLY
            block-size: 67108864
            fory-schema-mode: COMPATIBLE          # 可选，覆写全局
            cleanup:                              # 单队列覆写，字段为空则沿用全局
              enabled: true                       # 优先于全局 enabled，全局关闭时也会清理该队列
              retention: 6h
              reserve-cycles-before-head: 2
              require-listener-position: true
              all-consumers-tracked: true
              protected-consumer-ids: [trade-archive]
        listener:
          enabled: true                           # false 时注册但不自动启动
          default-idle-mode: PARK                 # BUSY_SPIN / YIELD / PARK / SLEEP
          default-idle-time-ms: 10
          default-max-retries: 0
          default-retry-delay-ms: 100
          default-retry-backoff-mode: FIXED       # FIXED / LINEAR / EXPONENTIAL
          default-max-retry-delay-ms: 1000
          default-failure-policy: CONTINUE        # CONTINUE / STOP
          default-batch-size: 1
          default-daemon: true
        cleanup:
          enabled: false                          # 全局默认开关（默认关闭），单队列 enabled 可覆写
          check-interval: 2h
          initial-delay: 5m
          retention: 2h                           # 文件 lastModified 早于 now - retention 才可删
          reserve-cycles-before-head: 1
          require-listener-position: true
          all-consumers-tracked: false            # 不确认为 true 时永远不删文件
```

### 3.3 写入

```java
@Resource
private ChronicleQueueTemplate queueTemplate;

long idx = queueTemplate.writeText("trade", "hello");
queueTemplate.writeBytes("trade_bin", bytes);                 // 文档字段 "b"
queueTemplate.writeFory("trade_obj", orderDto);               // 文档字段 "d"，队列配置的模式（默认 COMPATIBLE）
queueTemplate.writeFory("trade_obj", orderDto, SchemaMode.CONSISTENT); // 显式模式，读取端须一致
queueTemplate.writeObject("tick", marketTicker);             // BytesMarshallable
queueTemplate.writeDocument("trade", wire -> wire.write("price").float64(1.2));
queueTemplate.writeKeyValue("trade", "k", "v");

try (ChronicleQueuePublisher p = queueTemplate.openPublisher("trade")) {   // 长期持有
    p.publishText("a");
    p.publishFory(dto);
}
```
- 写入都会按需创建队列（使用 `queues` 中的同名定义）；返回 `lastIndexAppended()`。
- Template 内部按队列缓存最多 128 个共享 Publisher，所有方法 `synchronized`，可多线程调用。

### 3.4 读取

| 方式 | 用法 | 说明 |
|---|---|---|
| Template 共享读取 | `readText/readBytes/readFory/readObject/readDocument(+Batch)(queue, consumerId[, strategy], …)` | consumerId 必填；按 (queue, consumerId) 缓存最多 256 个共享 Consumer；本进程未打开但磁盘上已有队列目录（单队列 `path` 或 `<default-path>/<queue>`）时会打开它；目录不存在才返回 null，不会创建队列 |
| 长期 Consumer | `try (var c = queueTemplate.openConsumer("trade", "c1")) { c.consumeText(); }` | 会按需创建队列；同一 (queue, consumerId) 在本进程只能被一个 Consumer/共享读取/Listener 持有，否则 `IllegalStateException("NamedTailer is already in use")` |
| 匿名 Consumer | `openConsumer(queue)` | 非持久化位点 |
| peek | `peekFirstText/peekLastText/peekTextAtIndex`、`peek*Bytes`、`peek*Fory(…[, SchemaMode])` | 临时 Tailer，不影响位点；同样会打开磁盘上已存在的队列，目录不存在返回 null |
| 位点控制 | `toStart/toEnd/moveToIndex/getTailerIndex(queue, consumerId)` | 作用于共享 Consumer |

- 带 consumerId 的是 Chronicle NamedTailer，位点持久化在队列目录中，重启后继续。
- `TailerStartStrategy`：只在 Consumer（长期 Consumer、Template 共享 Consumer、Listener）创建后的**第一次定位**时执行一次，之后的读取都从当前位置继续（在此之前调用过 `toStart/toEnd/moveToIndex` 则不再执行）：
  - `RESUME`（默认）：继续上次位置，首次从头。
  - `RESUME_LATEST`：首次定位且 index 为 0 时跳到末尾，之后继续。
  - `START`：首次定位回到开头，之后顺序读。
  - `END`：首次定位跳到末尾，之后读取新写入的消息。
  - Template 共享 Consumer 被缓存淘汰或 `clearSharedResources()` 后会重新创建，策略会再执行一次；对持久化位点的 NamedTailer，`START`/`END` 在每次重新创建（含应用重启）时都会重新定位。
- Fory 消息的 SchemaMode：默认按队列配置（单队列 `fory-schema-mode` > 全局 `fory-schema-mode`，默认 `COMPATIBLE`，容忍字段增删）；`writeFory/readFory/readForyBatch/peek*Fory`、Publisher `publishFory`、Consumer `consumeFory/consumeForyBatch` 都有带 `SchemaMode` 的重载。读写两端模式必须一致，两种模式字节流互不兼容。
- 原始 `createTailer(queue, tailerId)` 已废弃并直接抛 `UnsupportedOperationException`。

### 3.5 @ChronicleQueueListener

```java
@Component
public class TradeListener {

    @ChronicleQueueListener(queue = "trade", consumerId = "trade-text-listener")
    public void onText(String text) { }

    @ChronicleQueueListener(queue = "trade_obj", consumerId = "trade-obj-listener",
            maxRetries = 3, retryDelayMs = 200, retryBackoffMode = ChronicleQueueListenerRetryBackoffMode.EXPONENTIAL,
            errorQueue = "trade_obj_error", failurePolicy = ChronicleQueueListenerFailurePolicy.CONTINUE)
    public void onOrder(OrderDto order) { }                          // 自动推断为 FORY

    @ChronicleQueueListener(queue = "settle", consumerId = "settle-listener",
            maxRetries = 3, errorQueue = "settle_error",              // errorQueue 用于记录失败详情
            failurePolicy = ChronicleQueueListenerFailurePolicy.STOP) // 停在失败消息，修复后 start/重启会重投
    public void onSettle(SettleDto dto) { }

    @ChronicleQueueListener(queue = "trade", consumerId = "trade-batch", batchSize = 100)
    public void onBatch(List<String> texts) { }

    @ChronicleQueueListener(queue = "tick", consumerId = "tick-fast",
            startStrategy = TailerStartStrategy.RESUME_LATEST, idleMode = ChronicleQueueListenerIdleMode.BUSY_SPIN)
    public void onTick(MarketTicker t) { }                          // BytesMarshallable，需无参构造
}
```
- 方法必须**恰好一个参数**；格式 `AUTO` 推断：`String`→TEXT、`byte[]`→BYTES、`BytesMarshallable`→MARSHALLABLE、`Wire`→WIRE、其他→FORY。参数是 `List<X>` 或 `batchSize > 1` 即为批量监听（必须是带泛型的 List）。
- `consumerId` 与 `threadName` 支持 `${...}` 占位符；`queue`、`errorQueue` 不支持。
- **`consumerId` 必填**：它是持久化位点的 NamedTailer ID，留空时启动注册阶段抛 `IllegalStateException`（不再自动生成，避免重命名 Bean/方法/参数类型后变成新消费者从头重放）。
- 每个 listener 一个独立线程（默认 daemon），在 `afterSingletonsInstantiated` 时启动；同一 (queue, consumerId) 重复注册抛异常。
- FORY 格式按队列配置的 SchemaMode（默认 `COMPATIBLE`）反序列化，与 `writeFory` 默认一致。
- 投递语义：先以原始形式读取（位点前进），再反序列化并调用方法。重试只在内存中重复调用；`CONTINUE` 跳过失败消息；`STOP` 先把位点**回退到失败消息**（批量为该批第一条）再让 listener 进入 FAILED，`registry.start(queue, id)` 或应用重启后会重新投递该消息（若起始策略为 `START`/`END` 则按策略重新定位）。配置 `errorQueue` 时把 `ChronicleQueueListenerErrorMessage`（原队列、consumerId、方法签名、格式、payload、异常信息与堆栈、时间）用 Fory 写入错误队列；`STOP` + `errorQueue` 时失败消息既会进入错误队列、之后也会被重投，业务需幂等。
- 读取/反序列化阶段的消息级异常（如 FORY 反序列化失败、BytesMarshallable 无无参构造）与处理失败一样走 `failurePolicy` / `errorQueue`（反序列化失败时 payload 为原始 `byte[]`，不重试）；只有未读到具体消息的队列级异常才让 listener 线程退出（FAILED）。
- 管理：注入 `ChronicleQueueListenerRegistry`，`getListenerStatuses()`、`getListenerStatus(queue, id)`、`getListenerMetrics()`、`getQueueListenerMetrics([queue])`、`pause/resume/stop/start(queue, id)`。
- 自定义错误处理：声明 `ChronicleQueueListenerErrorHandler` Bean，`handle(queue, consumerId, method, throwable)`。

### 3.6 文件清理（cleanup）

- 某队列的有效开关 = 单队列 `cleanup.enabled`（已设置时）否则全局 `cleanup.enabled`；有效开关为 true 且 `all-consumers-tracked=true`（全局或单队列）时才会删除。全局关闭时单队列 `enabled=true`（YAML 或 `setCleanupOverride`）可单独开启；全局开启时单队列 `enabled=false` 可跳过某个队列。
- 删除条件：`.cq4` 文件不在保留窗口 `[min(lastCycle - reserve, 所有已知 NamedTailer 最小 cycle), lastCycle]` 内，且 `lastModified < now - retention`。
- 已知 NamedTailer = 本进程通过框架打开过的 consumerId + 注册的 listener + `protected-consumer-ids`。外部进程或其他服务的消费者必须列入 `protected-consumer-ids`。
- 某个已知 NamedTailer 位点 ≤ 0 且 `require-listener-position=true`（或它在 protected 列表中）时，整轮放弃该队列。
- 通过 `registerQueue` 外部注册的队列不清理。
- 编程式覆写：`chronicleQueueManager.setCleanupOverride(queueName, override)`。

---

## 4. 生成代码时的规则

### Do
- Map：容量敏感的 Map 在 YAML 中声明 `max-entries` 和 `average-value-size`；自定义 POJO 值声明具体值类型（`initMap` 默认自动用 Fory，或 `initForyMap` / `use-fory-marshaller: true` 强制），持久化数据设置 `fory-schema-mode: COMPATIBLE`。
- Map：热点零 GC 读取让值类型实现 `BytesMarshallable` 并用 `getUsing`；读-改-写用 `updateWithLock`。
- Map：不使用 put/remove 返回值的写进程开启 `put-returns-null` / `remove-returns-null`。
- Queue：生产环境在 `queues` 中声明队列（读写进程使用相同的 `path`），Template 共享读取会打开其他进程已创建的队列目录。
- Queue：`@ChronicleQueueListener` 必须显式写 `consumerId`（框架强制）；需要保留失败详情时配置 `errorQueue`，需要停在失败消息等待修复时用 `STOP`。
- Queue：Fory 消息保持默认 `COMPATIBLE`，读写两端使用同一模式。
- Queue：同一 consumerId 只由一个消费者（Listener、长期 Consumer、Template 共享读取三选一）使用。
- Queue：新消费者只要新消息用 `RESUME_LATEST`，而不是 `END`。
- 开启 cleanup 时同时确认 `all-consumers-tracked` 并把外部消费者列入 `protected-consumer-ids`。
- 按 Chronicle 要求配置 Java 21 的 `--add-opens` / `--add-exports`。

### Don't
- 不要把 chronicle-map / chronicle-queue 当成跨机器的缓存或 MQ。
- 只需要其中一个子模块时按需引用 `libs.componentChronicleMap` / `libs.componentChronicleQueue`，不必引入整个 `libs.bundles.storage`。
- 不要在同一 JVM 内用多个 `ChronicleMapManager` 打开同一个持久化文件；不要删除运行中的 `.lck` 文件。
- 不要中途切换已持久化 Map 的 Fory SchemaMode。
- 不要使用带 `Class<K>, Class<V>` 参数的已废弃 Template 方法。
- 不要用 `Object`/接口/抽象类作为需要 Fory 的 Map 值类型。
- 不要期望读取方法上的策略在每次调用时都生效（只在首次定位时生效一次）；要重新定位请调用 `toStart/toEnd/moveToIndex`。
- 不要直接 `createTailer(queue, tailerId)`（已禁用）。
- 不要在中途切换已有队列数据的 `fory-schema-mode`。
- 不要在 `CONTINUE` 策略的 at-least-once 业务中直接依赖 Listener 的位点（它是“先读后处理”，失败消息会被跳过，需配合 `errorQueue`）。

---

## 5. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | chronicle-map使用手册 §3.2 | `initMap("userCache", String.class, UserInfo.class)` 后直接 put 业务对象 | `initMap` 只在全局 `fory-marshaller-enabled=true` 时才自动用 Fory；默认关闭时由 Chronicle 原生处理，`UserInfo` 需实现 `Serializable` 等 Chronicle 支持的形式。业务 POJO 应使用 `initForyMap` **已修复**：`fory-marshaller-enabled` 默认改为 true，`initMap`/3 参数与 7 参数 `getOrCreateMap` 对具体业务类自动使用 Fory（Object/接口/抽象类除外），手册示例可直接使用。 |
| 2 | chronicle-map使用手册 §7 | `persistence-enabled=false` 时所有 Map 均为纯内存 | 编程式 `getOrCreateMap/getOrCreateForyMap(..., filePath)` 传入非空 filePath 时仍会持久化 **已修复**：`persistence-enabled` 成为总开关，关闭时编程式传入的 filePath 被忽略（WARN）并创建纯内存 Map，与声明式一致。 |
| 3 | chronicle-map 源码 | — | 7 参数的 `getOrCreateMap(...)` 强制不使用 Fory（即使全局开关为 true）；3 参数版本按全局开关自动识别 **已修复**：7 参数版本改为按全局开关 + 值类型自动识别，新增带 `Boolean useForyMarshaller` 的 8 参数重载用于显式指定。 |
| 4 | chronicle-map 源码 | Manager 标注 `@Lazy` | `ChronicleMapTemplate` 非 Lazy 且依赖 Manager，Manager 与声明式 Map 都在启动时创建，`@Lazy` 实际无效（chronicle-queue 同理） **已修复**：移除 chronicle-map / chronicle-queue Manager 上无效的 `@Lazy`，自动配置改为参数注入，文档说明 Manager 在启动时创建。 |
| 5 | chronicle-map 源码（手册未提及） | — | 带类型参数的旧 `put/putIfAbsent/putAll/computeIfAbsent/putMarshallable/putWriteMarshallable` 会自动创建 Map，与新方法“不存在即失败”的约定相反 **已修复**：旧写入方法改为委托新方法，Map 不存在时抛 `IllegalStateException`，不再自动创建。 |
| 6 | chronicle-map / chronicle-queue 文档 | 未提及 JVM 参数与依赖版本 | 依赖为 EA 版本（chronicle-map 3.27ea1、chronicle-queue 5.27ea10）；在 Java 21 上通常需要 `--add-opens/--add-exports` **已修复**：离线仓库只有 EA 版本，版本保持不变；§1 已补充版本说明与 Java 21 所需 `--add-opens/--add-exports` 参数清单。 |
| 7 | chronicle-queue 源码 | 包名 | 包名为 `com.easyfk.chronicle.queue`，不在框架统一的 `com.mcst` 包下；配置前缀为 `easyfk.config.storage.queue`（不是 chronicle.queue） **已修复**：包名已改为 `com.mcst.easyfk.chronicle.queue`（源码、测试、AutoConfiguration.imports 同步），配置前缀保持 `easyfk.config.storage.queue`。 |
| 8 | chronicle-queue-使用手册 §6.3 | `END`：从尾部开始 | 读取方法上的策略每次调用都会执行，`END` 会在每次读取前跳到末尾，轮询读取几乎永远读不到消息；`START` 在批量读取中会反复返回同一批 **已修复**：读取策略只在 Consumer 创建后第一次定位时执行一次，之后从当前位置继续，`END` 可用于轮询，`START` 不再重复返回同一批。 |
| 9 | chronicle-queue-使用手册 §5.3 / §5.5 | `create-directories-on-startup=false` 时，后续首次使用队列时仍会按预定义配置创建 | 写入和 `openConsumer` 会创建队列，但 Template 的 `read*` 共享读取（`createIfMissing=false`）在本进程未创建队列时直接返回 null。只读进程若关闭启动预创建，会一直读不到数据 **已修复**：Template `read*`/`peek*` 在本进程未打开但磁盘上已有队列目录时会打开该队列（`Manager.getExistingQueue`），目录不存在才返回 null。 |
| 10 | chronicle-queue-使用手册 §7.4.1 | `consumerId` 留空时框架自动生成 | 自动生成值依赖 beanName、方法名、参数类型名，任何重命名都会产生新消费者并按 startStrategy 重新开始（默认从头重放） **已修复**：`consumerId` 改为必填，留空在注册阶段抛 `IllegalStateException`，不再自动生成。 |
| 11 | chronicle-queue-使用手册 §7.4.1 | `STOP`：记录失败后停止当前 listener | 失败消息在调用前已被读取，位点已越过；listener 停止后重启不会重新消费这条消息（未配置 errorQueue 时该消息丢失） **已修复**：`STOP` 会把位点（含 NamedTailer 持久化位点）回退到失败消息再停止，重新 start 或重启后会重投该消息。 |
| 12 | chronicle-queue 源码 | — | FORY 等格式在读取/反序列化阶段抛出的异常不进入重试，直接使监听线程退出（状态 FAILED） **已修复**：监听改为先读原始数据再反序列化，消息级读取/反序列化异常走 failurePolicy/errorQueue，不再让监听线程退出。 |
| 13 | `ChronicleQueueDefinedInfo.CleanupOverride` 注释 | 单队列 `enabled`：true 强制启用 | 清理自动配置以全局 `cleanup.enabled=true` 为条件，全局关闭时单队列 true 无效 **已修复**：清理调度器不再以全局开关为条件，每个队列按“单队列 enabled 优先、否则全局 enabled”判断，全局关闭时单队列 true 可单独生效。 |
| 14 | chronicle-queue 源码 | — | `ChronicleQueueCleanupAutoConfiguration` 带 `@EnableScheduling`，开启清理会为整个应用启用 Spring 调度（会激活业务中原本未生效的 `@Scheduled`） **已修复**：清理改用组件私有的 `SmartLifecycle` 单线程调度器，不再使用 `@EnableScheduling`。 |
| 15 | chronicle-queue 源码 | — | `ChronicleQueueListenerBeanPostProcessor` 是普通 BPP 且依赖 Registry → Template → Manager，这几个 Bean 会被提前创建（启动日志会出现 “not eligible for getting processed by all BeanPostProcessors”） **已修复**：BPP 改为 static `@Bean`，只持有 `ObjectProvider<Registry>`，扫描结果在所有单例实例化后才注册，不再提前创建 Registry/Template/Manager。 |
| 16 | chronicle-queue 源码 | — | `readFory/consumeFory/writeFory` 不支持传 SchemaMode，持久化消息使用 serializer-fory 全局默认模式（默认 SCHEMA_CONSISTENT），类结构变化后旧消息无法读取 **已修复**：新增 `fory-schema-mode`（全局默认 COMPATIBLE，可单队列覆写），读写、peek、Listener 默认使用队列模式，并提供带 `SchemaMode` 的重载。 |
| 17 | easyfk-dependencies `settings.gradle` | `storage` bundle 包含 `storageChronicle`（`com.mcst:storage-chronicle`） | 仓库中不存在 `storage-chronicle` 模块，引用整个 `storage` bundle 可能解析失败（推断，未运行验证）；应单独引用 `componentChronicleMap` / `componentChronicleQueue` **已修复**：easyfk-dependencies 的 `storage` bundle 已移除 `storageChronicle`，只包含存在的模块。 |
| 18 | chronicle-queue-使用手册 §7.4.10 | `failurePolicy = STOP` 示例 | 见第 11 条：STOP 后失败消息不会被重放，示例未配置 errorQueue，失败消息直接丢失 **已修复**：见第 11 条，STOP 后失败消息会被重投；§3.5 示例补充了 STOP + errorQueue 的写法与重复投递说明。 |
