# easyfk-gateway Skill 参考文档

> 所属项目：`easyfk-base`　模块：`easyfk-gateway`（单模块）
> 坐标：`com.mcst:easyfk-gateway:3.2.12`
> 依据：全部源码（8 个类），对齐 `gateway开发文档.md`、`gateway特点.md`。
> 以源码为准；差异见文末「复查记录」。

---

## 1. 模块定位

基于 Spring Cloud Gateway（WebFlux/Netty），提供**两个** `GlobalFilter`，下游微服务配合 `web-micro` 使用：
- `RequestGatewayFilter`（第一阶段，路由过滤器之前）：请求头解析、TraceId、签名验证（v1 MD5 / v2 HMAC-SHA256，与 web-prd 一致）加时间戳新鲜度和 nonce 原子防重放，验签通过后再解析 JWT 会话。
- `GatewayAuthorizationFilter`（第二阶段，StripPrefix/RewritePath 等路由过滤器之后）：三级 URI 权限拦截和 `IExtendGatewayFilter` 扩展调用。

阻塞调用（Redis、JWT、动态密钥、`checkUriSecurityLevel` RPC、`checkAuth`）全部通过 `GatewayContextUtil.blocking` 在 `Schedulers.boundedElastic()` 上执行，不占用 Netty 事件循环。请求级数据保存在 exchange 属性中（键见 `GatewayAttributeConstant`：`TRACE_ID`、`REQUEST_HEADERS`、`USER_DATA`、`ORIGINAL_PATH`、`DOWNSTREAM_PATH`、`BYPASS`）；ThreadLocal（`RequestHeaderContext`/`TraceIdContext`/`UserDataContext`/MDC）只在 blocking 回调内部设置，并在同一线程内清理，Dubbo/Feign 等依赖 ThreadLocal 的远程调用仍可拿到上下文。

依赖（全部为 api）：`easyfk-core`、`easyfk-web:web-common`（会传递 `web-base`，即 JWT/上下文）、`easyfk-authority`，以及 `spring-cloud-starter-gateway`（排除 logging）。

运行前提，需要由网关工程自行提供：
- `ICacheService` 实现（如 `cache-redis`）：开启签名时必须有。缺失时启动打印 ERROR 日志，需验签的请求返回 `SYSTEM_BUSY`（503）。
- `UserDataManager`：需要 `easyfk.config.login.cache-type=redis`，用于登录态和权限校验。缺失时只能解析 JWT、拿不到 UserData，LOGIN 级返回 UNLOGIN；AUTHORITY 级返回 `SYSTEM_BUSY`（503）并打印 ERROR 日志。
- `IAuthResourceApi` 实现（通常是对权限服务的 Dubbo/Feign 远程调用）：开启权限拦截时必须有。三者均通过 `ObjectProvider` 按需获取；`IAuthResourceApi` 缺失时启动打印 ERROR 日志，运行时除 `exclude-paths` 外的请求一律返回 `SYSTEM_BUSY`（503，fail-closed），不会因缺失而放行。

---

## 2. 自动配置

`GatewayFilterConfigure`（启用 `GatewayFilterProperties`）注册两个 Bean，均为 `@ConditionalOnMissingBean`：
- `requestHeaderGatewayFilter`（`RequestGatewayFilter`）：order 默认 `Ordered.HIGHEST_PRECEDENCE + 100`，可用 `easyfk.config.gateway.filter-order` 调整。它在所有路由过滤器（order 1..n）之前执行；如果你自己的 GlobalFilter 必须更早，order 设得比它更小即可。
- `gatewayAuthorizationFilter`（`GatewayAuthorizationFilter`）：order 固定为 `RouteToRequestUrlFilter.ROUTE_TO_URL_FILTER_ORDER + 1`（10001），在路由过滤器和 `RouteToRequestUrlFilter` 之后、负载均衡（10150）和 Netty 转发之前执行。

web-common 配置：

