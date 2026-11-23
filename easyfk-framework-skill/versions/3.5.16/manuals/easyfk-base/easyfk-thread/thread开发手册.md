# easyfk-thread 开发文档

## 1. 模块概述

`easyfk-thread` 是 EasyFK 框架的**线程池管理与异步任务模块**，提供以下核心能力：

- **六种预定义线程池**：通用、异步（@Async）、调度（@Scheduled）、I/O 密集型、CPU 密集型、重试线程池
- **全链路 TraceId 传递**：自动在父子线程间传递 TraceId + MDC 日志上下文
- **线程池动态监控与自动伸缩**：基于负载指标（线程利用率 / 队列利用率）自动扩缩容
- **重试执行器**：支持同步/异步模式、三种退避策略、信号量并发控制、降级处理
- **CompletableFuture 转换工具**：将阻塞调用转为异步，并自动解包 BaseResult

---

## 2. 依赖关系

```groovy
dependencies {
    compileOnly project(':easyfk-core')
}
```

| 依赖 | 说明 |
|---|---|
| `easyfk-core` | 提供 `TraceIdContext`、`RequestHeaderConstant`、`EmptyUtil`、`BaseResult` |

---

## 3. 包结构

```
easyfk-thread/
├── build.gradle
└── src/main/java/com/mcst/easyfk/thread/
    ├── config/
    │   ├── ThreadPoolConfig.java              # 线程池自动配置（核心）
    │   └── ThreadPoolMonitorAutoConfig.java   # 监控自动配置
    ├── properties/
    │   ├── ThreadPoolBaseProperties.java       # 线程池基础配置
    │   ├── ThreadPoolArgs.java                # 线程池参数（可复用）
    │   ├── ThreadPoolMonitorProperties.java   # 监控配置
    │   └── DynamicAdjustmentConfig.java       # 动态调整配置
    ├── CustomTaskExecutor.java                # 增强的任务执行器（TraceId 传递）
    ├── ThreadPoolMetrics.java                 # 线程池指标数据
    ├── ThreadPoolMonitor.java                 # 线程池监控器
    ├── AsyncThreadPoolMonitor.java            # 异步线程池监控器
    ├── ThreadPoolMonitorManager.java          # 监控器管理器
    ├── AdjustmentDecision.java                # 调整决策
    ├── async/
    │   └── CompletableFutureConvert.java      # CompletableFuture 转换工具
    └── retry/
        ├── RetryConfig.java                   # 重试配置
        ├── RetryContext.java                  # 重试上下文
        ├── RetryCallback.java                 # 重试回调接口
        ├── BackoffStrategy.java               # 退避策略枚举
        ├── RetryableOperation.java            # 可重试操作接口
        └── RetryExecutor.java                 # 重试执行器
```

---

## 4. 配置属性

### 4.1 线程池基础配置

配置前缀：`easyfk.config.thread.pool`

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `create-common-pool` | Boolean | `false` | 是否创建通用线程池 |
| `create-async-pool` | Boolean | `false` | 是否创建异步执行线程池（配合 @Async） |
| `create-schedule-pool` | Boolean | `false` | 是否创建任务调度线程池（配合 @Scheduled） |
| `create-io-intensive-pool` | Boolean | `false` | 是否创建 I/O 密集型线程池 |
| `create-cpu-intensive-pool` | Boolean | `false` | 是否创建 CPU 密集型线程池 |
| `create-retry` | Boolean | `false` | 是否创建重试线程池 + RetryExecutor |

### 4.2 线程池参数（ThreadPoolArgs）

每种线程池都有独立的参数配置：

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `core-pool-size` | Integer | CPU 核心数 | 核心线程数（未设置时自动获取） |
| `max-pool-size` | Integer | 核心数 × 1.5 | 最大线程数（确保 ≥ 核心数） |
| `queue-capacity` | Integer | 200 | 队列容量 |
| `keep-alive-seconds` | Integer | 60 | 空闲线程存活时间 |
| `thread-name-prefix` | String | `custom-thread-` | 线程名前缀 |
| `wait-for-tasks-to-complete-on-shutdown` | Boolean | `true` | 关闭时等待任务完成 |
| `await-termination-seconds` | Integer | 60 | 等待终止时间 |
| `allow-core-thread-time-out` | Boolean | `false` | 核心线程是否超时回收 |
| `prestart-all-core-threads` | Boolean | `false` | 是否预热核心线程 |
| `rejected-execution-handler` | String | `CALLER_RUNS` | 拒绝策略：ABORT / CALLER_RUNS / DISCARD / DISCARD_OLDEST |

