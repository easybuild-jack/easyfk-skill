# etcd-cluster Skill 参考文档

> 来源：`etcd-cluster/` 源码（api / core / starter）、`docs/etcd集群使用文档.md`、`docs/etcd集群设计文档.md`、`docs/etcd-cluster组件介绍.md`。
> 版本：3.5.16；jetcd 0.8.8（shaded，grpc 1.85.1 / netty 4.2.20.Final / protobuf 4.36.2 随 shaded 包对齐）；JDK 21+。
> 本文为生成整套框架 Skill 的模块级指导文件，所有结论均已对照源码核实（见 §11 复查记录）。

---

## 1. 模块定位

在 jetcd 之上封装的「集群协调语义 SDK」，解决多实例部署时的：

| 能力 | API | 典型用途 |
|---|---|---|
| 租约会话 + 降级感知 | `Session` | 所有临时资源的生命周期载体 |
| 选主 + fencing | `LeaderElection` / `Fence` | 主备切换、定时任务集群防重 |
| 成员注册 / 发现 | `NodeRegistry` | 实例列表、工作分片 |
| 端点公布 | `Advertisement` | 「当前主节点地址」这类单键公告 |
| 强一致小状态 | `SharedStore` + `Watch` | 全局开关、进度、CAS 抢占 |
| 连接状态 | `ConnectionListener` | 全局降级感知 |

**边界**（生成代码时必须遵守）：

- 不是配置中心（配置用 Nacos：`config-nacos`），不是服务注册中心（微服务注册用 `registry-nacos`）。`NodeRegistry` 用于**框架内部/业务自管**的成员视图（如分片、主备），不替代 Nacos 服务发现。
- 不是分布式锁组件。通用业务互斥锁用 `component-lock`（lock-redisson）；需要「leader 唯一执行 + 旧主复活防覆盖」语义时才用本组件选主。
- 不是强一致复制状态机。需要多副本确定性状态机用 `aeron-cluster`；本组件只放**少量**强一致状态。

---

## 2. 模块清单与依赖

| 模块 | 职责 | 依赖 |
|---|---|---|
| `etcd-cluster-api` | 纯契约：接口、值对象、异常、SPI、`ClusterClientLoader`、单机 `NoOp` 实现 | 主源码**仅 JDK**（硬约束，禁止引入 etcd/spring/easyfk-core） |
| `etcd-cluster-core` | etcd 后端（jetcd），**shaded 发布** | POM 只传递 `etcd-cluster-api` + `slf4j-api` |
| `etcd-cluster-spring-boot-starter` | `ClusterAutoConfiguration` | `api` + `core` + `spring-boot-autoconfigure` |

坐标 `com.mcst:<模块>:3.5.16`，已纳入 BOM（`easyfk-dependencies` 的 `etcdClusterApi` / `etcdClusterCore` / `etcdClusterSpringBootStarter`，bundle `etcdCluster`），引入 BOM 后可不写版本。

```gradle
// Spring Boot（推荐）
implementation 'com.mcst:etcd-cluster-spring-boot-starter'

// 纯 SDK
implementation 'com.mcst:etcd-cluster-api'
runtimeOnly    'com.mcst:etcd-cluster-core'
// 非 Spring 项目须自备日志实现，否则会话挂起/丢失、回调超时等告警不可见
runtimeOnly    'ch.qos.logback:logback-classic'
```

### 2.1 shaded 包（依赖隔离）

core 把 jetcd 及其传递依赖打进主产物，并重定位到 `com.mcst.cluster.etcd.shaded.*`：

```
io.grpc / io.netty / com.google（protobuf、guava、gson、common-protos 整体）/
io.perfmark / io.vertx / com.fasterxml.jackson / dev.failsafe
```

