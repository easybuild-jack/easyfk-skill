# easyfk-web/web-micro 开发文档

## 1. 模块概述

`web-micro` 是 EasyFK 框架为**微服务（网关后端服务）**提供的 Web 基础设施模块。适用于经过 `easyfk-gateway` 网关转发后的下游微服务，提供以下核心能力：

- **请求上下文还原**：从请求头中提取 TraceId、AccessToken、Language 等信息，还原为 ThreadLocal 上下文
- **用户数据上下文加载**：通过 JWT 解析获取登录用户，从缓存中加载完整的 UserData
- **全局异常处理**：统一处理参数校验异常、业务异常和系统异常，返回标准化的 ResponseResult
- **Jackson 全局序列化配置**：Java 8 时间类型的统一格式化

本模块是 `easyfk-web` 多层模块体系中面向微服务场景的组合模块，依赖 `web-simple`（Web 容器 + easyfk-core）、`web-common`（通用配置 + 工具）、`web-base`（JWT + 上下文管理）。

---

## 2. 依赖关系

### 2.1 模块依赖图

```
web-micro
├── web-simple
│   ├── spring-boot-starter-web（排除 Tomcat + Logging）
│   ├── spring-boot-starter-undertow（默认容器）
│   └── easyfk-core
└── web-common
    ├── web-base
    │   ├── easyfk-authority（用户权限管理）
    │   └── easyfk-core（编译期）
    ├── easyfk-core（编译期）
    └── spring-web（编译期）
```

### 2.2 web-micro build.gradle

```groovy
dependencies {
    api project(':easyfk-web:web-simple')
    api project(':easyfk-web:web-common')
}
```

### 2.3 web-simple build.gradle

```groovy
dependencies {
    api('org.springframework.boot:spring-boot-starter-web') {
        exclude group: 'org.springframework.boot', module: 'spring-boot-starter-logging'
        exclude group: 'org.springframework.boot', module: 'spring-boot-starter-tomcat'
    }
    api project(':easyfk-core')
    api 'org.springframework.boot:spring-boot-starter-undertow'
}
```

### 2.4 web-common build.gradle

```groovy
dependencies {
    compileOnly project(':easyfk-core')
    compileOnly('org.springframework:spring-web')
    api project(':easyfk-web:web-base')
}
```

### 2.5 web-base build.gradle

```groovy
dependencies {
    compileOnly project(':easyfk-core')
    api project(':easyfk-authority')
}
```

---

## 3. 包结构

```
easyfk-web/
├── web-simple/                         # Web 容器层
│   └── (spring-boot-starter-web + Undertow + easyfk-core)
│
├── web-base/                           # 基础管理层
│   ├── config/
│   │   └── WebBaseConfig.java          # 自动配置（JwtManager + ContextDataManager）
│   ├── manager/
│   │   ├── JwtManager.java             # JWT 创建与解析
│   │   └── ContextDataManager.java     # 上下文数据管理器
│   ├── properties/
│   │   └── JwtProperties.java          # JWT 配置
│   └── vo/
│       └── ParseJwtResult.java         # JWT 解析结果
│
├── web-common/                         # 通用配置层
│   ├── config/
│   │   └── WebCommonConfig.java        # 注册属性配置
│   ├── properties/
│   │   ├── InterceptProperties.java    # 拦截器配置
│   │   ├── SecurityProperties.java     # 安全配置
│   │   └── CorsProperties.java         # 跨域配置
│   ├── constant/
│   │   ├── ErrorRequest.java           # 错误请求枚举（15 种错误类型）
│   │   ├── RequestConstant.java        # 请求常量
│   │   └── SignConstant.java           # 签名常量
│   ├── util/
│   │   ├── InterceptorExcludeUriUtil.java  # URI 排除匹配工具
│   │   └── CheckIgnoreSecurityUriUtil.java # 安全忽略 URI 工具
│   ├── vo/
│   │   └── FilterChainData.java        # 过滤链传递数据
│   └── resources/
│       └── i18n/
│           ├── webMessages_zh_CN.properties  # 简体中文
│           ├── webMessages_zh_TW.properties  # 繁体中文（台湾）
│           ├── webMessages_zh_HK.properties  # 繁体中文（香港）
│           ├── webMessages_en_US.properties  # 英文
│           └── webMessages_vi_VN.properties  # 越南语
│
└── web-micro/                          # 微服务组合层（本模块）
    ├── config/
    │   └── MicroWebConfig.java         # 自动配置
    ├── exception/
    │   └── MicroExceptionHandler.java  # 全局异常处理
    └── filter/
        └── RequestBaseFilter.java      # 请求前置过滤器
```

