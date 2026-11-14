# easyfk-web/web-prd 开发文档

## 1. 模块概述

`web-prd` 是 EasyFK 框架为**独立部署（非微服务/无网关）**的 Web 应用提供的完整 Web 基础设施模块。与 `web-micro`（网关后端微服务）不同，`web-prd` 内置了完整的安全防护链（签名验证、防重放攻击）、本地权限拦截器、Controller 层 AOP 切面、CORS 跨域过滤器、时间参数转换器、权限资源自动初始化等能力，适用于面向前端直接访问的独立应用。

---

## 2. 依赖关系

```groovy
dependencies {
    api project(':easyfk-web:web-simple')
    api project(':easyfk-web:web-common')
}
```

```
web-prd
├── web-simple
│   ├── spring-boot-starter-web（排除 Tomcat + Logging）
│   ├── spring-boot-starter-undertow
│   └── easyfk-core
└── web-common
    ├── web-base
    │   ├── easyfk-authority
    │   └── easyfk-core
    ├── easyfk-core
    └── spring-web
```

---

## 3. 包结构

```
web-prd/
├── config/
│   ├── PrdWebConfig.java               # 核心自动配置
│   ├── WebInterceptorRegister.java      # 拦截器注册
│   └── ControllerAspectConfigure.java   # Controller AOP 配置
├── api/
│   ├── IApiClientStore.java             # API 调用方存储接口（可自定义实现）
│   └── PropertiesApiClientStore.java    # 配置版调用方存储
├── filter/
│   ├── RequestBaseFilter.java           # 请求前置过滤器（含安全链）
│   ├── ApiAuthFilter.java               # API 调用鉴权过滤器（OpenAPI 风格）
│   └── SecurityHeadersFilter.java       # 安全响应头过滤器
├── interceptor/
│   └── LocalInterceptor.java            # 本地权限拦截器
├── annotation/
│   ├── RequestToken.java                # 表单重复提交注解
│   └── Idempotent.java                  # 接口幂等注解
├── aspect/
│   ├── ControllerAspect.java            # Controller 切面（含 SQL 注入入口校验）
│   ├── RequestTokenAspect.java          # 表单重复提交切面
│   └── IdempotentAspect.java            # 接口幂等切面
├── exception/
│   ├── PrdExceptionHandler.java         # 全局异常处理
│   ├── DuplicateSubmitException.java    # 重复提交异常（REQUEST_AGAIN）
│   └── IdempotentException.java         # 幂等拦截异常（IDEMPOTENT_ERROR）
├── converter/
│   ├── DateConverter.java               # String → Date
│   ├── LocalDateConverter.java          # String → LocalDate
│   ├── LocalDateTimeConverter.java      # String → LocalDateTime
│   └── LocalTimeConverter.java          # String → LocalTime
├── runner/
│   └── InitResourceRunner.java          # 权限资源自动初始化
├── properties/
│   ├── PrdWebProperties.java            # PRD Web 配置
│   ├── ResourceInitProperties.java      # 资源初始化配置
│   └── ControllerAspectProperties.java  # 切面配置
├── util/
│   ├── FailRequestUtil.java             # 失败响应工具
│   ├── RequestUtil.java                 # 请求工具（URL/Ajax/微信检测）
│   ├── StaticUriUtil.java               # 静态资源判断
│   ├── BodyCachingRequestWrapper.java   # 请求体缓存包装（v2 签名摘要计算）
│   ├── RequestTokenUtil.java            # Request-Token 一次性令牌下发
│   ├── SqlGuardUtil.java                # SQL 注入入口校验（字段/关键词白名单）
│   └── ApiSignUtil.java                 # API 调用鉴权签名工具（HMAC-SHA256）
└── vo/
    ├── LoginRequestVO.java              # 登录请求 VO
    ├── SiteLoginSuccessVO.java          # 登录成功响应 VO
    └── RegistryRequestVO.java           # 注册请求 VO
```

---

## 4. 配置属性

### 4.1 PrdWebProperties

配置前缀：`easyfk.config.web.prd`

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `open-interceptor` | Boolean | `true` | 是否开启本地拦截器 |
| `open-filter` | Boolean | `true` | 是否开启请求前置过滤器 |
| `pic-code-cache-name` | String | `PicCodes` | 图片验证码缓存名称 |
| `code-time-to-live` | Duration | 5min | 图片验证码有效期 |

### 4.2 ResourceInitProperties

配置前缀：`easyfk.config.resource.init`

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `open` | Boolean | `false` | 是否启用权限资源自动初始化 |
| `group` | String | `default` | 资源组名称（`default` 表示全部，多个逗号分隔） |
| `normal` | Boolean | `false` | 是否生成非权限资源（`@LoginResource` 标记的） |

### 4.3 ControllerAspectProperties

配置前缀：`easyfk.config.aspect.controller`

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `open` | Boolean | `true` | 是否开启 Controller 切面 |
| `pointcut` | String | null | 自定义切面表达式（与内置表达式 OR 合并） |

### 4.4 继承的配置

来自 `web-common`：

| 配置前缀 | 说明 |
|---|---|
| `easyfk.config.web.security.*` | 安全配置（签名、防重放、时间窗） |
| `easyfk.config.web.intercept.*` | 拦截器配置 |
| `easyfk.config.web.cors.*` | 跨域配置 |
| `easyfk.config.web.jwt.*` | JWT 配置 |

