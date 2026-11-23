# db-clickhouse 开发手册

## 1. 模块概述

`db-clickhouse` 是 EasyFK 框架中面向 ClickHouse 列式数据库的数据访问组件。该模块基于 Spring Boot 自动配置和 HikariCP 高性能连接池，提供注解驱动的实体映射、通用 CRUD 操作、灵活的条件查询构建以及原生 SQL 执行能力，适用于日志分析、时序数据存储、实时报表统计等大数据量场景。

## 2. 依赖引入

### Maven

```xml
<dependency>
    <groupId>com.mcst</groupId>
    <artifactId>db-clickhouse</artifactId>
</dependency>
```

### Gradle

```gradle
dependencies {
    implementation 'com.mcst:db-clickhouse'
}
```

> 版本号由框架统一 BOM 管理，无需手动指定。

该模块会自动传递引入以下依赖：
- `clickhouse-jdbc` — ClickHouse JDBC 驱动
- `httpclient5` / `httpcore5` — HTTP Client 5（ClickHouse HTTP 协议通信）
- `guava` — Google Guava 工具库
- `easyfk-core` — EasyFK 框架核心
- `service-base` — EasyFK 服务基础模块
- `spring-boot-starter-jdbc` — Spring Boot JDBC 支持

## 3. 配置说明

### 3.1 配置属性

所有配置项统一在 `easyfk.config.db.clickhouse` 前缀下。

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `url` | String | — | JDBC 连接地址（**必填**，配置后模块自动生效） |
| `username` | String | — | 连接用户名 |
| `password` | String | — | 连接密码 |
| `database` | String | — | 默认数据库名称 |
| `minPoolSize` | Integer | `5` | 连接池最小空闲连接数 |
| `maxPoolSize` | Integer | `20` | 连接池最大连接数 |
| `connectionTimeout` | Integer | `30000` | 连接超时时间（毫秒） |
| `socketTimeout` | Integer | `300000` | Socket 超时时间（毫秒） |

### 3.2 配置示例

```yaml
easyfk:
  config:
    db:
      clickhouse:
        url: jdbc:clickhouse://localhost:8123/default
        username: default
        password: your_password
        database: default
        minPoolSize: 5
        maxPoolSize: 20
        connectionTimeout: 30000
        socketTimeout: 300000
```

### 3.3 连接池参数

模块内置 HikariCP 连接池，已预设以下优化参数：

| 参数 | 值 | 说明 |
|------|------|------|
| 连接池名称 | `ClickHouseHikariPool` | 便于监控和日志区分 |
| 连接测试查询 | `SELECT 1` | 定期检测连接可用性 |
| 连接最大生命周期 | 30 分钟 | 防止连接长期持有导致资源泄漏 |
| 空闲连接超时 | 10 分钟 | 及时回收空闲连接 |

## 4. 注解说明

### 4.1 @ClickHouseTable

标记实体类对应的 ClickHouse 表名，作用于类级别。

| 属性 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | String | 是 | 表名 |
| `database` | String | 否 | 数据库名（不指定则使用配置中的默认数据库） |

### 4.2 @ClickHouseColumn

标记实体类字段对应的 ClickHouse 列名及属性，作用于字段级别。

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | String | `""` | 列名（为空则自动将驼峰字段名转为下划线格式） |
| `primaryKey` | boolean | `false` | 是否为主键 |
| `timestamp` | boolean | `false` | 是否为时间戳字段（用于时间范围查询） |
| `partitionKey` | boolean | `false` | 是否为分区键 |
| `ignore` | boolean | `false` | 是否忽略该字段（不参与数据库操作） |

## 5. 使用方式

### 5.1 定义实体类

```java
@Data
@ClickHouseTable(name = "user_event_log")
public class UserEventLog {

    @ClickHouseColumn(name = "event_id", primaryKey = true)
    private String eventId;

    @ClickHouseColumn(name = "user_id")
    private Long userId;

    @ClickHouseColumn(name = "event_type")
    private String eventType;

    @ClickHouseColumn(name = "event_data")
    private String eventData;

    @ClickHouseColumn(name = "create_time", timestamp = true)
    private LocalDateTime createTime;

    @ClickHouseColumn(ignore = true)
    private String tempField;
}
```

> 未添加 `@ClickHouseColumn` 注解的字段，默认自动将驼峰命名转换为下划线命名参与数据库操作。标记 `ignore = true` 的字段将被排除。

### 5.2 创建 Repository

继承 `BaseClickHouseRepositoryImpl`，即可获得全部基础 CRUD 能力：

```java
@Repository
public class UserEventLogRepository extends BaseClickHouseRepositoryImpl<UserEventLog> {

    // 可在此添加自定义查询方法
}
```

