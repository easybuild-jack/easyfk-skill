# orm-sharding 开发手册

## 1. 模块概述

`orm-sharding` 是 EasyFK 框架中基于 Apache ShardingSphere JDBC 的分库分表组件。该模块作为依赖传递层，将 ShardingSphere JDBC（`ShardingSphereDriver`，5.5.3）及常用功能插件集成到框架体系中，配合 `orm-mybatis` 或 `orm-flex` 使用，为应用提供**透明化的分库分表、读写分离、数据加密和分布式事务**能力，业务代码无需任何改动。

## 2. 依赖引入

### Maven

```xml
<dependency>
    <groupId>com.mcst</groupId>
    <artifactId>orm-sharding</artifactId>
</dependency>
```

### Gradle

```gradle
dependencies {
    implementation 'com.mcst:orm-sharding'
}
```

> 版本号由框架统一 BOM 管理，无需手动指定。

该模块会自动传递引入以下依赖（ShardingSphere 5.5.3）：
- `shardingsphere-jdbc` — ShardingSphere JDBC 驱动（`org.apache.shardingsphere.driver.ShardingSphereDriver`）
- `shardingsphere-infra-url-classpath` / `shardingsphere-infra-url-absolutepath` — 支持 `jdbc:shardingsphere:classpath:` 与 `jdbc:shardingsphere:absolutepath:` 两种 URL
- `shardingsphere-infra-data-source-pool-hikari` — HikariCP 数据源创建
- `shardingsphere-authority-simple` — 默认权限实现（`ALL_PERMITTED`）
- `shardingsphere-standalone-mode-repository-memory` / `shardingsphere-standalone-mode-repository-jdbc` — 单机模式元数据持久化
- `shardingsphere-jdbc-dialect-mysql` / `shardingsphere-jdbc-dialect-postgresql` — MySQL、PostgreSQL 方言
- `shardingsphere-sharding-core`、`shardingsphere-broadcast-core`、`shardingsphere-readwrite-splitting-core`、`shardingsphere-encrypt-core`、`shardingsphere-mask-core`、`shardingsphere-shadow-core` — 分片、广播表、读写分离、加密、脱敏、影子库

