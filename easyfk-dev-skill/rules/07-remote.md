# 07 Remote 层：Spring Cloud（OpenFeign）与 Dubbo

只有项目里已经有 remote 模块、或者用户要求对外提供远程调用时才写。基类、HTTP 映射和限制见 `modules/easyfk-remote-skill.md`，RPC 透传与 Dubbo 配置见 `modules/easyfk-component-rpc-skill.md`。

```
调用方业务代码 ──注入──> IXxxApi
                          │ 实现：XxxApiScImpl / XxxApiDubboImpl（消费方）
                          ▼
                   IXxxRemote（远程契约）── RPC ──> XxxRemoteImpl（提供方）──> IXxxService
```

三个角色：

| 角色 | 放哪 | Cloud | Dubbo |
|---|---|---|---|
| 契约 `IXxxRemote` | `<mod>-cloud-api` / `<mod>-dubbo-api` | `extends IBaseRemote<Resp, String, Req>`，加 `@FeignClient` | `extends IDubboBaseRemote<Resp, String, Req>` |
| 提供方 `XxxRemoteImpl` | `<mod>-cloud-provider` / `<mod>-dubbo-provider` | `extends BaseRemoteImpl<IXxxService, ...>`，是一个 `@RestController` | `extends DubboBaseRemoteImpl<IXxxService, ...>`，导出为 Dubbo 服务 |
| 消费方 | `<mod>-cloud-api` / `<mod>-dubbo-api` | `XxxApiScImpl extends BaseApiRemoteImpl<IXxxRemote, ...> implements IXxxApi` | `XxxApiDubboImpl extends DubboBaseApiRemoteImpl<IXxxRemote, ...> implements IXxxApi` |

模块名和类名跟项目现状：smart 形态是 `-sc/-sc-client`（契约和消费方）+ `-sc/-sc-provider`（提供方），契约常叫 `IXxxScRemote`、提供方叫 `XxxScRemoteImpl`；sc 形态把契约和消费方放在 `-api` 里；auth 这类组件化项目是 `-remote/-cloud-api` + `-remote/-cloud-provider`。项目已有一种命名时照用，不新起一套。

泛型顺序和 Api 一致：**Resp、主键、Req**。基础方法都由基类实现，类体里只写扩展方法。

## 1. Spring Cloud（OpenFeign）

### 1.1 契约

```java
@FeignClient(value = "${easyfk.config.remote.trade.service-id:trade-server}",
        path = "${easyfk.config.remote.trade.base-path:/remote}/trade/order")
public interface IOrderRemote extends IBaseRemote<OrderResp, String, OrderReq> {

    @PostMapping(value = "/cancel", consumes = MediaType.APPLICATION_JSON_VALUE)
    BaseResult<?> cancel(@RequestBody OrderCancelVO vo);

    @GetMapping("/checkOrderNo")
    boolean checkOrderNo(@RequestParam("orderNo") String orderNo);
}
```

- 服务名和路径前缀都用占位符 `easyfk.config.remote.<模块>.service-id` / `base-path`，带默认值，部署时可改。路径是 `<base-path>/<模块>/<实体>`，默认前缀 `/remote`，和给前端的 `/api/...` 分开。
- 扩展方法必须写 HTTP 注解：传对象用 `@PostMapping(consumes = APPLICATION_JSON_VALUE)` + `@RequestBody`，传简单参数用 `@GetMapping` + `@RequestParam("名字")`，名字显式写。
- 一个方法最多一个 `@RequestBody`。参数多于一个对象时，合成一个 VO。
- 不用可变参数，不用没有 `@RequestParam` / `@RequestBody` 的参数。
- 基类的 `queryByIdOptimize`、`queryOneByFieldOptimize` 的 `selectColumns` 是必填参数，调用时不能传 null。
- `queryOneByField` 的 `value` 经过 HTTP 后在服务端是 String，非字符串字段不要用它查。

### 1.2 提供方

```java
@RestController
@RequestMapping("${easyfk.config.remote.trade.base-path:/remote}/trade/order")
public class OrderRemoteImpl
        extends BaseRemoteImpl<IOrderService, OrderResp, String, OrderReq>
        implements IOrderRemote {

    @Override
    public BaseResult<?> cancel(OrderCancelVO vo) {
        return this.baseService.cancel(vo.getOrderId());
    }

    @Override
    public boolean checkOrderNo(String orderNo) {
        return this.baseService.checkOrderNo(orderNo);
    }
}
```

