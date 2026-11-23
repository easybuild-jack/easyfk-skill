# easyfk-web API 签名速查（easyfk 3.2.12）

> 坐标：`com.mcst:web-simple、web-base、web-common、web-prd、web-micro`　源码：`easyfk-base/easyfk-web/web-simple`、`easyfk-base/easyfk-web/web-base`、`easyfk-base/easyfk-web/web-common`、`easyfk-base/easyfk-web/web-prd`、`easyfk-base/easyfk-web/web-micro`
> 由 `scripts/gen-api.py` 从 56 个源文件自动提取，共 56 个类型、113 个方法/构造器、111 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-web-skill.md](../modules/easyfk-web-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 配置项（@ConfigurationProperties）

### `easyfk.config.web.jwt` ← JwtProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `secret` | `String` | `DEFAULT_SECRET` | 签名密钥,项目可通过 easyfk.config.web.jwt.secret 覆盖 |
| `salt` | `String` | `DEFAULT_SALT` | 签名盐值,与 secret 共同派生签名密钥,项目可通过 easyfk.config.web.jwt.salt 覆盖。 修改 secret 或 salt 后存量 token 全部失效。 |
| `expires-second` | `Integer` | `DEFAULT_EXPIRES_SECOND` | Token 有效期(秒),默认 3 小时;<=0 视为未配置并按默认值处理 |
| `allowed-algorithms` | `String` | `"HS256"` | 允许的签名算法白名单(逗号分隔,不区分大小写)。 默认仅 HS256;验签前强制校验,防止 alg=none / 算法混淆攻击。 |

### `easyfk.config.web.cors` ← CorsProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `open` | `boolean` | `—` | 是否开启跨域 |
| `allow-credentials` | `boolean` | `false` | 是否允许携带凭据（Cookie/Authorization）。为 true 时 cors-domain 必须配置为具体域名，不允许为空或包含 '*' |
| `cors-domain` | `String` | `"*"` | 允许跨域的域名（支持 origin pattern）,多个用英文逗号隔开 |
| `allowed-header` | `String` | `"*"` | 允许跨域的自定义头信息,多个用英文逗号隔开 |
| `allowed-method` | `String` | `"*"` | 允许跨域的Method,多个用英文逗号隔开 |
| `path-pattern` | `String` | `"/**"` | 跨域配置生效的路径（Ant 模式），多个用英文逗号隔开 |

### `easyfk.config.web.intercept` ← InterceptProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `exclude-paths` | `List<String>` | `—` | 拦截器过滤uri |
| `open-gateway-interceptor` | `boolean` | `—` | 是否开启网关拦截器 |
| `auth-type` | `Integer` | `0` | 权限拦截等级，0：只检测是否登录，1：检测登录并是否有权 |
| `refresh-user-auth` | `boolean` | `false` | 是否刷新UserAuth |
| `require-auth-by-default` | `boolean` | `—` | 未标注 @LoginResource/@AuthResource 的接口是否默认要求登录（默认 false，保持兼容； 开启后业务未标注的接口也会校验登录态，避免漏标导致接口匿名可访问） |
| `custom-gateway-filter` | `boolean` | `—` | 是否使用自定义网关过滤器（仅 gateway 使用） |

### `easyfk.config.web.security` ← SecurityProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `ignore-uri` | `List<String>` | `—` | 允许忽略安全地址 |
| `timeout` | `Duration` | `Duration.ofSeconds(150)` | 时间戳新鲜度窗口：\|服务端时间 - Timestamp\| 不得超过该值；Nonce 防重放 TTL 为其 2 倍 |
| `open` | `boolean` | `—` | 是否开启接口安全控制 |
| `sign-key` | `String` | `"mcst_sign_reset"` | 生成验签的key |
| `sign-key-dynamic` | `boolean` | `—` | 验签的key是否是动态的 |
| `sign-version` | `String` | `"v1"` | 签名版本：v1 = MD5（兼容存量客户端，同时接受 v1/v2 请求）； v2 = HMAC-SHA256（绑定方法+URI+请求体摘要），配置为 v2 时拒绝 v1 请求且必须携带 Timestamp |

### `easyfk.config.web.api-auth` ← ApiAuthProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `open` | `boolean` | `—` | 是否开启 API 调用鉴权。开启后除 ignore-uri/静态资源外，所有接口必须携带 App-Id / Api-Timestamp / Api-Nonce / Api-Sign（+ Api-Body）请求头。 |
| `timeout` | `Duration` | `Duration.ofSeconds(150)` | 时间戳新鲜度窗口与 Nonce 防重放 TTL，默认 150 秒 |
| `ignore-uri` | `List<String>` | `—` | 忽略 API 鉴权的 URI（精确或 Ant 模式），如 /health、/api/public/** |
| `clients` | `List<ApiClient>` | `new ArrayList<>()` | 内置调用方列表（配置方式，生产建议使用数据库/缓存并实现 IApiClientStore 自定义加载） |

### `easyfk.config.aspect.controller` ← ControllerAspectProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `open` | `Boolean` | `Boolean.TRUE` |  |
| `pointcut` | `String` | `—` | 切面表达式 |

### `easyfk.config.web.prd` ← PrdWebProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `open-interceptor` | `boolean` | `true` | 是否开启登录/权限拦截器（LocalInterceptor） |
| `open-filter` | `boolean` | `true` | 是否开启请求前置过滤器（RequestBaseFilter：上下文还原、签名防重放） |
| `open-request-token` | `boolean` | `true` | 是否开启 @RequestToken 表单防重 |
| `open-idempotent` | `boolean` | `true` | 是否开启 @Idempotent 接口幂等 |
| `security-headers` | `boolean` | `true` | 是否开启安全响应头过滤器 |

### `easyfk.config.resource.init` ← ResourceInitProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `open` | `Boolean` | `Boolean.FALSE` | 是否生成资源数据 |
| `group` | `String` | `"default"` | 生成资源组名称，default 表示所有组,多个用英文逗号隔开，initResource 为true 生效 |
| `normal` | `Boolean` | `Boolean.FALSE` | 是否生成非权限资源，initResource 为true 生效 |


## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `web-base` | `com.mcst.easyfk.web.base.config.WebBaseConfig` |
| `web-common` | `com.mcst.easyfk.web.common.config.WebCommonConfig` |
| `web-prd` | `com.mcst.easyfk.web.prd.config.PrdWebConfig` |
| `web-micro` | `com.mcst.easyfk.web.micro.config.MicroWebConfig` |

## 类型索引

- `com.mcst.easyfk.web.base.config`：[WebBaseConfig](#webbaseconfig)
- `com.mcst.easyfk.web.base.manager`：[ContextDataManager](#contextdatamanager)、[JwtManager](#jwtmanager)
- `com.mcst.easyfk.web.base.properties`：[JwtProperties](#jwtproperties)
- `com.mcst.easyfk.web.base.vo`：[ParseJwtResult](#parsejwtresult)
- `com.mcst.easyfk.web.common.config`：[WebCommonConfig](#webcommonconfig)
- `com.mcst.easyfk.web.common.constant`：[ErrorRequest](#errorrequest)、[RequestConstant](#requestconstant)、[SignConstant](#signconstant)
- `com.mcst.easyfk.web.common.jackson`：[JacksonTimeFormats](#jacksontimeformats)
- `com.mcst.easyfk.web.common.properties`：[CorsProperties](#corsproperties)、[InterceptProperties](#interceptproperties)、[SecurityProperties](#securityproperties)
- `com.mcst.easyfk.web.common.util`：[CheckIgnoreSecurityUriUtil](#checkignoresecurityuriutil)、[HttpStatusResolver](#httpstatusresolver)、[InterceptorExcludeUriUtil](#interceptorexcludeuriutil)
- `com.mcst.easyfk.web.micro.config`：[MicroWebConfig](#microwebconfig)
- `com.mcst.easyfk.web.micro.exception`：[MicroExceptionHandler](#microexceptionhandler)
- `com.mcst.easyfk.web.micro.filter`：[RequestBaseFilter](#requestbasefilter)
- `com.mcst.easyfk.web.prd.annotation`：[Idempotent](#idempotent)、[RequestToken](#requesttoken)
- `com.mcst.easyfk.web.prd.api`：[IApiClientStore](#iapiclientstore)、[PropertiesApiClientStore](#propertiesapiclientstore)
- `com.mcst.easyfk.web.prd.aspect`：[ControllerAspect](#controlleraspect)、[IdempotentAspect](#idempotentaspect)、[RequestTokenAspect](#requesttokenaspect)
- `com.mcst.easyfk.web.prd.config`：[ControllerAspectConfigure](#controlleraspectconfigure)、[PrdWebConfig](#prdwebconfig)、[WebInterceptorRegister](#webinterceptorregister)
- `com.mcst.easyfk.web.prd.converter`：[DateConverter](#dateconverter)、[LocalDateConverter](#localdateconverter)、[LocalDateTimeConverter](#localdatetimeconverter)、[LocalTimeConverter](#localtimeconverter)
- `com.mcst.easyfk.web.prd.exception`：[DuplicateSubmitException](#duplicatesubmitexception)、[IdempotentException](#idempotentexception)、[PrdExceptionHandler](#prdexceptionhandler)
- `com.mcst.easyfk.web.prd.filter`：[ApiAuthFilter](#apiauthfilter)、[RequestBaseFilter](#requestbasefilter)、[SecurityHeadersFilter](#securityheadersfilter)
- `com.mcst.easyfk.web.prd.interceptor`：[LocalInterceptor](#localinterceptor)
- `com.mcst.easyfk.web.prd.properties`：[ApiAuthProperties](#apiauthproperties)、[ControllerAspectProperties](#controlleraspectproperties)、[PrdWebProperties](#prdwebproperties)、[ResourceInitProperties](#resourceinitproperties)
- `com.mcst.easyfk.web.prd.runner`：[InitResourceRunner](#initresourcerunner)
- `com.mcst.easyfk.web.prd.util`：[ApiSignUtil](#apisignutil)、[BodyCachingRequestWrapper](#bodycachingrequestwrapper)、[ClientIpUtil](#clientiputil)、[FailRequestUtil](#failrequestutil)、[RequestTokenUtil](#requesttokenutil)
    [RequestUtil](#requestutil)、[SqlGuardUtil](#sqlguardutil)、[StaticUriUtil](#staticuriutil)
- `com.mcst.easyfk.web.prd.vo`：[LoginRequestVO](#loginrequestvo)、[RegistryRequestVO](#registryrequestvo)、[SiteLoginSuccessVO](#siteloginsuccessvo)

## 包 `com.mcst.easyfk.web.base.config`

### WebBaseConfig

`public class WebBaseConfig`　注解：`@AutoConfiguration` `@EnableConfigurationProperties(JwtProperties.class)`

**方法**

```java
@Bean JwtManager getJwtManager()
@Bean ContextDataManager getContextDataManager()
```

## 包 `com.mcst.easyfk.web.base.manager`

### ContextDataManager

`public class ContextDataManager`　注解：`@Slf4j`　Request context manager: trace id, JWT user context and cache refresh.

**方法**

```java
void doDataContext(boolean refreshUserAuth)
void doDataContext(String traceId, boolean refreshUserAuth)  // 沿用上游传入的 traceId（缺失或格式非法时新生成），再还原用户上下文
void createTraceId()
void clearContext()
```

### JwtManager

`public class JwtManager`　注解：`@SuppressWarnings("all")` `@Slf4j`　JWT manager with signature verification and expiry validation.

**字段 / 常量**

```java
static final String ERROR_CODE_SIGN_INVALID = "JWT_SIGN_INVALID"
static final String ERROR_CODE_EXPIRED = "JWT_EXPIRED"
static final String ERROR_CODE_FORMAT = "JWT_FORMAT"
```

**方法**

```java
String createJwtByString(String content)
<T> String createJwtByObject(T obj)
<T> ParseJwtResult<T> getObjectContent(String token, Class<T> tClass)
ParseJwtResult<String> getStringContent(String token)
```

## 包 `com.mcst.easyfk.web.base.properties`

### JwtProperties

`public class JwtProperties`　Lombok：`@Data`　注解：`@Slf4j` `@ConfigurationProperties(prefix = "easyfk.config.web.jwt")`　JWT 配置属性。 提供默认密钥与盐值便于开箱即用,项目可通过 easyfk.config.web.jwt.secret / easyfk.config.web.jwt.salt 覆盖…

**字段 / 常量**

```java
static final String DEFAULT_SECRET = "XX#$%()(#*!()!KL<><MQLMNQNQJQKabcdefgh1234?N<:{LWPW"  // 框架默认密钥(仅用于开箱即用,生产环境必须覆盖)
static final String DEFAULT_SALT = "easyfk@jwt#salt$9Qm2Lx7Vr4Tz8Kp1"  // 框架默认盐值(仅用于开箱即用,生产环境必须覆盖)
static final int DEFAULT_EXPIRES_SECOND = 10800  // 默认 Token 有效期(秒):3 小时
String secret = DEFAULT_SECRET  // 签名密钥,项目可通过 easyfk.config.web.jwt.secret 覆盖
String salt = DEFAULT_SALT  // 签名盐值,与 secret 共同派生签名密钥,项目可通过 easyfk.config.web.jwt.salt 覆盖。 修改 secret 或 salt 后存量 token 全部失效。
Integer expiresSecond = DEFAULT_EXPIRES_SECOND  // Token 有效期(秒),默认 3 小时;<=0 视为未配置并按默认值处理
String allowedAlgorithms = "HS256"  // 允许的签名算法白名单(逗号分隔,不区分大小写)。 默认仅 HS256;验签前强制校验,防止 alg=none / 算法混淆攻击。
```

**方法**

```java
@PostConstruct void validate()
```

## 包 `com.mcst.easyfk.web.base.vo`

### ParseJwtResult

`public class ParseJwtResult<T> implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)` `@NoArgsConstructor`　Result of parsing and verifying a JWT.

**字段 / 常量**

```java
boolean success
T data
boolean expires  // Whether the token is expired.
String errorCode  // Failure reason code: JWT_SIGN_INVALID / JWT_EXPIRED / JWT_FORMAT.
```

**构造器**

```java
ParseJwtResult(boolean success)
ParseJwtResult(T data)
```

## 包 `com.mcst.easyfk.web.common.config`

### WebCommonConfig

`public class WebCommonConfig`　注解：`@AutoConfiguration` `@EnableConfigurationProperties({SecurityProperties.class, InterceptProperties.class, CorsProperties.class})`

_无 public 成员。_

## 包 `com.mcst.easyfk.web.common.constant`

### ErrorRequest

`public enum ErrorRequest`　过滤器/切面错误码及其 HTTP 状态码。 状态码约定：参数/请求头格式错误 400，未认证（未登录、签名/时间戳/防重放失败、调用方无效）401， 无权限 403，业务拒绝 200（以 code 区分）…

**枚举常量**

```java
UNLOGIN("UNLOGIN", "当前登录已过期或未登录", 401)  // 未登录
UNAUTH("UNAUTH", "您没有访问权限", 403)
HEARD_EMPTY("HEARD_EMPTY", "请求失败", 400)
NONCE_EMPTY("NONCE_EMPTY", "请求失败", 400)
RESET_SIGN_EMPTY("RESET_SIGN_EMPTY", "请求失败", 400)
TIMESTAMP_EMPTY("TIMESTAMP_EMPTY", "请求失败", 400)
TIMESTAMP_ERROR("TIMESTAMP_ERROR", "请求失败", 400)
NONCE_FORMAT_ERROR("NONCE_FORMAT_ERROR", "请求失败", 400)
SIGN_ERROR("SIGN_ERROR", "验证失败", 401)
EXPIRED("EXPIRED", "请求失败", 401)
API_AGAIN("API_AGAIN", "非法请求", 401)
REQUEST_TOKEN_EMPTY("REQUEST_TOKEN_EMPTY", "请求失败", 400)
REQUEST_AGAIN("REQUEST_AGAIN", "请求失败", 200)
IDEMPOTENT_ERROR("IDEMPOTENT_ERROR", "请求失败", 200)
JWT_ERROR("JWT_ERROR", "请求失败", 401)
DYNAMIC_SIGN_KEY_TIMEOUT("DYNAMIC_SIGN_KEY_TIMEOUT", "请求失败", 503)
API_CLIENT_MISSING("API_CLIENT_MISSING", "请求失败", 401)
API_CLIENT_INVALID("API_CLIENT_INVALID", "请求失败", 401)
API_CLIENT_DISABLED("API_CLIENT_DISABLED", "请求失败", 403)
API_SIGN_ERROR("API_SIGN_ERROR", "验证失败", 401)
API_TIMESTAMP_ERROR("API_TIMESTAMP_ERROR", "请求失败", 400)
API_EXPIRED("API_EXPIRED", "请求失败", 401)
API_NONCE_ERROR("API_NONCE_ERROR", "请求失败", 400)
API_UNAUTHORIZED("API_UNAUTHORIZED", "请求失败", 403)
SYSTEM_BUSY("SYSTEM_BUSY", "请求失败", 503)
```

**字段 / 常量**

```java
String code
String message
final int httpStatus
```

**构造器**

```java
ErrorRequest(String code, String message, int httpStatus)
```

**方法**

```java
static ErrorRequest ofCode(String code)  // 按错误码查找，未匹配返回 null
String getCode()
void setCode(String code)
String getMessage()
void setMessage(String message)
int getHttpStatus()
```

### RequestConstant

`public interface RequestConstant`

**字段 / 常量**

```java
String REST_SECURITY_CACHE_NAME = "Request_Security"
String REQUEST_TOKEN_CACHE_NAME = "Request_Token"
String IDEMPOTENT_CACHE_NAME = "Idempotent"
String API_AUTH_CACHE_NAME = "Api_Auth"
```

### SignConstant

`public interface SignConstant`

**字段 / 常量**

```java
String DYNAMIC_SIGN_KEY_CACHE_KEY = "Security_Dynamic_Sign_Key"
String DYNAMIC_SIGN_KEY_CACHE_NAME = "Security_Dynamic"
```

## 包 `com.mcst.easyfk.web.common.jackson`

### JacksonTimeFormats

`public final class JacksonTimeFormats`　Jackson 时间格式：秒后的小数部分为 0 时不输出，否则按毫秒(3位)/微秒(6位)/纳秒(9位)输出； 解析时兼容无小数及 1~9 位小数

**字段 / 常量**

```java
static final DateTimeFormatter DATETIME_FORMATTER = withOptionalFraction("yyyy-MM-dd HH:mm:ss")
static final DateTimeFormatter TIME_FORMATTER = withOptionalFraction("HH:mm:ss")
```

#### JacksonTimeFormats.LocalDateTimeSerializer

`public static class LocalDateTimeSerializer extends com.fasterxml.jackson.datatype.jsr310.ser.LocalDateTimeSerializer`

**构造器**

```java
LocalDateTimeSerializer()
```

**方法**

```java
JsonSerializer<?> createContextual(SerializerProvider prov, BeanProperty property) throws JsonMappingException
void serialize(LocalDateTime value, JsonGenerator gen, SerializerProvider provider) throws IOException
```

#### JacksonTimeFormats.LocalTimeSerializer

`public static class LocalTimeSerializer extends com.fasterxml.jackson.datatype.jsr310.ser.LocalTimeSerializer`

**构造器**

```java
LocalTimeSerializer()
```

**方法**

```java
JsonSerializer<?> createContextual(SerializerProvider prov, BeanProperty property) throws JsonMappingException
void serialize(LocalTime value, JsonGenerator gen, SerializerProvider provider) throws IOException
```

## 包 `com.mcst.easyfk.web.common.properties`

### CorsProperties

`public class CorsProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.web.cors")`

**字段 / 常量**

```java
boolean open  // 是否开启跨域
boolean allowCredentials = false  // 是否允许携带凭据（Cookie/Authorization）。为 true 时 cors-domain 必须配置为具体域名，不允许为空或包含 '*'
String corsDomain = "*"  // 允许跨域的域名（支持 origin pattern）,多个用英文逗号隔开
String allowedHeader = "*"  // 允许跨域的自定义头信息,多个用英文逗号隔开
String allowedMethod = "*"  // 允许跨域的Method,多个用英文逗号隔开
String pathPattern = "/**"  // 跨域配置生效的路径（Ant 模式），多个用英文逗号隔开
```

### InterceptProperties

`public class InterceptProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.web.intercept")`

**字段 / 常量**

```java
List<String> excludePaths  // 拦截器过滤uri
boolean openGatewayInterceptor  // 是否开启网关拦截器
Integer authType = 0  // 权限拦截等级，0：只检测是否登录，1：检测登录并是否有权
boolean refreshUserAuth = false  // 是否刷新UserAuth
boolean requireAuthByDefault  // 未标注 @LoginResource/@AuthResource 的接口是否默认要求登录（默认 false，保持兼容； 开启后业务未标注的接口也会校验登录态，避免漏标导致接口匿名可访问）
boolean customGatewayFilter  // 是否使用自定义网关过滤器（仅 gateway 使用）
```

### SecurityProperties

`public class SecurityProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.web.security")`

**字段 / 常量**

```java
List<String> ignoreUri  // 允许忽略安全地址
Duration timeout = Duration.ofSeconds(150)  // 时间戳新鲜度窗口：|服务端时间 - Timestamp| 不得超过该值；Nonce 防重放 TTL 为其 2 倍
boolean open  // 是否开启接口安全控制
String signKey = "mcst_sign_reset"  // 生成验签的key
boolean signKeyDynamic  // 验签的key是否是动态的
String signVersion = "v1"  // 签名版本：v1 = MD5（兼容存量客户端，同时接受 v1/v2 请求）； v2 = HMAC-SHA256（绑定方法+URI+请求体摘要），配置为 v2 时拒绝 v1 请求且必须携带 Timestamp
```

## 包 `com.mcst.easyfk.web.common.util`

### CheckIgnoreSecurityUriUtil

`public class CheckIgnoreSecurityUriUtil`

**方法**

```java
static boolean isPass(String requestUri, List<String> ignoreUris)
```

### HttpStatusResolver

`public final class HttpStatusResolver`　业务错误码到 HTTP 状态码的统一映射（prd / micro 异常处理器共用）。 映射规则：命中 ErrorRequest 时取其状态码…

**字段 / 常量**

```java
static final int OK = 200
static final int BAD_REQUEST = 400
static final int UNAUTHORIZED = 401
static final int FORBIDDEN = 403
static final int SERVICE_UNAVAILABLE = 503
```

**方法**

```java
static int resolveBusinessStatus(String code)
```

### InterceptorExcludeUriUtil

`public class InterceptorExcludeUriUtil`

**方法**

```java
static boolean containsUri(String requestUri, InterceptProperties properties)
```

## 包 `com.mcst.easyfk.web.micro.config`

### MicroWebConfig

`public class MicroWebConfig`　注解：`@AutoConfiguration`

**方法**

```java
@Bean @ConditionalOnMissingBean MicroExceptionHandler microExceptionHandler()
@Bean @ConditionalOnMissingBean RequestBaseFilter requestBaseFilter()
@Bean @ConditionalOnMissingBean(ObjectMapper.class) ObjectMapper serializingObjectMapper()  // 全局设置Jackson序列化方式
```

## 包 `com.mcst.easyfk.web.micro.exception`

### MicroExceptionHandler

`public class MicroExceptionHandler`　注解：`@ControllerAdvice` `@Slf4j`　全局异常处理。 HTTP 状态码约定（与 web-prd 一致）：参数校验/请求格式错误 400，未登录 401，无权限 403， 业务异常 200（响应体 code 区分…

**方法**

```java
@ExceptionHandler(value = {BindException.class, ValidationException.class, HandlerMethodValidationException.class}) @ResponseBody @ResponseStatus(HttpStatus.BAD_REQUEST) ResponseResult<?> bindExceptionHandler(Exception e)
@ExceptionHandler(value = {MissingServletRequestParameterException.class, MissingRequestHeaderException.class, MissingServletRequestPartException.class, MethodArgumentTypeMismatchException.class, HttpMediaTypeNotSupportedException.class}) @ResponseBody @ResponseStatus(HttpStatus.BAD_REQUEST) ResponseResult<?> badRequestHandler(Exception e)
@ExceptionHandler(value = HttpMessageNotReadableException.class) @ResponseBody @ResponseStatus(HttpStatus.BAD_REQUEST) ResponseResult<?> messageNotReadableHandler(HttpMessageNotReadableException e)
@ExceptionHandler(value = BusinessException.class) @ResponseBody ResponseEntity<ResponseResult<?>> businessExceptionHandler(BusinessException e)  // 业务异常处理
@ExceptionHandler(value = HttpRequestMethodNotSupportedException.class) @ResponseBody @ResponseStatus(HttpStatus.METHOD_NOT_ALLOWED) ResponseResult<?> methodNotSupportedException(HttpRequestMethodNotSupportedException exception)
@ExceptionHandler(value = {NoResourceFoundException.class, NoHandlerFoundException.class}) @ResponseBody @ResponseStatus(HttpStatus.NOT_FOUND) ResponseResult<?> notFoundHandler(Exception exception)
@ExceptionHandler(value = SocketTimeoutException.class) @ResponseBody @ResponseStatus(HttpStatus.SERVICE_UNAVAILABLE) ResponseResult<?> socketTimeoutException(SocketTimeoutException exception)
@ExceptionHandler(value = Exception.class) @ResponseBody @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR) ResponseResult<?> exceptionHandler(Exception e)  // 处理其他异常
```

## 包 `com.mcst.easyfk.web.micro.filter`

### RequestBaseFilter

`public class RequestBaseFilter extends OncePerRequestFilter`　注解：`@Slf4j`

**方法**

```java
void doFilterInternal(@NotNull HttpServletRequest httpServletRequest, @NotNull HttpServletResponse httpServletResponse, @NotNull FilterChain filterChain) throws ServletException, IOException
void destroy()
```

## 包 `com.mcst.easyfk.web.prd.annotation`

### Idempotent

`public @interface Idempotent`　注解：`@Target(ElementType.METHOD)` `@Retention(RetentionPolicy.RUNTIME)` `@Documented`　接口幂等注解:同一幂等键在窗口内只允许执行一次业务。 key 支持 SpEL 表达式,基于方法入参,如 "#args[0].orderNo" 或 "#p0.orderNo"; 为空时使用 类名+方法名 作为默认键…

**方法**

```java
String key() default ""  // 幂等键 SpEL 表达式
long ttlSeconds() default 60  // 幂等窗口(秒),默认 60
boolean onDuplicateFail() default true  // 重复请求处理:true=抛 IDEMPOTENT_ERROR;false=直接返回 null(仅支持对象返回值)
```

### RequestToken

`public @interface RequestToken`　注解：`@Target(ElementType.METHOD)` `@Retention(RetentionPolicy.RUNTIME)` `@Documented`　表单重复提交防护注解。 verify=true 时,请求必须携带 Request-Token 头,且该 token 只能被成功消费一次 (原子删除缓存中的 token,删除失败即未签发、已过期或重复提交,返回 REQUE…

**方法**

```java
boolean verify() default true  // 是否校验 Request-Token(默认 true)
@Deprecated long ttlSeconds() default 300  // 已不再使用:token 有效期由 RequestTokenUtil.issue 的 ttlSeconds 决定
```

## 包 `com.mcst.easyfk.web.prd.api`

### IApiClientStore

`public interface IApiClientStore`　API 调用方存储接口：根据 App-Id 获取调用方信息。 默认实现为配置版 PropertiesApiClientStore； 业务可自定义实现（数据库/Redis）并注册同名 Bean 覆盖。

**方法**

```java
ApiAuthProperties.ApiClient getClient(String appId)  // 根据调用方标识获取调用方信息
```

### PropertiesApiClientStore

`public class PropertiesApiClientStore implements IApiClientStore`　配置版 API 调用方存储：从 getClients() 读取。

**构造器**

```java
PropertiesApiClientStore(ApiAuthProperties properties)
```

**方法**

```java
ApiAuthProperties.ApiClient getClient(String appId)
```

## 包 `com.mcst.easyfk.web.prd.aspect`

### ControllerAspect

`public class ControllerAspect implements MethodInterceptor`　注解：`@Slf4j`

**方法**

```java
Object invoke(MethodInvocation methodInvocation) throws Throwable
```

### IdempotentAspect

`public class IdempotentAspect implements MethodInterceptor`　注解：`@Slf4j`　接口幂等切面:同一幂等键在窗口内只允许执行业务一次

**方法**

```java
Object invoke(MethodInvocation methodInvocation) throws Throwable
```

### RequestTokenAspect

`public class RequestTokenAspect implements MethodInterceptor`　注解：`@Slf4j`　表单重复提交切面:原子校验 Request-Token 一次性使用。 缓存键带用户维度,可防止同用户重复提交;但 token 本身不携带签发者强绑定, 跨用户复用同一 token 无法被本机制识别(请求身份仍由 JWT…

**方法**

```java
Object invoke(MethodInvocation methodInvocation) throws Throwable
```

## 包 `com.mcst.easyfk.web.prd.config`

### ControllerAspectConfigure

`public class ControllerAspectConfigure`　注解：`@AutoConfiguration` `@EnableConfigurationProperties({ControllerAspectProperties.class})` `@ConditionalOnProperty(name = "easyfk.config.aspect.controller.open", havingValue = "true", matchIfMissing = true)`

**方法**

```java
@Bean(name = "controllerInterceptorAdvisor") AspectJExpressionPointcutAdvisor controllerInterceptorAdvisor()
@Bean @ConditionalOnMissingBean ControllerAspect controllerAspect()
```

### PrdWebConfig

`public class PrdWebConfig`　注解：`@AutoConfiguration` `@EnableConfigurationProperties({PrdWebProperties.class, ResourceInitProperties.class, ApiAuthProperties.class})` `@ImportAutoConfiguration({ControllerAspectConfigure.class})`

**方法**

```java
@Bean Converter<String, Date> dateConverter()  // 前端字符串形式的时间参数转换处理
@Bean Converter<String, LocalDate> localDateConverter()
@Bean Converter<String, LocalDateTime> localDateTimeConverter()
@Bean Converter<String, LocalTime> localTimeConverter()
@Bean @ConditionalOnMissingBean @ConditionalOnProperty(name = "easyfk.config.web.prd.open-interceptor", havingValue = "true", matchIfMissing = true) WebInterceptorRegister apiInterceptorRegister()
@Bean @ConditionalOnMissingBean @ConditionalOnProperty(name = "easyfk.config.web.prd.open-interceptor", havingValue = "true", matchIfMissing = true) LocalInterceptor localInterceptor()
@Bean @ConditionalOnMissingBean @ConditionalOnProperty(name = "easyfk.config.web.prd.open-request-token", havingValue = "true", matchIfMissing = true) RequestTokenAspect requestTokenAspect()
@Bean @ConditionalOnProperty(name = "easyfk.config.web.prd.open-request-token", havingValue = "true", matchIfMissing = true) DefaultPointcutAdvisor requestTokenAdvisor(RequestTokenAspect requestTokenAspect)
@Bean @ConditionalOnMissingBean @ConditionalOnProperty(name = "easyfk.config.web.prd.open-idempotent", havingValue = "true", matchIfMissing = true) IdempotentAspect idempotentAspect()
@Bean @ConditionalOnProperty(name = "easyfk.config.web.prd.open-idempotent", havingValue = "true", matchIfMissing = true) DefaultPointcutAdvisor idempotentAdvisor(IdempotentAspect idempotentAspect)
@Bean @ConditionalOnMissingBean @ConditionalOnProperty(name = "easyfk.config.web.prd.open-filter", havingValue = "true", matchIfMissing = true) RequestBaseFilter requestBaseFilter()
@Bean @ConditionalOnMissingBean @ConditionalOnProperty(name = "easyfk.config.web.api-auth.open", havingValue = "true") IApiClientStore apiClientStore(ApiAuthProperties apiAuthProperties)
@Bean @ConditionalOnMissingBean(name = "apiAuthFilterRegistration") @ConditionalOnProperty(name = "easyfk.config.web.api-auth.open", havingValue = "true") FilterRegistrationBean<ApiAuthFilter> apiAuthFilterRegistration(ApiAuthProperties apiAuthProperties, IApiClientStore apiClientStore, @Lazy ICacheService cacheService)
@Bean @ConditionalOnMissingBean PrdExceptionHandler prdExceptionHandler()
@Bean @ConditionalOnMissingBean(ObjectMapper.class) ObjectMapper serializingObjectMapper()  // 全局设置Jackson序列化方式
@Bean @ConditionalOnMissingBean @ConditionalOnProperty(name = "easyfk.config.web.cors.open", havingValue = "true") CorsFilter myCorsFilter()  // CORS 过滤器排在所有框架过滤器之前：预检请求直接由其应答，拒绝响应也能带上正确的跨域头
@Bean @ConditionalOnMissingBean @ConditionalOnProperty(name = "easyfk.config.web.prd.security-headers", havingValue = "true", matchIfMissing = true) SecurityHeadersFilter securityHeadersFilter()
@Bean @ConditionalOnProperty(name = "easyfk.config.resource.init.open", havingValue = "true") InitResourceRunner startedCallback()
```

### WebInterceptorRegister

`public class WebInterceptorRegister implements WebMvcConfigurer`

**方法**

```java
void addInterceptors(@NotNull InterceptorRegistry registry)
```

## 包 `com.mcst.easyfk.web.prd.converter`

### DateConverter

`public class DateConverter implements Converter<String, Date>`　springmvc 字符串格式时间参数的转换类，将接收到的string类型的时间转换成Date类型

**方法**

```java
Date convert(String source)
```

### LocalDateConverter

`public class LocalDateConverter implements Converter<String, LocalDate>`　springmvc 字符串格式时间参数的转换类，将接收到的string类型的时间转换成LocalDate类型

**方法**

```java
LocalDate convert(String source)
```

### LocalDateTimeConverter

`public class LocalDateTimeConverter implements Converter<String, LocalDateTime>`　springmvc 字符串格式时间参数的转换类，将接收到的string类型的时间转换成LocalDateTime类型

**方法**

```java
LocalDateTime convert(String source)
```

### LocalTimeConverter

`public class LocalTimeConverter implements Converter<String, LocalTime>`　springmvc 字符串格式时间参数的转换类，将接收到的string类型的时间转换成LocalTime类型

**方法**

```java
LocalTime convert(String source)
```

## 包 `com.mcst.easyfk.web.prd.exception`

### DuplicateSubmitException

`public class DuplicateSubmitException extends BusinessException`　重复提交异常:对应 ErrorRequest.REQUEST_AGAIN / REQUEST_TOKEN_EMPTY

**构造器**

```java
DuplicateSubmitException(String errorCode, String message)
```

### IdempotentException

`public class IdempotentException extends BusinessException`　幂等拦截异常:对应 ErrorRequest.IDEMPOTENT_ERROR

**构造器**

```java
IdempotentException(String errorCode, String message)
```

### PrdExceptionHandler

`public class PrdExceptionHandler`　注解：`@ControllerAdvice` `@Slf4j`　全局异常处理。 HTTP 状态码约定（与 web-micro 一致）：参数校验/请求格式错误 400，未登录 401，无权限 403， 业务异常 200（响应体 code 区分…

**方法**

```java
@ExceptionHandler(value = {BindException.class, ValidationException.class, HandlerMethodValidationException.class}) @ResponseBody @ResponseStatus(HttpStatus.BAD_REQUEST) ResponseResult<?> bindExceptionHandler(Exception e)
@ExceptionHandler(value = {MissingServletRequestParameterException.class, MissingRequestHeaderException.class, MissingServletRequestPartException.class, MethodArgumentTypeMismatchException.class, HttpMediaTypeNotSupportedException.class}) @ResponseBody @ResponseStatus(HttpStatus.BAD_REQUEST) ResponseResult<?> badRequestHandler(Exception e)
@ExceptionHandler(value = HttpMessageNotReadableException.class) @ResponseBody @ResponseStatus(HttpStatus.BAD_REQUEST) ResponseResult<?> messageNotReadableHandler(HttpMessageNotReadableException e)
@ExceptionHandler(value = BusinessException.class) @ResponseBody ResponseEntity<ResponseResult<?>> businessExceptionHandler(BusinessException e)  // 业务异常处理
@ExceptionHandler(value = HttpRequestMethodNotSupportedException.class) @ResponseBody @ResponseStatus(HttpStatus.METHOD_NOT_ALLOWED) ResponseResult<?> methodNotSupportedException(HttpRequestMethodNotSupportedException exception)
@ExceptionHandler(value = {NoResourceFoundException.class, NoHandlerFoundException.class}) @ResponseBody @ResponseStatus(HttpStatus.NOT_FOUND) ResponseResult<?> notFoundHandler(Exception exception)
@ExceptionHandler(value = SocketTimeoutException.class) @ResponseBody @ResponseStatus(HttpStatus.SERVICE_UNAVAILABLE) ResponseResult<?> socketTimeoutException(SocketTimeoutException exception)
@ExceptionHandler(value = Exception.class) @ResponseBody @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR) ResponseResult<?> exceptionHandler(Exception e)  // 处理其他异常
```

## 包 `com.mcst.easyfk.web.prd.filter`

### ApiAuthFilter

`public class ApiAuthFilter extends OncePerRequestFilter`　注解：`@Slf4j`　API 调用鉴权过滤器（OpenAPI 风格，安全级调用方认证）。 校验调用方身份（App-Id + Secret 签名）…

**构造器**

```java
ApiAuthFilter(ApiAuthProperties apiAuthProperties, IApiClientStore apiClientStore, ICacheService cacheService)
```

**方法**

```java
void doFilterInternal(HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse, FilterChain filterChain) throws ServletException, IOException
```

### RequestBaseFilter

`public class RequestBaseFilter extends OncePerRequestFilter`　注解：`@Slf4j`　请求前置基础过滤器：请求头本地线程处理、签名验证（v1 MD5 / v2 HMAC-SHA256）、 时间戳（必填）新鲜度校验、Nonce 原子防重放…

**方法**

```java
void doFilterInternal(HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse, FilterChain filterChain) throws ServletException, IOException
void destroy()
```

### SecurityHeadersFilter

`public class SecurityHeadersFilter extends OncePerRequestFilter`　安全响应头过滤器：补全点击劫持、内容嗅探等安全头，业务可自行覆盖。

**方法**

```java
void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain) throws ServletException, IOException
```

## 包 `com.mcst.easyfk.web.prd.interceptor`

### LocalInterceptor

`public class LocalInterceptor implements HandlerInterceptor`　注解：`@Slf4j`　用户登录拦截器：未登录 401（UN_LOGIN），无权限 403（UN_AUTH），权限服务缺失 500

**方法**

```java
boolean preHandle(@NotNull HttpServletRequest request, @NotNull HttpServletResponse response, @NotNull Object handler) throws Exception
```

## 包 `com.mcst.easyfk.web.prd.properties`

### ApiAuthProperties

`public class ApiAuthProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.web.api-auth")`　API 调用鉴权配置（OpenAPI 风格）：调用方以 App-Id + Secret 签名访问接口。 与业务用户权限（@LoginResource/@AuthResource）解耦： 本鉴权校验"调用方是否有资格调用接…

**字段 / 常量**

```java
boolean open  // 是否开启 API 调用鉴权。开启后除 ignore-uri/静态资源外，所有接口必须携带 App-Id / Api-Timestamp / Api-Nonce / Api-Sign（+ Api-Body）请求头。
Duration timeout = Duration.ofSeconds(150)  // 时间戳新鲜度窗口与 Nonce 防重放 TTL，默认 150 秒
List<String> ignoreUri  // 忽略 API 鉴权的 URI（精确或 Ant 模式），如 /health、/api/public/**
List<ApiClient> clients = new ArrayList<>()  // 内置调用方列表（配置方式，生产建议使用数据库/缓存并实现 IApiClientStore 自定义加载）
```

#### ApiAuthProperties.ApiClient

`public static class ApiClient`　Lombok：`@Data`　API 调用方

**字段 / 常量**

```java
String appId  // 调用方唯一标识（请求头 App-Id）
String secret  // 调用方密钥（仅服务端持有，用于签名验证）
boolean enabled = true  // 是否启用，false 时该调用方所有请求被拒绝
List<String> allowedUris  // 允许访问的 URI（精确或 Ant 模式）；为空表示允许全部接口
```

### ControllerAspectProperties

`public class ControllerAspectProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.aspect.controller")`

**字段 / 常量**

```java
Boolean open = Boolean.TRUE
String pointcut  // 切面表达式
```

### PrdWebProperties

`public class PrdWebProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.web.prd")`　web-prd 组件开关，实际由 PrdWebConfig 中的 @ConditionalOnProperty 读取，此处声明用于配置元数据

**字段 / 常量**

```java
boolean openInterceptor = true  // 是否开启登录/权限拦截器（LocalInterceptor）
boolean openFilter = true  // 是否开启请求前置过滤器（RequestBaseFilter：上下文还原、签名防重放）
boolean openRequestToken = true  // 是否开启 @RequestToken 表单防重
boolean openIdempotent = true  // 是否开启 @Idempotent 接口幂等
boolean securityHeaders = true  // 是否开启安全响应头过滤器
```

### ResourceInitProperties

`public class ResourceInitProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.resource.init")`

**字段 / 常量**

```java
Boolean open = Boolean.FALSE  // 是否生成资源数据
String group = "default"  // 生成资源组名称，default 表示所有组,多个用英文逗号隔开，initResource 为true 生效
Boolean normal = Boolean.FALSE  // 是否生成非权限资源，initResource 为true 生效
```

## 包 `com.mcst.easyfk.web.prd.runner`

### InitResourceRunner

`public class InitResourceRunner implements CommandLineRunner, ApplicationContextAware`　注解：`@Slf4j` `@Order(0)`

**方法**

```java
void run(String... args)
void setApplicationContext(@NotNull ApplicationContext applicationContext) throws BeansException
```

## 包 `com.mcst.easyfk.web.prd.util`

### ApiSignUtil

`public final class ApiSignUtil`　API 调用鉴权签名工具（OpenAPI 风格，HMAC-SHA256）。 签名原文： App-Id={appId}&Timestamp={timestamp}&Nonce={nonce}&Method={method}…

**方法**

```java
static String buildSignText(String appId, String timestamp, String nonce, String method, String uri, String bodyHash)  // 构造签名原文
static String sign(String appId, String timestamp, String nonce, String method, String uri, String bodyHash, String secret)  // 计算签名
static boolean verify(String appId, String timestamp, String nonce, String method, String uri, String bodyHash, String secret, String sign)  // 验证签名（常量时间比较，大小写不敏感）
```

### BodyCachingRequestWrapper

`public class BodyCachingRequestWrapper extends HttpServletRequestWrapper`　Lombok：`@Getter`　注解：`@Slf4j`　请求体缓存包装器：预读并缓存请求体，供 v2 签名计算摘要， 同时保证下游（Controller）仍可重复读取输入流…

**字段 / 常量**

```java
static final long MAX_CACHE_BODY_SIZE = 2 * 1024 * 1024L  // 最大缓存请求体字节数，超过则标记溢出并放弃缓存，避免内存被大请求打满
final byte[] body
final boolean overflow
@Getter(lombok.AccessLevel.NONE) final byte[] overflowPrefix  // 溢出时已预读的字节，下游读取时需先回放再续读原始流
```

**构造器**

```java
BodyCachingRequestWrapper(HttpServletRequest request) throws IOException
```

**方法**

```java
static boolean shouldCache(HttpServletRequest request)  // 是否需要缓存请求体（v2 签名场景）
ServletInputStream getInputStream() throws IOException
BufferedReader getReader() throws IOException
```

### ClientIpUtil

`public class ClientIpUtil`

**方法**

```java
static String getClientIp(HttpServletRequest request)
```

### FailRequestUtil

`public class FailRequestUtil`　过滤器/拦截器拒绝请求时写出 JSON 错误响应。 跨域响应头由 CorsFilter 负责（其顺序先于框架其他过滤器），此处不写跨域头。

**方法**

```java
static ResponseResult<?> failRequestInfo(ErrorRequest errorRequest)
static void failRequest(HttpServletResponse httpServletResponse, ErrorRequest errorRequest) throws IOException
static void failRequest(HttpServletResponse httpServletResponse, int httpStatus, ResponseResult<?> responseResult) throws IOException
```

### RequestTokenUtil

`public final class RequestTokenUtil`　Request-Token 一次性令牌下发工具

**方法**

```java
static String issue(ICacheService cacheService, String userId, long ttlSeconds)  // 生成一次性 Request-Token 并写入缓存
static String buildKey(String userId, String token)  // 构造缓存键(带用户维度,匿名场景使用 anonymous)
```

### RequestUtil

`public class RequestUtil`

**方法**

```java
static String getRequestUrl(HttpServletRequest request)
static String getCanonicalUri(HttpServletRequest request)  // 签名用规范 URI：去掉 contextPath 的原始路径（不解码）；存在 query string 时追加 ? + 原始 query string（不解码、不排序）。 v2 接口签名与 API 调用方鉴权共用此口径。
static String getRefererUrl(HttpServletRequest request)
static boolean isAjax(HttpServletRequest request)
static boolean isWeChatRequest(HttpServletRequest request)  // 检测是不是使用微信浏览器访问
static boolean isQqRequest(HttpServletRequest request)
```

### SqlGuardUtil

`public final class SqlGuardUtil`　web 入口层 SQL 注入防护：查询字段名、关键词白名单/格式校验（第一道防线， 根治在 repository / orm 层的参数化与列名校验）。

**方法**

```java
static void assertFieldNames(String[] fields, String paramName)  // 校验字段名数组，非法即抛业务异常
static void assertKeyword(String keyword)  // 校验关键词：长度与危险字符
static void validateSearchRequest(SearchRequest<?> searchRequest)  // 校验 SearchRequest 中由客户端可控的字段名与关键词
```

### StaticUriUtil

`public class StaticUriUtil`

**方法**

```java
static boolean isStaticUrl(String url)
```

## 包 `com.mcst.easyfk.web.prd.vo`

### LoginRequestVO

`public class LoginRequestVO implements Serializable`　Lombok：`@Data` `@NoArgsConstructor` `@Accessors(chain = true)` `@AllArgsConstructor`　注解：`@Schema(description = "登录数据对象")`

**字段 / 常量**

```java
@Schema(description = "图形验证码Token", name = "picToken") String picToken
@NotBlank(message = "登录账号不可为空") @Schema(description = "账号、手机号、邮箱等", name = "loginAccount") String loginAccount
@Schema(description = "登录密码，加密", name = "password") String password
@Schema(description = "客户端类型", name = "clientType") String clientType  // 客户端类型
@Schema(description = "设备信息", name = "deviceInfo") String deviceInfo  // 设备信息
@Schema(description = "图片验证码", name = "picCode") String picCode
@Schema(description = "手机验证码", name = "smsCode") String smsCode
@Schema(description = "登录类型，accountAndPic：图片验证码+账户+密码，account：账户+密码，mobile：手机号+短信验证码", name = "type") String type
@Schema(description = "登录成功后的跳转URL", name = "returnUrl") String returnUrl
```

### RegistryRequestVO

`public class RegistryRequestVO implements Serializable`　Lombok：`@Data` `@NoArgsConstructor` `@Accessors(chain = true)`　注解：`@Schema`

**字段 / 常量**

```java
@Schema(description = "手机号码", name = "phone") String phone
@Schema(description = "手机验证码", name = "smsCode") String smsCode
@Schema(description = "登录密码，密文", name = "loginPwd") String loginPwd
@Schema(description = "邮箱", name = "email") String email
@Schema(description = "用户名", name = "name") String name
@Schema(description = "推荐人", name = "referrerId") String referrerId  // 推荐人
@Schema(description = "注册渠道", name = "registryChannel") String registryChannel
```

### SiteLoginSuccessVO

`public class SiteLoginSuccessVO implements Serializable`　Lombok：`@Data` `@NoArgsConstructor` `@Accessors(chain = true)` `@AllArgsConstructor`　注解：`@Schema(description = "登录成功后返回前端的数据")`

**字段 / 常量**

```java
@Schema(description = "Token信息", name = "accessToken") String accessToken
@Schema(description = "当前登录用户头像信息", name = "headImage") String headImage
@Schema(description = "登录成功后的跳转URL", name = "returnUrl") String returnUrl
@Schema(description = "状态", name = "status") Integer status
```
