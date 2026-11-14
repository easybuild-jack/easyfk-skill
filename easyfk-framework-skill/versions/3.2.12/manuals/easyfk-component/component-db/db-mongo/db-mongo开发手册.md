# db-mongo 开发手册

## 1. 模块概述

`db-mongo` 是 EasyFK 框架中面向 MongoDB 文档数据库的数据访问组件。该模块基于 Spring Data MongoDB，采用 Entity → DAO → Repository 分层架构，提供智能 ID 管理、自动审计、泛型 CRUD、灵活条件查询构建以及 DTO/实体自动转换能力，适用于内容管理、用户画像、日志存储、电商商品等文档型数据场景。

## 2. 依赖引入

### Maven

```xml
<dependency>
    <groupId>com.mcst</groupId>
    <artifactId>db-mongo</artifactId>
</dependency>
```

### Gradle

```gradle
dependencies {
    implementation 'com.mcst:db-mongo'
}
```

> 版本号由框架统一 BOM 管理，无需手动指定。

该模块会自动传递引入以下依赖：
- `spring-boot-starter-data-mongodb` — Spring Data MongoDB 数据访问支持
- `easyfk-core` — EasyFK 框架核心工具类和 DTO
- `easyfk-repository` — EasyFK 通用 Repository 接口定义
- `service-base` — EasyFK 服务基础模块

## 3. 配置说明

### 3.1 MongoDB 连接配置

在 `application.yml` 中配置 MongoDB 连接信息：

```yaml
spring:
  data:
    mongodb:
      uri: mongodb://localhost:27017/easyfk
```

或分别配置各项参数：

```yaml
spring:
  data:
    mongodb:
      host: localhost
      port: 27017
      database: easyfk
      username: your_username
      password: your_password
```

### 3.2 连接池配置

通过 URI 参数配置连接池：

```yaml
spring:
  data:
    mongodb:
      uri: mongodb://localhost:27017/easyfk?maxPoolSize=50&minPoolSize=10&maxIdleTimeMS=60000
```

### 3.3 自动配置

模块通过 `MongoAutoConfig` 自动完成以下配置：

| 配置项 | 说明 |
|--------|------|
| MongoDB 审计 | 自动启用 `@EnableMongoAuditing`，支持 `@CreatedDate` 和 `@LastModifiedDate` |
| 时间提供器 | 配置 `DateTimeProvider`，使用 `LocalDateTime.now()` 作为审计时间源 |
| 激活条件 | 当 classpath 中存在 `MongoTemplate` 时自动激活 |

## 4. 架构层次

模块采用三层架构，职责清晰：

```
┌────────────────────────────────────────────────┐
│                  Service 层                     │
│          注入 Repository，调用业务方法            │
└──────────────────────┬─────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────┐
│         Repository 层 (BaseMongoRepositoryImpl) │
│     DTO ↔ Entity 自动转换 · 实现 IBaseRepository │
└──────────────────────┬─────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────┐
│           DAO 层 (BaseSpringMongoDAO)           │
│         CRUD 操作 · MongoTemplate 封装          │
└──────────────────────┬─────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────┐
│          Entity 层 (BaseMongoEntity)            │
│       智能 ID · 自动审计 · 序列化支持             │
└────────────────────────────────────────────────┘
```

## 5. 实体层

### 5.1 BaseMongoEntity 基类

所有 MongoDB 实体类需继承 `BaseMongoEntity`，自动获得以下能力：

| 字段 | 类型 | 注解 | 说明 |
|------|------|------|------|
| `objectId` | `ObjectId` | `@Id` | MongoDB 主键（`_id`），持久化存储 |
| `id` | `String` | `@Transient` | 字符串形式 ID，不持久化，方便传输 |
| `createdAt` | `LocalDateTime` | `@CreatedDate` | 创建时间，插入时自动设置 |
| `updatedAt` | `LocalDateTime` | `@LastModifiedDate` | 更新时间，插入和更新时自动设置 |

**智能 ID 转换机制：**

- 调用 `setId(String)` 时，同时设置 `objectId` 和 `id`
- 调用 `getId()` 时，若 `id` 为空但 `objectId` 存在，自动从 `objectId` 转换
- 调用 `setObjectId(ObjectId)` 时，同时更新 `id`

### 5.2 定义实体类

```java
@Data
@EqualsAndHashCode(callSuper = true)
@Document(collection = "products")
public class Product extends BaseMongoEntity {

    @Indexed(unique = true)
    private String productCode;

    private String name;
    private String description;
    private BigDecimal price;
    private Integer stock;
    private String category;
    private String status;
}
```

