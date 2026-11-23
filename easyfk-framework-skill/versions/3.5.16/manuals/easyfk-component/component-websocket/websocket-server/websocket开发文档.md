# EasyFK WebSocket Server 开发文档

## 1. 项目概述

`websocket-server` 是 EasyFK 框架中的 WebSocket 服务组件，基于 **Netty** 构建高性能 WebSocket 服务器，提供实时消息推送能力。支持多策略消息推送、频道订阅管理、JWT 认证、HMAC-SHA256 接口鉴权，以及基于 Disruptor 的高性能异步消息发送。

### 1.1 技术栈

| 技术 | 用途 |
|------|------|
| Netty | WebSocket 服务器核心，处理连接、编解码、消息收发 |
| Disruptor (LMAX) | 高性能无锁队列，用于消息发送的异步处理 |
| Caffeine | 高性能本地缓存，管理用户会话数据与活跃时间 |
| JWT | 用户身份认证与令牌验证 |
| HMAC-SHA256 | 接口签名鉴权（含时间戳、nonce 防重放） |
| Spring Boot AutoConfiguration | 自动配置与 Bean 管理 |
| Fastjson2 | JSON 序列化/反序列化 |

### 1.2 模块依赖

```gradle
dependencies {
    api project(':component-cache:cache-caffeine')
    api project(':component-websocket:websocket-api')
    api('com.mcst:queue-disruptor')
    api('com.mcst:easyfk-authority')
    api('com.mcst:web-base')
    api('io.netty:netty-all')
}
```

父项目 `component-websocket` 统一依赖了 `com.mcst:easyfk-core`；`websocket-api` 的 `build.gradle` 为空，group/version/仓库由根工程统一管理。

---

## 2. 项目结构

```
websocket-server/
├── build.gradle
└── src/main/
    ├── java/com/mcst/easyfk/websocket/
    │   ├── config/
    │   │   └── ServerConfig.java              # Spring Boot 自动配置类
    │   ├── enums/
    │   │   └── EventType.java                 # 事件类型枚举
    │   ├── handler/
    │   │   ├── UserEventHandler.java          # 用户事件处理器接口（业务方实现）
    │   │   └── WebSocketHandler.java          # WebSocket 核心处理器
    │   ├── interceptor/
    │   │   ├── AuthInterceptor.java           # 认证拦截器标记接口（握手属性常量、会话ID生成）
    │   │   ├── DefaultAuthInterceptor.java    # 默认认证拦截器
    │   │   ├── HandshakeResult.java           # 握手结果对象
    │   │   └── WebSocketInterceptor.java      # 拦截器接口
    │   ├── manager/
    │   │   ├── impl/
    │   │   │   └── SocketManagerImpl.java     # Socket 管理器实现
    │   │   ├── ISocketManager.java            # Socket 管理器接口
    │   │   └── WsUserDataManager.java         # 用户会话数据管理器
    │   ├── properties/
    │   │   └── WebSocketProperties.java       # 配置属性类
    │   ├── security/
    │   │   ├── NonceValidator.java            # nonce 防重放校验器
    │   │   └── TrustedProxyMatcher.java       # 可信代理 IP/CIDR 匹配
    │   ├── sender/
    │   │   ├── SessionSendDispatcher.java     # 消息发送分发器（Disruptor 分片）
    │   │   ├── SessionSendEvent.java          # 发送事件对象
    │   │   ├── SessionSendWorker.java         # 实际发送工作器
    │   │   ├── WebSocketMessageSender.java    # 消息发送器（核心）
    │   │   └── WsSendProcessor.java           # Disruptor 消费处理器
    │   ├── server/
    │   │   ├── PushMessageServer.java         # 消息推送服务入口（实现 IPushWsMsgApi）
    │   │   └── WebSocketServer.java           # Netty WebSocket 服务器
    │   ├── strategy/
    │   │   ├── impl/
    │   │   │   ├── NotificationPushStrategy.java      # 通知推送策略（全员广播）
    │   │   │   └── UserPushStrategy.java              # 用户推送策略（定点推送）
    │   │   ├── MessagePushStrategy.java       # 推送策略接口
    │   │   └── MessagePushStrategySelector.java  # 策略选择器
    │   ├── util/
    │   │   └── SecuritySignUtil.java          # 安全签名工具类
    │   └── vo/
    │       ├── PushMessage.java               # 推送消息对象
    │       └── ResponseMessage.java           # 响应消息对象
    └── resources/META-INF/spring/
        └── org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

---

## 3. 核心组件详解

### 3.1 WebSocketServer — Netty 服务器

**文件**: `server/WebSocketServer.java`

Netty WebSocket 服务器的启动与关闭管理。实现 `SmartLifecycle`，在容器刷新阶段**同步**绑定端口；SSL 配置缺失/证书加载失败、端口被占用等启动失败会抛出 `IllegalStateException`，导致 Spring 应用启动失败（不会出现应用启动但端口未监听的情况）。容器关闭时通过 `stop()` 释放端口与线程组。

**Pipeline 组成**:

| Handler | 作用 |
|---------|------|
| `IdleStateHandler` | 空闲超时检测，超时时长由 `sessionTimeoutSeconds` 配置 |
| `HttpServerCodec` | HTTP 编解码器（WebSocket 握手基于 HTTP） |
| `ChunkedWriteHandler` | 分块写入处理器 |
| `HttpObjectAggregator` | HTTP 消息聚合器，最大内容长度由 `maxContentLength` 配置 |
| `WebSocketServerCompressionHandler` | WebSocket 消息压缩 |
| `WebSocketFrameAggregator` | 将分片帧聚合为完整消息，聚合后最大长度为 `maxFrameSize`，超出时关闭连接 |
| `WebSocketHandler` | 业务处理器（Sharable，全局单例） |

**关键配置项**:

| Socket 选项 | 值 | 说明 |
|------------|-----|------|
| `SO_BACKLOG` | 1024 | 连接等待队列大小 |
| `SO_REUSEADDR` | true | 地址复用 |
| `SO_KEEPALIVE` | true | TCP 保活 |
| `TCP_NODELAY` | true | 禁用 Nagle 算法，减少延迟 |
| `WRITE_BUFFER_WATER_MARK` | 8KB / 16KB | 写缓冲区水位线 |

### 3.2 WebSocketHandler — 核心处理器

**文件**: `handler/WebSocketHandler.java`

`@ChannelHandler.Sharable` 标注，全局共享单例。负责处理 WebSocket 连接的完整生命周期。

#### 3.2.1 连接建立流程

```
客户端发起 HTTP 升级请求
    ↓
