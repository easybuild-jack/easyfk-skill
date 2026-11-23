# easyfk-component-websocket Skill 参考文档

> 模块：`easyfk-component/component-websocket`（websocket-api / websocket-server）
> 坐标：`com.mcst:websocket-api`、`com.mcst:websocket-server`
> 依据：两个子模块源码 + `websocket开发文档.md`、`websocket前端对接文档.md`、`websocket模块特点.md`、`easyfk-base/EasyFK框架开发手册.md` §3.12 / §4.5
> 文档与源码不一致时 **以源码为准**，差异见文末「复查记录」。

---

## 1. 模块定位

| 子模块 | 内容 | 依赖 |
|---|---|---|
| websocket-api | `PushWsMessageParam`、`WsUserOptParam`、`WsUserData`、`ChannelTypeEnum`、`NotificationLevel`、接口 `IPushWsMsgApi` | 父工程统一 `api easyfk-core`；`build.gradle` 为空，group/version/仓库均由根工程管理 |
| websocket-server | 基于 **Netty 独立端口** 的 WebSocket 服务：握手鉴权、会话管理、心跳、定点/广播推送 | `cache-caffeine`、`websocket-api`、`queue-disruptor`、`easyfk-authority`、`web-base`、`netty-all` |

- 包名统一为 `com.mcst.easyfk.websocket.*`（旧手册中的 `com.mcst.easyfk.ws.*` 不存在）。
- 服务端只维护“连接”和“身份索引”，**不存储任何订阅关系**；订阅语义由业务通过 `UserEventHandler` 自行实现。
- 全部状态在本机内存中，组件不提供跨节点路由。
- `PushMessageServer` 实现了 `IPushWsMsgApi`，在 WebSocket 服务内可直接注入 `IPushWsMsgApi`；其他服务调用需业务自行暴露（HTTP/RPC/MQ）。

---

## 2. 自动配置

`ServerConfig`（`@AutoConfiguration`，无开关，引入 websocket-server 即启动 Netty 服务）：

| Bean | 条件 | 说明 |
|---|---|---|
| `WebSocketServer` | `@ConditionalOnMissingBean` | 实现 `SmartLifecycle`，容器刷新时**同步**绑定端口；SSL 配置缺失/证书加载失败、端口占用等会抛 `IllegalStateException`，**Spring 应用启动失败** |
| `WebSocketHandler` | 同上 | `@Sharable` 单例；内含心跳检测、心跳发送池、消息处理池；拦截器链中没有任何 `AuthInterceptor` 时启动输出 WARN |
| `defaultAuthInterceptor`（`DefaultAuthInterceptor`） | `@ConditionalOnMissingBean(AuthInterceptor.class)` + `default-auth-enabled=true`（默认） | 声明任意 `AuthInterceptor` Bean 或配置 `default-auth-enabled: false` 即可替换；只实现 `WebSocketInterceptor` 的 Bean 是追加 |
| `ISocketManager`（`SocketManagerImpl`） | `@ConditionalOnMissingBean` | userSessionId ↔ Channel 双向映射 |
| `NonceValidator` | 同上 | TTL 取 `max(security-nonce-ttl-seconds, 2 × security-timestamp-tolerance-seconds)`；开启鉴权且仍用默认密钥时输出 WARN |
| `SessionSendWorker` / `SessionSendDispatcher` / `WebSocketMessageSender` | 同上 | 定点消息走 Disruptor 分片队列；广播直接批量 write |
| `NotificationPushStrategy` / `UserPushStrategy` / `MessagePushStrategySelector` | 同上 | 选择器注入容器中**全部** `MessagePushStrategy` Bean（含业务自定义），构造时按 `getOrder()` 排序 |
| `PushMessageServer` | 同上 | 服务端推送入口，实现 `IPushWsMsgApi` |

前置条件：
- `DefaultAuthInterceptor` 以 `@Resource` 注入 `JwtManager`（web-base 无条件注册），以 `ObjectProvider<UserDataManager>` 获取 `UserDataManager`。容器中没有 `UserDataManager`（authority 默认 `easyfk.config.login.cache-type=database` 时不注册）时，携带 Token 的握手只能校验 JWT、拿不到 userId，按匿名连接；`must-login=true` 时则以 401 `AUTH_USER_MISSING` 拒绝。需要登录连接时配置 `cache-type: redis` 或自行注册 `UserDataManager`。

