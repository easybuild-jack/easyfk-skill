# easyfk-component-mq Skill 参考文档

> 模块：`easyfk-component/component-mq`（mq-common / mq-rocket / mq-rabbit / mq-kafka）
> 坐标：`com.mcst:mq-rocket` / `com.mcst:mq-rabbit` / `com.mcst:mq-kafka`（均已传递 `mq-common` 与 `easyfk-core`；版本由 easyfk-dependencies 管理）
> 依据：各子模块源码 + `mq-rocket开发手册.md`、`RocketMQ使用教程.md`、`mq-rabbit开发手册.md`、`mq-rabbit技术特点.md`、`RabbitMQ使用教程.md`、`mq-kafka使用教程.md`、`mq-kafka技术特点.md`
> 文档与源码不一致时 **以源码为准**，差异见文末「复查记录」。

---

## 1. 模块定位

| 子模块 | 底层 | 作用 |
|---|---|---|
| mq-common | protobuf-java 4.36.2 | 统一消息模型 `CommonMessage<T>` / `ProtobufMessage<T>`、`MessageBuilder`、`ProtobufUtils`、消息头常量 |
| mq-rocket | rocketmq-spring-boot-starter 2.3.6 | `RocketProducer`（普通/延迟/顺序，同步/异步），消费直接用 `@RocketMQMessageListener` |
| mq-rabbit | spring-boot-starter-amqp | `RabbitProducer`（topic→exchange，key/tags→routingKey，延迟插件），JSON 转换器，消费用 `@RabbitListener` |
| mq-kafka | spring-kafka + kafka-streams（版本由 Boot 3.5.16 管理）+ serializer-fory | `KafkaProducer`（String/byte[]/Protobuf 三通道）、多数据源 Bean 注册、`AbstractKafkaPartitionConsumer`、Kafka Streams 支持 |

三种 MQ **只封装了发送端**，消费端都使用原生注解（Kafka 额外提供分区并行消费模板）。

---

## 2. mq-common：统一消息模型

### 2.1 BaseMessage 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| topic | String | 只有 `@NotBlank`（无长度、字符限制，`order-topic` 合法）。Rocket/Kafka Producer 发送前调用 `MessageCheckUtil.checkTopic`，message 为 null 或 topic 空白时抛 `IllegalArgumentException`；Rabbit 的 topic 可为空（回退默认 exchange，见 4.2） |
| delayTime | Long | 延迟毫秒；Rocket/Rabbit 生效，**Kafka 忽略** |
| sendTimestamp | Long | 为空时自动取当前时间（Rocket/Rabbit 回写到消息对象，Kafka 不回写） |
| messageId | String | 为空时自动生成雪花 ID 并回写到消息对象 |
| messageKey | String | Rocket=顺序 hashKey + 消息 KEYS；Rabbit=routingKey；Kafka=record key |
| tags | String | Rocket=`topic:tags`；Rabbit=routingKey 备选 + header；Kafka=header |
| partition | Integer | **仅 Kafka** |
| properties | Map<String,String> | 自定义头，三种 MQ 的所有发送方式都会发送（Rocket=用户属性，Rabbit/Kafka=header）；null 键/值跳过 |

`CommonMessage<T>`、`ProtobufMessage<T extends com.google.protobuf.Message>` 各增加一个 `data` 字段。

### 2.2 MessageBuilder

```java
CommonMessage<OrderDTO> msg = MessageBuilder.create()
        .topic("order_topic")
        .messageKey(orderId)
        .tags("CREATED")
        .delayTime(30_000L)
        .property("source", "web")
        .buildCommonMessage(orderDTO);
ProtobufMessage<OrderProto> pm = MessageBuilder.create().topic("quote_topic").partition(2).buildProtobufMessage(proto);
```
- 可用方法：`topic / delayTime / sendTimestamp / messageId / messageKey / tags / partition / property / properties / buildCommonMessage / buildProtobufMessage`（`partition` 仅 Kafka 生效）。

### 2.3 其他
- `ProtobufUtils.serialize(msg)` / `deserialize(bytes, Clazz.class)`（反射调用 `parseFrom`）/ `toJSONString(msg)`。
- `MessageCheckUtil.checkMessage(msg)` / `checkTopic(msg)`：Producer 使用的发送前校验，失败抛 `IllegalArgumentException`。
- `MessageHeaderConstants`：`MESSAGE_ID="messageId"`、`SEND_TIMESTAMP="sendTimestamp"`、`TAGS="tags"`。
- `MqTypeEnums`：`ROCKET`、`RABBIT`、`KAFKA`，框架内未使用。
- mq-common 本身没有自动配置（也没有 imports 文件）。

---

## 3. mq-rocket

### 3.1 配置

```yaml
easyfk:
  config:
    mq:
      rocket:
        enable-rocket: true        # 必须，RocketMqConfig 的开关
rocketmq:
  name-server: 192.168.1.100:9876;192.168.1.101:9876
  producer:
    group: order-producer-group   # 必填，否则 starter 不创建 RocketMQTemplate
    send-message-timeout: 3000
    retry-times-when-send-failed: 2
```
- `RocketMqConfig`（`@AutoConfiguration`，`@Import(RocketMQAutoConfiguration)`）注册 `RocketProducer`、`RocketProducerHelper`（均 `@ConditionalOnMissingBean`）。
- 属性类 `RocketMqProperties`（`easyfk.config.mq.rocket`，只有 `enableRocket` 字段），由 `RocketMqConfig` 通过 `@EnableConfigurationProperties` 注册，可注入使用。