handleHttpRequest()
    ↓
执行拦截器链 beforeHandshake()（按 order 排序，正序执行）
    ↓ 全部通过
从拦截器属性获取 userSessionId
    ↓
创建握手器（协议版本不支持则直接拒绝）
    ↓
socketManager.connectUser() 建立连接
    ↓
更新会话活跃时间
    ↓
WebSocket 协议握手
    ↓
向下游派发 connect 事件（所有连接，已登录的携带 userId/accountId）+ 发送欢迎消息
    ↓
执行拦截器链 afterHandshake()（逆序执行）
```

#### 3.2.2 消息处理流程

客户端发送的 `TextWebSocketFrame` 被解析为 `WsUserOptParam`，根据 `eventType` 分类处理：

| eventType | 处理逻辑 |
|-----------|---------|
| `pong` | 更新会话活跃时间（心跳响应） |
| `online` | 返回会话在线状态确认 |
| `connect` | 拒绝（该事件仅由服务端派发，防止客户端伪造连接事件） |
| 其他（如 subscribe/unsubscribe） | 如开启鉴权则验证签名，补齐身份信息后透传给 `UserEventHandler`，订阅语义完全由业务方实现 |

其他帧与异常输入：

| 输入 | 处理 |
|------|------|
| 无法解析为 `WsUserOptParam` 的文本（非 JSON、数组、`null` 等） | 回复 `success=false`“消息格式错误：必须是符合协议的JSON对象”，连接保持 |
| 分片文本消息 | 由 `WebSocketFrameAggregator` 聚合后按普通文本处理 |
| 二进制帧 | 发送关闭帧 `1003`（INVALID_MESSAGE_TYPE）并关闭连接 |
| 孤立续帧 | 被聚合器丢弃 |
| 已被同会话新连接接管的旧连接上的文本帧 | 忽略 |

> **注意**: 用户身份只在握手阶段确定（连接时携带 `Access-Token`），登录状态变化时客户端需断开重连。握手成功后服务端会向下游 `UserEventHandler` 派发一次 `connect` 事件（登录信息已合并在该事件中：匿名连接仅携带 userSessionId/clientId/clientType，已登录连接额外携带 userId/accountId），业务据此建立"会话 ↔ 用户"的关联。

消息处理通过独立的线程池 `messageHandleExecutor` 异步执行，不阻塞 Netty 的 I/O 线程。

#### 3.2.3 心跳机制

- **定时心跳任务**: 由 `heartbeatExecutor` 以 `heartbeatIntervalSeconds` 为间隔定期执行
- **心跳发送线程池**: `heartbeatSendExecutor` 并行发送 Ping 消息
- **超时检测**: 检查每个会话的最后活跃时间，超过 `sessionTimeoutSeconds` 则关闭连接
- **Ping 消息格式**: 使用 `PushMessage` 封装，channel 为 `heartbeat`

#### 3.2.4 连接关闭

- `channelInactive`: 连接关闭时清理 `socketManager`、`sessionLastActiveTime`、`WsUserDataManager`
- `userEventTriggered`: Netty `IdleStateEvent` 触发超时关闭
- `exceptionCaught`: 区分客户端主动断开与服务端异常，避免无意义的错误日志

### 3.3 拦截器体系

#### WebSocketInterceptor 接口

```java
public interface WebSocketInterceptor {
    HandshakeResult beforeHandshake(ChannelHandlerContext ctx, FullHttpRequest request, 
                                     Map<String, Object> attributes);
    default void afterHandshake(...) {}
    default int getOrder() { return 0; }
}
```

- `beforeHandshake`: 握手前拦截，可用于 Token 验证、IP 白名单、限流等
- `afterHandshake`: 握手后处理，可用于日志记录、事件触发
- `getOrder`: 数值越小越先执行

#### AuthInterceptor — 认证拦截器标记接口

`AuthInterceptor extends WebSocketInterceptor`，定义握手属性常量（`ATTR_USER_SESSION_ID`、`ATTR_WS_USER_DATA` 等）和 `buildUserSessionId(clientType, clientId, userId)`。

- 容器中存在任意 `AuthInterceptor` Bean 时，不再注册 `DefaultAuthInterceptor`（替换默认认证）。
- 配置 `default-auth-enabled: false` 也会关闭默认认证。
- 只实现 `WebSocketInterceptor` 的 Bean 会**追加**到拦截器链，不会替换默认认证。
- 拦截器链中没有任何 `AuthInterceptor` 时，启动输出 WARN（握手会因缺少 userSessionId 返回 500 `MISSING_SESSION_ID`）。

自定义认证拦截器必须写入 `ATTR_USER_SESSION_ID`（建议用 `AuthInterceptor.buildUserSessionId` 生成），并写入 `ATTR_WS_USER_DATA`（`WsUserData`），框架在 `connectUser` 成功后再写入 `WsUserDataManager`。

#### DefaultAuthInterceptor — 默认认证拦截器

**执行优先级**: `order = -100`（最先执行）

**处理流程**:
1. 解析客户端 IP：仅当 TCP 对端命中 `trusted-proxies` 时才读取转发头，否则用 TCP 地址（见 9.2）
2. 提取 `clientType`（默认 `APP`，最长 32 字符）和 `clientId`（最长 128 字符）。开启鉴权时 `Client-ID` 必填（缺失返回 400 `CLIENT_ID_MISSING`）；未开启鉴权且未传时生成一次性随机 ID
3. 如开启接口鉴权：校验时间戳时效 → HMAC-SHA256 签名 → nonce 防重放（见 3.6）
4. 提取 JWT Token 并验证（可带 `Bearer ` 前缀）；`mustLogin=true` 时 Token 必填且必须取到 UserData（否则 401 `AUTH_USER_MISSING`）
5. 生成与身份绑定的会话标识：`AuthInterceptor.buildUserSessionId(clientType, clientId, userId)`，即对 clientType、clientId、`u:{userId}`（匿名为 `anonymous`）做长度前缀拼接后取 SHA256
6. 将 `WsUserData` 放入握手属性 `ATTR_WS_USER_DATA`，由 `WebSocketHandler` 在连接注册成功后写入 `WsUserDataManager`

会话替换规则：只有同一用户（或同为匿名）使用相同 clientType + clientId 的新连接才会替换旧连接；不同用户使用相同 Client-ID 会得到不同会话，无法顶替已登录会话。

**支持的请求参数提取方式**（同时支持请求头与查询参数）:

| 参数名 | 请求头 Key | 查询参数 Key |
|-------|-----------|------------|
| Token | `Access-Token` | `Access-Token` |
| 客户端ID | `Client-ID` | `Client-ID` |
| 客户端类型 | `Client-Type` | `Client-Type` |
| 随机数 | `Request-Nonce` | `Request-Nonce` |
| 时间戳（毫秒） | `Timestamp` | `Timestamp` |
| 签名 | `Reset-Sign` | `Reset-Sign` |

**握手错误码**: `AUTH_TOKEN_MISSING` / `AUTH_TOKEN_INVALID` / `AUTH_USER_MISSING` / `TIMESTAMP_INVALID` / `SIGN_INVALID` / `NONCE_REUSED`（401），`ORIGIN_NOT_ALLOWED`（403），`PATH_NOT_FOUND`（404），`INVALID_REQUEST` / `CLIENT_ID_MISSING` / `INVALID_CLIENT_ID` / `INVALID_CLIENT_TYPE`（400），`MISSING_SESSION_ID` / `CONNECTION_FAILED` / `HANDSHAKE_ERROR` / `INTERCEPTOR_ERROR`（500）。

### 3.4 会话管理

#### ISocketManager 接口 & SocketManagerImpl 实现

管理在线用户的 Channel 映射关系：

```
userSessionId  ←→  Channel（双向映射）
```

**核心方法**:
- `connectUser(channel, userSessionId)`: 建立连接（同会话重连时原子替换并关闭旧连接）
- `disconnectUser(userSessionId, channel)`: 断开连接（带 Channel 一致性校验），并回调下游 `clearUserSubscriptions(WsUserData)` 清理业务侧订阅（回调异常会被记录，不影响后续清理）
- `getUserSession(userSessionId)`: 获取用户 Channel（自动检测 Channel 活跃状态）
- `getAllUserSessions()`: 获取所有在线 Channel
- `getUserSessionId(channel)`: 反向查找用户 ID

> 订阅关系完全由业务方自持，组件内不存储任何订阅数据，仅在连接断开时回调下游清理。

#### WsUserDataManager — 用户数据管理

使用 `Caffeine` 缓存管理用户会话数据，支持以下三种索引（均随连接生命周期管理，握手写入、断开清理，不按时间过期）：

| 缓存 | Key | Value | 容量 |
|------|-----|-------|------|
| `WS_USER_DATA_CACHE` | userSessionId | WsUserData | 10万 |
| `USER_ID_SESSION_CACHE` | userId | Set\<userSessionId\> | 10万 |
| `ACCOUNT_ID_SESSION_CACHE` | accountId | Set\<userSessionId\> | 10万 |

支持一个用户/账户多个会话（多端登录/多标签页场景）。`WsUserDataManager` 是进程内静态缓存，不是 Bean，不能替换。

### 3.5 消息发送体系

#### 消息发送架构

```
PushMessageServer（IPushWsMsgApi）
    ↓ pushMessage(PushWsMessageParam)
