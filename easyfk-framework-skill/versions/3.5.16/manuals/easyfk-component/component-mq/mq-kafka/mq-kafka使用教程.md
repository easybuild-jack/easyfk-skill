# EasyFK Kafka消息队列使用教程

## 目录

1. [概述](#概述)
2. [组件架构](#组件架构)
3. [快速开始](#快速开始)
4. [详细使用指南](#详细使用指南)
5. [配置说明](#配置说明)
6. [消息消费](#消息消费)
7. [二进制与Protobuf消息](#二进制与protobuf消息)
8. [Kafka Streams](#kafka-streams)
9. [性能优化配置](#性能优化配置)
10. [最佳实践](#最佳实践)
11. [常见问题](#常见问题)

## 概述

EasyFK Kafka消息队列组件基于Spring
Kafka实现，提供了高吞吐量的消息发送解决方案。该组件与框架内其他MQ组件（RocketMQ、RabbitMQ）保持统一的API风格，并支持字符串消息、通用二进制消息、Protobuf消息以及Kafka
Streams流处理。

### 核心特性

- 📤 **统一API**：与RocketMQ、RabbitMQ保持一致的CommonMessage消息模型
- 🚀 **高吞吐量**：支持百万级TPS的消息处理能力
- 🗄 **多数据源**：支持同时连接多个Kafka集群，按数据源名称隔离生产者/消费者
- 📦 **二进制消息支持**：内置通用 `byte[]` 通道，同时支持 Protobuf 场景
- 🌊 **Kafka Streams**：支持流处理，实现实时数据处理
- 🔄 **同步/异步**：支持同步和异步两种发送模式（异步基于 `CompletableFuture` 回调）
- 🎯 **分区路由**：支持通过messageKey或指定partition进行分区路由
- ⚡ **幂等性**：支持生产者幂等性，防止消息重复
- 🧵 **分区并行消费**：提供 `AbstractKafkaPartitionConsumer` 模板基类，单poll线程+分区级worker并行处理

### Kafka核心概念

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Kafka Cluster                              │
│                                                                     │
│  ┌──────────┐         ┌───────────────────────────────────┐        │
│  │ Producer │ ──────► │             Topic                 │        │
│  └──────────┘         │  ┌─────────┐ ┌─────────┐ ┌─────────┐│       │
│                       │  │Partition│ │Partition│ │Partition││       │
│                       │  │    0    │ │    1    │ │    2    ││       │
│                       │  └─────────┘ └─────────┘ └─────────┘│       │
│                       └───────────────────────────────────┘        │
│                                      │                              │
│                       ┌──────────────┼──────────────┐              │
│                       ▼              ▼              ▼              │
│                 ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│                 │Consumer 1│  │Consumer 2│  │Consumer 3│           │
│                 └──────────┘  └──────────┘  └──────────┘           │
│                 └──────────── Consumer Group ───────────┘           │
└─────────────────────────────────────────────────────────────────────┘
```

| 概念                 | 说明                   |
|--------------------|----------------------|
| **Topic**          | 主题，消息的逻辑分类           |
| **Partition**      | 分区，Topic的物理分片，支持并行处理 |
| **Offset**         | 偏移量，消息在分区中的唯一标识      |
| **Consumer Group** | 消费者组，同组内消费者分摊消费分区    |
| **Broker**         | 服务节点，Kafka集群中的单个服务器  |
| **Replica**        | 副本，分区的备份，提供高可用       |

## 组件架构

```
mq-kafka/
├── client/                           # 多数据源客户端
│   └── KafkaClientRegistry.java     # 多数据源客户端注册表
├── config/                           # 配置类
│   ├── KafkaMqConfig.java           # 核心自动配置类
│   ├── KafkaDatasourceBeanRegistrar.java   # 多数据源Bean注册器
│   ├── KafkaDatasourceConfigSupport.java   # 数据源配置解析工具
│   └── KafkaStreamsConfig.java      # Kafka Streams配置
├── consumer/                         # 消费者模板
│   └── AbstractKafkaPartitionConsumer.java # 分区并行消费模板基类
├── producer/                         # 生产者
│   └── KafkaProducer.java           # 消息生产者（核心API）
├── properties/                       # 配置属性
│   └── KafkaMqProperties.java       # Kafka配置属性
├── streams/                          # Kafka Streams
│   ├── processor/                    # 流处理器
│   │   ├── BaseStreamProcessor.java
│   │   └── StreamProcessorRegistry.java
│   └── serde/                        # 序列化/反序列化
│       ├── BaseMessageSerde.java
│       ├── ProtobufMessageSerde.java
│       └── SerdeFactory.java
└── util/                             # 工具类
    └── KafkaMessageUtil.java        # 消息工具类
```

## 快速开始

### 1. 添加依赖

在您的项目的`build.gradle`中添加依赖：

```gradle
dependencies {
    implementation 'com.mcst.easyfk:mq-kafka'
}
```

### 2. 配置Kafka连接

在`application.yml`中配置Kafka连接信息：

```yaml
easyfk:
  config:
    mq:
      kafka:
        # 开启Kafka（必须设置为true）
        enable-kafka: true

spring:
  kafka:
    bootstrap-servers: 127.0.0.1:9092
    consumer:
      group-id: my-consumer-group
      auto-offset-reset: earliest
    producer:
      acks: all
```

### 3. 使用示例

```java
@Service
public class OrderService {
    
    @Resource
    private KafkaProducer kafkaProducer;
    
    public void sendOrderMessage(String orderId) {
        // 创建消息对象
        CommonMessage<OrderDTO> message = new CommonMessage<>();
        message.setTopic("order-topic");              // Topic名称
        message.setMessageKey(orderId);               // 消息Key（用于分区路由）
        message.setData(new OrderDTO(orderId, "商品A", 99.00));
        
        // 同步发送消息
        kafkaProducer.syncSendMessage(message);
    }
}
```

## 详细使用指南

### 核心API - KafkaProducer

`KafkaProducer`是消息发送的核心操作类，支持普通字符串消息、通用二进制消息和Protobuf消息：

#### 1. 同步发送消息

```java
@Resource
private KafkaProducer kafkaProducer;

public void syncSend() {
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("my-topic");           // Topic名称
    message.setMessageKey("order-123");     // 消息Key（可选，用于分区路由）
    message.setData("Hello Kafka");         // 消息体
    
    // 同步发送，等待发送完成（30秒超时）
    kafkaProducer.syncSendMessage(message);
}
```

#### 2. 异步发送消息

```java
public void asyncSend() {
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("my-topic");
    message.setMessageKey("order-456");
    message.setData("Hello Kafka Async");
    
    // 异步发送，立即返回
    kafkaProducer.asyncSendMessage(message);
}
```

#### 3. 指定分区发送

```java
public void sendToPartition() {
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("my-topic");
    message.setPartition(2);  // 指定发送到分区2
    message.setData("发送到指定分区");
    
    kafkaProducer.syncSendMessage(message);
}
```

#### 4. 发送带标签的消息

```java
public void sendWithTags() {
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("event-topic");
    message.setTags("user.login");  // 标签会添加到消息头中
    message.setData("用户登录事件");
    
    kafkaProducer.syncSendMessage(message);
}
```

#### 5. 发送带自定义属性的消息

```java
public void sendWithProperties() {
    CommonMessage<OrderDTO> message = new CommonMessage<>();
    message.setTopic("order-topic");
    message.setMessageKey("ORD001");
    message.setData(new OrderDTO("ORD001", "商品A", 99.00));
    
    // 设置自定义消息属性（会添加到Kafka Headers）
    Map<String, String> properties = new HashMap<>();
    properties.put("source", "web");
    properties.put("version", "v1.0");
    properties.put("traceId", "trace-12345");
    message.setProperties(properties);
    
    kafkaProducer.syncSendMessage(message);
}
```

#### 6. 发送二进制消息

```java
public void sendByteMessage() {
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("binary-topic");
    message.setMessageKey("binary-001");
    message.setData("Hello Binary");
    
    // 同步发送为byte[]消息
    kafkaProducer.syncSendMessageWithByte(message);
    
    // 异步发送为byte[]消息
    kafkaProducer.asyncSendMessageWithByte(message);
}
```

说明：

- `data` 为 `byte[]` 时会原样发送
- `data` 为 `String` 或基础类型时会按 UTF-8 转为 `byte[]`
- `data` 为复杂对象时会使用 `ForySerializer` 序列化后发送

#### 7. 发送Protobuf消息

```java
public void sendProtobuf() {
    // 假设有一个Protobuf定义的OrderProto消息
    OrderProto orderProto = OrderProto.newBuilder()
        .setOrderId("ORD001")
        .setProductName("商品A")
        .setPrice(99.00)
        .build();
    
    ProtobufMessage<OrderProto> message = new ProtobufMessage<>();
    message.setTopic("order-protobuf-topic");
    message.setMessageKey("ORD001");
    message.setData(orderProto);
    
    // 同步发送Protobuf消息
    kafkaProducer.syncSendProtobufMessage(message);
    
    // 异步发送Protobuf消息
    kafkaProducer.asyncSendProtobufMessage(message);
}
```

### CommonMessage字段说明

| 字段            | 类型      | 必填 | 说明          | Kafka映射     |
|---------------|---------|----|-------------|-------------|
| topic         | String  | 是  | 主题名称        | Topic       |
| data          | T       | 是  | 消息体数据       | Value       |
| messageKey    | String  | 否  | 业务键         | Key（用于分区路由） |
| partition     | Integer | 否  | 指定分区        | Partition   |
| tags          | String  | 否  | 消息标签        | Headers     |
| messageId     | String  | 否  | 消息ID（自动生成）  | Headers     |
| sendTimestamp | Long    | 否  | 发送时间戳（自动生成） | Headers     |
| properties    | Map     | 否  | 自定义扩展属性     | Headers     |

## 配置说明

### EasyFK配置

```yaml
easyfk:
  config:
    mq:
      kafka:
        # 开启Kafka消息队列（必须）
        enable-kafka: true
        
        # 是否开启Kafka Streams
        enable-streams: false
        
        # Kafka Streams配置
        streams:
          # 应用ID
          application-id: streams-app
          # Streams使用的数据源名称（可选，默认使用主数据源）
          datasource: default
          # 状态存储目录
          state-dir: /tmp/kafka-streams
          # 处理保证级别：at_least_once, exactly_once, exactly_once_v2
          processing-guarantee: at_least_once
          # 提交间隔（毫秒）
          commit-interval-ms: 30000
          # 状态存储缓存大小（字节）
          cache-max-bytes-buffering: 10485760
          # 流处理线程数
          num-stream-threads: 2
```

### 多数据源配置

组件支持同时连接多个 Kafka 集群。不配置 `datasources` 时进入**单数据源兼容模式**，自动使用
`spring.kafka.*` 构造名为 `default` 的数据源；配置了 `datasources` 后，以数据源级配置优先，未配置的项回退到
`spring.kafka.*` 或框架默认值。

```yaml
easyfk:
  config:
    mq:
      kafka:
        enable-kafka: true
        # 主数据源名称（默认 default），legacy Bean 名（kafkaTemplate 等）指向该数据源
        primary-datasource: default
        datasources:
          default:
            bootstrap-servers: 127.0.0.1:9092
            producer:
              acks: all
            consumer:
              group-id: my-group
          report:
            bootstrap-servers: 192.168.1.100:9092
            consumer:
              group-id: report-group
              ack-mode: manual
            # 附加原生客户端配置（同时作用于生产者和消费者）
            properties:
              security.protocol: SASL_PLAINTEXT
```

每个数据源会按 `<数据源名> + 后缀` 的命名规则注册一组 Bean：

| Bean 名称                                    | 类型                                        | 说明               |
|--------------------------------------------|-------------------------------------------|------------------|
| `<name>KafkaTemplate`                       | `KafkaTemplate<String, String>`           | 字符串消息模板          |
| `<name>ByteKafkaTemplate`                   | `KafkaTemplate<String, byte[]>`           | 二进制消息模板          |
| `<name>ProtobufKafkaTemplate`               | `KafkaTemplate<String, byte[]>`           | Protobuf消息模板     |
| `<name>ListenerContainerFactory`            | `ConcurrentKafkaListenerContainerFactory` | 字符串监听容器工厂        |
| `<name>ByteListenerContainerFactory`        | 同上                                        | 二进制监听容器工厂        |
| `<name>ProtobufListenerContainerFactory`    | 同上                                        | Protobuf监听容器工厂   |
| `<name>BatchListenerContainerFactory`       | 同上                                        | 字符串批量监听容器工厂      |
| `<name>BatchByteListenerContainerFactory`   | 同上                                        | 二进制批量监听容器工厂      |
| `<name>BatchProtobufListenerContainerFactory` | 同上                                      | Protobuf批量监听容器工厂 |

主数据源同时注册无前缀的 legacy 别名（`kafkaTemplate`、`byteKafkaTemplate`、`listenerContainerFactory`、
`batchListenerContainerFactory` 等），保证旧代码无需修改。

也可以通过 `KafkaClientRegistry` 按数据源名称获取模板：

```java
@Resource
private KafkaClientRegistry kafkaClientRegistry;

public void sendToReportCluster(String payload) {
    // 按数据源名称获取模板
    KafkaTemplate<String, String> template = kafkaClientRegistry.getStringTemplate("report");
    template.send("report-topic", payload);

    // 不带参数则使用主数据源
    kafkaClientRegistry.getByteTemplate().send("binary-topic", payload.getBytes(StandardCharsets.UTF_8));
}
```

消费端通过 `containerFactory` 指定数据源：

```java
@KafkaListener(
    topics = "report-topic",
    groupId = "report-group",
    containerFactory = "reportListenerContainerFactory"  // 使用 report 数据源
)
public void handleReportMessage(String message) {
    // ...
}
```

### Spring Kafka完整配置

> **取值规则**：easyfk 工厂的每项配置按 `easyfk.config.mq.kafka.datasources.<name>.producer/consumer.*` →
> Spring Boot 标准键 → 内置默认值 取值。只有 Boot 定义的键会被读取：`producer.acks/retries/batch-size/buffer-memory/compression-type`、
> `consumer.group-id/auto-offset-reset/enable-auto-commit/max-poll-records/heartbeat-interval/fetch-min-size/fetch-max-wait/auto-commit-interval/isolation-level`、
> `listener.concurrency/ack-mode`、`spring.kafka.properties.*`（仅单数据源兼容模式）。
> `linger-ms`、`enable-idempotence`、`max-in-flight-requests-per-connection`、`request-timeout-ms`、`delivery-timeout-ms`、
> `session-timeout-ms`、`max-poll-interval-ms`、`concurrency`、`ack-mode` 等 easyfk 扩展项只能写在
> `easyfk.config.mq.kafka.datasources.<name>.producer/consumer` 下（下面 yaml 中写在 `spring.kafka.*` 下的这几项对 easyfk 工厂无效，仅作参数说明）。
>
> **序列化器按通道固定**：String 通道 key/value 均为 String，Byte/Protobuf 通道 value 为 byte[]；
> `key-serializer` / `value-serializer` / `key-deserializer` / `value-deserializer` 以及 `properties` 中的同名项都不会生效，
> 这是为了保证 `kafkaTemplate` / `byteKafkaTemplate` 等 Bean 的泛型类型与实际编码一致。需要其他序列化方式请自定义 ProducerFactory/ConsumerFactory。

```yaml
spring:
  kafka:
    # Broker地址（多个用逗号分隔）
    bootstrap-servers: 127.0.0.1:9092,127.0.0.1:9093,127.0.0.1:9094
    
    # ==================== 生产者配置 ====================
    producer:
      # 确认模式：0不等待确认，1等待Leader确认，all等待所有ISR确认
      acks: all
      # 重试次数
      retries: 3
      # 批量发送大小（字节）
      batch-size: 16384
      # 发送延迟（毫秒），用于批量发送优化
      linger-ms: 5
      # 缓冲区大小（字节）
      buffer-memory: 33554432
      # 压缩类型：none, gzip, snappy, lz4, zstd
      compression-type: snappy
      # 开启幂等性
      enable-idempotence: true
      # 单连接最大未确认请求数
      max-in-flight-requests-per-connection: 5
      # 请求超时时间（毫秒）
      request-timeout-ms: 30000
      # 传输超时时间（毫秒）
      delivery-timeout-ms: 120000
    # ==================== 消费者配置 ====================
    consumer:
      # 消费者组ID
      group-id: default-group
      # 偏移量重置策略：earliest从头开始，latest从最新开始
      auto-offset-reset: earliest
      # 是否自动提交偏移量：默认 false，由监听容器在消息处理完成后提交（开启后可能先提交后处理，崩溃丢消息）
      enable-auto-commit: false
      # 自动提交间隔（毫秒）
      auto-commit-interval: 5000
      # 单次拉取最大记录数
      max-poll-records: 500
      # 会话超时时间（毫秒）
      session-timeout-ms: 30000
      # 心跳间隔（毫秒）
      heartbeat-interval-ms: 10000
      # 最小拉取字节数
      fetch-min-bytes: 1024
      # 最大等待时间（毫秒）
      fetch-max-wait-ms: 500
      # 事务隔离级别：read_uncommitted, read_committed
      isolation-level: read_committed
      # 两次poll的最大间隔（毫秒）
      max-poll-interval-ms: 300000

    # ==================== 监听容器配置 ====================
    listener:
      # 并发消费者数量（数据源未配置 consumer.concurrency 时使用）
      concurrency: 3
      # 提交模式：batch(默认，每批处理完提交), record, manual, manual_immediate, count, time, count_time
      ack-mode: batch
```

### 配置项详解

#### 生产者关键配置

| 配置项                  | 默认值    | 说明                      |
|----------------------|--------|-------------------------|
| `acks`               | all    | 消息确认模式，all最可靠           |
| `retries`            | 3      | 发送失败重试次数                |
| `batch-size`         | 16384  | 批量发送大小，增大可提高吞吐量         |
| `linger-ms`          | 5      | 发送延迟，配合batch-size优化批量发送 |
| `compression-type`   | snappy | 压缩算法，推荐snappy或lz4       |
| `enable-idempotence` | true   | 幂等性，防止重复发送              |

#### 消费者关键配置

| 配置项                  | 默认值      | 说明          |
|----------------------|----------|-------------|
| `group-id`           | -        | 消费者组ID，必须配置 |
| `auto-offset-reset`  | earliest | 偏移量重置策略     |
| `enable-auto-commit` | false    | 是否自动提交偏移量（默认由容器处理完后提交） |
| `max-poll-records`   | 500      | 单次拉取最大记录数   |
| `concurrency`        | 3        | 并发消费者数量（`datasources.<name>.consumer.concurrency` 或 `spring.kafka.listener.concurrency`） |
| `ack-mode`           | batch    | 提交模式（`datasources.<name>.consumer.ack-mode` 或 `spring.kafka.listener.ack-mode`） |

## 消息消费

### 基本消费者

```java
@Component
@Slf4j
public class OrderConsumer {
    
    @KafkaListener(topics = "order-topic", groupId = "order-consumer-group")
    public void handleOrderMessage(String message) {
        log.info("收到订单消息: {}", message);
        // 处理业务逻辑
        processOrder(message);
    }
}
```

### 消费JSON对象

```java
@Component
public class UserConsumer {
    
    @KafkaListener(
        topics = "user-topic",
        groupId = "user-consumer-group",
        containerFactory = "listenerContainerFactory"
    )
    public void handleUserMessage(@Payload String payload,
                                   @Header(KafkaHeaders.RECEIVED_TOPIC) String topic,
                                   @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
                                   @Header(KafkaHeaders.OFFSET) long offset,
                                   @Header(KafkaHeaders.RECEIVED_KEY) String key) {
        log.info("收到消息，topic: {}, partition: {}, offset: {}, key: {}", 
                 topic, partition, offset, key);
        
        // 反序列化JSON
        UserDTO user = JSONObject.parseObject(payload, UserDTO.class);
        processUser(user);
    }
}
```

### 手动确认消费

```java
@Component
public class ManualAckConsumer {
    
    @KafkaListener(
        topics = "order-topic",
        groupId = "manual-ack-group",
        containerFactory = "listenerContainerFactory"
    )
    public void handleWithManualAck(String message, Acknowledgment ack) {
        try {
            log.info("收到消息: {}", message);
            // 处理业务逻辑
            processMessage(message);
            // 手动确认
            ack.acknowledge();
        } catch (Exception e) {
            log.error("处理消息失败", e);
            // 不确认，消息会被重新消费
        }
    }
}
```

配置手动确认模式：

```yaml
spring:
  kafka:
    listener:
      ack-mode: manual
# 或按数据源配置：easyfk.config.mq.kafka.datasources.<name>.consumer.ack-mode: manual
```

> 说明：当 `ack-mode` 配置为 `manual`、`manual_immediate`、`record`、`count`、`time`、`count_time`
> 等由监听容器管理提交的模式时，组件会自动将 `enable.auto.commit` 关闭（即使配置为 true）并输出 WARN 日志，
> 避免客户端自动提交与容器提交互相冲突。

### 批量消费

```java
@Component
public class BatchConsumer {
    
    @KafkaListener(
        topics = "batch-topic",
        groupId = "batch-consumer-group",
        containerFactory = "batchListenerContainerFactory"
    )
    public void handleBatch(List<String> messages, Acknowledgment ack) {
        log.info("批量收到消息，数量: {}", messages.size());
        
        try {
            for (String message : messages) {
                processMessage(message);
            }
            ack.acknowledge();
        } catch (Exception e) {
            log.error("批量处理失败", e);
        }
    }
}
```

批量消费配置：

```java
@Bean
public ConcurrentKafkaListenerContainerFactory<String, String> batchListenerContainerFactory() {
    ConcurrentKafkaListenerContainerFactory<String, String> factory = 
        new ConcurrentKafkaListenerContainerFactory<>();
    factory.setConsumerFactory(consumerFactory());
    factory.setBatchListener(true);  // 开启批量消费
    factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL);
    return factory;
}
```

### 消费二进制/Protobuf消息

```java
@Component
public class ByteConsumer {
    
    @KafkaListener(
        topics = "binary-topic",
        groupId = "binary-consumer-group",
        containerFactory = "byteListenerContainerFactory"
    )
    public void handleBytes(byte[] data) {
        log.info("收到二进制消息，长度: {}", data.length);
    }
}
```

消费 Protobuf 消息时也复用同一个 `byteListenerContainerFactory`：

```java
@Component
public class ProtobufConsumer {
    
    @KafkaListener(
        topics = "order-protobuf-topic",
        groupId = "protobuf-consumer-group",
        containerFactory = "byteListenerContainerFactory"
    )
    public void handleProtobuf(byte[] data) {
        try {
            // 反序列化Protobuf
            OrderProto order = ProtobufUtils.deserialize(data, OrderProto.class);
            log.info("收到Protobuf订单: {}", order);
            processOrder(order);
        } catch (Exception e) {
            log.error("Protobuf反序列化失败", e);
        }
    }
}
```

### 分区并行消费模板（AbstractKafkaPartitionConsumer）

面向低延迟、高吞吐场景（如行情推送），组件提供了 `AbstractKafkaPartitionConsumer` 模板基类：
单个 poll 线程拉取消息，按分区分发给独立的 worker 线程处理，同分区严格串行、不同分区并行。

> ⚠️ **重要：该基类是 at-most-once（至多一次）语义。** 消息分发到 worker 队列后立即异步提交
> offset（先提交、后处理），且 worker 队列满时会丢弃整批消息。进程崩溃或消费积压时可能丢消息。
> 需要 at-least-once 语义的业务请使用 `@KafkaListener` 配合手动 ack，不要使用该基类。

```java
@Component
public class QuoteConsumer extends AbstractKafkaPartitionConsumer {

    @Resource(name = "byteConsumerFactory")
    private ConsumerFactory<String, byte[]> consumerFactory;

    @Override
    protected String getTopic() {
        return "quote-topic";
    }

    @Override
    protected ConsumerFactory<String, byte[]> getConsumerFactory() {
        return consumerFactory;
    }

    @Override
    protected String getConsumerName() {
        return "quote";
    }

    @Override
    protected void processMessage(byte[] value, TopicPartition partition) {
        // 同分区消息严格串行，无需考虑线程安全与 offset 提交
        QuoteProto quote = ProtobufUtils.deserialize(value, QuoteProto.class);
        updateLocalCache(quote);
    }
}
```

可选扩展点：

| 方法                          | 默认值      | 说明                                  |
|------------------------------|-----------|-------------------------------------|
| `getPollTimeout()`           | 10ms      | poll 超时，低延迟场景保持默认，普通场景可调大           |
| `getWorkerQueueCapacity()`   | 5000 批次  | worker 队列容量，队满丢弃整批并打 WARN            |
| `getGroupId()`               | null      | 返回非 null 时覆盖 ConsumerFactory 的 group.id |
| `getAutoOffsetReset()`       | null      | 返回非 null 时覆盖 auto.offset.reset（如重放场景） |
| `onPartitionsAssignedHook()` | 空实现      | 分区分配后回调，可用于预热缓存                    |
| `onPartitionsRevokedHook()`  | 空实现      | 分区撤销后回调，可用于持久化本地状态                 |

## 二进制与Protobuf消息

### Protobuf优势

- **更小的体积**：比JSON序列化小3-10倍
- **更快的速度**：序列化/反序列化速度快20-100倍
- **强类型**：编译时类型检查，减少运行时错误
- **向前/向后兼容**：支持字段的增删改

### 定义Protobuf消息

```protobuf
// order.proto
syntax = "proto3";
package com.mcst.easyfk.proto;

message OrderProto {
    string order_id = 1;
    string product_name = 2;
    double price = 3;
    int32 quantity = 4;
    int64 create_time = 5;
}
```

### 发送Protobuf消息

```java
@Service
public class ProtobufOrderService {
    
    @Resource
    private KafkaProducer kafkaProducer;
    
    public void sendProtobufOrder(String orderId, String productName, double price) {
        OrderProto orderProto = OrderProto.newBuilder()
            .setOrderId(orderId)
            .setProductName(productName)
            .setPrice(price)
            .setQuantity(1)
            .setCreateTime(System.currentTimeMillis())
            .build();
        
        ProtobufMessage<OrderProto> message = new ProtobufMessage<>();
        message.setTopic("order-protobuf-topic");
        message.setMessageKey(orderId);
        message.setData(orderProto);
        
        kafkaProducer.syncSendProtobufMessage(message);
    }
}
```

## Kafka Streams

### 启用Kafka Streams

```yaml
easyfk:
  config:
    mq:
      kafka:
        enable-kafka: true
        enable-streams: true
        streams:
          application-id: my-streams-app
          num-stream-threads: 2
```

### 自定义流处理器

```java
@Component
public class OrderStreamProcessor extends BaseStreamProcessor {

    @Override
    protected String getProcessorName() {
        return "order-processor";
    }

    @Override
    protected String[] getInputTopics() {
        return new String[]{"order_topic"};
    }

    @Override
    protected String[] getOutputTopics() {
        return new String[]{"high_value_order_topic", "order_count_topic"};
    }

    @Override
    protected void buildTopology(StreamsBuilder builder) {
        // 默认 value serde 是 ByteArray，必须显式指定；jsonMessage(OrderDTO.class) 读取 KafkaProducer.syncSendMessage 发出的消息
        KStream<String, CommonMessage<OrderDTO>> orders = builder.stream("order_topic",
                Consumed.with(Serdes.String(), SerdeFactory.jsonMessage(OrderDTO.class)));

        // 过滤金额大于100的订单，输出格式仍与 KafkaProducer 一致（value 只含 data，元数据在 headers）
        orders.filter((key, msg) -> msg != null && msg.getData().getPrice() > 100)
              .to("high_value_order_topic", Produced.with(Serdes.String(), SerdeFactory.jsonMessage(OrderDTO.class)));

        // 统计订单数量（按 key 分组，count 结果为 Long）
        orders.groupByKey(Grouped.with(Serdes.String(), SerdeFactory.jsonMessage(OrderDTO.class)))
              .count(Materialized.as("order-count-store"))
              .toStream()
              .to("order_count_topic", Produced.with(Serdes.String(), Serdes.Long()));
    }
}
```

> Streams 使用 `streams.datasource`（为空时主数据源）的 `bootstrap-servers` 与 `properties`（安全认证等）；
> `streams.auto-offset-reset` / `session-timeout-ms` / `heartbeat-interval-ms` 可配置，`streams.properties` 可追加任意原生配置。

## 性能优化配置

### 1. 生产者优化

```yaml
spring:
  kafka:
    producer:
      # 增大批量发送大小
      batch-size: 65536
      # 增加发送延迟以聚合更多消息
      linger-ms: 20
      # 增大缓冲区
      buffer-memory: 67108864
      # 使用高效压缩
      compression-type: lz4
      # 确保幂等性
      enable-idempotence: true
      acks: all
```

### 2. 消费者优化

```yaml
spring:
  kafka:
    consumer:
      # 增加单次拉取数量
      max-poll-records: 1000
      # 增加最小拉取字节数
      fetch-min-bytes: 10240
      # 适当增加等待时间
      fetch-max-wait: 1000ms
    listener:
      # 增加并发数
      concurrency: 10
      # 手动提交获得更好控制
      ack-mode: manual_immediate
```

### 3. 批量发送

```java
public void batchSend(List<OrderDTO> orders) {
    for (OrderDTO order : orders) {
        CommonMessage<OrderDTO> message = new CommonMessage<>();
        message.setTopic("order-topic");
        message.setMessageKey(order.getOrderId());
        message.setData(order);
        
        // 异步发送提高吞吐量
        kafkaProducer.asyncSendMessage(message);
    }
}
```

### 4. 分区策略优化

```java
// 使用messageKey确保相同业务ID的消息发送到同一分区
public void sendWithPartitionKey(String orderId, OrderDTO order) {
    CommonMessage<OrderDTO> message = new CommonMessage<>();
    message.setTopic("order-topic");
    message.setMessageKey(orderId);  // 相同orderId会发送到同一分区
    message.setData(order);
    
    kafkaProducer.syncSendMessage(message);
}
```

### 性能优化建议总结

| 优化项              | 建议值        | 说明                |
|------------------|------------|-------------------|
| batch-size       | 32KB-64KB  | 增大可提高吞吐量          |
| linger-ms        | 10-50ms    | 配合batch-size使用    |
| compression-type | lz4/snappy | lz4速度快，snappy压缩比好 |
| max-poll-records | 500-2000   | 根据消息大小调整          |
| concurrency      | CPU核心数*2   | 不要超过分区数           |
| acks             | all        | 高可靠场景必须设置         |

## 最佳实践

### 1. Topic命名规范

```java
// ✅ 推荐：语义清晰、层级分明
String topic = "order-create-topic";
String topic = "user-login-event";
String topic = "payment-success-notify";

// ❌ 不推荐：含义模糊
String topic = "topic1";
String topic = "data";
```

### 2. 消息Key设计

```java
// ✅ 使用业务ID作为Key，保证顺序性
message.setMessageKey(orderId);

// ✅ 组合Key
message.setMessageKey(userId + ":" + orderId);

// ❌ 不设置Key会导致随机分区，无法保证顺序
message.setMessageKey(null);
```

### 3. 消息幂等性处理

```java
@Component
public class IdempotentConsumer {
    
    @Resource
    private StringRedisTemplate redisTemplate;
    
    @KafkaListener(topics = "order-topic", groupId = "idempotent-group")
    public void handleOrder(String message,
                            @Header(MessageHeaderConstants.MESSAGE_ID) String messageId,
                            Acknowledgment ack) {
        // 幂等性检查
        String lockKey = "kafka:consumed:" + messageId;
        Boolean success = redisTemplate.opsForValue().setIfAbsent(lockKey, "1", 24, TimeUnit.HOURS);
        
        if (Boolean.FALSE.equals(success)) {
            log.warn("消息已处理，messageId: {}", messageId);
            ack.acknowledge();
            return;
        }
        
        try {
            processOrder(message);
            ack.acknowledge();
        } catch (Exception e) {
            redisTemplate.delete(lockKey);
            throw e;
        }
    }
}
```

### 4. 异常处理

```java
@AutoConfiguration
public class KafkaErrorHandlerConfig {
    
    @Bean
    public DefaultErrorHandler errorHandler() {
        // 配置重试策略
        FixedBackOff fixedBackOff = new FixedBackOff(1000L, 3);
        
        DefaultErrorHandler errorHandler = new DefaultErrorHandler(
            (record, exception) -> {
                // 重试失败后的处理
                log.error("消息处理失败，发送到死信队列，topic: {}, partition: {}, offset: {}",
                    record.topic(), record.partition(), record.offset(), exception);
                // 发送到死信队列
                sendToDeadLetterQueue(record);
            },
            fixedBackOff
        );
        
        // 不重试的异常类型
        errorHandler.addNotRetryableExceptions(IllegalArgumentException.class);
        
        return errorHandler;
    }
}
```

### 5. 消息顺序性保证

```java
// 确保相同业务ID的消息发送到同一分区
public void sendOrderedMessages(String orderId, List<String> events) {
    for (String event : events) {
        CommonMessage<String> message = new CommonMessage<>();
        message.setTopic("order-event-topic");
        message.setMessageKey(orderId);  // 使用orderId作为Key
        message.setData(event);
        
        // 同步发送确保顺序
        kafkaProducer.syncSendMessage(message);
    }
}

// 消费端：使用单线程消费
@KafkaListener(topics = "order-event-topic", concurrency = "1")
public void handleOrderEvent(String message) {
    // 单线程消费保证顺序
}
```

### 6. 事务消息

```java
@AutoConfiguration
public class KafkaTransactionConfig {
    
    @Bean
    public KafkaTransactionManager<String, String> kafkaTransactionManager(
            ProducerFactory<String, String> producerFactory) {
        return new KafkaTransactionManager<>(producerFactory);
    }
}

@Service
public class TransactionalService {
    
    @Resource
    private KafkaTemplate<String, String> kafkaTemplate;
    
    @Transactional("kafkaTransactionManager")
    public void sendWithTransaction(List<String> messages) {
        for (String message : messages) {
            kafkaTemplate.send("tx-topic", message);
        }
        // 事务提交后消息才可见
    }
}
```

## 常见问题

### 1. 消息发送失败

**问题现象**：发送消息时抛出TimeoutException

**排查步骤**：

```java
// 1. 检查Broker连接
// 2. 检查Topic是否存在
// 3. 增加超时时间
spring:
  kafka:
    producer:
      request-timeout-ms: 60000
      delivery-timeout-ms: 120000
```

### 2. 消息重复消费

**解决方案**：

1. 开启幂等性处理（见最佳实践第3条）
2. 使用数据库唯一约束
3. 使用Redis分布式锁

### 3. 消费者Rebalance频繁

**解决方案**：

```yaml
spring:
  kafka:
    consumer:
      # 增加session超时时间
      session-timeout-ms: 45000
      # 减少心跳间隔
      heartbeat-interval-ms: 15000
      # 增加poll间隔
      max-poll-interval-ms: 600000
      # 减少单次拉取数量
      max-poll-records: 100
```

### 4. 消息积压

**解决方案**：

```yaml
spring:
  kafka:
    listener:
      # 增加并发数（不超过分区数）
      concurrency: 20
    consumer:
      # 增加单次拉取数量
      max-poll-records: 1000
```

### 5. 消息丢失

**解决方案**：

```yaml
spring:
  kafka:
    producer:
      acks: all                    # 等待所有ISR确认
      enable-idempotence: true     # 开启幂等性
      retries: 3                   # 重试次数
    consumer:
      enable-auto-commit: false    # 关闭自动提交（组件默认即为 false）
    listener:
      ack-mode: manual             # 手动确认
```

### 6. Lag过高

**排查步骤**：

```bash
# 查看消费者Lag
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group my-consumer-group
```

**解决方案**：

1. 增加消费者数量（不超过分区数）
2. 优化消费处理逻辑
3. 增加分区数

## 版本信息

- **组件版本**：mq-kafka
- **依赖版本**：Spring Kafka 3.x、kafka-streams 3.9.x（版本由 Spring Boot 3.5 管理）
- **兼容性**：Spring Boot 3.x（异步发送基于 `CompletableFuture` 回调）
- **Kafka版本**：2.8+

## 附录：三种MQ对比

| 特性       | Kafka  | RocketMQ | RabbitMQ |
|----------|--------|----------|----------|
| **吞吐量**  | 百万级TPS | 十万级TPS   | 万级TPS    |
| **延迟**   | 毫秒级    | 毫秒级      | 微秒级      |
| **消息堆积** | 亿级     | 亿级       | 百万级      |
| **顺序消息** | 分区内有序  | 队列内有序    | 队列内有序    |
| **延迟消息** | 不支持    | 原生支持     | 插件支持     |
| **事务消息** | 支持     | 支持       | 不支持      |
| **适用场景** | 大数据、日志 | 电商、金融    | 企业应用     |

## 技术支持

如遇到使用问题，请联系技术支持团队或查阅相关文档。
