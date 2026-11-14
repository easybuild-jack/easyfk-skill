# easyfk-queue/queue-disruptor 开发文档

## 1. 模块概述

`queue-disruptor` 是 EasyFK 框架的**高性能内存队列模块**，基于 LMAX Disruptor 4.0 构建，提供了低延迟、高吞吐量的事件处理能力。该模块通过 Spring Boot 自动配置机制，支持声明式的队列定义和 Processor 自动绑定，开发者只需实现 `Processor` 接口即可完成队列的消费逻辑。

---

## 2. 模块依赖

| 依赖 | 版本 | 说明 |
|---|---|---|
| `com.lmax:disruptor` | `4.0.0` | LMAX Disruptor 高性能队列框架 |

**build.gradle:**
```groovy
dependencies {
    api('com.lmax:disruptor:4.0.0')
}
```

---

## 3. 包结构

```
com.mcst.easyfk.queue.disruptor
├── api/                          # 接口定义
│   ├── IIngestQueue<T>             - 摄入队列接口
│   ├── Processor<T>                - 数据处理器接口
│   ├── KeyOrderedProcessor<T>       - 按业务 Key 保序的处理器接口
│   └── IQueueLifecycle             - 队列生命周期接口
├── config/                       # 自动配置
│   ├── DisruptorQueueAutoConfiguration - 自动配置类
│   └── ShutdownManager             - 优雅关闭管理器
├── core/                         # 核心实现
│   ├── DisruptorIngestQueue<T>     - Disruptor 队列实现（含 Builder）
│   ├── IngestQueueManager          - 队列管理器（门面类）
│   ├── IngestQueueRegistry         - 队列注册表
│   ├── Event<T>                    - 事件对象
│   ├── EventFactoryImpl<T>         - 事件工厂
│   └── GenericWorkHandler<T>       - 通用工作处理器（分片）
├── enums/                        # 枚举
│   ├── OrderingMode                 - 分片/保序模式
│   └── WaitStrategyType             - 等待策略类型
└── properties/                   # 配置属性
    └── DisruptorQueuesProperties   - 队列配置属性
```

---

## 4. 快速开始

### 4.1 实现 Processor

```java
@Component("orderProcessor")
public class OrderProcessor implements Processor<OrderData> {

    @Override
    public void process(OrderData item) throws Exception {
        // 处理订单数据
        orderService.processOrder(item);
    }
}
```

### 4.2 发送数据到队列

```java
@Service
public class OrderService {

    @Resource
    private IngestQueueManager queueManager;

    public void submitOrder(OrderData order) {
        // 阻塞模式发送
        queueManager.send("orderProcessor", order);

        // 非阻塞模式发送（推荐）
        boolean success = queueManager.trySend("orderProcessor", order, 100, TimeUnit.MILLISECONDS);
    }
}
```

**说明：** 模块会自动发现 `Processor` Bean 并创建同名队列，无需任何配置即可使用。

> **注意消费线程的总量。** 每个队列都会按 `workers` 拉起一组独立的消费线程，而自动注册会为
> **每一个** `Processor` Bean 各建一个队列，因此消费线程总数是 `队列数 × workers`。
> `workers` 默认取 CPU 核心数，所以 32 核机器上的 6 个 `Processor` 会产生 192 个消费线程。
> 需要控制时，可以显式下调 `workers`，或用 `auto-register: false` 关掉自动注册改为逐个声明。
> 启动完成后模块会打印一条 `Disruptor queues ready: queues=..., consumer threads=...` 供核对。

### 4.3 可选配置

```yaml
easyfk:
  config:
    queue:
      disruptor:
        buffer-size: 65536          # 全局 RingBuffer 大小（2的幂）
        workers: 4                  # 全局工作线程数（注意：消费线程总数 = 队列数 × 本值）
        producer-type: MULTI        # 全局生产者类型，默认 MULTI
        wait-strategy: BLOCKING     # 全局等待策略
        ordering-mode: AUTO         # AUTO / KEY_HASH / NONE
        auto-register: true         # 是否为未显式声明的 Processor 自动建队列
        queues:
          orderProcessor:           # 队列名称（对应 Processor Bean 名称）
            buffer-size: 131072     # 覆盖全局配置
            workers: 8
            producer-type: MULTI
            wait-strategy: YIELDING
            ordering-mode: KEY_HASH # 覆盖全局保序模式
            processor-bean: orderProcessor  # 可选，显式绑定
            ingest:
              max-spin-nanos: 500000
            thread:
              name-prefix: order-worker-
              daemon: true
              priority: 5
            shutdown:
              await-ms: 60000
```

---

## 5. 核心接口

### 5.1 Processor\<T\> —— 数据处理器

```java
public interface Processor<T> {
    void process(T item) throws Exception;
}
```

