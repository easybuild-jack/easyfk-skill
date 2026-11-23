# component-db Skill 参考文档

> 所属项目：`easyfk-component`　子模块：`db-redis`、`db-mysql`、`db-postgresql`、`db-mongo`、`db-clickhouse`
> 坐标：`com.mcst:db-<子模块>:3.2.12`
> 依据：5 个子模块全部源码，对齐 `db-redis开发手册.md`、`db-redis技术特点.md`、`db-mongo开发手册.md`、`db-mongo技术特点.md`、`db-clickhouse开发手册.md`、`db-clickhouse技术特点.md`（db-mysql、db-postgresql 没有文档）。
> 以源码为准；差异见文末「复查记录」。
> **`db-influx`（InfluxDB 时序库）已下线**，不再收录其用法与签名；需要时序库时自行引入 `influxdb-client-java`。

---

## 1. 子模块一览

| 子模块 | 内容 | 依赖 | 自动配置 |
|---|---|---|---|
| `db-redis` | Redis 多数据源连接、`RedisOptManager` 操作 API、发布订阅、智能序列化 | core、thread、spring-data-redis、kryo、commons-pool2 | `RedisDbConfig`（无条件） |
| `db-mysql` | 只有 `mysql-connector-j` 驱动依赖 | — | 无 |
| `db-postgresql` | 只有 `postgresql` 驱动依赖 | — | 无 |
| `db-mongo` | `BaseMongoEntity` → `BaseSpringMongoDAO` → `BaseMongoRepositoryImpl`（实现 `IBaseRepository`） | spring-data-mongodb、repository、service-base | `MongoAutoConfig`（开启审计） |
| `db-clickhouse` | `ClickHouseJdbcHolder`（内部持有 Hikari 数据源，不注册为 DataSource Bean）+ `BaseClickHouseRepositoryImpl`（拼接并校验 SQL） | clickhouse-jdbc、starter-jdbc、service-base | `ClickHouseConfig`（配置了 `url` 才生效） |
ORM（MyBatis/Flex/Hibernate）位于 `component-orm`，关系库只需要引 `db-mysql` / `db-postgresql` 驱动，再配合 orm 模块使用。

---

## 2. db-redis

### 2.1 两种模式

| 模式 | 开关 | 连接来源 | 可用的连接键 |
|---|---|---|---|
| 简单模式（默认） | `easyfk.config.db.redis.enable-dynamic=false` | Spring Boot 的 `spring.data.redis.*` | 只有 `default::default` |
| 动态模式 | `enable-dynamic=true` | `easyfk.config.db.redis.datasource.{name}.*`（Lettuce + commons-pool2） | `{ds}::default`，以及每个 `databases` 别名 `{ds}::{alias}` |

在动态模式下，`default-data-source` 默认库的连接工厂和 `RedisTemplate<String, Object>`（框架序列化器）以 `@Primary` Bean 暴露，Boot 的 Redis 自动配置随之让位：`redisTemplate`、Boot 的 `stringRedisTemplate`、actuator 的 redis 健康检查都使用这个真实连接。连接工厂由 `RedisConnectionManager` 统一关闭。

```yaml
easyfk:
  config:
    db:
      redis:
        enable-dynamic: true
        default-data-source: primary        # 必须是 datasource 中的某个 key
        redis-serializer: DEFAULT           # DEFAULT(Jackson) / FastJSON / KRYO
        trusted-packages: [com.example.]    # 多态反序列化额外信任的类名前缀（在默认前缀之外追加）
        datasource:
          primary:
            host: 10.0.0.1
            port: 6379
            password: xxx
            database: 0
            databases: {cache: 1, session: 2}   # 索引不能与 database 重复，且彼此不能重复
            timeout: 2s
            pool: {max-active: 32, max-idle: 16, min-idle: 4, max-wait: 1s}
          cluster-ds:
            username: app                     # Redis 6 ACL 用户名（可选，三种模式都生效）
            password: xxx
            cluster:
              nodes: [10.0.0.1:7000, 10.0.0.2:7000]
        biz-db:
          db-map:
            order: {datasource: primary, database-name: cache}
```