> 无需声明 `id`、`objectId`、`createdAt`、`updatedAt` 字段，均从基类继承。建议使用 `@Document` 指定集合名，`@Indexed` 标记索引字段。

## 6. DAO 层

### 6.1 创建 DAO

继承 `BaseSpringMongoDAO<T>`，即可获得全部 CRUD 能力：

```java
@Repository
public class ProductDAO extends BaseSpringMongoDAO<Product> {

    // 可在此添加自定义查询方法
}
```

### 6.2 API 参考

#### 插入操作

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `insert(entity)` | 实体对象 | void | 插入单条记录 |
| `insertBatch(entities)` | 实体列表 | void | 批量插入（自动分批，每批 1000 条） |
| `insertAndReturnId(entity)` | 实体对象 | `String` | 插入并返回字符串形式 ID |
| `saveOrUpdate(entity)` | 实体对象 | void | 存在则更新，不存在则插入 |

#### 删除操作

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `deleteById(id)` | 主键 | `DeleteResult` | 按 ID 删除 |
| `deleteByCondition(condition)` | `SearchCondition` | `DeleteResult` | 按条件删除 |
| `deleteByQuery(query)` | `Query` | `DeleteResult` | 按 Query 对象删除 |
| `delete(entity)` | 实体对象 | `DeleteResult` | 按实体删除 |

#### 查询操作

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `findById(id, selectColumns...)` | 主键, 可选字段 | `T` | 按 ID 查询（支持字段选择） |
| `findOne(key, value)` | 字段名, 值 | `T` | 按单字段查询一条 |
| `findOne(valueMap)` | `Map<String, Object>` | `T` | 按多字段匹配查询一条 |
| `findOne(query)` | `Query` | `T` | 按 Query 对象查询一条 |
| `findOneByEntity(example)` | 示例实体 | `T` | 按示例实体查询一条（非空字段匹配） |
| `findByField(field, value)` | 字段名, 值 | `List<T>` | 按单字段查询列表 |
| `findByField(valueMap)` | `Map<String, Object>` | `List<T>` | 按多字段匹配查询列表 |
| `findByEntity(example)` | 示例实体 | `List<T>` | 按示例实体查询列表 |
| `findByCondition(condition)` | `SearchCondition` | `List<T>` | 按条件查询列表 |
| `findOneByCondition(condition)` | `SearchCondition` | `T` | 按条件查询单条 |
| `findByPage(condition)` | `SearchCondition` | `PageResult<T>` | 分页查询（含总数） |
| `findAll()` | — | `List<T>` | 查询全部记录 |

#### 更新操作

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `updateEntity(entity)` | 实体对象 | `UpdateResult` | **全量更新**：null 字段会被 unset |
| `updateEntitySelective(entity, nullProps...)` | 实体对象, 需清空字段名 | `UpdateResult` | **增量更新**：仅 set 非空字段，`nullProps` 显式清空 |
| `updateEntityByCondition(entity, condition)` | 实体对象, 查询条件 | `UpdateResult` | **条件批量更新**：批量写入非空字段 |
| `updateFirst(entity, condition)` | 实体对象, 查询条件 | `UpdateResult` | 条件更新第一条匹配记录 |
| `atomicIncrement(condition, field, value)` | 查询条件, 字段名, 增量值 | `T` | 原子递增字段值，返回更新后实体 |

> **更新语义说明：**
> - `updateEntity`：全量覆盖，未赋值字段会被 `unset`，适合完全同步实体的场景
> - `updateEntitySelective`：增量更新，只 `set` 非空字段；若需要清空字段，在 `nullProperties` 中显式声明
> - `updateEntityByCondition`：条件增量更新，批量写入非空字段，自动刷新 `updatedAt`
> - 所有更新操作会自动设置 `updatedAt` 为当前时间

#### 统计操作

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `count()` | — | `long` | 统计全部记录数 |
| `count(key, value)` | 字段名, 值 | `long` | 按字段统计 |
| `count(query)` | `Query` | `long` | 按 Query 统计 |
| `count(condition)` | `SearchCondition` | `long` | 按条件统计 |
| `countByEntity(entity)` | 示例实体 | `long` | 按示例实体统计 |
| `countByCondition(condition)` | `SearchCondition` | `long` | 按条件统计 |
| `exists(field, value)` | 字段名, 值 | `boolean` | 判断字段值是否存在 |
| `exists(condition)` | `SearchCondition` | `boolean` | 按条件判断是否存在 |
| `exists(query)` | `Query` | `boolean` | 按 Query 判断是否存在 |
| `exists(example)` | 示例实体 | `boolean` | 按示例实体判断是否存在 |

