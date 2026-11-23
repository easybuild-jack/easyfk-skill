# component-orm Skill 参考文档

> 所属项目：`easyfk-component`　子模块：`orm-mybatis`、`orm-flex`、`orm-hibernate`、`orm-sharding`
> 坐标：`com.mcst:orm-mybatis` / `orm-flex` / `orm-hibernate` / `orm-sharding`（3.5.16）
> 依据：四个子模块的全部源码与 `build.gradle`，另外核对了 MyBatis-Flex 1.11.8 的 `FlexGlobalConfig` 源码和 ShardingSphere 5.5.3 的驱动与规则文件格式；对齐了各子模块的 `开发手册.md` 和 `技术特点.md`。
> 以源码为准；差异见文末「复查记录」。

---

## 1. 选型与共性

| 子模块 | 底层框架 | Repository 基类 | 实体基类 | 自动配置 |
|---|---|---|---|---|
| `orm-mybatis`（**推荐，功能最完整**） | MyBatis-Plus 3.5.18.1 | `BaseMyBatisRepositoryImpl<M extends BaseMapper<P>, T(DTO), P extends Model<?>, PK>`，同时继承 `ServiceImpl<M,P>` | `BaseMyBatisPlusEntity<T>`（含 insertTime、lastUpdateTime、deleted）/ `BaseMyBatisPlusSimpleEntity<T>` | `MybatisPlusConfigure` |
| `orm-flex` | MyBatis-Flex 1.11.8 | `BaseFlexRepositoryImpl<M extends BaseMapper<P>, T, P extends Model<?>, PK>` | `BaseFlexEntity<T>` / `BaseFlexSimpleEntity<T>` | `FlexConfigure` |
| `orm-hibernate` | Spring Data JPA + Hibernate | `BaseHibernateRepositoryImpl<R extends JpaRepository<P,PK> & JpaSpecificationExecutor<P>, T, P, PK>` | `BaseHibernateEntity` / `BaseHibernateSimpleEntity`（`@MappedSuperclass`） | `HibernateConfigure` |
| `orm-sharding` | ShardingSphere-JDBC **5.5.3**（`ShardingSphereDriver` 方式，非 starter） | 只提供依赖，没有代码 | — | 由 ShardingSphere 驱动自身完成 |

共性：
- 三个 ORM 都实现了 `IBaseRepository<T, PK>`（接口语义见 [easyfk-repository](easyfk-repository-skill.md)）。所有 orm 子模块都会传递引入 `easyfk-core`、`easyfk-repository`、`service-base`。
- DTO 和 PO 之间用 `TransformUtil` 做同名属性拷贝；泛型的第 2 个参数是 DTO，第 3 个参数是 PO。**DTO 里必须有主键字段，并且和 PO 同名**。
- 三者共同的查询语义：
  - 等值条件中，值为空（`EmptyUtil.isEmpty`，包括 `""`）的会被**跳过**；
  - 同一个字段同时出现在 equals 和 notEquals、in、like、range 中时，**所有条件按 AND 叠加**（equals 不会被丢弃）；
  - 区间条件中，`GreaterThan`/`GreaterThanOrEqual`/`Equal` 优先读 **startValue**、为空时读 endValue；`LessThan`/`LessThanOrEqual` 优先读 **endValue**、为空时读 startValue；Between 只有一端有值时，退化为 `>=` 或 `<=`；字符串形式的日期或时间会自动转换为 LocalDate 或 LocalDateTime；
  - `orLikeConditions`（同字段多值 OR）和 `keywordCondition`（多字段 OR）三个 ORM 都支持，均为参数化 LIKE；
  - 没有指定排序、并且实体有 `insertTime` 字段时，默认按 insert_time 降序排列；
  - 分页默认第 1 页、每页 10 条（页码从 1 开始）；设置了 `top` 时，等价于查第 1 页、每页 top 条，并且不查总数。
- 只能启用一个 ORM 子模块。