| 配置 | 默认值 | 网关中的作用 |
|---|---|---|
| `easyfk.config.web.security.open` | false | 是否开启签名、时间戳新鲜度和 nonce 防重放 |
| `easyfk.config.web.security.sign-version` | `v1` | `v1`：同时接受 v1（MD5）和 v2（HMAC-SHA256）请求；`v2`：拒绝 v1 请求。客户端用 `Sign-Version: v2` 头声明版本 |
| `easyfk.config.web.security.sign-key` / `sign-key-dynamic` / `ignore-uri` / `timeout` | `mcst_sign_reset` / false / null / 150s | 签名密钥、动态密钥、免签 URI（按网关侧原始路径做 Ant 匹配）、时间戳允许偏差（±timeout）；nonce TTL 为 2 × timeout，覆盖整个可接受窗口。`timeout` 是 `Duration`，必须带单位（如 `150s`），不带单位按毫秒解析 |
| `easyfk.config.web.intercept.open-gateway-interceptor` | false | 是否开启三级 URI 权限拦截 |
| `easyfk.config.web.intercept.exclude-paths` | null | 权限拦截排除路径（按**网关侧原始路径**做 Ant 匹配，如 `/user-service/login`） |
| `easyfk.config.web.intercept.refresh-user-auth` | false | 每个请求是否刷新用户 token 有效期 |
| `easyfk.config.web.intercept.custom-gateway-filter` | false | 是否把整个流程交给 `ICustomGatewayFilter` |
| `easyfk.config.web.jwt.*` | 见 web 文档 | 必须与签发 token 的服务保持**同一套 secret/salt** |

网关专属配置（`GatewayFilterProperties`，前缀 `easyfk.config.gateway`）：

| 配置 | 默认值 | 作用 |
|---|---|---|
| `filter-order` | `Ordered.HIGHEST_PRECEDENCE + 100` | `RequestGatewayFilter` 的执行顺序 |
| `api-doc-path` | `/v3/api-docs` | 请求路径**以它结尾**时视为接口文档请求，原样转发（不改写路径、保留服务前缀），跳过签名和权限校验；配置为空串则不放行文档请求 |
| `max-sign-body-size` | `2MB` | v2 签名时缓存请求体的上限 |

`api-auth`、`cors`、`require-auth-by-default`、`auth-type` 对网关**无效**。跨域请使用 Spring Cloud Gateway 自带的 `spring.cloud.gateway.globalcors`，网关的失败响应也会按它补充 CORS 头。

---

## 3. 过滤流程（以源码为准）