## 7. Repository 层

### 7.1 创建 Repository

`BaseMongoRepositoryImpl` 负责 DTO 与 Entity 之间的自动转换，面向 Service 层提供统一接口：

```java
@Repository
public class ProductRepository
        extends BaseMongoRepositoryImpl<ProductDAO, ProductDTO, Product, String> {

    // 可在此添加自定义业务查询方法
}
```

**泛型参数说明：**

| 泛型 | 含义 | 示例 |
|------|------|------|
| `D` | DAO 类型 | `ProductDAO` |
| `T` | DTO 类型（业务层使用） | `ProductDTO` |
| `P` | Entity 类型（数据层使用） | `Product` |
| `PK` | 主键类型 | `String` |

### 7.2 API 参考

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `queryById(id, selectColumns...)` | 主键, 可选字段 | `T` (DTO) | 按 ID 查询 |
| `queryByCondition(condition)` | `SearchCondition` | `List<T>` | 条件查询列表 |
| `queryOneByCondition(condition)` | `SearchCondition` | `T` | 条件查询单条 |
| `queryOneByField(field, value, selectFields...)` | 字段名, 值, 可选字段 | `T` | 按字段查询单条 |
| `queryByField(field, value, selectFields...)` | 字段名, 值, 可选字段 | `List<T>` | 按字段查询列表 |
| `queryByPage(condition)` | `SearchCondition` | `PageResult<T>` | 分页查询 |
| `insert(param)` | DTO 对象 | `BaseResult<?>` | 插入 |
| `insertAndReturnId(param)` | DTO 对象 | `PK` | 插入并返回 ID |
| `insertBatch(data)` | DTO 列表 | `BaseResult<?>` | 批量插入 |
| `deleteById(id)` | 主键 | `BaseResult<?>` | 按 ID 删除 |
| `deleteByCondition(condition)` | `SearchCondition` | `BaseResult<?>` | 条件删除 |
| `updateBySelective(param, nullProps...)` | DTO 对象, 需清空字段名 | `BaseResult<?>` | 增量更新 |
| `updateEntityByCondition(param, condition)` | DTO 对象, 查询条件 | `BaseResult<?>` | 条件批量更新 |
| `saveOrUpdateBySelective(param, nullProps...)` | DTO 对象, 需清空字段名 | `BaseResult<?>` | 有 ID 则更新，无 ID 则插入 |
| `exists(field, value)` | 字段名, 值 | `boolean` | 存在性检查 |
| `exists(condition)` | `SearchCondition` | `boolean` | 条件存在性检查 |
| `countByCondition(condition)` | `SearchCondition` | `long` | 条件统计 |

## 8. 查询条件构建

### 8.1 使用 SCBuilder

通过 `SCBuilder` 构建 `SearchCondition`，`MongoConditionBuilder` 会自动转换为 MongoDB `Query`：

```java
SearchCondition condition = SCBuilder.builder()
    .equalsConditions("category", "electronics")
    .likeConditions("name", ".*iPhone.*")
    .rangeConditions(new RangeCondition("price", 500.0, null, RangeConditionType.GreaterThan))
    .descFields("createdAt")
    .pageSearch(new PageSearch(1, 20))
    .build();
```

### 8.2 支持的查询条件类型

| 条件类型 | SCBuilder 方法 | 说明 |
|----------|----------------|------|
| 精确匹配 | `equalsConditions(key, value)` | 字段等于指定值 |
| 不等匹配 | `notEqualsConditions(key, value)` | 字段不等于指定值 |
| 模糊匹配 | `likeConditions(key, pattern)` | 正则表达式匹配 |
| IN 查询 | `inConditions(key, values)` | 字段值在列表中 |
| 范围查询 | `rangeConditions(RangeCondition...)` | 大于/大于等于/小于/小于等于/Between |
| 升序排序 | `ascFields(fields...)` | 升序排序字段 |
| 降序排序 | `descFields(fields...)` | 降序排序字段 |
| 分页 | `pageSearch(PageSearch)` | 分页参数 |
| 字段选择 | `selectFields(fields...)` | 只查询指定字段 |
| 限制数量 | `top(count)` | 限制返回记录数 |

### 8.3 RangeCondition 范围条件类型