MessagePushStrategySelector
    ↓ select() 选择策略
MessagePushStrategy（内置2种 + 容器中业务自定义的策略 Bean）
    ↓ push()
WebSocketMessageSender
    ├─ sendMessageToUser()            → SessionSendDispatcher → Disruptor → SessionSendWorker
    ├─ sendMessageToUserByUserId()    → SessionSendDispatcher → Disruptor → SessionSendWorker
    ├─ sendMessageToUserByAccountId() → SessionSendDispatcher → Disruptor → SessionSendWorker
    └─ broadcastToAll()               → batchBroadcast()（直接批量写入，跳过 Disruptor）
```

#### 消息推送策略（策略模式）

| 策略 | 优先级 | 匹配条件 | 推送方式 |
|------|--------|---------|---------|
| `NotificationPushStrategy` | 0（最高） | channel = "notification"，无用户标识 | 全员广播 |
| `UserPushStrategy` | 2 | 有 userSessionId / userId / accountId 任意一个 | 定点推送（channel=notification 且带用户标识时也走此策略，实现通知定点推送） |

> 用户标识指 `userSessionId`、`userId`、`accountId` 三个字段。三者均支持逗号分隔的多个值，同时传入多个维度时分别推送；userId/accountId 通过 `WsUserDataManager` 的反向索引解析为该用户/账户的全部在线会话（多端登录时每端都会收到）。
>
> 订阅关系由业务方自持：业务根据自己存储的订阅关系算出目标用户，构建带用户标识的推送参数调用本组件；不带用户标识且非 notification 频道的参数没有匹配策略，`pushMessage` 返回 `success=false` 的失败结果（说明需携带用户标识或使用 notification 广播），不向调用方抛异常；策略内的参数校验异常同样转为失败结果。
>
> 容器中所有 `MessagePushStrategy` Bean（含业务自定义）都会被选择器收集，按 `getOrder()` 升序匹配。

#### SessionSendDispatcher — Disruptor 分片分发

用于单用户/少量用户的消息发送：

- **分片机制**: 根据 `userSessionId` 的 hash 值选择分片，同一会话的消息进入同一分片队列
- **保序**: `WsSendProcessor` 实现 `KeyOrderedProcessor`，以 Channel id 为保序键，分片内多 worker 时同一 Channel 的消息仍按入队顺序发送
- **队列类型**: 基于 LMAX Disruptor 的 RingBuffer
- **丢弃**: 入队等待超过 `sendQueueTryTimeoutMs`（默认 50ms）或 Channel 不可写时丢弃消息，**不保证送达**
- **监控统计**: 每 10 秒输出入队/队列满丢弃/发送/不可写丢弃及广播统计；有丢弃时以 WARN 输出（天然限频），否则以 INFO 输出

#### WebSocketMessageSender — 消息发送器

性能优化方案：

1. **零拷贝**: 使用 `retainedDuplicate()` 共享底层 ByteBuf，避免数据复制
2. **批量写入**: `batchBroadcast()` 先批量 `write()`，再统一 `flush()`，减少系统调用

**背压控制**: 发送前检查 `channel.isWritable()`，不可写时跳过，防止消息积压。

### 3.6 安全签名

**文件**: `util/SecuritySignUtil.java`

#### HMAC-SHA256 签名
```
签名数据 = ClientType=xxx&ClientId=xxx&Nonce=xxx&Timestamp=xxx&Param=xxx
签名结果 = hex(HMAC-SHA256(签名数据, secret))
```

- **Timestamp**: 毫秒时间戳十进制字符串。握手取请求头/查询参数 `Timestamp`，业务消息取 JSON 字段 `timestamp`。
- **Param**: 握手为空串；业务消息为 `eventData` 按顶层 key ASCII 升序（TreeMap）后的 fastjson2 序列化结果，空 eventData 为空串。
- **校验顺序**: 时间戳时效（`|now - timestamp| ≤ securityTimestampToleranceSeconds`，默认 300 秒）→ 签名（`MessageDigest.isEqual` 常量时间比较，大小写不敏感）→ nonce 防重放（签名通过后才登记）。
- **nonce TTL**: 取 `max(securityNonceTtlSeconds, 2 × securityTimestampToleranceSeconds)`，覆盖时间戳的整个有效区间，窗口外的历史请求因时间戳过期被拒，不能重放。
- `pong` / `online` / `connect` 不验签。

> MD5 签名方式已删除。

---

## 4. 配置参数

配置前缀：`easyfk.config.websocket`

### 4.1 基础配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `path` | `/ws` | WebSocket 访问路径，握手时校验（忽略查询参数与末尾斜杠），为空时不校验 |
| `port` | `8081` | Netty 服务器监听端口 |
| `mustLogin` | `false` | 是否要求登录才能连接（Token 有效且能取到 UserData） |
| `securitySecret` | `easyfk@ws#2026!` | 接口鉴权密钥（生产环境务必修改，开启鉴权且未修改会输出告警日志） |
| `enableSecurity` | `false` | 是否开启接口鉴权（开启后 `Client-ID`、`Request-Nonce`、`Timestamp`、`Reset-Sign` 必填） |
| `securityTimestampToleranceSeconds` | `300` | 签名时间戳允许偏差（秒） |
| `securityNonceTtlSeconds` | `600` | nonce 防重放窗口时长（秒），实际生效值不小于 2 × 时间戳偏差 |
| `defaultAuthEnabled` | `true` | 是否注册 `DefaultAuthInterceptor`；false 时需自行提供认证拦截器 |
| `trustedProxies` | `[]` | 可信反向代理 IP/CIDR 列表；为空时不信任任何转发头，非法条目启动报错 |
| `allowCrossOrigin` | `true` | 是否允许跨域：true 时按 `allowedOrigins` 白名单校验 Origin 头；false 时仅允许与 Host 同源的请求（无 Origin 头的请求始终放行） |
| `allowedOrigins` | `["*"]` | 允许的跨域来源白名单，包含 `*` 时全部放行 |
| `sessionTimeoutSeconds` | `1800` | 会话超时时间（秒，默认30分钟） |
| `heartbeatIntervalSeconds` | `30` | 心跳检测间隔（秒） |
| `maxFrameSize` | `65536` | WebSocket 帧最大大小，也是分片消息聚合后的最大长度（字节，64KB） |
| `maxContentLength` | `65536` | HTTP 最大内容长度（字节，64KB） |

