# EasyFK RocketMQ消息队列使用教程

## 目录

1. [概述](#概述)
2. [组件架构](#组件架构)
3. [快速开始](#快速开始)
4. [详细使用指南](#详细使用指南)
5. [配置说明](#配置说明)
6. [消息消费](#消息消费)
7. [延迟消息](#延迟消息)
8. [顺序消息](#顺序消息)
9. [性能优化配置](#性能优化配置)
10. [最佳实践](#最佳实践)
11. [常见问题](#常见问题)

## 概述

EasyFK RocketMQ消息队列组件基于Apache RocketMQ Spring Boot
Starter实现，提供了简单易用的消息发送解决方案。该组件与框架内其他MQ组件（RabbitMQ、Kafka）保持统一的API风格，便于切换和迁移。

### 核心特性

- 📤 **统一API**：与RabbitMQ、Kafka保持一致的CommonMessage消息模型
- ⏰ **延迟消息**：原生支持任意精度的延迟消息
- 🔢 **顺序消息**：支持分区顺序消息，保证同一业务的消息顺序消费
- 🔄 **同步/异步**：支持同步和异步两种发送模式
- 🏷️ **消息标签**：支持Tag过滤，实现消息分类
- 🔧 **自动配置**：开箱即用的Spring Boot自动配置

### RocketMQ核心概念

```
┌─────────────────────────────────────────────────────────────────────┐
│                        RocketMQ Cluster                             │
│                                                                     │
│  ┌──────────┐         ┌────────────┐         ┌──────────────────┐  │
│  │ Producer │ ──────► │NameServer │ ◄─────► │     Broker       │  │
│  └──────────┘         └────────────┘         │  ┌────────────┐  │  │
│       │                                      │  │   Topic    │  │  │
│       │              Topic:Tag               │  │ ┌────────┐ │  │  │
│       └─────────────────────────────────────►│  │ │Queue 0 │ │  │  │
│                                              │  │ │Queue 1 │ │  │  │
│                                              │  │ │Queue 2 │ │  │  │
│                                              │  │ └────────┘ │  │  │
│                                              │  └────────────┘  │  │
│                                              └──────────────────┘  │
│                                                       │            │
│                                                       ▼            │
│                                              ┌──────────────────┐  │
│                                              │    Consumer      │  │
│                                              │  (ConsumerGroup) │  │
│                                              └──────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

| 概念                | 说明                   |
|-------------------|----------------------|
| **NameServer**    | 注册中心，管理Broker路由信息    |
| **Broker**        | 消息存储服务器，负责消息的存储和转发   |
| **Topic**         | 消息主题，消息的逻辑分类         |
| **Tag**           | 消息标签，用于同一Topic下的消息过滤 |
| **Queue**         | 消息队列，Topic下的物理分区     |
| **ConsumerGroup** | 消费者组，同组消费者负载均衡消费     |

## 组件架构

```
mq-rocket/
├── config/                        # 配置类
│   └── RocketMqConfig.java       # 自动配置类
├── producer/                      # 生产者
│   ├── RocketProducer.java       # 消息生产者（核心API）
│   └── RocketProducerHelper.java # 生产者辅助类（底层封装）
├── properties/                    # 配置属性
│   └── RocketMqProperties.java   # RocketMQ配置属性
└── util/                          # 工具类
    └── RocketMessageUtil.java    # 消息工具类
```

## 快速开始

### 1. 添加依赖

在您的项目的`build.gradle`中添加依赖：

```gradle
dependencies {
    implementation 'com.mcst:mq-rocket'
}
```

### 2. 配置RocketMQ连接

在`application.yml`中配置RocketMQ连接信息：

```yaml
easyfk:
  config:
    mq:
      rocket:
        # 开启RocketMQ（必须设置为true）
        enable-rocket: true

rocketmq:
  name-server: 127.0.0.1:9876
  producer:
    group: easyfk-producer-group
```

### 3. 使用示例

```java
@Service
public class OrderService {
    
    @Resource
    private RocketProducer rocketProducer;
    
    public void sendOrderMessage(String orderId) {
        // 创建消息对象
        CommonMessage<OrderDTO> message = new CommonMessage<>();
        message.setTopic("ORDER_TOPIC");           // 主题名称
        message.setTags("order_create");           // 消息标签
        message.setData(new OrderDTO(orderId, "商品A", 99.00));
        
        // 同步发送消息
        rocketProducer.syncSendMessage(message);
    }
}
```

## 详细使用指南

### 核心API - RocketProducer

`RocketProducer`是消息发送的核心操作类，提供同步和异步两种发送模式：

#### 1. 同步发送普通消息

```java
@Resource
private RocketProducer rocketProducer;

public void syncSend() {
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("TEST_TOPIC");           // 主题名称
    message.setData("Hello RocketMQ");        // 消息体
    
    // 同步发送，等待发送完成
    rocketProducer.syncSendMessage(message);
}
```

#### 2. 异步发送消息

```java
public void asyncSend() {
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("TEST_TOPIC");
    message.setData("Hello RocketMQ Async");
    
    // 异步发送，立即返回
    rocketProducer.asyncSendMessage(message);
}
```

#### 3. 发送带标签的消息

```java
public void sendWithTags() {
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("ORDER_TOPIC");
    message.setTags("order_create");  // 设置消息标签，用于消费者过滤
    message.setData("订单创建消息");
    
    // 发送后，topic实际为：ORDER_TOPIC:order_create
    rocketProducer.syncSendMessage(message);
}
```

#### 4. 发送延迟消息

```java
public void sendDelayMessage() {
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("ORDER_TOPIC");
    message.setTags("order_timeout");
    message.setData("订单超时检查");
    message.setDelayTime(30000L);  // 延迟30秒，单位：毫秒
    
    // 发送延迟消息
    rocketProducer.syncSendMessage(message);
}
```

#### 5. 发送顺序消息

```java
public void sendOrderlyMessage() {
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("ORDER_TOPIC");
    message.setTags("order_status");
    message.setMessageKey("ORDER_12345");  // 设置messageKey，相同key的消息发送到同一队列
    message.setData("订单状态变更");
    
    // 发送顺序消息
    rocketProducer.syncSendMessage(message);
}
```

#### 6. 发送复杂对象消息

```java
public void sendObjectMessage() {
    OrderDTO order = new OrderDTO();
    order.setOrderId("ORD001");
    order.setProductName("商品A");
    order.setPrice(99.00);
    
    CommonMessage<OrderDTO> message = new CommonMessage<>();
    message.setTopic("ORDER_TOPIC");
    message.setTags("order_create");
    message.setData(order);  // 对象会自动序列化
    
    rocketProducer.syncSendMessage(message);
}
```

### CommonMessage字段说明

| 字段            | 类型     | 必填 | 说明          | RocketMQ映射     |
|---------------|--------|----|-------------|----------------|
| topic         | String | 是  | 主题名称        | Topic          |
| data          | T      | 是  | 消息体数据       | Message Body   |
| tags          | String | 否  | 消息标签        | Topic:Tag      |
| messageKey    | String | 否  | 业务键（顺序消息）   | HashKey        |
| delayTime     | Long   | 否  | 延迟时间（毫秒）    | DelayTimeMills |
| messageId     | String | 否  | 消息ID（自动生成）  | Header         |
| sendTimestamp | Long   | 否  | 发送时间戳（自动生成） | Header         |

## 配置说明

### EasyFK配置

```yaml
easyfk:
  config:
    mq:
      rocket:
        # 开启RocketMQ消息队列（必须）
        enable-rocket: true
```

### RocketMQ配置

```yaml
rocketmq:
  # NameServer地址（多个用分号分隔）
  name-server: 127.0.0.1:9876;127.0.0.1:9877
  
  # 生产者配置
  producer:
    # 生产者组名（必须）
    group: easyfk-producer-group
    # 发送消息超时时间（毫秒）
    send-message-timeout: 3000
    # 消息体最大值（字节）
    max-message-size: 4194304
    # 同步发送失败重试次数
    retry-times-when-send-failed: 2
    # 异步发送失败重试次数
    retry-times-when-send-async-failed: 2
    # 发送失败是否重试其他Broker
    retry-next-server: true
    # 是否启用消息轨迹
    enable-msg-trace: false
    # 自定义消息轨迹Topic
    customized-trace-topic: RMQ_SYS_TRACE_TOPIC
    
  # 消费者配置
  consumer:
    # 消费者组名
    group: easyfk-consumer-group
    # 消息消费线程数
    consume-thread-min: 20
    consume-thread-max: 64
    # 单次消费最大消息数
    consume-message-batch-max-size: 1
    # 拉取消息间隔（毫秒）
    pull-interval: 0
    # 单次拉取最大消息数
    pull-batch-size: 32
```

### 配置项详解

| 配置项                            | 默认值   | 说明              |
|--------------------------------|-------|-----------------|
| `enable-rocket`                | false | 是否启用RocketMQ组件  |
| `name-server`                  | -     | NameServer地址，必填 |
| `producer.group`               | -     | 生产者组名，必填        |
| `send-message-timeout`         | 3000  | 发送超时时间（毫秒）      |
| `retry-times-when-send-failed` | 2     | 同步发送失败重试次数      |

## 消息消费

### 基本消费者

```java
@Component
@Slf4j
@RocketMQMessageListener(
    topic = "ORDER_TOPIC",
    consumerGroup = "order-consumer-group",
    selectorExpression = "order_create"  // Tag过滤
)
public class OrderConsumer implements RocketMQListener<String> {
    
    @Override
    public void onMessage(String message) {
        log.info("收到订单消息: {}", message);
        // 处理业务逻辑
        processOrder(message);
    }
}
```

### 消费JSON对象

```java
@Component
@RocketMQMessageListener(
    topic = "ORDER_TOPIC",
    consumerGroup = "order-consumer-group"
)
public class OrderObjectConsumer implements RocketMQListener<OrderDTO> {
    
    @Override
    public void onMessage(OrderDTO order) {
        log.info("收到订单对象: orderId={}, productName={}", 
                 order.getOrderId(), order.getProductName());
        processOrder(order);
    }
}
```

### 消费原始消息（获取消息头）

```java
@Component
@RocketMQMessageListener(
    topic = "ORDER_TOPIC",
    consumerGroup = "order-consumer-group"
)
public class OrderRawConsumer implements RocketMQListener<MessageExt> {
    
    @Override
    public void onMessage(MessageExt messageExt) {
        String messageId = messageExt.getMsgId();
        String topic = messageExt.getTopic();
        String tags = messageExt.getTags();
        String body = new String(messageExt.getBody(), StandardCharsets.UTF_8);
        
        log.info("收到消息，messageId: {}, topic: {}, tags: {}, body: {}", 
                 messageId, topic, tags, body);
    }
}
```

### 多Tag消费

```java
@Component
@RocketMQMessageListener(
    topic = "ORDER_TOPIC",
    consumerGroup = "order-multi-tag-group",
    selectorExpression = "order_create || order_cancel || order_pay"  // 多个Tag用||分隔
)
public class OrderMultiTagConsumer implements RocketMQListener<String> {
    
    @Override
    public void onMessage(String message) {
        log.info("收到订单消息: {}", message);
    }
}
```

### 顺序消费

```java
@Component
@RocketMQMessageListener(
    topic = "ORDER_TOPIC",
    consumerGroup = "order-orderly-group",
    consumeMode = ConsumeMode.ORDERLY  // 顺序消费模式
)
public class OrderOrderlyConsumer implements RocketMQListener<String> {
    
    @Override
    public void onMessage(String message) {
        log.info("顺序消费消息: {}", message);
        // 同一Queue中的消息会顺序消费
    }
}
```

### 广播消费

```java
@Component
@RocketMQMessageListener(
    topic = "BROADCAST_TOPIC",
    consumerGroup = "broadcast-consumer-group",
    messageModel = MessageModel.BROADCASTING  // 广播模式
)
public class BroadcastConsumer implements RocketMQListener<String> {
    
    @Override
    public void onMessage(String message) {
        log.info("广播消息: {}", message);
        // 所有消费者都会收到消息
    }
}
```

## 延迟消息

RocketMQ 原生支持延迟消息，无需额外配置：

### 发送延迟消息

```java
public void sendDelayMessage() {
    // 方式1：使用CommonMessage
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("DELAY_TOPIC");
    message.setData("延迟消息内容");
    message.setDelayTime(60000L);  // 延迟60秒
    
    rocketProducer.syncSendMessage(message);
}
```

### 延迟消息应用场景

```java
// 场景1：订单超时取消
public void createOrder(String orderId) {
    // 创建订单...
    
    // 发送延迟消息，30分钟后检查订单状态
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("ORDER_TOPIC");
    message.setTags("order_timeout_check");
    message.setData(orderId);
    message.setDelayTime(30 * 60 * 1000L);  // 30分钟
    
    rocketProducer.syncSendMessage(message);
}

// 场景2：定时提醒
public void scheduleReminder(String userId, long delayMs) {
    CommonMessage<String> message = new CommonMessage<>();
    message.setTopic("REMINDER_TOPIC");
    message.setData(userId);
    message.setDelayTime(delayMs);
    
    rocketProducer.syncSendMessage(message);
}
```

## 顺序消息

### 顺序消息原理

RocketMQ通过将相同业务ID的消息发送到同一个Queue，消费者顺序消费该Queue来保证消息顺序。

### 发送顺序消息

```java
// 订单状态变更必须顺序处理：创建 -> 支付 -> 发货 -> 完成
public void sendOrderStatusMessages(String orderId) {
    List<String> statuses = Arrays.asList("created", "paid", "shipped", "completed");
    
    for (String status : statuses) {
        CommonMessage<String> message = new CommonMessage<>();
        message.setTopic("ORDER_STATUS_TOPIC");
        message.setMessageKey(orderId);  // 相同订单ID发送到同一Queue
        message.setData(status);
        
        // 同步发送保证顺序
        rocketProducer.syncSendMessage(message);
    }
}
```

### 顺序消费配置

```java
@Component
@RocketMQMessageListener(
    topic = "ORDER_STATUS_TOPIC",
    consumerGroup = "order-status-group",
    consumeMode = ConsumeMode.ORDERLY  // 关键：顺序消费模式
)
public class OrderStatusConsumer implements RocketMQListener<String> {
    
    @Override
    public void onMessage(String status) {
        log.info("顺序处理订单状态: {}", status);
        // 按顺序处理：created -> paid -> shipped -> completed
    }
}
```

## 性能优化配置

### 1. 生产者优化

```yaml
rocketmq:
  producer:
    # 发送超时时间
    send-message-timeout: 3000
    # 压缩消息阈值（字节）
    compress-msg-body-over-howmuch: 4096
    # 同步发送重试次数
    retry-times-when-send-failed: 2
    # 异步发送重试次数
    retry-times-when-send-async-failed: 2
```

### 2. 消费者优化

```yaml
rocketmq:
  consumer:
    # 消费线程池配置
    consume-thread-min: 20
    consume-thread-max: 64
    # 单次拉取最大消息数
    pull-batch-size: 32
    # 单次消费最大消息数
    consume-message-batch-max-size: 1
    # 拉取间隔（0表示立即拉取）
    pull-interval: 0
```

### 3. 批量发送

```java
public void batchSend(List<OrderDTO> orders) {
    for (OrderDTO order : orders) {
        CommonMessage<OrderDTO> message = new CommonMessage<>();
        message.setTopic("ORDER_TOPIC");
        message.setTags("order_batch");
        message.setData(order);
        
        // 异步发送提高吞吐量
        rocketProducer.asyncSendMessage(message);
    }
}
```

### 4. 消费者并发配置

```java
@Component
@RocketMQMessageListener(
    topic = "HIGH_THROUGHPUT_TOPIC",
    consumerGroup = "high-throughput-group",
    consumeThreadNumber = 32  // 消费线程数
)
public class HighThroughputConsumer implements RocketMQListener<String> {
    
    @Override
    public void onMessage(String message) {
        // 高并发处理
    }
}
```

### 性能优化建议总结

| 优化项                            | 建议值       | 说明               |
|--------------------------------|-----------|------------------|
| send-message-timeout           | 3000-5000 | 发送超时时间，网络差时适当增加  |
| retry-times-when-send-failed   | 2-3       | 发送重试次数           |
| consume-thread-max             | 20-64     | 消费线程数，根据CPU核心数调整 |
| pull-batch-size                | 32-100    | 单次拉取消息数，值越大吞吐量越高 |
| consume-message-batch-max-size | 1-10      | 单次消费消息数          |

## 最佳实践

### 1. Topic和Tag设计原则

```java
// ✅ 推荐：Topic按业务域划分，Tag按消息类型划分
String topic = "ORDER_TOPIC";
String tagCreate = "order_create";
String tagCancel = "order_cancel";
String tagPay = "order_pay";

// ✅ 推荐：命名清晰
String topic = "USER_ACCOUNT_TOPIC";
String tag = "balance_change";

// ❌ 不推荐：含义模糊
String topic = "TOPIC_1";
String tag = "tag1";
```

### 2. 消息幂等性处理

```java
@Component
@RocketMQMessageListener(topic = "ORDER_TOPIC", consumerGroup = "order-group")
public class IdempotentConsumer implements RocketMQListener<MessageExt> {
    
    @Resource
    private StringRedisTemplate redisTemplate;
    
    @Override
    public void onMessage(MessageExt messageExt) {
        String msgId = messageExt.getMsgId();
        String lockKey = "mq:consumed:" + msgId;
        
        // 幂等性检查
        Boolean success = redisTemplate.opsForValue()
            .setIfAbsent(lockKey, "1", 24, TimeUnit.HOURS);
        
        if (Boolean.FALSE.equals(success)) {
            log.warn("消息已处理，msgId: {}", msgId);
            return;
        }
        
        try {
            // 处理业务逻辑
            String body = new String(messageExt.getBody());
            processMessage(body);
        } catch (Exception e) {
            // 处理失败，删除幂等标记
            redisTemplate.delete(lockKey);
            throw e;  // 抛出异常触发重试
        }
    }
}
```

### 3. 消息重试机制

```java
@Component
@RocketMQMessageListener(
    topic = "ORDER_TOPIC",
    consumerGroup = "order-group",
    maxReconsumeTimes = 3  // 最大重试次数
)
public class RetryConsumer implements RocketMQListener<MessageExt> {
    
    @Override
    public void onMessage(MessageExt messageExt) {
        int reconsumeTimes = messageExt.getReconsumeTimes();
        log.info("消费消息，重试次数: {}", reconsumeTimes);
        
        try {
            processMessage(messageExt);
        } catch (Exception e) {
            if (reconsumeTimes >= 3) {
                // 达到最大重试次数，记录日志或发送到死信队列
                log.error("消息处理失败，已达最大重试次数", e);
                saveToDeadLetter(messageExt);
                return;
            }
            throw e;  // 抛出异常触发重试
        }
    }
}
```

### 4. 死信队列处理

```java
@Component
@RocketMQMessageListener(
    topic = "%DLQ%order-group",  // 死信队列Topic格式
    consumerGroup = "dlq-consumer-group"
)
public class DeadLetterConsumer implements RocketMQListener<MessageExt> {
    
    @Override
    public void onMessage(MessageExt messageExt) {
        log.error("收到死信消息，msgId: {}, body: {}", 
                  messageExt.getMsgId(), 
                  new String(messageExt.getBody()));
        // 记录日志、告警、人工处理等
    }
}
```

### 5. 消息顺序性保证

```java
// 保证同一订单的消息顺序处理
public void sendOrderedMessages(String orderId, List<String> events) {
    for (String event : events) {
        CommonMessage<String> message = new CommonMessage<>();
        message.setTopic("ORDER_EVENT_TOPIC");
        message.setMessageKey(orderId);  // 同一订单使用相同messageKey
        message.setData(event);
        
        // 必须同步发送才能保证顺序
        rocketProducer.syncSendMessage(message);
    }
}
```

## 常见问题

### 1. 消息发送失败

**问题现象**：消息发送时抛出异常

**排查步骤**：

```java
// 1. 检查NameServer是否可用
// 2. 检查Topic是否存在
// 3. 检查生产者组名是否配置
// 4. 查看日志中的详细错误信息
```

**解决方案**：

```yaml
rocketmq:
  producer:
    # 增加发送超时时间
    send-message-timeout: 5000
    # 增加重试次数
    retry-times-when-send-failed: 3
    retry-next-server: true
```

### 2. 消息重复消费

**解决方案**：实现幂等性处理（见最佳实践第2条）

### 3. 消费者阻塞

**问题现象**：消息堆积，消费者处理缓慢

**解决方案**：

```java
@RocketMQMessageListener(
    topic = "HIGH_LOAD_TOPIC",
    consumerGroup = "high-load-group",
    consumeThreadNumber = 32  // 增加消费线程数
)
```

### 4. 顺序消息消费乱序

**排查步骤**：

1. 确认发送时使用了同步发送
2. 确认设置了相同的messageKey
3. 确认消费者配置了`ConsumeMode.ORDERLY`

```java
// 发送端
message.setMessageKey(orderId);  // 必须设置
rocketProducer.syncSendMessage(message);  // 必须同步发送

// 消费端
@RocketMQMessageListener(
    topic = "...",
    consumerGroup = "...",
    consumeMode = ConsumeMode.ORDERLY  // 必须顺序消费
)
```

### 5. NameServer连接失败

**解决方案**：

```yaml
rocketmq:
  # 多个NameServer用分号分隔，提高可用性
  name-server: 192.168.1.100:9876;192.168.1.101:9876
```

### 6. 延迟消息不生效

**排查步骤**：

1. 确认delayTime单位为毫秒
2. 确认RocketMQ版本支持任意精度延迟（5.0+），低版本只支持固定延迟级别

## 版本信息

- **组件版本**：mq-rocket
- **依赖版本**：RocketMQ Spring Boot Starter
- **兼容性**：Spring Boot 3.x
- **RocketMQ版本**：4.9+ / 5.0+

## 附录：消息类型对比

| 消息类型     | 使用场景      | 配置方式                               |
|----------|-----------|------------------------------------|
| **普通消息** | 一般业务场景    | 默认                                 |
| **顺序消息** | 需要保证消费顺序  | 设置messageKey + ConsumeMode.ORDERLY |
| **延迟消息** | 定时任务、超时处理 | 设置delayTime                        |
| **广播消息** | 通知所有消费者   | MessageModel.BROADCASTING          |
| **事务消息** | 分布式事务     | 使用RocketMQTemplate                 |

## 技术支持

如遇到使用问题，请联系技术支持团队或查阅相关文档。
