# easyfk-repository Skill 参考文档

> 所属项目：`easyfk-base`　模块：`easyfk-repository`（单模块）
> 坐标：`com.mcst:easyfk-repository:3.2.12`
> 依据：全部源码（16 个文件）。模块本身没有独立文档，对齐了 `EasyFK框架开发手册.md` §3.2 / §4.1.2 和 `核心模块说明.md` §5.3。
> 为了说明运行时语义，参考了实现层 `orm-mybatis` 的 `BaseMyBatisRepositoryImpl`、`MyBatisPlusWrapperUtil`，以及代码生成器模板 `repository*.java.ftl`。
> 以源码为准；差异见文末「复查记录」。

---

## 1. 模块定位

数据访问抽象层，与具体 ORM 无关。包含以下内容：

- `IBaseRepository<T, PK>`：通用 CRUD 接口，**T 是 DTO，不是 PO**；
- `SearchCondition` 与链式构建器 `SCBuilder<T>`：统一的查询条件模型；
- `ConditionUtil`：把前端传入的 `SearchRequest<T>` 转换为 `SearchCondition`；
- `RepositoryUtil`：保存或更新、唯一性校验、按请求删除；
- 持久化注解 `@AutoUpdateTime`、`@DefaultValueOnSave`、`@EntityColumn`，以及 `SqlGuardUtil`（列名白名单和 SQL 片段校验）。

依赖：`api project(':easyfk-core')`。主键、唯一性、区间等注解（`@PrimaryKey`、`@SingleUniqueField`、`@CombUniqueField`、`@PrimaryField`、`@BetweenStart/End`、`@AssistConditionField`）都定义在 core 中。

实现层位于 `easyfk-component`：

| 实现 | 基类 |
|---|---|
| orm-mybatis | `BaseMyBatisRepositoryImpl<M, T, P, PK>` |
| orm-flex | `BaseFlexRepositoryImpl<M, T, P, PK>` |
| orm-hibernate | `BaseHibernateRepositoryImpl<R, T, P, PK>` |
| db-mongo | `BaseMongoRepositoryImpl` |

本模块**没有自动配置**。

---

## 2. 定义 Repository（以生成器模板为准）

```java
// 接口：放在 repository 包
import com.mcst.easyfk.repository.api.IBaseRepository;

public interface IProductRepository extends IBaseRepository<ProductDto, String> {
}

// 实现：放在 repository.impl 包（MyBatis-Plus）
@Repository
public class ProductRepositoryImpl
        extends BaseMyBatisRepositoryImpl<ProductMapper, ProductDto, Product, String>
        implements IProductRepository {
}
```

泛型的顺序是 `<Mapper, Dto, Po, PK>`：

- 实现类通过反射读取第 2 个泛型参数作为 DTO 类型，因此**必须用一个具体子类直接继承**，并写全泛型；
- 实现层负责 PO 与 DTO 之间的互转（`TransformUtil`）。

---

## 3. IBaseRepository 方法

| 方法 | 说明 |
|---|---|
| `queryById(id, selectColumns...)` | 不存在时返回 null |
| `queryByCondition(c)` | 设置了 `top` 时转为第 1 页、每页 top 条，且不统计总数 |
| `queryOneByCondition(c)` / `queryOneByField(f, v, select...)` | 取第一条，**不会限制查询条数**；数据较多时应加 `top(1)` |
| `queryByField(f, v, select...)` | f 是 PO 的字段名 |
| `countByCondition(c)` / `exists(c)` / `exists(f, v)` | |
| `queryByPage(c)` | 需要设置 `pageSearch`，返回 `PageResult<T>`（total 和 rows） |
| `insert(t)` / `insertAndReturnId(t)` / `insertBatch(list)` | |
| `deleteById(id)` / `deleteByCondition(c)` | |
| `updateBySelective(t, nullProperties...)` | 按主键只更新非空字段；`nullProperties` 中的字段会被显式更新为 null |
| `updateEntityByCondition(t, c)` | 按条件批量更新 |
| `saveOrUpdateBySelective(t, nullProperties...)` | |

查询没有显式排序时，如果实体有 `insertTime` 字段，mybatis 实现会默认追加 `ORDER BY insert_time DESC`。

---

## 4. SCBuilder 与 SearchCondition

