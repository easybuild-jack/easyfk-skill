# rpc-dubbo 开发手册

## 1. 模块概述

`rpc-dubbo` 是 EasyFK 框架中基于 Apache Dubbo 的高性能 RPC 远程调用组件。该模块集成了 Dubbo Spring Boot Starter 和 Nacos 注册中心，并通过自定义 `DubboFilter` 实现了 **TraceId 链路追踪透传**和 **AccessToken 身份凭证透传**，使 Dubbo 服务间的调用具备完整的上下文传递能力，同时在服务端调用完成后自动清理线程上下文，避免资源泄漏。

## 2. 依赖引入

### Maven

```xml
<dependency>
    <groupId>com.mcst</groupId>
    <artifactId>rpc-dubbo</artifactId>
</dependency>
```

### Gradle

```gradle
dependencies {
    implementation 'com.mcst:rpc-dubbo'
}
```

> 版本号由框架统一 BOM 管理，无需手动指定。

该模块会自动传递引入以下依赖：
- `dubbo-spring-boot-starter` — Apache Dubbo Spring Boot 集成
- `dubbo-registry-nacos` — Dubbo Nacos 注册中心适配
- `web-base` — EasyFK Web 基础模块（包含 `ContextDataManager` 等上下文管理能力）

## 3. 工作原理

rpc-dubbo 通过 Dubbo SPI 扩展机制注册 `DubboFilter`，在 Consumer（消费端）和 Provider（服务端）两侧自动激活，实现上下文的双向透传：

```
Consumer 端                              Provider 端
┌────────────────────┐                   ┌────────────────────┐
│  业务代码发起调用    │                   │  接收 Dubbo 请求    │
│        │           │                   │        │           │
│        ▼           │                   │        ▼           │
│  DubboFilter       │   Dubbo RPC       │  DubboFilter       │
│  (Consumer 侧)     │ ──────────────▶   │  (Provider 侧)     │
│  · 读取 TraceId    │   Attachment:     │  · 提取 TraceId    │
│  · 读取 AccessToken│   traceId         │  · 提取 AccessToken│
│  · 写入 Attachment │   accessToken     │  · 设置上下文       │
│        │           │                   │        │           │
│        ▼           │                   │        ▼           │
│  发送 RPC 请求      │                   │  执行业务逻辑       │
└────────────────────┘                   │        │           │
                                         │        ▼           │
                                         │  清理线程上下文     │
                                         └────────────────────┘
```

### 核心流程

1. **Consumer 端**：从当前线程的 `TraceIdContext` 获取 TraceId，从 `RequestHeaderContext` 获取 AccessToken，通过 Dubbo 的 `Invocation.setAttachment()` 机制传递到 Provider 端
2. **Provider 端**：从 `Invocation.getAttachment()` 中提取 TraceId 和 AccessToken，通过 `ContextDataManager` 初始化上下文数据（包括 TraceId 设置、请求头信息恢复等）
3. **资源清理**：Provider 端业务逻辑执行完成后，在 `finally` 块中调用 `ContextDataManager.clearContext()` 清理线程上下文，避免线程池复用导致的数据污染

## 4. SPI 注册机制

DubboFilter 通过 Dubbo SPI 扩展机制自动注册，无需在 Spring 配置中手动声明：

**SPI 配置文件**：`META-INF/dubbo/org.apache.dubbo.rpc.Filter`

```
dubboFilter=com.mcst.easyfk.rpc.dubbo.filter.DubboFilter
```

**激活条件**：

```java
@Activate(group = {CommonConstants.CONSUMER, CommonConstants.PROVIDER}, order = -1000)
```

| 属性 | 值 | 说明 |
|------|---|------|
| `group` | `CONSUMER, PROVIDER` | 消费端和服务端双向激活 |
| `order` | `-1000` | 高优先级，确保在其他 Filter 之前执行 |

> Filter 自动激活，开发者无需在配置文件中手动添加 filter 声明。

## 5. 使用指南

### 5.1 服务提供者配置

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
  scan:
    base-packages: com.example.service.impl
```

### 5.2 定义 Dubbo 服务接口

在公共 API 模块中定义接口：

```java
public interface UserService {

    UserDTO getUserById(Long id);

    List<UserDTO> queryUsers(UserQueryDTO query);

    void createUser(UserCreateDTO dto);

    void updateUser(Long id, UserUpdateDTO dto);

    void deleteUser(Long id);
}
```

### 5.3 实现服务提供者

```java
@DubboService(version = "1.0.0")
public class UserServiceImpl implements UserService {

    @Autowired
    private UserRepository userRepository;

    @Override
    public UserDTO getUserById(Long id) {
        return userRepository.queryById(id);
    }

    @Override
    public List<UserDTO> queryUsers(UserQueryDTO query) {
        return userRepository.queryList(query);
    }

    @Override
    public void createUser(UserCreateDTO dto) {
        userRepository.insert(dto);
    }

    @Override
    public void updateUser(Long id, UserUpdateDTO dto) {
        dto.setId(id);
        userRepository.updateById(dto);
    }

    @Override
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }
}
```

### 5.4 服务消费者配置

```yaml
dubbo:
  application:
    name: order-service
  registry:
    address: nacos://192.168.1.100:8848
    parameters:
      namespace: dev
```

### 5.5 注入并调用

```java
@Service
public class OrderService {

    @DubboReference(version = "1.0.0")
    private UserService userService;

    public OrderDTO createOrder(OrderCreateDTO dto) {
        // 像调用本地方法一样调用远程服务
        // DubboFilter 自动透传 TraceId 和 AccessToken
        UserDTO user = userService.getUserById(dto.getUserId());
        // ... 业务逻辑
    }
}
```

## 6. 配置说明

### 6.1 注册中心配置（Nacos）

```yaml
dubbo:
  registry:
    address: nacos://192.168.1.100:8848
    parameters:
      namespace: dev
      group: DEFAULT_GROUP
