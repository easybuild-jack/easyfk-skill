# easyfk-queue Skill 参考文档

> 所属项目：`easyfk-base`　子模块：`queue-disruptor`
> 坐标：`com.mcst:queue-disruptor:3.5.16`
> 依据：全部源码（15 个文件），对齐 `disruptor使用手册.md`、`disruptor特点.md`、`EasyFK框架开发手册.md` §3.8、`easyfk-component/docs/disruptor开发手册.md`。
> 以源码为准；差异见文末「复查记录」。

---

## 1. 模块定位

基于 **LMAX Disruptor 4.0.0** 的进程内高性能内存队列。业务方实现 `Processor<T>` 并注册为 Bean，模块会自动创建同名队列；生产方通过 `IngestQueueManager` 按队列名投递。

适用场景：进程内异步解耦，例如审计日志、埋点、行情或指标的批量落库、多段流水线处理。

**不适用于**：
- 需要持久化或保证不丢失的消息，因为队列纯内存，进程崩溃或关停超时后数据会丢失，这类场景应使用 MQ；
- 跨进程或跨实例通信；
- 需要失败重试或死信的场景，模块没有内置机制，只提供 `Processor#onError` 钩子供业务自行实现。

依赖：`api 'com.lmax:disruptor:4.0.0'`、`api project(':easyfk-core')`。

---

## 2. 引入与自动配置

```groovy
implementation platform('com.mcst:easyfk-dependencies:3.5.16')
implementation 'com.mcst:queue-disruptor'
```

`AutoConfiguration.imports` 中声明了 `DisruptorQueueAutoConfiguration`，**没有任何开关**，引入后即生效。它注册以下 Bean：

| Bean | 说明 |
|---|---|
| `ingestQueueManager` | 门面类，`@ConditionalOnMissingBean`，延迟获取 Registry |
| `ingestQueueRegistry` | `@ConditionalOnMissingBean`；在创建过程中建立所有队列，并**启动全部消费线程** |
| `disruptorShutdownManager` | `@ConditionalOnMissingBean`；实现 `DisposableBean`，容器关闭时并行排空各队列 |

业务方自定义 `IngestQueueRegistry` 时，框架不再建队，队列的创建与启动完全由业务方负责。

建队流程：

1. 遍历 `queues.*` 中显式配置的队列。找不到 Processor 时**启动失败**。
2. `auto-register=true`（默认）时，为每个未绑定的 `Processor` Bean 建立一个与 Bean 同名的队列。自动注册失败同样**启动失败**（`IllegalStateException: Failed to auto-register disruptor queue for processor bean: xxx`），与显式队列一致。
3. 全部队列注册完成后，统一 `start()`，并打印 `Disruptor queues ready: queues=N, consumer threads=M`。

Processor 的查找规则：

1. 配置了 `processor-bean` 时按名称查找；
2. 否则按队列名匹配 Bean 名；
3. 容器中只有一个 Processor 时直接使用它，并打 WARN；
4. 以上都不满足时抛出异常。

---

## 3. 配置

前缀：`easyfk.config.queue.disruptor`

### 3.1 全局配置

| 属性 | 默认值 | 说明 |
|---|---|---|
| `buffer-size` | 65536 | 向上取整到 2 的幂，上限 2^30，≤0 时抛异常 |
| `workers` | CPU 核数 | 每个队列的消费线程数，上限 1000；**消费线程总数 = 队列数 × workers** |
| `producer-type` | `MULTI` | `SINGLE` / `MULTI` |
| `wait-strategy` | `BLOCKING` | `BLOCKING` / `YIELDING` / `BUSY_SPIN` |
| `ordering-mode` | `AUTO` | `AUTO` / `KEY_HASH` / `NONE` |
| `auto-register` | true | 是否为未声明的 Processor 自动建队列 |
| `send-timeout` | `10s` | `send()` 在队列满时的最长等待时间，必须为正数，否则启动失败 |
| `ingest.max-spin-nanos` | 500000 | 全局默认，见 §3.2 |
| `thread.name-prefix` | 空 | 全局前缀，拼接在 Processor Bean 名之前（如 `dq-` → `dq-auditProcessor-0`） |
| `thread.daemon` / `thread.priority` | true / 5 | 全局默认 |
| `shutdown.await-ms` | 60000 | 全局默认 |

