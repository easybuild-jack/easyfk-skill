# lock-redisson 开发手册

## 1. 模块概述

`lock-redisson` 是 EasyFK 框架中基于 Redisson 的分布式锁组件。该模块提供四种锁类型（可重入锁、公平锁、读锁、写锁）、四种 Redis 部署模式（单机、主从、哨兵、集群）、看门狗自动续期机制，以及模板化的加锁执行 API（单锁、批量锁、嵌套锁），适用于分布式环境下的并发控制、资源互斥、幂等防重等场景。

## 2. 依赖引入

### Maven

```xml
<dependency>
    <groupId>com.mcst</groupId>
    <artifactId>lock-redisson</artifactId>
</dependency>
```

### Gradle

```gradle
dependencies {
    implementation 'com.mcst:lock-redisson'
}
```

> 版本号由框架统一 BOM 管理，无需手动指定。

该模块会自动传递引入以下依赖：
- `redisson` — Redisson 分布式锁客户端

## 3. 配置说明

### 3.1 配置属性

所有配置项统一在 `easyfk.config.lock.redisson` 前缀下。

#### 基础配置

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `host` | String | `127.0.0.1` | Redis 服务器地址 |
| `port` | int | `6379` | Redis 服务器端口 |
| `password` | String | — | 连接密码 |
| `database` | int | `0` | 数据库索引 |
| `minimumIdleSize` | int | `10` | 最小空闲连接数 |
| `pattern` | RedisPattern | `SINGLE` | Redis 部署模式 |

#### 主从模式配置

| 属性 | 类型 | 说明 |
|------|------|------|
| `masterAddresses` | String | 主节点地址 |
| `slaveAddresses` | String[] | 从节点地址列表 |

#### 哨兵模式配置

| 属性 | 类型 | 说明 |
|------|------|------|
| `sentinelAddresses` | String[] | 哨兵节点地址列表 |
| `masterName` | String | 主服务器名称 |

#### 集群模式配置

| 属性 | 类型 | 说明 |
|------|------|------|
| `nodeAddress` | String[] | 集群节点地址列表 |

### 3.2 配置示例

#### 单机模式

```yaml
easyfk:
  config:
    lock:
      redisson:
        host: 192.168.1.100
        port: 6379
        password: your_password
        database: 0
        minimumIdleSize: 10
        pattern: SINGLE
```

#### 哨兵模式

```yaml
easyfk:
  config:
    lock:
      redisson:
        password: your_password
        database: 0
        pattern: SENTINEL
        masterName: mymaster
        sentinelAddresses:
          - redis://192.168.1.100:26379
          - redis://192.168.1.101:26379
          - redis://192.168.1.102:26379
```

#### 集群模式

```yaml
easyfk:
  config:
    lock:
      redisson:
        password: your_password
        pattern: CLUSTER
        nodeAddress:
          - redis://192.168.1.100:7000
          - redis://192.168.1.100:7001
          - redis://192.168.1.100:7002
          - redis://192.168.1.101:7000
          - redis://192.168.1.101:7001
          - redis://192.168.1.101:7002
```

#### 主从模式

```yaml
easyfk:
  config:
    lock:
      redisson:
        password: your_password
        database: 0
        pattern: MASTERSLAVE
        masterAddresses: redis://192.168.1.100:6379
        slaveAddresses:
          - redis://192.168.1.101:6379
          - redis://192.168.1.102:6379
```

## 4. 锁类型说明

通过 `LockType` 枚举指定锁类型：

| 锁类型 | 枚举值 | 说明 |
|--------|--------|------|
| **可重入锁** | `REENTRANT_LOCK` | 同一线程可多次获取同一把锁，不会死锁 |
| **公平锁** | `FAIR_LOCK` | 按请求顺序获取锁，保证公平性（**默认**） |
| **读锁** | `READ_LOCK` | 读写锁的读端，允许多个线程同时持有 |
| **写锁** | `WRITE_LOCK` | 读写锁的写端，互斥独占 |

## 5. 使用方式

### 5.1 注入 RLockTemplate

```java
@Service
public class OrderService {

    @Resource
    private RLockTemplate rLockTemplate;
}
```

### 5.2 核心概念

- **waitTime**：等待获取锁的最长时间，超时返回 `null`
- **leaseTime**：锁的租约时间（持有时间）。设为 `-1` 表示启用**看门狗机制**，自动续期直到手动释放
- **看门狗机制**：Redisson 默认每 10 秒自动续期锁，防止业务未完成锁就过期

