# orm-flex 开发手册

## 1. 模块概述

`orm-flex` 是 EasyFK 框架中基于 MyBatis-Flex 的 ORM 组件。该模块实现了框架统一的 `IBaseRepository` 接口，提供完整的 CRUD、分页查询、条件构建、逻辑删除、自动填充、DTO/PO 自动转换等能力，与 `orm-mybatis`（MyBatis-Plus 版本）API 完全对齐，适用于需要高性能 ORM 或从 MyBatis-Plus 迁移到 MyBatis-Flex 的 Spring Boot 3.x 项目。

## 2. 依赖引入

### Maven

```xml
<dependency>
    <groupId>com.mcst</groupId>
    <artifactId>orm-flex</artifactId>
</dependency>
```

### Gradle

```gradle
dependencies {
    implementation 'com.mcst:orm-flex'
}
```

> 版本号由框架统一 BOM 管理，无需手动指定。

该模块会自动传递引入以下依赖：
- `mybatis-flex-spring-boot3-starter` (1.11.4) — MyBatis-Flex 核心
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
| 逻辑删除 | 字段 `deleted`，正常值 `0`，删除值 `1` |
| 插入监听器 | 自动填充创建时间、版本号、逻辑删除标志 |
| 更新监听器 | 自动填充更新时间 |
| Mapper 扫描 | 自动扫描 `com.mcst.**.persistence.mapper` 包 |
| SQL 审计 | 开发模式下自动记录 SQL 及执行时间 |

## 4. 实体基类

### 4.1 BaseFlexEntity（完整版）

包含创建时间、更新时间和逻辑删除字段，适用于大多数业务表。

```java
@Data
@Table("t_order")
@EqualsAndHashCode(callSuper = true)
public class OrderPO extends BaseFlexEntity<OrderPO> {

    @Id(keyType = KeyType.Auto)
    private Long id;

    private String orderNo;
    private BigDecimal amount;
    private Integer status;

    // 继承字段：insertTime、lastUpdateTime、deleted
}
```

| 继承字段 | 类型 | 说明 |
|----------|------|------|
| `insertTime` | LocalDateTime | 插入时间（自动填充 `now()`） |
| `lastUpdateTime` | LocalDateTime | 最后更新时间（插入/更新时自动填充 `now()`） |
| `deleted` | Integer | 逻辑删除标志（`0`=正常，`1`=删除） |

### 4.2 BaseFlexSimpleEntity（简化版）

不包含逻辑删除字段，仅包含时间戳字段，适用于日志表、记录表等无需逻辑删除的场景。

```java
@Data
@Table("t_operation_log")
@EqualsAndHashCode(callSuper = true)
public class OperationLogPO extends BaseFlexSimpleEntity<OperationLogPO> {

    @Id(keyType = KeyType.Auto)
    private Long id;

    private String operationType;
    private String content;

    // 继承字段：insertTime、lastUpdateTime
}
```

## 5. 自动填充机制

`AutoSetValueHandler` 在插入和更新时自动填充指定字段（仅当字段值为 `null` 时填充）：

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

> 填充策略：仅当字段当前值为 `null` 时才填充，不会覆盖已有值。

## 6. Repository 层

### 6.1 定义 Mapper

```java
public interface OrderMapper extends BaseMapper<OrderPO> {
}
```

### 6.2 定义 Repository

```java
@Repository
public class OrderRepository extends BaseFlexRepositoryImpl<OrderMapper, OrderDTO, OrderPO, Long> {
}
```

泛型参数说明：

| 参数 | 类型 | 说明 |
|------|------|------|
| `M` | `OrderMapper` | Mapper 接口 |
| `T` | `OrderDTO` | DTO 类型（对外暴露） |
| `P` | `OrderPO` | PO 实体类型（持久层） |
| `PK` | `Long` | 主键类型 |

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
| `insertBatch(data)` | `BaseResult<?>` | 批量插入 |
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

`SearchCondition` 是框架统一的查询条件构建器，支持多种条件类型：

### 7.1 条件类型

| 条件类型 | 设置方法 | 说明 |
|----------|----------|------|
| 等值 | `setEqualsConditions(map)` | `field = value` |
| 不等值 | `setNotEqualsConditions(map)` | `field != value` |
| 模糊 | `setLikeConditions(map)` | `field LIKE '%value%'` |
| IN | `setInConditions(map)` | `field IN (v1, v2, ...)` |
| 区间 | `setRangeConditions(list)` | `field > / >= / < / <= / BETWEEN` |
| NULL | `setNullFields(fields)` | `field IS NULL` |
| 自定义 SQL | `setCustomConditionSql(sql)` | 原生 SQL 条件拼接 |

### 7.2 排序、分组、字段选择

| 设置方法 | 说明 |
|----------|------|
| `setAscFields(fields)` | 升序排序字段 |
| `setDescFields(fields)` | 降序排序字段 |
| `setDescFirst(true)` | 降序优先（同时有升序和降序时） |
| `setGroupFields(fields)` | 分组字段 |
| `setSelectFields(fields)` | 查询字段（不设置则查询全部） |
| `setChange(true)` | 是否驼峰转下划线（默认 `true`） |

### 7.3 分页