**配置路径映射：**

| 线程池 | 配置前缀 |
|---|---|
| 通用 | `easyfk.config.thread.pool.common-pool-args.*` |
| 异步 | `easyfk.config.thread.pool.async-pool-args.*` |
| 调度 | `easyfk.config.thread.pool.schedule-pool-args.*` |
| I/O 密集 | `easyfk.config.thread.pool.io-intensive-pool-args.*` |
| CPU 密集 | `easyfk.config.thread.pool.cpu-intensive-pool-args.*` |
| 重试 | `easyfk.config.thread.pool.retry-pool-args.*` |

### 4.3 监控配置

配置前缀：`easyfk.config.thread.pool.monitor`

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `enabled` | boolean | `false` | 是否启用监控 |
| `auto-discovery` | boolean | `true` | 是否自动发现线程池 |
| `auto-start` | boolean | `true` | 是否自动启动监控 |
| `include-names` | List\<String\> | `[]` | 包含的线程池名称（空表示全部） |
| `exclude-names` | List\<String\> | `[]` | 排除的线程池名称 |

### 4.4 动态调整配置（DynamicAdjustmentConfig）

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `enabled` | Boolean | `true` | 是否启用动态调整 |
| `monitoring-interval` | Duration | 30s | 监控间隔 |
| `cooldown-period` | Duration | 2min | 冷却期（两次调整最小间隔） |
| `min-core-pool-size` | Integer | 2 | 最小核心线程数 |
| `max-core-pool-size` | Integer | 20 | 最大核心线程数 |
| `scale-up-step` | Integer | 2 | 扩容步长 |
| `scale-down-step` | Integer | 1 | 缩容步长 |
| `high-load-threshold` | Double | 80.0 | 高负载阈值（线程利用率 %） |
| `low-load-threshold` | Double | 30.0 | 低负载阈值（线程利用率 %） |
| `queue-high-threshold` | Double | 70.0 | 队列高负载阈值（%） |
| `queue-low-threshold` | Double | 20.0 | 队列低负载阈值（%） |
| `async-monitoring-enabled` | Boolean | `true` | 是否启用异步监控 |
| `async-monitoring-pool-size` | Integer | 2 | 异步监控线程池大小 |
| `async-monitoring-queue-capacity` | Integer | 100 | 异步监控队列容量 |
| `async-monitoring-timeout-seconds` | Integer | 30 | 异步监控超时时间 |

---

## 5. 配置示例

```yaml
easyfk:
  config:
    thread:
      pool:
        create-common-pool: true
        create-async-pool: true
        create-schedule-pool: true
        create-io-intensive-pool: true
        create-retry: true

        common-pool-args:
          core-pool-size: 8
          max-pool-size: 16
          queue-capacity: 500
          thread-name-prefix: "common-"
          rejected-execution-handler: CALLER_RUNS

        async-pool-args:
          core-pool-size: 4
          queue-capacity: 200

        io-intensive-pool-args:
          core-pool-size: 16
          max-pool-size: 32
          queue-capacity: 1000
          keep-alive-seconds: 120

        retry-pool-args:
          core-pool-size: 2
          thread-name-prefix: "retry-"

        monitor:
          enabled: true
          auto-discovery: true
          auto-start: true
          exclude-names:
            - retryScheduledExecutor
          default-config:
            monitoring-interval: 30s
            cooldown-period: 2m
            high-load-threshold: 80.0
            low-load-threshold: 30.0
            async-monitoring-enabled: true
          configs:
            commonTaskExecutor:
              high-load-threshold: 70.0
              max-core-pool-size: 30
              scale-up-step: 3
```

---

## 6. 自动配置

### 6.1 ThreadPoolConfig

`@AutoConfiguration` 类，注册所有线程池 Bean：

| Bean 名称 | 类型 | 条件 | 说明 |
|---|---|---|---|
| `commonTaskExecutor` | `CustomTaskExecutor` | `create-common-pool=true` | 通用线程池 |
| `asyncTaskExecutor` | `CustomTaskExecutor` | `create-async-pool=true` | 异步线程池（前缀自动设为 `async-`） |
| `scheduleTaskExecutor` / `taskScheduler` | `TaskScheduler` | `create-schedule-pool=true` | 调度线程池（`@Primary`） |
| `ioIntensiveTaskExecutor` | `CustomTaskExecutor` | `create-io-intensive-pool=true` | I/O 密集型线程池 |
| `cpuIntensiveTaskExecutor` | `CustomTaskExecutor` | `create-cpu-intensive-pool=true` | CPU 密集型线程池 |
| `retryScheduledExecutor` | `ScheduledExecutorService` | `create-retry=true` | 重试调度线程池 |
| `retryExecutor` | `RetryExecutor` | `create-retry=true` | 重试执行器 |