**Mapper 和 Repository 扫描是自动的**（与是否使用 `ApplicationStarter` 无关）：
- mybatis/flex：自动配置 `MybatisPlusMapperScanConfigure` / `FlexMapperScanConfigure`（排在 MyBatis-Plus/Flex 官方自动配置之前）注册 `MapperScannerConfigurer`，扫描**应用启动类所在包（`AutoConfigurationPackages`）+ `com.mcst.**.persistence.mapper`**，只注册继承了对应 `BaseMapper` 或标注了 `@Mapper` 的接口。
- hibernate：`HibernateScanConfigure` 把实体扫描设为"应用包 + `com.mcst.**.persistence`"，Repository 扫描设为"应用包 + `com.mcst.**.persistence.repository`"（遵守 `spring.data.jpa.repositories.enabled`）。
- 业务方自己写了 `@MapperScan`（或任何 `MapperScannerConfigurer`/`MapperFactoryBean`）、`@EnableJpaRepositories`、`@EntityScan` 时，对应的自动扫描**整体让位**，此时框架包需要业务方自己包含进去。
- `ApplicationStarter.run(...)` 仍可使用，但 `*ServiceScanner` 已经不带任何扫描注解，等价于 `SpringApplication.run`。

---

## 2. orm-mybatis

### 2.1 自动配置（`MybatisPlusConfigure`，无开关）

- `MybatisPlusInterceptor`（`@ConditionalOnMissingBean`），包含两个拦截器：
  - `BlockAttackInnerInterceptor`：拒绝没有 WHERE 条件的 UPDATE/DELETE；
  - `PaginationInnerInterceptor(dbType)`：dbType 是**启动时拿一个连接读取 JDBC URL 来识别的**，识别失败时回退为 MYSQL。注意：DataSource 必须存在，启动时还会真实连一次数据库。
- `AutoSetValueHandler`（`MetaObjectHandler`，`@ConditionalOnMissingBean`），只填充值为 null 的字段：
  - insert 时：`createTime`、`insertTime`、`lastUpdateTime`、`modifyTime`、`updateTime` 填当前时间，`version` 填 1L，`deleted` 填 0；
  - update 时：`modifyTime`、`updateTime`、`lastUpdateTime` 填当前时间；
  - 前提是这些字段标注了 `@TableField(fill = …)`。基类的 insertTime、lastUpdateTime、deleted 已经标注；自己新增的字段需要自己加注解。

### 2.2 实体、Mapper、Repository

```java
@Data @EqualsAndHashCode(callSuper = true)
@TableName("t_order")
public class OrderPO extends BaseMyBatisPlusEntity<OrderPO> {
    @TableId(type = IdType.AUTO)        // queryById、updateBySelective(nullProps) 的主键列名取自 MP TableInfo（@TableId(value) 生效）
    private Long id;
    private String orderNo;
    private Integer status;
}   // 继承的字段：insertTime(INSERT 时填充)、lastUpdateTime(@AutoUpdateTime，INSERT_UPDATE 时填充)、deleted(@TableLogic，select=false)

public interface OrderMapper extends BaseMapper<OrderPO> {}

@Repository
public class OrderRepository extends BaseMyBatisRepositoryImpl<OrderMapper, OrderDTO, OrderPO, Long> {}

@SpringBootApplication                  // 启动类所在包及子包下的 Mapper 会被自动扫描；自己写 @MapperScan 会关闭自动扫描
public class App { public static void main(String[] a) { SpringApplication.run(App.class, a); } }
```

> **3.5.16 起的包名变化**：MyBatis-Plus 3.5.18 把 ActiveRecord `Model` 与 `ServiceImpl` 从 `com.baomidou.mybatisplus.extension.*` 迁到 `com.baomidou.mybatisplus.spring.*`。框架的 `BaseMyBatisPlusEntity` / `BaseMyBatisPlusSimpleEntity` / `BaseMyBatisRepositoryImpl` 已同步改 import，业务代码只要**直接 import 过** `extension.activerecord.Model` 或 `extension.service.impl.ServiceImpl` 就要跟着改，否则编译不过。业务实体继承 `BaseMyBatisPlusEntity` 的无需改。

### 2.3 方法行为要点

