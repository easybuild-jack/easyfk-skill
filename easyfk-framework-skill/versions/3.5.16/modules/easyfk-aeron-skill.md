# easyfk-aeron Skill 参考文档

> 所属项目：`easyfk-aeron`（独立 Gradle 工程，16 个子模块）　坐标：`com.mcst:<module>:3.5.16`，BOM 中为 `aeron` bundle
> 依据：全部子模块 `src/main` 源码、各模块 `build.gradle`、`settings.gradle`（自有 catalog）、starter 单元测试；对齐 `docs/` 下《Aeron 组件使用手册》《aeron协议说明》《序列化Codec接入指南》《监控指南》《Aeron Chronicle 状态存储指南》《跨语言互通指南》。
> 文档与源码不一致时 **以源码为准**，差异见文末「复查记录」。

---

## 1. 模块定位

基于 Aeron 1.54.2 的**超低时延消息广播 SDK**：一个发送方 → N 个接收方，IPC（共享内存）/ UDP 单播 / UDP 组播（MDC）。

- **只做 fan-out 广播**：不持久化消息、没有 ack / 重投 / 回放、没有消费位点；掉线或晚加入的订阅方收不到历史消息。
- 需要补历史、ack 重投、自动 rebalance、跨实例全局有序时，用 component-mq（Kafka / RocketMQ / RabbitMQ）或 aeron-cluster，**不要用本组件**。
- 同机单进程内的持久化顺序队列用 component-chronicle 的 chronicle-queue。

| 场景 | 推荐搭配 |
|---|---|
| 同机进程间高频广播（行情、撮合 → 风控） | `aeron:ipc` + `INLINE` + `BUSY_SPIN` |
| 跨主机点对点 | `aeron:udp?endpoint=host:port` |
| 一发多收、订阅方动态加入 | UDP MDC |
| 同 key 保序 + 跨 key 并行 | 多 partition + 按 key 发送 |
| 下游多实例分摊 | 静态分组消费（`partition-assignment`） |
| 发送侧绝不能丢 | Outbox + 消费端 `dedup-window` |
| 事件流 → 可查询状态表 | aeron-chronicle |

## 2. 模块清单与依赖

包名统一 `com.mcst.aeron.*`。

| 模块 | 作用 | 何时引入 |
|---|---|---|
| `aeron-spring-boot-starter` | 自动装配；`api` 传递 common / driver / producer / consumer / producer-outbox | **Spring Boot 服务一律引它** |
| `aeron-codec-fory` | Apache Fory 二进制 codec（wire id 5），POJO 零配置兜底的前提 | 收发 POJO 时（默认推荐） |
| `aeron-codec-json` | Jackson JSON codec（wire id 3） | 需要可读 wire / 跨语言 |
| `aeron-codec-protobuf` | Protobuf codec（wire id 2），`api` 传递 `protobuf-java:4.36.2` | 跨语言强 schema |
| `aeron-codec-sbe` | SBE 泛型适配（wire id 1），**不含** sbe-tool | 极致低延迟、跨语言 |
| `aeron-compression-lz4` / `-zstd` | LZ4（id 1）/ Zstd（id 2），含 native | 大 payload；DEFLATE（id 3）内置于 common |
| `aeron-metrics-micrometer` | Micrometer 指标适配 | 接 Prometheus |
| `aeron-chronicle` | 事件流物化到 Chronicle Map，`api` 传递 `com.mcst:chronicle-map` | 需要状态表 |
| `aeron-common` / `aeron-driver` / `aeron-producer` / `aeron-consumer` / `aeron-store` / `aeron-producer-outbox` | 核心 SDK | 非 Spring 场景手写 builder 时 |
| `aeron-examples` | 可运行示例 | 不作为依赖引入 |

```groovy
dependencies {
    implementation platform('com.mcst:easyfk-dependencies:3.5.16')
    implementation 'com.mcst:aeron-spring-boot-starter'
    implementation 'com.mcst:aeron-codec-fory'
    // 可选
    // implementation 'com.mcst:aeron-compression-lz4'
    // implementation 'com.mcst:aeron-metrics-micrometer'
    // implementation 'org.springframework.boot:spring-boot-starter-actuator'
}
```

