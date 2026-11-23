# EasyFK RabbitMQ消息队列使用教程

## 目录

1. [概述](#概述)
2. [组件架构](#组件架构)
3. [快速开始](#快速开始)
4. [详细使用指南](#详细使用指南)
5. [配置说明](#配置说明)
6. [消息消费](#消息消费)
7. [延迟消息](#延迟消息)
8. [性能优化配置](#性能优化配置)
9. [最佳实践](#最佳实践)
10. [常见问题](#常见问题)

## 概述

EasyFK RabbitMQ消息队列组件基于Spring AMQP实现，提供了简单易用的消息发送解决方案。该组件与框架内其他MQ组件（RocketMQ、Kafka）保持统一的API风格，便于切换和迁移。

### 核心特性

- 📤 **统一API**：与RocketMQ、Kafka保持一致的CommonMessage消息模型
- ⏰ **延迟消息**：支持通过延迟插件实现延迟消息
- 🔄 **同步/异步**：支持同步和异步两种发送模式
- ✅ **消息确认**：支持发布确认（Publisher Confirm）和返回回调
- 🎯 **灵活路由**：基于Exchange + RoutingKey的灵活路由机制
- 🔧 **自动配置**：开箱即用的Spring Boot自动配置

### RabbitMQ核心概念

```
┌─────────────────────────────────────────────────────────────────┐
│                        RabbitMQ Broker                         │
│                                                                 │
│  ┌──────────┐    routingKey    ┌─────────┐    binding    ┌────────┐  │
│  │ Producer │ ──────────────► │ Exchange│ ────────────► │ Queue  │  │
│  └──────────┘                  └─────────┘               └────────┘  │
│                                     │                         │      │
│                                     │      ┌─────────┐        │      │
│                                     └────► │ Queue 2 │        │      │
│                                            └─────────┘        │      │
│                                                               ▼      │
│                                                          ┌──────────┐│
│                                                          │ Consumer ││
│                                                          └──────────┘│
└─────────────────────────────────────────────────────────────────┘
```

| 概念               | 说明                         |
|------------------|----------------------------|
| **Exchange**     | 交换机，接收消息并根据路由规则分发到队列       |
| **Queue**        | 队列，存储消息的容器                 |
| **Binding**      | 绑定关系，定义Exchange到Queue的路由规则 |
| **RoutingKey**   | 路由键，用于消息的路由匹配              |
| **Virtual Host** | 虚拟主机，用于隔离不同应用的资源           |

## 组件架构

```
mq-rabbit/
├── config/                       # 配置类
│   └── RabbitMqConfig.java      # 自动配置类（RabbitTemplate、消息转换器）
├── producer/                     # 生产者
│   ├── RabbitProducer.java      # 消息生产者（核心API）
│   └── RabbitProducerHelper.java # 生产者辅助类（底层封装）
├── properties/                   # 配置属性
│   └── RabbitMqProperties.java  # RabbitMQ配置属性
└── util/                         # 工具类
    └── RabbitMessageUtil.java   # 消息工具类
```

## 快速开始

### 1. 添加依赖

在您的项目的`build.gradle`中添加依赖：

```gradle
dependencies {
    implementation 'com.mcst.easyfk:mq-rabbit'
}
```

### 2. 配置RabbitMQ连接

在`application.yml`中配置RabbitMQ连接信息：

```yaml
easyfk:
  config:
    mq:
      rabbit:
        # 开启RabbitMQ（必须设置为true）
        enable-rabbit: true
        # 默认Exchange名称
        exchange: easyfk.direct.exchange
        # 延迟消息Exchange名称
        delay-exchange: easyfk.delay.exchange

spring:
  rabbitmq:
    host: 127.0.0.1
    port: 5672
    username: guest
    password: guest
    virtual-host: /
```

### 3. 使用示例

```java
@Service
public class OrderService {
    
    @Resource
    private RabbitProducer rabbitProducer;
    
    public void sendOrderMessage(String orderId) {
        // 创建消息对象
        CommonMessage<OrderDTO> message = new CommonMessage<>();
        message.setTopic("order.exchange");        // Exchange名称
        message.setMessageKey("order.create");     // RoutingKey
        message.setData(new OrderDTO(orderId, "商品A", 99.00));
        
        // 同步发送消息
        rabbitProducer.syncSendMessage(message);
    }
}
```

## 详细使用指南

### 核心API - RabbitProducer

`RabbitProducer`是消息发送的核心操作类，提供同步和异步两种发送模式：

#### 1. 同步发送消息

```java
@Resource
private RabbitProducer rabbitProducer;

public void syncSend() {
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("my.exchange");           // Exchange名称
    message.setMessageKey("my.routing.key");   // RoutingKey
    message.setData("Hello RabbitMQ");         // 消息体
    
    // 同步发送，等待发送完成
    rabbitProducer.syncSendMessage(message);
}
```

#### 2. 异步发送消息

```java
public void asyncSend() {
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("my.exchange");
    message.setMessageKey("my.routing.key");
    message.setData("Hello RabbitMQ Async");
    
    // 异步发送，立即返回
    rabbitProducer.asyncSendMessage(message);
}
```

#### 3. 发送延迟消息

```java
public void sendDelayMessage() {
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("order.exchange");
    message.setMessageKey("order.timeout");
    message.setData("订单超时检查");
    message.setDelayTime(30000L);  // 延迟30秒，单位：毫秒
    
    // 发送延迟消息（需要安装延迟插件）
    rabbitProducer.syncSendMessage(message);
}
```

#### 4. 发送带标签的消息

```java
public void sendWithTags() {
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("event.exchange");
    message.setTags("user.login");  // 如果没有messageKey，tags将作为routingKey
    message.setData("用户登录事件");
    
    rabbitProducer.syncSendMessage(message);
}
```

#### 5. 发送带自定义属性的消息

```java
public void sendWithProperties() {
    CommonMessage<OrderDTO> message = new CommonMessage<>();
    message.setTopic("order.exchange");
    message.setMessageKey("order.create");
    message.setData(new OrderDTO("ORD001", "商品A", 99.00));
    
    // 设置自定义消息属性
    Map<String, String> properties = new HashMap<>();
    properties.put("source", "web");
    properties.put("version", "v1.0");
    message.setProperties(properties);
    
    rabbitProducer.syncSendMessage(message);
}
```

### CommonMessage字段说明

| 字段            | 类型     | 必填 | 说明          | RabbitMQ映射             |
|---------------|--------|----|-------------|------------------------|
| topic         | String | 是  | 主题名称        | Exchange名称             |
| data          | T      | 是  | 消息体数据       | Message Body           |
| messageKey    | String | 否  | 业务键         | RoutingKey（优先）         |
| tags          | String | 否  | 消息标签        | RoutingKey（次选）/ Header |
| delayTime     | Long   | 否  | 延迟时间（毫秒）    | x-delay Header         |
| messageId     | String | 否  | 消息ID（自动生成）  | MessageId              |
| sendTimestamp | Long   | 否  | 发送时间戳（自动生成） | Timestamp              |
| properties    | Map    | 否  | 自定义扩展属性     | Headers                |

## 配置说明

### EasyFK配置

```yaml
easyfk:
  config:
    mq:
      rabbit:
        # 开启RabbitMQ消息队列（必须）
        enable-rabbit: true
        
        # 默认Exchange名称
        exchange: easyfk.direct.exchange
        
        # 延迟消息Exchange名称（需要安装延迟插件）
        delay-exchange: easyfk.delay.exchange
        
        # 是否启用发布确认回调
        confirm-callback: false
        
        # 是否启用返回回调（消息无法路由时触发）
        return-callback: false
```

### Spring RabbitMQ配置

```yaml
spring:
  rabbitmq:
    # 连接配置
    host: 127.0.0.1
    port: 5672
    username: guest
    password: guest
    virtual-host: /
    
    # 连接超时时间
    connection-timeout: 10000
    
    # 发布确认类型：none, simple, correlated
    publisher-confirm-type: correlated
    
    # 开启发布返回
    publisher-returns: true
    
    # 消息模板配置
    template:
      # 强制消息（消息无法路由时返回）
      mandatory: true
      # 接收超时时间
      receive-timeout: 30000
      # 回复超时时间
      reply-timeout: 30000
    
    # 监听器配置
    listener:
      simple:
        # 消费者并发数
        concurrency: 5
        # 最大并发数
        max-concurrency: 10
        # 确认模式：none, manual, auto
        acknowledge-mode: manual
        # 预取数量
        prefetch: 10
        # 重试配置
        retry:
          enabled: true
          initial-interval: 1000
          max-attempts: 3
          max-interval: 10000
          multiplier: 2.0
    
    # 缓存配置
    cache:
      channel:
        # 缓存的Channel数量
        size: 25
        # 获取Channel的超时时间
        checkout-timeout: 0
      connection:
        # 缓存模式：channel, connection
        mode: channel
```

### 配置项详解

| 配置项                | 默认值                    | 说明                  |
|--------------------|------------------------|---------------------|
| `enable-rabbit`    | false                  | 是否启用RabbitMQ组件      |
| `exchange`         | easyfk.direct.exchange | 默认Direct Exchange名称 |
| `delay-exchange`   | easyfk.delay.exchange  | 延迟消息Exchange名称      |
| `confirm-callback` | false                  | 启用发布确认回调            |
| `return-callback`  | false                  | 启用消息返回回调            |

## 消息消费

### 基本消费者

```java
@Component
@Slf4j
public class OrderConsumer {
    
    @RabbitListener(
        bindings = @QueueBinding(
            value = @Queue(value = "order.queue", durable = "true"),
            exchange = @Exchange(value = "order.exchange", type = ExchangeTypes.DIRECT),
            key = "order.create"
        )
    )
    public void handleOrderCreate(String message, Channel channel, 
                                   @Header(AmqpHeaders.DELIVERY_TAG) long deliveryTag) {
        try {
            log.info("收到订单消息: {}", message);
            // 处理业务逻辑
            processOrder(message);
            // 手动确认
            channel.basicAck(deliveryTag, false);
        } catch (Exception e) {
            log.error("处理订单消息失败", e);
            try {
                // 拒绝消息并重新入队
                channel.basicNack(deliveryTag, false, true);
            } catch (IOException ex) {
                log.error("消息确认失败", ex);
            }
        }
    }
}
```

### 消费JSON对象

```java
@Component
public class UserConsumer {
    
    @RabbitListener(queues = "user.queue")
    public void handleUserMessage(@Payload UserDTO user, 
                                   @Headers Map<String, Object> headers,
                                   Channel channel,
                                   @Header(AmqpHeaders.DELIVERY_TAG) long deliveryTag) throws IOException {
        try {
            // 获取消息头信息
            String messageId = (String) headers.get(MessageHeaderConstants.MESSAGE_ID);
            Long timestamp = (Long) headers.get(MessageHeaderConstants.SEND_TIMESTAMP);
            
            log.info("收到用户消息，messageId: {}, timestamp: {}, user: {}", 
                     messageId, timestamp, user);
            
            // 处理业务逻辑
            processUser(user);
            
            // 确认消息
            channel.basicAck(deliveryTag, false);
        } catch (Exception e) {
            // 处理失败，拒绝消息
            channel.basicNack(deliveryTag, false, false);
        }
    }
}
```

### 使用消息工具类

```java
@RabbitListener(queues = "raw.queue")
public void handleRawMessage(Message message, Channel channel) throws IOException {
    // 使用工具类获取消息信息
    String messageId = RabbitMessageUtil.getMessageId(message);
    Long timestamp = RabbitMessageUtil.getTimestamp(message);
    String body = RabbitMessageUtil.getBodyAsString(message);
    
    // 获取自定义消息头
    String customHeader = RabbitMessageUtil.getHeaderValue(message, "customKey", String.class);
    
    log.info("messageId: {}, timestamp: {}, body: {}", messageId, timestamp, body);
    
    channel.basicAck(message.getMessageProperties().getDeliveryTag(), false);
}
```

## 延迟消息

### 方案一：使用延迟插件（推荐）

需要安装 `rabbitmq_delayed_message_exchange` 插件：

```bash
# 下载插件
wget https://github.com/rabbitmq/rabbitmq-delayed-message-exchange/releases/download/v3.12.0/rabbitmq_delayed_message_exchange-3.12.0.ez

# 复制到插件目录
cp rabbitmq_delayed_message_exchange-3.12.0.ez /usr/lib/rabbitmq/lib/rabbitmq_server-3.12.x/plugins/

# 启用插件
rabbitmq-plugins enable rabbitmq_delayed_message_exchange
```

配置延迟Exchange：

```java
@AutoConfiguration
public class RabbitDelayConfig {
    
    @Bean
    public CustomExchange delayExchange() {
        Map<String, Object> args = new HashMap<>();
        args.put("x-delayed-type", "direct");
        return new CustomExchange("easyfk.delay.exchange", "x-delayed-message", true, false, args);
    }
    
    @Bean
    public Queue delayQueue() {
        return new Queue("delay.queue", true);
    }
    
    @Bean
    public Binding delayBinding() {
        return BindingBuilder
            .bind(delayQueue())
            .to(delayExchange())
            .with("delay.routing.key")
            .noargs();
    }
}
```

发送延迟消息：

```java
public void sendDelayMessage() {
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("easyfk.delay.exchange");
    message.setMessageKey("delay.routing.key");
    message.setData("延迟消息内容");
    message.setDelayTime(60000L);  // 延迟60秒
    
    rabbitProducer.syncSendMessage(message);
}
```

### 方案二：TTL + 死信队列

```java
@AutoConfiguration
public class DeadLetterConfig {
    
    // 死信交换机
    @Bean
    public DirectExchange deadLetterExchange() {
        return new DirectExchange("dlx.exchange");
    }
    
    // 死信队列（实际消费队列）
    @Bean
    public Queue deadLetterQueue() {
        return new Queue("dlx.queue", true);
    }
    
    // 死信绑定
    @Bean
    public Binding deadLetterBinding() {
        return BindingBuilder.bind(deadLetterQueue())
            .to(deadLetterExchange())
            .with("dlx.routing.key");
    }
    
    // 延迟队列（设置TTL和死信）
    @Bean
    public Queue delayQueue() {
        Map<String, Object> args = new HashMap<>();
        args.put("x-dead-letter-exchange", "dlx.exchange");
        args.put("x-dead-letter-routing-key", "dlx.routing.key");
        args.put("x-message-ttl", 60000);  // 消息TTL 60秒
        return new Queue("ttl.delay.queue", true, false, false, args);
    }
}
```

## 性能优化配置

### 1. 连接池配置

```yaml
spring:
  rabbitmq:
    cache:
      channel:
        # Channel缓存数量，根据并发量调整
        size: 50
        # 获取Channel超时时间（0表示无限等待）
        checkout-timeout: 5000
      connection:
        # 连接缓存模式
        mode: channel
        # connection模式下的连接数
        size: 10
```

### 2. 生产者优化

```yaml
spring:
  rabbitmq:
    # 开启发布确认（性能有影响，按需开启）
    publisher-confirm-type: correlated
    publisher-returns: true
    
    template:
      mandatory: true
```

```java
@AutoConfiguration
public class RabbitProducerConfig {
    
    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);
        
        // 设置消息转换器
        template.setMessageConverter(new Jackson2JsonMessageConverter());
        
        // 开启Channel事务（不推荐，影响性能）
        // template.setChannelTransacted(true);
        
        return template;
    }
}
```

### 3. 消费者优化

```yaml
spring:
  rabbitmq:
    listener:
      simple:
        # 消费者初始并发数
        concurrency: 10
        # 最大并发数
        max-concurrency: 20
        # 预取数量（每次从队列拉取的消息数）
        prefetch: 50
        # 确认模式：manual手动确认性能更好
        acknowledge-mode: manual
        # 消费者批量处理
        batch-size: 10
```

### 4. 批量发送

```java
public void batchSend(List<OrderDTO> orders) {
    for (OrderDTO order : orders) {
        CommonMessage<OrderDTO> message = new CommonMessage<>();
        message.setTopic("order.exchange");
        message.setMessageKey("order.batch");
        message.setData(order);
        
        // 异步发送提高吞吐量
        rabbitProducer.asyncSendMessage(message);
    }
}
```

### 5. 消息压缩

```java
@Bean
public MessageConverter messageConverter() {
    Jackson2JsonMessageConverter converter = new Jackson2JsonMessageConverter();
    // 大消息可以考虑压缩
    return converter;
}
```

### 性能优化建议总结

| 优化项                    | 建议值        | 说明                 |
|------------------------|------------|--------------------|
| channel.size           | 25-100     | 根据并发量调整            |
| concurrency            | 5-20       | 根据CPU核心数和业务特点调整    |
| prefetch               | 10-100     | 值越大吞吐量越高，但可能造成消息堆积 |
| acknowledge-mode       | manual     | 手动确认性能更好，但需要处理确认逻辑 |
| publisher-confirm-type | correlated | 需要确认时使用，否则设为none   |

## 最佳实践

### 1. Exchange和Queue设计原则

```java
// ✅ 推荐：按业务域划分Exchange
String orderExchange = "order.exchange";
String userExchange = "user.exchange";
String paymentExchange = "payment.exchange";

// ✅ 推荐：RoutingKey语义清晰
String routingKey = "order.create";
String routingKey = "order.cancel";
String routingKey = "order.payment.success";

// ❌ 不推荐：含义模糊
String exchange = "exchange1";
String routingKey = "key1";
```

### 2. 消息幂等性处理

```java
@Component
public class IdempotentConsumer {
    
    @Resource
    private StringRedisTemplate redisTemplate;
    
    @RabbitListener(queues = "order.queue")
    public void handleOrder(String message, Channel channel,
                            @Header(AmqpHeaders.DELIVERY_TAG) long deliveryTag,
                            @Header(MessageHeaderConstants.MESSAGE_ID) String messageId) throws IOException {
        
        // 幂等性检查
        String lockKey = "mq:consumed:" + messageId;
        Boolean success = redisTemplate.opsForValue().setIfAbsent(lockKey, "1", 24, TimeUnit.HOURS);
        
        if (Boolean.FALSE.equals(success)) {
            log.warn("消息已处理，messageId: {}", messageId);
            channel.basicAck(deliveryTag, false);
            return;
        }
        
        try {
            // 处理业务逻辑
            processOrder(message);
            channel.basicAck(deliveryTag, false);
        } catch (Exception e) {
            // 处理失败，删除幂等标记
            redisTemplate.delete(lockKey);
            channel.basicNack(deliveryTag, false, true);
        }
    }
}
```

### 3. 消息重试机制

```yaml
spring:
  rabbitmq:
    listener:
      simple:
        retry:
          enabled: true
          initial-interval: 1000    # 首次重试间隔
          max-attempts: 3           # 最大重试次数
          max-interval: 10000       # 最大重试间隔
          multiplier: 2.0           # 重试间隔倍数
```

### 4. 死信队列处理

```java
@AutoConfiguration
public class DeadLetterQueueConfig {
    
    @Bean
    public Queue orderQueue() {
        Map<String, Object> args = new HashMap<>();
        // 设置死信交换机
        args.put("x-dead-letter-exchange", "order.dlx.exchange");
        args.put("x-dead-letter-routing-key", "order.dlx");
        return new Queue("order.queue", true, false, false, args);
    }
    
    @Bean
    public DirectExchange dlxExchange() {
        return new DirectExchange("order.dlx.exchange");
    }
    
    @Bean
    public Queue dlxQueue() {
        return new Queue("order.dlx.queue", true);
    }
    
    @Bean
    public Binding dlxBinding() {
        return BindingBuilder.bind(dlxQueue()).to(dlxExchange()).with("order.dlx");
    }
}

// 死信消费者
@Component
public class DlxConsumer {
    
    @RabbitListener(queues = "order.dlx.queue")
    public void handleDeadLetter(Message message, Channel channel) throws IOException {
        log.error("收到死信消息: {}", new String(message.getBody()));
        // 记录日志、告警、人工处理等
        channel.basicAck(message.getMessageProperties().getDeliveryTag(), false);
    }
}
```

### 5. 消息顺序性保证

```java
// 使用相同的RoutingKey发送到同一个Queue，单消费者消费
public void sendOrderedMessage(String orderId, List<String> events) {
    for (String event : events) {
        CommonMessage<String> message = new CommonMessage<>();
        message.setTopic("order.exchange");
        message.setMessageKey("order." + orderId);  // 同一订单使用相同RoutingKey
        message.setData(event);
        
        // 同步发送保证顺序
        rabbitProducer.syncSendMessage(message);
    }
}
```

### 6. 消息持久化配置

```java
@AutoConfiguration
public class DurableConfig {
    
    // 持久化Exchange
    @Bean
    public DirectExchange durableExchange() {
        return new DirectExchange("durable.exchange", true, false);
    }
    
    // 持久化Queue
    @Bean
    public Queue durableQueue() {
        return new Queue("durable.queue", true);  // durable=true
    }
}
```

## 常见问题

### 1. 消息发送失败

**问题现象**：消息发送时抛出异常

**排查步骤**：

```java
// 1. 检查连接是否正常
// 2. 检查Exchange是否存在
// 3. 开启confirm和return回调查看详细错误

easyfk:
  config:
    mq:
      rabbit:
        confirm-callback: true
        return-callback: true
```

### 2. 消息丢失

**解决方案**：

```yaml
spring:
  rabbitmq:
    # 开启发布确认
    publisher-confirm-type: correlated
    publisher-returns: true
    template:
      mandatory: true
    listener:
      simple:
        # 手动确认
        acknowledge-mode: manual
```

### 3. 消息重复消费

**解决方案**：实现幂等性处理（见最佳实践第2条）

### 4. 消费者阻塞

**问题现象**：消息堆积，消费者处理缓慢

**解决方案**：

```yaml
spring:
  rabbitmq:
    listener:
      simple:
        # 增加并发数
        concurrency: 10
        max-concurrency: 20
        # 减少预取数量
        prefetch: 10
```

### 5. 连接断开重连

**解决方案**：

```yaml
spring:
  rabbitmq:
    # 自动重连（默认开启）
    connection-timeout: 10000
    # 开启心跳
    requested-heartbeat: 60
```

### 6. 延迟消息不生效

**排查步骤**：

1. 确认是否安装了 `rabbitmq_delayed_message_exchange` 插件
2. 检查Exchange类型是否为 `x-delayed-message`
3. 检查delayTime单位是否为毫秒

```bash
# 检查插件状态
rabbitmq-plugins list | grep delay
```

## 版本信息

- **组件版本**：mq-rabbit
- **依赖版本**：Spring Boot Starter AMQP
- **兼容性**：Spring Boot 3.x
- **RabbitMQ版本**：3.9+

## 附录：Exchange类型说明

| 类型          | 说明                       | 使用场景   |
|-------------|--------------------------|--------|
| **Direct**  | 精确匹配RoutingKey           | 点对点通信  |
| **Fanout**  | 广播到所有绑定队列                | 广播通知   |
| **Topic**   | 模式匹配RoutingKey（支持*和#通配符） | 多级路由   |
| **Headers** | 根据消息头匹配                  | 复杂路由规则 |

## 技术支持

如遇到使用问题，请联系技术支持团队或查阅相关文档。