**JWT 配置（web-base）：`easyfk.config.web.jwt`**

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `secret` | String | 框架默认密钥 | 签名密钥，生产环境务必覆盖 |
| `salt` | String | 框架默认盐值 | 签名盐值，与 `secret` 经 HMAC-SHA256 派生实际签名密钥，生产环境务必覆盖；修改后存量 token 失效 |
| `expires-second` | Integer | `10800` | Token 有效期（秒），默认 3 小时；`<=0` 按默认值处理。不含 `exp` 的 token 一律拒绝 |
| `allowed-algorithms` | String | `HS256` | 签名算法白名单（逗号分隔，不区分大小写），防止 alg=none 算法混淆攻击 |

**安全配置（web-common）：`easyfk.config.web.security`**

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `open` | boolean | `false` | 是否开启接口安全控制（签名 + 防重放） |
| `ignore-uri` | List\<String\> | null | 忽略安全校验的 URI（精确或 Ant 模式，如 `/login`、`/login/**`） |
| `timeout` | Duration | `150s` | 时间戳新鲜度窗口与 Nonce 防重放 TTL |
| `sign-key` | String | `mcst_sign_reset` | 生成验签的密钥（生产环境务必覆盖） |
| `sign-key-dynamic` | boolean | `false` | 验签密钥是否动态（从缓存获取） |
| `sign-version` | String | `v1` | 签名版本：`v1`=MD5（兼容存量）；`v2`=HMAC-SHA256（绑定 Method/URI/请求体摘要） |
| `key-time-to-live` | Duration | `10min` | 动态密钥缓存存活时间 |

**重复提交与幂等开关（web-prd）：`easyfk.config.web.prd`**

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `open-request-token` | Boolean | `true` | 是否启用 `@RequestToken` 表单重复提交切面 |
| `open-idempotent` | Boolean | `true` | 是否启用 `@Idempotent` 接口幂等切面 |
| `security-headers` | Boolean | `true` | 是否启用安全响应头过滤器（`security-headers`） |

**API 调用鉴权（web-prd）：`easyfk.config.web.api-auth`**

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `open` | Boolean | `false` | 是否开启 API 调用鉴权（OpenAPI 风格，调用方 App-Id + Secret 签名） |
| `timeout` | Duration | `150s` | 时间戳新鲜度窗口与 Nonce 防重放 TTL |
| `ignore-uri` | List\<String\> | null | 忽略 API 鉴权的 URI（精确或 Ant 模式） |
| `clients[].app-id` | String | - | 调用方标识 |
| `clients[].secret` | String | - | 调用方密钥（仅服务端持有） |
| `clients[].enabled` | Boolean | `true` | 调用方是否启用 |
| `clients[].allowed-uris` | List\<String\> | null | 该调用方允许访问的 URI（Ant 模式），为空表示全部 |

**拦截器配置（web-common）：`easyfk.config.web.intercept`**

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `exclude-paths` | List\<String\> | null | 拦截器排除的 URI（精确或 Ant 模式） |
| `auth-type` | Integer | `0` | 权限拦截等级：`0`=只检测登录，`1`=检测登录并校验权限 |
| `require-auth-by-default` | boolean | `false` | 未标注 `@LoginResource`/`@AuthResource` 的接口是否默认要求登录（开启后防止漏标导致接口匿名可访问） |
| `refresh-user-auth` | boolean | `false` | 是否刷新 UserAuth 缓存 |
| `open-gateway-interceptor` | boolean | `false` | 是否开启网关权限拦截（配合 easyfk-gateway 使用） |
| `verify-param` | boolean | `false` | 是否验证参数防篡改（v2 签名已覆盖该能力，此开关保留兼容） |
| `custom-local-interceptor` | boolean | `false` | 是否使用自定义本地拦截器 |
| `custom-local-filter` | boolean | `false` | 是否使用自定义本地过滤器 |
| `custom-gateway-filter` | boolean | `false` | 是否使用自定义网关过滤器 |

---

## 5. 配置示例

```yaml
easyfk:
  config:
    web:
      prd:
        open-interceptor: true
        open-filter: true
        pic-code-cache-name: PicCodes
        code-time-to-live: 5m
      security:
        open: true
        sign-key: "your-sign-key"
        sign-key-dynamic: false
        sign-version: v1          # v1=MD5 兼容存量；v2=HMAC-SHA256 推荐升级
        timeout: 150s
        ignore-uri:
          - /api/public
          - /health
      intercept:
        exclude-paths:
          - /api/login
          - /api/register
        auth-type: 1
        refresh-user-auth: true
      cors:
        open: true
        cors-domain: "https://yourdomain.com"
      jwt:
        secret: "your-jwt-secret"
        salt: "your-jwt-salt"
        expires-second: 10800
        allowed-algorithms: HS256
      api-auth:
        open: false                     # 默认关闭；开启后所有接口要求调用方鉴权
        timeout: 150s
        ignore-uri:
          - /health
        clients:
          - app-id: partner-app
            secret: "partner-secret-xxxx"
            allowed-uris:
              - /order/**
      prd:
        open-request-token: true
        open-idempotent: true
        security-headers: true
    aspect:
      controller:
        open: true
        pointcut: "execution(public * com.example..*.controller..*.*(..))"
    resource:
      init:
        open: true
        group: default
        normal: false
```

---

## 6. 自动配置

### 6.1 PrdWebConfig

注册的 Bean：

