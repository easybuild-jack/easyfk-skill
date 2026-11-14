# component-lock Skill 参考文档

> 所属项目：`easyfk-component`　子模块：`lock-redisson`
> 坐标：`com.mcst:lock-redisson:3.2.12`
> 依据：`lock-redisson` 全部源码（`RLockConfig`、`RedissonProperties`、`RLockTemplate`、`RedissonLockManager`、`LockAcquireFailedException`、枚举）；对齐 `lock-redisson开发手册.md`、`lock-redisson技术特点.md`。
> 以源码为准；差异见文末「复查记录」。

---

## 1. 模块定位

基于 Redisson 的分布式锁模板。它**自己创建 `RedissonClient`**，与 db-redis 的连接配置相互独立，所以 Redis 地址要单独再配置一份。依赖只有 `org.redisson:redisson`（排除了 jackson 和 snakeyaml）；`easyfk-core` 是 compileOnly，运行时由业务项目提供（引入 web/service 等模块时会自然带上）。框架内部没有其他模块依赖它。

## 2. 启用与配置（前缀 `easyfk.config.lock.redisson`）

```yaml
easyfk:
  config:
    lock:
      redisson:
        enabled: true                        # 必须显式开启，否则整个模块都不生效
        pattern: SINGLE                      # SINGLE / MASTERSLAVE / SENTINEL / CLUSTER
        address: redis://10.0.0.1:6379       # SINGLE 模式使用，必须带 redis:// 或 rediss:// 前缀
        username:                            # 所有模式（Redis 6 ACL）
        password: xxx                        # 所有模式
        database: 0                          # CLUSTER 模式不支持（Redis Cluster 只有 db0），其余模式生效
        minimum-idle-size: 10                # 所有模式；主从/哨兵/集群同时用于 master 和 slave 连接池
        # MASTERSLAVE：master-addresses: redis://...   slave-addresses: [redis://..., ...]
        # SENTINEL：master-name: mymaster    sentinel-addresses: [redis://...:26379, ...]
        # CLUSTER：node-address: [redis://...:7000, ...]
```

激活后注册的 Bean：
- `redissonClient`：带 `@ConditionalOnMissingBean`，可以用自定义的 RedissonClient 覆盖，`destroyMethod=shutdown`；
- `redissonLockManager`；
- `redissonLockTemplate`（类型为 `RLockTemplate`）。

## 3. 锁类型（`LockType`）

| 枚举 | Redisson 对象 | 说明 |
|---|---|---|
| `FAIR_LOCK`（**所有模板方法的默认值**，传 null 时也用它） | `getFairLock(key)` | 按排队顺序获取，可重入；比普通锁多维护一个队列和超时集合，开销较大 |
| `REENTRANT_LOCK` | `getLock(key)` | 普通可重入锁，性能最好 |
| `READ_LOCK` / `WRITE_LOCK` | `getReadWriteLock(key).readLock()/writeLock()` | 读写锁 |

**同一个 key 只能使用一种锁类型**：读写锁与普通锁、公平锁使用的 Redis 数据结构不同，混用会导致互斥失效或出错。

## 4. RLockTemplate API

| 方法 | 加锁方式 | 失败时 |
|---|---|---|
| `withTryLock(key, biz)` / `(key, lockType, biz)` | `tryLock()` 不等待，看门狗续期 | 抛 `LockAcquireFailedException` |
| `withTryLock(key, waitTime, unit, biz)` / `(key, waitTime, unit, lockType, biz)` | `tryLock(wait, -1, unit)`，看门狗续期 | 抛 `LockAcquireFailedException` |
| `withTryLock(key, waitTime, leaseTime, unit, biz)` / `(…, lockType, biz)` | `tryLock(wait, lease, unit)`，lease 大于 0 时到期自动释放，不续期 | 抛 `LockAcquireFailedException` |
| `withTryLockMulti(keys, waitTime, unit, biz)` / `(keys, wait, lease, unit, lockType, biz)` | 复制 keys 并按字典序排序后依次加锁（不去重，重复 key 依赖可重入）；**waitTime 是所有锁共享的总等待时间**，耗尽后剩余的锁各做一次不等待的尝试 | 释放已获取的锁并抛 `LockAcquireFailedException`（`lockKey` 为失败的那个 key）；**keys 为空时不加锁，直接执行 biz** |
| `withNestedLock(outerKey, innerKeys, waitTime, unit, biz)` / `(…, lease, unit, lockType, biz)` | 外层锁最多等 waitTime，内层锁再共享一个新的 waitTime | 释放已获取的锁并抛 `LockAcquireFailedException` |
| `tryLock(key, wait, lease, unit, lockType)` | 手动加锁 | 返回 null（返回值是锁对象，不存在歧义） |
| `unlock(lock)` | 只有当前线程持有锁时才释放 | — |
| `getLock(key, lockType)` | 只拿到锁对象，不加锁 | — |

