# aeron-cluster Skill 参考文档

> 所属项目：`aeron-cluster`（独立 Gradle 工程，4 个子模块）　坐标：`com.mcst:<module>:3.5.16`，BOM 中归 `aeron` bundle
> 依据：全部子模块 `src/main` 源码、各模块 `build.gradle`、`settings.gradle`（catalog 只保留 lombok / processor）、starter 单元测试；对齐 `docs/` 下《Cluster使用手册》《Cluster架构设计》《Cluster组件特点介绍》。
> 文档与源码不一致时 **以源码为准**，差异见文末「复查记录」。

---

## 1. 模块定位

基于 Aeron Cluster 1.54.2（Raft 共识）的**状态机式 RPC 框架**：业务写一个确定性状态机，框架负责日志复制、选主、持久化、快照、故障转移；客户端发命令拿 `CompletableFuture` 响应，写操作线性一致。

| 适合 | 不适合（改用） |
|---|---|
| 配置 / 元数据中心、服务注册权威源 | 几十 GB 起的海量数据 → 数据库 / 分布式存储 |
| 分布式锁、序列号 / 号段生成 | 高吞吐消息总线（>10 万 TPS）→ easyfk-aeron 广播或 MQ |
| 任务调度协调、分片归属 | 异步事件流处理 → component-mq |
| 高可用计数器、限流配额 | 跨 region 强一致 → 专门方案 |
| 小型订单 / 撮合引擎 | 需要阻塞 IO 的业务逻辑（状态机里禁止） |

前提：业务状态**能放进单机内存**（典型 < 10 GB），写入要求强一致胜过吞吐。

与 easyfk-aeron 的关系：两者独立部署、独立升级，cluster 只复用 `aeron-common` 的 `Codec<T>` / `CodecRegistry` / `CodecIds` 契约，**codec 实现可两边共用**。

## 2. 模块清单与依赖

包名统一 `com.mcst.aeron.cluster.*`。

| 模块 | 作用 | 何时引入 |
|---|---|---|
| `aeron-cluster-spring-boot-starter` | 自动装配节点 / 客户端 / 健康检查 / 事件监听；`api` 传递 core + client | **Spring Boot 服务一律引它** |
| `aeron-cluster-core` | 状态机 SPI、节点生命周期、快照、帧协议、幂等基类、metrics SPI；零 Spring | 非 Spring 场景起节点 |
| `aeron-cluster-client` | 客户端（`ClusterClient`、重连、重试装饰器） | 非 Spring 场景只做调用方 |
| `aeron-cluster-test` | 嵌入式单 / 三节点集群、`ClusterAwait`、JUnit5 扩展 | **仅 `testImplementation`** |

```groovy
dependencies {
    implementation platform('com.mcst:easyfk-dependencies:3.5.16')
    implementation 'com.mcst:aeron-cluster-spring-boot-starter'
    implementation 'com.mcst:aeron-codec-fory'          // 可选: 复用 easyfk-aeron 的 codec, starter 默认 registry 经 ServiceLoader 自动注册
    // implementation 'org.springframework.boot:spring-boot-starter-actuator'
    testImplementation 'com.mcst:aeron-cluster-test'          // 版本由 BOM 管理
}
```

- 第三方版本**由 BOM 的 `aeronRuntime` bundle 统一约束**（本版本起不再写在本工程 catalog）：`aeron-cluster` / `aeron-archive` / `aeron-client` / `aeron-driver` **1.54.2**、`agrona` **2.7.1**，由 core 以 `api` 传递。**禁止**业务单独覆盖或 `exclude` Aeron / Agrona，必须与 easyfk-aeron 同版本（两者共用同一套 BOM 约束）。
- `aeron-cluster-core` 以 `api` 依赖 `com.mcst:aeron-common` 和 `slf4j-api`，core / client **不传递 Spring 和 easyfk-core**；starter 额外 `api` 传递 `spring-boot-autoconfigure`；`aeron-cluster-test` 以 `api` 传递 `junit-jupiter-api`、`awaitility`（版本由 BOM 管）。业务代码用到 easyfk-core 时自己声明，不要指望从 cluster 传递。
- 运行环境：**JDK 21**、Spring Boot 3.5.16（jakarta）。只有 `AutoConfiguration.imports`，没有 `spring.factories`。

### 2.1 JVM 参数（必须）

Aeron / Agrona 在 JDK 21 上需要反射访问，节点和客户端进程都要加：

