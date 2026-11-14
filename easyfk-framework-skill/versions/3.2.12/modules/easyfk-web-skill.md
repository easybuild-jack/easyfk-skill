# easyfk-web Skill 参考文档

> 所属项目：`easyfk-base`　子模块：`web-simple`、`web-base`、`web-common`、`web-micro`、`web-prd`
> 坐标：`com.mcst:web-<子模块>:3.2.12`（业务工程只引 `web-prd` 或 `web-micro`）
> 依据：5 个子模块全部源码，对齐 `web-prd开发手册.md`、`web-prd技术特点.md`、`web-micro开发手册.md`、`web-micro技术特点.md`、`EasyFK框架开发手册.md` §3.4，以及根目录的 `web-prd安全优化方案.md`、`web安全与幂等审查报告.md`。
> 以源码为准；差异见文末「复查记录」。

---

## 1. 模块定位与选型

| 子模块 | 角色 | 业务方是否直接引用 |
|---|---|---|
| `web-simple` | 只有 build.gradle：`spring-boot-starter-web`（排除 logging、tomcat）+ `spring-boot-starter-undertow` + core | 否（被 micro/prd 传递） |
| `web-base` | JWT（`JwtManager`）+ 请求上下文（`ContextDataManager`） | 否 |
| `web-common` | 配置属性（cors/intercept/security）、错误码 `ErrorRequest`、缓存名常量、URI 匹配工具、i18n 消息 | 否 |
| `web-micro` | **网关后面的内部微服务**：只还原上下文，不鉴权、不验签 | 是 |
| `web-prd` | **直接对外的单体 / BFF**：签名防重放、登录与权限拦截、幂等、API 调用方鉴权、CORS、安全头、资源初始化 | 是 |

依赖链：`web-base → easyfk-authority`（api），`web-common → web-base`（api），`web-micro / web-prd → web-simple + web-common`（api）。

选型规则：
- 前面有 `easyfk-gateway` 做统一鉴权 → 用 `web-micro`。
- 浏览器 / App / 第三方直接访问本服务 → 用 `web-prd`。
- **两者不要同时引入**：都注册了名为 `requestBaseFilter` 的 Bean 和全局异常处理器。

---

## 2. web-base：JWT 与上下文

### 2.1 自动配置

`WebBaseConfig` **无条件**注册 `JwtManager`、`ContextDataManager`，并启用 `JwtProperties`（没有 `@ConditionalOnMissingBean`）。

### 2.2 JWT 配置 `easyfk.config.web.jwt`

| 属性 | 默认值 | 说明 |
|---|---|---|
| `secret` | 内置默认值 | 生产必须覆盖，未覆盖只打 WARN 日志 |
| `salt` | 内置默认值 | 实际签名密钥 = HMAC-SHA256(secret) 作用于 salt；改动后存量 token 全部失效 |
| `expires-second` | `10800`（3 小时） | `<=0` 时按默认值处理 |
| `allowed-algorithms` | `HS256` | 逗号分隔的算法白名单，用来防 `alg=none` |

### 2.3 JwtManager

```java
String token = jwtManager.createJwtByObject(loginUser);   // fastjson 序列化后放进 "content" claim，并写入 iat/exp
String token2 = jwtManager.createJwtByString("text");
LoginUser u = jwtManager.getObjectContent(token, LoginUser.class);
String s = jwtManager.getStringContent(token);
```

- 校验顺序：算法白名单 → 签名 → 缺少 `exp` 报 `JWT_FORMAT` → 过期报 `JWT_EXPIRED` → content 为空报 `JWT_FORMAT`。签名错误报 `JWT_SIGN_INVALID`。
- **payload 只签名不加密**：不要往 token 里放手机号、密码等敏感数据。

### 2.4 ContextDataManager

| 方法 | 行为 |
|---|---|
| `doDataContext(boolean refreshUserAuth)` | 从 `RequestHeaderContext` 取 accessToken（忽略空值和 `"undefined"`），解析为 `LoginUser` 并写入 `loginToken`，再通过 `UserDataManager.getUserData` 写入 `UserDataContext`。参数为 true 时刷新用户 token；若存在名为 `asyncTaskExecutor` 的 Bean 则异步执行 |
| `doDataContext(String traceId, boolean refreshUserAuth)` | traceId 非空且匹配 `^[A-Za-z0-9\-_.]{1,64}$` 时沿用（写入 `TraceIdContext` 和 MDC），否则调用 `createTraceId()` 新生成；随后调用 `doDataContext(refreshUserAuth)`。web-micro 使用 |
| `createTraceId()` | `IdUtil.randomUUID()` 生成 traceId，写入 `TraceIdContext` 和 MDC |
| `clearContext()` | 移除 TraceId、RequestHeader、UserData 三个 ThreadLocal，并调用 `MDC.clear()`（清空**全部** MDC） |