### 3.2 RocketProducer 发送规则

`SendResult syncSendMessage(CommonMessage<T>)` / `void asyncSendMessage(CommonMessage<T>)`：
1. 先校验 message 非 null、topic 非空白，否则抛 `IllegalArgumentException`；destination = `topic`，tags 非空时为 `topic:tags`。
2. 优先级：`delayTime > 0` → 延迟消息；否则 `messageKey` 非空 → 顺序消息（`syncSendOrderly/asyncSendOrderly`，messageKey 作 hashKey）；否则普通消息。
3. 头：`messageId`（为空自动雪花并回写）、`sendTimestamp`（为空取当前时间并回写）、全部 `properties`（作为用户属性，null 键/值跳过）；`messageKey` 同时设置为 RocketMQ `KEYS`（控制台可按 Key 查询）。
4. 异步延迟消息真正异步：转换为原生消息后 `setDelayTimeMs` 并通过 `producer.send(msg, callback)` 发送。
5. 同时设置 delayTime 和 messageKey 时只按延迟处理（messageKey 只作 KEYS），顺序性失效。
6. 同步发送返回 `SendResult`：无返回结果时抛 `MessagingException`，状态非 `SEND_OK`（刷盘/从节点超时等）记 WARN 并原样返回，由调用方决定是否重试；异步结果只记日志（非 SEND_OK 为 WARN，异常为 ERROR）。
7. 任意毫秒延迟需要 RocketMQ 5.x Broker 的定时消息能力。

`RocketProducerHelper`（底层）：`SendResult syncSendMessage(topic, Message)`、`asyncSendMessage`、`SendResult sendDelayMessage(topic, msg, delayMs)`、`asyncSendDelayMessage(topic, msg, delayMs)`、`SendResult syncSendOrderlyMessage(topic, msg, hashKey)`、`asyncSendOrderlyMessage`。

### 3.3 消费

```java
@Component
@RocketMQMessageListener(topic = "order_topic", consumerGroup = "order_consumer_group",
        selectorExpression = "CREATED || PAID", consumeMode = ConsumeMode.ORDERLY)
public class OrderConsumer implements RocketMQListener<MessageExt> {
    @Override
    public void onMessage(MessageExt ext) {
        String messageId = RocketMessageUtil.getMessageId(ext);              // 用户属性 messageId（非 Broker msgId）
        Long ts = RocketMessageUtil.getSendTimestamp(ext);
        String source = RocketMessageUtil.getHeaderValue(ext, "source", String.class);   // properties
        String key = RocketMessageUtil.getKeys(ext);                         // messageKey
        OrderDTO order = RocketMessageUtil.getBody(ext, OrderDTO.class);     // JSON 体，String.class 原样返回
    }
}
```
- 需要头信息时用 `RocketMQListener<MessageExt>`；只要消息体时用 `RocketMQListener<OrderDTO>`。**不要**用 `RocketMQListener<Message<OrderDTO>>`（starter 会把 `Message` 当作消息体反序列化目标）。
- `RocketMessageUtil`（MessageExt 版）：`getHeaderValue(ext, key, clazz)`（先取用户属性，`KEYS`/`TAGS` 取系统属性；支持 String/Long/Integer/Boolean 转换，失败返回 null）、`getMessageId`、`getSendTimestamp`、`getKeys`、`getTags`、`getBodyAsString`（UTF-8）、`getBody(ext, clazz)`（fastjson2）。`getHeaderValue(Message<?>, key, clazz)` 仍保留，仅用于 Spring `Message`。
- 消费端必须幂等（at-least-once）。

---

## 4. mq-rabbit

### 4.1 配置

```yaml
easyfk:
  config:
    mq:
      rabbit:
        enable-rabbit: true                  # 必须
        exchange: easyfk.direct.exchange     # topic 为空时才使用
        delay-exchange: easyfk.delay.exchange
        confirm-callback: false              # true 时为 Boot 的 RabbitTemplate 设置 ConfirmCallback（记录日志）
        return-callback: false               # true 时设置 ReturnsCallback 并强制 mandatory=true
        async:                               # 异步发送专用线程池
          core-pool-size: 2
          max-pool-size: 8
          queue-capacity: 10000              # 满了由调用线程同步发送（背压，不丢）
          keep-alive-seconds: 60
          await-termination-seconds: 30      # 关闭时等待已提交任务发送完成
spring:
  rabbitmq:
    host: 127.0.0.1
    port: 5672
    username: guest
    password: guest
    publisher-confirm-type: correlated       # 需要 confirm 时
    publisher-returns: true                  # 需要 return 回调时
```
- `RabbitMqConfig`（`@Import(RabbitAutoConfiguration)`）注册 `Jackson2JsonMessageConverter`（Bean 名 `jsonMessageConverter`，`@ConditionalOnMissingBean`，Boot 的 `RabbitTemplate` 自动使用它）、`RabbitTemplateCustomizer`（配置回调，作用于 Boot 创建的 `rabbitTemplate`）、`RabbitProducer`、`RabbitProducerHelper`（均 `@ConditionalOnMissingBean`）。
- 组件**不声明** Exchange/Queue/Binding，需要业务自行 `@Bean` 声明或在 `@RabbitListener(bindings=...)` 中声明；延迟交换机需声明为 `x-delayed-message` 类型（`x-delayed-type` 参数）并安装 `rabbitmq_delayed_message_exchange` 插件。

