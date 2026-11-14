# Cluster SDK 使用手册

> 受众: aeron-cluster 框架的<b>业务方使用者</b>. 不需要懂 Aeron / Raft 内部细节即可上手.
> 想了解内部原理 / 升级框架: 见 docs/Cluster架构设计.md.

## 目录

- 1. 项目定位
- 2. 适用场景与不适用场景
- 3. 5 分钟快速上手
- 4. 状态机 (ClusterStateMachine) 详解
- 5. 客户端 (ClusterClient) 详解
- 6. Snapshot
- 7. Spring Boot 集成
- 8. 测试夹具
- 9. 部署
- 10. 可观测性
- 11. 常见模式 / 食谱
- 12. 故障排查 FAQ
- 13. 版本兼容矩阵

## 1. 项目定位

aeron-cluster 是基于 Aeron Cluster (Raft 共识) 的<b>状态机式 RPC 框架</b>:

- 业务方写一个<b>状态机类</b> (实现 `ClusterStateMachine<C>`), 框架负责: 复制日志 / 选主 / 持久化 / 故障转移.
- 业务方写一个<b>客户端调用</b> (`client.sendAndAwait(codec, command, respCodec, timeoutMs)`), 拿到一个 `CompletableFuture<R>`.
- 框架保证: 命令在多数派提交后才会被状态机消费, 状态机回放结果对业务<b>线性一致</b>.

简单来说就是: 你写业务逻辑, 框架给你"高可用 + 强一致"; 你不需要懂 Raft, 也不需要懂 Aeron.



## 2. 适用场景与不适用场景

### 2.1 推荐用 cluster

- 配置中心 / 元数据中心 (高读低写, 强一致).
- 分布式锁 / 序列号生成器.
- 任务调度协调器 (谁在哪个分片上跑).
- 路由 / 拓扑 / 服务注册的<b>权威源</b>.
- 高可用计数器 / 计数池 / 限流配额.
- 小型订单引擎 / 撮合引擎 (微秒级延迟).

特征: 业务状态<b>能放进单机内存</b> (典型 < 10 GB), 写操作<b>线性一致</b>胜过吞吐, 节点故障要求自动 fail-over.

### 2.2 不要用 cluster

- 海量数据存储 (几十 GB 起步) -> 用真正的 DB / 分布式存储.
- 高吞吐消息总线 (>10 万 TPS 单分区) -> 用 broadcast 仓库 aeron, 或 Kafka.
- 异步事件流处理 -> 用消息队列, 不用 RPC.
- 跨地域 (跨 region) 强一致 -> Raft 不友好高延迟链路, 考虑专门方案.

### 2.3 与 broadcast SDK 的关系

| 项 | broadcast (aeron) | cluster (aeron-cluster) |
|---|---|---|
| 解决问题 | 高吞吐多对多消息总线 | 强一致 RPC + 状态机 |
| 一致性 | 至少一次 / 至多一次 | 线性一致 |
| 典型 TPS | 单 stream 百万级 | 万级 (受 Raft 限制) |
| 延迟 | 单边几十微秒 | 端到端毫秒级 (3 节点 round trip) |
| 是否需要选主 | 否 | 是 |
| 节点数 | 1 (broker) + N (consumer) | 3 / 5 / 7 (奇数) |

两者完全独立: cluster 仓库不依赖 broadcast jar, 只共用 `aeron-common` 的 `Codec<T>` 接口契约.



## 3. 5 分钟快速上手

目标: 在本机起一个单节点集群, 跑一个简单计数器, 客户端发命令拿响应.

### 3.1 加依赖 (Gradle)

```groovy
dependencies {
    // 只需要客户端:
    implementation 'com.mcst:aeron-cluster-client:3.2.12'

    // 内嵌节点 (业务方做集群一员时):
    implementation 'com.mcst:aeron-cluster-core:3.2.12'

    // Spring Boot 集成 (推荐):
    implementation 'com.mcst:aeron-cluster-spring-boot-starter:3.2.12'

    // 测试夹具 (写 IT 时用; 已纳入 easyfk-dependencies BOM):
    testImplementation 'com.mcst:aeron-cluster-test:3.2.12'
}
```

### 3.2 实现状态机

```java
public final class CounterStateMachine implements ClusterStateMachine<Long> {

    public static final int BUSINESS_VERSION = 1;
    public static final Codec<Long> CODEC = new LongCodec();

    private long counter;

    @Override
    public void onCommand(ClusterSession session, Long command, ClusterContext ctx) {
        if (command == 0L) {
            session.respond(CODEC, counter);                    // GET
        } else {
            counter += command;                                  // ADD
            session.respond(CODEC, counter);
        }
    }

    @Override
    public void takeSnapshot(SnapshotWriter writer) {
        writer.writeHeader(SnapshotMagic.FRAMEWORK_VERSION_V1, BUSINESS_VERSION);
        writer.write(CODEC, counter);
    }

    @Override
    public void loadSnapshot(SnapshotReader reader) {
        reader.readHeader(BUSINESS_VERSION);
        if (reader.hasMore()) {
            counter = reader.read(CODEC);
        }
    }

    static final class LongCodec implements Codec<Long> {
        public byte codecId() { return (byte) 100; }   // 100 起的业务自定义段
        public Class<Long> type() { return Long.class; }
        public int encodedLength(Long v) { return Long.BYTES; }
        public int encode(Long v, MutableDirectBuffer buf, int off) {
            buf.putLong(off, v);
            return Long.BYTES;
        }
        public Long decode(DirectBuffer buf, int off, int len) {
            return buf.getLong(off);
        }
    }
}
```

### 3.3 起单节点 (用测试夹具最快)

```java
import com.mcst.aeron.cluster.test.fixture.EmbeddedSingleNodeCluster;
import com.mcst.aeron.cluster.test.wait.ClusterAwait;
import com.mcst.aeron.common.codec.CodecRegistry;

import java.nio.file.Files;

CodecRegistry codecs = CodecRegistry.minimal();
codecs.register(CounterStateMachine.CODEC);

try (EmbeddedSingleNodeCluster cluster =
         EmbeddedSingleNodeCluster.launch(new CounterStateMachine(), codecs, Files.createTempDirectory("demo"))) {

    ClusterAwait.untilLeaderElected(List.of(cluster.node()));
    ClusterAwait.untilConnected(cluster.client());

    Long resp1 = cluster.client()
            .sendAndAwait(CounterStateMachine.CODEC, 7L, CounterStateMachine.CODEC, 5_000L)
            .get(10, TimeUnit.SECONDS);
    System.out.println(resp1);   // 7

    Long resp2 = cluster.client()
            .sendAndAwait(CounterStateMachine.CODEC, 3L, CounterStateMachine.CODEC, 5_000L)
            .get(10, TimeUnit.SECONDS);
    System.out.println(resp2);   // 10

    Long get = cluster.client()
            .sendAndAwait(CounterStateMachine.CODEC, 0L, CounterStateMachine.CODEC, 5_000L)
            .get(10, TimeUnit.SECONDS);
    System.out.println(get);     // 10
}
```

到这里就结束了. 单节点集群完整跑通, 你写的业务状态机已经在工作.

> 5 分钟版本不涉及生产部署, 只验证 API 跑通. 真上生产请看 §9 部署章节.



## 4. 状态机 (ClusterStateMachine) 详解

### 4.1 接口签名

```java
public interface ClusterStateMachine<C> {
    // 节点启动后第一次回调, 早于任何 onCommand / loadSnapshot.
    default void onStart(ClusterContext ctx) {}

    // 一条命令已被 Raft 提交, 回放. 必须是确定性的.
    void onCommand(ClusterSession session, C command, ClusterContext ctx);

    // 业务通过 ctx.scheduleTimer 注册的定时器到期.
    default void onTimer(long timerId, ClusterContext ctx) {}

    // 节点角色变化 (LEADER / FOLLOWER / CANDIDATE / UNKNOWN).
    default void onRoleChange(ClusterRole role) {}

    // 客户端会话打开 / 关闭.
    default void onSessionOpen(ClusterSession session) {}
    default void onSessionClose(ClusterSession session, CloseReason reason) {}

    // Snapshot 读写.
    default void takeSnapshot(SnapshotWriter writer) {}
    default void loadSnapshot(SnapshotReader reader) {}

    // 节点关闭前最后回调 (尽力而为, 不保证一定回调).
    default void onStop() {}

    // 声明本状态机能识别的 codec id, 框架据此校验 wire 上的 codec id 合法性.
    default Set<Integer> declaredCommandCodecIds() { return Collections.emptySet(); }
}
```