`UserDataManager` 以 `required=false` 注入。没有 redis 登录缓存（`easyfk.config.login.cache-type=redis`）时只能解析 JWT，`UserDataContext` 始终为空。

---

## 3. web-common：公共配置与常量

`WebCommonConfig` 只启用下面三个配置类。

**拦截 `easyfk.config.web.intercept`**

| 属性 | 默认值 | 是否生效 |
|---|---|---|
| `exclude-paths` | null | 生效：prd 拦截器的排除路径（Ant 匹配） |
| `auth-type` | `0` | 生效：`0` 只校验登录；非 0 时对 `@AuthResource` 额外调用 `checkAuth` |
| `require-auth-by-default` | false | 生效：未标注注解的接口也要求登录 |
| `refresh-user-auth` | false | 生效：prd 与 micro 过滤器每个请求都刷新用户 token |
| `open-gateway-interceptor` | false | 只在 gateway 中使用 |
| `custom-gateway-filter` | false | 只在 gateway 中使用（见 gateway 文档） |

`verify-param`、`custom-local-interceptor`、`custom-local-filter` 已删除（原为无引用的占位属性）。

**安全 `easyfk.config.web.security`**（只在 prd 中使用）

| 属性 | 默认值 | 说明 |
|---|---|---|
| `open` | false | 签名加防重放的总开关 |
| `ignore-uri` | null | 对去掉 contextPath 的路径做精确或 Ant 匹配；静态资源（见复查 #11）也会自动跳过 |
| `timeout` | 150s | 时间戳新鲜度窗口（服务端时间与 Timestamp 之差的绝对值不超过 timeout）；nonce TTL 为 **2×timeout**，覆盖整个可接受期 |
| `sign-key` | `mcst_sign_reset` | 生产必须覆盖 |
| `sign-key-dynamic` | false | 为 true 时从缓存 `Security_Dynamic::Security_Dynamic_Sign_Key` 读取密钥（需由业务自行写入） |
| `sign-version` | `v1` | `v1`：同时接受 v1/v2 请求（客户端 `Sign-Version` 头决定）；`v2`：拒绝 v1 请求 |

`key-time-to-live` 已删除（原为无引用属性）。

**跨域 `easyfk.config.web.cors`**（只在 prd 中使用）：`open=false`、`allow-credentials=false`、`cors-domain=*`、`allowed-header=*`、`allowed-method=*`、`path-pattern=/**`（逗号分隔多个 Ant 路径，每个路径注册同一份 CORS 配置）。默认值可直接开启 `open=true`（允许任意来源、不带凭据）；需要携带 Cookie 时设 `allow-credentials=true` 并把 `cors-domain` 配成具体域名或子域模式（如 `https://*.example.com`），否则启动报 `IllegalStateException` 并提示配置方法。

常量与工具：
- `ErrorRequest`：过滤器和切面使用的错误码枚举，共 25 个，例如 `SIGN_ERROR`、`EXPIRED`、`API_AGAIN`、`NONCE_*`、`API_CLIENT_*`、`REQUEST_AGAIN`、`IDEMPOTENT_ERROR`、`SYSTEM_BUSY`、`JWT_ERROR`。每个值带 `httpStatus`（见 §5.8），`ErrorRequest.ofCode(code)` 按 code 反查。`PARAM_SIGN_EMPTY`、`VERIFY_EMPTY`、`VERIFY_ERROR` 已删除。
- `HttpStatusResolver.resolveBusinessStatus(code)`：业务错误码到 HTTP 状态码的统一映射，prd/micro 异常处理器共用（见 §5.8）。
- `RequestConstant` 缓存命名空间：`Request_Security`、`Request_Token`、`Idempotent`、`Api_Auth`。
- `CheckIgnoreSecurityUriUtil`、`InterceptorExcludeUriUtil`：Ant 匹配工具。
- `JacksonTimeFormats`：带可选小数秒的时间序列化器。
- i18n `i18n/webMessages`（zh_CN/zh_TW/zh_HK/en_US/vi_VN）：`SystemErrorMsg`、`DateFormatErrorMsg`、`DateTimeFormatErrorMsg`、`TimeFormatErrorMsg`、`ServerBusyMsg`。

---

## 4. web-micro（网关后的微服务）

`MicroWebConfig` 注册以下 Bean，全部带 `@ConditionalOnMissingBean`：

| Bean | 说明 |
|---|---|
| `requestBaseFilter` | 读取 `TRACE_ID`、`Access-Token`、`Language` 请求头 → `doDataContext(traceId, intercept.refresh-user-auth)` → 放行 → finally 中 `clearContext()` |
| `microExceptionHandler` | 与 prd 相同的状态码约定（§5.8）：校验 400、业务 200（特定 code 除外）、未知 500 等 |
| `serializingObjectMapper` | NON_NULL、`yyyy-MM-dd HH:mm:ss`、忽略未知字段 |

