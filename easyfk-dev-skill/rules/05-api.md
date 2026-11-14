# 05 Api 层：IXxxApi 与 XxxApiServerImpl

`IXxxApi` 是这个实体对外的唯一契约：本服务的 Controller 用它，其他服务也用它。实现有三种，换依赖包就能在本地、Feign、Dubbo 之间切换，调用方代码不变：

| 实现 | 位置 | 做什么 |
|---|---|---|
| `XxxApiServerImpl` | `<mod>-server` | 本地实现，委派给 `IXxxService` |
| `XxxApiScImpl` | `<mod>-cloud-api` | Feign 消费方，委派给 `IXxxRemote`，见 [07-remote.md](07-remote.md) |
| `XxxApiDubboImpl` | `<mod>-dubbo-api` | Dubbo 消费方，委派给 `IXxxRemote`，见 [07-remote.md](07-remote.md) |

## 1. 接口

放在 `<mod>-api` 模块的 `<base>.api` 包：

```java
public interface IOrderApi extends IBaseApi<OrderResp, String, OrderReq> {

    /**
     * 取消订单。订单已发货时抛出业务异常。
     */
    BaseResult<?> cancel(String orderId);
}
```

- 泛型 **Resp、主键、Req**，与 `IXxxService` 一致。
- 基础方法 `IBaseApi` 都有：`queryById(id)`、`queryByIdOptimize(id, String[])`、`queryOneByField`、`queryList`、`queryOne`、`count`、`exists`、`queryByPage`、`save`、`delete`、`insertAndReturnId`。不要重复声明。
- 方法要能跨进程调用：**不用可变参数**；参数和返回值都是可序列化的 Req / Resp / VO / 基本类型，不传 `SearchCondition`、Entity、Dto、`HttpServletRequest` 这类对象。
- 需要指定查询列时用 `queryByIdOptimize(id, columns)`，不要在 Api 上加可变参数的重载。
- 只有确实要对外提供的能力才加到 `IXxxApi`；只在 Service 内部用的方法留在 `IXxxService`。

## 2. 本地实现

放在 `<mod>-server` 的 `<base>.server.impl` 包：

```java
public class OrderApiServerImpl
        extends BaseApiServiceImpl<IOrderService, OrderResp, String, OrderReq>
        implements IOrderApi {

    @Override
    public BaseResult<?> cancel(String orderId) {
        return this.baseService.cancel(orderId);
    }
}
```

- 继承 `BaseApiServiceImpl<IXxxService, Resp, 主键, Req>`，基础方法全部由基类委派给 Service，**类体里不写基础方法**。
- 扩展方法只做一层转发，用基类已经注入好的 `this.baseService`，不再另外 `@Resource` 注入同一个 Service。
- 不在这里写业务逻辑、事务、参数校验。这些都在 Service。
- `BaseApiServiceImpl` 是抽象类，按泛型注入 Service。容器里必须**正好有一个** `IXxxService` 的 Bean，否则启动失败。新增实体时 Service 和 ApiServerImpl 一起注册。
- 注册方式跟项目现状（`@AutoConfiguration` 里 `@Bean @ConditionalOnMissingBean`，返回类型写 `IXxxApi`；或者 `@Service`），见 [09-config.md](09-config.md)。

## 3. 给 Api 加方法时同步改哪些地方

`IXxxApi` 加了一个方法，项目里有的实现都要补上，否则编译失败或者调用方拿到的实现缺方法：

1. `IXxxService` 加方法，`XxxServiceImpl` 实现业务。
2. `XxxApiServerImpl` 转发给 `this.baseService`。
3. 有 Cloud 时：`IXxxRemote` 加带 HTTP 注解的方法，`XxxRemoteImpl` 转发给 Service，`XxxApiScImpl` 转发给 Feign 客户端。
4. 有 Dubbo 时：`IXxxRemote` 加方法，`XxxRemoteImpl` 转发给 Service，`XxxApiDubboImpl` 转发给 Dubbo 引用。

## 4. 调用方怎么用

- 业务代码只注入 `IXxxApi`：`@Resource private IOrderApi orderApi;`。不注入 `IXxxRemote`，也不注入别的模块的 `IXxxService`。
- 同一个服务里的 Controller 也只注入 `IXxxApi`，这样以后拆成微服务时 Controller 不用改。
