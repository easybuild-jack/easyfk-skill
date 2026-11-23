# easyfk-cache API 签名速查（easyfk 3.5.16）

> 坐标：`com.mcst:easyfk-cache`　源码：`easyfk-base/easyfk-cache`
> 由 `scripts/gen-api.py` 从 1 个源文件自动提取，共 1 个类型、10 个方法/构造器、0 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-cache-skill.md](../modules/easyfk-cache-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 类型索引

- `com.mcst.easyfk.cache.api`：[ICacheService](#icacheservice)

## 包 `com.mcst.easyfk.cache.api`

### ICacheService

`public interface ICacheService`

**方法**

```java
Long getSetCountByKey(String key, String namespace)  // 获取指定缓存键对应的SET集合中的元素数量 该方法用于统计Redis SET数据结构中存储的元素个数，常用于缓存数据量监控和业务逻辑判断。 如果指定的key不存在或不是SET类型，则返回0。
BaseResult<?> cacheObject(String key, Object value, String namespace)  // 缓存对象数据
BaseResult<?> cacheObject(String key, Object value, Duration timeToLive, String namespace)  // 短暂缓存数据
<T> T queryByKey(String key, String namespace)  // 根据缓存的KEY获取数据
void expireKey(String key, Duration timeToLive, String namespace)  // 对缓存的KEY进行过期设置
void expireKeyAt(String key, Date date, String namespace)  // 对缓存的KEY进行过期设置
long getKeyExpire(String key, String namespace)  // 获取缓存KEY的剩余过期时间
boolean existKey(String key, String namespace)  // 是否存在 key
boolean setIfAbsent(String key, Object value, Duration timeToLive, String namespace)  // 原子写入：仅当 key 不存在时写入并设置过期时间 用于防重放、防重复提交、幂等控制等需要原子"占用"的场景， 避免 existKey + cacheObject 两步操作在并发下产生竞态…
BaseResult<?> removeKey(String key, String namespace)  // 根据key删除数据
```
