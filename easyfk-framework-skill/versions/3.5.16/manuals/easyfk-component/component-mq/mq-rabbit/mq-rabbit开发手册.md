# mq-rabbit 开发手册

## 1. 模块概述

`mq-rabbit` 是 EasyFK 框架中基于 RabbitMQ 的消息队列组件。该模块基于 Spring AMQP，提供统一的消息发送 API（同步/异步）、延迟消息支持（基于 `rabbitmq_delayed_message_exchange` 插件）、Jackson JSON 自动序列化、发布确认与返回回调机制，并与框架内 Kafka、RocketMQ 组件共享 `CommonMessage` 消息模型，适用于微服务解耦、异步通信、延迟任务、事件驱动等场景。

## 2. 依赖引入

### Maven

```xml
<dependency>
    <groupId>com.mcst</groupId>
    <artifactId>mq-rabbit</artifactId>
</dependency>
```

### Gradle

```gradle
dependencies {
    implementation 'com.mcst:mq-rabbit'
}
```

> 版本号由框架统一 BOM 管理，无需手动指定。

该模块会自动传递引入以下依赖：
- `spring-boot-starter-amqp` — Spring AMQP 集成
- `mq-common` — EasyFK 通用消息模型（`CommonMessage`、`BaseMessage`）

## 3. 配置说明

### 3.1 启用模块

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `easyfk.config.mq.rabbit.enable-rabbit` | Boolean | `false` | 启用 RabbitMQ（**必须设为 `true`**） |
| `easyfk.config.mq.rabbit.exchange` | String | `easyfk.direct.exchange` | 默认 Exchange 名称 |
| `easyfk.config.mq.rabbit.delay-exchange` | String | `easyfk.delay.exchange` | 延迟消息 Exchange 名称 |
| `easyfk.config.mq.rabbit.confirm-callback` | Boolean | `false` | 是否启用发布确认回调 |
| `easyfk.config.mq.rabbit.return-callback` | Boolean | `false` | 是否启用返回回调（消息无法路由时触发） |

### 3.2 基础配置示例

```yaml
easyfk:
  config:
    mq:
      rabbit:
        enable-rabbit: true
        exchange: my-app.direct.exchange
        delay-exchange: my-app.delay.exchange
        confirm-callback: true
        return-callback: true

spring:
  rabbitmq:
    host: 192.168.1.100
    port: 5672
    username: guest
    password: guest
    virtual-host: /
```

### 3.3 生产环境配置示例

```yaml
easyfk:
  config:
    mq:
      rabbit:
        enable-rabbit: true
        exchange: order.direct.exchange
        delay-exchange: order.delay.exchange
        confirm-callback: true
        return-callback: true

spring:
  rabbitmq:
    host: mq-cluster.internal
    port: 5672
    username: ${RABBIT_USER}
    password: ${RABBIT_PASSWORD}
    virtual-host: /production
    publisher-confirm-type: correlated
    publisher-returns: true
    listener:
      simple:
        acknowledge-mode: manual
        prefetch: 10
        concurrency: 5
        max-concurrency: 20
    connection-timeout: 10000
```

## 4. 消息发送

### 4.1 注入 RabbitProducer

```java
@Service
public class OrderService {

    @Resource
    private RabbitProducer rabbitProducer;
}
```

### 4.2 发送 API

| 方法 | 说明 |
|------|------|
| `syncSendMessage(message)` | 同步发送（阻塞等待 Broker 确认） |
| `asyncSendMessage(message)` | 异步发送（CompletableFuture 异步执行） |

两个方法均自动识别延迟消息：当 `CommonMessage.delayTime > 0` 时，自动路由到延迟交换机。

### 4.3 CommonMessage 消息结构

`CommonMessage<T>` 是消息载体，继承自 `BaseMessage`：

| 属性 | 类型 | RabbitMQ 映射 | 说明 |
|------|------|---------------|------|
| `topic` | String | Exchange 名称 | 为空时使用默认 Exchange |
| `data` | T (Serializable) | 消息体 | 消息数据（Jackson JSON 自动序列化） |
| `messageId` | String | MessageProperties.messageId | 消息 ID（为空时自动生成雪花 ID） |
| `messageKey` | String | RoutingKey（优先） | 分区路由键 |
| `tags` | String | RoutingKey（次选）/ Header | 消息标签 |
| `sendTimestamp` | Long | MessageProperties.timestamp | 发送时间戳（为空时自动填充） |
| `delayTime` | Long | x-delay Header | 延迟时间（毫秒），> 0 时走延迟交换机 |
| `properties` | Map | Headers | 自定义 Header 属性 |

