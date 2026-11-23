# easyfk-gateway API 签名速查（easyfk 3.2.12）

> 坐标：`com.mcst:easyfk-gateway`　源码：`easyfk-base/easyfk-gateway`
> 由 `scripts/gen-api.py` 从 9 个源文件自动提取，共 9 个类型、15 个方法/构造器、11 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-gateway-skill.md](../modules/easyfk-gateway-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 配置项（@ConfigurationProperties）

### `easyfk.config.gateway` ← GatewayFilterProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `filter-order` | `int` | `Ordered.HIGHEST_PRECEDENCE + 100` | RequestGatewayFilter（请求头/签名/会话阶段）的执行顺序，默认 HIGHEST_PRECEDENCE + 100 |
| `api-doc-path` | `String` | `"/v3/api-docs"` | 接口文档路径后缀：请求路径以此结尾时视为文档请求，跳过签名与权限校验；为空则不放行任何文档请求 |
| `max-sign-body-size` | `DataSize` | `DataSize.ofMegabytes(2)` | v2 签名时缓存请求体的最大字节数 |


## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `easyfk-gateway` | `config.com.mcst.easyfk.gateway.config.GatewayFilterConfigure` |

## 类型索引

- `com.mcst.easyfk.gateway.config`：[GatewayFilterConfigure](#gatewayfilterconfigure)
- `com.mcst.easyfk.gateway.constant`：[GatewayAttributeConstant](#gatewayattributeconstant)
- `com.mcst.easyfk.gateway.filter`：[GatewayAuthorizationFilter](#gatewayauthorizationfilter)、[ICustomGatewayFilter](#icustomgatewayfilter)、[IExtendGatewayFilter](#iextendgatewayfilter)、[RequestGatewayFilter](#requestgatewayfilter)
- `com.mcst.easyfk.gateway.properties`：[GatewayFilterProperties](#gatewayfilterproperties)
- `com.mcst.easyfk.gateway.util`：[FailRequestUtil](#failrequestutil)、[GatewayContextUtil](#gatewaycontextutil)

## 包 `com.mcst.easyfk.gateway.config`

### GatewayFilterConfigure

`public class GatewayFilterConfigure`　注解：`@AutoConfiguration` `@EnableConfigurationProperties(GatewayFilterProperties.class)`

**方法**

```java
@Bean @ConditionalOnMissingBean RequestGatewayFilter requestHeaderGatewayFilter()
@Bean @ConditionalOnMissingBean GatewayAuthorizationFilter gatewayAuthorizationFilter()
```

## 包 `com.mcst.easyfk.gateway.constant`

### GatewayAttributeConstant

`public interface GatewayAttributeConstant`　网关请求级数据在 ServerWebExchange 属性中的键。 响应式链路会切换线程，网关不依赖 ThreadLocal 跨阶段传递数据，统一存放在 exchange 属性中。

**字段 / 常量**

```java
String PREFIX = "easyfk.gateway."
String BYPASS = PREFIX + "bypass"  // 跳过网关校验（CORS 预检、文档请求、自定义过滤器模式），值为 Boolean.TRUE
String TRACE_ID = PREFIX + "traceId"  // 本次请求的 TraceId（String）
String REQUEST_HEADERS = PREFIX + "requestHeaders"  // 解析后的请求头（RequestHeaders），会话解析后含 loginToken
String USER_DATA = PREFIX + "userData"  // 当前登录用户（UserData），未登录时不存在该属性
String ORIGINAL_PATH = PREFIX + "originalPath"  // 客户端请求的网关侧原始路径（String，路由过滤器改写前）
String DOWNSTREAM_PATH = PREFIX + "downstreamPath"  // 下游服务实际收到的路径（String，权限校验使用）
```

## 包 `com.mcst.easyfk.gateway.filter`

### GatewayAuthorizationFilter

`public class GatewayAuthorizationFilter implements GlobalFilter, Ordered`　注解：`@Slf4j`　网关第二阶段过滤器：三级 URI 权限校验与 IExtendGatewayFilter 扩展调用。 顺序为 ROUTE_TO_URL_FILTER_ORDER + 1：此时 StripPrefix/RewritePath…

**字段 / 常量**

```java
static final int ORDER = RouteToRequestUrlFilter.ROUTE_TO_URL_FILTER_ORDER + 1
```

**方法**

```java
@PostConstruct void init()
Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain)
int getOrder()
```

### ICustomGatewayFilter

`public interface ICustomGatewayFilter`

**方法**

```java
Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain)  // 自定义网关拦截器
```

### IExtendGatewayFilter

`public interface IExtendGatewayFilter`

**方法**

```java
void doExtendIntercept(ServerWebExchange exchange)  // 在默认校验全部通过、转发下游之前同步调用（可存在多个实现，按 @Order 顺序执行），此时路由过滤器已执行。 方法可能在事件循环线程或 boundedElastic 线程执行，不应包含阻塞操作…
```

### RequestGatewayFilter

`public class RequestGatewayFilter implements GlobalFilter, Ordered`　注解：`@Slf4j`　网关第一阶段过滤器（路由过滤器之前执行）：请求头解析、TraceId、签名验证（v1 MD5 / v2 HMAC-SHA256，与 web-prd 一致）、 时间戳新鲜度、Nonce 原子防重放…

**方法**

```java
@PostConstruct void init()
Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain)
int getOrder()
```

## 包 `com.mcst.easyfk.gateway.properties`

### GatewayFilterProperties

`public class GatewayFilterProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.gateway")`　网关过滤器配置

**字段 / 常量**

```java
int filterOrder = Ordered.HIGHEST_PRECEDENCE + 100  // RequestGatewayFilter（请求头/签名/会话阶段）的执行顺序，默认 HIGHEST_PRECEDENCE + 100
String apiDocPath = "/v3/api-docs"  // 接口文档路径后缀：请求路径以此结尾时视为文档请求，跳过签名与权限校验；为空则不放行任何文档请求
DataSize maxSignBodySize = DataSize.ofMegabytes(2)  // v2 签名时缓存请求体的最大字节数
```

## 包 `com.mcst.easyfk.gateway.util`

### FailRequestUtil

`public class FailRequestUtil`　网关失败响应：HTTP 状态码取 getHttpStatus()（与 web 模块一致）， 响应体为 ResponseResult{code,msg}…

**方法**

```java
static Mono<Void> failRequest(ServerWebExchange exchange, ErrorRequest errorRequest)
static Mono<Void> failRequest(ServerWebExchange exchange, ErrorRequest errorRequest, CorsConfigurationSource corsSource)
static HttpStatusCode httpStatus(ErrorRequest errorRequest)
static CorsConfigurationSource buildCorsSource(GlobalCorsProperties globalCorsProperties)  // 基于 Spring Cloud Gateway 的 globalcors 配置构建 CORS 配置源，未配置时返回 null
```

### GatewayContextUtil

`public class GatewayContextUtil`　网关阻塞调用工具：在 boundedElastic 线程上执行阻塞逻辑（Redis、RPC、JWT 等）， 执行期间把 exchange 中的请求数据放入 ThreadLocal 上下文，并在同一线程内清理。

**方法**

```java
static <T> Mono<T> blocking(ServerWebExchange exchange, Callable<T> callable)  // 在弹性线程池中执行阻塞逻辑，callable 不允许返回 null
```