全局的 `ingest` / `thread` / `shutdown` 对自动注册的队列和显式队列中未设置的项都生效。

枚举类的取值不区分大小写；无法识别时回退到默认值，并打 WARN（日志中搜索 `falling back to`）。

### 3.2 队列级配置 `queues.<队列名>.*`

| 属性 | 默认值 | 说明 |
|---|---|---|
| `buffer-size` / `workers` / `producer-type` / `wait-strategy` / `ordering-mode` | 取全局值 | 覆盖全局配置 |
| `processor-bean` | 队列名 | 显式绑定 Processor Bean |
| `ingest.max-spin-nanos` | 取全局值（500000） | 队列满时生产者每轮 park 的时长，取值 0 到 1 秒 |
| `thread.name-prefix` | 全局前缀 + Processor Bean 名 | 设置后作为完整前缀；自动补齐结尾的 `-`，最长 50 字符 |
| `thread.daemon` | 取全局值（true） | |
| `thread.priority` | 取全局值（5） | 取值 1 到 10，超出范围启动失败 |
| `shutdown.await-ms` | 取全局值（60000） | 关闭时的排空等待时间 |

优先级：队列级 > 全局 > 代码默认。

```yaml
easyfk:
  config:
    queue:
      disruptor:
        workers: 2                 # 控制总线程数
        send-timeout: 5s
        shutdown:
          await-ms: 20000          # 自动注册的队列同样生效
        queues:
          auditProcessor:
            buffer-size: 32768
            workers: 4
            wait-strategy: BLOCKING
            thread:
              name-prefix: audit
            shutdown:
              await-ms: 30000      # 小于 K8s terminationGracePeriodSeconds
```

### 3.3 producer-type

- `SINGLE` 只有在**整个进程中只有一个线程**向该队列投递时才是安全的。
- 模块只使用 `tryNext()`，Disruptor 的单线程断言不会触发。多线程投递时事件会**被静默覆盖而丢失**，不会抛异常。
- 以下几种情况都属于多生产者：Web 请求线程投递、Processor 向下游队列投递、定时任务投递。**一律保持 `MULTI`**。

### 3.4 wait-strategy

| 策略 | 特点 |
|---|---|
| `BLOCKING` | 默认，CPU 友好，延迟较高 |
| `YIELDING` | 低延迟，CPU 占用中等 |
| `BUSY_SPIN` | 延迟最低，每个消费线程占满 100% CPU，只适用于有独占核心的场景 |

---

## 4. 消费端

### 4.1 Processor

```java
@Component("auditProcessor")              // Bean 名 = 队列名
public class AuditProcessor implements Processor<AuditEvent> {
    @Override
    public void process(AuditEvent e) throws Exception {
        auditRepository.save(e);
    }

    @Override
    public void onError(AuditEvent e, Throwable error) {   // 可选，默认只记日志并丢弃
        auditFailRepository.save(e, error.getMessage());
    }
}
```

- **同一个 Processor 实例会被 workers 个线程并发调用**，必须是线程安全的。
- `process` 抛出的异常（`VirtualMachineError` 除外）交给 `Processor#onError(item, error)`，在同一消费线程中执行。默认实现记录 ERROR 日志（`Disruptor processor ... failed, event dropped`）后**丢弃该事件，不会重试**；需要重试、落库补偿或转投死信队列时覆盖 `onError`。`onError` 自身抛出的异常只记录日志，消费线程继续运行。`orderingKey` 抛出的异常仍由 Disruptor 的 ExceptionHandler 记录（`Disruptor consumer error at seq=...`）。
- 消费线程**透传 TraceId**：投递时捕获投递线程 `TraceIdContext` 的 traceId 存入事件，消费时写入 `TraceIdContext` 与 MDC `TRACE_ID`（`process` 与 `onError` 期间有效），处理完清除。投递时没有 traceId 的事件消费时也不带。只透传 `TRACE_ID`，其他 MDC key 不透传。
- 事件处理完成后，payload 会在 `finally` 中被置为 null，因此不要在 `process` 之外持有事件引用。
- 队列没有泛型校验。投递错误类型时，会在消费端以 `ClassCastException` 的形式记录日志并丢弃。

### 4.2 分片与保序（ordering-mode）