实现该接口定义队列的消费逻辑。每个 `Processor` Bean 会自动关联一个同名队列。

### 5.2 KeyOrderedProcessor\<T\> —— 按业务 Key 保序

```java
public interface KeyOrderedProcessor<T> extends Processor<T> {
    Object orderingKey(T item);
}
```

处理器实现该接口后，`AUTO` 或 `KEY_HASH` 模式会按 `orderingKey()` 返回值进行哈希分片。相同 Key 的事件固定由同一个 Worker 按 RingBuffer 序列顺序处理，从而保证同 Key FIFO。

- 推荐返回 `String`、`Long`、`Integer`、`UUID` 等不可变类型。
- `orderingKey()` 应轻量、线程安全、结果稳定且不抛异常。
- 返回 `null` 时，该事件回退为按 RingBuffer sequence 分片，不保证业务顺序。
- 热点 Key 只会使用一个 Worker，其吞吐量受单 Worker 处理能力限制。

### 5.3 IIngestQueue\<T\> —— 摄入队列接口

| 方法 | 说明 |
|---|---|
| `accept(T item)` | 阻塞式放入队列，队列满时自旋等待 |
| `tryAccept(T item, long timeout, TimeUnit unit)` | 超时式放入队列，超时返回 false |

### 5.4 IQueueLifecycle —— 生命周期接口

| 方法 | 说明 |
|---|---|
| `start()` | 启动队列 |
| `shutdown(long awaitMs)` | 优雅关闭队列，等待指定毫秒数 |

---

## 6. 核心组件详解

### 6.1 IngestQueueManager —— 队列管理器（门面类）

提供统一的队列操作入口，**推荐在业务代码中使用此类**。

| 方法 | 返回值 | 说明 |
|---|---|---|
| `getQueue(name)` | `IIngestQueue<T>` | 获取队列实例 |
| `send(name, item)` | `boolean` | 阻塞模式发送 |
| `trySend(name, item, timeout, unit)` | `boolean` | 非阻塞超时发送（推荐） |
| `sendBatch(name, items, timeout, unit)` | `int` | 批量发送，返回成功数量 |
| `sendWithRetry(name, item, maxRetries, timeout, unit)` | `boolean` | 带重试的发送（递增退避） |
| `hasQueue(name)` | `boolean` | 检查队列是否存在 |
| `getAllQueueNames()` | `Set<String>` | 获取所有队列名称 |
| `getAllQueues()` | `Map<String, IIngestQueue<?>>` | 获取所有队列实例 |

**在 Processor 中访问其他队列：**

```java
@Component("stepOneProcessor")
public class StepOneProcessor implements Processor<RawData> {

    @Resource
    private IngestQueueManager queueManager;

    @Override
    public void process(RawData item) throws Exception {
        ProcessedData result = doProcess(item);
        // 发送到下一个队列（管道模式）
        queueManager.trySend("stepTwoProcessor", result, 100, TimeUnit.MILLISECONDS);
    }
}
```

### 6.2 DisruptorIngestQueue —— 核心队列实现

基于 Disruptor RingBuffer 实现的高性能队列。

**accept() 流程：**

```
accept(item)
    │
    ├─ null 检查 → null 直接返回
    │
    ├─ running 检查 → 已关闭抛 RejectedExecutionException
    │
    └─ 自旋循环
        ├─ 中断检查 → 已中断抛 RejectedExecutionException
        ├─ running 检查 → 已关闭抛 RejectedExecutionException
        ├─ 容量检查 → 有空间 → tryPublishEvent → 成功返回
        └─ 无空间 → LockSupport.parkNanos(maxSpinNanos) → 继续循环
```

**tryPublishEvent() 流程：**

```
tryPublishEvent(item)
    │
    ├─ ringBuffer.tryNext() → 非阻塞申请序列号
    │       └─ 容量不足 → 返回 false（由调用方自旋重试或超时）
    ├─ ringBuffer.get(seq) → 获取 Event 对象
    ├─ event.targetShard = 未分配 → 清除复用对象的旧路由
    ├─ event.setPayload(item) → 设置负载
    ├─ ringBuffer.publish(seq) → 发布事件
    │
    └─ 异常处理
        └─ 发布空事件（payload=null）→ 保持序列号一致性
```

### 6.3 GenericWorkHandler —— 分片工作处理器

使用普通 `final class` 实现，支持两种分片策略：

- `NONE`：按 RingBuffer sequence 取模，仅提供并行处理，不保证业务顺序。
- `KEY_HASH`：按业务 Key 哈希分片，保证同 Key FIFO。
- `AUTO`：处理器实现 `KeyOrderedProcessor` 时使用 `KEY_HASH`，否则使用 `NONE`。

