# mq-rocket 开发手册

## 1. 模块概述

`mq-rocket` 是 EasyFK 框架中基于 Apache RocketMQ 的消息队列组件。该模块基于 RocketMQ Spring Boot Starter，提供统一的消息发送 API（同步/异步）、三种消息类型（普通消息、延迟消息、顺序消息）、Tag 消息过滤、消息头自动注入，并与框架内 Kafka、RabbitMQ 组件共享 `CommonMessage` 消息模型，适用于高可靠消息传递、顺序消费、延迟任务、事件驱动等场景。

## 2. 依赖引入

### Maven

```xml
<dependency>
    <groupId>com.mcst</groupId>
    <artifactId>mq-rocket</artifactId>
</dependency>
```

### Gradle

```gradle
dependencies {
    implementation 'com.mcst:mq-rocket'
}
```

> 版本号由框架统一 BOM 管理，无需手动指定。

该模块会自动传递引入以下依赖：
- `rocketmq-spring-boot-starter` — RocketMQ Spring Boot 集成
- `mq-common` — EasyFK 通用消息模型（`CommonMessage`、`BaseMessage`）

## 3. 配置说明

### 3.1 启用模块

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `easyfk.config.mq.rocket.enable-rocket` | Boolean | `false` | 启用 RocketMQ（**必须设为 `true`**） |

### 3.2 基础配置示例

```yaml
easyfk:
  config:
    mq:
      rocket:
        enable-rocket: true

rocketmq:
  name-server: 192.168.1.100:9876
  producer:
    group: my-producer-group
    send-message-timeout: 3000
    retry-times-when-send-failed: 2
    retry-times-when-send-async-failed: 2
```

### 3.3 集群配置示例

```yaml
rocketmq:
  name-server: 192.168.1.100:9876;192.168.1.101:9876
  producer:
    group: order-producer-group
    send-message-timeout: 5000
    retry-times-when-send-failed: 3
    retry-times-when-send-async-failed: 3
    max-message-size: 4194304
    compress-message-body-threshold: 4096
```

### 3.4 生产者配置参考

| 属性 | 说明 |
|------|------|
| `rocketmq.name-server` | NameServer 地址（多个用 `;` 分隔） |
| `rocketmq.producer.group` | 生产者组名称 |
| `rocketmq.producer.send-message-timeout` | 发送超时时间（毫秒） |
| `rocketmq.producer.retry-times-when-send-failed` | 同步发送失败重试次数 |
| `rocketmq.producer.retry-times-when-send-async-failed` | 异步发送失败重试次数 |
| `rocketmq.producer.max-message-size` | 最大消息体大小（字节） |
| `rocketmq.producer.compress-message-body-threshold` | 消息压缩阈值（字节） |

## 4. 消息发送

### 4.1 注入 RocketProducer

```java
@Service
public class OrderService {

    @Resource
    private RocketProducer rocketProducer;
}
```

### 4.2 发送 API

| 方法 | 说明 |
|------|------|
| `syncSendMessage(message)` | 同步发送（阻塞等待 Broker 确认） |
| `asyncSendMessage(message)` | 异步发送（SendCallback 异步回调） |

两个方法均根据 `CommonMessage` 字段自动识别消息类型：

| 条件 | 消息类型 | 说明 |
|------|----------|------|
| `delayTime > 0` | 延迟消息 | 延迟指定毫秒后投递 |
| `messageKey` 不为空 | 顺序消息 | 相同 messageKey 保证顺序 |
| 其他 | 普通消息 | 标准投递 |

### 4.3 CommonMessage 消息结构

`CommonMessage<T>` 是消息载体，继承自 `BaseMessage`：

| 属性 | 类型 | RocketMQ 映射 | 说明 |
|------|------|---------------|------|
| `topic` | String | Topic | 目标 Topic |
| `data` | T (Serializable) | 消息体 | 消息数据 |
| `messageId` | String | Header: messageId | 消息 ID（为空时自动生成雪花 ID） |
| `messageKey` | String | hashKey（顺序消息） | 顺序消息路由键 |
| `tags` | String | Topic 后缀（`topic:tags`） | 消息标签，用于消费端过滤 |
| `sendTimestamp` | Long | Header: sendTimestamp | 发送时间戳（为空时自动填充） |
| `delayTime` | Long | 延迟时间（毫秒） | > 0 时自动发送延迟消息 |

### 4.4 Topic 与 Tag 映射规则

