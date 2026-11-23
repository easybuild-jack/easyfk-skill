# easyfk-component-db API 签名速查（easyfk 3.2.12）

> 坐标：`com.mcst:db-redis、db-mongo、db-clickhouse`　源码：`easyfk-component/component-db/db-redis`、`easyfk-component/component-db/db-mongo`、`easyfk-component/component-db/db-clickhouse`
> 由 `scripts/gen-api.py` 从 47 个源文件自动提取，共 47 个类型、382 个方法/构造器、84 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-component-db-skill.md](../modules/easyfk-component-db-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 配置项（@ConfigurationProperties）

### `easyfk.config.db.redis.biz-db` ← BizDbProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `db-map` | `Map<String, BizDb>` | `new HashMap<>()` | 业务数据库配置 |

### `easyfk.config.db.redis.pubsub` ← PushSubProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `open` | `Boolean` | `Boolean.FALSE` |  |
| `channel` | `String` | `RedisConstants.DEFAULT_DATASOURCE` | 订阅的频道 |
| `datasource` | `String` | `RedisConstants.DEFAULT_DATASOURCE` | 数据源 |
| `database-name` | `String` | `RedisConstants.DEFAULT_DATABASE` | 数据库名称 |
| `is-consumer` | `Boolean` | `Boolean.FALSE` | 是否是消费者 |
| `thread-pool-args` | `ThreadPoolArgs` | `new ThreadPoolArgs()` | TaskExecutor配置 |
| `retry` | `RetryConfig` | `new RetryConfig()` | 消息重试配置 |

### `easyfk.config.db.redis` ← RedisProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `enable-dynamic` | `Boolean` | `Boolean.FALSE` | 是否启用动态数据源 |
| `redis-serializer` | `RedisValueSerializer` | `—` | Redis序列化器类型 |
| `trusted-packages` | `List<String>` | `new ArrayList<>()` | Jackson 多态反序列化额外允许的类名前缀（默认已包含 com.mcst.、java.util.、java.time.、java.lang.、java.math.） |
| `default-data-source` | `String` | `RedisConstants.DEFAULT_DATASOURCE` | 默认数据源名称 |
| `datasource` | `Map<String, RedisDataSourceConfig>` | `new HashMap<>()` | 多数据源配置 |

### `easyfk.config.db.clickhouse` ← ClickHouseProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `url` | `String` | `—` | 连接地址，例如: jdbc:clickhouse://localhost:8123/default |
| `username` | `String` | `—` | 用户名 |
| `password` | `String` | `—` | 密码 |
| `database` | `String` | `—` | 数据库名称 |
| `min-pool-size` | `Integer` | `5` | 连接池最小连接数 |
| `max-pool-size` | `Integer` | `20` | 连接池最大连接数 |
| `connection-timeout` | `Integer` | `30000` | 连接超时时间（毫秒） |
| `socket-timeout` | `Integer` | `300000` | Socket超时时间（毫秒） |


## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `db-redis` | `com.mcst.easyfk.db.redis.config.RedisDbConfig` |
| `db-mongo` | `com.mcst.easyfk.db.mongo.config.MongoAutoConfig` |
| `db-clickhouse` | `com.mcst.db.clickhouse.config.ClickHouseConfig` |

## 类型索引

- `com.mcst.db.clickhouse.annotation`：[ClickHouseColumn](#clickhousecolumn)、[ClickHouseTable](#clickhousetable)
- `com.mcst.db.clickhouse.config`：[ClickHouseConfig](#clickhouseconfig)、[ClickHouseJdbcHolder](#clickhousejdbcholder)
- `com.mcst.db.clickhouse.properties`：[ClickHouseProperties](#clickhouseproperties)
- `com.mcst.db.clickhouse.repository`：[BaseClickHouseRepositoryImpl](#baseclickhouserepositoryimpl)、[IBaseClickHouseRepository](#ibaseclickhouserepository)
- `com.mcst.db.clickhouse.search`：[ClickHouseRelativeTime](#clickhouserelativetime)、[ClickHouseSearchCondition](#clickhousesearchcondition)
- `com.mcst.db.clickhouse.utils`：[ClickHouseSearchConditionUtil](#clickhousesearchconditionutil)、[ClickHouseSqlUtil](#clickhousesqlutil)
- `com.mcst.easyfk.db.mongo.config`：[MongoAutoConfig](#mongoautoconfig)
- `com.mcst.easyfk.db.mongo.dao`：[BaseSpringMongoDAO](#basespringmongodao)
- `com.mcst.easyfk.db.mongo.entities`：[BaseMongoEntity](#basemongoentity)
- `com.mcst.easyfk.db.mongo.repository`：[BaseMongoRepositoryImpl](#basemongorepositoryimpl)
- `com.mcst.easyfk.db.mongo.util`：[MongoConditionBuilder](#mongoconditionbuilder)
- `com.mcst.easyfk.db.redis.config`：[DynamicRedisConfig](#dynamicredisconfig)、[PubSubConfig](#pubsubconfig)、[RedisDbConfig](#redisdbconfig)、[SimpleRedisConfig](#simpleredisconfig)
- `com.mcst.easyfk.db.redis.constants`：[RedisConstants](#redisconstants)、[RedisValueSerializer](#redisvalueserializer)
- `com.mcst.easyfk.db.redis.factory`：[ConnectionFactoryBuilder](#connectionfactorybuilder)
- `com.mcst.easyfk.db.redis.helper`：[RedisConfigHelper](#redisconfighelper)、[RedisConfigValidator](#redisconfigvalidator)
- `com.mcst.easyfk.db.redis.manager`：[RedisConnectionManager](#redisconnectionmanager)、[RedisOptManager](#redisoptmanager)
- `com.mcst.easyfk.db.redis.param`：[DsAndDbArgs](#dsanddbargs)、[KeyArgs](#keyargs)、[NamespaceArgs](#namespaceargs)、[RedisArgsHelper](#redisargshelper)
- `com.mcst.easyfk.db.redis.properties`：[BizDbProperties](#bizdbproperties)、[PushSubProperties](#pushsubproperties)、[RedisProperties](#redisproperties)
- `com.mcst.easyfk.db.redis.pubsub`：[IMessageListener](#imessagelistener)、[IPublishSubscribe](#ipublishsubscribe)、[PublishSubscribeImpl](#publishsubscribeimpl)、[SubscriptionManager](#subscriptionmanager)
- `com.mcst.easyfk.db.redis.pubsub.retry`：[DeadLetterCleanupConfig](#deadlettercleanupconfig)、[DeadLetterCleanupManager](#deadlettercleanupmanager)、[MessageRetryManager](#messageretrymanager)、[RetryConfig](#retryconfig)、[RetryableMessage](#retryablemessage)
- `com.mcst.easyfk.db.redis.serializer`：[FastJson2RedisSerializer](#fastjson2redisserializer)、[KryoRedisSerializer](#kryoredisserializer)、[SmartRedisSerializer](#smartredisserializer)
- `com.mcst.easyfk.db.redis.util`：[RedisUtil](#redisutil)

## 包 `com.mcst.db.clickhouse.annotation`

### ClickHouseColumn

`public @interface ClickHouseColumn`　注解：`@Target(ElementType.FIELD)` `@Retention(RetentionPolicy.RUNTIME)` `@Documented`　ClickHouse列注解 用于标记实体类字段对应的ClickHouse列名和属性

**方法**

```java
String name() default ""  // 列名（如果为空则使用字段名转下划线格式）
boolean primaryKey() default false  // 是否为主键（排序键）列：update 时不会出现在 SET 中
boolean timestamp() default false  // 是否为时间戳字段：查询条件未指定 timeField 时，用作 start/stop 时间范围和默认排序的列
boolean partitionKey() default false  // 是否为分区键列：update 时不会出现在 SET 中
boolean ignore() default false  // 是否忽略该字段（不参与 insert/update）
```

### ClickHouseTable

`public @interface ClickHouseTable`　注解：`@Target(ElementType.TYPE)` `@Retention(RetentionPolicy.RUNTIME)` `@Documented`　ClickHouse表注解 用于标记实体类对应的ClickHouse表名

**方法**

```java
String name()  // 表名
String database() default ""  // 数据库名（可选，如果不指定则使用配置的默认数据库）
```

## 包 `com.mcst.db.clickhouse.config`

### ClickHouseConfig

`public class ClickHouseConfig`　注解：`@AutoConfiguration` `@EnableConfigurationProperties(ClickHouseProperties.class)` `@ConditionalOnProperty(prefix = "easyfk.config.db.clickhouse", name = "url")` `@AutoConfigureAfter(DataSourceAutoConfiguration.class)`　ClickHouse 自动配置 只注册 ClickHouseJdbcHolder，不注册 DataSource / JdbcTemplate 类型的 Bean…

**方法**

```java
@Bean @ConditionalOnMissingBean ClickHouseJdbcHolder clickHouseJdbcHolder(ClickHouseProperties clickHouseProperties)
```

### ClickHouseJdbcHolder

`public class ClickHouseJdbcHolder implements DisposableBean`　注解：`@Slf4j`　ClickHouse 连接持有者 DataSource 与 JdbcTemplate 只由本类持有、不注册为 Spring Bean， 因此不会参与按类型注入…

**构造器**

```java
ClickHouseJdbcHolder(ClickHouseProperties properties)
```

**方法**

```java
JdbcTemplate getJdbcTemplate()  // 获取 ClickHouse 专用 JdbcTemplate（首次调用时初始化连接池）
DataSource getDataSource()  // 获取 ClickHouse 数据源（首次调用时初始化连接池）
void destroy()
```

## 包 `com.mcst.db.clickhouse.properties`

### ClickHouseProperties

`public class ClickHouseProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.db.clickhouse")`

**字段 / 常量**

```java
String url  // 连接地址，例如: jdbc:clickhouse://localhost:8123/default
String username  // 用户名
String password  // 密码
String database  // 数据库名称
Integer minPoolSize = 5  // 连接池最小连接数
Integer maxPoolSize = 20  // 连接池最大连接数
Integer connectionTimeout = 30000  // 连接超时时间（毫秒）
Integer socketTimeout = 300000  // Socket超时时间（毫秒）
```

## 包 `com.mcst.db.clickhouse.repository`

### BaseClickHouseRepositoryImpl

`public class BaseClickHouseRepositoryImpl<T> implements IBaseClickHouseRepository<T>`　注解：`@Slf4j`　通用ClickHouse数据访问对象基类实现

**字段 / 常量**

```java
Class<T> modelClass
```

**构造器**

```java
@SuppressWarnings("unchecked") BaseClickHouseRepositoryImpl()
```

**方法**

```java
JdbcTemplate getJdbcTemplate()  // ClickHouse 专用 JdbcTemplate（首次调用时初始化连接池）
void insert(T entity)
void insertBatch(List<T> entities)
void insertBatch(List<T> entities, int batchSize)
List<T> queryList(ClickHouseSearchCondition condition)
T queryOne(ClickHouseSearchCondition condition)
long count(ClickHouseSearchCondition condition)
List<Map<String, Object>> aggregate(ClickHouseSearchCondition condition)
void deleteByTimeRange(String startTime, String endTime)
void delete(ClickHouseSearchCondition condition)
void update(T entity, ClickHouseSearchCondition condition)
List<T> executeQuery(String sql)
List<Map<String, Object>> executeQueryForMap(String sql)
int executeUpdate(String sql)
boolean tableExists()
String getTableName()
```

### IBaseClickHouseRepository

`public interface IBaseClickHouseRepository<T>`　通用ClickHouse数据访问对象基类接口 提供基础的CRUD操作功能

**方法**

```java
void insert(T entity)  // 单条数据插入
void insertBatch(List<T> entities)  // 批量数据插入
void insertBatch(List<T> entities, int batchSize)  // 批量数据插入（指定批次大小）
List<T> queryList(ClickHouseSearchCondition condition)  // 条件查询
T queryOne(ClickHouseSearchCondition condition)  // 查询单条记录
long count(ClickHouseSearchCondition condition)  // 查询总数
List<Map<String, Object>> aggregate(ClickHouseSearchCondition condition)  // 执行聚合查询
void deleteByTimeRange(String startTime, String endTime)  // 删除数据（根据时间范围）
void delete(ClickHouseSearchCondition condition)  // 删除数据（根据条件） 注意：ClickHouse的删除是异步的，使用ALTER TABLE ... DELETE
void update(T entity, ClickHouseSearchCondition condition)  // 更新数据（根据条件） 注意：ClickHouse的更新是异步的，使用ALTER TABLE ... UPDATE
List<T> executeQuery(String sql)  // 执行原生SQL查询
List<Map<String, Object>> executeQueryForMap(String sql)  // 执行原生SQL查询，返回Map列表
int executeUpdate(String sql)  // 执行原生SQL（INSERT/UPDATE/DELETE等）
boolean tableExists()  // 检查表是否存在
String getTableName()  // 获取表名
```

## 包 `com.mcst.db.clickhouse.search`

### ClickHouseRelativeTime

`public final class ClickHouseRelativeTime implements Serializable`　ClickHouse 相对时间表达式，如 -1h、+2d（单位 s/m/h/d/w/y） 只有显式包装成本类型的值才会被渲染为 now() ± INTERVAL n UNIT，普通字符串值一律按字符串字面量处理。

**方法**

```java
static ClickHouseRelativeTime of(String expression)
static boolean isRelativeTime(String expression)
String toSql()  // 渲染为 ClickHouse SQL 表达式
String toString()
```

### ClickHouseSearchCondition

`public class ClickHouseSearchCondition implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)`　ClickHouse查询条件封装类

**字段 / 常量**

```java
Integer top  // 取前N条数据
String start  // 查询开始时间
String stop  // 查询结束时间
String timeField  // 时间字段名（用于时间范围查询和默认排序）；为空时取实体 @ClickHouseColumn(timestamp = true) 字段，再缺省为 create_time
String[] selectFields  // 查询字段
String[] aggregationFunctions  // 聚合函数，如：count(*), sum(amount), avg(price)
String[] groupByFields  // 分组字段
Map<String, String> likeConditions  // 模糊查询条件 (LIKE)
Map<String, Object> equalsConditions  // 等于查询条件
Map<String, Object> notEqualsConditions  // 不等于查询条件
Map<String, List<?>> inConditions  // IN查询条件
Map<String, Object> gtConditions  // 大于查询条件
Map<String, Object> gteConditions  // 大于等于查询条件
Map<String, Object> ltConditions  // 小于查询条件
Map<String, Object> lteConditions  // 小于等于查询条件
Map<String, Object[]> betweenConditions  // BETWEEN查询条件，key为字段名，value为[min, max]数组
PageSearch pageSearch  // 分页查询条件
String customWhere  // 自定义WHERE条件（校验后拼接到SQL中，不允许 ;、注释和 DDL/DML 关键字）
String customSql  // 自定义SQL（完全自定义查询，必须是 SELECT/WITH，校验规则同 customWhere）
String[] descFields  // 降序排序字段
String[] ascFields  // 升序排序字段
Boolean defaultDesc = Boolean.TRUE  // 默认排序方向，true为降序，false为升序
Boolean useFinal = Boolean.FALSE  // 是否使用FINAL关键字（用于ReplacingMergeTree等表引擎）
```

## 包 `com.mcst.db.clickhouse.utils`

### ClickHouseSearchConditionUtil

`public class ClickHouseSearchConditionUtil`　ClickHouse查询条件转换工具类

**方法**

```java
static <T, P> ClickHouseSearchCondition createSearchCondition(SearchRequest<P> searchRequest, Class<T> entityClass)  // 将 SearchRequest 转换为 ClickHouseSearchCondition
static <T> void createEqualsCondition(T entity, Map<String, Object> equalsMap) throws IllegalAccessException  // 根据实体对象非空字段构建等于条件
```

### ClickHouseSqlUtil

`public class ClickHouseSqlUtil`　注解：`@Slf4j`　ClickHouse SQL生成工具类 值统一转义后以字面量拼接；表名、列名、排序/分组/查询字段必须是合法标识符…

**字段 / 常量**

```java
static final String DEFAULT_TIME_FIELD = "create_time"  // 未指定时间字段且实体没有 @ClickHouseColumn(timestamp = true) 字段时使用的时间列
```

**方法**

```java
static String getTableName(Class<?> clazz)  // 获取表名
static String getColumnName(Field field)  // 获取列名
static List<Field> getColumnFields(Class<?> clazz)  // 参与读写的列字段（排除 shouldIgnore(Field) 的字段）
static boolean isUpdatable(Field field)  // 是否可出现在 ALTER TABLE ... UPDATE 的 SET 中：ClickHouse 不允许更新主键列和分区键列
static String resolveTimeField(ClickHouseSearchCondition condition, Class<?> clazz)  // 解析时间范围与默认排序使用的时间列：条件显式指定 → 实体 timestamp = true 字段 → DEFAULT_TIME_FIELD
static <T> String buildInsertSql(T entity)  // 构建插入SQL
static <T> String buildBatchInsertSql(List<T> entities, Class<T> clazz)  // 构建多行 VALUES 的批量插入SQL
static <T> String buildUpdateSql(T entity, ClickHouseSearchCondition condition, Class<T> clazz)  // 构建 ALTER TABLE ... UPDATE mutation：只更新非空、非忽略、非主键/分区键字段；没有可更新字段时返回 null
static String buildDeleteSql(ClickHouseSearchCondition condition, Class<?> clazz)  // 构建 ALTER TABLE ... DELETE mutation
static <T> String buildQuerySql(ClickHouseSearchCondition condition, Class<T> clazz)  // 构建查询SQL
static <T> String buildCountSql(ClickHouseSearchCondition condition, Class<T> clazz)  // 构建Count查询SQL
static String buildWhereClause(ClickHouseSearchCondition condition, Class<?> clazz)  // 构建WHERE子句（时间列按 resolveTimeField 解析）
static boolean shouldIgnore(Field field)  // 是否不作为列参与读写：static/transient/合成字段，或 @ClickHouseColumn(ignore = true)
static String formatValue(Object value)  // 将值格式化为 SQL 字面量；只有 ClickHouseRelativeTime 会渲染为时间表达式
static String formatTimeValue(String timeStr)  // 格式化 start/stop：支持 now()、相对时间（如 -1h）和绝对时间字符串
static String checkIdentifier(String name, String what)  // 校验标识符（列名、表名，可带一级 db. 前缀）
static String checkFragment(String fragment, String what)  // 校验自定义 SQL 片段：去掉引号内的内容后，不允许出现 ;、注释、未闭合的引号以及 DDL/DML 关键字
static String checkReadOnlySql(String sql, String what)  // 校验自定义只读查询：必须以 SELECT/WITH 开头，并满足 checkFragment
```

## 包 `com.mcst.easyfk.db.mongo.config`

### MongoAutoConfig

`public class MongoAutoConfig`　注解：`@AutoConfiguration` `@ConditionalOnClass(MongoTemplate.class)` `@EnableMongoAuditing(dateTimeProviderRef = "mongoAuditingDateTimeProvider")`　Auto configuration for easyfk mongo support.

**方法**

```java
@Bean @ConditionalOnMissingBean(name = "mongoAuditingDateTimeProvider") DateTimeProvider mongoAuditingDateTimeProvider()
```

## 包 `com.mcst.easyfk.db.mongo.dao`

### BaseSpringMongoDAO

`public class BaseSpringMongoDAO<T extends BaseMongoEntity>`　注解：`@SuppressWarnings({"null", "unused"})`　Generic Mongo DAO that provides CRUD helpers based on SearchCondition.

**字段 / 常量**

```java
Class<T> entityClazz  // DAO 绑定的实体类型
@Autowired MongoTemplate mongoTemplate  // Spring Data 的 Mongo 操作入口
```

**构造器**

```java
@SuppressWarnings("unchecked") BaseSpringMongoDAO()  // 通过反射解析泛型实体类型。
BaseSpringMongoDAO(Class<T> entityClazz)  // 显式传入实体类型的构造器。
```

**方法**

```java
Class<T> getEntityClass()  // 获取底层实体类型。
void insert(T entity)  // 插入单条记录。
void saveOrUpdate(T entity)  // 保存单条记录。 存在则更新，不存在则插入。
void insertBatch(List<T> entities)  // 批量插入，自动按 BATCH_SIZE 分批。
String insertAndReturnId(T entity)  // 插入并返回字符串形式的主键。
DeleteResult delete(T entity)  // 根据实体删除。
DeleteResult deleteById(Object id)  // 根据主键删除。
DeleteResult deleteByQuery(Query q)  // 根据 Query 删除。
DeleteResult deleteByCondition(SearchCondition condition)  // 根据条件删除。
boolean exists(SearchCondition condition)  // 判断条件结果是否存在。
boolean exists(Query q)  // 根据 Query 判断是否存在。
boolean exists(String field, Object value)  // 判断某个字段值是否存在。
boolean exists(T example)  // 根据示例实体判断是否存在。
long count()  // 统计集合全部记录数。
long count(String key, Object value)  // 根据单字段统计数量。
long count(Query q)  // 根据 Query 统计数量。
long count(SearchCondition condition)  // 根据 SearchCondition 统计数量。
long countByEntity(T entity)  // 根据示例实体统计数量。
long countByCondition(SearchCondition condition)  // SearchCondition 快捷统计。
T findOne(String key, Object value)  // 根据单字段查询一条。
T findOne(Map<String, Object> valueMap)  // 根据多字段精确匹配查询一条。
T findOne(Query q)  // 执行任意 Query 查询一条。
T findOneByEntity(T example)  // 根据示例实体查询一条。
List<T> findByEntity(T example)  // 根据示例实体查询列表。
T findById(Object id, String... selectColumns)  // 根据主键查询，可选择部分字段。
List<T> findByField(String field, Object value)  // 根据单字段条件查询列表。
List<T> findByField(Map<String, Object> valueMap)  // 根据多字段匹配查询列表。
List<T> findByCondition(SearchCondition condition)  // 根据 SearchCondition 查询列表。
List<T> findAll()  // 查询集合全部数据。
T findOneByCondition(SearchCondition condition)  // 根据 SearchCondition 查询单条。
PageResult<T> findByPage(SearchCondition searchCondition)  // SearchCondition 分页查询。
UpdateResult updateEntity(T entity)  // 全量更新：null 字段会被 unset。
UpdateResult updateEntitySelective(T entity, String... nullProperties)  // 增量更新：仅对非空字段 set，nullProperties 显式清空。
UpdateResult updateFirst(T newEntity, SearchCondition condition)  // 根据条件更新第一条记录 可实现乐观锁效果
UpdateResult updateEntityByCondition(T newEntity, SearchCondition condition)  // 条件增量更新：批量写入 newEntity 非空字段。
T atomicIncrement(SearchCondition condition, String field, Number value)  // 原子增加字段值，并返回更新后的实体
```

## 包 `com.mcst.easyfk.db.mongo.entities`

### BaseMongoEntity

`public class BaseMongoEntity implements Serializable`　Lombok：`@Data`　MongoDB 完整实体类 继承基础实体类，增加软删除功能 适用于需要软删除的业务场景

**字段 / 常量**

```java
@Serial static final long serialVersionUID = 1L
@Id @JSONField(serialize = false) @JsonIgnore ObjectId objectId  // MongoDB 主键 在数据库中存储为 _id -- GETTER -- 获取 ObjectId
@Transient String id  // 字符串形式的 ID，不持久化到数据库 用于方便的 ID 访问和传输
@CreatedDate LocalDateTime createdAt  // 创建时间 自动在插入时设置
@LastModifiedDate LocalDateTime updatedAt  // 更新时间 自动在插入和更新时设置
```

**方法**

```java
void setId(String id)  // 设置 ID 同时设置 ObjectId 和字符串形式的 ID
String getId()  // 获取字符串形式的 ID 如果 id 为空但 objectId 存在，则从 objectId 转换
void setObjectId(ObjectId objectId)  // 设置 ObjectId 同时更新字符串形式的 ID
```

## 包 `com.mcst.easyfk.db.mongo.repository`

### BaseMongoRepositoryImpl

`public class BaseMongoRepositoryImpl<D extends BaseSpringMongoDAO<P>, T extends Serializable, P extends BaseMongoEntity, PK extends Serializable> implements IBaseRepository<T, PK>`　注解：`@SuppressWarnings("unchecked")`　Generic mongo repository implementation mirroring behaviour of the MyBatis base repo.

**字段 / 常量**

```java
Class<T> dtoClazz
Class<P> entityClazz
@Autowired D baseMongoDAO
```

**构造器**

```java
BaseMongoRepositoryImpl()
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
PK insertAndReturnId(T param)
BaseResult<?> insertBatch(List<T> data)
BaseResult<?> deleteById(PK id)
BaseResult<?> deleteByCondition(SearchCondition condition)
BaseResult<?> updateEntityByCondition(T param, SearchCondition condition)
BaseResult<?> updateBySelective(T param, String... nullProperties)
BaseResult<?> saveOrUpdateBySelective(T param, String... nullProperties)
SearchCondition buildEqualsCondition(String field, Object value, String... selectFields)
```

## 包 `com.mcst.easyfk.db.mongo.util`

### MongoConditionBuilder

`public final class MongoConditionBuilder`　注解：`@SuppressWarnings("null")`　Helper class responsible for transforming SearchCondition into Mongo Query.

**方法**

```java
static Query buildQuery(SearchCondition condition, boolean withSelectedFields, Class<?> entityClazz)
static Query buildBaseQuery(SearchCondition condition, boolean withSelectedFields)
static void applyTop(Query query, Integer top)
```

## 包 `com.mcst.easyfk.db.redis.config`

### DynamicRedisConfig

`public class DynamicRedisConfig`　注解：`@Slf4j` `@AutoConfiguration` `@ConditionalOnProperty(prefix = "easyfk.config.db.redis", name = "enable-dynamic", havingValue = "true")` `@AutoConfigureBefore(RedisAutoConfiguration.class)`　Redis动态数据源配置类 当启用动态数据源时，会自动配置多个RedisTemplate和数据源管理器

**方法**

```java
@Bean(destroyMethod = "") @Primary RedisConnectionFactory redisConnectionFactory()  // 对外暴露默认数据源（default-data-source）的默认库连接工厂
@Bean @Primary RedisTemplate<String, Object> redisTemplate()  // 默认数据源的 RedisTemplate（与简单模式一致，使用框架序列化器），替代 Boot 默认的 redisTemplate
@PostConstruct void init()
```

### PubSubConfig

`public class PubSubConfig`　注解：`@AutoConfiguration` `@EnableConfigurationProperties(PushSubProperties.class)` `@ConditionalOnProperty(name = "easyfk.config.db.redis.pubsub.open", havingValue = "true")`

**方法**

```java
@Bean @ConditionalOnMissingBean IPublishSubscribe publishSubscribe()
@Bean("redisTaskExecutor") @ConditionalOnProperty(name = "easyfk.config.db.redis.pubsub.is-consumer", havingValue = "true") ThreadPoolTaskExecutor redisTaskExecutor()  // 配置Redis消息监听容器的TaskExecutor
@Bean @ConditionalOnMissingBean SubscriptionManager subscriptionManager()
```

### RedisDbConfig

`public class RedisDbConfig`　注解：`@AutoConfiguration` `@EnableConfigurationProperties({RedisProperties.class, BizDbProperties.class})` `@ImportAutoConfiguration({PubSubConfig.class, DynamicRedisConfig.class, SimpleRedisConfig.class})`　Redis默认配置类 当未启用动态数据源时，使用Spring Boot默认的Redis配置

**方法**

```java
@Bean @ConditionalOnMissingBean RedisConnectionManager redisConnectionManager()
@Bean @ConditionalOnMissingBean RedisOptManager redisOptManager()
@Bean @ConditionalOnMissingBean RedisArgsHelper keyArgsHelper()
```

### SimpleRedisConfig

`public class SimpleRedisConfig`　注解：`@Slf4j` `@AutoConfiguration` `@ConditionalOnProperty(prefix = "easyfk.config.db.redis", name = "enable-dynamic", havingValue = "false", matchIfMissing = true)`　Redis默认配置类 当未启用动态数据源时，使用Spring Boot默认的Redis配置

**方法**

```java
@Bean @Primary RedisTemplate<String, Object> redisTemplate()  // 创建默认的 RedisTemplate 使用自定义序列化器，非事务模式 注意：创建完成后会自动注册到 RedisConnectionManager（通过 @PostConstruct）
```

## 包 `com.mcst.easyfk.db.redis.constants`

### RedisConstants

`public final class RedisConstants`　Redis相关常量

**字段 / 常量**

```java
static final String DEFAULT_DATASOURCE = "default"  // 默认数据源名称
static final String DEFAULT_DATABASE = "default"  // 默认数据库名称
static final String CONNECTION_KEY_SEPARATOR = "::"  // 连接键分隔符
```

### RedisValueSerializer

`public enum RedisValueSerializer`

**枚举常量**

```java
DEFAULT  // 默认序列化器
FastJSON  // FastJson
KRYO  // kryo
```

## 包 `com.mcst.easyfk.db.redis.factory`

### ConnectionFactoryBuilder

`public class ConnectionFactoryBuilder`　注解：`@Slf4j`　Redis连接工厂建造者 支持单机、集群、哨兵三种部署模式，提供完整的连接池、SSL、拓扑刷新等高级功能 专为生产环境设计，确保高性能、高可用性和安全性

**方法**

```java
static RedisConnectionFactory createConnectionFactory(String dataSourceName, RedisDataSourceConfig config)  // 根据配置创建RedisConnectionFactory 支持单机、集群、哨兵三种模式，自动应用连接池、SSL等高级配置
```

## 包 `com.mcst.easyfk.db.redis.helper`

### RedisConfigHelper

`public class RedisConfigHelper`　注解：`@Slf4j`　Redis配置助手类，提供便捷的配置构建方法

**方法**

```java
static RedisProperties.RedisDataSourceConfig createStandalone(String host, int port, int database)  // 创建单机模式数据源配置
static RedisProperties.RedisDataSourceConfig createStandalone(String host, int port, int database, String password)  // 创建单机模式数据源配置（带密码）
static RedisProperties.RedisDataSourceConfig createCluster(String... nodes)  // 创建集群模式数据源配置
static RedisProperties.RedisDataSourceConfig createSentinel(String master, String... sentinelNodes)  // 创建哨兵模式数据源配置
static RedisProperties.RedisDataSourceConfig createCluster(String password, String... nodes)  // 创建集群模式数据源配置（带密码）
static RedisProperties.RedisDataSourceConfig.PoolConfig createHighConcurrencyPool()  // 创建高并发连接池配置
static RedisProperties.RedisDataSourceConfig.PoolConfig createStandardPool()  // 创建标准连接池配置
static RedisProperties.RedisDataSourceConfig.PoolConfig createLightweightPool()  // 创建轻量级连接池配置
static RedisProperties.RedisDataSourceConfig withPool(RedisProperties.RedisDataSourceConfig config, RedisProperties.RedisDataSourceConfig.PoolConfig pool)  // 为配置应用连接池
static RedisProperties.RedisDataSourceConfig withTimeout(RedisProperties.RedisDataSourceConfig config, Duration timeout)  // 为配置设置超时
static RedisProperties.RedisDataSourceConfig createDataCenterCluster(String... nodes)  // 创建用于系统数据中心的集群配置（高性能）
static RedisProperties.RedisDataSourceConfig createConfigCluster(String... nodes)  // 创建用于配置数据的集群配置（标准性能）
static RedisProperties.RedisDataSourceConfig createCacheStandalone(String host, int port, int database)  // 创建用于缓存的单机配置（轻量级）
static String getConfigSummary(String name, RedisProperties.RedisDataSourceConfig config)  // 打印配置摘要信息
static RedisProperties.RedisDataSourceConfig withDatabase(RedisProperties.RedisDataSourceConfig config, String databaseAlias, int databaseIndex)  // 为配置添加数据库别名
static RedisProperties.RedisDataSourceConfig withDatabases(RedisProperties.RedisDataSourceConfig config, Map<String, Integer> databases)  // 为配置批量添加数据库别名
static Map<String, Integer> createDatabaseMap(String... pairs)  // 创建多数据库映射
static RedisProperties.RedisDataSourceConfig withSsl(RedisProperties.RedisDataSourceConfig config)  // 启用SSL配置
static RedisProperties.RedisDataSourceConfig withSsl(RedisProperties.RedisDataSourceConfig config, String trustStore, String trustStorePassword)  // 配置SSL
static void validateAndLog(String name, RedisProperties.RedisDataSourceConfig config)  // 验证配置完整性
static String getConfigMode(RedisProperties.RedisDataSourceConfig config)  // 获取配置模式描述
```

### RedisConfigValidator

`public class RedisConfigValidator`　注解：`@Slf4j`　Redis配置验证器

**方法**

```java
static void validateConfig(RedisProperties redisProperties)  // 验证Redis配置
```

## 包 `com.mcst.easyfk.db.redis.manager`

### RedisConnectionManager

`public class RedisConnectionManager implements DisposableBean`　注解：`@Slf4j`　Redis模板管理器 管理数据源和数据库级别的RedisTemplate，保证并发安全

**方法**

```java
void putRedisTemplate(String key, RedisTemplate<String, Object> redisTemplate)
void putConnectionFactory(String key, RedisConnectionFactory factory)
RedisTemplate<String, Object> getRedisTemplate(String datasource, String databaseName)
RedisConnectionFactory getConnectionFactory(String datasource, String databaseName)
RedisTemplate<String, Object> getRedisTemplate(DsAndDbArgs args)  // 获取指定数据源和数据库的RedisTemplate
RedisTemplate<String, Object> getTransactionalRedisTemplate(String datasource, String databaseName)
RedisTemplate<String, Object> getTransactionalRedisTemplate(DsAndDbArgs args)
RedisConnectionFactory getConnectionFactory(DsAndDbArgs args)  // 获取指定数据源和数据库的RedisConnectionFactory
@PreDestroy void preDestroy()
void destroy() throws Exception  // DisposableBean接口实现
```

### RedisOptManager

`public class RedisOptManager`　注解：`@Slf4j` `@DependsOn("redisConnectionManager")` `@SuppressWarnings("all")`　Spring Redis管理器 支持多数据源和多数据库操作 依赖于RedisConnectionManager，确保在连接管理器销毁前完成操作清理

**方法**

```java
Set<String> getKeys(String pattern, KeyArgs args)  // 根据模式匹配获取Redis中的所有键,包含全部类型的数据结构
Long autoId(KeyArgs args)  // 自动生成递增ID
Long autoIdByExpire(KeyArgs args, Duration timeToLive)  // 生成带过期时间的自动递增ID 如果键不存在过期时间或已过期，则设置新的过期时间
void expireKey(KeyArgs args, Duration timeToLive)  // 为Redis键设置过期时间,包含全部类型的数据结构
void expireKeyAt(KeyArgs args, Date date)  // 为Redis键设置在指定时间点过期,包含全部类型的数据结构
long getKeyExpire(KeyArgs args)  // 获取Redis键的过期时间,包含全部类型的数据结构
boolean existKey(KeyArgs args)  // 检查Redis中是否存在指定的键,包含全部类型的数据结构
BaseResult<?> deleteKey(KeyArgs args)  // 删除Redis中的指定键,包含全部类型的数据结构
BaseResult<?> putObject(KeyArgs args, Object value)  // 存储对象到Redis,针对KV数据结构
BaseResult<?> putObject(KeyArgs args, Object value, Duration timeToLive)  // 存储对象到Redis并设置过期时间,针对KV数据结构
boolean putIfAbsent(KeyArgs args, Object value, Duration timeToLive)  // 原子写入：仅当 key 不存在时写入并设置过期时间（对应 Redis SET NX EX）
<T> T getObject(KeyArgs args)  // 从Redis中获取对象,针对KV数据结构
BaseResult<?> multiSetForValue(Map<String, Object> keyValues, NamespaceArgs args)  // 批量保存键值对到Redis,针对KV数据结构
BaseResult<?> multiSetIfNotExistsForValue(Map<String, Object> keyValues, NamespaceArgs args)  // 批量保存键值对到Redis（仅当所有键都不存在时） 这是一个原子操作，要么所有键都设置成功，要么都不设置
<T> List<T> multiGetForValue(List<String> keys, NamespaceArgs args)  // 批量获取Redis中多个键的值
BaseResult<?> putValueToHash(KeyArgs args, String hashKey, Object obj)  // 向Hash中存储单个字段值
BaseResult<?> putObjectToHash(KeyArgs args, Object obj)  // 将Java对象转换为Map并存储到Hash中
BaseResult<?> putMapToHash(KeyArgs args, Map<String, Object> objectMap)  // 将Map中的所有键值对存储到Hash中
boolean existHashKey(KeyArgs args, String hashKey)  // 检查Hash中是否存在指定的字段
Map<String, Object> getMapFromHash(KeyArgs args)  // 获取Hash中的所有字段和值，转换为Map返回
<T> T getObjectFromHash(KeyArgs args, Class<T> clazz)  // 从Hash中获取所有字段值并转换为指定类型的Java对象
<T> T getValueFromHash(KeyArgs args, String hashKey)  // 从Hash中获取指定字段的值
List<Object> getAllValuesFromHash(KeyArgs args)  // 获取Hash中所有字段的值
List<Object> getValuesFromHash(KeyArgs args, List<String> hashKeys)  // 批量获取Hash中指定字段的值
Long getHashSize(KeyArgs args)  // 获取Hash中字段的数量
BaseResult<?> deleteObjectFromHash(KeyArgs args, String... hashKeys)  // 从Hash中删除指定的字段
BaseResult<?> putObjectToList(KeyArgs args, Object value)  // 向List的右端（尾部）添加元素
BaseResult<?> putObjectToListAtIndex(KeyArgs args, Object value, long index)  // 在List的指定索引位置设置元素值
BaseResult<?> putObjectsToList(KeyArgs args, List<?> values)  // 批量向List的右端（尾部）添加多个元素
<T> T getAndRemoveFirstObjectFromList(KeyArgs args)  // 获取并移除List的第一个元素（左端弹出）
<T> T getAndRemoveLastObjectFromList(KeyArgs args)  // 获取并移除List的最后一个元素（右端弹出）
<T> T getObjectFromList(KeyArgs args, long index)  // 获取List中指定索引位置的元素
<T> List<T> getAllObjectFromList(KeyArgs args)  // 获取List中的所有元素
BaseResult<?> deleteObjectFromList(KeyArgs args, Object value)  // 从List中删除指定值的元素 删除从尾部开始的第一个匹配元素
Long getListSize(KeyArgs args)  // 获取List的长度
<T> List<T> getPageFromList(KeyArgs args, int page, int pageSize)  // 从List中获取指定页的数据
<T> List<T> getRangeFromList(KeyArgs args, long start, long end)  // 从List中获取指定范围的数据
BaseResult<?> putObjectToSet(KeyArgs args, Object value)  // 向Set中添加元素
BaseResult<?> putObjectToZSet(KeyArgs args, Object value, double score)  // 向有序Set（ZSet）中添加带分数的元素
BaseResult<?> putObjectsToSet(KeyArgs args, Set<?> values)  // 批量向Set中添加多个元素
BaseResult<?> putObjectsToZSet(KeyArgs args, Set<ZSetOperations.TypedTuple<Object>> values)  // 批量向有序Set（ZSet）中添加带分数的元素
Long getSetSize(KeyArgs args)  // 获取Set中元素的数量
Long getZSetSize(KeyArgs args)  // 获取有序Set（ZSet）中元素的数量
Boolean objectIsSetMember(KeyArgs args, Object value)  // 检查元素是否是Set的成员
Boolean objectIsZSetMember(KeyArgs args, Object value)  // 检查元素是否是有序Set（ZSet）的成员
<T> Set<T> getAllObjectFromSet(KeyArgs args)  // 获取Set中的所有元素
<T> Set<T> getAllObjectFromZSet(KeyArgs args)  // 获取有序Set（ZSet）中的所有元素（按分数升序排列）
BaseResult<?> deleteObjectFromSet(KeyArgs args, Object... value)  // 从Set中删除指定元素
BaseResult<?> deleteObjectFromZSet(KeyArgs args, Object... value)  // 从有序Set（ZSet）中删除指定元素
<T> Set<T> getPageFromZSet(KeyArgs args, int page, int pageSize)  // 从有序Set（ZSet）中获取指定页的数据
<T> Set<T> getRangeFromZSet(KeyArgs args, double min, double max)  // 从有序Set（ZSet）中获取指定分数范围的元素
<T> Set<T> getRangeFromZSet(KeyArgs args, double min, double max, int page, int pageSize)  // 从有序Set（ZSet）中获取指定分数范围和页码的元素
List<Object> executePipelined(RedisCallback<Object> pipelineCallback, DsAndDbArgs args)  // 执行Redis管道批量操作 管道操作可以将多个Redis命令打包发送，减少网络往返次数，提高性能
List<Object> executePipelinedSimple(Consumer<RedisConnection> pipelineOperations, DsAndDbArgs args)  // 执行Redis管道批量操作（简化版本） 提供更简洁的API，直接操作RedisConnection
List<Object> executeTransaction(BiConsumer<RedisOperations<String, Object>, UnaryOperator<String>> transactionOperations, NamespaceArgs args)  // 执行Redis事务 事务保证一组命令的原子性执行，要么全部成功，要么全部失败
List<Object> executeTransactionWithWatch(List<String> watchKeys, BiConsumer<RedisOperations<String, Object>, UnaryOperator<String>> transactionOperations, NamespaceArgs namespaceArgs)  // 执行带WATCH的Redis事务 WATCH命令用于监视一个或多个键，如果在事务执行前这些键被修改，事务将被取消
<T> T executeLuaScript(String script, List<String> keys, List<Object> args, NamespaceArgs namespaceArgs)  // 执行Lua脚本（通用方法） Lua脚本在Redis服务器端执行，保证原子性，可用于复杂的数据操作
<T> T executeLuaScript(String script, Class<T> returnType, List<String> keys, List<Object> args, NamespaceArgs namespaceArgs)  // 执行Lua脚本（指定返回类型） 提供类型安全的Lua脚本执行，明确指定返回值类型
```

## 包 `com.mcst.easyfk.db.redis.param`

### DsAndDbArgs

`public class DsAndDbArgs`　Lombok：`@Data`

**字段 / 常量**

```java
String datasource = RedisConstants.DEFAULT_DATASOURCE  // 数据源
String databaseName = RedisConstants.DEFAULT_DATABASE  // 数据库名称
```

### KeyArgs

`public class KeyArgs extends NamespaceArgs`　Lombok：`@EqualsAndHashCode(callSuper = true)` `@Data`

**字段 / 常量**

```java
String key  // 键名
```

### NamespaceArgs

`public class NamespaceArgs extends DsAndDbArgs`　Lombok：`@EqualsAndHashCode(callSuper = true)` `@Data`

**字段 / 常量**

```java
String namespace  // 命名空间
```

### RedisArgsHelper

`public class RedisArgsHelper`　注解：`@SuppressWarnings("unused")`

**方法**

```java
KeyArgs createKeyArgs(String bizName, String key, String namespace)
KeyArgs createKeyArgs(String datasource, String database, String key, String namespace)
NamespaceArgs createNamespaceArgs(String bizName, String namespace)
NamespaceArgs createNamespaceArgs(String datasource, String database, String namespace)
DsAndDbArgs createDsAndDbArgs(String bizName)
DsAndDbArgs createDsAndDbArgs(String datasource, String database)
```

## 包 `com.mcst.easyfk.db.redis.properties`

### BizDbProperties

`public class BizDbProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.db.redis.biz-db")`

**字段 / 常量**

```java
Map<String, BizDb> dbMap = new HashMap<>()  // 业务数据库配置
```

#### BizDbProperties.BizDb

`public static class BizDb`　Lombok：`@Data`

**字段 / 常量**

```java
String datasource = RedisConstants.DEFAULT_DATASOURCE  // 数据源名称
String databaseName = RedisConstants.DEFAULT_DATABASE  // 数据库名称
```

### PushSubProperties

`public class PushSubProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.db.redis.pubsub")`

**字段 / 常量**

```java
Boolean open = Boolean.FALSE
String channel = RedisConstants.DEFAULT_DATASOURCE  // 订阅的频道
String datasource = RedisConstants.DEFAULT_DATASOURCE  // 数据源
String databaseName = RedisConstants.DEFAULT_DATABASE  // 数据库名称
Boolean isConsumer = Boolean.FALSE  // 是否是消费者
ThreadPoolArgs threadPoolArgs = new ThreadPoolArgs()  // TaskExecutor配置
RetryConfig retry = new RetryConfig()  // 消息重试配置
```

### RedisProperties

`public class RedisProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.db.redis")`　Redis多数据源配置属性

**字段 / 常量**

```java
Boolean enableDynamic = Boolean.FALSE  // 是否启用动态数据源
RedisValueSerializer redisSerializer  // Redis序列化器类型
List<String> trustedPackages = new ArrayList<>()  // Jackson 多态反序列化额外允许的类名前缀（默认已包含 com.mcst.、java.util.、java.time.、java.lang.、java.math.）
String defaultDataSource = RedisConstants.DEFAULT_DATASOURCE  // 默认数据源名称
Map<String, RedisDataSourceConfig> datasource = new HashMap<>()  // 多数据源配置
```

#### RedisProperties.RedisDataSourceConfig

`public static class RedisDataSourceConfig`　Lombok：`@Data`　Redis数据源配置类

**字段 / 常量**

```java
String host = "localhost"  // Redis服务器地址
Integer port = 6379  // Redis服务器端口
Integer database = 0  // 默认数据库索引（0-15），集群模式下无效
Map<String, Integer> databases = new HashMap<>()  // 多数据库配置（数据库别名 -> 数据库索引） 例如：cache -> 1, session -> 2, business -> 0
String password  // 密码
String username  // 用户名
Duration timeout = Duration.ofMillis(2000)  // 连接超时时间
Boolean ssl = Boolean.FALSE  // 是否启用SSL
SslConfig sslConfig  // SSL配置
PoolConfig pool = new PoolConfig()  // 连接池配置
ClusterConfig cluster  // 集群配置
SentinelConfig sentinel  // 哨兵配置
```

##### RedisProperties.RedisDataSourceConfig.PoolConfig

`public static class PoolConfig`　Lombok：`@Data`　连接池配置

**字段 / 常量**

```java
Integer maxActive = 32  // 最大连接数
Integer maxIdle = 16  // 最大空闲连接数
Integer minIdle = 4  // 最小空闲连接数
Duration maxWait = Duration.ofSeconds(1)  // 获取连接最大等待时间
Boolean testOnBorrow = Boolean.FALSE  // 是否在获取连接时验证连接
Boolean testWhileIdle = Boolean.TRUE  // 是否在空闲时验证连接
Duration timeBetweenEvictionRuns = Duration.ofSeconds(30)  // 空闲连接检测间隔
```

##### RedisProperties.RedisDataSourceConfig.ClusterConfig

`public static class ClusterConfig`　Lombok：`@Data`　集群配置

**字段 / 常量**

```java
List<String> nodes  // 集群节点列表
Integer maxRedirects = 3  // 最大重定向次数
Boolean topologyRefresh = Boolean.TRUE  // 是否启用拓扑刷新
Duration topologyRefreshPeriod = Duration.ofSeconds(30)  // 拓扑刷新间隔
Boolean adaptiveRefresh = Boolean.TRUE  // 是否启用自适应拓扑刷新
```

##### RedisProperties.RedisDataSourceConfig.SentinelConfig

`public static class SentinelConfig`　Lombok：`@Data`　哨兵配置

**字段 / 常量**

```java
List<String> nodes  // 哨兵节点列表
String master = "mymaster"  // 主服务器名称
String sentinelPassword  // 哨兵密码
```

##### RedisProperties.RedisDataSourceConfig.SslConfig

`public static class SslConfig`　Lombok：`@Data`　SSL配置

**字段 / 常量**

```java
String trustStore  // 信任存储路径
String trustStorePassword  // 信任存储密码
String keyStore  // 密钥存储路径
String keyStorePassword  // 密钥存储密码
Boolean verifyPeer = Boolean.TRUE  // 是否验证对等证书
Boolean verifyHostname = Boolean.TRUE  // 是否启用主机名验证
```

## 包 `com.mcst.easyfk.db.redis.pubsub`

### IMessageListener

`public interface IMessageListener<T>`　Redis发布订阅消息监听器接口（泛型版本）

**方法**

```java
void onMessage(String channel, T message)  // 接收到普通频道消息时的回调
default void onPatternMessage(String pattern, String channel, T message)  // 接收到模式匹配频道消息时的回调
default void onSubscribe(String channel, int count)  // 订阅成功时的回调
default void onUnsubscribe(String channel, int count)  // 取消订阅时的回调
default void onPatternSubscribe(String pattern, int count)  // 模式订阅成功时的回调
default void onPatternUnsubscribe(String pattern, int count)  // 取消模式订阅时的回调
default void onConnectionLost(Exception ex)  // 连接异常时的回调
default void onConnectionRecovered()  // 连接恢复时的回调
```

### IPublishSubscribe

`public interface IPublishSubscribe`　Redis发布订阅接口

**方法**

```java
Long publish(String channel, String message)  // 发布消息到指定频道
Long publish(String channel, String message, String channelPrefix)  // 发布消息到指定频道（带频道前缀）
<T> Long publishObject(String channel, T message)  // 发布对象消息到指定频道
<T> Long publishObject(String channel, Object message, String channelPrefix)  // 发布对象消息到指定频道（带频道前缀）
String subscribe(String channel, IMessageListener<String> listener)  // 订阅指定频道（字符串消息）
String subscribe(String channel, IMessageListener<String> listener, String channelPrefix)  // 订阅指定频道（字符串消息，带频道前缀）
String subscribeObject(String channel, IMessageListener<Object> listener)  // 订阅指定频道（对象消息）
String subscribeObject(String channel, IMessageListener<Object> listener, String channelPrefix)  // 订阅指定频道（对象消息，带频道前缀）
String psubscribe(String pattern, IMessageListener<String> listener)  // 订阅匹配模式的频道（字符串消息，支持通配符）
String psubscribe(String pattern, IMessageListener<String> listener, String channelPrefix)  // 订阅匹配模式的频道（字符串消息，支持通配符，带频道前缀）
String psubscribeObject(String pattern, IMessageListener<Object> listener)  // 订阅匹配模式的频道（对象消息，支持通配符）
String psubscribeObject(String pattern, IMessageListener<Object> listener, String channelPrefix)  // 订阅匹配模式的频道（对象消息，支持通配符，带频道前缀）
void unsubscribe(String subscriptionId)  // 取消订阅指定频道
void unsubscribeChannel(String channel)  // 取消订阅指定频道
void unsubscribeChannel(String channel, String channelPrefix)  // 取消订阅指定频道（带频道前缀）
void punsubscribe(String pattern)  // 取消模式订阅
void punsubscribe(String pattern, String channelPrefix)  // 取消模式订阅（带频道前缀）
Set<String> getActiveChannels()  // 获取活跃的频道列表
Set<String> getActiveChannels(String channelPrefix)  // 获取活跃的频道列表（带频道前缀）
Long getChannelSubscribers(String channel)  // 获取指定频道的订阅者数量
Long getChannelSubscribers(String channel, String channelPrefix)  // 获取指定频道的订阅者数量（带频道前缀）
```

### PublishSubscribeImpl

`public class PublishSubscribeImpl implements IPublishSubscribe`

**方法**

```java
Long publish(String channel, String message)  // 发布消息到指定频道
Long publish(String channel, String message, String channelPrefix)  // 发布消息到指定频道（带频道前缀）
Long publishObject(String channel, Object message)  // 发布对象消息到指定频道
Long publishObject(String channel, Object message, String channelPrefix)  // 发布对象消息到指定频道（带频道前缀）
String subscribe(String channel, IMessageListener<String> listener)  // 订阅指定频道
String subscribe(String channel, IMessageListener<String> listener, String channelPrefix)  // 订阅指定频道（带频道前缀）
String subscribeObject(String channel, IMessageListener<Object> listener)  // 订阅指定频道（支持对象消息）
String subscribeObject(String channel, IMessageListener<Object> listener, String channelPrefix)  // 订阅指定频道（支持对象消息，带频道前缀）
String psubscribe(String pattern, IMessageListener<String> listener)  // 订阅匹配模式的频道（支持通配符）
String psubscribe(String pattern, IMessageListener<String> listener, String channelPrefix)  // 订阅匹配模式的频道（支持通配符，带频道前缀）
String psubscribeObject(String pattern, IMessageListener<Object> listener)  // 订阅匹配模式的频道（支持通配符，支持对象消息）
String psubscribeObject(String pattern, IMessageListener<Object> listener, String channelPrefix)  // 订阅匹配模式的频道（支持通配符，支持对象消息，带频道前缀）
void unsubscribe(String subscriptionId)  // 取消订阅指定频道
void unsubscribeChannel(String channel)  // 取消订阅指定频道
void unsubscribeChannel(String channel, String channelPrefix)  // 取消订阅指定频道（带频道前缀）
void punsubscribe(String pattern)  // 取消模式订阅
void punsubscribe(String pattern, String channelPrefix)  // 取消模式订阅（带频道前缀）
Set<String> getActiveChannels()  // 获取活跃的频道列表
Set<String> getActiveChannels(String channelPrefix)  // 获取活跃的频道列表（带频道前缀）
Long getChannelSubscribers(String channel)  // 获取指定频道的订阅者数量
Long getChannelSubscribers(String channel, String channelPrefix)  // 获取指定频道的订阅者数量（带频道前缀）
```

### SubscriptionManager

`public class SubscriptionManager implements DisposableBean, ApplicationListener<ContextClosedEvent>`　注解：`@Slf4j` `@DependsOn("redisConnectionManager")` `@SuppressWarnings("all")`　Redis订阅管理器 依赖于RedisConnectionManager，确保在连接管理器销毁前完成订阅清理

**方法**

```java
String subscribeChannel(String channel, IMessageListener<String> messageListener, String channelPrefix)  // 订阅频道
String subscribeObjectChannel(String channel, IMessageListener<Object> messageListener, String channelPrefix)  // 订阅频道（支持对象消息）
String subscribePattern(String pattern, IMessageListener<String> messageListener, String channelPrefix)  // 订阅模式
String subscribeObjectPattern(String pattern, IMessageListener<Object> messageListener, String channelPrefix)  // 订阅模式（支持对象消息）
void unsubscribe(String subscriptionId)  // 取消订阅
void unsubscribeChannel(String channel, String channelPrefix)  // 取消频道订阅
void unsubscribePattern(String pattern, String channelPrefix)  // 取消模式订阅
void clearAllSubscriptions()  // 清理所有订阅
@PreDestroy void preDestroy()  // 优雅关闭处理 - @PreDestroy注解
boolean isShuttingDown()  // 检查是否正在关闭
int getActiveSubscriptionCount()  // 获取当前活跃订阅数量
Map<String, Long> getExceptionStatistics()  // 获取异常统计信息
void clearExceptionStatistics()  // 清理异常统计
MessageRetryManager.RetryStatistics getRetryStatistics()  // 获取重试统计信息
void clearDeadLetterQueue()  // 清理死信队列
RetryableMessage[] getDeadLetterMessages()  // 获取死信队列消息
DeadLetterCleanupManager.CleanupResult manualCleanupDeadLetterQueue()  // 手动触发死信队列清理
DeadLetterCleanupManager.CleanupStatistics getDeadLetterCleanupStatistics()  // 获取死信队列清理统计
void startDeadLetterAutoCleanup()  // 启动死信队列自动清理
void stopDeadLetterAutoCleanup()  // 停止死信队列自动清理
void onApplicationEvent(ContextClosedEvent event)
void destroy() throws Exception
Long publish(String channel, String message)  // 发布消息到指定频道
Long publish(String channel, String message, String channelPrefix)  // 发布消息到指定频道（带频道前缀）
Long publishObject(String channel, Object message)  // 发布对象消息到指定频道
Long publishObject(String channel, Object message, String channelPrefix)  // 发布对象消息到指定频道（带频道前缀）
String subscribe(String channel, IMessageListener<String> listener)  // 订阅指定频道
String subscribe(String channel, IMessageListener<String> listener, String channelPrefix)  // 订阅指定频道（带频道前缀）
String subscribeObject(String channel, IMessageListener<Object> listener)  // 订阅指定频道（支持对象消息）
String subscribeObject(String channel, IMessageListener<Object> listener, String channelPrefix)  // 订阅指定频道（支持对象消息，带频道前缀）
String subscribePatternPublic(String pattern, IMessageListener<String> listener)  // 订阅匹配模式的频道（支持通配符）
String subscribePatternPublic(String pattern, IMessageListener<String> listener, String channelPrefix)  // 订阅匹配模式的频道（支持通配符，带频道前缀）
String psubscribeObject(String pattern, IMessageListener<Object> listener)  // 订阅匹配模式的频道（支持通配符，支持对象消息）
String psubscribeObject(String pattern, IMessageListener<Object> listener, String channelPrefix)  // 订阅匹配模式的频道（支持通配符，支持对象消息，带频道前缀）
void unsubscribeChannel(String channel)  // 取消订阅指定频道
void unsubscribePattern(String pattern)  // 取消模式订阅
void unsubscribe(String pattern, String channelPrefix)  // 取消模式订阅（带频道前缀）
Set<String> getActiveChannels()  // 获取活跃的频道列表
Set<String> getActiveChannels(String channelPrefix)  // 获取活跃的频道列表（带频道前缀）
Long getChannelSubscribers(String channel)  // 获取指定频道的订阅者数量
Long getChannelSubscribers(String channel, String channelPrefix)  // 获取指定频道的订阅者数量（带频道前缀）
```

## 包 `com.mcst.easyfk.db.redis.pubsub.retry`

### DeadLetterCleanupConfig

`public class DeadLetterCleanupConfig`　Lombok：`@Data`　死信队列自动清理配置

**字段 / 常量**

```java
Boolean enabled = true  // 是否启用自动清理
Duration cleanupInterval = Duration.ofHours(2)  // 清理间隔
Duration maxRetentionTime = Duration.ofDays(7)  // 最大保留时间
Integer maxCapacity = 1000  // 最大容量（超过时清理最老的消息）
CleanupStrategy strategy = CleanupStrategy.TIME_BASED  // 清理策略
Integer maxCleanupBatchSize = 100  // 每次清理的最大数量
Boolean keepRecentFailures = true  // 是否保留最近的失败消息（用于问题排查）
Integer keepRecentCount = 50  // 保留的最近失败消息数量
```

**方法**

```java
static DeadLetterCleanupConfig defaultConfig()  // 创建默认配置
static DeadLetterCleanupConfig conservativeConfig()  // 创建保守清理配置（保留时间更长）
static DeadLetterCleanupConfig aggressiveConfig()  // 创建激进清理配置（保留时间较短）
static DeadLetterCleanupConfig highVolumeConfig()  // 创建高容量配置（适合高吞吐量场景）
void validate()  // 验证配置有效性
```

#### DeadLetterCleanupConfig.CleanupStrategy

`public enum CleanupStrategy`　清理策略枚举

**枚举常量**

```java
TIME_BASED  // 基于时间清理：清理超过保留时间的消息
CAPACITY_BASED  // 基于容量清理：当超过最大容量时清理最老的消息
HYBRID  // 混合策略：同时基于时间和容量
```

### DeadLetterCleanupManager

`public class DeadLetterCleanupManager`　注解：`@Slf4j`　死信队列自动清理管理器 负责定期清理死信队列中的过期或过多消息

**构造器**

```java
DeadLetterCleanupManager(DeadLetterCleanupConfig config, BlockingQueue<RetryableMessage> deadLetterQueue)
```

**方法**

```java
void start()  // 启动自动清理
void stop()  // 停止自动清理
CleanupResult manualCleanup()  // 手动触发清理
CleanupStatistics getStatistics()  // 获取清理统计信息
```

#### DeadLetterCleanupManager.CleanupResult

`public record CleanupResult(int cleanedCount, String strategy, String description)`　清理结果记录

**构造参数（record 组件）**

```java
int cleanedCount
String strategy
String description
```

#### DeadLetterCleanupManager.CleanupStatistics

`public record CleanupStatistics(LocalDateTime startTime, LocalDateTime currentTime, long totalCleanupOperations, long totalCleanedMessages, long timeBasedCleanups, long capacityBasedCleanups, LocalDateTime lastCleanupTime, int currentQueueSize, DeadLetterCleanupConfig config)`　清理统计记录

**构造参数（record 组件）**

```java
LocalDateTime startTime
LocalDateTime currentTime
long totalCleanupOperations
long totalCleanedMessages
long timeBasedCleanups
long capacityBasedCleanups
LocalDateTime lastCleanupTime
int currentQueueSize
DeadLetterCleanupConfig config
```

**方法**

```java
String toFormattedString()
```

### MessageRetryManager

`public class MessageRetryManager`　注解：`@Slf4j` `@SuppressWarnings("all")`　消息重试管理器 负责管理消息重试队列、死信队列和重试调度

**构造器**

```java
MessageRetryManager(RetryConfig retryConfig)
MessageRetryManager(RetryConfig retryConfig, DeadLetterCleanupConfig cleanupConfig)
```

**方法**

```java
boolean addToRetryQueue(String messageType, String channel, Object messageContent, IMessageListener<?> listener, Exception exception, String subscriptionId)  // 添加消息到重试队列（增强版本，包含队列满时的智能处理策略）
RetryStatistics getStatistics()  // 获取重试统计信息
void clearDeadLetterQueue()  // 清理死信队列
RetryableMessage[] getDeadLetterMessages()  // 获取死信队列消息
DeadLetterCleanupManager.CleanupResult manualCleanupDeadLetterQueue()  // 手动触发死信队列清理
DeadLetterCleanupManager.CleanupStatistics getCleanupStatistics()  // 获取死信队列清理统计
void startAutoCleanup()  // 启动自动清理
void stopAutoCleanup()  // 停止自动清理
@PreDestroy void shutdown()  // 优雅关闭
```

#### MessageRetryManager.RetryStatistics

`public record RetryStatistics(int retryQueueSize, int deadLetterQueueSize, long totalRetryAttempts, long successfulRetries, long failedRetries, long deadLetterMessages)`　重试统计信息记录

**构造参数（record 组件）**

```java
int retryQueueSize
int deadLetterQueueSize
long totalRetryAttempts
long successfulRetries
long failedRetries
long deadLetterMessages
```

**方法**

```java
double getRetrySuccessRate()
```

### RetryConfig

`public class RetryConfig`　Lombok：`@Data`　消息重试配置

**字段 / 常量**

```java
Boolean enabled = true  // 是否启用重试机制
Integer maxRetries = 3  // 最大重试次数
Duration initialDelay = Duration.ofSeconds(1)  // 初始重试间隔
Duration maxDelay = Duration.ofSeconds(60)  // 最大重试间隔
Double multiplier = 2.0  // 重试间隔倍数（指数退避）
Integer queueSize = 1000  // 重试队列大小
Integer deadLetterQueueSize = 100  // 死信队列大小
Integer retryThreadPoolSize = 2  // 重试线程池大小
DeadLetterCleanupConfig deadLetterCleanup = new DeadLetterCleanupConfig()  // 死信队列自动清理配置
```

**方法**

```java
static RetryConfig defaultConfig()  // 创建默认配置
static RetryConfig highReliabilityConfig()  // 创建高可靠性配置
static RetryConfig fastFailConfig()  // 创建快速失败配置
Duration calculateDelay(int retryCount)  // 计算重试延迟时间
```

### RetryableMessage

`public record RetryableMessage(String id, String messageType, String channel, Object messageContent, IMessageListener<?> listener, Exception lastException, int retryCount, LocalDateTime nextRetryTime, LocalDateTime firstFailureTime, String subscriptionId)`　可重试消息实体

**构造参数（record 组件）**

```java
String id
String messageType
String channel
Object messageContent
IMessageListener<?> listener
Exception lastException
int retryCount
LocalDateTime nextRetryTime
LocalDateTime firstFailureTime
String subscriptionId
```

**方法**

```java
static RetryableMessage create(String messageType, String channel, Object messageContent, IMessageListener<?> listener, Exception exception, String subscriptionId)  // 创建新的重试消息
RetryableMessage nextRetry(Exception newException, LocalDateTime nextRetryTime)  // 创建下一次重试的消息
boolean canRetry(int maxRetries)  // 检查是否可以重试
boolean isTimeToRetry()  // 检查是否到了重试时间
long getFailureDurationMinutes()  // 获取失败持续时间
```

## 包 `com.mcst.easyfk.db.redis.serializer`

### FastJson2RedisSerializer

`public class FastJson2RedisSerializer implements RedisSerializer<Object>`　注解：`@Slf4j`

**构造器**

```java
FastJson2RedisSerializer()
FastJson2RedisSerializer(Collection<String> trustedPackages)
```

**方法**

```java
byte[] serialize(Object source) throws SerializationException
Object deserialize(byte[] bytes) throws SerializationException
```

### KryoRedisSerializer

`public class KryoRedisSerializer implements RedisSerializer<Object>`　注解：`@Slf4j`

**构造器**

```java
KryoRedisSerializer()
KryoRedisSerializer(Supplier<Kryo> kryoSupplier)
```

**方法**

```java
byte[] serialize(Object value) throws SerializationException
Object deserialize(byte[] bytes) throws SerializationException
```

### SmartRedisSerializer

`public class SmartRedisSerializer implements RedisSerializer<Object>`　智能 Redis 值序列化器

**字段 / 常量**

```java
static final List<String> DEFAULT_TRUSTED_PACKAGES = List.of("com.mcst.", "java.util.", "java.time.", "java.lang.", "java.math.")  // Jackson 多态反序列化默认允许的类名前缀
```

**构造器**

```java
SmartRedisSerializer()
SmartRedisSerializer(RedisValueSerializer valueSerializer)
SmartRedisSerializer(RedisValueSerializer valueSerializer, @Nullable Collection<String> extraTrustedPackages)
```

**方法**

```java
RedisValueSerializer getValueSerializer()
synchronized void setValueSerializer(@Nullable RedisValueSerializer valueSerializer)
byte[] serialize(@Nullable Object value) throws SerializationException
Object deserialize(@Nullable byte[] bytes) throws SerializationException
```

## 包 `com.mcst.easyfk.db.redis.util`

### RedisUtil

`public class RedisUtil`

**方法**

```java
static String wrapKey(KeyArgs redisOptArgs)  // 包装key
static String wrapKey(String namespace, String key)
static SmartRedisSerializer valueSerializer(RedisValueSerializer valueSerializer)
static SmartRedisSerializer valueSerializer(RedisValueSerializer valueSerializer, Collection<String> trustedPackages)
static SmartRedisSerializer valueSerializer(RedisProperties properties)  // 按 RedisProperties 中的序列化方式和信任包创建值序列化器
static RedisTemplate<String, Object> createRedisTemplate(RedisConnectionFactory factory, boolean enableTransactionSupport, RedisValueSerializer valueSerializer)
static RedisTemplate<String, Object> createRedisTemplate(RedisConnectionFactory factory, boolean enableTransactionSupport, RedisProperties properties)
```
