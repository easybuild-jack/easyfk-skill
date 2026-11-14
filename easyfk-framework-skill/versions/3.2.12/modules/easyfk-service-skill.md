# easyfk-service Skill 参考文档

> 所属项目：`easyfk-base`　子模块：`service-api`、`service-base`
> 坐标：`com.mcst:service-api:3.2.12`、`com.mcst:service-base:3.2.12`
> 依据：两个子模块全部源码（8 个文件），对齐 `EasyFK框架开发手册.md` §3.3 / §4.1 和 `核心模块说明.md` §5.6。标准分层写法以代码生成器模板为准：`my_service`、`my_serviceImpl`、`base_api`、`serverApiImpl`。
> 以源码为准；差异见文末「复查记录」。

---

## 1. 模块定位与分层

| 子模块 | 内容 | 依赖 |
|---|---|---|
| `service-api` | 只有接口：`IBaseService`、`IBaseApi`、`IBaseFluxService`、`IBaseFluxApi` | `compileOnly easyfk-core` |
| `service-base` | `BaseApiServiceImpl`（Api 层委派实现）、`ServiceUtil`、`SearchRequestUtil`、`UserDataFiltrationUtil` | `api` 引入 service-api、core、repository、authority |

两个子模块**都没有自动配置**。

标准分层（生成器模板）如下，泛型约定 **T = Resp（出参），PK = 主键，R = Req（入参）**：

```
Controller / Remote
      │  IXxxApi extends IBaseApi<XxxResp, PK, XxxReq>                 ← 对外契约，可被 Dubbo/Cloud 暴露
      ▼
XxxApiServerImpl extends BaseApiServiceImpl<IXxxService, XxxResp, PK, XxxReq> implements IXxxApi
      │  委派
      ▼
IXxxService extends IBaseService<XxxResp, PK, XxxReq>                  ← 业务逻辑
XxxServiceImpl implements IXxxService                                  ← SearchRequest 通过 ConditionUtil 转换，Req 转 Dto 后交给 ServiceUtil
      │
      ▼
IXxxRepository extends IBaseRepository<XxxDto, PK>                     ← 见 repository 文档
```

---

## 2. 接口

### 2.1 IBaseService<T, PK, R>

| 方法 | 说明 |
|---|---|
| `T queryById(PK id, String... selectColumns)` | |
| `T queryOneByField(String field, Object value, String... selectColumns)` | |
| `List<T> queryList(SearchRequest<R>)` / `T queryOne(SearchRequest<R>)` | |
| `long count(SearchRequest<R>)` / `boolean exists(SearchRequest<R>)` | |
| `PageResult<T> queryByPage(SearchRequest<R>)` | |
| `BaseResult<?> save(ModifyRequest<R>)` / `BaseResult<?> delete(ModifyRequest<R>)` | |
| `PK insertAndReturnId(R param)` | |

### 2.2 IBaseApi<T, PK, R>

方法与 IBaseService 相同，区别在于**没有可变参数**，以便 RPC 序列化：

- `queryById(PK)`、`queryOneByField(f, v)`；
- 需要指定列时使用 `queryByIdOptimize(PK, String[])`、`queryOneByFieldOptimize(f, v, String[])`。

### 2.3 IBaseFluxService<T, R> / IBaseFluxApi<T, R>

用于**没有主键的场景**（关系表、流水表），只有 `save`、`queryList`、`count`、`queryByPage`、`delete` 五个方法。它们是普通的同步接口，**与响应式（Reactor Flux）无关**。remote-dubbo 和 remote-cloud 中有对应的 `*FluxRemoteImpl` 和 `*FluxApiRemoteImpl`。

---

## 3. service-base

### 3.1 BaseApiServiceImpl<I extends IBaseService<T,PK,R>, T, PK, R>（abstract）

- 抽象类，必须由子类继承使用。通过 `@Autowired protected I baseService`（按子类声明的泛型 `I` 解析）注入，所有方法都委派给它。**容器中找不到唯一的 `I` Bean 时启动失败**（`NoSuchBeanDefinitionException` / `NoUniqueBeanDefinitionException`）。
- `queryByPage`：请求中没有 `pageSearch` 时，默认使用 `new PageSearch(1, 20)`，并且**会修改传入的 request 对象**。
- 子类只需要声明泛型，不需要写任何方法：