```
--add-opens java.base/java.lang=ALL-UNNAMED
--add-opens java.base/java.lang.reflect=ALL-UNNAMED
--add-opens java.base/java.io=ALL-UNNAMED
--add-opens java.base/java.nio=ALL-UNNAMED
--add-opens java.base/java.util.zip=ALL-UNNAMED
--add-opens java.base/sun.nio.ch=ALL-UNNAMED
--add-opens java.base/jdk.internal.misc=ALL-UNNAMED
```

框架自身构建默认**跳过测试**，需 `./gradlew test -PrunTests`；IT 用 `@Tag("it")`，未按 tag 过滤。

## 3. 状态机（服务端核心）

### 3.1 接口

```java
public interface ClusterStateMachine<C> {
    default void onStart(ClusterContext ctx) {}                       // 有快照时 loadSnapshot 先于它
    void onCommand(ClusterSession session, C command, ClusterContext ctx);  // 唯一必须实现
    default void onTimer(long timerId, ClusterContext ctx) {}
    default void onRoleChange(ClusterRole role) {}                    // UNKNOWN/FOLLOWER/CANDIDATE/LEADER
    default void onSessionOpen(ClusterSession session) {}
    default void onSessionClose(ClusterSession session, CloseReason reason) {}
    default void takeSnapshot(SnapshotWriter writer) {}
    default void loadSnapshot(SnapshotReader reader) {}
    default void onStop() {}                                          // 尽力而为, 不保证调用
    default Set<Integer> declaredCommandCodecIds() { return Collections.emptySet(); }  // 空 = 不校验
}
```

- `C` 是命令域上界：多种命令用 `sealed interface` + `record`，在 `onCommand` 里 `switch` / `instanceof` 分发。**每种命令一个 `Codec`**，节点和客户端的 `CodecRegistry` 都要注册。
- Spring 下用 `@ClusterStateMachineBean`（等价 `@Component`）或 `@Component` 标注；**容器内只能有一个 `ClusterStateMachine` bean**（按类型单注入）。

### 3.2 线程模型与确定性（硬约束）

所有回调都在 ClusteredServiceContainer 的**单线程 agent** 上同步执行，follower 也会回放同样的命令：

| 禁止 | 改用 |
|---|---|
| 阻塞 IO（HTTP / DB / 文件 / MQ） | 数据放进命令；外部系统由集群外进程处理后再发命令回写 |
| 长 CPU 计算（>1 ms 拖慢整集群） | 客户端预计算，状态机只接收结果 |
| `synchronized` / `Lock` | 不需要，单线程 |
| `System.currentTimeMillis()` / `LocalDateTime.now()` 做业务时间 | `ctx.clusterTimeMs()` |
| `Math.random()` / `UUID.randomUUID()` | 从命令或 `clusterTimeMs` 派生种子的自管伪随机 |
| 依赖 `HashMap` 迭代顺序 | `LinkedHashMap` / `TreeMap` / 排序后迭代 |
| `Locale.getDefault()` / 系统时区 | 显式传参 |
| 在其它线程调 `ctx` / `session` 方法、修改状态 | 只在状态机回调里调用 |
| 持有 Aeron 内部对象（`Image` / `Publication` / `Counter`） | — |

- `onCommand` 抛 `RuntimeException`：框架吞掉、记 `metrics.onError` + `onCommandRejected("state_machine_throw:...")`，**不会发响应**，客户端只能等超时；抛出前已改的状态不会回滚。业务错误应**显式 `respond` 错误结果**，不要靠抛异常。
- `onStart` / `loadSnapshot` 抛异常会让节点启动失败（fail-fast）。
- 命令先过 `declaredCommandCodecIds` 校验，再用节点 `CodecRegistry` 解码；未注册 / 未声明 / 解码失败的命令被丢弃并记 `onCommandRejected`。

### 3.3 ClusterContext

```java
ctx.memberId();  ctx.role();
ctx.clusterTimeMs();                         // Raft 提交时间, 业务时间戳 / TTL / 超时一律用它
ctx.timeMs();                                // 墙钟 (可注入 ClusterClock), 不要用于业务状态
ctx.scheduleTimer(timerId, deadlineMs);      // deadline 是绝对 cluster time; 同 id 重复 schedule 覆盖
ctx.cancelTimer(timerId);
ctx.reportError(t);                          // 上报 metrics + log, 不中断
ctx.publishEgress(session, codec, value);    // = session.publishEvent
```

`timerId` 由业务自管且全局唯一；`onTimer` 里续期要重新 `scheduleTimer(id, ctx.clusterTimeMs() + period)`。

### 3.4 ClusterSession

