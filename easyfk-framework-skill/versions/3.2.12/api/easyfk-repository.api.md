# easyfk-repository API 签名速查（easyfk 3.2.12）

> 坐标：`com.mcst:easyfk-repository`　源码：`easyfk-base/easyfk-repository`
> 由 `scripts/gen-api.py` 从 16 个源文件自动提取，共 16 个类型、80 个方法/构造器、49 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-repository-skill.md](../modules/easyfk-repository-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 类型索引

- `com.mcst.easyfk.repository.api`：[IBaseRepository](#ibaserepository)
- `com.mcst.easyfk.repository.enums`：[DbTypeEnum](#dbtypeenum)
- `com.mcst.easyfk.repository.persistence.annotation`：[AutoUpdateTime](#autoupdatetime)、[DefaultValueOnSave](#defaultvalueonsave)、[EntityColumn](#entitycolumn)
- `com.mcst.easyfk.repository.persistence.enums`：[DefaultValueType](#defaultvaluetype)
- `com.mcst.easyfk.repository.search`：[KeywordCondition](#keywordcondition)、[RangeCondition](#rangecondition)、[RangeConditionType](#rangeconditiontype)、[SCBuilder](#scbuilder)、[SearchCondition](#searchcondition)
- `com.mcst.easyfk.repository.util`：[ConditionUtil](#conditionutil)、[ModelSetFieldDefaultValueUtil](#modelsetfielddefaultvalueutil)、[RepositoryUtil](#repositoryutil)、[SelectFieldUtil](#selectfieldutil)、[SqlGuardUtil](#sqlguardutil)

## 包 `com.mcst.easyfk.repository.api`

### IBaseRepository

`public interface IBaseRepository<T extends Serializable, PK extends Serializable>`

**方法**

```java
T queryById(PK id, String... selectColumns)  // 根据Id值查询
List<T> queryByCondition(SearchCondition condition)  // 据条件查询数据
T queryOneByCondition(SearchCondition condition)  // 据条件查询数据
T queryOneByField(String field, Object value, String... selectFields)  // 根据字段和值查询一条数据
List<T> queryByField(String field, Object value, String... selectFields)  // 根据字段和值查询列表数据
long countByCondition(SearchCondition condition)  // 根据条件查询总数
PageResult<T> queryByPage(SearchCondition condition)  // 分页查询
boolean exists(SearchCondition condition)  // 根据条件查询记录是否存在
boolean exists(String field, Object value)  // exists
BaseResult<?> insert(T param)  // 保存实体对象
PK insertAndReturnId(T param)  // 保存实体对象并返回主键值
BaseResult<?> insertBatch(List<T> data)  // 批量添加
BaseResult<?> deleteById(PK id)  // 根据StringId 删除数据
BaseResult<?> deleteByCondition(SearchCondition condition)  // 根据条件删除
BaseResult<?> updateBySelective(T param, String... nullProperties)  // 修改部分数据，如果实体对象的某个属性为null则不更新
BaseResult<?> updateEntityByCondition(T newEntity, SearchCondition condition)  // 根据条件部分更新，属性值为null不更新
BaseResult<?> saveOrUpdateBySelective(T entity, String... nullProperties)  // 新增或选择性更新实体对象。 实体对象必须继承BaseModel/BaseMongoEntity/BaseMyBatisEntity其中一个
```

## 包 `com.mcst.easyfk.repository.enums`

### DbTypeEnum

`public enum DbTypeEnum`　Lombok：`@Getter` `@AllArgsConstructor`

**枚举常量**

```java
MYSQL("mysql", "MySql数据库")  // MYSQL
MARIADB("mariadb", "MariaDB数据库")  // MARIADB
ORACLE("oracle", "Oracle11g及以下数据库(12c及以上推荐使用ORACLE_12C)")  // ORACLE
ORACLE_12C("oracle12c", "Oracle12c+数据库")  // oracle12c new pagination
DB2("db2", "DB2数据库")  // DB2
H2("h2", "H2数据库")  // H2
HSQL("hsql", "HSQL数据库")  // HSQL
SQLITE("sqlite", "SQLite数据库")  // SQLITE
POSTGRE_SQL("postgresql", "Postgre数据库")  // POSTGRE
SQL_SERVER2005("sqlserver2005", "SQLServer2005数据库")  // SQLSERVER2005
SQL_SERVER("sqlserver", "SQLServer数据库")  // SQLSERVER
```

**字段 / 常量**

```java
final String db
final String name
```

**方法**

```java
static DbTypeEnum getDbType(String dbType)
```

## 包 `com.mcst.easyfk.repository.persistence.annotation`

### AutoUpdateTime

`public @interface AutoUpdateTime`　注解：`@Retention(RetentionPolicy.RUNTIME)` `@Target({ElementType.FIELD})`　标志实体对象的更新时间字段，用于在更新操作是自动更新修改时间

**方法**

```java
String value() default ""
```

### DefaultValueOnSave

`public @interface DefaultValueOnSave`　注解：`@Retention(RetentionPolicy.RUNTIME)` `@Target({ElementType.FIELD})`　设置实体对象的属性的默认值

**方法**

```java
String value() default ""
String strValue() default ""
int intValue() default 0
DefaultValueType type() default DefaultValueType.STRING
boolean booValue() default false
```

### EntityColumn

`public @interface EntityColumn`　注解：`@Target(ElementType.FIELD)` `@Retention(RetentionPolicy.RUNTIME)`

**方法**

```java
String value() default ""
String comment() default ""
```

## 包 `com.mcst.easyfk.repository.persistence.enums`

### DefaultValueType

`public enum DefaultValueType`

**枚举常量**

```java
STRING  // 字符
INTEGER  // 整数
BOOLEAN  // 布尔
UUID  // UUID
DATE  // 日期
DATETIME  // 日期时间
SNOWFLAKEID  // 雪花算法ID
```

## 包 `com.mcst.easyfk.repository.search`

### KeywordCondition

`public class KeywordCondition implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)`　关键词多字段模糊查询条件（参数化构建，防止 SQL 注入）。

**字段 / 常量**

```java
List<String> fields
String keyword
```

### RangeCondition

`public class RangeCondition implements Serializable`　Lombok：`@Data` `@NoArgsConstructor` `@Accessors(chain = true)`

**字段 / 常量**

```java
String field
Object startValue
Object endValue
RangeConditionType type
```

**构造器**

```java
RangeCondition(String field, Object startValue, RangeConditionType type)  // 如果只有一个区间条件，请设置在startValue中
RangeCondition(String field, Object startValue, Object endValue)  // 如果同时设置了startValue 和 endValue ,默认就是between类型的条件
```

### RangeConditionType

`public enum RangeConditionType`

**枚举常量**

```java
GreaterThan  // 大于
GreaterThanOrEqual  // 大于或等于
Between  // 之间
LessThan  // 小于
LessThanOrEqual  // 小于或等于
Equal  // 等于
```

### SCBuilder

`public record SCBuilder<T>(SearchCondition condition)`　SearchConditionBuilder

**构造参数（record 组件）**

```java
SearchCondition condition
```

**方法**

```java
static <T> SCBuilder<T> builder()
static <T> SCBuilder<T> builder(SearchCondition condition)
SCBuilder<T> exampleAndPage(PageSearch pageSearchInfo, Object example, String... likeFields)
SCBuilder<T> likeConditions(String field, String value)
SCBuilder<T> likeConditions(EFunction<T, ?> field, String value)
SCBuilder<T> likeConditions(Map<String, String> conditions)
SCBuilder<T> orLikeConditions(String field, List<String> values)  // OR 模糊查询：同字段多个值之间使用 OR 拼接（参数化，防注入）
SCBuilder<T> keywordConditions(List<String> fields, String keyword)  // 关键词多字段模糊查询：关键词同时匹配多个字段（OR，参数化，防注入）
SCBuilder<T> equalsConditions(String field, Object value)
SCBuilder<T> notEqualsConditions(String field, Object value)
SCBuilder<T> equalsConditions(Map<String, Object> conditions)
SCBuilder<T> notEqualsConditions(Map<String, Object> conditions)
SCBuilder<T> selectFields(String... fields)
SCBuilder<T> descFields(String... fields)
SCBuilder<T> descFields(Boolean descFirst, String... fields)
SCBuilder<T> ascFields(String... fields)
SCBuilder<T> nullFields(String... fields)
SCBuilder<T> page(PageSearch pageSearchInfo)
SCBuilder<T> customConditionSql(String customConditionSql)
SCBuilder<T> inCondition(String field, List<?> values)
SCBuilder<T> inCondition(String field, Object... values)
@SafeVarargs final SCBuilder<T> example(Object example, EFunction<T, ?>... likeFields)
@SafeVarargs final SCBuilder<T> exampleAndPage(PageSearch pageSearchInfo, Object example, EFunction<T, ?>... likeFields)
SCBuilder<T> equalsConditions(EFunction<T, ?> field, Object value)
SCBuilder<T> notEqualsConditions(EFunction<T, ?> field, Object value)
SCBuilder<T> top(Integer top)
@SafeVarargs final SCBuilder<T> selectFields(EFunction<T, ?>... fields)
@SafeVarargs final SCBuilder<T> descFields(EFunction<T, ?>... fields)
@SafeVarargs final SCBuilder<T> descFields(Boolean descFirst, EFunction<T, ?>... fields)
@SafeVarargs final SCBuilder<T> ascFields(EFunction<T, ?>... fields)
@SafeVarargs final SCBuilder<T> nullFields(EFunction<T, ?>... fields)
@SafeVarargs final SCBuilder<T> groupFields(EFunction<T, ?>... fields)
SCBuilder<T> inCondition(EFunction<T, ?> field, List<?> values)
SCBuilder<T> inCondition(EFunction<T, ?> field, Object... values)
SCBuilder<T> rangeCondition(RangeCondition rangeCondition)
SCBuilder<T> rangeCondition(List<RangeCondition> rangeConditions)
SearchCondition build()
```

### SearchCondition

`public class SearchCondition implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)`

**字段 / 常量**

```java
Integer top
String[] selectFields
String[] descFields
String[] ascFields
String[] groupFields
String[] nullFields
Boolean descFirst  // Desc排序条件是否在前
Map<String, String> likeConditions
Map<String, List<String>> orLikeConditions  // OR 模糊查询条件：字段 -> 多个值（同字段多值之间 OR，参数化）
KeywordCondition keywordCondition  // 关键词多字段模糊查询（参数化）
Map<String, Object> equalsConditions
Map<String, Object> notEqualsConditions
Map<String, List<?>> inConditions
List<RangeCondition> rangeConditions
PageSearch pageSearch
String customConditionSql  // 自定义查询条件Sql，这里的字段请使用sql里定义的字段，是原生的sql语句
Boolean change = Boolean.TRUE
```

## 包 `com.mcst.easyfk.repository.util`

### ConditionUtil

`public class ConditionUtil`　注解：`@Slf4j`　SearchRequest 转成 SearchCondition 对象

**方法**

```java
static <T> SearchCondition conditionByRequest(SearchRequest<T> searchRequest)
```

### ModelSetFieldDefaultValueUtil

`public class ModelSetFieldDefaultValueUtil`　注解：`@Slf4j`　根据DefaultValue注解在进行新增记录时给实体对象赋默认值

**方法**

```java
static void setFieldDefaultValue(Object entity)
```

### RepositoryUtil

`public class RepositoryUtil`　注解：`@SuppressWarnings("all")`

**方法**

```java
static <T extends Serializable, PK extends Serializable> PK insertAndReturnId(T paramObj, IBaseRepository<T, PK> baseRepository)  // 插入对象并返回其主键 此方法用于向数据库插入一个对象，并获取插入后生成的主键值 它首先检查对象的唯一性，以确保数据的完整性
static <T extends Serializable, PK extends Serializable> BaseResult<?> save(ModifyRequest<T> request, IBaseRepository<T, PK> baseRepository, Class<T> tClass)  // 保存操作方法注释 该方法负责处理保存操作，可以处理单个实体或实体列表它首先检查请求中的参数列表是否为空， 如果为空，则检查单个参数对象是否为空，如果两者都为空，则抛出异常如果参数列表不为空，则遍历列表…
static <T extends Serializable, PK extends Serializable> BaseResult<?> save(T parmaObj, IBaseRepository<T, PK> baseRepository, String... nullProperties)  // 保存对象到数据库 如果对象中的主键值存在且不为空，则尝试更新数据库中的对应记录； 否则，将对象作为新记录插入数据库
static <T extends Serializable, PK extends Serializable> BaseResult<?> checkUniqueAndUpdate(T parmaObj, Map<String, Object> idValueMap, IBaseRepository<T, PK> baseRepository, String... nullProperties)  // 检查实体对象的唯一性并更新数据库记录 此方法验证参数对象是否为空，使用主键排除当前记录的唯一性校验，最后直接更新数据库
static <T extends Serializable, PK extends Serializable> void checkUnique(T parma, IBaseRepository<T, PK> baseRepository)  // 检查实体对象的唯一性字段是否已经存在于数据库中 该方法通过反射获取标注了SingleUniqueField和CombUniqueField注解的字段， 并检查这些字段在数据库中的唯一性
static <T extends Serializable, PK extends Serializable> void checkUniqueExcludeSelf(T parma, Map<String, Object> excludeIdMap, IBaseRepository<T, PK> baseRepository)  // 检查实体对象的唯一性字段是否已经存在于数据库中（排除当前记录） 该方法通过反射获取标注了SingleUniqueField和CombUniqueField注解的字段，并检查这些字段在数据库中的唯一性
static <T extends Serializable, PK extends Serializable> BaseResult<?> delete(ModifyRequest<T> param, IBaseRepository<T, PK> baseRepository, Class<T> tClass)
```

### SelectFieldUtil

`public class SelectFieldUtil`

**方法**

```java
static String[] getPrimaryField(Class<?> clazz)
static String[] getPrimaryField(Class<?> clazz, String... otherFields)
```

### SqlGuardUtil

`public final class SqlGuardUtil`　SQL 注入防护工具：列名白名单校验 + 自定义 SQL 片段危险语法检测。

**方法**

```java
static void assertColumn(String field)  // 校验字段/列名合法性，非法直接抛异常。
static String toColumn(String field, boolean convert)  // 校验并转换字段名为数据库列名（驼峰转下划线）。
static boolean isUnsafeSqlFragment(String sql)  // 自定义 SQL 片段是否包含危险语法（分号/注释/DDL/DML 关键字）。
static void assertSafeSqlFragment(String sql)  // 校验自定义 SQL 片段，危险语法直接抛异常。
```
