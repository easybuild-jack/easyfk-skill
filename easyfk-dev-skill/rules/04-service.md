# 04 Service 层

业务逻辑都在 Service：条件组装、数据隔离、唯一性以外的业务校验、关联检查、事务。`IBaseService`、`ServiceUtil`、`UserDataFiltrationUtil` 的完整行为见 `modules/easyfk-service-skill.md`。

## 1. 接口

```java
public interface IOrderService extends IBaseService<OrderResp, String, OrderReq> {

    /**
     * 取消订单。订单已发货时抛出业务异常，取消成功返回成功结果。
     */
    BaseResult<?> cancel(String orderId);
}
```

- 泛型 **Resp、主键、Req**。基础方法不重复声明。
- `IXxxService` 只在进程内用，可以有可变参数；对外契约是 `IXxxApi`（见 [05-api.md](05-api.md)）。
- 扩展方法在接口上写注释：做什么、失败意味着什么。

## 2. 实现

```java
@Slf4j
public class OrderServiceImpl implements IOrderService {
    @Resource
    private IOrderRepository orderRepository;

    @Resource
    private IOrderItemRepository orderItemRepository;

    @Override
    public OrderResp queryById(String id, String... selectColumns) {
        return TransformUtil.transformObj(this.orderRepository.queryById(id, selectColumns), OrderResp.class);
    }

    @Override
    public OrderResp queryOneByField(String field, Object value, String... selectColumns) {
        return TransformUtil.transformObj(this.orderRepository.queryOneByField(field, value, selectColumns), OrderResp.class);
    }

    @Override
    public List<OrderResp> queryList(SearchRequest<OrderReq> param) {
        return TransformUtil.transformList(this.orderRepository.queryByCondition(ConditionUtil.conditionByRequest(param)), OrderResp.class);
    }

    @Override
    public OrderResp queryOne(SearchRequest<OrderReq> param) {
        return TransformUtil.transformObj(this.orderRepository.queryOneByCondition(ConditionUtil.conditionByRequest(param)), OrderResp.class);
    }

    @Override
    public long count(SearchRequest<OrderReq> param) {
        return this.orderRepository.countByCondition(ConditionUtil.conditionByRequest(param));
    }

    @Override
    public boolean exists(SearchRequest<OrderReq> param) {
        return this.orderRepository.exists(ConditionUtil.conditionByRequest(param));
    }

    @Override
    public PageResult<OrderResp> queryByPage(SearchRequest<OrderReq> param) {
        return TransformUtil.transformPageResult(this.orderRepository.queryByPage(ConditionUtil.conditionByRequest(param)), OrderResp.class);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public BaseResult<?> save(ModifyRequest<OrderReq> param) {
        return ServiceUtil.save(param, this.orderRepository, OrderDto.class);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public BaseResult<?> delete(ModifyRequest<OrderReq> param) {
        List<?> ids = param.getIdList();
        if (EmptyUtil.isEmpty(ids)) {
            throw new BusinessException(OrderErrorEnum.ID_REQUIRED);
        }
        SearchCondition used = SCBuilder.<OrderItemDto>builder()
                .inCondition(OrderItemDto::getOrderId, ids)
                .build();
        if (this.orderItemRepository.exists(used)) {
            throw new BusinessException(OrderErrorEnum.ORDER_IN_USE);
        }
        return ServiceUtil.delete(param, this.orderRepository, OrderDto.class);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public String insertAndReturnId(OrderReq param) {
        return ServiceUtil.insertAndReturnId(param, this.orderRepository, OrderDto.class);
    }
}
```

### 2.1 查询

- 查询统一走 `ConditionUtil.conditionByRequest(param)` → Repository → `TransformUtil` 转 Resp。不在 Service 里手动把 Req 的字段一个个搬进条件。
- `ConditionUtil` 会把 `parmaObj` 里所有非空字段转成等值条件，`likeFields` 里的字段转成 LIKE，`searchKeyWord` 配合没有值的 `likeFields` 做多字段模糊查询。所以前端传什么字段就按什么字段查，Controller 只需要声明哪些字段走 LIKE。
- 默认条件之外还要加条件时，在 Service 里用 `SCBuilder` 基于转换结果追加：`SCBuilder.builder(ConditionUtil.conditionByRequest(param)).equalsConditions(...).build()`。字段用方法引用（`OrderDto::getStatus`），不写字符串。
- `queryOne*` 不限制条数，可能命中多条时加 `top(1)` 或用唯一条件。
- `queryList` 必须有上限：前端下拉、导出等场景由调用方设置 `top`，Service 里给内部调用的列表查询也要带上限或分页。
- 循环里不查库。先按 `inCondition` 一次查出来，再在内存里组装。