| Bean | 类型 | 条件 | 说明 |
|---|---|---|---|
| `dateConverter` | `Converter<String, Date>` | 无条件 | Date 参数转换 |
| `localDateConverter` | `Converter<String, LocalDate>` | 无条件 | LocalDate 参数转换 |
| `localDateTimeConverter` | `Converter<String, LocalDateTime>` | 无条件 | LocalDateTime 参数转换 |
| `localTimeConverter` | `Converter<String, LocalTime>` | 无条件 | LocalTime 参数转换 |
| `apiInterceptorRegister` | `WebInterceptorRegister` | `open-interceptor=true`（默认生效） | 拦截器注册 |
| `localInterceptor` | `LocalInterceptor` | `open-interceptor=true` | 本地权限拦截器 |
| `requestBaseFilter` | `RequestBaseFilter` | `open-filter=true`（默认生效） | 请求前置过滤器 |
| `apiAuthFilter` | `ApiAuthFilter` | `api-auth.open=true` | API 调用鉴权过滤器 |
| `apiClientStore` | `IApiClientStore` | `api-auth.open=true` | 配置版调用方存储 |
| `prdExceptionHandler` | `PrdExceptionHandler` | `@ConditionalOnMissingBean` | 全局异常处理 |
| `requestTokenAspect` | `RequestTokenAspect` | `open-request-token=true`（默认生效） | 表单重复提交切面 |
| `requestTokenAdvisor` | `DefaultPointcutAdvisor` | `open-request-token=true` | `@RequestToken` 注解切点 |
| `idempotentAspect` | `IdempotentAspect` | `open-idempotent=true`（默认生效） | 接口幂等切面 |
| `idempotentAdvisor` | `DefaultPointcutAdvisor` | `open-idempotent=true` | `@Idempotent` 注解切点 |
| `securityHeadersFilter` | `SecurityHeadersFilter` | `security-headers=true`（默认生效） | 安全响应头过滤器 |
| `serializingObjectMapper` | `ObjectMapper` | `@ConditionalOnMissingBean` | Jackson 全局配置 |
| `myCorsFilter` | `CorsFilter` | `cors.open=true` | CORS 跨域过滤器 |
| `startedCallback` | `InitResourceRunner` | `resource.init.open=true` | 权限资源初始化 |

### 6.2 ControllerAspectConfigure

| Bean | 类型 | 条件 | 说明 |
|---|---|---|---|
| `controllerInterceptorAdvisor` | `AspectJExpressionPointcutAdvisor` | `aspect.controller.open=true`（默认生效） | Controller AOP 切面 |
| `controllerAspect` | `ControllerAspect` | `@ConditionalOnMissingBean` | 方法拦截器 |

---

## 7. RequestBaseFilter（请求前置过滤器）

`web-prd` 的核心过滤器，继承 `OncePerRequestFilter`，包含完整的安全防护链：

> 过滤器顺序：当 `api-auth.open=true` 时，`ApiAuthFilter`（API 调用鉴权）以最高优先级**先于**本过滤器执行；本过滤器负责安全签名/防重放与 JWT 上下文。

```
HTTP 请求到达
    │
    ├─ TRACE 方法 → 返回 405（安全防护）
    │
    ├─ 静态资源（StaticUriUtil.isStaticUrl）
    │   └─ 直接 filterChain.doFilter()（跳过全部逻辑）
    │
    └─ 非静态请求
        │
        ├─ 1. createTraceId()（生成全链路追踪 ID）
        │
        ├─ 2. doLocalHeaderFilter()（提取请求头字段，accessToken 仅从 Header 读取）
        │      ├─ language / resetSign / paramSign
        │      ├─ timestamp / requestToken / accessToken
        │      ├─ requestNonce / deviceNo / clientType
        │      └─ → RequestHeaderContext（ThreadLocal）
        │
        ├─ 3. doDataContext()（JWT 解析 + 用户数据加载）
        │      └─ JWT 验签 + 过期校验 + 算法白名单（web-base JwtManager）
        │
        ├─ 4. doSecurityFilterMethod()（安全签名校验）
        │      ├─ 忽略白名单 URI → 放行
        │      ├─ 检查请求头完整性（headers/nonce/sign/timestamp）
        │      ├─ Nonce 格式校验（8~64 位 [A-Za-z0-9-_]）
        │      ├─ 时间戳新鲜度校验（|now - timestamp| <= timeout）
        │      ├─ 获取签名密钥（静态或动态）
        │      ├─ 签名验证（v1 MD5 / v2 HMAC-SHA256）
        │      └─ Nonce 原子占用（setIfAbsent，仅首次放行）
        │
        ├─ 5. filterChain.doFilter()
        │
        └─ finally: clearContext()
```

### 7.1 提取的请求头字段

| 字段 | 请求头名称 | 说明 |
|---|---|---|
| `accessToken` | `Access-Token` | 认证令牌（仅从 Header 读取，不再支持 URL 参数，避免 Token 泄漏到日志/Referer） |
| `language` | `Language` | 语言标识 |
| `resetSign` | `Reset-Sign` | 请求签名 |
| `paramSign` | `Param-Sign` | 参数签名 |
| `timestamp` | `Timestamp` | 时间戳 |
| `requestToken` | `Request-Token` | 请求令牌 |
| `requestNonce` | `Request-Nonce` | 防重放随机串 |
| `deviceNo` | `Device-No` | 设备编号 |
| `clientType` | `Client-Type` | 客户端类型 |
| `signVersion` | `Sign-Version` | 签名版本（`v1`/`v2`，仅在安全校验时读取，不入 RequestHeaders） |
| `signBody` | `Sign-Body` | 请求体 SHA-256 摘要（v2 签名使用） |

### 7.2 安全签名验证

**v1（默认，兼容存量客户端）：**

