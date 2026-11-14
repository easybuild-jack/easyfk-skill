# component-cache Skill 参考文档

> 所属项目：`easyfk-component`　子模块：`cache-caffeine`、`cache-redis`
> 坐标：`com.mcst:cache-caffeine` / `com.mcst:cache-redis`（3.2.12）
> 依据：两个子模块全部源码；对齐 `Cache-Caffeine开发手册.md`、`Cache-Caffeine技术特点.md`、`cache-redis-开发手册.md`。
> 以源码为准；差异见文末「复查记录」。

---

## 1. 选型

| 子模块 | 定位 | 提供的 Bean | 依赖 |
|---|---|---|---|
| `cache-redis` | **框架默认的分布式缓存实现**（`ICacheService` 的唯一实现）+ Spring Cache 的 `RedisCacheManager` | `cacheManager`（RedisCacheManager，`@Primary @Lazy`）、`cacheService`（ICacheService） | easyfk-cache、db-redis |
| `cache-caffeine` | 进程内本地缓存工具 `LocalCacheManager`，可选的 Spring `CaffeineCacheManager` | `localCacheManager`（自动注册，`@ConditionalOnMissingBean`）；开关打开时 `cacheManager` | caffeine、easyfk-core、starter-cache |
- 框架内部的组件（web 的防重/幂等、authority、autoId 等）依赖 `ICacheService`，所以**业务项目一般都要引入 `cache-redis`**。
- `cache-redis` 无条件开启 `@EnableCaching` 并注册 `RedisCacheManager`。如果同时开启 `cache-caffeine` 的 CacheManager，两者都标了 `@Primary`（caffeine 的 `@ConditionalOnMissingBean` 按 `CacheManager` 类型判断，redis 的按 `RedisCacheManager` 类型判断），最终生效哪个取决于自动配置的加载顺序。需要 Spring 注解缓存时**只选一个 CacheManager**。

---

## 2. cache-caffeine

### 2.1 自动配置

| 配置类 | 是否在 `AutoConfiguration.imports` 中 | 条件 | 作用 |
|---|---|---|---|
| `CaffeineCacheConfig` | 是 | `easyfk.config.cache.caffeine.create-spring-cache-manager=true` | `@EnableCaching`，注册 `@Primary @Lazy` 的 `CaffeineCacheManager` |
| `CaffeineSimpleConfig` | 是 | `@ConditionalOnMissingBean` | 注册 `LocalCacheManager` |

- 引入依赖后 `LocalCacheManager` 自动注册，可以自定义同类型 Bean 覆盖。

```yaml
easyfk:
  config:
    cache:
      caffeine:
        create-spring-cache-manager: true    # kebab 写法（驼峰 createSpringCacheManager 也可）
        default-cache-name: default
        time-to-live: 10m                    # 默认 0 表示不过期；粒度为秒
        maximum-size: 5000                   # 默认 10000
        caches:                              # 每个缓存单独设置 TTL 和容量；TTL 默认 30m，容量默认 10000
          - cache-name: userCache
            time-to-live: 30m
            maximum-size: 2000
```

`caches` 中没有声明的缓存名，会按 `time-to-live` 和 `maximum-size` 动态创建。

### 2.2 LocalCacheManager

内部按类型分别存放 `Cache`、`LoadingCache`、`AsyncCache`、`AsyncLoadingCache`，但**缓存名在四种类型之间全局唯一**：同一个名字只能属于一种类型。

| 类型 | 创建 | 访问 |
|---|---|---|
| Cache | `getOrCreateCache(name, ttl, maxSize)`、`getOrCreateCache(name, ttl, expireType(0写/1读，其他值抛 IllegalArgumentException), maxSize)`、`getOrCreateCache(name, maxSize)`（不过期）、`getOrCreateCacheWithStats`、`getOrCreateWeakValuesCache`、`getOrCreateSoftValuesCache`、`getOrCreateWeakKeysCache` | `get(name,key)`、`get(name,key,fn)`、`put`、`evict`、`getAll`、`putAll`、`evictAll`、`clear`、`estimatedSize`、`cleanUp`（**对四种类型都可用**，异步缓存走 `synchronous()` 视图） |
| LoadingCache | `getOrCreateLoadingCache(name, ttl, maxSize, loader)`、`(name, ttl, expireType, maxSize, loader)`、`(name, expireAfterWrite, refreshAfterWrite, maxSize, loader)`、`getOrCreateLoadingCacheWithStats` | `getFromLoadingCache`、`getAllFromLoadingCache`、`refreshLoadingCache` |
| AsyncCache | `getOrCreateAsyncCache(name, ttl, maxSize)`、`(name, ttl, expireType, maxSize)` | `getFromAsyncCache(name,key,fn)`、`putToAsyncCache(name,key,future)` |
| AsyncLoadingCache | `getOrCreateAsyncLoadingCache(name, ttl, maxSize, CacheLoader / AsyncCacheLoader)`、`(name, ttl, refresh, maxSize, loader)` | `getFromAsyncLoadingCache`、`getAllFromAsyncLoadingCache` |
| 通用 | `removeCache(name)`（移除后可用新参数重建）、`containsCache(name)` | |