数据源配置项：
- 连接与基础：`host`（默认 localhost；配置了 cluster/sentinel 时忽略）、`port`、`database`（0–15）、`databases`、`username`（ACL）、`password`、`timeout`、`ssl`。
- SSL `ssl-config.*`（`ssl: true` 时生效）：`trust-store`、`trust-store-password`、`key-store`、`key-store-password`（路径支持 `classpath:`/`file:`，证书库不存在时启动失败）、`verify-peer`（默认 true）、`verify-hostname`（默认 true；Lettuce 只能整体关闭校验，`verify-hostname=false` 必须同时 `verify-peer=false`）。
- 连接池 `pool.*`：`max-active`、`max-idle`、`min-idle`、`max-wait`、`test-on-borrow`、`test-while-idle`、`time-between-eviction-runs`。
- 集群 `cluster.*`：`nodes`、`max-redirects`、`topology-refresh`、`topology-refresh-period`、`adaptive-refresh`。
- 哨兵 `sentinel.*`：`nodes`、`master`、`sentinel-password`。

- 全局：`redis-serializer`、`trusted-packages`（Jackson/FastJSON 多态反序列化额外允许的类名前缀，默认已允许 `com.mcst.`、`java.util.`、`java.time.`、`java.lang.`、`java.math.`）。

### 2.2 参数对象与 key

参数对象只能通过 `RedisArgsHelper` 创建（构造器不对外开放）：

```java
@Resource private RedisArgsHelper argsHelper;
@Resource private RedisOptManager redis;

KeyArgs k1 = argsHelper.createKeyArgs("order", "123", "Order");              // 按 biz-db 业务名查找；业务名不存在时静默回退到 default
KeyArgs k2 = argsHelper.createKeyArgs("primary", "cache", "123", "Order");   // 依次为 ds, db, key, namespace
NamespaceArgs ns = argsHelper.createNamespaceArgs("primary", "cache", "Order");
DsAndDbArgs ds = argsHelper.createDsAndDbArgs("primary", "cache");
```

- 最终的 Redis key 为 **`namespace::key`**（双冒号）；namespace 为空时只用 key。
- datasource 填 `default` 时会映射到 `default-data-source`。

### 2.3 RedisOptManager 主要 API

| 类别 | 方法 |
|---|---|
| 键 | `existKey`、`deleteKey`、`expireKey(args, Duration)`、`expireKeyAt`、`getKeyExpire`、`getKeys(pattern, args)`（匹配 `namespace::pattern`，执行的是阻塞的 KEYS 命令，生产大库慎用） |
| 自增 | `autoId(args)`、`autoIdByExpire(args, ttl)`（Lua 原子执行 INCR，key 无过期时间时才设置 PEXPIRE） |
| KV | `putObject(args, v[, ttl])`、`putIfAbsent(args, v, ttl)`（SET NX EX，原子操作）、`getObject`、`multiSetForValue` / `multiSetIfNotExistsForValue` / `multiGetForValue`（参数为 NamespaceArgs） |
| Hash | `putValueToHash`、`putObjectToHash`、`putMapToHash`、`getValueFromHash`、`getMapFromHash`、`getObjectFromHash(args, Class)`、`getAllValuesFromHash`、`getValuesFromHash`、`getHashSize`、`existHashKey`、`deleteObjectFromHash` |
| List | `putObjectToList`、`putObjectsToList`（逐条 RPUSH）、`putObjectToListAtIndex`、`getObjectFromList`、`getAllObjectFromList`、`getRangeFromList`、`getPageFromList`、`getAndRemoveFirst/LastObjectFromList`、`deleteObjectFromList`、`getListSize` |
| Set/ZSet | `putObjectToSet`、`putObjectsToSet`、`getAllObjectFromSet`、`objectIsSetMember`、`deleteObjectFromSet`、`getSetSize`；`putObjectToZSet`、`putObjectsToZSet`、`getAllObjectFromZSet`、`getPageFromZSet`、`getRangeFromZSet(min,max[,page,size])`、`objectIsZSetMember`、`deleteObjectFromZSet`、`getZSetSize` |
| 管道 | `executePipelined(RedisCallback, DsAndDbArgs)`、`executePipelinedSimple(Consumer<RedisConnection>, DsAndDbArgs)` |
| 事务 | `executeTransaction((ops, key) -> {...}, NamespaceArgs)`、`executeTransactionWithWatch(watchKeys, (ops, key) -> {...}, ns)`：回调第二个参数是 key 包装函数，回调内必须用 `key.apply("k1")` 得到 `namespace::k1`；watchKeys 自动包装 |
| Lua | `executeLuaScript(script, keys, args, ns)`、`executeLuaScript(script, Class, keys, args, ns)`：KEYS 自动加 namespace；ARGV 中的 String/数值/布尔按纯文本传入，其他对象用值序列化器 |