### 5.3 注入使用

```java
@Service
public class EventService {

    @Resource
    private UserEventLogRepository eventLogRepository;
}
```

## 6. API 参考

### 6.1 IBaseClickHouseRepository 接口方法

#### 插入操作

| 方法 | 参数 | 说明 |
|------|------|------|
| `insert(entity)` | 实体对象 | 单条数据插入 |
| `insertBatch(entities)` | 实体列表 | 批量插入（默认批次 1000 条） |
| `insertBatch(entities, batchSize)` | 实体列表, 批次大小 | 批量插入（指定批次大小） |

#### 查询操作

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `queryList(condition)` | 查询条件 | `List<T>` | 条件查询列表 |
| `queryOne(condition)` | 查询条件 | `T` | 查询单条记录（自动 LIMIT 1） |
| `count(condition)` | 查询条件 | `long` | 查询总数 |
| `aggregate(condition)` | 查询条件 | `List<Map>` | 聚合查询（需设置聚合函数和分组字段） |

#### 删除操作

| 方法 | 参数 | 说明 |
|------|------|------|
| `delete(condition)` | 查询条件 | 条件删除（ALTER TABLE DELETE，**必须包含 WHERE 条件**） |
| `deleteByTimeRange(start, end)` | 起止时间字符串 | 按时间范围删除 |

#### 更新操作

| 方法 | 参数 | 说明 |
|------|------|------|
| `update(entity, condition)` | 实体对象, 查询条件 | 条件更新（ALTER TABLE UPDATE，**必须包含 WHERE 条件**） |

#### 原生 SQL 操作

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `executeQuery(sql)` | SQL 语句 | `List<T>` | 原生 SQL 查询，结果映射为实体 |
| `executeQueryForMap(sql)` | SQL 语句 | `List<Map>` | 原生 SQL 查询，结果映射为 Map |
| `executeUpdate(sql)` | SQL 语句 | `int` | 原生 SQL 执行（INSERT/UPDATE/DELETE） |

#### 工具方法

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `tableExists()` | `boolean` | 检查实体对应的表是否存在（查询 system.tables） |
| `getTableName()` | `String` | 获取实体对应的表名 |

## 7. 查询条件详解

### 7.1 ClickHouseSearchCondition 属性

`ClickHouseSearchCondition` 支持链式调用（`@Accessors(chain = true)`）。

#### 时间范围

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `start` | String | — | 开始时间（支持绝对时间和相对时间） |
| `stop` | String | — | 结束时间（支持绝对时间和相对时间） |
| `timeField` | String | `create_time` | 时间字段名 |

#### 条件查询

| 属性 | 类型 | 说明 |
|------|------|------|
| `equalsConditions` | `Map<String, Object>` | 等于条件 |
| `notEqualsConditions` | `Map<String, Object>` | 不等于条件 |
| `likeConditions` | `Map<String, String>` | 模糊查询条件（LIKE） |
| `inConditions` | `Map<String, List<?>>` | IN 查询条件 |
| `gtConditions` | `Map<String, Object>` | 大于条件 |
| `gteConditions` | `Map<String, Object>` | 大于等于条件 |
| `ltConditions` | `Map<String, Object>` | 小于条件 |
| `lteConditions` | `Map<String, Object>` | 小于等于条件 |
| `betweenConditions` | `Map<String, Object[]>` | BETWEEN 条件（value 为 `[min, max]` 数组） |

#### 聚合与分组

| 属性 | 类型 | 说明 |
|------|------|------|
| `aggregationFunctions` | `String[]` | 聚合函数，如 `count(*)`, `sum(amount)`, `avg(price)` |
| `groupByFields` | `String[]` | 分组字段 |
| `selectFields` | `String[]` | 自定义查询字段 |

#### 排序

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `descFields` | `String[]` | — | 降序排序字段 |
| `ascFields` | `String[]` | — | 升序排序字段 |
| `defaultDesc` | Boolean | `true` | 默认按时间字段降序排列 |

#### 分页与限制

| 属性 | 类型 | 说明 |
|------|------|------|
| `pageSearch` | `PageSearch` | 分页查询（包含 page 和 limit） |
| `top` | Integer | 取前 N 条数据 |

#### 高级选项

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `customWhere` | String | — | 自定义 WHERE 条件（直接拼接到 SQL） |
| `customSql` | String | — | 完全自定义 SQL（跳过条件构建） |
| `useFinal` | Boolean | `false` | 是否使用 FINAL 关键字（用于 ReplacingMergeTree 等表引擎） |

### 7.2 相对时间表达式

时间字段支持相对时间表达式，格式为 `[+-]数字单位`：

