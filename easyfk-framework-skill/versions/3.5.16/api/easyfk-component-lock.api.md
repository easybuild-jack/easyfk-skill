# easyfk-component-lock API 签名速查（easyfk 3.5.16）

> 坐标：`com.mcst:lock-redisson`　源码：`easyfk-component/component-lock/lock-redisson`
> 由 `scripts/gen-api.py` 从 7 个源文件自动提取，共 7 个类型、20 个方法/构造器、22 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-component-lock-skill.md](../modules/easyfk-component-lock-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 配置项（@ConfigurationProperties）

### `easyfk.config.lock.redisson` ← RedissonProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `enabled` | `boolean` | `false` | 是否启用Redisson Lock |
| `address` | `String` | `"redis://127.0.0.1:6379"` |  |
| `password` | `String` | `—` |  |
| `username` | `String` | `—` |  |
| `database` | `int` | `0` |  |
| `minimum-idle-size` | `int` | `10` | 最小空闲的Redis连接量 |
| `pattern` | `RedisPattern` | `RedisPattern.SINGLE` | redis模式，默认是单机模式 |
| `slave-addresses` | `String[]` | `—` | 主从模式从节点地址 |
| `master-addresses` | `String` | `—` | 主从模式主节点地址 |
| `sentinel-addresses` | `String[]` | `—` | 哨兵模式节点地址 |
| `master-name` | `String` | `—` | 哨兵模式MasterName |
| `node-address` | `String[]` | `—` | 集群模式节点地址 |


## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `lock-redisson` | `com.mcst.easyfk.lock.redisson.config.RLockConfig` |

## 类型索引

- `com.mcst.easyfk.lock.redisson`：[RLockTemplate](#rlocktemplate)
- `com.mcst.easyfk.lock.redisson.config`：[RLockConfig](#rlockconfig)
- `com.mcst.easyfk.lock.redisson.enums`：[LockType](#locktype)、[RedisPattern](#redispattern)
- `com.mcst.easyfk.lock.redisson.exception`：[LockAcquireFailedException](#lockacquirefailedexception)
- `com.mcst.easyfk.lock.redisson.manager`：[RedissonLockManager](#redissonlockmanager)
- `com.mcst.easyfk.lock.redisson.properties`：[RedissonProperties](#redissonproperties)

## 包 `com.mcst.easyfk.lock.redisson`

### RLockTemplate

`public class RLockTemplate`　分布式锁模板 withTryLock / withTryLockMulti / withNestedLock 加锁失败时抛 LockAcquireFailedException（业务方法不执行）…

**构造器**

```java
RLockTemplate(RedissonLockManager redissonLockManager)
```

**方法**

```java
RLock getLock(String key, LockType lockType)  // 获取锁对象
RLock tryLock(String key, long waitTime, long leaseTime, TimeUnit unit, LockType lockType) throws InterruptedException  // 加锁并返回锁对象 获取失败返回 null
void unlock(RLock lock)  // 释放锁
<T, E extends Exception> T withTryLock(String key, ThrowingSupplier<T, E> bizMethod) throws Exception  // 加锁执行业务方法 无等待尝试加锁执，加锁失败立即抛出异常 默认使用公平锁 加锁成功后，启用看门狗机制，自动续期
<T, E extends Exception> T withTryLock(String key, LockType lockType, ThrowingSupplier<T, E> bizMethod) throws Exception  // 加锁执行业务方法 无等待尝试加锁执，加锁失败立即抛出异常 加锁成功后，启用看门狗机制，自动续期
<T, E extends Exception> T withTryLock(String key, long waitTime, TimeUnit unit, ThrowingSupplier<T, E> bizMethod) throws Exception  // 加锁执行业务方法 阻塞等待指定时间 默认使用公平锁 加锁成功后，启用看门狗机制，自动续期
<T, E extends Exception> T withTryLock(String key, long waitTime, TimeUnit unit, LockType lockType, ThrowingSupplier<T, E> bizMethod) throws Exception  // 加锁执行业务方法 阻塞等待指定时间 加锁成功后，启用看门狗机制，自动续期
<T, E extends Exception> T withTryLock(String key, long waitTime, long leaseTime, TimeUnit unit, ThrowingSupplier<T, E> bizMethod) throws Exception  // 加锁执行业务方法 阻塞等待，自定义锁的租约时间 默认使用公平锁
<T, E extends Exception> T withTryLock(String key, long waitTime, long leaseTime, TimeUnit unit, LockType lockType, ThrowingSupplier<T, E> bizMethod) throws Exception  // 加锁执行业务方法 阻塞等待，自定义锁的租约时间
<T, E extends Exception> T withTryLockMulti(List<String> keys, long waitTime, TimeUnit unit, ThrowingSupplier<T, E> bizMethod) throws Exception  // 批量加锁执行业务方法 按 keys 字典序排序后依次加锁，防止死锁 任一锁获取失败则释放已获取的锁并抛出异常
<T, E extends Exception> T withTryLockMulti(List<String> keys, long waitTime, long leaseTime, TimeUnit unit, LockType lockType, ThrowingSupplier<T, E> bizMethod) throws Exception  // 批量加锁执行业务方法 按 keys 字典序排序后依次加锁，防止死锁 任一锁获取失败则释放已获取的锁并抛出异常
<T, E extends Exception> T withNestedLock(String outerKey, List<String> innerKeys, long waitTime, TimeUnit unit, ThrowingSupplier<T, E> bizMethod) throws Exception  // 嵌套锁执行业务方法 先获取外层锁，再批量获取内层锁，最后执行业务 适用于：订单锁（幂等）+ 商品锁（并发控制）的场景
<T, E extends Exception> T withNestedLock(String outerKey, List<String> innerKeys, long waitTime, long leaseTime, TimeUnit unit, LockType lockType, ThrowingSupplier<T, E> bizMethod) throws Exception  // 嵌套锁执行业务方法（完整参数版）
```

## 包 `com.mcst.easyfk.lock.redisson.config`

### RLockConfig

`public class RLockConfig`　注解：`@AutoConfiguration` `@EnableConfigurationProperties(RedissonProperties.class)` `@ConditionalOnProperty(prefix = "easyfk.config.lock.redisson", name = "enabled", havingValue = "true")`

**方法**

```java
@Bean RedissonLockManager redissonLockManager(RedissonClient redissonClient)
@Bean RLockTemplate redissonLockTemplate(RedissonLockManager redissonLockManager)
@Bean(destroyMethod = "shutdown") @ConditionalOnMissingBean RedissonClient redissonClient()
```

## 包 `com.mcst.easyfk.lock.redisson.enums`

### LockType

`public enum LockType`

**枚举常量**

```java
REENTRANT_LOCK  // 可重入锁
FAIR_LOCK  // 公平锁
READ_LOCK  // 读锁
WRITE_LOCK  // 写锁
```

### RedisPattern

`public enum RedisPattern`

**枚举常量**

```java
MASTERSLAVE  // 主从
SINGLE  // 单例
SENTINEL  // 哨兵
CLUSTER  // 集群
```

## 包 `com.mcst.easyfk.lock.redisson.exception`

### LockAcquireFailedException

`public class LockAcquireFailedException extends BusinessException`　Lombok：`@Getter`　在等待时间内未能获取分布式锁 由 RLockTemplate.withTryLock / withTryLockMulti / withNestedLock 抛出， 用于与"业务方法返回 null"区分…

**字段 / 常量**

```java
static final String ERROR_CODE = "LOCK_ACQUIRE_FAILED"
final String lockKey  // 获取失败的锁 key
```

**构造器**

```java
LockAcquireFailedException(String lockKey)
```

## 包 `com.mcst.easyfk.lock.redisson.manager`

### RedissonLockManager

`public class RedissonLockManager`　按锁类型获取 Redisson 锁对象，lockType 为 null 时使用公平锁

**构造器**

```java
RedissonLockManager(RedissonClient redissonClient)
```

**方法**

```java
RLock getRedisLock(String key, LockType lockType)
```

## 包 `com.mcst.easyfk.lock.redisson.properties`

### RedissonProperties

`public class RedissonProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.lock.redisson")`

**字段 / 常量**

```java
boolean enabled = false  // 是否启用Redisson Lock
String address = "redis://127.0.0.1:6379"
String password
String username
int database = 0
int minimumIdleSize = 10  // 最小空闲的Redis连接量
RedisPattern pattern = RedisPattern.SINGLE  // redis模式，默认是单机模式
String[] slaveAddresses  // 主从模式从节点地址
String masterAddresses  // 主从模式主节点地址
String[] sentinelAddresses  // 哨兵模式节点地址
String masterName  // 哨兵模式MasterName
String[] nodeAddress  // 集群模式节点地址
```