```java
session.id();                         // Aeron 分配的会话 id (每次重连都会变, 不能当业务 clientId)
session.correlationId();              // 仅 onCommand 期间有效
session.respond(codec, value);        // 对当前命令的应答 (RESPONSE 帧, 带 correlationId)
session.respondBytes(bytes);
session.publishEvent(codec, value);   // 主动推送 (EGRESS_EVENT 帧, 无 correlationId)
session.close(CloseReason.SERVICE_ACTION);
session.isOpen();
```

- `respond` / `publishEvent` 只有 LEADER 真正发出；FOLLOWER / CANDIDATE 上返回 `-1` 静默丢弃，**不要判断角色**。
- 其它负值是 Aeron `Publication` 状态码（背压等），框架只记 `onRespondDropped`，不重发。
- 同一 session id 打开期间是同一个实例，可以在状态机线程上跨回调保留（watcher 模式），**必须在 `onSessionClose` 里移除**。
- 快照时刻已打开的会话在重启恢复时**不会**再触发 `onSessionOpen`；与会话相关的业务状态要随快照持久化。

### 3.5 主动推送（watcher / 广播）

```java
private final List<ClusterSession> watchers = new ArrayList<>();

case Subscribe s -> { watchers.add(session); session.respond(AckCodec.INSTANCE, ACK); }
case Update u    -> { apply(u); for (ClusterSession w : watchers) w.publishEvent(UpdateCodec.INSTANCE, u); }

@Override public void onSessionClose(ClusterSession s, CloseReason r) { watchers.remove(s); }
```

客户端在 `ClusterEventListener.onEgressEvent(codecId, buffer, offset, length)` 接收，自行解码。EGRESS_EVENT 不经去重表，需要幂等消费时在 payload 里带业务去重键。

### 3.6 幂等状态机（重试安全的前提）

客户端超时后无法判断命令是否已执行。凡是客户端会重试的写命令，状态机都应继承 `AbstractIdempotentStateMachine<C>`：

```java
public final class AccountStateMachine extends AbstractIdempotentStateMachine<AccountCmd> {
    protected long clientIdOf(AccountCmd c)  { return c.clientId(); }   // 跨重连稳定; NOT_TRACKED(-1) = 不去重 (只读命令)
    protected long requestIdOf(AccountCmd c) { return c.requestId(); }  // 同 client 内单调递增
    protected void applyCommand(ClusterSession s, AccountCmd c, ClusterContext ctx) { ...; s.respond(...); }
    protected int snapshotVersion() { return 1; }
    protected void writeState(SnapshotWriter w) { ... }                 // 不要写 header
    protected void readState(SnapshotReader r, int storedVersion) { ... } // 不要读 header
}
```

- `onCommand` / `takeSnapshot` / `loadSnapshot` 是 `final`，由基类接管；重复请求直接回放缓存响应，过期请求丢弃。
- `clientId` **不能用 `session.id()`**；clientId 基数要有界，确认永久下线的调 `forgetClient`。
- 已上线的普通状态机改继承该基类会改变快照布局（最前面多一个去重表），必须全新启动或自行迁移快照。

### 3.7 状态审计（可选）

状态机实现 `StateAuditSource` 后，可在任意线程调 `ClusterNode.captureAuditView()` 拿到某个 log position 的一致只读视图（`StateAuditView`，`counts()` + `export(sink)`）。`captureAuditView` 在 agent 线程执行，必须 O(1) 返回 COW 视图；`export` 在调用方线程执行；视图**必须 close**，单节点最多 16 个未关闭视图。

## 4. 快照

### 4.1 同步快照（默认）

```java
public static final int BUSINESS_VERSION = 2;

@Override public void takeSnapshot(SnapshotWriter w) {
    w.writeHeader(SnapshotMagic.FRAMEWORK_VERSION_V1, BUSINESS_VERSION);   // 先且只写一次
    w.write(StateCodec.INSTANCE, state);                                  // 或 writeBytes(...)
}

@Override public void loadSnapshot(SnapshotReader r) {
    SnapshotHeader h = r.readHeader(BUSINESS_VERSION);   // 流上版本 > 参数时抛 ClusterSnapshotException(拒绝加载)
    if (h.businessVersion() < BUSINESS_VERSION) { /* 旧格式兼容读取 */ }
    while (r.hasMore()) { ... r.read(codec) / r.readBytes() ... }        // 顺序必须与写入完全一致
}
```

- `BUSINESS_VERSION` 业务自管：in-memory 结构或 codec 编码一变就 +1，并保留旧版本读取路径，补"读旧快照"单测。
- **单条 entry 上限 = snapshot-channel 的 term-length / 8**（默认 8m → 1 MB），超限在 `takeSnapshot` 时失败；大状态拆成多条 entry 写，或用异步快照。
- `write*` 是拷贝语义，可复用同一块缓冲分片写出；加载时整个快照流一次性读进内存，heap 要留够。

