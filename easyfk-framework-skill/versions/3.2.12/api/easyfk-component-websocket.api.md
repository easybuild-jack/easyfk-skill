# easyfk-component-websocket API 签名速查（easyfk 3.2.12）

> 坐标：`com.mcst:websocket-server、websocket-api`　源码：`easyfk-component/component-websocket/websocket-server`、`easyfk-component/component-websocket/websocket-api`
> 由 `scripts/gen-api.py` 从 34 个源文件自动提取，共 34 个类型、105 个方法/构造器、86 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-component-websocket-skill.md](../modules/easyfk-component-websocket-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 配置项（@ConfigurationProperties）

### `easyfk.config.websocket` ← WebSocketProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `path` | `String` | `"/ws"` | WebSocket访问路径 默认为 /ws |
| `port` | `int` | `8081` | WebSocket服务器端口（Netty独立端口） 默认8081 |
| `must-login` | `Boolean` | `Boolean.FALSE` | 是否必须登录才能订阅 默认不要求登录 |
| `security-secret` | `String` | `DEFAULT_SECURITY_SECRET` | 接口鉴权加盐 用于签名验证等安全场景，建议生产环境修改此默认值 |
| `enable-security` | `boolean` | `Boolean.FALSE` | 是否开启接口鉴权，默认不开启 |
| `security-nonce-ttl-seconds` | `long` | `600` | nonce防重放窗口时长（秒） 开启接口鉴权后，同一nonce在窗口内重复使用将被拒绝； 实际生效值不小于 2 × securityTimestampToleranceSeconds… |
| `security-timestamp-tolerance-seconds` | `long` | `300` | 签名时间戳允许的偏差（秒） 开启接口鉴权后，\|服务器时间 - Timestamp\| 超过该值的握手与业务消息将被拒绝 默认300秒 |
| `default-auth-enabled` | `boolean` | `true` | 是否注册默认认证拦截器 DefaultAuthInterceptor 设为false或自行声明 AuthInterceptor 类型的Bean时不注册，此时由自定义认证拦截器负责写入会话属性 默认true |
| `trusted-proxies` | `List<String>` | `new ArrayList<>()` | 可信反向代理地址（IP或CIDR，如 10.0.0.0/8、192.168.1.10、::1） 仅当TCP直连地址命中该列表时才解析 X-Forwarded-For / X-Real-IP 等转发头… |
| `allow-cross-origin` | `boolean` | `true` | 是否支持跨域 true时按allowedOrigins白名单校验请求的Origin头； false时仅允许与Host同源的请求（无Origin头的请求始终放行） |
| `allowed-origins` | `String[]` | `{"*"}` | 允许的跨域来源 默认允许所有来源，生产环境建议配置具体域名 |
| `session-timeout-seconds` | `long` | `1800` | 用户会话超时时间（秒） 默认30分钟 |
| `heartbeat-interval-seconds` | `long` | `30` | 心跳检测间隔（秒） 默认30秒 |
| `max-frame-size` | `int` | `65536` | 消息缓冲区大小（字节） 默认64KB |
| `max-content-length` | `int` | `65536` | 最大内容长度（字节） 默认64KB |
| `boss-threads` | `int` | `1` | Boss线程组线程数 默认1 |
| `worker-threads` | `int` | `0` | Worker线程组线程数 默认0表示使用默认值（CPU核心数*2） |
| `ssl-enabled` | `boolean` | `false` | 是否启用SSL（wss） 启用时必须同时配置sslCertPath和sslKeyPath，否则服务启动失败 默认false |
| `ssl-cert-path` | `String` | `—` | SSL证书路径（X.509 PEM格式证书链文件） |
| `ssl-key-path` | `String` | `—` | SSL私钥路径（PKCS#8 PEM格式私钥文件） |
| `performance` | `Performance` | `new Performance()` | 性能相关配置 |


## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `websocket-server` | `com.mcst.easyfk.websocket.config.ServerConfig` |

## 类型索引

- `com.mcst.easyfk.websocket.api`：[IPushWsMsgApi](#ipushwsmsgapi)
- `com.mcst.easyfk.websocket.config`：[ServerConfig](#serverconfig)
- `com.mcst.easyfk.websocket.enums`：[ChannelTypeEnum](#channeltypeenum)、[EventType](#eventtype)、[NotificationLevel](#notificationlevel)
- `com.mcst.easyfk.websocket.handler`：[UserEventHandler](#usereventhandler)、[WebSocketHandler](#websockethandler)
- `com.mcst.easyfk.websocket.interceptor`：[AuthInterceptor](#authinterceptor)、[DefaultAuthInterceptor](#defaultauthinterceptor)、[HandshakeResult](#handshakeresult)、[WebSocketInterceptor](#websocketinterceptor)
- `com.mcst.easyfk.websocket.manager`：[ISocketManager](#isocketmanager)、[WsUserDataManager](#wsuserdatamanager)
- `com.mcst.easyfk.websocket.manager.impl`：[SocketManagerImpl](#socketmanagerimpl)
- `com.mcst.easyfk.websocket.param`：[PushWsMessageParam](#pushwsmessageparam)、[WsUserOptParam](#wsuseroptparam)
- `com.mcst.easyfk.websocket.properties`：[WebSocketProperties](#websocketproperties)
- `com.mcst.easyfk.websocket.security`：[NonceValidator](#noncevalidator)、[TrustedProxyMatcher](#trustedproxymatcher)
- `com.mcst.easyfk.websocket.sender`：[SessionSendDispatcher](#sessionsenddispatcher)、[SessionSendEvent](#sessionsendevent)、[SessionSendWorker](#sessionsendworker)、[WebSocketMessageSender](#websocketmessagesender)、[WsSendProcessor](#wssendprocessor)
- `com.mcst.easyfk.websocket.server`：[PushMessageServer](#pushmessageserver)、[WebSocketServer](#websocketserver)
- `com.mcst.easyfk.websocket.strategy`：[MessagePushStrategy](#messagepushstrategy)、[MessagePushStrategySelector](#messagepushstrategyselector)
- `com.mcst.easyfk.websocket.strategy.impl`：[NotificationPushStrategy](#notificationpushstrategy)、[UserPushStrategy](#userpushstrategy)
- `com.mcst.easyfk.websocket.util`：[SecuritySignUtil](#securitysignutil)
- `com.mcst.easyfk.websocket.vo`：[PushMessage](#pushmessage)、[ResponseMessage](#responsemessage)、[WsUserData](#wsuserdata)

## 包 `com.mcst.easyfk.websocket.api`

### IPushWsMsgApi

`public interface IPushWsMsgApi`　WebSocket消息推送接口 websocket-server 中由 PushMessageServer 实现；跨服务调用时由业务在 WebSocket 服务中自行暴露（HTTP/RPC/MQ）

**方法**

```java
BaseResult<?> pushMessage(PushWsMessageParam param)  // 推送消息 必须携带 userSessionId/userId/accountId 之一，或 channel=notification 且不带用户标识（全员系统通知）…
```

## 包 `com.mcst.easyfk.websocket.config`

### ServerConfig

`public class ServerConfig`　注解：`@Slf4j` `@AutoConfiguration` `@EnableConfigurationProperties({WebSocketProperties.class})`　推送消息配置类

**方法**

```java
@Bean @ConditionalOnMissingBean PushMessageServer pushMessageServer()  // 推送入口，同时作为 IPushWsMsgApi 的本地实现
@Bean @ConditionalOnMissingBean WebSocketServer webSocketServer()
@Bean @ConditionalOnMissingBean WebSocketHandler webSocketHandler()
@Bean @ConditionalOnMissingBean(AuthInterceptor.class) @ConditionalOnProperty(prefix = "easyfk.config.websocket", name = "default-auth-enabled", havingValue = "true", matchIfMissing = true) DefaultAuthInterceptor defaultAuthInterceptor()  // 默认的WebSocket认证拦截器 用于Token验证、用户信息提取等； 声明任意 AuthInterceptor Bean 或配置 default-auth-enabled=false 即可替换…
@Bean @ConditionalOnMissingBean ISocketManager socketManager()
@Bean @ConditionalOnMissingBean NonceValidator nonceValidator(WebSocketProperties webSocketProperties)  // Nonce防重放校验器 开启接口鉴权且仍在使用默认密钥时输出告警
@Bean @ConditionalOnMissingBean SessionSendWorker sessionSendWorker(ISocketManager socketManager)
@Bean @ConditionalOnMissingBean SessionSendDispatcher sessionSendDispatcher(WebSocketProperties webSocketProperties, SessionSendWorker sessionSendWorker, ISocketManager socketManager)
@Bean @ConditionalOnMissingBean WebSocketMessageSender webSocketMessageSender()  // WebSocket消息发送器
@Bean @ConditionalOnMissingBean NotificationPushStrategy notificationPushStrategy(WebSocketMessageSender messageSender)  // 系统通知推送策略
@Bean @ConditionalOnMissingBean UserPushStrategy userPushStrategy(WebSocketMessageSender messageSender)  // 用户推送策略
@Bean @ConditionalOnMissingBean MessagePushStrategySelector messagePushStrategySelector(List<MessagePushStrategy> strategies)  // 消息推送策略选择器 订阅关系由业务方自持，组件内置定点推送与全员广播两类策略； 容器中所有 MessagePushStrategy Bean（含业务自定义）都会参与选择，按 getOrder 排序
```

## 包 `com.mcst.easyfk.websocket.enums`

### ChannelTypeEnum

`public enum ChannelTypeEnum`　Lombok：`@Getter`

**枚举常量**

```java
NOTIFICATION("notification", "通知")  // 通知频道
CHAT("chat", "聊天")  // 聊天频道
HEARTBEAT("heartbeat", "心跳")  // 心跳频道
BIZ("biz", "具体业务")  // 具体业务频道
```

**字段 / 常量**

```java
final String code
final String description
```

**构造器**

```java
ChannelTypeEnum(String code, String description)
```

### EventType

`public enum EventType`　Lombok：`@Getter`　WebSocket消息类型枚举 定义客户端和服务器之间通信的消息类型

**枚举常量**

```java
CONNECT("connect", "连接建立")  // 连接建立 由服务端在握手成功后向下游派发（所有连接都会派发，不区分是否登录）， 事件参数携带 userSessionId/clientId/clientType，已登录连接还携带 userId/accountId…
SUBSCRIBE("subscribe", "订阅")  // 订阅消息
UNSUBSCRIBE("unsubscribe", "取消订阅")  // 取消订阅消息
PING("ping", "心跳检测")  // 心跳检测消息（服务器发送）
PONG("pong", "心跳响应")  // 心跳响应消息（客户端响应）
ONLINE("online", "检查是否在线")  // 检查是否在线(前端检查当前会话是否有效)
```

**字段 / 常量**

```java
final String code
final String description
```

**构造器**

```java
EventType(String code, String description)
```

**方法**

```java
static EventType fromCode(String code)  // 根据code获取枚举
```

### NotificationLevel

`public enum NotificationLevel`　Lombok：`@Getter`

**枚举常量**

```java
NORMAL("normal", "普通")  // 普通通知
IMPORTANT("important", "重要")  // 重要通知
URGENT("urgent", "紧急")  // 紧急通知
```

**字段 / 常量**

```java
final String code
final String description
```

**构造器**

```java
NotificationLevel(String code, String description)
```

**方法**

```java
static NotificationLevel fromCode(String code)  // 按code或枚举名解析通知级别（忽略大小写） 无法识别时返回NORMAL，避免调用方传值不规范导致推送失败
```

## 包 `com.mcst.easyfk.websocket.handler`

### UserEventHandler

`public interface UserEventHandler`　用户事件处理器函数式接口 用于处理客户端提交的业务事件，具体业务逻辑由下游实现

**方法**

```java
BaseResult<?> handleUserEvent(WsUserOptParam wsUserOptParam)  // 处理用户提交的事件
default void clearUserSubscriptions(WsUserData userData)  // 清除用户订阅 在会话断开（含被同会话新连接替换）时由组件回调，下游据此清理与该会话相关的业务订阅数据； 应以 getUserSessionId() 为键清理…
```

### WebSocketHandler

`public class WebSocketHandler extends SimpleChannelInboundHandler<Object>`　注解：`@Slf4j` `@ChannelHandler.Sharable`　WebSocket处理器 处理WebSocket连接的生命周期事件

**方法**

```java
@PostConstruct void init()
void channelRead0(ChannelHandlerContext ctx, Object msg) throws Exception
void channelInactive(ChannelHandlerContext ctx) throws Exception
void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) throws Exception
void userEventTriggered(ChannelHandlerContext ctx, Object evt) throws Exception
@PreDestroy void shutdown()
```

## 包 `com.mcst.easyfk.websocket.interceptor`

### AuthInterceptor

`public interface AuthInterceptor extends WebSocketInterceptor`　WebSocket认证拦截器标记接口 容器中存在该类型的Bean时不再注册默认的 DefaultAuthInterceptor，从而替换默认认证…

**字段 / 常量**

```java
String ATTR_USER_SESSION_ID = "userSessionId"
String ATTR_USER_ID = "userId"
String ATTR_ACCOUNT_ID = "accountId"
String ATTR_CLIENT_ID = "clientId"
String ATTR_CLIENT_TYPE = "clientType"
String ATTR_WS_USER_DATA = "wsUserData"  // 握手属性：待注册的 WsUserData，由 WebSocketHandler 在连接注册成功后写入 WsUserDataManager
String ANONYMOUS_USER = "anonymous"  // 匿名连接在会话标识中使用的用户占位
```

**方法**

```java
static String buildUserSessionId(String clientType, String clientId, String userId)  // 生成会话标识：SHA256(clientType、clientId、userId（匿名为 anonymous）按长度前缀拼接) 会话与认证身份绑定，不同用户（含匿名）使用相同 Client-ID 时得到不同会话…
static String lengthPrefixed(String value)
```

### DefaultAuthInterceptor

`public class DefaultAuthInterceptor implements AuthInterceptor`　注解：`@Slf4j`　默认的WebSocket认证拦截器 用于在WebSocket连接建立前从请求头或查询参数中获取和验证Token 会话标识由 clientType + clientId + 登录用户共同决定…

**方法**

```java
@PostConstruct void init()
HandshakeResult beforeHandshake(ChannelHandlerContext ctx, FullHttpRequest request, Map<String, Object> attributes)
void afterHandshake(ChannelHandlerContext ctx, FullHttpRequest request, Map<String, Object> attributes, Exception exception)
int getOrder()
```

### HandshakeResult

`public class HandshakeResult`　Lombok：`@Getter` `@Setter`　WebSocket握手结果 用于拦截器返回握手验证的结果

**字段 / 常量**

```java
boolean success  // 是否允许继续握手
HttpResponseStatus httpStatus  // HTTP状态码
String errorCode  // 业务错误码
String errorMessage  // 错误描述信息
long timestamp  // 错误发生时间戳
```

**方法**

```java
static HandshakeResult success()  // 创建成功结果
static HandshakeResult fail(HttpResponseStatus httpStatus, String errorCode, String errorMessage)  // 创建失败结果
static HandshakeResult unauthorized(String errorCode, String errorMessage)  // 创建未授权错误结果
static HandshakeResult forbidden(String errorCode, String errorMessage)  // 创建禁止访问错误结果
static HandshakeResult serverError(String errorCode, String errorMessage)  // 创建服务器内部错误结果
static HandshakeResult badRequest(String errorCode, String errorMessage)  // 创建请求错误结果
```

### WebSocketInterceptor

`public interface WebSocketInterceptor`　WebSocket握手拦截器接口 用于在WebSocket连接建立前后执行自定义逻辑 实现此接口可以进行Token验证、IP白名单、限流等业务处理

**方法**

```java
HandshakeResult beforeHandshake(ChannelHandlerContext ctx, FullHttpRequest request, Map<String, Object> attributes)  // WebSocket握手前的处理 在WebSocket连接建立之前被调用，可以用于验证Token、检查IP等
default void afterHandshake(ChannelHandlerContext ctx, FullHttpRequest request, Map<String, Object> attributes, Exception exception)  // WebSocket握手完成后的处理 在WebSocket连接成功建立后被调用，可以用于记录日志、触发事件等
default int getOrder()  // 获取拦截器的执行顺序 数值越小优先级越高，越先执行
```

## 包 `com.mcst.easyfk.websocket.manager`

### ISocketManager

`public interface ISocketManager`　在线用户管理接口 提供会话与Channel的连接管理能力（订阅关系由业务方自持，本组件不管理订阅） 支持同一用户在不同客户端登录的会话管理

**方法**

```java
boolean connectUser(Channel channel, String userSessionId)  // 用户连接时调用
boolean disconnectUser(String userSessionId)  // 用户断开连接时调用
boolean disconnectUser(String userSessionId, Channel channel)  // 用户断开连接时调用（带Channel一致性校验） 仅当当前注册的Channel与传入Channel是同一实例时才执行清理， 防止同会话重连场景下旧连接的关闭回调误清理新连接
boolean isOnline(String userSessionId)  // 判断用户是否在线
Channel getUserSession(String userSessionId)  // 获取用户的Channel
Collection<Channel> getAllUserSessions()  // 获取所有用户的所有Channel
String getUserSessionId(Channel channel)  // 根据Channel获取用户会话ID
```

### WsUserDataManager

`public class WsUserDataManager`　注解：`@Slf4j`　WebSocket用户数据管理器 管理用户的会话数据，使用高性能本地缓存

**方法**

```java
static WsUserData getWsUserData(String userSessionId)
static Set<String> getSessionIdsByUserId(String userId)  // 根据用户ID获取所有关联的会话ID
static Set<String> getSessionIdsByAccountId(String accountId)  // 根据账户ID获取所有关联的会话ID
static List<WsUserData> getWsUserDataByUserId(String userId)  // 根据用户ID获取所有会话的用户数据
static void addOrUpdateWsUserData(WsUserData wsUserData)
static void removeWsUserData(String userSessionId)
```

## 包 `com.mcst.easyfk.websocket.manager.impl`

### SocketManagerImpl

`public class SocketManagerImpl implements ISocketManager`　注解：`@Slf4j`　本地在线用户管理实现 使用Map在内存中存储会话与Channel的映射关系 订阅关系完全由业务方自持，本组件仅在连接断开时回调下游清理…

**字段 / 常量**

```java
static final AttributeKey<String> USER_SESSION_ID = AttributeKey.valueOf("userSessionId")  // 用户会话ID属性键
```

**方法**

```java
boolean connectUser(Channel channel, String userSessionId)
boolean disconnectUser(String userSessionId)
boolean disconnectUser(String userSessionId, Channel channel)
boolean isOnline(String userSessionId)
Channel getUserSession(String userSessionId)
Collection<Channel> getAllUserSessions()
String getUserSessionId(Channel channel)
```

## 包 `com.mcst.easyfk.websocket.param`

### PushWsMessageParam

`public class PushWsMessageParam implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)`　注解：`@Schema(description = "推送Websocket消息请求参数对象")`

**字段 / 常量**

```java
@Schema(description = "频道，例如：kline,quote,order,notification等", name = "channel") String channel  // 频道，例如：kline,quote,order,notification,chat等
@Schema(description = "类型 具体产品类型，例如：通知，公告，系统消息，或者具体某个产品", name = "category") String category  // 类型 具体产品类型，例如：通知，公告，系统消息，或者具体某个产品
@Schema(description = "用户SessionID，多个用逗号隔开", name = "userSessionId") String userSessionId  // 用户SessionID，多个用逗号隔开
@Schema(description = "用户ID，多个用逗号隔开", name = "userId") String userId  // 用户ID，多个用逗号隔开
@Schema(description = "账户ID，多个用逗号隔开", name = "accountId") String accountId  // 账户ID，多个用逗号隔开
@Schema(description = "数据信息", name = "data") Map<String, Object> data  // 数据信息
```

### WsUserOptParam

`public class WsUserOptParam`　Lombok：`@Data` `@Accessors(chain = true)` `@Builder` `@NoArgsConstructor` `@AllArgsConstructor`　注解：`@Schema(description = "用户操作参数对象")`

**字段 / 常量**

```java
@Schema(description = "用户SessionID", name = "userSessionId", hidden = true) String userSessionId  // 用户websocketSessionId，由 clientType、clientId 与登录用户（匿名为 anonymous）共同计算的 SHA256 不是用户ID，而是用户在WebSocket连接时分配的唯一会话ID
@Schema(description = "事件类型", name = "eventType") String eventType
@Schema(description = "账户ID", name = "accountId", hidden = true) String accountId  // 账户ID
@Schema(description = "用户ID", name = "userId", hidden = true) String userId  // 用户ID
@Schema(description = "客户端ID", name = "clientId", hidden = true) String clientId
@Schema(description = "事件数据", name = "eventData") Map<String, Object> eventData
@Schema(description = "客户端类型，APP/PC/BMS", name = "clientType") String clientType  // 客户端类型，APP/PC/BMS
@Schema(description = "请求随机数", name = "nonce") String nonce  // 请求随机数，用于签名验证
@Schema(description = "请求时间戳（毫秒）", name = "timestamp") Long timestamp  // 请求时间戳（毫秒），开启鉴权时参与签名并校验时效
@Schema(description = "请求签名", name = "sign") String sign  // 请求签名，用于接口鉴权
```

## 包 `com.mcst.easyfk.websocket.properties`

### WebSocketProperties

`public class WebSocketProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.websocket")`　WebSocket配置属性类 用于管理WebSocket相关的配置参数

**字段 / 常量**

```java
String path = "/ws"  // WebSocket访问路径 默认为 /ws
int port = 8081  // WebSocket服务器端口（Netty独立端口） 默认8081
static final String DEFAULT_SECURITY_SECRET = "easyfk@ws#2026!"  // 默认接口鉴权密钥 生产环境开启鉴权时必须修改，否则签名形同虚设
Boolean mustLogin = Boolean.FALSE  // 是否必须登录才能订阅 默认不要求登录
String securitySecret = DEFAULT_SECURITY_SECRET  // 接口鉴权加盐 用于签名验证等安全场景，建议生产环境修改此默认值
boolean enableSecurity = Boolean.FALSE  // 是否开启接口鉴权，默认不开启
long securityNonceTtlSeconds = 600  // nonce防重放窗口时长（秒） 开启接口鉴权后，同一nonce在窗口内重复使用将被拒绝； 实际生效值不小于 2 × securityTimestampToleranceSeconds…
long securityTimestampToleranceSeconds = 300  // 签名时间戳允许的偏差（秒） 开启接口鉴权后，|服务器时间 - Timestamp| 超过该值的握手与业务消息将被拒绝 默认300秒
boolean defaultAuthEnabled = true  // 是否注册默认认证拦截器 DefaultAuthInterceptor 设为false或自行声明 AuthInterceptor 类型的Bean时不注册，此时由自定义认证拦截器负责写入会话属性 默认true
List<String> trustedProxies = new ArrayList<>()  // 可信反向代理地址（IP或CIDR，如 10.0.0.0/8、192.168.1.10、::1） 仅当TCP直连地址命中该列表时才解析 X-Forwarded-For / X-Real-IP 等转发头…
boolean allowCrossOrigin = true  // 是否支持跨域 true时按allowedOrigins白名单校验请求的Origin头； false时仅允许与Host同源的请求（无Origin头的请求始终放行）
String[] allowedOrigins = {"*"}  // 允许的跨域来源 默认允许所有来源，生产环境建议配置具体域名
long sessionTimeoutSeconds = 1800  // 用户会话超时时间（秒） 默认30分钟
long heartbeatIntervalSeconds = 30  // 心跳检测间隔（秒） 默认30秒
int maxFrameSize = 65536  // 消息缓冲区大小（字节） 默认64KB
int maxContentLength = 65536  // 最大内容长度（字节） 默认64KB
int bossThreads = 1  // Boss线程组线程数 默认1
int workerThreads = 0  // Worker线程组线程数 默认0表示使用默认值（CPU核心数*2）
boolean sslEnabled = false  // 是否启用SSL（wss） 启用时必须同时配置sslCertPath和sslKeyPath，否则服务启动失败 默认false
String sslCertPath  // SSL证书路径（X.509 PEM格式证书链文件）
String sslKeyPath  // SSL私钥路径（PKCS#8 PEM格式私钥文件）
Performance performance = new Performance()  // 性能相关配置
```

#### WebSocketProperties.Performance

`public static class Performance`　Lombok：`@Data`　性能相关配置

**字段 / 常量**

```java
int sendShardCount = 8  // WebSocket发送队列分片数量 默认8，高并发推送场景可按需调大
int sendQueueWorkersPerShard = 1  // 每个发送队列分片的工作线程数 默认1；大于1时仍按Channel保序，但会增加常驻线程数
int sendQueueBufferSize = 16384  // 每个发送队列的RingBuffer大小 必须是2的幂次方，最小1024
int sendQueueTryTimeoutMs = 50  // 尝试入队的最大等待时间（毫秒） 超时未入队的消息被丢弃，并计入丢弃统计（每10秒以WARN输出一次）
String sendQueueThreadPrefix = "ws-send-"  // 发送队列线程名前缀
String sendQueueWaitStrategy = "BLOCKING"  // 发送队列等待策略（BLOCKING/YIELDING/BUSY_SPIN） 默认BLOCKING，空闲时不占用CPU；YIELDING/BUSY_SPIN 会让每个发送线程持续占用CPU
int heartbeatPoolCoreSize = Math.max(16, Runtime.getRuntime().availableProcessors() * 2)  // 心跳发送线程池核心线程数
int heartbeatPoolMaxSize = Math.max(32, Runtime.getRuntime().availableProcessors() * 4)  // 心跳发送线程池最大线程数
int heartbeatPoolQueueSize = 50000  // 心跳发送线程池队列容量
int messagePoolCoreSize = Math.max(32, Runtime.getRuntime().availableProcessors() * 4)  // 消息处理线程池核心线程数
int messagePoolMaxSize = Math.max(64, Runtime.getRuntime().availableProcessors() * 8)  // 消息处理线程池最大线程数
int messagePoolQueueSize = 20000  // 消息处理线程池队列容量
```

## 包 `com.mcst.easyfk.websocket.security`

### NonceValidator

`public class NonceValidator`　注解：`@Slf4j`　Nonce防重放校验器 记录时间窗口内已使用过的nonce，同一nonce在窗口内重复出现时判定为重放请求并拒绝 签名协议包含时间戳并校验时效，nonce缓存TTL必须覆盖时间戳的整个有效区间（2 × 允许偏差）…

**构造器**

```java
NonceValidator(long nonceTtlSeconds)
```

**方法**

```java
boolean tryUseNonce(String nonce)  // 尝试使用nonce 原子地检查并记录：首次出现返回true；窗口内重复出现返回false（判定为重放）
```

### TrustedProxyMatcher

`public class TrustedProxyMatcher`　可信代理地址匹配器 支持单个IP与CIDR（IPv4/IPv6），只接受IP字面量，不做DNS解析

**构造器**

```java
TrustedProxyMatcher(Collection<String> entries)
```

**方法**

```java
boolean isEmpty()
boolean matches(String ip)  // 判断地址是否命中可信代理列表
static byte[] toBytes(String ip)  // 将IP字面量转为字节数组，IPv4映射的IPv6地址统一转为IPv4；非IP字面量返回null
```

## 包 `com.mcst.easyfk.websocket.sender`

### SessionSendDispatcher

`public class SessionSendDispatcher`　注解：`@Slf4j`　将消息分发到固定分片的Disruptor队列

**构造器**

```java
SessionSendDispatcher(WebSocketProperties webSocketProperties, SessionSendWorker sessionSendWorker, ISocketManager socketManager)
```

**方法**

```java
@SuppressWarnings("unchecked") @PostConstruct void init()
void publish(Channel channel, TextWebSocketFrame textFrame)  // 发布消息到发送队列（用于单用户/少量用户消息） 本方法接管textFrame的所有权：入队成功后由消费端负责释放， 任何失败/提前返回路径都会在此释放，保证引用计数闭环
@PreDestroy void destroy()
```

### SessionSendEvent

`public class SessionSendEvent`　Lombok：`@Data` `@Accessors(chain = true)`　WebSocket消息发送事件 封装待发送的会话与消息内容

**字段 / 常量**

```java
Channel channel  // Netty Channel
TextWebSocketFrame textFrame  // 预创建的TextWebSocketFrame对象 同一条消息推送给多个用户时，复用同一个 TextWebSocketFrame 实例
```

**方法**

```java
SessionSendEvent clear()  // 清理事件对象，释放引用以便GC
```

### SessionSendWorker

`public class SessionSendWorker`　注解：`@Slf4j`　负责实际的WebSocket消息发送与异常清理

**构造器**

```java
SessionSendWorker(ISocketManager socketManager)
```

**方法**

```java
static long getAndResetNotWritableCount()  // 获取 Channel 不可写次数（供监控使用）
static long getAndResetSentCount()  // 获取总发送次数（供监控使用）
void send(Channel channel, TextWebSocketFrame textFrame)  // 发送消息到指定Channel 本方法消费textFrame：写入成功交由Netty释放，跳过发送的路径在此释放
```

### WebSocketMessageSender

`public class WebSocketMessageSender`　注解：`@Slf4j`　WebSocket消息发送器 负责处理各种消息发送场景：定点（会话/用户/账户）与全员广播 性能设计： - 定点消息走 Disruptor 分片队列异步发送 - 广播使用 retainedDuplicate() 零拷贝…

**方法**

```java
void sendMessageToUser(String userSessionId, PushMessage<?> message)  // 向指定用户发送消息（少量用户仍走 Disruptor，保证可靠性）
void sendMessageToUserByUserId(String userId, PushMessage<?> message)  // 根据用户ID向指定用户发送消息（支持逗号分隔的多个用户ID） 通过 WsUserDataManager 将 userId 解析为 sessionId，再逐一发送
void sendMessageToUserByAccountId(String accountId, PushMessage<?> message)  // 根据账户ID向指定账户的所有在线会话发送消息（支持逗号分隔的多个账户ID） 通过 WsUserDataManager 将 accountId 解析为 sessionId，再逐一发送
void broadcastToAll(PushMessage<?> message)  // 向所有在线用户广播消息（全员通知，高性能版本） 使用方案3：直接批量广播
void sendSystemNotification(String title, String content, NotificationLevel level)  // 发送系统通知给所有在线用户
void sendSystemNotification(String title, String content)  // 发送系统通知给所有在线用户（默认普通等级）
Map<String, Long> getAndResetBroadcastStats()  // 【优化新增】获取并重置广播统计
```

### WsSendProcessor

`public class WsSendProcessor implements KeyOrderedProcessor<SessionSendEvent>`　Lombok：`@RequiredArgsConstructor`　Disruptor消费者：按 Channel 保序处理发送事件 实现 KeyOrderedProcessor，分片内多 worker 时同一 Channel 的消息固定由同一线程串行发送…

**方法**

```java
Object orderingKey(SessionSendEvent event)
void process(SessionSendEvent event)
```

## 包 `com.mcst.easyfk.websocket.server`

### PushMessageServer

`public class PushMessageServer implements IPushWsMsgApi`　注解：`@Slf4j`　消息推送服务（IPushWsMsgApi 的本地实现） 使用策略模式处理不同类型的消息推送

**方法**

```java
BaseResult<?> pushMessage(PushWsMessageParam param)  // 推送消息 根据参数自动路由推送策略： - 带 userSessionId/userId/accountId：定点推送到对应在线会话 - channel=notification 且无用户标识：全员广播系统通知 - 其他组…
```

### WebSocketServer

`public class WebSocketServer implements SmartLifecycle`　注解：`@Slf4j`　WebSocket服务器 启动和管理WebSocket服务 作为 SmartLifecycle 在容器刷新阶段同步绑定端口，SSL 配置错误、端口占用等启动失败 会抛出异常并导致 Spring 应用启动失败

**方法**

```java
synchronized void start()
synchronized void stop()
boolean isRunning()
```

## 包 `com.mcst.easyfk.websocket.strategy`

### MessagePushStrategy

`public interface MessagePushStrategy`　消息推送策略接口

**方法**

```java
boolean support(PushWsMessageParam param)  // 判断该策略是否支持当前推送参数
void push(PushWsMessageParam param, PushMessage<Map<String, Object>> message)  // 执行消息推送
default int getOrder()  // 获取策略优先级，数字越小优先级越高
```

### MessagePushStrategySelector

`public class MessagePushStrategySelector`　消息推送策略选择器

**构造器**

```java
MessagePushStrategySelector(List<MessagePushStrategy> strategies)
```

**方法**

```java
MessagePushStrategy select(PushWsMessageParam param)  // 根据推送参数选择合适的策略
```

## 包 `com.mcst.easyfk.websocket.strategy.impl`

### NotificationPushStrategy

`public record NotificationPushStrategy(WebSocketMessageSender messageSender) implements MessagePushStrategy`　系统通知推送策略（全员广播） 仅处理不带用户标识的通知推送；携带userSessionId/userId/accountId的通知 会落入UserPushStrategy进行定点推送

**构造参数（record 组件）**

```java
WebSocketMessageSender messageSender
```

**方法**

```java
boolean support(PushWsMessageParam param)
void push(PushWsMessageParam param, PushMessage<Map<String, Object>> message)
int getOrder()
```

### UserPushStrategy

`public record UserPushStrategy(WebSocketMessageSender messageSender) implements MessagePushStrategy`　推送消息给特定用户策略 支持三种用户维度定位：userSessionId（会话）、userId（用户）、accountId（账户）， 多个维度同时传入时分别推送（同一会话命中多个维度会收到多条）

**构造参数（record 组件）**

```java
WebSocketMessageSender messageSender
```

**方法**

```java
boolean support(PushWsMessageParam param)
void push(PushWsMessageParam param, PushMessage<Map<String, Object>> message)
int getOrder()
```

## 包 `com.mcst.easyfk.websocket.util`

### SecuritySignUtil

`public class SecuritySignUtil`　注解：`@Slf4j`　WebSocket安全签名工具类 签名算法：hex(HMAC-SHA256(ClientType=xxx&ClientId=xxx&Nonce=xxx&Timestamp=xxx&Param=xxx, secret))…

**方法**

```java
static String generateHmacSign(String clientType, String clientId, String nonce, Long timestamp, String param, String secret)  // 生成HMAC-SHA256签名
static boolean verifyHmacSign(String clientType, String clientId, String nonce, Long timestamp, String param, String secret, String sign)  // 验证HMAC-SHA256签名（大小写不敏感，常量时间比较）
static boolean isTimestampFresh(Long timestamp, long toleranceSeconds)  // 校验时间戳是否在允许偏差内
static Long parseTimestamp(String timestamp)  // 解析毫秒时间戳字符串，非法时返回null
static String sortAndSerializeParam(Map<String, Object> paramMap)  // 对Map参数按顶层key的ASCII码排序并转为JSON字符串，空Map返回空串
```

## 包 `com.mcst.easyfk.websocket.vo`

### PushMessage

`public class PushMessage<T> implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)`　注解：`@Schema(description = "服务端推送数据对象")`

**字段 / 常量**

```java
@Schema(description = "频道，例如：kline,quote,order,notification等", name = "channel") String channel
@Schema(description = "类别", name = "category") String category
@Schema(description = "数据信息", name = "data") T data
@Schema(description = "推送时间", name = "time") Instant timestamp
```

### ResponseMessage

`public class ResponseMessage<T> implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)`　注解：`@Schema(description = "服务端事件响应对象")`

**字段 / 常量**

```java
@Schema(description = "是否成功", name = "success") Boolean success
@Schema(description = "提示消息", name = "message") String message
@Schema(description = "数据信息", name = "data") T data
@Schema(description = "响应时间", name = "time") Instant timestamp
```

### WsUserData

`public class WsUserData implements Serializable`　Lombok：`@Data` `@Builder` `@NoArgsConstructor` `@AllArgsConstructor`

**字段 / 常量**

```java
String userSessionId  // 用户会话ID
String userId  // 用户ID
String accountId  // 账户ID
String clientId  // 客户端ID
String clientIp  // 客户端IP
String clientType  // 客户端类型
```