### 4.2 Netty 线程配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `bossThreads` | `1` | Boss 线程数（接受连接） |
| `workerThreads` | `0` | Worker 线程数（0=CPU核心数×2） |

### 4.3 SSL 配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `sslEnabled` | `false` | 是否启用 SSL（wss），启用后客户端使用 `wss://` 连接 |
| `sslCertPath` | - | SSL 证书链文件路径（X.509 PEM 格式），启用 SSL 时必填 |
| `sslKeyPath` | - | SSL 私钥文件路径（PKCS#8 PEM 格式），启用 SSL 时必填 |

> **注意**: `sslEnabled=true` 但证书或私钥未配置/加载失败时，Spring 应用启动失败。生产环境也可以选择在 Nginx/负载均衡层做 SSL 终结，此时保持 `sslEnabled=false` 即可。

### 4.4 性能配置 (`easyfk.config.websocket.performance`)

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `sendShardCount` | `8` | Disruptor 发送队列分片数 |
| `sendQueueWorkersPerShard` | `1` | 每个分片的工作线程数（大于1时仍按 Channel 保序） |
| `sendQueueBufferSize` | `16384` | 每个分片的 RingBuffer 大小（必须是2的幂，最小1024） |
| `sendQueueTryTimeoutMs` | `50` | 入队最大等待时间（毫秒），超时丢弃并计数 |
| `sendQueueThreadPrefix` | `ws-send-` | 发送线程名前缀 |
| `sendQueueWaitStrategy` | `BLOCKING` | Disruptor 等待策略（BLOCKING/YIELDING/BUSY_SPIN，非法值回退 BLOCKING）；YIELDING/BUSY_SPIN 下每个发送线程空闲时也占用 CPU |
| `heartbeatPoolCoreSize` | `max(16, CPU×2)` | 心跳线程池核心线程数 |
| `heartbeatPoolMaxSize` | `max(32, CPU×4)` | 心跳线程池最大线程数 |
| `heartbeatPoolQueueSize` | `50000` | 心跳线程池队列容量 |
| `messagePoolCoreSize` | `max(32, CPU×4)` | 消息处理线程池核心线程数 |
| `messagePoolMaxSize` | `max(64, CPU×8)` | 消息处理线程池最大线程数 |
| `messagePoolQueueSize` | `20000` | 消息处理线程池队列容量 |

