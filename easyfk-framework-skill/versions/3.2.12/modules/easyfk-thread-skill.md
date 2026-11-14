# easyfk-thread Skill 参考文档

> 所属项目：`easyfk-base`　模块：`easyfk-thread`（单模块）
> 坐标：`com.mcst:easyfk-thread:3.2.12`
> 依据：全部源码（25 个文件），对齐 `thread开发手册.md`、`thread技术特点.md`、`EasyFK框架开发手册.md` §3.9。
> 以源码为准；差异见文末「复查记录」。

---

## 1. 模块定位

线程池管理与异步任务模块，提供：

- 6 类按需创建的线程池（通用、异步、调度、I/O 密集、CPU 密集、重试），所有开关默认关闭；
- `CustomTaskExecutor`：`ThreadPoolTaskExecutor` 子类，跨线程透传 `TraceIdContext` 和 MDC `TRACE_ID`；调度池、重试池和监控线程同样透传（`TraceIdPropagator`）；
- 线程池监控与动态扩缩容（只调整 `corePoolSize`，默认只作用于框架创建的线程池）；
- `RetryExecutor`：同步 / 异步重试，提供 3 种退避策略和信号量并发限制；
- `CompletableFutureConvert`：带超时的异步调用，并自动解包 `BaseResult`。

依赖：`easyfk-core` 是 `compileOnly`，需要由应用自行引入。

---

## 2. 引入与自动配置

```groovy
implementation platform('com.mcst:easyfk-dependencies:3.2.12')
implementation 'com.mcst:easyfk-core'
implementation 'com.mcst:easyfk-thread'
```

- `AutoConfiguration.imports` 只声明了 `ThreadPoolConfig`，监控配置 `ThreadPoolMonitorAutoConfig` 由它通过 `@ImportAutoConfiguration` 引入，并受 `easyfk.config.thread.pool.monitor.enabled=true` 控制。
- 框架**没有** `@EnableAsync`、`@EnableScheduling`，也没有 `AsyncConfigurer`。需要的话由业务方自己开启。

---

## 3. Bean 一览

配置前缀：`easyfk.config.thread.pool`

| Bean 名称 | 类型 | 开关（默认 false） | 默认线程前缀 | TraceId 透传 |
|---|---|---|---|---|
| `commonTaskExecutor` | `CustomTaskExecutor` | `create-common-pool` | `custom-thread-` | 是 |
| `asyncTaskExecutor` | `CustomTaskExecutor` | `create-async-pool` | `async-` | 是 |
| `scheduleTaskExecutor` / `taskScheduler` | `TraceAwareTaskScheduler`（只实现 `TaskScheduler`，内部委托 `ThreadPoolTaskScheduler`） | `create-schedule-pool` | `scheduled-` | 是；调度时无 traceId 则每次执行生成新的 |
| `ioIntensiveTaskExecutor` | `CustomTaskExecutor` | `create-io-intensive-pool` | `io-intensive-` | 是 |
| `cpuIntensiveTaskExecutor` | `CustomTaskExecutor` | `create-cpu-intensive-pool` | `cpu-intensive-` | 是 |
| `retryScheduledExecutor` | `TraceAwareScheduledThreadPoolExecutor`（`autowireCandidate=false`） | `create-retry`（`@ConditionalOnMissingBean(name)`） | `retry-` | 是 |
| `retryExecutor` | `RetryExecutor` | `create-retry`（`@ConditionalOnMissingBean`） | — | — |

前缀的规则：`ThreadPoolTaskExecutor` 类线程池的配置值仍为默认值 `custom-thread-` 时，替换成上表中的专属前缀；调度池和重试池的 `thread-name-prefix` 默认为空，为空时使用上表前缀。

`retryScheduledExecutor` 不是自动装配候选，按类型注入 `Executor` / `ScheduledExecutorService` 拿不到它；`RetryExecutor` 按名称获取它，业务方自定义同名 Bean 时也按名称生效。