- `@RequestMapping` 路径必须和 `@FeignClient(path)` 完全一致。
- 扩展方法只转发给继承来的 `this.baseService`，不写业务逻辑。
- 提供方本身是 Controller，会经过 web 层的过滤器和拦截器。它只给内部服务调用，网关路由不要把 `/remote/**` 暴露到公网。

### 1.3 消费方

```java
public class OrderApiScImpl
        extends BaseApiRemoteImpl<IOrderRemote, OrderResp, String, OrderReq>
        implements IOrderApi {

    @Override
    public BaseResult<?> cancel(String orderId) {
        return this.baseScRemote.cancel(new OrderCancelVO().setOrderId(orderId));
    }
}
```

- 扩展方法用基类已注入的 `this.baseScRemote`，不再 `@Resource` 注入同一个 Feign 客户端。
- 注册：在 `<mod>-cloud-api` 的配置类里 `@Bean @ConditionalOnMissingBean`，返回类型 `IXxxApi`，并 `@EnableConfigurationProperties(XxxApiProperties.class)`；属性类 `@ConfigurationProperties(prefix = "easyfk.config.remote.<模块>")`，字段 `serviceId`、`basePath`。见 [09-config.md](09-config.md)。
- 调用方启动类要 `@EnableFeignClients(basePackages = "<契约所在包>")`，否则 Feign 客户端不会生成。

## 2. Dubbo

### 2.1 契约

```java
public interface IOrderRemote extends IDubboBaseRemote<OrderResp, String, OrderReq> {

    BaseResult<?> cancel(String orderId);
}
```

- 普通接口，不加 Spring MVC 注解。参数和返回值都要实现 `Serializable`。
- 不用可变参数。

### 2.2 提供方

```java
public class OrderRemoteImpl
        extends DubboBaseRemoteImpl<IOrderService, OrderResp, String, OrderReq>
        implements IOrderRemote {

    @Override
    public BaseResult<?> cancel(String orderId) {
        return this.baseService.cancel(orderId);
    }
}
```

导出有两种写法，跟项目现状：

1. 用 `ServiceConfig` 手动导出（auth 的写法）。**提供方实现类本身也要注册成 Bean**，否则 `ServiceConfig` 拿不到它：

```java
@AutoConfiguration
public class TradeProviderConfig {
    @Bean
    @ConditionalOnMissingBean
    public OrderRemoteImpl orderRemoteImpl() {
        return new OrderRemoteImpl();
    }

    @Bean
    @ConditionalOnMissingBean
    public ServiceConfig<IOrderRemote> orderRemoteServiceConfig(OrderRemoteImpl orderRemoteImpl) {
        ServiceConfig<IOrderRemote> serviceConfig = new ServiceConfig<>();
        serviceConfig.setInterface(IOrderRemote.class);
        serviceConfig.setRef(orderRemoteImpl);
        serviceConfig.export();
        return serviceConfig;
    }
}
```

2. 在实现类上加 `@DubboService`，由 Dubbo 扫描导出。

### 2.3 消费方

```java
public class OrderApiDubboImpl
        extends DubboBaseApiRemoteImpl<IOrderRemote, OrderResp, String, OrderReq>
        implements IOrderApi {

    @Override
    public BaseResult<?> cancel(String orderId) {
        return this.dubboBaseRemote.cancel(orderId);
    }
}
```

- 扩展方法用基类的 `this.dubboBaseRemote`（基类已用 `@DubboReference` 注入）。**不要用 `@Resource` / `@Autowired` 再注入 `IXxxRemote`**，Spring 容器里没有这个 Bean，拿不到 Dubbo 代理。
- 注册：在 `<mod>-dubbo-api` 的配置类里 `@Bean @ConditionalOnMissingBean`，返回类型 `IXxxApi`。
- 基类的 `@DubboReference` 没有指定 `version`、`group`、`timeout`。超时、重试用 `dubbo.consumer.*` 全局配置；提供方导出时设了 `version` / `group`，消费方必须一致，否则调不通。非幂等方法 `retries` 必须为 0。

## 3. 通用规则

- 调用方业务代码只注入 `IXxxApi`，不直接依赖 `IXxxRemote`。
- 契约加方法时，提供方和消费方都要实现；Cloud 和 Dubbo 都有时两套都改（见 [05-api.md](05-api.md) §3）。
- 远程调用不放在数据库事务里，不放在循环里逐条调。需要批量时在契约上加批量方法。
- 链路追踪和用户上下文透传依赖 `rpc-cloud` / `rpc-dubbo` 组件。异步线程里发起远程调用时，用 easyfk-thread 的 `CustomTaskExecutor` 保证 TraceId 透传。
- 远程调用失败（超时、服务不可用）由调用方决定是抛业务异常还是降级，不要静默吞掉返回 null。