### 4.2 异步快照（几百 MB 级状态）

状态机额外实现 `AsyncSnapshotSource`：

```java
@Override public SnapshotView captureSnapshot(long logPosition) {   // agent 线程, 必须 O(1)
    ImmutableState snap = state.cowSnapshot();
    return new SnapshotView() {
        public void write(SnapshotWriter w) {                         // 后台线程, 写法同 takeSnapshot
            w.writeHeader(SnapshotMagic.FRAMEWORK_VERSION_V1, BUSINESS_VERSION);
            w.write(StateCodec.INSTANCE, snap);
        }
        public void close() { }
    };
}
```

- 实现后同步 `takeSnapshot` 不再被调用，`loadSnapshot` 保持不变。
- 真实数据写到节点本地的 `snapshot-<logPosition>.snap`（默认 `clusterDir/snapshots`，保留 `snapshot-ext-retain-count` 份）。Aeron 快照复制**不会**复制这些文件，重建节点前要从健康节点拷过来。
- **不要手工删**目录里的 `.pending` / `.tmp`，崩溃回退靠它们。

### 4.3 触发与磁盘治理

| 方式 | 说明 |
|---|---|
| 周期 | `snapshot-interval-ms`（默认 1 h，`<= 0` 禁用），仅 leader 触发；`snapshot-quiet-windows: ["02:00-04:00"]` 跳过窗口（本地时区，可跨午夜）。**不要配到分钟级** |
| 手动 | `ClusterNode.triggerSnapshot()`，仅 leader 返回 true，不受静默窗口限制 |
| 运维 | Aeron `ClusterTool snapshot` |
| 优雅关闭 | Aeron 自动触发 |

Aeron 开源版不会删旧快照 recording，archiveDir 会无界增长。生产必须设 `archive-retain-snapshot-count: 3`（启用时 ≥ 3，0 = 禁用），按快照组保留并裁剪 raft log；`archive-segment-file-length` 留空自动跟随 term-length，显式配置须是 2 的幂、∈ [64 KB, 1 GB] 且 ≥ term-length。

## 5. 客户端

### 5.1 调用

```java
// 等响应: timeoutMs 内必定完成 (正常 / ClusterTimeoutException / ClusterClientException)
CompletableFuture<OrderResp> f = client.sendAndAwait(PlaceCodec.INSTANCE, cmd, RespCodec.INSTANCE, 3_000L);
// 不带 timeoutMs 的重载用 response-timeout-ms (默认 3000)

// fire-and-forget: 不分配 correlation 槽位
long pos = client.send(CmdCodec.INSTANCE, cmd);   // <0 = 未连接 / 背压, 由调用方决定重试; publication 永久错时抛异常
```

- `send` / `sendAndAwait` 线程安全，可任意线程调用。
- future 的回调在 **poller 线程**执行：`thenApply` 里不要做重活或阻塞，用 `thenApplyAsync(executor)`；也不要在业务线程无超时 `get()`。
- 未连接时 `sendAndAwait` 立即以 `ClusterClientException("client not connected")` 失败。
- 断线重连会建立**新会话**，旧会话上未返回的请求只能等超时。

### 5.2 重试

starter **不提供**重试配置；需要重试时自己声明 `ClusterClient` bean（见 6.4）：

```java
RetryPolicy policy = RetryPolicy.builder()
        .maxAttempts(3).initialBackoffMs(20).maxBackoffMs(500).factor(2.0)
        .retryOnTimeout(false)     // 默认 false; 只有服务端继承 AbstractIdempotentStateMachine 时才能开
        .build();
ClusterClient client = ClusterClientBuilder.createRetrying(cfg, policy);
```

| 失败 | 默认重试 | 原因 |
|---|---|---|
| `ClusterClientException`（offer 失败 / 未连接） | 是 | 命令确定没进集群 |
| `ClusterTimeoutException` | **否** | 可能已执行，重试会重复 |
| 其它 | 否 | `retryableException(Predicate)` 自定义 |

`send` 的重试在**调用线程上 sleep** 退避；`sendAndAwait` 在独立线程上调度。最坏总耗时 ≈ `maxAttempts × timeoutMs + 退避`。

### 5.3 重连与事件

- 重连策略默认 `NONE`（断线即放弃并回调 `onDisconnected`）。**生产必须配 `EXPONENTIAL_BACKOFF`**，否则 leader 切换 / 滚动升级时客户端直接失效。
- 重连只处理**已连上后**的断线；首次 `connect()` 失败直接抛 `ClusterClientException`。
- `onDisconnected` 表示重连已放弃，之后 send 全部失败，业务应走降级或让进程退出由编排系统拉起。
- `keep-alive-interval-ms`（默认 2000）必须小于集群 session 超时（10 s），否则空闲会话会被 TIMEOUT 关闭。