---

## 4. 线程池参数（`ThreadPoolArgs`）

`ThreadPoolTaskExecutor` 类线程池对应一组参数：`common-pool-args`、`async-pool-args`、`io-intensive-pool-args`、`cpu-intensive-pool-args`。

| 属性 | 默认值 | 说明 |
|---|---|---|
| `core-pool-size` | CPU 核数 | 为空时取 `availableProcessors()` |
| `max-pool-size` | `ceil(core × 1.5)` | 最终取 `max(max, core)` |
| `queue-capacity` | 200 | |
| `keep-alive-seconds` | 60 | |
| `thread-name-prefix` | `custom-thread-` | 见 §3 |
| `wait-for-tasks-to-complete-on-shutdown` | true | |
| `await-termination-seconds` | 60 | |
| `allow-core-thread-timeout` | false | |
| `prestart-all-core-threads` | false | |
| `rejected-execution-handler` | `CALLER_RUNS` | 取值 `ABORT` / `CALLER_RUNS` / `DISCARD` / `DISCARD_OLDEST`，未知值也按 `CALLER_RUNS` 处理 |

调度池 `schedule-pool-args` 和重试池 `retry-pool-args` 使用 `ScheduledPoolArgs`。两者底层都是 `ScheduledThreadPoolExecutor`（线程数固定、无界延迟队列），因此**没有** `max-pool-size`、`queue-capacity`、`keep-alive-seconds`、`allow-core-thread-timeout`、`prestart-all-core-threads`，写了也会被忽略：

| 属性 | 默认值 | 说明 |
|---|---|---|
| `core-pool-size` | CPU 核数 | 线程数 |
| `thread-name-prefix` | 空 | 为空时调度池 `scheduled-`、重试池 `retry-` |
| `wait-for-tasks-to-complete-on-shutdown` | true | 关闭时是否继续执行已排队的延迟任务 |
| `await-termination-seconds` | 60 | 只有调度池使用 |
| `rejected-execution-handler` | `CALLER_RUNS` | 队列无界，只在线程池关闭后提交时触发 |

推荐配置：

```yaml
easyfk:
  config:
    thread:
      pool:
        create-common-pool: true
        create-async-pool: true
        create-io-intensive-pool: true
        create-retry: true
        common-pool-args:
          core-pool-size: 4
          max-pool-size: 8
          thread-name-prefix: common-
        io-intensive-pool-args:
          core-pool-size: 16      # 约为 CPU × 2
          max-pool-size: 32
          keep-alive-seconds: 120
        cpu-intensive-pool-args:
          core-pool-size: 9       # 约为 CPU + 1
          max-pool-size: 9
          queue-capacity: 50
          rejected-execution-handler: ABORT
```

---

## 5. 使用线程池

### 5.1 注入：必须按名称

```java
@Resource(name = "ioIntensiveTaskExecutor")
private CustomTaskExecutor ioExecutor;

// 或者
public OrderService(@Qualifier("commonTaskExecutor") Executor executor) { ... }
```

调度池注册为只实现 `TaskScheduler` 的 `TraceAwareTaskScheduler`，重试池不是自动装配候选，二者都不会被按类型注入的 `Executor` 或不带名称的 `@Async` 选中。但框架的 `CustomTaskExecutor` 线程池都没有 `@Primary`：

- 开启了多个 `CustomTaskExecutor` 时，按类型注入 `Executor` / `TaskExecutor` 会因候选不唯一而失败；
- 容器中有多个 `TaskExecutor` 时，不带名称的 `@Async` 会退化为 `SimpleAsyncTaskExecutor`，每个任务新建一个线程。开启任一 `CustomTaskExecutor` 后，Spring Boot 默认的 `applicationTaskExecutor` 也会因为已存在 Executor 而不再创建。

### 5.2 @Async

```java
@EnableAsync              // 由业务方开启
@Configuration
public class AsyncConfig {}

@Async("asyncTaskExecutor")   // 必须写明名称
public void sendMail(...) {}
```