| 表达式 | 说明 | 生成 SQL |
|--------|------|----------|
| `-1d` | 1 天前 | `now() - INTERVAL 1 DAY` |
| `-2h` | 2 小时前 | `now() - INTERVAL 2 HOUR` |
| `-30m` | 30 分钟前 | `now() - INTERVAL 30 MINUTE` |
| `+1h` | 1 小时后 | `now() + INTERVAL 1 HOUR` |
| `-1w` | 1 周前 | `now() - INTERVAL 1 WEEK` |
| `-1y` | 1 年前 | `now() - INTERVAL 1 YEAR` |
| `now` / `now()` | 当前时间 | `now()` |

支持的时间单位：`s`（秒）、`m`（分）、`h`（时）、`d`（天）、`w`（周）、`y`（年）。

### 7.3 SearchRequest 自动转换

`ClickHouseSearchConditionUtil.createSearchCondition()` 可将框架通用的 `SearchRequest` 自动转换为 `ClickHouseSearchCondition`，自动处理：
- 参数对象非空字段 → 等于条件
- `BasicParam` 中的分页、Top、时间范围、排序参数
- 驼峰字段名自动转下划线

```java
@PostMapping("/search")
public List<UserEventLog> search(@RequestBody SearchRequest<UserEventParam> request) {
    ClickHouseSearchCondition condition =
        ClickHouseSearchConditionUtil.createSearchCondition(request, UserEventLog.class);
    return eventLogRepository.queryList(condition);
}
```

## 8. 实战示例

### 8.1 单条插入

```java
UserEventLog log = new UserEventLog();
log.setEventId("evt_001");
log.setUserId(10086L);
log.setEventType("LOGIN");
log.setCreateTime(LocalDateTime.now());

eventLogRepository.insert(log);
```

### 8.2 批量插入

```java
List<UserEventLog> logs = new ArrayList<>();
for (int i = 0; i < 5000; i++) {
    UserEventLog log = new UserEventLog();
    log.setEventId("evt_" + i);
    log.setUserId((long) (i % 100));
    log.setEventType("PAGE_VIEW");
    log.setCreateTime(LocalDateTime.now());
    logs.add(log);
}

// 默认每批 1000 条
eventLogRepository.insertBatch(logs);

// 自定义批次大小
eventLogRepository.insertBatch(logs, 2000);
```

### 8.3 条件查询

```java
ClickHouseSearchCondition condition = new ClickHouseSearchCondition()
    .setEqualsConditions(Map.of("event_type", "LOGIN"))
    .setStart("-7d")
    .setStop("now")
    .setDescFields(new String[]{"create_time"})
    .setTop(100);

List<UserEventLog> logs = eventLogRepository.queryList(condition);
```

### 8.4 分页查询

```java
ClickHouseSearchCondition condition = new ClickHouseSearchCondition()
    .setEqualsConditions(Map.of("user_id", 10086L))
    .setPageSearch(new PageSearch(1, 20));

List<UserEventLog> list = eventLogRepository.queryList(condition);
long total = eventLogRepository.count(condition);
```

### 8.5 聚合查询

```java
ClickHouseSearchCondition condition = new ClickHouseSearchCondition()
    .setAggregationFunctions(new String[]{"event_type", "count(*) as cnt"})
    .setGroupByFields(new String[]{"event_type"})
    .setStart("-30d")
    .setDescFields(new String[]{"cnt"})
    .setTop(10);

List<Map<String, Object>> result = eventLogRepository.aggregate(condition);
// 结果示例：[{event_type=LOGIN, cnt=12345}, {event_type=PAGE_VIEW, cnt=98765}]
```

### 8.6 BETWEEN 查询

```java
ClickHouseSearchCondition condition = new ClickHouseSearchCondition()
    .setBetweenConditions(Map.of("user_id", new Object[]{100L, 200L}));

List<UserEventLog> logs = eventLogRepository.queryList(condition);
```

### 8.7 IN 查询

```java
ClickHouseSearchCondition condition = new ClickHouseSearchCondition()
    .setInConditions(Map.of("event_type", List.of("LOGIN", "LOGOUT", "REGISTER")));

List<UserEventLog> logs = eventLogRepository.queryList(condition);
```

### 8.8 条件删除

```java
// 按时间范围删除
eventLogRepository.deleteByTimeRange("2025-01-01 00:00:00", "2025-06-30 23:59:59");

// 按条件删除
ClickHouseSearchCondition condition = new ClickHouseSearchCondition()
    .setEqualsConditions(Map.of("event_type", "TEST"));
eventLogRepository.delete(condition);
```

### 8.9 条件更新