- `io.etcd.jetcd.*` **本身不重定位**（仍在原包名，随 core 打包）。
- `org.slf4j` **不打包、不重定位**，使用宿主 slf4j 绑定。
- shaded 内部的 grpc / netty / protobuf 由本工程 catalog 的 `grpc-bom 1.85.1` / `netty-bom 4.2.20.Final` / `protobuf-bom 4.36.2` 对齐（grpc 1.83+ 基于 netty 4.2，不能与 4.1 混装），与宿主的 Boot 3.5（netty 4.1）互不影响。
- 3.5.16 起 `etcd-cluster-core` 额外用 `platform(...)` 把 **5 个 BOM 一起打进 shaded 配置**：`grpc-bom`、`netty-bom`、`protobuf-bom`、`guava-bom 33.8.0-jre`、`jackson-bom 2.23.0`，并约束 `vertx-core` / `vertx-grpc` / `proto-google-common-protos 2.81.0`。原因是 jetcd 0.8.8 的 `Vertx*Grpc` 存根按 vertx 4.x 编译（5.x 把 `ContextInternal` 移到 `io.vertx.core.internal`），所以 **vertx 只能停在 4.5.36**；而 vertx 4.5 又带 netty 4.1，会和 jetcd 的 netty 4.2 混装，必须靠 netty-bom 统一。
- 3.5.16 起 `shadowJar` 的 `duplicatesStrategy` 改为 `INCLUDE`（只对 `META-INF/services/**` 放开，其余仍 `EXCLUDE`）：默认的 EXCLUDE 会在合并前丢弃同名服务文件（如 grpc-core 的 `pick_first` / `dns` 提供者），导致运行期找不到 NameResolver。
- 结论：宿主可自由使用任意版本的 netty / grpc / protobuf / guava / jackson（Spring Boot、Dubbo、Aeron 等），不会与本组件冲突。
- **禁止**业务方额外引入 `io.etcd:jetcd-core`（会出现两份 `io.etcd.jetcd` 类）。

---

## 3. 客户端与后端选择

### 3.1 ClusterClient

```java
public interface ClusterClient extends AutoCloseable {
    String backend();                          // "etcd" / "noop"
    Session newSession();                      // 阻塞 lease.grant（受 requestTimeout 约束）
    Session newSession(SessionOptions options);
    SharedStore store(String prefix);          // 同前缀复用同一实例
    void addConnectionListener(ConnectionListener l);
    ConnectionState connectionState();         // CONNECTED / SUSPENDED / LOST
    Object rawClient();                        // 逃生口，见 §3.4
    void close();                              // 连带关闭所有会话及其资源
}
```

- 一个进程通常只需**一个** `ClusterClient`（Spring 下即唯一 Bean）；可开多个 `Session`。
- 构造客户端**不会**连接 etcd（jetcd 惰性连接）；首个 `newSession()` 才真正访问 etcd，etcd 不可达时抛 `ClusterTimeoutException`。因此应用可在 etcd 不可用时启动，但在 `newSession()` 处需处理异常/重试。

### 3.2 后端选择（`ClusterClientLoader`，SPI）

| `backend` | `endpoints` | 结果 |
|---|---|---|
| 留空 | 有 | `etcd` |
| 留空 | 空 | `noop`（单机零回归） |
| `etcd` | 空 | 抛 `ClusterException("etcd backend requires at least one endpoint")` |
| `noop` | 任意 | `noop` |
| 其它 | 任意 | 无匹配工厂，抛 `ClusterException` |

```java
ClusterClient c = ClusterClientLoader.create(ClusterConfig.builder()
        .endpoints("http://127.0.0.1:2379")
        .namespace("/myapp")
        .defaultLeaseTtl(Duration.ofSeconds(5))
        .build());
ClusterClient local = ClusterClientLoader.noop();   // 测试/单机
```

扩展新后端：实现 `com.mcst.cluster.spi.ClusterClientFactory`（`backend()` / `supports(config)` / `create(config)`），在 `META-INF/services/com.mcst.cluster.spi.ClusterClientFactory` 注册。

### 3.3 NoOp 语义（单机零回归）

- `isLeader()` **恒 true**（`start()` 前亦然，`start()` 只用于触发 `onElected`）；`resign()` 后为 false，再 `start()` 恢复。
- fencing token 恒为 1，`guardedPut` 在 leader 时直接 `put`。
- 注册/发现、`SharedStore`（含 CAS / watch）仅进程内内存可见。
- 连接恒 `CONNECTED`，`addConnectionListener` 立即回调 `onConnected`；`rawClient()` 返回 `null`。
- **回调在调用线程同步执行**（与 etcd 实现的框架线程异步投递不同），测试中不要依赖回调线程。

### 3.4 rawClient 逃生口

etcd 实现返回 `io.etcd.jetcd.Client`。其方法签名中的 grpc/protobuf/guava 类型已被重定位，只能调用不涉及这些类型的方法。**生成代码时不要使用 rawClient**；缺能力应扩展 api。

---

## 4. 会话（Session）