### 5.3 @Scheduled

开启 `create-schedule-pool=true` 并且 `@EnableScheduling` 后，`@Scheduled` 任务会使用 `taskScheduler`（按类型 `TaskScheduler` 或名称 `taskScheduler` 解析）。调度时若当前线程有 traceId 则沿用，否则**每次执行生成一个新的 traceId**（UUID），同一次执行的日志可以关联。

### 5.4 TraceId 透传（`TraceIdPropagator`）

- 统一由 `TraceIdPropagator` 实现：提交时捕获 `TraceIdContext` 的 traceId；执行前写入 `TraceIdContext` 与 MDC `TRACE_ID`；`finally` 中**恢复执行线程原有的值**（`CALLER_RUNS` 在调用方线程执行时不会抹掉调用方的 traceId）。提交时没有 traceId 的任务，执行期间也不带 traceId，屏蔽 `InheritableThreadLocal` 在创建线程时遗留的旧值。
- 覆盖范围：
  - `CustomTaskExecutor`：通过 `TaskDecorator` 实现，`execute`、`submit` 和 `@Async` 都会生效；`setTaskDecorator(userDecorator)` 时用户装饰器包在内层，框架透传保留在最外层，传入 `null` 时恢复为默认装饰器；
  - 调度池 `TraceAwareTaskScheduler`：见 §5.3；
  - 重试池 `TraceAwareScheduledThreadPoolExecutor`：覆盖 `schedule*`，因此 `execute` / `submit` 也生效；异步重试与降级补发都沿用 `executeAsync` 调用方的 traceId；
  - 监控线程：每轮监控生成一个新的 traceId，异步监控的工作线程沿用该轮的 traceId。
- 自建线程池可以直接使用 `TraceIdPropagator.wrap(Runnable/Callable)`、`wrapOrGenerate(...)` 或 `TraceIdPropagator.DECORATOR`。
- 透传只针对 `TRACE_ID` 这一个 key，其他 MDC key 和 ThreadLocal **不会**透传。

---

## 6. 监控与动态扩缩容

### 6.1 配置

前缀：`easyfk.config.thread.pool.monitor`

| 属性 | 默认值 | 说明 |
|---|---|---|
| `enabled` | false | 总开关 |
| `auto-discovery` | true | 自动发现容器中的 `ThreadPoolTaskExecutor` Bean，范围见下 |
| `auto-start` | true | 启动后自动开始监控 |
| `monitor-all-executors` | false | `include-names` 为空时，是否监控全部 `ThreadPoolTaskExecutor`（含第三方库、业务自建的线程池）；false 时只监控框架自动配置创建的线程池 |
| `include-names` / `exclude-names` | [] | 按 Bean 名称过滤；`include-names` 非空时只监控列表中的线程池（第三方线程池通过它显式纳入），exclude 优先 |
| `default-config` | 见下表 | 默认调整参数 |
| `configs.<beanName>` | — | 单个线程池的独立参数 |

`DynamicAdjustmentConfig` 的属性：

| 属性 | 默认值 |
|---|---|
| `enabled` | true |
| `monitoring-interval` | `PT30S` |
| `cooldown-period` | `PT2M` |
| `min-core-pool-size` / `max-core-pool-size` | 2 / 20 |
| `keep-initial-core-pool-size` | true（缩容不低于注册监控时的核心线程数） |
| `scale-up-step` / `scale-down-step` | 2 / 1 |
| `high-load-threshold` / `low-load-threshold` | 80.0 / 30.0（线程利用率 %） |
| `queue-high-threshold` / `queue-low-threshold` | 70.0 / 20.0（队列利用率 %） |
| `async-monitoring-enabled` | true |
| `async-monitoring-pool-size` / `-queue-capacity` / `-timeout-seconds` | 2 / 100 / 30 |