### 4.5 配置示例

```yaml
easyfk:
  config:
    websocket:
      path: /ws
      port: 8081
      mustLogin: false
      enableSecurity: true
      securitySecret: "your-production-secret-key"
      securityTimestampToleranceSeconds: 300
      trustedProxies:
        - 10.0.0.0/8          # Nginx / SLB 所在网段
      allowedOrigins:
        - https://www.example.com
      sessionTimeoutSeconds: 1800
      heartbeatIntervalSeconds: 30
      performance:
        # 默认 8 × 1 线程、BLOCKING 已适合大多数场景；高推送量时再调大
        sendShardCount: 16
        sendQueueWorkersPerShard: 2
        sendQueueWaitStrategy: BLOCKING
```

---

## 5. 扩展开发指南

### 5.1 实现自定义用户事件处理器

业务方通过实现 `UserEventHandler` 接口来处理客户端发送的业务事件：

```java
@Component
public class MyUserEventHandler implements UserEventHandler {

    @Override
    public BaseResult<?> handleUserEvent(WsUserOptParam param) {
        String eventType = param.getEventType();
        Map<String, Object> eventData = param.getEventData();
        
        switch (eventType) {
            case "connect":
                // 连接建立（服务端派发）：param中携带userSessionId/clientId/clientType，
                // 已登录连接还携带userId/accountId，业务据此建立 会话<->用户 关联
                return BRBuilder.successResult();
            case "subscribe":
                // 处理订阅逻辑：订阅关系存储在业务系统中，组件不感知
                return BRBuilder.successResult();
            case "unsubscribe":
                // 处理取消订阅逻辑
                return BRBuilder.successResult();
            default:
                // 处理其他自定义事件
                return BRBuilder.successResult();
        }
    }

    @Override
    public void clearUserSubscriptions(WsUserData userData) {
        // 会话断开（或被同会话新连接替换）时清理业务层订阅数据，按 userSessionId 清理；
        // clientId 在不同 clientType / 用户之间可能重复，不要按 clientId 清理
        removeBySessionId(userData.getUserSessionId());
    }
}
```