- 第三方版本**全部由 BOM 的 `aeronRuntime` bundle 约束**（本版本起不再写在本工程 catalog）：`aeron-all` / `aeron-driver` / `aeron-client` / `aeron-archive` / `aeron-cluster` **1.54.2**、`agrona` **2.7.1**、`sbe-tool` **1.42.0**（catalog 中有别名，没有模块引用；SBE codegen 在业务自己的 schema 工程里做）、`protobuf-java` / `-util` **4.36.2**、`lz4-java` **1.14.0**、`zstd-jni` **1.5.7-28**。`micrometer-core` 也不再写死版本，跟随 Boot 3.5。JSON 的 Jackson、Fory（经 `com.mcst:serializer-fory`）同样由 BOM 管理。**不要**在业务工程里覆盖 Aeron / Agrona 版本，aeron-cluster 与本工程必须同版本。
- 核心 SDK 与 starter **不传递 Spring 和 easyfk-core**：`aeron-common` / `aeron-store` / `aeron-driver` 只 `api` 传递 `slf4j-api`，starter、`aeron-chronicle` 的 Spring 依赖都是 `compileOnly`（见复查记录 #6）。非 Spring 项目自己加一个日志实现（如 `logback-classic`）；Spring Boot / easyfk 项目已带 Logback，不要再加 `slf4j-simple`。业务代码用到 easyfk-core 时自己声明。
- 运行环境：**JDK 21**；starter 要求 Spring Boot ≥ 2.6.13（`SpringBootVersionCheck`），同时提供 `spring.factories` 与 `AutoConfiguration.imports`。

### 2.1 JVM 参数（必须）

```
--add-opens java.base/java.lang=ALL-UNNAMED
--add-opens java.base/java.lang.reflect=ALL-UNNAMED
--add-opens java.base/java.io=ALL-UNNAMED
--add-opens java.base/java.nio=ALL-UNNAMED
--add-opens java.base/java.util.zip=ALL-UNNAMED
--add-opens java.base/sun.nio.ch=ALL-UNNAMED
--add-opens java.base/jdk.internal.misc=ALL-UNNAMED
```
启动脚本、Dockerfile、Gradle `test { jvmArgs ... }` 都要加。用到 aeron-chronicle 时还要叠加 chronicle skill 文档 §1 的参数。

## 3. Spring Boot 接入（推荐路径）

### 3.1 配置（前缀 `easyfk.config.aeron`）

```yaml
easyfk:
  config:
    aeron:
      enabled: true                      # false：整个 starter 不装配
      codec:
        default-codec: fory              # fory（默认）| none
      metrics:
        enabled: true
      shutdown:
        timeout: 30s
      # producer: { enabled: false }     # 全局开关，优先于 per-driver；纯订阅服务用
      # consumer: { enabled: false }     # 全局开关；纯发送服务用
      driver:                            # 单 driver（内部归一为 drivers.default）；与 drivers 互斥
        embedded: true                   # false 时 aeron-dir 必填，连外部 MediaDriver
        aeron-dir: /dev/shm/aeron-app
        dir-delete-on-start: false       # starter 默认 false；SDK builder 默认 true
        dir-delete-on-shutdown: true
        driver-timeout-ms: 10000
        threading-mode: SHARED           # SHARED | SHARED_NETWORK | DEDICATED | INVOKER（仅 embedded）
        # driver-idle-strategy: BUSY_SPIN  # 仅 embedded；不配用 Aeron 默认
        # mtu-length: 8KB                # UDP MTU，单帧上限 = mtu − 32；(0, 65504] 且 32 的倍数
        # ipc-mtu-length: 8KB
        producer:
          enabled: true
          channels: [aeron:ipc]          # 下标即 partitionId；单元素 = 纯 fan-out
          base-stream-id: 1001
          # partitioner: MURMUR3         # 不配：单 partition SINGLETON，多 partition MURMUR3
          no-key-strategy: ROUND_ROBIN   # ROUND_ROBIN | FIRST | TOPIC_HASH
          backpressure:
            strategy: RETRY_THEN_FAIL    # BLOCK | DROP_NEWEST | FAIL | RETRY_THEN_FAIL
            retries: 100
          outbox:
            enabled: false               # 见 §3.7
        consumer:
          enabled: true
          channels: [aeron:ipc]          # 必须与 producer.channels 等长
          base-stream-id: 1001           # 必须与 producer 一致
          # partition-assignment: [0, 1] # 静态分组消费；不配 = 订全部
          # group-id: billing            # 仅作 metrics tag
          delivery-mode: RING_BUFFER_POOL # INLINE | RING_BUFFER_POOL
          worker-threads: 1
          ring-buffer-capacity: 65536
          fragment-limit: 16
          dedup-window: 0                # 0 关闭；否则 ≥2 的 2 的幂；每 partition 独立
          idle-strategy: BACKOFF         # BUSY_SPIN | NO_OP | YIELDING | BACKOFF | SLEEPING
          reuse-inline-context: false    # 仅 INLINE 生效
          max-decompressed-bytes: 16MB   # ≥ 1024，防 zip-bomb
```