---

## 3. 配置（前缀 `easyfk.config.websocket`）

```yaml
easyfk:
  config:
    websocket:
      port: 8081                      # Netty 独立端口，与 server.port 无关
      path: /ws                       # 握手路径，忽略查询参数与末尾斜杠，不匹配返回 404 PATH_NOT_FOUND；为空时不校验
      must-login: false               # true 时必须携带有效 JWT 且能取到 UserData
      enable-security: false          # 握手和业务消息的 HMAC-SHA256 签名
      security-secret: easyfk@ws#2026!  # 默认值，开启鉴权时必须修改
      security-timestamp-tolerance-seconds: 300  # 签名时间戳允许偏差
      security-nonce-ttl-seconds: 600            # 实际 TTL ≥ 2 × 时间戳偏差
      default-auth-enabled: true      # false 时不注册 DefaultAuthInterceptor
      trusted-proxies: []             # 可信反向代理 IP/CIDR；默认空 = 不信任任何转发头
      allow-cross-origin: true        # true：按 allowed-origins 校验；false：只允许与 Host 同源
      allowed-origins: ["*"]          # 无 Origin 头的请求总是放行
      session-timeout-seconds: 1800
      heartbeat-interval-seconds: 30
      max-frame-size: 65536           # 单帧最大负载，也是分片消息聚合后的最大长度
      max-content-length: 65536       # 握手 HTTP 请求最大长度
      boss-threads: 1
      worker-threads: 0               # 0 = Netty 默认（CPU × 2）
      ssl-enabled: false              # true 时必须配置下面两项（PEM 证书链 + PKCS#8 私钥）
      ssl-cert-path:
      ssl-key-path:
      performance:
        send-shard-count: 8
        send-queue-workers-per-shard: 1
        send-queue-buffer-size: 16384       # 最小 1024
        send-queue-try-timeout-ms: 50       # 入队等待超时，超时即丢弃并计数
        send-queue-thread-prefix: ws-send-
        send-queue-wait-strategy: BLOCKING  # BLOCKING / YIELDING / BUSY_SPIN，非法值回退 BLOCKING
        heartbeat-pool-core-size: max(16, CPU×2)
        heartbeat-pool-max-size: max(32, CPU×4)
        heartbeat-pool-queue-size: 50000
        message-pool-core-size: max(32, CPU×4)
        message-pool-max-size: max(64, CPU×8)
        message-pool-queue-size: 20000
```
- 默认创建 8 × 1 = 8 个 Disruptor 发送线程，等待策略 `BLOCKING`，空闲时不占 CPU。推送量很大且对延迟敏感时再调大分片数/线程数或改用 `YIELDING`（每个发送线程空闲时也会占用 CPU）；`queue-disruptor` 目前不提供 `SLEEPING` 策略。
- `ssl-enabled=true` 但证书缺失或加载失败、端口被占用时，`WebSocketServer.start()` 抛异常，Spring 应用启动失败。
- `trusted-proxies` 只接受 IP 字面量或 CIDR（如 `10.0.0.0/8`、`::1`），非法条目在启动时报错。

---

## 4. 连接与握手

### 4.1 握手参数（请求头优先，其次同名查询参数）

| 参数 | Key | 说明 |
|---|---|---|
| Token | `Access-Token` | JWT 原文，可带 `Bearer ` 前缀（不区分大小写，会被去掉） |
| 客户端 ID | `Client-ID` | 最长 128 字符；**开启鉴权时必填**（缺失返回 400 `CLIENT_ID_MISSING`）；未开启鉴权且不传时服务端生成一次性随机 ID（每次连接都不同） |
| 客户端类型 | `Client-Type` | 默认 `APP`，最长 32 字符 |
| 随机数 | `Request-Nonce` | 开启鉴权时必填 |
| 时间戳 | `Timestamp` | 开启鉴权时必填，毫秒时间戳 |
| 签名 | `Reset-Sign` | 开启鉴权时必填 |