### 4.2 类型参数 C 的用法

`C` 是命令域的<b>上界</b>. 业务方有多种命令时:

```java
public sealed interface OrderCommand permits Place, Cancel, Query {}
public record Place(long orderId, ...) implements OrderCommand {}
public record Cancel(long orderId) implements OrderCommand {}
public record Query(long orderId) implements OrderCommand {}

public final class OrderStateMachine implements ClusterStateMachine<OrderCommand> {
    @Override
    public void onCommand(ClusterSession session, OrderCommand cmd, ClusterContext ctx) {
        if (cmd instanceof Place p)         handlePlace(session, p);
        else if (cmd instanceof Cancel c)   handleCancel(session, c);
        else if (cmd instanceof Query q)    handleQuery(session, q);
    }
    // ...
}
```

每种命令<b>必须</b>有自己的 `Codec`, 且在客户端 / 服务端的 `CodecRegistry` 中都已注册.

### 4.3 ClusterContext 能做什么

`ctx` 由框架在每次回调时传入, 有效期仅在该回调内. <b>禁止</b>跨回调持有.

```java
ctx.memberId();              // 本节点 id
ctx.role();                  // LEADER / FOLLOWER / CANDIDATE / UNKNOWN
ctx.timeMs();                // wall clock (业务可注入 ClusterClock 覆盖)
ctx.clusterTimeMs();         // raft committed time (业务展示时间戳一律用这个!)
ctx.scheduleTimer(id, dl);   // 注册定时器, 到期回调 onTimer(id, ctx)
ctx.cancelTimer(id);         // 取消
ctx.idle();                  // 让出 CPU, 业务做长 CPU 计算时礼貌挂出
ctx.reportError(t);          // 异步上报错误到 metrics + log, 不打断状态机
```

### 4.4 ClusterSession 能做什么

```java
session.id();                            // raft 分配的全局唯一 id
session.sessionId();                     // 同 id() 但包成 SessionId 强类型
session.correlationId();                 // 当前命令的 corrId, 仅 onCommand 内有意义
session.responseCount();                 // 已 respond 次数 (debug)
session.respond(codec, value);           // 把 value 编码成 RESPONSE 发回客户端
session.respondBytes(payload);           // raw bytes 版本
session.close(CloseReason.SERVICE_ACTION); // 主动关闭
session.isOpen();                        // 是否还活着
```

`respond` 在 follower / candidate 上<b>静默丢弃</b>且不抛异常: 状态机回放路径上, follower 也会执行 onCommand, 但只有 leader 真正 publish RESPONSE; 这是设计如此, 业务方不需要特判角色.

### 4.5 线程模型 (硬约束)

所有回调都在 ClusteredServiceContainer 的<b>单线程 agent</b> 上同步执行. 这意味着:

- 禁止任何阻塞 IO (HTTP / DB / 文件 fsync).
- 禁止 `synchronized` / `ReentrantLock` (单线程, 加锁纯属浪费).
- 禁止长 CPU 计算 (>1ms 即影响整集群延迟).
- 禁止持有 Aeron 内部对象引用 (`Image` / `Publication` / `Counter`).
- 允许调 `ctx.scheduleTimer(...)` / `session.respond(...)` / `metrics.onXxx(...)`.

不可避免的长任务: cluster 状态机的硬约束是<b>所有状态变更必须确定性</b>, 因此"切线程异步算 + 把结果再喂回状态机"这条路不能简单使用 —— 异步线程的结果不会出现在 raft log 里, replay 时无法重现.

正确的做法只有两类:

1. <b>预计算法</b>: 把重活搬到客户端做, 状态机只接受已经算好的结果. 例如: 客户端先算 hash / 编号 / 报文, 再发命令把结果写进集群.
2. <b>外部数据 + 命令二步法</b>: 第一条命令记录"开始算", 业务层进程 (集群外) 监听该命令, 算完之后再通过<b>另一条命令</b>把结果写回集群. 集群上的 timer 只用于"超时兜底" (按 `ctx.clusterTimeMs() + deadlineMs` 调度).

```java
@Override
public void onCommand(ClusterSession session, MyCmd cmd, ClusterContext ctx) {
    if (cmd instanceof StartHeavy s) {
        jobs.put(s.jobId(), JobState.PENDING);
        ctx.scheduleTimer(s.jobId(), ctx.clusterTimeMs() + 30_000); // 30s 超时
        session.respond(ACK_CODEC, "queued");
        // 业务方独立服务监听 raft log, 在外部 CPU pool 算完后通过
        // client.send(FinishHeavyCodec, new FinishHeavy(jobId, result)) 回写
    } else if (cmd instanceof FinishHeavy f) {
        jobs.put(f.jobId(), JobState.DONE);
        ctx.cancelTimer(f.jobId());
    }
}

@Override
public void onTimer(long timerId, ClusterContext ctx) {
    if (jobs.get(timerId) == JobState.PENDING) {
        jobs.put(timerId, JobState.TIMEOUT);
    }
}
```

> 关键纪律: `ctx.scheduleTimer` / `session.respond` 都<b>只能</b>在状态机线程调用 (即 onCommand / onTimer / onSession* 回调内). 在自管线程上调它们会污染状态机, 且<b>必然</b>破坏确定性 —— snapshot replay 时无法重现. 详见 §11.3 timer 食谱.

### 4.6 确定性约束 (CRITICAL)

状态机回放时<b>必须</b>得到与上次完全相同的状态. 这意味着:

- 不能用 `System.currentTimeMillis()` 直接做业务时间 -> 用 `ctx.clusterTimeMs()`.
- 不能用 `Math.random()` / `UUID.randomUUID()` -> 自管伪随机数, 种子从命令 / `clusterTimeMs` 派生.
- 不能依赖 hashmap iteration 顺序 -> 用 `LinkedHashMap` 或排序后 iterate.
- 不能调外部系统 (HTTP / DB) -> 状态全部进集群, 或异步通过 timer 回环.



## 5. 客户端 (ClusterClient) 详解

### 5.1 创建客户端

```java
import com.mcst.aeron.cluster.client.api.*;
import com.mcst.aeron.cluster.client.config.ClusterClientConfig;

CodecRegistry codecs = CodecRegistry.minimal();
codecs.register(MyCmdCodec.INSTANCE);
codecs.register(MyRespCodec.INSTANCE);

ClusterClientConfig cfg = ClusterClientConfig.builder()
        .ingressEndpoints("0=10.0.0.1:9001,1=10.0.0.2:9001,2=10.0.0.3:9001")
        .codecRegistry(codecs)
        .responseTimeoutMs(5_000)
        .reconnectStrategy(ReconnectStrategy.exponentialBackoff(200, 5_000, 2.0, 10))
        .build();

ClusterClient client = ClusterClientBuilder.create(cfg);
client.connect();   // 同步, 失败抛 ClusterClientException
```

`ingressEndpoints` 必须列出<b>全部</b>节点 (不只是 leader). 框架自动选出当前 leader.

其它常用 builder 项:

| 项 | 默认 | 说明 |
|---|---|---|
| `keepAliveIntervalMs` | 2_000 | 保活间隔, 必须小于集群 session 空闲超时 (`aeron.cluster.session.timeout`, 默认 10s), 否则空闲 session 会被集群以 TIMEOUT 关闭 |
| `connectTimeoutMs` | 10_000 | `AeronCluster.connect` 超时 |
| `egressChannel` | `aeron:udp?endpoint=localhost:0` | 接收响应的 channel, 0 = OS 分端口 |
| `enableBackgroundPoller` | true | 关闭后业务需自调 `pollEgress()` |
| `pollerIdleSleepNs` | 1_000_000 | poller 空转 sleep |

