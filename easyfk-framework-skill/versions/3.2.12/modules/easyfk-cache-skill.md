# easyfk-cache Skill 参考文档

> 所属项目：`easyfk-base`　模块：`easyfk-cache`（单模块，纯接口）
> 坐标：`com.mcst:easyfk-cache:3.2.12`
> 依据：源码 `ICacheService.java`；实现类为 `easyfk-component/component-cache/cache-redis` 中的 `RedisCacheServiceImpl`、`RedisCacheConfig`、`db-redis` 的 `RedisOptManager`、`RedisArgsHelper` 和 `RedisUtil`。对齐了 `EasyFK框架开发手册.md` §3.6 / §6.4 和 `核心模块说明.md` §5.4。
> 以源码为准；差异见文末「复查记录」。

---

## 1. 模块定位

本模块只定义缓存抽象接口 `com.mcst.easyfk.cache.api.ICacheService`，**不包含实现，也不包含自动配置**。

- 依赖：`compileOnly project(':easyfk-core')`，因为接口返回 `BaseResult`。
- 目前唯一的实现是 `com.mcst:cache-redis`（位于 easyfk-component）。它通过 `@ConditionalOnMissingBean` 注册 `RedisCacheServiceImpl`，同时开启 `@EnableCaching` 并注册一个 `@Primary` 的 `RedisCacheManager`。
- 框架内部的使用方如下，它们运行时都需要容器中存在一个 `ICacheService` Bean：

| 使用方 | 用途 |
|---|---|
| `easyfk-authority` `RedisUserDataManagerImpl` | 登录态 `UserData` / `UserAuth` 的存储、续期和踢出 |
| `web-prd` `IdempotentAspect` / `RequestTokenAspect` / `ApiAuthFilter` / `RequestBaseFilter` | 幂等占位、一次性 Token、nonce 防重放、动态签名密钥 |
| `easyfk-gateway` `RequestGatewayFilter` | 动态签名密钥、nonce 防重放 |

---

## 2. 引入

```groovy
implementation platform('com.mcst:easyfk-dependencies:3.2.12')
implementation 'com.mcst:easyfk-core'
implementation 'com.mcst:easyfk-cache'      // 只有接口
implementation 'com.mcst:cache-redis'       // Redis 实现，需要配置 db-redis 数据源
```

Redis 实现的配置前缀为 `easyfk.config.cache.redis`：

| 属性 | 说明 |
|---|---|
| `datasource` | db-redis 的数据源名 |
| `database-name` | 库名 |
| `time-to-live` | Spring Cache 的默认 TTL |
| `caches` | 每个 cacheName 单独的 TTL |

这些属性的详细说明放在 cache-redis 的 skill 文档中。

---

## 3. 接口契约

**参数顺序约定：`namespace` 永远是最后一个参数。**

| 方法 | 说明 |
|---|---|
| `BaseResult<?> cacheObject(key, value, namespace)` | 写入，**永不过期** |
| `BaseResult<?> cacheObject(key, value, Duration ttl, namespace)` | 写入并设置 TTL（Redis 实现按 `ttl.getSeconds()` 截断到秒） |
| `<T> T queryByKey(key, namespace)` | 读取，不存在时返回 null；泛型是未经检查的强转 |
| `boolean existKey(key, namespace)` | 判断 key 是否存在 |
| `boolean setIfAbsent(key, value, Duration ttl, namespace)` | key 不存在时写入并设置 TTL。返回 true 表示本次占位成功 |
| `void expireKey(key, Duration ttl, namespace)` | 重新设置 TTL |
| `void expireKeyAt(key, Date at, namespace)` | 设置到某个时间点过期 |
| `long getKeyExpire(key, namespace)` | 剩余 TTL（秒），按 Redis TTL 的语义：-1 表示永不过期，-2 表示 key 不存在 |
| `Long getSetCountByKey(key, namespace)` | 返回 SET 类型 key 的元素个数 |
| `BaseResult<?> removeKey(key, namespace)` | 删除 key，返回的 data 为 Boolean，表示是否删除成功 |

Redis 实现的行为：