## 6. Spring Boot 接入

### 6.1 配置（前缀 `easyfk.config.aeron.cluster`）

节点（三节点生产，三台机器 `member-id` 分别为 0/1/2，`topology` 全部一致）：

```yaml
easyfk:
  config:
    aeron:
      cluster:
        node:
          enabled: true
          member-id: 0
          media-driver-mode: EMBEDDED          # EXTERNAL = 复用已起的 driver
          aeron-dir: /dev/shm/aeron-cluster-0  # 三个目录必须互不相同; 留空落到 java.io.tmpdir
          archive-dir: /data/aeron-cluster/archive
          cluster-dir: /data/aeron-cluster/cluster
          snapshot-interval-ms: 3600000
          archive-retain-snapshot-count: 3     # 生产必开
          # snapshot-channel: aeron:ipc?alias=snapshot|term-length=8m
          # snapshot-quiet-windows: ["02:00-04:00"]
          # snapshot-ext-dir / snapshot-ext-retain-count: 2
          # archive-segment-file-length / archive-retention-interval-ms: 3600000
          # idle-strategy: BACKOFF             # NOOP|BUSY_SPIN|YIELDING|BACKOFF|SLEEP_NS:<n>|SLEEP_MS:<n>
          # leader-heartbeat-timeout-ns: 10000000000
          # shutdown-timeout-ms: 10000
          # delete-dirs-on-start / delete-dirs-on-close: false   # 生产禁止置 true
          topology:
            - { member-id: 0, ingress: 10.0.0.1:9001, consensus: 10.0.0.1:9002, log: 10.0.0.1:9003, catchup: 10.0.0.1:9004, archive: 10.0.0.1:9005 }
            - { member-id: 1, ingress: 10.0.0.2:9001, consensus: 10.0.0.2:9002, log: 10.0.0.2:9003, catchup: 10.0.0.2:9004, archive: 10.0.0.2:9005 }
            - { member-id: 2, ingress: 10.0.0.3:9001, consensus: 10.0.0.3:9002, log: 10.0.0.3:9003, catchup: 10.0.0.3:9004, archive: 10.0.0.3:9005 }
```

客户端：

```yaml
easyfk:
  config:
    aeron:
      cluster:
        client:
          enabled: true
          ingress-endpoints: "0=10.0.0.1:9001,1=10.0.0.2:9001,2=10.0.0.3:9001"   # 必须列全部节点
          response-timeout-ms: 3000
          connect-timeout-ms: 10000
          # egress-channel: aeron:udp?endpoint=localhost:0
          # aeron-dir:                      # 留空 = 客户端自起嵌入式 driver
          # keep-alive-interval-ms: 2000
          # enable-background-poller: true
          reconnect:
            strategy: EXPONENTIAL_BACKOFF    # 默认 NONE
            initial-delay-ms: 200
            max-delay-ms: 5000
            factor: 2.0
            max-attempts: 10
```

- `node.enabled` / `client.enabled` 默认都是 `false`；同一进程可以两者都开。
- `node.enabled=true` 但容器里**没有** `ClusterStateMachine` bean 时，节点**静默不装配**（`@ConditionalOnBean`）。
- `shutdown.mark-file-wait-ms` 未接线，设置无效。
- 每个节点用 5 个 UDP 端口，节点之间全部放行；客户端只需访问 ingress。

### 6.2 Bean

| Bean | 类型 | 条件 / 覆盖 |
|---|---|---|
| `aeronClusterCodecRegistry` | `CodecRegistry`（`withDefaults()`，ServiceLoader 加载 codec） | 容器内无任何 `CodecRegistry` 时；节点和客户端共用 |
| `aeronClusterNode` | `ClusterNode`（bean 创建时即 `launch`） | `node.enabled=true` 且有状态机 bean；`@ConditionalOnMissingBean` |
| `aeronClusterClient` | `ClusterClient` | `client.enabled=true`；`@ConditionalOnMissingBean` |
| `aeronClusterClientLifecycle` | 上下文启动末尾注册 listener 并 `connect()` | 随 client |
| `aeronClusterLifecycle` | 停机时先关 client 再关 node | 总是 |
| `aeronClusterEventListenerBeanPostProcessor` | 扫描 `@ClusterEventListener` 方法 | 总是 |
| `aeronClusterHealth` | `HealthIndicator`，路径 `/actuator/health/aeronClusterHealth` | classpath 有 actuator |

