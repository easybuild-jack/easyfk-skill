# 06 Controller 层

Controller 放在 `-prd-bms` / `-prd-client`、`<mod>-prd`，或单模块项目的 `controller` 包里（见 [01-project.md](01-project.md) §2）。它只做四件事：接收参数、把参数组装成 `SearchRequest` / `ModifyRequest`、调 `IXxxApi`、用 `RRBuilder` 包装返回。返回结构、全局异常处理、拦截器和鉴权的行为见 `modules/easyfk-web-skill.md`、`modules/easyfk-authority-skill.md`。

## 1. 类

```java
@Tag(name = "订单相关接口", description = "订单相关接口")
@RestController
@RequestMapping("/api/bms/trade/order")
@ResourceController(group = "tradeManage", id = "tradeManage", name = "交易管理", sort = 20000, path = "/trade")
public class OrderBmsController {
    @Resource
    private IOrderApi orderApi;
}
```

- 管理后台和客户端的接口分开写，不放在同一个 Controller 里：

| 端 | 模块 | 类名 | 路径 |
|---|---|---|---|
| 管理后台 | `-prd-bms` | `XxxBmsController` | `/api/bms/<模块>/<实体小驼峰>` |
| 客户端（App、小程序、H5 等） | `-prd-client` | `XxxController` | `/api/<模块>/<实体小驼峰>` |

  项目只有一个 prd 模块、或者没有区分两端时，跟项目现状。两端都要同一个能力时各写一个接口，都调同一个 `IXxxApi`，不互相调用；客户端接口只开放客户端需要的字段和操作，不照搬后台的全部接口（尤其是删除、启用禁用）。
- 路径格式与同项目其他 Controller 保持一致。
- 放在名为 `controller` 的包里。框架的 `ControllerAspect` 按 `com.mcst..*.controller..*` 切入，对 `SearchRequest` 做字段名和关键词的 SQL 注入校验；业务包名不是 `com.mcst` 开头时，要配置 `easyfk.config.aspect.controller.pointcut`，否则校验不生效。
- 只注入 `IXxxApi`，不注入 Service、Repository、Remote。
- `@Tag`、每个方法的 `@Operation(summary = "...")` 都写中文。
- 注册方式跟项目现状（组件扫描，或者像 auth 那样在 Controller 配置类里注册），见 [09-config.md](09-config.md)。

## 2. 标准接口

管理后台的一个可维护实体通常有下面六个接口（上面的 `OrderBmsController`）。客户端一般只要详情、分页或列表这类查询，加上业务需要的少数写操作。用户只要其中几个时，只写要求的。

| 接口 | 方法与路径 | 入参 | 返回 |
|---|---|---|---|
| 详情 | `GET /detail` | `@RequestParam("id") String id` | `RRBuilder.buildSuccessBody(api.queryById(id))` |
| 分页 | `GET /queryPage` | `@Validated XxxReq`（查询串） | `RRBuilder.buildBodyByPageResult(api.queryByPage(...))` |
| 新增 / 编辑 | `POST /addOrEdit` | `@Validated @RequestBody XxxEditReq` | `RRBuilder.buildBodyByBaseResult(api.save(...))` |
| 批量删除 | `POST /delete` | `@Validated @RequestBody BatchBasicReq<String>` | `RRBuilder.buildBodyByBaseResult(api.delete(...))` |
| 启用 / 禁用 | `POST /disable` | `@Validated @RequestBody DisableFieldReq` | `RRBuilder.buildBodyByBaseResult(api.save(...))` |
| 下拉列表 | `GET /selectList` | `@RequestParam(value = "name", required = false) String name` | `RRBuilder.buildSuccessBody(api.queryList(...))` |