```java
UserEventLog updateEntity = new UserEventLog();
updateEntity.setEventType("UPDATED_TYPE");

ClickHouseSearchCondition condition = new ClickHouseSearchCondition()
    .setEqualsConditions(Map.of("event_id", "evt_001"));

eventLogRepository.update(updateEntity, condition);
```

### 8.10 使用 FINAL 关键字

对于 `ReplacingMergeTree` 引擎的表，查询时可启用 FINAL 以获取去重后的最新数据：

```java
ClickHouseSearchCondition condition = new ClickHouseSearchCondition()
    .setUseFinal(true)
    .setEqualsConditions(Map.of("user_id", 10086L));

List<UserEventLog> logs = eventLogRepository.queryList(condition);
// 生成 SQL: SELECT * FROM user_event_log FINAL WHERE user_id = 10086 ORDER BY create_time DESC
```

### 8.11 原生 SQL 查询

```java
// 返回实体列表
List<UserEventLog> logs = eventLogRepository.executeQuery(
    "SELECT * FROM user_event_log WHERE event_type = 'LOGIN' LIMIT 10"
);

// 返回 Map 列表
List<Map<String, Object>> result = eventLogRepository.executeQueryForMap(
    "SELECT event_type, count(*) as cnt FROM user_event_log GROUP BY event_type"
);

// 执行 DDL / DML
eventLogRepository.executeUpdate(
    "ALTER TABLE user_event_log DELETE WHERE create_time < '2025-01-01'"
);
```

## 9. 自动配置机制

| 配置类 | 说明 |
|--------|------|
| `ClickHouseConfig` | 自动注册 ClickHouse 数据源和 JdbcTemplate |

- 通过 Spring Boot `AutoConfiguration.imports` 声明自动配置入口
- 使用 `@EnableConfigurationProperties` 自动绑定 `ClickHouseProperties`
- 仅当配置了 `easyfk.config.db.clickhouse.url` 时才会激活
- 使用 `@Lazy` 延迟初始化，不影响主数据源启动
- 在 `DataSourceAutoConfiguration` 之后配置，避免数据源冲突
- 注入时使用 `@Resource(name = "clickHouseJdbcTemplate")` 指定 Bean 名称

## 10. 安全特性

### 10.1 SQL 注入防护

- 所有字符串值自动进行转义处理（反斜杠、单引号）
- 值格式化统一通过 `ClickHouseSqlUtil.formatValue()` 处理

### 10.2 误操作保护

- 删除操作（`delete`）**强制要求** WHERE 条件，防止全表删除
- 更新操作（`update`）**强制要求** WHERE 条件，防止全表更新
- 空实体插入抛出 `IllegalArgumentException`
- 空更新条件抛出 `IllegalArgumentException`

## 11. 包结构

```
com.mcst.db.clickhouse
├── annotation
│   ├── ClickHouseTable.java              # 表名注解
│   └── ClickHouseColumn.java             # 列名注解
├── config
│   └── ClickHouseConfig.java             # Spring Boot 自动配置类
├── properties
│   └── ClickHouseProperties.java         # 配置属性绑定类
├── repository
│   ├── IBaseClickHouseRepository.java    # 通用仓库接口
│   └── BaseClickHouseRepositoryImpl.java # 通用仓库实现
├── search
│   └── ClickHouseSearchCondition.java    # 查询条件封装类
└── utils
    ├── ClickHouseSearchConditionUtil.java # 查询条件转换工具类
    └── ClickHouseSqlUtil.java            # SQL 构建工具类
```

## 12. 最佳实践

1. **合理设置连接池大小**：ClickHouse 适合少量长连接，不建议 `maxPoolSize` 设置过大。一般 10~30 即可满足需求。
2. **批量写入优先**：ClickHouse 对高频小量写入不友好，请尽量使用 `insertBatch()` 积攒数据后批量写入，建议单批次 1000~5000 条。
3. **善用相对时间**：查询近期数据时，使用相对时间表达式（如 `-1d`、`-7d`）比拼接绝对时间字符串更简洁，且自动适配服务端时间。
4. **ReplacingMergeTree 配合 FINAL**：若表引擎为 `ReplacingMergeTree`，查询时设置 `useFinal = true` 确保获取去重后的最新数据。
5. **避免频繁 DELETE / UPDATE**：ClickHouse 的删除和更新是 `ALTER TABLE` 异步操作，不适合高频使用，应以追加写入为主。
6. **原生 SQL 兜底**：对于复杂查询（如子查询、JOIN、窗口函数），使用 `executeQuery()` 或 `executeQueryForMap()` 执行原生 SQL。
7. **注解映射简化代码**：为实体类添加 `@ClickHouseTable` 和 `@ClickHouseColumn` 注解，可免去手写 SQL 中表名和列名的映射工作。
