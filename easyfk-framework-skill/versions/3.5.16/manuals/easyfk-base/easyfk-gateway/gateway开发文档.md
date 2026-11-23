# easyfk-gateway 开发文档

## 1. 模块概述

`easyfk-gateway` 是 EasyFK 框架的**网关过滤层模块**，基于 Spring Cloud Gateway 构建，提供全局请求过滤、安全签名校验、会话管理、权限拦截等核心网关能力。该模块作为所有请求的统一入口，实现了请求头解析、接口安全验证、登录态检测、权限控制等完整的网关过滤链。

---

## 2. 模块依赖

| 依赖模块 | 依赖方式 | 说明 |
|---|---|---|
| `easyfk-core` | `api` | 核心模块，提供 DTO、上下文、工具类等 |
| `easyfk-web:web-common` | `api` | Web 公共模块，提供拦截配置、安全属性、URI 工具等 |
| `easyfk-authority` | `api` | 权限模块，提供权限校验和资源安全级别判断 |
| `spring-cloud-starter-gateway` | `api` | Spring Cloud Gateway 核心（排除 logging） |

**build.gradle:**
```groovy
dependencies {
    api project(':easyfk-core')
    api project(':easyfk-web:web-common')
    api project(':easyfk-authority')
    api('org.springframework.cloud:spring-cloud-starter-gateway') {
        exclude group: 'org.springframework.boot', module: 'spring-boot-starter-logging'
    }
}
```

---

## 3. 包结构

```
com.mcst.easyfk.gateway
├── config/                   # 自动配置
│   └── GatewayFilterConfigure  - Spring Boot 自动配置类
├── filter/                   # 过滤器
│   ├── RequestGatewayFilter    - 核心全局网关过滤器
│   ├── ICustomGatewayFilter    - 自定义网关过滤器接口
│   └── IExtendGatewayFilter    - 扩展网关过滤器接口
└── util/                     # 工具类
    └── FailRequestUtil         - 失败响应工具类
```

---

## 4. 核心组件详解

### 4.1 RequestGatewayFilter —— 全局网关过滤器

`RequestGatewayFilter` 实现了 `GlobalFilter` 和 `Ordered` 接口，是模块的核心类，处理所有经过网关的请求。

**执行优先级：** `getOrder() = 0`（最高优先级）

#### 4.1.1 依赖注入

| 依赖 | 类型 | 注入方式 | 说明 |
|---|---|---|---|
| `securityProperties` | `SecurityProperties` | `@Resource` | 安全配置属性 |
| `gatewayProperties` | `GatewayProperties` | `@Resource` | Spring Cloud Gateway 路由配置 |
| `properties` | `InterceptProperties` | `@Resource` | 拦截器配置属性 |
| `cacheService` | `ICacheService` | `@Resource @Lazy` | 缓存服务（延迟加载） |
| `userDataManager` | `UserDataManager` | `@Autowired(required=false)` | 用户权限管理器（可选） |
| `interceptProperties` | `InterceptProperties` | `@Resource` | 拦截器配置 |
| `customGatewayFilter` | `ICustomGatewayFilter` | `@Autowired(required=false)` | 自定义过滤器（可选） |
| `authResourceApi` | `IAuthResourceApi` | `@Resource @Lazy` | 权限资源 API（延迟加载） |
| `contextDataManager` | `ContextDataManager` | `@Resource` | 上下文数据管理器 |

#### 4.1.2 过滤器主流程

```
请求进入 filter()
    │
    ├─ 1. OPTIONS 请求 → 直接放行
    │
    ├─ 2. 自定义过滤器开关 → 委托 ICustomGatewayFilter 处理
    │
    ├─ 3. Knife4j 文档请求（/v3/api-docs）→ 路径重写后放行
    │
    ├─ 4. 解析请求头 → 构建 RequestHeaders 对象
    │     ├─ Reset-Sign（签名）
    │     ├─ Param-Sign（参数签名）
    │     ├─ Timestamp（时间戳）
    │     ├─ Request-Token（请求令牌）
    │     ├─ Access-Token（访问令牌）
    │     ├─ Request-Nonce（请求随机数）
    │     ├─ Device-No（设备号）
    │     └─ Client-Type（客户端类型）
    │
    ├─ 5. 创建 TraceId（链路追踪）
    │
    ├─ 6. 会话过滤（sessionFilter）→ 加载用户数据上下文
    │
    ├─ 7. 安全过滤（securityFilter，可开关）
    │     └─ 失败 → 清理上下文 + 返回错误响应
    │
    ├─ 8. 网关拦截（gatewayIntercept，可开关）
    │     ├─ 排除 URI → 直接放行
    │     ├─ LOGIN 级别 → 检查登录态
    │     └─ AUTHORITY 级别 → 检查登录态 + 权限
    │
    └─ 9. 返回成功 → 将 FilterChainData 写入请求头传递给下游服务
         └─ doFinally → 清理 ThreadLocal 上下文
```