- 枚举类字符串大小写不敏感，非法值启动期抛 `IllegalStateException`（带允许值列表）。
- 不配任何 `driver` / `drivers` 时启动失败（`no aeron driver configured`）。
- 同一 driver 内 producer 与 consumer 的 `base-stream-id` 或 `channels` 长度不一致，启动只打 WARN，**运行时静默收不到消息**。

### 3.2 多 driver

```yaml
easyfk:
  config:
    aeron:
      default-driver: ipc-local          # 多 driver 必填，且必须是 drivers 的 key
      drivers:
        ipc-local:
          aeron-dir: /dev/shm/aeron-ipc
          producer: { channels: [aeron:ipc] }
          consumer: { channels: [aeron:ipc] }
        udp-prod:
          embedded: false
          aeron-dir: /var/lib/aeron-prod
          producer: { channels: ["aeron:udp?endpoint=10.0.1.5:40123"] }
          consumer: { enabled: false }
```

- driver 名必须匹配 `[a-zA-Z][a-zA-Z0-9_-]{0,31}`。
- Bean 名：单 driver 为 `aeronDriverManager` / `aeronCodecRegistry` / `aeronProducer` / `aeronConsumer`；多 driver 为 `<前缀>_<driver 名驼峰>`（`ipc-local` → `aeronProducer_ipcLocal`），`default-driver` 对应的 bean 另有不带后缀的 alias。
- **`default-driver` 只决定 alias，不是 `@AeronTopic` 的默认值**：多 driver 时 `@AeronTopic` 必须写 `driver`，否则启动失败。
- 每个 bean 都带 `@AeronDriver("<原始 driver 名>")` 限定符。

### 3.3 发送

```java
@Service
public class TickPublisher {
    @Autowired
    private Producer producer;                                   // 单 driver

    @Autowired @AeronDriver("udp-prod")
    private Producer udpProducer;                                // 多 driver（或 @AeronProducerRef("udp-prod")）

    public void publish(TradeTick tick) {
        producer.send("ticks.aapl", tick);                       // 不给 key：按 no-key-strategy 选 partition
        producer.send("orders.new", order.getCustomerId(), order); // 给 key：同 key 同 partition、严格 FIFO
        producer.sendAll("orders.new", customerId, List.of(o1, o2)); // 同 key 批量，保 FIFO
        producer.send("orders.new", order, traceHigh, traceLow);  // 业务自带 128-bit msgId
    }
}
```

- **字段类型一律声明为接口 `com.mcst.aeron.producer.Producer`**。开启 outbox 后 bean 运行时类型是 `OutboxProducer`，按 `AeronProducer` 注入会失败。
- 返回值 `>= 0` 表示已接受（直发是 Aeron position，outbox 是 WAL 序号），`-1` 表示被 `DROP_NEWEST` 丢弃；**只判断符号**。`sendAll` 返回成功条数，中途异常不回滚已发部分。
- `payload` 不能为 null；codec 按 `payload.getClass()` **精确匹配**，子类不会落到父类 codec。
- **single-writer**：同一个 producer 的 `send` / `sendAll` / `close` 必须串行（底层 `ExclusivePublication`）。多线程发送要么单线程 + 队列串行化，要么每个线程各自构建 producer（共享 driver）。
- `isConnected()` = 至少一个 partition 有订阅方；`isAllConnected()` = 全部；没有订阅方时发送会进入背压。
- 需要「启动即发」放到 `ApplicationRunner` / `ApplicationReadyEvent`；`@PostConstruct` 时订阅可能尚未建立。

### 3.4 订阅：`@AeronTopic`

```java
@Component
public class TradeSubscriber {

    @AeronTopic(value = "trades.new", payloadType = Trade.class)
    public void onTrade(Trade t, MessageContext ctx) { }

    @AeronTopic(value = "trades.delete", payloadType = TradeKey.class)
    public void onDelete(TradeKey k) { }

    @AeronTopic(driver = "udp-prod", value = "audit.events", payloadType = AuditEvent.class) // 多 driver 必填 driver
    public void onAudit(AuditEvent e) { }
}
```