---

## 4. 配置属性

### 4.1 JWT 配置

配置前缀：`easyfk.config.web.jwt`

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `secret` | String | 内置默认值 | JWT 签名私钥，生产环境务必覆盖 |
| `salt` | String | 内置默认值 | 签名盐值，与 `secret` 共同派生签名密钥，生产环境务必覆盖 |
| `expires-second` | Integer | `10800`（3 小时） | JWT 过期时间（秒），`<=0` 按默认值处理 |

### 4.2 拦截器配置

配置前缀：`easyfk.config.web.intercept`

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `exclude-paths` | List\<String\> | null | 拦截器排除的 URI 列表 |
| `open-gateway-interceptor` | boolean | false | 是否开启网关拦截器 |
| `auth-type` | Integer | 0 | 权限拦截等级：0=只检测登录，1=检测登录+权限 |
| `refresh-user-auth` | boolean | false | 是否刷新用户权限缓存 |
| `verify-param` | boolean | false | 是否验证参数防篡改 |
| `custom-local-interceptor` | boolean | false | 是否使用自定义本地拦截器 |
| `custom-local-filter` | boolean | false | 是否使用自定义本地过滤器 |
| `custom-gateway-filter` | boolean | false | 是否使用自定义网关过滤器 |

### 4.3 安全配置

配置前缀：`easyfk.config.web.security`

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `open` | boolean | false | 是否开启接口安全控制 |
| `ignore-uri` | List\<String\> | null | 忽略安全检查的 URI |
| `timeout` | Duration | 150s | 防重放超时时间 |
| `sign-key` | String | `mcst_sign_reset` | 签名密钥 |
| `sign-key-dynamic` | boolean | false | 签名密钥是否动态 |
| `key-time-to-live` | Duration | 10min | 动态密钥存活时间 |

### 4.4 跨域配置

配置前缀：`easyfk.config.web.cors`

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `open` | boolean | false | 是否开启跨域 |
| `allow-credentials` | boolean | true | 是否允许携带凭证 |
| `cors-domain` | String | `*` | 允许跨域的域名 |
| `allowed-header` | String | `*` | 允许的自定义头 |
| `allowed-method` | String | `*` | 允许的 HTTP Method |
| `path-pattern` | String | `/**` | 跨域路径模式 |

---

## 5. 自动配置

### 5.1 MicroWebConfig

```
META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
→ com.mcst.easyfk.web.micro.config.MicroWebConfig
```

注册的 Bean：

| Bean | 类型 | 条件 | 说明 |
|---|---|---|---|
| `microExceptionHandler` | `MicroExceptionHandler` | `@ConditionalOnMissingBean` | 全局异常处理器 |
| `requestBaseFilter` | `RequestBaseFilter` | `@ConditionalOnMissingBean` | 请求前置过滤器 |
| `serializingObjectMapper` | `ObjectMapper` | `@ConditionalOnMissingBean(ObjectMapper.class)` | Jackson 全局配置 |

### 5.2 WebBaseConfig

注册的 Bean：

| Bean | 类型 | 说明 |
|---|---|---|
| `jwtManager` | `JwtManager` | JWT 创建与解析管理器 |
| `contextDataManager` | `ContextDataManager` | 上下文数据管理器 |