`SCBuilder<T>` 是一个 record。可以从 `SCBuilder.<UserDto>builder()` 或 `builder(existingCondition)` 开始，链式调用后 `build()`。大多数方法都有 `String` 字段名和 `EFunction<T,?>` 方法引用（`UserDto::getName`）两种重载。

| 方法 | 生成的条件 |
|---|---|
| `equalsConditions(f, v)` / `(Map)` | `=` |
| `notEqualsConditions(f, v)` / `(Map)` | `<>` |
| `likeConditions(f, v)` / `(Map)` | `LIKE %v%` |
| `orLikeConditions(f, List<String>)` | `(f LIKE a OR f LIKE b)` |
| `keywordConditions(List<f>, kw)` | `(f1 LIKE kw OR f2 LIKE kw …)` |
| `inCondition(f, List / varargs)` | `IN`，对同一字段多次调用时会合并并去重 |
| `rangeCondition(RangeCondition / List)` | `>`、`>=`、`<`、`<=`、`BETWEEN`、`=`，由 `RangeConditionType` 决定 |
| `nullFields(f...)` | `IS NULL` |
| `selectFields` / `descFields` / `ascFields` / `descFields(descFirst, …)` / `groupFields` | 查询列、排序、分组；`groupFields` 只有 EFunction 版本 |
| `page(PageSearch)` / `top(n)` | 分页 / 前 n 条 |
| `customConditionSql(sql)` | 原样拼接的 SQL 片段，多次调用时用 `AND` 连接 |
| `example(obj, likeFields...)` / `exampleAndPage(page, obj, likeFields...)` | 把对象中非空的字段转换为等值条件；`likeFields` 中列出的字段改为 LIKE |

```java
SearchCondition c = SCBuilder.<UserDto>builder()
        .equalsConditions(UserDto::getStatus, 1)
        .likeConditions(UserDto::getUserName, keyword)
        .inCondition(UserDto::getDeptId, deptIds)
        .rangeCondition(new RangeCondition("createTime", start, end))   // Between
        .descFields(UserDto::getCreateTime)
        .page(new PageSearch(pageNo, pageSize))
        .build();
PageResult<UserDto> page = userRepository.queryByPage(c);
```

使用时需要注意的语义：

- **字段名使用 Java 属性名（驼峰）**。`SearchCondition.change` 默认为 true，实现层会把它转换为下划线列名。
- **列名白名单**：`String` 字段名重载会经过 `SqlGuardUtil.assertColumn` 校验，规则为 `^[A-Za-z][A-Za-z0-9_.]{0,127}$`，不合法时抛 `IllegalArgumentException`。但 `equalsConditions(Map)`、`notEqualsConditions(Map)` **不做校验**，不要把前端传入的 Map 直接交给它们。
- `SCBuilder` 在调用 like / orLike / in / notEquals / range 时，会移除**此前**已加入的同字段 equals 条件；之后再加入的 equals（例如 `example()` 放在最后）不会被移除。ORM 实现层已不再剔除（三个 ORM 都按 AND 叠加，见 orm skill 复查记录 #3）。
- `example()` 的规则：
  - 跳过以下字段：
    - null、空白字符串、空集合；
    - `serialVersionUID`、`log`；
    - 已经设置了 in 或 notEq 条件的字段；
    - 标注了 `@AssistConditionField`、`@BetweenStart`、`@BetweenEnd` 的字段。
  - **`0` 和 `false` 不算空**，会生成等值条件。因此 DTO 字段必须使用包装类型。
  - 类型为 `PageSearch` 的字段会被当作分页参数。
- `customConditionSql` 在实现层执行前会经过 `SqlGuardUtil.assertSafeSqlFragment`，拒绝 `; -- /* */` 和 DDL/DML 关键字。但它仍是**原样拼接**，只能用于可信的内部常量，**不能拼接用户输入**。
- `likeConditions(Map)` 和 `equalsConditions(Map)` 在 condition 中原本没有对应 Map 时，会直接引用传入的 Map 对象，之后对 Map 的修改会影响条件。

---

## 5. ConditionUtil：把 SearchRequest 转换为 SearchCondition

`SearchCondition c = ConditionUtil.conditionByRequest(searchRequest);`