- 签名：返回 `void`；参数 `(T)` 或 `(T, MessageContext)`，第二个参数必须是 `com.mcst.aeron.consumer.MessageContext`；public 或包级可见、非 static、非 abstract、不声明受检异常。不符合时启动失败。
- topic：字符集 `[A-Za-z0-9.\-_]`，长度 1..255，精确匹配（不支持通配符）。
- 同一 consumer 重复订阅同一 topic 抛 `IllegalStateException`；不支持退订单个 topic。
- consumer 被关闭（全局或所有 per-driver `enabled=false`）却仍有 `@AeronTopic` 时，`AeronLifecycle.start()` 一次列出全部残留方法并启动失败。
- handler 抛出的异常被 SDK 拦截并上报 `metrics.onError`，不会中断 poll；**没有重试**，消息直接丢弃。
- `MessageContext`：`topic()`、`partition()`、`msgIdHigh()/msgIdLow()`、`timestampNanos()`、`codecId()`、`compressionId()`、`latencyMicros()`（两端墙钟相减，跨主机只作粗略观测）。

### 3.5 投递模式与线程

| 配置 | 行为 | 约束 |
|---|---|---|
| `RING_BUFFER_POOL`（默认） | poll 线程解码后投递到 worker 池（`ArrayBlockingQueue`） | `worker-threads > 1` 时 handler 并发执行，**必须线程安全**；队列满直接丢弃并计 `onDispatchDropped` |
| `INLINE` | handler 在 poll 线程上执行 | handler 阻塞会拖慢整条链路；只放极轻的逻辑 |
| `reuse-inline-context: true` | INLINE 下复用 `MessageContext` | ctx 只在回调期间有效，不得保存引用 |

每个被订阅的 partition 各一个 poll 线程（`aeronmq-poll-*`），各占一个 idle strategy；`BUSY_SPIN` / `NO_OP` 会让每个 poll 线程占满一核。

### 3.6 Codec 注册

| 方式 | 写法 | 说明 |
|---|---|---|
| A：`@Bean Codec<T>`（推荐显式） | `@Bean Codec<Trade> tradeCodec() { return ForyCodec.forType(Trade.class); }` | 每个 driver 的 registry 都会注册 |
| B：YAML | 见下方 | 可用 `drivers` 限定生效范围 |
| C：零配置兜底 | classpath 有 `aeron-codec-fory` 且 `default-codec=fory` | 未注册的 POJO 在 subscribe / send 时自动 `ForyCodec.forType(T)` |

```yaml
easyfk:
  config:
    aeron:
      codecs:
        - class-name: com.mcst.aeron.codec.fory.ForyCodec   # 注意是 class-name，不是 class
          factory-method: forType                            # 为空则调用无参构造
          factory-args: [com.your.app.Order]                 # 只支持 Class 类型参数
          drivers: [ipc-local]                               # 省略 = 所有 driver
```

- 同一 `type` 被 A 和 B 重复注册时启动失败。显式注册始终优先于兜底。
- `byte[]`（RawBytes，id 0）、`String`（id 4）内置，无需注册。
- Fory 兜底只注册主类型：**含嵌套 POJO（`List<Item>` 等）时必须显式写** `ForyCodec.builder(Order.class).register(Item.class).build()`；JAVA 模式下两端的 `register` 顺序必须完全一致（或给每个类型指定 `typeId`）。
- 跨语言互通设 `default-codec: none`，并对每个类型显式注册 JSON / Protobuf / SBE codec（跨语言路线**不含 Fory**）。Fory XLANG 模式要求每个注册类都给 `typeId` 或 `typeName`。
- 收发两端的 payload 类型必须是同一个类（全限定名一致），建议放到共享 domain jar。
- 自定义 codec 实现 `com.mcst.aeron.common.codec.Codec<T>`，wire id 从 `CodecIds.FIRST_USER_DEFINED`（100）起；`encodedLength` 与 `encode` 必须对同一对象给出一致长度。