### 5.2 同步等响应 (sendAndAwait)

```java
CompletableFuture<MyResp> future =
        client.sendAndAwait(MyCmdCodec.INSTANCE, new MyCmd(...), MyRespCodec.INSTANCE, 3_000L);

try {
    MyResp resp = future.get(5, TimeUnit.SECONDS);
    // 业务逻辑
} catch (TimeoutException te) {
    // 框架自身超时 + future.get 超时 双保护
} catch (ExecutionException ee) {
    // ee.getCause() 是 ClusterTimeoutException / ClusterClientException 之一
}
```

注意: future 的回调 (`thenApply`, `whenComplete`) 在<b>客户端 poller 线程</b>上执行, <b>不要</b>在里面做长任务. 重活用 `thenApplyAsync(executor)`.

### 5.3 fire-and-forget (send)

```java
long pos = client.send(MyCmdCodec.INSTANCE, new MyCmd(...));
if (pos < 0L) {
    // 客户端未连接 / 已关闭, 业务方决定重试或上报失败
}
```

不需要响应的写命令优先用 `send`: 客户端不分配 correlation 槽位, 内存 / CPU 都更省.

### 5.4 监听集群事件

```java
client.addEventListener(new ClusterEventListener() {
    @Override
    public void onNewLeader(long sessionId, long termId, int leaderMemberId) {
        log.info("leader switched to {}", leaderMemberId);
    }
    @Override
    public void onDisconnected() {
        // 重连策略已放弃, 业务方该走 fallback 或退出进程
    }
    @Override
    public void onReconnected(int attempts) {
        log.info("reconnected after {} attempts", attempts);
    }
    @Override
    public void onEgressEvent(int codecId, DirectBuffer buf, int offset, int length) {
        // 服务端经 session.publishEvent / ctx.publishEgress 主动推送的 EGRESS_EVENT 帧 (无 correlation), 业务自行 decode.
        // 广播给多个 session 见 §11.4.
    }
});
```

### 5.5 关闭

```java
client.close();   // 幂等, 可以多次调
```

close 会:

1. 停 poller 线程 (interrupt + join 1s).
2. 把所有 outstanding `CompletableFuture` 以 `ClusterClientException("client closing")` 完成.
3. 释放 Aeron 资源 + 嵌入式 driver.

### 5.6 带重试的客户端 (RetryingClusterClient)

```java
RetryPolicy policy = RetryPolicy.builder()
        .maxAttempts(3)              // 含首次; 默认 3
        .initialBackoffMs(20)        // 指数退避起点; 默认 20ms
        .maxBackoffMs(500)           // 退避上限; 默认 500ms
        .factor(2.0)
        .retryOnTimeout(false)       // 默认 false! 仅命令幂等时才可打开
        .build();

ClusterClient client = ClusterClientBuilder.createRetrying(cfg, policy);
// 或给已有 client 套装饰: ClusterClientBuilder.withRetry(delegate, policy)
```

重试安全性分类 (框架默认行为):

| 失败类型 | 是否默认重试 | 原因 |
|---|---|---|
| offer 失败 / 未连接 (`ClusterClientException`) | 是 | 命令确定没进集群, 重试绝对安全 |
| 响应超时 (`ClusterTimeoutException`) | <b>否</b> | 命令可能已 apply, 盲目重试会重复执行 |
| 其它异常 (codec mismatch 等) | 否 | 可通过 `retryableException(Predicate)` 自定义 |

`retryOnTimeout(true)` 仅当命令幂等时使用: 服务端状态机继承 `AbstractIdempotentStateMachine` (见 `core.idempotence` 包), 命令 payload 携带稳定 `clientId` + 单调递增 `requestId`, 框架按 `(clientId, requestId)` 去重并回放缓存的响应, 把客户端"至少一次发送"收敛成状态机侧"恰好一次"执行. 去重表随 snapshot 持久化.



## 6. Snapshot

Snapshot 是 cluster 的"内存状态序列化到磁盘"的机制, 用于:

- 节点重启<b>不必</b>从头回放整个 raft log (上百万条命令时显著加速启动).
- 新节点 catch-up 从 snapshot + 增量 log 追平 leader.

### 6.1 takeSnapshot (写)

```java
@Override
public void takeSnapshot(SnapshotWriter writer) {
    writer.writeHeader(SnapshotMagic.FRAMEWORK_VERSION_V1, MY_BUSINESS_VERSION);

    // 用 codec 写业务对象
    writer.write(LongCodec.INSTANCE, counter);

    // 或者写 raw bytes
    byte[] sub = encodeMyComplexState();
    writer.writeBytes(sub);

    // 大状态可以分段写, 每段后 flush 给 archive 收口
    for (Bucket b : buckets) {
        writer.write(BucketCodec.INSTANCE, b);
        writer.flush();   // 给 archive 一个收口机会
    }
}
```

调用顺序: `writeHeader` 一次, 然后任意次 `write*`. 框架在 takeSnapshot 返回后会自动再 flush 一次, 业务方手动 flush 仅在分段背压场景下需要.

### 6.2 loadSnapshot (读)

```java
@Override
public void loadSnapshot(SnapshotReader reader) {
    SnapshotHeader h = reader.readHeader(MY_BUSINESS_VERSION);
    if (h.businessVersion() < MY_BUSINESS_VERSION) {
        // 旧 snapshot, 走兼容逻辑
    }

    if (reader.hasMore()) {
        counter = reader.read(LongCodec.INSTANCE);
    }
    while (reader.hasMore()) {
        Bucket b = reader.read(BucketCodec.INSTANCE);
        buckets.add(b);
    }
}
```

调用顺序: `readHeader` 必须第一个调; 然后 `hasMore + read*` 循环. <b>读的顺序必须和写的顺序完全一致</b>.

### 6.3 业务版本 (BUSINESS_VERSION)

业务方<b>必须</b>自管 `businessVersion`. 改了状态机的 in-memory 结构 (新增字段, 改 codec 编码) 必须 +1, 否则旧节点重启读 snapshot 会乱掉.

最佳实践: BUSINESS_VERSION 写成 `public static final int`, 改的时候同时改:

1. BUSINESS_VERSION 数字 +1.
2. takeSnapshot 写新版本号.
3. loadSnapshot 在 readHeader 后判断 `header.businessVersion()`, 对旧版本走<b>兼容读取路径</b>.
4. 单元测试覆盖"读旧版本 snapshot".

### 6.4 大 snapshot 的内存

`SnapshotImageReader` 启动时一次性把整个 snapshot 字节流 drain 到内存. 业务状态预期上 GB 时:

- 调大 JVM heap (`-Xmx`).
- 考虑用 `writer.writeBytes(DirectBuffer, offset, length)` 直接写 off-heap, 避开多余 copy.
- 评估业务能不能拆分到多节点 (cluster 不是数据库, 不擅长存几十 GB).

### 6.5 触发快照的四种方式

| 方式 | 入口 | 说明 |
|---|---|---|
| 周期快照 | `snapshot-interval-ms` (默认 3_600_000 = 1h; `<= 0` 禁用) | 框架边车线程每隔该时长<b>仅在 leader</b> 上触发一次; 配 `snapshot-quiet-windows: ["02:00-04:00"]` 可设静默窗口 (本地时区, 支持跨午夜), 窗口内跳过. 别配到分钟级, 磁盘代价见 §9.3 |
| 手动触发 | `ClusterNode.triggerSnapshot()` | 仅 leader 生效, 非 leader / 未运行 / 上次快照进行中返回 false; 不受静默窗口限制; 适合运维在低峰前手动收口 |
| 管理工具 | Aeron `ClusterTool` | 直接切换节点控制开关, 与框架周期触发同一机制 |
| 优雅关闭 | `node.close()` | Aeron 在 ClusteredServiceContainer 关闭时自动触发 |

