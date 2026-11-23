# easyfk-component-orm API 签名速查（easyfk 3.2.12）

> 坐标：`com.mcst:orm-mybatis、orm-flex、orm-hibernate、orm-sharding`　源码：`easyfk-component/component-orm/orm-mybatis`、`easyfk-component/component-orm/orm-flex`、`easyfk-component/component-orm/orm-hibernate`、`easyfk-component/component-orm/orm-sharding`
> 由 `scripts/gen-api.py` 从 45 个源文件自动提取，共 45 个类型、170 个方法/构造器、23 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-component-orm-skill.md](../modules/easyfk-component-orm-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `orm-mybatis` | `com.mcst.easyfk.service.mybatisplus.config.MybatisPlusMapperScanConfigure` |
| `orm-mybatis` | `com.mcst.easyfk.service.mybatisplus.config.MybatisPlusConfigure` |
| `orm-flex` | `com.mcst.easyfk.service.flex.config.FlexMapperScanConfigure` |
| `orm-flex` | `com.mcst.easyfk.service.flex.config.FlexConfigure` |
| `orm-hibernate` | `com.mcst.easyfk.service.hibernate.config.HibernateScanConfigure` |
| `orm-hibernate` | `com.mcst.easyfk.service.hibernate.config.HibernateConfigure` |

## 类型索引

- `com.mcst.easyfk.service.flex`：[ApplicationStarter](#applicationstarter)、[FlexServiceScanner](#flexservicescanner)
- `com.mcst.easyfk.service.flex.config`：[FlexConfigure](#flexconfigure)、[FlexMapperScanConfigure](#flexmapperscanconfigure)
- `com.mcst.easyfk.service.flex.handler`：[AutoSetValueHandler](#autosetvaluehandler)
- `com.mcst.easyfk.service.flex.impl`：[BaseFlexRepositoryImpl](#baseflexrepositoryimpl)
- `com.mcst.easyfk.service.flex.persistence`：[BaseFlexEntity](#baseflexentity)、[BaseFlexSimpleEntity](#baseflexsimpleentity)
- `com.mcst.easyfk.service.flex.util`：[EqualConditionUtil](#equalconditionutil)、[FlexUtil](#flexutil)、[FlexWrapperUtil](#flexwrapperutil)、[InConditionUtil](#inconditionutil)、[LikeConditionUtil](#likeconditionutil)
    [NullConditionUtil](#nullconditionutil)、[RangeConditionUtil](#rangeconditionutil)
- `com.mcst.easyfk.service.hibernate`：[ApplicationStarter](#applicationstarter)、[HibernateServiceScanner](#hibernateservicescanner)
- `com.mcst.easyfk.service.hibernate.config`：[HibernateConfigure](#hibernateconfigure)、[HibernateScanConfigure](#hibernatescanconfigure)
- `com.mcst.easyfk.service.hibernate.handler`：[AutoSetValueHandler](#autosetvaluehandler)
- `com.mcst.easyfk.service.hibernate.impl`：[BaseHibernateRepositoryImpl](#basehibernaterepositoryimpl)
- `com.mcst.easyfk.service.hibernate.persistence`：[BaseHibernateEntity](#basehibernateentity)、[BaseHibernateSimpleEntity](#basehibernatesimpleentity)
- `com.mcst.easyfk.service.hibernate.util`：[EqualConditionUtil](#equalconditionutil)、[HibernateUtil](#hibernateutil)、[HibernateWrapperUtil](#hibernatewrapperutil)、[InConditionUtil](#inconditionutil)、[LikeConditionUtil](#likeconditionutil)
    [NullConditionUtil](#nullconditionutil)、[RangeConditionUtil](#rangeconditionutil)
- `com.mcst.easyfk.service.mybatisplus`：[ApplicationStarter](#applicationstarter)、[MybatisPlusServiceScanner](#mybatisplusservicescanner)
- `com.mcst.easyfk.service.mybatisplus.config`：[MybatisPlusConfigure](#mybatisplusconfigure)、[MybatisPlusMapperScanConfigure](#mybatisplusmapperscanconfigure)
- `com.mcst.easyfk.service.mybatisplus.handler`：[AutoSetValueHandler](#autosetvaluehandler)
- `com.mcst.easyfk.service.mybatisplus.impl`：[BaseMyBatisRepositoryImpl](#basemybatisrepositoryimpl)
- `com.mcst.easyfk.service.mybatisplus.persistence`：[BaseMyBatisPlusEntity](#basemybatisplusentity)、[BaseMyBatisPlusSimpleEntity](#basemybatisplussimpleentity)
- `com.mcst.easyfk.service.mybatisplus.util`：[EqualConditionUtil](#equalconditionutil)、[InConditionUtil](#inconditionutil)、[LikeConditionUtil](#likeconditionutil)、[MyBatisPlusWrapperUtil](#mybatispluswrapperutil)、[MybatisPlusUtil](#mybatisplusutil)
    [NullConditionUtil](#nullconditionutil)、[RangeConditionUtil](#rangeconditionutil)

## 包 `com.mcst.easyfk.service.flex`

### ApplicationStarter

`public class ApplicationStarter`　MyBatis-Flex 自动配置启动类

**方法**

```java
static void run(Class<?> clazz, String[] args)
static void run(Class<?>[] primarySources, String[] args)
```

### FlexServiceScanner

`public class FlexServiceScanner`　兼容保留的扫描入口类

_无 public 成员。_

## 包 `com.mcst.easyfk.service.flex.config`

### FlexConfigure

`public class FlexConfigure`　注解：`@AutoConfiguration`　MyBatis-Flex 配置类

**方法**

```java
@Bean @ConditionalOnMissingBean AutoSetValueHandler autoSetValueHandler()
@Bean MyBatisFlexCustomizer mybatisFlexCustomizer(AutoSetValueHandler autoSetValueHandler, @Value("${easyfk.orm.flex.sql-audit:false}") boolean sqlAudit)  // 配置 MyBatis-Flex 全局配置
```

### FlexMapperScanConfigure

`public class FlexMapperScanConfigure`　注解：`@AutoConfiguration(before = MybatisFlexAutoConfiguration.class)` `@ConditionalOnMissingBean({MapperFactoryBean.class, MapperScannerConfigurer.class})` `@Import(FlexMapperScanConfigure.Registrar.class)`　Mapper 自动扫描配置

_无 public 成员。_

## 包 `com.mcst.easyfk.service.flex.handler`

### AutoSetValueHandler

`public class AutoSetValueHandler implements InsertListener, UpdateListener`　MyBatis-Flex 自动填充处理器

**方法**

```java
void onInsert(Object entity)
void onUpdate(Object entity)
```

## 包 `com.mcst.easyfk.service.flex.impl`

### BaseFlexRepositoryImpl

`public class BaseFlexRepositoryImpl<M extends BaseMapper<P>, T extends Serializable, P extends Model<?>, PK extends Serializable> implements IBaseRepository<T, PK>`　注解：`@SuppressWarnings("unchecked")`　MyBatis-Flex Repository 基础实现类

**字段 / 常量**

```java
Class<T> dtoClazz
Class<P> entityClazz
@Autowired M baseMapper
```

**构造器**

```java
BaseFlexRepositoryImpl()
```

**方法**

```java
Class<P> getEntityClass()
T queryById(PK id, String... selectColumns)
List<T> queryByCondition(SearchCondition condition)
T queryOneByCondition(SearchCondition condition)
T queryOneByField(String field, Object value, String... selectFields)
List<T> queryByField(String field, Object value, String... selectFields)
boolean exists(String field, Object value)
long countByCondition(SearchCondition condition)
PageResult<T> queryByPage(SearchCondition condition)
boolean exists(SearchCondition condition)
BaseResult<?> insert(T param)
BaseResult<?> insertBatch(List<T> data)
PK insertAndReturnId(T param)
BaseResult<?> deleteById(PK id)
BaseResult<?> deleteByCondition(SearchCondition condition)
BaseResult<?> updateEntityByCondition(T param, SearchCondition condition)
BaseResult<?> updateBySelective(T param, String... nullProperties)
BaseResult<?> saveOrUpdateBySelective(T param, String... nullProperties)
```

## 包 `com.mcst.easyfk.service.flex.persistence`

### BaseFlexEntity

`public class BaseFlexEntity<T extends Model<T>> extends Model<T>`　Lombok：`@EqualsAndHashCode(callSuper = true)` `@Data` `@Accessors(chain = true)`　MyBatis-Flex 实体基类（完整版）

**字段 / 常量**

```java
@Column(value = "insert_time", onInsertValue = "now()") LocalDateTime insertTime
@Column(value = "last_update_time", onInsertValue = "now()", onUpdateValue = "now()") LocalDateTime lastUpdateTime
@Column(value = "deleted", isLogicDelete = true) @JSONField(serialize = false) Integer deleted
```

### BaseFlexSimpleEntity

`public class BaseFlexSimpleEntity<T extends Model<T>> extends Model<T>`　Lombok：`@EqualsAndHashCode(callSuper = true)` `@Data` `@Accessors(chain = true)`　MyBatis-Flex 实体基类（简化版）

**字段 / 常量**

```java
@Column(value = "insert_time", onInsertValue = "now()") LocalDateTime insertTime
@Column(value = "last_update_time", onInsertValue = "now()", onUpdateValue = "now()") LocalDateTime lastUpdateTime
```

## 包 `com.mcst.easyfk.service.flex.util`

### EqualConditionUtil

`public class EqualConditionUtil`　等值条件工具类

**方法**

```java
static void build(QueryWrapper wrapper, String fieldName, Object value, boolean needConvert)  // 构建等值查询条件
static void buildBatch(QueryWrapper wrapper, Map<String, Object> conditions, boolean needConvert)  // 批量构建等值条件
```

### FlexUtil

`public class FlexUtil`　注解：`@SuppressWarnings("unchecked")`　MyBatis-Flex 通用工具类

**方法**

```java
static <T> T queryById(Object id, Class<T> entityClazz, BaseMapper<T> baseMapper, String... selectColumns)
static <T> T queryById(Object id, Class<T> entityClazz, BaseMapper<T> baseMapper, boolean change, String... selectColumns)
static <T> BaseResult<?> deleteById(Object id, BaseMapper<T> baseMapper, Class<T> entityClazz)
static <T> BaseResult<?> saveOrUpdateEntityMethod(BaseMapper<T> baseMapper, T entity, String... nullProperties)
static <E, T> E saveAndReturnId(BaseMapper<T> baseMapper, T entity)
static <T> boolean isUpdate(Object entity, BaseMapper<T> baseMapper)
static <T> PageResult<T> queryByPage(BaseMapper<T> baseMapper, SearchCondition condition, Class<T> entityClazz)
static <T> BaseResult<?> updateBySelective(T entity, String[] nullProperties, BaseMapper<T> baseMapper)
```

### FlexWrapperUtil

`public class FlexWrapperUtil`　MyBatis-Flex 查询条件构建工具类

**方法**

```java
static void queryWrapperSelectColumns(QueryWrapper queryWrapper, String[] selectColumns, boolean change)
static QueryWrapper createFindByFieldWrapper(String field, Object value)
static QueryWrapper getWrapperBySearchCondition(SearchCondition condition, Class<?> clazz)
static QueryWrapper getBaseWrapperBySearchCondition(SearchCondition condition, Class<?> clazz)
static QueryWrapper getBaseWrapperToUpdate(SearchCondition condition)
static boolean hasEffectiveCondition(SearchCondition condition)  // 判断查询条件中是否存在至少一个会生效的 WHERE 条件（用于拒绝无条件的删除/更新）
```

### InConditionUtil

`public class InConditionUtil`　IN条件工具类

**方法**

```java
static void build(QueryWrapper wrapper, String fieldName, Object value, boolean needConvert)  // 构建IN查询条件
static void buildNotIn(QueryWrapper wrapper, String fieldName, List<?> values, boolean needConvert)  // 构建NOT IN条件
static void buildBatch(QueryWrapper wrapper, Map<String, List<?>> conditions, boolean needConvert)  // 批量构建IN条件
static void buildNotInBatch(QueryWrapper wrapper, Map<String, List<?>> conditions, boolean needConvert)  // 批量构建NOT IN条件
```

### LikeConditionUtil

`public class LikeConditionUtil`　模糊查询条件工具类

**方法**

```java
static void build(QueryWrapper wrapper, String fieldName, Object value, boolean needConvert)  // 构建模糊查询条件
static void buildWithType(QueryWrapper wrapper, String fieldName, Object value, boolean needConvert, LikeType likeType)  // 根据指定类型构建模糊查询条件
static void buildBatch(QueryWrapper wrapper, Map<String, String> conditions, boolean needConvert, LikeType likeType)  // 批量构建模糊查询条件
```

#### LikeConditionUtil.LikeType

`public enum LikeType`

**枚举常量**

```java
LIKE
LIKE_LEFT
LIKE_RIGHT
```

### NullConditionUtil

`public class NullConditionUtil`　NULL条件工具类

**方法**

```java
static void build(QueryWrapper wrapper, String fieldName, Object value, boolean needConvert)  // 构建NULL查询条件
static void buildIsNull(QueryWrapper wrapper, String fieldName, boolean needConvert)  // 构建IS NULL条件
static void buildIsNotNull(QueryWrapper wrapper, String fieldName, boolean needConvert)  // 构建IS NOT NULL条件
static void buildIsNullBatch(QueryWrapper wrapper, List<String> fieldNames, boolean needConvert)  // 批量构建IS NULL条件
static void buildIsNotNullBatch(QueryWrapper wrapper, List<String> fieldNames, boolean needConvert)  // 批量构建IS NOT NULL条件
```

### RangeConditionUtil

`public class RangeConditionUtil`　区间条件工具类

**方法**

```java
static void build(QueryWrapper wrapper, String fieldName, Object value, boolean needConvert)  // 构建区间查询条件
static void buildRange(QueryWrapper wrapper, RangeCondition rangeCondition, boolean needConvert)  // 构建区间条件
static void buildBatch(QueryWrapper wrapper, List<RangeCondition> rangeConditions, boolean needConvert)  // 批量构建区间条件
```

## 包 `com.mcst.easyfk.service.hibernate`

### ApplicationStarter

`public class ApplicationStarter`　Hibernate 自动配置启动类

**方法**

```java
static void run(Class<?> clazz, String[] args)
static void run(Class<?>[] primarySources, String[] args)
```

### HibernateServiceScanner

`public class HibernateServiceScanner`　兼容保留的扫描入口类

_无 public 成员。_

## 包 `com.mcst.easyfk.service.hibernate.config`

### HibernateConfigure

`public class HibernateConfigure`　注解：`@AutoConfiguration`　Hibernate 配置类

**方法**

```java
@Bean @ConditionalOnMissingBean AutoSetValueHandler autoSetValueHandler()
```

### HibernateScanConfigure

`public class HibernateScanConfigure`　注解：`@AutoConfiguration(after = HibernateJpaAutoConfiguration.class, before = JpaRepositoriesAutoConfiguration.class)` `@Import(HibernateScanConfigure.EntityScanRegistrar.class)`　实体与 JPA Repository 自动扫描配置

_无 public 成员。_

## 包 `com.mcst.easyfk.service.hibernate.handler`

### AutoSetValueHandler

`public class AutoSetValueHandler`　Hibernate 自动填充处理器（JPA EntityListener）

**方法**

```java
@PrePersist void onPrePersist(Object entity)
@PreUpdate void onPreUpdate(Object entity)
```

## 包 `com.mcst.easyfk.service.hibernate.impl`

### BaseHibernateRepositoryImpl

`public class BaseHibernateRepositoryImpl<R extends JpaRepository<P, PK> & JpaSpecificationExecutor<P>, T extends Serializable, P, PK extends Serializable> implements IBaseRepository<T, PK>`　注解：`@SuppressWarnings("unchecked")` `@Transactional(rollbackFor = Exception.class)`　Hibernate Repository 基础实现类

**字段 / 常量**

```java
Class<T> dtoClazz
Class<P> entityClazz
@Autowired R jpaRepository
@PersistenceContext EntityManager entityManager
```

**构造器**

```java
BaseHibernateRepositoryImpl()
```

**方法**

```java
Class<P> getEntityClass()
@Transactional(readOnly = true) T queryById(PK id, String... selectColumns)
@Transactional(readOnly = true) List<T> queryByCondition(SearchCondition condition)
@Transactional(readOnly = true) T queryOneByCondition(SearchCondition condition)
@Transactional(readOnly = true) T queryOneByField(String field, Object value, String... selectFields)
@Transactional(readOnly = true) List<T> queryByField(String field, Object value, String... selectFields)
@Transactional(readOnly = true) boolean exists(String field, Object value)
@Transactional(readOnly = true) long countByCondition(SearchCondition condition)
@Transactional(readOnly = true) PageResult<T> queryByPage(SearchCondition condition)
@Transactional(readOnly = true) boolean exists(SearchCondition condition)
BaseResult<?> insert(T param)
BaseResult<?> insertBatch(List<T> data)
PK insertAndReturnId(T param)
BaseResult<?> deleteById(PK id)
BaseResult<?> deleteByCondition(SearchCondition condition)
BaseResult<?> updateEntityByCondition(T param, SearchCondition condition)
BaseResult<?> updateBySelective(T param, String... nullProperties)
BaseResult<?> saveOrUpdateBySelective(T param, String... nullProperties)
```

## 包 `com.mcst.easyfk.service.hibernate.persistence`

### BaseHibernateEntity

`public abstract class BaseHibernateEntity implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)`　注解：`@MappedSuperclass` `@EntityListeners(com.mcst.easyfk.service.hibernate.handler.AutoSetValueHandler.class)`　Hibernate 实体基类（完整版）

**字段 / 常量**

```java
@Column(name = "insert_time") LocalDateTime insertTime
@Column(name = "last_update_time") LocalDateTime lastUpdateTime
@Column(name = "deleted") @JSONField(serialize = false) Integer deleted
```

### BaseHibernateSimpleEntity

`public abstract class BaseHibernateSimpleEntity implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)`　注解：`@MappedSuperclass` `@EntityListeners(com.mcst.easyfk.service.hibernate.handler.AutoSetValueHandler.class)`　Hibernate 实体基类（简化版）

**字段 / 常量**

```java
@Column(name = "insert_time") LocalDateTime insertTime
@Column(name = "last_update_time") LocalDateTime lastUpdateTime
```

## 包 `com.mcst.easyfk.service.hibernate.util`

### EqualConditionUtil

`public class EqualConditionUtil`　等值条件工具类

**方法**

```java
static Predicate build(CriteriaBuilder cb, Root<?> root, String fieldName, Object value)  // 构建等值查询条件
static List<Predicate> buildBatch(CriteriaBuilder cb, Root<?> root, Map<String, Object> conditions)  // 批量构建等值条件
```

### HibernateUtil

`public class HibernateUtil`　注解：`@SuppressWarnings("unchecked")`　Hibernate 通用工具类

**方法**

```java
static <T> T queryById(Object id, Class<T> entityClazz, EntityManager em)
static <T, PK extends Serializable> BaseResult<?> deleteById(Object id, EntityManager em, Class<T> entityClazz)
static <T> BaseResult<?> deleteByCondition(EntityManager em, SearchCondition condition, Class<T> entityClazz)
static <T> BaseResult<?> saveOrUpdateEntityMethod(EntityManager em, T entity, Class<T> entityClazz, String... nullProperties)
static <E, T> E saveAndReturnId(EntityManager em, T entity)
static <T> boolean isUpdate(Object entity, EntityManager em, Class<T> entityClazz)
static <T> PageResult<T> queryByPage(EntityManager em, JpaSpecificationExecutor<T> executor, SearchCondition condition, Class<T> entityClazz)  // 分页查询：totalCount=false 时不执行 count；selectFields 非空时只查询指定属性
static <T> List<T> queryList(EntityManager em, Class<T> entityClazz, Specification<T> spec, Sort sort, String[] selectFields, Pageable pageable)  // 按 Specification 查询实体列表
static <T> BaseResult<?> updateBySelective(T entity, String[] nullProperties, EntityManager em, Class<T> entityClazz)
static <T> int updateEntityByCondition(T entity, SearchCondition condition, EntityManager em, Class<T> entityClazz)
static String getIdFieldName(Class<?> entityClazz)  // 获取实体的主键字段名
```

### HibernateWrapperUtil

`public class HibernateWrapperUtil`　Hibernate 查询条件构建工具类

**方法**

```java
static List<Predicate> buildPredicates(SearchCondition condition, Root<?> root, CriteriaBuilder cb)  // 核心方法：根据 SearchCondition 构建 Predicate 列表（不含逻辑删除过滤）
static <T> Specification<T> getSpecificationBySearchCondition(SearchCondition condition, Class<T> entityClazz)  // 构建用于 SELECT 查询的 Specification（自动包含逻辑删除过滤和分组）
static <T> Specification<T> getBaseSpecificationToUpdate(SearchCondition condition)  // 构建用于 UPDATE/DELETE 的 Specification（不含排序/分组/字段选择）
static <T> Specification<T> getCountSpecification(SearchCondition condition, Class<T> entityClazz)  // 构建用于 count/exists 的 Specification（包含逻辑删除过滤，不含分组）
static Sort getSort(SearchCondition condition, Class<?> entityClazz)  // 根据 SearchCondition 构建排序
static Pageable getPageable(SearchCondition condition, Class<?> entityClazz)  // 根据 SearchCondition 构建 Pageable
static void addNotDeletedPredicate(List<Predicate> predicates, Root<?> root, CriteriaBuilder cb, Class<?> entityClazz)  // 实体存在 deleted 字段时追加 deleted = 0 过滤
```

### InConditionUtil

`public class InConditionUtil`　IN条件工具类

**方法**

```java
static Predicate build(Root<?> root, String fieldName, List<?> values)  // 构建IN查询条件
static Predicate buildNotIn(CriteriaBuilder cb, Root<?> root, String fieldName, List<?> values)  // 构建NOT IN条件
static List<Predicate> buildBatch(Root<?> root, Map<String, List<?>> conditions)  // 批量构建IN条件
static List<Predicate> buildNotInBatch(CriteriaBuilder cb, Root<?> root, Map<String, List<?>> conditions)  // 批量构建NOT IN条件
```

### LikeConditionUtil

`public class LikeConditionUtil`　模糊查询条件工具类

**方法**

```java
static Predicate build(CriteriaBuilder cb, Root<?> root, String fieldName, Object value)  // 构建模糊查询条件
static Predicate buildWithType(CriteriaBuilder cb, Root<?> root, String fieldName, Object value, LikeType likeType)  // 根据指定类型构建模糊查询条件
static List<Predicate> buildBatch(CriteriaBuilder cb, Root<?> root, Map<String, String> conditions, LikeType likeType)  // 批量构建模糊查询条件
```

#### LikeConditionUtil.LikeType

`public enum LikeType`

**枚举常量**

```java
LIKE
LIKE_LEFT
LIKE_RIGHT
```

### NullConditionUtil

`public class NullConditionUtil`　NULL条件工具类

**方法**

```java
static Predicate buildIsNull(CriteriaBuilder cb, Root<?> root, String fieldName)  // 构建IS NULL条件
static Predicate buildIsNotNull(CriteriaBuilder cb, Root<?> root, String fieldName)  // 构建IS NOT NULL条件
static List<Predicate> buildIsNullBatch(CriteriaBuilder cb, Root<?> root, List<String> fieldNames)  // 批量构建IS NULL条件
static List<Predicate> buildIsNotNullBatch(CriteriaBuilder cb, Root<?> root, List<String> fieldNames)  // 批量构建IS NOT NULL条件
```

### RangeConditionUtil

`public class RangeConditionUtil`　区间条件工具类

**方法**

```java
@SuppressWarnings({"unchecked", "rawtypes"}) static Predicate buildRange(CriteriaBuilder cb, Root<?> root, RangeCondition rangeCondition)  // 构建区间条件
static List<Predicate> buildBatch(CriteriaBuilder cb, Root<?> root, List<RangeCondition> rangeConditions)  // 批量构建区间条件
```

## 包 `com.mcst.easyfk.service.mybatisplus`

### ApplicationStarter

`public class ApplicationStarter`

**方法**

```java
static void run(Class<?> clazz, String[] args)
static void run(Class<?>[] primarySources, String[] args)
```

### MybatisPlusServiceScanner

`public class MybatisPlusServiceScanner`　兼容保留的扫描入口类

_无 public 成员。_

## 包 `com.mcst.easyfk.service.mybatisplus.config`

### MybatisPlusConfigure

`public class MybatisPlusConfigure`　注解：`@AutoConfiguration`

**方法**

```java
@Bean @ConditionalOnMissingBean AutoSetValueHandler autoSetValueHandler()
@Bean @ConditionalOnMissingBean MybatisPlusInterceptor mybatisPlusInterceptor()
```

### MybatisPlusMapperScanConfigure

`public class MybatisPlusMapperScanConfigure`　注解：`@AutoConfiguration(before = MybatisPlusAutoConfiguration.class)` `@ConditionalOnMissingBean({MapperFactoryBean.class, MapperScannerConfigurer.class})` `@Import(MybatisPlusMapperScanConfigure.Registrar.class)`　Mapper 自动扫描配置

_无 public 成员。_

## 包 `com.mcst.easyfk.service.mybatisplus.handler`

### AutoSetValueHandler

`public class AutoSetValueHandler implements MetaObjectHandler`

**方法**

```java
void insertFill(MetaObject metaObject)
void updateFill(MetaObject metaObject)
```

## 包 `com.mcst.easyfk.service.mybatisplus.impl`

### BaseMyBatisRepositoryImpl

`public class BaseMyBatisRepositoryImpl<M extends BaseMapper<P>, T extends Serializable, P extends Model<?>, PK extends Serializable> extends ServiceImpl<M, P> implements IBaseRepository<T, PK>`　注解：`@SuppressWarnings("unchecked")`

**字段 / 常量**

```java
Class<T> dtoClazz
```

**构造器**

```java
BaseMyBatisRepositoryImpl()
```

**方法**

```java
T queryById(PK id, String... selectColumns)
List<T> queryByCondition(SearchCondition condition)
T queryOneByCondition(SearchCondition condition)
T queryOneByField(String field, Object value, String... selectFields)
List<T> queryByField(String field, Object value, String... selectFields)
boolean exists(String field, Object value)
long countByCondition(SearchCondition condition)
PageResult<T> queryByPage(SearchCondition condition)
boolean exists(SearchCondition condition)
BaseResult<?> insert(T param)
BaseResult<?> insertBatch(List<T> data)
PK insertAndReturnId(T param)
BaseResult<?> deleteById(PK id)
BaseResult<?> deleteByCondition(SearchCondition condition)
BaseResult<?> updateEntityByCondition(T param, SearchCondition condition)
BaseResult<?> updateBySelective(T param, String... nullProperties)
BaseResult<?> saveOrUpdateBySelective(T param, String... nullProperties)
```

## 包 `com.mcst.easyfk.service.mybatisplus.persistence`

### BaseMyBatisPlusEntity

`public class BaseMyBatisPlusEntity<T extends Model<?>> extends Model<T>`　Lombok：`@Data` `@EqualsAndHashCode(callSuper = true)` `@Accessors(chain = true)`

**字段 / 常量**

```java
@TableField(fill = FieldFill.INSERT) LocalDateTime insertTime
@AutoUpdateTime @TableField(fill = FieldFill.INSERT_UPDATE) LocalDateTime lastUpdateTime
@TableLogic @JSONField(serialize = false) @TableField(fill = FieldFill.INSERT, select = false) Integer deleted
```

### BaseMyBatisPlusSimpleEntity

`public class BaseMyBatisPlusSimpleEntity<T extends Model<?>> extends Model<T>`　Lombok：`@Data` `@EqualsAndHashCode(callSuper = true)` `@Accessors(chain = true)`

**字段 / 常量**

```java
@TableField(fill = FieldFill.INSERT) LocalDateTime insertTime
@AutoUpdateTime @TableField(fill = FieldFill.INSERT_UPDATE) LocalDateTime lastUpdateTime
```

## 包 `com.mcst.easyfk.service.mybatisplus.util`

### EqualConditionUtil

`public class EqualConditionUtil`　等值条件工具类

**方法**

```java
static <T> void build(QueryWrapper<T> wrapper, String fieldName, Object value, boolean needConvert)  // 构建等值查询条件
static <T> void buildBatch(QueryWrapper<T> wrapper, Map<String, Object> conditions, boolean needConvert)  // 批量构建等值条件
```

### InConditionUtil

`public class InConditionUtil`　IN条件工具类

**方法**

```java
static <T> void build(QueryWrapper<T> wrapper, String fieldName, Object value, boolean needConvert)  // 构建IN查询条件
static <T> void buildNotIn(QueryWrapper<T> wrapper, String fieldName, List<?> values, boolean needConvert)  // 构建NOT IN条件
static <T> void buildBatch(QueryWrapper<T> wrapper, Map<String, List<?>> conditions, boolean needConvert)  // 批量构建IN条件
static <T> void buildNotInBatch(QueryWrapper<T> wrapper, Map<String, List<?>> conditions, boolean needConvert)  // 批量构建NOT IN条件
```

### LikeConditionUtil

`public class LikeConditionUtil`　模糊查询条件工具类

**方法**

```java
static <T> void build(QueryWrapper<T> wrapper, String fieldName, Object value, boolean needConvert)  // 构建模糊查询条件
static <T> void buildWithType(QueryWrapper<T> wrapper, String fieldName, Object value, boolean needConvert, LikeType likeType)  // 根据指定类型构建模糊查询条件
static <T> void buildBatch(QueryWrapper<T> wrapper, Map<String, String> conditions, boolean needConvert, LikeType likeType)  // 批量构建模糊查询条件
```

#### LikeConditionUtil.LikeType

`public enum LikeType`

**枚举常量**

```java
LIKE
LIKE_LEFT
LIKE_RIGHT
```

### MyBatisPlusWrapperUtil

`public class MyBatisPlusWrapperUtil`　MyBatis Plus 查询条件构建工具类

**方法**

```java
static <T> void queryWrapperSelectColumns(QueryWrapper<T> queryWrapper, String[] selectColumns, boolean change)
static <T> QueryWrapper<T> createFindByFieldWrapper(String field, Object value)
static <T> QueryWrapper<T> getWrapperBySearchCondition(SearchCondition condition, Class<T> clazz)
static <T> QueryWrapper<T> getBaseWrapperBySearchCondition(SearchCondition condition, Class<T> clazz)
static <T> QueryWrapper<T> getBaseWrapperToUpdate(SearchCondition condition)
```

### MybatisPlusUtil

`public class MybatisPlusUtil`　注解：`@SuppressWarnings("unchecked")`

**方法**

```java
static <T> T queryById(Object id, Class<T> entityClazz, BaseMapper<T> baseMapper, String... selectColumns)
static <T> T queryById(Object id, Class<T> entityClazz, BaseMapper<T> baseMapper, boolean change, String... selectColumns)
static <T> BaseResult<?> deleteById(Object id, BaseMapper<T> baseMapper, Class<T> entityClazz)
static <T> BaseResult<?> saveOrUpdateEntityMethod(BaseMapper<T> baseMapper, T entity, String... nullProperties)
static <E, T> E saveAndReturnId(BaseMapper<T> baseMapper, T entity)
static <T> boolean isUpdate(Object entity, BaseMapper<T> baseMapper)
static <T> PageResult<T> queryByPage(BaseMapper<T> baseMapper, SearchCondition condition, Class<T> entityClazz)
static <T> BaseResult<?> updateBySelective(T entity, String[] nullProperties, BaseMapper<T> baseMapper)
static String resolveKeyColumn(Class<?> entityClazz)  // 主键列名：优先取 MyBatis-Plus TableInfo，其次 @TableId(value)，最后字段名转下划线
static String resolveKeyProperty(Class<?> entityClazz)  // 主键属性名
static String resolveColumn(Class<?> entityClazz, String property)  // 属性名转列名；属性不存在于实体时抛出异常，避免拼入任意列名
```

### NullConditionUtil

`public class NullConditionUtil`　NULL条件工具类

**方法**

```java
static <T> void build(QueryWrapper<T> wrapper, String fieldName, Object value, boolean needConvert)  // 构建NULL查询条件
static <T> void buildIsNull(QueryWrapper<T> wrapper, String fieldName, boolean needConvert)  // 构建IS NULL条件
static <T> void buildIsNotNull(QueryWrapper<T> wrapper, String fieldName, boolean needConvert)  // 构建IS NOT NULL条件
static <T> void buildIsNullBatch(QueryWrapper<T> wrapper, List<String> fieldNames, boolean needConvert)  // 批量构建IS NULL条件
static <T> void buildIsNotNullBatch(QueryWrapper<T> wrapper, List<String> fieldNames, boolean needConvert)  // 批量构建IS NOT NULL条件
```

### RangeConditionUtil

`public class RangeConditionUtil`　区间条件工具类

**方法**

```java
static <T> void build(QueryWrapper<T> wrapper, String fieldName, Object value, boolean needConvert)  // 构建区间查询条件
static <T> void buildRange(QueryWrapper<T> wrapper, RangeCondition rangeCondition, boolean needConvert)  // 构建区间条件
static <T> void buildBatch(QueryWrapper<T> wrapper, List<RangeCondition> rangeConditions, boolean needConvert)  // 批量构建区间条件
```