```
签名原文 = "Request-Nonce={nonce}&Timestamp={timestamp}&Key={signKey}"
签名结果 = MD5(签名原文)
验证条件 = 签名结果 == headers.getResetSign()
```

**v2（推荐升级，防篡改绑定请求）：**

```
签名原文 = method + "\n" + requestUri + "\n" + bodyHash + "\n" + nonce + "\n" + timestamp
bodyHash = SHA-256(请求体字节) 的十六进制串（GET/HEAD/无请求体按空串）
签名结果 = HMAC-SHA256(签名原文, signKey)
请求头    = Sign-Version: v2
          + Sign-Body: {bodyHash}
          + Reset-Sign: {签名结果}
          + Request-Nonce / Timestamp
```

- 通过 `easyfk.config.web.security.sign-version=v2` 启用服务端 v2 校验
- v2 将 Method、URI、请求体摘要纳入签名，可防参数篡改（等价于原 `Param-Sign` 能力）
- 服务端对可缓存请求体（JSON 等）会比对 `Sign-Body` 与实际请求体摘要；multipart/表单/超大请求体跳过比对，签名仍覆盖客户端上报的摘要
- 切换建议：先灰度客户端全部支持 v2 后再切服务端配置

**时间戳（可选）：**

- 客户端**不传** `Timestamp` 头：不校验新鲜度，签名原文中 `Timestamp` 按空串处理（兼容客户端时钟偏差场景）
- 客户端**传了** `Timestamp` 头：服务端校验格式与新鲜度（`|now - timestamp| <= timeout`），格式错误返回 `TIMESTAMP_ERROR`，超窗返回 `EXPIRED`
- 建议正常客户端始终携带时间戳以获得完整防重放能力；时钟偏差较大的客户端可暂不传

### 7.3 防重放攻击

```
1. Nonce 格式校验：8~64 位 [A-Za-z0-9-_]，非法返回 NONCE_FORMAT_ERROR
2. 时间戳新鲜度校验（仅当客户端传入 Timestamp 头时）：|now - timestamp| <= timeout，超窗返回 EXPIRED（兼容秒级时间戳）
3. 签名验证通过后，原子占用 nonce：
   setIfAbsent(nonce, timeout) → true  放行（首次）
                               → false 返回 API_AGAIN（重复/重放）
4. timeout 后 nonce 自动过期；缓存写入失败按拒绝处理，不静默降级
```

> 说明：nonce 占用为原子操作（Redis `SET NX EX`），并发相同 nonce 仅一个放行；时间戳不传时不校验，传入时参与签名原文并做新鲜度校验；缓存不可用时按 fail-closed 拒绝并返回 `SYSTEM_BUSY`。

### 7.4 JWT 安全（web-base）

`ContextDataManager` 通过 `JwtManager` 解析 `Access-Token`：

```java
// 验签：校验 HS256 签名（伪造/篡改返回 JWT_SIGN_INVALID）
jwt.setKey(secret).verify();
// 过期：校验 exp 声明（过期返回 JWT_EXPIRED）
JWTValidator.of(jwt).validateDate();
// 算法白名单：拒绝 alg=none 等算法混淆攻击
allowed-algorithms 默认仅 HS256
```

- 密钥：`easyfk.config.web.jwt.secret`（默认提供框架密钥，生产必须覆盖，未覆盖启动输出告警日志）
- 盐值：`easyfk.config.web.jwt.salt`（实际签名密钥 = HMAC-SHA256(secret, salt)，生产必须覆盖，未覆盖启动输出告警日志）
- 有效期：`easyfk.config.web.jwt.expires-second`（默认 10800 秒，即 3 小时；签发必写 `exp`，缺少 `exp` 的 Token 直接拒绝）
- 算法白名单：`easyfk.config.web.jwt.allowed-algorithms`（默认 `HS256`，可配置 `HS256,HS384,HS512`）
- 存量 Token：引入加盐后签名密钥已变化，升级前签发的旧 Token 全部失效，用户需重新登录；之后修改 secret 或 salt 同样会使存量 Token 失效

---

## 8. LocalInterceptor（本地权限拦截器）

基于 `HandlerInterceptor` 实现注解驱动的权限校验：

```
请求到达 Controller 方法
    │
    ├─ URI 在排除列表中 → 放行
    │
    ├─ handler 是 HandlerMethod？
    │   │
    │   ├─ 有 @LoginResource / @AuthResource / require-auth-by-default？
    │   │   │
    │   │   ├─ UserData 为空 → 返回 UN_LOGIN
    │   │   │
    │   │   ├─ 有 @AuthResource？
    │   │   │   │
    │   │   │   ├─ 检查 authCachedKey → UserAuth 为空 → UN_LOGIN
    │   │   │   │
    │   │   │   └─ authType != 0？
    │   │   │       ├─ checkAuth(key, url) 成功 → 放行
    │   │   │       └─ 失败 → 返回 UN_AUTH + 自定义消息
    │   │   │
    │   │   └─ 只有 @LoginResource → 有 UserData 即放行
    │   │
    │   └─ 无权限注解且未开启 require-auth-by-default → 放行
    │
    └─ 非 HandlerMethod → 放行
```

**配置说明：**

- `easyfk.config.web.intercept.auth-type`：权限拦截等级，`0` 仅校验登录态，`1` 额外校验 URL 权限
- `easyfk.config.web.intercept.require-auth-by-default`：默认 `false`（未标注注解的接口直接放行，保持兼容）；开启后未标注接口也要求登录，避免漏标导致接口匿名可访问
- **开启 `require-auth-by-default` 后，登录、注册、回调等匿名接口必须加入 `exclude-paths`（如 `/api/login`），否则会被要求登录而自锁**
- `@AuthResource` 支持标注在方法或类上（类级对整个控制器生效），无权限时返回 `UN_AUTH` 并支持 `unPassMsg` 自定义提示