周期触发是"尽力而为": 落在静默窗口 / 上一次快照未完成的周期会跳过, 不保证严格等间隔.

`snapshot-channel` 默认 `aeron:ipc?alias=snapshot|term-length=8m` (不是 Aeron 的 IPC 默认 64MB term ——
那会让每个快照 recording 至少占 64MB 定长段文件). term-length 的两个方向: 调大放开单条 entry 上限
(= term-length / 8, 默认 1MB) 并降低写出背压; 调小减少每个快照 recording 的磁盘占用. 配套磁盘治理见 §9.3.

### 6.6 异步快照 (大状态 opt-in)

默认快照是<b>同步内联</b>: `takeSnapshot` 在状态机线程上把整个状态写进 Aeron 快照流, 状态越大, 状态机停顿越久.
状态达到几百 MB 级时, 可以让状态机额外实现 `AsyncSnapshotSource` 切到<b>异步两阶段</b>: 状态机线程只做 O(1) 捕获,
大块序列化由框架后台线程写到外置文件.

```java
public final class BigStateMachine implements ClusterStateMachine<MyCmd>, AsyncSnapshotSource {

    @Override
    public SnapshotView captureSnapshot(long logPosition) {
        // 在状态机线程上调用, 必须 O(1): 抓取一个不可变视图 (COW 结构引用 / 快速拷贝)
        final ImmutableState snapshot = state.copyOnWriteSnapshot();
        return new SnapshotView() {
            @Override
            public void write(SnapshotWriter writer) {
                // 框架后台线程执行; 写法与同步 takeSnapshot 完全相同
                writer.writeHeader(SnapshotMagic.FRAMEWORK_VERSION_V1, BUSINESS_VERSION);
                writer.write(StateCodec.INSTANCE, snapshot);
            }
            @Override
            public void close() {
                // 释放视图资源 (写出完成后框架自动调用)
            }
        };
    }

    // loadSnapshot 写法完全不变: 框架自动区分内联流与外置文件, 业务读代码零改动
}
```

要点:

- 实现该 SPI 后, 同步 `takeSnapshot` <b>不再被调用</b> (两种写法二选一, 不用都实现).
- 真实状态写到外置文件 `snapshot-<logPosition>.snap` (默认目录 `clusterDir/snapshots`, 可用 `snapshot-ext-dir` 覆盖;
  保留份数 `snapshot-ext-retain-count`, 默认 2); Aeron 快照流上只留一条 manifest (文件名 + logPosition).
- ⚠️ 不要手工删除该目录下的 `.pending` / `.tmp` 文件: 崩溃恢复靠它们识别半成品快照并自动回退.
- 参考: `aeron-cluster-test` 里的 `AsyncCounterStateMachine` demo.



## 7. Spring Boot 集成

### 7.1 加 starter

```groovy
implementation 'com.mcst:aeron-cluster-spring-boot-starter:3.2.12'
```

starter 内部按 `@ConditionalOnProperty` 装配, 默认全部关闭, 业务方按需打开.

### 7.2 业务侧实现

```java
@ClusterStateMachineBean   // 等价 @Component, 但语义更清楚
public class OrderStateMachine implements ClusterStateMachine<OrderCommand> {
    @Override
    public void onCommand(ClusterSession session, OrderCommand cmd, ClusterContext ctx) {
        // ...
    }
}

@Component
public class OrderEventHandler {

    @ClusterEventListener(Event.NEW_LEADER)
    public void onLeaderSwitch(long sessionId, long termId, int leaderId) {
        log.info("leader is {}", leaderId);
    }

    @ClusterEventListener(Event.DISCONNECTED)
    public void onDisconnected() {
        log.warn("cluster client disconnected, all reconnect attempts exhausted");
    }

    @ClusterEventListener(Event.RECONNECTED)
    public void onReconnected(int attempts) {
        log.info("reconnected after {} attempts", attempts);
    }
}

@Configuration
public class ClusterCodecConfig {
    // 名为 aeronClusterCodecRegistry 的 bean 专供 cluster 使用 (与 easyfk-aeron 同进程时也不会冲突);
    // 未声明时, cluster 取容器内唯一 (或 @Primary) 的 CodecRegistry, 都没有则用 CodecRegistry.withDefaults().
    @Bean("aeronClusterCodecRegistry")
    CodecRegistry clusterCodecRegistry() {
        CodecRegistry reg = CodecRegistry.minimal();
        reg.register(OrderPlaceCodec.INSTANCE);
        reg.register(OrderCancelCodec.INSTANCE);
        reg.register(OrderRespCodec.INSTANCE);
        return reg;
    }
}
```

### 7.3 application.yml

#### 节点 (3 节点生产部署示例)

```yaml
easyfk:
  config:
    aeron:
      cluster:
        node:
          enabled: true
          member-id: 0                 # 本节点 id, 三个节点分别 0/1/2
          media-driver-mode: EMBEDDED
          aeron-dir: /var/lib/aeron-cluster/aeron
          archive-dir: /var/lib/aeron-cluster/archive
          cluster-dir: /var/lib/aeron-cluster/cluster
          snapshot-interval-ms: 3600000  # 周期快照(ms), 默认 1h; <=0 禁用(仅 ClusterTool/优雅关闭触发). 别配到分钟级, 见 §9.3
          # snapshot-channel: aeron:ipc?alias=snapshot|term-length=8m  # 默认即此; term-length/8=单条 entry 上限
          # archive-segment-file-length: 8m        # archive 段长; 留空=auto 跟随 snapshot-channel term-length
          # archive-retain-snapshot-count: 3       # 保留快照组数(启用须>=3); 默认 0=禁用清理(archiveDir 无界增长)
          # archive-retention-interval-ms: 3600000 # 保留清理检查间隔, 默认 1h
          # snapshot-quiet-windows: ["02:00-04:00"]  # 周期快照静默窗口(本地时区, 支持跨午夜)
          # snapshot-ext-dir: /var/lib/aeron-cluster/snapshots  # 异步快照外置目录; 默认 clusterDir/snapshots
          # snapshot-ext-retain-count: 2           # 外置快照保留份数(>=1)
          idle-strategy: BACKOFF       # 见 §11 食谱
          topology:
            - member-id: 0
              ingress:   10.0.0.1:9001
              consensus: 10.0.0.1:9002
              log:       10.0.0.1:9003
              catchup:   10.0.0.1:9004
              archive:   10.0.0.1:9005
            - member-id: 1
              ingress:   10.0.0.2:9001
              consensus: 10.0.0.2:9002
              log:       10.0.0.2:9003
              catchup:   10.0.0.2:9004
              archive:   10.0.0.2:9005
            - member-id: 2
              ingress:   10.0.0.3:9001
              consensus: 10.0.0.3:9002
              log:       10.0.0.3:9003
              catchup:   10.0.0.3:9004
              archive:   10.0.0.3:9005
```

#### 客户端

```yaml
easyfk:
  config:
    aeron:
      cluster:
        client:
          enabled: true
          ingress-endpoints: "0=10.0.0.1:9001,1=10.0.0.2:9001,2=10.0.0.3:9001"
          response-timeout-ms: 5000
          # keep-alive-interval-ms: 2000   # 必须 < aeron.cluster.session.timeout(默认 10s)
          reconnect:
            strategy: EXPONENTIAL_BACKOFF
            initial-delay-ms: 200
            max-delay-ms: 5000
            factor: 2.0
            max-attempts: 10
```

### 7.4 自动注入

starter 自动注入两个核心 bean (业务方按需注入):

```java
@Service
public class OrderService {
    private final ClusterClient client;
    public OrderService(ClusterClient client) { this.client = client; }

    public CompletableFuture<OrderResp> placeOrder(OrderPlace cmd) {
        return client.sendAndAwait(OrderPlaceCodec.INSTANCE, cmd, OrderRespCodec.INSTANCE, 3_000L);
    }
}
```

### 7.5 自定义覆盖

