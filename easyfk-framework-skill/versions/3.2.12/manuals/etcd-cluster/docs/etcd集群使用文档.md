# 集群管理框架（Cluster Management）使用文档

> 面向接入方：如何引入、配置与使用本框架完成选主、成员注册/发现、端点公布、强一致小状态共享。
> 实现原理见《设计文档》。

---

## 1. 引入依赖

- 坐标 group：`com.mcst`
- 当前版本：`3.2.12`（与仓库 / `easyfk-dependencies` BOM 一致）
- 运行要求：**JDK 21+**

### 1.1 Spring Boot 项目（推荐）

```gradle
dependencies {
    implementation 'com.mcst:etcd-cluster-spring-boot-starter:3.2.12'
}
```

starter 传递 `etcd-cluster-api` 与 `etcd-cluster-core`，并通过 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 自动装配一个 `ClusterClient` Bean（业务项目无需再 `@Import` / 复制自动装配类）。starter 自身只额外依赖 `spring-boot-autoconfigure`，使用方需已有 Spring Boot 运行时。

### 1.2 纯 SDK 项目（不依赖 Spring）

```gradle
dependencies {
    implementation 'com.mcst:etcd-cluster-api:3.2.12'   // 编译期只依赖契约
    runtimeOnly    'com.mcst:etcd-cluster-core:3.2.12'  // 运行期提供 etcd 实现（SPI）
}
```

> 业务代码只 import `com.mcst.cluster.*` 的 **api** 包，不要直接依赖 `etcd` 实现包，便于后端可插拔与依赖隔离。
>
> core 只传递 `slf4j-api`，非 Spring 项目需自备日志实现（如 `logback-classic`），否则 etcd 相关日志（会话挂起/丢失、回调超时告警等）不可见。

---

## 2. 快速开始

### 2.1 Spring Boot

`application.yml`（配置前缀 `easyfk.config.cluster`）：

> 旧前缀 `mcst.config.cluster` 已废弃：仅当新前缀下没有任何配置时才回落读取（启动打印告警），两者不合并，请尽快迁移。

```yaml
easyfk:
  config:
    cluster:
      enabled: true                 # 默认 true；false 时不装配 ClusterClient
      endpoints:                    # 为空则回落单机 NoOp（零回归）
        - http://127.0.0.1:2379
      namespace: /myapp             # 全局 key 前缀（命名空间隔离）
      lease-ttl: 5s
      auto-recreate-session: true
      request-timeout: 5s
      callback-timeout: 3s
      # username / password / authority / tls.* 按需
```

注入使用：

```java
@Service
public class MyService {
    private final ClusterClient cluster;

    public MyService(ClusterClient cluster) {
        this.cluster = cluster;
    }
}
```

### 2.2 纯 SDK

```java
ClusterConfig config = ClusterConfig.builder()
        .endpoints("http://127.0.0.1:2379")
        .namespace("/myapp")
        .defaultLeaseTtl(Duration.ofSeconds(5))
        .build();

try (ClusterClient cluster = ClusterClientLoader.create(config)) {
    // ... 使用 cluster
}

// 单机零回归（无需 etcd）：
ClusterClient local = ClusterClientLoader.noop();
```

---

## 3. 核心用法

### 3.1 会话（Session）

选主 / 注册 / 公布都挂在会话上，会话关闭即连带释放。

```java
Session session = cluster.newSession();              // 默认会话选项
// 或自定义：
Session s2 = cluster.newSession(SessionOptions.builder()
        .leaseTtl(Duration.ofSeconds(10))
        .autoRecreate(true)
        .build());

session.addListener(new SessionListener() {
    @Override public void onEstablished(long leaseId) { }
    @Override public void onSuspended() { }   // 降级：lease 未过期，不要立即让位/停副作用
    @Override public void onLost() { }        // lease 过期：挂其上的资源已失效
});
```

### 3.2 选主 + Fencing（主备/防重）