要点：
- **不验签、不鉴权、不校验登录**，完全信任网关，所以 micro 服务不得直接暴露到公网。
- 沿用网关透传的 `TRACE_ID`；请求头缺失或格式非法（不匹配 `^[A-Za-z0-9\-_.]{1,64}$`）时**新生成** traceId。
- `easyfk.config.web.intercept.refresh-user-auth=true` 时每个请求刷新用户 token（需要 `UserDataManager`）。
- `@LoginResource` / `@AuthResource` 在 micro 中不生效，权限由网关负责。

micro 实际读取的配置只有：`easyfk.config.web.jwt.*`（含 `allowed-algorithms`，经 web-base `JwtManager`）、`easyfk.config.web.intercept.refresh-user-auth`、`easyfk.config.login.*`（经 authority 的 `UserDataManager`）。`easyfk.config.web.security.*`（含 `sign-version`）、`easyfk.config.web.cors.*`、`intercept.exclude-paths/auth-type/require-auth-by-default`、`easyfk.config.web.prd.*`、`easyfk.config.web.api-auth.*` 在 micro 中**均不生效**（这些能力由网关或 prd 提供），配置了也不会报错。

---

## 5. web-prd（直接对外服务）

### 5.1 自动配置与开关

所有 Bean 都在 `PrdWebConfig` 中注册，它通过 `@ImportAutoConfiguration` 引入 `ControllerAspectConfigure`。

| 能力 | Bean | 开关（缺省值） |
|---|---|---|
| 时间参数转换 | `Date/LocalDate/LocalDateTime/LocalTime` Converter | 无条件 |
| 本地权限拦截器 | `localInterceptor` + `apiInterceptorRegister`（`/**`，排除 `exclude-paths`） | `easyfk.config.web.prd.open-interceptor`（true） |
| 请求前置过滤器 | `requestBaseFilter` | `easyfk.config.web.prd.open-filter`（true） |
| 表单防重 | `requestTokenAspect` + `requestTokenAdvisor`（`@RequestToken`） | `easyfk.config.web.prd.open-request-token`（true） |
| 接口幂等 | `idempotentAspect` + `idempotentAdvisor`（`@Idempotent`） | `easyfk.config.web.prd.open-idempotent`（true） |
| 安全响应头 | `securityHeadersFilter` | `easyfk.config.web.prd.security-headers`（true） |
| API 调用方鉴权 | `apiClientStore`（`PropertiesApiClientStore`）+ `apiAuthFilterRegistration`（`HIGHEST_PRECEDENCE + 1`，`/*`） | `easyfk.config.web.api-auth.open`（false） |
| CORS | `myCorsFilter`（`CorsFilter` 子类，`Ordered.HIGHEST_PRECEDENCE`，最先执行） | `easyfk.config.web.cors.open`（false） |
| 资源初始化 | `startedCallback`（`InitResourceRunner`） | `easyfk.config.resource.init.open`（false） |
| Controller 切面 | `controllerInterceptorAdvisor` + `controllerAspect` | `easyfk.config.aspect.controller.open`（true） |
| 异常处理 / ObjectMapper | `prdExceptionHandler` / `serializingObjectMapper` | `@ConditionalOnMissingBean` |

`PrdWebProperties`（`easyfk.config.web.prd`）声明 `open-interceptor`、`open-filter`、`open-request-token`、`open-idempotent`、`security-headers`（均默认 true），用于生成配置元数据；实际开关由上表的 `@ConditionalOnProperty` 读取。`pic-code-cache-name`、`code-time-to-live` 已删除（原为无引用属性）。

### 5.2 请求处理链

```
CorsFilter（cors.open=true，HIGHEST_PRECEDENCE，预检请求在此直接应答）
ApiAuthFilter（api-auth.open=true，HIGHEST_PRECEDENCE + 1）
  └ App-Id → 调用方存在且启用 → allowed-uris(Ant) → Api-Timestamp(必填+新鲜度) → Api-Nonce(必填, 8~64位)
    → Api-Body 与实际 body 的 SHA-256 比对（仅当 body 被缓存）→ Api-Sign 校验 → setIfAbsent("ApiAuth:{appId}:{nonce}", TTL=2×timeout)
RequestBaseFilter
  ├ TRACE 方法 → 405；静态资源（/static/ 前缀或静态后缀）→ 直接放行
  ├ createTraceId()（总是新建，不读取 TRACE_ID 头）
  ├ 读取 Access-Token/Language/Reset-Sign/Timestamp/Request-Token/Request-Nonce/Device-No/Client-Type
  ├ doDataContext(intercept.refresh-user-auth)
  ├ security.open=true 时：ignore-uri → nonce → Reset-Sign → 版本降级检查 → Timestamp(必填+新鲜度) → 签名 → setIfAbsent(nonce, TTL=2×timeout)
  └ finally clearContext()
SecurityHeadersFilter
LocalInterceptor（HandlerInterceptor）
ControllerAspect → RequestTokenAspect / IdempotentAspect → Controller
```

