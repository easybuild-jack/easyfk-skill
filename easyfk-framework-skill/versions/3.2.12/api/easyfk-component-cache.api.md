# easyfk-component-cache API 签名速查（easyfk 3.2.12）

> 坐标：`com.mcst:cache-redis、cache-caffeine`　源码：`easyfk-component/component-cache/cache-redis`、`easyfk-component/component-cache/cache-caffeine`
> 由 `scripts/gen-api.py` 从 9 个源文件自动提取，共 9 个类型、49 个方法/构造器、14 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-component-cache-skill.md](../modules/easyfk-component-cache-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 配置项（@ConfigurationProperties）

### `easyfk.config.cache.redis` ← RedisCacheProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `datasource` | `String` | `RedisConstants.DEFAULT_DATASOURCE` | 缓存数据源 |
| `database-name` | `String` | `RedisConstants.DEFAULT_DATABASE` | 缓存数据库名称 |
| `time-to-live` | `Duration` | `Duration.ZERO` |  |
| `caches` | `List<RedisDefinedInfo>` | `—` | 自定义缓存配置集合信息 |

### `easyfk.config.cache.caffeine` ← CaffeineCacheProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `create-spring-cache-manager` | `boolean` | `false` | 是否创建Spring缓存管理器 |
| `default-cache-name` | `String` | `"default"` | 默认缓存名称 |
| `time-to-live` | `Duration` | `Duration.ZERO` | 默认过期时间 |
| `maximum-size` | `long` | `10000` | 最大缓存条目数 |
| `caches` | `List<CaffeineDefinedInfo>` | `—` | 自定义缓存配置集合信息 |


## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `cache-redis` | `com.mcst.easyfk.cache.redis.config.RedisCacheConfig` |
| `cache-caffeine` | `com.mcst.easyfk.cache.caffeine.config.CaffeineSimpleConfig` |
| `cache-caffeine` | `com.mcst.easyfk.cache.caffeine.config.CaffeineCacheConfig` |

## 类型索引

- `com.mcst.easyfk.cache.caffeine.config`：[CaffeineCacheConfig](#caffeinecacheconfig)、[CaffeineDefinedInfo](#caffeinedefinedinfo)、[CaffeineSimpleConfig](#caffeinesimpleconfig)
- `com.mcst.easyfk.cache.caffeine.manager`：[LocalCacheManager](#localcachemanager)
- `com.mcst.easyfk.cache.caffeine.properties`：[CaffeineCacheProperties](#caffeinecacheproperties)
- `com.mcst.easyfk.cache.redis`：[RedisCacheServiceImpl](#rediscacheserviceimpl)
- `com.mcst.easyfk.cache.redis.config`：[RedisCacheConfig](#rediscacheconfig)、[RedisDefinedInfo](#redisdefinedinfo)
- `com.mcst.easyfk.cache.redis.properties`：[RedisCacheProperties](#rediscacheproperties)

## 包 `com.mcst.easyfk.cache.caffeine.config`

### CaffeineCacheConfig

`public class CaffeineCacheConfig`　注解：`@SuppressWarnings("all")` `@AutoConfiguration` `@EnableCaching` `@EnableConfigurationProperties(CaffeineCacheProperties.class)` `@ConditionalOnProperty(prefix = "easyfk.config.cache.caffeine", name = "create-spring-cache-manager", havingValue = "true")`　Caffeine缓存配置类

**方法**

```java
@Bean @Primary @Lazy @ConditionalOnMissingBean CacheManager cacheManager()
```

### CaffeineDefinedInfo

`public class CaffeineDefinedInfo`　Lombok：`@Data`　Caffeine缓存定义信息

**字段 / 常量**

```java
String cacheName  // 缓存名称
Duration timeToLive = Duration.ofMinutes(30)  // 缓存有效期，和缓存名称一一对应
long maximumSize = 10000  // 最大缓存条目数
```

### CaffeineSimpleConfig

`public class CaffeineSimpleConfig`　注解：`@AutoConfiguration`

**方法**

```java
@Bean @ConditionalOnMissingBean LocalCacheManager localCacheManager()
```

## 包 `com.mcst.easyfk.cache.caffeine.manager`

### LocalCacheManager

`public class LocalCacheManager`　注解：`@Slf4j` `@SuppressWarnings("all")`　本地缓存管理器 规则： 缓存名在四种类型（Cache / LoadingCache / AsyncCache / AsyncLoadingCache）之间全局唯一…

**方法**

```java
<T> Cache<String, T> getOrCreateCache(String cacheName, Duration expireAfterWrite, int maxSize)  // 获取或创建缓存
<T> Cache<String, T> getOrCreateCache(String cacheName, Duration expireAfterWrite, int expireType, int maxSize)  // 获取或创建缓存
<T> Cache<String, T> getOrCreateCache(String cacheName, int maxSize)  // 获取或创建缓存（不过期，仅受容量控制）
<T> T get(String cacheName, String key)  // 获取缓存值
void put(String cacheName, String key, Object value)  // 放入缓存
void evict(String cacheName, String key)  // 移除缓存
<T> T get(String cacheName, String key, Function<String, T> mappingFunction)  // 获取缓存值，如果不存在则通过mappingFunction加载
<T> Map<String, T> getAll(String cacheName, Set<String> keys)  // 批量获取缓存值
void putAll(String cacheName, Map<String, Object> map)  // 批量放入缓存
void evictAll(String cacheName, Set<String> keys)  // 批量移除缓存
void clear(String cacheName)  // 清空指定缓存的所有条目
long estimatedSize(String cacheName)  // 获取缓存的预估大小
void cleanUp(String cacheName)  // 手动触发缓存清理
boolean containsCache(String cacheName)  // 是否存在指定名称的缓存（任意类型）
void removeCache(String cacheName)  // 删除一个已管理的缓存实例，删除后可用新参数重新创建
<T> LoadingCache<String, T> getOrCreateLoadingCache(String cacheName, Duration expireAfterWrite, int maxSize, CacheLoader<String, T> loader)  // 获取或创建LoadingCache（自动加载缓存），写入后过期
<T> LoadingCache<String, T> getOrCreateLoadingCache(String cacheName, Duration expire, int expireType, int maxSize, CacheLoader<String, T> loader)  // 获取或创建LoadingCache（自动加载缓存），支持选择过期类型
<T> LoadingCache<String, T> getOrCreateLoadingCache(String cacheName, Duration expireAfterWrite, Duration refreshAfterWrite, int maxSize, CacheLoader<String, T> loader)  // 获取或创建LoadingCache（自动加载缓存），支持写后刷新
<T> LoadingCache<String, T> getOrCreateLoadingCacheWithStats(String cacheName, Duration expireAfterWrite, int maxSize, CacheLoader<String, T> loader)  // 获取或创建带统计功能的LoadingCache
<T> T getFromLoadingCache(String cacheName, String key)  // 从LoadingCache中获取值（自动加载）
<T> Map<String, T> getAllFromLoadingCache(String cacheName, Set<String> keys)  // 从LoadingCache中批量获取值（自动加载）
void refreshLoadingCache(String cacheName, String key)  // 手动刷新LoadingCache中的某个键
<T> AsyncCache<String, T> getOrCreateAsyncCache(String cacheName, Duration expireAfterWrite, int maxSize)  // 获取或创建AsyncCache（异步缓存），写入后过期
<T> AsyncCache<String, T> getOrCreateAsyncCache(String cacheName, Duration expire, int expireType, int maxSize)  // 获取或创建AsyncCache（异步缓存），支持选择过期类型
<T> CompletableFuture<T> getFromAsyncCache(String cacheName, String key, Function<String, T> mappingFunction)  // 从AsyncCache中异步获取值
void putToAsyncCache(String cacheName, String key, CompletableFuture<Object> value)  // 向AsyncCache中放入值
<T> AsyncLoadingCache<String, T> getOrCreateAsyncLoadingCache(String cacheName, Duration expireAfterWrite, int maxSize, CacheLoader<String, T> loader)  // 获取或创建AsyncLoadingCache（异步自动加载缓存），写入后过期
<T> AsyncLoadingCache<String, T> getOrCreateAsyncLoadingCache(String cacheName, Duration expireAfterWrite, int maxSize, AsyncCacheLoader<String, T> asyncLoader)  // 获取或创建AsyncLoadingCache（异步自动加载缓存），使用异步加载器
<T> AsyncLoadingCache<String, T> getOrCreateAsyncLoadingCache(String cacheName, Duration expireAfterWrite, Duration refreshAfterWrite, int maxSize, CacheLoader<String, T> loader)  // 获取或创建带刷新功能的AsyncLoadingCache
<T> CompletableFuture<T> getFromAsyncLoadingCache(String cacheName, String key)  // 从AsyncLoadingCache中异步获取值（自动加载）
<T> CompletableFuture<Map<String, T>> getAllFromAsyncLoadingCache(String cacheName, Set<String> keys)  // 从AsyncLoadingCache中异步批量获取值（自动加载）
<T> Cache<String, T> getOrCreateCacheWithStats(String cacheName, Duration expireAfterWrite, int maxSize)  // 获取或创建带统计功能的Cache
<T> Cache<String, T> getOrCreateWeakValuesCache(String cacheName, Duration expireAfterWrite, int maxSize)  // 获取或创建弱引用值的Cache，当值没有其他强引用时可被GC回收
<T> Cache<String, T> getOrCreateSoftValuesCache(String cacheName, Duration expireAfterWrite, int maxSize)  // 获取或创建软引用值的Cache，当内存不足时值可被GC回收
<T> Cache<String, T> getOrCreateWeakKeysCache(String cacheName, Duration expireAfterWrite, int maxSize)  // 获取或创建弱引用键的Cache，当键没有其他强引用时可被GC回收 注意：weakKeys 使用引用相等（==）比较键，内容相同但实例不同的 String 键无法命中
```

## 包 `com.mcst.easyfk.cache.caffeine.properties`

### CaffeineCacheProperties

`public class CaffeineCacheProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.cache.caffeine")`　Caffeine缓存配置属性

**字段 / 常量**

```java
boolean createSpringCacheManager = false  // 是否创建Spring缓存管理器
String defaultCacheName = "default"  // 默认缓存名称
Duration timeToLive = Duration.ZERO  // 默认过期时间
long maximumSize = 10000  // 最大缓存条目数
List<CaffeineDefinedInfo> caches  // 自定义缓存配置集合信息
```

## 包 `com.mcst.easyfk.cache.redis`

### RedisCacheServiceImpl

`public class RedisCacheServiceImpl implements ICacheService`

**方法**

```java
Long getSetCountByKey(String pattern, String namespace)
BaseResult<?> cacheObject(String key, Object value, String namespace)
BaseResult<?> cacheObject(String key, Object value, Duration times, String namespace)
<T> T queryByKey(String key, String namespace)
void expireKey(String key, Duration times, String namespace)
boolean existKey(String key, String namespace)
boolean setIfAbsent(String key, Object value, Duration timeToLive, String namespace)
void expireKeyAt(String key, Date date, String namespace)
long getKeyExpire(String key, String namespace)
BaseResult<?> removeKey(String key, String namespace)
```

## 包 `com.mcst.easyfk.cache.redis.config`

### RedisCacheConfig

`public class RedisCacheConfig`　注解：`@AutoConfiguration` `@EnableCaching` `@EnableConfigurationProperties(RedisCacheProperties.class)`

**方法**

```java
@Bean @Primary @Lazy @ConditionalOnMissingBean RedisCacheManager cacheManager()
@Bean @ConditionalOnMissingBean ICacheService cacheService()
```

### RedisDefinedInfo

`public class RedisDefinedInfo`　Lombok：`@Data`

**字段 / 常量**

```java
String cacheName  // 缓存名称
Duration timeToLive = Duration.ofMinutes(30)  // 缓存有效期，和缓存名称一一对应
```

## 包 `com.mcst.easyfk.cache.redis.properties`

### RedisCacheProperties

`public class RedisCacheProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.cache.redis")`

**字段 / 常量**

```java
String datasource = RedisConstants.DEFAULT_DATASOURCE  // 缓存数据源
String databaseName = RedisConstants.DEFAULT_DATABASE  // 缓存数据库名称
Duration timeToLive = Duration.ZERO
List<RedisDefinedInfo> caches  // 自定义缓存配置集合信息
```