任何一个 bean 都可以业务方自定义, starter 用 `@ConditionalOnMissingBean` 让位:

```java
@Bean
ClusterMetrics myClusterMetrics(MeterRegistry mr) {
    return new MyMicrometerClusterMetrics(mr);
}

@Bean
RoleChangeListener roleChangeListener() {
    return (prev, curr, termId) -> log.info("role: {} -> {} term {}", prev, curr, termId);
}

@Bean
ClusterClock clusterClock() {
    return new MyNtpAwareClock();    // 测试时可以注入 fixed clock
}
```

### 7.6 Health Indicator

依赖 actuator 后自动暴露 `/actuator/health/aeronClusterHealth` (bean 名 `aeronClusterHealth`, Spring Boot 只剥离 `HealthIndicator` 后缀, 因此路径保留 `Health`). 字段按容器内是否装了 `ClusterNode` / `ClusterClient` 取并集 (二者皆可单独存在):

```json
{
  "status": "UP",
  "details": {
    "node.memberId": 0,
    "node.role": "LEADER",
    "node.running": true,
    "client.connected": true,
    "client.sessionId": 17,
    "client.leaderMemberId": 0
  }
}
```

判定规则 (节点 / 客户端 bean 任一存在即生效):

| 状态 | 条件 |
|---|---|
| UP | 节点 (若有) `isRunning()=true` 且 客户端 (若有) `isConnected()=true` |
| DOWN | 至少一个 bean 存在但<b>未</b>就绪 |
| UNKNOWN | 两个 bean 都没装 (`easyfk.config.aeron.cluster.node.enabled=false` 且 `easyfk.config.aeron.cluster.client.enabled=false`) |



## 8. 测试夹具

`aeron-cluster-test` 提供两套嵌入式集群供 IT 用. 不要在生产代码里依赖此模块.

### 8.1 单节点 (开发自测 / 接口验证)

```java
@Test
void counterRoundtrip(@TempDir Path tmp) throws Exception {
    CodecRegistry codecs = CodecRegistry.minimal();
    codecs.register(CounterStateMachine.CODEC);

    try (EmbeddedSingleNodeCluster cluster =
             EmbeddedSingleNodeCluster.launch(new CounterStateMachine(), codecs, tmp)) {

        ClusterAwait.untilLeaderElected(List.of(cluster.node()));
        ClusterAwait.untilConnected(cluster.client());

        Long resp = cluster.client()
                .sendAndAwait(CounterStateMachine.CODEC, 7L, CounterStateMachine.CODEC, 5_000L)
                .get(10, TimeUnit.SECONDS);
        assertThat(resp).isEqualTo(7L);
    }
}
```

> 单节点 = 1 个 raft member, 没有真正的多数派故障容忍, 仅适合 demo / 接口测试.

### 8.2 三节点 (生产场景仿真)

```java
@Test
void leaderFailover(@TempDir Path tmp) throws Exception {
    CodecRegistry codecs = CodecRegistry.minimal();
    codecs.register(CounterStateMachine.CODEC);

    try (EmbeddedThreeNodeCluster cluster =
             EmbeddedThreeNodeCluster.launch(CounterStateMachine::new, codecs, tmp)) {

        ClusterAwait.untilLeaderElected(cluster.nodes());
        ClusterAwait.untilConnected(cluster.client());

        int oldLeader = cluster.currentLeaderMemberId();

        // kill leader
        cluster.nodes().get(oldLeader).close();

        // 客户端会自动 failover 到新 leader
        ClusterAwait.untilTrue("new leader elected",
                () -> cluster.currentLeaderMemberId() != oldLeader && cluster.currentLeaderMemberId() != -1,
                Duration.ofSeconds(15));

        Long resp = cluster.client()
                .sendAndAwait(CounterStateMachine.CODEC, 5L, CounterStateMachine.CODEC, 10_000L)
                .get(15, TimeUnit.SECONDS);
        assertThat(resp).isEqualTo(5L);
    }
}
```

### 8.3 JUnit 5 扩展

`EmbeddedClusterExtension` 是一个 `AfterEachCallback`: 测试代码把自行 launch 的 fixture 通过静态方法
`EmbeddedClusterExtension.register(extensionContext, cluster)` 登记到 `ExtensionContext.Store` 后, 每个测试结束时自动 close, 避免漏关. 支持 `EmbeddedSingleNodeCluster` 与 `EmbeddedThreeNodeCluster` 两种 fixture.

> 注意: 该扩展<b>不</b>提供测试方法参数级的 fixture 自动注入; 简单场景推荐直接用 try-with-resources (见 §8.1 / §8.2).

### 8.4 ClusterAwait 等待 API

```java
ClusterAwait.untilLeaderElected(nodes);
ClusterAwait.untilLeaderElected(nodes, Duration.ofSeconds(60));
ClusterAwait.untilConnected(client);
ClusterAwait.untilCommittedAtLeast(metrics, 100);   // 等到累计提交 >= 100 条
ClusterAwait.untilSnapshotTaken(metrics);
ClusterAwait.untilTrue("custom", () -> cond, Duration.ofSeconds(10));
```

### 8.5 IT 标记

测试夹具会真起 ClusteredMediaDriver, 单测耗时 5–15s. 框架自带的集群 IT (如 `EmbeddedSingleNodeClusterSmokeTest` / `PeriodicSnapshotIT`) 用 `@Tag("it")` 标记.

> 注意: 框架自身构建脚本默认<b>跳过</b>全部测试 (`onlyIf { project.hasProperty('runTests') }`), 需 `./gradlew test -PrunTests` 才执行, 且未按 tag 过滤 (带 `-PrunTests` 时 IT 一并执行). 业务方如需隔离 IT, 可在自己的 `build.gradle` 里配 `useJUnitPlatform { excludeTags 'it' }`.



## 9. 部署

### 9.1 节点数选型

| 节点数 | 容错 | 写延迟 | 推荐场景 |
|---|---|---|---|
| 1 | 0 (单点) | 最低 | demo / 开发 |
| 3 | 1 | 中 | 生产标准 |
| 5 | 2 | 较高 | 高可用关键服务 |
| 7+ | 3+ | 高 | 不推荐, 收益递减 |

<b>必须用奇数</b>. 偶数节点 (2 / 4 / 6) Raft 多数派要求与 N-1 相同, 多花 coordination 成本不增加容错. 框架的 `ClusterTopology.validate` 会对偶数 / 单节点拓扑发 WARN.

### 9.2 端口规划

每个节点占<b>5 个 UDP 端口</b>:

| 端口 | 用途 |
|---|---|
| ingress | 客户端连进来发命令 |
| consensus | Raft 节点间共识投票 |
| log | Raft 日志 replication |
| catchup | 落后节点 catch-up |
| archive | Archive 控制通道 (跨节点 archive client 用) |

防火墙必须放行所有节点之间的这些 UDP 端口. 客户端只需访问 `ingress` 端口.

### 9.3 磁盘

每个节点 3 个独立目录, <b>必须互不重叠</b>:

| 目录 | 内容 | 推荐磁盘 |
|---|---|---|
| `aeronDir` | Aeron driver 共享内存映射 | tmpfs / RAM 盘 (短期数据) |
| `archiveDir` | snapshot + raft log 持久化 | SSD (顺序写多, 大块数据) |
| `clusterDir` | ConsensusModule 元数据 | SSD (小块, 频繁 fsync) |

容量估算: 单条命令 + 帧头 ~ 24+payload 字节; 100 万条/天的业务大约每天 100 MB raft log. snapshot 视业务状态而定 (内存 dump 大小).

#### archiveDir 增长治理 (重要)

Aeron 开源版<b>不会</b>自动删除旧快照 recording (官方的 Data Retention Regulator 是 Premium 功能). 每次快照
固定新建 `1 + service 数` 个 recording, 每个至少占一个<b>定长预分配</b>的段文件 —— 即使快照本身只有几 KB.
所以 archiveDir 的增长由<b>快照频率</b>主导, 与业务量几乎无关, 不治理会无界涨. 框架提供两个配套旋钮:

