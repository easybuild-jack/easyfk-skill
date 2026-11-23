# easyfk-remote Skill 参考文档

> 所属项目：`easyfk-base`　子模块：`remote-dubbo`、`remote-cloud`
> 坐标：`com.mcst:remote-dubbo:3.5.16`、`com.mcst:remote-cloud:3.5.16`
> 依据：两个子模块全部源码（12 个文件），对齐 `EasyFK框架开发手册.md` §3.10 和 `核心模块说明.md` §5.8。接线方式以代码生成器模板为准：`dubbo/*.ftl`、`springcloud/*.ftl`。
> 以源码为准；差异见文末「复查记录」。

---

## 1. 模块定位

本模块把 service 层的 `IBaseService` / `IBaseApi` 契约适配到 RPC 协议上，**只有接口和委派基类**。它不包含以下内容：

- 自动配置；
- 注册中心和协议配置；
- 上下文透传。TraceId 与登录信息的透传由 `easyfk-component` 中的 `rpc-dubbo`（`DubboFilter`）和 `rpc-cloud`（`FeignClientInterceptor`）提供。

依赖关系：

| 子模块 | 依赖 |
|---|---|
| 父模块（对两个子模块生效） | `api` 引入 `service-api`、`easyfk-core` |
| `remote-dubbo` | `compileOnly org.apache.dubbo:dubbo:3.3.7` |
| `remote-cloud` | `compileOnly spring-web` |

Dubbo 和 OpenFeign 的运行时依赖需要由业务方或 component 的 rpc 模块提供。

泛型约定与 service 层一致：**T = Resp，PK = 主键，R = Req**。

---

## 2. 角色与类

| 角色 | Dubbo | Spring Cloud |
|---|---|---|
| 远程契约 | `IDubboBaseRemote<T,PK,R>`（普通接口） | `IBaseRemote<T,PK,R>`（带 Spring MVC 注解） |
| 提供者：Remote 实现，委派给 `IBaseService` | `DubboBaseRemoteImpl<I extends IBaseService, T, PK, R>` | `BaseRemoteImpl<I extends IBaseService, T, PK, R>` |
| 消费者：实现 `IBaseApi`，委派给远程契约 | `DubboBaseApiRemoteImpl<I extends IDubboBaseRemote, T, PK, R>`（字段使用 `@DubboReference`） | `BaseApiRemoteImpl<I extends IBaseRemote, T, PK, R>`（字段使用 `@Autowired`，即注入 Feign 客户端） |
| 无主键（Flux）版本 | `IDubboBaseFluxRemote` / `DubboBaseFluxRemoteImpl` / `DubboBaseFluxApiRemoteImpl` | `IBaseFluxRemote` / `BaseFluxRemoteImpl` / `BaseFluxApiRemoteImpl` |

调用链：

```
消费方业务代码 ──注入──> IXxxApi（IBaseApi）
                         │ 实现类：XxxApiDubboImpl / XxxApiScImpl（消费者基类）
                         ▼
                  IXxxRemote（远程契约）── RPC ──> XxxRemoteImpl（提供者基类）──> IXxxService
```

所有委派基类的 `queryByPage` 在请求中没有 `pageSearch` 时，都会默认使用 `PageSearch(1, 20)`（会修改入参）。

---

## 3. Dubbo 接线（生成器写法）

```java
// 契约（放在 api 模块，供消费方依赖）
public interface IProductRemote extends IDubboBaseRemote<ProductResp, String, ProductReq> { }

// 提供者
public class ProductRemoteImpl
        extends DubboBaseRemoteImpl<IProductService, ProductResp, String, ProductReq>
        implements IProductRemote { }

@AutoConfiguration
public class ProductModuleProviderConfig {
    @Bean
    @ConditionalOnMissingBean
    public ServiceConfig<IProductRemote> productRemoteServiceConfig(ProductRemoteImpl impl) {
        ServiceConfig<IProductRemote> sc = new ServiceConfig<>();
        sc.setInterface(IProductRemote.class);
        sc.setRef(impl);
        sc.export();
        return sc;
    }
}
// 生成器的写法是用 ServiceConfig 手动导出；在提供者类上加 @DubboService 也可以

// 消费者
@Service
public class ProductApiDubboImpl
        extends DubboBaseApiRemoteImpl<IProductRemote, ProductResp, String, ProductReq>
        implements IProductApi { }
```

---

## 4. Spring Cloud（OpenFeign）接线（生成器写法）

