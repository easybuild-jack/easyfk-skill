# easyfk-component-rpc Skill 参考文档

> 模块：`easyfk-component/component-rpc`（rpc-dubbo / rpc-cloud）
> 坐标：`com.mcst:rpc-dubbo`、`com.mcst:rpc-cloud`（版本由 easyfk-dependencies 管理）
> 依据：两个子模块源码 + `rpc-dubbo开发手册.md`、`rpc-dubbo技术特点.md`、`rpc-cloud开发手册.md`、`rpc-cloud技术特点.md`
> 文档与源码不一致时 **以源码为准**，差异见文末「复查记录」。
> 与 easyfk-base 的 `easyfk-remote`（remote-dubbo / remote-cloud，服务接口层封装）配合使用，本模块只负责 RPC 通道的上下文透传与异常解码。

---

## 1. 模块定位

| 子模块 | 依赖 | 提供 |
|---|---|---|
| rpc-dubbo | dubbo-spring-boot-starter 3.3.7、dubbo-registry-nacos 3.3.7、web-base | `DubboFilter`（TraceId / Access-Token / Language 透传 + Provider 端上下文重建与恢复）、`DubboDirectInvoker`（直连调用工具，自动注册） |
| rpc-cloud | spring-cloud-starter-openfeign（排除 starter-logging、ribbon）、spring-cloud-loadbalancer、web-common；Spring Cloud 2025.0.3 | `FeignClientInterceptor`（TraceId / Access-Token / Language 请求头）、`FeignErrorDecoder`（错误响应 → `BusinessException`） |

两个子模块都通过父工程 `api easyfk-core`。

---

## 2. rpc-dubbo

### 2.1 DubboFilter（自动生效）

- 通过 Dubbo SPI 注册：`META-INF/dubbo/org.apache.dubbo.rpc.Filter` → `dubboFilter=com.mcst.easyfk.rpc.dubbo.filter.DubboFilter`。
- `@Activate(group = {CONSUMER, PROVIDER}, order = -1000)`，无需配置。
- 根据 `invoker.getUrl()` 的 `side` 参数判断两端，透传的头与 rpc-cloud `FeignClientInterceptor`、web-micro `RequestBaseFilter` 一致：
  - **Consumer**：attachment 写入 `TRACE_ID`（`TraceIdContext`）、`Access-Token`、`Language`（`RequestHeaderContext.getRequestHeaders()` 的 accessToken / language），值为空的不写。
  - **Provider**：调用前先快照当前线程的 TraceId / MDC / `RequestHeaderContext` / `UserDataContext`；然后按 attachment 设置 `TraceIdContext` + `MDC["TRACE_ID"]`（未传时清除，不生成新 traceId），用 `Access-Token` / `Language` 新建 `RequestHeaders` 写入 `RequestHeaderContext`（都未传时清除），并清除 `UserDataContext`（用户信息由业务按 token 自行加载）。
  - **Provider 调用结束（finally）**：恢复调用前的快照（快照为空则清除），injvm 等同线程场景不会清掉调用方上下文；异常只打 warn。
- 不透传 `UserData`、`ContextDataManager` 中的其他数据及其他请求头；需要时业务自行写 Dubbo Filter 或在调用前 `RpcContext.getClientAttachment().setAttachment(...)`。

### 2.2 典型配置

```yaml
dubbo:
  application:
    name: user-service
  protocol:
    name: dubbo
    port: 20880
  registry:
    address: nacos://192.168.1.100:8848
    parameters:
      namespace: dev
  consumer:
    timeout: 3000
    retries: 0        # 非幂等接口必须为 0
    check: false
  scan:
    base-packages: com.example.service.impl
```

```java
@DubboService(version = "1.0.0")
public class UserServiceImpl implements UserService { ... }

@DubboReference(version = "1.0.0", check = false)
private UserService userService;
```
- DTO 实现 `Serializable`；接口放在独立 API 模块供两端引用。

### 2.3 DubboDirectInvoker（直连调用）

`DubboConfig`（`@AutoConfiguration`，已在 `META-INF/spring/...AutoConfiguration.imports` 中声明）自动注册 `DubboDirectInvoker` Bean（`@ConditionalOnMissingBean`），直接注入即可：