### 2.2 写入

- 保存统一用 `ServiceUtil.save(param, repo, XxxDto.class)`：有主键且记录存在时按主键选择性更新（只更新非空字段），否则插入；插入前按 `@SingleUniqueField` / `@CombUniqueField` 校验唯一性。不要自己先查再判断 insert 还是 update。
- 新增后要拿主键时用 `insertAndReturnId`。
- 删除用 `ServiceUtil.delete`，删除前的关联检查（被引用不能删）写在 Service 里，见上例。
- 要把某个字段显式改成 null 时，用 `ModifyRequest` 的 `enableNullFields`（由 Controller 用 `MRPBuilder` 设置），不要先查出整条再覆盖。

### 2.3 事务

- `save`、`delete`、`insertAndReturnId` 和所有自定义写方法加 `@Transactional(rollbackFor = Exception.class)`。`ServiceUtil.save` 会逐条写 `paramList`，批量启用禁用时一条失败要整批回滚。
- 事务只加在 Service 实现的 public 方法上，不加在 Controller、ApiServerImpl、Repository 上。同一个类里方法互相调用不走代理，事务不生效，需要时拆到另一个 Service。
- 事务里不做远程调用、不发 MQ、不做耗时 IO。必须在提交后才做的事（如发消息），用 `TransactionSynchronization` 或项目已有的事件机制在提交后执行。
- Service 模块要能编译 `@Transactional`：`build.gradle` 里 `compileOnly 'org.springframework:spring-tx'`（参考结构 [01-project.md](01-project.md)）。

### 2.4 SaaS 数据隔离

实体有租户字段（如 `agentId`、`merchantId`）、并且项目要求按当前登录用户隔离数据时才做：

```java
@Override
public PageResult<OrderResp> queryByPage(SearchRequest<OrderReq> param) {
    UserDataFiltrationUtil.saasDataFiltration(param, OrderReq.class, Map.of(
            OrderReq::getAgentId, UserData::getAgentId,
            OrderReq::getMerchantId, UserData::getMerchantId
    ));
    return TransformUtil.transformPageResult(this.orderRepository.queryByPage(ConditionUtil.conditionByRequest(param)), OrderResp.class);
}

@Override
@Transactional(rollbackFor = Exception.class)
public BaseResult<?> save(ModifyRequest<OrderReq> param) {
    UserDataFiltrationUtil.setSaasData(param, Map.of(
            OrderReq::getAgentId, UserData::getAgentId,
            OrderReq::getMerchantId, UserData::getMerchantId
    ));
    return ServiceUtil.save(param, this.orderRepository, OrderDto.class);
}
```

- 查询（`queryList`、`queryByPage`、`queryOne`、`count`）用 `saasDataFiltration`，写入用 `setSaasData`，两边的字段要对应。
- 上下文里没有 `UserData`（异步线程、定时任务、内部 RPC 没透传用户）时，这两个方法直接跳过，返回全量数据。必须隔离的场景先判断 `UserDataContext.getUserData() != null`，为空就抛异常。
- 平台用户和 Customer 用户会被跳过。Customer 的数据范围要按 userId 自己加条件。
- 按部门等「IN 范围」隔离用 `dataInFiltration`。

### 2.5 依赖注入

- 用 `@Resource` 注入自己模块的 Repository 接口；需要别的业务模块的数据时，注入对方的 `IXxxApi`，不注入对方的 Repository 或 Service。
- 不注入 Mapper，不 `new` Repository。

## 3. 不要这样做

- 在 Controller 或 ApiServerImpl 里写业务判断，或者让 Controller 直接调 Repository。
- 返回 Dto 或 Entity 给上层。Service 对外只返回 Resp。
- 用 `queryList` 不带上限去查全表，再在内存里分页或筛选。
- 用 `customConditionSql` 拼接前端传来的值。
- 自己拼 `UPDATE ... SET deleted = 1` 做删除，绕过 Repository。