---

## 9. ControllerAspect（Controller 切面）

基于 `MethodInterceptor` 实现 Controller 层方法拦截：

**默认切面表达式：**
```
execution(public * com.mcst..*.controller..*.*(..))
```

可通过 `pointcut` 配置追加自定义表达式（OR 合并）。

**功能：**
- 记录方法调用开始/结束的 debug 日志
- 记录当前操作人信息（UserDataContext）
- SQL 注入入口校验：对 `SearchRequest` 的字段名/关键词做白名单校验（非法返回参数错误）
- 序列化并记录方法参数（过滤 HttpServletRequest/Response/MultipartRequest）
- 捕获并记录异常，然后继续抛出

---

## 10. PrdExceptionHandler（全局异常处理）

五级异常分类处理：

| 异常类型 | 处理方式 |
|---|---|
| `BindException` / `ValidationException` / `MethodArgumentNotValidException` | HTTP 400 + `RRBuilder.buildFailByException(e)` 提取校验错误 |
| `BusinessException` | 使用 errorCode + errorMsg |
| `HttpRequestMethodNotSupportedException` | HTTP 405 + 泛化消息（不透出原始异常） |
| `SocketTimeoutException` | I18N 消息 `ServerBusyMsg`，状态码 BUSYNESS |
| `Exception`（兜底） | I18N 消息，智能识别日期反序列化错误 |

**智能日期错误识别：**
```java
if (errMsg.contains("Failed to deserialize java.time.LocalDate")) {
    code = "DateFormatErrorMsg";
} else if (errMsg.contains("Failed to deserialize java.time.LocalDateTime")) {
    code = "DateTimeFormatErrorMsg";
} else if (errMsg.contains("Failed to deserialize java.time.LocalTime")) {
    code = "TimeFormatErrorMsg";
}
```

---

## 11. InitResourceRunner（权限资源自动初始化）

启动时自动扫描带有 `@ResourceController` 注解的 Controller，提取权限资源并批量保存：

```
应用启动（CommandLineRunner，Order=0）
    │
    ├─ open=false → 跳过
    │
    ├─ 扫描 @ResourceController Bean
    │   ├─ group="default" → 全部
    │   └─ group="xxx" → 按组过滤
    │
    └─ 遍历每个 Controller
        │
        ├─ 创建菜单资源（@ResourceController 元数据）
        │
        └─ 遍历所有方法
            ├─ 解析 URL（@GetMapping/@PostMapping/@PutMapping/@DeleteMapping/@RequestMapping）
            ├─ 跳过通配路径（*、{参数}）
            │
            ├─ 有 @AuthResource → 创建权限资源
            └─ 无 @AuthResource + normal=true
                ├─ 有 @LoginResource → level=1（需登录）
                └─ 无注解 → level=0（公开）
```

---

## 12. 时间参数转换器

四种 Spring MVC 参数转换器，处理前端字符串形式的时间参数：

| 转换器 | 输入格式 | 输出类型 |
|---|---|---|
| `DateConverter` | `yyyy-MM-dd HH:mm:ss` / `yyyy-MM-dd` / `HH:mm:ss`（自动识别长度） | `Date` |
| `LocalDateConverter` | `yyyy-MM-dd` | `LocalDate` |
| `LocalDateTimeConverter` | `yyyy-MM-dd HH:mm:ss` | `LocalDateTime` |
| `LocalTimeConverter` | `HH:mm:ss` | `LocalTime` |

---

## 13. 工具类

### 13.1 FailRequestUtil

```java
// 构建失败响应对象
ResponseResult<?> result = FailRequestUtil.failRequestInfo(ErrorRequest.SIGN_ERROR);

// 直接写入 HTTP 响应
FailRequestUtil.failRequest(httpServletResponse, ErrorRequest.UNLOGIN);
FailRequestUtil.failRequest(httpServletResponse, responseResult);
```

### 13.2 RequestUtil

```java
String url = RequestUtil.getRequestUrl(request);       // 获取去除 contextPath 后的 URI
boolean isAjax = RequestUtil.isAjax(request);           // 判断 Ajax 请求
boolean isWeChat = RequestUtil.isWeChatRequest(request); // 判断微信浏览器
boolean isQQ = RequestUtil.isQqRequest(request);         // 判断 QQ 浏览器
```

### 13.3 StaticUriUtil

```java
boolean isStatic = StaticUriUtil.isStaticUrl(url);
```

匹配 `/static/` 前缀和静态文件扩展名。

### 13.4 BodyCachingRequestWrapper

请求体缓存包装器（v2 签名/API 鉴权计算请求体摘要时使用），缓存 JSON 等常规请求体并允许下游重复读取；GET/HEAD、multipart、表单提交不缓存，超大请求体（>2MB）标记溢出并跳过摘要比对。

### 13.5 RequestTokenUtil

```java
// 生成一次性表单防重令牌（与 @RequestToken 配套）
String token = RequestTokenUtil.issue(cacheService, userId, 300);
```

### 13.6 SqlGuardUtil

```java
// 入口层 SQL 注入校验：SearchRequest 字段名/关键词白名单
SqlGuardUtil.validateSearchRequest(searchRequest);
```

### 13.7 ApiSignUtil