使用要点：
- 同名缓存再次 `getOrCreate*`：类型与参数（过期方式、过期时间、刷新时间、容量、统计、引用类型）一致时返回已有实例；**不一致时抛 `IllegalStateException`**。加载器（loader）不参与比较，始终使用首次创建时的加载器。
- 缓存**必须先 `getOrCreate*` 才能访问**：所有访问方法（包括 `get(name, key)`）在缓存不存在时统一抛 `IllegalStateException`；类型专用方法（如 `getFromLoadingCache`）用在其他类型的缓存上也抛 `IllegalStateException`。缓存存在但 key 未命中时 `get(name, key)` 返回 null。
- 推荐直接持有 `getOrCreate*` 返回的 Caffeine 原生实例来操作。

```java
private Cache<String, UserDTO> userCache;

@PostConstruct
void init() { userCache = localCacheManager.getOrCreateCache("user:info", Duration.ofMinutes(10), 5000); }

UserDTO u = userCache.get(id, this::loadFromDb);
```

---

## 3. cache-redis

```yaml
easyfk:
  config:
    cache:
      redis:
        datasource: default        # db-redis 的数据源名（简单模式下只有 default）
        database-name: default     # 数据源下 databases 的别名
        time-to-live: 30m          # 默认 0 表示不过期
        caches:                    # 一旦配置，见下方"重要"
          - cache-name: users
            time-to-live: 2h       # 默认 30m
```

### 3.1 RedisCacheManager（Spring Cache 注解）

- key 用 String 序列化，格式为 `cacheName::key`。
- value 用 db-redis 的 `SmartRedisSerializer`，类型由 `easyfk.config.db.redis.redis-serializer` 决定。
- 默认配置 `disableCachingNullValues`，null 不缓存；`@Cacheable` 的方法返回 null 时**不会报错**，只是不写入缓存。
- 始终设置 `cacheDefaults` 与 `transactionAware`：`caches` 中声明的缓存使用各自的 TTL，**未声明的缓存名同样使用框架默认配置**（框架序列化器、全局 `time-to-live`、不缓存 null）。
- 数值和布尔值可以直接缓存：db-redis 的序列化器会带上类型，`@Cacheable` 返回 `Long`、`Integer`、`Boolean` 时读回原类型。缓存的业务对象需位于 `com.mcst.` 下或加入 `easyfk.config.db.redis.trusted-packages`，否则反序列化会被拒绝。

### 3.2 ICacheService（编程式）

实际 key 为 `namespace::key`，落在 `datasource` + `database-name` 指定的连接上。各方法的语义见 [easyfk-cache](easyfk-cache-skill.md)。

| 方法 | 委托给 RedisOptManager 的方法 |
|---|---|
| `cacheObject(key, v, ns)` / `cacheObject(key, v, Duration, ns)` | `putObject`（不传 Duration 时永不过期） |
| `queryByKey(key, ns)` | `getObject`（同样有数值读回为 String 的问题） |
| `existKey` / `removeKey` / `expireKey` / `expireKeyAt` / `getKeyExpire` | 同名方法 |
| `setIfAbsent(key, v, ttl, ns)` | `putIfAbsent`（SET NX EX，原子操作） |
| `getSetCountByKey(key, ns)` | `getSetSize`（SCARD；参数名叫 pattern，实际是 key） |

### 3.3 多数据源

先在 db-redis 中开启动态模式并配置别名，再让 cache 指向这个别名：

```yaml
easyfk:
  config:
    db:
      redis:
        enable-dynamic: true            # 不开启时只有 default::default，指向别名会找不到连接
        default-data-source: default
        datasource:
          default:
            host: 127.0.0.1
            database: 0
            databases: {cache-db: 1}    # 别名的索引不能与 database 重复
    cache:
      redis:
        datasource: default
        database-name: cache-db
```

