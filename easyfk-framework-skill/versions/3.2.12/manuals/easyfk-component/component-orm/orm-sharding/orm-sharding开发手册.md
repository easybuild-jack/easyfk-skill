# orm-sharding 开发手册

## 1. 模块概述

`orm-sharding` 是 EasyFK 框架中基于 Apache ShardingSphere JDBC 的分库分表组件。该模块作为依赖传递层，将 ShardingSphere JDBC Spring Boot Starter 集成到框架体系中，配合 `orm-mybatis` 或 `orm-flex` 使用，为应用提供**透明化的分库分表、读写分离、数据加密和分布式事务**能力，业务代码无需任何改动。

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

该模块会自动传递引入以下依赖：
- `shardingsphere-jdbc-core-spring-boot-starter` — Apache ShardingSphere JDBC 核心

> **注意**：`orm-sharding` 通常与 `orm-mybatis` 或 `orm-flex` 配合使用，需同时引入 ORM 组件。

## 3. 工作原理

ShardingSphere JDBC 作为 JDBC 增强驱动，工作在应用层与数据库之间：

```
应用代码 → MyBatis-Plus / MyBatis-Flex → ShardingSphere JDBC → 实际数据源
```

- 对上层应用完全透明，无需修改 SQL 或业务代码
- 通过 YAML 配置即可实现分库分表、读写分离等能力
- 与框架的 `BaseMyBatisRepositoryImpl` / `BaseFlexRepositoryImpl` 无缝兼容

## 4. 配置说明

### 4.1 分库分表配置

```yaml
spring:
  shardingsphere:
    mode:
      type: Standalone
      repository:
        type: JDBC
    datasource:
      names: ds0,ds1
      ds0:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://192.168.1.100:3306/db_order_0
        username: root
        password: root
      ds1:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://192.168.1.101:3306/db_order_1
        username: root
        password: root
    rules:
      sharding:
        tables:
          t_order:
            actual-data-nodes: ds$->{0..1}.t_order_$->{0..3}
            database-strategy:
              standard:
                sharding-column: user_id
                sharding-algorithm-name: db-hash-mod
            table-strategy:
              standard:
                sharding-column: order_id
                sharding-algorithm-name: table-hash-mod
            key-generate-strategy:
              column: order_id
              key-generator-name: snowflake
        sharding-algorithms:
          db-hash-mod:
            type: HASH_MOD
            props:
              sharding-count: 2
          table-hash-mod:
            type: HASH_MOD
            props:
              sharding-count: 4
        key-generators:
          snowflake:
            type: SNOWFLAKE
    props:
      sql-show: true  # 开发环境显示路由后的 SQL
```

### 4.2 读写分离配置

```yaml
spring:
  shardingsphere:
    datasource:
      names: master,slave0,slave1
      master:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://192.168.1.100:3306/mydb
        username: root
        password: root
      slave0:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://192.168.1.101:3306/mydb
        username: root
        password: root
      slave1:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://192.168.1.102:3306/mydb
        username: root
        password: root
    rules:
      readwrite-splitting:
        data-sources:
          readwrite_ds:
            write-data-source-name: master
            read-data-source-names:
              - slave0
              - slave1
            load-balancer-name: round-robin
        load-balancers:
          round-robin:
            type: ROUND_ROBIN
```

### 4.3 分库分表 + 读写分离组合配置

```yaml
spring:
  shardingsphere:
    datasource:
      names: master0,master1,slave0_0,slave0_1,slave1_0,slave1_1
      # ... 数据源配置省略
    rules:
      sharding:
        tables:
          t_order:
            actual-data-nodes: readwrite_ds_$->{0..1}.t_order_$->{0..3}
            database-strategy:
              standard:
                sharding-column: user_id
                sharding-algorithm-name: db-hash-mod
            table-strategy:
              standard:
                sharding-column: order_id
                sharding-algorithm-name: table-hash-mod
        sharding-algorithms:
          db-hash-mod:
            type: HASH_MOD
            props:
              sharding-count: 2
          table-hash-mod:
            type: HASH_MOD
            props:
              sharding-count: 4
      readwrite-splitting:
        data-sources:
          readwrite_ds_0:
            write-data-source-name: master0
            read-data-source-names: [slave0_0, slave0_1]
            load-balancer-name: round-robin
          readwrite_ds_1:
            write-data-source-name: master1
            read-data-source-names: [slave1_0, slave1_1]
            load-balancer-name: round-robin
        load-balancers:
          round-robin:
            type: ROUND_ROBIN
```

### 4.4 数据加密配置

```yaml
spring:
  shardingsphere:
    rules:
      encrypt:
        tables:
          t_user:
            columns:
              phone:
                cipher-column: phone_cipher
                encryptor-name: aes-encryptor
              id_card:
                cipher-column: id_card_cipher
                encryptor-name: aes-encryptor
        encryptors:
          aes-encryptor:
            type: AES
            props:
              aes-key-value: my-secret-key-1234
```

## 5. 常用分片算法

| 算法类型 | 说明 | 适用场景 |
|----------|------|----------|
| `HASH_MOD` | 哈希取模 | 均匀分布，推荐 |
| `MOD` | 直接取模 | 数字类型主键 |
| `VOLUME_RANGE` | 基于容量的范围分片 | 按数据量分片 |
| `BOUNDARY_RANGE` | 基于边界的范围分片 | 按 ID 范围分片 |
| `AUTO_INTERVAL` | 自动间隔分片 | 按时间分片 |
| `INLINE` | 行表达式 | 灵活自定义 |

### 行表达式示例

```yaml
sharding-algorithms:
  inline-order:
    type: INLINE
    props:
      algorithm-expression: t_order_$->{order_id % 4}
```

## 6. 主键生成策略

| 策略 | 说明 |
|------|------|
| `SNOWFLAKE` | 雪花算法（推荐），分布式唯一 ID |
| `UUID` | UUID 字符串 |
| `NANOID` | NanoID |

```yaml
key-generators:
  snowflake:
    type: SNOWFLAKE
    props:
      worker-id: 1
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

```yaml
spring:
  shardingsphere:
    props:
      sql-show: true
      max-connections-size-per-query: 2
      check-table-metadata-enabled: true
```

## 9. 最佳实践

1. **分片键选择**：选择高基数、查询频率高的字段作为分片键（如 `user_id`、`order_id`），避免使用更新频繁的字段。
2. **分片算法**：推荐使用 `HASH_MOD`，数据分布均匀；范围查询多时可考虑 `BOUNDARY_RANGE`。
3. **主键策略**：分库分表场景推荐使用 `SNOWFLAKE` 雪花算法生成全局唯一 ID。
4. **避免跨片查询**：查询条件尽量包含分片键，避免全库扫描。
5. **绑定表**：有关联关系的表使用相同的分片策略和分片键，避免跨片 JOIN。
6. **读写分离**：生产环境建议配合读写分离，分散读压力。
7. **开发调试**：开发环境开启 `sql-show: true`，查看实际路由的 SQL。
8. **ID 类型**：使用 ShardingSphere 主键生成时，MyBatis-Plus 的 `@TableId` 设为 `IdType.ASSIGN_ID` 或 `IdType.INPUT`。
9. **事务注意**：跨库事务需要分布式事务支持，ShardingSphere 支持 XA 和 BASE 两种模式。