```java
// 契约 + Feign 客户端
@FeignClient(value = "${服务ID}", path = "/api/product")
public interface IProductRemote extends IBaseRemote<ProductResp, String, ProductReq> { }

// 提供者：对外暴露 REST
@RestController
@RequestMapping("/api/product")
public class ProductRemoteImpl
        extends BaseRemoteImpl<IProductService, ProductResp, String, ProductReq>
        implements IProductRemote { }

// 消费者
@Service
public class ProductApiScImpl
        extends BaseApiRemoteImpl<IProductRemote, ProductResp, String, ProductReq>
        implements IProductApi { }
```

生成器会额外生成 `XxxApiProperties`（`easyfk.config.remote.<module>.service-id/base-path`），并在 SMART 项目中生成以 `@ConditionalOnMissingBean` 注册 `IXxxApi` 实现的配置类。

`IBaseRemote` 的 HTTP 映射：

| 方法 | 映射 |
|---|---|
| `queryById` / `queryByIdOptimize` / `queryOneByField` / `queryOneByFieldOptimize` | `GET`，参数通过 `@RequestParam` 传递（`id`、`field`、`value`、`selectColumns`） |
| `queryList` / `queryOne` / `count` / `exists` / `queryByPage` / `save` / `insertAndReturnId` / `delete` | `POST`，JSON 格式的 `@RequestBody` |

注意事项：
- `@RequestParam` 默认是必填的，调用 `queryByIdOptimize` 和 `queryOneByFieldOptimize` 时，`selectColumns` **不能为 null**。
- `queryOneByField` 的 `value` 声明为 `Object`，经过 HTTP 后在服务端会变成 String。
- 提供者的 `@RequestMapping` 路径必须与 `@FeignClient(path)` 一致。
- 提供者本身就是 Controller，会受到 web 层过滤器和拦截器的约束（详见 web 文档）。

---

## 5. 生成代码时的规则

**应该这样做：**

- 契约和 Api 接口放在独立的 api 模块中，供消费方依赖；提供者和消费者的实现分别放在服务端和客户端模块。
- 消费方的业务代码**只注入 `IXxxApi`**，不直接依赖 `IXxxRemote`，以便在 Dubbo 和 Cloud 之间切换或改为本地调用（`ApiServerImpl`）。
- 在契约上新增业务方法时，提供者和消费者两侧都要实现。Cloud 契约需要添加 `@GetMapping` / `@PostMapping` 注解。
- 链路追踪和用户上下文透传需要引入 component 中的 `rpc-dubbo` 或 `rpc-cloud`。

**不要这样做：**

- 不要在 Cloud 契约上使用可变参数，或者使用不带 `@RequestParam` / `@RequestBody` 的参数。
- 不要按照框架手册 §3.10.3 的写法编写 `IUserRemoteService extends IBaseRemote<UserDto, Long, UserResp>` 或 `DubboBaseRemoteImpl<UserDto, Long, UserResp>`。泛型的顺序和个数都不对，而且 Dubbo 契约应继承 `IDubboBaseRemote`。
- 不要把 Flux 系列当作异步或响应式接口。

---

## 6. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | 框架手册 §3.10.2 | `IBaseFluxRemote` 是"异步远程调用接口" | 实际是同步接口，用于无主键的场景 |
| 2 | 框架手册 §3.10.3 | `import com.mcst.easyfk.remote.IBaseRemote` | 实际包是 `com.mcst.easyfk.remote.sc`；Dubbo 的契约是 `com.mcst.easyfk.remote.dubbo.IDubboBaseRemote` |
| 3 | 框架手册 §3.10.3 | Dubbo 提供者继承 `IBaseRemote`，写作 `DubboBaseRemoteImpl<UserDto, Long, UserResp>` | 应继承 `IDubboBaseRemote<Resp, PK, Req>`；基类有 4 个泛型，第一个是 `IBaseService` 的子接口 |
| 4 | 框架手册 §3.10.3 | 消费端直接用 `@DubboReference` 注入 Remote | 框架推荐的写法是消费者继承 `DubboBaseApiRemoteImpl`，业务代码注入 `IXxxApi` |
| 5 | 核心模块说明 §5.8 | `compileOnly` 依赖，不会传递 | 描述正确；还应补充：上下文透传不在本模块，而在 component 的 rpc-dubbo / rpc-cloud |
| 6 | 文档未说明 | Cloud GET 接口的参数 | `selectColumns` 为必填，`value` 为 `Object` 类型，经过 HTTP 后会变成 String |