| 类型 | 说明 | 构造方式 |
|------|------|----------|
| `GreaterThan` | 大于 (`>`) | `new RangeCondition("price", 100.0, null, RangeConditionType.GreaterThan)` |
| `GreaterThanOrEqual` | 大于等于 (`>=`) | `new RangeCondition("stock", 10, null, RangeConditionType.GreaterThanOrEqual)` |
| `LessThan` | 小于 (`<`) | `new RangeCondition("age", 18, null, RangeConditionType.LessThan)` |
| `LessThanOrEqual` | 小于等于 (`<=`) | `new RangeCondition("discount", 90, null, RangeConditionType.LessThanOrEqual)` |
| `Equal` | 等于 (`=`) | `new RangeCondition("level", 5, null, RangeConditionType.Equal)` |
| `Between` | 介于之间 (`>= AND <=`) | `new RangeCondition("price", 100.0, 1000.0, RangeConditionType.Between)` |

> `Between` 类型：只提供 `startValue` 等价于 `>=`，只提供 `endValue` 等价于 `<=`。

### 8.4 默认排序

如果实体类包含 `createdAt` 字段且未指定排序条件，查询会自动按 `createdAt` 降序排列。

## 9. 实战示例

### 9.1 DTO 定义

```java
@Data
public class ProductDTO implements Serializable {
    private String id;
    private String productCode;
    private String name;
    private String description;
    private BigDecimal price;
    private Integer stock;
    private String category;
    private String status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
```

### 9.2 单条插入与返回 ID

```java
ProductDTO dto = new ProductDTO();
dto.setProductCode("PROD-001");
dto.setName("iPhone 15");
dto.setPrice(new BigDecimal("7999.00"));
dto.setStock(100);

String id = productRepository.insertAndReturnId(dto);
```

### 9.3 批量插入

```java
List<ProductDTO> products = new ArrayList<>();
for (int i = 0; i < 5000; i++) {
    ProductDTO dto = new ProductDTO();
    dto.setName("Product " + i);
    dto.setPrice(BigDecimal.valueOf(100 + i));
    products.add(dto);
}
// 自动分批，每批 1000 条
productRepository.insertBatch(products);
```

### 9.4 条件查询

```java
SearchCondition condition = SCBuilder.builder()
    .equalsConditions("category", "electronics")
    .equalsConditions("status", "ACTIVE")
    .rangeConditions(new RangeCondition("price", 100.0, 1000.0, RangeConditionType.Between))
    .descFields("createdAt")
    .build();

List<ProductDTO> products = productRepository.queryByCondition(condition);
```

### 9.5 分页查询

```java
SearchCondition condition = SCBuilder.builder()
    .equalsConditions("category", "electronics")
    .descFields("createdAt")
    .pageSearch(new PageSearch(1, 20))
    .build();

PageResult<ProductDTO> page = productRepository.queryByPage(condition);
// page.getRows()  — 当前页数据
// page.getTotal() — 总记录数
```

### 9.6 模糊查询

```java
SearchCondition condition = SCBuilder.builder()
    .likeConditions("name", ".*iPhone.*")
    .build();

List<ProductDTO> products = productRepository.queryByCondition(condition);
```

### 9.7 字段选择查询

```java
// 方式一：Repository 层直接指定
ProductDTO product = productRepository.queryById(id, "name", "price", "stock");

// 方式二：通过 SearchCondition 指定
SearchCondition condition = SCBuilder.builder()
    .equalsConditions("category", "electronics")
    .selectFields("name", "price", "stock")
    .build();
List<ProductDTO> products = productRepository.queryByCondition(condition);
```

### 9.8 增量更新

```java
ProductDTO update = new ProductDTO();
update.setId(productId);
update.setPrice(new BigDecimal("6999.00"));
update.setStock(50);

// 仅更新 price 和 stock 字段
productRepository.updateBySelective(update);

// 更新 price 和 stock，同时清空 description 和 remark 字段
productRepository.updateBySelective(update, "description", "remark");
```

### 9.9 条件批量更新

```java
ProductDTO template = new ProductDTO();
template.setStatus("INACTIVE");

SearchCondition condition = SCBuilder.builder()
    .rangeConditions(new RangeCondition("stock", null, 0, RangeConditionType.LessThanOrEqual))
    .build();

productRepository.updateEntityByCondition(template, condition);
```

### 9.10 保存或更新

```java
ProductDTO dto = new ProductDTO();
dto.setId(existingId);       // 有 ID → 更新
dto.setName("Updated Name");
productRepository.saveOrUpdateBySelective(dto);

ProductDTO newDto = new ProductDTO();  // 无 ID → 插入
newDto.setName("New Product");
productRepository.saveOrUpdateBySelective(newDto);
```