| 方法 | 行为 |
|---|---|
| `queryById(id, cols...)` | 按主键列（MP `TableInfo.keyColumn`，其次 `@TableId(value)`）查询；id 为空返回 null；实体没有主键时**抛 BusinessException** |
| `queryByField(field, value, cols...)` | 反射创建一个实体并设置该字段的值，再用 `new QueryWrapper<>(entity)` 查询；如果实体有基本类型字段，其默认值也会成为查询条件 |
| `exists(field, value)` | 通过 `resolveColumn` 把属性名映射为实体真实列名；属性不存在时抛 BusinessException |
| `countByCondition`、`exists(cond)`、`deleteByCondition`、`updateEntityByCondition` | 只使用条件部分，不带 order、select、group |
| `deleteByCondition` / `updateEntityByCondition` 的条件为空时 | 被 BlockAttack 拦截，**抛异常**（不会删除或更新全表） |
| `insert` | `ServiceImpl.save`；`insertBatch` 使用 `saveBatch`（默认每批 1000） |
| `insertAndReturnId` | insert 后读取 `@TableId` 字段的值 |
| `deleteById(id)` | 支持单个 id、`"1,2,3"` 字符串、Collection；有 `@TableLogic` 时为逻辑删除 |
| `updateBySelective(dto)` | 走 `updateById`，忽略 null 字段 |
| `updateBySelective(dto, "remark", …)` | 把第一个 `@AutoUpdateTime` 字段设为当前时间，把列出的、值为空的属性（经 `resolveColumn` 校验并取真实列名）`SET col = NULL`，然后按主键列更新；实体没有主键或主键值为空时**返回失败结果**"更新数据缺少主键" |
| `saveOrUpdateBySelective` | 先看 `@PrimaryKey`（core 注解）是否有值，没有再看 `@TableId`；按主键 count 判断记录是否存在，存在则 updateBySelective，否则 insert |

条件构建：
- 列名经过 `SqlGuardUtil.toColumn` 白名单校验的有：equals、notEquals、nullFields、like、in、range、orLike、keyword、排序、分组、select。
- `customConditionSql` 先经过 `assertSafeSqlFragment` 检查，然后用 `wrapper.apply` 拼接。

原生能力：Repository 本身就是 `IService<P>`，可以直接用 `lambdaQuery()`、`lambdaUpdate()`、`saveBatch(list, n)`。

---

## 3. orm-flex

### 3.1 自动配置（`FlexConfigure`）

- 全局设置逻辑删除列 `deleted`（正常值 0，删除值 1），**对所有包含 deleted 列的表生效**。
- 注册 `AutoSetValueHandler` 为插入/更新监听器（以 `Object.class` 登记，对所有实体生效），填充 createTime、version、deleted 等字段（只填 null 字段）。基类上的 `@Column(onInsertValue = "now()", onUpdateValue = "now()")` 仍然有效。
- SQL 审计通过 `easyfk.orm.flex.sql-audit=true` 开启（默认关闭），审计日志以 INFO 输出完整 SQL 和耗时。
- 没有分页方言识别，使用 Flex 默认的 MySQL 方言。
- 没有 BlockAttack 拦截器，但 Repository 层的 `deleteByCondition` / `updateEntityByCondition` 在 SearchCondition 中没有任何有效过滤条件时**直接抛 IllegalArgumentException**；`updateBySelective(dto, nullProps…)` 主键值为空时返回失败结果，不会退化为全表更新。
- AutoConfiguration.imports 中是 `FlexMapperScanConfigure`（Mapper 自动扫描）和 `FlexConfigure`。

### 3.2 使用

```java
@Data @EqualsAndHashCode(callSuper = true)
@Table("t_order")
public class OrderPO extends BaseFlexEntity<OrderPO> {
    @Id(keyType = KeyType.Auto)   // 找不到 @Id 时会回退到 core 的 @PrimaryKey
    private Long id;
    private String orderNo;
}
public interface OrderMapper extends BaseMapper<OrderPO> {}            // com.mybatisflex.core.BaseMapper
@Repository
public class OrderRepository extends BaseFlexRepositoryImpl<OrderMapper, OrderDTO, OrderPO, Long> {}   // mapper 通过 @Autowired 注入
```

### 3.3 与 orm-mybatis 的差异

- 与 orm-mybatis 一样使用 SqlGuardUtil：equals、notEquals、nullFields、like、orLike、keyword、in、range、排序、分组、select 的列名都经过 `toColumn` 白名单校验；`customConditionSql` 先 `assertSafeSqlFragment` 再 `wrapper.and(sql)`。
- 支持 `orLikeConditions`（同字段多值 OR）和 `keywordCondition`（多字段 OR），参数化 LIKE。
- `queryByField` 和 `exists(field, value)` 用的是 `QueryWrapper.eq(列, 值)`（列名经过白名单校验），不是 example 查询。
- `updateBySelective(dto, nullProps…)`：用 `UpdateEntity.ofNotNull` 构造更新对象，把指定的属性置为 null，再按 `@Id` 或 `@PrimaryKey` 执行 `updateByQuery`。
- 分页参数 `totalCount=false` 时，会用"页码 × 每页条数"作为伪总数来跳过 count 查询，返回的 total 为 0。