```java
// API 调用鉴权签名（OpenAPI 风格，HMAC-SHA256）
String sign = ApiSignUtil.sign(appId, timestamp, nonce, method, uri, bodyHash, secret);
boolean valid = ApiSignUtil.verify(appId, timestamp, nonce, method, uri, bodyHash, secret, sign);
```

---

## 14. VO 对象

### 14.1 LoginRequestVO（登录请求）

| 字段 | 说明 | 校验 |
|---|---|---|
| `loginAccount` | 账号/手机号/邮箱 | `@NotBlank` |
| `password` | 登录密码（加密） | — |
| `picToken` | 图形验证码 Token | — |
| `picCode` | 图片验证码 | — |
| `smsCode` | 手机验证码 | — |
| `type` | 登录类型：`accountAndPic` / `account` / `mobile` | — |
| `returnUrl` | 登录成功跳转 URL | — |

### 14.2 SiteLoginSuccessVO（登录成功响应）

| 字段 | 说明 |
|---|---|
| `accessToken` | JWT Token |
| `headImage` | 用户头像 |
| `returnUrl` | 跳转 URL |
| `status` | 状态码 |

### 14.3 RegistryRequestVO（注册请求）

| 字段 | 说明 |
|---|---|
| `phone` | 手机号码 |
| `smsCode` | 短信验证码 |
| `loginPwd` | 登录密码（密文） |
| `email` | 邮箱 |
| `name` | 用户名 |
| `referrerId` | 推荐人 |
| `registryChannel` | 注册渠道 |

---

## 15. CORS 跨域过滤器

通过 `easyfk.config.web.cors.open=true` 启用：

```java
CorsConfiguration corsConfiguration = new CorsConfiguration();
String corsDomain = corsProperties.getCorsDomain();
if (EmptyUtil.isEmpty(corsDomain)) {
    corsConfiguration.addAllowedOriginPattern("*");   // 未配置域名且不携带凭据时允许所有来源
} else {
    for (String origin : corsDomain.split(",")) {
        if (EmptyUtil.isNotEmpty(origin)) {
            corsConfiguration.addAllowedOriginPattern(origin.trim());
        }
    }
}
for (String header : corsProperties.getAllowedHeader().split(",")) {
    if (EmptyUtil.isNotEmpty(header)) {
        corsConfiguration.addAllowedHeader(header.trim());
    }
}
for (String method : corsProperties.getAllowedMethod().split(",")) {
    if (EmptyUtil.isNotEmpty(method)) {
        corsConfiguration.addAllowedMethod(method.trim());
    }
}
corsConfiguration.setAllowCredentials(corsProperties.isAllowCredentials());
corsConfiguration.setMaxAge(3600L);
```

- 使用 `addAllowedOriginPattern` 替代 `addAllowedOrigin`，支持通配符模式匹配
- **安全限制**：`allow-credentials=true` 时 `cors-domain` 不允许为 `*` 或为空，否则启动即失败（`IllegalStateException`），必须配置具体域名
- `cors-domain` / `allowed-header` / `allowed-method` 支持英文逗号分隔多个值
- `cors-domain` 未配置且 `allow-credentials=false` 时回退为允许所有来源（`*`）；空项会被自动过滤

---

## 16. 表单重复提交防护（@RequestToken）

### 16.1 原理

`Request-Token` 为一次性令牌：前端提交前先从服务端获取 token，提交时放入 `Request-Token` 请求头；服务端通过缓存原子占用（`setIfAbsent`），同一 token 只能被消费一次，重复提交返回 `REQUEST_AGAIN`。

### 16.2 使用步骤

**第一步：下发令牌（业务侧调用）**

```java
@Resource
@Lazy
private ICacheService cacheService;

// 登录后或进入表单页时生成一次性令牌
@GetMapping("/form-token")
public ResponseResult<String> formToken() {
    String token = RequestTokenUtil.issue(cacheService, currentUserId(), 300);
    return RRBuilder.buildSuccessBody(token);
}
```

**第二步：在提交接口上标注注解**

```java
@PostMapping("/order/submit")
@RequestToken(verify = true, ttlSeconds = 300)
public ResponseResult<OrderVO> submit(@RequestBody OrderSubmitVO order) {
    return orderService.submit(order);
}
```

**第三步：前端携带令牌提交**

```http
POST /order/submit HTTP/1.1
Content-Type: application/json
Request-Token: 5c1f2a...（第一步获取的令牌）

{ "orderNo": "20260805001" }
```

### 16.3 注解参数

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `verify` | boolean | `true` | 是否校验 `Request-Token`（`false` 仅占位） |
| `ttlSeconds` | long | `300` | 令牌有效时长（秒） |

### 16.4 错误码与注意事项

- 未携带令牌：`REQUEST_TOKEN_EMPTY`
- 令牌已使用/重复提交：`REQUEST_AGAIN`
- 令牌缓存键带用户维度（`userId:token`），匿名场景使用 `anonymous`；令牌本身不携带签发者强绑定，请求身份仍由 JWT 登录态控制
- 令牌一经消费即失效（业务失败后需重新获取令牌再提交）

---

## 17. 接口幂等（@Idempotent）

### 17.1 原理

同一"幂等键"在窗口内只允许执行业务一次：执行前原子占用缓存键，重复请求返回 `IDEMPOTENT_ERROR`（或静默忽略）；业务成功后在窗口内保持占用，业务异常时释放幂等键允许重试。

### 17.2 使用示例