> **说明**：`shardingsphere-jdbc-core-spring-boot-starter` 自 5.3.0 起已停止发布，`spring.shardingsphere.*` 配置前缀随之废弃。
> 自 5.5.3 起 ShardingSphere 的功能与数据库类型均为可插拔模块，Oracle、SQLServer 等其它数据库需自行引入对应的 `shardingsphere-jdbc-dialect-xxx`；
> ZooKeeper/etcd 集群模式、XA（Atomikos/Narayana）、Seata AT 等可选插件同理，参见 [Optional Plugins](https://shardingsphere.apache.org/document/current/en/user-manual/shardingsphere-jdbc/optional-plugins/)。

> **注意**：`orm-sharding` 通常与 `orm-mybatis` 或 `orm-flex` 配合使用，需同时引入 ORM 组件。

## 3. 工作原理

ShardingSphere JDBC 作为 JDBC 增强驱动，工作在应用层与数据库之间：

```
应用代码 → MyBatis-Plus / MyBatis-Flex → ShardingSphere JDBC → 实际数据源
```

- 对上层应用完全透明，无需修改 SQL 或业务代码
- 通过 YAML 规则文件即可实现分库分表、读写分离等能力
- 以 JDBC 驱动方式接入：Spring Boot 的 `spring.datasource` 指向 `ShardingSphereDriver` 和规则文件，由 Boot 默认的 HikariCP 包装 ShardingSphere 逻辑数据源
- 与框架的 `BaseMyBatisRepositoryImpl` / `BaseFlexRepositoryImpl` 无缝兼容

## 4. 配置说明

### 4.1 接入方式

在 `application.yml` 中将数据源驱动指定为 `ShardingSphereDriver`，URL 指向 classpath 下的规则文件（也可用 `jdbc:shardingsphere:absolutepath:/path/to/sharding.yaml` 指向文件系统路径）：

```yaml
spring:
  datasource:
    driver-class-name: org.apache.shardingsphere.driver.ShardingSphereDriver
    url: jdbc:shardingsphere:classpath:sharding.yaml
```

规则文件（如 `src/main/resources/sharding.yaml`）的整体结构：

```yaml
databaseName: sharding_db   # 逻辑库名，默认 logic_db
mode:                       # 运行模式，缺省为 Standalone
dataSources:                # 真实数据源
rules:                      # 规则列表，以 !SHARDING、!READWRITE_SPLITTING、!ENCRYPT 等标签声明
props:                      # 属性配置
```

> **注意**：规则文件使用 ShardingSphere 原生 YAML 格式（驼峰命名，如 `actualDataNodes`、`shardingColumn`），
> 与旧版 starter 的 `spring.shardingsphere.*`（短横线命名）不通用，升级时需整体迁移。
> 行表达式推荐使用 `${...}`，旧写法 `$->{...}` 仍然兼容。
> ShardingSphere 在启动时加载真实表的元数据，分片涉及的物理表需要提前创建。
> 5.4 起未分片的单表不再自动加载，读写分离、数据加密等场景下的普通表必须通过 `!SINGLE` 规则声明（见 4.7），否则会出现路由到错误数据源、加密列不改写等问题。

### 4.2 分库分表配置

```yaml
databaseName: sharding_db
mode:
  type: Standalone
  repository:
    type: JDBC
dataSources:
  ds_0:
    dataSourceClassName: com.zaxxer.hikari.HikariDataSource
    driverClassName: com.mysql.cj.jdbc.Driver
    jdbcUrl: jdbc:mysql://192.168.1.100:3306/db_order_0
    username: root
    password: root
  ds_1:
    dataSourceClassName: com.zaxxer.hikari.HikariDataSource
    driverClassName: com.mysql.cj.jdbc.Driver
    jdbcUrl: jdbc:mysql://192.168.1.101:3306/db_order_1
    username: root
    password: root
rules:
- !SHARDING
  tables:
    t_order:
      actualDataNodes: ds_${0..1}.t_order_${0..3}
      databaseStrategy:
        standard:
          shardingColumn: user_id
          shardingAlgorithmName: db-inline
      tableStrategy:
        standard:
          shardingColumn: order_id
          shardingAlgorithmName: table-inline
      keyGenerateStrategy:
        column: order_id
        keyGeneratorName: snowflake
  shardingAlgorithms:
    db-inline:
      type: INLINE
      props:
        algorithm-expression: ds_${user_id % 2}
    table-inline:
      type: INLINE
      props:
        algorithm-expression: t_order_${order_id % 4}
  keyGenerators:
    snowflake:
      type: SNOWFLAKE
props:
  sql-show: true  # 开发环境显示路由后的 SQL
```

> **注意**：`MOD`、`HASH_MOD`、`VOLUME_RANGE`、`BOUNDARY_RANGE`、`AUTO_INTERVAL` 属于自动分片算法，只能用于 `autoTables`；
> 在 `tables`（配合 `actualDataNodes`）中使用会在启动时报 `can not use auto sharding algorithm`。

使用自动分片算法时，由 ShardingSphere 根据 `sharding-count` 自动计算真实表（`t_order_0` ~ `t_order_3`）在数据源间的分布：

```yaml
rules:
- !SHARDING
  autoTables:
    t_order:
      actualDataSources: ds_${0..1}
      shardingStrategy:
        standard:
          shardingColumn: order_id
          shardingAlgorithmName: auto-hash-mod
  shardingAlgorithms:
    auto-hash-mod:
      type: HASH_MOD
      props:
        sharding-count: 4
```

### 4.3 读写分离配置

```yaml
dataSources:
  write_ds:
    dataSourceClassName: com.zaxxer.hikari.HikariDataSource
    driverClassName: com.mysql.cj.jdbc.Driver
    jdbcUrl: jdbc:mysql://192.168.1.100:3306/mydb
    username: root
    password: root
  read_ds_0:
    dataSourceClassName: com.zaxxer.hikari.HikariDataSource
    driverClassName: com.mysql.cj.jdbc.Driver
    jdbcUrl: jdbc:mysql://192.168.1.101:3306/mydb
    username: root
    password: root
  read_ds_1:
    dataSourceClassName: com.zaxxer.hikari.HikariDataSource
    driverClassName: com.mysql.cj.jdbc.Driver
    jdbcUrl: jdbc:mysql://192.168.1.102:3306/mydb
    username: root
    password: root
rules:
- !READWRITE_SPLITTING
  dataSourceGroups:
    readwrite_ds:
      writeDataSourceName: write_ds
      readDataSourceNames:
        - read_ds_0
        - read_ds_1
      transactionalReadQueryStrategy: PRIMARY  # 事务内读请求走主库
      loadBalancerName: round-robin
  loadBalancers:
    round-robin:
      type: ROUND_ROBIN
- !SINGLE
  tables:
    - "*.*"   # 加载读写分离逻辑数据源中的全部单表
```

### 4.4 分库分表 + 读写分离组合配置

```yaml
dataSources:
  # write_ds_0, write_ds_1, read_ds_0_0, read_ds_0_1, read_ds_1_0, read_ds_1_1 配置省略
rules:
- !SHARDING
  tables:
    t_order:
      actualDataNodes: readwrite_ds_${0..1}.t_order_${0..3}
      databaseStrategy:
        standard:
          shardingColumn: user_id
          shardingAlgorithmName: db-inline
      tableStrategy:
        standard:
          shardingColumn: order_id
          shardingAlgorithmName: table-inline
  shardingAlgorithms:
    db-inline:
      type: INLINE
      props:
        algorithm-expression: readwrite_ds_${user_id % 2}
    table-inline:
      type: INLINE
      props:
        algorithm-expression: t_order_${order_id % 4}
- !READWRITE_SPLITTING
  dataSourceGroups:
    readwrite_ds_0:
      writeDataSourceName: write_ds_0
      readDataSourceNames: [read_ds_0_0, read_ds_0_1]
      loadBalancerName: round-robin
    readwrite_ds_1:
      writeDataSourceName: write_ds_1
      readDataSourceNames: [read_ds_1_0, read_ds_1_1]
      loadBalancerName: round-robin
  loadBalancers:
    round-robin:
      type: ROUND_ROBIN
```

### 4.5 数据加密配置

```yaml
rules:
- !ENCRYPT
  tables:
    t_user:
      columns:
        phone:
          cipher:
            name: phone_cipher
            encryptorName: aes-encryptor
        id_card:
          cipher:
            name: id_card_cipher
            encryptorName: aes-encryptor
  encryptors:
    aes-encryptor:
      type: AES
      props:
        aes-key-value: my-secret-key-1234
        digest-algorithm-name: SHA-1
- !SINGLE
  tables:
    - "*.*"   # t_user 未分片时需作为单表加载，加密规则才能生效
```

> 内置加密算法为 `AES`（可逆加密）与 `MD5`（辅助查询列），SM3/SM4 等国密算法已移至 ShardingSphere Plugin 仓库，需要时自行引入。

### 4.6 广播表配置

所有库中数据完全一致的字典表，5.4 起由独立的 `!BROADCAST` 规则声明（不再写在 `!SHARDING` 的 `broadcastTables` 中）：

```yaml
rules:
- !BROADCAST
  tables:
    - t_dict
```

### 4.7 单表配置

未参与分片的表称为单表，5.4 起需显式声明需要加载的单表：

```yaml
rules:
- !SINGLE
  tables:
    - "*.*"          # 加载全部数据源的全部单表
    # - ds_0.t_user  # 或按 数据源.表名 精确声明
    # - ds_0.*       # 或加载指定数据源的全部单表
```

## 5. 常用分片算法

| 算法类型 | 说明 | 适用场景 |
|----------|------|----------|
| `HASH_MOD` | 哈希取模（自动分片，仅 `autoTables`） | 均匀分布，推荐 |
| `MOD` | 直接取模（自动分片，仅 `autoTables`） | 数字类型主键 |
| `VOLUME_RANGE` | 基于容量的范围分片（自动分片，仅 `autoTables`） | 按数据量分片 |
| `BOUNDARY_RANGE` | 基于边界的范围分片（自动分片，仅 `autoTables`） | 按 ID 范围分片 |
| `AUTO_INTERVAL` | 自动间隔分片（自动分片，仅 `autoTables`） | 按时间分片 |
| `INTERVAL` | 时间范围分片 | 按固定时间间隔分片 |
| `INLINE` | 行表达式 | 灵活自定义 |
| `COMPLEX_INLINE` | 复合行表达式 | 多分片键 |
| `HINT_INLINE` | Hint 行表达式 | 强制路由 |
| `CLASS_BASED` | 自定义类 | 自定义分片算法 |

### 行表达式示例

```yaml
shardingAlgorithms:
  inline-order:
    type: INLINE
    props:
      algorithm-expression: t_order_${order_id % 4}
```

## 6. 主键生成策略

| 策略 | 说明 |
|------|------|
| `SNOWFLAKE` | 雪花算法（推荐），分布式唯一 ID |
| `UUID` | UUID 字符串 |

> NanoID、CosId 等主键生成算法已移至 ShardingSphere Plugin 仓库，内置仅保留 `SNOWFLAKE` 与 `UUID`。

```yaml
keyGenerators:
  snowflake:
    type: SNOWFLAKE
    props:
      worker-id: 1
      max-vibration-offset: 3  # 主键同时作为分片键时建议配置为 (2^n)-1，避免取模分布不均
```

## 7. 与 ORM 组件配合使用

### 7.1 与 orm-mybatis 配合

```java
// 实体类无需任何修改
@Data
@TableName("t_order")
@EqualsAndHashCode(callSuper = true)
public class OrderPO extends BaseMyBatisPlusEntity<OrderPO> {
    @TableId(type = IdType.ASSIGN_ID)  // 使用 ShardingSphere 分配 ID
    private Long orderId;
    private Long userId;
    private BigDecimal amount;
}

// Repository 无需任何修改
@Repository
public class OrderRepository extends BaseMyBatisRepositoryImpl<OrderMapper, OrderDTO, OrderPO, Long> {
}

// 使用方式完全不变
OrderDTO order = orderRepository.queryById(1L);
orderRepository.insert(orderDTO);
// ShardingSphere 自动路由到正确的库和表
```

### 7.2 与 orm-flex 配合

```java
@Data
@Table("t_order")
@EqualsAndHashCode(callSuper = true)
public class OrderPO extends BaseFlexEntity<OrderPO> {
    @Id(keyType = KeyType.None)  // 由 ShardingSphere 生成 ID
    private Long orderId;
    private Long userId;
    private BigDecimal amount;
}

@Repository
public class OrderRepository extends BaseFlexRepositoryImpl<OrderMapper, OrderDTO, OrderPO, Long> {
}
```

## 8. 常用属性配置

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `sql-show` | `false` | 是否打印路由后的 SQL（开发环境推荐开启） |
| `sql-simple` | `false` | 是否简化 SQL 输出 |
| `max-connections-size-per-query` | `1` | 每个查询最大连接数 |
| `check-table-metadata-enabled` | `false` | 是否检查表元数据一致性 |
| `kernel-executor-size` | `infinite` | 内核执行器线程数 |

以上属性配置在规则文件的 `props` 节点下：

```yaml
props:
  sql-show: true
  max-connections-size-per-query: 2
  check-table-metadata-enabled: true
```

> 5.5.3 起 SQL 日志的 logger 名称由 `ShardingSphere-SQL` 改为 `org.apache.shardingsphere.sql`，日志配置需同步调整。

## 9. 最佳实践

1. **分片键选择**：选择高基数、查询频率高的字段作为分片键（如 `user_id`、`order_id`），避免使用更新频繁的字段。
2. **分片算法**：推荐使用 `HASH_MOD`（`autoTables`）或 `INLINE`（`tables`），数据分布均匀；范围查询多时可考虑 `BOUNDARY_RANGE`。
3. **主键策略**：分库分表场景推荐使用 `SNOWFLAKE` 雪花算法生成全局唯一 ID。
4. **避免跨片查询**：查询条件尽量包含分片键，避免全库扫描。
5. **绑定表**：有关联关系的表使用相同的分片策略和分片键，避免跨片 JOIN。
6. **读写分离**：生产环境建议配合读写分离，分散读压力。
7. **开发调试**：开发环境开启 `sql-show: true`，查看实际路由的 SQL。
8. **ID 类型**：使用 ShardingSphere 主键生成时，MyBatis-Plus 的 `@TableId` 设为 `IdType.ASSIGN_ID` 或 `IdType.INPUT`。
9. **事务注意**：跨库事务需要分布式事务支持，ShardingSphere 支持 XA 和 BASE 两种模式，需额外引入 `shardingsphere-transaction-xa-atomikos` / `shardingsphere-transaction-xa-narayana` 或 `shardingsphere-transaction-base-seata-at`。
