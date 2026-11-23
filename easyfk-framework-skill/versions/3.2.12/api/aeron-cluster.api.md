# aeron-cluster API 签名速查（easyfk 3.2.12）

> 坐标：`com.mcst:aeron-cluster-core、aeron-cluster-client、aeron-cluster-spring-boot-starter`　源码：`aeron-cluster/aeron-cluster-core`、`aeron-cluster/aeron-cluster-client`、`aeron-cluster/aeron-cluster-spring-boot-starter`、`aeron-cluster/aeron-cluster-test`
> 由 `scripts/gen-api.py` 从 97 个源文件自动提取，共 76 个类型、465 个方法/构造器、67 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/aeron-cluster-skill.md](../modules/aeron-cluster-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 配置项（@ConfigurationProperties）

### `easyfk.config.aeron.cluster` ← ClusterProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `node` | `NodeProperties` | `new NodeProperties()` |  |
| `client` | `ClientProperties` | `new ClientProperties()` |  |
| `shutdown` | `ShutdownProperties` | `new ShutdownProperties()` |  |


## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `aeron-cluster-spring-boot-starter` | `com.mcst.aeron.cluster.spring.autoconfig.ClusterAutoConfiguration` |

## 类型索引

- `com.mcst.aeron.cluster.client.api`：[ClusterClient](#clusterclient)、[ClusterClientBuilder](#clusterclientbuilder)、[ClusterEventListener](#clustereventlistener)、[ReconnectStrategy](#reconnectstrategy)、[RetryPolicy](#retrypolicy)
- `com.mcst.aeron.cluster.client.config`：[ClusterClientConfig](#clusterclientconfig)
- `com.mcst.aeron.cluster.client.internal`：[AeronClusterClient](#aeronclusterclient)、[RetryingClusterClient](#retryingclusterclient)
- `com.mcst.aeron.cluster.core.api`：[AsyncSnapshotSource](#asyncsnapshotsource)、[ClusterClock](#clusterclock)、[ClusterContext](#clustercontext)、[ClusterSession](#clustersession)、[ClusterStateMachine](#clusterstatemachine)
    [RoleChangeListener](#rolechangelistener)、[SnapshotHeader](#snapshotheader)、[SnapshotReader](#snapshotreader)、[SnapshotView](#snapshotview)、[SnapshotWriter](#snapshotwriter)
    [StateAuditContext](#stateauditcontext)、[StateAuditSink](#stateauditsink)、[StateAuditSource](#stateauditsource)、[StateAuditView](#stateauditview)、[SystemClusterClock](#systemclusterclock)
- `com.mcst.aeron.cluster.core.config`：[ClusterMember](#clustermember)、[ClusterNodeConfig](#clusternodeconfig)、[ClusterTopology](#clustertopology)、[MediaDriverMode](#mediadrivermode)、[SnapshotQuietWindow](#snapshotquietwindow)
- `com.mcst.aeron.cluster.core.exception`：[ClusterClientException](#clusterclientexception)、[ClusterCommandException](#clustercommandexception)、[ClusterConfigException](#clusterconfigexception)、[ClusterException](#clusterexception)、[ClusterSnapshotException](#clustersnapshotexception)
    [ClusterTimeoutException](#clustertimeoutexception)
- `com.mcst.aeron.cluster.core.frame`：[ClusterFrameHeader](#clusterframeheader)、[ClusterFrameProtocol](#clusterframeprotocol)、[ClusterFrameType](#clusterframetype)
- `com.mcst.aeron.cluster.core.idempotence`：[AbstractIdempotentStateMachine](#abstractidempotentstatemachine)
- `com.mcst.aeron.cluster.core.internal`：[ClusterDirLayout](#clusterdirlayout)、[ClusterMarkFileHelper](#clustermarkfilehelper)、[EmbeddedClusterNode](#embeddedclusternode)、[ExternalClusterNode](#externalclusternode)、[FrameworkClusteredService](#frameworkclusteredservice)
    [IdleStrategyFactory](#idlestrategyfactory)
- `com.mcst.aeron.cluster.core.lifecycle`：[ClusterNode](#clusternode)
- `com.mcst.aeron.cluster.core.metrics`：[ClusterMetrics](#clustermetrics)、[InMemoryClusterMetrics](#inmemoryclustermetrics)、[NoopClusterMetrics](#noopclustermetrics)
- `com.mcst.aeron.cluster.core.role`：[ClusterRole](#clusterrole)
- `com.mcst.aeron.cluster.core.session`：[CloseReason](#closereason)、[SessionId](#sessionid)
- `com.mcst.aeron.cluster.core.snapshot`：[SnapshotEntryHeader](#snapshotentryheader)、[SnapshotFileFormat](#snapshotfileformat)、[SnapshotMagic](#snapshotmagic)
- `com.mcst.aeron.cluster.core.timer`：[ClusterTimer](#clustertimer)
- `com.mcst.aeron.cluster.core.wire`：[ClusterCommandFrameEncoder](#clustercommandframeencoder)、[ClusterEgressFrameEncoder](#clusteregressframeencoder)、[ClusterFrameDecoder](#clusterframedecoder)、[ClusterResponseFrameEncoder](#clusterresponseframeencoder)
- `com.mcst.aeron.cluster.spring.actuator`：[ClusterHealthIndicator](#clusterhealthindicator)
- `com.mcst.aeron.cluster.spring.annotation`：[ClusterEventListener](#clustereventlistener)、[ClusterStateMachineBean](#clusterstatemachinebean)
- `com.mcst.aeron.cluster.spring.autoconfig`：[ClusterActuatorAutoConfiguration](#clusteractuatorautoconfiguration)、[ClusterAutoConfiguration](#clusterautoconfiguration)、[ClusterClientAutoConfiguration](#clusterclientautoconfiguration)、[ClusterNodeAutoConfiguration](#clusternodeautoconfiguration)
- `com.mcst.aeron.cluster.spring.properties`：[ClusterProperties](#clusterproperties)
- `com.mcst.aeron.cluster.spring.runtime`：[ClusterClientLifecycle](#clusterclientlifecycle)、[ClusterEventListenerBeanPostProcessor](#clustereventlistenerbeanpostprocessor)、[ClusterLifecycle](#clusterlifecycle)
- `com.mcst.aeron.cluster.test.extension`：[EmbeddedClusterExtension](#embeddedclusterextension)
- `com.mcst.aeron.cluster.test.fixture`：[ClusterClientFixture](#clusterclientfixture)、[EmbeddedSingleNodeCluster](#embeddedsinglenodecluster)、[EmbeddedThreeNodeCluster](#embeddedthreenodecluster)、[PortAllocator](#portallocator)
- `com.mcst.aeron.cluster.test.wait`：[ClusterAwait](#clusterawait)

## 包 `com.mcst.aeron.cluster.client.api`

### ClusterClient

`public interface ClusterClient extends AutoCloseable`　业务方使用 Cluster 的入口. 由 ClusterClientBuilder 构造.

**方法**

```java
void connect()  // 同步建立与集群的连接 (包括 ingress publication + egress subscription). 失败抛 ClusterClientException.
boolean isConnected()
long clusterSessionId()  // Aeron 分配的会话 id; 未连接时返回 -1.
int leaderMemberId()  // 当前认为的 leader memberId; 未知时返回 -1.
<T> long send(Codec<T> codec, T command)  // Fire-and-forget 发送一条命令.
<T, R> CompletableFuture<R> sendAndAwait(Codec<T> codec, T command, Codec<R> respCodec, long timeoutMs)  // 发送一条命令并等待对应 RESPONSE (按 correlation id 匹配). 返回 future 时命令可能尚未编码完成, 框架保证 future 在 timeout 内必定 complete (正常完成 /…
<T, R> CompletableFuture<R> sendAndAwait(Codec<T> codec, T command, Codec<R> respCodec)  // 用 config.responseTimeoutMs 作为超时调 sendAndAwait(Codec, Object, Codec, long).
int pollEgress()  // 在调用线程上 poll 一次 egress, 用于关闭了 backgroundPoller 的场景. 返回处理的 fragment 数.
void addEventListener(ClusterEventListener listener)
void removeEventListener(ClusterEventListener listener)
void close()
```

### ClusterClientBuilder

`public final class ClusterClientBuilder`　创建 ClusterClient 的统一入口. 不调 build(), 直接传一份已构造好的 config 即可.

**方法**

```java
static ClusterClient create(ClusterClientConfig config)
static ClusterClient createRetrying(ClusterClientConfig config, RetryPolicy policy)  // 创建一个带重试的客户端: 在 AeronClusterClient 外套 RetryingClusterClient.
static ClusterClient withRetry(ClusterClient delegate, RetryPolicy policy)  // 给一个已有的 ClusterClient 套上重试装饰 (便于自定义 delegate / 测试).
```

### ClusterEventListener

`public interface ClusterEventListener`　业务方注册的 egress 事件回调. 框架在 poller 线程上同步回调, 业务实现禁止做阻塞 IO.

**方法**

```java
default void onEgressEvent(int codecId, DirectBuffer buffer, int offset, int length)  // Leader 主动推送的 egress event (frame_type=EGRESS_EVENT, 无 correlation).
default void onNewLeader(long clusterSessionId, long leadershipTermId, int newLeaderMemberId)  // New leader 通知. 框架已经自动切换 ingress endpoint, 业务通常无需额外动作.
default void onDisconnected()  // 客户端检测到断连且重连策略已放弃时回调. 触发场景: none(): 第一次断连立即放弃, 立即回调; ExponentialBackoffReconnectStrategy: 重试 maxAttempts 次仍失败后回…
default void onReconnected(int attempts)  // 客户端重连成功; attempts 是本次成功对应的尝试次数 (从 1 开始).
```

### ReconnectStrategy

`public interface ReconnectStrategy`　客户端重连策略 SPI. 框架在检测到 ingress publication 不可用 (连接被切断 / new leader 但未及时收到 hint) 时回调 nextDelayMs(int) 决定下次尝试的 slee…

**方法**

```java
long nextDelayMs(int attempt)
static ReconnectStrategy none()  // 直接放弃, 不重连.
static ReconnectStrategy exponentialBackoff(long initialDelayMs, long maxDelayMs, double factor, int maxAttempts)  // 指数退避: initial * factor^(attempt-1), 上限 max, 最多 maxAttempts 次.
```

### RetryPolicy

`public final class RetryPolicy`　RetryingClusterClient 的重试策略. 不可变, Builder 构造.

**方法**

```java
int maxAttempts()  // 最大尝试次数 (含首次); 1 表示不重试.
boolean retryOnTimeout()  // 是否对响应超时重试 (仅在命令幂等时才应打开).
Predicate<Throwable> retryableException()  // 业务自定义的"可重试"判定; 可能为 null.
long backoffMs(int attempt)  // 第 attempt 次重试 (1-based) 前的退避毫秒.
static RetryPolicy defaults()  // 默认策略: 最多 3 次, 20ms 起指数退避到 500ms, 不对超时重试.
static Builder builder()
```

#### RetryPolicy.Builder

`public static final class Builder`

**方法**

```java
Builder maxAttempts(int v)
Builder initialBackoffMs(long v)
Builder maxBackoffMs(long v)
Builder factor(double v)
Builder retryOnTimeout(boolean v)  // 打开对响应超时的重试. 仅当命令幂等时使用 —— 否则重复执行风险由业务自负.
Builder retryableException(Predicate<Throwable> v)  // 追加一个自定义"可重试"判定, 用于默认分类之外的异常.
RetryPolicy build()
```

## 包 `com.mcst.aeron.cluster.client.config`

### ClusterClientConfig

`public final class ClusterClientConfig`　cluster 客户端配置. 不可变, Builder 构造, 全字段 final.

**方法**

```java
String ingressEndpoints()
String egressChannel()
String aeronDir()
CodecRegistry codecRegistry()
ReconnectStrategy reconnectStrategy()
long responseTimeoutMs()
long connectTimeoutMs()
long pollerIdleSleepNs()
long keepAliveIntervalMs()
boolean enableBackgroundPoller()
boolean ownsAeronDir()
ClusterMetrics metrics()
static Builder builder()
```

#### ClusterClientConfig.Builder

`public static final class Builder`

**方法**

```java
Builder ingressEndpoints(String v)
Builder egressChannel(String v)
Builder aeronDir(String v)
Builder codecRegistry(CodecRegistry v)
Builder reconnectStrategy(ReconnectStrategy v)
Builder responseTimeoutMs(long v)
Builder connectTimeoutMs(long v)
Builder pollerIdleSleepNs(long v)
Builder keepAliveIntervalMs(long v)
Builder enableBackgroundPoller(boolean v)
Builder metrics(ClusterMetrics v)
ClusterClientConfig build()
```

## 包 `com.mcst.aeron.cluster.client.internal`

### AeronClusterClient

`public final class AeronClusterClient implements ClusterClient`

**构造器**

```java
AeronClusterClient(ClusterClientConfig config)
```

**方法**

```java
void connect()
boolean isConnected()
long clusterSessionId()
int leaderMemberId()
<T> long send(Codec<T> codec, T command)
<T, R> CompletableFuture<R> sendAndAwait(Codec<T> codec, T command, Codec<R> respCodec, long timeoutMs)
<T, R> CompletableFuture<R> sendAndAwait(Codec<T> codec, T command, Codec<R> respCodec)
int pollEgress()
void addEventListener(ClusterEventListener listener)
void removeEventListener(ClusterEventListener listener)
void close()
```

### RetryingClusterClient

`public final class RetryingClusterClient implements ClusterClient`　给任意 ClusterClient 套一层重试的装饰器, 把"网络抖动下发送失败"的处理从每个调用点收敛到一处.

**构造器**

```java
RetryingClusterClient(ClusterClient delegate, RetryPolicy policy)
```

**方法**

```java
void connect()
boolean isConnected()
long clusterSessionId()
int leaderMemberId()
int pollEgress()
void addEventListener(ClusterEventListener listener)
void removeEventListener(ClusterEventListener listener)
<T> long send(Codec<T> codec, T command)
<T, R> CompletableFuture<R> sendAndAwait(Codec<T> codec, T command, Codec<R> respCodec, long timeoutMs)
<T, R> CompletableFuture<R> sendAndAwait(Codec<T> codec, T command, Codec<R> respCodec)
void close()
long retryCount()  // 已发生的重试次数 (累计).
long exhaustedCount()  // 重试次数耗尽仍失败的次数 (累计).
```

## 包 `com.mcst.aeron.cluster.core.api`

### AsyncSnapshotSource

`public interface AsyncSnapshotSource`　异步快照 SPI (opt-in): 业务状态机可选实现本接口, 实现即启用两阶段异步快照.

**方法**

```java
SnapshotView captureSnapshot(long logPosition)  // 在 agent 线程同步调用 (仍在 onTakeSnapshot 时序内), 捕获 logPosition 时刻的不可变一致状态视图.
```

### ClusterClock

`public interface ClusterClock`　时间源 SPI.

**方法**

```java
long timeMs()  // 进程墙钟时间 (毫秒).
long clusterTimeMs()  // 集群时间 (毫秒) -- Raft 已提交命令所对应的 cluster 时间.
```

### ClusterContext

`public interface ClusterContext extends ClusterTimer`　状态机的 "出向" 通道. 由框架在每个回调入参里提供.

**方法**

```java
int memberId()  // 本节点的 member id.
ClusterRole role()  // 本节点当前角色.
long timeMs()  // 进程墙钟时间 (毫秒). 业务方对外暴露的时间戳不要用这个 -- 用 clusterTimeMs().
long clusterTimeMs()  // 集群时间 (毫秒) = Raft 已提交命令对应的 cluster time.
void idle()  // 让出 CPU. 业务方在状态机回调里若不可避免做了短 CPU 计算, 可以礼貌挂出. 禁止用此方法实现 sleep 或同步等待.
void reportError(Throwable t)  // 异步上报一个业务错误 -- 框架转发到 metrics + log, 不会打断状态机回放.
default ClusterTimer timer()  // 把当前 context 视为一个独立 ClusterTimer 引用, 方便业务把 timer 能力下放到 子模块而不传整个 ClusterContext.
default <T> long publishEgress(ClusterSession session, Codec<T> codec, T value)  // Leader 主动向指定 session 推送一个 egress event (EGRESS_EVENT 帧). 便捷入口, 等价于 session.publishEvent(codec, value) -- 适合在 o…
default long publishEgressBytes(ClusterSession session, byte[] payload)  // raw bytes 版本的 publishEgress.
```

### ClusterSession

`public interface ClusterSession`　单个客户端会话句柄. 由框架在 onCommand / onSessionOpen 回调入参中提供, 生命周期由框架管理: 同一 session id 在打开期间始终是同一个实例, 业务可在状态机线程上 跨回调保留引用…

**方法**

```java
long id()  // 由 Aeron Cluster 分配的全局唯一 session id.
default SessionId sessionId()  // 同 id(), 包成强类型 SessionId, 方便业务方塞 Map / Set 而避免与其它 long id 串用. 默认实现一次性分配, 如果业务在热路径反复调用, 推荐复用 id() 直接拿原始 long.
long correlationId()  // 当前 inbound 命令的 correlation id; 仅在 onCommand 回调期间有意义, 其它回调上调用返回 -1.
default int responseCount()  // 本 session 自打开以来已成功 offer 的 response 帧数 (含被框架在非 leader 节点上静默 drop 的次数, 仅用于调试 / 诊断, 不参与业务逻辑). 实现可返回 0 以保持向后兼容.
<T> long respond(Codec<T> codec, T value)  // 用 codec 编码 value 并作为 egress response 发回客户端.
long respondBytes(byte[] payload)  // 直接以 raw bytes 作为 egress response.
default <T> long publishEvent(Codec<T> codec, T value)  // Leader 主动推送一个 egress event 给本 session 对应的客户端 (wire frame_type=EGRESS_EVENT, 无 correlation), 客户端按帧类型分发到 onEgres…
default long publishEventBytes(byte[] payload)  // 直接以 raw bytes 作为 egress event 主动推送. 语义同 publishEvent.
void close(CloseReason reason)  // 显式关闭该 session. 框架会在下一个 work tick 上回调 onSessionClose.
boolean isOpen()  // 当前 session 是否仍打开.
```

### ClusterStateMachine

`public interface ClusterStateMachine<C>`　业务方唯一必须实现的核心 SPI.

**方法**

```java
default void onStart(ClusterContext ctx)  // 节点启动回调, 早于任何 onCommand / onTimer / onSession*. 若存在快照, loadSnapshot 先于本回调执行 -- 即 onStart 内可见已恢复的状态.
void onCommand(ClusterSession session, C command, ClusterContext ctx)  // 一条命令已被 Raft 提交, 状态机按顺序回放.
default void onTimer(long timerId, ClusterContext ctx)  // 业务通过 scheduleTimer 注册的定时器到期回调.
default void onRoleChange(ClusterRole role)  // 节点角色变化.
default void onSessionOpen(ClusterSession session)  // 客户端会话打开 (Aeron Cluster 通过 ingress 收到 SessionConnect).
default void onSessionClose(ClusterSession session, CloseReason reason)  // 客户端会话关闭.
default void takeSnapshot(SnapshotWriter writer)  // 框架触发 snapshot, 业务方把当前 in-memory 状态写入 writer.
default void loadSnapshot(SnapshotReader reader)  // 启动 / catch-up 时从 snapshot 恢复 in-memory 状态.
default void onStop()  // 节点关闭前最后回调, 业务可释放本机资源 (定时器线程, 连接池等). 框架不保证此方法一定被调到 (例如 JVM 直接 kill -9), 所以业务方不能把"必须释放"的资源放在这里.
default Set<Integer> declaredCommandCodecIds()  // 声明本状态机能识别的命令 codec id 集合 (来自 com.mcst.aeron.common.codec.CodecIds 或业务自定义段 >= 100)…
```

### RoleChangeListener

`public interface RoleChangeListener`　注解：`@FunctionalInterface`　角色变更的独立监听 SPI, 与 onRoleChange(ClusterRole) 互补 -- 后者侧重让状态机改写内部 dispatch (例如 follower 上挂起对外 publish), 前者侧重业务"运营层…

**方法**

```java
void onRoleChange(ClusterRole previous, ClusterRole current, long termId)
```

### SnapshotHeader

`public final class SnapshotHeader`　已读取的 snapshot stream 头部信息. 业务方在 loadSnapshot 入口 通过 readHeader(int) 拿到本对象, 用 businessVersion() 决定如何加载.

**构造器**

```java
SnapshotHeader(int frameworkVersion, int businessVersion)
```

**方法**

```java
int frameworkVersion()
int businessVersion()
boolean equals(Object o)
int hashCode()
String toString()
```

### SnapshotReader

`public interface SnapshotReader`　业务状态机的 snapshot "入向" 接口.

**方法**

```java
SnapshotHeader readHeader(int maxBusinessVersion)  // 读取并校验 stream 头.
boolean hasMore()  // 还有未消费的 entry.
<T> T read(Codec<T> codec)  // 读取下一个 ENTRY_TYPE_CODEC_TYPED entry. 要求传入的 codec 的 wire id 与 stream 上一致; 不一致时抛 ClusterSnapshotException.
byte[] readBytes()  // 读取下一个 ENTRY_TYPE_BYTES entry, 返回新分配的 byte[].
int readBytes(MutableDirectBuffer dst, int offset)  // 把下一个 entry 的 payload 复制到 dst, 返回 payload 长度.
```

### SnapshotView

`public interface SnapshotView extends AutoCloseable`　captureSnapshot(long) 返回的不可变一致状态视图.

**方法**

```java
void write(SnapshotWriter writer)  // 把视图内容序列化到 writer. 由框架后台快照线程调用, 允许长时间执行; 本线程不与 agent 线程共享任何可变状态.
void close()  // 写出完成 / 失败后由框架调用, 释放视图资源. 幂等.
```

### SnapshotWriter

`public interface SnapshotWriter`　业务状态机的 snapshot "出向" 接口.

**方法**

```java
void writeHeader(int frameworkVersion, int businessVersion)  // 写入版本头: framework 内部版本 + 业务方声明的 snapshot schema 版本.
<T> void write(Codec<T> codec, T value)  // 把一个业务对象按 codec 序列化到 snapshot 流中. 内部按 ENTRY_TYPE_CODEC_TYPED 写.
void writeBytes(byte[] payload)  // 把原始字节直接写入 snapshot 流, 内部按 ENTRY_TYPE_BYTES 写. 拷贝语义: 返回后 payload 可复用.
void writeBytes(DirectBuffer src, int offset, int length)  // 把原始字节直接写入 snapshot 流, 内部按 ENTRY_TYPE_BYTES 写. 拷贝语义: 返回时 [offset, offset+length) 已复制进内部缓冲, src 可立即复用.
void flush()  // 强制刷出: 业务在分段写入大状态时调用, 给 archive 一个收口的机会. 通常不必显式调.
```

### StateAuditContext

`public final class StateAuditContext`　状态审计视图的精确捕获位置与节点信息。

**构造器**

```java
StateAuditContext(int memberId, ClusterRole role, long logPosition, long clusterTimeMs)
```

**方法**

```java
int memberId()
ClusterRole role()
long logPosition()
long clusterTimeMs()
```

### StateAuditSink

`public interface StateAuditSink`　注解：`@FunctionalInterface`　状态审计记录接收器，由业务工程实现为文件、分页缓存或校验器。

**方法**

```java
void writeRecord(String dataset, byte[] key, byte[] value) throws Exception
```

### StateAuditSource

`public interface StateAuditSource`　可审计状态机实现的扩展接口。

**方法**

```java
StateAuditView captureAuditView(StateAuditContext context)
```

### StateAuditView

`public interface StateAuditView extends AutoCloseable`　状态机在某个日志位置的一致、只读视图。

**方法**

```java
StateAuditContext context()  // 必须返回框架传给 captureAuditView(StateAuditContext) 的同一个上下文。
Map<String, Long> counts()  // 各业务数据集的记录数；返回值在视图生命周期内不可变。
void export(StateAuditSink sink) throws Exception  // 以稳定的业务定义顺序导出规范化记录。
void close()  // 释放 COW 版本引用等视图资源；实现必须幂等。
```

### SystemClusterClock

`public final class SystemClusterClock implements ClusterClock`　直接走 wall clock 的 ClusterClock 实现.

**字段 / 常量**

```java
static final SystemClusterClock INSTANCE = new SystemClusterClock()
```

**方法**

```java
long timeMs()
long clusterTimeMs()
```

## 包 `com.mcst.aeron.cluster.core.config`

### ClusterMember

`public final class ClusterMember`　集群拓扑中的一个 member.

**方法**

```java
int memberId()
String ingressEndpoint()
String consensusEndpoint()
String logEndpoint()
String catchupEndpoint()
String archiveEndpoint()
String toEndpointsString()  // Aeron Cluster ConsensusModule 期望的 member endpoints 字符串格式: ",,,,"
String toString()
boolean equals(Object o)
int hashCode()
static Builder builder()
```

#### ClusterMember.Builder

`public static final class Builder`

**方法**

```java
Builder memberId(int v)
Builder ingressEndpoint(String v)
Builder consensusEndpoint(String v)
Builder logEndpoint(String v)
Builder catchupEndpoint(String v)
Builder archiveEndpoint(String v)
ClusterMember build()
```

### ClusterNodeConfig

`public final class ClusterNodeConfig`　一份不可变的 cluster 节点配置. 通过 builder() 构建, 字段全部 final, build 阶段全量校验.

**字段 / 常量**

```java
static final long DEFAULT_SNAPSHOT_INTERVAL_MS = 3_600_000L  // snapshotIntervalMs() 默认值: 1 小时.
static final String DEFAULT_SNAPSHOT_CHANNEL = "aeron:ipc?alias=snapshot|term-length=8m"  // snapshotChannel() 默认值.
static final int MIN_ARCHIVE_RETAIN_SNAPSHOT_COUNT = 3  // archiveRetainSnapshotCount() 启用时的最小值.
static final long DEFAULT_ARCHIVE_RETENTION_INTERVAL_MS = 3_600_000L  // archiveRetentionIntervalMs() 默认值: 1 小时.
```

**方法**

```java
int memberId()
ClusterTopology topology()
ClusterStateMachine<?> stateMachine()
CodecRegistry codecRegistry()
Path aeronDir()
Path archiveDir()
Path clusterDir()
long snapshotIntervalMs()  // 周期快照间隔 (毫秒), 默认 DEFAULT_SNAPSHOT_INTERVAL_MS (1 小时). > 0: leader 每隔该时长 请求一次集群快照 (压实 raft log、加速重启/追赶)…
String snapshotChannel()  // Snapshot publication 的完整 Aeron channel URI, 同时作用于 ConsensusModule 与 ClusteredServiceContainer…
List<SnapshotQuietWindow> snapshotQuietWindows()  // 周期快照静默窗口列表 (本地时区); 落在任一窗口内的周期触发被跳过 (打点 onSnapshotSkipped). 手动触发 (triggerSnapshot()) 不受影响.
Path snapshotExtDir()  // 外置快照文件目录 (异步快照的大块状态载体); null = 默认 clusterDir/snapshots. 见 resolvedSnapshotExtDir().
Path resolvedSnapshotExtDir()  // 外置快照文件目录的最终路径 (处理默认值).
int snapshotExtRetainCount()  // 外置快照文件保留份数 (完整写出的); 超出的旧文件在新快照写出成功后清理. 默认 2, 必须 >= 1.
int archiveSegmentFileLength()  // Archive recording 段文件长度 (字节) 的原始配置值; <= 0 表示 auto. 实际生效值见 resolvedArchiveSegmentFileLength().
int resolvedArchiveSegmentFileLength()  // 实际传给 Archive 的段文件长度. archiveSegmentFileLength() 未显式配置时 auto 取快照流的 term length (默认 channel 下即 8MB).
int archiveRetainSnapshotCount()  // 保留的快照组数; 0 (默认) 禁用 archive 保留清理, 启用时必须 >= MIN_ARCHIVE_RETAIN_SNAPSHOT_COUNT.
long archiveRetentionIntervalMs()  // archive 保留清理的检查间隔 (毫秒), 默认 DEFAULT_ARCHIVE_RETENTION_INTERVAL_MS (1 小时)…
long leaderHeartbeatTimeoutNs()
long shutdownTimeoutMs()
MediaDriverMode mediaDriverMode()
boolean deleteDirsOnStart()
boolean deleteDirsOnClose()
ClusterMetrics metrics()
ClusterClock clock()
RoleChangeListener roleChangeListener()
String idleStrategySpec()  // 节点 agent 线程的 idle 策略 spec 字符串 (见 IdleStrategyFactory.of); null = 用框架默认…
ClusterMember member()
static Builder builder()
static int parseSizeBytes(String name, String spec)  // 把 Aeron size 记法 ("8m" / "64k" / 纯字节数) 解析成 int 字节数; null / 空串 = 0.
```

#### ClusterNodeConfig.Builder

`public static final class Builder`

**方法**

```java
Builder memberId(int v)
Builder topology(ClusterTopology v)
Builder stateMachine(ClusterStateMachine<?> v)
Builder codecRegistry(CodecRegistry v)
Builder aeronDir(Path v)
Builder archiveDir(Path v)
Builder clusterDir(Path v)
Builder snapshotIntervalMs(long v)  // 见 snapshotIntervalMs(). <= 0 禁用周期快照.
Builder snapshotChannel(String v)  // 见 snapshotChannel(). null = DEFAULT_SNAPSHOT_CHANNEL.
Builder snapshotQuietWindows(List<String> specs)  // 见 snapshotQuietWindows(). spec 格式 "HH:mm-HH:mm", 支持跨午夜.
Builder snapshotExtDir(Path v)  // 见 snapshotExtDir(). null = clusterDir/snapshots.
Builder snapshotExtRetainCount(int v)  // 见 snapshotExtRetainCount(). 必须 >= 1.
Builder archiveSegmentFileLength(int v)  // 见 archiveSegmentFileLength(). <= 0 = auto (跟随快照流 term length).
Builder archiveSegmentFileLength(String spec)  // 同 archiveSegmentFileLength(int), 但接受 Aeron size 记法 ("8m" / "64k" / 纯字节数); null / 空串 = auto. 给配置来自文本的接入方直接透传用.
Builder archiveRetainSnapshotCount(int v)  // 见 archiveRetainSnapshotCount(). 0 = 禁用; 否则必须 >= MIN_ARCHIVE_RETAIN_SNAPSHOT_COUNT.
Builder archiveRetentionIntervalMs(long v)  // 见 archiveRetentionIntervalMs().
Builder leaderHeartbeatTimeoutNs(long v)
Builder shutdownTimeoutMs(long v)
Builder mediaDriverMode(MediaDriverMode v)
Builder deleteDirsOnStart(boolean v)
Builder deleteDirsOnClose(boolean v)
Builder metrics(ClusterMetrics v)
Builder clock(ClusterClock v)
Builder roleChangeListener(RoleChangeListener v)
Builder idleStrategySpec(String v)  // 见 idleStrategySpec().
ClusterNodeConfig build()
```

### ClusterTopology

`public final class ClusterTopology`　一份不可变的集群拓扑视图. 节点启动后不允许动态变更 -- Aeron Cluster 当前版本对动态成员 变更支持不完善, 框架层面直接禁止以减少踩坑面.

**方法**

```java
static ClusterTopology of(ClusterMember... members)
static ClusterTopology of(List<ClusterMember> members)
List<ClusterMember> members()
int size()
Optional<ClusterMember> find(int memberId)
ClusterMember require(int memberId)
String ingressEndpoints()  // Aeron Cluster client 期望的 ingress endpoints 字符串: "0=host:port,1=host:port,..."
String clusterMembersString()  // Aeron Cluster ConsensusModule 期望的 cluster members 字符串: ",|,|...", 其中 endpoints 是 5 元组逗号分隔.
String toString()
boolean equals(Object o)
int hashCode()
```

### MediaDriverMode

`public enum MediaDriverMode`　节点用的 Aeron MediaDriver 工作模式.

**枚举常量**

```java
EMBEDDED
EXTERNAL
```

### SnapshotQuietWindow

`public final class SnapshotQuietWindow`　周期快照的"静默窗口": 落在窗口内的周期触发被跳过 (手动触发 / 优雅关闭快照不受影响).

**方法**

```java
static SnapshotQuietWindow parse(String spec)  // 解析 "HH:mm-HH:mm"; 非法格式抛 ClusterConfigException.
static List<SnapshotQuietWindow> parseAll(List<String> specs)  // 批量解析; null / 空列表返回不可变空列表.
boolean contains(LocalTime time)  // time 是否落在本窗口内 (半开区间, 支持跨午夜).
LocalTime start()
LocalTime end()
String toString()
```

## 包 `com.mcst.aeron.cluster.core.exception`

### ClusterClientException

`public class ClusterClientException extends ClusterException`　客户端连接 / 重连 / 响应等待相关的失败.

**构造器**

```java
ClusterClientException(String message)
ClusterClientException(String message, Throwable cause)
```

### ClusterCommandException

`public class ClusterCommandException extends ClusterException`　命令处理失败 (codec 解码失败 / 帧头损坏 / 业务状态机抛错被框架包装).

**构造器**

```java
ClusterCommandException(String message)
ClusterCommandException(String message, Throwable cause)
```

### ClusterConfigException

`public class ClusterConfigException extends ClusterException`　配置非法 (字段缺失 / 值越界 / 拓扑冲突 等).

**构造器**

```java
ClusterConfigException(String message)
ClusterConfigException(String message, Throwable cause)
```

### ClusterException

`public class ClusterException extends RuntimeException`　cluster SDK 全部异常基类. 与 broadcast SDK 的 AeronMqException 物理隔离, 维持"两个仓库异常树独立"的契约 (见 docs/Cluster独立项目规划.md §6).

**构造器**

```java
ClusterException(String message)
ClusterException(String message, Throwable cause)
ClusterException(Throwable cause)
```

### ClusterSnapshotException

`public class ClusterSnapshotException extends ClusterException`　snapshot 写入 / 加载阶段的失败 (版本不兼容, 写超时, 反序列化错).

**构造器**

```java
ClusterSnapshotException(String message)
ClusterSnapshotException(String message, Throwable cause)
```

### ClusterTimeoutException

`public class ClusterTimeoutException extends ClusterClientException`　客户端 send-and-await 等待响应超时.

**构造器**

```java
ClusterTimeoutException(String message)
ClusterTimeoutException(String message, Throwable cause)
```

## 包 `com.mcst.aeron.cluster.core.frame`

### ClusterFrameHeader

`public final class ClusterFrameHeader`　解码后的 cluster 帧头, 可复用以避免热路径分配.

**方法**

```java
byte version()
byte frameType()
byte codecId()
byte flags()
long correlationId()
int payloadLength()
int payloadOffset()
int frameLength()
boolean isCommand()
boolean isResponse()
boolean isEgressEvent()
boolean isLeaderHint()
void reset()
```

### ClusterFrameProtocol

`public final class ClusterFrameProtocol`　cluster session 上承载应用层帧的字节布局.

**字段 / 常量**

```java
static final int MAGIC = 0x4C434541  // wire 上 'A','E','C','L'; LE 视角 0x4C434541.
static final byte VERSION_V1 = 0x01
static final int OFFSET_MAGIC = 0
static final int OFFSET_VERSION = 4
static final int OFFSET_FRAME_TYPE = 5
static final int OFFSET_CODEC = 6
static final int OFFSET_FLAGS = 7
static final int OFFSET_CORRELATION_ID = 8
static final int OFFSET_PAYLOAD_LEN = 16
static final int OFFSET_PADDING = 20
static final int HEADER_LENGTH = 24
```

**方法**

```java
static int frameLength(int payloadLen)
static int writeHeader(MutableDirectBuffer dst, int offset, byte frameType, byte codecId, long correlationId, int payloadLen)  // 写入帧头. 调用方负责接着把 payload 写到 offset + HEADER_LENGTH 起始处.
static void readHeader(DirectBuffer src, int offset, int length, ClusterFrameHeader out)  // 校验并解析帧头到 ClusterFrameHeader.
```

### ClusterFrameType

`public final class ClusterFrameType`　cluster wire 帧类型常量.

**字段 / 常量**

```java
static final byte COMMAND = 0x01
static final byte RESPONSE = 0x02
static final byte EGRESS_EVENT = 0x03
static final byte LEADER_HINT = 0x04
```

**方法**

```java
static boolean isKnown(byte type)
static String name(byte type)
```

## 包 `com.mcst.aeron.cluster.core.idempotence`

### AbstractIdempotentStateMachine

`public abstract class AbstractIdempotentStateMachine<C> implements ClusterStateMachine<C>`　提供"客户端请求去重"的状态机基类 —— 网络抖动 / 重连下客户端"至少一次"重发的正确性底座.

**字段 / 常量**

```java
static final long NOT_TRACKED = -1L  // clientIdOf 返回此值表示命令不参与去重.
```

**方法**

```java
abstract long clientIdOf(C command)  // 取命令所属的业务级 client id. 返回 NOT_TRACKED 表示该命令不去重 (照常 apply, 不缓存). 必须是跨客户端重连稳定的标识, 不能用 Aeron session id.
abstract long requestIdOf(C command)  // 取命令在其 client 内单调递增的 request id; 仅当 clientIdOf != NOT_TRACKED 时有意义.
abstract void applyCommand(ClusterSession session, C command, ClusterContext ctx)  // 业务逻辑入口 (替代 onCommand). 在其中照常 session.respond(...).
abstract int snapshotVersion()  // 业务 snapshot schema 版本; 改了 writeState 结构必须 +1.
abstract void writeState(SnapshotWriter writer)  // 写业务 in-memory 状态 (不要写 header).
abstract void readState(SnapshotReader reader, int storedVersion)  // 读业务 in-memory 状态 (不要读 header). 此时 reader 已越过去重表 blob.
final void onCommand(ClusterSession session, C command, ClusterContext ctx)
final void takeSnapshot(SnapshotWriter writer)
final void loadSnapshot(SnapshotReader reader)
void onDuplicateSuppressed(long clientId, long requestId)  // 命中重试并回放缓存响应时回调 (默认 no-op). 业务可重写以接 metrics.
void onStaleDropped(long clientId, long requestId)  // 丢弃过期重试时回调 (默认 no-op).
final void forgetClient(long clientId)  // 主动遗忘某个 client 的去重记录 (该 client 永久离线时回收内存). 仅在状态机线程调用.
final int trackedClientCount()  // 当前去重表跟踪的 client 数量.
final long duplicatesSuppressed()  // 自启动 / 上次 snapshot 以来被去重 (回放缓存) 的请求数.
final long staleDropped()  // 自启动 / 上次 snapshot 以来被丢弃的过期重试数.
```

## 包 `com.mcst.aeron.cluster.core.internal`

### ClusterDirLayout

`public final class ClusterDirLayout`　工具类: 按 memberId 推导 aeron / archive / cluster 三个目录的标准路径, 以及做创建 / 删除的 IO 辅助.

**方法**

```java
static ClusterDirLayout under(Path base, int memberId)
static ClusterDirLayout of(Path aeronDir, Path archiveDir, Path clusterDir, int memberId)
Path base()
int memberId()
Path aeronDir()
Path archiveDir()
Path clusterDir()
ClusterDirLayout createDirs()
ClusterDirLayout deleteIfExists()
```

### ClusterMarkFileHelper

`public final class ClusterMarkFileHelper`　处理 Aeron Cluster / Archive / Driver 留下的 mark file (i.e. *.dat)…

**方法**

```java
static boolean hasMarkFile(Path dir)
static int cleanStaleMarkFiles(Path dir)  // 删除 dir 下全部 mark file (即 *.dat). 仅在确认对应 Aeron 进程已退出时调用, 否则会破坏正在运行的服务.
static boolean stableShutdown(Path dir, long timeoutMs)  // 同步等待 mark file 消失. 在 close 后立即重启同一目录时调一次, 避免新进程被旧 mark file 阻塞.
```

### EmbeddedClusterNode

`public final class EmbeddedClusterNode implements ClusterNode`　嵌入式集群节点: 同一 JVM 里启动 MediaDriver + Archive + ConsensusModule + ClusteredServiceContainer.

**构造器**

```java
EmbeddedClusterNode(ClusterNodeConfig config)
```

**方法**

```java
static ClusterNode launch(ClusterNodeConfig config)
void start()
void close()
int memberId()
ClusterRole role()
boolean triggerSnapshot()
CompletableFuture<StateAuditView> captureAuditView()
boolean isRunning()
Path aeronDir()
Path clusterDir()
```

### ExternalClusterNode

`public final class ExternalClusterNode implements ClusterNode`　外挂模式集群节点: 业务方已经在 host 上起了独立的 MediaDriver 进程 (通常多个 Aeron 服务共享), 框架只负责 Archive + ConsensusModule + ClusteredServ…

**构造器**

```java
ExternalClusterNode(ClusterNodeConfig config)
```

**方法**

```java
static ClusterNode attach(ClusterNodeConfig config)
void start()
void close()
int memberId()
ClusterRole role()
boolean triggerSnapshot()
CompletableFuture<StateAuditView> captureAuditView()
boolean isRunning()
Path aeronDir()
Path clusterDir()
```

### FrameworkClusteredService

`public final class FrameworkClusteredService implements ClusteredService`　把业务 ClusterStateMachine 适配到 Aeron 原生的 ClusteredService.

**方法**

```java
ClusterRole lastObservedRole()  // Lock-free getter, 供 EmbeddedClusterNode.role() 任意线程读.
CompletableFuture<StateAuditView> captureAuditView()  // 从任意线程提交一致性审计视图捕获请求。真正的捕获会在 Agent 线程执行， Future 的完成则切到节点专属线程，避免调用方回调阻塞 Agent。
void onStart(Cluster cluster, Image snapshotImage)
void onSessionOpen(ClientSession session, long timestamp)
void onSessionClose(ClientSession session, long timestamp, io.aeron.cluster.codecs.CloseReason closeReason)
void onSessionMessage(ClientSession session, long timestamp, DirectBuffer buffer, int offset, int length, Header header)
void onTimerEvent(long correlationId, long timestamp)
int doBackgroundWork(long nowNs)
void onTakeSnapshot(ExclusivePublication snapshotPublication)
void onRoleChange(Cluster.Role newRole)
void onTerminate(Cluster cluster)
void onNewLeadershipTermEvent(long leadershipTermId, long logPosition, long timestamp, long termBaseLogPosition, int leaderMemberId, int logSessionId, java.util.concurrent.TimeUnit timeUnit, int appVersion)
```

### IdleStrategyFactory

`public final class IdleStrategyFactory`　集中创建 Aeron / Agrona IdleStrategy 实例的工厂.

**方法**

```java
static IdleStrategy defaultStrategy()  // 工厂默认: 后退式三段策略, 兼顾延迟与 CPU 友好.
static IdleStrategy of(String spec)  // 按字符串名构造 IdleStrategy. 名字格式 "BACKOFF", "SLEEP_NS:1000" 等 (冒号后跟可选参数).
```

## 包 `com.mcst.aeron.cluster.core.lifecycle`

### ClusterNode

`public interface ClusterNode extends AutoCloseable`　集群节点门面. 业务方持有该接口的引用即可控制节点生命周期 -- 框架内部隐藏了 Aeron MediaDriver / Archive / ConsensusModule / ClusteredServiceConta…

**方法**

```java
static ClusterNode launch(ClusterNodeConfig config)  // 按 config.mediaDriverMode() 选择 EmbeddedClusterNode (EMBEDDED) 或 ExternalClusterNode (EXTERNAL) 并启动…
void start()  // 启动节点. 启动过程包括: (EMBEDDED 模式) 起 ClusteredMediaDriver, 含 Driver + Archive + ConsensusModule…
void close()  // 优雅关闭节点 (按 ServiceContainer / ConsensusModule / Archive / Driver 的反向顺序).
int memberId()  // 当前节点 member id (来自 config).
ClusterRole role()  // 当前节点角色; 节点未启动 / 已关闭时返回 UNKNOWN.
boolean triggerSnapshot()  // 程序化手动触发一次集群快照 (与 ClusterTool snapshot 等价), 供运维错峰使用.
default CompletableFuture<StateAuditView> captureAuditView()  // 在集群 Agent 线程捕获一个一致、只读的业务状态视图。
boolean isRunning()  // 节点是否已成功启动且未关闭.
Path aeronDir()  // aeron driver dir (host 系统路径).
Path clusterDir()  // cluster dir (含 raft log / mark file / pending snapshot).
```

## 包 `com.mcst.aeron.cluster.core.metrics`

### ClusterMetrics

`public interface ClusterMetrics`　Cluster SDK 的指标采集 SPI. 默认实现 NoopClusterMetrics, 业务方按需注入自家实现接 Prometheus / OTel.

**方法**

```java
static ClusterMetrics noop()
void onCommandCommitted(int codecId, int payloadBytes, long processLatencyNs)  // Raft 已提交一条命令, 状态机已完成处理 (含 codec 解码 + onCommand 回调).
void onCommandRejected(int codecId, String reason)  // 命令被拒绝 (codec id 未声明 / frame 校验失败 / 状态机抛错并被框架 catch).
void onSnapshotTaken(long bytes, long durationNs)
void onSnapshotLoaded(long bytes, long durationNs)
default void onSnapshotTaken(long bytes, long durationNs, long logPosition)  // 快照写出完成 (含 logPosition 维度). 同步快照在 agent 线程回调; 异步快照在框架后台 快照写出线程回调 (此时 agent 线程早已恢复处理命令).
default void onSnapshotLoaded(long bytes, long durationNs, long logPosition)  // 快照加载完成 (含 logPosition 维度; 同步快照恢复时 logPosition 传 -1). 默认委托给两参版本.
default void onSnapshotRequested()  // 周期触发器成功向 ConsensusModule 请求了一次快照 (仅 leader; 在触发器边车线程回调).
default void onSnapshotSkipped(String reason)  // 一次周期快照触发被跳过 (在触发器边车线程回调).
default void onSnapshotFailed(Throwable t, long logPosition)  // 快照失败 (同步: takeSnapshot 抛错; 异步: 捕获 / manifest 写出 / 后台文件写出失败). 默认委托给 onError(Throwable), 旧实现无需改动.
default void onArchiveRetentionPurged(int snapshotGroups, long recordings, long segmentFiles)  // 一轮 archive 保留清理真的删掉了东西 (在保留清理边车线程回调; 无事可做的轮次不回调).
default void onArchiveRetentionSkipped(String reason)  // 一轮 archive 保留清理被跳过 (在保留清理边车线程回调).
void onRoleChange(ClusterRole previous, ClusterRole current, long termId)
void onSessionOpened(long sessionId)
void onSessionClosed(long sessionId, CloseReason reason)
void onRespondDropped(long sessionId, String reason)  // 在非 leader 节点上对 session 调用 respond 被静默丢弃.
void onTimerScheduled(long timerId)
void onTimerFired(long timerId)
void onTimerCancelled(long timerId)
void onClientSend(int codecId, int payloadBytes)
void onClientResponse(int codecId, int payloadBytes, long roundTripNs)
void onClientReconnect(int attempt)
void onError(Throwable t)
```

### InMemoryClusterMetrics

`public final class InMemoryClusterMetrics implements ClusterMetrics`　内存累加 metrics, 供单测 / IT 断言用 (不要用于生产观测).

**方法**

```java
void onCommandCommitted(int codecId, int payloadBytes, long processLatencyNs)
void onCommandRejected(int codecId, String reason)
void onSnapshotTaken(long bytes, long durationNs)
void onSnapshotTaken(long bytes, long durationNs, long logPosition)
void onSnapshotLoaded(long bytes, long durationNs)
void onSnapshotRequested()
void onSnapshotSkipped(String reason)
void onSnapshotFailed(Throwable t, long logPosition)
void onArchiveRetentionPurged(int snapshotGroups, long recordings, long segmentFiles)
void onArchiveRetentionSkipped(String reason)
void onRoleChange(ClusterRole previous, ClusterRole current, long termId)
void onSessionOpened(long sessionId)
void onSessionClosed(long sessionId, CloseReason reason)
void onRespondDropped(long sessionId, String reason)
void onTimerScheduled(long timerId)
void onTimerFired(long timerId)
void onTimerCancelled(long timerId)
void onClientSend(int codecId, int payloadBytes)
void onClientResponse(int codecId, int payloadBytes, long roundTripNs)
void onClientReconnect(int attempt)
void onError(Throwable t)
long commandCommitted()
long commandRejected()
long commandBytes()
long snapshotTaken()
long snapshotLoaded()
long snapshotBytes()
long snapshotRequested()
long snapshotSkipped()
long snapshotFailed()
long lastSnapshotLogPosition()
long archiveRetentionRuns()
long archiveRetentionGroups()
long archiveRetentionRecordings()
long archiveRetentionSegments()
long archiveRetentionSkipped()
long sessionsOpened()
long sessionsClosed()
long respondDropped()
long timersScheduled()
long timersFired()
long timersCancelled()
long clientSent()
long clientResponded()
long clientReconnects()
long errors()
ClusterRole currentRole()
long currentTerm()
Throwable lastError()
```

### NoopClusterMetrics

`public final class NoopClusterMetrics implements ClusterMetrics`　默认实现; 全空, 零分配.

**字段 / 常量**

```java
static final NoopClusterMetrics INSTANCE = new NoopClusterMetrics()
```

**方法**

```java
void onCommandCommitted(int codecId, int payloadBytes, long processLatencyNs)
void onCommandRejected(int codecId, String reason)
void onSnapshotTaken(long bytes, long durationNs)
void onSnapshotLoaded(long bytes, long durationNs)
void onRoleChange(ClusterRole previous, ClusterRole current, long termId)
void onSessionOpened(long sessionId)
void onSessionClosed(long sessionId, CloseReason reason)
void onRespondDropped(long sessionId, String reason)
void onTimerScheduled(long timerId)
void onTimerFired(long timerId)
void onTimerCancelled(long timerId)
void onClientSend(int codecId, int payloadBytes)
void onClientResponse(int codecId, int payloadBytes, long roundTripNs)
void onClientReconnect(int attempt)
void onError(Throwable t)
```

## 包 `com.mcst.aeron.cluster.core.role`

### ClusterRole

`public enum ClusterRole`　集群节点的当前角色, 由框架在 Raft 选主 / 角色切换时设置. 不直接复用上游 SBE codec, 避免业务代码强依赖 Aeron 内部包.

**枚举常量**

```java
UNKNOWN  // 角色未确定 (节点刚启动 / 适配层尚未收到第一次 onRoleChange).
FOLLOWER  // 跟随者: 只回放 Raft committed log, 不接受 client 命令.
CANDIDATE  // 候选者: 选举进行中, 短暂角色.
LEADER  // 领导者: 接受 client 命令并对状态机回调中的 ClusterSession.respond() 真正发出回执.
```

**方法**

```java
static ClusterRole fromAeronCode(int code)  // 把 Aeron 原生 cluster 角色 code (0=FOLLOWER, 1=CANDIDATE, 2=LEADER) 适配到本枚举.
boolean isLeader()
```

## 包 `com.mcst.aeron.cluster.core.session`

### CloseReason

`public enum CloseReason`　客户端会话关闭原因, 透传 Aeron Cluster 上游的会话关闭原因.

**枚举常量**

```java
CLIENT_ACTION  // 客户端主动 close.
TIMEOUT  // 心跳超时, 框架被动关闭.
SERVICE_ACTION  // 框架 / 业务方主动调 session.close().
UNKNOWN  // 兜底.
```

### SessionId

`public final class SessionId`　Cluster 会话 id 的 value object 形式. 内部就是 Aeron Cluster 分配的 long, 包一层主要是为了:

**字段 / 常量**

```java
static final long NONE_VALUE = -1L
static final SessionId NONE = new SessionId(NONE_VALUE)
```

**方法**

```java
static SessionId of(long value)
long value()
boolean isNone()
boolean equals(Object o)
int hashCode()
String toString()
```

## 包 `com.mcst.aeron.cluster.core.snapshot`

### SnapshotEntryHeader

`public final class SnapshotEntryHeader`　单条 snapshot entry 的 wire 头.

**字段 / 常量**

```java
static final byte ENTRY_TYPE_BYTES = 0
static final byte ENTRY_TYPE_CODEC_TYPED = 1
static final int OFFSET_ENTRY_TYPE = 0
static final int OFFSET_CODEC_ID = 1
static final int OFFSET_RESERVED = 2
static final int OFFSET_PAYLOAD_LEN = 4
static final int HEADER_LENGTH = 8
```

### SnapshotFileFormat

`public final class SnapshotFileFormat`　外置快照文件 (异步快照的大块状态载体) 的物理格式常量.

**字段 / 常量**

```java
static final int TRAILER_MAGIC = 0x58434541  // wire 上字节序: 'A','E','C','X' (0x41 0x45 0x43 0x58).
static final int TRAILER_VERSION = 1
static final int OFFSET_TRAILER_MAGIC = 0
static final int OFFSET_TRAILER_VERSION = 4
static final int OFFSET_PAYLOAD_LENGTH = 8
static final int OFFSET_LOG_POSITION = 16
static final int OFFSET_CRC32 = 24
static final int TRAILER_LENGTH = 32
static final String FILE_PREFIX = "snapshot-"
static final String FILE_SUFFIX = ".snap"
static final String TMP_SUFFIX = ".tmp"
static final String PENDING_SUFFIX = ".pending"
```

**方法**

```java
static String fileName(long logPosition)  // 外置快照文件的规范名: snapshot-.snap.
```

### SnapshotMagic

`public final class SnapshotMagic`　Snapshot stream 起始 magic + 版本号常量, 详见 docs/Cluster协议规约.md.

**字段 / 常量**

```java
static final int MAGIC = 0x53434541  // wire 上字节序: 'A','E','C','S' (0x41 0x45 0x43 0x53).
static final byte FRAMEWORK_VERSION_V1 = 0x01
static final byte FRAMEWORK_VERSION_V2_EXTERNAL = 0x02  // 异步快照 manifest 格式: Aeron 快照流里只有一个 manifest entry (logPosition + 外置文件引用), 业务状态由框架后台线程写到外置快照文件 (见 SnapshotFileFor…
static final int OFFSET_MAGIC = 0
static final int OFFSET_FRAMEWORK_VERSION = 4
static final int OFFSET_BUSINESS_VERSION = 5
static final int OFFSET_RESERVED = 6
static final int STREAM_HEADER_LENGTH = 8
```

## 包 `com.mcst.aeron.cluster.core.timer`

### ClusterTimer

`public interface ClusterTimer`　集群定时器的最小接口. 框架的 ClusterContext 直接 extends 本接口, 业务方因此可以 把"只用 timer"的代码 (例如分片到独立类的子模块) 单独依赖 ClusterTimer, 而不必拖一整…

**方法**

```java
boolean scheduleTimer(long timerId, long deadlineMs)  // 注册一个定时器, 到期后框架会回调 ClusterStateMachine.onTimer(timerId, ctx).
boolean cancelTimer(long timerId)  // 取消已注册的定时器.
```

## 包 `com.mcst.aeron.cluster.core.wire`

### ClusterCommandFrameEncoder

`public final class ClusterCommandFrameEncoder`　把业务命令编码成 cluster wire COMMAND 帧.

**方法**

```java
static <T> int encode(MutableDirectBuffer buf, int offset, long correlationId, Codec<T> codec, T value)  // 用 codec 编码 value 并写入 COMMAND 帧.
static int encodeBytes(MutableDirectBuffer buf, int offset, long correlationId, byte[] payload)  // 直接以 RAW codec id 把字节流写入 COMMAND 帧 (调试 / 自定义场景).
```

### ClusterEgressFrameEncoder

`public final class ClusterEgressFrameEncoder`　把 Leader 主动推送的事件编码成 cluster wire EGRESS_EVENT 帧.

**方法**

```java
static <T> int encode(MutableDirectBuffer buf, int offset, Codec<T> codec, T value)
static int encodeBytes(MutableDirectBuffer buf, int offset, byte[] payload)
```

### ClusterFrameDecoder

`public final class ClusterFrameDecoder`　通用 cluster wire 帧解码 helper. Command / Response / Egress 三种帧的字节布局完全相同, 解码侧只需根据 frame_type 分发即可, 因此用单个 decoder 即…

**方法**

```java
static void decodeHeader(DirectBuffer src, int offset, int length, ClusterFrameHeader out)  // 校验并解析帧头. out 会被原地填入, 调用方可复用对象以避免分配.
static byte[] copyPayload(DirectBuffer src, ClusterFrameHeader header)  // 取 payload 字节; 调用方可以再走 codec.decode.
static <T> T decodePayload(DirectBuffer src, ClusterFrameHeader header, CodecRegistry registry)  // 按 header 携带的 codec id 在 registry 中查 codec 并解码 payload.
static <T> T decodePayload(DirectBuffer src, ClusterFrameHeader header, Codec<T> codec)  // 显式传入期望 codec, 校验 wire 上的 codec id 一致后解码.
static boolean isCommand(ClusterFrameHeader h)  // 便利 typed 别名, 便于业务读 RESPONSE / EGRESS 帧时不必重复判 frame_type.
static boolean isResponse(ClusterFrameHeader h)
static boolean isEgressEvent(ClusterFrameHeader h)
```

### ClusterResponseFrameEncoder

`public final class ClusterResponseFrameEncoder`　把命令处理结果编码成 cluster wire RESPONSE 帧.

**方法**

```java
static <T> int encode(MutableDirectBuffer buf, int offset, long correlationId, Codec<T> codec, T value)
static int encodeBytes(MutableDirectBuffer buf, int offset, long correlationId, byte[] payload)
```

## 包 `com.mcst.aeron.cluster.spring.actuator`

### ClusterHealthIndicator

`public final class ClusterHealthIndicator implements HealthIndicator`　Actuator HealthIndicator: 同时关注节点角色与客户端连接状态.

**构造器**

```java
ClusterHealthIndicator(ObjectProvider<ClusterNode> nodeProvider, ObjectProvider<ClusterClient> clientProvider)
```

**方法**

```java
Health health()
```

## 包 `com.mcst.aeron.cluster.spring.annotation`

### ClusterEventListener

`public @interface ClusterEventListener`　注解：`@Target(ElementType.METHOD)` `@Retention(RetentionPolicy.RUNTIME)` `@Documented`　方法级注解, 把任意 bean 上的方法挂到 ClusterClient 的 egress 事件回调链上.

**方法**

```java
Event value() default Event.EGRESS
```

### ClusterStateMachineBean

`public @interface ClusterStateMachineBean`　注解：`@Target(ElementType.TYPE)` `@Retention(RetentionPolicy.RUNTIME)` `@Documented` `@Component`　语义化注解, 标在业务方实现的 ClusterStateMachine 类上, 等价 @Component 但语义更清楚.

**方法**

```java
@AliasFor(annotation = Component.class) String value() default ""
```

## 包 `com.mcst.aeron.cluster.spring.autoconfig`

### ClusterActuatorAutoConfiguration

`public class ClusterActuatorAutoConfiguration`　注解：`@Configuration(proxyBeanMethods = false)` `@ConditionalOnClass(HealthIndicator.class)`　只在 classpath 含 actuator (即 HealthIndicator) 时, 才把 ClusterHealthIndicator 装为 bean…

**方法**

```java
@Bean("aeronClusterHealth") @ConditionalOnMissingBean(name = "aeronClusterHealth") ClusterHealthIndicator aeronClusterHealth(ObjectProvider<ClusterNode> nodeProvider, ObjectProvider<ClusterClient> clientProvider)
```

### ClusterAutoConfiguration

`public class ClusterAutoConfiguration`　注解：`@Configuration(proxyBeanMethods = false)` `@AutoConfigureAfter(name = "com.mcst.aeron.spring.autoconfig.AeronCodecAutoConfiguration")` `@EnableConfigurationProperties(ClusterProperties.class)` `@Import({ ClusterNodeAutoConfiguration.class, ClusterClientAutoConfiguration.class, ClusterActuatorAutoConfiguration.class })`　cluster-spring-boot-starter 的主装配类.

**字段 / 常量**

```java
static final String CLUSTER_CODEC_REGISTRY_BEAN = "aeronClusterCodecRegistry"  // cluster 专用 registry 的 bean 名; 业务声明同名 bean 即可让 cluster 与其它组件使用不同的 registry.
```

**方法**

```java
@Bean(CLUSTER_CODEC_REGISTRY_BEAN) @org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean(CodecRegistry.class) CodecRegistry aeronClusterCodecRegistry()
@Bean @org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean static ClusterEventListenerBeanPostProcessor aeronClusterEventListenerBeanPostProcessor(ObjectProvider<ClusterMetrics> metricsProvider)  // 扫描业务 bean 上的 @ClusterEventListener 方法并适配为 ClusterEventListener bean…
@Bean @org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean ClusterLifecycle aeronClusterLifecycle(ObjectProvider<ClusterNode> nodeProvider, ObjectProvider<ClusterClient> clientProvider)  // 节点 + 客户端统一关闭顺序协调器, 先于 ClusterClientLifecycle stop, 内部先关 client 再关 node.
```

### ClusterClientAutoConfiguration

`public class ClusterClientAutoConfiguration`　注解：`@Configuration(proxyBeanMethods = false)` `@ConditionalOnProperty(prefix = "easyfk.config.aeron.cluster.client", name = "enabled", havingValue = "true")`　当 easyfk.config.aeron.cluster.client.enabled=true 时装配 ClusterClient bean.

**方法**

```java
@Bean(destroyMethod = "close") @ConditionalOnMissingBean ClusterClient aeronClusterClient(ClusterProperties props, BeanFactory beanFactory, ObjectProvider<CodecRegistry> codecRegistries, ObjectProvider<ClusterMetrics> metricsProvider)
@Bean @ConditionalOnMissingBean ClusterClientLifecycle aeronClusterClientLifecycle(ClusterClient client, ObjectProvider<ClusterEventListener> listenersProvider)
```

### ClusterNodeAutoConfiguration

`public class ClusterNodeAutoConfiguration`　注解：`@Configuration(proxyBeanMethods = false)` `@ConditionalOnProperty(prefix = "easyfk.config.aeron.cluster.node", name = "enabled", havingValue = "true")` `@ConditionalOnBean(ClusterStateMachine.class)`　当 easyfk.config.aeron.cluster.node.enabled=true 且 classpath / 容器内存在 ClusterStateMachine bean 时, 装配 ClusterNode…

**方法**

```java
@Bean(destroyMethod = "close") @ConditionalOnMissingBean ClusterNode aeronClusterNode(ClusterProperties props, ClusterStateMachine<?> stateMachine, BeanFactory beanFactory, ObjectProvider<CodecRegistry> codecRegistries, ObjectProvider<ClusterMetrics> metricsProvider, ObjectProvider<RoleChangeListener> roleChangeListenerProvider, ObjectProvider<ClusterClock> clockProvider)
```

## 包 `com.mcst.aeron.cluster.spring.properties`

### ClusterProperties

`public class ClusterProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.aeron.cluster")`　easyfk.config.aeron.cluster.* 配置入口.

**字段 / 常量**

```java
final NodeProperties node = new NodeProperties()
final ClientProperties client = new ClientProperties()
final ShutdownProperties shutdown = new ShutdownProperties()
```

#### ClusterProperties.ShutdownProperties

`public static class ShutdownProperties`　Lombok：`@Data`

**字段 / 常量**

```java
long markFileWaitMs = 5_000L  // 当前版本未接线, 设置无效; 关闭等待只认 node.shutdown-timeout-ms.
```

#### ClusterProperties.NodeProperties

`public static class NodeProperties`　Lombok：`@Data`

**字段 / 常量**

```java
boolean enabled = false  // 是否装配 ClusterNode bean.
int memberId = -1  // 本节点 memberId, 必须落在 topology 内.
MediaDriverMode mediaDriverMode = MediaDriverMode.EMBEDDED  // MediaDriver 工作模式; EMBEDDED 框架自起 driver, EXTERNAL 复用业务方已起的 driver dir.
String aeronDir  // Aeron driver dir; 留空则默认 ${java.io.tmpdir}/aeron-cluster-/aeron.
String archiveDir  // Archive dir; 留空则默认 ${java.io.tmpdir}/aeron-cluster-/archive.
String clusterDir  // Cluster dir; 留空则默认 ${java.io.tmpdir}/aeron-cluster-/cluster.
long snapshotIntervalMs = ClusterNodeConfig.DEFAULT_SNAPSHOT_INTERVAL_MS  // 周期快照间隔; 0 = 禁用 (仅 ClusterTool / 优雅关闭触发). 别配到分钟级, 见手册 §9.3.
String snapshotChannel  // Snapshot publication 的完整 Aeron channel URI; 留空 = ClusterNodeConfig.DEFAULT_SNAPSHOT_CHANNEL (term-length=8m)…
List<String> snapshotQuietWindows = new ArrayList<>()  // 周期快照静默窗口列表, spec 格式 "HH:mm-HH:mm" (本地时区, 支持跨午夜); 窗口内不触发周期快照.
String snapshotExtDir  // 外置快照文件目录 (异步快照); 留空 = clusterDir/snapshots.
int snapshotExtRetainCount = 2  // 外置快照文件保留份数, 必须 >= 1.
String archiveSegmentFileLength  // Archive recording 段文件长度, Aeron size 记法 ("4m" / "65536"); 留空 = auto, 跟随 snapshot-channel 的 term-length (默认即 8m)…
int archiveRetainSnapshotCount = 0  // 保留的快照组数; 0 = 禁用 archive 保留清理 (archiveDir 会无界增长), 启用时必须 >= 3. Aeron 开源版不会自动删除旧快照 recording, 见手册 §9.3.
long archiveRetentionIntervalMs = ClusterNodeConfig.DEFAULT_ARCHIVE_RETENTION_INTERVAL_MS  // archive 保留清理的检查间隔; 仅 archive-retain-snapshot-count > 0 时生效.
long leaderHeartbeatTimeoutNs = 10_000_000_000L
long shutdownTimeoutMs = 10_000L
boolean deleteDirsOnStart = false
boolean deleteDirsOnClose = false
String idleStrategy  // Aeron agent idle 策略 spec (见 IdleStrategyFactory.of); 留空 = 框架默认 (BACKOFF).
List<TopologyMember> topology = new ArrayList<>()  // 节点拓扑, 全集群必须一致, 加入集群后不允许动态变更.
```

#### ClusterProperties.ClientProperties

`public static class ClientProperties`　Lombok：`@Data`

**字段 / 常量**

```java
boolean enabled = false  // 是否装配 ClusterClient bean.
String ingressEndpoints  // 全部 ingress endpoints, 形如 "0=host:port,1=host:port,..." 不需要业务方关心谁是 leader.
String egressChannel = "aeron:udp?endpoint=localhost:0"  // 客户端用以接收响应的 channel.
String aeronDir  // 留空 = 客户端自起嵌入式 MediaDriver; 非空 = 连业务方已存在的 driver dir.
long responseTimeoutMs = 3_000L
long connectTimeoutMs = 10_000L
long pollerIdleSleepNs = 1_000_000L
long keepAliveIntervalMs = 2_000L  // 保活间隔; 必须小于集群 session 空闲超时 (aeron.cluster.session.timeout, 默认 10s), 否则空闲 session 会被 CLOSED(TIMEOUT).
boolean enableBackgroundPoller = true
final ReconnectProperties reconnect = new ReconnectProperties()
```

#### ClusterProperties.ReconnectProperties

`public static class ReconnectProperties`　Lombok：`@Data`

**字段 / 常量**

```java
Strategy strategy = Strategy.NONE
long initialDelayMs = 200L
long maxDelayMs = 5_000L
double factor = 2.0
int maxAttempts = 10
```

##### ClusterProperties.ReconnectProperties.Strategy

`public enum Strategy`

**枚举常量**

```java
NONE
EXPONENTIAL_BACKOFF
```

#### ClusterProperties.TopologyMember

`public static class TopologyMember`　Lombok：`@Data`

**字段 / 常量**

```java
int memberId = -1
String ingress
String consensus
String log
String catchup
String archive
```

## 包 `com.mcst.aeron.cluster.spring.runtime`

### ClusterClientLifecycle

`public final class ClusterClientLifecycle implements SmartLifecycle`　用 Spring SmartLifecycle 控制 connect() 的时机, 并把容器内所有 ClusterEventListener bean wire 到 client 上.

**字段 / 常量**

```java
static final int LATE_PHASE = Integer.MAX_VALUE - 1000  // 比默认 phase 大, 保证业务 bean 都 ready 后再 connect.
```

**构造器**

```java
ClusterClientLifecycle(ClusterClient client, ObjectProvider<ClusterEventListener> listenersProvider)
```

**方法**

```java
void start()
void stop()
boolean isRunning()
int getPhase()
```

### ClusterEventListenerBeanPostProcessor

`public final class ClusterEventListenerBeanPostProcessor implements BeanPostProcessor, ClusterEventListener`　扫描容器内所有 bean 的方法, 把标注 ClusterEventListener 的方法收集为对应类型的回调, 自身实现 ClusterEventListener, 在容器内作为一个 listener bean 注册…

**构造器**

```java
ClusterEventListenerBeanPostProcessor()  // 默认构造: 不接 metrics, 业务方法异常仅打 WARN log. 仅 Spring 自动装配在 metrics bean 缺失时使用.
ClusterEventListenerBeanPostProcessor(ObjectProvider<ClusterMetrics> metricsProvider)
```

**方法**

```java
Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException
void onEgressEvent(int codecId, DirectBuffer buffer, int offset, int length)
void onNewLeader(long clusterSessionId, long leadershipTermId, int newLeaderMemberId)
void onDisconnected()
void onReconnected(int attempts)
List<String> registeredMethodNames()  // 供测试观察用.
```

### ClusterLifecycle

`public final class ClusterLifecycle implements SmartLifecycle`　节点 + 客户端的统一 shutdown 协调器.

**字段 / 常量**

```java
static final int SHUTDOWN_FIRST_PHASE = ClusterClientLifecycle.LATE_PHASE + 1000  // stop 阶段 SmartLifecycle 按 phase 倒序执行, 这里比 client lifecycle 大, 因此先 stop.
```

**构造器**

```java
ClusterLifecycle(ObjectProvider<ClusterNode> nodeProvider, ObjectProvider<ClusterClient> clientProvider)
```

**方法**

```java
void start()
void stop()
boolean isRunning()
int getPhase()
```

## 包 `com.mcst.aeron.cluster.test.extension`

### EmbeddedClusterExtension

`public final class EmbeddedClusterExtension implements AfterEachCallback`　JUnit5 @ExtendWith(EmbeddedClusterExtension.class) 注解的简单实现.

**方法**

```java
static void register(ExtensionContext ctx, EmbeddedSingleNodeCluster c)
static void register(ExtensionContext ctx, EmbeddedThreeNodeCluster c)
void afterEach(ExtensionContext ctx)
```

## 包 `com.mcst.aeron.cluster.test.fixture`

### ClusterClientFixture

`public final class ClusterClientFixture`　包装 ClusterClient 给测试代码用的 fixture: 加几个常用的 "await" 风格 helper, 让 IT 写起来更短.

**构造器**

```java
ClusterClientFixture(ClusterClient client)
```

**方法**

```java
ClusterClient client()
void awaitConnected(Duration timeout)  // 在 timeout 内反复检查 isConnected(), 若超时则抛 AssertionError.
<T, R> R sendAndAwaitSync(Codec<T> codec, T command, Codec<R> respCodec, Duration timeout)  // sendAndAwait 的同步版本: 等到 future complete 或超时.
<T> long sendUntilAccepted(Codec<T> codec, T command, Duration timeout)  // 反复 send 直到 publication position > 0 或超时. 给"客户端刚 connect 时偶尔 NOT_CONNECTED"场景兜底.
```

### EmbeddedSingleNodeCluster

`public final class EmbeddedSingleNodeCluster implements AutoCloseable`　单节点嵌入式集群: 一个 cluster member + 一个 cluster client, 全部跑在同一 JVM.

**方法**

```java
static EmbeddedSingleNodeCluster launch(ClusterStateMachine<?> stateMachine, CodecRegistry codecRegistry, Path baseDir)
static EmbeddedSingleNodeCluster launch(ClusterStateMachine<?> stateMachine, CodecRegistry codecRegistry, Path baseDir, long snapshotIntervalMs)  // 同 launch(ClusterStateMachine, CodecRegistry, Path), 但显式指定 snapshotIntervalMs (用于 IT 验证周期快照; <= 0 禁用).
ClusterNode node()
ClusterClient client()
InMemoryClusterMetrics metrics()
ClusterMetrics metricsAsSpi()
Path baseDir()
void close()
```

### EmbeddedThreeNodeCluster

`public final class EmbeddedThreeNodeCluster implements AutoCloseable`　三节点嵌入式集群: Raft 多数派 = 2/3, 用于演示真正的选主 / kill leader / catch-up 等场景.

**方法**

```java
static EmbeddedThreeNodeCluster launch(Supplier<? extends ClusterStateMachine<?>> stateMachineFactory, CodecRegistry codecRegistry, Path baseDir)
List<ClusterNode> nodes()
List<InMemoryClusterMetrics> metrics()
ClusterTopology topology()
ClusterClient client()
Path baseDir()
int currentLeaderMemberId()  // 找当前 leader, 没选出来时返回 -1.
void close()
```

### PortAllocator

`public final class PortAllocator`　自由端口分配器: 用 ServerSocket(0) 让 OS 分配一组互不重复的端口, 用于并发 IT 启动嵌入式集群时 避免端口冲突.

**方法**

```java
static int allocate()
static List<Integer> allocate(int n)  // 一次分配 n 个互不相同的端口.
```

## 包 `com.mcst.aeron.cluster.test.wait`

### ClusterAwait

`public final class ClusterAwait`　Awaitility 风格的语法糖, 把 cluster 常见的"等到某状态"封装成可读 API.

**方法**

```java
static void untilLeaderElected(List<ClusterNode> nodes)
static void untilLeaderElected(List<ClusterNode> nodes, Duration timeout)
static void untilConnected(ClusterClient client)
static void untilConnected(ClusterClient client, Duration timeout)
static void untilCommittedAtLeast(InMemoryClusterMetrics metrics, long n)
static void untilCommittedAtLeast(InMemoryClusterMetrics metrics, long n, Duration timeout)
static void untilSnapshotTaken(InMemoryClusterMetrics metrics)
static void untilTrue(String label, BooleanSupplier condition, Duration timeout)
```