当设置了 `tags` 时，实际发送的 destination 为 `topic:tags` 格式：

```
topic = "order-topic", tags = "ORDER_CREATED"
→ 实际 destination = "order-topic:ORDER_CREATED"
```

消费端可通过 Tag 进行消息过滤，只接收指定 Tag 的消息。

## 5. 实战示例

### 5.1 同步发送普通消息

```java
CommonMessage<OrderDTO> message = new CommonMessage<>();
message.setTopic("order-topic");
message.setData(orderDTO);

rocketProducer.syncSendMessage(message);
```

### 5.2 异步发送普通消息

```java
CommonMessage<String> message = new CommonMessage<>();
message.setTopic("notification-topic");
message.setData("用户注册成功");

rocketProducer.asyncSendMessage(message);
```

### 5.3 发送带 Tag 的消息

```java
CommonMessage<OrderDTO> message = new CommonMessage<>();
message.setTopic("order-topic");
message.setData(orderDTO);
message.setTags("ORDER_CREATED");  // 消费端可按 Tag 过滤

rocketProducer.syncSendMessage(message);
// 实际 destination: order-topic:ORDER_CREATED
```

### 5.4 发送延迟消息

```java
CommonMessage<OrderDTO> message = new CommonMessage<>();
message.setTopic("order-topic");
message.setData(orderDTO);
message.setDelayTime(30 * 60 * 1000L);  // 30 分钟后投递

rocketProducer.syncSendMessage(message);
// 自动识别 delayTime > 0，调用 syncSendDelayTimeMills
```

### 5.5 发送顺序消息

相同 `messageKey` 的消息会被发送到同一个队列，保证消费顺序。

```java
String orderId = "ORD_001";

// 消息 1：创建订单
CommonMessage<String> msg1 = new CommonMessage<>();
msg1.setTopic("order-topic");
msg1.setData("订单创建");
msg1.setMessageKey(orderId);
rocketProducer.syncSendMessage(msg1);

// 消息 2：支付成功
CommonMessage<String> msg2 = new CommonMessage<>();
msg2.setTopic("order-topic");
msg2.setData("支付成功");
msg2.setMessageKey(orderId);
rocketProducer.syncSendMessage(msg2);

// 消息 3：发货完成
CommonMessage<String> msg3 = new CommonMessage<>();
msg3.setTopic("order-topic");
msg3.setData("发货完成");
msg3.setMessageKey(orderId);
rocketProducer.syncSendMessage(msg3);

// 三条消息按顺序消费：创建订单 → 支付成功 → 发货完成
```

### 5.6 消费普通消息

```java
@Component
@RocketMQMessageListener(
    topic = "order-topic",
    consumerGroup = "order-consumer-group"
)
public class OrderConsumer implements RocketMQListener<OrderDTO> {

    @Override
    public void onMessage(OrderDTO order) {
        // 处理订单
    }
}
```

### 5.7 消费带 Tag 过滤的消息

```java
@Component
@RocketMQMessageListener(
    topic = "order-topic",
    consumerGroup = "order-created-consumer-group",
    selectorExpression = "ORDER_CREATED || ORDER_PAID"  // 只消费指定 Tag
)
public class OrderCreatedConsumer implements RocketMQListener<OrderDTO> {

    @Override
    public void onMessage(OrderDTO order) {
        // 只处理 ORDER_CREATED 和 ORDER_PAID 标签的消息
    }
}
```

### 5.8 消费顺序消息

```java
@Component
@RocketMQMessageListener(
    topic = "order-topic",
    consumerGroup = "order-orderly-consumer-group",
    consumeMode = ConsumeMode.ORDERLY  // 顺序消费模式
)
public class OrderOrderlyConsumer implements RocketMQListener<String> {

    @Override
    public void onMessage(String message) {
        // 按顺序消费消息
    }
}
```

### 5.9 使用 RocketMessageUtil 获取消息头

```java
@Component
@RocketMQMessageListener(
    topic = "order-topic",
    consumerGroup = "order-consumer-group"
)
public class OrderConsumer implements RocketMQListener<Message<OrderDTO>> {

    @Override
    public void onMessage(Message<OrderDTO> message) {
        // 获取消息头
        String messageId = RocketMessageUtil.getHeaderValue(message, "messageId", String.class);
        Long timestamp = RocketMessageUtil.getHeaderValue(message, "sendTimestamp", Long.class);

        // 获取消息体
        OrderDTO order = message.getPayload();
    }
}
```