---

## 4. orm-hibernate

### 4.1 使用

```java
@Entity @Table(name = "t_order")
@Data @EqualsAndHashCode(callSuper = true)
public class OrderPO extends BaseHibernateEntity {      // 带 @EntityListeners(AutoSetValueHandler)
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String orderNo;
}
public interface OrderJpaRepository extends JpaRepository<OrderPO, Long>, JpaSpecificationExecutor<OrderPO> {}

@Repository
public class OrderRepository extends BaseHibernateRepositoryImpl<OrderJpaRepository, OrderDTO, OrderPO, Long> {}
```

- 类级别 `@Transactional(rollbackFor = Exception.class)`，查询方法为 `readOnly`。
- **字段名使用 JPA 属性名（驼峰）**；`change` 参数不起作用；逻辑删除过滤值写死为 0。
- `@PrePersist` 填充 `createTime`、`insertTime`、`lastUpdateTime`、`modifyTime`、`updateTime`、`version=1L`、`deleted=0`（只填 null 的字段）。`@PreUpdate` 对 `lastUpdateTime`、`modifyTime`、`updateTime` **总是覆盖为当前时间**。

### 4.2 方法行为要点（与另外两个 ORM 的差异较大）

| 方法 | 行为 |
|---|---|
| `queryById(id)` | `em.find`，结果为逻辑删除数据（`deleted != 0`）时返回 null |
| `queryById(id, cols...)` | cols 非空时用 Criteria Tuple 投影只查询这些属性（加 `deleted = 0`），结果填充到新建的非托管实体再转 DTO，未选属性为 null |
| `queryByField` / `exists(field,v)` | 字段等值查询，并加上 `deleted = 0`；`queryByField` 的 selectFields 非空时同样走 Tuple 投影 |
| `queryByCondition` / `queryByPage` | 使用 Specification 并加上 `deleted = 0`。`selectFields` 走 Tuple 投影；`orLike`（同字段多值 OR）、`keyword`（多字段 OR）用 Criteria `LIKE` 实现；`customConditionSql` **抛 UnsupportedOperationException**。`totalCount=false` 时**不执行 count**（直接 Criteria 查询 + offset/limit），total 为 0 |
| `countByCondition` / `exists(cond)` | 加上 `deleted = 0` |
| `insert` / `insertBatch` | `em.persist`，批量时逐条 persist 后统一 flush；`insertAndReturnId` 会立即 flush |
| `deleteById` | 有 `deleted` 字段时执行批量 `UPDATE deleted=1`，否则单条用 `em.remove`、批量用 CriteriaDelete |
| `deleteByCondition` | 条件为空时**抛 BusinessException**，不会删除整张表 |
| `updateBySelective(dto, nullProps…)` | 执行 CriteriaUpdate 批量更新：跳过主键和 `serialVersionUID`；`@AutoUpdateTime` 字段以及 `lastUpdateTime`/`modifyTime`/`updateTime`（LocalDateTime）设为当前时间；nullProps 中的字段强制置 null，其余字段非空才 set（空字符串也会被跳过）。**这条路径绕过 `@PreUpdate`，也不会更新持久化上下文** |
| `updateEntityByCondition` | 所有非 null 字段都会 set，更新时间字段同上；条件为空时**抛 BusinessException**；附加 `deleted = 0` |

---

## 5. orm-sharding

**3.5.16 起换了接入方式**：从 `shardingsphere-jdbc-core-spring-boot-starter:5.2.1` 迁到 **`shardingsphere-jdbc:5.5.3` 驱动 + YAML 规则文件**。原因是该 starter 自 5.3.0 起停止发布，`spring.shardingsphere.*` 配置前缀随之废弃（5.2.1 又只支持 snakeyaml 1.x，与 Boot 3.5 的 snakeyaml 2.x 不兼容）。