- 客户端 IP：默认只用 TCP 直连地址。只有 TCP 地址命中 `trusted-proxies` 时才读取转发头：`X-Forwarded-For` 从右往左跳过可信代理，取第一个不可信地址（全部可信时取最左侧）；没有可用的 XFF 时依次取 `X-Real-IP`、`Proxy-Client-IP`、`WL-Proxy-Client-IP`；非 IP 字面量的值被忽略。
- 会话标识：`userSessionId = SHA256(按长度前缀拼接 clientType、clientId、"u:"+userId 或 "anonymous")`（`AuthInterceptor.buildUserSessionId`），**与认证身份绑定**。只有同一用户（或同为匿名）使用相同 clientType + clientId 的新连接才会替换并关闭旧连接（并对旧会话回调 `clearUserSubscriptions`）；其他用户或匿名连接即使使用相同 Client-ID 也得到不同会话，无法顶替已登录会话。
- 登录：Token 存在时 `JwtManager.getObjectContent(token, LoginUser.class)` 校验，再用 `UserDataManager.getUserData` 取 userId / accountId。`must-login=true` 时必须 JWT 有效且取到 UserData，否则 401（`AUTH_TOKEN_MISSING` / `AUTH_TOKEN_INVALID` / `AUTH_USER_MISSING`）。
- 身份只在握手时确定；登录/登出后客户端必须断开重连（会得到新的 userSessionId）。

### 4.2 握手流程

1. Origin 校验 → 2. 路径校验（不匹配 404 `PATH_NOT_FOUND`）→ 3. 拦截器链 `beforeHandshake`（按 `getOrder()` 升序，默认拦截器为 -100）→ 4. 从 attributes 取 `userSessionId`（键 `AuthInterceptor.ATTR_USER_SESSION_ID`）→ 5. 创建握手器 → 6. `connectUser` → 7. 把 attributes 中的 `ATTR_WS_USER_DATA` 写入 `WsUserDataManager` → 8. 协议握手 → 9. 异步：向 `UserEventHandler` 派发 `connect` 事件（只要 `WsUserData` 存在，匿名连接也派发）并发送欢迎消息 → 10. `afterHandshake`（逆序，finally 中执行，失败时也会调用）。

- 握手失败返回 HTTP JSON：`{"success":false,"code":...,"message":...,"timestamp":毫秒}`，并带 `X-Error-Code` / `X-Error-Message` 头。错误码：`AUTH_TOKEN_MISSING` / `AUTH_TOKEN_INVALID` / `AUTH_USER_MISSING` / `TIMESTAMP_INVALID` / `SIGN_INVALID` / `NONCE_REUSED`（401），`ORIGIN_NOT_ALLOWED`（403），`PATH_NOT_FOUND`（404），`INVALID_REQUEST` / `CLIENT_ID_MISSING` / `INVALID_CLIENT_ID` / `INVALID_CLIENT_TYPE`（400），`MISSING_SESSION_ID` / `CONNECTION_FAILED` / `HANDSHAKE_ERROR` / `INTERCEPTOR_ERROR`（500）。
- 替换默认认证：实现 `AuthInterceptor`（`WebSocketInterceptor` 的标记子接口）并注册为 Bean，或配置 `default-auth-enabled: false` 后自行注册拦截器。替换者必须写入 `ATTR_USER_SESSION_ID`（建议用 `AuthInterceptor.buildUserSessionId` 生成，保证与身份绑定），并写入 `ATTR_WS_USER_DATA`（`WsUserData`），由框架在连接注册成功后写入 `WsUserDataManager`。只实现 `WebSocketInterceptor` 是追加而不是替换。
- `WsUserData` 只在整个拦截器链通过且 `connectUser` 成功后才写入，后续拦截器拒绝或握手失败不会残留或覆盖在线会话的身份数据。

### 4.3 消息与心跳

客户端上行文本帧按 `WsUserOptParam` 解析（`eventType`、`eventData`、`nonce`、`timestamp`、`sign`），在 `messageHandleExecutor` 中异步处理：

| eventType | 处理 |
|---|---|
| `pong` | 仅记录（任何文本帧/Ping/Pong 控制帧都会刷新活跃时间） |
| `online` | 返回 `{"success":true,"message":"当前会话处于在线状态！"}` |
| `connect` | 拒绝（仅服务端派发） |
| 其他（含缺失） | `enable-security=true` 时验签 → 用连接身份补齐 userSessionId/userId/accountId/clientId/clientType → `UserEventHandler.handleUserEvent` → 回 `ResponseMessage` |