节点会自动注入容器里的 `ClusterMetrics`、`RoleChangeListener`、`ClusterClock`（可选，各一个）；客户端只注入 `ClusterMetrics`。

节点 / 客户端使用的 `CodecRegistry` 按以下顺序选取：名为 `aeronClusterCodecRegistry` 的 bean → 容器内唯一（或 `@Primary`）的 `CodecRegistry` → 有多个且无法区分时启动失败（`ClusterConfigException`）。starter 排在 easyfk-aeron 的 codec 装配之后，与之同进程时默认 bean 让位，单 driver 下直接共用 aeron 的 registry。

### 6.3 注入与事件监听

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final ClusterClient clusterClient;
    public CompletableFuture<OrderResp> place(OrderPlace cmd) {
        return clusterClient.sendAndAwait(OrderPlaceCodec.INSTANCE, cmd, OrderRespCodec.INSTANCE);
    }
}

@Component
public class ClusterEvents {
    @ClusterEventListener(Event.NEW_LEADER)  public void onLeader(long sessionId, long termId, int leaderId) { }
    @ClusterEventListener(Event.DISCONNECTED) public void onDown() { }
    @ClusterEventListener(Event.RECONNECTED) public void onUp(int attempts) { }          // 或无参
    @ClusterEventListener(Event.EGRESS)      public void onPush(int codecId, DirectBuffer buf, int offset, int length) { }
}
```

- 注解是 `com.mcst.aeron.cluster.spring.annotation.ClusterEventListener`，与接口 `com.mcst.aeron.cluster.client.api.ClusterEventListener` **同名**，注意 import。
- 签名不匹配启动期 fail-fast；回调在 poller 线程上执行，禁止阻塞；方法抛异常只记 WARN + `metrics.onError`。
- `EGRESS` 回调里的 `buffer` 只在回调期间有效，需要保留就先拷贝。

### 6.4 自定义覆盖

```java
@Bean("aeronClusterCodecRegistry")   // cluster 专用; 与 easyfk-aeron 同进程也不冲突
CodecRegistry clusterCodecRegistry() {
    return CodecRegistry.minimal().register(OrderPlaceCodec.INSTANCE).register(OrderRespCodec.INSTANCE);
}

@Bean   // 需要重试时: 覆盖 client bean, 仍须 client.enabled=true 才会装配 lifecycle 自动 connect
ClusterClient aeronClusterClient(CodecRegistry codecs) {
    ClusterClientConfig cfg = ClusterClientConfig.builder()
            .ingressEndpoints("0=10.0.0.1:9001,1=10.0.0.2:9001,2=10.0.0.3:9001")
            .codecRegistry(codecs)
            .reconnectStrategy(ReconnectStrategy.exponentialBackoff(200, 5_000, 2.0, 10))
            .build();
    return ClusterClientBuilder.createRetrying(cfg, RetryPolicy.defaults());
}

@Bean ClusterMetrics clusterMetrics(MeterRegistry mr) { return new MyMicrometerClusterMetrics(mr); }
@Bean RoleChangeListener roleChangeListener() { return (prev, curr, term) -> log.info("role {} -> {} term {}", prev, curr, term); }
```

- 与 easyfk-aeron starter 同进程且 aeron 配了**多个 driver** 时，容器内有多个 `CodecRegistry`，必须声明 `aeronClusterCodecRegistry`（或标一个 `@Primary`），否则启动失败。
- `ClusterMetrics` 有 15 个抽象方法 + 7 个 default（快照请求 / 跳过 / 失败、archive 保留清理），方法内**禁止**在热路径拼字符串，标签预先缓存。

### 6.5 启停时序

- **启动**：`ClusterNode` 在 bean 创建时同步启动（加载快照、加入集群）；客户端在 `SmartLifecycle` phase `Integer.MAX_VALUE - 1000` 时 `connect()`，晚于 Web 容器开始接收请求。`connect-timeout-ms` 内连不上则**应用启动失败**，所以集群要先于客户端应用就绪。
- **停止**：`ClusterLifecycle`（phase `Integer.MAX_VALUE`）最先执行，先 close 客户端再 close 节点，早于 Web 容器优雅停机；停机窗口内的请求调 cluster 会立即失败。
- 健康检查：节点 `isRunning` 且客户端 `isConnected` 时为 UP；details 含 `node.role`，运维据此识别 leader。

## 7. 非 Spring 用法

```java
CodecRegistry codecs = CodecRegistry.minimal().register(CmdCodec.INSTANCE).register(RespCodec.INSTANCE);