```java
@Operation(summary = "详情")
@GetMapping("/detail")
@LoginResource
public ResponseResult<OrderResp> detail(@RequestParam("id") String id) {
    return RRBuilder.buildSuccessBody(this.orderApi.queryById(id));
}

@Operation(summary = "分页查询")
@GetMapping("/queryPage")
@AuthResource(id = "orderManage", name = "订单管理", pId = "tradeManage", pName = "交易管理", sort = 20100, path = "/trade/order", category = ResourceCategory.menu)
public ResponseResult<List<OrderResp>> queryPage(@Validated OrderReq req) {
    SRPBuilder<OrderReq> builder = SRPBuilder.<OrderReq>builder().example(req);
    if (EmptyUtil.isNotEmpty(req.getOrderNo())) {
        builder.likeFields(OrderReq::getOrderNo);
    }
    return RRBuilder.buildBodyByPageResult(this.orderApi.queryByPage(builder.build()));
}

@Operation(summary = "新增/编辑")
@PostMapping("/addOrEdit")
@AuthResource(id = "orderAddOrEdit", name = "新增/编辑", title = "新增/编辑", pId = "orderManage", pName = "订单管理", sort = 20101, category = ResourceCategory.action, actionCode = "addOrEdit")
public ResponseResult<?> addOrEdit(@Validated @RequestBody OrderEditReq editReq) {
    ModifyRequest<OrderReq> request = MRPBuilder.buildRequest(editReq, OrderReq.class);
    return RRBuilder.buildBodyByBaseResult(this.orderApi.save(request));
}

@Operation(summary = "批量删除")
@PostMapping("/delete")
@AuthResource(id = "orderDelete", name = "删除订单", title = "删除", pId = "orderManage", pName = "订单管理", sort = 20102, category = ResourceCategory.action, actionCode = "delete")
public ResponseResult<?> delete(@Validated @RequestBody BatchBasicReq<String> batchReq) {
    List<String> ids = SplitUtil.split(batchReq.getIds());
    ModifyRequest<OrderReq> request = MRPBuilder.<OrderReq>builder().ids(ids).build();
    return RRBuilder.buildBodyByBaseResult(this.orderApi.delete(request));
}

@Operation(summary = "启用/禁用")
@PostMapping("/disable")
@AuthResource(id = "orderDisable", name = "启用/禁用订单", title = "启用/禁用", pId = "orderManage", pName = "订单管理", sort = 20103, category = ResourceCategory.action, actionCode = "disable")
public ResponseResult<?> disable(@Validated @RequestBody DisableFieldReq disableReq) {
    DisableActionParam<OrderReq> param = new DisableActionParam<OrderReq>(disableReq)
            .setIdField(OrderReq::getOrderId)
            .setValueField(OrderReq::getForbiddenFlag)
            .setTClass(OrderReq.class);
    List<OrderReq> list = DisableUtil.createObjListByDisableAction(param);
    if (EmptyUtil.isEmpty(list)) {
        return RRBuilder.buildFailedBody("参数错误");
    }
    ModifyRequest<OrderReq> request = MRPBuilder.<OrderReq>builder().paramList(list).build();
    return RRBuilder.buildBodyByBaseResult(this.orderApi.save(request));
}

@Operation(summary = "订单下拉列表")
@GetMapping("/selectList")
@LoginResource
public ResponseResult<List<OrderResp>> selectList(@RequestParam(value = "name", required = false) String name) {
    OrderReq example = new OrderReq();
    example.setTop(20);
    SRPBuilder<OrderReq> builder = SRPBuilder.<OrderReq>builder()
            .selectFields(OrderReq::getOrderId, OrderReq::getOrderNo, OrderReq::getForbiddenFlag);
    if (EmptyUtil.isNotEmpty(name)) {
        example.setSearchKeyWord(name);
        builder.likeFields(OrderReq::getOrderNo);
    }
    return RRBuilder.buildSuccessBody(this.orderApi.queryList(builder.example(example).build()));
}
```

### 2.1 写法要点