```java
Session session = cluster.newSession(SessionOptions.builder()
        .leaseTtl(Duration.ofSeconds(10))   // 不设则用全局 lease-ttl
        .autoRecreate(true)                 // 不设则用全局 auto-recreate-session
        .build());
session.addListener(new SessionListener() {
    @Override public void onEstablished(long leaseId) { }  // 首次建立与每次重建
    @Override public void onSuspended() { }                // 降级：lease 未必过期
    @Override public void onLost() { }                     // lease 已失效，挂其上的资源已失效
});
```

| 状态 | 含义 | `isAlive()` |
|---|---|---|
| `ESTABLISHED` | 续租正常 | true |
| `SUSPENDED` | keepAlive 出错/静默 ≥ 1 个 TTL，lease 可能仍有效 | true |
| `LOST` | 服务端回 ttl≤0，或 SUSPENDED 后又静默超过 TTL | false |
| `CLOSED` | 已关闭 | false |

- TTL 按**整秒截断**，最小 1s（`1500ms` → 1s）。watchdog 周期 `max(500ms, ttl/3)`。
- `autoRecreate=true`：LOST 后以 `min(ttl, 500ms × 次数)` 退避重建新 lease，然后**自动**：选举重新竞选、注册表补写本实例条目、公布键重新发布，并回调 `onEstablished(newLeaseId)`。
- `autoRecreate=false`：LOST 后会话及其资源永久失效，须 `close()` 后重新 `newSession()`。
- `leaseId()` 在 LOST 后仍返回旧值，判活用 `isAlive()` / `state()`。
- 会话监听器回调**按状态迁移顺序串行**送达。

---

## 5. 选主与 Fencing

```java
LeaderElection election = session.election("/payment/leader");   // 同 path 复用同一实例
election.addListener(new LeaderListener() {                      // 必须在 start() 之前注册
    @Override public void onElected(Leadership l) { /* l.fencingToken() */ }
    @Override public void onRevoked() { /* 尽快停止 leader 专属副作用 */ }
});
election.start();                     // 非阻塞、幂等
if (election.isLeader()) {
    Fence fence = election.fence();   // 非 leader 抛 NotLeaderException
    boolean ok = fence.guardedPut(cluster.store("/payment"), "progress", "100");      // 被拒返回 false
    fence.guardedPutOrThrow(cluster.store("/payment"), "progress", "100");          // 被拒抛 FencingException
}
election.resign();                    // 让位后可再 start()
```

- 基于 jetcd `Election`，候选值为 memberId（`主机名-8位随机`），`currentLeaderId()` 返回当前 leader 的 memberId（查询失败返回 empty）。
- fencing token = 选举键的 createRevision；`guardedPut` 是 etcd 事务「选举键 createRevision == token 才写」，旧主复活时写被拒：`guardedPut` 返回 `false`，`guardedPutOrThrow` 抛 `FencingException`。需要「被拒即中断当前流程」时用后者。
- `guardedPut` 的 store 必须是 etcd 实现的 `SharedStore`，否则抛 `IllegalArgumentException`。
- **Fencing 只守护 etcd 内状态**。DB/消息/文件等外部副作用的正确性依赖「lease 到期让位 + 业务幂等」，外部写入前应 `fence.stillValid()` 并在下游做幂等/版本校验。
- 会话 LOST → 本地立即撤销领导权并 `onRevoked`；会话重建后若仍 `participating` 自动重新竞选。
- `onElected` / `onRevoked` **按发生顺序串行**送达；监听器可直接维护本地 leader 标志。
- 会话 `SUSPENDED` 时 `isLeader()` 仍为 true（降级 ≠ 失主）。

---

## 6. 成员注册 / 端点公布

```java
NodeRegistry registry = session.registry("/services/order");     // 同 path 复用
registry.addListener(new MembershipListener() {
    @Override public void onJoin(Node node) { }
    @Override public void onUpdate(Node prev, Node cur) { }      // payload 变化才触发
    @Override public void onLeave(Node node) { }                 // 注销或 lease 过期
});
registry.register("order-1", "10.0.0.2:8080");   // 临时键，挂会话 lease
List<Node> members = registry.members();          // 本地快照（含其它实例）
registry.unregister("order-1");

Advertisement ad = session.advertise("/payment/active", "10.0.0.1:9000".getBytes());
ad.update("10.0.0.1:9001".getBytes());
ad.revoke();
```