`KEY_HASH` 模式下，每个事件只计算一次目标分片，并将结果缓存在 `Event` 中。其他 handler 复用该结果，不会在业务处理期间并发读取可变 payload，从而避免同一事件被重复路由。

处理完成后，无论业务处理是否抛出异常，winner handler 都会在 `finally` 中清空 payload，避免 RingBuffer 复用对象长期持有业务数据。

**NONE 分片示例（4个 Worker）：**

| 序列号 | Worker 0 | Worker 1 | Worker 2 | Worker 3 |
|---|---|---|---|---|
| 0 | 处理 | 跳过 | 跳过 | 跳过 |
| 1 | 跳过 | 处理 | 跳过 | 跳过 |
| 2 | 跳过 | 跳过 | 处理 | 跳过 |
| 3 | 跳过 | 跳过 | 跳过 | 处理 |

### 6.4 ShutdownManager —— 优雅关闭

实现 `DisposableBean`，在 Spring 容器销毁时自动关闭所有队列：

```
Spring 容器关闭
    │
    └─ ShutdownManager.destroy()
        │
        ├─ 所有队列并行提交关闭任务，每个队列取自己的 awaitMs（默认 60000ms）
        │   └─ IQueueLifecycle.shutdown(awaitMs)
        │       ├─ CAS 设置 running=false（幂等）
        │       ├─ 等待进行中的 accept 完成
        │       └─ disruptor.shutdown(awaitMs, MILLISECONDS)
        │
        └─ 统一等待，总预算 = max(各队列 awaitMs) + 5s 余量
```

**为什么是并行的：** 每个队列的 `await-ms` 默认就有 60 秒，串行关闭时总耗时是各队列之和。6 个队列最坏要等 360 秒，远超常见的容器关停超时和 K8s 的 `terminationGracePeriodSeconds`，进程会被强杀，尚未排空的事件反而全部丢失。并行之后总耗时退化为各队列中的最大值。

如果部署环境的关停宽限期比较短，应当把 `shutdown.await-ms` 调到宽限期以内，而不是依赖默认的 60 秒。

---

## 7. 等待策略

| 策略 | 枚举值 | CPU 占用 | 延迟 | 适用场景 |
|---|---|---|---|---|
| 阻塞等待 | `BLOCKING` | 低 | 较高 | 默认策略，适合大多数场景 |
| 让出等待 | `YIELDING` | 中 | 较低 | 低延迟与 CPU 资源的平衡 |
| 忙等待 | `BUSY_SPIN` | 极高（100%） | 最低 | 对延迟极其敏感的场景 |

---

## 8. 配置属性详解

### 8.1 全局配置

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `buffer-size` | Integer | 65536 | RingBuffer 大小（自动对齐到 2 的幂，上限 2^30） |
| `workers` | Integer | CPU 核心数 | 每个队列的工作线程数量；消费线程总数 = 队列数 × 本值 |
| `producer-type` | String | `MULTI` | 生产者类型：`SINGLE` / `MULTI`，改 `SINGLE` 前务必读 8.3 |
| `wait-strategy` | String | `BLOCKING` | 等待策略：`BLOCKING` / `YIELDING` / `BUSY_SPIN` |
| `ordering-mode` | String | `AUTO` | 分片/保序模式：`AUTO` / `KEY_HASH` / `NONE` |
| `auto-register` | boolean | `true` | 是否为未显式声明的 `Processor` Bean 自动创建队列 |

> 取值无法识别时（例如把 `BLOCKING` 写成 `BLOKING`）不会启动失败，而是回退到默认值并打一条
> WARN 日志，排查配置未生效时可以先搜索 `falling back to`。

### 8.2 队列级配置（覆盖全局）

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `buffer-size` | Integer | 全局值 | RingBuffer 大小 |
| `workers` | Integer | 全局值 | 工作线程数量 |
| `producer-type` | String | 全局值 | 生产者类型 |
| `wait-strategy` | String | 全局值 | 等待策略 |
| `ordering-mode` | String | 全局值 | 分片/保序模式 |
| `processor-bean` | String | 队列名称 | 显式绑定 Processor Bean |
| `ingest.max-spin-nanos` | long | 500000 | 生产者自旋等待纳秒数 |
| `thread.name-prefix` | String | Processor Bean 名称 | 工作线程名称前缀 |
| `thread.daemon` | boolean | true | 是否为守护线程 |
| `thread.priority` | int | 5 | 线程优先级（1-10） |
| `shutdown.await-ms` | long | 60000 | 关闭等待时间（毫秒） |

**配置优先级：** 队列特定配置 > 全局配置 > 代码默认值

### 8.3 关于 `producer-type`：SINGLE 的使用前提