| Codec | 工厂 |
|---|---|
| Fory | `ForyCodec.forType(T.class)` / `ForyCodec.builder(T.class).register(X.class).typeId(101).crossLanguage(true).build()` |
| JSON | `JsonCodec.forType(T.class)` / `JsonCodec.builder(T.class).objectMapper(m).build()`（默认是 `new ObjectMapper()`，不带 JavaTimeModule） |
| Protobuf | `new ProtobufCodec<>(Msg.class)` / `ProtobufCodec.builder(Msg.class).extensionRegistry(r).build()`；每个消息类型一个实例 |
| SBE | `SbeCodec.fixedLength(T.class, len, T::encode, T::decode)` / `SbeCodec.varLength(T.class, T::maxBytes, T::encode, T::decode)` |

### 3.7 Outbox（先持久化再转发）

```yaml
        producer:
          outbox:
            enabled: true
            wal-dir: /var/lib/myapp/aeron-wal   # 不配：aeron-store-wal/<driver 名>（相对工作目录）
            fsync-policy: INTERVAL              # PER_RECORD | INTERVAL | OS_BUFFERED
            flush-interval-millis: 100
            store-type: SEGMENTED               # SEGMENTED | SINGLE_FILE
            segment-bytes: 67108864             # 仅 SEGMENTED，≥ 1024
            checkpoint-every-records: 1
            drain-on-close-millis: 5000
```

- `send` 返回即已落盘；后台单线程转发到 Aeron，失败原地重试、不跳过；重启从 checkpoint 续发，**携带相同 msgId**。
- 投递语义变为 at-least-once：**消费端必须开 `dedup-window`**（窗口按峰值速率 × 可能的重放时长估算）。
- 保证的是「发送侧不丢」，不是「消费侧补历史」。
- 每个开启 outbox 的 producer 必须使用**独立的 `wal-dir`**，多写者共用会互相损坏；生产环境显式指定到持久盘。
- 超过帧上限的消息在落盘前就抛 `OutboxException`，不会写入 WAL。
- WAL CRC 损坏时转发器停机并上报 `onError`，数据保留待人工处理。

### 3.8 压缩、指标、健康检查、生命周期

- **压缩**：声明 `@Bean CompressionCodec`（如 `Lz4Compression.INSTANCE`、`new ZstdCompression(3)`）即对 producer 生效；多 driver 各自压缩时 bean 名取 driver 名（原名或驼峰），匹配不到则告警并不压缩。消费端按帧头自动解压，但**必须引入对应压缩模块**。短消息（< 几百字节）和 SBE 不建议压缩。
- **指标**：classpath 有 `aeron-metrics-micrometer` 且容器里有 `MeterRegistry` 时自动注册 `ProducerMetrics` / `ConsumerMetrics` / `OutboxMetrics`（均可被业务同类型 bean 覆盖）。指标只按 `partition` / `group` 打标签，**不按 topic 打标签**（防止基数爆炸）。重点告警：`aeron.outbox.backlog.bytes`、`aeron.consumer.dispatch.dropped`、`aeron.producer.backpressure.dropped`。
- **健康检查**：引入 actuator 后自动注册 `aeron` HealthIndicator；只要 driver 的 Aeron client 在线就是 UP，`producer.isConnected()` 不参与判定。关闭：`management.health.aeron.enabled=false`。
- **生命周期**：`AeronLifecycle`（phase `Integer.MIN_VALUE + 1000`）启动顺序 driver → producer → 订阅全部 `@AeronTopic` → `consumer.start()`；关闭顺序 consumer → producer → driver，总超时 `shutdown.timeout`。不支持同一 context 内 stop 后立即 start。
- starter 的停机、健康检查只处理 `aeron*` 前缀的 bean，业务自己实现的 `Producer` / `Consumer` 不受托管。

## 4. 核心 SDK（非 Spring 场景）

```java
try (DriverManager driver = DriverManager.embedded(DriverConfig.builder()
             .aeronDir("/dev/shm/aeron-svc1").dirDeleteOnStart(false).build());
     AeronProducer producer = AeronProducer.builder()
             .driver(driver)                                   // 或 ownDriver(driver)：close 时连带关闭 driver
             .config(ProducerConfig.builder().channels(ChannelSpec.ipc()).baseStreamId(1001).build())
             .codec(ForyCodec.forType(Order.class))
             .compression(Lz4Compression.INSTANCE)             // 可选
             .build();
     AeronConsumer consumer = AeronConsumer.builder()
             .driver(driver)
             .config(ConsumerConfig.builder().channels(ChannelSpec.ipc()).baseStreamId(1001).dedupWindow(1 << 16).build())
             .codec(ForyCodec.forType(Order.class))
             .build()) {
    consumer.subscribe("orders.new", Order.class, (o, ctx) -> { });
    consumer.start();                                          // subscribe 之后再 start
    producer.send("orders.new", order);
}
```