过滤器拒绝请求时通过 `FailRequestUtil` 写出 JSON（`ResponseResult`，code 取自 `ErrorRequest`），HTTP 状态码取 `ErrorRequest.httpStatus`（见 §5.8）。不再写死 `Access-Control-Allow-Origin: *`，跨域头由最先执行的 CorsFilter 负责。

### 5.3 接口签名（`security.open=true`）

| 版本 | 触发方式 | 签名原文 | 算法 |
|---|---|---|---|
| v1（默认） | 不传 `Sign-Version` 头 | `Request-Nonce={nonce}&Timestamp={ts}&Key={signKey}` | MD5，结果放在 `Reset-Sign` |
| v2 | 请求头 `Sign-Version: v2` | `{METHOD}\n{规范URI}\n{Sign-Body}\n{nonce}\n{ts}` | HMAC-SHA256(signKey)，十六进制，比较不区分大小写 |

- **规范 URI**（v2 签名与 API 鉴权共用，`RequestUtil.getCanonicalUri`）：`request.getRequestURI()` 去掉 contextPath 后的原始路径（不解码），若 `request.getQueryString()` 非空再追加 `?` + 原始 query string（不解码、不排序、原样）。例：contextPath=`/app`，请求 `GET /app/order/list?page=1&size=20` → `/order/list?page=1&size=20`；无 query 时为 `/order/list`。客户端必须用实际发出的 query 字节串签名。
- `Timestamp` **必填**（v1 与 v2 都是），缺失返回 `TIMESTAMP_EMPTY`，非数字返回 `TIMESTAMP_ERROR`；服务端时间与 ts 之差的绝对值超过 `timeout` 返回 `EXPIRED`，秒级和毫秒级都兼容。签名原文中的 ts 为解析后的数值字符串。
- body 只在非 GET/HEAD、非 multipart、非表单提交且不超过 2MB 时缓存并比对；否则直接信任客户端上报的摘要。
- nonce 键为全局的 `Request_Security::{nonce}`，TTL 为 **2×timeout**（时间戳在 [now-timeout, now+timeout] 内都被接受，nonce 必须存活到整个可接受期结束）。缓存异常时拒绝请求（`SYSTEM_BUSY`）。
- `ignore-uri` 按去掉 contextPath 的路径匹配（与 API 鉴权的 `ignore-uri` 口径一致）。
- `Param-Sign` 请求头不再读取（参数防篡改由 v2 签名覆盖）。

### 5.4 API 调用方鉴权（`api-auth.open=true`）

```yaml
easyfk.config.web.api-auth:
  open: true
  timeout: 150s
  ignore-uri: [/health]
  clients:
    - app-id: partner-app
      secret: "xxx"
      enabled: true
      allowed-uris: [/order/**]   # 为空表示全部放行
```

签名：`ApiSignUtil.sign(appId, timestamp, nonce, METHOD, 规范URI, bodyHash, secret)`，签名原文为 `App-Id={appId}&Timestamp={Api-Timestamp 原始字符串}&Nonce={nonce}&Method={METHOD}&Uri={规范URI}&Body={bodyHash}`，规范 URI 与 §5.3 相同（去 contextPath + `?原始query`），算法 HMAC-SHA256，结果为小写十六进制，服务端用常量时间比较（客户端签名大小写不敏感）。`Api-Timestamp` **必填**并校验新鲜度（缺失或非数字 `API_TIMESTAMP_ERROR`，超窗 `API_EXPIRED`），nonce TTL 为 2×timeout。`allowed-uris` / `ignore-uri` 仍按不含 query 的路径匹配。如需从库表加载调用方，自定义 `IApiClientStore` Bean 即可覆盖默认实现。开启后，除 `ignore-uri` 和静态资源外**所有接口**都要求调用方签名，前端也包括在内。

### 5.5 登录与权限：LocalInterceptor