### 5.10 使用 RocketProducerHelper（底层 API）

```java
@Resource
private RocketProducerHelper rocketProducerHelper;

Message<OrderDTO> message = MessageBuilder.withPayload(orderDTO)
    .setHeader("customKey", "customValue")
    .build();

// 同步发送
rocketProducerHelper.syncSendMessage("order-topic", message);

// 异步发送
rocketProducerHelper.asyncSendMessage("order-topic", message);

// 延迟消息
rocketProducerHelper.sendDelayMessage("order-topic", message, 60000L);

// 同步顺序消息
rocketProducerHelper.syncSendOrderlyMessage("order-topic", message, "orderId-001");

// 异步顺序消息
rocketProducerHelper.asyncSendOrderlyMessage("order-topic", message, "orderId-001");
```

## 6. RocketProducerHelper API

| 方法 | 说明 |
|------|------|
| `syncSendMessage(topic, message)` | 同步发送普通消息 |
| `asyncSendMessage(topic, message)` | 异步发送普通消息 |
| `sendDelayMessage(topic, message, delayTime)` | 发送延迟消息（毫秒级精度） |
| `syncSendOrderlyMessage(topic, message, hashKey)` | 同步发送顺序消息 |
| `asyncSendOrderlyMessage(topic, message, hashKey)` | 异步发送顺序消息 |

## 7. RocketMessageUtil 工具类

| 方法 | 返回类型 | 说明 |
|------|----------|------|
| `getHeaderValue(message, key, clazz)` | `T` | 从 Spring Message 中获取指定类型的 Header 值 |

## 8. 消息类型决策流程

```
CommonMessage 传入
       │
       ├── delayTime > 0 ？
       │       └── 是 → 发送延迟消息（syncSendDelayTimeMills）
       │
       ├── messageKey 不为空 ？
       │       └── 是 → 发送顺序消息（syncSendOrderly / asyncSendOrderly）
       │
       └── 其他 → 发送普通消息（syncSend / asyncSend）
```

> 延迟消息优先级最高。当同时设置了 `delayTime` 和 `messageKey` 时，按延迟消息处理。

## 9. 自动配置机制

| 配置类 | 条件 | 说明 |
|--------|------|------|
| `RocketMqConfig` | `enable-rocket = true` | 核心自动配置 |

自动注册的 Bean：

| Bean 名称 | 类型 | 说明 |
|-----------|------|------|
| `rocketMQProducer` | `RocketProducer` | 消息生产者（核心 API） |
| `rocketProducerHelper` | `RocketProducerHelper` | 生产者辅助类（底层 API） |

所有 Bean 均支持 `@ConditionalOnMissingBean`，可自定义覆盖。`RocketMQTemplate` 由 `rocketmq-spring-boot-starter` 自动配置提供。

## 10. 包结构

```
com.mcst.easyfk.mq.rocket
├── config
│   └── RocketMqConfig.java              # 自动配置（注册 Producer Bean）
├── producer
│   ├── RocketProducer.java              # 消息生产者（核心 API：普通/延迟/顺序，同步/异步）
│   └── RocketProducerHelper.java        # 生产者辅助类（底层 RocketMQTemplate 封装）
├── properties
│   └── KafkaMqProperties.java           # 配置属性类（enable-rocket 开关）
└── util
    └── RocketMessageUtil.java           # 消息工具类（Header 获取）
```

## 11. 最佳实践

1. **合理使用消息类型**：
   - **普通消息**：无顺序要求的场景（通知、日志）
   - **顺序消息**：状态流转有先后关系的场景（订单状态变更）
   - **延迟消息**：需要定时触发的场景（订单超时取消）
2. **Tag 过滤**：同一 Topic 下使用 Tag 区分消息类别，消费端通过 `selectorExpression` 过滤，减少无效消费。
3. **顺序消息的 messageKey**：使用业务 ID（如订单号）作为 messageKey，确保同一业务的消息路由到同一队列。
4. **生产者组命名**：每个应用使用唯一的 producer group，避免冲突。
5. **消费者组命名**：每个消费场景使用独立的 consumer group。
6. **重试与超时**：生产环境建议适当增大 `send-message-timeout` 和重试次数。
7. **统一消息模型**：使用 `CommonMessage` 发送，便于在 Kafka / RabbitMQ 之间切换。
8. **消息幂等**：消费端必须做幂等处理，RocketMQ 默认 `at-least-once` 语义，可能重复投递。
