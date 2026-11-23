# etcd-cluster API 签名速查（easyfk 3.5.16）

> 坐标：`com.mcst:etcd-cluster-api、etcd-cluster-core、etcd-cluster-spring-boot-starter`　源码：`etcd-cluster/etcd-cluster-api`、`etcd-cluster/etcd-cluster-core`、`etcd-cluster/etcd-cluster-spring-boot-starter`
> 由 `scripts/gen-api.py` 从 51 个源文件自动提取，共 40 个类型、199 个方法/构造器、23 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/etcd-cluster-skill.md](../modules/etcd-cluster-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 配置项（@ConfigurationProperties）

### `easyfk.config.cluster` ← ClusterProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `enabled` | `boolean` | `true` | 是否启用（false 时不装配 ClusterClient bean）。 |
| `backend` | `String` | `—` | 后端：etcd / noop。留空时按是否配置 endpoints 自动选择。 |
| `endpoints` | `List<String>` | `new ArrayList<>()` | etcd endpoints，如 http://127.0.0.1:2379。为空则回落到 NoOp（单机零回归）。 |
| `username` | `String` | `—` |  |
| `password` | `String` | `—` |  |
| `namespace` | `String` | `""` | 全局 key 命名空间前缀。 |
| `lease-ttl` | `Duration` | `Duration.ofSeconds(5)` | 默认 lease TTL（文档 C6 默认 5s）。 |
| `auto-recreate-session` | `boolean` | `true` | 会话丢失后是否自动重建（文档 C5 默认自动）。 |
| `request-timeout` | `Duration` | `Duration.ofSeconds(5)` |  |
| `callback-timeout` | `Duration` | `Duration.ofSeconds(3)` |  |
| `authority` | `String` | `—` |  |
| `tls` | `Tls` | `new Tls()` |  |


## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `etcd-cluster-spring-boot-starter` | `com.mcst.cluster.spring.ClusterAutoConfiguration` |

## 类型索引

- `com.mcst.cluster`：[ClusterClient](#clusterclient)、[ClusterClientLoader](#clusterclientloader)
- `com.mcst.cluster.config`：[ClusterConfig](#clusterconfig)
- `com.mcst.cluster.connection`：[ConnectionListener](#connectionlistener)、[ConnectionState](#connectionstate)
- `com.mcst.cluster.election`：[Fence](#fence)、[LeaderElection](#leaderelection)、[LeaderListener](#leaderlistener)、[Leadership](#leadership)
- `com.mcst.cluster.etcd`：[EtcdClusterClient](#etcdclusterclient)、[EtcdClusterClientFactory](#etcdclusterclientfactory)
- `com.mcst.cluster.etcd.metrics`：[ClusterMetrics](#clustermetrics)
- `com.mcst.cluster.etcd.support`：[Bytes](#bytes)、[ClusterExecutors](#clusterexecutors)、[EtcdFutures](#etcdfutures)、[Keys](#keys)
- `com.mcst.cluster.exception`：[ClusterClosedException](#clusterclosedexception)、[ClusterException](#clusterexception)、[ClusterTimeoutException](#clustertimeoutexception)、[FencingException](#fencingexception)、[NotLeaderException](#notleaderexception)
    [SessionLostException](#sessionlostexception)
- `com.mcst.cluster.noop`：[NoOpClusterClient](#noopclusterclient)、[NoOpClusterClientFactory](#noopclusterclientfactory)
- `com.mcst.cluster.registry`：[Advertisement](#advertisement)、[MembershipListener](#membershiplistener)、[Node](#node)、[NodeRegistry](#noderegistry)
- `com.mcst.cluster.session`：[Session](#session)、[SessionListener](#sessionlistener)、[SessionOptions](#sessionoptions)、[SessionState](#sessionstate)
- `com.mcst.cluster.spi`：[ClusterClientFactory](#clusterclientfactory)
- `com.mcst.cluster.spring`：[ClusterAutoConfiguration](#clusterautoconfiguration)、[ClusterProperties](#clusterproperties)
- `com.mcst.cluster.store`：[KeyValue](#keyvalue)、[SharedStore](#sharedstore)、[Watch](#watch)、[WatchEvent](#watchevent)、[WatchListener](#watchlistener)

## 包 `com.mcst.cluster`

### ClusterClient

`public interface ClusterClient extends AutoCloseable`　集群管理客户端——进程级入口。负责连接生命周期、会话创建、共享存储与连接降级感知。

**方法**

```java
String backend()  // 后端标识，如 "etcd" / "noop"。
Session newSession()  // 用默认会话选项创建一个新会话。
Session newSession(SessionOptions options)  // 用指定会话选项创建一个新会话。
SharedStore store(String prefix)  // 获取指定前缀下的共享存储视图。
void addConnectionListener(ConnectionListener listener)  // 注册连接状态监听器（降级感知）。
ConnectionState connectionState()  // 当前连接状态。
Object rawClient()  // 逃生口：返回底层后端原生客户端（etcd 实现下为 jetcd Client）。 高级/小众需求直接操作原生客户端，框架不为其扩 API。NoOp 实现返回 null。
void close()  // 关闭客户端，释放所有会话与连接资源。
```

### ClusterClientLoader

`public final class ClusterClientLoader`　通过 SPI（ServiceLoader）加载并创建 ClusterClient 的入口（纯 SDK，不依赖 Spring）。

**方法**

```java
static ClusterClient noop()  // 单机 NoOp 客户端（无需任何后端）。
static ClusterClient create(ClusterConfig config)
```

## 包 `com.mcst.cluster.config`

### ClusterConfig

`public final class ClusterConfig`　集群管理框架的不可变配置对象。

**方法**

```java
String backend()
List<String> endpoints()
String username()
String password()
String namespace()
Duration defaultLeaseTtl()
boolean autoRecreateSession()
Duration requestTimeout()
Duration callbackTimeout()
String tlsCaCertPath()
String tlsClientCertPath()
String tlsClientKeyPath()
String authority()
boolean hasEndpoints()
boolean tlsEnabled()
static Builder builder()
static ClusterConfig noop()  // 单机零回归配置（NoOp 后端，无 endpoints）。
String toString()
```

#### ClusterConfig.Builder

`public static final class Builder`

**方法**

```java
Builder backend(String backend)
Builder endpoints(List<String> endpoints)
Builder endpoints(String... endpoints)
Builder addEndpoint(String endpoint)
Builder username(String username)
Builder password(String password)
Builder namespace(String namespace)
Builder defaultLeaseTtl(Duration defaultLeaseTtl)
Builder autoRecreateSession(boolean autoRecreateSession)
Builder requestTimeout(Duration requestTimeout)
Builder callbackTimeout(Duration callbackTimeout)
Builder tlsCaCertPath(String tlsCaCertPath)
Builder tlsClientCertPath(String tlsClientCertPath)
Builder tlsClientKeyPath(String tlsClientKeyPath)
Builder authority(String authority)
ClusterConfig build()
```

## 包 `com.mcst.cluster.connection`

### ConnectionListener

`public interface ConnectionListener`　连接状态变化监听器（降级感知）。

**方法**

```java
default void onConnected()  // 连接（重新）建立。
default void onSuspended()  // 连接挂起（抖动 / 暂不可达，lease 未到期）。
default void onLost()  // 连接丢失（lease 过期 / 长时间不可达）。
```

### ConnectionState

`public enum ConnectionState`　与后端（etcd）的连接状态。降级语义的核心：连接挂起 ≠ 立即失主。

**枚举常量**

```java
CONNECTED  // 已连接，读写正常。
SUSPENDED  // 连接挂起（短暂抖动 / 网络不可达，但 lease 尚未到期）。 此期间不应立即让出 leader 身份；读操作可返回最后已知快照。
LOST  // 连接丢失（lease 已过期或长时间不可达）。挂在 session 上的资源应视为失效。
```

## 包 `com.mcst.cluster.election`

### Fence

`public interface Fence`　围栏（fencing）令牌句柄。用于在「旧主可能复活」的场景下守护对 etcd 内状态的写。

**方法**

```java
long token()  // 本次领导权的 fencing token（单调递增）。
boolean stillValid()  // token 当前是否仍然有效（即本实例仍持有领导权）。
boolean guardedPut(SharedStore store, String key, byte[] value)  // 守护写：仅当本 token 仍有效时，才把 value 写入 store 的 key。
default boolean guardedPut(SharedStore store, String key, String value)
default void guardedPutOrThrow(SharedStore store, String key, byte[] value)  // 同 guardedPut(SharedStore, String, byte[])，但 token 失效被拒时抛出异常而非返回 false。
default void guardedPutOrThrow(SharedStore store, String key, String value)
```

### LeaderElection

`public interface LeaderElection extends AutoCloseable`　一个选举位（由 Session.election(path) 创建，挂在该 session 上）。

**方法**

```java
void start()  // 开始竞选。非阻塞：当选/失主通过 LeaderListener 异步通知。 多次调用幂等。
boolean isLeader()  // 本实例当前是否为 leader。
Optional<Leadership> leadership()  // 本实例当前持有的领导权（非 leader 时为空）。
Optional<String> currentLeaderId()  // 当前集群 leader 的标识（无论是否为本实例；未知时为空）。
void addListener(LeaderListener listener)  // 注册监听器。已是 leader 时注册不会补发 onElected，请先注册再 start()。
Fence fence()  // 获取守护写所需的 fence 句柄。
void resign()  // 主动让位（若当前为 leader）。让位后可再次 start() 参与竞选。
String path()  // 选举路径。
void close()  // 停止竞选并释放资源（若为 leader 则先让位）。
```

### LeaderListener

`public interface LeaderListener`　选主状态变化监听器。

**方法**

```java
default void onElected(Leadership leadership)  // 本实例当选为 leader。
default void onRevoked()  // 本实例失去 leader 身份（主动让位 / lease 过期 / 连接丢失）。
```

### Leadership

`public record Leadership(String leaderId, long fencingToken, long leaseId)`　一次当选所代表的领导权快照。

**构造参数（record 组件）**

```java
String leaderId
long fencingToken
long leaseId
```

## 包 `com.mcst.cluster.etcd`

### EtcdClusterClient

`public final class EtcdClusterClient implements ClusterClient`　etcd 后端的 ClusterClient 实现。

**字段 / 常量**

```java
static final String BACKEND = "etcd"
```

**构造器**

```java
EtcdClusterClient(ClusterConfig config)
```

**方法**

```java
String backend()
Session newSession()
synchronized Session newSession(SessionOptions options)
synchronized SharedStore store(String prefix)
synchronized void addConnectionListener(ConnectionListener listener)
ConnectionState connectionState()
Object rawClient()
ClusterMetrics metrics()
void close()
```

### EtcdClusterClientFactory

`public final class EtcdClusterClientFactory implements ClusterClientFactory`　etcd 后端工厂（SPI）。

**方法**

```java
String backend()
boolean supports(ClusterConfig config)
ClusterClient create(ClusterConfig config)
```

## 包 `com.mcst.cluster.etcd.metrics`

### ClusterMetrics

`public final class ClusterMetrics`　关键路径指标（文档 §10 可观测）。轻量自带实现，可被外部采集导出。

**方法**

```java
void incrLeadershipChanges()
void incrKeepAliveFailures()
void incrWatchReconnects()
void incrSessionRecreations()
void incrConnectionSuspends()
void incrConnectionLosses()
void incrFencedWrites()
long leadershipChanges()
long keepAliveFailures()
long watchReconnects()
long sessionRecreations()
long connectionSuspends()
long connectionLosses()
long fencedWrites()
String toString()
```

## 包 `com.mcst.cluster.etcd.support`

### Bytes

`public final class Bytes`　ByteSequence 与 JDK 类型互转。

**方法**

```java
static ByteSequence of(String s)
static ByteSequence of(byte[] b)
static String str(ByteSequence bs)
static byte[] bytes(ByteSequence bs)
```

### ClusterExecutors

`public final class ClusterExecutors implements AutoCloseable`　框架专用线程资源：回调线程池 + 调度线程池。

**构造器**

```java
ClusterExecutors(String namePrefix, Duration callbackWarnAfter)
```

**方法**

```java
void dispatch(String name, Runnable callback)  // 在回调线程池执行用户回调，并对超时告警。
OrderedDispatcher newOrderedDispatcher()  // 创建一个「串行有序」分发器：同一分发器上提交的回调严格按提交顺序、一次一个地执行， 既隔离调用线程（不阻塞 jetcd watch 线程），又满足 WatchListener「事件按 key 维度有序」的承诺…
ScheduledExecutorService scheduler()
ExecutorService io()
void close()
```

#### ClusterExecutors.OrderedDispatcher

`public final class OrderedDispatcher`　串行有序分发器：用一个「在飞」标志保证同一分发器在任意时刻只有一个 drain 任务占用回调池线程， 队列按 FIFO 逐个执行，从而保证回调按提交顺序串行执行；空闲时不占用任何线程。

**方法**

```java
void dispatch(String name, Runnable callback)  // 按提交顺序串行执行 callback。
```

### EtcdFutures

`public final class EtcdFutures`　jetcd CompletableFuture 的同步等待与异常归一化工具。

**方法**

```java
static <T> T await(CompletableFuture<T> future, Duration timeout, String op)
```

### Keys

`public final class Keys`　etcd 键路径拼接 / 去前缀。框架自行管理命名空间前缀（不依赖 jetcd 的 namespace 选项）， 以保证 KV / 选举 / 注册 / 锁 全部一致。

**方法**

```java
static String join(String prefix, String key)  // 拼接前缀与子键，规整为单个 '/' 分隔。
static String strip(String prefix, String fullKey)  // 去掉 fullKey 的前缀，得到逻辑键。 与 join 对称：join("/state","flag") → "/state/flag"， strip 后应为 "flag"（而非 "/flag"）。
```

## 包 `com.mcst.cluster.exception`

### ClusterClosedException

`public class ClusterClosedException extends ClusterException`　在 ClusterClient / Session 等资源已关闭后继续调用时抛出。

**构造器**

```java
ClusterClosedException(String message)
```

### ClusterException

`public class ClusterException extends RuntimeException`　集群管理框架所有受检/非受检异常的根类型。

**构造器**

```java
ClusterException(String message)
ClusterException(String message, Throwable cause)
ClusterException(Throwable cause)
```

### ClusterTimeoutException

`public class ClusterTimeoutException extends ClusterException`　与后端（etcd）交互在给定时限内未完成时抛出。

**构造器**

```java
ClusterTimeoutException(String message)
ClusterTimeoutException(String message, Throwable cause)
```

### FencingException

`public class FencingException extends ClusterException`　fencing 守护写失败：fencing token 已失效（旧主复活被新主抢占）， 或守护写的事务前置条件不满足。由 Fence.guardedPutOrThrow 抛出。

**构造器**

```java
FencingException(String message)
FencingException(String message, Throwable cause)
```

### NotLeaderException

`public class NotLeaderException extends ClusterException`　当前实例不是 leader，却调用了仅 leader 可用的操作（如获取 Fence）时抛出。

**构造器**

```java
NotLeaderException(String message)
```

### SessionLostException

`public class SessionLostException extends ClusterException`　会话（租约）已丢失（lease 过期或被撤销）后，继续使用挂在该会话上的资源 （选举、注册、端点公布、锁等）时抛出。

**构造器**

```java
SessionLostException(String message)
SessionLostException(String message, Throwable cause)
```

## 包 `com.mcst.cluster.noop`

### NoOpClusterClient

`public final class NoOpClusterClient implements ClusterClient`　单机零回归客户端：不连接任何后端。

**字段 / 常量**

```java
static final String BACKEND = "noop"
```

**构造器**

```java
NoOpClusterClient()
NoOpClusterClient(String namespace)
```

**方法**

```java
String backend()
Session newSession()
synchronized Session newSession(SessionOptions options)
synchronized SharedStore store(String prefix)
synchronized void addConnectionListener(ConnectionListener listener)
ConnectionState connectionState()
Object rawClient()
synchronized void close()
```

### NoOpClusterClientFactory

`public final class NoOpClusterClientFactory implements ClusterClientFactory`　NoOp 后端工厂（SPI）。随 cluster-api 一起提供，保证「不配 etcd」时始终有可用实现。

**方法**

```java
String backend()
boolean supports(ClusterConfig config)
ClusterClient create(ClusterConfig config)
```

## 包 `com.mcst.cluster.registry`

### Advertisement

`public interface Advertisement extends AutoCloseable`　端点公布句柄（由 Session.advertise(key, value) 创建）。

**方法**

```java
String key()  // 公布的键。
void update(byte[] value)  // 更新公布的值。
default void update(String value)
void revoke()  // 主动撤销公布。
default void close()
```

### MembershipListener

`public interface MembershipListener`　成员上下线 / 变更监听器。

**方法**

```java
default void onJoin(Node node)  // 新成员加入。
default void onLeave(Node node)  // 成员离开（主动注销 / lease 过期被感知）。
default void onUpdate(Node previous, Node current)  // 成员 payload 更新。
```

### Node

`public record Node(String id, byte[] payload, long revision)`　注册表中的一个成员节点。

**构造参数（record 组件）**

```java
String id
byte[] payload
long revision
```

**方法**

```java
String payloadAsString()
static Node of(String id, byte[] payload)
boolean equals(Object o)
int hashCode()
String toString()
```

### NodeRegistry

`public interface NodeRegistry extends AutoCloseable`　成员注册表（由 Session.registry(path) 创建，挂在该 session 上）。

**方法**

```java
void register(String id, byte[] payload)  // 注册（或覆盖）本实例在该路径下的成员条目。
void update(String id, byte[] payload)  // 更新本实例已注册条目的 payload。
void unregister(String id)  // 注销本实例的成员条目。
List<Node> members()  // 当前成员快照。
void addListener(MembershipListener listener)  // 注册成员变化监听器。
void close()
default void register(String id, String payload)
default void update(String id, String payload)
```

## 包 `com.mcst.cluster.session`

### Session

`public interface Session extends AutoCloseable`　租约会话——本框架的中心抽象。选主 / 注册 / 端点公布 / 锁都「挂」在 session 上： session 失效即这些资源一并失效，语义统一。

**方法**

```java
long leaseId()  // 底层租约 id。
boolean isAlive()  // 会话当前是否存活（ESTABLISHED 或挂起但未过期）。
SessionState state()  // 会话状态。
LeaderElection election(String path)  // 获取/创建指定路径上的选举位。
NodeRegistry registry(String path)  // 获取/创建指定路径上的成员注册表。
Advertisement advertise(String key, byte[] value)  // 公布一个随会话过期自动撤销的端点。
void addListener(SessionListener listener)  // 注册会话生命周期监听器。
void close()  // 关闭会话：撤销 lease，连带释放挂在其上的所有资源。
```

### SessionListener

`public interface SessionListener`　会话生命周期监听器。

**方法**

```java
default void onEstablished(long leaseId)  // 会话（重新）建立成功（含 autoRecreate 后的重建）。
default void onSuspended()  // 连接挂起：续租受阻但 lease 未到期（降级窗口）。
default void onLost()  // 会话丢失：lease 过期/撤销，挂在其上的资源失效。
```

### SessionOptions

`public final class SessionOptions`　会话级可选项。未显式设置的项回落到 ClusterConfig 的默认值。

**方法**

```java
Duration leaseTtl()  // 覆盖默认 lease TTL；null 表示用配置默认值。
Boolean autoRecreate()  // 覆盖默认「会话丢失自动重建」；null 表示用配置默认值。
static SessionOptions defaults()
static Builder builder()
```

#### SessionOptions.Builder

`public static final class Builder`

**方法**

```java
Builder leaseTtl(Duration leaseTtl)
Builder autoRecreate(boolean autoRecreate)
SessionOptions build()
```

### SessionState

`public enum SessionState`　会话状态。

**枚举常量**

```java
ESTABLISHED  // 租约有效、续租正常。
SUSPENDED  // 连接挂起，续租暂时受阻但 lease 尚未到期（降级窗口，身份仍保留）。
LOST  // 租约已丢失（过期/撤销）。挂在其上的资源失效。
CLOSED  // 会话已关闭。
```

## 包 `com.mcst.cluster.spi`

### ClusterClientFactory

`public interface ClusterClientFactory`　后端实现工厂（SPI / ServiceLoader）。

**方法**

```java
String backend()  // 本工厂支持的后端标识，如 "etcd" / "noop"。
default boolean supports(ClusterConfig config)  // 是否能处理给定配置（默认按 backend 匹配）。
ClusterClient create(ClusterConfig config)  // 创建客户端实例（应已完成连接初始化或惰性连接）。
```

## 包 `com.mcst.cluster.spring`

### ClusterAutoConfiguration

`public class ClusterAutoConfiguration`　注解：`@Configuration(proxyBeanMethods = false)` `@EnableConfigurationProperties(ClusterProperties.class)` `@Conditional(ClusterAutoConfiguration.OnClusterEnabled.class)`　集群管理框架自动装配：按 easyfk.config.cluster.* 配置创建唯一的 ClusterClient（etcd 或 NoOp）。

**方法**

```java
@Bean(destroyMethod = "close") @ConditionalOnMissingBean ClusterClient clusterClient(ClusterProperties props, Environment environment)
```

### ClusterProperties

`public class ClusterProperties`　注解：`@ConfigurationProperties(prefix = ClusterProperties.PREFIX)`　集群管理框架的 Spring Boot 配置项，前缀 easyfk.config.cluster。

**字段 / 常量**

```java
static final String PREFIX = "easyfk.config.cluster"
static final String LEGACY_PREFIX = "mcst.config.cluster"  // 已废弃的旧前缀，仅用于兼容回落。
boolean enabled = true  // 是否启用（false 时不装配 ClusterClient bean）。
String backend  // 后端：etcd / noop。留空时按是否配置 endpoints 自动选择。
List<String> endpoints = new ArrayList<>()  // etcd endpoints，如 http://127.0.0.1:2379。为空则回落到 NoOp（单机零回归）。
String username
String password
String namespace = ""  // 全局 key 命名空间前缀。
Duration leaseTtl = Duration.ofSeconds(5)  // 默认 lease TTL（文档 C6 默认 5s）。
boolean autoRecreateSession = true  // 会话丢失后是否自动重建（文档 C5 默认自动）。
Duration requestTimeout = Duration.ofSeconds(5)
Duration callbackTimeout = Duration.ofSeconds(3)
String authority
final Tls tls = new Tls()
```

**方法**

```java
boolean isEnabled()
void setEnabled(boolean enabled)
String getBackend()
void setBackend(String backend)
List<String> getEndpoints()
void setEndpoints(List<String> endpoints)
String getUsername()
void setUsername(String username)
String getPassword()
void setPassword(String password)
String getNamespace()
void setNamespace(String namespace)
Duration getLeaseTtl()
void setLeaseTtl(Duration leaseTtl)
boolean isAutoRecreateSession()
void setAutoRecreateSession(boolean autoRecreateSession)
Duration getRequestTimeout()
void setRequestTimeout(Duration requestTimeout)
Duration getCallbackTimeout()
void setCallbackTimeout(Duration callbackTimeout)
String getAuthority()
void setAuthority(String authority)
Tls getTls()
```

#### ClusterProperties.Tls

`public static class Tls`　TLS 配置。

**方法**

```java
String getCaCertPath()
void setCaCertPath(String caCertPath)
String getClientCertPath()
void setClientCertPath(String clientCertPath)
String getClientKeyPath()
void setClientKeyPath(String clientKeyPath)
```

## 包 `com.mcst.cluster.store`

### KeyValue

`public record KeyValue(String key, byte[] value, long createRevision, long modRevision, long version, long lease)`　共享存储中的一个键值条目（含 etcd revision 元数据）。

**构造参数（record 组件）**

```java
String key
byte[] value
long createRevision
long modRevision
long version
long lease
```

**方法**

```java
String valueAsString()  // 以 UTF-8 解码 value。
static KeyValue of(String key, byte[] value)
boolean equals(Object o)
int hashCode()
String toString()
```

### SharedStore

`public interface SharedStore`　强一致的小状态共享存储（非通用大容量 KV / 配置中心）。

**方法**

```java
Optional<KeyValue> get(String key)  // 读取单个键。不存在返回 empty()。
List<KeyValue> getPrefix(String keyPrefix)  // 按前缀批量读取。
void put(String key, byte[] value)  // 写入（持久键，无 lease）。
boolean compareAndSet(String key, byte[] expectedValue, byte[] newValue)  // CAS 写入：当且仅当当前值等于 expectedValue 时写入 newValue。
boolean delete(String key)  // 删除键。
Watch watch(String keyOrPrefix, boolean prefix, long fromRevision, WatchListener listener)  // 注册 watch。
void putCoalesced(String key, byte[] latest, Duration minInterval)  // 高频写收敛：同一 key 在 minInterval 内的多次写只保留最新值，异步合并刷出， 以保护 etcd 写预算…
long currentRevision()  // 当前 store 的最新 revision（用于初始化 watch 水位）。
default Optional<String> getString(String key)
default void put(String key, String value)
default boolean compareAndSet(String key, String expectedValue, String newValue)
default Watch watch(String keyOrPrefix, WatchListener listener)
default Watch watchPrefix(String keyPrefix, WatchListener listener)
```

### Watch

`public interface Watch extends AutoCloseable`　一个活跃的 watch 句柄。关闭即停止接收事件。

**方法**

```java
long lastRevision()  // 已处理到的最新 revision（重连重放的水位线）。
void close()  // 停止 watch 并释放资源。可重复调用。
```

### WatchEvent

`public record WatchEvent(EventType type, KeyValue keyValue, KeyValue prevKeyValue)`　一次 watch 事件。

**构造参数（record 组件）**

```java
EventType type
KeyValue keyValue
KeyValue prevKeyValue
```

#### WatchEvent.EventType

`public enum EventType`

**枚举常量**

```java
PUT
DELETE
```

### WatchListener

`public interface WatchListener`　watch 事件回调。

**方法**

```java
void onEvents(List<WatchEvent> events)  // 一批事件（同一 watch 响应内的事件保持顺序）。
default void onError(Throwable error)  // watch 在内部不可恢复地失败时回调（如 revision 已被 compaction 清除）。 调用方通常应重新读取全量快照并重建 watch。
default void onClosed()  // watch 正常关闭后回调。
```