### 4.4 消息映射规则

**Exchange 选择逻辑：**
1. `delayTime > 0` → 使用 `delayExchange`（延迟交换机）
2. `topic` 不为空 → 使用 `topic` 作为 Exchange
3. 都为空 → 使用默认 `exchange`（配置文件中指定）

**RoutingKey 选择逻辑：**
1. `messageKey` 不为空 → 使用 `messageKey`
2. `tags` 不为空 → 使用 `tags`
3. 都为空 → 空字符串 `""`

## 5. 实战示例

### 5.1 同步发送普通消息

```java
CommonMessage<OrderDTO> message = new CommonMessage<>();
message.setTopic("order.direct.exchange");
message.setData(orderDTO);
message.setMessageKey("order.created");
message.setTags("ORDER_CREATED");

rabbitProducer.syncSendMessage(message);
```

### 5.2 异步发送普通消息

```java
CommonMessage<String> message = new CommonMessage<>();
message.setTopic("notification.fanout.exchange");
message.setData("用户注册成功");
message.setMessageKey("user.registered");

rabbitProducer.asyncSendMessage(message);
```

### 5.3 发送延迟消息

延迟消息需要 RabbitMQ 安装 `rabbitmq_delayed_message_exchange` 插件。

```java
CommonMessage<OrderDTO> message = new CommonMessage<>();
message.setData(orderDTO);
message.setMessageKey("order.timeout.check");
message.setDelayTime(30 * 60 * 1000L);  // 30 分钟后发送

rabbitProducer.syncSendMessage(message);
// 自动识别 delayTime > 0，路由到延迟交换机
```

### 5.4 自定义 Header 属性

```java
CommonMessage<String> message = new CommonMessage<>();
message.setTopic("event.topic.exchange");
message.setData("event data");
message.setTags("USER_EVENT");

Map<String, String> props = new HashMap<>();
props.put("source", "order-service");
props.put("traceId", "trace_12345");
message.setProperties(props);

rabbitProducer.syncSendMessage(message);
```

### 5.5 消费消息

```java
@Component
public class OrderConsumer {

    @RabbitListener(queues = "order-queue")
    public void onMessage(OrderDTO order) {
        // Jackson 自动反序列化为 OrderDTO
        // 处理订单
    }
}
```

### 5.6 消费原生 Message（获取 Header）

```java
@Component
public class OrderConsumer {

    @RabbitListener(queues = "order-queue")
    public void onMessage(Message message) {
        // 获取消息 ID
        String messageId = RabbitMessageUtil.getMessageId(message);

        // 获取时间戳
        Long timestamp = RabbitMessageUtil.getTimestamp(message);

        // 获取自定义 Header
        String traceId = RabbitMessageUtil.getHeaderValue(message, "traceId", String.class);

        // 获取消息体
        String body = RabbitMessageUtil.getBodyAsString(message);
    }
}
```

### 5.7 使用 RabbitProducerHelper（底层 API）

`RabbitProducerHelper` 提供更底层的发送方法，适用于需要精细控制的场景：

```java
@Resource
private RabbitProducerHelper rabbitProducerHelper;

// 同步发送
rabbitProducerHelper.syncSendMessage("my-exchange", "my-routing-key", data);

// 同步发送（带关联数据）
CorrelationData correlationData = new CorrelationData("unique-id");
rabbitProducerHelper.syncSendMessage("my-exchange", "my-routing-key", data, correlationData);

// 异步发送
rabbitProducerHelper.asyncSendMessage("my-exchange", "my-routing-key", data);

// 延迟消息
rabbitProducerHelper.sendDelayMessage("delay-exchange", "my-routing-key", data, 60000L);

// 带自定义属性发送
MessageProperties props = new MessageProperties();
props.setMessageId("msg-001");
props.setHeader("customKey", "customValue");
rabbitProducerHelper.sendMessageWithProperties("my-exchange", "my-routing-key", data, props);

// 发送原生消息
Message rawMessage = new Message(body, messageProperties);
rabbitProducerHelper.sendRawMessage("my-exchange", "my-routing-key", rawMessage);
```