```java
@Service
public class ProductApiServerImpl
        extends BaseApiServiceImpl<IProductService, ProductResp, String, ProductReq>
        implements IProductApi {
}
```

### 3.2 Service 实现（生成器写法）

```java
@Service
public class ProductServiceImpl implements IProductService {
    @Resource
    private IProductRepository productRepository;

    @Override
    public List<ProductResp> queryList(SearchRequest<ProductReq> param) {
        return TransformUtil.transformList(
                productRepository.queryByCondition(ConditionUtil.conditionByRequest(param)), ProductResp.class);
    }

    @Override
    public PageResult<ProductResp> queryByPage(SearchRequest<ProductReq> param) {
        return TransformUtil.transformPageResult(
                productRepository.queryByPage(ConditionUtil.conditionByRequest(param)), ProductResp.class);
    }

    @Override
    public BaseResult<?> save(ModifyRequest<ProductReq> param) {
        return ServiceUtil.save(param, productRepository, ProductDto.class);
    }

    @Override
    public BaseResult<?> delete(ModifyRequest<ProductReq> param) {
        return ServiceUtil.delete(param, productRepository, ProductDto.class);
    }

    @Override
    public String insertAndReturnId(ProductReq param) {
        return ServiceUtil.insertAndReturnId(param, productRepository, ProductDto.class);
    }
    // queryById / queryOneByField / queryOne / count / exists 的写法与上面相同
}
```

### 3.3 ServiceUtil

| 方法 | 行为 |
|---|---|
| `save(ModifyRequest<R>, repo, Class<T>)` | 先用 `convertRequest` 把 R 转为 T（`TransformUtil`），再调用 `RepositoryUtil.save`（有主键且记录存在时更新，否则插入，并做唯一性校验） |
| `delete(ModifyRequest<R>, repo, Class<T>)` | 转换后调用 `RepositoryUtil.delete` |
| `insertAndReturnId(R, repo, Class<T>)` | 转换后调用 `RepositoryUtil.insertAndReturnId` |
| `convertRequest(ModifyRequest<R>, Class<T>)` | 复制 `enableNullFields`、`idList`、`parmaObj`、`paramList` |

`TransformUtil` 依赖 Spring 上下文（详见 core 文档）。

### 3.4 SearchRequestUtil

- `addInConditionForRequest(request, EFunction, List)`：通过 `SRPBuilder` 追加 IN 条件。
- `addEqConditionForRequest(request, Class<T>, EFunction, value)`：把值**写入 `request.parmaObj` 的对应字段**（parmaObj 为空时会创建实例）。之后 `ConditionUtil` 的 example 会把它转为等值条件。它会**覆盖**前端传入的同名字段值，异常只调用 `printStackTrace`。

### 3.5 UserDataFiltrationUtil（数据权限 / SaaS 隔离）

当前用户信息来自 `UserDataContext.getUserData()`，由 web-base 在每次请求时写入。

| 方法 | 作用 | 跳过条件 |
|---|---|---|
| `saasDataFiltration(searchRequest, Class<T>, T::getTenantId, UserData::getXxx)` / `(…, Map)` | 查询时把当前用户的字段值作为**等值条件**写入 parmaObj | 没有 UserData；用户类型为 **Platform 或 Customer**（type 为空时视为 Platform）；用户字段值为空 |
| `setSaasData(modifyRequest, T::getTenantId, UserData::getXxx)` / `(…, Map)` | 保存时把用户字段值写入每一条 param | 同上 |
| `dataInFiltration(searchRequest, T::getDeptId, UserData::getXxx)` / `(…, Map)` | 把用户字段值作为 **IN 条件**。字符串值按逗号拆分，值为 `"全部"` 或 `"*"` 时跳过；`Collection` 转为 List，数组展开，其他单值（如 Long）包装为单元素 List | 没有 UserData；字段值为空。**不按用户类型跳过** |

```java
@Override
public PageResult<OrderResp> queryByPage(SearchRequest<OrderReq> param) {
    UserDataFiltrationUtil.saasDataFiltration(param, OrderReq.class, OrderReq::getMerchantId, UserData::getMerchantId);
    return TransformUtil.transformPageResult(
            orderRepository.queryByPage(ConditionUtil.conditionByRequest(param)), OrderResp.class);
}
```