```

### 6.2 协议配置

```yaml
dubbo:
  protocol:
    name: dubbo
    port: 20880
    threads: 200            # 业务线程池大小
    payload: 8388608        # 最大请求体 8MB
    serialization: hessian2 # 序列化方式
```

### 6.3 消费者配置

```yaml
dubbo:
  consumer:
    timeout: 3000           # 调用超时（毫秒）
    retries: 2              # 失败重试次数
    check: false            # 启动时不检查服务是否可用
    loadbalance: random     # 负载均衡策略
```

### 6.4 提供者配置

```yaml
dubbo:
  provider:
    timeout: 5000           # 服务端超时（毫秒）
    threads: 200            # 业务线程数
    executes: 0             # 服务端并发执行限制，0 不限制
```

### 6.5 多注册中心配置

```yaml
dubbo:
  registries:
    registry1:
      address: nacos://192.168.1.100:8848
      parameters:
        namespace: dev
    registry2:
      address: nacos://192.168.1.200:8848
      parameters:
        namespace: dev
```

## 7. 上下文透传

### 7.1 TraceId 透传

`DubboFilter` 自动在消费端和服务端之间传递 TraceId：

```
网关生成 TraceId: abc123
  → 服务A (Consumer) DubboFilter 写入 Attachment: traceId=abc123
    → 服务B (Provider) DubboFilter 提取 traceId=abc123，设置到 TraceIdContext
      → 服务B (Consumer) DubboFilter 写入 Attachment: traceId=abc123
        → 服务C (Provider) DubboFilter 提取 traceId=abc123
```

> TraceId 在整个 Dubbo 调用链中保持一致，配合日志框架可实现全链路日志串联。

### 7.2 AccessToken 透传

DubboFilter 同时支持 AccessToken 的跨服务传递：

- Consumer 端：从 `RequestHeaderContext` 获取 AccessToken，过滤 `undefined` 等无效值后写入 Attachment
- Provider 端：从 Attachment 提取 AccessToken，恢复到 `RequestHeaderContext`，使下游服务可获取当前用户身份信息

### 7.3 上下文清理

Provider 端在业务逻辑执行完成后，自动调用 `ContextDataManager.clearContext()` 清理线程上下文：

- 防止 Dubbo 线程池复用时上下文数据污染
- 清理操作在 `finally` 块中执行，保证异常场景也能正常清理
- 清理失败仅打印 warn 日志，不影响业务流程

## 8. 高级用法

### 8.1 服务版本管理

```java
// 提供者 —— 多版本并存
@DubboService(version = "1.0.0")
public class UserServiceV1Impl implements UserService { ... }

@DubboService(version = "2.0.0")
public class UserServiceV2Impl implements UserService { ... }

// 消费者 —— 指定版本
@DubboReference(version = "2.0.0")
private UserService userService;
```

### 8.2 服务分组

```java
@DubboService(group = "primary")
public class PrimaryUserServiceImpl implements UserService { ... }

@DubboService(group = "secondary")
public class SecondaryUserServiceImpl implements UserService { ... }

@DubboReference(group = "primary")
private UserService userService;
```

### 8.3 直连调试

开发环境可跳过注册中心直接指定服务地址：

```java
@DubboReference(url = "dubbo://192.168.1.100:20880")
private UserService userService;
```

### 8.4 异步调用

```java
@DubboReference(version = "1.0.0")
private UserService userService;

public CompletableFuture<UserDTO> getUserAsync(Long id) {
    // Dubbo 3 原生异步支持
    return CompletableFuture.supplyAsync(() -> userService.getUserById(id));
}
```

### 8.5 负载均衡策略

```java
// 支持：random（随机）、roundrobin（轮询）、leastactive（最少活跃）、consistenthash（一致性哈希）
@DubboReference(version = "1.0.0", loadbalance = "roundrobin")
private UserService userService;
```

### 8.6 服务降级

```java
@DubboReference(version = "1.0.0", mock = "com.example.mock.UserServiceMock")
private UserService userService;
```

```java
public class UserServiceMock implements UserService {

    @Override
    public UserDTO getUserById(Long id) {
        // 降级逻辑：返回默认值或缓存数据
        return new UserDTO();
    }

    // ... 其他方法的降级实现
}
```

## 9. 最佳实践

1. **接口独立模块**：将 Dubbo 服务接口定义在独立的 API 模块中，提供者和消费者共同引用，保证接口一致性。
2. **版本管理**：使用 `version` 进行服务版本管理，支持灰度发布和多版本并存。
3. **超时设置**：根据接口复杂度合理设置 `timeout`，避免全局统一超时导致慢接口拖垮快接口。
4. **重试策略**：幂等接口可配置重试（`retries`），非幂等接口（如创建、扣款）应设为 `retries: 0`。
5. **启动检查**：开发环境可设置 `check: false` 避免依赖服务未启动时无法启动，生产环境建议设为 `true`。
6. **线程池配置**：根据业务特点调整 Provider 端线程池大小，IO 密集型可适当调大。
7. **序列化**：默认 `hessian2` 序列化，DTO 对象需实现 `Serializable` 接口。
8. **链路追踪**：确保所有微服务都引入 rpc-dubbo 组件，保证 TraceId 和 AccessToken 在整个调用链中完整传递。
9. **避免大对象传输**：Dubbo 适合传输小数据量的 RPC 调用，大文件传输应使用其他方案（如 OSS）。
10. **服务降级**：核心调用链路建议配置 mock 降级，避免下游服务故障导致级联失败。