### 6.2 ThreadPoolMonitorAutoConfig

`@AutoConfiguration` 类，条件：`monitor.enabled=true`

- 注册 `ThreadPoolMonitorManager` Bean，容器关闭时自动停止其管理的全部监控器
- 注册 `ThreadPoolMonitorRegistrar`，由它完成线程池的自动发现

`ThreadPoolMonitorRegistrar` 实现 `SmartInitializingSingleton`，在所有单例装配完成后执行发现动作，
避免在配置类初始化阶段就触发线程池 Bean 的提前实例化：

- 扫描所有 `ThreadPoolTaskExecutor` Bean
- 根据 include/exclude 规则过滤
- 为每个线程池创建 `ThreadPoolMonitor`，支持特定配置和默认配置，并注册到 `ThreadPoolMonitorManager`
- 自动启动监控（`auto-start=true` 时）

> 注意：发现逻辑必须通过注入拿到 `ThreadPoolMonitorManager`。`@AutoConfiguration` 等价于
> `@Configuration(proxyBeanMethods = false)`，在配置类内部直接调用 `@Bean` 方法拿到的是新建对象而非容器中的 Bean。

---

## 7. CustomTaskExecutor（TraceId 传递）

继承 `ThreadPoolTaskExecutor`，通过 `TaskDecorator` 织入上下文传递：

```java
public class CustomTaskExecutor extends ThreadPoolTaskExecutor {

    public CustomTaskExecutor() {
        super.setTaskDecorator(CustomTaskExecutor::withTraceId);
    }

    @Override
    public void setTaskDecorator(TaskDecorator taskDecorator) {
        super.setTaskDecorator(task -> withTraceId(taskDecorator.decorate(task)));
    }

    private static Runnable withTraceId(Runnable task) {
        final String traceId = TraceIdContext.getTraceId();
        return () -> {
            try {
                if (EmptyUtil.isNotEmpty(traceId)) {
                    TraceIdContext.setTraceId(traceId);
                    MDC.put(RequestHeaderConstant.TRACE_ID, traceId);
                }
                task.run();
            } finally {
                TraceIdContext.remove();
                MDC.remove(RequestHeaderConstant.TRACE_ID);
            }
        };
    }
}
```

**功能：**
- 提交任务前捕获当前线程的 TraceId
- 任务执行时自动注入 TraceId 到子线程的 `TraceIdContext` 和 `MDC`
- 任务结束后清理，防止泄漏

**为什么用 TaskDecorator 而不是重写 `execute()`：**
`ThreadPoolTaskExecutor` 的 `submit()` 与 `submitListenable()` 直接操作内层的 `ThreadPoolExecutor`，
不会经过外层的 `execute()`；而 `@Async` 在返回值为 `void` 或 `Future` 时走的正是 `submit()`。
只有 `TaskDecorator` 是在内层执行器上生效的，能够覆盖 `execute` / `submit` / `@Async` 的全部提交路径。

业务方仍可调用 `setTaskDecorator()` 追加自己的装饰器，TraceId 传递会保留在最外层，不会被覆盖。

---

## 8. 线程池监控

### 8.1 ThreadPoolMetrics（指标数据）

| 指标 | 说明 |
|---|---|
| `corePoolSize` | 核心线程数 |
| `maxPoolSize` | 最大线程数 |
| `activeThreadCount` | 活跃线程数 |
| `poolSize` | 当前线程池大小 |
| `queueSize` | 队列中等待任务数 |
| `queueCapacity` | 队列容量 |
| `completedTaskCount` | 已完成任务数 |
| `taskCount` | 总任务数 |
| `threadUtilization` | 线程利用率（active / core × 100） |
| `queueUtilization` | 队列利用率（queueSize / capacity × 100） |
| `loadStatus` | 负载状态：LOW / MEDIUM / HIGH / CRITICAL |

### 8.2 AdjustmentDecision（调整决策）

| 类型 | 说明 |
|---|---|
| `SCALE_UP` | 扩容 |
| `SCALE_DOWN` | 缩容 |
| `NO_CHANGE` | 无需调整 |