- 每个事件会广播给全部 N 个 handler，只有目标分片的 handler 执行处理，其余 handler 取模后直接返回。这不是工作窃取。
- `NONE`：按 `floorMod(sequence, N)` 分片，可以并行处理，但不保证业务顺序。
- `KEY_HASH`：Processor 必须实现 `KeyOrderedProcessor`，否则**启动失败**。按 Key 的哈希值分片，同一个 Key 在单个队列实例内保持 FIFO。
- `AUTO`：如果 Processor 实现了 `KeyOrderedProcessor`，等同于 `KEY_HASH`，否则等同于 `NONE`。

```java
@Component("orderProcessor")
public class OrderProcessor implements KeyOrderedProcessor<OrderData> {
    @Override public Object orderingKey(OrderData o) { return o.getOrderId(); }
    @Override public void process(OrderData o) { ... }
}
```

`orderingKey` 的要求：
- 应该轻量、线程安全、结果稳定，并返回不可变类型（String / Long / UUID）；
- 返回 null 时回退为按 sequence 分片，该事件不再保序；
- 抛出异常时，该事件会被丢弃。

热点 Key 的影响：所有事件都落在同一个 handler 上，而槽位必须等全部 handler 都处理过才能复用，因此会**拖慢整个队列**，生产者也会被反压。

---

## 5. 生产端（`IngestQueueManager`）

| 方法 | 返回 | 行为 |
|---|---|---|
| `send(name, item)` | boolean | 队列满时最多等待 `send-timeout`（默认 10s），超时打 WARN 并返回 false；队列不存在、关闭中、被中断或发生异常时返回 false；item 为 null 时返回 true |
| `trySend(name, item, timeout, unit)` | boolean | 超时返回 false；timeout 为 0 时只尝试一次；关闭中或被中断时返回 false |
| `sendBatch(name, items, timeout, unit)` | int | timeout 是**整批的总截止时间**，每项只用剩余时间，截止后剩余各项只做一次非阻塞尝试；返回成功的数量，null 项跳过 |
| `sendWithRetry(name, item, maxRetries, timeout, unit)` | boolean | 最多执行 maxRetries+1 次 `trySend`，每次间隔 10ms×n |
| `getQueue` / `hasQueue` / `getAllQueueNames` / `getAllQueues` | — | 查询 |

```java
@Resource
private IngestQueueManager queueManager;

if (!queueManager.trySend("auditProcessor", event, 100, TimeUnit.MILLISECONDS)) {
    log.warn("审计队列已满，降级处理");   // 必须处理 false
}
```

- 在 Web 请求线程和 Processor 内部（管道模式）**优先使用 `trySend`** 指定较短的超时，并处理返回 false 的情况。`send` 在下游变慢时会阻塞调用线程直到 `send-timeout`。
- 底层 `IIngestQueue#accept` 仍是无超时的阻塞投递，业务代码不要直接调用。
- 队列名写错时只会打 WARN 并返回 false，不会抛异常。
- 管道模式：Processor 注入 `IngestQueueManager` 后向下游投递。不要注入 `IngestQueueRegistry`，否则会形成循环依赖。

---

## 6. 关闭与数据安全

- 容器关闭时，`ShutdownManager` 为每个队列开一个线程并行执行 `shutdown(awaitMs)`，总等待时间为 max(awaitMs) + 5s。
- 单个队列的关闭过程：
  1. 用 CAS 把状态置为不再运行，之后的投递一律被拒绝；
  2. 等待 min(100ms, awaitMs/10)，让进行中的投递完成；
  3. 调用 `disruptor.shutdown(awaitMs)` 排空队列，超时则打 WARN；**未处理完的事件会丢失**。
- 进程被强杀、OOM 或崩溃时，RingBuffer 中的数据会全部丢失。
- `shutdown.await-ms` 应小于部署平台的关停宽限期。

---

## 7. 生成代码时的规则

**应该这样做：**

- Processor 的 Bean 名称就是队列名，应显式写在 `@Component("xxxProcessor")` 中，生产方使用同一个字符串（建议定义为常量）。
- 显式设置全局 `workers`。默认值是 CPU 核数，乘以队列数后线程数量可能很大。
- 需要失败补偿时覆盖 `Processor#onError`（重试、落库或转投死信队列）。
- 需要同一业务键保序时，实现 `KeyOrderedProcessor` 并配置 `ordering-mode: KEY_HASH`（让漏实现接口的情况在启动时就失败）。
- 生产方使用 `trySend` 并处理 false；使用 `send` 时同样要处理 false。
- 自动注册的队列通过全局 `thread` / `shutdown` / `ingest` 调整参数。