```java
@Resource
private DubboDirectInvoker dubboDirectInvoker;
```

```java
// 泛化调用：不依赖接口 jar，POJO 参数可传 Map
Object r = dubboDirectInvoker.invokeGeneric(
        "com.example.api.UserService", "10.0.0.8", 20880,
        "getUserById", new String[]{"java.lang.Long"}, new Object[]{1L},
        null, "1.0.0", 3000, 0);

// 强类型调用：反射定位方法
Object r2 = dubboDirectInvoker.invokeTyped(
        UserService.class, "10.0.0.8", 20880,
        "getUserById", new Class<?>[]{Long.class}, new Object[]{1L},
        null, "1.0.0", null, null);   // timeout 默认 3000ms，retries 默认 0
```
- URL 形如 `dubbo://host:port?group=x&version=y`，`check=false`，绕过注册中心。
- **每次调用都新建并销毁 `ReferenceConfig`**，开销大，只适合调试、运维、低频编排；高频调用请用 `@DubboReference` 或自行缓存 `ReferenceConfig`。
- `invokeTyped` 声明 `throws Exception`，业务异常被包装在 `InvocationTargetException` 中，需要 `getCause()`。

---

## 3. rpc-cloud

### 3.1 自动配置

`FeignConfigure`（在 `AutoConfiguration.imports` 中）注册：

| Bean | 条件 | 作用 |
|---|---|---|
| `FeignErrorDecoder` | `@ConditionalOnMissingBean(ErrorDecoder.class)`（容器中已有任意 `ErrorDecoder` 时不注册） | 全局 ErrorDecoder |
| `FeignClientInterceptor` | 无条件 | 全局 RequestInterceptor |

Spring Cloud OpenFeign 会把容器中的 `ErrorDecoder` / `RequestInterceptor` Bean 应用到所有 Feign 客户端。

**组件不加 `@EnableFeignClients`**，业务启动类必须自行添加：

```java
@SpringBootApplication
@EnableFeignClients(basePackages = "com.example.client")
public class OrderApplication { }
```

### 3.2 FeignClientInterceptor

- 添加请求头 **`TRACE_ID`**（`TraceIdContext`）、**`Access-Token`**、**`Language`**（`RequestHeaderContext` 的 accessToken / language），值为空或业务已显式设置同名头时跳过。
- 不传用户信息等其他头；需要时自定义 `RequestInterceptor` Bean（会与本拦截器叠加生效）。

### 3.3 FeignErrorDecoder（仅非 2xx 响应触发）

1. 以 UTF-8 读取响应体（无 body 或读取失败视为空）。
2. 体是 JSON 对象且 `code` 非空、不是 `SystemError`/`SystemErrorMsg` → `new BusinessException(code, msg)`。
3. 其余情况（无 body、非 JSON 如网关 HTML、缺少 code、系统错误 code）→ `RuntimeException(I18NUtil.getMessage("SystemErrorMsg", "i18n/webMessages"))`，并记 warn 日志。

与服务端配合：`web-micro` 的 `MicroExceptionHandler` 返回 HTTP 500 + `ResponseResult{code,msg}`（系统异常 code 为 `SystemError`），web-prd 的系统异常 code 为 `SystemErrorMsg`，两者都会还原为国际化系统异常，业务异常还原为 `BusinessException`。

```java
try {
    return userClient.getUserById(id);
} catch (BusinessException e) {
    log.warn("远程业务异常 code={}, msg={}", e.getErrorCode(), e.getErrorMsg());
    throw e;
}
```

### 3.4 常用 OpenFeign 配置

```yaml
spring:
  cloud:
    openfeign:
      client:
        config:
          default:
            connect-timeout: 5000
            read-timeout: 10000
            logger-level: BASIC
      circuitbreaker:
        enabled: true          # 使用 fallback/fallbackFactory 时必须开启，并引入断路器实现
```

### 3.5 启用 `@FeignClient(fallback = ...)` 降级

rpc-cloud **不自带断路器实现**，也不开启 `spring.cloud.openfeign.circuitbreaker.enabled`，默认 fallback/fallbackFactory 不生效（调用失败直接抛 FeignErrorDecoder 解码出的异常）。启用步骤：