### 4.2 RabbitProducer 发送规则

`void syncSendMessage(CommonMessage<T>)` / `CompletableFuture<Void> asyncSendMessage(CommonMessage<T>)`：
- data 无类型约束（不要求 `Serializable`），序列化用 JSON 转换器。
- message 为 null 抛 `IllegalArgumentException`。
- exchange：`delayTime > 0` 时用 `delay-exchange`（**忽略 topic**）；否则 topic 非空白用 topic，否则用 `exchange` 配置；最终 exchange 为 null 时抛 `IllegalArgumentException`（`exchange: ""` 表示 AMQP 默认交换机，routingKey 即队列名）。
- routingKey：`messageKey` > `tags` > `""`。
- 同步/异步、普通/延迟**所有路径**都设置 AMQP `messageId`、`timestamp`，header 写入 `messageId`、`sendTimestamp`、`tags` 和全部 `properties`；为空的 messageId/sendTimestamp 会回写到 commonMessage。
- 异步发送在 `RabbitProducerHelper` 独占的有界线程池（`easyfk.config.mq.rabbit.async.*`，线程名 `easyfk-rabbit-async-N`）中执行，队列满由调用线程同步执行；返回的 Future 在发送失败时异常完成（同时记 ERROR 日志）；Bean 销毁时等待已提交任务完成（超时后丢弃剩余并告警）。线程池不注册为 Bean，不影响 Boot 的 `applicationTaskExecutor`。

`RabbitProducerHelper`（底层）：`syncSendMessage(ex, rk, obj[, CorrelationData])`、`CompletableFuture<Void> asyncSendMessage(ex, rk, obj[, MessageProperties])`、`sendDelayMessage(ex, rk, obj, delayMs[, MessageProperties])`（`setDelayLong`）、`CompletableFuture<Void> asyncSendDelayMessage(...)`、`sendMessageWithProperties(ex, rk, obj, MessageProperties)`（只复制 messageId/timestamp/headers）、`sendRawMessage(ex, rk, Message)`。

### 4.3 消费

```java
@RabbitListener(bindings = @QueueBinding(
        value = @Queue(value = "order.queue", durable = "true"),
        exchange = @Exchange(value = "order_exchange", type = ExchangeTypes.DIRECT),
        key = "order.create"))
public void onOrder(OrderDTO order, Message raw) {
    String messageId = RabbitMessageUtil.getMessageId(raw);
    Long ts = RabbitMessageUtil.getHeaderValue(raw, "sendTimestamp", Long.class);
}
```
- `RabbitMessageUtil`：`getHeaderValue`（支持 String/Long/Integer 转换）、`getMessageId`、`getTimestamp`、`getBody`、`getBodyAsString`（平台默认字符集）。
- 所有发送路径都带 messageId/sendTimestamp/tags/properties 头，延迟消息与异步消息同样可读取。

---

## 5. mq-kafka

### 5.1 开关与数据源

```yaml
easyfk:
  config:
    mq:
      kafka:
        enable-kafka: true                 # 必须；KafkaDatasourceBeanRegistrar 与 KafkaMqConfig 都以此为条件
        primary-datasource: default        # 默认 default
        datasources:                       # 不配置时用 spring.kafka.bootstrap-servers 构造名为 primary-datasource 的数据源
          default:
            bootstrap-servers: 127.0.0.1:9092
            producer: { acks: all, retries: 3, compression-type: snappy }
            consumer: { group-id: order-group, ack-mode: manual, concurrency: 3, auto-offset-reset: earliest }
            properties: { security.protocol: SASL_PLAINTEXT }   # 生产/消费共用的原生配置
          report:
            bootstrap-servers: 10.0.0.2:9092
        enable-streams: false
```
- 数据源名不是 `default` 且 `primary-datasource` 保持默认时，取第一个数据源为主；`primary-datasource` 显式指定却不存在时启动报错。数据源未配置 `bootstrap-servers` 时回退 `spring.kafka.bootstrap-servers`。
- 单数据源兼容模式（未配置 `datasources`）：用 `spring.kafka.bootstrap-servers` 构造数据源，`spring.kafka.properties.*` 作为该数据源的 `properties`。
- 生产者默认：`acks=all`、`retries=3`、`batch-size=16384`、`linger-ms=5`、`enable-idempotence=true`、`max-in-flight=5`、`compression-type=snappy`、`request-timeout=30000`、`delivery-timeout=120000`。
- 消费者默认：`auto-offset-reset=earliest`、**`enable-auto-commit=false`**、`max-poll-records=500`、`group-id=default-group`、`isolation-level=read_committed`、`concurrency=3`、**`ack-mode=batch`**（容器在每批消息处理完成后提交 offset，at-least-once）。
- 每项取值顺序：`datasources.<name>.producer/consumer.*` → Spring Boot **标准键**（按 Boot 类型解析，支持 `5s`、`64KB` 等写法）→ 内置默认；之后 `datasources.<name>.properties`、`producer/consumer.properties` 覆盖。读取的 Boot 键只有：`spring.kafka.producer.acks/retries/batch-size/buffer-memory/compression-type`、`spring.kafka.consumer.group-id/auto-offset-reset/enable-auto-commit/max-poll-records/heartbeat-interval/fetch-min-size/fetch-max-wait/auto-commit-interval/isolation-level`、`spring.kafka.listener.concurrency/ack-mode`。
- easyfk 扩展项（`linger-ms`、`enable-idempotence`、`max-in-flight-requests-per-connection`、`request-timeout-ms`、`delivery-timeout-ms`、`session-timeout-ms`、`max-poll-interval-ms`、`concurrency`、`ack-mode` 等）**只能**写在 `easyfk.config.mq.kafka.datasources.<name>.producer/consumer` 下；`spring.kafka.consumer.concurrency/ack-mode` 等非 Boot 键不再读取。
- **key/value 序列化器按通道固定（设计如此）**：String 通道 key/value=String，Byte/Protobuf 通道 key=String、value=byte[]；在所有配置之后写入，`key-serializer`/`value-serializer`/`*-deserializer` 及 `properties` 中的同名项都不生效，保证模板泛型与编码一致。需要其他序列化请自定义 ProducerFactory/ConsumerFactory 同名 Bean。
- `ack-mode` 支持 batch/auto(=batch)/record/manual/manual_immediate/count/time/count_time（大小写与 `-`/`_` 均可）；非 batch 模式下显式开启的 `enable-auto-commit` 会被强制关闭并 WARN；batch 模式显式开启自动提交时 WARN 提示可能丢消息；未知值回退 BATCH。
- 监听容器统一设置 `DefaultErrorHandler()`（默认退避重试 9 次后记录日志并跳过）。