- 命中 `exclude-paths` → 放行。
- `@LoginResource` 只识别方法级；`@AuthResource` 方法级优先，其次控制器类级（类级注解对该控制器所有方法生效）。无注解且 `require-auth-by-default=false` → 放行。
- `UserDataContext` 为空 → HTTP 401 + `UN_LOGIN`（"您未登录或登录超时"）。
- 有 `@AuthResource` 时：`UserDataManager` 通过 `ObjectProvider` 获取，缺失时 HTTP 500 + `ERROR`（"权限服务未配置"，并打 ERROR 日志）；取 `getUserAuth(loginToken)`，为空返回 401 `UN_LOGIN`；`auth-type≠0` 时再执行 `checkAuth(loginToken, url)`，结果非 `success=true, data=true` 时返回 HTTP 403 + `UN_AUTH`（优先使用 `unPassMsg`）。
- 只有 `@LoginResource`，或只靠 `require-auth-by-default` 时，只校验登录。
- 拦截结果以 JSON（`RRBuilder.buildFailedBody`）返回，状态码如上。`WebInterceptorRegister` 通过 `ObjectProvider` 获取 `LocalInterceptor`，缺失时启动失败。
- `require-auth-by-default=true` 时，登录、注册、回调等匿名接口必须写进 `exclude-paths`。

### 5.6 @RequestToken 与 @Idempotent

```java
@PostMapping("/payment/create")
@Idempotent(key = "#p0.orderNo", ttlSeconds = 60, onDuplicateFail = true)
public ResponseResult<PaymentVO> create(@RequestBody PaymentCreateVO p) { ... }
```

- `@Idempotent`：缓存键 `Idempotent::Idempotent:{userId|anonymous}:{SpEL值或 类名.方法名}`。执行前 `setIfAbsent`；成功后按 ttl 续期；抛异常时删除键，允许重试。重复请求抛 `IdempotentException`（`IDEMPOTENT_ERROR`），或在 `onDuplicateFail=false` 时返回 null（基本类型返回值会抛异常）。SpEL 变量有 `#p0..#pN` 和 `#args`。
- `@RequestToken(verify)`：先由 `RequestTokenUtil.issue(cacheService, userId, ttlSeconds)` 下发令牌（写入 `Request_Token::{userId|anonymous}:{token}`），提交时读取 `Request-Token` 头，缺失报 `REQUEST_TOKEN_EMPTY`；对该键执行 `removeKey`，删除成功才算首次消费，未签发或已消费报 `REQUEST_AGAIN`。
- 两个切面都在缓存异常时拒绝请求（`SYSTEM_BUSY`），异常都由 `PrdExceptionHandler` 按 `BusinessException` 处理，状态码按 §5.8：`REQUEST_TOKEN_EMPTY` 400、`REQUEST_AGAIN`/`IDEMPOTENT_ERROR` 200、`SYSTEM_BUSY` 503。

### 5.7 其他组件

- **ControllerAspect**：切点 `execution(public * com.mcst..*.controller..*.*(..))`，可用 `aspect.controller.pointcut` 以 OR 追加。对参数中的 `SearchRequest` 执行 `SqlGuardUtil.validateSearchRequest`，校验字段名 `^[A-Za-z][A-Za-z0-9_.]{0,127}$`、排序字段、关键词（不超过 64 字符且不含 `' ; -- /* */` 和 DDL/DML 关键字）。**只有 debug 级别开启时**才序列化参数：跳过 `ServletRequest/ServletResponse/HttpSession/MultipartFile/MultipartRequest/InputStreamSource/InputStream/OutputStream/Reader/Writer/Errors` 类型参数，字段名（不区分大小写）包含 `password/passwd/pwd/token/secret/credential` 的值替换为 `******`，序列化失败不影响请求。**业务包名不是 `com.mcst` 时必须配置 pointcut**，否则 SQL 入口校验不生效。
- **PrdExceptionHandler**：状态码约定见 §5.8；日期反序列化错误（`HttpMessageNotReadableException`）返回 400 + 对应 i18n 消息，接口不存在返回 404。
- **SecurityHeadersFilter**：补齐 `X-Content-Type-Options: nosniff`、`X-Frame-Options: SAMEORIGIN`、`Referrer-Policy: strict-origin-when-cross-origin`、`X-XSS-Protection: 0`，已存在的响应头不覆盖。
- **CORS**：默认 `allow-credentials=false`、`cors-domain=*`，`cors.open=true` 即可启动。`allow-credentials=true` 时 `cors-domain` 为空或含 `*` 项会**启动失败**并提示配置具体域名（子域模式 `https://*.example.com` 允许）。`maxAge` 为 3600，多个值用逗号分隔；`path-pattern` 决定注册路径。过滤器以 `HIGHEST_PRECEDENCE` 执行，保证预检请求不被 ApiAuth/签名过滤器拦截，且拒绝响应带正确的跨域头。
- **InitResourceRunner**（`resource.init.open=true`）：扫描 `@ResourceController` Bean。`group=default` 表示全部，否则按逗号拆分后**精确匹配**组名。为类生成菜单资源，为带 `@AuthResource` 的方法（或类级 `@AuthResource` 覆盖的方法）生成权限资源；`normal=true` 时其余方法生成 normal 资源（有 `@LoginResource` 时 level=1）。URL 只取 `value()[0]`，含 `*` 或 `{` 的路径跳过。结果逐条调用 `IAuthResourceApi.save`；该 Bean 缺失时打 WARN 并跳过。
- **工具类**：`RequestUtil.getRequestUrl`（去掉 contextPath）、`ClientIpUtil.getClientIp`（取 XFF 等请求头的第一个 IP，可被伪造，不要用于安全判断）、`StaticUriUtil`、`FailRequestUtil`、`BodyCachingRequestWrapper`、`ApiSignUtil`、`RequestTokenUtil`、`SqlGuardUtil`。
- **VO**：`LoginRequestVO`、`SiteLoginSuccessVO`、`RegistryRequestVO`。