```
RequestGatewayFilter.filter(exchange)            // order = filter-order，路由过滤器之前
 ├ CORS 预检请求（OPTIONS + Origin + Access-Control-Request-Method）→ 标记 BYPASS 放行；普通 OPTIONS 照常校验
 ├ custom-gateway-filter=true → 标记 BYPASS，交给 ICustomGatewayFilter（未注册 Bean 时记 ERROR 日志并返回 SYSTEM_BUSY）
 ├ 路径以 api-doc-path 结尾 → 标记 BYPASS，原样转发（不改写路径）
 ├ 解析 Reset-Sign/Timestamp/Request-Token/Access-Token/Request-Nonce/Device-No/Client-Type/Language
 │    → exchange 属性 REQUEST_HEADERS；新建 TraceId → TRACE_ID；网关侧原始路径 → ORIGINAL_PATH
 ├ security.open=true 且不在 ignore-uri → 准备签名
 │    sign-version=v2 而客户端不是 v2 → SIGN_ERROR
 │    客户端 v2 且为非 GET/HEAD、非 multipart/表单 → 响应式缓存请求体（DataBufferUtils.join，上限 max-sign-body-size）
 │       Content-Length 超限：不缓存、跳过请求体比对（与 web-prd 一致）；未声明长度且读取超限：SIGN_ERROR
 ├ [boundedElastic] 先验签，再解析会话
 │    验签：nonce 必填且匹配 ^[A-Za-z0-9-_]{8,64}$ → Reset-Sign 必填 → Timestamp 必填（v1/v2 都要求）且为数字
 │       → |now - ts| ≤ timeout（兼容秒级）→ 取密钥（静态或动态，查询异常 SYSTEM_BUSY）
 │       → v1：MD5("Request-Nonce={n}&Timestamp={ts}&Key={key}")
 │         v2：Sign-Body 必须等于服务端算出的 SHA-256(body)（已缓存时），
 │             HMAC-SHA256(key, "{METHOD}\n{canonicalUri}\n{Sign-Body}\n{nonce}\n{ts}")
 │             canonicalUri = 网关侧原始路径（不解码，去掉 base-path）+ 有 query 时 "?" + 原始 query（不解码、不排序），
 │             与 web-prd RequestUtil.getCanonicalUri 口径一致
 │       → 与 Reset-Sign 常量时间比较 → setIfAbsent(nonce, 2 × timeout) 原子占用，失败 API_AGAIN，缓存异常 SYSTEM_BUSY
 │    会话：ContextDataManager.doDataContext(refresh-user-auth) → JWT 解析 + getUserData → exchange 属性 USER_DATA
 │       （异常按 SYSTEM_BUSY 拒绝）
 └ 转发：设置 TRACE_ID 请求头，其余头（Access-Token、Language 等）原样透传

（路由过滤器 StripPrefix/RewritePath 等、RouteToRequestUrlFilter 执行）

GatewayAuthorizationFilter.filter(exchange)      // order = 10001
 ├ BYPASS → 放行
 ├ 没有 REQUEST_HEADERS 属性（第一阶段未执行）→ ERROR 日志 + SYSTEM_BUSY
 ├ 下游路径 = GATEWAY_REQUEST_URL_ATTR 的 rawPath（取不到时用改写后的请求路径）→ 属性 DOWNSTREAM_PATH
 ├ open-gateway-interceptor=true
 │    exclude-paths（匹配 ORIGINAL_PATH）放行
 │    IAuthResourceApi 未注册 → SYSTEM_BUSY
 │    [boundedElastic] level = checkUriSecurityLevel(下游路径)（异常 SYSTEM_BUSY；返回 null 按 LOGIN 处理）
 │       UNIMPEDED：放行；LOGIN：无 UserData 返回 UNLOGIN
 │       AUTHORITY：无 UserData 或 loginToken 返回 UNLOGIN；无 UserDataManager 返回 SYSTEM_BUSY；
 │                  checkAuth(loginToken, 下游路径) 不为 true 返回 UNAUTH
 │    适用于 yml、Discovery Locator、Java DSL 定义的全部路由，不会因为识别不出服务而跳过鉴权
 └ 放行：按顺序调用全部 IExtendGatewayFilter.doExtendIntercept(exchange) → chain.filter
```

失败响应由 `gateway.util.FailRequestUtil.failRequest(exchange, ErrorRequest, CorsConfigurationSource)` 写出，响应体为 `ResponseResult{code,msg}` 的 JSON，HTTP 状态码取 `ErrorRequest.getHttpStatus()`（web-common 统一定义，与 web 模块一致）。网关会用到的错误：

| 错误 | HTTP 状态 |
|---|---|
| `NONCE_EMPTY`、`NONCE_FORMAT_ERROR`、`RESET_SIGN_EMPTY`、`TIMESTAMP_EMPTY`、`TIMESTAMP_ERROR`（请求头缺失或格式错误） | 400 |
| `UNLOGIN`、`SIGN_ERROR`、`EXPIRED`、`API_AGAIN`（未认证、验签/时间戳/防重放失败） | 401 |
| `UNAUTH` | 403 |
| `SYSTEM_BUSY`、`DYNAMIC_SIGN_KEY_TIMEOUT`（缓存/权限服务不可用、必需 Bean 缺失、动态密钥过期） | 503 |

请求带 `Origin` 且被 `spring.cloud.gateway.globalcors` 允许时，失败响应会补充 `Access-Control-Allow-Origin`、`Vary: Origin`，以及按配置补充 `Allow-Credentials`、`Expose-Headers`（网关路由映射已写过时不重复写）。

---

## 4. 扩展方式

