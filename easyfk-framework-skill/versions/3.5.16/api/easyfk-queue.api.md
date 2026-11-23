# easyfk-queue API 签名速查（easyfk 3.5.16）

> 坐标：`com.mcst:queue-disruptor`　源码：`easyfk-base/easyfk-queue/queue-disruptor`
> 由 `scripts/gen-api.py` 从 15 个源文件自动提取，共 15 个类型、41 个方法/构造器、18 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-queue-skill.md](../modules/easyfk-queue-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 配置项（@ConfigurationProperties）

### `easyfk.config.queue.disruptor` ← DisruptorQueuesProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `buffer-size` | `Integer` | `—` | RingBuffer 大小（必须为2的幂），默认 65536 |
| `workers` | `Integer` | `—` | worker 数量，默认=物理核心数； 注意消费线程总数是 队列数 × worker 数：每个 worker 对应一个独立的 Disruptor 消费线程… |
| `producer-type` | `String` | `—` | 生产者类型：SINGLE/MULTI，默认 MULTI SINGLE 对应的 SingleProducerSequencer 不设置任何内存屏障， 多个线程并发投递会拿到相同的序列号并静默覆盖彼此的事件… |
| `wait-strategy` | `String` | `—` | 等待策略：BLOCKING / YIELDING / BUSY_SPIN，默认 BLOCKING |
| `ordering-mode` | `String` | `—` | 分片/保序模式：AUTO / KEY_HASH / NONE，默认 AUTO AUTO 表示根据 Processor 是否实现 KeyOrderedProcessor 自动决定… |
| `auto-register` | `boolean` | `true` | 是否为未在 queues 中显式声明的 Processor Bean 自动创建队列，默认 true 自动创建的每个队列都会按 workers 拉起独立的消费线程组… |
| `send-timeout` | `Duration` | `Duration.ofSeconds(10)` | IngestQueueManager#send 在队列满时的最长等待时间，默认 10 秒，必须为正数。 超时后返回 false |
| `ingest` | `Ingest` | `new Ingest()` | 全局摄入配置，队列级 queues..ingest 未设置的项回退到这里 |
| `thread` | `ThreadConf` | `new ThreadConf()` | 全局线程配置，队列级 queues..thread 未设置的项回退到这里。 全局 name-prefix 会拼接在 Processor Bean 名之前，队列级 name-prefix 则直接作为完整前缀 |
| `shutdown` | `Shutdown` | `new Shutdown()` | 全局关闭配置，队列级 queues..shutdown 未设置的项回退到这里 |
| `queues` | `Map<String, QueueConf>` | `new LinkedHashMap<>()` |  |


## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `queue-disruptor` | `com.mcst.easyfk.queue.disruptor.config.DisruptorQueueAutoConfiguration` |

## 类型索引

- `com.mcst.easyfk.queue.disruptor.api`：[IIngestQueue](#iingestqueue)、[IQueueLifecycle](#iqueuelifecycle)、[KeyOrderedProcessor](#keyorderedprocessor)、[Processor](#processor)
- `com.mcst.easyfk.queue.disruptor.config`：[DisruptorQueueAutoConfiguration](#disruptorqueueautoconfiguration)、[ShutdownManager](#shutdownmanager)
- `com.mcst.easyfk.queue.disruptor.core`：[DisruptorIngestQueue](#disruptoringestqueue)、[Event](#event)、[EventFactoryImpl](#eventfactoryimpl)、[GenericWorkHandler](#genericworkhandler)、[IngestQueueManager](#ingestqueuemanager)
    [IngestQueueRegistry](#ingestqueueregistry)
- `com.mcst.easyfk.queue.disruptor.enums`：[OrderingMode](#orderingmode)、[WaitStrategyType](#waitstrategytype)
- `com.mcst.easyfk.queue.disruptor.properties`：[DisruptorQueuesProperties](#disruptorqueuesproperties)

## 包 `com.mcst.easyfk.queue.disruptor.api`

### IIngestQueue

`public interface IIngestQueue<T>`　摄入队列接口 该接口定义了向队列中提交数据的基本操作。 实现类负责将提交的数据项放入底层队列中，并确保数据能够被消费者处理。

**方法**

```java
void accept(T item)  // 接受一个数据项并将其放入队列 该方法会尝试将数据项放入队列，如果队列已满，则会阻塞直到有空间可用。 如果队列已关闭，可能会抛出异常。
default boolean tryAccept(T item, long timeout, java.util.concurrent.TimeUnit unit)  // 尝试在指定的超时时间内将数据项放入队列 该方法会尝试将数据项放入队列，如果在指定的超时时间内无法放入，则返回false。 默认实现抛出 UnsupportedOperationException…
```

### IQueueLifecycle

`public interface IQueueLifecycle`　队列生命周期管理接口 该接口定义了队列的生命周期管理操作，包括启动和关闭。 实现该接口的队列可以被外部系统控制其启动和关闭过程。

**方法**

```java
void start()  // 启动队列 该方法用于初始化和启动队列，使其准备好接收和处理数据。 对于已经启动的队列，该方法应该是幂等的。
void shutdown(long awaitMs) throws InterruptedException, TimeoutException  // 关闭队列 该方法用于优雅地关闭队列，等待正在处理的任务完成。 如果在指定的等待时间内无法完成关闭，则可能抛出TimeoutException。
```

### KeyOrderedProcessor

`public interface KeyOrderedProcessor<T> extends Processor<T>`　按业务 Key 保序的处理器接口（opt-in） 当 Processor 同时实现该接口后，队列在多 worker 场景下会按 orderingKey(Object) 返回值进行哈希分片：相同 Key 的事件一定路由到同…

**方法**

```java
Object orderingKey(T item)  // 返回用于路由分片的业务 Key 框架对非空 Key 调用 key.hashCode() 后做扰动再取模分片， 因此 Key 的 hashCode() 必须稳定（同一 JVM 周期内相同实例多次调用结果一致）…
```

### Processor

`public interface Processor<T>`　数据处理器接口 该接口定义了处理队列中数据项的核心业务逻辑。 实现该接口的类负责定义如何处理从队列中消费的每个数据项。 处理器通常由应用程序提供，作为队列消费者的业务逻辑实现。

**方法**

```java
void process(T item) throws Exception  // 处理单个数据项 该方法由队列的消费者线程调用，用于处理从队列中获取的数据项。 实现类应该在此方法中定义具体的业务处理逻辑。 抛出的异常会交给 onError(Object, Throwable) 处理，事件不会自动重试。
default void onError(T item, Throwable error)  // process(Object) 抛出异常时的回调，在同一个消费线程中执行，traceId 与 process 一致 默认记录 ERROR 日志后丢弃该事件…
```

## 包 `com.mcst.easyfk.queue.disruptor.config`

### DisruptorQueueAutoConfiguration

`public class DisruptorQueueAutoConfiguration`　注解：`@SuppressWarnings({"unchecked", "rawtypes"})` `@AutoConfiguration` `@EnableConfigurationProperties(DisruptorQueuesProperties.class)`　Disruptor队列自动配置类 该类负责自动配置和创建基于Disruptor的队列实例。它通过以下方式工作： 1. 自动发现所有Processor类型的Bean 2…

**方法**

```java
@Bean @ConditionalOnMissingBean IngestQueueManager ingestQueueManager(ApplicationContext applicationContext, DisruptorQueuesProperties props)  // 创建IngestQueueManager实例 该方法负责管理所有队列的生命周期，包括创建、启动、停止和销毁。 它通过ApplicationContext获取所有队列实例，并提供统一的API接口供外部使用。
@Bean @ConditionalOnMissingBean IngestQueueRegistry ingestQueueRegistry(DisruptorQueuesProperties props, ListableBeanFactory factory)  // 创建并配置IngestQueueRegistry，注册所有队列实例 该方法执行以下操作： 1. 创建队列注册表 2. 处理显式配置的队列，优先级最高 3. 为未配置的Processor自动创建队列
@Bean @ConditionalOnMissingBean ShutdownManager disruptorShutdownManager(IngestQueueRegistry registry, DisruptorQueuesProperties props)  // 创建ShutdownManager，负责在应用关闭时正确关闭所有队列
```

### ShutdownManager

`public record ShutdownManager(IngestQueueRegistry registry, DisruptorQueuesProperties props) implements DisposableBean`　队列关闭管理器 该类负责在Spring容器关闭时，优雅地关闭所有注册的队列。 它实现了Spring的DisposableBean接口，在容器销毁时自动调用destroy方法…

**构造参数（record 组件）**

```java
IngestQueueRegistry registry
DisruptorQueuesProperties props
```

**方法**

```java
void destroy()  // 销毁方法，由Spring容器在关闭时调用 该方法会并行关闭所有注册的队列，并等待全部完成或到达总超时。 单个队列关闭过程中的异常会被记录，不影响其他队列。
```

## 包 `com.mcst.easyfk.queue.disruptor.core`

### DisruptorIngestQueue

`public class DisruptorIngestQueue<T> implements IIngestQueue<T>, IQueueLifecycle`　基于Disruptor实现的摄入队列 该类是IIngestQueue接口的核心实现，基于LMAX Disruptor高性能队列框架。 它提供了高吞吐量、低延迟的队列实现，支持多种等待策略和生产者模式…

**方法**

```java
int workers()  // 该队列实际占用的消费线程数量 每个 worker 对应一个独立的 Disruptor 消费线程，因此进程内的消费线程总数是各队列本值之和。
void accept(T item)  // 接受一个数据项并将其放入队列 该方法实现了IIngestQueue接口的accept方法。 它会尝试将数据项放入RingBuffer，如果RingBuffer已满，则会自旋等待直到有空间可用…
boolean tryAccept(T item, long timeout, java.util.concurrent.TimeUnit unit)  // 尝试在指定的超时时间内将数据项放入队列 该方法实现了IIngestQueue接口的tryAccept方法。 它会尝试在指定的超时时间内将数据项放入RingBuffer，如果在超时时间内无法放入，则返回false…
void start()  // 启动队列的消费线程 该方法实现了IQueueLifecycle接口的start方法，可重复调用（后续调用为空操作）…
void shutdown(long awaitMs) throws TimeoutException  // 关闭队列 该方法实现了IQueueLifecycle接口的shutdown方法。 它会设置队列状态为关闭，并等待所有正在处理的事件完成。 如果在指定的等待时间内无法完成关闭，则可能抛出TimeoutException。
```

#### DisruptorIngestQueue.Builder

`public static class Builder<T>`　DisruptorIngestQueue的构建器类 该类实现了Builder模式，用于创建和配置DisruptorIngestQueue实例。 它提供了流式API，可以方便地设置各种参数。

**字段 / 常量**

```java
static final int MAX_BUFFER_SIZE = 1 <<30  // RingBuffer 最大槽位数
static final int DEFAULT_BUFFER_SIZE = 65536  // 默认 RingBuffer 槽位数
```

**方法**

```java
Builder<T> bufferSize(int bufferSize)  // 设置缓冲区大小 缓冲区大小必须是2的幂，该方法会自动调整为不小于指定值的最小2的幂。
Builder<T> workers(int workers)  // 设置工作线程数量 工作线程数量至少为1，该方法会自动调整为至少1的值。
Builder<T> producerType(com.lmax.disruptor.dsl.ProducerType p)  // 设置生产者类型，默认 MULTI SINGLE 仅在能确证全进程只有一个线程投递时才可使用。 Disruptor 的 SingleProducerSequencer 明确声明"不支持多线程访问…
Builder<T> waitStrategy(WaitStrategyType ws)  // 设置等待策略 等待策略决定了消费者在没有可用事件时如何等待。
Builder<T> threadNamePrefix(String p)  // 设置线程名称前缀 该前缀用于命名工作线程，便于识别和调试。
Builder<T> daemon(boolean d)  // 设置是否使用守护线程 如果设置为true，则工作线程将作为守护线程运行，不会阻止JVM退出。
Builder<T> priority(int p)  // 设置线程优先级 线程优先级范围为1-10，其中1为最低优先级，10为最高优先级。
Builder<T> maxSpinNanos(long n)  // 设置最大自旋等待纳秒数 当RingBuffer已满时，生产者会自旋等待，该参数控制每次自旋的最大等待时间。
Builder<T> processor(Processor<T> p)  // 设置处理器 处理器用于处理队列中的数据项，是必需的组件。
Builder<T> orderingMode(OrderingMode mode)  // 设置分片/保序模式 决定多 worker 场景下事件如何在 handler 间分片： AUTO（默认）：根据 Processor 是否实现 KeyOrderedProcessor 自动判定…
DisruptorIngestQueue<T> buildAndStart()  // 构建并启动队列 等价于 build() 之后立即调用 start()。
DisruptorIngestQueue<T> build()  // 构建队列，但不启动消费线程 需要先把多个队列全部注册到 IngestQueueRegistry 再统一启动时使用本方法： 一旦消费线程跑起来…
```

### Event

`public class Event<T>`　事件类 该类表示在Disruptor环形缓冲区中传递的事件对象。 它包含一个泛型负载，用于存储实际的业务数据。 事件对象在RingBuffer初始化时预分配，并在整个生命周期中被重用， 以避免频繁的对象创建和垃圾回收…

_无 public 成员。_

### EventFactoryImpl

`public class EventFactoryImpl<T> implements EventFactory<Event<T>>`　Event工厂实现类 该类实现了Disruptor的EventFactory接口，用于创建新的Event对象。 在Disruptor框架中，RingBuffer需要一个EventFactory来预分配和重用事件对象…

**方法**

```java
Event<T> newInstance()  // 创建一个新的Event实例 该方法由Disruptor框架调用，用于在RingBuffer初始化时预分配事件对象， 以及在需要新事件时获取事件实例。
```

### GenericWorkHandler

`public final class GenericWorkHandler<T> implements EventHandler<Event<T>>`　通用工作处理器 该类实现了Disruptor的EventHandler接口，负责处理RingBuffer中的事件…

**构造器**

```java
GenericWorkHandler(Processor<T> processor, int shardIndex, int shardTotal, OrderingMode mode)  // 构造函数
```

**方法**

```java
void onEvent(Event<T> event, long sequence, boolean endOfBatch) throws Exception  // 处理事件 该方法由 Disruptor 框架调用： 根据 OrderingMode 计算分片，仅当命中本 handler 时才进入业务逻辑； 跳过空负载（来自异常兜底的占位事件）…
void onStart()  // 消费线程由 Disruptor 在启动线程上创建，会经 InheritableThreadLocal 继承启动线程的 traceId，这里先清掉
Processor<T> processor()
int shardIndex()
int shardTotal()
```

### IngestQueueManager

`public class IngestQueueManager`　注解：`@SuppressWarnings("ALL")` `@Slf4j`　队列管理器 - 门面类 该类作为获取和操作队列的统一入口，避免 Processor 直接依赖 IngestQueueRegistry 导致循环依赖…

**字段 / 常量**

```java
static final Duration DEFAULT_SEND_TIMEOUT = Duration.ofSeconds(10)  // send 的默认最长等待时间
```

**构造器**

```java
IngestQueueManager(ApplicationContext applicationContext)  // 构造函数，send 使用默认超时 DEFAULT_SEND_TIMEOUT
IngestQueueManager(ApplicationContext applicationContext, Duration sendTimeout)  // 构造函数
```

**方法**

```java
<T> IIngestQueue<T> getQueue(String queueName)  // 获取指定名称的队列 如果队列不存在，返回 null。调用者应该检查返回值。
<T> boolean send(String queueName, T item)  // 向指定队列发送数据（有界阻塞模式） 队列已满时最多等待配置的 send-timeout（默认 10 秒），超时返回 false 并打 WARN…
<T> boolean trySend(String queueName, T item, long timeout, TimeUnit unit)  // 向指定队列尝试发送数据（非阻塞模式，推荐） 该方法会在指定的超时时间内尝试将数据放入队列。 队列不存在、投递超时、队列已关闭或当前线程被中断时返回 false…
boolean hasQueue(String queueName)  // 检查队列是否存在
Set<String> getAllQueueNames()  // 获取所有已注册的队列名称 该方法可用于监控、调试或动态队列管理。
Map<String, IIngestQueue<?>> getAllQueues()  // 获取所有已注册的队列 返回一个不可修改的映射，包含所有队列名称和实例。
<T> int sendBatch(String queueName, Iterable<T> items, long timeout, TimeUnit unit)  // 批量发送数据到指定队列 依次尝试将列表中的每个数据项发送到队列，timeout 是整批的总截止时间： 每一项只能使用剩余时间，截止时间到达后剩余各项只做一次非阻塞尝试…
<T> boolean sendWithRetry(String queueName, T item, int maxRetries, long timeout, TimeUnit unit)  // 带重试的发送 如果首次发送失败，会进行指定次数的重试。 每次重试之间会有递增的延迟（简单的退避策略）。
```

### IngestQueueRegistry

`public class IngestQueueRegistry`　摄入队列注册表 该类维护了所有创建的队列实例的注册表，提供了注册、查找和获取所有队列的功能。 它作为队列管理的中心组件，使应用程序能够通过名称引用和访问队列实例。 线程安全：底层使用 ConcurrentHashMap…

**方法**

```java
<T> void register(String name, IIngestQueue<T> queue)  // 注册一个队列实例 将给定名称与队列实例关联，并存储在注册表中。 如果已存在同名队列，则会被覆盖。
@SuppressWarnings("unchecked") <T> IIngestQueue<T> get(String name)  // 通过名称获取队列实例 根据提供的名称查找并返回对应的队列实例。 如果找不到对应的队列，则返回null。
Map<String, IIngestQueue<?>> all()  // 获取所有注册的队列 返回一个不可修改的映射，包含所有注册的队列名称和实例。 这对于批量操作（如关闭所有队列）非常有用。
```

## 包 `com.mcst.easyfk.queue.disruptor.enums`

### OrderingMode

`public enum OrderingMode`　队列分片/保序模式 控制多 worker 场景下事件如何在 handler 间分片：

**枚举常量**

```java
AUTO
KEY_HASH
NONE
```

### WaitStrategyType

`public enum WaitStrategyType`　等待策略类型枚举 该枚举定义了Disruptor可用的不同等待策略类型。 等待策略决定了消费者在没有可用事件时如何等待，影响性能和CPU使用率。

**枚举常量**

```java
BLOCKING  // 阻塞等待策略 使用锁和条件变量实现的等待策略。 当没有可用事件时，消费者线程会阻塞，直到有新事件可用。 这种策略在低延迟不是最高优先级时最合适，可以节省CPU资源。
YIELDING  // 让出等待策略 使用Thread.yield()实现的等待策略。 当没有可用事件时，消费者线程会让出CPU时间片，但会很快再次检查。 这种策略在低延迟和CPU资源之间取得平衡，适合大多数应用场景。
BUSY_SPIN  // 忙等待策略 使用自旋实现的等待策略。 当没有可用事件时，消费者线程会持续检查，占用100%的CPU时间。 这种策略提供最低的延迟，但会消耗大量CPU资源，只适合对延迟极其敏感的场景。
```

**方法**

```java
abstract WaitStrategy create()  // 创建对应的Disruptor WaitStrategy实例
```

## 包 `com.mcst.easyfk.queue.disruptor.properties`

### DisruptorQueuesProperties

`public class DisruptorQueuesProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.queue.disruptor")`　Disruptor队列配置属性类 该类用于从配置文件中加载Disruptor队列相关的配置参数。 配置前缀为"easyfk.config.queue.disruptor"。 支持全局配置和针对特定队列的配置。

**字段 / 常量**

```java
Integer bufferSize  // RingBuffer 大小（必须为2的幂），默认 65536
Integer workers  // worker 数量，默认=物理核心数； 注意消费线程总数是 队列数 × worker 数：每个 worker 对应一个独立的 Disruptor 消费线程…
String producerType  // 生产者类型：SINGLE/MULTI，默认 MULTI SINGLE 对应的 SingleProducerSequencer 不设置任何内存屏障， 多个线程并发投递会拿到相同的序列号并静默覆盖彼此的事件…
String waitStrategy  // 等待策略：BLOCKING / YIELDING / BUSY_SPIN，默认 BLOCKING
String orderingMode  // 分片/保序模式：AUTO / KEY_HASH / NONE，默认 AUTO AUTO 表示根据 Processor 是否实现 KeyOrderedProcessor 自动决定…
boolean autoRegister = true  // 是否为未在 queues 中显式声明的 Processor Bean 自动创建队列，默认 true 自动创建的每个队列都会按 workers 拉起独立的消费线程组…
Duration sendTimeout = Duration.ofSeconds(10)  // IngestQueueManager#send 在队列满时的最长等待时间，默认 10 秒，必须为正数。 超时后返回 false
Ingest ingest = new Ingest()  // 全局摄入配置，队列级 queues..ingest 未设置的项回退到这里
ThreadConf thread = new ThreadConf()  // 全局线程配置，队列级 queues..thread 未设置的项回退到这里。 全局 name-prefix 会拼接在 Processor Bean 名之前，队列级 name-prefix 则直接作为完整前缀
Shutdown shutdown = new Shutdown()  // 全局关闭配置，队列级 queues..shutdown 未设置的项回退到这里
Map<String, QueueConf> queues = new LinkedHashMap<>()
```

**方法**

```java
long resolveMaxSpinNanos(QueueConf conf)  // 解析队列的最大自旋纳秒数：队列级 > 全局 > 代码默认
boolean resolveDaemon(QueueConf conf)  // 解析队列消费线程是否为守护线程：队列级 > 全局 > 代码默认（true）
int resolvePriority(QueueConf conf)  // 解析队列消费线程优先级：队列级 > 全局 > 代码默认
long resolveAwaitMs(String queueName)  // 解析指定队列的关闭排空等待时间：队列级 > 全局 > 代码默认
```

#### DisruptorQueuesProperties.QueueConf

`public static class QueueConf`　Lombok：`@Data`　单个队列的配置 用于配置特定队列的参数，可覆盖全局配置

**字段 / 常量**

```java
Integer bufferSize
Integer workers
String producerType
String waitStrategy
String orderingMode
String processorBean
Ingest ingest = new Ingest()
ThreadConf thread = new ThreadConf()
Shutdown shutdown = new Shutdown()
```

#### DisruptorQueuesProperties.Ingest

`public static class Ingest`　Lombok：`@Data`　队列摄入配置 控制数据摄入相关的参数，null 表示回退到上一级配置

**字段 / 常量**

```java
static final long DEFAULT_MAX_SPIN_NANOS = 500_000L
Long maxSpinNanos
```

#### DisruptorQueuesProperties.ThreadConf

`public static class ThreadConf`　Lombok：`@Data`　线程配置 控制工作线程的参数，如名称前缀、是否为守护线程、优先级等，null 表示回退到上一级配置

**字段 / 常量**

```java
static final int DEFAULT_PRIORITY = 5
String namePrefix
Boolean daemon
Integer priority
```

#### DisruptorQueuesProperties.Shutdown

`public static class Shutdown`　Lombok：`@Data`　关闭配置 控制队列关闭过程的参数，如等待时间，null 表示回退到上一级配置

**字段 / 常量**

```java
static final long DEFAULT_AWAIT_MS = 60_000L
Long awaitMs
```
