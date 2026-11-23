# Cache-Redis 分布式缓存组件 — 开发手册

> 基于 Spring Cache + Redis 的分布式缓存自动配置组件，提供**注解驱动 + 编程式**双模式的 Redis 缓存能力，支持多缓存空间独立 TTL 配置。

---

## 目录

- [一、组件概述](#一组件概述)
  - [1.1 功能简介](#11-功能简介)
  - [1.2 依赖关系](#12-依赖关系)
  - [1.3 源码结构](#13-源码结构)
- [二、快速开始](#二快速开始)
  - [2.1 引入依赖](#21-引入依赖)
  - [2.2 基础配置](#22-基础配置)
  - [2.3 使用示例](#23-使用示例)
- [三、配置详解](#三配置详解)
  - [3.1 cache-redis 配置项](#31-cache-redis-配置项)
  - [3.2 多缓存空间独立 TTL](#32-多缓存空间独立-ttl)
  - [3.3 多数据源场景（进阶）](#33-多数据源场景进阶)
- [四、核心组件详解](#四核心组件详解)
  - [4.1 RedisCacheConfig 自动配置](#41-rediscacheconfig-自动配置)
  - [4.2 RedisCacheManager（注解驱动）](#42-rediscachemanager注解驱动)
  - [4.3 ICacheService / RedisCacheServiceImpl（编程式操作）](#43-icacheservice--rediscacheserviceimpl编程式操作)
- [五、使用方式](#五使用方式)
  - [5.1 Spring Cache 注解方式](#51-spring-cache-注解方式)
  - [5.2 编程式缓存操作（ICacheService）](#52-编程式缓存操作icacheservice)
- [六、注意事项](#六注意事项)

---

## 一、组件概述

### 1.1 功能简介

`cache-redis` 组件是 EasyFK 框架的分布式 Redis 缓存方案，提供两种使用模式：

1. **注解驱动模式**：通过 `@Cacheable`、`@CachePut`、`@CacheEvict` 等 Spring Cache 标准注解声明式管理缓存
2. **编程式模式**：通过 `ICacheService` 接口直接进行缓存的增删查改操作

核心特性：
- 基于 Spring Boot `@AutoConfiguration` 自动配置 `RedisCacheManager`，引入即用
- 通过 `@EnableCaching` 自动启用 Spring Cache 注解支持
- 支持为不同缓存空间（cacheName）配置独立的 TTL
- Key 使用 `StringRedisSerializer` 序列化，Value 使用 `SmartRedisSerializer`（跟随 `db-redis` 全局 `redis-serializer` 配置）
- 默认禁止缓存 `null` 值（`disableCachingNullValues`）

### 1.2 依赖关系

```
cache-redis
├── easyfk-cache（缓存接口层，定义 ICacheService）
└── db-redis（Redis 连接管理，提供 RedisConnectionManager、RedisOptManager、RedisArgsHelper 等）
```

对应 `build.gradle`：

```groovy
dependencies {
    api('com.mcst:easyfk-cache')
    api project(':component-db:db-redis')
}
```

### 1.3 源码结构

```
cache-redis/src/main/java/com/mcst/easyfk/cache/redis/
├── config/
│   ├── RedisCacheConfig.java         # 自动配置类，注册 RedisCacheManager 和 ICacheService Bean
│   └── RedisDefinedInfo.java         # 单个缓存空间配置（cacheName + timeToLive）
├── properties/
│   └── RedisCacheProperties.java     # 配置属性类（prefix: easyfk.config.cache.redis）
└── RedisCacheServiceImpl.java        # ICacheService 的 Redis 实现
```

---

## 二、快速开始

### 2.1 引入依赖

**Gradle 方式**：

```groovy
dependencies {
    implementation("com.mcst:cache-redis")
}
```

**Maven 方式**：

```xml
<dependency>
    <groupId>com.mcst</groupId>
    <artifactId>cache-redis</artifactId>
</dependency>
```

> 版本由 EasyFK BOM 统一管理，无需手动指定版本号。

### 2.2 基础配置

默认情况下，使用 Spring Boot 标准的 Redis 配置即可：

```yaml
# Spring Redis 标准配置
spring:
  data:
    redis:
      host: 127.0.0.1
      port: 6379
      password: your-password
      database: 0

# cache-redis 缓存配置
easyfk:
  config:
    cache:
      redis:
        time-to-live: 30m                  # 全局默认 TTL
```

> 如需多数据源支持，可通过 `db-redis` 组件的自定义配置指定缓存使用的数据源，详见 [3.3 多数据源场景（进阶）](#33-多数据源场景进阶)。

### 2.3 使用示例

**注解方式**：

```java
@Service
public class UserService {

    @Cacheable(value = "users", key = "#userId")
    public UserDTO getUserById(Long userId) {
        return userMapper.selectById(userId);
    }
}
```

**编程方式**：

```java
@Service
public class UserService {

    @Resource
    private ICacheService cacheService;

    public UserDTO getUserById(Long userId) {
        String key = "user:" + userId;
        // namespace 参数为命名空间，作为 Key 前缀隔离（最终 Redis key 为 namespace::key）
        UserDTO user = cacheService.queryByKey(key, "user-ns");
        if (user != null) {
            return user;
        }
        user = userMapper.selectById(userId);
        if (user != null) {
            cacheService.cacheObject(key, user, Duration.ofMinutes(30), "user-ns");
        }
        return user;
    }
}
```

---

## 三、配置详解

### 3.1 cache-redis 配置项

配置前缀：`easyfk.config.cache.redis`

对应属性类：`RedisCacheProperties`

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `datasource` | String | `default` | Redis 数据源名称（对应 `db-redis` 中 `datasource` 下配置的数据源 key） |
| `database-name` | String | `default` | Redis 数据库别名（对应数据源配置中 `databases` Map 的 key） |
| `time-to-live` | Duration | `0`（永不过期） | 全局默认缓存过期时间 |
| `caches` | List\<RedisDefinedInfo\> | （空） | 自定义缓存空间配置列表 |

**Duration 格式示例**：
- `30m` — 30 分钟
- `2h` — 2 小时
- `1d` — 1 天
- `0` — 永不过期

### 3.2 多缓存空间独立 TTL

通过 `caches` 配置为每个缓存空间设置独立的 TTL。

对应属性类：`RedisDefinedInfo`

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `cache-name` | String | — | 缓存空间名称，对应 `@Cacheable(value = "xxx")` |
| `time-to-live` | Duration | `30m` | 该缓存空间的过期时间 |

```yaml
easyfk:
  config:
    cache:
      redis:
        time-to-live: 30m
        caches:
          - cache-name: users
            time-to-live: 2h
          - cache-name: verify-code
            time-to-live: 5m
          - cache-name: dict
            time-to-live: 1d
```

> **重要行为说明**：当配置了 `caches` 列表时，`RedisCacheManager` 仅对列表中声明的缓存空间应用自定义 TTL 配置（基于全局配置 `config.entryTtl(info.getTimeToLive())` 创建），**不会**对 `caches` 之外的缓存空间设置 `cacheDefaults`。如果使用了 `caches` 中未声明的缓存名称，该缓存空间将使用 Spring Cache 的默认行为（无 TTL，允许缓存 null 值）。
>
> 当**未配置** `caches` 时，全局配置（包含 `time-to-live`、序列化器、禁止缓存 null 值）将通过 `cacheDefaults` 应用到所有缓存空间，并启用事务感知（`transactionAware`）。

### 3.3 多数据源场景（进阶）

默认情况下，使用 Spring Boot 标准 Redis 配置（`spring.data.redis.*`）即可，无需额外配置数据源。

当需要**多 Redis 数据源**时，可通过 `db-redis` 组件的自定义配置（`easyfk.config.db.redis`）管理多个数据源，并在 `cache-redis` 中通过 `datasource` + `database-name` 指定缓存使用哪个数据源和数据库。

```yaml
easyfk:
  config:
    db:
      redis:
        redis-serializer: FastJSON           # 序列化器，可选：DEFAULT / FastJSON / KRYO
        default-data-source: default
        datasource:
          default:
            host: 127.0.0.1
            port: 6379
            password: your-password
            database: 0
            databases:
              default: 0
              cache-db: 1                    # 数据库别名 cache-db → 索引 1

    cache:
      redis:
        datasource: default                  # 指定使用 db-redis 中的数据源名称
        database-name: cache-db              # 指定使用数据源中别名为 cache-db 的库（索引 1）
        time-to-live: 30m
        caches:
          - cache-name: users
            time-to-live: 2h
          - cache-name: verify-code
            time-to-live: 5m
```

**说明**：
- `datasource` 和 `database-name` 的默认值均为 `default`，单数据源场景下无需配置
- `database-name` 对应数据源配置中 `databases` Map 的 key（别名），而不是 Redis 数据库索引数字

---

## 四、核心组件详解

### 4.1 RedisCacheConfig 自动配置

`RedisCacheConfig` 是本组件的自动配置入口，通过 Spring Boot `@AutoConfiguration` 机制注册。

注册路径：`META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`

```
com.mcst.easyfk.cache.redis.config.RedisCacheConfig
```

该配置类完成以下工作：
- 标注 `@EnableCaching`，启用 Spring Cache 注解支持
- 绑定 `RedisCacheProperties` 配置属性
- 注入 `RedisProperties`（db-redis 全局配置，用于获取序列化器类型）
- 注入 `RedisConnectionManager`（db-redis 连接管理器，用于获取 `RedisConnectionFactory`）
- 注册 `RedisCacheManager` Bean
- 注册 `ICacheService` Bean（实现类 `RedisCacheServiceImpl`）

### 4.2 RedisCacheManager（注解驱动）

组件自动配置的 `RedisCacheManager` 作为 Spring Cache 的缓存管理器，支持 `@Cacheable`、`@CachePut`、`@CacheEvict` 等标准注解。

**Bean 特性**：
- `@Primary`：当存在多个 `CacheManager` 时默认使用此实例
- `@Lazy`：延迟初始化，确保 `RedisConnectionManager` 在 `@PostConstruct` 阶段完成连接工厂初始化后再创建
- `@ConditionalOnMissingBean`：允许业务项目自定义覆盖

**基础 RedisCacheConfiguration**：

```
defaultCacheConfig()
  → entryTtl(全局 time-to-live)
  → serializeValuesWith(SmartRedisSerializer，类型由 db-redis 的 redis-serializer 决定)
  → serializeKeysWith(StringRedisSerializer)
  → disableCachingNullValues()
```

**构建逻辑**：

- **配置了 `caches` 列表时**：遍历列表，为每个 `cacheName` 创建独立的 `RedisCacheConfiguration`（在基础配置上覆盖 `entryTtl`），通过 `initialCacheNames` + `withInitialCacheConfigurations` 构建。未在列表中声明的缓存名称使用 Spring 默认行为。
- **未配置 `caches` 时**：通过 `cacheDefaults(config)` 将基础配置应用到所有缓存空间，并启用 `transactionAware()`。

### 4.3 ICacheService / RedisCacheServiceImpl（编程式操作）

`ICacheService` 是 EasyFK 缓存抽象接口（来自 `easyfk-cache` 依赖），`RedisCacheServiceImpl` 为其 Redis 实现。

内部通过 `RedisArgsHelper.createKeyArgs(datasource, databaseName, key, namespace)` 创建 `KeyArgs` 参数对象，再委托给 `RedisOptManager` 执行实际的 Redis 操作。所有操作自动路由到 `RedisCacheProperties` 配置的 `datasource` + `databaseName` 指定的 Redis 实例。

**Key 组装规则**：最终存入 Redis 的 Key 格式为 `namespace::key`（由 `RedisUtil.wrapKey()` 实现，分隔符为 `::`）。

#### API 一览

| 方法签名 | 返回值 | 说明 |
|---------|--------|------|
| `cacheObject(String key, Object value, String namespace)` | `BaseResult<?>` | 写入缓存（永不过期） |
| `cacheObject(String key, Object value, Duration times, String namespace)` | `BaseResult<?>` | 写入缓存（指定过期时间） |
| `queryByKey(String key, String namespace)` | `<T> T` | 查询缓存值 |
| `existKey(String key, String namespace)` | `boolean` | 判断 Key 是否存在 |
| `removeKey(String key, String namespace)` | `BaseResult<?>` | 删除缓存 |
| `expireKey(String key, Duration times, String namespace)` | `void` | 设置/更新过期时间 |
| `expireKeyAt(String key, Date date, String namespace)` | `void` | 设置到期时间点 |
| `getKeyExpire(String key, String namespace)` | `long` | 获取剩余过期时间（秒），不存在或永不过期返回 -1 |
| `getSetCountByKey(String pattern, String namespace)` | `Long` | 获取 Set 集合大小 |

**参数说明**：

- `key`：缓存键，由业务自行定义
- `namespace`：命名空间，作为 Key 前缀实现数据隔离（最终 Redis Key = `namespace::key`）
- `times`：`java.time.Duration` 类型的过期时间
- `namespace`、`key`、`datasource`、`databaseName` 均不允许为空，否则 `RedisArgsHelper` 会抛出 `RuntimeException`

---

## 五、使用方式

### 5.1 Spring Cache 注解方式

**基础查询缓存**：

```java
@Service
public class ProductService {

    @Cacheable(value = "products", key = "#productId")
    public ProductDTO getProduct(Long productId) {
        return productMapper.selectById(productId);
    }

    @CachePut(value = "products", key = "#product.id")
    public ProductDTO updateProduct(ProductDTO product) {
        productMapper.updateById(product);
        return product;
    }

    @CacheEvict(value = "products", key = "#productId")
    public void deleteProduct(Long productId) {
        productMapper.deleteById(productId);
    }

    @CacheEvict(value = "products", allEntries = true)
    public void refreshAllProducts() {
        // 清空整个 products 缓存空间
    }
}
```

注解中 `value` 对应 YAML 中 `caches` 列表里的 `cache-name`，例如：

```yaml
caches:
  - cache-name: products       # ← 对应 @Cacheable(value = "products")
    time-to-live: 30m
```

### 5.2 编程式缓存操作（ICacheService）

```java
@Service
public class OrderService {

    @Resource
    private ICacheService cacheService;

    private static final String NS = "order";

    // 写入缓存（永不过期）
    public void cacheOrder(String orderId, OrderDTO order) {
        cacheService.cacheObject(orderId, order, NS);
    }

    // 写入缓存（指定 TTL）
    public void cacheOrderWithTtl(String orderId, OrderDTO order) {
        cacheService.cacheObject(orderId, order, Duration.ofMinutes(30), NS);
    }

    // 查询缓存
    public OrderDTO getOrder(String orderId) {
        return cacheService.queryByKey(orderId, NS);
    }

    // 判断 Key 是否存在
    public boolean orderExists(String orderId) {
        return cacheService.existKey(orderId, NS);
    }

    // 删除缓存
    public void removeOrder(String orderId) {
        cacheService.removeKey(orderId, NS);
    }

    // 设置/更新过期时间
    public void renewOrder(String orderId) {
        cacheService.expireKey(orderId, Duration.ofMinutes(30), NS);
    }

    // 设置到期时间点
    public void expireOrderAt(String orderId, Date deadline) {
        cacheService.expireKeyAt(orderId, deadline, NS);
    }

    // 获取剩余过期时间（秒）
    public long getOrderTtl(String orderId) {
        return cacheService.getKeyExpire(orderId, NS);
    }
}
```

---

## 六、注意事项

### 6.1 Redis 连接配置

默认情况下使用 Spring Boot 标准 Redis 配置（`spring.data.redis.*`）。如果需要多数据源，通过 `db-redis` 组件的自定义配置（`easyfk.config.db.redis`）管理，详见 [3.3 多数据源场景](#33-多数据源场景进阶)。

### 6.2 null 值不会被缓存

组件默认配置了 `disableCachingNullValues()`，这意味着：
- `@Cacheable` 方法返回 `null` 时不会写入缓存
- 下次相同参数仍会穿透到实际方法执行
- 如果需要防止缓存穿透，请在业务层返回空对象代替 `null`

### 6.3 注解方式与编程方式的 Key 格式不同

- **注解方式**：Key 格式为 `cacheName::key`（Spring Cache 默认的 `::` 分隔）
- **编程方式**：Key 格式为 `namespace::key`（由 `RedisUtil.wrapKey()` 拼接）

两种方式的 Key 命名空间不同，不要混用来读写同一个缓存数据。选择一种方式并保持统一。

### 6.4 caches 配置与未配置的行为差异

- **配置了 `caches`**：只有列表中声明的缓存空间会应用自定义 TTL 和序列化配置；未声明的缓存空间使用 Spring Cache 默认行为（无 TTL、允许 null）。
- **未配置 `caches`**：全局配置（TTL、序列化器、禁止 null）通过 `cacheDefaults` 应用到所有缓存空间，且启用事务感知。

如果需要让所有缓存空间都使用全局配置，不要配置 `caches` 列表，仅设置全局 `time-to-live` 即可。

### 6.5 序列化器配置

Value 序列化器由 `db-redis` 的 `easyfk.config.db.redisson.redis-serializer` 全局控制，可选值为 `RedisValueSerializer` 枚举：

| 值 | 说明 |
|----|------|
| `DEFAULT` | 默认序列化器（SmartRedisSerializer） |
| `FastJSON` | FastJSON 序列化 |
| `KRYO` | Kryo 序列化 |

确保缓存对象可被配置的序列化器正确序列化/反序列化。

---

> **文档版本**：2.0 | **最后更新**：2026-03-11