### 2.4 序列化（SmartRedisSerializer）

- key 和 hashKey 一律使用 String 序列化。
- value 的处理方式：
  - `String` 写成纯文本，`byte[]` 原样写入。
  - 数值（Long/Integer/Short/Byte/Double/Float/BigDecimal/BigInteger）、`Boolean`、`Character` 写成带类型的信封 `{"@scalar":"java.lang.Long","value":"123"}`，读回时还原为原类型。
  - 其他对象按 `redis-serializer` 序列化：Jackson（NON_FINAL 默认类型，多态类型只允许 `trusted-packages` 白名单）、FastJSON2（autoType 同样受白名单限制）或 Kryo（不限制类）。
- 因为数值不再是纯文本，用 `putObject` 写入数值的 key **不能再执行 INCR/INCRBY**；计数器请用 `autoId`/Lua。INCR 产生的计数值是纯文本，`getObject` 读回为 String。
- 升级前用旧版本写入的纯文本数值，读回仍是 String。

### 2.5 发布订阅（`easyfk.config.db.redis.pubsub.open=true`）

配置项：`pubsub.datasource`、`pubsub.database-name`（发布和订阅使用的连接）、`pubsub.retry.*`（`enabled`、`max-retries`、`initial-delay`、`max-delay`、`queue-size`、`dead-letter-queue-size`、`retry-thread-pool-size`、`dead-letter-cleanup.*`）。`pubsub.channel` 未使用；`is-consumer=true` 时创建 `redisTaskExecutor`，监听容器用它分发消息（否则用容器默认执行器）。监听容器在首次订阅时创建，并手动 `afterPropertiesSet()` + `start()`。

```java
@Resource private IPublishSubscribe pubSub;
pubSub.publish("order:created", "123");
pubSub.publish("created", "123", "order");                // 第三个参数 channelPrefix：实际频道为 "order::created"，不是数据源
pubSub.publishObject("order:events", event);
String id = pubSub.subscribe("order:created", (ch, msg) -> {...});
pubSub.subscribeObject(...); pubSub.psubscribe("order:*", ...); pubSub.unsubscribe(id);
```

监听器抛出的异常会进入内存重试队列（指数退避），失败后转入内存死信队列，进程重启后全部丢失。发布和订阅固定使用 `pubsub.datasource` / `pubsub.database-name` 指定的连接。

---

## 3. db-mongo

```java
@Document("product")
public class Product extends BaseMongoEntity { private String name; private BigDecimal price; }   // objectId(@Id) + id(@Transient) + createdAt/updatedAt(审计)

@Repository
public class ProductDAO extends BaseSpringMongoDAO<Product> {}

@Repository
public class ProductRepository extends BaseMongoRepositoryImpl<ProductDAO, ProductDTO, Product, String> {}
// 泛型依次为：D=DAO, T=DTO, P=Entity, PK=主键（应为 String）
```

- `MongoAutoConfig`：`@EnableMongoAuditing`，审计时间来源为 `LocalDateTime.now()`，可通过名为 `mongoAuditingDateTimeProvider` 的 Bean 覆盖。业务代码**不要再声明** `@EnableMongoAuditing`。
- Repository 提供的方法：`queryById(id, cols...)`、`queryByCondition`、`queryOneByCondition`、`queryOneByField`、`queryByField`、`queryByPage`（默认 1/10）、`exists`、`countByCondition`、`insert`、`insertAndReturnId`（返回十六进制 ObjectId 字符串）、`insertBatch`（每 1000 条一批）、`deleteById`、`deleteByCondition`、`updateBySelective(dto, nullProps...)`、`updateEntityByCondition`（updateMulti）、`saveOrUpdateBySelective`。
- DAO 额外提供：`atomicIncrement(condition, field, n)`（findAndModify，返回更新后的文档）、`findByEntity` / `countByEntity`（按非空字段做 example 查询，跳过 Date 字段）、`updateEntity`（**全量更新**：值为 null 的字段会被 `$unset`）。
- `SearchCondition` 到 `Query` 的映射：
  - equals → `is`，notEquals → `ne`，in → `in`。
  - like → `regex(Pattern.quote(value))`：按字面量做包含匹配，正则元字符不生效。
  - range → `gt/gte/lt/lte/is/between`；下界类条件取 startValue（缺省用 endValue），上界类条件取 endValue（缺省用 startValue）。
  - 所有条件统一用 `$and` 组合，同一字段可以叠加多个范围/等值条件。
  - 排序使用 asc/descFields，默认按 `createdAt` 降序；top 对应 limit。