- 未注册 `UserEventHandler` 时业务事件返回 `success=false`“用户事件处理器未配置”。
- 无法解析为 `WsUserOptParam` 的文本（非 JSON、JSON 数组、`null` 等）回复 `success=false`“消息格式错误：必须是符合协议的JSON对象”，连接保持；处理过程中的其他异常回复 `success=false`“消息处理失败”。
- 分片消息由 `WebSocketFrameAggregator` 聚合为完整文本帧再处理，聚合后超过 `max-frame-size` 时关闭连接；孤立的续帧被聚合器丢弃。
- 二进制帧：服务端发送关闭帧 `1003`（INVALID_MESSAGE_TYPE，reason `Binary frames are not supported`）并关闭连接。
- 服务端每 `heartbeat-interval-seconds` 发送应用层 JSON ping（`{"channel":"heartbeat","data":{"type":"ping","timestamp":...}}`，不是 WebSocket Ping 控制帧）；`session-timeout-seconds` 内无任何上行即关闭连接。
- 断开（关闭帧、超时、发送失败、异常）统一走 `disconnectUser(sessionId, channel)`：回调 `clearUserSubscriptions(WsUserData)`（回调异常会被记录，不影响后续清理）后清理 `WsUserData` 与 userId/accountId 索引；被新连接接管的旧 Channel 不会误清理新会话。

### 4.4 签名（enable-security=true）

```
原文 = "ClientType={clientType}&ClientId={clientId}&Nonce={nonce}&Timestamp={timestamp}&Param={param}"
sign = hex(HMAC-SHA256(原文, security-secret))   // 大小写不敏感，服务端用 MessageDigest.isEqual 常量时间比较
```
- `timestamp` 为毫秒时间戳的十进制字符串；`|服务器时间 - timestamp|` 超过 `security-timestamp-tolerance-seconds`（默认 300s）时拒绝（握手 401 `TIMESTAMP_INVALID`，消息回复“签名验证失败：时间戳缺失或已过期”）。客户端需与服务器时钟同步。
- 握手：`Timestamp` 放在请求头或同名查询参数；`param` 为空串；clientType 取实际值（默认 `APP`），clientId 取客户端传入的 `Client-ID`（开启鉴权时必填）。
- 业务消息：JSON 中携带 `"timestamp": 毫秒数字`；`param` = `eventData` 按**顶层** key 的 ASCII 升序（TreeMap）后用 fastjson2 序列化，空 eventData 为空串；clientType / clientId 取握手时绑定的值。嵌套对象和数字的序列化格式必须与前端 `JSON.stringify` 一致（推断，未运行验证）。
- 校验顺序：时间戳 → 签名 → nonce。nonce 必填，签名通过后才登记；TTL 至少为 2 × 时间戳偏差（默认 600s），时间戳有效期内同一 nonce 只能用一次，过了有效期的请求因时间戳过期被拒，不能重放。
- `pong` / `online` / `connect` 不验签。
- **密钥暴露风险**：浏览器端签名必须把 `security-secret` 下发到前端，任何人都能从页面中取出密钥，签名只能防止随意伪造和重放，不能视为身份认证；身份必须依赖 `Access-Token`。需要真正保护的场景应由服务端为每个用户/会话签发短期密钥，或只在可信客户端（App、服务端）开启。

```js
// 前端握手签名示例（Web Crypto）
const ts = Date.now().toString();
const nonce = crypto.randomUUID();
const raw = `ClientType=${clientType}&ClientId=${clientId}&Nonce=${nonce}&Timestamp=${ts}&Param=`;
const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
const sig = [...new Uint8Array(await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(raw)))]
    .map(b => b.toString(16).padStart(2, '0')).join('');
// 浏览器 WebSocket 不能自定义请求头，用查询参数传递
const qs = new URLSearchParams({ 'Client-ID': clientId, 'Client-Type': clientType,
    'Request-Nonce': nonce, 'Timestamp': ts, 'Reset-Sign': sig, 'Access-Token': token });
new WebSocket(`wss://host:8081/ws?${qs}`);
```

---

## 5. 服务端推送

```java
@Resource
private PushMessageServer pushMessageServer;   // 或 @Resource private IPushWsMsgApi pushWsMsgApi;