| 旋钮 (spring 配置) | 默认 | 作用 |
|---|---|---|
| `node.archive-segment-file-length` | auto (= `snapshot-channel` term-length, 默认 8MB) | 段长越小, 小快照浪费的预分配磁盘越少; 显式配置须 2 的幂、∈ [64KB, 1GB]、且 >= 快照流 term-length (Aeron size 记法如 `"4m"`). 只影响新建 recording, 老目录无需清空 |
| `node.archive-retain-snapshot-count` | 0 (禁用) | `> 0` 启用框架的保留清理边车: 每 `node.archive-retention-interval-ms` (默认 1h) 只保留最新 N 组快照, 更老的整组删除, 并把 raft log 裁到最老保留组的位置之前. 启用时必须 >= 3 (崩溃回退要逐层退, 留足余量) |

要点:

- 保留以<b>快照组</b>为单位 (一次快照 = ConsensusModule + 各 service 一整组 recording), 恢复时整组取用,
  不会删到恢复还需要的数据; 各节点只清本地 archive, 独立保留, 无需跨节点错峰.
- 开启清理后稳态磁盘占用 ≈ `retain-count 组 × (1 + service 数) × 段长` + 保留点之后的 raft log.
- 周期快照间隔别配到分钟级: 10 分钟一次快照, 单 service 一天就产生 288 个段文件.
- 清理是尽力而为的: 某轮删不掉 (如 recording 正被追赶中的节点 replay) 下个周期自动重试, 不影响节点服务.
- 已删 recording 在 archive catalog 里留的定长槽位要停机跑 `ArchiveTool.compact` 才回收; 占磁盘的是段文件
  (已删), 槽位本身占空间很小.

### 9.4 启动顺序

3 节点同时拉起即可, 没有先后强约束. Raft 内部会选主. 推荐做法:

1. 业务方 deploy 时把 3 个节点的 systemd unit 用同一个 timer 同时拉起.
2. 监控 `/actuator/health/aeronClusterHealth` 等 1 个节点变 LEADER 后认为集群可服务.
3. 客户端应用晚于集群启动. starter 在 Spring 上下文启动末尾同步 `connect()`, 在 `connect-timeout-ms` (默认 10s) 内连不上会抛 `ClusterClientException` 导致应用启动失败; `reconnect` 策略只作用于<b>已连上后</b>的断线重连, 不覆盖首次 connect.

### 9.5 关闭与重启

- <b>禁止</b> kill -9. cluster 节点 graceful close 会写 mark file 让 archive 落盘干净, kill -9 会留 dirty cluster dir, 重启时需要走 catch-up.
- 单节点重启: 先 close 一个节点, 等剩 2 个节点重新选主成功后再 close 下一个 (保留多数派可服务).
- 全集群重启: 三个节点都关 -> raft log 完整保留在 archive -> 重新拉起后会重放, 状态恢复. 但中间不可服务.

### 9.6 集群升级 (滚动)

原则: <b>先升级所有 follower, 最后升级 leader</b>. 这样升级过程中只发生一次 leader 切换 (在最后一步), 客户端受影响最少.

通过 `/actuator/health/aeronClusterHealth` 的 `node.role` 或日志先识别当前 leader. 例如三节点拓扑里 leader 是 2 号:

```
# 1) 先升级两个 follower (顺序无关), 每升完一个等同步追平再升下一个:
节点 0 (FOLLOWER) close -> 升级 jar -> 启动 -> ClusterAwait.untilCommittedAtLeast 验证追平
节点 1 (FOLLOWER) close -> 升级 jar -> 启动 -> 同上

# 2) 最后升级 leader, 触发一次新选主 (剩下的 follower 之一接管):
节点 2 (LEADER)   close -> 触发选主 (节点 0 或 1 升为 leader) -> 升级 jar -> 启动
```

升级期间客户端会经历一次短暂 leader 切换, `EXPONENTIAL_BACKOFF` 重连策略足以覆盖.

> 切勿同时关闭 2 个节点 —— 三节点集群多数派要求 2 个活, 同时关 2 个会导致集群停服.

注意:

- 业务方<b>修改 BUSINESS_VERSION</b> 时必须保证新版本能读旧 snapshot, 否则升级期会 fail.
- 状态机回放结果必须确定性向后兼容, 否则旧节点和新节点回放同一条日志结果不同 -> 集群分裂.



## 10. 可观测性

### 10.1 关键指标 (ClusterMetrics)

接 Prometheus / OTel 时实现 `ClusterMetrics` 的 15 个抽象方法即可 (另有 7 个 default 扩展方法 —
`onSnapshotTaken` / `onSnapshotLoaded` 的 logPosition 重载, `onSnapshotRequested` / `onSnapshotSkipped` /
`onSnapshotFailed`, `onArchiveRetentionPurged` / `onArchiveRetentionSkipped` — 按需覆盖, 用于观测
快照触发 / 跳过 / 失败与 archive 保留清理):

```java
@Bean
ClusterMetrics clusterMetrics(MeterRegistry mr) {
    return new ClusterMetrics() {
        public void onCommandCommitted(int codecId, int payloadBytes, long latencyNs) {
            mr.timer("aeron_cluster_command", "codec", String.valueOf(codecId))
              .record(latencyNs, TimeUnit.NANOSECONDS);
        }
        public void onCommandRejected(int codecId, String reason) {
            mr.counter("aeron_cluster_command_rejected", "codec", String.valueOf(codecId), "reason", reason)
              .increment();
        }
        public void onSnapshotTaken(long bytes, long durationNs) { /* ... */ }
        public void onSnapshotLoaded(long bytes, long durationNs) { /* ... */ }
        public void onRoleChange(ClusterRole prev, ClusterRole curr, long termId) { /* ... */ }
        public void onSessionOpened(long sid) { /* ... */ }
        public void onSessionClosed(long sid, CloseReason r) { /* ... */ }
        public void onRespondDropped(long sid, String reason) { /* ... */ }
        public void onTimerScheduled(long id) { /* ... */ }
        public void onTimerFired(long id) { /* ... */ }
        public void onTimerCancelled(long id) { /* ... */ }
        public void onClientSend(int codecId, int payloadBytes) { /* ... */ }
        public void onClientResponse(int codecId, int payloadBytes, long rttNs) { /* ... */ }
        public void onClientReconnect(int attempt) { /* ... */ }
        public void onError(Throwable t) { /* ... */ }
    };
}
```

注意: 任何 metrics 方法都<b>禁止</b>在热路径分配字符串. 标签值预先构造缓存.

### 10.2 监控仪表板建议

| 指标 | 类型 | 建议告警 |
|---|---|---|
| `aeron_cluster_command` p99 latency | Histogram | > 100ms 持续 1min |
| `aeron_cluster_command_rejected` rate | Counter | > 1/s 持续 1min |
| `aeron_cluster_role_change` rate | Counter | > 1 次 / 5min (频繁切主) |
| `aeron_cluster_snapshot_taken_duration` | Histogram | > 10s 持续多次 |
| `aeron_cluster_client_reconnect` | Counter | 突发 spike |
| `aeron_cluster_error` rate | Counter | > 0 即看 log |
| archive 保留清理 (`onArchiveRetentionPurged` / `...Skipped`) | Counter | 启用清理后长期无 purged 且 archiveDir 持续上涨 (清理未生效); skipped reason=`error` 持续增长 |

### 10.3 日志关键字

框架以 SLF4J 输出, 业务方接 logback / log4j2. 关键 logger:

| logger | 关键场景 |
|---|---|
| `com.mcst.aeron.cluster.core.internal.EmbeddedClusterNode` | INFO 节点启停 / 异常 |
| `com.mcst.aeron.cluster.core.internal.FrameworkClusteredService` | WARN 状态机抛错 / 未知 session |
| `com.mcst.aeron.cluster.core.internal.FrameworkClusterContext` | WARN 业务 reportError |
| `com.mcst.aeron.cluster.client.internal.AeronClusterClient` | INFO 连接 / 重连; WARN 重连失败 |
| `com.mcst.aeron.cluster.client.internal.PendingResponseRegistry` | DEBUG outstanding count |