- 字符串 id 只有是合法 ObjectId（24 位十六进制）时才转换为 `ObjectId`，其他字符串按原样作为主键（适用于按 id 查询/删除）。继承 `BaseMongoEntity` 的实体主键类型固定是 `ObjectId`，按实体更新时 id 不是合法 ObjectId 会抛 `IllegalArgumentException`。
- `deleteByCondition`、`updateFirst`、`updateEntityByCondition` 条件为空时抛异常，拒绝操作整个集合。
- `saveOrUpdateBySelective`：DTO 的 `@Id` 字段或转换后实体的 id 非空则更新，否则插入。

---

## 4. db-clickhouse（配置了 `easyfk.config.db.clickhouse.url` 才生效）

```yaml
easyfk.config.db.clickhouse:
  url: jdbc:clickhouse://10.0.0.5:8123/analytics
  username: default
  password: xxx
  database: analytics
  min-pool-size: 5
  max-pool-size: 20
  connection-timeout: 30000
  socket-timeout: 300000
```

- Bean：只有 `ClickHouseJdbcHolder`。ClickHouse 的 DataSource / JdbcTemplate **不注册为 Spring Bean**（主数据源仍是唯一候选，Boot 的 JdbcTemplate/MyBatis/事务自动配置不受影响）；连接池在首次调用 `holder.getJdbcTemplate()` 时创建，容器关闭时释放。
- 实体：`@ClickHouseTable(name, database)`，字段用 `@ClickHouseColumn(name, ignore, primaryKey, partitionKey, timestamp)`。列名默认为字段名的下划线形式，表名、库名、列名都必须是合法标识符。
  - static/transient/合成字段与 `ignore = true` 不参与读写；
  - `primaryKey`、`partitionKey` 字段不会出现在 `update` 的 SET 中（ClickHouse 不允许更新键列）；
  - `timestamp = true` 的字段作为默认时间列（条件未指定 `timeField` 时）。
- Repository：`class XxxRepo extends BaseClickHouseRepositoryImpl<XxxEntity>`，提供以下方法：
  - `insert`、`insertBatch(list[, batchSize=1000])`（拼接多行 VALUES）；
  - `queryList`、`queryOne`、`count`、`aggregate`（返回 Map 列表）；
  - `delete(condition)`、`update(entity, condition)`（都是异步的 `ALTER TABLE ... DELETE/UPDATE` mutation，**WHERE 为空时拒绝执行**）；
  - `deleteByTimeRange`；
  - `executeQuery(sql)`、`executeQueryForMap(sql)`。
- `ClickHouseSearchCondition` 支持的条件：
  - 比较类：`equals`、`notEquals`、`like`、`in`、`gt`、`gte`、`lt`、`lte`、`between`；
  - 时间范围：`start/stop` 作用于 `timeField`（未指定时取 `timestamp = true` 字段，再缺省为 `create_time`），`start/stop` 支持 `-1h`/`+2d`、`now()` 和日期时间字符串；
  - 其他：`customWhere`、`customSql`、`selectFields`、`aggregationFunctions`、`groupByFields`、`asc/descFields`、`pageSearch`、`top`、`useFinal`。
  - 条件值中的相对时间必须显式写成 `ClickHouseRelativeTime.of("-1h")` 才会渲染为 `now() - INTERVAL`；普通字符串一律按字面量处理。
- SQL 仍是字符串拼接，但：值转义 `\` 和 `'`；字段名、selectFields、order/group by 按标识符正则校验；`aggregationFunctions`、`customWhere` 拒绝 `;`、注释和 DDL/DML 关键字；`customSql` 还必须以 SELECT/WITH 开头。这些校验只是兜底，片段仍不能来自用户输入。

---

## 5. 生成代码时的规则