| 设置方法 | 说明 |
|----------|------|
| `setPageSearch(new PageSearch(page, limit))` | 设置分页参数 |
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
// 金额大于 100
ranges.add(new RangeCondition("amount", RangeConditionType.GreaterThan, 100, null));
// 创建时间范围
ranges.add(new RangeCondition("insertTime", RangeConditionType.Between, "2024-01-01", "2024-12-31"));
condition.setRangeConditions(ranges);

List<OrderDTO> orders = orderRepository.queryByCondition(condition);
```

### 8.4 IN 查询

```java
SearchCondition condition = new SearchCondition();

Map<String, List<?>> inMap = new HashMap<>();
inMap.put("status", List.of(1, 2, 3));
inMap.put("type", List.of("A", "B"));
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

// 批量插入
List<OrderDTO> orders = List.of(order1, order2, order3);
orderRepository.insertBatch(orders);

// 选择性更新（非空字段更新）
OrderDTO updateDTO = new OrderDTO();
updateDTO.setId(1L);
updateDTO.setStatus(2);
orderRepository.updateBySelective(updateDTO);

// 选择性更新 + 指定置空字段
orderRepository.updateBySelective(updateDTO, "remark", "memo");

// 保存或更新（有 ID 且存在则更新，否则插入）
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
Map<String, Object> eqMap = Map.of("status", 0);
condition.setEqualsConditions(eqMap);
orderRepository.deleteByCondition(condition);
```

### 8.8 按字段查询

```java
// 按字段查询列表
List<OrderDTO> orders = orderRepository.queryByField("status", 1);

// 按字段查询单条
OrderDTO order = orderRepository.queryOneByField("orderNo", "ORD_001");

// 指定查询字段
OrderDTO order = orderRepository.queryOneByField("orderNo", "ORD_001", "id", "orderNo", "amount");

// 判断是否存在
boolean exists = orderRepository.exists("orderNo", "ORD_001");
```

## 9. DTO / PO 自动转换

`BaseFlexRepositoryImpl` 内部自动完成 DTO 和 PO 之间的转换：

- **查询**：PO → DTO（通过 `TransformUtil.transformObj`）
- **插入/更新**：DTO → PO（通过 `TransformUtil.transformObj`）
- **列表转换**：`TransformUtil.transformList`

开发者只需关注 DTO 层，无需手动处理 PO 转换。

## 10. 条件构建工具类

模块提供 6 个独立的条件构建工具类，支持直接构建 `QueryWrapper`：

| 工具类 | 说明 |
|--------|------|
| `EqualConditionUtil` | 等值条件（eq），支持单个和批量 |
| `InConditionUtil` | IN / NOT IN 条件，支持批量 |
| `LikeConditionUtil` | 模糊查询（LIKE / LIKE_LEFT / LIKE_RIGHT） |
| `RangeConditionUtil` | 区间条件（gt / ge / lt / le / between），支持日期字符串自动转换 |
| `NullConditionUtil` | IS NULL / IS NOT NULL，支持批量 |
| `FlexWrapperUtil` | 核心构建器，整合以上所有条件类型 |

## 11. 包结构

```
com.mcst.easyfk.service.flex
├── ApplicationStarter.java                # 启动入口（集成 Mapper 扫描）
├── FlexServiceScanner.java                # Mapper 包扫描配置
├── config
│   └── FlexConfigure.java                 # 全局配置（逻辑删除 / 监听器 / SQL 审计）
├── handler
│   └── AutoSetValueHandler.java           # 自动填充处理器（插入/更新时间、版本号）
├── impl
│   └── BaseFlexRepositoryImpl.java        # IBaseRepository 实现（核心 CRUD）
├── persistence
│   ├── BaseFlexEntity.java                # 实体基类（完整版：时间 + 逻辑删除）
│   └── BaseFlexSimpleEntity.java          # 实体基类（简化版：仅时间）
└── util
    ├── EqualConditionUtil.java            # 等值条件构建
    ├── FlexUtil.java                      # 通用工具（ID查询 / 删除 / 分页 / 保存更新）
    ├── FlexWrapperUtil.java               # QueryWrapper 核心构建器
    ├── InConditionUtil.java               # IN 条件构建
    ├── LikeConditionUtil.java             # 模糊查询条件构建
    ├── NullConditionUtil.java             # NULL 条件构建
    └── RangeConditionUtil.java            # 区间条件构建
```

## 12. 最佳实践

1. **实体基类选择**：有逻辑删除需求用 `BaseFlexEntity`，无需逻辑删除用 `BaseFlexSimpleEntity`。
2. **DTO 与 PO 分离**：PO 对应数据库表结构，DTO 对外暴露，Repository 自动完成转换。
3. **字段命名**：Java 层使用驼峰命名，框架自动转换为下划线列名（`change = true`）。
4. **自动填充**：时间字段命名建议使用 `insertTime`、`lastUpdateTime`，与基类和填充处理器一致。
5. **批量删除**：`deleteById` 支持逗号分隔的字符串、集合、单个 ID，根据场景选择。
6. **选择性更新**：`updateBySelective` 仅更新非空字段；需要将某字段置空时，通过 `nullProperties` 参数指定。
7. **分页默认值**：未设置分页参数时，默认查询第 1 页、每页 10 条。
8. **默认排序**：未设置排序条件时，如果实体包含 `insertTime` 字段，自动按 `insert_time DESC` 排序。
9. **条件优先级**：当同一字段同时出现在 `equalsConditions` 和 `inConditions`/`likeConditions`/`rangeConditions` 中时，等值条件会被自动移除，以避免冲突。