校验规则：要求 `max-core > min-core`，并且两组阈值都满足 high > low。否则监控器构造时抛出 `IllegalArgumentException`，**导致应用启动失败**。

### 6.2 调整算法

- 线程利用率 = `activeCount / corePoolSize`；队列利用率 = 已用 / 容量。
- **扩容**：线程利用率 ≥ high **或** 队列利用率 ≥ queueHigh 时，core 增加一个 step（不超过 maxCore）；新的 core 大于 max 时，同步上调 maxPoolSize。
- **缩容**：线程利用率 ≤ low **且** 队列利用率 ≤ queueLow 时，core 减少一个 step；下限为 `max(minCore, 注册时的 core)`（`keep-initial-core-pool-size=false` 时只受 minCore 约束），因此默认只会把扩上去的线程收回到配置值；maxPoolSize 不会回调。
- 两次调整之间有冷却期。
- 只监控 `ThreadPoolTaskExecutor`，调度池和重试池不在监控范围内。
- 异步监控模式出现 OOM 时，自动降级为同步模式。

**注意**：`max-core=20` 是扩容上限。配置了较大 core 的线程池（如 core=32）在 `max-core` 不大于有效下限时不会扩容，监控器构造时会打印警告；这类线程池应在 `configs.<beanName>` 中设置更大的 `max-core-pool-size`。

```yaml
easyfk:
  config:
    thread:
      pool:
        monitor:
          enabled: true
          include-names: [commonTaskExecutor, asyncTaskExecutor, ioIntensiveTaskExecutor]
          default-config:
            monitoring-interval: PT30S
            cooldown-period: PT2M
          configs:
            ioIntensiveTaskExecutor:
              min-core-pool-size: 16
              max-core-pool-size: 64
```

### 6.3 编程接口

- `ThreadPoolMonitorManager`：`addMonitor(name, monitor)`、`getMonitor`、`getAllMonitors`、`removeMonitor`、`startAllMonitoring`、`stopAllMonitoring`、`getAllStatistics()`。
- `ThreadPoolMonitor`：
  - 构造方法 `new ThreadPoolMonitor(name, executor, config)`；
  - `startMonitoring()` / `stopMonitoring()`，可以重复启停；
  - `getStatistics()`；
  - `manualAdjust()`：立即采集一次并决策，同样受冷却期约束；
  - `resetStatistics()`。
- `DynamicAdjustmentConfig` 的预置模板：
  - `defaultConfig()`：30s / 2min / 80% / 步长 2；
  - `highPerformanceConfig()`：15s / 1min / 70% / 步长 3，异步 4 线程；
  - `conservativeConfig()`：2min / 5min / 90% / 步长 1，关闭异步。

---

## 7. 重试执行器（`RetryExecutor`）

需要开启 `create-retry=true`，然后注入 `RetryExecutor`。

### 7.1 RetryConfig（Builder）

| 字段 | 默认值 | 说明 |
|---|---|---|
| `maxRetries` | 3 | 重试次数，**不含首次**，总执行次数 = maxRetries + 1；不能小于 0 |
| `baseDelayMs` | 500 | 不能小于 0 |
| `backoffStrategy` | `LINEAR` | `LINEAR`=base×n、`EXPONENTIAL`=base×2^(n-1)、`FIXED`=base，n 为第几次重试 |
| `maxConcurrentRetries` | 100 | 只用于异步模式，必须大于 0 |
| `businessKey` | null | 只用于日志 |
| `enableFallback` | true | 见 §7.3 |
| `retryFor` | `{Exception.class}` | 白名单，按 `isAssignableFrom` 匹配子类 |
| `noRetryFor` | `{}` | 黑名单，优先级高于白名单 |

### 7.2 同步模式

```java
Order o = retryExecutor.execute(config, () -> orderClient.query(id));
```