- `DriverManager.embedded(cfg)` / `DriverManager.external(aeronDir)`；**SDK builder 的 `dirDeleteOnStart` 默认 true**，同机多 JVM 必须改成 false 且各用不同 `aeronDir`（或共用一个外部 driver）。
- `ChannelSpec.ipc()` / `ipcUntethered()`（仅订阅端）/ `udpUnicast("host:port")` / `udpMdc(group, port)`；YAML 写法 `aeron:ipc?tether=false` 只能用在 consumer，producer 端配置会启动失败。
- Outbox 手动包装：`OutboxProducer.wrap(raw, outboxConfig, CodecRegistry.withDefaults(), MessageIdGenerator.snowflake(), OutboxMetrics.noop(), true)`；包装后**不得再直接用 raw 发送**。
- 部署期校验静态分组：`Cluster.validateAssignments(List.of(Set.of(0,1), Set.of(2,3)), 4)`（要求完全覆盖且互不重叠）。

## 5. 关键约束

| 约束 | 说明 |
|---|---|
| 帧大小 | 单帧 = 40 字节头 + topic + payload，必须 ≤ `mtu − 32`（默认 MTU 1408 → 1376 字节）；SDK 用 `tryClaim`，**不会自动分片**。超限抛 `AeronMqException: frame size N exceeds ...`。调大 `mtu-length` / `ipc-mtu-length`（UDP 超过 1500 需要 jumbo frame），或业务分块；调 term buffer 无效 |
| 两端对齐 | producer 与 consumer 的 `channels` 长度、`base-stream-id`、codec 类型必须一致，否则静默收不到 |
| 慢订阅 | Aeron 默认 tethered：一个不消费的订阅方会把 producer 拖进背压。可丢的行情 / 快照订阅端改用 `aeron:ipc?tether=false`；at-least-once 链路不能用 |
| 背压 | `RETRY_THEN_FAIL`（默认，重试后抛 `BackpressureException`）/ `BLOCK`（业务线程无限阻塞）/ `FAIL` / `DROP_NEWEST`（返回 -1）。`PublicationTerminalException` 表示 publication 已失效，需重建 producer |
| 去重 | `dedup-window` 是近窗口防抖，不是强幂等；内存约 `窗口 × partition 数 × 16` 字节 |
| 多 partition 无 key | 按 `no-key-strategy` 逐条选 partition，跨消息不保序；要保序就传 key |

异常层次：`AeronMqException` → `BackpressureException` → `PublicationTerminalException`；`CodecException`、`CompressionException`、`FrameDecodeException`。消费端的解码、解压、帧异常都只上报 `metrics.onError`，不进入 handler。

## 6. aeron-chronicle（事件流 → 状态表）

```java
@Bean
AeronChronicleBindingSpec<QuoteEvent, String, Quote> quoteState() {
    return AeronChronicleBindingSpec.<QuoteEvent, String, Quote>builder()
            .topic("md.quote").eventType(QuoteEvent.class)
            .mapName("quotes").keyType(String.class).valueType(Quote.class)
            .key(QuoteEvent::symbol)
            .value(e -> new Quote(e.symbol(), e.price(), e.version()))
            .tombstoneWhen(e -> e.op() == 1)          // 可选：命中则 remove
            .versionedBy(Quote::version)              // 可选：参数是存储值 V，不是事件
            // .driver("ipc-a") / .consumerBeanName("...")  多 driver 时指定
            .build();
}
```

- 开关 `easyfk.config.aeron.chronicle.enabled`（默认 true）；Map 本身按 `easyfk.config.chronicle.map.*` 配置（见 chronicle skill 文档），推荐在 `maps` 中预声明并开启 `put-returns-null` / `remove-returns-null`。
- `AeronChronicleLifecycle`（phase `MIN_VALUE + 500`）早于 `AeronLifecycle` 完成订阅；任一绑定失败即启动失败。
- `filePath(...)` 必须和 `mapParams(...)` 一起设置；原生类型值用 `.plainMarshaller()`。
- 状态物化建议 `delivery-mode: INLINE`；用 `RING_BUFFER_POOL` 时必须配 `versionedBy`，否则同 key 并发乱序可能停在旧值。
- key / value 提取为 null 时计为畸形事件丢弃；提取函数抛异常则上报 `onError`。
- 编程式使用 `StateMaterializer.builder().map(...).key(...).value(...).build()` 后 `consumer.subscribe(topic, E.class, materializer)`；关闭时**先关 consumer 再关 map**，否则可能 SIGSEGV。
- 状态表只能由本组件单写；跨进程读端的建表参数必须完全一致。