**Do**
- Redis 单实例用简单模式（`spring.data.redis.*`）；需要多实例或多库时用动态模式。
- 通过 `RedisArgsHelper` 创建参数，用 namespace 区分业务；需要原子性时用 `putIfAbsent` 或 Lua；事务回调中的 key 一律用回调提供的 `key.apply(...)` 包装。
- 计数器用 `autoId` / `autoIdByExpire` 或 Lua，不要先 `putObject` 数值再 INCR。
- 缓存的业务类放在 `com.mcst.` 下，或把包前缀加入 `trusted-packages`，否则 Jackson/FastJSON 反序列化会拒绝。
- Mongo 的 DTO 主键字段用 `String id`；`saveOrUpdateBySelective` 会按 id 是否为空选择更新或插入。
- ClickHouse 的字段名、排序、聚合和自定义 SQL 只能使用代码常量或白名单值（框架只做兜底校验）。
- ClickHouse 条件里需要相对时间时用 `ClickHouseRelativeTime.of("-1h")`。
- ClickHouse 直接执行 SQL 时注入 `ClickHouseJdbcHolder` 并调用 `getJdbcTemplate()`。

**Don't**
- 不要把 `publish(channel, msg, x)` 的第三个参数当作数据源（它是频道前缀）。
- 不要在生产大库上频繁调用 `getKeys`（KEYS 是阻塞命令）。
- 不要再按名称注入 `clickHouseDataSource` / `clickHouseJdbcTemplate`（已不是 Bean）。
- 不要再引入 `db-influx` 或使用 `BaseFluxRepositoryImpl` / `FluxSearchCondition`：该子模块已下线，坐标与类都不再提供。

---