### 10.4 actuator 端点

`/actuator/health/aeronClusterHealth` —— 集群 / 节点状态. 详见 §7.6.



## 11. 常见模式 / 食谱

### 11.1 写一个键值存储 (KV)

```java
public sealed interface KvCmd permits Put, Get, Del {}
public record Put(String key, byte[] value) implements KvCmd {}
public record Get(String key)              implements KvCmd {}
public record Del(String key)              implements KvCmd {}

public final class KvStateMachine implements ClusterStateMachine<KvCmd> {
    private final Map<String, byte[]> store = new HashMap<>();

    @Override
    public void onCommand(ClusterSession s, KvCmd cmd, ClusterContext ctx) {
        switch (cmd) {
            case Put p -> {
                store.put(p.key(), p.value());
                s.respondBytes(new byte[]{1});                // ack
            }
            case Get g -> {
                byte[] v = store.get(g.key());
                s.respondBytes(v != null ? v : new byte[0]);
            }
            case Del d -> {
                byte[] old = store.remove(d.key());
                s.respondBytes(old != null ? new byte[]{1} : new byte[]{0});
            }
        }
    }

    @Override
    public void takeSnapshot(SnapshotWriter writer) {
        writer.writeHeader(SnapshotMagic.FRAMEWORK_VERSION_V1, 1);
        writer.writeBytes(serializeMap(store));
    }

    @Override
    public void loadSnapshot(SnapshotReader reader) {
        reader.readHeader(1);
        if (reader.hasMore()) {
            store.putAll(deserializeMap(reader.readBytes()));
        }
    }
}
```

### 11.2 高可用计数器 (序列号生成)

```java
public final class IdGenStateMachine implements ClusterStateMachine<Long> {
    private long nextId = 1L;

    @Override
    public void onCommand(ClusterSession s, Long batchSize, ClusterContext ctx) {
        long start = nextId;
        nextId += batchSize;
        s.respond(LongCodec.INSTANCE, start);    // 返回区间起始
    }

    @Override
    public void takeSnapshot(SnapshotWriter w) {
        w.writeHeader(SnapshotMagic.FRAMEWORK_VERSION_V1, 1);
        w.write(LongCodec.INSTANCE, nextId);
    }

    @Override
    public void loadSnapshot(SnapshotReader r) {
        r.readHeader(1);
        if (r.hasMore()) nextId = r.read(LongCodec.INSTANCE);
    }
}
```

每次客户端 `sendAndAwait(IdGenCodec, batchSize, LongCodec, ...)` 拿到一个区间起始, 进程内自管 batchSize 个 id 用完再来.

### 11.3 周期性任务 (用 Timer)

```java
@Override
public void onStart(ClusterContext ctx) {
    ctx.scheduleTimer(TIMER_HEARTBEAT, ctx.clusterTimeMs() + 1000);
}

@Override
public void onTimer(long timerId, ClusterContext ctx) {
    if (timerId == TIMER_HEARTBEAT) {
        // 周期任务: 清理过期 session / 上报状态等
        cleanupExpired(ctx.clusterTimeMs());

        // 续 timer
        ctx.scheduleTimer(TIMER_HEARTBEAT, ctx.clusterTimeMs() + 1000);
    }
}
```

注意: timer 触发时间是<b>cluster time</b>, 不是 wall clock. 回放时同样的 timer 会按同样 cluster time 触发, 保证确定性.

### 11.4 广播事件给多个订阅 session (EGRESS_EVENT 主动推送)

> 服务端主动推送现已走专门的 `EGRESS_EVENT` 帧: 用 `session.publishEvent(codec, value)` (或 `ctx.publishEgress(session, codec, value)`). 客户端侧从 `ClusterEventListener.onEgressEvent` 收到, 与 `sendAndAwait` 的 future <b>互不串扰</b> —— EGRESS_EVENT 不带 correlationId, 不会误 complete 任何 pending future. 这优于早期"用 RESPONSE 帧广播"的变通法 (后者会让其它 session 收到一个带陌生 correlationId 的 RESPONSE).

业务方在状态机里保存 session 引用, 在事件发生时遍历 publishEvent:

```java
private final List<ClusterSession> watchers = new ArrayList<>();

@Override
public void onCommand(ClusterSession s, MyCmd cmd, ClusterContext ctx) {
    if (cmd instanceof Subscribe) {
        watchers.add(s);              // <b>仅</b>在 leader 上才能 publish; follower 上 add 也无害
        s.respond(AckCodec.INSTANCE, ack);   // 对订阅命令本身的应答仍走 respond
    } else if (cmd instanceof Update u) {
        applyUpdate(u);
        // 主动广播给所有订阅者 (EGRESS_EVENT, 无 correlation); 触发更新的 caller 另由 respond 拿 sendAndAwait 响应:
        for (ClusterSession w : watchers) {
            w.publishEvent(UpdateCodec.INSTANCE, u);
        }
    }
}

@Override
public void onTimer(long timerId, ClusterContext ctx) {
    // 没有 inbound 命令的回调里, 用保留的 session 引用推送 (ctx 入口与 session.publishEvent 等价):
    for (ClusterSession w : watchers) {
        ctx.publishEgress(w, TickCodec.INSTANCE, tick);
    }
}

@Override
public void onSessionClose(ClusterSession s, CloseReason reason) {
    watchers.remove(s);   // <b>必须</b>清理, 否则 watchers 持续增长引发内存泄漏
}
```

注意:

- session 在 follower 上 publishEvent / respond 都静默丢弃 (返回 -1) —— 框架设计如此, 业务方不需要特判 role.
- watchers 列表的增删<b>必须</b>在状态机线程上 (即 onCommand / onTimer / onSessionClose 内). 不要在外部线程 mutate.
- EGRESS_EVENT 是一次性主动推送, <b>不</b>经服务端去重表 (`AbstractIdempotentStateMachine`) 缓存回放; 若客户端需要幂等消费, 请在 push 的 payload 内自带业务可去重的标识.
- 客户端区分"自己 sendAndAwait 的响应"与"被动广播"很自然: 前者走 `onResponse`/future, 后者走 `onEgressEvent`, 无需再靠 payload 字段或 correlationId 推断.

### 11.5 idle 策略选型

| spec | 行为 | 适用 |
|---|---|---|
| `NOOP` / `NONE` | 纯热轮询, 100% CPU | 绝对低延迟, 独占 CPU |
| `BUSY_SPIN` / `SPIN` | `Thread.onSpinWait` | 极低延迟 (微秒级 RPC), 独占机器 |
| `YIELDING` / `YIELD` | `Thread.yield` | 低延迟, 允许让出 |
| `BACKOFF` (默认) | spin -> yield -> park 三段退化 | 通用 |
| `SLEEP_NS:1000` | 固定 sleep 1us | 低 CPU 占用, 延迟可接受 |
| `SLEEP_MS:1` | sleep 1ms | 开发 / 测试环境, 后台任务 |

通过 `easyfk.config.aeron.cluster.node.idle-strategy` 或 `ClusterNodeConfig.builder().idleStrategySpec(...)` 设置.

### 11.6 关闭 / 停服

Spring Boot 优雅停服自动处理: `ClusterLifecycle` (phase = `Integer.MAX_VALUE`, 最先 stop) 在 stop 内先 close 客户端再 close 节点, 随后 `ClusterClientLifecycle` 只做 listener 解绑. 业务方一般不需要手动管.

> 注意: 二者 phase 都高于 Web 容器优雅停机 (`SmartLifecycle.DEFAULT_PHASE - 2048`), 因此会早于它执行; 停机窗口内仍在处理的 HTTP 请求再调 `ClusterClient` 会立即失败, 业务侧需容忍.

非 Spring 场景:

```java
try {
    // 业务运行
} finally {
    client.close();   // 等 outstanding future 全部 fail
    node.close();     // 等 mark file 落盘
}
```