ClusterNode node = ClusterNode.launch(ClusterNodeConfig.builder()
        .memberId(0)
        .topology(ClusterTopology.of(ClusterMember.builder().memberId(0)
                .ingressEndpoint("10.0.0.1:9001").consensusEndpoint("10.0.0.1:9002").logEndpoint("10.0.0.1:9003")
                .catchupEndpoint("10.0.0.1:9004").archiveEndpoint("10.0.0.1:9005").build() /* , 其余成员 */))
        .stateMachine(new OrderStateMachine())
        .codecRegistry(codecs)
        .aeronDir(Path.of("/dev/shm/aeron-0")).archiveDir(Path.of("/data/archive")).clusterDir(Path.of("/data/cluster"))
        .archiveRetainSnapshotCount(3)
        .build());

ClusterClient client = ClusterClientBuilder.create(ClusterClientConfig.builder()
        .ingressEndpoints("0=10.0.0.1:9001,1=10.0.0.2:9001,2=10.0.0.3:9001")
        .codecRegistry(codecs)
        .reconnectStrategy(ReconnectStrategy.exponentialBackoff(200, 5_000, 2.0, 10))
        .build());
client.connect();
try { ... } finally { client.close(); node.close(); }   // close 均幂等
```

`ClusterNodeConfig.build()` 会全量校验：`memberId` 必须在拓扑内、三个目录互不相同、段长 / 保留份数合法，否则抛 `ClusterConfigException`。偶数节点或单节点拓扑只打 WARN。

## 8. 测试

```java
@Test
void roundTrip(@TempDir Path tmp) throws Exception {
    CodecRegistry codecs = CodecRegistry.minimal().register(CounterStateMachine.CODEC);
    try (EmbeddedSingleNodeCluster c = EmbeddedSingleNodeCluster.launch(new CounterStateMachine(), codecs, tmp)) {
        ClusterAwait.untilLeaderElected(List.of(c.node()));
        ClusterAwait.untilConnected(c.client());
        assertThat(c.client().sendAndAwait(CODEC, 7L, CODEC, 5_000L).get(10, SECONDS)).isEqualTo(7L);
    }
}
```

- 故障转移用 `EmbeddedThreeNodeCluster.launch(Supplier<状态机>, codecs, dir)`（每个节点一个新实例），`currentLeaderMemberId()` + 关闭 leader 节点模拟切主。
- `ClusterAwait`：`untilLeaderElected` / `untilConnected` / `untilCommittedAtLeast(metrics, n)` / `untilSnapshotTaken(metrics)` / `untilTrue(label, cond, timeout)`；**禁止用 `Thread.sleep` 等集群状态**。
- `EmbeddedClusterExtension.register(extensionContext, cluster)` 在每个测试后自动 close；不提供参数注入。
- 单个 IT 5–15 s，标 `@Tag("it")`。状态机的纯业务逻辑优先用桩 `ClusterSession` / `ClusterContext` 做单测，不必起集群。

## 9. 部署与运维要点

- 节点数用**奇数**：生产 3（容错 1），关键服务 5（容错 2）；单节点只用于开发。
- 目录：`aeronDir` 放 tmpfs / `/dev/shm`，`archiveDir` / `clusterDir` 放 SSD，三者互不重叠。
- **禁止 `kill -9`**；逐个重启，等剩余节点重新选出 leader 再动下一个，**不能同时停两个**（三节点）。
- 滚动升级：先 follower，最后 leader。改了 `BUSINESS_VERSION` 必须保证新版本能读旧快照，且新旧版本对同一条日志的回放结果必须一致。
- `topology` 加入集群后不支持动态变更。

## 10. Do / Don't（生成代码时必须遵守）

**Do**
- 状态机只依赖命令内容、自身状态和 `ctx.clusterTimeMs()`，保证确定性。
- 每种命令 / 响应一个 `Codec`，自定义 wire id ≥ 100，节点和客户端注册同一套 codec 实现。
- 业务失败显式 `respond` 错误结果对象；需要重试的写命令走 `AbstractIdempotentStateMachine` + 稳定 `clientId` / 递增 `requestId`。
- 快照写 header + `BUSINESS_VERSION`，结构变更即 +1 并保留旧版本读取，补读旧快照单测。
- 生产配置 `reconnect.strategy: EXPONENTIAL_BACKOFF`、`archive-retain-snapshot-count: 3`、显式三个目录。
- `sendAndAwait` 总是带超时，结果用 `thenApplyAsync(业务线程池)` 或带超时的 `get` 处理。
- 测试用 `aeron-cluster-test` 的 fixture + `ClusterAwait`。

**Don't**
- 不要在状态机里做 IO、加锁、读墙钟、生成随机数 / UUID、依赖 HashMap 顺序。
- 不要在 `onCommand` 用抛异常表达业务失败。
- 不要用 `session.id()` 作为业务客户端标识。
- 不要在状态机外的线程调用 `ctx` / `session` 或修改状态。
- 不要对非幂等命令打开 `retryOnTimeout`。
- 不要在 future 回调 / `@ClusterEventListener` 方法里阻塞 poller 线程。
- 不要把 cluster 当数据库或消息总线用，也不要把高吞吐广播迁到 cluster。
- 不要单独升级 / 排除 Aeron、Agrona；不要在生产开 `delete-dirs-on-start`。
- 不要手删 archiveDir 里的 recording 或外置快照目录的 `.pending` / `.tmp`。
- 不要自己实现 Raft、选主、重连、幂等去重、快照文件格式，框架都已提供。

## 11. 复查记录

| # | 位置 | 问题 | 处理 |
|---|---|---|---|
| 1 | `ClusterNodeAutoConfiguration` | 手册 §7.5 说声明 `RoleChangeListener` / `ClusterClock` bean 即可覆盖，但自动装配只注入了 `ClusterMetrics`，这两个 bean 不生效 | **已修复**：可选注入并传入 `ClusterNodeConfig`；未声明时行为不变 |
| 2 | 健康检查路径 | bean 名 `aeronClusterHealth`，Spring Boot 只剥离 `HealthIndicator` 后缀，实际路径是 `/actuator/health/aeronClusterHealth`，手册 / 架构文档写成 `/aeronCluster` | 文档已改为实际路径；代码不变 |
| 3 | `ClusterLifecycle` 注释、手册 §11.6 | 写的是"比 ClusterClientLifecycle 更晚 stop"，实际 phase 更大、最先 stop（内部先关 client 再关 node） | 注释和手册已更正，并补充"早于 Web 优雅停机"提示；行为不变 |
| 4 | 手册 §9.4 | "启动 30s 内允许 connect 失败"与实现不符：首次 connect 失败会让应用启动失败，重连策略只管连上后的断线 | 手册已更正 |
| 5 | `ClusterSession` / `FrameworkClusterSession` javadoc | 写"禁止跨回调持有 / 按命令新建"，实际按 session id 缓存同一实例，手册 watcher 模式依赖这一点 | javadoc 已更正 |
| 6 | 手册 §8.5 | 说 `./gradlew test` 会跑全部测试，实际根 `build.gradle` 默认跳过，需 `-PrunTests` | 手册已更正 |
| 7 | 与 easyfk-aeron starter 混用 | 两边都可能注册名为 `aeronCodecRegistry` 的 `CodecRegistry`，无装配顺序约束，结果取决于处理顺序 | **已修复**：默认 bean 改名 `aeronClusterCodecRegistry`，`@AutoConfigureAfter` aeron 的 `AeronCodecAutoConfiguration`，节点 / 客户端按"专用名 → 唯一 / @Primary → fail-fast"选取 |
| 8 | `aeron-cluster-core/build.gradle` | `api("com.mcst:easyfk-core")` 只用到 slf4j，却向使用方传递 Spring Boot / Hutool 等；client / starter 上的 `compileOnly easyfk-core` 冗余 | **已修复**：core 改 `api slf4j-api`，删除 client / starter 的 `compileOnly easyfk-core`，starter 显式 `api spring-boot-autoconfigure`（原先靠 easyfk-core 传递）；`testImplementation easyfk-core` 保留 |
| 9 | `ClusterProperties.shutdown.mark-file-wait-ms` | 属性未接线 | javadoc 标注无效；手册原已说明 |
| 10 | `aeron-cluster-test` | 不在 easyfk-dependencies BOM 中 | **已修复**：catalog 新增 `aeronClusterTest` 并加入 `aeron` bundle，手册同步 |
| 11 | `StateAuditSource` / `captureAuditView` | 手册未介绍 | 本文 §3.7 补充 |

#7、#8 修改后已执行 `compileJava compileTestJava` 编译通过；未运行测试（按要求）。
| 11 | `settings.gradle`（本工程 catalog） | 上一版：`aeron-cluster` / `aeron-archive` / `aeron-client` / `aeron-driver` 1.52.1、`agrona` 2.5.0 写死在本工程，与 easyfk-aeron 各写一套 | 本版本 catalog 只保留 `easyfkDependencies` / `lombok` / `processor`，Aeron 与 Agrona 改为无版本坐标，由 BOM 的 `aeronRuntime` bundle 约束（1.54.2 / 2.7.1）。**已修复**：两个工程不会再出现版本漂移 |