提供工厂方法：`scaleUp()`、`scaleDown()`、`noChange()`

### 8.3 ThreadPoolMonitor（监控器）

核心功能：
- `startMonitoring()` — 启动监控（CAS 幂等保护）
- `stopMonitoring()` — 停止监控
- `manualAdjust()` — 手动触发一次调整
- `getStatistics()` — 获取完整统计信息
- `resetStatistics()` — 重置统计数据

支持同步 / 异步两种监控模式，OOM 时自动降级为同步模式。

### 8.4 ThreadPoolMonitorManager（管理器）

集中管理所有监控器：

```java
// 获取指定监控器
ThreadPoolMonitor monitor = manager.getMonitor("commonTaskExecutor");

// 获取所有统计
Map<String, Map<String, Object>> stats = manager.getAllStatistics();

// 启动/停止所有监控
manager.startAllMonitoring();
manager.stopAllMonitoring();
```

---

## 9. CompletableFuture 转换工具

### 9.1 通用异步转换

```java
CompletableFuture<Result> future = CompletableFutureConvert.async(
    () -> slowService.query(param),
    5,   // 超时秒数
    ioIntensiveTaskExecutor
);
```

### 9.2 BaseResult 自动解包

```java
CompletableFuture<UserDto> future = CompletableFutureConvert.asyncForBaseResult(
    () -> userApi.getUser(userId),
    3,   // 超时秒数
    ioIntensiveTaskExecutor
);

// future 直接包含 UserDto，无需手动解包 BaseResult
// 失败时自动抛出 RuntimeException("REMOTE_FAIL: code:msg")
```

---

## 10. 重试执行器

### 10.1 退避策略（BackoffStrategy）

| 策略 | 计算公式 | baseDelay=500ms 示例 |
|---|---|---|
| `LINEAR` | base × attempt | 500ms, 1000ms, 1500ms |
| `EXPONENTIAL` | base × 2^(attempt-1) | 500ms, 1000ms, 2000ms |
| `FIXED` | base（恒定） | 500ms, 500ms, 500ms |

### 10.2 RetryConfig（重试配置）

```java
RetryConfig config = RetryConfig.builder()
    .maxRetries(3)                              // 最大重试 3 次
    .baseDelayMs(500)                           // 基础延迟 500ms
    .backoffStrategy(BackoffStrategy.LINEAR)    // 线性退避
    .maxConcurrentRetries(100)                  // 最大并发重试数
    .businessKey("pushMsg:user123")             // 业务标识
    .enableFallback(true)                       // 启用降级
    .retryFor(new Class[]{IOException.class})   // 仅重试 IO 异常
    .noRetryFor(new Class[]{IllegalArgumentException.class}) // 参数异常不重试
    .build();
```

### 10.3 同步模式

```java
@Resource
private RetryExecutor retryExecutor;

// 同步执行，失败自动重试，所有重试完成后返回或抛异常
try {
    String result = retryExecutor.execute(config, () -> {
        return httpClient.get(url);
    });
} catch (Exception e) {
    // 所有重试都失败后的异常
}
```

### 10.4 异步模式

```java
retryExecutor.executeAsync(config, () -> {
    rocketProducer.send(message);
    return null;
}, new RetryCallback<Void>() {
    @Override
    public void onSuccess(Void result, int attempt) {
        log.info("发送成功，尝试次数: {}", attempt);
    }

    @Override
    public void onFinalFailure(Exception e, int totalAttempts) {
        log.error("发送最终失败，总尝试: {}", totalAttempts, e);
    }
});
```

### 10.5 RetryCallback（回调接口）

| 方法 | 说明 |
|---|---|
| `onSuccess(T result, int attempt)` | 操作成功时调用（首次或重试后） |
| `onFinalFailure(Exception e, int totalAttempts)` | 最终失败时调用 |

两个方法都有默认空实现，可按需覆盖。

---

## 11. 预定义配置模板

`DynamicAdjustmentConfig` 提供三种预置配置：

| 模板 | 方法 | 监控间隔 | 冷却期 | 高负载阈值 | 扩容步长 | 异步监控 |
|---|---|---|---|---|---|---|
| 默认 | `defaultConfig()` | 30s | 2min | 80% | 2 | 启用 |
| 高性能 | `highPerformanceConfig()` | 15s | 1min | 70% | 3 | 启用（4线程） |
| 保守 | `conservativeConfig()` | 2min | 5min | 90% | 1 | 关闭 |