// 定点：userSessionId / userId / accountId 任填其一或多个，均支持逗号分隔
pushMessageServer.pushMessage(new PushWsMessageParam()
        .setUserId("10001,10002")
        .setChannel("order").setCategory("fill")
        .setData(Map.of("orderId", "12345", "status", "filled")));

// 订阅推送：业务按自己存储的订阅关系算出会话列表，再定点推送
pushMessageServer.pushMessage(new PushWsMessageParam()
        .setUserSessionId(String.join(",", subscriberSessionIds))
        .setChannel("quote").setCategory("BTCUSDT")
        .setData(Map.of("price", "50000.00")));

// 全员广播系统通知：channel=notification 且无任何用户标识，data 必须含 title、content
pushMessageServer.pushMessage(new PushWsMessageParam()
        .setChannel(ChannelTypeEnum.NOTIFICATION.getCode())
        .setData(Map.of("title", "系统维护", "content", "凌晨2点维护", "level", "important")));

// 也可直接使用发送器
webSocketMessageSender.broadcastToAll(pushMessage);
webSocketMessageSender.sendSystemNotification("标题", "内容", NotificationLevel.URGENT);
```

策略选择（按 order）：

| 策略 | order | 条件 | 行为 |
|---|---|---|---|
| `NotificationPushStrategy` | 0 | channel = `notification` 且三个用户标识都为空 | 校验 title / content，`level` 按 code 或枚举名解析（无法识别为 NORMAL），广播 `{channel:notification, category:level, data:{title,content,level,levelDescription}}` |
| `UserPushStrategy` | 2 | userSessionId / userId / accountId 任一非空 | 三个维度**分别推送**，同一会话被多个维度命中会收到多条 |
| 业务自定义 | 自定 | 自定 | 声明为 `MessagePushStrategy` Bean 即自动参与选择（按 order） |
| 其他组合 | — | 例如只有 channel / category | `PushMessageServer.pushMessage` 返回失败结果（`success=false`，msg 说明必须携带用户标识或使用 notification 广播），不再向调用方抛异常；直接调 `MessagePushStrategySelector.select` 仍抛 `BusinessException` |

- 推送格式：`PushMessage{channel, category, data, timestamp(Instant)}`；同步返回 `BRBuilder.successResult()`，只代表已入队，不代表送达。策略中的参数校验异常（如通知缺 title）同样转为失败结果。
- 定点发送：按 userSessionId 哈希选分片，`tryAccept` 超时（默认 50ms）丢弃；Channel 不可写（写缓冲水位 8KB/16KB）时丢弃；写失败会关闭并清理该连接。**不保证送达**；同一 Channel 的消息按入队顺序发送（`WsSendProcessor` 实现 `KeyOrderedProcessor`，以 Channel id 为保序键）。
- 丢弃计数：队列满丢弃、不可写丢弃、广播跳过不可写分别计数，`SessionSendDispatcher` 每 10 秒汇总一次；有丢弃时以 **WARN** 输出（天然限频），否则有活动时输出 INFO。可通过 `send-queue-buffer-size`、`send-queue-try-timeout-ms` 调整。
- 广播：遍历所有在线 Channel，跳过不活跃或不可写的连接，批量 write 后统一 flush，不经过 Disruptor。
- 跨服务推送：WebSocket 服务内可直接注入 `IPushWsMsgApi`（即 `PushMessageServer`）；其他服务调用需业务在 WebSocket 服务里暴露 Controller / RPC / MQ 消费者转调它。多实例部署时用 MQ 广播到每个 WS 节点，或维护 userId → 节点的路由表。

---

## 6. 业务扩展

```java
@Component
public class MyUserEventHandler implements UserEventHandler {

    @Override
    public BaseResult<?> handleUserEvent(WsUserOptParam param) {
        return switch (String.valueOf(param.getEventType())) {
            case "connect" -> { bindSession(param.getUserSessionId(), param.getUserId()); yield BRBuilder.successResult(); }
            case "subscribe" -> { subscribe(param.getUserSessionId(), param.getEventData()); yield BRBuilder.successResult(); }
            case "unsubscribe" -> { unsubscribe(param.getUserSessionId(), param.getEventData()); yield BRBuilder.successResult(); }
            default -> BRBuilder.failResult(null, "unsupported event");
        };
    }