### 5.2 每个数据源注册的 Bean（`<name>` 为数据源名）

| Bean | 类型 |
|---|---|
| `<name>ProducerFactory` / `<name>ByteProducerFactory` / `<name>ProtobufProducerFactory` | `DefaultKafkaProducerFactory` |
| `<name>KafkaTemplate` / `<name>ByteKafkaTemplate` / `<name>ProtobufKafkaTemplate` | `KafkaTemplate<String,String>` / `<String,byte[]>` / `<String,byte[]>` |
| `<name>ConsumerFactory` / `<name>ByteConsumerFactory` / `<name>ProtobufConsumerFactory` | `DefaultKafkaConsumerFactory` |
| `<name>ListenerContainerFactory` / `<name>ByteListenerContainerFactory` / `<name>ProtobufListenerContainerFactory` | 单条监听 |
| `<name>BatchListenerContainerFactory` / `<name>BatchByteListenerContainerFactory` / `<name>BatchProtobufListenerContainerFactory` | 批量监听 |

- 主数据源的 String ProducerFactory、KafkaTemplate、ConsumerFactory 标记 `@Primary`，并注册别名：`producerFactory`、`byteProducerFactory`、`protobufProducerFactory`、`kafkaTemplate`、`byteKafkaTemplate`、`protobufKafkaTemplate`、`consumerFactory`、`byteConsumerFactory`、`protobufConsumerFactory`、`listenerContainerFactory`、`batchListenerContainerFactory`、`byteListenerContainerFactory`、`batchByteListenerContainerFactory`、`protobufListenerContainerFactory` 与 `protobufKafkaListenerContainerFactory`（两者同指 Protobuf 单条工厂）、`batchProtobufListenerContainerFactory`。
- `kafkaListenerContainerFactory` 也作为主数据源 `<name>ListenerContainerFactory` 的别名（替换 Boot 自动配置生成的同名定义；用户自定义的同名 Bean 保持不变），因此 `@KafkaListener` 不写 `containerFactory` 时使用 easyfk 的工厂。
- 已存在同名 Bean 时不覆盖（可用同名 Bean 自定义）。

### 5.3 KafkaProducer（固定使用主数据源）

| 方法 | 模板 | value 编码 |
|---|---|---|
| `syncSendMessage(CommonMessage<T>)` / `asyncSendMessage` | `kafkaTemplate` | String 原样；数字/布尔/字符原样 toString；其他对象 fastjson2 `toJSONString`；null 作 tombstone |
| `syncSendMessageWithByte(CommonMessage<T>)` / `asyncSendMessageWithByte` | `byteKafkaTemplate` | byte[] 原样；String/基础类型 UTF-8；其他对象 `ForySerializer.serialize` |
| `syncSendProtobufMessage(ProtobufMessage<T>)` / `asyncSendProtobufMessage` | `byteKafkaTemplate` | `ProtobufUtils.serialize` |

- 只发送 `data` 本身，不发送整个 CommonMessage 包装；data 为 null 时发送 tombstone（Protobuf 通道同样）。
- 构建 record 前校验 message 非 null、topic 非空白，否则直接抛 `IllegalArgumentException`（同步/异步都抛，不包装为发送失败）。
- record：`partition` 非空 → `(topic, partition, messageKey, value)`；否则 messageKey 非空 → `(topic, key, value)`；否则 `(topic, value)`。
- headers：`messageId`（为空自动生成并**回写**到 message）、`tags`、`sendTimestamp`（字符串形式的毫秒数）、全部 `properties`（UTF-8，null 键/值跳过）。
- 同步：`get(30s)` 并返回 `SendResult`，失败抛 `RuntimeException("Kafka消息发送失败")`（中断时恢复中断标志）；异步：返回 `CompletableFuture<SendResult>`，失败时同时记 ERROR 日志。
- `delayTime` 不生效（Kafka 无延迟消息）。
- 多数据源发送：注入 `KafkaClientRegistry`，`getStringTemplate("report")` / `getByteTemplate(name)` / `getProtobufTemplate(name)` / `getListenerContainerFactory(beanName)`，无参方法返回主数据源。