| SearchRequest 字段 | 转换结果 |
|---|---|
| `pageSearch` / `selectFields` / `nullFields` | 原样设置 |
| `parmaObj` 继承自 `BasicParam` | `page`+`limit` 转为分页（totalCount 默认为 true）；`top`；`descFields`/`ascFields` 按逗号拆分 |
| `inParams` | IN |
| `parmaObj` 上的 `@BetweenStart(field)` / `@BetweenEnd(field)` | **两端都有值时**才生成 BETWEEN |
| `gThanFields` / `gThanOrEqualFields` / `lThanFields` / `lThanOrEqualFields` | 取 parmaObj 中对应字段的值，生成范围条件，**随后把 parmaObj 中的该字段置为 null**（避免再生成等值条件） |
| `likeFields` | 有值时生成 LIKE；值中含逗号时拆成 orLike；没有值的字段与 `BasicParam.searchKeyWord` 组合成关键词多字段 LIKE |
| `notFields` | 取 parmaObj 中的值，生成 `<>` |
| 最后 | 用 `example(parmaObj)` 把剩余非空字段转为等值条件 |

注意：
- 这个工具**会修改传入的 parmaObj**（范围字段会被置为 null）。
- 内部异常只调用 `printStackTrace()`，不会抛出。

---

## 6. RepositoryUtil

| 方法 | 行为 |
|---|---|
| `save(T, repo, nullProperties...)` | 有 `@PrimaryKey` 值且记录存在时，校验唯一性（排除自己）后执行 `updateBySelective`；否则校验唯一性后 `insert` |
| `save(ModifyRequest<T>, repo, Class<T>)` | 对 `paramList` 或 `parmaObj` 逐条调用 save；两者都为空时抛 RuntimeException |
| `insertAndReturnId(T, repo)` | 校验唯一性后插入，并返回主键 |
| `checkUnique` / `checkUniqueExcludeSelf` | `@SingleUniqueField` 校验单字段唯一；`@CombUniqueField(combinationField=…)` 校验组合唯一（组合字段的值为空时抛 BusinessException）；重复时抛 `BusinessException(repetitionMsg)` |
| `delete(ModifyRequest<T>, repo, Class<T>)` | parmaObj 带主键时，按 example 条件删除；否则按 `idList` 或 `paramList` 中的主键执行 `IN` 删除；都没有时返回失败结果，`msg` 为 "删除失败" |

唯一性校验是先 `exists` 再写入，**不是原子操作**，数据库层面必须同时建立唯一索引。

---

## 7. 持久化注解与默认值

- `@DefaultValueOnSave(type=…, strValue/intValue/booValue)`：由 `ModelSetFieldDefaultValueUtil.setFieldDefaultValue(entity)` 在字段为空时填充默认值。
  - 可选类型：`STRING`、`INTEGER`、`BOOLEAN`、`UUID`（32 位简单 UUID）、`DATE`（`LocalDate`）、`DATETIME`（`LocalDateTime`）、`SNOWFLAKEID`（long）。
  - **字段类型必须与生成的值类型匹配**，否则赋值失败时只调用 `printStackTrace`，字段保持为空。
  - 注解的 `value()` 属性没有被使用。
- `@AutoUpdateTime`：由 orm 实现层（MybatisPlusUtil、FlexUtil、HibernateUtil）在更新时自动设置时间，`BaseMyBatisPlusEntity` 的更新时间字段已标注此注解。
- `@EntityColumn(value, comment)`：只被代码生成器使用，运行时没有任何作用。
- `DbTypeEnum.getDbType(String)`：按 `db` 值（不区分大小写）查找，找不到时返回 null。
- `SelectFieldUtil.getPrimaryField(Class, others...)`：返回标注了 `@PrimaryField` 的字段名，并追加 others。

---

## 8. 生成代码时的规则

**应该这样做：**

- 按照「接口 `IXxxRepository extends IBaseRepository<XxxDto, PK>` + 实现 `XxxRepositoryImpl extends BaseMyBatisRepositoryImpl<XxxMapper, XxxDto, Xxx, PK>`」编写；建议直接使用代码生成器。
- 查询条件优先使用 `EFunction` 方法引用重载（`UserDto::getName`），避免手写字符串。
- DTO 与查询参数对象的字段使用包装类型（`Integer`、`Boolean`、`Long`）。
- `queryOne*` 在可能命中多条记录时，加 `top(1)` 或使用唯一条件。
- 唯一性约束同时依赖 `@SingleUniqueField` / `@CombUniqueField` 和数据库唯一索引。
- 批量删除和更新必须带明确的条件（主键 IN 或业务键）。