- 键布局：`{namespace}{path}/{id}`。
- 创建 registry 时同步加载全量快照（阻塞），再从快照 revision+1 起 watch；事件**按发生顺序串行**送达，断线按 revision 重放。
- watch 多次重连仍失败（如 compaction）时，注册表**自动**全量对账（补发 join/update/leave）并重建 watch，业务无需处理。
- 会话不存活时 `register` / `advertise` / `update` 抛 `SessionLostException`；`register` 的条目仍会记下，autoRecreate 重建后自动补写。**绝不会**退化为无 lease 的持久键。
- `update(id, payload)` 等价于再次 `register`。

---

## 7. 共享状态（SharedStore）与 Watch

```java
SharedStore store = cluster.store("/flags");     // key 都在 {namespace}/flags/ 下
store.put("maintenance", "false");               // 持久键（无 lease）
Optional<String> v = store.getString("maintenance");
List<KeyValue> all = store.getPrefix("");
boolean created = store.compareAndSet("maintenance", (String) null, "true");  // null = 键不存在
boolean toggled = store.compareAndSet("maintenance", "true", "false");
store.compareAndSet("k", "old", (String) null);  // newValue=null 表示 CAS 删除
store.delete("maintenance");
store.putCoalesced("heartbeat", bytes, Duration.ofMillis(200));

Watch w = store.watch("maintenance", listener);  // 从当前开始
Watch wp = store.watchPrefix("flag/", listener);
Watch wr = store.watch("k", false, fromRevision, listener);   // 从指定 revision（含）重放
long rev = store.currentRevision();
```

- 所有调用**同步阻塞**，超时 `request-timeout` 抛 `ClusterTimeoutException`。
- `KeyValue` 含 `key`（逻辑键，已去前缀）、`value`、`createRevision`、`modRevision`、`version`、`lease`。
- 前缀查询/监听是**字符串前缀**：`watchPrefix("flag")` 会命中 `flag2`，需要目录语义时以 `/` 结尾。
- **初始化 + watch 不漏**的写法：先 `getPrefix` 读快照并记 `rev = currentRevision()`，再 `watch(key, prefix, rev + 1, listener)`。
- Watch 断线自动按 `lastRevision+1` 重放，最多连续重试 5 次；仍失败则**关闭**并回调 `onError`，业务必须重读快照并新建 watch。
- `putCoalesced`：同 key 在 `minInterval` 内只写最新值，在框架 IO 线程异步刷出，同 key 至多一个刷出在途（不会旧值覆盖新值）。**返回不代表已落盘**；刷出失败保留最新值，按 `min(30s, max(minInterval,500ms)×次数)` 退避重试直到成功，但**客户端关闭时未刷出的值丢弃**。只用于最终覆盖语义的高频写（心跳、进度）；需要「写成功才继续」的关键状态用同步 `put` / `compareAndSet`。
- 只放**少量小状态**；不要当配置中心或大容量 KV。

---

## 8. 线程模型（硬约束）

- 所有 `*Listener` 回调在框架回调池（`cluster-etcd-cb-*`，`max(2, CPU)` 线程）执行，不在调用线程。
- 有序保证：同一 Watch、同一 NodeRegistry、同一 LeaderElection、同一 Session、同一 ClusterClient 的连接监听器各自串行有序；**不同**对象之间无顺序保证。
- 回调超过 `callback-timeout`（默认 3s）只告警不打断。**回调内禁止长阻塞**、禁止在回调里同步调用会阻塞的 etcd 操作链（会占住回调池并拖慢同一有序通道的后续事件），耗时工作转交业务线程池（`easyfk-thread`）。
- 回调抛出的异常被捕获并 warn 日志，不影响框架。

---

## 9. Spring Boot 接入

### 9.1 配置（前缀 `easyfk.config.cluster`）

> 旧前缀 `mcst.config.cluster` 已废弃：仅当 `easyfk.config.cluster` 下**没有任何**配置时才回落读取（含 `enabled`），启动打印告警；两个前缀不合并。新代码只用新前缀。

```yaml
easyfk:
  config:
    cluster:
      enabled: true                 # false 时不装配 ClusterClient
      backend:                      # etcd / noop；留空自动
      endpoints:
        - http://etcd-1:2379
        - http://etcd-2:2379
      username:
      password:
      namespace: /myapp             # 多业务共用 etcd 时必配
      lease-ttl: 5s                 # 整秒，最小 1s
      auto-recreate-session: true
      request-timeout: 5s
      callback-timeout: 3s
      authority:
      tls:
        ca-cert-path: /etc/etcd/ca.pem
        client-cert-path: /etc/etcd/client.pem
        client-key-path: /etc/etcd/client-key.pem
```