    @Override
    public void clearUserSubscriptions(WsUserData userData) {   // 断开会话的完整身份
        removeBySessionId(userData.getUserSessionId());
    }
}
```
- `handleUserEvent` 在消息处理线程池中执行（核心线程 ≥32，队列满时 CallerRunsPolicy 回到 Netty I/O 线程），必须线程安全，避免长时间阻塞。
- `connect` 事件的返回值被忽略。
- 返回 `BaseResult` 时：`success` 透传；失败时 `message` 取 `msg`；`data` 非空时透传。
- 查询身份：`WsUserDataManager.getWsUserData(sessionId)`、`getSessionIdsByUserId(userId)`、`getSessionIdsByAccountId(accountId)`、`getWsUserDataByUserId(userId)`（静态方法，容量各 10 万）。`WsUserDataManager` 是**进程内静态缓存，不是 Bean，不能替换**；分布式场景需要业务自建 userId → 节点的路由，`ISocketManager` 也只能管理本机 Channel。
- 在线判断：`ISocketManager.isOnline(sessionId)` / `getUserSession(sessionId)`。

---

## 7. 生成代码时的规则

### Do
- 业务模块依赖 `websocket-api` 中的参数类；只有 WebSocket 接入服务依赖 `websocket-server`。
- 推送一律带用户标识（userSessionId / userId / accountId），只有全员系统通知才用 `channel=notification` 且不带标识。
- 订阅关系保存在业务侧，并以 `userSessionId` 为键；`clearUserSubscriptions(WsUserData)` 时按 `userData.getUserSessionId()` 清理。
- 客户端始终传稳定唯一的 `Client-ID`（每个设备/标签页一个）；开启鉴权时必须传。
- 需要登录连接时确保存在 `UserDataManager`（`easyfk.config.login.cache-type: redis`）。
- 开启 `enable-security` 时修改 `security-secret`，客户端每次使用新的 nonce 和当前毫秒时间戳，并保持时钟同步。
- 生产环境配置具体的 `allowed-origins`；经 Nginx/SLB 接入时把代理地址配置到 `trusted-proxies` 并透传 `X-Forwarded-For` / `X-Real-IP`。
- 替换默认认证时实现 `AuthInterceptor`，用 `AuthInterceptor.buildUserSessionId` 生成会话标识，并写入 `ATTR_WS_USER_DATA`。
- 按需调整 `performance`（分片数、等待策略），关注 10 秒统计中的丢弃 WARN，并为 Netty 端口单独做负载均衡与健康检查。

### Don't
- 不要使用旧手册的 `com.mcst.easyfk.ws.*` 包名、`EventHandler` 接口或 `easyfk.config.ws.*` 配置；不要期望 `IPushWsMsgApi` 能被其他服务直接远程注入（需业务暴露）。
- 不要把 userId 填进 `userSessionId`，也不要在前端自行计算 userSessionId。
- 不要只填 channel / category 去“按订阅推送”，组件没有这种策略，会返回失败结果。
- 不要依赖推送的送达；关键业务消息需要业务层确认或补偿。
- 不要在没有配置 `trusted-proxies` 的情况下依赖转发头里的客户端 IP。
- 不要以为实现 `WebSocketInterceptor` 就能替换默认认证（需实现 `AuthInterceptor` 或关闭 `default-auth-enabled`）。
- 不要把 `security-secret` 当成身份凭证；浏览器端持有的密钥视同公开。
- 不要发送二进制帧（会被 1003 关闭）。

---

## 8. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | 框架开发手册 §3.12.2 | 配置前缀 `easyfk.config.ws`，含 `sub-save-type`、`enable-sock-js`、`max-subscriptions-per-user`、`message-buffer-size`、`performance.batch-threshold/core-pool-size...` | 前缀为 `easyfk.config.websocket`，这些配置项全部不存在；实际配置见第 3 节 |
| 2 | 框架开发手册 §3.12.1 / §3.12.3 | 内置订阅机制（频道 + 产品）；实现 `com.mcst.easyfk.ws.server.handler.EventHandler`，`clearUserSubscriptions(userSessionId)`，返回 `BaseResult.success()` | 组件不存订阅；接口为 `com.mcst.easyfk.websocket.handler.UserEventHandler`，回调为 `clearUserSubscriptions(WsUserData)`（见 #19）；`BaseResult.success()` 不存在，应使用 `BRBuilder.successResult()` |
| 3 | 框架开发手册 §3.12.3、§4.5 | 注入 `IPushWsMsgApi`（包 `com.mcst.easyfk.ws.api`），`setUserSessionId(userId.toString())` 推送给用户；只设 channel + category 推送给订阅者 | 包名是 `com.mcst.easyfk.websocket.api`，且框架内无实现类，注入会失败；按用户推送应使用 `setUserId`；只有 channel + category 时没有匹配策略，抛 `BusinessException` **已修复**：`PushMessageServer` 实现 `IPushWsMsgApi` 可直接注入；仅 channel/category 时返回带明确说明的失败结果；按用户推送用 `setUserId` |
| 4 | 开发文档 §5.4、特点文档 | `IPushWsMsgApi` 可用于跨服务推送 | 只有接口定义，`PushMessageServer` 未实现它，需要业务自行实现并暴露 **已修复**：`PushMessageServer implements IPushWsMsgApi`，本服务内可注入；跨服务仍需业务通过 HTTP/RPC/MQ 暴露 |
| 5 | 开发文档 §3.5、特点文档 §2.2 / 场景表 | Disruptor 分片“同一用户消息进入同一分片，保证顺序”“保证可靠有序” | 同一会话确实进入同一分片，但每分片默认 2 个消费线程且 `WsSendProcessor` 未实现 `KeyOrderedProcessor`（按 sequence 分片），同一会话消息可能乱序；队列满（50ms）或 Channel 不可写时直接丢弃 **已修复**：`WsSendProcessor` 实现 `KeyOrderedProcessor`（按 Channel id 保序）；丢弃仍会发生，但分类计数并每 10 秒以 WARN 汇总输出 |
| 6 | 开发文档 §6 | 所有 Bean 均 `@ConditionalOnMissingBean`，可自定义同类型 Bean 覆盖 | 默认拦截器条件是 `@ConditionalOnMissingBean(DefaultAuthInterceptor.class)`，自定义 `WebSocketInterceptor` 只会追加；自定义 `MessagePushStrategy` 不会被 Selector 收集 **已修复**：Selector 注入全部 `MessagePushStrategy`；默认拦截器条件改为 `@ConditionalOnMissingBean(AuthInterceptor.class)` + `default-auth-enabled`，实现 `AuthInterceptor` 即可替换默认认证 |
| 7 | 开发文档 §4.1、前端文档 §1.1 | `path` 为 WebSocket 访问路径 | 握手不校验请求 URI，任意路径都能升级；`path` 只用于日志和心跳消息中的 `data.path`（路径段数 >2 时） **已修复**：握手校验请求路径（忽略查询参数与末尾斜杠），不匹配返回 404 `PATH_NOT_FOUND` |
| 8 | 开发文档 §4.3 | `sslEnabled=true` 但证书缺失时服务启动失败 | 只有 Netty 服务启动失败（守护线程中捕获并记录日志），Spring 应用正常启动，端口不监听 **已修复**：`WebSocketServer` 实现 `SmartLifecycle` 同步 bind，任何启动失败抛 `IllegalStateException` 使 Spring 应用启动失败 |
| 9 | 开发文档 §3.3 / 前端文档 §1.2 | `mustLogin=true` 时必须登录 | 只校验 JWT 有效；`UserDataManager` 取不到用户数据时仍以 userId 为空的身份连接成功 **已修复**：`must-login=true` 时取不到 UserData 返回 401 `AUTH_USER_MISSING` |
| 10 | 开发文档 §1.2 / §3.3 | 未说明 `UserDataManager` 依赖 | `@Resource @Lazy UserDataManager`；authority 默认不注册该 Bean，携带 Token 的握手会在调用时失败并返回 500（推断，未运行验证） **已修复**：改为 `ObjectProvider<UserDataManager>`，缺失时按匿名处理（`must-login=true` 时 401） |
| 11 | 前端文档 §1.3 / §5 | 开启鉴权时连接签名使用客户端的 clientId | 未传 `Client-ID` 时服务端用 UA + IP 生成 clientId 参与验签，客户端无法计算，开启鉴权时 `Client-ID` 实际上是必填 **已修复**：开启鉴权时缺少 `Client-ID` 返回 400 `CLIENT_ID_MISSING`；未开启鉴权时生成一次性随机 ID（不再用 UA+IP） |
| 12 | 开发文档 §3.3、前端文档 §1.2 | Token 通过 `Access-Token` 传递 | 代码定义了 `BEARER_PREFIX` 但未使用，带 `Bearer ` 前缀的 Token 会校验失败 **已修复**：`Bearer ` 前缀（不区分大小写）会被去掉后再校验 |
| 13 | 前端文档 Q7 | 每个客户端（clientType + clientId）拥有独立会话，多端互不影响 | 会话 ID 只由 clientType + clientId 决定，与用户无关；任何人使用相同的 Client-ID 连接都会顶掉原连接并接管发往该会话的推送 **已修复**：会话 ID 改为 SHA256(clientType, clientId, userId/anonymous)，只有同一用户（或同为匿名）的同 Client-ID 连接才会替换旧连接，其他人无法顶替已登录会话 |
| 14 | 开发文档 §9.2 | 按 `X-Forwarded-For` > `X-Real-IP` > TCP 地址解析 IP | 还会读取 `Proxy-Client-IP`、`WL-Proxy-Client-IP`；所有 IP 头均无可信代理校验，客户端可伪造 **已修复**：新增 `trusted-proxies`（IP/CIDR，默认空），只有 TCP 对端是可信代理时才解析转发头（XFF 从右向左跳过可信代理），否则使用 TCP 地址 |
| 15 | 开发文档 §9.3、前端文档 §5 | nonce 防重放 | 与文档一致：nonce 必填且窗口内唯一，但协议无时间戳，窗口外可重放；签名比较不是常量时间；浏览器端需持有密钥 **已修复**：签名原文加入 `Timestamp` 并校验时效（默认 ±300s，nonce TTL ≥ 2 倍偏差），签名先于 nonce 校验，使用 `MessageDigest.isEqual` 常量时间比较；浏览器持有密钥的风险已在 §4.4 说明（无法靠代码消除） |
| 16 | 特点文档 对比表 | 订阅管理“内置频道+类别体系” | 与同文档“组件零订阅状态”矛盾，源码中没有任何订阅存储 |
| 17 | 特点文档 扩展点表 | 替换 `ISocketManager` 可用于分布式场景 | `WsUserDataManager`（身份索引）是静态本地缓存，不能通过 Bean 替换；替换 `ISocketManager` 也无法跨节点持有 Netty Channel **已说明**：未改代码，限制已写入 §6；分布式需业务自建路由 |
| 18 | 源码 | — | 默认拦截器在链中途写入 `WsUserData`，后续拦截器拒绝或握手失败时不回滚；若已有同 sessionId 的在线连接，其身份数据会被覆盖 **已修复**：`WsUserData` 放入握手属性 `ATTR_WS_USER_DATA`，在 `connectUser` 成功后才写入 `WsUserDataManager` |
| 19 | 源码 | — | `clearUserSubscriptions` 按 clientId 回调，同一 clientId 的不同 clientType（如 APP 与 PC）断开任一端时，业务若按 clientId 清理会误清另一端 **已修复**：接口改为 `clearUserSubscriptions(WsUserData)`，传入断开会话的完整身份，业务按 userSessionId 清理（API 不兼容变更） |
| 20 | 源码 | — | 非 JSON 文本消息回复 `success=true`“消息已收到”；二进制帧与分片续帧被静默忽略 **已修复**：无法解析的文本回复 `success=false`“消息格式错误”；分片消息经 `WebSocketFrameAggregator` 聚合后正常处理；二进制帧以关闭码 1003 关闭连接 |
| 21 | 开发文档 §4.4 | `sendQueueWorkersPerShard` 默认 2、等待策略 `YIELDING` | 与源码一致，但默认 64 个发送线程在 YIELDING 下空闲也会占用 CPU（推断，未运行验证） **已修复**：默认改为 8 分片 × 1 线程、RingBuffer 16384、等待策略 `BLOCKING` |
| 22 | websocket-api `build.gradle` | — | 子模块自带 `group/version/repositories/junit` 配置，与其他模块统一由根工程管理的方式不一致（不影响使用） **已修复**：`build.gradle` 清空，与 `autoId-api` 一致，全部由根工程与父工程管理 |