### 5.3 WebCommonConfig

注册配置属性：`SecurityProperties`、`InterceptProperties`、`CorsProperties`

---

## 6. RequestBaseFilter（请求前置过滤器）

继承 `OncePerRequestFilter`，在每个请求开始时还原上下文：

```
HTTP 请求到达微服务
    │
    ├─ 从 ThreadLocal 获取或创建 RequestHeaders
    │
    ├─ 提取请求头信息
    │   ├─ TRACE_ID → traceId 变量
    │   ├─ ACCESS_TOKEN → headers.accessToken
    │   └─ LANGUAGE → headers.language
    │
    ├─ 非空字段写入 RequestHeaderContext（ThreadLocal）
    │
    ├─ contextDataManager.doDataContext(traceId)
    │   ├─ JWT 解析 AccessToken → LoginUser
    │   ├─ UserDataManager 加载 UserData → UserDataContext
    │   ├─ TraceId → TraceIdContext + MDC
    │   └─ （可选）异步刷新用户权限缓存
    │
    ├─ filterChain.doFilter() ← 继续后续处理
    │
    └─ finally: contextDataManager.clearContext()
        ├─ TraceIdContext.remove()
        ├─ MDC.clear()
        ├─ RequestHeaderContext.remove()
        └─ UserDataContext.remove()
```

---

## 7. MicroExceptionHandler（全局异常处理）

使用 `@ControllerAdvice` 统一处理所有异常：

| 异常类型 | HTTP 状态码 | 处理方式 |
|---|---|---|
| `BindException` / `ValidationException` / `MethodArgumentNotValidException` | 500 | `RRBuilder.buildFailByException(e)` 提取校验错误信息 |
| `BusinessException` | 500 | 使用 `errorCode` + `errorMsg` 构建响应 |
| `Exception`（兜底） | 500 | 使用 I18N 国际化消息 `SystemErrorMsg` |

**国际化支持：** 系统异常消息通过 `I18NUtil.getMessage("SystemErrorMsg", "i18n/webMessages")` 获取，支持 5 种语言：
- 简体中文（zh_CN）
- 繁体中文-台湾（zh_TW）
- 繁体中文-香港（zh_HK）
- 英文（en_US）
- 越南语（vi_VN）

---

## 8. ContextDataManager（上下文数据管理器）

核心管理类，负责请求上下文的全生命周期：

### 8.1 上下文初始化

```java
// 微服务场景：从请求头中的 traceId 恢复上下文
contextDataManager.doDataContext(traceId);
```

**内部流程：**
1. 从 `RequestHeaderContext` 获取 AccessToken
2. 过滤无效 Token（空值、`"undefined"`）
3. `JwtManager.getObjectContent()` 解析 JWT → `LoginUser`
4. `UserDataManager.getUserData()` 从缓存加载 `UserData`
5. 写入 `UserDataContext`（ThreadLocal）
6. 设置 TraceId → `TraceIdContext` + `MDC`

### 8.2 上下文清理

```java
contextDataManager.clearContext();
```

一次性清理四个 ThreadLocal：
- `TraceIdContext.remove()`
- `MDC.clear()`
- `RequestHeaderContext.remove()`
- `UserDataContext.remove()`

### 8.3 创建 TraceId

```java
contextDataManager.createTraceId();
```

使用 `IdUtil.randomUUID()` 生成新的 TraceId，写入 `TraceIdContext` + `MDC`。（网关场景使用）

---

## 9. JwtManager（JWT 管理器）

### 9.1 创建 JWT

```java
// 从字符串创建
String token = jwtManager.createJwtByString("content");

// 从对象创建（自动 JSON 序列化）
String token = jwtManager.createJwtByObject(loginUser);
```

### 9.2 解析 JWT

```java
// 解析为对象
ParseJwtResult<LoginUser> result = jwtManager.getObjectContent(token, LoginUser.class);
if (result.isSuccess()) {
    LoginUser user = result.getData();
}

// 解析为字符串
ParseJwtResult<String> result = jwtManager.getStringContent(token);
```