- **查询**：`SRPBuilder.<XxxReq>builder().example(req)` 把前端传的非空字段作为等值条件，文本字段要模糊查询时加 `likeFields(...)`。分页参数 `page`、`limit`、排序 `ascFields` / `descFields` 都在 `BasicParam` 里，前端直接传，Controller 不另外处理。
- **下拉列表**：`selectFields` 只查要显示的列；**一定要设 `top`**，否则会查全表。关键词放在 `searchKeyWord`，配合不带值的 `likeFields` 做多字段模糊查询。
- **新增编辑**：`MRPBuilder.buildRequest(editReq, XxxReq.class)` 把 EditReq 转成 Req 包进 `ModifyRequest`。带主键就是编辑，不带就是新增，由 `ServiceUtil.save` 判断，Controller 不分两个接口。要把字段清空时用 `MRPBuilder.builder().enableNullFields(...)`。
- **删除**：前端传逗号分隔的 `ids`，用 `SplitUtil.split` 拆开再交给 `MRPBuilder.ids(...)`。
- **启用禁用**：用 `DisableUtil` 按 `ids` 和 `value` 批量构造「只有主键和状态字段」的对象，再走 `save`。不要为启用、禁用各写一个接口。
- 参数名都用 `@RequestParam("xxx")` 显式写出，不依赖编译参数 `-parameters`。
- 返回值统一 `ResponseResult<T>`，用 `RRBuilder` 构造：查单个和列表用 `buildSuccessBody`，分页用 `buildBodyByPageResult`，Service 返回 `BaseResult` 时用 `buildBodyByBaseResult`，参数类失败用 `buildFailedBody(msg)` 或 `buildFailedBody(code, msg)`。
- 业务异常直接往上抛，由框架的全局异常处理转成失败响应。Controller 里不写 `try/catch` 吞异常，也不 `catch` 后返回 `buildFailedBody`。

### 2.2 当前用户

需要当前登录用户时用 `UserDataContext.getUserData()`，**先判空**再用。用户相关的赋值（租户、操作人）尽量放到 Service 里统一处理（见 [04-service.md](04-service.md) 的 SaaS 隔离）。

客户端接口查的是「我的」数据时，必须用当前登录用户的 userId 限定范围，不能信任前端传来的 userId。SaaS 隔离工具会跳过 Customer 类型用户，客户端的数据范围要自己加条件。

## 3. 权限注解

| 场景 | 注解 |
|---|---|
| 菜单（通常挂在分页查询上） | `@AuthResource(..., category = ResourceCategory.menu)`，`path` 写前端路由 |
| 按钮（新增编辑、删除、启用禁用、导出等） | `@AuthResource(..., category = ResourceCategory.action, actionCode = "...")`，`pId` 指向所属菜单的 `id` |
| 只要登录就能访问（详情、下拉列表等） | `@LoginResource`（只能标在方法上） |
| 匿名访问 | 不加注解，并确认项目没有开 `easyfk.config.web.intercept.require-auth-by-default`，或者已经把路径加入 `easyfk.config.web.intercept.exclude-paths` |
| 控制器分组 | 类上 `@ResourceController(group, id, name, sort, path)`，同一业务模块的 Controller 用同一个 `group` |

- `@AuthResource` 的 `id` 全局唯一，`name` 必填。`id` 的命名、`sort` 的编号段跟同项目已有 Controller 的规律走。
- 不加任何注解、又没开 `require-auth-by-default` 时，接口是**匿名可访问**的。每个新接口都要明确属于上表哪一类。
- `@LoginResource` / `@AuthResource` 只在 `web-prd` 里生效。微服务（`web-micro`）里的接口由网关鉴权，注解照写，以便权限资源统一注册。

## 4. 不要这样做

- 在 Controller 里写业务判断、拼查询条件之外的逻辑、调多个 Api 组装业务流程。流程放进 Service，再通过 Api 暴露。
- Controller 直接返回 Dto、Entity，或者返回 `Map`。
- 用 `@RequestBody` 接收 GET 请求的参数，或把查询条件做成 `POST` 的 JSON 而项目里同类接口都是 GET。
- 自定义返回包装类，绕开 `ResponseResult` / `RRBuilder`。