- 在**调用方线程**中执行，用 `Thread.sleep` 实现退避，不使用重试线程池。
- 遇到不可重试的异常时立即抛出原异常；次数用尽后抛出最后一次的异常。
- 线程被中断时抛出 `RuntimeException("重试被中断")`，并恢复中断标记。
- 由于会阻塞调用线程，不要在 Web 请求线程中配置较长的退避时间。

### 7.3 异步模式

```java
retryExecutor.executeAsync(config, () -> notifyClient.send(msg), new RetryCallback<>() {
    @Override public void onSuccess(Void r, int attempt) { ... }
    @Override public void onFinalFailure(Exception e, int totalAttempts) { ... }
});
```

- **首次执行在调用方线程中同步进行**，只有失败之后的重试才提交到 `retryScheduledExecutor`。
- 一条重试链只占用一个信号量许可。信号量**按 `maxConcurrentRetries` 的数值分组**，所有配置了相同数值的调用方共享同一个信号量，与 `businessKey` 无关。
- 获取不到许可，或者调度被拒绝时：
  - `enableFallback=true`：在重试线程池中把**同一个 operation** 再执行一次（这里的"降级"指补执行一次，并不是调用另一段备用逻辑）。线程池也拒绝时，在当前线程执行。
  - `enableFallback=false`：直接调用 `onFinalFailure`。
- 回调抛出的异常会被捕获并记录日志，不会触发重试。callback 可以为 null。
- 重试线程沿用 `executeAsync` 调用方的 traceId（重试池为 `TraceAwareScheduledThreadPoolExecutor`）；业务方自定义 `retryScheduledExecutor` 时需自行保证透传。

---

## 8. CompletableFutureConvert

```java
CompletableFuture<User> f1 = CompletableFutureConvert.async(() -> userRepo.find(id), 3, ioExecutor);
CompletableFuture<User> f2 = CompletableFutureConvert.asyncForBaseResult(() -> userApi.getUser(id), 3, ioExecutor);
```

- 内部把任务包装为 `FutureTask` 提交到 `pool`，返回的 Future 带 `orTimeout(timeoutSec, SECONDS)`。超时（或调用方主动 `cancel`）时，Future 以 `TimeoutException`（或 `CancellationException`）结束，并对底层任务执行 `cancel(true)`：未开始的任务不再执行，正在执行的线程被中断。任务需要响应中断（阻塞 I/O、`sleep`、检查中断标记）才能真正提前结束。
- 线程池拒绝提交时，Future 立即以 `RejectedExecutionException` 结束。
- `asyncForBaseResult` 的解包规则：
  - `success=true` 时返回 data；
  - 结果为 null、`success` 为 false 或 null 时，抛出 `RuntimeException("REMOTE_FAIL: code:msg")`。
- 应传入框架的 `CustomTaskExecutor`，这样才能透传 TraceId。

---

## 9. 生成代码时的规则

**应该这样做：**

- 按需开启 `create-xxx` 开关；只写 `xxx-pool-args` **不会**创建线程池。
- 注入线程池时一律使用名称（`@Resource(name=…)` 或 `@Qualifier`），`@Async` 写明 `"asyncTaskExecutor"`。
- 阻塞 I/O 任务用 `ioIntensiveTaskExecutor`，纯计算任务用 `cpuIntensiveTaskExecutor`，一般后台任务用 `commonTaskExecutor`。
- 重试时用 `noRetryFor` 排除业务异常（如参数校验类异常），只对网络或超时类异常重试。
- 开启监控时，默认只监控框架线程池；需要监控第三方或自建线程池时用 `include-names` 显式纳入，并为大线程池设置匹配的 `max-core-pool-size`。
- 通过 `CompletableFutureConvert` 执行的任务要能响应中断，超时取消才能真正释放线程。

**不要这样做：**