#### 4.1.3 安全签名校验流程（securityFilter）

当 `securityProperties.isOpen() == true` 时启用：

```
securityFilter(exchange)
    │
    ├─ 1. 检查是否在忽略 URI 列表中 → 是则直接通过
    │
    ├─ 2. 校验请求头必填项
    │     ├─ RequestHeaders 不能为空
    │     ├─ Request-Nonce 不能为空
    │     ├─ Reset-Sign 不能为空
    │     └─ Timestamp 不能为空
    │
    ├─ 3. 获取签名密钥
    │     ├─ 静态模式 → 使用配置的 signKey
    │     └─ 动态模式 → 从缓存获取动态密钥
    │
    ├─ 4. 签名验证
    │     拼接：Request-Nonce={nonce}&Timestamp={ts}&Key={key}
    │     计算：MD5(拼接字符串)
    │     比较：计算结果 vs 请求头中的 Reset-Sign
    │
    └─ 5. 防重放攻击
          ├─ 检查 Request-Nonce 是否已存在于缓存
          │   └─ 存在 → 拒绝（接口重复调用）
          └─ 不存在 → 缓存该 Nonce（设置超时时间）
```

**签名算法：**
```
signText = "Request-Nonce=" + nonce + "&Timestamp=" + timestamp + "&Key=" + signKey
sign = MD5(signText)
```

#### 4.1.4 网关拦截流程（gatewayIntercept）

当 `properties.isOpenGatewayInterceptor() == true` 时启用：

```
gatewayIntercept(exchange, chain, gatewayData)
    │
    ├─ 1. 排除 URI 检查 → 匹配则直接放行
    │
    ├─ 2. 解析服务名
    │     └─ 从 Gateway 路由配置中匹配请求 URI 对应的服务
    │
    ├─ 3. 获取资源安全级别
    │     └─ authResourceApi.checkUriSecurityLevel(requestUri)
    │
    ├─ 4. 根据安全级别判断
    │     ├─ UNIMPEDED → 直接通过
    │     ├─ LOGIN → 检查 UserData 是否存在
    │     │   └─ 不存在 → 返回未登录错误
    │     └─ AUTHORITY → 检查 UserData + 权限
    │         ├─ 未登录 → 返回未登录错误
    │         └─ 无权限 → 返回未授权错误
    │
    └─ 5. 通过 → 写入 FilterChainData 到下游请求头
```

#### 4.1.5 请求头传递机制

过滤器通过后，`FilterChainData`（包含解析后的请求头信息）被序列化为 JSON，写入下游请求的 `CHAIN_NAME` Header 中：

```java
ServerHttpRequest request = exchange.getRequest().mutate()
    .header(RequestHeaderConstant.CHAIN_NAME, JSON.toJSONString(gatewayData))
    .build();
```

下游微服务可通过该 Header 获取网关层解析后的统一上下文数据。

### 4.2 ICustomGatewayFilter —— 自定义网关过滤器接口

当业务需要**完全替换**默认过滤逻辑时使用。

```java
public interface ICustomGatewayFilter {
    Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain);
}
```

**启用条件：** 配置 `properties.isCustomGatewayFilter() == true`，并注册 `ICustomGatewayFilter` 实现 Bean。

**使用示例：**
```java
@Component
public class MyCustomGatewayFilter implements ICustomGatewayFilter {

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        // 完全自定义的过滤逻辑
        return chain.filter(exchange);
    }
}
```

### 4.3 IExtendGatewayFilter —— 扩展网关过滤器接口

当业务需要在默认过滤流程基础上**追加扩展逻辑**时使用。

```java
public interface IExtendGatewayFilter {
    void doExtendIntercept(ServerWebExchange exchange);
}
```