```java
@PostMapping("/payment/create")
@Idempotent(key = "#args[0].orderNo", ttlSeconds = 60, onDuplicateFail = true)
public ResponseResult<PaymentVO> createPayment(@RequestBody PaymentCreateVO param) {
    return paymentService.create(param);
}
```

### 17.3 注解参数

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `key` | String | 空 | 幂等键 SpEL 表达式，如 `#args[0].orderNo`、`#p0.orderNo`；为空时使用 `类名.方法名` |
| `ttlSeconds` | long | `60` | 幂等窗口（秒），窗口内重复请求被拦截 |
| `onDuplicateFail` | boolean | `true` | `true`=抛 `IDEMPOTENT_ERROR`；`false`=返回 `null`（仅支持对象返回值，不支持基本类型） |

### 17.4 注意事项

- 幂等键自动拼入当前登录用户维度（`Idempotent:{userId}:{key}`），不同用户互不影响
- 幂等键应选择业务唯一标识（订单号、流水号、业务单号等），避免使用时间戳等每次变化的值
- 业务异常时幂等键自动释放，客户端可重试；网络超时等不确定场景请配合业务侧唯一约束兜底
- 一期不缓存业务结果：窗口内重复请求返回错误码，不返回首次执行结果

---

## 18. SQL 注入防范

### 18.1 防护层次

| 层次 | 位置 | 能力 |
|---|---|---|
| 入口校验 | `ControllerAspect` + `SqlGuardUtil`（web-prd） | 校验 `SearchRequest`/`BasicParam` 的字段名与关键词 |
| 构建校验 | `SCBuilder`（easyfk-repository） | 所有字符串字段入口列名白名单校验 |
| 参数化构建 | `ConditionUtil.doLike` 等 | 模糊/关键词/多值条件全部参数化，不再手工拼接 SQL |
| ORM 兜底 | `MyBatisPlusWrapperUtil` 及条件工具（orm-mybatis） | 排序/分组/字段列名校验 + 自定义 SQL 危险语法拦截 |

### 18.2 字段名规则

字段名（`selectFields`、`ascFields`、`descFields`、`likeFields`、`inParams` 等）必须匹配：

```
^[A-Za-z][A-Za-z0-9_.]{0,127}$
```

- 字母开头，可包含字母/数字/下划线/点（点用于表前缀，如 `t1.id`）
- 拒绝空白、引号、分号、括号、注释符等注入特征字符
- 非法字段名返回参数错误，不再进入 SQL 构建

### 18.3 关键词规则

`searchKeyWord` 长度上限 64，且禁止包含 `'`、`;`、`--`、`/*`、`*/` 及 DDL/DML 关键字（`exec/insert/update/delete/drop/alter/truncate/create`）。

### 18.4 自定义 SQL 限制

`SCBuilder.customConditionSql(...)` 属于内部可信 API，ORM 层在 `wrapper.apply()` 前会检测分号、注释符及 DDL/DML 关键字，命中即拒绝执行（`IllegalArgumentException`）。客户端数据不得直接传入该 API。

### 18.5 推荐写法

```java
// 推荐：参数化条件（自动防注入）
SearchRequest<OrderQuery> req = new SearchRequest<>();
req.setLikeFields(new String[]{"orderNo"});
req.setParmaObj(new OrderQuery().setOrderNo("2026"));

// 等价于参数化 LIKE：WHERE order_no LIKE '%2026%'
```

---

## 19. 其他安全加固

### 19.1 安全响应头

`SecurityHeadersFilter` 默认启用（`easyfk.config.web.prd.security-headers=true`），自动补全：

| 响应头 | 值 |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `SAMEORIGIN` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `X-XSS-Protection` | `0` |

业务已设置的响应头不会被覆盖。

### 19.2 ignore-uri 匹配规则（行为变更）

- 原实现为"包含子串"匹配，存在 `/login` 误放行 `/login-admin` 的风险
- 现改为**精确或 Ant 模式**匹配：`/login` 仅匹配 `/login`；放行子路径需配置 `/login/**`
- 拦截器排除路径（`exclude-paths`）同样使用 Ant 匹配，两处规则一致

### 19.3 异常与错误码

- 参数校验失败返回 HTTP 400（`BindException`/`ValidationException`/`MethodArgumentNotValidException`）
- 请求方法不支持返回 HTTP 405，且不向客户端透出 Spring 原始异常信息
- 重复提交/幂等拦截通过 `BusinessException` 体系返回 `REQUEST_AGAIN`/`IDEMPOTENT_ERROR`

---

## 20. 接口调用鉴权（OpenAPI 风格）

### 20.1 定位与原理

接口调用鉴权是**安全级调用方认证**：调用方（第三方系统、内部服务、开放平台 App）必须携带 `App-Id` 与 `Api-Sign` 签名才能调用接口，解决"谁在调用 API"的问题。

它与业务用户权限是**两层独立体系**：

| 维度 | 接口调用鉴权（本章） | 用户权限（第 8 章） |
|---|---|---|
| 认证对象 | 调用方（App/系统） | 登录用户（BMS 用户/会员） |
| 凭据 | App-Id + Secret 签名 | Access-Token（JWT） |
| 校验位置 | `ApiAuthFilter`（过滤器，先执行） | `LocalInterceptor`（拦截器，后执行） |
| 失败结果 | `API_CLIENT_*` / `API_SIGN_ERROR` 等 | `UN_LOGIN` / `UN_AUTH` |
| 用途 | 第三方开放接口、服务间调用 | 业务系统内用户操作 |

开启后，除 `ignore-uri` 与静态资源外，**所有接口默认要求调用方鉴权**（无需逐个标注）。

