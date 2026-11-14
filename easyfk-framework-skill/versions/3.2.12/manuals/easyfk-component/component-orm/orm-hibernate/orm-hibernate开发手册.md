# orm-hibernate 开发手册

## 1. 模块概述

`orm-hibernate` 是 EasyFK 框架中基于 Spring Data JPA + Hibernate 的 ORM 组件。该模块实现了框架统一的 `IBaseRepository` 接口，提供完整的 CRUD、分页查询、条件构建、逻辑删除、自动填充、DTO/PO 自动转换等能力，与 `orm-flex`（MyBatis-Flex 版本）、`orm-mybatis`（MyBatis-Plus 版本）API 完全对齐，适用于需要 JPA 标准规范或 Hibernate 高级特性的 Spring Boot 3.x 项目。

## 2. 依赖引入

### Maven

```xml
<dependency>
    <groupId>com.mcst</groupId>
    <artifactId>orm-hibernate</artifactId>
</dependency>
```

### Gradle

```gradle
dependencies {
    implementation 'com.mcst:orm-hibernate'
}
```

> 版本号由框架统一 BOM 管理，无需手动指定。

该模块会自动传递引入以下依赖：
- `spring-boot-starter-data-jpa` — Spring Data JPA + Hibernate 核心

## 3. 配置说明

### 3.1 数据源配置

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?useUnicode=true&characterEncoding=utf-8&serverTimezone=Asia/Shanghai
    username: root
    password: root
    driver-class-name: com.mysql.cj.jdbc.Driver
  jpa:
    hibernate:
      ddl-auto: none
    show-sql: false
    properties:
      hibernate:
        format_sql: true
        dialect: org.hibernate.dialect.MySQLDialect
```

### 3.2 自动配置

模块无需额外开关，引入依赖后自动生效，自动完成以下配置：

| 配置项 | 说明 |
|--------|------|
| 逻辑删除 | 字段 `deleted`，正常值 `0`，删除值 `1`（Repository 层自动处理） |
| 插入监听器 | 自动填充创建时间、版本号、逻辑删除标志（@PrePersist） |
| 更新监听器 | 自动填充更新时间（@PreUpdate） |
| Entity 扫描 | 自动扫描 `com.mcst.**.persistence` 包 |
| Repository 扫描 | 自动扫描 `com.mcst.**.persistence.repository` 包 |

## 4. 实体基类

### 4.1 BaseHibernateEntity（完整版）

包含创建时间、更新时间和逻辑删除字段，适用于大多数业务表。

```java
@Data
@Entity
@Table(name = "t_order")
@EqualsAndHashCode(callSuper = true)
public class OrderPO extends BaseHibernateEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String orderNo;
    private BigDecimal amount;
    private Integer status;

    // 继承字段：insertTime、lastUpdateTime、deleted
}
```

| 继承字段 | 类型 | 说明 |
|----------|------|------|
| `insertTime` | LocalDateTime | 插入时间（@PrePersist 自动填充） |
| `lastUpdateTime` | LocalDateTime | 最后更新时间（@PrePersist/@PreUpdate 自动填充） |
| `deleted` | Integer | 逻辑删除标志（`0`=正常，`1`=删除） |

### 4.2 BaseHibernateSimpleEntity（简化版）

不包含逻辑删除字段，仅包含时间戳字段，适用于日志表、记录表等无需逻辑删除的场景。

```java
@Data
@Entity
@Table(name = "t_operation_log")
@EqualsAndHashCode(callSuper = true)
public class OperationLogPO extends BaseHibernateSimpleEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String operationType;
    private String content;

    // 继承字段：insertTime、lastUpdateTime
}
```

## 5. 自动填充机制

`AutoSetValueHandler` 通过 JPA `@PrePersist` 和 `@PreUpdate` 回调在插入和更新时自动填充指定字段（仅当字段值为 `null` 时填充）：

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

### 6.1 定义 JPA Repository 接口

```java
public interface OrderJpaRepository extends JpaRepository<OrderPO, Long>, JpaSpecificationExecutor<OrderPO> {
}
```

### 6.2 定义 Repository

```java
@Repository
public class OrderRepository extends BaseHibernateRepositoryImpl<OrderJpaRepository, OrderDTO, OrderPO, Long> {
}
```

泛型参数说明：

| 参数 | 类型 | 说明 |
|------|------|------|
| `R` | `OrderJpaRepository` | JPA Repository 接口（需同时继承 JpaRepository 和 JpaSpecificationExecutor） |
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

// 查询指定字段（JPA 模式下加载完整实体）
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

`BaseHibernateRepositoryImpl` 内部自动完成 DTO 和 PO 之间的转换：

- **查询**：PO → DTO（通过 `TransformUtil.transformObj`）
- **插入/更新**：DTO → PO（通过 `TransformUtil.transformObj`）
- **列表转换**：`TransformUtil.transformList`

开发者只需关注 DTO 层，无需手动处理 PO 转换。

## 10. 条件构建工具类

模块提供 6 个独立的条件构建工具类，支持直接构建 JPA Criteria Predicate：

| 工具类 | 说明 |
|--------|------|
| `EqualConditionUtil` | 等值条件（eq），支持单个和批量 |
| `InConditionUtil` | IN / NOT IN 条件，支持批量 |
| `LikeConditionUtil` | 模糊查询（LIKE / LIKE_LEFT / LIKE_RIGHT） |
| `RangeConditionUtil` | 区间条件（gt / ge / lt / le / between），支持日期字符串自动转换 |
| `NullConditionUtil` | IS NULL / IS NOT NULL，支持批量 |
| `HibernateWrapperUtil` | 核心构建器，整合以上所有条件类型，输出 Specification |

## 11. 包结构

```
com.mcst.easyfk.service.hibernate
├── ApplicationStarter.java                    # 启动入口（集成 Entity/Repository 扫描）
├── HibernateServiceScanner.java               # Entity 和 JPA Repository 包扫描配置
├── config
│   └── HibernateConfigure.java                # 全局配置（自动填充处理器）
├── handler
│   └── AutoSetValueHandler.java               # 自动填充处理器（@PrePersist/@PreUpdate）
├── impl
│   └── BaseHibernateRepositoryImpl.java       # IBaseRepository 实现（核心 CRUD）
├── persistence
│   ├── BaseHibernateEntity.java               # 实体基类（完整版：时间 + 逻辑删除）
│   └── BaseHibernateSimpleEntity.java         # 实体基类（简化版：仅时间）
└── util
    ├── EqualConditionUtil.java                # 等值条件构建
    ├── HibernateUtil.java                     # 通用工具（ID查询 / 删除 / 分页 / 保存更新）
    ├── HibernateWrapperUtil.java              # Specification 核心构建器
    ├── InConditionUtil.java                   # IN 条件构建
    ├── LikeConditionUtil.java                 # 模糊查询条件构建
    ├── NullConditionUtil.java                 # NULL 条件构建
    └── RangeConditionUtil.java                # 区间条件构建