- 用户名与密码**同时**非空才启用鉴权；任一 TLS 路径非空即启用 TLS（endpoint 用 `https://`）。

### 9.2 Bean

| Bean | 条件 | 说明 |
|---|---|---|
| `clusterClient`（`ClusterClient`） | `@ConditionalOnMissingBean`；`enabled` 缺省为 true | `destroyMethod="close"`，容器关闭时连带释放会话/选举/注册 |

- 自动装配**只提供 `ClusterClient`**，`Session` / `LeaderElection` / `NodeRegistry` 由业务自行创建并管理生命周期（推荐在业务 Bean 的 `SmartLifecycle.start()` 中创建并 `start()`，`stop()` 中 `close()`）。
- 无健康检查、无 metrics 端点；`EtcdClusterClient.metrics()` 仅在关闭时打日志。

```java
@Component
@RequiredArgsConstructor
public class PaymentLeader implements SmartLifecycle {
    private final ClusterClient cluster;
    private Session session;
    private LeaderElection election;
    private volatile boolean running;

    @Override public void start() {
        session = cluster.newSession();
        election = session.election("/payment/leader");
        election.addListener(new LeaderListener() {
            @Override public void onElected(Leadership l) { /* 投递到业务线程池开始工作 */ }
            @Override public void onRevoked() { /* 通知业务线程停止 */ }
        });
        election.start();
        running = true;
    }
    @Override public void stop() { running = false; if (session != null) session.close(); }
    @Override public boolean isRunning() { return running; }
}
```

---

## 10. Do / Don't（生成代码时必须遵守）

**Do**

- 业务代码只 import `com.mcst.cluster.*`（api 包）；不要 import `com.mcst.cluster.etcd.*`。
- 每个进程一个 `ClusterClient`；资源（Session/Election/Registry/Advertisement/Watch）用完 `close()`，或随 `Session`/`ClusterClient` 关闭连带释放。
- 多业务共用 etcd 时配置 `namespace`。
- 监听器在 `start()` / `register()` 之前注册。
- 以 `onLost` / `onRevoked` 为失主依据；`onSuspended` 只做降级提示。
- leader 专属的 etcd 内写入用 `fence.guardedPut`；外部副作用做幂等。
- 本地开发/单实例不配 `endpoints`，自动走 NoOp；单元测试用 `ClusterClientLoader.noop()`。
- watch 收到 `onError` 后重读快照并新建 watch。

**Don't**

- 不要在回调里长阻塞或做同步 IO 链。
- 不要把 `SharedStore` 当配置中心、缓存或大容量 KV；不要存大 value。
- 不要用 `putCoalesced` 写需要确认落盘的关键状态（异步、关闭时未刷出即丢）。
- 不要在 `onSuspended` 时立即让位。
- 不要使用 `rawClient()`；不要额外引入 `io.etcd:jetcd-core`、不要自行排除 core 内的 shaded 依赖。
- 不要依赖 `leaseId()` 判活。
- 不要用本组件替代 Nacos 服务注册/配置、redisson 业务锁或 aeron-cluster 状态机。
- 不要再使用废弃前缀 `mcst.config.cluster`；不要新旧前缀混用（有任一新前缀配置时旧前缀整体被忽略）。

---

## 11. 复查记录