- 不要按类型注入 `Executor` / `TaskExecutor`，也不要使用不带名称的 `@Async`。
- 不要配置 `retry-pool-args.max-pool-size` / `queue-capacity`（已不存在，会被忽略），扩大重试池应调大 `core-pool-size`。
- 不要把 `executeAsync` 当作完全异步的调用：首次执行会阻塞调用方。
- 不要把调度池 Bean 当作 `ThreadPoolTaskScheduler` 或 `Executor` 注入，它的类型是 `TraceAwareTaskScheduler`。
- 不要在 `@Bean` 中手动 `new ThreadPoolTaskExecutor` 又期望它透传 TraceId，应该使用 `new CustomTaskExecutor()`，或用 `TraceIdPropagator.DECORATOR` 作为 TaskDecorator。

---

## 10. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | 框架手册 §3.9.2 | 配置示例只写了 `common-pool-args` | 没有 `create-common-pool: true`，按此配置通用线程池不会被创建 |
| 2 | 技术特点 §2.11 | `@Primary` 调度池会被 `@Scheduled` **和 `RetryExecutor`** 自动使用 | `RetryExecutor` 注入的是 `retryScheduledExecutor`，与调度池无关 |
| 3 | 技术特点 §2.11 | `@Primary` "消除冲突" | 它同时也是 `TaskExecutor`，会被按类型注入的 Executor 和无名称的 `@Async` 选中，并且不透传 TraceId **已修复**：去掉 `@Primary`，调度池注册为只实现 `TaskScheduler` 的 `TraceAwareTaskScheduler`，不再是 Executor 候选，并透传/生成 TraceId |
| 4 | 技术特点 §2.2 | 调度池使用语义化前缀 | 前缀硬编码为 `scheduled-`，`schedule-pool-args.thread-name-prefix` 不生效 |
| 5 | 开发手册 / 技术特点 | 重试池可配置 max-pool-size | `ScheduledThreadPoolExecutor` 线程数固定为 core，max 和 queue-capacity 都无效 **已修复**：调度池与重试池改用 `ScheduledPoolArgs`，不再提供 `max-pool-size`、`queue-capacity` 等无效参数 |
| 6 | 技术特点 §2.7 | "降级处理" | 降级就是对同一个 operation 再执行一次，不存在独立的 fallback 函数 |
| 7 | 开发手册 §10.4 | 只给了异步模式的示例 | 没有说明首次执行在调用方线程中同步进行（技术特点 §2.7 的流程图有标注） |
| 8 | 开发手册 / 技术特点 | TraceId 全链路透传 | 只有 `CustomTaskExecutor` 透传；调度池、重试池、监控线程都不透传 **已修复**：调度池、重试池、监控线程统一通过 `TraceIdPropagator` 透传 traceId（无上游 traceId 的定时/监控任务每次执行生成新值） |
| 9 | 开发手册 §8 | 默认 `min/max-core-pool-size` 为 2 / 20 | 没有说明它会作用于所有被发现的线程池，可能把大线程池缩到 2，或把扩容上限限制在 20；也会监控第三方库的 `ThreadPoolTaskExecutor` **已修复**：默认只监控框架创建的线程池（第三方通过 `include-names` 或 `monitor-all-executors` 纳入），缩容不低于注册时的核心线程数 |
| 10 | 技术特点 §2.10 | `orTimeout` 防止线程永久阻塞 | 只结束 Future，不会中断或取消底层任务，执行线程仍被占用 **已修复**：超时或主动取消时对底层 `FutureTask` 执行 `cancel(true)`，未开始的任务不再执行，运行中的线程被中断 |
| 11 | 两份文档 | 未说明 | `asyncForBaseResult` 在 `success` 为 null 时抛 NPE |
| 12 | 开发手册 §2 | `ThreadPoolMonitorAutoConfig` 是自动配置 | 它不在 imports 文件中，而是由 `ThreadPoolConfig` 通过 `@ImportAutoConfiguration` 引入 |
| 13 | 框架手册 / 开发手册 | 未说明 | 框架不提供 `@EnableAsync` / `@EnableScheduling` / `AsyncConfigurer`，需要业务方自行开启并指定执行器 |