### 9.11 原子递增

```java
SearchCondition condition = SCBuilder.builder()
    .equalsConditions("productCode", "PROD-001")
    .build();

// stock 字段原子减 1，返回更新后的实体
Product updated = productDAO.atomicIncrement(condition, "stock", -1);
```

### 9.12 基于示例的查询

```java
Product example = new Product();
example.setCategory("electronics");
example.setStatus("ACTIVE");

// 查询所有 category=electronics 且 status=ACTIVE 的记录
List<Product> products = productDAO.findByEntity(example);

// 检查是否存在
boolean exists = productDAO.exists(example);
```

### 9.13 条件删除

```java
// 按 ID 删除
productRepository.deleteById(productId);

// 按条件删除
SearchCondition condition = SCBuilder.builder()
    .equalsConditions("status", "DISCONTINUED")
    .build();
productRepository.deleteByCondition(condition);
```

### 9.14 Service 层完整示例

```java
@Service
public class ProductService {

    @Resource
    private ProductRepository productRepository;

    public BaseResult<?> createProduct(ProductDTO dto) {
        return productRepository.insert(dto);
    }

    public PageResult<ProductDTO> searchProducts(String keyword, String category,
                                                  BigDecimal minPrice, BigDecimal maxPrice,
                                                  int page, int size) {
        SCBuilder builder = SCBuilder.builder();
        if (EmptyUtil.isNotEmpty(keyword)) {
            builder.likeConditions("name", ".*" + keyword + ".*");
        }
        if (EmptyUtil.isNotEmpty(category)) {
            builder.equalsConditions("category", category);
        }
        if (minPrice != null || maxPrice != null) {
            builder.rangeConditions(
                new RangeCondition("price", minPrice, maxPrice, RangeConditionType.Between));
        }
        SearchCondition condition = builder
            .equalsConditions("status", "ACTIVE")
            .descFields("createdAt")
            .pageSearch(new PageSearch(page, size))
            .build();

        return productRepository.queryByPage(condition);
    }
}
```

## 10. 自动配置机制

| 配置类 | 说明 |
|--------|------|
| `MongoAutoConfig` | 自动启用 MongoDB 审计功能 |

- 通过 Spring Boot `AutoConfiguration.imports` 声明自动配置入口
- 当 classpath 中存在 `MongoTemplate` 时自动激活
- 自动启用 `@EnableMongoAuditing`，无需手动配置
- 配置 `DateTimeProvider`，审计时间使用 `LocalDateTime.now()`
- 可通过自定义 `mongoAuditingDateTimeProvider` Bean 覆盖默认时间提供器

## 11. 包结构

```
com.mcst.easyfk.db.mongo
├── config
│   └── MongoAutoConfig.java              # Spring Boot 自动配置类
├── dao
│   └── BaseSpringMongoDAO.java           # 通用 DAO 基类
├── entities
│   └── BaseMongoEntity.java              # 实体基类（ID 管理 + 审计字段）
├── repository
│   └── BaseMongoRepositoryImpl.java      # 通用 Repository 实现（DTO/Entity 转换）
└── util
    └── MongoConditionBuilder.java        # 查询条件构建器（SearchCondition → Query）
```

## 12. 最佳实践

1. **实体类设计**：继承 `BaseMongoEntity` 即可，无需声明 ID 和审计字段。使用 `@Document` 指定集合名，`@Indexed` 标记索引字段。
2. **分层使用**：Service 层注入 Repository（操作 DTO），仅在需要底层操作时直接注入 DAO。
3. **增量更新优先**：使用 `updateEntitySelective` / `updateBySelective` 而非 `updateEntity`，避免意外清空字段。
4. **字段选择查询**：不需要完整对象时，使用 `selectFields` 减少网络传输和内存占用。
5. **批量操作**：大量数据写入使用 `insertBatch()`（自动分批），批量修改使用 `updateEntityByCondition()`。
6. **分页查询**：大数据集避免 `findAll()`，使用 `findByPage()` / `queryByPage()` 分页查询。
7. **索引优化**：为常用查询字段添加 `@Indexed`，为复合查询使用 `@CompoundIndex`。
8. **模糊查询转义**：`likeConditions` 使用正则表达式，注意转义特殊字符（如 `.`、`*`、`(`）。
9. **事务支持**：MongoDB 4.0+ 副本集环境下，可使用 Spring `@Transactional` 实现多文档事务。