### 5.4 消费

```java
@KafkaListener(topics = "order_topic", groupId = "order-group", containerFactory = "listenerContainerFactory")
public void onOrder(ConsumerRecord<String, String> record, Acknowledgment ack) {   // ack 仅 manual 类 ack-mode 可用
    OrderDTO order = KafkaMessageUtil.getMessageBodyFromStringRecord(record, OrderDTO.class);
    Map<String, String> headers = KafkaMessageUtil.extractHeaders(record);
    ack.acknowledge();
}

@KafkaListener(topics = "quote_topic", containerFactory = "byteListenerContainerFactory")
public void onQuote(ConsumerRecord<String, byte[]> record) {
    QuoteProto q = KafkaMessageUtil.getMessageBodyFromByteRecord(record, QuoteProto.class);
}

@KafkaListener(topics = "report_topic", containerFactory = "reportListenerContainerFactory")   // 指定数据源
public void onReport(String payload) { }
```
- `syncSendMessageWithByte` 发出的复杂对象需用 `ForySerializer` 反序列化，KafkaMessageUtil 没有对应方法。

### 5.5 AbstractKafkaPartitionConsumer（低延迟分区并行消费）

```java
@Component
public class QuoteConsumer extends AbstractKafkaPartitionConsumer {
    @Resource(name = "byteConsumerFactory")
    private ConsumerFactory<String, byte[]> consumerFactory;
    @Override protected String getTopic() { return "quote_topic"; }
    @Override protected ConsumerFactory<String, byte[]> getConsumerFactory() { return consumerFactory; }
    @Override protected String getConsumerName() { return "quote"; }
    @Override protected void processMessage(byte[] value, TopicPartition tp) {
        QuoteProto q = ProtobufUtils.deserialize(value, QuoteProto.class);
    }
}
```
- `SmartLifecycle`：一个 poll 线程 + 每个分区一个 worker 线程；同分区串行、不同分区并行。
- **at-least-once**：worker 每处理完一批记录已处理 offset，poll 线程只 `commitAsync` 已处理的 offset（先处理后提交）；ConsumerFactory 的 `enable.auto.commit` 应为 false（easyfk 工厂默认即 false）。
- 队列满（默认 5000 批）时 `pause` 该分区并 `seek` 回本批首条 offset，队列降到一半以下再 `resume`，不丢消息。
- 分区撤销 / 停止 / poll 异常退出时：等待被撤销分区的 worker 处理完队列（最长 `getWorkerShutdownTimeoutMs()`），超时则中止 worker（不再处理剩余消息），然后 `commitSync` 只提交已处理的 offset，未处理部分由新持有者重新消费；`onPartitionsLost` 只停止 worker 不提交。
- processMessage 抛异常只打日志并视为已处理（不重试）；重平衡/崩溃可能重复投递，处理需幂等。
- `processMessage` 只拿到 value（空 value 被过滤，但其 offset 照常推进），拿不到 key/headers/offset。
- 可覆盖：`getPollTimeout()`(10ms)、`getWorkerQueueCapacity()`(5000)、`getWorkerShutdownTimeoutMs()`(3000，应小于 `max.poll.interval.ms`)、`getPollThreadJoinTimeoutMs()`(5000)、`getRestartBackoffMs()`(5000)、`getGroupId()`、`getAutoOffsetReset()`、`onPartitionsAssignedHook`、`onPartitionsRevokedHook`。
- 只订阅一个 topic；poll 循环遇到异常时关闭 consumer，按 `getRestartBackoffMs()` 退避后重建并重新订阅。
- `isRunning()`：已 start 未 stop 且 poll 线程存活（退避重建期间仍为 true）；`isConsuming()`：当前有活跃的 poll 会话，可用于健康检查。

### 5.6 Kafka Streams

```yaml
easyfk.config.mq.kafka:
  enable-kafka: true
  enable-streams: true
  streams:
    application-id: order-streams
    datasource: default             # 不填用主数据源；取其 bootstrap-servers 和 properties（SASL/SSL 等）
    state-dir: /tmp/kafka-streams
    processing-guarantee: at_least_once   # exactly_once_v2
    num-stream-threads: 2
    default-deserialization-exception-handler: logAndContinue   # logAndFail
    default-production-exception-handler: fail                  # continue
    auto-offset-reset: earliest     # 默认 earliest
    session-timeout-ms: 30000
    heartbeat-interval-ms: 10000
    properties: { replication.factor: 3 }   # 任意 Streams/客户端原生配置，最后写入
```
- `KafkaStreamsConfig` 由 `KafkaMqConfig` 通过 `@ImportAutoConfiguration` 引入，带 `@EnableKafkaStreams`；默认 serde：key=String，**value=ByteArray**；时间戳提取器为 `WallclockTimestampExtractor`。配置写入顺序：内置项 → 数据源 `properties` → `streams.properties`。
- 处理器：