### 5.8 HTTP 状态码约定（prd 与 micro 一致）

| 场景 | HTTP 状态码 | 响应体 code |
|---|---|---|
| 参数校验失败（`BindException`/`MethodArgumentNotValidException`/`ValidationException`/`HandlerMethodValidationException`）、缺参数/类型不匹配/请求体不可解析 | 400 | `PARAM_ERROR` |
| 过滤器请求头缺失或格式错误（`HEARD_EMPTY`、`NONCE_*`、`RESET_SIGN_EMPTY`、`TIMESTAMP_*`、`API_TIMESTAMP_ERROR`、`API_NONCE_ERROR`、`REQUEST_TOKEN_EMPTY`） | 400 | 对应 `ErrorRequest` |
| 未认证：未登录（`UN_LOGIN`/`UNLOGIN`）、`JWT_ERROR`、签名/过期/重放（`SIGN_ERROR`、`EXPIRED`、`API_AGAIN`）、调用方缺失/无效/签名错误/过期 | 401 | 对应 code |
| 无权限（`UN_AUTH`/`UNAUTH`、`API_UNAUTHORIZED`、`API_CLIENT_DISABLED`） | 403 | 对应 code |
| 接口不存在 / 方法不支持 | 404 / 405 | `ERROR` |
| `BusinessException` | 200 | 异常的 errorCode；但 code 命中 `ErrorRequest` 或为 `UN_LOGIN`/`UN_AUTH`/`PARAM_ERROR`/`BUSYNESS` 时按上表取 401/403/400/503 |
| `REQUEST_AGAIN`、`IDEMPOTENT_ERROR` | 200 | 对应 code |
| 安全依赖不可用（`SYSTEM_BUSY`、`DYNAMIC_SIGN_KEY_TIMEOUT`）、`SocketTimeoutException`（`BUSYNESS`） | 503 | 对应 code |
| 其他异常 | 500 | `ERROR` + i18n `SystemErrorMsg` |

客户端仍应以响应体 `code` 为准判断业务结果；状态码用于网关、监控和浏览器区分失败类别。

---

## 6. 生成代码时的规则

**Do**
- 对外服务引 `web-prd`，网关后的服务引 `web-micro`，二者只引一个。
- 生产环境必须覆盖 `jwt.secret`、`jwt.salt`、`security.sign-key`；开启 CORS 时配置具体 `cors-domain`（需要 Cookie 时同时设 `allow-credentials: true`）。
- 需要登录的接口在**方法上**标 `@LoginResource`，需要权限的接口在方法或控制器类上标 `@AuthResource`（同时设置 `auth-type: 1`）。推荐开启 `require-auth-by-default: true`，并把匿名接口写进 `exclude-paths`。
- 资金、订单类写接口用 `@Idempotent(key = "#p0.业务单号")`，并在数据库层加唯一约束兜底。
- 业务包名不是 `com.mcst` 时配置 `easyfk.config.aspect.controller.pointcut`。
- 开启签名时客户端必须携带 `Timestamp`（缺失直接拒绝），推荐服务端配置 `sign-version: v2`，客户端使用 `Sign-Version: v2` + `Sign-Body`，并按 §5.3 的规范 URI（去 contextPath + `?原始query`）签名。
- 客户端按 HTTP 状态码区分失败类别（401 重新登录 / 403 无权限 / 400 参数错误），按响应体 `code` 判断业务结果。
- 第三方调用开启 `api-auth`，`secret` 只放在服务端；动态吊销调用方需自定义 `IApiClientStore`。
- 在 Controller 中通过 `UserDataContext.getUserData()` 获取当前用户；在异步线程中需要自行透传上下文。

**Don't**
- 不要在类上标 `@LoginResource` 并期望它保护整个控制器（`@LoginResource` 只识别方法级；类级保护用 `@AuthResource` 或 `require-auth-by-default`）。
- 不要再配置 `verify-param`、`key-time-to-live`、`pic-code-*`、`custom-local-*`，也不要依赖 `Param-Sign` 头（均已删除）。
- 不要在 micro 中配置 security / cors / exclude-paths 并期望生效（见 §4）。
- 不要把 web-micro 服务暴露到公网，也不要在 micro 中依赖登录或权限注解。
- 不要往 JWT 里放敏感信息；不要用 `ClientIpUtil` 的结果做风控或白名单判断。
- 不要在签名原文中对 query 重新编码或排序：规范 URI 使用原始 query string。
- 不要在 `MDC` 中放请求外的长期数据：`clearContext` 会 `MDC.clear()`。