---

## 4. 生成代码时的规则

**Do**
- 业务需要分布式缓存或框架组件依赖 `ICacheService` 时，引入 `cache-redis`，注入 `ICacheService` 或使用 `@Cacheable`。
- 使用 Spring Cache 注解时，缓存的值使用 DTO 或 String；需要单独 TTL 的 cacheName 声明在 `caches` 中。
- 使用 `LocalCacheManager` 时直接注入，在初始化阶段 `getOrCreate*`（同名缓存每次传相同参数），并持有返回的原生实例。
- 开启 Caffeine 的 CacheManager 时，YAML 中写 `create-spring-cache-manager: true`，并且不要同时使用 cache-redis 的注解缓存。

**Don't**
- 不要对同一个缓存名用不同参数 `getOrCreate*`（会抛 `IllegalStateException`），也不要在不同类型之间复用缓存名。
- 不要混用注解方式（`cacheName::key`）和 `ICacheService`（`namespace::key`）来读写同一份数据。

---

## 5. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | caffeine 手册 §3.3 / §4.1 / §5、技术特点 | 引入后 `LocalCacheManager` 自动注册，`CaffeineSimpleConfig` 始终生效 | `AutoConfiguration.imports` 中只有 `CaffeineCacheConfig`，`CaffeineSimpleConfig` 不会被加载，**`LocalCacheManager` 不存在**（除非业务的组件扫描覆盖到该包） **已修复**：imports 同时登记 `CaffeineSimpleConfig` 与 `CaffeineCacheConfig`，`LocalCacheManager` 自动注册（`@ConditionalOnMissingBean`） |
| 2 | caffeine 手册 §3.1 / §3.3 / §4.2、技术特点 | YAML 写 `create-spring-cache-manager: true` | 条件是 `@ConditionalOnProperty(name = "create_spring_cache_manager")`。按 Spring Boot 的解析规则（带下划线的名字不是合法的规范属性名，会退回精确匹配），推断 kebab 写法不会触发条件，需要写下划线原样的 key（未实际启动验证） **已修复**：条件改为 `create-spring-cache-manager`，kebab 与驼峰写法均可触发 |
| 3 | caffeine 手册 §6 | 不设置过期就只受容量控制 | 与源码一致。另外：`getOrCreate*` 遇到同名缓存时忽略新参数；四种缓存类型各自独立存放，`get/put` 只查找普通 Cache；缓存不存在时 `get` 返回 null，其余方法抛异常 **已修复**：缓存名跨类型全局唯一，同名再次 `getOrCreate*` 参数不一致时抛 `IllegalStateException`；通用 `get/put/evict` 等对四种类型都生效；缓存不存在时所有方法统一抛 `IllegalStateException` |
| 4 | cache-redis 手册 §6.5 | 序列化器由 `easyfk.config.db.redisson.redis-serializer` 控制 | 应为 `easyfk.config.db.redis.redis-serializer` |
| 5 | cache-redis 手册 §3.3 | 多数据源示例：`databases: {default: 0, cache-db: 1}`，同时 `database: 0` | ① 没有写 `enable-dynamic: true`，简单模式下不存在 `default::cache-db`，会找不到连接；② db-redis 的校验器禁止 `databases` 中的索引与 `database` 重复（0 与 0 冲突），启动报错 |
| 6 | cache-redis 手册 §3.2 / §6.4 | 配置 caches 后，未声明的缓存使用 Spring 默认行为 | 与源码一致。手册没有说明的是：Spring 默认配置是 **JDK 序列化**，并且同时失去了 `transactionAware` **已修复**：始终设置 `cacheDefaults(框架默认配置)` 与 `transactionAware`，未声明的缓存同样使用框架序列化器、全局 TTL、不缓存 null |
| 7 | cache-redis 手册 §1.1 / §4.2 | 值使用 SmartRedisSerializer | Number、Boolean 写成字符串，读回来是 String。`@Cacheable` 返回 Long 等类型，命中缓存时调用方会 `ClassCastException`；`ICacheService.queryByKey` 也一样。（根因在 db-redis 的 `SmartRedisSerializer`，由 db-redis 负责修复，cache 模块无改动） **已修复**：db-redis 的 `SmartRedisSerializer` 把数值/布尔/字符写成带类型信封，读回原类型；旧版本写入的纯文本数值读回仍是 String |
| 8 | cache-redis 手册 §4.3 | `getSetCountByKey(String pattern, …)` | 参数是 key，执行 SCARD，不支持模式匹配 |