**使用示例：**
```java
@Component
public class MyExtendFilter implements IExtendGatewayFilter {

    @Override
    public void doExtendIntercept(ServerWebExchange exchange) {
        // 附加的拦截逻辑，如日志记录、限流等
    }
}
```

### 4.4 FailRequestUtil —— 失败响应工具类

提供统一的网关层错误响应构建能力：

```java
public static Mono<Void> failRequest(ServerWebExchange exchange, ErrorRequest errorRequest)
```

**响应格式：**
- HTTP 状态码：`400 Bad Request`
- Content-Type：`application/json; charset=utf-8`
- 响应体：`ResponseResult` JSON 格式，包含错误码和错误信息

**错误类型（来自 ErrorRequest 枚举）：**

| 错误 | 说明 |
|---|---|
| `HEARD_EMPTY` | 请求头为空 |
| `NONCE_EMPTY` | 随机数为空 |
| `RESET_SIGN_EMPTY` | 签名为空 |
| `TIMESTAMP_EMPTY` | 时间戳为空 |
| `DYNAMIC_SIGN_KEY_TIMEOUT` | 动态签名密钥超时 |
| `SIGN_ERROR` | 签名验证失败 |
| `API_AGAIN` | 接口重复调用 |
| `UNLOGIN` | 未登录 |
| `UNAUTH` | 未授权 |

### 4.5 GatewayFilterConfigure —— 自动配置

```java
@AutoConfiguration
public class GatewayFilterConfigure {

    @Bean
    @ConditionalOnMissingBean
    public RequestGatewayFilter requestHeaderGatewayFilter() {
        return new RequestGatewayFilter();
    }
}
```

通过 Spring Boot 自动配置注册 `RequestGatewayFilter` Bean。使用 `@ConditionalOnMissingBean`，支持业务覆盖默认实现。

---

## 5. 配置项说明

| 配置来源 | 关键属性 | 说明 |
|---|---|---|
| `SecurityProperties` | `open` | 是否开启安全签名校验 |
| | `signKey` | 签名密钥 |
| | `signKeyDynamic` | 是否使用动态签名密钥 |
| | `ignoreUri` | 忽略安全校验的 URI 列表 |
| | `timeout` | Nonce 缓存超时时间（防重放） |
| `InterceptProperties` | `openGatewayInterceptor` | 是否开启网关权限拦截 |
| | `customGatewayFilter` | 是否启用自定义过滤器 |
| | `refreshUserAuth` | 是否刷新用户权限缓存 |
| | 排除 URI 配置 | 不拦截的 URI 列表 |

---

## 6. 请求头常量

以下请求头将被网关解析并封装到 `RequestHeaders` 对象中：

| Header 名称 | 对应字段 | 说明 |
|---|---|---|
| `Reset-Sign` | `resetSign` | 请求签名 |
| `Param-Sign` | `paramSign` | 参数签名 |
| `Timestamp` | `timestamp` | 请求时间戳 |
| `Request-Token` | `requestToken` | 请求令牌 |
| `Access-Token` | `accessToken` | 访问令牌 |
| `Request-Nonce` | `requestNonce` | 请求随机数（防重放） |
| `Device-No` | `deviceNo` | 设备编号 |
| `Client-Type` | `clientType` | 客户端类型 |

---

## 7. 集成指南

### 7.1 引入依赖

```groovy
dependencies {
    implementation project(':easyfk-gateway')
}
```

### 7.2 基本配置

```yaml
# 开启安全签名校验
security:
  open: true
  sign-key: "your-sign-key"
  sign-key-dynamic: false
  timeout: 300

# 开启网关权限拦截
intercept:
  open-gateway-interceptor: true
  custom-gateway-filter: false
  refresh-user-auth: true
```

### 7.3 自定义过滤器

**方式一：完全替换** —— 实现 `ICustomGatewayFilter`，开启 `customGatewayFilter` 配置

**方式二：扩展追加** —— 实现 `IExtendGatewayFilter`，在默认流程基础上追加逻辑

**方式三：替换核心过滤器** —— 注册自定义 `RequestGatewayFilter` Bean 覆盖默认实现

### 7.4 Knife4j 文档集成

模块内置了对 Knife4j API 文档的支持。当请求 URI 包含 `/v3/api-docs` 时，自动将路径重写为 `/v3/api-docs`，确保网关层的文档聚合正常工作。