```java
Session session = cluster.newSession();
LeaderElection election = session.election("/payment/leader");

election.addListener(new LeaderListener() {
    @Override public void onElected(Leadership leadership) {
        // 当选：可开始只允许 leader 执行的工作
    }
    @Override public void onRevoked() {
        // 失主：尽快停止 leader 专属副作用
    }
});
election.start();   // 非阻塞；多次调用幂等

if (election.isLeader()) {
    Fence fence = election.fence();                  // 非 leader 时抛 NotLeaderException
    SharedStore store = cluster.store("/payment");
    // 守护写：旧主复活时该写会被拒（仅守护 etcd 内状态）
    boolean ok = fence.guardedPut(store, "progress", "100");
    // 或：被拒时抛 FencingException
    fence.guardedPutOrThrow(store, "progress", "100");
}

election.resign();  // 主动让位，可再次 start() 参与竞选
```

> **Fencing 边界**：`guardedPut` 只能保证 etcd 内状态不被旧主覆盖；对 DB/消息/文件等**外部副作用**，正确性须依赖「lease 到期让位 + 业务幂等」。

### 3.3 成员注册与发现

```java
Session session = cluster.newSession();
NodeRegistry registry = session.registry("/services/order");

registry.addListener(new MembershipListener() {
    @Override public void onJoin(Node node) { }
    @Override public void onLeave(Node node) { }     // 主动注销或 lease 过期
    @Override public void onUpdate(Node prev, Node cur) { }
});

registry.register("order-1", "10.0.0.2:8080");       // 本实例条目挂 lease，会话失效自动消失
List<Node> members = registry.members();             // 当前成员快照
registry.unregister("order-1");
```

事件保证：同一注册表上的 `onJoin/onUpdate/onLeave` **按发生顺序串行**送达；断线重连后按 revision 重放，调用方无需自行去重。

### 3.4 端点公布

```java
Advertisement ad = session.advertise("/payment/active", "10.0.0.1:9000".getBytes());
ad.update("10.0.0.1:9001".getBytes());   // 更新公布值
ad.revoke();                              // 主动撤销（会话失效也会自动撤销）
```

### 3.5 强一致共享状态（SharedStore）

适用于全局开关、进度、CAS 抢占等**少量**强一致状态（非通用大容量 KV）。

```java
SharedStore store = cluster.store("/flags");

// 读写
store.put("maintenance", "false");
Optional<String> v = store.getString("maintenance");
List<KeyValue> all = store.getPrefix("");

// CAS：expected 传 null 表示「键不存在」
boolean created = store.compareAndSet("maintenance", (String) null, "true");
boolean toggled = store.compareAndSet("maintenance", "true", "false");

// 高频写收敛（窗口内只保留最新值，异步刷出，保护写预算；失败保留最新值退避重试，客户端关闭时未刷出的值丢弃）
store.putCoalesced("heartbeat", "1".getBytes(), Duration.ofMillis(50));

// watch（断线自动重放；不可恢复时回调 onError，应重读快照并重建）
Watch watch = store.watch("maintenance", new WatchListener() {
    @Override public void onEvents(List<WatchEvent> events) { }
    @Override public void onError(Throwable error) { }
    @Override public void onClosed() { }
});
// 也可：store.watchPrefix("flag/", listener)
watch.close();
```

### 3.6 连接降级感知

```java
cluster.addConnectionListener(new ConnectionListener() {
    @Override public void onConnected() { }
    @Override public void onSuspended() { }   // 抖动/暂不可达，lease 未过期：不要立即让位
    @Override public void onLost() { }        // lease 过期/长时间不可达
});
ConnectionState state = cluster.connectionState();
```

### 3.7 逃生口：原生客户端

```java
Object raw = cluster.rawClient();        // etcd 实现下为 jetcd Client；NoOp 返回 null
if (raw instanceof io.etcd.jetcd.Client client) {
    // 小众/高级需求直接操作原生客户端
}
```

> 注意：`io.etcd.jetcd.*` 随 core 打包且**未重定位**，但其方法签名中的 grpc/protobuf/guava 类型均已重定位到 `com.mcst.cluster.etcd.shaded.*`。业务方**不要**再额外引入 `io.etcd:jetcd-core`（会出现两份 `io.etcd.jetcd` 类）；需要原生能力时只调用不涉及重定位类型的方法，或优先提需求扩展 api。

---

## 4. 典型场景

| 场景 | 组合 |
|---|---|
| 主备服务选主 + 故障切换 | `LeaderElection` + `Fence` + `Advertisement` + `SharedStore` |
| 定时任务集群防重 | `LeaderElection`（同一时刻只一个实例执行） |
| 微服务实例注册/发现 | `NodeRegistry` + watch |
| 强一致全局开关/进度 | `SharedStore` 的 CAS / watch / `putCoalesced` |
| 工作分片/任务认领 | `NodeRegistry`（成员）+ `SharedStore`（CAS 抢占） |