默认值是 `MULTI`。**只有在能确证整个进程自始至终只有一个线程向该队列投递时，才可以改成 `SINGLE`。**

Disruptor 的 `SingleProducerSequencer` 在类注释里写得很直白：

> Not safe for use from multiple threads as it does not implement any barriers.

它申请序列号的核心动作是 `this.nextValue += n`，作用在一个**非 volatile 的长整型字段**上，是非原子的读-改-写。两个线程并发投递时会拿到同一个序列号，各自把数据写进同一个 RingBuffer 槽位，再对同一序列号发布两次。结果是**其中一条事件被静默覆盖**：不抛异常、不打日志、监控上也看不出来，只有对账时才会发现少了数据。

需要格外注意两点：

1. `IngestQueueManager.send()` / `trySend()` 对所有线程开放。Web 请求线程直接投递是常态；而在 `Processor` 里向下游队列投递（本手册 4.2 的示例写法）意味着上游队列的 N 个消费线程同时是下游队列的 N 个生产者。这些场景全都是多生产者。
2. Disruptor 4.0 为这类误用加了断言 `assert sameThread() : "Accessed by two threads - use ProducerType.MULTI!"`，但**该断言只存在于 `next()` 中**。本模块出于超时可控的考虑只使用 `tryNext()`（原因见《disruptor特点》），所以即使带 `-ea` 运行，这个误用也不会被捕获。

配置成 `SINGLE` 时启动日志里会有一条 WARN 提醒，属于预期行为。`MULTI` 的代价只是申请序列号时多一次 CAS，绝大多数场景下不构成瓶颈。

---

## 9. 自动配置机制

### 9.1 Processor 自动发现

模块启动时自动扫描所有 `Processor` 类型的 Bean，并为每个 Processor 创建对应的队列：

```
启动流程
    │
    ├─ 1. 扫描配置文件中显式定义的队列（优先级最高）
    │     └─ 查找对应 Processor Bean → 创建并注册队列（此时尚未启动消费线程）
    │
    ├─ 2. 扫描未被绑定的 Processor Bean（auto-register: true 时）
    │     └─ 使用全局默认配置 → 自动创建并注册队列（同样尚未启动）
    │
    └─ 3. 全部注册完成后，统一启动所有队列的消费线程
```

第 3 步单独拆出来是必要的：消费线程一旦跑起来，`Processor` 就可能立刻通过 `IngestQueueManager` 向下游队列投递（即 10.2 的管道模式），而按注册顺序边建边启动时，下游队列可能还没进注册表，投递会以 `Queue not found` 静默失败。

### 9.2 Processor 查找规则

1. 如果配置了 `processor-bean`，直接按名称查找
2. 如果未配置，尝试用队列名称匹配 Processor Bean 名称
3. 如果容器中只有一个 Processor，直接使用（会打 WARN，因为队列名写错时表现完全相同）
4. 以上都不匹配时抛出异常

---

## 10. 使用模式

### 10.1 单队列模式

```java
@Component("logProcessor")
public class LogProcessor implements Processor<LogEntry> {
    @Override
    public void process(LogEntry item) {
        // 写入日志存储
    }
}
```

### 10.2 管道模式（多队列串联）

```java
@Component("parseProcessor")
public class ParseProcessor implements Processor<RawData> {
    @Resource
    private IngestQueueManager queueManager;

    @Override
    public void process(RawData item) {
        ParsedData parsed = parse(item);
        queueManager.trySend("enrichProcessor", parsed, 100, TimeUnit.MILLISECONDS);
    }
}

@Component("enrichProcessor")
public class EnrichProcessor implements Processor<ParsedData> {
    @Override
    public void process(ParsedData item) {
        // 数据增强处理
    }
}
```

### 10.3 同 Key 保序模式

```java
@Component("orderProcessor")
public class OrderProcessor implements KeyOrderedProcessor<OrderData> {

    @Override
    public Object orderingKey(OrderData item) {
        return item.getOrderId();
    }

    @Override
    public void process(OrderData item) {
        orderService.processOrder(item);
    }
}
```

使用默认 `ordering-mode: AUTO` 即可自动启用同 Key 保序。也可配置 `KEY_HASH` 强制校验处理器必须实现 `KeyOrderedProcessor`；否则队列创建时会失败。

该保证仅覆盖同一个队列实例中的事件处理顺序，不保证不同队列、不同应用实例或重新分片后的全局顺序。

### 10.4 带重试的发送

```java
boolean success = queueManager.sendWithRetry("targetQueue", data, 3, 50, TimeUnit.MILLISECONDS);
```

### 10.5 批量发送

```java
List<OrderData> orders = getOrders();
int sent = queueManager.sendBatch("orderProcessor", orders, 100, TimeUnit.MILLISECONDS);
```