### 5.2 实现自定义拦截器

业务方可以实现 `WebSocketInterceptor` **追加**自定义拦截逻辑（不会替换默认认证）：

```java
@Component
public class IpWhitelistInterceptor implements WebSocketInterceptor {

    @Override
    public HandshakeResult beforeHandshake(ChannelHandlerContext ctx, 
                                           FullHttpRequest request, 
                                           Map<String, Object> attributes) {
        String ip = getClientIp(ctx);
        if (!isAllowed(ip)) {
            return HandshakeResult.forbidden("IP_BLOCKED", "IP not in whitelist");
        }
        return HandshakeResult.success();
    }

    @Override
    public int getOrder() {
        return -200; // 在默认认证拦截器之前执行
    }
}
```

> 需要可信的客户端 IP 时，优先从 `ATTR_WS_USER_DATA` 中的 `clientIp`（默认认证已按 `trusted-proxies` 解析）读取，或自行按同样规则校验 TCP 对端，不要直接信任转发头。

#### 替换默认认证

实现 `AuthInterceptor` 并注册为 Bean，默认的 `DefaultAuthInterceptor` 将不再注册：

```java
@Component
public class MyAuthInterceptor implements AuthInterceptor {

    @Override
    public HandshakeResult beforeHandshake(ChannelHandlerContext ctx, FullHttpRequest request,
                                           Map<String, Object> attributes) {
        String userId = authenticate(request);               // 业务自己的认证
        String clientId = request.headers().get("Client-ID");
        String clientType = "APP";
        String sessionId = AuthInterceptor.buildUserSessionId(clientType, clientId, userId);
        attributes.put(ATTR_USER_SESSION_ID, sessionId);
        attributes.put(ATTR_WS_USER_DATA, WsUserData.builder()
                .userSessionId(sessionId).userId(userId)
                .clientId(clientId).clientType(clientType).build());
        return HandshakeResult.success();
    }

    @Override
    public int getOrder() {
        return -100;
    }
}
```

### 5.3 服务端主动推送消息

通过 `PushMessageServer`（或其接口 `IPushWsMsgApi`）推送消息，返回值 `success=true` 只代表已入队，不代表送达：