- 实际写入 Redis 的 key 是 `namespace + "::" + key`，数据源和库由 `easyfk.config.cache.redis.datasource/database-name` 决定。
- `key`、`namespace` 为空时会抛出 `RuntimeException("key not empty" / "namespace not empty")`。
- `setIfAbsent` 在 Redis 实现中是原子的（`SET NX EX`）。接口中它是**抽象方法**，自定义实现必须提供原子实现。
- 值的序列化由 db-redis 配置的 `redis-serializer` 决定，缓存对象必须能被该序列化器处理。
- 接口**没有**向 SET 中添加元素的方法。`getSetCountByKey` 只能统计通过其他途径（例如 `RedisOptManager`）写入的 SET。

---

## 4. 使用示例

```java
import com.mcst.easyfk.cache.api.ICacheService;

@Service
public class ProductService {

    private static final String NS = "product";
    private static final Duration TTL = Duration.ofMinutes(5);

    @Resource
    private ICacheService cacheService;

    public ProductDto get(Long id) {
        String key = String.valueOf(id);
        ProductDto cached = cacheService.queryByKey(key, NS);
        if (cached != null) {
            return cached;
        }
        ProductDto dto = TransformUtil.transform(productRepository.findById(id), ProductDto.class);
        if (dto != null) {
            cacheService.cacheObject(key, dto, TTL, NS);
        }
        return dto;
    }

    @Transactional(rollbackFor = Exception.class)
    public void update(ProductDto dto) {
        productRepository.update(dto);
        cacheService.removeKey(String.valueOf(dto.getId()), NS);
    }

    // 防重复提交 / 幂等占位
    public boolean tryLock(String bizNo) {
        return cacheService.setIfAbsent(bizNo, "1", Duration.ofSeconds(30), "submit-lock");
    }
}
```

---

## 5. 生成代码时的规则

**应该这样做：**

- 注入 `ICacheService` 接口，不要直接依赖 `RedisCacheServiceImpl`。
- 把 namespace 定义为常量，按业务域划分，key 中不要再重复写 namespace 前缀。
- 写入时尽量带 TTL；TTL 不要小于 1 秒（Redis 实现会截断到秒）。
- 凡是"占用"类语义（例如幂等、防重放、分布式占位），使用 `setIfAbsent`。
- 读出数据后先判断是否为 null，再使用。

**不要这样做：**

- 不要用 `existKey` + `cacheObject` 实现占位，这两步之间存在竞态。
- 不要传入空的 key 或 namespace。
- 不要指望 `queryByKey` 做类型转换，读出值的类型由序列化器决定，类型不符时会 `ClassCastException`。
- 不要使用框架手册中出现的 `getObject(ns, key, Class)`、`cacheObject(ns, key, value, long)`、`delete(ns, key)`，接口中没有这些方法。
- 自定义 `ICacheService` 实现时，不要用 `existKey` + `cacheObject` 两步实现 `setIfAbsent`。

---

## 6. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | 框架手册 §3.6.2 / §6.4 | `import com.mcst.easyfk.cache.ICacheService` | 包名是 `com.mcst.easyfk.cache.api` |
| 2 | 框架手册 §3.6.2 / §6.4 | `getObject(ns, key, Class)`、`cacheObject(ns, key, value, 60L)`、`delete(ns, key)` | 这些方法都不存在。实际方法为 `queryByKey(key, ns)`、`cacheObject(key, value, Duration, ns)`、`removeKey(key, ns)`，namespace 放在最后 |
| 3 | 核心模块说明 §5.4 | 方法列表中缺少 `setIfAbsent` / `expireKeyAt` | 接口中有这两个方法；`setIfAbsent` 的默认实现不是原子的 **已修复**：`setIfAbsent` 改为抽象方法，实现类必须提供原子实现（唯一实现 `RedisCacheServiceImpl` 已覆盖） |
| 4 | 核心模块说明 §5.4 | "具体实现由业务项目提供（如 Redis）" | 框架已提供 `cache-redis` 实现（自动配置，`@ConditionalOnMissingBean`） |
| 5 | 核心模块说明 §5.4 | "按 key 前缀区分" | Redis 实现中实际的 key 格式是 `namespace::key`，namespace 为必填 |
| 6 | 源码 `ICacheService` | `expireKeyAt` 之后有一段孤立的 Javadoc | 这段注释没有对应的方法，属于残留 **已修复**：已删除残留注释 |
| 7 | 框架使用方 | — | `easyfk-gateway` 的 `RequestGatewayFilter` 在 nonce 防重放中使用 `existKey` + `cacheObject`，不是原子的，存在并发绕过的风险（在 gateway 文档中复查） |