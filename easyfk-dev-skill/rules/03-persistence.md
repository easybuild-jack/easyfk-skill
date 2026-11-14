# 03 持久层：Entity / Mapper / Repository（MyBatis-Plus）

本篇只写 `orm-mybatis`（MyBatis-Plus）的写法。用 MyBatis-Flex 或 Hibernate 的项目，分层和 Repository 接口不变，实体和实现类读 `modules/easyfk-component-orm-skill.md`，并参照项目里已有的实体。Repository 的条件、分页、默认排序等行为见 `modules/easyfk-repository-skill.md`。

持久层放在哪个模块看项目形态（[01-project.md](01-project.md) §2）：single / sc / smart 都放在 server 的 `repository`、`persistence` 包里；组件化项目（如 auth）拆成 `-orm-api`（接口）和 `-orm-plus`（实现）。

## 1. Repository 接口

Service 只依赖它：

```java
public interface IOrderRepository extends IBaseRepository<OrderDto, String> {
}
```

- 泛型是 **Dto、主键**，不是 Entity。接口对外只暴露 Dto，Entity 不出持久层。
- 基础的查询、分页、计数、插入、按主键或条件删除、选择性更新，`IBaseRepository` 都有，不要重复声明。
- 需要自定义 SQL（多表关联、统计、批量更新）时，在这里加方法，参数和返回值用 Dto 或基本类型，不出现 Entity 和 Wrapper。

## 2. Entity

```java
@Data
@EqualsAndHashCode(callSuper = true)
@Accessors(chain = true)
@TableName("t_order")
@AutoMapper(target = OrderDto.class)
public class Order extends BaseMyBatisPlusEntity<Order> {

    @PrimaryKey
    @TableId(type = IdType.ASSIGN_UUID)
    private String orderId;

    /**
     * 订单编号
     */
    @SingleUniqueField(repetitionMsg = "订单编号已存在")
    private String orderNo;

    /**
     * 禁用状态 0可用，1禁用
     */
    private Integer forbiddenFlag;
}
```

- 继承 `BaseMyBatisPlusEntity<自己>`。基类已有 `insertTime`（插入时填充）、`lastUpdateTime`（插入和更新时填充）、`deleted`（`@TableLogic` 逻辑删除，查询不返回），不要重复声明。
- 主键 `String`，同时加 `@PrimaryKey` 和 `@TableId(type = IdType.ASSIGN_UUID)`，不用数据库自增。
- 字段与 `Dto` 同名同类型，只放表里有的列。唯一性注解与 `Dto` 保持一致（校验实际按 `Dto` 上的注解执行）。
- 列名按 MyBatis-Plus 默认的驼峰转下划线，不一致时才写 `@TableField("col")`；不是表字段的属性加 `@TableField(exist = false)`。
- 自己新增的、需要自动填充的时间字段要加 `@TableField(fill = ...)`，否则不会填。

### 2.1 建表

- 主键 `varchar(36)`。
- 必须有 `insert_time`、`last_update_time`（`datetime`）和 `deleted`（`int`，默认 0）三列，对应基类字段。
- 唯一字段建唯一索引。表有逻辑删除，删掉的数据仍占着唯一索引，同一个编号删除后无法再新增。业务需要「删除后可复用」时，按项目已有表的做法处理；项目没有先例时先问用户，不自行改逻辑删除的取值规则。
- 常用查询条件的列建普通索引。表和列都写 `COMMENT`。

## 3. Mapper

```java
public interface OrderMapper extends BaseMapper<Order> {
}
```

- 放在 `...persistence.mapper` 包下，继承 MyBatis-Plus 的 `BaseMapper<Entity>`。在启动类所在包或 `com.mcst.**.persistence.mapper` 下会被自动扫描。不要自己写 `@MapperScan`，写了会关闭框架的自动扫描，框架包也得自己加进去。
- 只有自定义 SQL 才写 Mapper XML，放在 `src/main/resources/mappings/XxxMapper.xml`（项目已有其他目录时跟项目）。XML 的 `namespace` 指向 Mapper，`resultMap` 的列和属性要与当前 Entity 对得上。表结构改了，XML 一起改。
- 单表条件查询不写 XML，用 Service 里的 `SCBuilder` 条件（见 [04-service.md](04-service.md)）。
- 自定义 SQL 用 `#{}` 传参。排序字段、列名这类只能用 `${}` 的地方，先用 `SqlGuardUtil` 做白名单校验。

## 4. Repository 实现

```java
public class OrderMybatisRepository
        extends BaseMyBatisRepositoryImpl<OrderMapper, OrderDto, Order, String>
        implements IOrderRepository {
}
```

- 泛型顺序：**Mapper、Dto、Entity、主键**。
- 基础方法基类都实现了，类体通常是空的。自定义方法在这里实现：用继承来的 `baseMapper` 或 `lambdaQuery()`，结果用 `TransformUtil` 转成 Dto 再返回。
- 注册方式跟项目现状：项目用 `@AutoConfiguration` + `@Bean` 注册的（如 auth 的 `XxxOrmPlusConfig`），在配置类里加一个 `@Bean @ConditionalOnMissingBean` 方法，返回类型写接口 `IOrderRepository`；项目用注解扫描的，加 `@Repository`。见 [09-config.md](09-config.md)。

## 5. 不要这样做

- Service 里注入 Mapper，或者让 Entity 出现在 Service 及以上的层。
- Repository 接口的泛型写成 Entity。
- 用数据库自增主键，或主键用 `Long`。
- 在 Repository 里写业务规则（唯一性以外的校验、跨表业务判断），这些放 Service。
- 用 `QueryWrapper` 的字符串列名拼条件后从 Service 传下来。