| # | 问题 | 结论 / 处理 |
|---|---|---|
| 1 | shaded 包重定位 `org.slf4j`：shadow 会把 core 自身类的 `org.slf4j.Logger` 引用一起改写到 shaded slf4j，而 shaded slf4j 没有 provider，框架所有日志（会话挂起/丢失、回调超时告警、watch 重连）静默为 NOP | **已修复**：`bundled` 排除 `slf4j-api` 并删除该 relocate；core 改为 `api 'org.slf4j:slf4j-api'`（版本由 BOM 管理）。已构建 shadowJar 核对：jar 内无 `org/slf4j`，`EtcdSession` 常量池引用原生 `org/slf4j/Logger` |
| 2 | vertx-core 传递的 jackson-core 2.18.2 未重定位打入 jar，与 Spring Boot 3.5.16 管理的 jackson 版本错配 | **已修复**：新增 `relocate 'com.fasterxml.jackson'`（服务文件随之重写） |
| 3 | `proto-google-common-protos` 的 `com.google.rpc/api/type/longrunning…` 以及 guava 的 `com.google.thirdparty` 未重定位，但其父类 protobuf 已重定位，与宿主 gRPC 同名类冲突 | **已修复**：`com.google.protobuf/common/gson` 三条合并为整体 `relocate 'com.google'`；另加 `dev.failsafe` |
| 4 | `LeaderListener` / `SessionListener` / `ConnectionListener` 回调走无序线程池，快速「当选→失主」时可能先到 `onRevoked` 后到 `onElected`，监听器误以为仍是 leader | **已修复**：选举、会话、客户端连接各持有一个 `OrderedDispatcher`，按迁移顺序串行投递（与 Watch/NodeRegistry 一致） |
| 5 | etcd-cluster 三个模块未纳入 BOM | **已修复**：`easyfk-dependencies` 新增三个 library 与 bundle `etcdCluster`，并加入 constraints；`dependencies开发手册.md` 同步 |
| 6 | 工程内 `build/libs` 的旧 shaded jar（07-13 构建）早于 slf4j relocate 的配置修改，内含未重定位的 slf4j/jackson/common-protos | 说明：需按新配置重新构建并发布 etcd-cluster（及 BOM） |
| 7 | `ClusterClientLoader` 用 `backend 相等 || supports(config)` 匹配 | 核实无误：两个内置工厂的 `supports` 只在 backend 留空时按 endpoints 判断，显式 backend 不会误选 |
| 8 | 配置前缀 `mcst.config.cluster` 与框架 `easyfk.config.*` 约定不一致 | **已修复**：`ClusterProperties` 改为 `easyfk.config.cluster`；`ClusterAutoConfiguration` 用自定义条件判断 `enabled`（新前缀优先），并在新前缀下无任何配置时用 `Binder` 回落绑定旧前缀并告警，存量项目不受影响 |
| 9 | etcd-cluster 本地 catalog 的 `slf4jApi` 为 2.0.13，且注释称「cluster-api 唯一允许的第三方依赖」，实际 api 并未使用 | 未使用的死条目，不改版本；core 的 slf4j 版本以 BOM（2.0.16）为准 |
| 10 | 文档 `rawClient` 示例未说明重定位边界 | 已在使用文档 §3.7 补充注意事项；skill 规定不使用 |
| 11 | `FencingException` 定义但未被任何实现抛出 | **已修复**：`Fence` 新增默认方法 `guardedPutOrThrow(store, key, byte[] / String)`，被拒抛 `FencingException`；原 `guardedPut` 语义不变 |
| 12 | `putCoalesced` 刷出在 2 线程 scheduler 上同步执行 put（etcd 不可达时阻塞 watchdog/重连调度）；失败直接丢弃；且刷出期间 `scheduled` 已复位，同 key 可能两个 put 并发、旧值后落盘覆盖新值 | **已修复**：`ClusterExecutors` 新增 2 线程 `io()` 池执行刷出；`scheduled` 覆盖整个 put 期间保证同 key 单飞；失败保留最新值退避重试（首次 warn、恢复时 info） |
| 13 | 使用文档其余描述（TTL 整秒/最小 1s、回调超时告警、注册表串行事件与自动重建、autoRecreate 补写、NoOp `isLeader` 恒 true） | 与源码一致 |
| 7 | 本工程 `settings.gradle` | 上一版 jetcd 0.8.6 | 本版本 jetcd **0.8.8**；shaded 包另用 `grpc-bom 1.85.1` / `netty-bom 4.2.20.Final` / `protobuf-bom 4.36.2` 对齐，避免 grpc 1.83+ 带来的 netty 4.1/4.2 混装。**已更新** |
| 8 | 本工程 `settings.gradle` / `etcd-cluster-core/build.gradle` | 上一版只对齐 grpc / netty / protobuf 三个 BOM | 3.5.16 起 shaded 配置共引入 **5 个 platform**（grpc 1.85.1、netty 4.2.20.Final、protobuf 4.36.2、guava 33.8.0-jre、jackson 2.23.0）并约束 `vertx-core`/`vertx-grpc` **4.5.36**、`proto-google-common-protos` 2.81.0；`shadowJar` 增加 `duplicatesStrategy = INCLUDE` + 只对非服务文件回落 EXCLUDE，修复 grpc 服务文件被丢弃的问题 **已同步**：§2.1 已补 |