```java
@Resource
private PushMessageServer pushMessageServer;   // 或 @Resource private IPushWsMsgApi pushWsMsgApi;

// 按会话ID推送（精确到某个连接）
PushWsMessageParam param = new PushWsMessageParam()
    .setUserSessionId("user-session-id")
    .setChannel("order")
    .setCategory("fill")
    .setData(Map.of("orderId", "12345", "status", "filled"));
pushMessageServer.pushMessage(param);

// 按用户ID推送（该用户所有在线会话，多端都会收到）
PushWsMessageParam paramByUser = new PushWsMessageParam()
    .setUserId("10001,10002")
    .setChannel("order")
    .setCategory("fill")
    .setData(Map.of("orderId", "12345", "status", "filled"));
pushMessageServer.pushMessage(paramByUser);

// 按账户ID推送（该账户所有在线会话）
PushWsMessageParam paramByAccount = new PushWsMessageParam()
    .setAccountId("acc-8888")
    .setChannel("order")
    .setCategory("fill")
    .setData(Map.of("orderId", "12345", "status", "filled"));
pushMessageServer.pushMessage(paramByAccount);

// 订阅类推送：业务根据自己存储的订阅关系算出目标会话，构建定点推送参数
// （例如订阅了 BTCUSDT 行情的会话列表由业务查询得到）
PushWsMessageParam param2 = new PushWsMessageParam()
    .setUserSessionId(String.join(",", subscriberSessionIds))
    .setChannel("quote")
    .setCategory("BTCUSDT")
    .setData(Map.of("price", "50000.00", "volume", "123.45"));
pushMessageServer.pushMessage(param2);

// 发送系统通知（全员广播）
PushWsMessageParam param3 = new PushWsMessageParam()
    .setChannel("notification")
    .setData(Map.of("title", "系统维护通知", "content", "系统将于凌晨2点维护", "level", "important"));
pushMessageServer.pushMessage(param3);

// 发送定点通知（仅指定用户收到，走 UserPushStrategy）
PushWsMessageParam param4 = new PushWsMessageParam()
    .setChannel("notification")
    .setUserId("10001")
    .setData(Map.of("title", "余额变动提醒", "content", "您的账户入账100元"));
pushMessageServer.pushMessage(param4);
```

### 5.4 通过 API 接口远程推送

`websocket-api` 模块定义了 `IPushWsMsgApi` 接口：

```java
public interface IPushWsMsgApi {
    BaseResult<?> pushMessage(PushWsMessageParam param);
}
```

`PushMessageServer` 实现了该接口，WebSocket 服务内可直接注入 `IPushWsMsgApi`。其他服务调用时，需要业务在 WebSocket 服务中通过 Controller / RPC 服务 / MQ 消费者暴露它，组件不提供远程实现。

只传 channel/category（无用户标识、非 notification）时返回失败结果，不会抛异常。

---

## 6. 自动配置

`ServerConfig` 通过 Spring Boot `@AutoConfiguration` 自动注册以下 Bean：

| Bean | 类型 | 说明 |
|------|------|------|
| `PushMessageServer` | 服务 | 消息推送服务入口（`IPushWsMsgApi` 实现） |
| `WebSocketServer` | 服务器 | Netty WebSocket 服务器（`SmartLifecycle`） |
| `WebSocketHandler` | 处理器 | WebSocket 核心处理器 |
| `DefaultAuthInterceptor` | 拦截器 | 默认认证拦截器；条件 `@ConditionalOnMissingBean(AuthInterceptor.class)` 且 `defaultAuthEnabled=true` |
| `SocketManagerImpl` | 管理器 | 在线用户管理 |
| `NonceValidator` | 安全 | nonce 防重放校验器 |
| `SessionSendWorker` | 发送器 | 消息发送工作器 |
| `SessionSendDispatcher` | 分发器 | Disruptor 分片分发器 |
| `WebSocketMessageSender` | 发送器 | 消息发送核心 |
| `NotificationPushStrategy` | 策略 | 通知推送策略（全员广播） |
| `UserPushStrategy` | 策略 | 用户推送策略（定点推送） |
| `MessagePushStrategySelector` | 选择器 | 策略选择器（收集容器中全部 `MessagePushStrategy`） |

除默认拦截器外，Bean 均使用 `@ConditionalOnMissingBean`，业务方可通过自定义同类型 Bean 覆盖。默认认证的替换方式见 3.3；`WsUserDataManager` 是静态工具类，不能通过 Bean 替换。

---

## 7. 线程模型