## 6. RabbitMessageUtil 工具类

| 方法 | 返回类型 | 说明 |
|------|----------|------|
| `getHeaderValue(message, key, clazz)` | `T` | 获取 Header 值（支持类型转换） |
| `getMessageId(message)` | `String` | 获取消息 ID |
| `getTimestamp(message)` | `Long` | 获取时间戳（毫秒） |
| `getBody(message)` | `byte[]` | 获取消息体字节数组 |
| `getBodyAsString(message)` | `String` | 获取消息体字符串 |

`getHeaderValue` 支持自动类型转换：
- 目标类型为 `String` → 调用 `toString()`
- 目标类型为 `Long` 且值为 `Number` → 数值转换
- 目标类型为 `Integer` 且值为 `Number` → 数值转换

## 7. 发布确认与返回回调

### 7.1 发布确认（Confirm Callback）

启用 `confirm-callback: true` 后，消息发送到 Exchange 后会触发确认回调：
- **确认成功**：消息已到达 Exchange
- **确认失败**：消息未到达 Exchange，日志输出失败原因

> 需同时配置 `spring.rabbitmq.publisher-confirm-type: correlated`

### 7.2 返回回调（Return Callback）

启用 `return-callback: true` 后，当消息无法从 Exchange 路由到 Queue 时触发回调：
- 日志输出 Exchange、RoutingKey、replyCode、replyText

> 需同时配置 `spring.rabbitmq.publisher-returns: true`

## 8. 自动配置机制

| 配置类 | 条件 | 说明 |
|--------|------|------|
| `RabbitMqConfig` | `enable-rabbit = true` | 核心自动配置 |

自动注册的 Bean：

| Bean 名称 | 类型 | 说明 |
|-----------|------|------|
| `jsonMessageConverter` | `Jackson2JsonMessageConverter` | JSON 消息转换器 |
| `rabbitTemplate` | `RabbitTemplate` | RabbitMQ 操作模板 |
| `rabbitProducer` | `RabbitProducer` | 消息生产者（核心 API） |
| `rabbitProducerHelper` | `RabbitProducerHelper` | 生产者辅助类（底层 API） |

所有 Bean 均支持 `@ConditionalOnMissingBean`，可自定义覆盖。

## 9. 包结构

```
com.mcst.easyfk.mq.rabbit
├── config
│   └── RabbitMqConfig.java              # 自动配置（RabbitTemplate / 消息转换器 / 确认回调）
├── producer
│   ├── RabbitProducer.java              # 消息生产者（核心 API：同步/异步 + 延迟自动路由）
│   └── RabbitProducerHelper.java        # 生产者辅助类（底层 RabbitTemplate 封装）
├── properties
│   └── RabbitMqProperties.java          # 配置属性类
└── util
    └── RabbitMessageUtil.java           # 消息工具类（Header 提取 / 类型转换）
```

## 10. 最佳实践

1. **Exchange 与 Queue 预先声明**：本组件只负责消息发送，Exchange、Queue、Binding 的声明建议在消费端通过 `@RabbitListener` 的 `bindings` 属性或 `@Bean` 声明。
2. **合理选择 Exchange 类型**：
   - **Direct**：精确路由，适合点对点通信
   - **Topic**：模式匹配路由，适合多级分类
   - **Fanout**：广播，适合通知场景
   - **Headers**：基于 Header 匹配路由
3. **启用发布确认**：生产环境建议开启 `confirm-callback` 和 `return-callback`，确保消息可靠投递。
4. **延迟消息注意事项**：使用延迟消息前确保 RabbitMQ 安装了 `rabbitmq_delayed_message_exchange` 插件，并正确声明延迟交换机。
5. **善用 messageKey**：将 messageKey 作为 RoutingKey，实现精确的消息路由。
6. **消费者手动确认**：高可靠场景建议配置 `acknowledge-mode: manual`，处理完成后手动 ACK。
7. **预取限制**：设置合理的 `prefetch` 值，避免消费者被大量消息淹没。
8. **统一消息模型**：使用 `CommonMessage` 发送，便于未来在 Kafka / RocketMQ 之间切换。
