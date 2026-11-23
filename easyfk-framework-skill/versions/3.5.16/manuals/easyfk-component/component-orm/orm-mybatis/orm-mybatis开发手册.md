# orm-mybatis 开发手册

## 1. 模块概述

`orm-mybatis` 是 EasyFK 框架中基于 MyBatis-Plus 的 ORM 组件。该模块实现了框架统一的 `IBaseRepository` 接口，提供完整的 CRUD、分页查询、条件构建、逻辑删除、自动填充、DTO/PO 自动转换、数据库类型自动识别等能力，同时集成了 MyBatis-Plus 的 `ServiceImpl` 能力，是框架默认推荐的 ORM 实现。

## 2. 依赖引入

### Maven

```xml
<dependency>
    <groupId>com.mcst</groupId>
    <artifactId>orm-mybatis</artifactId>
</dependency>
```

### Gradle

```gradle
dependencies {
    implementation 'com.mcst:orm-mybatis'
}
```

> 版本号由框架统一 BOM 管理，无需手动指定。

该模块会自动传递引入以下依赖：
- `mybatis-plus-spring-boot3-starter` — MyBatis-Plus Spring Boot 3 集成
- `mybatis-plus-jsqlparser` (3.5.18.1) — SQL 解析器
- `spring-boot-starter-jdbc` — Spring JDBC 支持

## 3. 配置说明

### 3.1 数据源配置

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?useUnicode=true&characterEncoding=utf-8&serverTimezone=Asia/Shanghai
    username: root
    password: root
    driver-class-name: com.mysql.cj.jdbc.Driver
```

### 3.2 自动配置

模块无需额外开关，引入依赖后自动生效，自动完成以下配置：

| 配置项 | 说明 |
|--------|------|
| 分页插件 | `PaginationInnerInterceptor`，自动识别数据库类型 |
| 防全表操作 | `BlockAttackInnerInterceptor`，防止全表更新/删除 |
| 自动填充 | `AutoSetValueHandler`，插入/更新时自动填充时间字段 |
| 逻辑删除 | `@TableLogic` 注解驱动 |
| Mapper 扫描 | 自动扫描 `com.mcst.**.persistence.mapper` 包 |
| 数据库类型 | 从 DataSource JDBC URL 自动识别（MySQL/Oracle/PostgreSQL 等） |

### 3.3 MyBatis-Plus 可选配置

```yaml
mybatis-plus:
  mapper-locations: classpath*:mapper/**/*.xml
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl  # 开发环境打印 SQL
  global-config:
    db-config:
      logic-delete-field: deleted
      logic-delete-value: 1
      logic-not-delete-value: 0
```

## 4. 实体基类

### 4.1 BaseMyBatisPlusEntity（完整版）

包含创建时间、更新时间和逻辑删除字段，适用于大多数业务表。

```java
@Data
@TableName("t_order")
@EqualsAndHashCode(callSuper = true)
public class OrderPO extends BaseMyBatisPlusEntity<OrderPO> {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String orderNo;
    private BigDecimal amount;
    private Integer status;

    // 继承字段：insertTime、lastUpdateTime、deleted
}
```

| 继承字段 | 类型 | 注解 | 说明 |
|----------|------|------|------|
| `insertTime` | LocalDateTime | `@TableField(fill = FieldFill.INSERT)` | 插入时自动填充 |
| `lastUpdateTime` | LocalDateTime | `@TableField(fill = FieldFill.INSERT_UPDATE)` + `@AutoUpdateTime` | 插入/更新时自动填充 |
| `deleted` | Integer | `@TableLogic` + `@TableField(fill = FieldFill.INSERT, select = false)` | 逻辑删除，查询时不返回 |

### 4.2 BaseMyBatisPlusSimpleEntity（简化版）

不包含逻辑删除字段，适用于日志表、记录表等。

```java
@Data
@TableName("t_operation_log")
@EqualsAndHashCode(callSuper = true)
public class OperationLogPO extends BaseMyBatisPlusSimpleEntity<OperationLogPO> {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String operationType;
    private String content;