## 6. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | redis 手册 §3.4 / §3.5 | 集群、哨兵配置示例（不写 host） | `host` 默认是 `localhost`，校验器（`RedisConfigValidator` 和 `ConnectionFactoryBuilder`）会把它算作 standalone，与 cluster/sentinel 同时成立，**启动报"不能同时配置多种连接模式"**。必须显式写 `host: ""`；`RedisConfigHelper.createCluster/createSentinel` 生成的配置同样会失败 **已修复**：配置了 cluster/sentinel 时忽略 host，无需再写 `host: ""` |
| 2 | redis 手册 §6.3 | 订阅频道和模式即可收到消息 | `SubscriptionManager` 手工 `new RedisMessageListenerContainer()`，**从未调用 `afterPropertiesSet()` 或 `start()`**，它也不是 Spring Bean。Spring Data Redis 3.x 的容器只在运行状态下才会订阅，所以**订阅端收不到任何消息**（发布端正常） **已修复**：监听容器创建后手动 `afterPropertiesSet()` + `start()`，订阅可正常收到消息 |
| 3 | redis 手册 §6.2 | `publish(channel, msg, "primary")` 指定数据源发布 | 第三个参数是频道前缀，实际发往 `primary::order:created`。发布和订阅固定使用 `pubsub.datasource/database-name`。手册也没有说明总开关 `pubsub.open=true` **已修复**：第三个参数更名为 `channelPrefix`，Javadoc 与文档写明实际频道为 `channelPrefix::channel`、数据源由 `pubsub.datasource` 决定；文档补充 `pubsub.open=true` |
| 4 | redis 手册 §4.3、技术特点 | key 格式为 `{namespace}:{key}` | 实际是 `namespace::key`（双冒号） **已修复**（文档）：本文 §2.2 统一以源码为准写作 `namespace::key`，代码不变 |
| 5 | redis 手册 §5.2 | `getKeys(pattern, args)` 按模式匹配 | pattern 参数被忽略，实际执行 `KEYS namespace::key`（阻塞命令） **已修复**：按 `namespace::pattern` 匹配 |
| 6 | redis 手册 §8、技术特点 | 动态模式自动阻止 Spring Boot 默认 Redis 自动配置 | 只注册了一个 `@Primary` 的 localhost 占位工厂，Boot 的 RedisTemplate、StringRedisTemplate、健康检查仍然会创建并指向 localhost **已修复**：动态模式以 `@Primary` 暴露默认数据源的真实连接工厂与 RedisTemplate，Boot 的 stringRedisTemplate、健康检查使用真实连接 |
| 7 | redis 手册 §3.6、技术特点 | 内置 SSL/TLS 支持 | 只调用了 `useSsl()`，`ssl-config` 中的 truststore/keystore/verify-peer 全部未使用；`username`（ACL）也未使用 **已修复**：truststore/keystore 通过 Lettuce `SslOptions` 生效，`verify-peer=false` 关闭校验；`username` 在单机/哨兵/集群三种模式都生效 |
| 8 | redis 手册 §3.7 | 智能序列化，兼容历史数据 | Number/Boolean 写成纯字符串，读回来是 String，按数值类型接收会 `ClassCastException`。Jackson 开启 `LaissezFaireSubTypeValidator` 加 NON_FINAL 默认类型，Redis 一旦被写入恶意数据，存在反序列化风险 **已修复**：数值/布尔/字符写成带类型信封，读回原类型；Jackson 改用 `BasicPolymorphicTypeValidator` 白名单（默认 com.mcst./java.util./java.time./java.lang./java.math.，可用 `trusted-packages` 追加），FastJSON autoType 同样受限 |
| 9 | redis 手册 §5.9 | 事务示例 `operations.opsForValue().set("key1", ...)` | 事务回调里的 key 不加 namespace，与其他 API 不一致；只有 watchKeys 和 Lua 的 KEYS 会加 **已修复**：事务回调改为 `(ops, key) -> {}`，通过 key 包装函数统一加 namespace（不兼容变更） |
| 10 | redis PubSubConfig | `is-consumer` 开启消费线程池 | `redisTaskExecutor` 没有被任何代码使用；监听容器也没有设置执行器 **已修复**：监听容器使用 `redisTaskExecutor`（存在时） |
| 11 | mongo 手册 §7.2 / §9.10 | `saveOrUpdateBySelective`：有 ID 则更新，无 ID 则插入 | 实现是在 **DTO** 上查找带 Spring Data `@Id` 注解的字段，手册示例的 DTO（`private String id`）没有这个注解，所以**总是走插入**；传入已有 id 时会触发主键冲突 **已修复**：DTO 的 `@Id` 或转换后实体的 id 非空即走更新 |
| 12 | mongo 手册 §8.2 / §12 | like 为正则匹配（需注意转义） | 直接 `Pattern.compile(用户输入)`，存在正则注入和 ReDoS 风险。对同一字段叠加多个范围或等值条件时，Spring Data 会抛"不能对同一字段添加第二个 criteria"异常 **已修复**：like 用 `Pattern.quote` 按字面量匹配；所有条件统一 `$and` 组合，同字段多条件不再报错 |
| 13 | mongo 手册 §7.2 | 条件删除、条件批量更新 | 条件为空时生成空 Query，会**删除或更新整个集合**，没有任何防护（SQL 侧有 BlockAttack 拦截，Mongo 没有） **已修复**：空条件的删除/批量更新直接抛异常 |
| 14 | mongo DAO | — | 字符串 id 一律 `new ObjectId(str)`，不支持自定义字符串主键 **已修复**：只有合法 ObjectId 才转换，其他字符串主键原样使用 |
| 15 | clickhouse 手册 §10.1、技术特点 | 自动转义，从源头杜绝 SQL 注入 | 只有"值"做了转义。字段名、selectFields、排序、分组、聚合函数、`customWhere`、`customSql` 都原样拼接；字符串值如果碰巧匹配 `-1h` 这类格式，会被当成时间表达式（`now() - INTERVAL`） **已修复**：标识符正则校验；聚合函数/customWhere/customSql 拒绝分号、注释和 DDL/DML，customSql 限 SELECT/WITH；相对时间只在显式使用 `ClickHouseRelativeTime` 时渲染 |
| 16 | clickhouse 手册 §4.2 | `primaryKey`、`timestamp`、`partitionKey` 注解属性 | 全部未被使用。insert/update 不跳过 static 字段（`serialVersionUID` 会被当作列 `serial_version_u_i_d`）；`update` 不跳过 `ignore` 字段 **已修复**：跳过 static/transient/合成与 `ignore` 字段；`primaryKey`/`partitionKey` 不进入 UPDATE SET；`timestamp` 字段作为默认时间列 |
| 17 | clickhouse 手册 §9、技术特点 | 延迟初始化，不影响主数据源 | `@Lazy` 只是推迟创建。DataSource 候选变成两个，主数据源没有 `@Primary` 时，Boot 中带 `@ConditionalOnSingleCandidate` 的自动配置（JdbcTemplate、MyBatis 等）会被跳过 **已修复**：DataSource/JdbcTemplate 不再注册为 Bean，改由 `ClickHouseJdbcHolder` 懒加载持有，主数据源保持唯一候选 |
| 18 | db-influx 子模块 | 原 §5 记录了 InfluxDB 访问的用法与 6 处修复 | 该子模块已下线，§5 整章、子模块表中的一行与 `api/` 中的 8 个类型（`InfluxDBConfig`、`BaseFluxRepositoryImpl`、`FluxSearchCondition` 等）已全部移除 **已删除**：需要时序库时自行引入 `influxdb-client-java` |
