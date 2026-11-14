# 09 Bean 注册、配置属性与依赖

## 1. Bean 怎么注册：跟项目现状

easyfk 项目里有两种注册方式，**新加的类和同模块已有的类用同一种**，不混用：

| 方式 | 适用 | 写法 |
|---|---|---|
| 自动配置类 + `@Bean` | 要被别的项目以 jar 依赖引入的可复用模块（如通用业务模块 auth）；架构类项目的库形态一律用这种，补充要求见 [11-architecture.md](11-architecture.md) §7 | 类上不加 `@Service` / `@Repository` / `@RestController` 注册；在 `@AutoConfiguration` 配置类里 `@Bean @ConditionalOnMissingBean`，并把配置类写进 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` |
| 组件扫描 | 普通业务项目，代码都在启动类所在包下 | 类上加 `@Service`、`@Repository`、`@RestController` |

判断方法：看同模块已有的 Service、Repository、Controller 类上有没有 `@Service` 这类注解，以及有没有 `XxxConfig` 里一排 `@Bean` 方法。拿不准就问用户。

### 1.1 自动配置方式

以 auth 为例，每一层一个配置类：

| 模块 | 配置类 | 注册什么 |
|---|---|---|
| `<mod>-orm-plus`（single / sc / smart 在 server 里） | `XxxOrmPlusConfig`（或并入 `XxxServerConfig`） | `IXxxRepository` |
| `<mod>-server` | `XxxServerConfig` | `IXxxService`、`IXxxApi`（`XxxApiServerImpl`），`@EnableConfigurationProperties(XxxProperties.class)` |
| `<mod>-prd`（或 `-prd-bms` / `-prd-client`） | `XxxControllerConfig` | Controller |
| `<mod>-cloud-api` / `<mod>-dubbo-api`（smart 为 `-sc-client`） | `XxxApiConfig`（smart 为 `XxxScConfig`） | `IXxxApi`（`XxxApiScImpl` / `XxxApiDubboImpl`） |
| `<mod>-dubbo-provider` | `XxxProviderConfig` | `XxxRemoteImpl` 和它的 `ServiceConfig` |

```java
@AutoConfiguration
@EnableConfigurationProperties(TradeProperties.class)
public class TradeServerConfig {

    @Bean
    @ConditionalOnMissingBean
    public IOrderService orderService() {
        return new OrderServiceImpl();
    }

    @Bean
    @ConditionalOnMissingBean
    public IOrderApi orderApi() {
        return new OrderApiServerImpl();
    }
}
```

- `@Bean` 方法的返回类型写**接口**（`IOrderService`、`IOrderApi`），`@ConditionalOnMissingBean` 才能按接口判断，使用方也能用自己的实现覆盖。
- 方法名用接口去掉 `I` 后的小驼峰（`orderService`、`orderApi`、`orderRepository`）。
- 新增实体时，在**每一层**的配置类里都加上对应的 `@Bean`。漏注册 Service 会导致 `XxxApiServerImpl` 启动失败。
- `XxxApiServerImpl` 和 `XxxApiScImpl` / `XxxApiDubboImpl` 都实现 `IXxxApi`，靠 `@ConditionalOnMissingBean` 和依赖哪个包来决定用哪一个。同一个应用不要同时引入本地实现和远程实现。
- 新建的配置类一定要写进 `AutoConfiguration.imports`，一行一个全限定类名。

### 1.2 组件扫描方式

- 类放在启动类所在包或子包下；Mapper 放在 `persistence.mapper` 包，框架自动扫描（见 [03-persistence.md](03-persistence.md)）。
- Service 实现类加 `@Service`，Repository 实现类加 `@Repository`，ApiServerImpl 加 `@Service`。
- 同一个接口只能有一个实现类带注解，否则按类型注入会失败。

## 2. 配置属性

```java
@Data
@ConfigurationProperties(prefix = "easyfk.config.trade")
public class TradeProperties {

    /**
     * 订单超时自动取消的分钟数
     */
    private Integer orderTimeoutMinutes = 30;
}
```

- 前缀统一 `easyfk.config.<模块>`，远程调用的配置在 `easyfk.config.remote.<模块>`（字段 `serviceId`、`basePath`）。不要用 `@Value` 到处读配置。
- 每个字段写中文注释，写清单位和默认值。有默认值的在字段上直接赋值。
- 配置属性类放 `<base>.server.properties` 包，由配置类 `@EnableConfigurationProperties` 启用。
- 项目引入了 `spring-boot-configuration-processor` 时，IDE 能提示这些配置；不要另写 `additional-spring-configuration-metadata.json` 去重复描述。
- 框架组件的配置项（如 `easyfk.config.lock.redisson.*`）以对应 `modules/xxx-skill.md` 为准，不凭记忆写。
- 不会变的值不做成配置。

## 3. 依赖声明

- `easyfk-dependencies` 已经管理的依赖不写版本号（见 [01-project.md](01-project.md) §2.5）。BOM 里没有的依赖自己写版本，在根构建文件集中锁定，不散落在各子模块；新引入前先在回复里说明理由。
- `com.mcst` 的依赖解析失败（找不到构件或 401）多半是没配私服，按 easyfk-framework-skill §8.1 检查仓库声明和本地令牌，不要改坐标或换成别的库绕过去。
- 只被编译用到、运行时由使用方提供的（如 `spring-tx`、`spring-web`、`openfeign`、`dubbo`），用 `compileOnly`。
- 模块之间暴露给下游的用 `api`，只在内部用的用 `implementation`。
- 不引入 easyfk-framework-skill 明确写了不要引入的库，也不引入和已有库功能重复的库（如已有 fastjson2 / Jackson 再引 Gson），清单见 easyfk-framework-skill §6。
