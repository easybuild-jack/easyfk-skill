# easyfk-component-mq API 签名速查（easyfk 3.5.16）

> 坐标：`com.mcst:mq-common、mq-rocket、mq-rabbit、mq-kafka`　源码：`easyfk-component/component-mq/mq-common`、`easyfk-component/component-mq/mq-rocket`、`easyfk-component/component-mq/mq-rabbit`、`easyfk-component/component-mq/mq-kafka`
> 由 `scripts/gen-api.py` 从 34 个源文件自动提取，共 33 个类型、159 个方法/构造器、30 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-component-mq-skill.md](../modules/easyfk-component-mq-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 配置项（@ConfigurationProperties）

### `easyfk.config.mq.rocket` ← RocketMqProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `enable-rocket` | `Boolean` | `Boolean.FALSE` | 开启RocketMQ消息队列 |

### `easyfk.config.mq.rabbit` ← RabbitMqProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `enable-rabbit` | `Boolean` | `Boolean.FALSE` | 开启RabbitMQ消息队列 |
| `exchange` | `String` | `"easyfk.direct.exchange"` | 默认Exchange名称 |
| `delay-exchange` | `String` | `"easyfk.delay.exchange"` | 延迟消息Exchange名称（需要安装rabbitmq_delayed_message_exchange插件） |
| `confirm-callback` | `Boolean` | `Boolean.FALSE` | 是否启用发布确认 |
| `return-callback` | `Boolean` | `Boolean.FALSE` | 是否启用返回回调（消息无法路由时触发） |
| `async` | `Async` | `new Async()` | 异步发送线程池配置 |

### `easyfk.config.mq.kafka` ← KafkaMqProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `enable-kafka` | `Boolean` | `Boolean.FALSE` | 开启Kafka消息队列 |
| `primary-datasource` | `String` | `"default"` | 主Kafka数据源名称。 旧版无数据源配置时会自动使用 spring.kafka.* 构造该数据源。 |
| `datasources` | `Map<String, Datasource>` | `new LinkedHashMap<>()` | 多Kafka数据源配置。 |
| `enable-streams` | `Boolean` | `Boolean.FALSE` | 是否开启Kafka Streams |
| `streams` | `Streams` | `new Streams()` | Kafka Streams配置 |


## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `mq-rocket` | `com.mcst.easyfk.mq.rocket.config.RocketMqConfig` |
| `mq-rabbit` | `com.mcst.easyfk.mq.rabbit.config.RabbitMqConfig` |
| `mq-kafka` | `com.mcst.easyfk.mq.kafka.config.KafkaDatasourceBeanRegistrar` |
| `mq-kafka` | `com.mcst.easyfk.mq.kafka.config.KafkaMqConfig` |

## 类型索引

- `com.mcst.easyfk.mq.common.constants`：[MessageHeaderConstants](#messageheaderconstants)
- `com.mcst.easyfk.mq.common.enums`：[MqTypeEnums](#mqtypeenums)
- `com.mcst.easyfk.mq.common.message`：[BaseMessage](#basemessage)、[CommonMessage](#commonmessage)、[MessageBuilder](#messagebuilder)、[ProtobufMessage](#protobufmessage)
- `com.mcst.easyfk.mq.common.util`：[MessageCheckUtil](#messagecheckutil)、[ProtobufUtils](#protobufutils)
- `com.mcst.easyfk.mq.kafka.client`：[KafkaClientRegistry](#kafkaclientregistry)
- `com.mcst.easyfk.mq.kafka.config`：[KafkaDatasourceBeanRegistrar](#kafkadatasourcebeanregistrar)、[KafkaDatasourceConfigSupport](#kafkadatasourceconfigsupport)、[KafkaMqConfig](#kafkamqconfig)、[KafkaStreamsConfig](#kafkastreamsconfig)
- `com.mcst.easyfk.mq.kafka.consumer`：[AbstractKafkaPartitionConsumer](#abstractkafkapartitionconsumer)
- `com.mcst.easyfk.mq.kafka.producer`：[KafkaProducer](#kafkaproducer)
- `com.mcst.easyfk.mq.kafka.properties`：[KafkaMqProperties](#kafkamqproperties)
- `com.mcst.easyfk.mq.kafka.streams.processor`：[BaseStreamProcessor](#basestreamprocessor)、[StreamProcessorRegistry](#streamprocessorregistry)
- `com.mcst.easyfk.mq.kafka.streams.serde`：[BaseMessageSerde](#basemessageserde)、[CommonMessageSerde](#commonmessageserde)、[ProtobufMessageSerde](#protobufmessageserde)、[SerdeFactory](#serdefactory)
- `com.mcst.easyfk.mq.kafka.util`：[KafkaMessageUtil](#kafkamessageutil)
- `com.mcst.easyfk.mq.rabbit.config`：[RabbitMqConfig](#rabbitmqconfig)
- `com.mcst.easyfk.mq.rabbit.producer`：[RabbitProducer](#rabbitproducer)、[RabbitProducerHelper](#rabbitproducerhelper)
- `com.mcst.easyfk.mq.rabbit.properties`：[RabbitMqProperties](#rabbitmqproperties)
- `com.mcst.easyfk.mq.rabbit.util`：[RabbitMessageUtil](#rabbitmessageutil)
- `com.mcst.easyfk.mq.rocket.config`：[RocketMqConfig](#rocketmqconfig)
- `com.mcst.easyfk.mq.rocket.producer`：[RocketProducer](#rocketproducer)、[RocketProducerHelper](#rocketproducerhelper)
- `com.mcst.easyfk.mq.rocket.properties`：[RocketMqProperties](#rocketmqproperties)
- `com.mcst.easyfk.mq.rocket.util`：[RocketMessageUtil](#rocketmessageutil)

## 包 `com.mcst.easyfk.mq.common.constants`

### MessageHeaderConstants

`public final class MessageHeaderConstants`　消息头常量定义

**字段 / 常量**

```java
static final String MESSAGE_ID = "messageId"  // 消息ID头字段名
static final String SEND_TIMESTAMP = "sendTimestamp"  // 发送时间戳头字段名
static final String TAGS = "tags"  // 消息标签头字段名
```

## 包 `com.mcst.easyfk.mq.common.enums`

### MqTypeEnums

`public enum MqTypeEnums`　Lombok：`@Getter`

**枚举常量**

```java
ROCKET("rocket", "Rocket")  // Rocket
RABBIT("rabbit", "Rabbit")  // Rabbit
KAFKA("kafka", "Kafka")  // Kafka
```

**字段 / 常量**

```java
final String value
final String name
```

**构造器**

```java
MqTypeEnums(String value, String name)
```

## 包 `com.mcst.easyfk.mq.common.message`

### BaseMessage

`public class BaseMessage implements Serializable`　Lombok：`@Data`

**字段 / 常量**

```java
@NotBlank(message = "topic不能为空") String topic  // 主题，不可为空（各 Producer 发送前会校验，见 MessageCheckUtil）
Long delayTime  // 延迟时间 单位 毫秒
Long sendTimestamp  // 消息时间戳
String messageId  // 消息ID
String messageKey  // 业务键/分片键/hash键,一般用于分区场景，保证消息的顺序性
String tags  // 消息标签，用于过滤
Integer partition  // 物理分区，一般只用于Kafka需要明确指定分区场景，只针对Kafka,其他MQ不支持。 推荐使用messageKey进行分区
Map<String, String> properties  // 自定义扩展属性
```

### CommonMessage

`public class CommonMessage<T> extends BaseMessage`　Lombok：`@EqualsAndHashCode(callSuper = true)` `@Data` `@Accessors(chain = true)`

**字段 / 常量**

```java
T data
```

### MessageBuilder

`public class MessageBuilder`　消息构建器，支持链式调用创建CommonMessage和ProtobufMessage对象

**方法**

```java
static MessageBuilder create()  // 创建消息构建器实例
MessageBuilder topic(String topic)  // 设置主题
MessageBuilder delayTime(Long delayTime)  // 设置延迟时间
MessageBuilder sendTimestamp(Long sendTimestamp)  // 设置消息时间戳
MessageBuilder messageId(String messageId)  // 设置消息ID
MessageBuilder messageKey(String messageKey)  // 设置业务键/分片键/hash键
MessageBuilder tags(String tags)  // 设置消息标签
MessageBuilder partition(Integer partition)  // 设置物理分区（仅 Kafka 生效）
MessageBuilder property(String key, String value)  // 添加自定义属性
MessageBuilder properties(Map<String, String> properties)  // 设置自定义属性集合
<T> CommonMessage<T> buildCommonMessage(T data)  // 构建CommonMessage对象
<T extends Message> ProtobufMessage<T> buildProtobufMessage(T data)  // 构建ProtobufMessage对象
```

### ProtobufMessage

`public class ProtobufMessage<T extends Message> extends BaseMessage`　Lombok：`@EqualsAndHashCode(callSuper = true)` `@Data` `@Accessors(chain = true)`

**字段 / 常量**

```java
T data
```

## 包 `com.mcst.easyfk.mq.common.util`

### MessageCheckUtil

`public final class MessageCheckUtil`　消息发送前的基础校验

**方法**

```java
static void checkMessage(BaseMessage message)  // 校验消息对象非空
static void checkTopic(BaseMessage message)  // 校验消息对象非空且 topic 不为空白
```

### ProtobufUtils

`public class ProtobufUtils`　注解：`@SuppressWarnings("all")` `@Slf4j`　Protobuf消息工具类 提供消息序列化、反序列化、包装等功能

**方法**

```java
static byte[] serialize(Message message)  // 将Protobuf消息序列化为字节数组
static <T extends Message> T deserialize(byte[] data, Class<T> messageClass)  // 从字节数组反序列化Protobuf消息
static String toJSONString(MessageOrBuilder message)  // Protobuf消息对象转JSON字符串 使用preservingProtoFieldNames保持proto字段名，omittingInsignificantWhitespace输出单行格式
```

## 包 `com.mcst.easyfk.mq.kafka.client`

### KafkaClientRegistry

`public class KafkaClientRegistry`　Kafka 多数据源客户端注册表。 由 KafkaDatasourceBeanRegistrar 按数据源维度统一注册具名 Bean，本类按命名约定从 Spring 容器中 反查并按数据源分组…

**构造器**

```java
KafkaClientRegistry(String primaryDatasource, Iterable<String> datasourceNames, Map<String, KafkaTemplate> kafkaTemplates, Map<String, ConcurrentKafkaListenerContainerFactory> listenerContainerFactories)
```

**方法**

```java
String getPrimaryDatasource()
KafkaTemplate<String, String> getStringTemplate()
KafkaTemplate<String, String> getStringTemplate(String datasource)
KafkaTemplate<String, byte[]> getByteTemplate()
KafkaTemplate<String, byte[]> getByteTemplate(String datasource)
KafkaTemplate<String, byte[]> getProtobufTemplate()
KafkaTemplate<String, byte[]> getProtobufTemplate(String datasource)
ConcurrentKafkaListenerContainerFactory getListenerContainerFactory(String beanName)
```

## 包 `com.mcst.easyfk.mq.kafka.config`

### KafkaDatasourceBeanRegistrar

`public class KafkaDatasourceBeanRegistrar implements BeanDefinitionRegistryPostProcessor, EnvironmentAware, Ordered`　注解：`@AutoConfiguration` `@ConditionalOnProperty(prefix = "easyfk.config.mq.kafka", name = "enable-kafka", havingValue = "true")` `@SuppressWarnings("unchecked")`　为每个Kafka数据源提前注册具名Bean，便于 @KafkaListener(containerFactory = "...") 使用…

**方法**

```java
void setEnvironment(Environment environment)
void postProcessBeanDefinitionRegistry(BeanDefinitionRegistry registry) throws BeansException
void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) throws BeansException
int getOrder()
```

### KafkaDatasourceConfigSupport

`public class KafkaDatasourceConfigSupport`　注解：`@Slf4j`　Kafka 数据源配置解析。 取值顺序：easyfk.config.mq.kafka.datasources..producer/consumer.* → Spring Boot 标准键（spring.kafka.pro…

_无 public 成员。_

### KafkaMqConfig

`public class KafkaMqConfig`　注解：`@EnableConfigurationProperties(KafkaMqProperties.class)` `@AutoConfiguration` `@ConditionalOnProperty(prefix = "easyfk.config.mq.kafka", name = "enable-kafka", havingValue = "true")` `@ImportAutoConfiguration(KafkaStreamsConfig.class)`

**方法**

```java
@Bean KafkaProducer kafkaProducer()  // Kafka生产者Bean。
@Bean KafkaClientRegistry kafkaClientRegistry(ApplicationContext applicationContext, KafkaMqProperties kafkaMqProperties, Environment environment)  // Kafka 多数据源客户端注册表，依赖 KafkaDatasourceBeanRegistrar 已注册好的 Bean。
```

### KafkaStreamsConfig

`public class KafkaStreamsConfig`　注解：`@Slf4j` `@AutoConfiguration` `@EnableKafkaStreams` `@ConditionalOnProperty(prefix = "easyfk.config.mq.kafka", name = "enable-streams", havingValue = "true")`　Kafka Streams配置类 提供Kafka Streams的自动配置和Bean管理

**方法**

```java
@Bean(name = KafkaStreamsDefaultConfiguration.DEFAULT_STREAMS_CONFIG_BEAN_NAME) KafkaStreamsConfiguration kafkaStreamsConfiguration()  // Kafka Streams配置Bean Spring Boot会自动使用此配置创建KafkaStreams实例
@Bean StreamProcessorRegistry streamProcessorRegistry(ObjectProvider<BaseStreamProcessor> processorProvider)  // 流处理器注册表，通过 @Bean 注册以保证在纯自动配置（无组件扫描）场景下可用。
```

## 包 `com.mcst.easyfk.mq.kafka.consumer`

### AbstractKafkaPartitionConsumer

`public abstract class AbstractKafkaPartitionConsumer implements SmartLifecycle`　注解：`@Slf4j`　Kafka 消费者模板基类（模板方法模式）。

**方法**

```java
abstract String getTopic()  // 返回要订阅的 Kafka Topic 名称。
abstract ConsumerFactory<String, byte[]> getConsumerFactory()  // 返回创建 KafkaConsumer 所用的 ConsumerFactory。 子类通过 @Resource / @Autowired 注入后在此返回。
abstract String getConsumerName()  // 返回消费者名称，用于 poll 线程和 worker 线程的命名前缀，便于日志和监控定位。 示例："quote" → poll 线程名 quote-consumer-poll…
abstract void processMessage(byte[] value, TopicPartition partition) throws Exception  // 处理单条原始消息（模板核心扩展点）。 此方法在 PartitionWorker 线程中被调用，同分区消息严格串行，不同分区并行。 实现时无需关心线程安全与 offset 提交，框架已处理。
Duration getPollTimeout()  // 正常消费的 poll 超时。默认 10ms，降低端到端延迟。
int getWorkerQueueCapacity()  // 每个 PartitionWorker 内部队列的最大批次容量。 默认 5000 批次，队列满时暂停该分区拉取，防止 poll 速度远快于处理时内存膨胀。
long getWorkerShutdownTimeoutMs()  // PartitionWorker 优雅停止时等待队列处理完的超时（ms）。默认 3000ms。 超时后 worker 被中止，未处理的消息不提交 offset…
long getPollThreadJoinTimeoutMs()  // stop() 等待 pollThread 退出的 join 超时（ms）。默认 5000ms。
void onPartitionsAssignedHook(Collection<TopicPartition> partitions)  // 分区分配完成后的扩展钩子。
void onPartitionsRevokedHook(Collection<TopicPartition> partitions)  // 分区被撤销后的扩展钩子。
String getGroupId()  // 返回消费者组 ID（group.id）。
String getAutoOffsetReset()  // 返回 offset 重置策略（auto.offset.reset）。
long getRestartBackoffMs()  // poll 循环异常退出后重建 consumer 的等待时间（ms）。默认 5000ms。
final void start()
final void stop()  // 优雅停止。 wakeup() 是唯一线程安全的 KafkaConsumer 方法，打断 pollThread 阻塞中的 poll()…
final boolean isRunning()  // 生命周期是否处于运行中：已 start 且未 stop，并且 poll 线程存活（异常后的退避重建期间仍为 true）。 是否正在实际消费请使用 isConsuming()。
final boolean isConsuming()  // 当前是否有活跃的 poll 会话（consumer 已订阅、未处于异常退避重建中），可用于健康检查。
```

## 包 `com.mcst.easyfk.mq.kafka.producer`

### KafkaProducer

`public class KafkaProducer`　注解：`@Slf4j` `@SuppressWarnings("all")`　Kafka消息生产者 提供同步和异步发送消息的功能

**方法**

```java
<T> SendResult<String, String> syncSendMessage(CommonMessage<T> message)  // 同步发送消息 同步发送是指发送方发送一条消息后，会等待服务器返回确认信息后再进行后续操作。这种方式适用于需要可靠性保证的场景。
<T extends Message> SendResult<String, byte[]> syncSendProtobufMessage(ProtobufMessage<T> message)
<T> SendResult<String, byte[]> syncSendMessageWithByte(CommonMessage<T> message)  // 同步发送消息，以byte[]的形式发送,会把消息体序列化为byte[]
<T> CompletableFuture<SendResult<String, String>> asyncSendMessage(CommonMessage<T> message)  // 异步发送消息 异步发送是指发送方发送一条消息后，不会等待服务器返回确认信息，而是直接返回。这种方式适用于需要快速响应的场景。
<T> CompletableFuture<SendResult<String, byte[]>> asyncSendMessageWithByte(CommonMessage<T> message)
<T extends Message> CompletableFuture<SendResult<String, byte[]>> asyncSendProtobufMessage(ProtobufMessage<T> message)
```

## 包 `com.mcst.easyfk.mq.kafka.properties`

### KafkaMqProperties

`public class KafkaMqProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.mq.kafka")`

**字段 / 常量**

```java
Boolean enableKafka = Boolean.FALSE  // 开启Kafka消息队列
String primaryDatasource = "default"  // 主Kafka数据源名称。 旧版无数据源配置时会自动使用 spring.kafka.* 构造该数据源。
Map<String, Datasource> datasources = new LinkedHashMap<>()  // 多Kafka数据源配置。
Boolean enableStreams = Boolean.FALSE  // 是否开启Kafka Streams
Streams streams = new Streams()  // Kafka Streams配置
```

#### KafkaMqProperties.Streams

`public static class Streams`　Lombok：`@Data`

**字段 / 常量**

```java
String datasource  // Kafka Streams使用的数据源，为空时使用主数据源； 取该数据源的 bootstrap-servers 与 properties（安全认证等）。 当前自动配置仍只创建一套默认Streams实例。
String autoOffsetReset = "earliest"  // 无已提交 offset 时的重置策略
Integer sessionTimeoutMs = 30000  // Consumer 会话超时（毫秒）
Integer heartbeatIntervalMs = 10000  // Consumer 心跳间隔（毫秒）
Map<String, String> properties = new LinkedHashMap<>()  // 附加 Streams/客户端原生配置，最后写入，可覆盖以上所有项
String applicationId = "streams-app"  // 应用ID，用于标识Streams应用实例
String stateDir = "/tmp/kafka-streams"  // 状态存储目录
String processingGuarantee = "at_least_once"  // 处理保证级别：at_least_once, exactly_once, exactly_once_v2
Long commitIntervalMs = 30000L  // 提交间隔时间（毫秒）
Long cacheMaxBytesBuffering = 10485760L  // 缓存最大字节数
String defaultDeserializationExceptionHandler = "logAndContinue"  // 默认反序列化异常处理器
String defaultProductionExceptionHandler = "fail"  // 默认生产异常处理器
Long retryBackoffMs = 100L  // 重试退避时间（毫秒）
Long reconnectBackoffMs = 50L  // 重连退避时间（毫秒）
Integer numStreamThreads = 2  // 流处理线程数量 默认设置为2，提供更好的并行处理能力
```

#### KafkaMqProperties.Datasource

`public static class Datasource`　Lombok：`@Data`

**字段 / 常量**

```java
String bootstrapServers  // Kafka broker地址，多个地址使用逗号分隔。
Producer producer = new Producer()  // 生产者配置。
Consumer consumer = new Consumer()  // 消费者配置。
Map<String, String> properties = new LinkedHashMap<>()  // 附加Kafka客户端配置。
```

#### KafkaMqProperties.Producer

`public static class Producer`　Lombok：`@Data`

**字段 / 常量**

```java
Integer retries
Integer batchSize
Integer lingerMs
Long bufferMemory
String acks
Boolean enableIdempotence
Integer maxInFlightRequestsPerConnection
String compressionType
Integer requestTimeoutMs
Integer deliveryTimeoutMs
Map<String, String> properties = new LinkedHashMap<>()
```

#### KafkaMqProperties.Consumer

`public static class Consumer`　Lombok：`@Data`

**字段 / 常量**

```java
String groupId
String autoOffsetReset
Boolean enableAutoCommit  // 客户端自动提交，默认 false（由监听容器在处理完成后提交）
Integer maxPollRecords
Integer sessionTimeoutMs
Integer heartbeatIntervalMs
Integer fetchMinBytes
Integer fetchMaxWaitMs
Integer concurrency  // 监听容器并发数，未配置时取 spring.kafka.listener.concurrency，默认 3
Integer autoCommitInterval
String isolationLevel
Integer maxPollIntervalMs
String ackMode  // 监听容器提交模式（batch/record/manual/manual_immediate/count/time/count_time，auto 等同 batch）…
Map<String, String> properties = new LinkedHashMap<>()
```

## 包 `com.mcst.easyfk.mq.kafka.streams.processor`

### BaseStreamProcessor

`public abstract class BaseStreamProcessor implements InitializingBean`　注解：`@Slf4j`　Kafka Streams处理器抽象基类 提供统一的流处理接口和生命周期管理

**方法**

```java
abstract String getProcessorName()  // 处理器名称，用于日志和监控
abstract void buildTopology(StreamsBuilder builder)  // 构建流处理拓扑 子类需要实现此方法来定义具体的流处理逻辑
abstract String[] getInputTopics()  // 获取输入主题名称
String[] getOutputTopics()  // 获取输出主题名称（可选）
void onProcessorInit()  // 处理器初始化回调 可以在此方法中进行自定义初始化逻辑
boolean validateProcessor()  // 处理器启动前的验证
final void afterPropertiesSet() throws Exception  // Spring Bean初始化完成后的回调 自动构建流处理拓扑
ProcessorStatus getProcessorStatus()  // 获取处理器状态信息
```

#### BaseStreamProcessor.ProcessorStatus

`public record ProcessorStatus(String name, String[] inputTopics, String[] outputTopics, String status)`　处理器状态信息类

**构造参数（record 组件）**

```java
String name
String[] inputTopics
String[] outputTopics
String status
```

**方法**

```java
static Builder builder()
```

##### BaseStreamProcessor.ProcessorStatus.Builder

`public static class Builder`

**方法**

```java
Builder name(String name)
Builder inputTopics(String[] inputTopics)
Builder outputTopics(String[] outputTopics)
Builder status(String status)
ProcessorStatus build()
```

### StreamProcessorRegistry

`public class StreamProcessorRegistry`　注解：`@SuppressWarnings("unused")` `@Slf4j`　Kafka Streams处理器注册管理器 负责管理所有的流处理器实例，提供统一的查询和监控接口 由 KafkaStreamsConfig 以 @Bean 方式注册，不依赖组件扫描。

**构造器**

```java
StreamProcessorRegistry(ObjectProvider<BaseStreamProcessor> processorProvider)
```

**方法**

```java
@PostConstruct void initRegistry()  // 初始化处理器注册表
void registerProcessor(BaseStreamProcessor processor)  // 注册处理器
BaseStreamProcessor getProcessor(String name)  // 获取指定名称的处理器
List<String> getAllProcessorNames()  // 获取所有处理器名称
List<BaseStreamProcessor> getAllProcessors()  // 获取所有处理器实例
int getProcessorCount()  // 获取处理器数量
boolean hasProcessor(String name)  // 检查处理器是否存在
List<BaseStreamProcessor.ProcessorStatus> getAllProcessorStatus()  // 获取所有处理器的状态信息
BaseStreamProcessor.ProcessorStatus getProcessorStatus(String name)  // 获取指定处理器的状态信息
ProcessorStatistics getStatistics()  // 获取处理器统计信息
```

#### StreamProcessorRegistry.ProcessorStatistics

`public record ProcessorStatistics(int totalProcessors, int totalInputTopics, int totalOutputTopics)`　处理器统计信息

**构造参数（record 组件）**

```java
int totalProcessors
int totalInputTopics
int totalOutputTopics
```

**方法**

```java
String toString()
```

## 包 `com.mcst.easyfk.mq.kafka.streams.serde`

### BaseMessageSerde

`public class BaseMessageSerde<T extends BaseMessage> implements Serde<T>`　注解：`@Slf4j` `@SuppressWarnings("all")`　BaseMessage 信封序列化器：value 为整个 BaseMessage（含 topic/messageId/data 等字段）的 JSON…

**构造器**

```java
BaseMessageSerde(Class<T> targetType)
BaseMessageSerde(Class<T> targetType, Type parseType)
```

**方法**

```java
static <D> BaseMessageSerde<CommonMessage<D>> commonMessageEnvelope(Class<D> dataType)  // 创建 data 为指定类型的 CommonMessage 信封 Serde
void configure(Map<String, ?> configs, boolean isKey)
void close()
Serializer<T> serializer()
Deserializer<T> deserializer()
```

#### BaseMessageSerde.BaseMessageSerializer

`public static class BaseMessageSerializer<T extends BaseMessage> implements Serializer<T>`　BaseMessage序列化器

**方法**

```java
void configure(Map<String, ?> configs, boolean isKey)
byte[] serialize(String topic, T data)
void close()
```

#### BaseMessageSerde.BaseMessageDeserializer

`public record BaseMessageDeserializer<T extends BaseMessage>(Class<T> targetType, Type parseType) implements Deserializer<T>`　BaseMessage反序列化器

**构造参数（record 组件）**

```java
Class<T> targetType
Type parseType
```

**方法**

```java
void configure(Map<String, ?> configs, boolean isKey)
T deserialize(String topic, byte[] data)
void close()
```

### CommonMessageSerde

`public class CommonMessageSerde<T> implements Serde<CommonMessage<T>>`　注解：`@Slf4j`　CommonMessage 的 Serde，与 KafkaProducer.syncSendMessage/asyncSendMessage（String 通道）格式兼容： value 只包含 data：String 原…

**构造器**

```java
CommonMessageSerde(Class<T> dataType)
```

**方法**

```java
Serializer<CommonMessage<T>> serializer()
Deserializer<CommonMessage<T>> deserializer()
```

#### CommonMessageSerde.CommonMessageSerializer

`public static class CommonMessageSerializer<T> implements Serializer<CommonMessage<T>>`

**方法**

```java
byte[] serialize(String topic, CommonMessage<T> message)
byte[] serialize(String topic, Headers headers, CommonMessage<T> message)
```

#### CommonMessageSerde.CommonMessageDeserializer

`public record CommonMessageDeserializer<T>(Class<T> dataType) implements Deserializer<CommonMessage<T>>`

**构造参数（record 组件）**

```java
Class<T> dataType
```

**方法**

```java
@SuppressWarnings("unchecked") CommonMessage<T> deserialize(String topic, byte[] data)
CommonMessage<T> deserialize(String topic, Headers headers, byte[] data)
```

### ProtobufMessageSerde

`public class ProtobufMessageSerde<T extends Message> implements Serde<ProtobufMessage<T>>`　注解：`@SuppressWarnings("unused")` `@Slf4j`　ProtobufMessage序列化器 专门用于处理包含Protobuf消息的ProtobufMessage对象…

**构造器**

```java
ProtobufMessageSerde(Class<T> protobufType)
```

**方法**

```java
void configure(Map<String, ?> configs, boolean isKey)
void close()
Serializer<ProtobufMessage<T>> serializer()
Deserializer<ProtobufMessage<T>> deserializer()
static <T extends Message> ProtobufMessageSerde<T> of(Class<T> protobufType)  // 创建指定Protobuf类型的Serde
```

#### ProtobufMessageSerde.ProtobufMessageSerializer

`public static class ProtobufMessageSerializer<T extends Message> implements Serializer<ProtobufMessage<T>>`　ProtobufMessage序列化器

**方法**

```java
void configure(Map<String, ?> configs, boolean isKey)
byte[] serialize(String topic, ProtobufMessage<T> data)
byte[] serialize(String topic, Headers headers, ProtobufMessage<T> data)
void close()
```

#### ProtobufMessageSerde.ProtobufMessageDeserializer

`public record ProtobufMessageDeserializer<T extends Message>(Class<T> protobufType) implements Deserializer<ProtobufMessage<T>>`　ProtobufMessage反序列化器

**构造参数（record 组件）**

```java
Class<T> protobufType
```

**方法**

```java
void configure(Map<String, ?> configs, boolean isKey)
ProtobufMessage<T> deserialize(String topic, byte[] data)
ProtobufMessage<T> deserialize(String topic, Headers headers, byte[] data)
void close()
```

### SerdeFactory

`public class SerdeFactory`　注解：`@SuppressWarnings("unused")`　Serde工厂类 提供统一的序列化器创建接口，简化Kafka Streams中的序列化配置

**方法**

```java
static <T extends BaseMessage> Serde<T> baseMessage(Class<T> messageType)  // 创建BaseMessage信封格式（value 为整个 BaseMessage 的 JSON）的Serde。 泛型 data 会被解析成 JSONObject…
static <T> Serde<CommonMessage<T>> commonMessageEnvelope(Class<T> dataType)  // 创建 CommonMessage 信封格式（value 为整个 CommonMessage 的 JSON）的Serde，data 按指定类型解析
static <T> Serde<CommonMessage<T>> jsonMessage(Class<T> dataType)  // 创建与 KafkaProducer String 通道（syncSendMessage/asyncSendMessage）兼容的 CommonMessage Serde： value 只含 data（JSON/字符串）…
static <T extends Message> Serde<ProtobufMessage<T>> protobufMessage(Class<T> protobufType)  // 创建ProtobufMessage的Serde（与 KafkaProducer Protobuf 通道兼容）
static Serde<String> string()  // 获取String类型的Serde
static Serde<Long> longValue()  // 获取Long类型的Serde
static Serde<Integer> integer()  // 获取Integer类型的Serde
static Serde<Double> doubleValue()  // 获取Double类型的Serde
static Serde<Float> floatValue()  // 获取Float类型的Serde
static Serde<byte[]> byteArray()  // 获取ByteArray类型的Serde
```

## 包 `com.mcst.easyfk.mq.kafka.util`

### KafkaMessageUtil

`public class KafkaMessageUtil`　注解：`@SuppressWarnings("unused")`

**方法**

```java
static <T> T getMessageBodyFromStringRecord(ConsumerRecord<String, String> record, Class<T> clazz)  // 从字符串类型的Kafka消费者记录中提取并解析消息体
static <T extends Message> T getMessageBodyFromByteRecord(ConsumerRecord<String, byte[]> record, Class<T> clazz)  // 从字节数组类型的Kafka消费者记录中提取并解析Protobuf消息体
static Map<String, String> extractHeaders(ConsumerRecord<String, ?> record)  // 提取消息头信息
static <T extends BaseMessage> KeyValue<String, T> extractKeyValue(T message)  // 从BaseMessage中提取键值对
static <T extends BaseMessage> KeyValueMapper<String, T, KeyValue<String, T>> baseMessageKeyValueMapper()  // BaseMessage到KeyValue的映射器
static <T> ValueMapper<CommonMessage<T>, T> jsonMessageDataExtractor()  // JsonMessage数据提取器
static <T extends Message> ValueMapper<ProtobufMessage<T>, T> protobufMessageDataExtractor()  // ProtobufMessage数据提取器
static <T extends BaseMessage> ValueMapper<T, String> topicExtractor()  // 消息主题提取器
static <T extends BaseMessage> ValueMapper<T, String> messageIdExtractor()  // 消息ID提取器
static <T extends BaseMessage> ValueMapper<T, Long> timestampExtractor()  // 消息时间戳提取器
static <T> ValueMapper<T, CommonMessage<T>> jsonMessageWrapper(String topic)  // 创建JsonMessage包装器
static <T extends Message> ValueMapper<T, ProtobufMessage<T>> protobufMessageWrapper(String topic)  // 创建ProtobufMessage包装器
static <T extends BaseMessage> org.apache.kafka.streams.kstream.Predicate<String, T> topicFilter(String targetTopic)  // 消息过滤器 - 按主题过滤
static <T extends BaseMessage> org.apache.kafka.streams.kstream.Predicate<String, T> timeRangeFilter(long startTime, long endTime)  // 消息过滤器 - 按时间范围过滤
static <T extends BaseMessage> KeyValueMapper<String, T, String> topicGrouper()  // 消息分组键提取器 - 按主题分组
static <T extends BaseMessage> KeyValueMapper<String, T, String> messageTypeGrouper()  // 消息分组键提取器 - 按消息类型分组
```

## 包 `com.mcst.easyfk.mq.rabbit.config`

### RabbitMqConfig

`public class RabbitMqConfig`　注解：`@Slf4j` `@AutoConfiguration` `@Import(RabbitAutoConfiguration.class)` `@EnableConfigurationProperties(RabbitMqProperties.class)` `@ConditionalOnProperty(prefix = "easyfk.config.mq.rabbit", name = "enable-rabbit", havingValue = "true")`

**方法**

```java
@Bean @ConditionalOnMissingBean MessageConverter jsonMessageConverter()  // 消息转换器，使用JSON格式
@Bean RabbitTemplateCustomizer easyfkRabbitTemplateCustomizer(RabbitMqProperties properties)  // 通过 Customizer 定制 Boot 创建的 RabbitTemplate（JSON 转换器由 Boot 自动取用 MessageConverter Bean）…
@Bean @ConditionalOnMissingBean RabbitProducer rabbitProducer()
@Bean @ConditionalOnMissingBean RabbitProducerHelper rabbitProducerHelper()
```

## 包 `com.mcst.easyfk.mq.rabbit.producer`

### RabbitProducer

`public class RabbitProducer`　注解：`@SuppressWarnings("unused")` `@Slf4j`

**方法**

```java
<T> void syncSendMessage(CommonMessage<T> commonMessage)  // 同步发送消息
<T> CompletableFuture<Void> asyncSendMessage(CommonMessage<T> commonMessage)  // 异步发送消息（使用 RabbitProducerHelper 的专用有界线程池）
```

### RabbitProducerHelper

`public class RabbitProducerHelper implements InitializingBean, DisposableBean`　注解：`@Slf4j`　RabbitMQ 发送底层封装。 异步发送使用本类独占的有界线程池（easyfk.config.mq.rabbit.async.*），队列满时由调用线程同步发送； 容器关闭时等待已提交任务发送完成…

**方法**

```java
void afterPropertiesSet()
void destroy()
void syncSendMessage(String exchange, String routingKey, Object message)  // 同步发送消息 同步发送是指发送方发送一条消息后，会等待服务器返回确认信息后再进行后续操作。这种方式适用于需要可靠性保证的场景。
void syncSendMessage(String exchange, String routingKey, Object message, CorrelationData correlationData)  // 同步发送消息（带correlationData）
CompletableFuture<Void> asyncSendMessage(String exchange, String routingKey, Object message)  // 异步发送消息 异步发送是指发送方发送一条消息后，不会等待服务器返回确认信息，而是直接返回。这种方式适用于需要快速响应的场景。
void sendDelayMessage(String exchange, String routingKey, Object message, long delayTime)  // 发送延迟消息 需要RabbitMQ安装rabbitmq_delayed_message_exchange插件
void sendDelayMessage(String exchange, String routingKey, Object message, long delayTime, MessageProperties messageProperties)  // 发送带消息属性的延迟消息
CompletableFuture<Void> asyncSendMessage(String exchange, String routingKey, Object message, MessageProperties messageProperties)  // 异步发送带消息属性的消息
CompletableFuture<Void> asyncSendDelayMessage(String exchange, String routingKey, Object message, long delayTime, MessageProperties messageProperties)  // 异步发送带消息属性的延迟消息
void sendMessageWithProperties(String exchange, String routingKey, Object message, MessageProperties messageProperties)  // 发送带消息属性的消息
void sendRawMessage(String exchange, String routingKey, Message message)  // 发送原生消息
```

## 包 `com.mcst.easyfk.mq.rabbit.properties`

### RabbitMqProperties

`public class RabbitMqProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.mq.rabbit")`

**字段 / 常量**

```java
Boolean enableRabbit = Boolean.FALSE  // 开启RabbitMQ消息队列
String exchange = "easyfk.direct.exchange"  // 默认Exchange名称
String delayExchange = "easyfk.delay.exchange"  // 延迟消息Exchange名称（需要安装rabbitmq_delayed_message_exchange插件）
Boolean confirmCallback = Boolean.FALSE  // 是否启用发布确认
Boolean returnCallback = Boolean.FALSE  // 是否启用返回回调（消息无法路由时触发）
Async async = new Async()  // 异步发送线程池配置
```

#### RabbitMqProperties.Async

`public static class Async`　Lombok：`@Data`

**字段 / 常量**

```java
Integer corePoolSize = 2  // 核心线程数
Integer maxPoolSize = 8  // 最大线程数
Integer queueCapacity = 10000  // 等待队列容量，队列满时由调用线程同步发送（背压，不丢消息）
Integer keepAliveSeconds = 60  // 非核心线程空闲存活时间（秒）
Integer awaitTerminationSeconds = 30  // 关闭时等待已提交任务发送完成的最长时间（秒）
```

## 包 `com.mcst.easyfk.mq.rabbit.util`

### RabbitMessageUtil

`public class RabbitMessageUtil`　RabbitMQ消息工具类 提供基于AMQP Message的消息头获取和消息体解析功能

**方法**

```java
@SuppressWarnings("unchecked") static <T> T getHeaderValue(Message message, String headerKey, Class<T> clazz)  // 从AMQP Message中获取消息头值
static String getMessageId(Message message)  // 获取消息ID
static Long getTimestamp(Message message)  // 获取消息时间戳
static byte[] getBody(Message message)  // 获取消息体内容（字节数组）
static String getBodyAsString(Message message)  // 获取消息体内容（字符串）
```

## 包 `com.mcst.easyfk.mq.rocket.config`

### RocketMqConfig

`public class RocketMqConfig`　注解：`@Slf4j` `@AutoConfiguration` `@Import(RocketMQAutoConfiguration.class)` `@EnableConfigurationProperties(RocketMqProperties.class)` `@ConditionalOnProperty(prefix = "easyfk.config.mq.rocket", name = "enable-rocket", havingValue = "true")`

**方法**

```java
@Bean @ConditionalOnMissingBean RocketProducer rocketMQProducer()
@Bean @ConditionalOnMissingBean RocketProducerHelper rocketProducerHelper()
```

## 包 `com.mcst.easyfk.mq.rocket.producer`

### RocketProducer

`public class RocketProducer`　注解：`@SuppressWarnings("unused")` `@Slf4j`

**方法**

```java
<T> SendResult syncSendMessage(CommonMessage<T> commonMessage)  // 同步发送消息
<T> void asyncSendMessage(CommonMessage<T> commonMessage)  // 异步发送消息
```

### RocketProducerHelper

`public class RocketProducerHelper`　注解：`@Slf4j`

**方法**

```java
<T> SendResult syncSendMessage(String topic, Message<T> message)  // 同步发送消息 同步发送是指发送方发送一条消息后，会等待服务器返回确认信息后再进行后续操作。这种方式适用于需要可靠性保证的场景。
<T> void asyncSendMessage(String topic, Message<T> message)  // 异步发送消息 异步发送是指发送方发送一条消息后，不会等待服务器返回确认信息，而是直接返回。这种方式适用于需要快速响应的场景。
<T> SendResult sendDelayMessage(String topic, Message<T> message, long delayTime)  // 同步发送延迟消息（任意毫秒延迟需要 RocketMQ 5.x Broker）
<T> void asyncSendDelayMessage(String topic, Message<T> message, long delayTime)  // 异步发送延迟消息（任意毫秒延迟需要 RocketMQ 5.x Broker）
<T> SendResult syncSendOrderlyMessage(String topic, Message<T> message, String hashKey)  // 发送顺序消息 顺序消息是指发送方发送多条消息时，这些消息会按照发送的顺序被消费者消费。 通过hashKey来确保相同业务ID的消息发送到同一个队列，从而保证消息的顺序性。
<T> void asyncSendOrderlyMessage(String topic, Message<T> message, String hashKey)  // 异步发送顺序消息 异步方式发送顺序消息，不会阻塞当前线程，适用于对响应时间要求较高的场景。
```

## 包 `com.mcst.easyfk.mq.rocket.properties`

### RocketMqProperties

`public class RocketMqProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.mq.rocket")`

**字段 / 常量**

```java
Boolean enableRocket = Boolean.FALSE  // 开启RocketMQ消息队列
```

## 包 `com.mcst.easyfk.mq.rocket.util`

### RocketMessageUtil

`public class RocketMessageUtil`　RocketMQ消息工具类 消费端推荐使用 RocketMQListener，配合本类的 MessageExt 方法读取 RocketProducer 写入的用户属性（messageId / sendTimestamp…

**方法**

```java
static <T> T getHeaderValue(Message<?> message, String headerKey, Class<T> clazz)  // 从Spring Message中获取消息头值
@SuppressWarnings("unchecked") static <T> T getHeaderValue(MessageExt message, String headerKey, Class<T> clazz)  // 从 MessageExt 中获取头值：先取用户属性，KEYS / TAGS 取消息系统属性； 字符串值按目标类型转换（支持 String / Long / Integer / Boolean），无法转换时返回 null
static String getMessageId(MessageExt message)  // 获取 RocketProducer 写入的业务消息ID（不是 Broker 生成的 msgId）
static Long getSendTimestamp(MessageExt message)  // 获取 RocketProducer 写入的发送时间戳（毫秒）
static String getKeys(MessageExt message)  // 获取消息 KEYS（RocketProducer 中为 messageKey）
static String getTags(MessageExt message)  // 获取消息 TAGS
static String getBodyAsString(MessageExt message)  // 以 UTF-8 读取消息体
@SuppressWarnings("unchecked") static <T> T getBody(MessageExt message, Class<T> clazz)  // 将消息体解析为目标类型：String 原样返回，其他类型按 JSON 解析 （RocketMQTemplate 默认以 JSON 序列化对象 payload）
```