| 方式 | 做法 | 实际效果 |
|---|---|---|
| 完全替换流程 | 实现 `ICustomGatewayFilter` Bean，并设 `custom-gateway-filter: true` | 除 CORS 预检外，所有请求只走自定义逻辑（两个阶段的校验都跳过）。开关打开但没有 Bean 时返回 503 并记 ERROR 日志 |
| 替换过滤器 | 注册自己的 `RequestGatewayFilter` / `GatewayAuthorizationFilter`（子类）Bean | `@ConditionalOnMissingBean` 生效。第二阶段依赖第一阶段写入的 exchange 属性，缺失时拒绝请求 |
| 追加逻辑 | 写独立的 `GlobalFilter` 并指定 order | 推荐用这种方式实现限流、日志等；需要用户信息时从 exchange 属性（`GatewayAttributeConstant`）读取，不要读 ThreadLocal |
| `IExtendGatewayFilter` | 实现接口并注册 Bean（可多个，按 `@Order`） | 全部校验通过、转发下游前同步调用，此时路由过滤器已执行。可能运行在事件循环或 boundedElastic 线程，不能阻塞，也不能中断请求 |

---

## 5. 与下游 web-micro 的配合

- 下游通过**原样透传**的 `Access-Token` 头重新解析 JWT 并加载 UserData，所以网关和下游必须使用相同的 JWT 配置，并共享同一个登录缓存（Redis）。
- 下游通过原样透传的 `Language` 头获取语言。
- 网关为每个请求新建 TraceId（忽略客户端传入的值），写入下游请求头 `TRACE_ID`，web-micro 读取它延续链路。
- 网关不再生成 `Chain-Data` 头；`RequestHeaderConstant.CHAIN_NAME` 与 web-common 的 `FilterChainData` 已删除。
- 下游 micro 不做鉴权，所以 micro 服务只能通过网关访问。

---

## 6. 生成代码时的规则

**Do**
- 网关工程依赖 `easyfk-gateway`，再加上 `cache-redis`、注册中心，以及 `IAuthResourceApi` 的远程实现；配置 `easyfk.config.login.cache-type: redis`。
- 配置写完整前缀：`easyfk.config.web.security.*`、`easyfk.config.web.intercept.*`。`timeout` 要带单位（如 `150s`）。
- 路由用 StripPrefix/RewritePath 把网关前缀去掉，使下游收到的路径与 Controller 路径一致：权限校验使用的就是下游路径（`/order-service/order/list` 经 `StripPrefix=1` 后按 `/order/list` 校验）。下游配置了 `context-path` 时，下游路径会包含它，而 web-prd 注册的资源路径不含 context-path，此时需要在路由中去掉或让权限服务按同样规则登记。
- 匿名接口（登录、注册、验证码）写进 `exclude-paths`（网关侧原始路径）；免签接口写进 `security.ignore-uri`（网关侧原始路径）。
- 前端按 HTTP 状态码加响应体 `code` 区分：401 且 `code=UNLOGIN` 去登录，401 的其他 code 是签名/时间戳/重放失败，403 提示无权限，400 是请求头错误，503 稍后重试；跨域用 `spring.cloud.gateway.globalcors`。
- 客户端签名的 URI 用请求网关时的路径（含服务前缀，不解码），有 query 时追加 `?` + 原始 query string（不解码、不排序，与实际发送的完全一致）；网关不处理 `Param-Sign`；建议服务端配置 `sign-version: v2`，客户端发送 `Sign-Version: v2`、`Timestamp`（毫秒）、`Request-Nonce`、`Sign-Body`（请求体 SHA-256 十六进制）。非 GET/HEAD、非 multipart/表单请求的 `Sign-Body` 必须等于服务端算出的摘要（空请求体即空字节的 SHA-256）；GET/HEAD/multipart/表单不比对请求体，`Sign-Body` 可不传，不传时按空串参与签名。
- 需要限流、日志等时，编写独立的 `GlobalFilter`；只需在转发前追加请求头等非阻塞操作时，实现 `IExtendGatewayFilter`。