```

## 12. 与 orm-flex 的差异

| 维度 | orm-flex (MyBatis-Flex) | orm-hibernate (Hibernate) |
|------|------------------------|---------------------------|
| 底层 ORM | MyBatis-Flex | Spring Data JPA + Hibernate |
| Mapper/Repository | `BaseMapper<P>` | `JpaRepository<P, PK> & JpaSpecificationExecutor<P>` |
| 查询构建器 | `QueryWrapper` | `Specification<T>` (JPA Criteria API) |
| 实体基类 | 继承 `Model<T>`（Active Record） | 使用 `@MappedSuperclass`（标准 JPA） |
| 逻辑删除 | MyBatis-Flex 全局配置 | Repository 层自动处理 |
| 自动填充 | `InsertListener` / `UpdateListener` | `@PrePersist` / `@PreUpdate` (JPA 生命周期回调) |
| 字段名映射 | 手动 camelCase → underscore | Hibernate 命名策略自动映射 |
| 条件字段名 | 使用数据库列名（下划线） | 使用 Java 属性名（驼峰） |
| 事务管理 | MyBatis 自行管理 | Spring `@Transactional` |

## 13. 最佳实践

1. **实体基类选择**：有逻辑删除需求用 `BaseHibernateEntity`，无需逻辑删除用 `BaseHibernateSimpleEntity`。
2. **DTO 与 PO 分离**：PO 对应数据库表结构，DTO 对外暴露，Repository 自动完成转换。
3. **JPA Repository 定义**：需同时继承 `JpaRepository` 和 `JpaSpecificationExecutor`。
4. **自动填充**：时间字段命名建议使用 `insertTime`、`lastUpdateTime`，与基类和填充处理器一致。
5. **批量删除**：`deleteById` 支持逗号分隔的字符串、集合、单个 ID，根据场景选择。
6. **选择性更新**：`updateBySelective` 仅更新非空字段；需要将某字段置空时，通过 `nullProperties` 参数指定。
7. **分页默认值**：未设置分页参数时，默认查询第 1 页、每页 10 条。
8. **默认排序**：未设置排序条件时，如果实体包含 `insertTime` 字段，自动按 `insertTime DESC` 排序。
9. **条件优先级**：当同一字段同时出现在 `equalsConditions` 和 `inConditions`/`likeConditions`/`rangeConditions` 中时，等值条件会被自动移除，以避免冲突。
10. **条件字段名**：SearchCondition 中的字段名使用 Java 属性名（驼峰格式），JPA Criteria API 自动通过 Hibernate 命名策略映射到数据库列。