## 6. API 参考

### 6.1 RLockTemplate 方法一览

#### 基础锁操作

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `getLock(key, lockType)` | 锁 key, 锁类型 | `RLock` | 获取锁对象（不加锁） |
| `tryLock(key, waitTime, leaseTime, unit, lockType)` | 锁 key, 等待时间, 租约时间, 时间单位, 锁类型 | `RLock` | 尝试加锁，成功返回锁对象，失败返回 `null` |
| `unlock(lock)` | 锁对象 | void | 释放锁（自动检查当前线程持有） |

#### 模板化加锁执行（推荐）

| 方法 | 说明 |
|------|------|
| `withTryLock(key, bizMethod)` | 无等待尝试加锁，公平锁，看门狗续期 |
| `withTryLock(key, lockType, bizMethod)` | 无等待尝试加锁，指定锁类型，看门狗续期 |
| `withTryLock(key, waitTime, unit, bizMethod)` | 带等待时间，公平锁，看门狗续期 |
| `withTryLock(key, waitTime, unit, lockType, bizMethod)` | 带等待时间，指定锁类型，看门狗续期 |
| `withTryLock(key, waitTime, leaseTime, unit, bizMethod)` | 带等待和租约时间，公平锁 |
| `withTryLock(key, waitTime, leaseTime, unit, lockType, bizMethod)` | 完整参数版，指定所有选项 |

#### 批量加锁

| 方法 | 说明 |
|------|------|
| `withTryLockMulti(keys, waitTime, unit, bizMethod)` | 批量加锁，公平锁，看门狗续期 |
| `withTryLockMulti(keys, waitTime, leaseTime, unit, lockType, bizMethod)` | 批量加锁，完整参数版 |

#### 嵌套加锁

| 方法 | 说明 |
|------|------|
| `withNestedLock(outerKey, innerKeys, waitTime, unit, bizMethod)` | 嵌套锁，公平锁，看门狗续期 |
| `withNestedLock(outerKey, innerKeys, waitTime, leaseTime, unit, lockType, bizMethod)` | 嵌套锁，完整参数版 |

> 所有 `withTryLock*` 方法：加锁成功执行业务并返回结果，加锁失败返回 `null`。**锁的释放完全自动**，无需手动 `unlock`。

## 7. 实战示例

### 7.1 最简用法：无等待加锁

```java
@Service
public class OrderService {

    @Resource
    private RLockTemplate rLockTemplate;

    public BaseResult<?> createOrder(OrderDTO order) throws Exception {
        return rLockTemplate.withTryLock("order:create:" + order.getUserId(), () -> {
            // 加锁成功，执行创建订单逻辑
            return doCreateOrder(order);
        });
        // 返回 null 表示加锁失败（有其他线程正在处理）
    }
}
```

### 7.2 带等待时间加锁

```java
public BaseResult<?> processPayment(String orderId) throws Exception {
    return rLockTemplate.withTryLock(
        "payment:" + orderId,
        5, TimeUnit.SECONDS,          // 最多等待 5 秒
        () -> {
            return doPayment(orderId);
        }
    );
}
```

### 7.3 指定租约时间（禁用看门狗）

```java
public void syncData(String taskId) throws Exception {
    rLockTemplate.withTryLock(
        "sync:" + taskId,
        10, 60, TimeUnit.SECONDS,     // 等待 10 秒，锁最多持有 60 秒
        () -> {
            doSync(taskId);
            return null;
        }
    );
}
```

### 7.4 指定锁类型

```java
// 使用可重入锁
public void process(String key) throws Exception {
    rLockTemplate.withTryLock(
        "task:" + key,
        5, TimeUnit.SECONDS,
        LockType.REENTRANT_LOCK,
        () -> {
            return doProcess(key);
        }
    );
}

// 使用读锁（允许并发读）
public ProductDTO getProduct(String productId) throws Exception {
    return rLockTemplate.withTryLock(
        "product:" + productId,
        LockType.READ_LOCK,
        () -> {
            return queryProduct(productId);
        }
    );
}

// 使用写锁（互斥写）
public void updateProduct(ProductDTO product) throws Exception {
    rLockTemplate.withTryLock(
        "product:" + product.getId(),
        5, TimeUnit.SECONDS,
        LockType.WRITE_LOCK,
        () -> {
            doUpdateProduct(product);
            return null;
        }
    );
}
```

### 7.5 批量加锁：多资源并发控制