    // 继承字段：insertTime、lastUpdateTime
}
```

## 5. 自动填充机制

`AutoSetValueHandler` 实现 MyBatis-Plus 的 `MetaObjectHandler` 接口：

### 插入时填充

| 字段名 | 填充值 | 说明 |
|--------|--------|------|
| `createTime` | `LocalDateTime.now()` | 创建时间 |
| `insertTime` | `LocalDateTime.now()` | 插入时间 |
| `lastUpdateTime` | `LocalDateTime.now()` | 最后更新时间 |
| `modifyTime` | `LocalDateTime.now()` | 修改时间 |
| `updateTime` | `LocalDateTime.now()` | 更新时间 |
| `version` | `1L` | 乐观锁版本号 |
| `deleted` | `0` | 逻辑删除标志（正常） |

### 更新时填充

| 字段名 | 填充值 | 说明 |
|--------|--------|------|
| `modifyTime` | `LocalDateTime.now()` | 修改时间 |
| `updateTime` | `LocalDateTime.now()` | 更新时间 |
| `lastUpdateTime` | `LocalDateTime.now()` | 最后更新时间 |

> 使用 MyBatis-Plus 原生 `fillStrategy`，仅当字段值为 `null` 时填充。

## 6. Repository 层

### 6.1 定义 Mapper

```java
public interface OrderMapper extends BaseMapper<OrderPO> {
}
```

### 6.2 定义 Repository

```java
@Repository
public class OrderRepository extends BaseMyBatisRepositoryImpl<OrderMapper, OrderDTO, OrderPO, Long> {
}
```

泛型参数说明：

| 参数 | 类型 | 说明 |
|------|------|------|
| `M` | `OrderMapper` | Mapper 接口（继承 `BaseMapper`） |
| `T` | `OrderDTO` | DTO 类型（对外暴露） |
| `P` | `OrderPO` | PO 实体类型（持久层） |
| `PK` | `Long` | 主键类型 |

> `BaseMyBatisRepositoryImpl` 同时继承了 `ServiceImpl<M, P>`，因此也拥有 MyBatis-Plus `IService` 的所有能力（如 `saveBatch`、`lambdaQuery` 等）。

### 6.3 IBaseRepository 完整 API

#### 查询方法

| 方法 | 返回类型 | 说明 |
|------|----------|------|
| `queryById(id, selectColumns...)` | `T` | 按主键查询（可选字段筛选） |
| `queryByCondition(condition)` | `List<T>` | 按条件查询列表 |
| `queryOneByCondition(condition)` | `T` | 按条件查询单条 |
| `queryByField(field, value, selectFields...)` | `List<T>` | 按字段查询列表 |
| `queryOneByField(field, value, selectFields...)` | `T` | 按字段查询单条 |
| `queryByPage(condition)` | `PageResult<T>` | 分页查询 |
| `exists(field, value)` | `boolean` | 按字段判断是否存在 |
| `exists(condition)` | `boolean` | 按条件判断是否存在 |
| `countByCondition(condition)` | `long` | 按条件统计数量 |

#### 插入方法

| 方法 | 返回类型 | 说明 |
|------|----------|------|
| `insert(param)` | `BaseResult<?>` | 插入单条记录 |
| `insertBatch(data)` | `BaseResult<?>` | 批量插入（MyBatis-Plus `saveBatch`） |
| `insertAndReturnId(param)` | `PK` | 插入并返回主键 |

#### 更新方法

| 方法 | 返回类型 | 说明 |
|------|----------|------|
| `updateBySelective(param, nullProperties...)` | `BaseResult<?>` | 选择性更新（非空字段） |
| `updateEntityByCondition(param, condition)` | `BaseResult<?>` | 按条件更新 |
| `saveOrUpdateBySelective(param, nullProperties...)` | `BaseResult<?>` | 有主键且存在则更新，否则插入 |

#### 删除方法

| 方法 | 返回类型 | 说明 |
|------|----------|------|
| `deleteById(id)` | `BaseResult<?>` | 按主键删除（支持单个/逗号分隔/集合） |
| `deleteByCondition(condition)` | `BaseResult<?>` | 按条件删除 |

## 7. SearchCondition 查询条件

`SearchCondition` 是框架统一的查询条件构建器：

### 7.1 条件类型

| 条件类型 | 设置方法 | 说明 |
|----------|----------|------|
| 等值 | `setEqualsConditions(map)` | `field = value` |
| 不等值 | `setNotEqualsConditions(map)` | `field != value` |
| 模糊 | `setLikeConditions(map)` | `field LIKE '%value%'` |
| IN | `setInConditions(map)` | `field IN (v1, v2, ...)` |
| 区间 | `setRangeConditions(list)` | `field > / >= / < / <= / BETWEEN` |
| NULL | `setNullFields(fields)` | `field IS NULL` |
| 自定义 SQL | `setCustomConditionSql(sql)` | 原生 SQL 条件拼接（`apply`） |

### 7.2 排序、分组、字段选择

| 设置方法 | 说明 |
|----------|------|
| `setAscFields(fields)` | 升序排序字段 |
| `setDescFields(fields)` | 降序排序字段 |
| `setDescFirst(true)` | 降序优先 |
| `setGroupFields(fields)` | 分组字段 |
| `setSelectFields(fields)` | 查询字段 |
| `setChange(true)` | 是否驼峰转下划线（默认 `true`） |

### 7.3 分页

| 设置方法 | 说明 |
|----------|------|
| `setPageSearch(new PageSearch(page, limit))` | 设置分页参数 |
| `setPageSearch(new PageSearch(page, limit, false))` | 不查总数 |
| `setTop(n)` | 查询前 N 条 |

### 7.4 区间条件类型（RangeConditionType）

| 类型 | SQL |
|------|-----|
| `GreaterThan` | `field > value` |
| `GreaterThanOrEqual` | `field >= value` |
| `LessThan` | `field < value` |
| `LessThanOrEqual` | `field <= value` |
| `Equal` | `field = value` |
| `Between` | `field BETWEEN start AND end` |

## 8. 实战示例

### 8.1 按主键查询

```java
@Resource
private OrderRepository orderRepository;