```java
@Component
public class OrderStreamProcessor extends BaseStreamProcessor {
    @Override protected String getProcessorName() { return "order-filter"; }
    @Override protected String[] getInputTopics() { return new String[]{"order_topic"}; }
    @Override protected String[] getOutputTopics() { return new String[]{"high_value_order_topic"}; }
    @Override protected void buildTopology(StreamsBuilder builder) {
        // jsonMessage(OrderDTO.class) 与 KafkaProducer.syncSendMessage 的格式兼容（value 只含 data，元数据在 headers）
        builder.stream("order_topic", Consumed.with(Serdes.String(), SerdeFactory.jsonMessage(OrderDTO.class)))
               .filter((k, msg) -> msg != null && msg.getData().getPrice() > 100)
               .to("high_value_order_topic", Produced.with(Serdes.String(), SerdeFactory.jsonMessage(OrderDTO.class)));
    }
}
```
- `BaseStreamProcessor` 在 `afterPropertiesSet` 中校验输入 topic 并调用 `buildTopology`（不会对共享 `StreamsBuilder` 调用 `build()`）；`StreamProcessorRegistry` 汇总处理器，`getProcessorStatus` 的 status 为共享 `KafkaStreams` 实例的状态（`CREATED/RUNNING/REBALANCING/ERROR/...`，未启动为 `NOT_STARTED`）。
- `SerdeFactory`：
  - `string/longValue/integer/doubleValue/floatValue/byteArray`；
  - `jsonMessage(Class<T> dataType)` → `CommonMessageSerde`：**与 KafkaProducer String 通道兼容**，value 只含 data（String 原样，数字/布尔 toString，其他 JSON），data 按 `dataType` 解析；messageId/tags/sendTimestamp/properties 通过 record headers 读写；tombstone 返回 null；
  - `protobufMessage(Clazz.class)`：value 为 Protobuf 字节（与 `syncSendProtobufMessage` 兼容），元数据同样走 headers；
  - `baseMessage(Class)` / `commonMessageEnvelope(Class<T> dataType)`：value 为**整个 BaseMessage 的 JSON 信封**，只用于上下游都按信封读写的 topic；`commonMessageEnvelope` 把 data 解析为指定类型（`baseMessage(CommonMessage.class)` 的 data 会是 `JSONObject`）。
- `KafkaMessageUtil` 的 Streams 工具：`extractKeyValue`、`baseMessageKeyValueMapper`、`jsonMessageDataExtractor`、`protobufMessageDataExtractor`、`topicExtractor`、`messageIdExtractor`、`timestampExtractor`、`jsonMessageWrapper(topic)`、`protobufMessageWrapper(topic)`、`topicFilter`、`timeRangeFilter`、`topicGrouper`、`messageTypeGrouper`。

---

## 6. 生成代码时的规则

### Do
- 引入哪个 MQ 就必须配置对应开关：`enable-rocket` / `enable-rabbit` / `enable-kafka: true`。
- RocketMQ 必须配置 `rocketmq.name-server` 和 `rocketmq.producer.group`。
- 所有 Producer 都必须设置非空白 topic（Rabbit 可留空以使用默认 exchange）；topic 命名不再有长度/字符限制。
- 需要顺序：Rocket 用 messageKey（不要同时设 delayTime）；Kafka 用 messageKey 或 `MessageBuilder.partition(n)`。
- 需要延迟：Rocket（5.x Broker）或 Rabbit（插件 + `x-delayed-message` 交换机）；Kafka 不支持。
- Rabbit 的 Exchange/Queue/Binding 由业务声明；需要确认异步发送结果时使用 `asyncSendMessage` 返回的 Future。
- Rocket 同步发送检查返回的 `SendResult.getSendStatus()`；消费端用 `RocketMQListener<MessageExt>` + `RocketMessageUtil` 读取头。
- Kafka 可靠消费：默认（`enable-auto-commit=false` + `ack-mode=batch`）即为处理完成后提交；需要逐条确认时 `ack-mode: manual` + `Acknowledgment.acknowledge()`；多数据源用 `<name>ListenerContainerFactory` 和 `KafkaClientRegistry`。
- Kafka 的 concurrency/ack-mode 等扩展项写在 `easyfk.config.mq.kafka.datasources.<name>.consumer` 下，或使用 Boot 标准键 `spring.kafka.listener.concurrency/ack-mode`。
- Kafka 消费 Protobuf 用 `byteListenerContainerFactory` 或 `protobufListenerContainerFactory`，再用 `ProtobufUtils.deserialize`。
- Kafka Streams 中按实际编码显式指定 `Consumed.with(...)` / `Produced.with(...)`；读取 KafkaProducer 发出的 JSON 消息用 `SerdeFactory.jsonMessage(Data.class)`。
- 所有消费端做幂等。

### Don't
- 不要依赖 Bean Validation 拦截非法 topic（Producer 只校验非空白）。
- 不要同时设置 Rocket 的 delayTime 和 messageKey 并期望顺序性。
- 不要把 Kafka 异步发送的 Future 丢弃后又期望知道失败（失败只记日志）；需要确认结果用 sync 方法或处理返回的 Future。
- 不要在 `AbstractKafkaPartitionConsumer.processMessage` 中依赖异常触发重试（异常视为已处理）。
- 不要在 Streams 中用 `baseMessage(...)` / `commonMessageEnvelope(...)` 解析 `KafkaProducer` 发出的消息（那是信封格式）。
- 不要配置 `key-serializer`/`value-serializer` 期望改变 easyfk 工厂的序列化器（按通道固定）。
- 不要把 `concurrency`、`ack-mode` 写在 `spring.kafka.consumer` 下（不是 Boot 标准键，不会被读取）。

---