- `biz` 的类型是 `com.mcst.easyfk.core.function.ThrowingSupplier<T, E>`，业务异常会原样抛出，`finally` 中释放锁。
- 加锁失败时抛 `com.mcst.easyfk.lock.redisson.exception.LockAcquireFailedException`（继承 `BusinessException`，`errorCode = LOCK_ACQUIRE_FAILED`，`getLockKey()` 返回失败的 key），biz 不会执行；biz 返回 null 时原样返回 null。
- `unit` 为 null 时抛 `IllegalArgumentException`（无等待的 `withTryLock(key, biz)` 不需要 unit）；`lockType` 为 null 时一律使用公平锁。
- 锁的释放与线程绑定：biz 内部切换线程或异步执行时，锁不会跟随过去，在 finally 中也只会释放当前线程持有的锁。

```java
@Resource private RLockTemplate lockTemplate;

public BaseResult<?> submit(String orderId) throws Exception {
    try {
        return lockTemplate.withTryLock("order:submit:" + orderId, 3, TimeUnit.SECONDS,
                LockType.REENTRANT_LOCK, () -> doSubmit(orderId));
    } catch (LockAcquireFailedException e) {
        return BRBuilder.failResult(null, "请勿重复提交");
    }
}
```

## 5. 生成代码时的规则

**Do**
- 配置 `enabled: true`，并单独配置 Redisson 的地址（带 `redis://` 前缀）。
- 性能敏感时显式传 `LockType.REENTRANT_LOCK`，只有确实需要先来先得时才用默认的公平锁。
- key 使用 `业务:资源:id` 的细粒度格式，并加上应用前缀，避免多个应用之间冲突。
- 捕获 `LockAcquireFailedException` 处理加锁失败（或交给全局 `BusinessException` 处理）；耗时不确定的业务用看门狗（不传 leaseTime 或传 -1）。

**Don't**
- 配置前缀只用 `easyfk.config.lock.redisson`，不要照原手册写其他前缀或 `host`/`port`；不要用返回 null 判断加锁失败。
- 不要用空的 keys 调用 `withTryLockMulti` 并期望"不加锁就失败"（它会直接执行 biz）。
- 不要在同一个 key 上混用读写锁和普通锁；不要在 biz 中异步执行受保护的逻辑。

## 6. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | 手册 §3 | 配置前缀不是 `easyfk.config` 开头 | 实际前缀是 `easyfk.config.lock.redisson`，按原手册配置完全不生效（skill 内的手册副本已改正前缀） |
| 2 | 手册 §3.1 / §3.2 | `host`、`port` 两个属性 | 没有这两个属性，使用的是 `address`（默认 `redis://127.0.0.1:6379`，必须带 scheme）；手册也漏了 `username` |
| 3 | 手册 §8、技术特点"零配置自动激活" | 引入依赖即自动注册三个 Bean | `RLockConfig` 带有 `@ConditionalOnProperty(name = "enable", havingValue = "true")`，**不配置就不生效**。另外属性类中的字段叫 `enabled`，与条件里的 `enable` 不一致：写 `enabled: true` 不会激活 **已修复**：条件改为 `enabled`，与属性字段一致，配置 `enabled: true` 激活 |
| 4 | 手册 §3.1 | 各模式通用 password、database、minimumIdleSize | `username` 和 `minimumIdleSize` 只有 SINGLE 模式使用；CLUSTER 模式不设置 database **已修复**：username、password、minimumIdleSize 应用到所有模式（主从/哨兵/集群同时设置 master 与 slave 最小空闲连接），database 应用到除 CLUSTER 外的模式；CLUSTER 只有 db0，按设计不支持 database |
| 5 | 手册 §6 / 技术特点 | 加锁失败返回 null | 与源码一致，但这与"业务返回 null"无法区分；Javadoc 写的"加锁失败时抛出异常"不对 **已修复**：`withTryLock/withTryLockMulti/withNestedLock` 加锁失败抛 `LockAcquireFailedException`（继承 `BusinessException`），业务返回 null 原样返回；Javadoc 已同步，手动 `tryLock` 仍返回 null |
| 6 | 技术特点"超时全回滚" | 批量锁任一失败就全部释放 | 与源码一致。补充：waitTime 是所有锁共享的总时长；keys 为空时直接执行业务；嵌套锁的内层锁会重新计算一个 waitTime；总等待时间耗尽后，剩余的锁各做一次不等待的尝试 |
| 7 | 手册 §10 | 公平锁是默认值 | 与源码一致，`lockType` 为 null 时也回退到公平锁。手册没有说明公平锁的额外开销 |
| 8 | 源码 | — | `RedisLockUtil` 与 `RedissonLockManager` 的实现重复；Redisson 的连接独立于 db-redis，需要配置两套 Redis 连接信息 **已修复**：删除 `RedisLockUtil`，统一使用 `RedissonLockManager`（lockType 为 null 时回退公平锁）；Redisson 连接独立于 db-redis 仍属设计如此 |