批量加锁自动按 key 字典序排序后依次加锁，**有效避免死锁**。任一锁获取失败则释放所有已获取的锁并返回 `null`。

```java
public BaseResult<?> transferStock(List<String> productIds) throws Exception {
    // 对多个商品同时加锁
    List<String> lockKeys = productIds.stream()
        .map(id -> "stock:" + id)
        .collect(Collectors.toList());

    return rLockTemplate.withTryLockMulti(
        lockKeys,
        5, TimeUnit.SECONDS,
        () -> {
            // 所有商品锁获取成功，执行转移库存逻辑
            return doTransferStock(productIds);
        }
    );
}
```

### 7.6 嵌套加锁：订单锁 + 商品锁

先获取外层锁（如订单幂等锁），再批量获取内层锁（如商品并发锁），适用于复合锁场景。

```java
public BaseResult<?> submitOrder(String orderId, List<String> productIds) throws Exception {
    // 外层锁：订单幂等控制
    String outerKey = "order:" + orderId;
    // 内层锁：商品库存并发控制
    List<String> innerKeys = productIds.stream()
        .map(id -> "product:stock:" + id)
        .collect(Collectors.toList());

    return rLockTemplate.withNestedLock(
        outerKey, innerKeys,
        5, TimeUnit.SECONDS,
        () -> {
            // 订单锁 + 所有商品锁均获取成功
            return doSubmitOrder(orderId, productIds);
        }
    );
}
```

### 7.7 手动控制锁（高级用法）

```java
public void manualLockExample(String key) throws InterruptedException {
    RLock lock = rLockTemplate.tryLock(
        key, 5, 30, TimeUnit.SECONDS, LockType.FAIR_LOCK
    );
    if (lock == null) {
        // 加锁失败
        return;
    }
    try {
        // 执行业务逻辑
        doBusiness();
    } finally {
        rLockTemplate.unlock(lock);
    }
}
```

## 8. 自动配置机制

| 配置类 | 说明 |
|--------|------|
| `RLockConfig` | 自动配置入口 |

- 通过 Spring Boot `AutoConfiguration.imports` 声明自动配置入口
- 使用 `@EnableConfigurationProperties` 自动绑定 `RedissonProperties`
- 自动注册三个 Bean：
  - `RedissonClient` — Redisson 客户端（`@ConditionalOnMissingBean`，可自定义覆盖）
  - `RedissonLockManager` — 锁管理器
  - `RLockTemplate` — 锁操作模板
- `RedissonClient` 使用 `destroyMethod = "shutdown"`，应用关闭时自动释放连接

## 9. 包结构

```
com.mcst.easyfk.lock.redisson
├── RLockTemplate.java                # 锁操作模板（核心 API）
├── config
│   └── RLockConfig.java              # Spring Boot 自动配置类
├── enums
│   ├── LockType.java                 # 锁类型枚举（可重入/公平/读/写）
│   └── RedisPattern.java             # Redis 部署模式枚举（单机/主从/哨兵/集群）
├── manager
│   └── RedissonLockManager.java      # 锁管理器（创建锁对象）
├── properties
│   └── RedissonProperties.java       # 配置属性类
└── util
    └── RedisLockUtil.java            # 静态工具类
```

## 10. 最佳实践

1. **优先使用 `withTryLock` 模板方法**：自动管理锁的获取和释放，避免忘记 `unlock` 导致死锁。
2. **合理设置等待时间**：根据业务耗时设置 `waitTime`，避免过长阻塞或过短失败。
3. **善用看门狗机制**：`leaseTime` 设为 `-1`（默认）启用自动续期，适合业务耗时不确定的场景。固定耗时业务可设置明确的租约时间。
4. **批量锁防死锁**：需要同时锁多个资源时使用 `withTryLockMulti`，框架自动按字典序排序加锁。
5. **嵌套锁分层控制**：订单幂等 + 商品并发等复合场景使用 `withNestedLock`。
6. **公平锁 vs 可重入锁**：需要按请求顺序获取锁选公平锁（默认），追求性能选可重入锁。
7. **读写锁提升并发**：读多写少场景使用 `READ_LOCK` / `WRITE_LOCK`，允许并发读、互斥写。
8. **锁粒度尽量细**：按业务资源 ID 加锁（如 `order:{orderId}`），避免用粗粒度锁降低并发能力。
9. **处理加锁失败**：`withTryLock*` 方法加锁失败返回 `null`，业务层需判断并做相应处理（如返回"请勿重复提交"）。