## 7. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | mq-common（无文档） | — | `src/main/resources/spring/...AutoConfiguration.imports` 少了 `META-INF`，且指向不存在的 `com.mcst.easyfk.mq.common.config.MqConfig`；当前不会被加载，所以没有影响，但属于残留错误 **已修复**：错误的 imports 文件已删除，mq-common 不再包含自动配置声明。 |
| 2 | 各手册示例 | topic 使用 `order-topic`、`order-exchange` 等 | `BaseMessage.topic` 声明禁止 `-`、长度 ≥ 5；因为 Producer 不做校验所以示例能跑，但与模型约束矛盾 **已修复**：`topic` 只保留 `@NotBlank`（`order-topic` 合法），Rocket/Kafka Producer 发送前校验 topic 非空白、Rabbit 校验最终 exchange 非 null，不满足抛 `IllegalArgumentException`。 |
| 3 | mq-common | `MessageBuilder` 覆盖全部字段 | 没有 `partition` 设置方法；`MqTypeEnums` 缺 RABBIT **已修复**：新增 `MessageBuilder.partition(Integer)`，`MqTypeEnums` 增加 `RABBIT`。 |
| 4 | mq-rocket开发手册 §5.9 | `RocketMQListener<Message<OrderDTO>>` + `RocketMessageUtil.getHeaderValue` 取头 | rocketmq-spring 2.3.x 监听器的泛型支持 `MessageExt`/`String`/具体 payload 类型；`Message<T>` 会被当成消息体 JSON 的目标类型反序列化，大概率失败（按 starter 源码推断，未运行验证）。取头应使用 `MessageExt.getUserProperty` **已修复**：`RocketMessageUtil` 新增 MessageExt 版 `getHeaderValue/getMessageId/getSendTimestamp/getKeys/getTags/getBodyAsString/getBody`，消费端用 `RocketMQListener<MessageExt>`（见 3.3）。 |
| 5 | mq-rocket开发手册 §3/§4 | 异步发送 | `asyncSendMessage` 在 `delayTime > 0` 时调用 `syncSendDelayTimeMills`，实际同步阻塞 **已修复**：异步延迟消息设置 `delayTimeMs` 后通过 `producer.send(msg, callback)` 真正异步发送。 |
| 6 | mq-rocket开发手册 消息字段表 | 未说明 properties | `properties` 完全不发送；`messageKey` 只作 hashKey，不设 RocketMQ KEYS **已修复**：`properties` 作为用户属性发送，`messageKey` 同时设置为 KEYS。 |
| 7 | mq-rocket 源码 | — | 属性类命名为 `KafkaMqProperties` 且未注册；同步发送不检查 `SendResult` 状态 **已修复**：属性类更名为 `RocketMqProperties` 并由 `RocketMqConfig` 的 `@EnableConfigurationProperties` 注册；同步发送检查并返回 `SendResult`（无结果抛异常，非 SEND_OK 告警）。 |
| 8 | mq-rabbit开发手册 / 技术特点 | `properties` 透传；“两种模式均自动处理延迟消息识别、消息属性注入” | 只有同步非延迟发送带头；`asyncSendMessage` 和延迟发送不带 messageId/sendTimestamp/tags/properties **已修复**：同步/异步、普通/延迟所有路径都带 messageId/timestamp 及 messageId/sendTimestamp/tags/properties 头。 |
| 9 | mq-rabbit开发手册 路由规则 | 延迟走 delayExchange，其次 topic，最后默认 exchange | 与源码一致；注意延迟时 topic 被忽略（RabbitMQ使用教程把 topic 设为延迟交换机名，实际无作用） |
| 10 | mq-rabbit开发手册 §6 | `confirm-callback` / `return-callback` 开启后回调生效 | `RabbitMqConfig` 通过 `@Import(RabbitAutoConfiguration)` 先导入 Boot 的配置；按 Spring 配置类加载顺序，Boot 的 `rabbitTemplate` 会先注册，easyfk 带回调的 `RabbitTemplate`（`@ConditionalOnMissingBean`）可能被跳过，回调不生效（推断，未运行验证）。另外 return 回调还需要 `mandatory=true`，源码没有设置，依赖 `spring.rabbitmq.template.mandatory` **已修复**：改为注册 `RabbitTemplateCustomizer` 定制 Boot 的 `rabbitTemplate`，开启 return-callback 时同时设置 `mandatory=true`。 |
| 11 | mq-rabbit 源码 | — | `RabbitProducer` 泛型要求 `T extends Serializable`，Rocket/Kafka 没有此限制；异步发送使用公共 ForkJoinPool **已修复**：去掉 `Serializable` 约束；异步发送改用 `RabbitProducerHelper` 独占的有界线程池（`easyfk.config.mq.rabbit.async.*`，队列满调用方执行，销毁时等待任务完成），并返回 `CompletableFuture<Void>`。 |
| 12 | mq-kafka使用教程 Spring Kafka 完整配置 | 可配置 `key-serializer`、`value-serializer` | easyfk 工厂写死序列化器，这两项对 easyfk Bean 无效；`spring.kafka.consumer.concurrency/ack-mode` 不是 Boot 标准键，只被 easyfk 读取 **已修复**：序列化器按通道固定属设计，现于所有配置之后写入并在 5.1 明确说明；回退只读取 Boot 标准键（按 Boot 类型解析），concurrency/ack-mode 改读 `datasources.<name>.consumer.*` 或 `spring.kafka.listener.concurrency/ack-mode`，其余 easyfk 扩展项只能写在 `easyfk.config.mq.kafka.datasources.<name>` 下；使用教程配置示例已同步。 |
| 13 | mq-kafka使用教程 普通消费示例 | `@KafkaListener(topics, groupId)` 不写 containerFactory | 默认工厂名为 `kafkaListenerContainerFactory`，easyfk 只注册 `listenerContainerFactory` 别名，因此会使用 Boot 自带工厂，easyfk 的 ack-mode/concurrency/错误处理器不生效（推断，未运行验证） **已修复**：`kafkaListenerContainerFactory` 注册为主数据源 `<name>ListenerContainerFactory` 的别名（替换 Boot 的同名定义，不覆盖用户自定义 Bean）。 |
| 14 | mq-kafka使用教程 多数据源 Bean 表 | 主数据源注册无前缀别名（`kafkaTemplate`、`listenerContainerFactory` 等），按“去掉前缀”的规律推测应为 `protobufListenerContainerFactory` | 实际 Protobuf 单条监听的别名是 `protobufKafkaListenerContainerFactory`，与其他别名命名规律不一致 **已修复**：同时注册 `protobufListenerContainerFactory` 别名，旧别名保留。 |
| 15 | mq-kafka使用教程 默认值 | `enable-auto-commit: true` 为默认 | 与源码一致，但 Spring Kafka 原生默认是 false；在 `ack-mode=auto/batch` 下由客户端自动提交，可能先提交后处理，崩溃时丢消息 **已修复**：`enable-auto-commit` 默认改为 false，`ack-mode` 默认 batch，由容器在每批处理完成后提交；显式开启自动提交时 WARN。 |
| 16 | mq-kafka使用教程 Kafka Streams 示例 | `OrderStreamProcessor` 只实现 `buildTopology`，`builder.stream("order-topic")` 读取 `KStream<String,String>` | 缺少抽象方法 `getProcessorName()`、`getInputTopics()`，无法编译；默认 value serde 是 ByteArray，不指定 `Consumed.with(String,String)` 会在运行时 ClassCastException，`count()` 结果写出也会序列化失败 **已修复**：使用教程示例补齐 `getProcessorName/getInputTopics/getOutputTopics`，输入输出显式指定 `Consumed/Produced/Grouped.with`（`SerdeFactory.jsonMessage(OrderDTO.class)`、count 结果用 `Serdes.Long()`）。 |
| 17 | mq-kafka技术特点 Streams 工具 | `SerdeFactory.jsonMessage()` 处理 JSON 消息 | 它按“整个 BaseMessage 的 JSON”解析，`KafkaProducer` 只发送 data，两者格式不兼容；且原始类型 `CommonMessage.class` 反序列化后 data 是 `JSONObject` **已修复**：`SerdeFactory.jsonMessage(Class<T> dataType)` 改为 `CommonMessageSerde`，与 KafkaProducer 一致（value 只含 data，元数据走 headers），data 按指定类型解析；信封格式另提供 `commonMessageEnvelope(Class)` 实现带类型解析；移除无类型的 `jsonMessage()` 与 `BaseMessageSerde.jsonMessageSerde/protobufMessageSerde`。 |
| 18 | mq-kafka 源码 | — | 同步发送在 `log.debug` 参数里直接调用 `JSONObject.toJSONString(message)`，无论日志级别都会序列化一次；`properties` 值为 null 时 `getBytes` NPE；`extractHeaders` 遇到 null 头值会 NPE **已修复**：不再在日志参数中序列化消息；null 键/值的 properties 跳过；`extractHeaders` 对 null 头值返回 null。 |
| 19 | mq-kafka 源码 | — | `AbstractKafkaPartitionConsumer` 的 poll 循环异常后线程退出且不重启，`isRunning()` 仍返回 true；分区撤销时 worker 3 秒内未处理完也会提交 offset；`BaseStreamProcessor` 在 debug 级别下对共享 `StreamsBuilder` 额外调用 `build()`（可能影响后续拓扑构建，未验证） **已修复**：poll 异常后退避重建 consumer；只提交 worker 已处理完成的 offset，队列满改为 pause+seek 背压，撤销/停止时等待 worker 处理完（超时中止且不提交未处理部分），`onPartitionsLost` 不提交；`isRunning()` 要求 poll 线程存活，新增 `isConsuming()`；`BaseStreamProcessor` 不再调用 `build()`，状态取 `KafkaStreams.state()`。 |
| 20 | mq-kafka 源码 | Streams 可用 `streams.datasource` 指定集群 | 只取 `bootstrap-servers`，数据源的 `properties`（安全认证等）不会带入 Streams；Consumer 的 `auto.offset.reset/session/heartbeat` 写死 **已修复**：Streams 带入所选数据源的 `properties`，新增 `streams.auto-offset-reset/session-timeout-ms/heartbeat-interval-ms` 与 `streams.properties`（最后写入）。 || 21 | 3.5.16 升级 | 文档原写 protobuf 4.28.2、rocketmq-spring 2.3.4、kafka-streams 3.6.2 | 4 个子模块 `build.gradle` 与 3.2.12 相同，版本变化全部来自 BOM：`protobuf` 4.28.2 → **4.36.2**、`rocketMq` 2.3.4 → **2.3.6**；`kafka-streams` 改为无版本坐标，跟随 Boot 3.5.16 管理的 Kafka 3.9.x（Kafka 4.x 需 Spring Kafka 4 / Boot 4，本版本不能升） **已更新**：§1 版本列已同步 |
