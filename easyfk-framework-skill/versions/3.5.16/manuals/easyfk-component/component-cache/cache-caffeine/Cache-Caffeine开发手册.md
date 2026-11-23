# Cache-Caffeine 开发手册

## 1. 模块概述

`cache-caffeine` 是 EasyFK 框架中基于 [Caffeine](https://github.com/ben-manes/caffeine) 的高性能本地缓存组件。该模块封装了 Caffeine 缓存库，提供统一的缓存管理能力，并与 Spring Boot 自动配置机制深度集成，支持编程式缓存操作和 Spring Cache 注解两种使用方式。

## 2. 依赖引入

在项目的 `build.gradle` 中添加依赖：

```gradle
dependencies {
    implementation 'com.mcst:cache-caffeine'
}
```

该模块会自动传递引入以下依赖：
- `com.github.ben-manes.caffeine:caffeine` — Caffeine 缓存核心库
- `com.mcst:easyfk-core` — EasyFK 核心模块
- `org.springframework.boot:spring-boot-starter-cache` — Spring Boot 缓存 Starter

## 3. 配置说明

### 3.1 配置属性

所有配置项统一在 `easyfk.config.cache.caffeine` 前缀下，可在 `application.yml` 或 `application.properties` 中配置。

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `create-spring-cache-manager` | Boolean | `false` | 是否创建 Spring CacheManager，设为 `true` 后可使用 `@Cacheable` 等注解 |
| `default-cache-name` | String | `"default"` | 默认缓存名称 |
| `time-to-live` | Duration | `0`（不过期） | 默认缓存过期时间 |
| `maximum-size` | Long | `10000` | 默认最大缓存条目数 |
| `caches` | List | — | 自定义缓存配置列表 |

### 3.2 自定义缓存配置（caches 列表项）

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `cache-name` | String | — | 缓存名称（必填） |
| `time-to-live` | Duration | `30m` | 缓存过期时间 |
| `maximum-size` | Long | `10000` | 最大缓存条目数 |

### 3.3 配置示例

#### 仅使用编程式缓存（默认模式）

无需任何配置，引入依赖后 `LocalCacheManager` 会自动注册为 Spring Bean。

#### 启用 Spring Cache 注解支持

```yaml
easyfk:
  config:
    cache:
      caffeine:
        create-spring-cache-manager: true
        default-cache-name: default
        time-to-live: 10m
        maximum-size: 5000
        caches:
          - cache-name: userCache
            time-to-live: 30m
            maximum-size: 2000
          - cache-name: configCache
            time-to-live: 1h
            maximum-size: 500
```

## 4. 使用方式

### 4.1 编程式缓存 — LocalCacheManager

`LocalCacheManager` 是核心缓存管理器，引入依赖后自动注入即可使用。它统一管理四种 Caffeine 缓存类型的创建和访问。

#### 4.1.1 注入 LocalCacheManager

```java
@Service
public class MyService {

    @Resource
    private LocalCacheManager localCacheManager;
}
```

#### 4.1.2 基础缓存（Cache）

**创建缓存：**

```java
// 创建一个写后10分钟过期、最多缓存1000条的缓存
Cache<String, User> userCache = localCacheManager.getOrCreateCache("userCache", Duration.ofMinutes(10), 1000);

// 仅指定最大数量（不过期）
Cache<String, Config> configCache = localCacheManager.getOrCreateCache("configCache", 5000);

// 指定过期类型：0=写后过期，1=读后过期
Cache<String, Token> tokenCache = localCacheManager.getOrCreateCache("tokenCache", Duration.ofHours(1), 1, 2000);
```

**CRUD 操作：**

```java
// 写入
localCacheManager.put("userCache", "user:1001", userObj);

// 读取
User user = localCacheManager.get("userCache", "user:1001");

// 读取（缓存未命中时自动加载）
User user = localCacheManager.get("userCache", "user:1001", key -> userService.findById(key));

// 删除
localCacheManager.evict("userCache", "user:1001");

// 清空整个缓存
localCacheManager.clear("userCache");
```

**批量操作：**

```java
// 批量读取
Set<String> keys = Set.of("user:1001", "user:1002", "user:1003");
Map<String, User> users = localCacheManager.getAll("userCache", keys);

// 批量写入
Map<String, Object> entries = Map.of("user:1001", user1, "user:1002", user2);
localCacheManager.putAll("userCache", entries);

// 批量删除
localCacheManager.evictAll("userCache", keys);
```

**缓存信息与维护：**

```java
// 获取缓存预估大小
long size = localCacheManager.estimatedSize("userCache");

// 手动触发缓存清理（触发过期条目回收）
localCacheManager.cleanUp("userCache");

// 删除已管理的缓存实例
localCacheManager.removeCache("userCache");
```

#### 4.1.3 自动加载缓存（LoadingCache）

适用于缓存未命中时需要自动从数据源加载的场景。

```java
// 创建自动加载缓存
LoadingCache<String, User> cache = localCacheManager.getOrCreateLoadingCache(
    "userCache",
    Duration.ofMinutes(10),
    1000,
    key -> userService.findById(key)  // CacheLoader
);

// 获取值（缓存未命中时自动调用 loader）
User user = localCacheManager.getFromLoadingCache("userCache", "user:1001");

// 批量获取（自动加载缺失的键）
Map<String, User> users = localCacheManager.getAllFromLoadingCache("userCache", Set.of("user:1001", "user:1002"));

// 手动刷新某个键
localCacheManager.refreshLoadingCache("userCache", "user:1001");
```

**支持写后自动刷新：**

```java
// 写后10分钟过期，写后5分钟触发异步刷新
LoadingCache<String, Config> cache = localCacheManager.getOrCreateLoadingCache(
    "configCache",
    Duration.ofMinutes(10),    // 过期时间
    Duration.ofMinutes(5),     // 刷新时间
    5000,
    key -> configService.load(key)
);
```

**带统计功能的 LoadingCache：**

```java
LoadingCache<String, User> cache = localCacheManager.getOrCreateLoadingCacheWithStats(
    "userCache",
    Duration.ofMinutes(10),
    1000,
    key -> userService.findById(key)
);

// 获取统计信息
CacheStats stats = cache.stats();
// stats.hitRate(), stats.missRate(), stats.loadCount() 等
```

#### 4.1.4 异步缓存（AsyncCache）

适用于需要非阻塞式缓存操作的场景。

```java
// 创建异步缓存
AsyncCache<String, User> asyncCache = localCacheManager.getOrCreateAsyncCache(
    "asyncUserCache",
    Duration.ofMinutes(10),
    1000
);

// 异步获取（未命中时通过函数加载）
CompletableFuture<User> future = localCacheManager.getFromAsyncCache(
    "asyncUserCache",
    "user:1001",
    key -> userService.findById(key)
);

// 异步放入
localCacheManager.putToAsyncCache(
    "asyncUserCache",
    "user:1001",
    CompletableFuture.supplyAsync(() -> userService.findById("user:1001"))
);
```

#### 4.1.5 异步自动加载缓存（AsyncLoadingCache）

结合自动加载与异步处理的缓存类型。

```java
// 使用同步 loader（Caffeine 自动包装为异步执行）
AsyncLoadingCache<String, User> cache = localCacheManager.getOrCreateAsyncLoadingCache(
    "asyncUserCache",
    Duration.ofMinutes(10),
    1000,
    (CacheLoader<String, User>) key -> userService.findById(key)
);

// 使用异步 loader
AsyncLoadingCache<String, User> cache = localCacheManager.getOrCreateAsyncLoadingCache(
    "asyncUserCache",
    Duration.ofMinutes(10),
    1000,
    (AsyncCacheLoader<String, User>) (key, executor) ->
        CompletableFuture.supplyAsync(() -> userService.findById(key), executor)
);

// 异步获取
CompletableFuture<User> future = localCacheManager.getFromAsyncLoadingCache("asyncUserCache", "user:1001");

// 异步批量获取
CompletableFuture<Map<String, User>> futures = localCacheManager.getAllFromAsyncLoadingCache(
    "asyncUserCache",
    Set.of("user:1001", "user:1002")
);
```

#### 4.1.6 特殊引用类型缓存

```java
// 弱引用值缓存 — 值无强引用时可被 GC 回收
Cache<String, User> weakCache = localCacheManager.getOrCreateWeakValuesCache("weakCache", Duration.ofMinutes(10), 1000);

// 软引用值缓存 — 内存不足时值可被 GC 回收
Cache<String, User> softCache = localCacheManager.getOrCreateSoftValuesCache("softCache", Duration.ofMinutes(10), 1000);

// 弱引用键缓存 — 键无强引用时可被 GC 回收
Cache<String, User> weakKeyCache = localCacheManager.getOrCreateWeakKeysCache("weakKeyCache", Duration.ofMinutes(10), 1000);

// 带统计功能的缓存
Cache<String, User> statsCache = localCacheManager.getOrCreateCacheWithStats("statsCache", Duration.ofMinutes(10), 1000);
```

### 4.2 Spring Cache 注解方式

启用 `create-spring-cache-manager: true` 后，可直接使用 Spring Cache 注解。

```java
@Service
public class UserService {

    @Cacheable(value = "userCache", key = "#id")
    public User findById(String id) {
        return userRepository.findById(id);
    }

    @CachePut(value = "userCache", key = "#user.id")
    public User update(User user) {
        return userRepository.save(user);
    }

    @CacheEvict(value = "userCache", key = "#id")
    public void delete(String id) {
        userRepository.deleteById(id);
    }

    @CacheEvict(value = "userCache", allEntries = true)
    public void clearAll() {
        // 清空 userCache 所有条目
    }
}
```

## 5. 自动配置机制

本模块利用 Spring Boot 自动配置实现零配置启动：

| 配置类 | 条件 | 说明 |
|--------|------|------|
| `CaffeineSimpleConfig` | 无条件（`@ConditionalOnMissingBean`） | 自动注册 `LocalCacheManager` Bean |
| `CaffeineCacheConfig` | `create_spring_cache_manager=true` | 创建 Spring `CacheManager` 并启用 `@EnableCaching` |

- `CaffeineSimpleConfig` 始终生效，确保 `LocalCacheManager` 可用
- `CaffeineCacheConfig` 仅在开启配置时生效，创建 `CaffeineCacheManager` 并标记为 `@Primary`

## 6. 缓存过期策略说明

| 策略 | 参数 | 说明 |
|------|------|------|
| 写后过期（expireAfterWrite） | `expireType=0`（默认） | 写入后经过指定时间自动过期 |
| 读后过期（expireAfterAccess） | `expireType=1` | 最后一次访问后经过指定时间过期，适合热点数据 |
| 写后刷新（refreshAfterWrite） | LoadingCache 专用 | 写入后经过指定时间，下次访问触发异步刷新，刷新期间返回旧值 |
| 不过期 | `Duration.ZERO` 或不设置 | 仅受 `maximumSize` 控制，满时按 LRU/LFU 策略淘汰 |

## 7. API 快速参考

### LocalCacheManager 方法列表

| 方法 | 说明 |
|------|------|
| `getOrCreateCache(name, expire, maxSize)` | 创建/获取基础缓存 |
| `getOrCreateCache(name, expire, expireType, maxSize)` | 创建/获取基础缓存（可选过期类型） |
| `getOrCreateCache(name, maxSize)` | 创建/获取不过期缓存 |
| `get(name, key)` | 获取缓存值 |
| `get(name, key, mappingFunction)` | 获取缓存值（未命中时加载） |
| `put(name, key, value)` | 放入缓存 |
| `evict(name, key)` | 删除单个缓存项 |
| `getAll(name, keys)` | 批量获取 |
| `putAll(name, map)` | 批量放入 |
| `evictAll(name, keys)` | 批量删除 |
| `clear(name)` | 清空缓存 |
| `estimatedSize(name)` | 获取预估大小 |
| `cleanUp(name)` | 手动触发清理 |
| `removeCache(name)` | 移除缓存实例 |
| `getOrCreateLoadingCache(...)` | 创建自动加载缓存（多种重载） |
| `getOrCreateLoadingCacheWithStats(...)` | 创建带统计的自动加载缓存 |
| `getFromLoadingCache(name, key)` | 从 LoadingCache 获取值 |
| `getAllFromLoadingCache(name, keys)` | 从 LoadingCache 批量获取 |
| `refreshLoadingCache(name, key)` | 刷新 LoadingCache 指定键 |
| `getOrCreateAsyncCache(...)` | 创建异步缓存 |
| `getFromAsyncCache(name, key, fn)` | 异步获取缓存值 |
| `putToAsyncCache(name, key, future)` | 异步放入缓存值 |
| `getOrCreateAsyncLoadingCache(...)` | 创建异步自动加载缓存（多种重载） |
| `getFromAsyncLoadingCache(name, key)` | 异步获取自动加载缓存值 |
| `getAllFromAsyncLoadingCache(name, keys)` | 异步批量获取自动加载缓存值 |
| `getOrCreateCacheWithStats(...)` | 创建带统计的缓存 |
| `getOrCreateWeakValuesCache(...)` | 创建弱引用值缓存 |
| `getOrCreateSoftValuesCache(...)` | 创建软引用值缓存 |
| `getOrCreateWeakKeysCache(...)` | 创建弱引用键缓存 |

## 8. 最佳实践

1. **缓存命名规范**：建议使用 `模块:实体` 格式命名，如 `user:info`、`config:system`，避免缓存名称冲突。
2. **合理设置过期时间**：根据数据更新频率设置过期时间，频繁变更的数据设置较短过期，配置类数据可适当延长。
3. **控制缓存大小**：通过 `maximumSize` 限制缓存条目数，防止内存溢出。
4. **优先使用 LoadingCache**：对需要自动加载的场景使用 LoadingCache，避免缓存穿透。
5. **善用刷新策略**：对配置类数据使用 `refreshAfterWrite`，在保证数据较新的同时避免请求阻塞。
6. **内存敏感场景**：使用弱引用/软引用缓存，让 GC 能在内存压力时自动回收缓存条目。
7. **监控缓存命中率**：使用带统计功能的缓存（`WithStats` 系列方法）来观察缓存效果，及时调整策略。

## 9. 包结构

```
com.mcst.easyfk.cache.caffeine
├── config
│   ├── CaffeineCacheConfig.java        # Spring Cache 管理器配置（条件激活）
│   ├── CaffeineDefinedInfo.java        # 缓存定义信息实体
│   └── CaffeineSimpleConfig.java       # LocalCacheManager 自动配置
├── manager
│   └── LocalCacheManager.java          # 核心缓存管理器
└── properties
    └── CaffeineCacheProperties.java    # 配置属性绑定类
```