1. 业务模块引入一个 Spring Cloud CircuitBreaker 实现（二选一）：
   - `org.springframework.cloud:spring-cloud-starter-circuitbreaker-resilience4j`（版本由 Spring Cloud BOM 2023.0.x 管理）；
   - 或已使用 Sentinel 时引入 `com.alibaba.cloud:spring-cloud-circuitbreaker-sentinel`（版本由 Spring Cloud Alibaba BOM 管理）。
2. 配置 `spring.cloud.openfeign.circuitbreaker.enabled: true`。
3. fallback 类实现 Feign 接口并注册为 Bean：

```java
@FeignClient(name = "user-service", fallback = UserClientFallback.class)
public interface UserClient { @GetMapping("/user/{id}") UserDTO getUserById(@PathVariable Long id); }

@Component
public class UserClientFallback implements UserClient {
    @Override public UserDTO getUserById(Long id) { return null; }
}
```
- 开启后 `FeignErrorDecoder` 抛出的 `BusinessException` 也会进入 fallback（会被断路器计为失败）；业务异常需要透传给调用方时使用 `fallbackFactory` 拿到原始异常后重新抛出，或在断路器配置中忽略 `BusinessException`。

---

## 4. 生成代码时的规则

### Do
- Dubbo 服务：`@DubboService` / `@DubboReference`，显式设置 `version`、`timeout`；非幂等接口 `retries = 0`。
- 需要直连调用时直接注入 `DubboDirectInvoker`（自动注册），并只用于低频场景。
- Feign：启动类加 `@EnableFeignClients(basePackages=...)`；调用方捕获 `BusinessException` 并用 `getErrorCode()` / `getErrorMsg()`。
- TraceId / Access-Token / Language 已由 Dubbo Filter 与 Feign 拦截器自动透传；需要透传其他头或用户信息时，Feign 写自定义 `RequestInterceptor`，Dubbo 写自定义 Filter 或设置 attachment；Provider 端按 Access-Token 自行加载用户信息。
- 使用 Feign fallback 时按 3.5 引入断路器实现并开启 `spring.cloud.openfeign.circuitbreaker.enabled`。
- 自定义错误解码：声明任意 `ErrorDecoder` Bean 即可替换默认的 `FeignErrorDecoder`。
- Dubbo 原生异步：接口返回 `CompletableFuture<T>`，或使用 `RpcContext` 异步 API；不要用 `CompletableFuture.supplyAsync` 包装同步调用冒充异步。

### Don't
- 不要假设 rpc-dubbo 会透传 `UserData` 或 `ContextDataManager` 的其他上下文（只透传 TraceId / Access-Token / Language）。
- 不要在高频路径用 `DubboDirectInvoker`。
- 不要在 Feign 调用中使用 `e.getCode()`（`BusinessException` 没有该方法）。
- 不要按旧手册使用 `traceId` 作为请求头名（实际是 `TRACE_ID`）。
- 不要期望未引入断路器实现时 `@FeignClient(fallback=...)` 生效。

---