- 模块只做依赖聚合，传递引入 15 个 5.5.3 构件：`shardingsphere-jdbc`、`infra-url-classpath`/`infra-url-absolutepath`（两种 URL 前缀）、`infra-data-source-pool-hikari`、`authority-simple`、`standalone-mode-repository-memory`/`-jdbc`、`jdbc-dialect-mysql`/`-postgresql`，以及 `sharding-core`/`broadcast-core`/`readwrite-splitting-core`/`encrypt-core`/`mask-core`/`shadow-core` 六个功能模块。
- 接入方式：把 Boot 的数据源指向驱动，规则文件放 classpath（或文件系统）：

  ```yaml
  spring:
    datasource:
      driver-class-name: org.apache.shardingsphere.driver.ShardingSphereDriver
      url: jdbc:shardingsphere:classpath:sharding.yaml   # 或 absolutepath:/path/to/sharding.yaml
  ```

- 规则文件是 ShardingSphere **原生 YAML**（驼峰，如 `actualDataNodes`、`shardingColumn`），顶层为 `databaseName` / `mode` / `dataSources` / `rules` / `props`；`rules` 用 `!SHARDING`、`!READWRITE_SPLITTING`、`!ENCRYPT`、`!BROADCAST`、`!SINGLE` 等标签声明。**与旧版 `spring.shardingsphere.*` 的短横线写法完全不通用，升级必须整体迁移**。
- 行表达式推荐 `${...}`，旧写法 `$->{...}` 仍兼容；分片涉及的物理表必须在启动前建好（启动时加载真实表元数据）。
- 5.4 起**未分片的单表不再自动加载**：读写分离、加密场景下的普通表必须用 `!SINGLE` 声明（常用 `tables: ["*.*"]`），否则会路由到错误数据源、加密列不改写。广播表也从 `!SHARDING.broadcastTables` 独立成 `!BROADCAST` 规则。
- 自动分片算法（`MOD`、`HASH_MOD`、`VOLUME_RANGE`、`BOUNDARY_RANGE`、`AUTO_INTERVAL`）**只能用于 `autoTables`**，配在 `tables`（带 `actualDataNodes`）上启动即报 `can not use auto sharding algorithm`。
- 方言与可选插件可插拔：Oracle / SQLServer 等需自行引入 `shardingsphere-jdbc-dialect-xxx`；ZooKeeper/etcd 集群模式、XA（Atomikos/Narayana）、Seata AT 同理。内置加密只有 `AES` / `MD5`，内置主键只有 `SNOWFLAKE` / `UUID`（SM3/SM4、NanoID、CosId 已移到 Plugin 仓库）。
- 主键：若希望由 ShardingSphere 的 `keyGenerateStrategy` 生成主键，INSERT 语句中**不能包含主键列**。MyBatis-Plus 的 `IdType.ASSIGN_ID` 是 MP 自己用雪花算法生成，与 ShardingSphere 无关。
- 分片表的条件要带上分片键。框架的默认排序（insert_time desc）加分页会在所有分片上执行，然后在内存里归并。

---

## 6. 生成代码时的规则

**Do**
- 默认选 orm-mybatis。实体继承 `BaseMyBatisPlusEntity<自身>`，主键用 `@TableId`，并且**字段名转成下划线后要等于列名**；DTO 中带同名的主键字段。
- Mapper/Repository 放在启动类所在包（或 `com.mcst.**.persistence.mapper`）下即可被自动扫描；需要自定义扫描范围时才写 `@MapperScan` / `@EnableJpaRepositories` / `@EntityScan`，并且要自己把框架包也写进去。
- 使用 `SearchCondition` 时，同一字段的多种条件会 AND 叠加；LessThan 类型的值放在 endValue（放在 startValue 也兼容）；字段名用驼峰。
- `customConditionSql` 只拼接代码中的常量片段（mybatis/flex 会做危险语法检测，但不能防止逻辑注入）。

**Don't**
- 不要在 hibernate 下使用 `customConditionSql`（会抛 UnsupportedOperationException），改用其它条件类型或自定义 JPQL。
- 不要用空条件调用 `deleteByCondition` / `updateEntityByCondition`（三个 ORM 都会抛异常）。
- 不要把前端传入的字段名当作可信输入；mybatis/flex 会做白名单校验并抛异常，hibernate 只接受实体属性名（非法属性同样抛异常）。
- 引入 orm-sharding 时必须同时改数据源驱动与规则文件（见 §5），不要只加依赖就启动。