## 7. 生成代码时的规则

### Do
- Spring Boot 服务引 `aeron-spring-boot-starter` + `aeron-codec-fory`，发送用 `@Autowired Producer`，接收用 `@AeronTopic`。
- 注入类型一律用 `Producer` 接口；多 driver 用 `@AeronDriver("name")` 或 `@AeronProducerRef` / `@AeronConsumerRef` 限定。
- 多 driver 时每个 `@AeronTopic` 都写 `driver`，并配置 `default-driver`。
- 含嵌套对象的 POJO 用 `@Bean Codec<T>` 显式声明 `ForyCodec.builder(T.class).register(...)`；收发两端共用同一份 domain 类。
- YAML 注册 codec 用 `class-name` 键。
- 同 key 需要保序时传 key；批量同 key 用 `sendAll(topic, key, list)`。
- 开启 outbox 时同时配置独立的 `wal-dir` 和消费端 `dedup-window`。
- 生产环境 `dir-delete-on-start: false`，同机多 JVM 用不同 `aeron-dir` 或共用外部 driver。
- 行情低延迟链路：`INLINE` + `BUSY_SPIN` + driver `DEDICATED`，并做核绑定。
- 消息偏大时调 `mtu-length` / `ipc-mtu-length`，或开启压缩；UDP 两端 driver 的 MTU 保持一致。
- 启动后立即发送的逻辑放在 `ApplicationRunner` / `ApplicationReadyEvent`。
- 按 §2.1 配置 JVM `--add-opens`。

### Don't
- 不要把本组件当 MQ：不要依赖它补历史、ack、重投或持久化位点。
- 不要多线程并发调用同一个 producer 的 `send`。
- 不要按 `AeronProducer` 具体类型注入（开启 outbox 后注入失败）；也不要在 outbox 包装后继续使用底层 raw producer 发送。
- 不要在 producer 的 channels 里写 `tether=false`；不要在 at-least-once 链路的订阅端用 `tether=false`。
- 不要把 `send` 返回值当 Aeron position 做比较。
- 不要让 producer / consumer 的 `channels` 长度或 `base-stream-id` 不一致。
- 不要在 `RING_BUFFER_POOL` + 多 worker 下写非线程安全的 handler；不要在 `INLINE` handler 里做 IO / DB / RPC。
- 不要保存 `reuse-inline-context` 模式下的 `MessageContext` 引用。
- 不要同时配置 `driver` 和 `drivers`；不要把同一类型同时用 `@Bean` 和 YAML 注册。
- 跨语言链路不要用 Fory，也不要依赖默认 Fory 兜底（设 `default-codec: none`）。
- 不要按 topic 给自定义指标打标签。
- 不要为本组件另引 Aeron / Agrona / Protobuf / LZ4 / Zstd 的其他版本，也不要另引 `slf4j-simple`。
- 不要在 `@PostConstruct` 里发送需要本进程订阅方收到的消息。

## 8. 复查记录