## 12. 故障排查 FAQ

### Q1. 节点启动后一直选不出 leader

可能原因:

- topology 端点不通: `consensus` / `log` / `catchup` 端口被防火墙挡了. 检查 3 个节点之间的 5 个 UDP 端口能 ping 通.
- 时钟漂移过大: 节点间系统时间差超过 raft 心跳周期 (默认 10s) 选主异常.
- 单节点拓扑 + `member-id` 不在 topology 内: 启动会抛 `ClusterConfigException`.
- archive dir 被占用 (上次没干净 close): 看 log 是否有 `Cluster Mark File ... existing` 错误, 确认上次进程已退出后再启.

诊断命令:

```bash
# 看节点角色
curl localhost:8080/actuator/health/aeronClusterHealth

# 看 cluster log
tail -f /var/log/myapp/myapp.log | grep -i 'cluster\|raft\|consensus'
```

### Q2. sendAndAwait 经常超时

可能原因:

- 客户端 `responseTimeoutMs` 配得太短. 默认 3000ms 在跨地域 / 重负载下不够, 调到 10000.
- 状态机 `onCommand` 内做了阻塞 IO / 长 CPU 计算. <b>禁止</b>这么做; 改成 timer 回环.
- leader 切换中: ExponentialBackoff 重连一般 1s 内恢复, 期间命令积压会延迟. 业务侧加重试.
- 网络丢包高: 看 `aeron-driver` agent 的错误计数 (`actuator/metrics` 暴露).

### Q3. 状态机回放时结果与之前不同 (集群分裂)

最常见原因 = 状态机有<b>非确定性逻辑</b>. 检查清单:

- 用了 `System.currentTimeMillis()` 做业务时间? -> 改用 `ctx.clusterTimeMs()`.
- 用了 `Math.random()` / `UUID.randomUUID()`? -> 自管伪随机数.
- 依赖 HashMap iteration 顺序? -> 改 LinkedHashMap 或排序后 iterate.
- 调外部系统 (HTTP / DB)? -> 严禁; 数据放命令里, 或 timer 异步回环.
- 用了 `Locale.getDefault()` / 系统时区? -> 显式传入参数, 不用环境.

### Q4. 重启后 snapshot 加载失败

错误日志通常是 `ClusterSnapshotException(VERSION_TOO_NEW)` 或 `magic mismatch`:

- VERSION_TOO_NEW: 说明集群其它节点已经升级到更高 BUSINESS_VERSION 写过 snapshot, 旧版本 jar 读不了. 解决: 升级本节点 jar.
- magic mismatch: snapshot 文件被破坏 / 跟其它流文件混了. 解决: 清空 archive 目录, 让节点从 leader catch-up (但要保留多数派服务能力).

### Q5. 内存不停增长

可能原因:

- 状态机内部 Map / List 没清理 (比如 watchers 收到 close 事件未 remove). 在 `onSessionClose` 里清理.
- snapshot 文件过大 + heap 不够大. 调大 -Xmx 或拆业务. SnapshotImageReader 启动时一次性把整个流读到内存.
- 客户端 PendingResponseRegistry outstanding 持续涨: sendAndAwait 比 response 来得快, 业务侧加流控.

### Q6. 客户端 connect 失败

```
ClusterClientException: failed to connect to cluster
```

逐项排查:

1. ingress 端点是否可达? `nc -uvz host port`.
2. 拓扑里只列了 leader? 必须列<b>全部</b>节点, 框架自己选 leader.
3. driver dir 冲突? 同机器多个客户端进程默认 embeddedDriver, 自动分配独立 dir; 跨进程<b>共享</b> driver 时 `aeronDir` 必须显式配相同路径.
4. 防火墙挡了 UDP? Aeron 全 UDP, TCP 防火墙规则不够.

### Q7. 关闭节点很慢

`shutdownTimeoutMs` 默认 10s. 慢的原因:

- 状态机 `onStop` 实现里做了阻塞 IO. 不要这么做.
- archive 在落盘 snapshot. 等就行.
- mark file 残留等待. `node.close()` 会同步等 mark file 消失, 最长 `easyfk.config.aeron.cluster.node.shutdown-timeout-ms`
  (默认 10s); 确认无残留问题时可调小该值缩短关闭时间.
  ⚠️ 注意: `easyfk.config.aeron.cluster.shutdown.mark-file-wait-ms` 属性当前版本<b>未接线</b>, 设置它没有任何效果,
  关闭等待只认 `node.shutdown-timeout-ms`.



## 13. 版本兼容矩阵

### 13.1 当前版本 (3.2.12) 依赖

| 组件 | 版本 |
|---|---|
| Java | 21 |
| Aeron | 1.52.1 |
| Agrona | 2.5.0 |
| Spring Boot | 3.2.12 |
| SLF4J | 2.0.16 |
| JUnit | 5.10.5 |
| Awaitility | 4.2.2 (test) |

> core / client 只依赖 Aeron、Agrona、`aeron-common` 与 `slf4j-api`, 不传递 Spring; starter 额外 `api` 传递 `spring-boot-autoconfigure`.
> Spring Boot / SLF4J / JUnit / Awaitility 等版本由 `com.mcst:easyfk-dependencies:3.2.12` BOM 统一管理; Aeron / Agrona 锁定在本仓库 `settings.gradle` 的 version catalog.

### 13.2 与 broadcast aeron SDK 的版本搭配

aeron-cluster 依赖 `com.mcst:aeron-common` jar (版本由 easyfk-dependencies BOM 统一管理), 复用其中的 `Codec<T>` / `CodecRegistry` / `CodecIds` 契约. 只要这三个类签名不变, cluster 与 broadcast 两套 SDK 可独立升级.

| 场景 | 推荐 |
|---|---|
| 项目同时用 broadcast + cluster | 两套 jar 都用最新版即可, 各自独立升级 |
| 仅用 cluster | 不需要引 broadcast jar |
| 自定义 codec | 同时注册到两套 `CodecRegistry`, codec 类本身 v1+ 二进制兼容 |

### 13.3 wire / snapshot 兼容承诺

| 协议 | 版本 | 承诺 |
|---|---|---|
| `ClusterFrameProtocol` MAGIC = `'A','E','C','L'` | 永远不改 | wire 兼容性的根 |
| `ClusterFrameProtocol` VERSION_V1 | 改成 V2 时框架保留对 V1 的兼容解码 | |
| `ClusterFrameType` 已分配 type id | 0x01-0x04 永久占用 | 新增类型分配新 id |
| `SnapshotMagic` MAGIC = `'A','E','C','S'` | 永远不改 | snapshot 兼容性的根 |
| `SnapshotMagic` FRAMEWORK_VERSION | V1 (内联) / V2_EXTERNAL (异步 manifest) 已分配; 读取侧按版本分发, 对旧版本保持兼容 | |
| `BUSINESS_VERSION` | <b>业务方自管</b>, 改了要兼容旧版本读取 | |

### 13.4 升级 SDK 风险评估

业务方升级 aeron-cluster SDK 版本时:

| 升级位 | 风险 | 检查清单 |
|---|---|---|
| patch | 低 | 跑业务 IT |
| minor | 中 | 跑全套 IT + 检查 deprecated API |
| major | 高 | 看 changelog, 可能需要改业务代码; 滚动升级前先在测试环境跑 |

业务方升级 Aeron / Agrona / Spring Boot 版本时:

| 升级位 | 谁负责 |
|---|---|
| Aeron / Agrona | 框架维护组锁定一致版本; 业务方不要单独覆盖 (`exclude` 某个 transitive) |
| Spring Boot | 业务方控制; 框架基于 Spring Boot 3.x (jakarta 命名空间) |
| SLF4J | 业务方控制 |

---

*对应 SDK 版本 3.2.12 (group `com.mcst`).*
*遇到本文档没覆盖的问题 -> 看 `docs/Cluster架构设计.md` 内部细节, 或在仓库提 issue.*