## 5. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | rpc-dubbo开发手册 §1/§3/§7.2；技术特点 | DubboFilter 透传 TraceId **和 AccessToken**；Provider 通过 `ContextDataManager` 初始化上下文，结束后 `ContextDataManager.clearContext()` | 只透传 `TRACE_ID`；Provider 只设置 `TraceIdContext` 和 MDC；清理时直接调用 `TraceIdContext.remove()`、`MDC.clear()`、`RequestHeaderContext.remove()`、`UserDataContext.remove()`，没有使用 ContextDataManager，也没有 AccessToken 处理 **已修复**：Consumer 端额外透传 `RequestHeaderContext` 的 `Access-Token`、`Language`（与 Feign 拦截器一致），Provider 端据此重建 `RequestHeaderContext`、清除 `UserDataContext`，结束后恢复调用前快照。 |
| 2 | rpc-dubbo（文档未提及） | — | `DubboDirectInvoker` / `DubboConfig` 存在，但模块没有 `META-INF/spring/...AutoConfiguration.imports`，Bean 不会自动注册 **已修复**：新增 imports 文件声明 `DubboConfig`，`DubboDirectInvoker` 自动注册。 |
| 3 | rpc-dubbo 源码 | — | Provider 端无论是否收到 traceId 都会在 finally 执行 `MDC.clear()` 等清理；若 Provider 与 Consumer 在同一线程执行（如 injvm 本地调用），会清掉调用方线程的上下文（按源码推断） **已修复**：Provider 端调用前快照 TraceId/MDC/RequestHeaders/UserData，finally 中恢复（快照为空才清除）。 |
| 4 | rpc-dubbo开发手册 §8.4 | “Dubbo 3 原生异步支持” 示例使用 `CompletableFuture.supplyAsync(() -> userService.getUserById(id))` | 这只是把同步调用放到公共线程池，不是 Dubbo 原生异步；原生异步应让接口返回 `CompletableFuture` 或使用 `RpcContext` 异步 API |
| 5 | rpc-dubbo开发手册 §2 | Maven 坐标 `com.mcst:rpc-dubbo` | 坐标正确；但 easyfk-dependencies 的 catalog 别名拼写为 `rpc-duboo` **已修复**：catalog 增加正确别名 `rpc-dubbo`。 |
| 6 | rpc-cloud开发手册 §3/§7；技术特点 | 请求头名为 `traceId` | 实际请求头为 `TRACE_ID`（`RequestHeaderConstant.TRACE_ID`） |
| 7 | rpc-cloud开发手册 §5.4 | `catch (BusinessException e)` 中使用 `e.getCode()` | `BusinessException` 的字段是 `errorCode` / `errorMsg`，应使用 `getErrorCode()` / `getErrorMsg()`，示例无法编译 |
| 8 | rpc-cloud开发手册 §3/§5.4 | code 为 SystemError **或解析失败时**返回国际化系统错误 | 只捕获 `IOException` 和 code 读取阶段的异常：响应无 body 时 `response.body()` 为 null 导致 NPE 直接抛出；非 JSON 响应体（如网关 HTML）会抛 fastjson2 `JSONException`；JSON 中没有 `code` 字段（如 Spring 默认错误体）会得到 `BusinessException(null, null)` **已修复**：无 body、读取失败、非 JSON、缺少 code 均返回国际化系统异常。 |
| 9 | rpc-cloud开发手册 §5.4 | 系统异常 code 为 `SystemError` | 只与 web-micro 的 `MicroExceptionHandler` 一致；web-prd 的系统异常 code 为 `SystemErrorMsg`，会被解码成 `BusinessException("SystemErrorMsg", ...)` **已修复**：`SystemError` 与 `SystemErrorMsg` 都按系统异常处理。 |
| 10 | rpc-cloud开发手册 §8.1；技术特点 | `@FeignClient(fallback = ...)` 降级 | 组件未引入断路器实现，也未开启 `spring.cloud.openfeign.circuitbreaker.enabled`，fallback 默认不生效 **已修复**（文档）：3.5 说明启用方式（引入 `spring-cloud-starter-circuitbreaker-resilience4j` 或 `spring-cloud-circuitbreaker-sentinel` + `spring.cloud.openfeign.circuitbreaker.enabled=true`）；本地离线仓库无 resilience4j 依赖，且断路器实现应由业务选择，组件不内置。 |
| 11 | rpc-cloud开发手册 §4 | “声明一个 `FeignErrorDecoder` 类型的 Bean 即可覆盖” | 正确：条件按 `FeignErrorDecoder` 类型判断，声明其他 `ErrorDecoder` 实现不会让默认 Bean 失效，此时容器中有两个 ErrorDecoder（OpenFeign 获取时可能冲突，未验证） **已修复**：条件改为 `@ConditionalOnMissingBean(ErrorDecoder.class)`，声明任意 ErrorDecoder 都会替换默认 Bean。 |
| 12 | rpc-cloud开发手册 §2 | 已排除 jackson 等冲突依赖 | 实际排除的是 `com.fasterxml.jackson.core` 整个 group；Jackson 由 web-common/Spring Boot Web 提供，单独使用 rpc-cloud 而不引入 Web 时需自行补 Jackson **已修复**：移除对 `com.fasterxml.jackson.core` 的排除，Jackson 随 openfeign starter 传递。 |