```
┌─────────────────────────────────────────────────────────────────┐
│                    Netty Thread Model                           │
│  BossGroup (1 thread)     →  接受连接                           │
│  WorkerGroup (N threads)  →  I/O 读写、编解码                    │
├─────────────────────────────────────────────────────────────────┤
│                    业务线程池                                     │
│  messageHandleExecutor    →  消息业务处理（WebSocketHandler）     │
│  heartbeatSendExecutor    →  心跳 Ping 发送                     │
│  heartbeatExecutor        →  心跳定时检测调度（单线程）            │
├─────────────────────────────────────────────────────────────────┤
│                    Disruptor 发送队列                             │
│  shardQueues[0..N-1]      →  单用户消息异步发送                   │
│  每个分片有独立的 Worker 线程                                     │
├─────────────────────────────────────────────────────────────────┤
│                    直接广播                                       │
│  WebSocketMessageSender   →  全员广播（跳过 Disruptor）          │
│  批量 write + 统一 flush                                        │
├─────────────────────────────────────────────────────────────────┤
│                    监控线程                                       │
│  ws-send-monitor          →  每10秒输出发送统计                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. API 模块（websocket-api）

### 8.1 数据对象

#### PushWsMessageParam — 推送消息参数

| 字段 | 类型 | 说明 |
|------|------|------|
| `channel` | String | 频道（如 kline, quote, order, notification, chat） |
| `category` | String | 类别（如具体产品ID） |
| `userSessionId` | String | 用户会话ID（多个逗号分隔） |
| `userId` | String | 用户ID（多个逗号分隔，解析为该用户的全部在线会话） |
| `accountId` | String | 账户ID（多个逗号分隔，解析为该账户的全部在线会话） |
| `data` | Map\<String, Object\> | 推送数据 |

#### WsUserOptParam — 用户操作参数

| 字段 | 类型 | 说明 |
|------|------|------|
| `eventType` | String | 事件类型 |
| `eventData` | Map\<String, Object\> | 事件数据 |
| `nonce` | String | 随机数（签名验证） |
| `timestamp` | Long | 毫秒时间戳（参与签名并校验时效） |
| `sign` | String | 签名（接口鉴权） |
| `userSessionId` / `userId` / `accountId` / `clientId` / `clientType` | String | 由服务端按连接身份补齐，客户端上行的值会被覆盖 |

### 8.2 枚举定义

#### ChannelTypeEnum — 频道类型

| 值 | Code | 说明 |
|----|------|------|
| `NOTIFICATION` | notification | 通知频道 |
| `CHAT` | chat | 聊天频道 |
| `HEARTBEAT` | heartbeat | 心跳频道 |
| `BIZ` | biz | 业务频道 |

#### NotificationLevel — 通知级别

| 值 | Code | 说明 |
|----|------|------|
| `NORMAL` | normal | 普通通知 |
| `IMPORTANT` | important | 重要通知 |
| `URGENT` | urgent | 紧急通知 |

#### EventType — 事件类型

| 值 | Code | 说明 |
|----|------|------|
| `CONNECT` | connect | 连接建立（服务端在握手成功后向下游派发，所有连接均派发；已登录连接携带 userId/accountId。不接受客户端上行） |
| `SUBSCRIBE` | subscribe | 订阅 |
| `UNSUBSCRIBE` | unsubscribe | 取消订阅 |
| `PING` | ping | 心跳检测（服务端发送） |
| `PONG` | pong | 心跳响应（客户端发送） |
| `ONLINE` | online | 检查在线状态 |

---

## 9. 部署注意事项

### 9.1 单机内存态架构与集群部署

本组件的连接映射（`SocketManagerImpl`）、用户会话数据（`WsUserDataManager`）均存储在**本机内存**中，组件本身不提供跨节点的会话共享或消息路由能力。多实例部署时需要业务侧自行解决推送路由，常见方案：

- **MQ 广播**：推送方将消息投递到 MQ（如 Kafka/RocketMQ），所有 WebSocket 节点各自消费并调用本地 `PushMessageServer`，目标用户不在本节点时静默跳过
- **粘性会话 + 路由表**：负载均衡按 clientId 做粘性转发，同时在 Redis 等共享存储中维护 userId → 节点 的路由表，推送方按路由表定向调用目标节点

### 9.2 反向代理配置

组件默认**不信任任何转发头**，客户端 IP 取 TCP 直连地址。经 Nginx/负载均衡接入时，把代理地址配置到 `trustedProxies`，并透传转发头：

- 只有 TCP 对端命中 `trustedProxies` 时才读取转发头
- `X-Forwarded-For` 从右往左跳过可信代理，取第一个不可信地址（全部可信时取最左侧）
- 没有可用的 XFF 时依次取 `X-Real-IP`、`Proxy-Client-IP`、`WL-Proxy-Client-IP`
- 非 IP 字面量的值一律忽略，不做 DNS 解析

```nginx
location /ws {
    proxy_pass http://websocket_backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_read_timeout 3600s;
}
```

### 9.3 安全建议

- 开启 `enableSecurity` 时务必修改默认 `securitySecret`（未修改会输出告警日志）
- 签名包含时间戳并校验时效（默认 ±300 秒），nonce 窗口至少为 2 倍偏差（默认 600 秒），客户端每次请求必须生成全新 nonce 并保持时钟同步
- 浏览器端签名需要把 `securitySecret` 下发到前端，密钥视同公开，签名只能防止随意伪造和重放，不能代替 `Access-Token` 做身份认证；需要更强保护时由服务端为每个用户/会话签发短期密钥，或只在可信客户端开启
- 会话标识与登录用户绑定，其他人使用相同 `Client-ID` 不能顶替已登录会话；匿名会话之间仍会按 Client-ID 互相替换
- 生产环境建议将 `allowedOrigins` 配置为具体域名，避免使用 `*`
- 不要把 Netty 端口直接暴露到公网后又把公网网段配置进 `trustedProxies`