**Don't**
- 不要在 `IExtendGatewayFilter` 或自定义 GlobalFilter 中执行阻塞调用，也不要读取 `UserDataContext` 等 ThreadLocal，改用 exchange 属性。
- 不要只开 `custom-gateway-filter` 而不注册 `ICustomGatewayFilter` Bean（会让所有请求返回 503）。
- 不要把需要鉴权的接口放在 `exclude-paths` 或以 `api-doc-path` 结尾的路径上。
- 不要依赖 `Chain-Data` 头，网关已不再生成它。

---

## 7. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | 特点 §2.1 / §2.10 | 非阻塞 I/O，不阻塞 Netty 事件循环；用 ThreadLocal 加 doFinally 安全管理上下文 | 过滤器在事件循环线程上**同步执行**以下阻塞调用：Redis（getUserData、existKey、cacheObject、动态密钥）、JWT 解析、`authResourceApi.checkUriSecurityLevel`（通常是远程 RPC）、`checkAuth`。上下文放在 ThreadLocal 中，`doFinally` 可能在另一个线程执行，清理不到原线程（下一个请求会覆盖 UserData，所以不会串用户，但阻塞问题仍会拖垮吞吐） **已修复**：所有阻塞调用经 `GatewayContextUtil.blocking` 在 boundedElastic 线程执行；请求数据存放在 exchange 属性中，ThreadLocal 只在回调内设置并在同一线程 finally 清理，不再依赖 doFinally |
| 2 | 开发文档 §4.1.3、特点 §2.3 | 签名加 Nonce 防重放 | 只检查 Timestamp **是否存在**，**不校验新鲜度**，nonce 过期（timeout）后可以原样重放。nonce 用 `existKey` + `cacheObject`，**非原子**，并发重放可同时通过。只支持 v1 MD5（不绑定 URI/body）；`Timestamp` 不是数字时 `Long.parseLong` 直接抛异常（500）。与 web-prd 实现不一致 **已修复**：Timestamp 必填、非数字返回 TIMESTAMP_ERROR、超出 `timeout` 返回 EXPIRED；nonce 格式校验并用 `setIfAbsent` 原子占用；nonce TTL 为 2 × timeout；支持与 web-prd 相同的 v2 HMAC-SHA256（绑定方法、规范 URI（路径 + 原始 query）、请求体摘要，请求体响应式缓存且有上限），`sign-version=v2` 时拒绝 v1 |
| 3 | 开发文档 §7.2 | 配置示例 `security:`、`intercept:`、`timeout: 300` | 前缀错误，应为 `easyfk.config.web.security` / `easyfk.config.web.intercept`。`timeout` 是 `Duration`，`300` 不带单位时按 **300 毫秒** 解析，nonce 几乎立即过期，防重放失效 |
| 4 | 开发文档 §4.3 / §7.3、特点 §2.7 | `IExtendGatewayFilter` 在默认流程基础上追加逻辑 | 接口没有被注入或调用，实现后不会执行 **已修复**：`GatewayAuthorizationFilter` 在全部校验通过、转发前通过 `ObjectProvider.orderedStream()` 依次调用所有实现 |
| 5 | 开发文档 §4.1.5、特点 §2.5 | 下游服务从 `Chain-Data` 头统一还原上下文 | 全框架没有代码读取 `Chain-Data`；web-micro 读取的是原始的 `Access-Token`、`TRACE_ID`、`Language` 头 **已修复**：网关不再生成 `Chain-Data`（相关常量与 `FilterChainData` 已删除），`Access-Token`、`Language` 原样透传，`TRACE_ID` 由网关写入 |
| 6 | 特点 §2.6 | TraceId 随请求上下文传递到下游 | 网关只在本地生成 TraceId（并且忽略客户端传入的值），不写 `TRACE_ID` 头，下游拿不到，链路断开 **已修复**：网关把新建的 TraceId 写入下游请求头 `TRACE_ID`（仍忽略客户端传入值） |
| 7 | 特点 §2.8、开发文档 §4.1.4 | 精确识别目标微服务，实现服务级访问控制 | 服务名只用来判断"是否为空"，并不参与鉴权。只解析 yml 路由中以 `**` 结尾的 Path 谓词，并用 `requestUri.contains(前缀)` 做子串匹配；路由 uri 不是 `lb://`，或路由来自 Discovery/Java DSL 时，**整个权限拦截被跳过，请求直接放行** **已修复**：不再解析 yml 路由，路由从 exchange（`GATEWAY_ROUTE_ATTR`/`GATEWAY_REQUEST_URL_ATTR`）获取，对 yml、Discovery、Java DSL 路由一律按下游路径鉴权，不会因识别不出服务而放行 |
| 8 | 特点 §3.1 | 不引入权限模块时，`UserDataManager` 可选，权限校验自动跳过 | `authority` 本身就是 api 依赖。`UserDataManager` 只有在 `login.cache-type=redis` 时才存在，缺失时 AUTHORITY 级别会 **NPE**（没有判空），而且 sessionFilter 只能解析 JWT，拿不到 UserData，所有 LOGIN 级别都返回 UNLOGIN。`IAuthResourceApi` 以 `@Resource @Lazy` 注入，缺失时首个请求才报错 **已修复**：`IAuthResourceApi`、`UserDataManager`、`ICacheService`、`ICustomGatewayFilter` 均用 `ObjectProvider` 获取；缺失时启动打印 ERROR 日志，运行时对受保护请求 fail-closed 返回 SYSTEM_BUSY（503），不再 NPE 或放行 |
| 9 | 特点 §2.1、开发文档 §4.1 | `getOrder()=0` 是最高优先级，在所有过滤器之前执行 | 0 不是最高优先级（`HIGHEST_PRECEDENCE=Integer.MIN_VALUE`），order 为负的 GlobalFilter 会先于它执行 **已修复**：`RequestGatewayFilter` 默认 order 为 `HIGHEST_PRECEDENCE + 100`，可通过 `easyfk.config.gateway.filter-order` 配置；鉴权阶段固定在路由过滤器之后（10001） |
| 10 | 特点 §2.2 | 签名验证（第 2 层）先于会话管理（第 3 层） | 实际顺序是先执行 sessionFilter（JWT 解析，可能还要查 Redis），再验签，未签名的请求也会消耗会话查询 **已修复**：先校验签名/时间戳/nonce，通过后才解析 JWT 和查询 UserData |
| 11 | 特点 §2.9 | Knife4j 透传 | 任何**包含** `/v3/api-docs` 的路径都会被改写为 `/v3/api-docs`，并跳过上下文和全部校验（改写后只能访问文档端点，风险较低，但会丢失服务前缀） **已修复**：只有以 `easyfk.config.gateway.api-doc-path`（默认 `/v3/api-docs`）结尾的路径才视为文档请求，原样转发不改写路径，配置为空可关闭放行 |
| 12 | 开发文档 §4.4 | 统一返回 400 | 属实。UNLOGIN/UNAUTH 也是 400（不是 401/403），并且失败响应没有 CORS 头，浏览器跨域时前端读不到错误体（需要 globalcors 补充） **已修复**：状态码取 `ErrorRequest.getHttpStatus()`（UNLOGIN/验签/过期/重放 401、UNAUTH 403、SYSTEM_BUSY/动态密钥过期 503、请求头缺失或格式错误 400）；请求 Origin 被 globalcors 允许时，失败响应补充 CORS 头 |
| 13 | 补充 | — | `checkUriSecurityLevel` 收到的是**网关侧完整路径**（含路由前缀，如 `/order-service/order/list`）。而 web-prd 的 `InitResourceRunner` 注册的是 Controller 路径（`/order/list`），两者对齐依赖权限服务实现或路由规划（如前缀与服务内 context-path 一致），否则资源匹配不上，按"其他级别"放行 **已修复**：鉴权移到路由过滤器之后执行，`checkUriSecurityLevel`/`checkAuth` 使用 `GATEWAY_REQUEST_URL_ATTR` 中的下游路径（已经过 StripPrefix/RewritePath）；下游有 context-path 时路径会包含它，需在路由中处理 |