---

## 7. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | mybatis 手册 §3.2、技术特点；flex 手册 §3.2；hibernate 手册 | Mapper（或 Repository）自动扫描 `com.mcst.**.persistence.mapper` | 只有使用 `ApplicationStarter.run` 启动时，才会加入 `*ServiceScanner`；而且只扫描 `com.mcst` 下的包。业务包名不同时，必须自己写 `@MapperScan` 等注解 **已修复**：新增 `MybatisPlusMapperScanConfigure`/`FlexMapperScanConfigure`/`HibernateScanConfigure` 自动配置，扫描"应用包（AutoConfigurationPackages）+ `com.mcst.**`"，业务方自定义扫描时自动让位，`*ServiceScanner` 不再带扫描注解 |
| 2 | mybatis 手册 §11 | 包结构中有 `annotation/Column.java` | 不存在这个文件 |
| 3 | mybatis 手册 §12 第 7 条 | "同一字段出现在多种条件中时，等值条件自动让位" | 实际是 equals **被静默丢弃**，用户同时给出的 `eq` 和 `range` 条件只剩 range（三个 ORM 都是这样） **已修复**：三个 ORM 删除 `replaceEqFields`，equals 与其它条件类型按 AND 叠加 |
| 4 | mybatis/flex/hibernate 手册 §7.4 | `LessThan`：`field < value` | 取的是 `startValue`；把值放在 endValue 时，这个条件会被忽略 **已修复**：三个 ORM 中 LessThan/LessThanOrEqual 优先取 endValue、为空取 startValue；GreaterThan/GreaterThanOrEqual/Equal 优先取 startValue、为空取 endValue |
| 5 | mybatis 源码 | — | `queryById` 和 `updateBySelective(nullProps)` 使用 "`@TableId` 字段名转下划线" 作为列名，`@TableId("col")` 中自定义的列名不生效；没有 `@TableId` 时 queryById 返回 null，updateBySelective 静默成功。`notEquals`、`nullFields`、`exists(field,v)` 不做列名校验。启动时会获取一次数据库连接 **已修复**：主键列名取自 TableInfoHelper（`@TableId(value)` 生效），无主键时 queryById 抛异常、updateBySelective 返回失败；notEquals/nullFields 经 `SqlGuardUtil.toColumn` 校验，`exists(field,v)` 经 `resolveColumn` 校验（启动时取一次连接识别方言的行为保留） |
| 6 | flex 手册 §3.2 / §5、技术特点 | 插入和更新监听器自动填充创建时间、版本号、逻辑删除标志 | `registerInsertListener(handler)` 和 `registerUpdateListener(handler)` 都没有传实体类，而 Flex 1.11.x 的实现是 `for (Class c : classes) …`，**一个监听器都不会注册**，自动填充完全失效。只有基类上 `@Column(onInsertValue/onUpdateValue="now()")` 的两个时间字段有效 **已修复**：监听器以 `Object.class` 登记，对所有实体生效 |
| 7 | flex 手册 §3.2 | 开发模式下自动开启 SQL 审计 | `isDevelopmentMode()` 写死返回 false，没有配置项能开启 **已修复**：通过 `easyfk.orm.flex.sql-audit=true` 开启审计 |
| 8 | flex 手册、技术特点 | 与 orm-mybatis 的 API 完全对齐 | 接口签名一致，但 flex **没有 SqlGuardUtil 校验**（customSql 直接拼接、列名不校验），也**不支持 orLike 和 keyword 条件**，没有 BlockAttack 拦截器，也没有分页方言识别 **已修复**：flex 全部列名经 `SqlGuardUtil.toColumn` 校验、customSql 经 `assertSafeSqlFragment`，实现 orLike/keyword，`deleteByCondition`/`updateEntityByCondition` 无有效条件时抛异常，`updateBySelective` 主键为空时返回失败（分页方言识别仍未提供，使用 Flex 默认方言） |
| 9 | hibernate 手册 §7.1 | `setCustomConditionSql(sql)` 拼接原生 SQL 条件 | `buildCustomSqlPredicate` 恒返回 true，SQL 片段被**丢弃**；同时还会额外加一个 `isTrue(literal(true)).in(literal(1))` 谓词，有生成非法 SQL 的风险 **已修复**：传入 customConditionSql 时抛 UnsupportedOperationException |
| 10 | hibernate 手册 §6.3 | `queryById(id, selectColumns...)` 可选择字段；queryByField 可选择字段 | `em.find` 忽略 selectColumns，而且**不过滤逻辑删除**；queryByField 也忽略 selectFields **已修复**：queryById(cols)/queryByField/queryByCondition/queryByPage 的选择字段用 Criteria Tuple 投影实现；orLike/keyword 用 Criteria LIKE OR 实现；`totalCount=false` 时不再执行 count |
| 11 | hibernate 手册 §3.2 | 逻辑删除由 Repository 层自动处理 | 只有 queryByCondition、queryByPage、queryByField、exists(field) 会加 `deleted = 0`；queryById、countByCondition、exists(cond)、updateEntityByCondition **不过滤** **已修复**：queryById、countByCondition、exists(cond)、updateEntityByCondition 均过滤 `deleted = 0` |
| 12 | hibernate 手册 §5 | `@PreUpdate` 自动填充更新时间 | 只在字段为 null 时才填充，已加载的实体更新时不会刷新。`updateBySelective` 和 `updateEntityByCondition` 走 CriteriaUpdate，根本不会触发 `@PreUpdate`；而基类的 lastUpdateTime 没有 `@AutoUpdateTime`，所以 **lastUpdateTime 永远不会被更新** **已修复**：`@PreUpdate` 总是覆盖 lastUpdateTime/modifyTime/updateTime；CriteriaUpdate 路径同样 set 这三个字段和 `@AutoUpdateTime` 字段 |
| 13 | hibernate 源码 | — | `deleteByCondition` 和 `updateEntityByCondition` 在条件为空时会作用于整张表，没有任何防护 **已修复**：条件为空时抛 BusinessException |
| 14 | hibernate 手册 §10 对比表 | "flex 的条件字段名使用数据库列名（下划线）" | flex 默认 `change=true`，会把驼峰转成下划线，所以驼峰写法也可以；只有 hibernate 必须使用属性名 |
| 15 | sharding 手册 §4.2 | `readwrite_ds.write-data-source-name` 扁平结构 | 3.2.12 时框架是 5.2.1，读写分离需要 `static-strategy` 这一层嵌套，手册的扁平写法不生效。**3.5.16 升到 5.5.3 后手册写法已正确**，5.5.x 就是 `writeDataSourceName` / `readDataSourceNames` 扁平结构 **已解决**：版本升级后差异消失 |
| 16 | sharding 手册 §7.1 | `@TableId(type = IdType.ASSIGN_ID)` 表示"使用 ShardingSphere 分配 ID" | ASSIGN_ID 是 MyBatis-Plus 自己的雪花算法。ShardingSphere 的 key-generator 只在 INSERT 不包含主键列时才会生效 |
| 17 | sharding 技术特点"完全兼容" | 透明、业务零改动 | 3.2.12 时版本固定 5.2.1（面向 Boot 2.x），与 Boot 3.5 的 snakeyaml 2.x 有兼容风险。**3.5.16 已升级到 5.5.3 并改用 `ShardingSphereDriver`**，snakeyaml 问题消失；但 `spring.shardingsphere.*` 配置前缀废弃、单表需 `!SINGLE` 声明、广播表独立成 `!BROADCAST`，**从 3.2.12 升级不是零改动**。框架默认的 insert_time 排序加分页仍会在所有分片上执行 **已修复**：依赖已迁移，§5 已按新接入方式重写 |
| 18 | `orm-mybatis` 源码（3.5.16） | 上一版 import `com.baomidou.mybatisplus.extension.activerecord.Model` / `extension.service.impl.ServiceImpl` | MyBatis-Plus 3.5.18.1 已迁到 `com.baomidou.mybatisplus.spring.*`，框架三个基类同步改 import；**业务代码直接 import 过旧包名的要改**（见 §2.2 的提示） |
| 19 | 各 `build.gradle` | 上一版：orm-flex 写死 MyBatis-Flex 1.11.4、orm-mybatis 写死 jsqlparser 3.5.14 | 本版本 `mybatis-flex` 由 BOM 管理（1.11.8），`mybatis-plus-jsqlparser` 写死 3.5.18.1（跟随 MP 主版本） |