**不要这样做：**

- 不要在 `customConditionSql` 中拼接任何用户输入。
- 不要把前端传入的 Map 交给 `equalsConditions(Map)` / `notEqualsConditions(Map)`，这两个方法不校验列名。
- 不要用空的 `SearchCondition` 调用 `deleteByCondition` / `updateEntityByCondition`。mybatis 实现依赖 `BlockAttackInnerInterceptor` 拦截，其他实现需要另行确认。
- 不要沿用框架手册 §3.2.2 中的 API，例如 `addLikeCondition`、`addEqCondition`、`setPageNo`、`setOrderBy`、`queryBySc`、`queryPageBySc`，这些方法都不存在。
- 不要把 Repository 定义成 Spring Data 风格、仅凭方法名推导查询的接口（例如 `findByUsername`）。`IBaseRepository` 没有这种能力。

---

## 9. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | 框架手册 §3.2.2 / §4.1.2 | `import com.mcst.easyfk.repository.IBaseRepository` | 实际包是 `com.mcst.easyfk.repository.api` |
| 2 | 框架手册 §3.2.2 | `repository.builder.SCBuilder`、`repository.condition.SearchCondition` | 两者都在 `com.mcst.easyfk.repository.search` 包 |
| 3 | 框架手册 §3.2.2 | `addLikeCondition`、`addEqCondition`、`addRangeCondition(f, BETWEEN, s, e)`、`setPageNo`、`setPageSize`、`setOrderBy("x DESC")` | 这些方法都不存在。实际方法为 `likeConditions`、`equalsConditions`、`rangeCondition(new RangeCondition(f, s, e))`、`page(new PageSearch(p, s))`、`descFields`；枚举值为 `Between`，不是 `BETWEEN` |
| 4 | 框架手册 §3.2.2 | `queryBySc` / `queryPageBySc` | 实际方法为 `queryByCondition` / `queryByPage` |
| 5 | 框架手册 §3.2.2 / §4.1.2 | `@Repository interface UserRepository extends IBaseRepository<UserEntity, Long>`，并带有 `findByUsername` | T 应为 DTO；必须有实现类继承 orm 基类；不支持方法名推导查询 |
| 6 | 核心模块说明 §5.3 | 未列出 | 缺少 `SqlGuardUtil`、`@EntityColumn`、`orLikeConditions`、`keywordConditions` |
| 7 | `DbTypeEnum.ORACLE` 的描述 | "高版本推荐使用 ORACLE_NEW" | 枚举中没有 `ORACLE_NEW`，对应的是 `ORACLE_12C` **已修复**：描述改为"12c及以上推荐使用ORACLE_12C" |
| 8 | 源码疑似缺陷 | `ConditionUtil.doLike` 在值含逗号时生成 orLike，但最后的 `example(parmaObj)` 会把原值（如 `"a,b"`）再作为等值条件加回 | mybatis 的 `replaceEqFields` 不剔除 orLike 字段，最终 SQL 为 `f='a,b' AND (f LIKE a OR f LIKE b)`，通常查不到数据 |
| 9 | 源码疑似缺陷 | `equalsConditions(Map)` / `notEqualsConditions(Map)` | 没有调用 `SqlGuardUtil.assertColumn`，与其他重载不一致 |
| 10 | 源码疑似缺陷 | `SelectFieldUtil` 的静态缓存 | 使用普通 `HashMap`，并发首次访问时存在线程安全问题 |
| 11 | 源码 | `ConditionUtil` / `ModelSetFieldDefaultValueUtil` / `SCBuilder.doExample` | 异常只调用 `printStackTrace()`，静默失败 |
| 12 | 源码 | `RepositoryUtil`、orm 三个 `*Util` 中的 `BRBuilder.failResult("错误信息")` | 单参重载是 `failResult(T data)`，错误信息被放进 `data`，`msg` 为空，前端拿不到失败原因 **已修复**：8 处改为 `failResult(msg, null)`（与 `BaseMongoRepositoryImpl` 一致） |
