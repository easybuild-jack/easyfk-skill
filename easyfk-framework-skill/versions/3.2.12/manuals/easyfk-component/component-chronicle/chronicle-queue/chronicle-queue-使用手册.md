# Chronicle Queue 使用手册

本文档面向 `chronicle-queue` 组件的使用者，说明这个组件能做什么、怎么配置、各个入口类怎么用、不同场景该选哪种 API。

阅读完本文档后，开发人员应该能明确：
- 这个组件适合解决什么问题
- `ChronicleQueueTemplate`、`ChronicleQueuePublisher`、`ChronicleQueueConsumer`、`@ChronicleQueueListener` 分别负责什么
- 文本、二进制、Fory 对象、`BytesMarshallable`、`Wire` 分别怎么发送和消费
- 高频写入、持续消费、普通业务读取分别应该怎么写
- 什么场景适合使用 listener，什么场景不适合

---

## 1. 组件定位

`chronicle-queue` 是基于 [OpenHFT Chronicle Queue](https://github.com/OpenHFT/Chronicle-Queue) 封装的本地消息队列组件。

它的定位是：
- 应用内或单机内的本地高性能消息队列
- 消息可落盘、可恢复、可按消费位点继续读取
- 适合事件流、行情流、任务流、异步处理链路

它**不是**分布式 MQ，不是 Kafka、RocketMQ、RabbitMQ 的替代品。

如果你的需求是下面这些，适合用它：
- 同一个应用内不同模块之间传递消息
- 同一台机器上的持续写入和持续消费
- 需要把消息落盘到本地，应用重启后继续消费
- 对延迟比较敏感，但不要求跨机器 broker

如果你的需求是下面这些，就不适合用它：
- 跨机器分布式广播
- 多节点消费者组协调
- 完整的重试、死信、路由、延迟消息、运维控制台
- 企业级 MQ 集群治理

---

## 2. 组件特点

### 2.1 本地文件队列

消息写入本地文件，不依赖外部 broker。

优点：
- 部署简单
- 启动快
- 本地读写性能高
- 不需要额外维护 MQ 集群

### 2.2 支持消费位点

不同 `consumerId` 会维护各自的消费位置。

这意味着：
- 同一个队列可以被多个消费者分别消费
- 应用重启后，命名消费者可以继续从上次位置读取
- 可以从头开始、从末尾开始或按历史位点继续消费

### 2.3 提供两类使用方式

这个组件既考虑开发友好，也考虑性能。

对外可以理解为四种入口：
- `ChronicleQueueTemplate`：最常用，适合大多数业务代码
- `ChronicleQueuePublisher`：固定线程持续写入时使用
- `ChronicleQueueConsumer`：固定线程持续读取时使用
- `@ChronicleQueueListener`：长期后台监听消费时使用

### 2.4 支持多种消息格式

支持下面几类消息：
- `String`
- `byte[]`
- Fory 序列化对象
- `BytesMarshallable`
- `Wire`

### 2.5 适合高频写入和持续消费

这个组件适合：
- 高频写入
- 长时间持续消费
- 对时效性有要求的本地消息流

但要注意：
- 便利接口不等于最低延迟接口
- 如果业务非常关注 GC 和抖动，优先使用 `ChronicleQueuePublisher`、`ChronicleQueueConsumer`、`BytesMarshallable` 或 `Wire`

---

## 3. Maven / Gradle 引入方式

### 3.1 Maven

```xml
<dependency>
    <groupId>com.mcst</groupId>
    <artifactId>chronicle-queue</artifactId>
</dependency>
```

### 3.2 Gradle

```gradle
dependencies {
    implementation 'com.mcst:chronicle-queue'
}
```

---

## 4. Spring 自动配置

组件启用后会自动注入下面这些 Bean：
- `ChronicleQueueManager`
- `ChronicleQueueTemplate`
- `ChronicleQueueListenerRegistry`
- `ChronicleQueueListenerBeanPostProcessor`
- 默认的 `ChronicleQueueListenerErrorHandler`
- 启用 `cleanup.enabled` 后注入 `ChronicleQueueCleanupTask` 及其调度配置

普通业务代码里，通常只需要直接注入 `ChronicleQueueTemplate`：

```java
@Service
public class MarketService {

    @Resource
    private ChronicleQueueTemplate queueTemplate;
}
```

如果你需要查看或控制 listener 的运行状态，也可以直接注入 `ChronicleQueueListenerRegistry`。

---

## 5. 配置说明

### 5.1 配置前缀

```yaml
easyfk:
  config:
    storage:
      queue:
```

### 5.2 基础配置示例

```yaml
easyfk:
  config:
    storage:
      queue:
        default-path: ./chronicle-queues
        default-roll-cycle: FAST_DAILY
        default-block-size: 0
        create-directories-on-startup: true
        cleanup:
          enabled: false
          check-interval: 2h
          initial-delay: 5m
          retention: 2h
          reserve-cycles-before-head: 1
          require-listener-position: true
          # 必须确认所有外部/跨 JVM NamedTailer 均已列入保护后才允许删除。
          all-consumers-tracked: false
        listener:
          enabled: true
          default-idle-mode: PARK
          default-idle-time-ms: 10
          default-max-retries: 0
          default-retry-delay-ms: 100
          default-retry-backoff-mode: FIXED
          default-max-retry-delay-ms: 1000
          default-failure-policy: CONTINUE
          default-batch-size: 1
          default-daemon: true
```

### 5.3 配置项说明

| 配置项 | 说明 |
|---|---|
| `default-path` | 队列文件默认存放路径 |
| `default-roll-cycle` | 默认滚动周期 |
| `default-block-size` | Chronicle Queue block 大小，`0` 表示使用默认值 |
| `create-directories-on-startup` | 是否在启动阶段按预定义队列提前初始化目录和队列；关闭后不影响运行期首次使用时按配置创建 |
| `cleanup.enabled` | 是否启用位点感知的滚动文件清理，默认关闭 |
| `cleanup.check-interval` | 清理任务 fixed-delay 检查间隔 |
| `cleanup.initial-delay` | 首次清理前的等待时间 |
| `cleanup.retention` | 滚动文件最短保留时间 |
| `cleanup.reserve-cycles-before-head` | writer 当前 cycle 之前额外保留的 cycle 数 |
| `cleanup.require-listener-position` | 已知 NamedTailer 尚无有效位点时是否放弃本轮清理 |
| `cleanup.all-consumers-tracked` | 是否确认所有需保护消费者均由框架跟踪或已显式配置；默认 false，未确认时不删除 |
| `listener.enabled` | 是否启用 listener 自动启动 |
| `listener.default-idle-mode` | listener 默认空闲策略 |
| `listener.default-idle-time-ms` | listener 默认空闲等待时间 |
| `listener.default-max-retries` | listener 默认最大重试次数 |
| `listener.default-retry-delay-ms` | listener 默认重试间隔 |
| `listener.default-retry-backoff-mode` | listener 默认重试退避策略 |
| `listener.default-max-retry-delay-ms` | listener 默认最大重试等待时间 |
| `listener.default-failure-policy` | listener 默认失败策略 |
| `listener.default-batch-size` | batch listener 默认批量大小 |
| `listener.default-daemon` | listener 默认是否使用 daemon 线程 |

### 5.4 预定义队列示例

```yaml
easyfk:
  config:
    storage:
      queue:
        default-path: ./chronicle-queues
        queues:
          - queue-name: market
            path: ./chronicle-queues/market
            roll-cycle: FAST_HOURLY
            block-size: 67108864
          - queue-name: trade
            path: ./chronicle-queues/trade
            roll-cycle: FAST_DAILY
            cleanup:
              all-consumers-tracked: true
              # 保护重启后尚未重新打开，或绕过框架 API 创建的 NamedTailer。
              protected-consumer-ids:
                - trade-archive
```

### 5.5 什么时候建议预定义

建议预定义的情况：
- 生产环境
- 队列名固定
- 希望应用启动时就初始化好队列目录
- 希望不同队列有明确的路径和滚动周期

不强制预定义的情况：
- 开发环境
- 队列较少
- 接受首次写入时自动创建

补充说明：
- `create-directories-on-startup=true` 时，会在应用启动阶段按预定义队列提前初始化
- `create-directories-on-startup=false` 时，不会在启动阶段提前创建，但后续首次使用队列时仍会按预定义配置创建

---

## 6. 核心概念

### 6.1 `queueName`

队列名称。

例如：
- `market`
- `trade`
- `order`
- `risk-event`

同一个 `queueName` 表示同一个队列。

### 6.2 `consumerId`

消费者标识。

它用于区分不同消费者自己的消费进度。

例如：

```java
queueTemplate.readText("market", "consumer-a");
queueTemplate.readText("market", "consumer-b");
```

这两个消费者读取的是同一个队列，但各自维护自己的读取位置，互不影响。

### 6.3 `TailerStartStrategy`

消费者启动时的起始策略，支持：
- `START`：从头开始
- `END`：从尾部开始
- `RESUME`：从历史消费位点继续
- `RESUME_LATEST`：如果没有历史位点则从尾部开始，否则从历史位点继续

### 6.4 消息格式

当前组件支持以下几类消息读写：
- 文本：`String`
- 二进制：`byte[]`
- Fory 对象：普通 Java 对象
- `BytesMarshallable`：更适合低 GC 的对象形式
- `Wire`：原始 Chronicle 文档访问方式

---

## 7. 四种主要使用方式

## 7.1 `ChronicleQueueTemplate`

定位：
- 统一入口
- 最适合普通业务代码
- 最适合快速接入

适合场景：
- 偶发写消息
- 普通读消息
- 管理类读取
- 查看消息内容
- 批量读取少量消息

不适合场景：
- 固定线程超高频持续写入
- 一个线程长期循环消费且对时延敏感

常用方法：
- 写入：`writeText`、`writeBytes`、`writeFory`、`writeObject`、`writeDocument`
- 读取：`readText`、`readBytes`、`readFory`、`readObject`、`readDocument`
- 批量读取：`readTextBatch`、`readBytesBatch`、`readForyBatch`、`readDocumentBatch`
- 查看消息：`peekFirstText`、`peekLastText`、`peekTextAtIndex`
- 消费位置：`toStart`、`toEnd`、`moveToIndex`
- 打开长期对象：`openPublisher`、`openConsumer`、`stream`

最小示例：

```java
@Resource
private ChronicleQueueTemplate queueTemplate;

public void sendTrade() {
    queueTemplate.writeText("trade", "TRADE|20260405|000001|12.31|100");
}

public void receiveTrade() {
    String message = queueTemplate.readText("trade", "trade-consumer");
    if (message != null) {
        System.out.println("收到消息: " + message);
    }
}
```

---

## 7.2 `ChronicleQueuePublisher`

定位：
- 长生命周期生产者
- 适合固定线程持续写入

适合场景：
- 行情生产线程
- 采集线程
- 订单事件持续写入
- 高频本地消息投递

特点：
- 单个 Publisher 串行复用长期 `Appender`，可安全地被多个线程调用
- 队列重建后会自动失效并重建内部资源
- 比反复通过便利接口写入更适合长时间持续写入
- `openPublisher` / `publisher` 返回调用方持有的独立资源，使用结束必须调用 `close()`

常用方法：
- `publishText(String text)`
- `publishBytes(byte[] data)`
- `publishFory(Object value)`
- `publish(BytesMarshallable value)`
- `publishDocument(Consumer<WireOut> writer)`
- `publishKeyValue(String key, String value)`
- `lastIndex()`
- `close()`

示例：

```java
@Resource
private ChronicleQueueTemplate queueTemplate;

public void publishMarketData() {
    try (ChronicleQueuePublisher publisher = queueTemplate.openPublisher("market")) {
        while (!Thread.currentThread().isInterrupted()) {
            String line = "TICK|000001|12.31|12.32|1000";
            publisher.publishText(line);
        }
    }
}
```

二进制示例：

```java
@Resource
private ChronicleQueueTemplate queueTemplate;

public void publishBinary() {
    try (ChronicleQueuePublisher publisher = queueTemplate.openPublisher("trade")) {
        byte[] body = "TRADE|20260405|600519|1550.00|2".getBytes(StandardCharsets.UTF_8);
        publisher.publishBytes(body);
    }
}
```

---

## 7.3 `ChronicleQueueConsumer`

定位：
- 长生命周期消费者
- 适合固定线程持续读取

适合场景：
- 后台消费线程
- 行情处理线程
- 风控线程
- 持续轮询本地事件流

特点：
- 当前线程会复用长期 `Tailer`
- 支持起始策略和位点控制
- 适合持续循环读取

常用方法：
- `consumeText()`
- `consumeText(StringBuilder destination)`
- `consumeBytes()`
- `consumeBytes(byte[] buffer)` （传入自带数组，全程避免再分配）
- `consume(BytesMarshallable destination)`
- `consumeFory(Class<T> targetType)` （底层走缓存池零拷贝映射对象）
- `consumeDocument(Function<Wire, T> reader)`
- `poll(Consumer<Wire> consumer)`
- `consumeTextBatch(int maxCount)`
- `toStart()`
- `toEnd()`
- `moveToIndex(long index)`
- `index()`
- `close()`

示例：

```java
@Resource
private ChronicleQueueTemplate queueTemplate;

public void consumeTrade() {
    try (ChronicleQueueConsumer consumer = queueTemplate.openConsumer("trade", "trade-consumer")) {
        while (true) {
            String message = consumer.consumeText();
            if (message != null) {
                System.out.println("处理消息: " + message);
            }
        }
    }
}
```

从头开始消费：

```java
try (ChronicleQueueConsumer consumer = queueTemplate.openConsumer("trade", "trade-history-consumer")) {
    consumer.toStart();
    while (true) {
        String message = consumer.consumeText();
        if (message == null) {
            break;
        }
        System.out.println(message);
    }
}
```

`BytesMarshallable` 示例：

```java
public class TickMessage implements BytesMarshallable {
    private String code;
    private double price;

    @Override
    public void readMarshallable(BytesIn<?> bytes) {
        this.code = bytes.readUtf8();
        this.price = bytes.readDouble();
    }

    @Override
    public void writeMarshallable(BytesOut<?> bytes) {
        bytes.writeUtf8(code);
        bytes.writeDouble(price);
    }
}
```

```java
try (ChronicleQueueConsumer consumer = queueTemplate.openConsumer("market", "market-consumer")) {
    TickMessage message = new TickMessage();
    while (true) {
        if (consumer.consume(message)) {
            System.out.println("code=" + message.getCode() + ", price=" + message.getPrice());
        }
    }
}
```

---

## 7.4 `@ChronicleQueueListener`

定位：
- 声明式监听消费
- 适合长期后台监听任务
- 由框架内部启动线程持续拉取消息并回调业务方法

要点：
- 它不是 broker 主动推送
- 本质上仍然是框架内部长期 `poll`
- 一个 listener 对应一个长期消费线程
- 同一个 `queue + consumerId` 不能重复注册 listener

适合场景：
- 应用启动后一直监听某个本地队列
- 风控、行情、异步任务等长期后台消费
- 希望用注解方式声明消费者

不适合场景：
- 偶尔读一条消息看看
- 请求进来时临时消费
- 管理后台查询队列内容
- 一次性补偿脚本

### 7.4.1 注解参数

| 参数 | 说明 |
|---|---|
| `queue` | 队列名称，必填 |
| `consumerId` | 消费者标识（必填，持久化位点的 NamedTailer ID），留空时启动报错 |
| `format` | 消息格式，默认 `AUTO` |
| `startStrategy` | 启动时消费起点，默认 `RESUME` |
| `idleMode` | 空闲等待策略，未配置时使用全局默认，默认值为 `PARK` |
| `idleTimeMs` | 空闲等待时长，未配置时使用全局默认，默认值为 `10` 毫秒；`PARK` 和 `SLEEP` 模式建议配置为大于 `0` 的值 |
| `threadName` | 监听线程名，留空时框架自动生成 |
| `daemonMode` | 线程类型，未配置时使用全局默认；当前全局默认是 daemon 线程 |
| `maxRetries` | 单条消息失败后的最大重试次数，未配置时使用全局默认，默认值为 `0` |
| `retryDelayMs` | 重试间隔，未配置时使用全局默认，默认值为 `100` 毫秒 |
| `retryBackoffMode` | 重试退避策略，未配置时使用全局默认，默认值为 `FIXED` |
| `maxRetryDelayMs` | 重试等待时间最大值，未配置时使用全局默认，默认值为 `1000` 毫秒 |
| `errorQueue` | 失败消息转发的目标队列，默认不转发 |
| `failurePolicy` | 失败后策略，未配置时使用全局默认，默认值为 `CONTINUE` |
| `batchSize` | 批量监听时一次拉取的消息数量，未配置时使用全局默认，默认值为 `1` |

`failurePolicy` 说明：
- `CONTINUE`：记录失败后继续消费后续消息
- `STOP`：记录失败后停止当前 listener

`retryBackoffMode` 说明：
- `FIXED`：固定间隔重试
- `LINEAR`：按线性递增等待时间重试
- `EXPONENTIAL`：按指数递增等待时间重试

`daemonMode` 说明：
- `DEFAULT`：使用全局默认配置
- `DAEMON`：使用 daemon 线程
- `USER_THREAD`：使用普通用户线程

### 7.4.2 listener 内部执行链路

listener 现在内部已经拆成几层职责，目的是把注册逻辑和运行逻辑分开，降低维护复杂度。

大致调用链如下：

- `ChronicleQueueListenerBeanPostProcessor`：扫描 `@ChronicleQueueListener`
- `ChronicleQueueListenerRegistry`：负责注册、启停、状态和指标管理
- `ChronicleQueueListenerEndpointResolver`：负责把注解和监听方法解析成运行时 endpoint，并合并全局默认配置
- `ChronicleQueueListenerContainer`：负责线程生命周期、状态流转、空闲等待
- `ChronicleQueueListenerMessageDispatcher`：负责按消息格式分发、批量处理、重试和错误转发

这些都是组件内部实现细节。业务开发时通常只需要关注：

- 注解参数怎么写
- 监听方法参数怎么声明
- 失败策略和空闲策略怎么配置
- 需要时通过 `ChronicleQueueListenerRegistry` 查看状态或控制启停

### 7.4.3 默认 `idleMode` 为什么是 `PARK`

现在 listener 默认使用 `PARK`，不是 `YIELD`。

原因是：
- `listener` 更适合长期后台监听
- 对普通业务来说，默认 `PARK` 更稳妥
- 没消息时不会一直空转抢占 CPU

补充说明：
- 如果显式使用 `PARK` 或 `SLEEP`，建议把 `idleTimeMs` 配成大于 `0` 的值
- `SLEEP` 且 `idleTimeMs=0` 不适合作为业务配置

如果你的场景是高频低延迟消费，可以显式改成：
- `YIELD`
- `BUSY_SPIN`

但这应该由明确的性能场景决定，不建议作为默认值。

### 7.4.4 失败处理、重试和错误队列

listener 现在支持基础失败处理能力：

- 单条消息可配置立即重试
- 重试耗尽后可继续消费后续消息
- 重试耗尽后可停止当前 listener
- 重试耗尽后可把失败消息封装后转发到另一个队列
- 支持固定、线性、指数三种退避策略

需要注意：

- 这里的重试是“当前 listener 线程内立即重试”
- 它不会回滚 Chronicle Queue 的消费位点
- 也不是 MQ 意义上的 ack / nack

也就是说，一条消息被读出来后，如果监听方法失败，框架只能在内存里对这条消息再执行几次监听逻辑，而不是把队列位置退回去重新消费。

如果配置了 `errorQueue`，写入错误队列的不是原始消息裸数据，而是一个结构化对象 `ChronicleQueueListenerErrorMessage`，其中包含：

- 原始队列名
- `consumerId`
- 监听方法签名
- 消息格式
- 是否批量监听
- 批量大小
- 原始 payload
- 错误信息
- 堆栈信息
- 失败时间

### 7.4.5 自动推断消息类型

当 `format=AUTO` 时，框架会按方法参数自动判断：
- `String` -> 文本消息
- `byte[]` -> 二进制消息
- `BytesMarshallable` -> `MARSHALLABLE`
- `Wire` -> `WIRE`
- 其他普通对象 -> `FORY`

### 7.4.6 文本监听示例

```java
@Component
public class TradeTextListener {

    @ChronicleQueueListener(queue = "trade", consumerId = "trade-text-listener")
    public void onMessage(String message) {
        System.out.println("收到交易消息: " + message);
    }
}
```

### 7.4.7 二进制监听示例

```java
@Component
public class TradeBytesListener {

    @ChronicleQueueListener(queue = "trade-bytes", consumerId = "trade-bytes-listener")
    public void onMessage(byte[] body) {
        String text = new String(body, StandardCharsets.UTF_8);
        System.out.println("收到二进制消息: " + text);
    }
}
```

### 7.4.8 Fory 对象监听示例

```java
@Data
public class TradeMessage {
    private String symbol;
    private double price;
    private int quantity;
}
```

```java
@Component
public class TradeObjectListener {

    @ChronicleQueueListener(queue = "trade-object", consumerId = "trade-object-listener")
    public void onMessage(TradeMessage message) {
        System.out.println(message.getSymbol() + ":" + message.getPrice());
    }
}
```

### 7.4.9 `BytesMarshallable` 监听示例

注意：监听参数类型需要有无参构造器。

```java
public class TickMessage implements BytesMarshallable {
    private String code;
    private double price;

    public TickMessage() {
    }

    @Override
    public void readMarshallable(BytesIn<?> bytes) {
        this.code = bytes.readUtf8();
        this.price = bytes.readDouble();
    }

    @Override
    public void writeMarshallable(BytesOut<?> bytes) {
        bytes.writeUtf8(code);
        bytes.writeDouble(price);
    }
}
```

```java
@Component
public class TickListener {

    @ChronicleQueueListener(queue = "market", consumerId = "market-listener")
    public void onMessage(TickMessage message) {
        System.out.println(message.getCode() + ":" + message.getPrice());
    }
}
```

### 7.4.10 配置重试和失败停止示例

```java
@Component
public class RiskEventListener {

    @ChronicleQueueListener(
            queue = "risk-event",
            consumerId = "risk-listener",
            maxRetries = 3,
            retryDelayMs = 50,
            failurePolicy = ChronicleQueueListenerFailurePolicy.STOP
    )
    public void onMessage(String message) {
        System.out.println("处理风控消息: " + message);
    }
}
```

### 7.4.11 配置批量监听示例

批量监听方法需要声明为 `List<T>` 参数，同时通过 `batchSize` 指定一次拉取多少条消息。

```java
@Component
public class TradeBatchListener {

    @ChronicleQueueListener(
            queue = "trade-text",
            consumerId = "trade-batch-listener",
            batchSize = 20
    )
    public void onMessage(List<String> messages) {
        System.out.println("本次收到 " + messages.size() + " 条交易消息");
    }
}
```

目前批量监听支持：

- `List<String>`
- `List<byte[]>`
- `List<普通 Fory 对象>`
- `List<BytesMarshallable>`
- `List<Wire>`

### 7.4.12 配置错误队列示例

```java
@Component
public class TradeObjectListener {

    @ChronicleQueueListener(
            queue = "trade-object",
            consumerId = "trade-object-listener",
            errorQueue = "trade-object-error",
            maxRetries = 2
    )
    public void onMessage(TradeMessage message) {
        System.out.println(message.getSymbol());
    }
}
```

说明：

- 错误队列里写入的是 `ChronicleQueueListenerErrorMessage`
- 其中的 `payload` 字段保存失败时的原始消息或批量消息
- `WIRE` 监听失败时，`payload` 保存的是原始字节快照，不是活的 `Wire` 对象

### 7.4.13 调整 listener 空闲策略示例

```java
@Component
public class MarketFastListener {

    @ChronicleQueueListener(
            queue = "market-fast",
            consumerId = "market-fast-listener",
            idleMode = ChronicleQueueListenerIdleMode.YIELD,
            startStrategy = TailerStartStrategy.RESUME_LATEST
    )
    public void onMessage(String message) {
        System.out.println(message);
    }
}
```

### 7.4.14 listener 状态查询与控制

`ChronicleQueueListenerRegistry` 提供了基础的 listener 管理能力：

- `getListenerStatuses()`
- `getListenerStatus(queueName, consumerId)`
- `getListenerMetrics()`
- `getQueueListenerMetrics()`
- `getQueueListenerMetrics(queueName)`
- `pause(queueName, consumerId)`
- `resume(queueName, consumerId)`
- `stop(queueName, consumerId)`
- `start(queueName, consumerId)`

状态信息里现在包含：

- 当前状态
- 已消费数量
- 重试次数
- 错误次数
- 最后一次消费时间
- 最后一次错误时间
- 最后一次错误信息

`getListenerMetrics()` 返回聚合指标，包括：

- listener 总数
- 各状态 listener 数量
- 累计消费总数
- 累计重试总数
- 累计错误总数

`getQueueListenerMetrics()` 返回按队列聚合的监听指标，包括：

- 每个队列的 listener 数量
- 每个队列正在运行、暂停、失败的 listener 数量
- 每个队列累计消费数、重试数、错误数

`state` 常见值说明：
- `NEW`：已创建但未启动
- `STARTING`：正在启动
- `RUNNING`：运行中
- `PAUSED`：已暂停
- `STOPPED`：已停止
- `FAILED`：因异常进入失败状态

示例：

```java
@Service
public class ListenerAdminService {

    @Resource
    private ChronicleQueueListenerRegistry listenerRegistry;

    public void pauseRiskListener() {
        listenerRegistry.pause("risk-event", "risk-listener");
    }

    public void printStatuses() {
        for (ChronicleQueueListenerStatus status : listenerRegistry.getListenerStatuses()) {
            System.out.println(status.queueName() + " -> " + status.state());
        }
    }
}
```

---

## 8. `ChronicleQueueTemplate` 主要 API 说明

下面按功能说明模板类里最常用的方法。

### 8.1 写入相关

#### `writeText(String queueName, String text)`
写入一条文本消息。

```java
queueTemplate.writeText("trade", "TRADE|000001|12.31|100");
```

#### `writeBytes(String queueName, byte[] data)`
写入一条二进制消息。

```java
queueTemplate.writeBytes("trade", "TRADE|000001|12.31|100".getBytes(StandardCharsets.UTF_8));
```

#### `writeFory(String queueName, Object value)`
使用 Fory 序列化写入对象。

```java
TradeMessage message = new TradeMessage();
message.setSymbol("000001");
message.setPrice(12.31);
message.setQuantity(100);
queueTemplate.writeFory("trade-object", message);
```

#### `writeObject(String queueName, BytesMarshallable value)`
写入 `BytesMarshallable` 对象。

```java
TickMessage tick = new TickMessage();
queueTemplate.writeObject("market", tick);
```

#### `writeDocument(String queueName, Consumer<WireOut> writer)`
使用 `WireOut` 自定义写入内容。

```java
queueTemplate.writeDocument("market", wire -> {
    wire.write("code").text("000001");
    wire.write("price").float64(12.31);
});
```

### 8.2 读取相关

#### `readText(String queueName, String consumerId)`
读取一条文本消息。

```java
String text = queueTemplate.readText("trade", "trade-consumer");
```

#### `readBytes(String queueName, String consumerId)`
读取一条二进制消息。

```java
byte[] body = queueTemplate.readBytes("trade", "trade-consumer");
```

#### `readFory(String queueName, String consumerId, Class<T> targetType)`
按 Fory 反序列化读取对象。

```java
TradeMessage message = queueTemplate.readFory("trade-object", "trade-object-consumer", TradeMessage.class);
```

#### `readObject(String queueName, String consumerId, BytesMarshallable destination)`
读取 `BytesMarshallable` 到现有对象。

```java
TickMessage tick = new TickMessage();
boolean success = queueTemplate.readObject("market", "market-consumer", tick);
```

#### `readDocument(String queueName, String consumerId, Function<Wire, T> reader)`
按 `Wire` 自定义读取。

```java
String line = queueTemplate.readDocument("market", "market-consumer", wire -> {
    String code = wire.read("code").text();
    double price = wire.read("price").float64();
    return code + ":" + price;
});
```

### 8.3 批量读取

批量接口适合一次取少量消息，不适合代替长期消费线程。

- `readTextBatch`
- `readBytesBatch`
- `readForyBatch`
- `readDocumentBatch`

示例：

```java
List<String> messages = queueTemplate.readTextBatch("trade", "trade-batch-consumer", 10);
for (String message : messages) {
    System.out.println(message);
}
```

### 8.4 查看消息但不建议用于持续消费

- `peekFirstText`
- `peekLastText`
- `peekTextAtIndex`
- `peekFirstBytes`
- `peekLastBytes`
- `peekBytesAtIndex`
- `peekFirstFory`
- `peekLastFory`
- `peekForyAtIndex`

这些方法适合：
- 调试
- 管理后台查看
- 人工排查

不适合：
- 高频消费链路
- 长循环消费线程

### 8.5 消费位点控制

- `toStart(queueName, consumerId)`
- `toEnd(queueName, consumerId)`
- `moveToIndex(queueName, consumerId, index)`
- `getTailerIndex(queueName, consumerId)`

示例：

```java
queueTemplate.toStart("trade", "trade-replay-consumer");
String first = queueTemplate.readText("trade", "trade-replay-consumer");
```

### 8.6 打开长期对象

- `openPublisher(queueName)`
- `publisher(queueName)`
- `openConsumer(queueName, consumerId)`
- `openConsumer(queueName)`
- `stream(queueName, consumerId)`

说明：
- `publisher(queueName)` 和 `openPublisher(queueName)` 语义相同
- `stream(queueName, consumerId)` 本质上就是打开一个长期 `Consumer`
- 这些方法返回的对象都由调用方负责关闭，推荐使用 try-with-resources
- 同一个 `consumerId` 不得由多个 `Consumer` 并发消费；共享消费请使用 Template 的 `read*` 方法或 Listener
- 直接 `createTailer(queueName, consumerId)` 已禁用；NamedTailer 必须通过 `openConsumer` 管理所有权和释放

---

## 9. 发送端和消费端的推荐写法

## 9.1 普通业务写入

优先：`ChronicleQueueTemplate`

```java
queueTemplate.writeText("notice", "系统启动完成");
```

## 9.2 高频持续写入

优先：`ChronicleQueuePublisher`

```java
ChronicleQueuePublisher publisher = queueTemplate.openPublisher("market");
while (true) {
    publisher.publishText("TICK|000001|12.31|1000");
}
```

## 9.3 普通业务读取

优先：`ChronicleQueueTemplate`

```java
String message = queueTemplate.readText("notice", "notice-consumer");
```

## 9.4 固定线程持续读取

优先：`ChronicleQueueConsumer`

```java
try (ChronicleQueueConsumer consumer = queueTemplate.openConsumer("market", "market-consumer")) {
    while (true) {
        String message = consumer.consumeText();
        if (message != null) {
            System.out.println(message);
        }
    }
}
```

## 9.5 后台监听消费

优先：`@ChronicleQueueListener`

```java
@Component
public class RiskListener {

    @ChronicleQueueListener(queue = "risk-event", consumerId = "risk-listener")
    public void onMessage(String message) {
        System.out.println("处理风控事件: " + message);
    }
}
```

---

## 10. listener 使用建议

这一节很重要。

### 10.1 listener 适合什么

适合：
- 应用启动后长期监听某个队列
- 独立后台线程持续处理消息
- 声明式消费比手写循环更方便的场景

### 10.2 listener 不适合什么

不适合：
- 只想偶尔读一条消息
- Web 请求里临时消费
- 管理后台查看消息
- 一次性补偿代码
- 低频业务却给每个小功能都开一个监听线程

### 10.3 为什么不能无脑用 listener

因为 listener 本质上是：
- 一个长期线程
- 一个长期 consumer
- 持续轮询队列

如果所有业务都无脑使用 listener，会带来：
- 后台线程越来越多
- 没消息时也会持续空转或等待
- 消费者语义容易混乱
- 排查问题更复杂

所以建议规则很简单：
- 持续后台消费：用 listener
- 普通读写：用 template
- 固定线程高频写：用 publisher
- 固定线程高频读：用 consumer

另外建议：
- 同一个 `queue` 下不要让多个 listener 共用同一个 `consumerId`
- 如果需要暂停某个监听器，优先通过 `ChronicleQueueListenerRegistry` 控制，不要直接杀线程

---

## 11. 性能建议

### 11.1 如果只是普通业务

直接用 `ChronicleQueueTemplate` 即可。

### 11.2 如果业务对延迟比较敏感

优先考虑：
- `ChronicleQueuePublisher`
- `ChronicleQueueConsumer`
- `BytesMarshallable`
- `Wire`

### 11.3 如果业务对 GC 比较敏感

优先考虑：
- `BytesMarshallable`
- 直接使用 Fory 序列化（底层已全量替换为 `ThreadLocal<MemoryBuffer>` 零拷贝技术，能够以近乎无 GC 的代价自动转化复杂对象）
- 使用预分配的可重用数组（调用带复用池的方法如 `consumeBytes(byte[] buffer)`）
- 避免热点路径频繁使用大体积的零散 `String` 拼接与分配

### 11.4 关于 `readBytes(..., byte[] buffer)`

这个接口的语义是“把消息读到调用方提供的 buffer 中”。

它适合：
- 兼容现有 `byte[]` 处理逻辑
- 由调用方管理接收缓冲区以彻底消除数组的动态二次分配

因为该方法在底层已经改为**完全的防范性零对象拷贝映射**（不再中转分配任何底层缓冲），所以如果你需要纯粹提取二进制包，它现在和 `BytesMarshallable` 一样达到了极限的低分配开销效果。

---

## 12. 常见问题

### 12.1 同一个队列可以有多个消费者吗

可以。

不同 `consumerId` 会维护各自的消费位置。

### 12.2 同一个 `consumerId` 可以被多个线程同时用吗

不建议。

更稳妥的做法是：
- 一个长期消费线程使用一个 `consumerId`
- 一个固定写入线程使用一个 `Publisher`

### 12.3 listener 是不是和 RocketMQ 一样的推送模型

不是。

它只是使用上类似“监听器”。本质还是框架内部长期拉取消息后回调业务方法。

### 12.4 为什么没有单独的 provider

当前项目已经有 `ChronicleQueuePublisher` 作为生产者能力入口。

如果再平行加一个 `provider` 概念，容易和 `publisher` 重复，增加使用成本。所以当前推荐直接把 `Publisher` 理解成发送端生产者。

---

## 13. 选型建议

如果你只想快速上手：
- 默认先用 `ChronicleQueueTemplate`

如果你是固定线程持续写入：
- 用 `ChronicleQueuePublisher`

如果你是固定线程持续读取：
- 用 `ChronicleQueueConsumer`

如果你要声明式后台监听：
- 用 `@ChronicleQueueListener`

如果你非常关心低延迟和 GC：
- 优先 `Publisher + Consumer`
- 优先 `BytesMarshallable` 或 `Wire`
- 不要把 listener 当成所有消费场景的默认入口

---

## 14. 一页总结

- `ChronicleQueueTemplate`：默认入口，最简单
- `ChronicleQueuePublisher`：固定线程持续写入
- `ChronicleQueueConsumer`：固定线程持续消费
- `@ChronicleQueueListener`：声明式长期后台监听
- `String` / `byte[]` / Fory：方便
- `BytesMarshallable` / `Wire`：更适合性能敏感场景
- listener 默认 `idleMode=PARK`，适合普通后台监听，不会默认激进抢 CPU