示例（任务认领）：

```java
NodeRegistry registry = session.registry("/workers");
registry.register("worker-1", "");
SharedStore tasks = cluster.store("/tasks");
boolean claimed = tasks.compareAndSet("shard-0", (String) null, "worker-1"); // 抢占成功
```

---

## 5. 配置参考

前缀 `easyfk.config.cluster`（Spring）/ `ClusterConfig.builder()`（SDK）：

| 配置 | 默认 | 说明 |
|---|---|---|
| `enabled` | true | 仅 Spring：false 时不装配 Bean |
| `backend` | 自动 | `etcd` / `noop`；留空按是否配 endpoints 自动选择 |
| `endpoints` | 空 | etcd 地址列表；为空回落 NoOp |
| `username` / `password` | 空 | etcd 鉴权 |
| `namespace` | `""` | 全局 key 前缀 |
| `lease-ttl` / `defaultLeaseTtl` | 5s | 会话租约 TTL（按整秒解析，最小 1s） |
| `auto-recreate-session` | true | 会话丢失后自动重建并重发选举/注册 |
| `request-timeout` | 5s | 单次 etcd 请求超时 |
| `callback-timeout` | 3s | 回调超时告警阈值 |
| `authority` | 空 | gRPC authority |
| `tls.ca-cert-path` | 空 | CA 证书路径 |
| `tls.client-cert-path` / `tls.client-key-path` | 空 | 客户端证书/私钥（双向 TLS） |

TLS 示例：

```yaml
easyfk:
  config:
    cluster:
      endpoints:
        - https://etcd-1:2379
      tls:
        ca-cert-path: /etc/etcd/ca.pem
        client-cert-path: /etc/etcd/client.pem
        client-key-path: /etc/etcd/client-key.pem
```

---

## 6. 最佳实践与注意事项

- **回调内禁长阻塞**：所有 `*Listener` 回调由框架专用线程调度，框架会对超过 `callback-timeout` 的回调告警。耗时工作请转交业务线程池。
- **降级 ≠ 失主**：收到 `onSuspended` 时 lease 尚未过期，**不要**立即让位或停止副作用；以 `onLost` / `onRevoked` 为准。
- **Fencing 只护 etcd 内状态**：外部副作用靠 lease 到期让位 + 业务幂等保证正确性。
- **watch 不漏不重**：断线重连按 revision 重放；收到 `onError`（如 compaction 不可恢复）应重读全量快照并重建（`NodeRegistry` 已内建自动重建）。
- **SharedStore 是小状态**：不要当配置中心/大容量 KV 用；高频写用 `putCoalesced` 收敛。
- **namespace 隔离**：多业务共用一套 etcd 时用 `namespace` 前缀隔离 key 空间。
- **资源释放**：`Session`/`LeaderElection`/`NodeRegistry`/`Advertisement`/`Watch` 均实现 `AutoCloseable`；`ClusterClient` 关闭会连带关闭其下所有会话与资源（Spring 下由容器 `destroy` 调用 `close`）。
- **单机零回归**：本地开发或单实例部署不配 `endpoints` 即走 NoOp，`isLeader()` 恒 true，行为等同单机。

---

## 7. 故障排查

| 现象 | 可能原因 / 处理 |
|---|---|
| `No ClusterClientFactory found for backend='etcd'` | 运行期 classpath 缺 `etcd-cluster-core`，确认已作为 `runtimeOnly` 引入 |
| 启动即走 NoOp | 未配置 `endpoints` 或 `backend` 未设为 `etcd` |
| 频繁 `onSuspended/onLost` | etcd 不可达/抖动或 `lease-ttl` 过小；检查网络与 TTL |
| `SessionLostException`（register/advertise） | 会话当前不存活；待 `onEstablished` 后重试（autoRecreate 会自动补写已注册条目） |
| watch 收到 `onError` | revision 被 compaction 等不可恢复错误；重读快照并重建 watch |
| 与业务进程 netty/protobuf 冲突 | 确认使用的是 core 的 shaded 发布包（grpc/netty/protobuf 已重定位） |