### 9.3 ParseJwtResult

| 字段 | 类型 | 说明 |
|---|---|---|
| `success` | boolean | 解析是否成功 |
| `data` | T | 解析出的数据 |
| `expires` | boolean | JWT 是否已过期 |

---

## 10. Jackson 全局序列化配置

`MicroWebConfig` 注册全局 `ObjectMapper`：

| 类型 | 序列化格式 | 反序列化格式 |
|---|---|---|
| `LocalDateTime` | `yyyy-MM-dd HH:mm:ss` | `yyyy-MM-dd HH:mm:ss` |
| `LocalDate` | `yyyy-MM-dd` | `yyyy-MM-dd` |
| `LocalTime` | `HH:mm:ss` | `HH:mm:ss` |
| `Date` | `yyyy-MM-dd HH:mm:ss` | — |

**其他配置：**
- `NON_NULL`：null 字段不参与序列化
- `FAIL_ON_EMPTY_BEANS = false`：空对象不抛异常
- `FAIL_ON_UNKNOWN_PROPERTIES = false`：忽略 JSON 中多余的字段

---

## 11. ErrorRequest 错误码枚举

web-common 定义了 15 种标准化错误码：

| 错误码 | 场景 |
|---|---|
| `UNLOGIN` | 未登录或登录过期 |
| `UNAUTH` | 无访问权限 |
| `HEARD_EMPTY` | 请求头为空 |
| `NONCE_EMPTY` | 随机串为空 |
| `RESET_SIGN_EMPTY` | ResetSign 为空 |
| `TIMESTAMP_EMPTY` | 时间戳为空 |
| `SIGN_ERROR` | 验签失败 |
| `EXPIRED` | 请求过期 |
| `API_AGAIN` | 接口重放 |
| `PARAM_SIGN_EMPTY` | ParamSign 为空 |
| `VERIFY_EMPTY` | 无验签数据 |
| `VERIFY_ERROR` | 参数签名失败 |
| `REQUEST_TOKEN_EMPTY` | RequestToken 为空 |
| `REQUEST_AGAIN` | 重复提交 |
| `JWT_ERROR` | JWT 无效 |

---

## 12. 工具类

### 12.1 InterceptorExcludeUriUtil

```java
boolean excluded = InterceptorExcludeUriUtil.containsUri(requestUri, interceptProperties);
```

检查请求 URI 是否在拦截器排除列表中。

### 12.2 CheckIgnoreSecurityUriUtil

```java
boolean pass = CheckIgnoreSecurityUriUtil.isPass(requestUri, ignoreUris);
```

检查请求 URI 是否应跳过安全检查：
- 自动忽略静态文件：`.html`、`.htm`、`.icon`、`.css`、`.js`、`.ico`
- 配置的忽略 URI 列表（包含匹配）

---

## 13. FilterChainData（过滤链传递数据）

微服务间传递的标准化数据容器：

```java
@Data
@Accessors(chain = true)
public class FilterChainData implements Serializable {
    private RequestHeaders headers;
    private LoginUser loginUser;
}
```

网关将解析后的 `RequestHeaders` 和 `LoginUser` 封装为 JSON 写入请求头，下游微服务从中还原上下文。

---

## 14. 快速接入

### 14.1 添加依赖

```groovy
dependencies {
    implementation project(':easyfk-web:web-micro')
}
```

### 14.2 配置 JWT

```yaml
easyfk:
  config:
    web:
      jwt:
        secret: "your-custom-secret-key"
```

### 14.3 使用上下文

```java
@RestController
public class UserController {

    @GetMapping("/user/info")
    public ResponseResult<UserData> getUserInfo() {
        // 自动由 RequestBaseFilter 注入
        UserData userData = UserDataContext.getUserData();
        String traceId = TraceIdContext.getTraceId();
        return RRBuilder.buildSuccessBody(userData);
    }
}
```