**不要这样做：**

- 不要配置 `producer-type: SINGLE`，除非能证明只有一个投递线程。
- 不要在请求线程中使用 `send()` 且依赖默认 10s 超时，应使用 `trySend` 并给出较短超时。
- 不要依赖它保存关键业务数据（例如订单、支付），它不保证不丢失。
- 不要在 Processor 中保存非线程安全的可变状态。
- 不要在没有独占 CPU 的环境中使用 `BUSY_SPIN`。
- 不要在 `onError` 中阻塞过久，它占用的是消费线程。

---

## 8. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | 框架手册 §3.8.1 | "工作窃取与基于哈希的分片" | 没有工作窃取。Disruptor 4 已移除 WorkerPool，实现方式是广播给所有 handler 后按分片过滤 |
| 2 | 特点 §2.1 | 通过 `ringBuffer.next()` 申请序列号 | 只使用 `tryNext()`，同一文档 §2.5 的描述是正确的 |
| 3 | 特点 §2.9 | 关闭时遍历 registry，逐个调用 shutdown | 实际为每个队列开线程并行关闭，总预算为 max(awaitMs)+5s；使用手册 §6.4 的描述是正确的 |
| 4 | 特点 §3.3 | "所有核心 Bean 使用 `@ConditionalOnMissingBean`" | 只有 `IngestQueueManager` 带这个注解，Registry 和 ShutdownManager 都不带 **已修复**：Registry 与 ShutdownManager 也加上 `@ConditionalOnMissingBean` |
| 5 | 使用手册 §5.1 / 框架手册 | 未说明 | `process` 抛出的异常只记录日志，该事件被丢弃，不会重试 **已修复**：异常交给可覆盖的 `Processor#onError(item, error)`，默认记录日志后丢弃 |
| 6 | 三份文档 | 未说明 | 消费线程不透传 TraceId / MDC **已修复**：投递时捕获 traceId 存入事件，消费期间写入 `TraceIdContext` 与 MDC `TRACE_ID`，处理完清除 |
| 7 | 使用手册 §4.2 | `send` 为"阻塞模式发送" | 没有任何超时上限，下游变慢时会无限期阻塞调用方；框架手册的示例在业务方法中直接使用 `send` **已修复**：`send` 最多等待可配置的 `send-timeout`（默认 10s），超时返回 false |
| 8 | 使用手册 §9.1 | 自动注册流程 | 显式队列失败会导致启动失败，而自动注册失败只打 ERROR 日志并跳过 **已修复**：自动注册失败同样抛 `IllegalStateException` 中止启动 |
| 9 | 使用手册 §8.2 | 列出了 `ingest` / `thread` / `shutdown` | 这三项只有队列级配置，自动注册的队列无法调整，必须显式声明 **已修复**：新增全局 `ingest` / `thread` / `shutdown`，按队列级 > 全局 > 默认回退，自动注册队列同样生效 |
| 10 | 框架手册 §3.8.2 | 使用 camelCase 配置键，Bean 名为 `auditQueue` | 依靠宽松绑定可以生效，但与其他文档使用的 kebab-case 不一致；Bean 名 = 队列名的约定是正确的 |
| 11 | 使用手册 §6.1 | `sendBatch` 的 timeout | timeout 按单项计算，整批最长耗时约为 n×timeout **已修复**：timeout 改为整批总截止时间，每项只用剩余时间 |
| 12 | `easyfk-component/docs/disruptor开发手册.md` §4.3 / §8.1 | 全局 `producer-type` 默认 `SINGLE`，全局配置只有 4 项 | 默认值为 `MULTI`；全局还有 `ordering-mode`（默认 AUTO）与 `auto-register`（默认 true） |
| 13 | `easyfk-component/docs/disruptor开发手册.md` §6.3 | `GenericWorkHandler` 按 `sequence % shardTotal` 分片 | 只是 `NONE` 模式的行为；`KEY_HASH` / `AUTO`（Processor 实现 `KeyOrderedProcessor`）时按业务 Key 哈希分片并保证同 Key FIFO |
