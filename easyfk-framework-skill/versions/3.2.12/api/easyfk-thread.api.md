# easyfk-thread API 签名速查（easyfk 3.2.12）

> 坐标：`com.mcst:easyfk-thread`　源码：`easyfk-base/easyfk-thread`
> 由 `scripts/gen-api.py` 从 25 个源文件自动提取，共 24 个类型、91 个方法/构造器、81 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-thread-skill.md](../modules/easyfk-thread-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 配置项（@ConfigurationProperties）

### `easyfk.config.thread.pool` ← ThreadPoolBaseProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `create-common-pool` | `Boolean` | `Boolean.FALSE` | 是否创建通用线程池 |
| `create-retry` | `Boolean` | `Boolean.FALSE` | 是否创建重试 |
| `create-async-pool` | `Boolean` | `Boolean.FALSE` | 是否创建异步执行线程池 为异步任务执行提供线程池支持 一般配合@Async注解使用 |
| `create-schedule-pool` | `Boolean` | `Boolean.FALSE` | 是否创建任务调度线程池 为任务调度提供线程池支持，用于定时任务的执行，一般配合@Scheduled注解使用 |
| `create-io-intensive-pool` | `Boolean` | `Boolean.FALSE` | 是否创建I/O密集型线程池 为I/O密集型任务执行提供线程池支持，用于I/O密集型任务的并行执行 |
| `create-cpu-intensive-pool` | `Boolean` | `Boolean.FALSE` | 是否创建CPU密集型线程池 为CPU密集型任务执行提供线程池支持，用于CPU密集型任务的并行执行 |
| `common-pool-args` | `ThreadPoolArgs` | `new ThreadPoolArgs()` | 通用线程池参数 |
| `async-pool-args` | `ThreadPoolArgs` | `new ThreadPoolArgs()` | 异步执行器线程池参数 |
| `schedule-pool-args` | `ScheduledPoolArgs` | `new ScheduledPoolArgs()` | 任务调度线程池参数 |
| `io-intensive-pool-args` | `ThreadPoolArgs` | `new ThreadPoolArgs()` | I/O密集型线程池参数 |
| `cpu-intensive-pool-args` | `ThreadPoolArgs` | `new ThreadPoolArgs()` | CPU密集型线程池参数 |
| `retry-pool-args` | `ScheduledPoolArgs` | `new ScheduledPoolArgs()` | 重试线程池参数 |

### `easyfk.config.thread.pool.monitor` ← ThreadPoolMonitorProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `enabled` | `boolean` | `false` | 是否启用监控 |
| `auto-discovery` | `boolean` | `true` | 是否自动发现线程池 |
| `auto-start` | `boolean` | `true` | 是否自动启动监控 |
| `monitor-all-executors` | `boolean` | `false` | 未声明 includeNames 时，是否监控容器中全部 ThreadPoolTaskExecutor（含第三方库与业务自建的线程池）。 默认 false，只监控框架自动配置创建的线程池 |
| `include-names` | `List<String>` | `new java.util.ArrayList<>()` | 包含的线程池名称（为空时按 monitorAllExecutors 决定范围），声明后只监控列表中的线程池 |
| `exclude-names` | `List<String>` | `new java.util.ArrayList<>()` | 排除的线程池名称 |
| `default-config` | `DynamicAdjustmentConfig` | `DynamicAdjustmentConfig.defaultConfig()` | 默认配置 |
| `configs` | `Map<String, DynamicAdjustmentConfig>` | `new HashMap<>()` | 特定线程池的配置 |


## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `easyfk-thread` | `com.mcst.easyfk.thread.config.ThreadPoolConfig` |

## 类型索引

- `com.mcst.easyfk.thread`：[AdjustmentDecision](#adjustmentdecision)、[AsyncThreadPoolMonitor](#asyncthreadpoolmonitor)、[CustomTaskExecutor](#customtaskexecutor)、[ThreadPoolMetrics](#threadpoolmetrics)、[ThreadPoolMonitor](#threadpoolmonitor)
    [ThreadPoolMonitorManager](#threadpoolmonitormanager)、[TraceAwareScheduledThreadPoolExecutor](#traceawarescheduledthreadpoolexecutor)、[TraceAwareTaskScheduler](#traceawaretaskscheduler)、[TraceIdPropagator](#traceidpropagator)
- `com.mcst.easyfk.thread.async`：[CompletableFutureConvert](#completablefutureconvert)
- `com.mcst.easyfk.thread.config`：[ThreadPoolConfig](#threadpoolconfig)、[ThreadPoolMonitorAutoConfig](#threadpoolmonitorautoconfig)、[ThreadPoolMonitorRegistrar](#threadpoolmonitorregistrar)
- `com.mcst.easyfk.thread.properties`：[DynamicAdjustmentConfig](#dynamicadjustmentconfig)、[ScheduledPoolArgs](#scheduledpoolargs)、[ThreadPoolArgs](#threadpoolargs)、[ThreadPoolBaseProperties](#threadpoolbaseproperties)、[ThreadPoolMonitorProperties](#threadpoolmonitorproperties)
- `com.mcst.easyfk.thread.retry`：[BackoffStrategy](#backoffstrategy)、[RetryCallback](#retrycallback)、[RetryConfig](#retryconfig)、[RetryContext](#retrycontext)、[RetryExecutor](#retryexecutor)
    [RetryableOperation](#retryableoperation)

## 包 `com.mcst.easyfk.thread`

### AdjustmentDecision

`public class AdjustmentDecision`　Lombok：`@Data` `@NoArgsConstructor` `@AllArgsConstructor`　线程池调整决策

**字段 / 常量**

```java
AdjustmentType adjustmentType  // 调整类型
int targetCorePoolSize  // 目标核心线程数
String reason  // 调整原因
ThreadPoolMetrics currentMetrics  // 当前指标
```

**方法**

```java
boolean shouldAdjust()  // 是否需要调整
boolean isScaleUp()  // 是否扩容
boolean isScaleDown()  // 是否缩容
int getAdjustmentAmount()  // 计算调整幅度
static AdjustmentDecision noChange(ThreadPoolMetrics metrics)  // 创建无需调整的决策
static AdjustmentDecision scaleUp(int targetSize, String reason, ThreadPoolMetrics metrics)  // 创建扩容决策
static AdjustmentDecision scaleDown(int targetSize, String reason, ThreadPoolMetrics metrics)  // 创建缩容决策
String toString()
```

#### AdjustmentDecision.AdjustmentType

`public enum AdjustmentType`　调整类型

**枚举常量**

```java
SCALE_UP  // 扩容
SCALE_DOWN  // 缩容
NO_CHANGE  // 无需调整
```

### AsyncThreadPoolMonitor

`public class AsyncThreadPoolMonitor`　注解：`@Slf4j`　异步线程池监控器 将监控逻辑异步化，避免影响主业务性能 调整决策由外部传入，与同步监控共用同一份实现，因此冷却期等约束在两种模式下行为一致。

**构造器**

```java
AsyncThreadPoolMonitor(String threadPoolName, ThreadPoolTaskExecutor taskExecutor, DynamicAdjustmentConfig config, Function<ThreadPoolMetrics, AdjustmentDecision> decisionFunction)
```

**方法**

```java
synchronized void startAsyncMonitoring()  // 开始异步监控
void stopAsyncMonitoring()  // 停止异步监控，等待在途任务结束
void stopAsyncMonitoring(boolean awaitTermination)  // 停止异步监控
AsyncMonitoringStatistics getAsyncStatistics()  // 获取异步监控统计信息
```

#### AsyncThreadPoolMonitor.AsyncMonitoringStatistics

`public static class AsyncMonitoringStatistics`　Lombok：`@Data`　异步监控统计数据

**字段 / 常量**

```java
long totalAsyncTasks
long successfulTasks
long failedTasks
double successRate
LocalDateTime startTime
boolean monitoring
boolean asyncEnabled
int asyncPoolSize
int asyncActiveCount
int asyncQueueSize
```

### CustomTaskExecutor

`public class CustomTaskExecutor extends ThreadPoolTaskExecutor`　会把调用方 traceId 传递到工作线程的线程池 上下文传递通过 setTaskDecorator 织入，而不是重写 execute…

**构造器**

```java
CustomTaskExecutor()
```

**方法**

```java
void setTaskDecorator(TaskDecorator taskDecorator)  // 追加业务自定义的装饰器，traceId 传递始终保留在最外层
boolean isFrameworkManaged()
void setFrameworkManaged(boolean frameworkManaged)
```

### ThreadPoolMetrics

`public class ThreadPoolMetrics`　Lombok：`@Data` `@NoArgsConstructor` `@AllArgsConstructor`　线程池指标数据

**字段 / 常量**

```java
int corePoolSize  // 当前核心线程数
int maxPoolSize  // 最大线程数
int activeThreadCount  // 当前活跃线程数
int poolSize  // 当前线程池大小
int queueSize  // 队列中等待的任务数
int queueCapacity  // 队列容量
long completedTaskCount  // 已完成的任务数
long taskCount  // 总任务数
LocalDateTime timestamp  // 采集时间
```

**方法**

```java
double getThreadUtilization()  // 计算线程利用率
double getQueueUtilization()  // 计算队列利用率
boolean isHighLoad(double threshold)  // 检查是否处于高负载状态
boolean isLowLoad(double threshold)  // 检查是否处于低负载状态
String getLoadStatus()  // 获取当前负载状态描述
String toString()
```

### ThreadPoolMonitor

`public class ThreadPoolMonitor`　注解：`@Slf4j`　通用线程池监控器 监控线程池状态，提供动态调整功能

**构造器**

```java
ThreadPoolMonitor(String threadPoolName, ThreadPoolTaskExecutor taskExecutor, DynamicAdjustmentConfig config)
ThreadPoolMonitor(ThreadPoolTaskExecutor taskExecutor, DynamicAdjustmentConfig config)
```

**方法**

```java
void startMonitoring()  // 开始监控
void stopMonitoring()  // 停止监控
Map<String, Object> getStatistics()  // 获取监控统计信息
AdjustmentDecision manualAdjust()  // 手动触发一次监控和调整
void resetStatistics()  // 重置统计数据
```

### ThreadPoolMonitorManager

`public class ThreadPoolMonitorManager`　注解：`@Slf4j`

**方法**

```java
void addMonitor(String name, ThreadPoolMonitor monitor)  // 添加监控器
ThreadPoolMonitor getMonitor(String name)  // 获取监控器
Map<String, ThreadPoolMonitor> getAllMonitors()  // 获取所有监控器
void startAllMonitoring()  // 启动所有监控
void stopAllMonitoring()  // 停止所有监控
Map<String, Map<String, Object>> getAllStatistics()  // 获取所有统计信息
ThreadPoolMonitor removeMonitor(String name)  // 移除监控器
```

### TraceAwareScheduledThreadPoolExecutor

`public class TraceAwareScheduledThreadPoolExecutor extends ScheduledThreadPoolExecutor`　会把提交方 traceId 传递到工作线程的定时线程池 execute 与 submit 在 ScheduledThreadPoolExecutor 内部都委托给 schedule…

**构造器**

```java
TraceAwareScheduledThreadPoolExecutor(int corePoolSize, ThreadFactory threadFactory, RejectedExecutionHandler handler)
```

**方法**

```java
ScheduledFuture<?> schedule(Runnable command, long delay, TimeUnit unit)
<V> ScheduledFuture<V> schedule(Callable<V> callable, long delay, TimeUnit unit)
ScheduledFuture<?> scheduleAtFixedRate(Runnable command, long initialDelay, long period, TimeUnit unit)
ScheduledFuture<?> scheduleWithFixedDelay(Runnable command, long initialDelay, long delay, TimeUnit unit)
```

### TraceAwareTaskScheduler

`public class TraceAwareTaskScheduler implements TaskScheduler, DisposableBean`　只暴露 TaskScheduler 能力的调度器 ThreadPoolTaskScheduler 同时实现了 TaskExecutor…

**构造器**

```java
TraceAwareTaskScheduler(ThreadPoolTaskScheduler delegate)
```

**方法**

```java
ThreadPoolTaskScheduler getDelegate()  // 底层调度线程池，用于读取运行指标，不要将其作为 Executor 提交普通任务
Clock getClock()
ScheduledFuture<?> schedule(Runnable task, Trigger trigger)
ScheduledFuture<?> schedule(Runnable task, Instant startTime)
ScheduledFuture<?> scheduleAtFixedRate(Runnable task, Instant startTime, Duration period)
ScheduledFuture<?> scheduleAtFixedRate(Runnable task, Duration period)
ScheduledFuture<?> scheduleWithFixedDelay(Runnable task, Instant startTime, Duration delay)
ScheduledFuture<?> scheduleWithFixedDelay(Runnable task, Duration delay)
void destroy()
```

### TraceIdPropagator

`public final class TraceIdPropagator`　traceId 跨线程传递工具 在提交线程上捕获 TraceIdContext 中的 traceId，在执行线程上写入 TraceIdContext 与 MDC TRACE_ID，执行结束后恢复执行线程原有的值…

**字段 / 常量**

```java
static final TaskDecorator DECORATOR = TraceIdPropagator::wrap  // 捕获当前 traceId 的任务装饰器
```

**方法**

```java
static Runnable wrap(Runnable task)  // 包装任务，执行期间使用提交时的 traceId
static <V> Callable<V> wrap(Callable<V> task)  // 包装任务，执行期间使用提交时的 traceId
static Runnable wrapOrGenerate(Runnable task)  // 包装任务，提交时存在 traceId 则沿用，否则每次执行都生成一个新的 traceId。 用于定时任务等没有上游请求的场景，使同一次执行的日志可以被关联起来
static <V> Callable<V> wrapOrGenerate(Callable<V> task)  // 包装任务，提交时存在 traceId 则沿用，否则每次执行都生成一个新的 traceId
static String newTraceId()  // 生成一个新的 traceId
```

## 包 `com.mcst.easyfk.thread.async`

### CompletableFutureConvert

`public class CompletableFutureConvert`　CompletableFuture 转换工具类 提供将同步/阻塞调用转换为异步 CompletableFuture 的便捷方法，支持超时控制。 特别针对返回 BaseResult 的远程调用场景进行了优化封装。

**方法**

```java
static <T> CompletableFuture<T> async(Supplier<T> call, long timeoutSec, Executor pool)  // 将同步任务转换为异步执行的 CompletableFuture，并设置超时时间 使用指定的线程池异步执行提供的任务，如果在超时时间内未完成…
static <T> CompletableFuture<T> asyncForBaseResult(Supplier<BaseResult<T>> call, long timeoutSec, Executor pool)  // 将返回 BaseResult 的阻塞调用转换为异步 CompletableFuture，并自动解包结果 适用于所有耗时的阻塞调用场景，包括但不限于：网络请求、远程调用（HTTP/RPC）、 数据库查询、文件 I/O 等…
```

## 包 `com.mcst.easyfk.thread.config`

### ThreadPoolConfig

`public class ThreadPoolConfig`　注解：`@AutoConfiguration` `@EnableConfigurationProperties({ThreadPoolBaseProperties.class, ThreadPoolMonitorProperties.class})` `@ImportAutoConfiguration({ThreadPoolMonitorAutoConfig.class})`

**方法**

```java
@Bean("commonTaskExecutor") @ConditionalOnProperty(name = "easyfk.config.thread.pool.create-common-pool", havingValue = "true") CustomTaskExecutor commonTaskExecutor()
@Bean("asyncTaskExecutor") @ConditionalOnProperty(name = "easyfk.config.thread.pool.create-async-pool", havingValue = "true") CustomTaskExecutor asyncTaskExecutor()
@Bean(name = {"scheduleTaskExecutor", "taskScheduler"}) @ConditionalOnProperty(name = "easyfk.config.thread.pool.create-schedule-pool", havingValue = "true") TraceAwareTaskScheduler scheduleTaskExecutor()  // 任务调度线程池 注册为只实现 TaskScheduler 的 TraceAwareTaskScheduler，不参与按类型注入 Executor 与无名称 @Async 的候选…
@Bean("ioIntensiveTaskExecutor") @ConditionalOnProperty(name = "easyfk.config.thread.pool.create-io-intensive-pool", havingValue = "true") CustomTaskExecutor ioIntensiveTaskExecutor()  // I/O密集型线程池 适用场景：文件读写、网络请求、数据库操作、远程调用等I/O密集型任务 推荐配置：核心线程数=CPU核心数*2，最大线程数=CPU核心数*4
@Bean("cpuIntensiveTaskExecutor") @ConditionalOnProperty(name = "easyfk.config.thread.pool.create-cpu-intensive-pool", havingValue = "true") CustomTaskExecutor cpuIntensiveTaskExecutor()  // CPU密集型线程池 适用场景：复杂计算、数据分析、图像处理、加密解密等CPU密集型任务 推荐配置：核心线程数=CPU核心数+1，最大线程数=CPU核心数+1
@Bean(name = "retryScheduledExecutor", autowireCandidate = false) @ConditionalOnMissingBean(name = "retryScheduledExecutor") @ConditionalOnProperty(name = "easyfk.config.thread.pool.create-retry", havingValue = "true") ScheduledExecutorService retryScheduledExecutor()  // 重试线程池 声明为非自动装配候选，避免它作为 Executor 被按类型注入；RetryExecutor 按名称获取
@Bean @ConditionalOnMissingBean @ConditionalOnProperty(name = "easyfk.config.thread.pool.create-retry", havingValue = "true") RetryExecutor retryExecutor(BeanFactory beanFactory)
```

### ThreadPoolMonitorAutoConfig

`public class ThreadPoolMonitorAutoConfig`　注解：`@AutoConfiguration` `@EnableConfigurationProperties(ThreadPoolMonitorProperties.class)` `@ConditionalOnProperty(name = "easyfk.config.thread.pool.monitor.enabled", havingValue = "true")`　线程池监控自动配置

**方法**

```java
@Bean(destroyMethod = "stopAllMonitoring") @ConditionalOnMissingBean ThreadPoolMonitorManager threadPoolMonitorManager()  // 线程池监控管理器，容器关闭时停止其管理的全部监控器
@Bean @ConditionalOnMissingBean ThreadPoolMonitorRegistrar threadPoolMonitorRegistrar(ThreadPoolMonitorManager threadPoolMonitorManager, ThreadPoolMonitorProperties threadPoolMonitorProperties, ApplicationContext applicationContext)
```

### ThreadPoolMonitorRegistrar

`public class ThreadPoolMonitorRegistrar implements SmartInitializingSingleton`　注解：`@Slf4j`　自动发现容器内的线程池并为其注册监控器 发现动作放在所有单例装配完成之后执行，避免在配置类初始化阶段就触发线程池 Bean 的提前实例化。

**构造器**

```java
ThreadPoolMonitorRegistrar(ThreadPoolMonitorManager manager, ThreadPoolMonitorProperties properties, ApplicationContext applicationContext)
```

**方法**

```java
void afterSingletonsInstantiated()
```

## 包 `com.mcst.easyfk.thread.properties`

### DynamicAdjustmentConfig

`public class DynamicAdjustmentConfig`　Lombok：`@Data`　注解：`@Validated`　动态线程池调整配置

**字段 / 常量**

```java
Boolean enabled = true  // 是否启用动态调整
Duration monitoringInterval = Duration.ofSeconds(30)  // 监控间隔
Duration cooldownPeriod = Duration.ofMinutes(2)  // 冷却期（两次调整之间的最小间隔）
Integer minCorePoolSize = 2  // 最小核心线程数
Integer maxCorePoolSize = 20  // 最大核心线程数
Boolean keepInitialCorePoolSize = true  // 缩容时是否保持不低于注册监控时线程池的核心线程数（即业务配置值）。 为 false 时只受 minCorePoolSize 约束
Integer scaleUpStep = 2  // 扩容步长
Integer scaleDownStep = 1  // 缩容步长
Double highLoadThreshold = 80.0  // 高负载阈值（线程利用率%）
Double lowLoadThreshold = 30.0  // 低负载阈值（线程利用率%）
Double queueHighThreshold = 70.0  // 队列高负载阈值（队列利用率%）
Double queueLowThreshold = 20.0  // 队列低负载阈值（队列利用率%）
Boolean asyncMonitoringEnabled = true  // 是否启用异步监控
Integer asyncMonitoringPoolSize = 2  // 异步监控线程池大小
Integer asyncMonitoringQueueCapacity = 100  // 异步监控任务队列容量
Integer asyncMonitoringTimeoutSeconds = 30  // 异步监控超时时间（秒）
```

**方法**

```java
void validate()  // 验证配置合法性
static DynamicAdjustmentConfig defaultConfig()  // 创建默认配置
static DynamicAdjustmentConfig highPerformanceConfig()  // 创建高性能配置
static DynamicAdjustmentConfig conservativeConfig()  // 创建保守配置
```

### ScheduledPoolArgs

`public class ScheduledPoolArgs`　Lombok：`@Data`　定时线程池参数，用于调度池与重试池 两者底层都是 ScheduledThreadPoolExecutor：线程数固定为核心线程数、任务队列是无界延迟队列…

**字段 / 常量**

```java
Integer corePoolSize  // 线程数，未设置时取 CPU 核心数
String threadNamePrefix  // 线程名称前缀，未设置时调度池为 scheduled-，重试池为 retry-
Boolean waitForTasksToCompleteOnShutdown = true  // 关闭时是否继续执行已排队的延迟任务
Integer awaitTerminationSeconds = 60  // 等待终止时间（秒），仅调度池使用
String rejectedExecutionHandler = "CALLER_RUNS"  // 拒绝策略：ABORT / CALLER_RUNS（默认）/ DISCARD / DISCARD_OLDEST。 由于队列无界，只在线程池关闭后提交任务时触发
```

**方法**

```java
Integer getActualCorePoolSize()  // 获取实际线程数，未设置时返回 CPU 核心数
String getActualThreadNamePrefix(String defaultPrefix)  // 获取实际线程名称前缀
```

### ThreadPoolArgs

`public class ThreadPoolArgs`　Lombok：`@Data`

**字段 / 常量**

```java
Integer corePoolSize  // 核心线程池大小 如果未设置，将自动获取CPU核心数
Integer maxPoolSize  // 最大线程池大小 如果未设置，将自动计算为核心线程数的1.5倍
Integer queueCapacity = 200  // 队列容量
Integer keepAliveSeconds = 60  // 线程空闲时间（秒）
String threadNamePrefix = "custom-thread-"  // 线程名称前缀
Boolean waitForTasksToCompleteOnShutdown = true  // 关闭时等待任务完成
Integer awaitTerminationSeconds = 60  // 等待终止时间（秒）
Boolean allowCoreThreadTimeOut = Boolean.FALSE  // 是否允许核心线程超时回收
Boolean prestartAllCoreThreads = Boolean.FALSE  // 是否预热核心线程
String rejectedExecutionHandler = "CALLER_RUNS"  // 拒绝策略 支持以下策略： - ABORT: AbortPolicy，拒绝任务并抛出RejectedExecutionException异常 - CALLER_RUNS: CallerRunsPolicy（默认）…
```

**方法**

```java
Integer getActualCorePoolSize()  // 获取实际的核心线程池大小 如果未设置，则返回CPU核心数
Integer getActualMaxPoolSize()  // 获取实际的最大线程池大小 如果未设置，则返回核心线程数的1.5倍 确保最大线程数不小于核心线程数
```

### ThreadPoolBaseProperties

`public class ThreadPoolBaseProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.thread.pool")`

**字段 / 常量**

```java
Boolean createCommonPool = Boolean.FALSE  // 是否创建通用线程池
Boolean createRetry = Boolean.FALSE  // 是否创建重试
Boolean createAsyncPool = Boolean.FALSE  // 是否创建异步执行线程池 为异步任务执行提供线程池支持 一般配合@Async注解使用
Boolean createSchedulePool = Boolean.FALSE  // 是否创建任务调度线程池 为任务调度提供线程池支持，用于定时任务的执行，一般配合@Scheduled注解使用
Boolean createIoIntensivePool = Boolean.FALSE  // 是否创建I/O密集型线程池 为I/O密集型任务执行提供线程池支持，用于I/O密集型任务的并行执行
Boolean createCpuIntensivePool = Boolean.FALSE  // 是否创建CPU密集型线程池 为CPU密集型任务执行提供线程池支持，用于CPU密集型任务的并行执行
ThreadPoolArgs commonPoolArgs = new ThreadPoolArgs()  // 通用线程池参数
ThreadPoolArgs asyncPoolArgs = new ThreadPoolArgs()  // 异步执行器线程池参数
ScheduledPoolArgs schedulePoolArgs = new ScheduledPoolArgs()  // 任务调度线程池参数
ThreadPoolArgs ioIntensivePoolArgs = new ThreadPoolArgs()  // I/O密集型线程池参数
ThreadPoolArgs cpuIntensivePoolArgs = new ThreadPoolArgs()  // CPU密集型线程池参数
ScheduledPoolArgs retryPoolArgs = new ScheduledPoolArgs()  // 重试线程池参数
```

### ThreadPoolMonitorProperties

`public class ThreadPoolMonitorProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.thread.pool.monitor")`　线程池监控配置属性

**字段 / 常量**

```java
boolean enabled = false  // 是否启用监控
boolean autoDiscovery = true  // 是否自动发现线程池
boolean autoStart = true  // 是否自动启动监控
boolean monitorAllExecutors = false  // 未声明 includeNames 时，是否监控容器中全部 ThreadPoolTaskExecutor（含第三方库与业务自建的线程池）。 默认 false，只监控框架自动配置创建的线程池
List<String> includeNames = new java.util.ArrayList<>()  // 包含的线程池名称（为空时按 monitorAllExecutors 决定范围），声明后只监控列表中的线程池
List<String> excludeNames = new java.util.ArrayList<>()  // 排除的线程池名称
DynamicAdjustmentConfig defaultConfig = DynamicAdjustmentConfig.defaultConfig()  // 默认配置
Map<String, DynamicAdjustmentConfig> configs = new HashMap<>()  // 特定线程池的配置
```

## 包 `com.mcst.easyfk.thread.retry`

### BackoffStrategy

`public enum BackoffStrategy`　退避策略枚举

**枚举常量**

```java
LINEAR  // 线性退避策略 延迟时间 = 基础延迟 × 重试次数 示例：baseDelay=500ms时，第1次500ms，第2次1000ms，第3次1500ms
EXPONENTIAL  // 指数退避策略 延迟时间 = 基础延迟 × (2 ^ (重试次数-1)) 示例：baseDelay=500ms时，第1次500ms，第2次1000ms，第3次2000ms
FIXED  // 固定延迟策略 延迟时间 = 基础延迟（恒定） 示例：baseDelay=500ms时，每次都是500ms
```

**方法**

```java
abstract long calculateDelay(long baseDelayMs, int attempt)  // 计算重试延迟时间
```

### RetryCallback

`public interface RetryCallback<T>`　重试回调接口

**方法**

```java
default void onSuccess(T result, int attempt)  // 操作成功时调用
default void onFinalFailure(Exception e, int totalAttempts)  // 操作最终失败时调用
```

### RetryConfig

`public class RetryConfig`　Lombok：`@Data` `@Builder`　重试配置类

**字段 / 常量**

```java
@Builder.Default int maxRetries = 3  // 最大重试次数（不包括首次尝试） 默认值：3 示例：设置为3表示总共会尝试4次（1次首次 + 3次重试）
@Builder.Default long baseDelayMs = 500L  // 基础延迟时间（毫秒） 默认值：500ms 实际延迟时间会根据退避策略计算
@Builder.Default BackoffStrategy backoffStrategy = BackoffStrategy.LINEAR  // 退避策略 默认值：LINEAR（线性退避）
@Builder.Default int maxConcurrentRetries = 100  // 最大并发重试链数 默认值：100 通过信号量控制，防止重试任务过多导致OOM 一次 executeAsync 触发的整条重试链（无论重试多少次）只占用一个名额，直到成功或最终失败才释放…
String businessKey  // 业务标识（用于日志和监控） 建议格式：业务类型:业务ID，例如 "pushMsg:user123" 如果为空，日志中将使用默认标识
@Builder.Default boolean enableFallback = true  // 是否启用降级策略 默认值：true 当信号量或线程池满载时，是否尝试立即补发
@Builder.Default Class<? extends Throwable>[] retryFor = new Class[]{Exception.class}  // 需要重试的异常类型 默认值：Exception.class（所有异常都重试） 可以指定特定异常，例如只重试网络异常
@Builder.Default Class<? extends Throwable>[] noRetryFor = new Class[0]  // 不需要重试的异常类型 默认值：空数组（不排除任何异常） 示例：设置为 {IllegalArgumentException.class} 表示参数异常不重试
```

**方法**

```java
boolean shouldRetry(Throwable throwable)  // 判断异常是否需要重试
String getBusinessKeyOrDefault()  // 获取业务标识，如果为空则返回默认值
```

### RetryContext

`public class RetryContext<T>`　Lombok：`@Data` `@Builder`　重试上下文

**字段 / 常量**

```java
RetryConfig config  // 重试配置
RetryableOperation<T> operation  // 可重试的操作
RetryCallback<T> callback  // 重试回调
@Builder.Default int currentAttempt = 1  // 当前尝试次数（从1开始，1表示首次尝试）
@Builder.Default long submitTime = System.currentTimeMillis()  // 任务提交时间戳
```

**方法**

```java
String getBusinessKey()  // 获取业务标识（用于日志）
boolean canRetry()  // 判断是否还可以继续重试
RetryContext<T> nextAttempt()  // 增加尝试次数并返回新的上下文（不可变模式）
```

### RetryExecutor

`public class RetryExecutor`　注解：`@Slf4j`　重试执行器 - 纯粹的重试机制组件

**构造器**

```java
RetryExecutor(ScheduledExecutorService executor)  // 创建重试执行器
```

**方法**

```java
<T> T execute(RetryConfig config, RetryableOperation<T> operation) throws Exception  // 执行操作（同步模式：等待所有重试完成）
<T> void executeAsync(RetryConfig config, RetryableOperation<T> operation, RetryCallback<T> callback)  // 执行操作（异步模式：立即返回，后台重试）
int getActiveRetryTasks()  // 获取当前活跃重试任务数
```

### RetryableOperation

`public interface RetryableOperation<T>`　注解：`@FunctionalInterface`　可重试的操作接口

**方法**

```java
T execute() throws Exception  // 执行操作
```