**用户类型跳过规则（设计如此）**：`saasDataFiltration` / `setSaasData` 只对 Agent、Merchant 等"租户侧"用户注入租户字段；Platform（平台运营，需看全量）与 Customer（终端客户，不归属租户，其数据范围应由业务按 userId 等自行限定）被跳过，type 为空按 Platform 处理。因此 Customer 的数据隔离**不能**依赖这两个方法。`dataInFiltration` 不看用户类型。

**安全提示**：上下文中**没有 UserData 时直接跳过过滤，返回全量数据**。例如异步线程、定时任务、内部 RPC 没有透传用户信息时，都属于这种情况。在必须隔离的场景中，应先断言 `UserDataContext.getUserData() != null`。

---

## 4. 生成代码时的规则

**应该这样做：**

- 严格按照 `Api → ApiServerImpl(BaseApiServiceImpl) → Service → Repository` 分层，泛型顺序为 `<Resp, PK, Req>`。建议使用代码生成器。
- Service 中使用 `ConditionUtil.conditionByRequest` 转换查询条件，用 `ServiceUtil` 执行写操作，用 `TransformUtil` 转换出参。
- 对外 RPC 契约使用 `IBaseApi`（没有可变参数）；`IBaseService` 只在进程内使用。
- 多租户查询和写入都要调用 `UserDataFiltrationUtil`（查询用 `saasDataFiltration` 或 `dataInFiltration`，写入用 `setSaasData`），并确认上下文中存在 UserData。
- 写操作放在 Service 层，用 `@Transactional(rollbackFor = Exception.class)` 控制事务。

**不要这样做：**

- 不要把 `IBaseFluxService` 当作响应式接口来使用。
- 不要直接实例化或注册 `BaseApiServiceImpl`（抽象类），也不要在没有对应 Service Bean 时声明 ApiServerImpl（启动失败）。
- 不要指望 SaaS 过滤对 Platform 或 Customer 用户生效，这两类用户会被直接跳过；Customer 数据范围需业务按 userId 自行过滤。
- 不要在 Service 中拼接原生 SQL 条件来做数据隔离，应使用上述工具或 `SCBuilder`。

---

## 5. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | 框架手册 §3.3.1 | `IBaseFluxService` / `IBaseFluxApi` 是"响应式服务接口" | 实际是普通的同步接口，含义是"没有主键"；核心模块说明 §5.6 的描述是正确的 |
| 2 | 框架手册 §3.3.2 / §4.1.3 | `IUserService extends IBaseApi<UserDto, Long, UserResp>` | 泛型顺序应为 `<Resp, PK, Req>`；Service 应继承 `IBaseService`，`IBaseApi` 用于 Api 层 |
| 3 | 框架手册 §3.3.2 / §4.1.4 | `UserServiceImpl extends BaseApiServiceImpl<UserDto, Long, UserResp>` | `BaseApiServiceImpl` 有 4 个泛型 `<I extends IBaseService, T, PK, R>`，用于 ApiServerImpl，不用于 Service |
| 4 | 框架手册 §4.1.4 | `BRBuilder.<T>builder().fail("…").build()`、`TransformUtil.transform(...)` | 方法名不符，实际为 `BRBuilder.failResult(msg, code)`（单参 `failResult(x)` 是把 x 放进 data）/ `BRBuilder.<T>builder(false).msg(msg).build()`、`TransformUtil.transformObj`（详见 core 文档） |
| 5 | 框架手册 §4.1.2 | Repository 中的 `findByUsername` | 不支持方法名推导查询（详见 repository 文档） |
| 6 | 核心模块说明 §5.6.2 | `BaseApiServiceImpl` 是"抽象实现" | 它不是 abstract 类；Service 通过 `required=false` 注入，缺失时运行期 NPE **已修复**：改为 abstract 类，`baseService` 改为必需注入，缺少 Service Bean 时启动失败。 |
| 7 | 核心模块说明 §5.6.2 | `UserDataFiltrationUtil` "自动注入过滤条件" | 需要业务代码显式调用；上下文缺少 UserData 时不做任何过滤；Platform 和 Customer 用户会被跳过（只对 saas 方法生效）。复核：跳过 Platform/Customer 属设计行为（平台看全量、终端客户不归属租户），不改代码，§3.5 已补充说明 |
| 8 | 源码 | `dataInFiltration` | 用户字段值既不是 String 也不是 List 时（例如 Long），会抛 `ClassCastException` **已修复**：String 按逗号拆分、Collection 转 List、数组展开、其他单值包装为单元素 List。 |