// 查询全部字段
OrderDTO order = orderRepository.queryById(1L);

// 查询指定字段
OrderDTO order = orderRepository.queryById(1L, "orderNo", "amount", "status");
```

### 8.2 条件查询

```java
SearchCondition condition = new SearchCondition();

// 等值条件
Map<String, Object> eqMap = new HashMap<>();
eqMap.put("status", 1);
eqMap.put("userId", 100L);
condition.setEqualsConditions(eqMap);

// 模糊查询
Map<String, String> likeMap = new HashMap<>();
likeMap.put("orderNo", "ORD2024");
condition.setLikeConditions(likeMap);

// 排序
condition.setDescFields(new String[]{"insertTime"});

List<OrderDTO> orders = orderRepository.queryByCondition(condition);
```

### 8.3 区间查询

```java
SearchCondition condition = new SearchCondition();

List<RangeCondition> ranges = new ArrayList<>();
ranges.add(new RangeCondition("amount", RangeConditionType.GreaterThan, 100, null));
ranges.add(new RangeCondition("insertTime", RangeConditionType.Between, "2024-01-01", "2024-12-31"));
condition.setRangeConditions(ranges);

List<OrderDTO> orders = orderRepository.queryByCondition(condition);
```

### 8.4 IN 查询

```java
SearchCondition condition = new SearchCondition();

Map<String, List<?>> inMap = new HashMap<>();
inMap.put("status", List.of(1, 2, 3));
condition.setInConditions(inMap);

List<OrderDTO> orders = orderRepository.queryByCondition(condition);
```

### 8.5 分页查询

```java
SearchCondition condition = new SearchCondition();
condition.setPageSearch(new PageSearch(1, 20));
condition.setDescFields(new String[]{"insertTime"});

PageResult<OrderDTO> pageResult = orderRepository.queryByPage(condition);
long total = pageResult.getTotal();
List<OrderDTO> rows = pageResult.getRows();
```

### 8.6 插入与更新

```java
// 插入
OrderDTO order = new OrderDTO();
order.setOrderNo("ORD_001");
order.setAmount(new BigDecimal("99.99"));
order.setStatus(0);
orderRepository.insert(order);

// 插入并返回主键
Long id = orderRepository.insertAndReturnId(order);

// 批量插入（使用 MyBatis-Plus saveBatch）
List<OrderDTO> orders = List.of(order1, order2, order3);
orderRepository.insertBatch(orders);

// 选择性更新
OrderDTO updateDTO = new OrderDTO();
updateDTO.setId(1L);
updateDTO.setStatus(2);
orderRepository.updateBySelective(updateDTO);

// 选择性更新 + 指定置空字段
orderRepository.updateBySelective(updateDTO, "remark", "memo");

// 保存或更新
orderRepository.saveOrUpdateBySelective(order);
```

### 8.7 删除

```java
// 单个删除
orderRepository.deleteById(1L);

// 批量删除（逗号分隔）
orderRepository.deleteById("1,2,3");

// 批量删除（集合）
orderRepository.deleteById(List.of(1L, 2L, 3L));