| # | 位置 | 问题 | 处理 |
|---|---|---|---|
| 1 | `CodecFactoryResolver`、手册 §17.5 | 手册示例和启动报错都写 `codecs[].class`，但 `CodecProperties` 的字段是 `className`，Spring 绑定键为 `class-name`；按手册写 `class:` 时绑定不上，启动报 `codecs[].class is required`，报错文字又引导用户继续写错的键（`AeronCodecAutoConfigurationTest` 也用了 `.class`，只校验了 BeanDefinition，没发现绑定失败） | **已修复**：报错文字与类注释改为 `class-name`；手册示例改为 `class-name:`；`CodecFactoryResolverTest`、`AeronCodecAutoConfigurationTest` 同步改用 `class-name`（本次未运行测试） |
| 2 | 手册 §17.2 / §18.1、`AeronProperties.defaultDriver` 注释 | 写「`@AeronTopic` 不写 driver 时用 `default-driver`」 | `AeronLifecycle` 在多 driver 下 `@AeronTopic` 未写 driver 直接抛异常（`AeronLifecycleTest.multiDriver_missingDriverAttribute_throws` 锁定此行为，与 `@AeronTopic` 注释一致）。**已修复**：保留代码行为，修正手册与 `AeronProperties` 注释：`default-driver` 只决定无后缀 alias |
| 3 | 手册 §16 | `StateMaterializer` 示例写 `.versionedBy(e -> e.getVersion())`，看起来是从事件取版本 | `versionedBy` 的参数是存储值 V。**已修复**：示例改为 `s -> s.getVersion()` 并注明 |
| 4 | 手册 §4.2 | 核心 SDK 依赖示例含 `runtimeOnly 'org.slf4j:slf4j-simple:2.0.13'` | Spring Boot / easyfk 项目已有 Logback，再加 slf4j-simple 会出现两个 SLF4J provider，版本也与 BOM（2.0.16）不一致。**已修复**：删除该行并加说明（#6 修复后核心 SDK 不再带日志实现，非 Spring 项目按说明自选） |
| 5 | `序列化Codec接入指南.md` §2.6.7 | 压缩示例 `producer.compression(...)`、`producer.send(topic, value, CompressionIds.LZ4)` | `compression` 只在 `AeronProducer.Builder` 上；`send` 没有按条指定压缩的重载，第三个参数会被当作 key 参与路由。**已修复**：改为 builder 写法并说明压缩是 producer 级配置 |
| 6 | `aeron-driver`、`aeron-producer` 的 `build.gradle`；手册 §1 / §4.2 | 手册称「核心 SDK 0 Spring 依赖」「starter 不向业务方传递 Spring 坐标」 | 两个模块以 `api` 依赖 `easyfk-core`，而 aeron 源码只用到其中的 slf4j（`aeron-common` / `aeron-consumer` / `aeron-store` 对 core 仅 `compileOnly`，运行期靠 driver 传递）。实际会传递 Spring Boot、Logback、Hutool、fastjson2。**已修复**：driver 改 `api slf4j-api`、producer 删除 `api easyfk-core`；`aeron-common` / `aeron-store` 由 `compileOnly easyfk-core` 改为 `api slf4j-api`（运行期原本靠 driver 传递）；删除 codec-json / protobuf / sbe 上未使用的 `compileOnly easyfk-core`；`aeron-chronicle` 的 Spring 自动装配原先靠 easyfk-core 传递编译，改为显式 `compileOnly spring-boot-autoconfigure`；手册 §4.2 日志说明同步。全部模块 `compileJava compileTestJava` 通过 |
| 7 | `跨语言互通指南.md` §1 / §6.4 | 写 Java 端依赖 Aeron `1.46.7`（`gradle/libs.versions.toml`） | 工程中没有 `libs.versions.toml`，版本在 `settings.gradle` 的 catalog **且本版本起移到 BOM**：Aeron 实际为 **1.54.2**（`aeronRuntime` bundle）。**已修复**：文档改为 1.54.2，来源写明是 BOM |
| 8 | `docs/` 各专题文档 | 链接指向已合并或不存在的文档：`发送端使用手册.md`、`接收端使用手册.md`、`Spring Boot 接入指南.md`、`分片设计.md`、`协议契约.md`、`Aeron客户端版本兼容矩阵.md` | **已修复**：改为指向《Aeron 组件使用手册》对应章节、`aeron协议说明.md` 或 `com.mcst.aeron.common.partition` 源码；没有替代文档的兼容矩阵链接改为指向 §6.4 或删除 |
| 9 | starter / store 源码注释 | 多处写「设计契约：`docs/Spring接入设计.md` §x」「`docs/aeron-store 持久化转发组件.md`」 | 这两份文档不存在。**保留**：只是注释，不影响行为；以本文与使用手册为准 |
| 10 | `settings.gradle`（aeron catalog） | 上一版 catalog 写死 `micrometer` 1.8.13（Boot 2.6 兼容基线） | 本版本已删除该写死版本，`aeron-metrics-micrometer` 用无版本坐标，跟随 Boot 3.5 的 Micrometer。**已修复** |
| 11 | `settings.gradle`、各子模块 `build.gradle` | 上一版：`aeron-all` / `agrona` / `sbe-tool` / `protobuf-java` / `lz4-java` / `zstd-jni` 版本写死在本工程 catalog，与 aeron-cluster 各写一套 | 本版本第三方运行时全部改为无版本坐标，由 BOM 的 `aeronRuntime` bundle 统一约束（1.54.2 / 2.7.1 / 1.42.0 / 4.36.2 / 1.14.0 / 1.5.7-28），两个工程共用一套版本。**已修复** |