---

## 7. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | prd 手册 §16、框架手册 §3.4 | 先调用 `RequestTokenUtil.issue` 下发令牌，再在提交接口上用 `@RequestToken` 校验，令牌只能消费一次 | `issue` 已经用 `cacheObject` 写入 `{userId}:{token}`，切面又对同一个键执行 `setIfAbsent`，**服务端下发的令牌第一次提交就返回 `REQUEST_AGAIN`**；客户端自己编造的随机串反而能通过一次。逻辑 bug（按"存在即消费"应改为原子删除 / getAndDelete） **已修复**：切面改为对签发键执行 `removeKey`，删除成功才算首次消费，未签发或已消费的令牌报 `REQUEST_AGAIN`。 |
| 2 | prd 手册 §4.4 / §7.2、技术特点 | `sign-version=v2` 启用服务端 v2 校验 | `SecurityProperties.signVersion` 全框架无引用，版本完全由客户端 `Sign-Version` 头决定（缺省 v1）。即便服务端"配置"为 v2，攻击者也可以降级到 MD5 v1，且 v1 不绑定 URI/body **已修复**：服务端 `sign-version=v2` 时拒绝 v1 请求（`SIGN_ERROR`）；Timestamp 现已对所有版本必填（见 #4）。 |
| 3 | prd 手册 §8、技术特点 §150 | `@AuthResource` 支持类级注解，对整个控制器生效 | `LocalInterceptor` 用 `handlerMethod.hasMethodAnnotation` 判断，只看方法。类级注解被忽略，接口会被**匿名放行**（`require-auth-by-default=false` 时）。`InitResourceRunner` 也只处理方法级注解 **已修复**：`LocalInterceptor` 与 `InitResourceRunner` 均识别控制器类级 `@AuthResource`（方法级优先）。 |
| 4 | prd 手册 §7.2 / §7.3 | 时间戳可选，nonce 原子防重放 | 不传 `Timestamp` 时跳过新鲜度校验，而 nonce 只缓存 `timeout`（150s）。**150 秒后同一请求可以原样重放**。API 鉴权的 `Api-Timestamp` 存在同样问题 **已修复**：签名 v1/v2 的 `Timestamp` 与 API 鉴权的 `Api-Timestamp` 均必填并校验新鲜度窗口 `timeout`，nonce TTL 改为 2×timeout，覆盖整个可接受时间范围。 |
| 5 | prd 手册 §13.4 | 超过 2MB 的请求体标记溢出，跳过摘要比对 | 溢出时 `body` 被置为空数组，而包装后的请求仍传给下游，**Controller 读到的是空 body**。开启 `security.open` 或 `api-auth.open` 后，大于 2MB 的 JSON 请求会丢失数据 **已修复**：溢出时下游先回放已预读的前缀再续读原始流，Controller 读到完整 body（仍跳过摘要比对）。 |
| 6 | prd 手册 §4.4 | cors 默认值 `allow-credentials=true`、`cors-domain=*` | 这组默认值在 `cors.open=true` 时直接触发 `IllegalStateException`，启动失败，必须显式配置域名（手册 §15 有说明，但默认值表未提示） **已修复**：`allow-credentials` 默认改为 false，默认值下 `cors.open=true` 可直接启动；`allow-credentials=true` 且域名为空或含 `*` 时启动失败并给出配置提示；CORS 过滤器改为最先执行。 |
| 7 | prd 手册 §4.1 | `PrdWebProperties` 含 `open-filter`；`pic-code-cache-name`、`code-time-to-live` 有效 | 类中没有 `open-filter`（只在 `@ConditionalOnProperty` 中使用）；`pic-code-*`、`key-time-to-live`、`verify-param`、`cors.path-pattern`、`custom-local-*` 均无引用 **已修复**：删除 `pic-code-*`、`code-time-to-live`、`key-time-to-live`、`verify-param`、`custom-local-*`；`PrdWebProperties` 补齐 `open-filter`、`open-request-token`、`open-idempotent`、`security-headers`；`cors.path-pattern` 用于注册 CORS 路径。 |
| 8 | prd 手册 §5 配置示例 | 示例 YAML | `web.prd` 键出现了两次，按 YAML 规则后者覆盖前者（或解析报错），`open-interceptor`、`open-filter` 等会丢失 |
| 9 | prd 手册 §6.1 | Bean 名 `apiAuthFilter` | 实际是 `FilterRegistrationBean`，Bean 名为 `apiAuthFilterRegistration` |
| 10 | prd 手册 §7.2 / §20.3 | v2 签名和 API 鉴权都"绑定 URI" | v2 用 `getRequestURI()`（含 contextPath），API 鉴权用去掉 contextPath 的 URI，两者口径不一致；且都不含 query string，GET 参数不受签名保护 **已修复**：两者统一使用规范 URI（去 contextPath 的原始路径 + 有 query 时 `?` + 原始 query string），query 参数受签名保护。 |
| 11 | prd 手册 §7 | 静态资源跳过全部逻辑 | 判断依据是 URL 以 `/static/` 开头或以 core `CharacterConstant.STATIC_URL` 中的后缀结尾，后缀包括 `.json`、`.xml`、`.txt`、`.html`，以及**不带点的 `htm`**。凡是以这些后缀结尾的业务路径（例如 `/api/export.json`、路径变量 `/file/{name}`、任何以 `htm` 结尾的路径）都会**绕过 API 鉴权、签名防重放和 TraceId/上下文还原**（拦截器仍执行，但此时没有 UserData） **已修复**：`StaticUriUtil` 对含 `;`、`..`、`%`、`\` 的 URL 一律不视为静态资源，后缀匹配不区分大小写；`STATIC_URL` 去掉了 `.json/.xml/.txt` 与不带点的 `htm`，只保留 css/js/图片/音视频/html/htm 等带点后缀。 |
| 12 | micro 手册 §6 | 过滤器中"（可选）异步刷新用户权限缓存" | micro 调用 `doDataContext(traceId)`，内部固定传 `false`，**从不刷新**；没有 TRACE_ID 头时也不会生成 traceId **已修复**：micro 调用 `doDataContext(traceId, intercept.refresh-user-auth)`，按配置刷新 token；TRACE_ID 缺失或格式非法时生成新 traceId。 |
| 13 | micro 手册 §4 | 配置表 | 缺少 `allowed-algorithms`、`require-auth-by-default`、`sign-version`；security、cors 配置对 micro 无效（micro 不读取） **已修复**：micro 现读取 `intercept.refresh-user-auth`；§4 明确列出 micro 生效的配置（jwt 含 `allowed-algorithms`、`refresh-user-auth`、`login.*`）与不生效的配置（security 含 `sign-version`、cors、`exclude-paths`/`auth-type`/`require-auth-by-default`、prd、api-auth）。 |
| 14 | prd/micro 手册 §7/§10 | 异常处理 | micro 对所有异常（包括校验异常、业务异常）都返回 HTTP 500；prd 对业务异常和兜底异常返回 HTTP 200，校验异常返回 400，两者状态码约定不同。过滤器和拦截器拒绝时都是 HTTP 200 **已修复**：prd 与 micro 统一为 §5.8 的约定（校验 400、未认证 401、无权限 403、业务 200、依赖不可用 503、未知 500），过滤器按 `ErrorRequest.httpStatus`、拦截器按 401/403 写出状态码。 |
| 15 | prd 手册 §11 | 按组过滤资源，多组用逗号分隔 | 实现为 `group.contains(controller.group())` 子串匹配（`group=admin` 也会匹配到 `ad` 组）。`IAuthResourceApi` 以 `required=false` 注入却直接调用，缺失时 NPE；类上没有 `@RequestMapping` 而方法 URL 以 `/` 结尾时也会 NPE **已修复**：组名按逗号拆分后精确匹配；`IAuthResourceApi` 缺失时 WARN 并跳过；类无 `@RequestMapping` 时 classUrl 按空串处理。 |
| 16 | 代码细节 | — | `LocalInterceptor`、`WebInterceptorRegister` 对 `@Lazy` 代理做的判空永远为非空，`userDataManager` 缺失时要到调用时才报错；`ControllerAspect` 无论日志级别都会执行 `JSON.toJSONString(args)`，有性能开销且可能把敏感参数写进日志 **已修复**：两处改用 `ObjectProvider` 真实判空（缺 `UserDataManager` 时 `@AuthResource` 接口返回 500 并记 ERROR，缺 `LocalInterceptor` 时启动失败）；`ControllerAspect` 仅在 debug 开启时序列化参数，跳过 Servlet/文件/流类参数并对 password/token/secret 等字段脱敏。 |
| 17 | `web安全与幂等审查报告.md` | Request-Token、Param-Sign、verifyParam 只定义未实现 | 现状：`@RequestToken` 已实现（但有 #1 的问题）；Param-Sign 只读入 header，没有校验（v2 签名替代了这部分能力）；verifyParam 仍是占位 **已修复**：删除 prd 对 `Param-Sign` 的读取、`verify-param` 属性及 `PARAM_SIGN_EMPTY`/`VERIFY_*` 错误码，参数防篡改统一由 v2 签名（含 query 与 body 摘要）承担。 |