**过滤器层级：**`ApiAuthFilter` 是**最高层过滤器**，通过 `FilterRegistrationBean` 以最高优先级注册，最先执行——调用方鉴权未通过时，请求在安全签名/防重放（`RequestBaseFilter`）与用户鉴权（`LocalInterceptor`）之前即被拒绝。

**默认关闭：**`easyfk.config.web.api-auth.open` 与 `easyfk.config.web.security.open` **默认均为 `false`**，两套机制都需要显式开启后才生效，不影响现有项目开箱行为。

### 20.2 配置示例

```yaml
easyfk:
  config:
    web:
      api-auth:
        open: true
        timeout: 150s
        ignore-uri:
          - /health
          - /api/public/**
        clients:
          - app-id: partner-app
            secret: "partner-secret-xxxx"
            enabled: true
            allowed-uris:          # 为空表示允许全部接口
              - /order/**
              - /payment/**
          - app-id: internal-svc
            secret: "internal-secret-yyyy"
```

### 20.3 请求头与签名算法

调用方请求需携带以下请求头：

| 请求头 | 必填 | 说明 |
|---|---|---|
| `App-Id` | 是 | 调用方标识 |
| `Api-Nonce` | 是 | 随机串（8~64 位 `[A-Za-z0-9-_]`），原子防重放 |
| `Api-Timestamp` | 否 | 毫秒/秒时间戳，传入则校验新鲜度（`timeout` 窗口内），不传不校验 |
| `Api-Body` | 有请求体时必填 | 请求体 SHA-256 十六进制串（服务端会与实际请求体比对）；无请求体可省略（按空串） |
| `Api-Sign` | 是 | 签名（HMAC-SHA256） |

签名原文：

```text
App-Id={appId}&Timestamp={timestamp}&Nonce={nonce}&Method={method}&Uri={uri}&Body={bodyHash}
```

- `method`：HTTP 方法（大写），如 `POST`
- `uri`：请求 URI（不含 contextPath），如 `/order/create`
- `bodyHash`：`SHA-256(请求体字节)` 的十六进制串，无请求体为空串
- `timestamp`：客户端原始字符串，与 `Api-Timestamp` 头完全一致（未传则空串）
- `Api-Sign = HMAC-SHA256(签名原文, secret)`（十六进制小写）

### 20.4 Java 客户端调用示例

```java
// 服务端：签名工具 ApiSignUtil（web-prd）
String sign = ApiSignUtil.sign(
        appId,                 // "partner-app"
        timestamp,             // 与 Api-Timestamp 头一致的原始字符串
        nonce,                 // 随机串
        "POST",                // HTTP 方法
        "/order/create",       // 请求 URI（不含 contextPath）
        bodyHash,              // SHA-256(body) 十六进制串，无 body 传 ""
        secret);               // 调用方密钥

// 客户端组装请求头（示例，使用 Apache HttpClient / OkHttp 同理）
// App-Id: partner-app
// Api-Nonce: {nonce}
// Api-Timestamp: {timestamp}
// Api-Body: {bodyHash}
// Api-Sign: {sign}
```

bodyHash 计算示例：

```java
String bodyHash = DigestUtil.sha256Hex(bodyBytes);   // hutool
```

### 20.5 错误码

| 错误码 | 场景 |
|---|---|
| `API_CLIENT_MISSING` | 未携带 `App-Id` |
| `API_CLIENT_INVALID` | 调用方不存在 |
| `API_CLIENT_DISABLED` | 调用方被禁用 |
| `API_UNAUTHORIZED` | 调用方无权访问该接口（`allowed-uris` 不匹配） |
| `API_TIMESTAMP_ERROR` | 时间戳格式错误 |
| `API_EXPIRED` | 时间戳超出新鲜度窗口 |
| `API_NONCE_ERROR` | Nonce 缺失或格式不合法 |
| `API_AGAIN` | Nonce 重放/重复请求 |
| `API_SIGN_ERROR` | 签名验证失败（密钥错误、请求被篡改） |
| `SYSTEM_BUSY` | 缓存/安全服务暂不可用（Redis 故障等，fail-closed 拒绝） |

### 20.6 自定义调用方存储

生产环境建议从数据库/Redis 加载调用方（支持动态吊销），实现 `IApiClientStore` 并注册 Bean 即可覆盖默认配置版：

```java
@Component
public class DbApiClientStore implements IApiClientStore {
    @Override
    public ApiAuthProperties.ApiClient getClient(String appId) {
        // 从数据库/缓存查询并组装 ApiAuthProperties.ApiClient
        return ...;
    }
}
```

### 20.7 注意事项

- 开启 API 调用鉴权后，业务侧所有客户端（含前端）都必须按调用方接入签名；如需保留部分匿名接口，配置 `ignore-uri`
- `App-Id` 与 `Secret` 属于敏感凭据，禁止出现在日志、URL、前端代码中；Secret 仅服务端持有
- 建议调用方接入 HTTPS；签名用于身份认证与防篡改，不能替代传输加密
- 与 `easyfk.config.web.security.open`（请求签名 + 防重放）可同时开启：前者校验调用方身份，后者校验请求完整性，两者独立
- **Nonce 占用顺序**：服务端先验签、后原子占用 Nonce；签名无效的请求不消耗防重放缓存，签名算错可换 Nonce 重试，重放请求返回 `API_AGAIN`
- **缓存故障处理**：Nonce 占用依赖的缓存不可用时（Redis 异常），按 fail-closed 拒绝并返回 `SYSTEM_BUSY`，不静默放行