// 按条件删除
SearchCondition condition = new SearchCondition();
condition.setEqualsConditions(Map.of("status", 0));
orderRepository.deleteByCondition(condition);
```

### 8.8 使用 MyBatis-Plus 原生能力

由于 `BaseMyBatisRepositoryImpl` 继承了 `ServiceImpl`，可直接使用 MyBatis-Plus 的全部能力：

```java
// Lambda 查询
List<OrderPO> list = orderRepository.lambdaQuery()
    .eq(OrderPO::getStatus, 1)
    .ge(OrderPO::getAmount, 100)
    .orderByDesc(OrderPO::getInsertTime)
    .list();

// Lambda 更新
orderRepository.lambdaUpdate()
    .set(OrderPO::getStatus, 2)
    .eq(OrderPO::getId, 1L)
    .update();

// 批量保存（分批提交）
orderRepository.saveBatch(poList, 500);
```

## 9. DTO / PO 自动转换

`BaseMyBatisRepositoryImpl` 内部自动完成 DTO 和 PO 之间的转换：

- **查询**：PO → DTO（通过 `TransformUtil.transformObj`）
- **插入/更新**：DTO → PO（通过 `TransformUtil.transformObj`）
- **列表转换**：`TransformUtil.transformList`

## 10. 安全防护

### 防全表操作

`BlockAttackInnerInterceptor` 拦截器自动阻止以下危险操作：
- 全表更新（`UPDATE` 无 `WHERE` 条件）
- 全表删除（`DELETE` 无 `WHERE` 条件）

### 数据库类型自动识别

`MybatisPlusConfigure` 通过 DataSource 的 JDBC URL 自动识别数据库类型，无需手动配置分页方言：
- MySQL → `DbType.MYSQL`
- Oracle → `DbType.ORACLE`
- PostgreSQL → `DbType.POSTGRE_SQL`
- 识别失败时默认使用 `DbType.MYSQL`

## 11. 包结构

```
com.mcst.easyfk.service.mybatisplus
├── ApplicationStarter.java                    # 启动入口（集成 Mapper 扫描）
├── MybatisPlusServiceScanner.java             # Mapper 包扫描配置
├── annotation
│   └── Column.java                            # 字段注解
├── config
│   └── MybatisPlusConfigure.java              # 自动配置（分页/防攻击/填充/数据库类型识别）
├── handler
│   └── AutoSetValueHandler.java               # MetaObjectHandler 自动填充
├── impl
│   └── BaseMyBatisRepositoryImpl.java         # IBaseRepository + ServiceImpl 实现
├── persistence
│   ├── BaseMyBatisPlusEntity.java             # 实体基类（完整版：时间 + 逻辑删除）
│   └── BaseMyBatisPlusSimpleEntity.java       # 实体基类（简化版：仅时间）
└── util
    ├── EqualConditionUtil.java                # 等值条件构建
    ├── InConditionUtil.java                   # IN 条件构建
    ├── LikeConditionUtil.java                 # 模糊查询条件构建
    ├── MyBatisPlusWrapperUtil.java            # QueryWrapper 核心构建器
    ├── MybatisPlusUtil.java                   # 通用工具（ID 查询/删除/分页/保存更新）
    ├── NullConditionUtil.java                 # NULL 条件构建
    └── RangeConditionUtil.java                # 区间条件构建
```

## 12. 最佳实践

1. **实体基类选择**：有逻辑删除需求用 `BaseMyBatisPlusEntity`，无需逻辑删除用 `BaseMyBatisPlusSimpleEntity`。
2. **DTO 与 PO 分离**：PO 对应数据库表结构，DTO 对外暴露，Repository 自动完成转换。
3. **字段命名**：Java 层使用驼峰命名，框架自动转换为下划线列名。
4. **选择性更新**：`updateBySelective` 仅更新非空字段；需要置空时通过 `nullProperties` 参数指定。
5. **分页默认值**：未设置分页参数时，默认查询第 1 页、每页 10 条。
6. **默认排序**：未设置排序条件时，如果实体包含 `insertTime` 字段，自动按 `insert_time DESC` 排序。
7. **条件优先级**：同一字段同时出现在多种条件中时，等值条件自动让位，避免冲突。
8. **批量操作**：`insertBatch` 使用 MyBatis-Plus 的 `saveBatch`，支持分批提交。
9. **与 orm-flex 迁移**：`IBaseRepository` 接口完全一致，迁移只需更换 Repository 基类和实体注解。
