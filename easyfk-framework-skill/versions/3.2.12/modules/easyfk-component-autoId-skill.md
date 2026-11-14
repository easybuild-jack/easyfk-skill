# component-autoId Skill 参考文档

> 所属项目：`easyfk-component`　子模块：`autoId-api`、`autoId-redis`（空模块 `autoId-tradition` 已删除）
> 坐标：`com.mcst:autoId-api` / `com.mcst:autoId-redis`（3.2.12）
> 依据：两个子模块全部源码，db-redis 的 `RedisOptManager.autoId/executeLuaScript`；对齐 `AutoId-Redis开发手册.md`、`AutoId-Redis技术特点.md`。
> 以源码为准；差异见文末「复查记录」。

---

## 1. 模块定位

| 子模块 | 内容 |
|---|---|
| `autoId-api` | 接口 `com.mcst.easyfk.autoId.api.IAutoIdService` |
| `autoId-redis` | `AutoIdRedisServiceImpl`：基于 Redis INCR 的实现，依赖 db-redis |

## 2. 接入

引入 `com.mcst:autoId-redis` 后由 `RedisAutoIdConfig` 自动注册 `IAutoIdService`（`@ConditionalOnMissingBean`，可自定义实现覆盖）。

配置项（前缀 `easyfk.config.autoid.redisson`）：

```yaml
easyfk:
  config:
    autoid:
      redisson:
        datasource: default  # db-redis 的数据源名
        database: default    # 数据源下的库别名
```

保持默认值 `default` 即可，ID 会落在 db-redis 的默认数据源、默认库上。前提是 db-redis 已经可用：简单模式用 `spring.data.redis.*`，动态模式需配置 `default-data-source`。

## 3. API

| 方法 | 生成结果 | Redis key（namespace 固定为 `AutoIdCache`） | 过期 |
|---|---|---|---|
| `createIncrementId()` / `(category)` / `(int length)` / `(category, int length)` | 自增序号左补零（默认 6 位） | `AutoIdCache::{category}`，默认 category 为 `AutoIdKey` | 永不过期 |
| `createDateIncrementId()` / `(category)` / `(Integer length)` / `(category, Integer length)` | `yyyyMMdd` + 序号 | `AutoIdCache::{category}_yyyyMMdd` | 25h |
| `createDateHourIncrementId()` / `(category)` / `(Integer length)` / `(category, Integer length)` | `yyyyMMddHH` + 序号 | `AutoIdCache::{category}_yyyyMMddHH` | 65min |

```java
@Resource private IAutoIdService autoIdService;

String orderNo = "ORD" + autoIdService.createDateIncrementId("order", 8);   // ORD2026111200000001
```

- 序号来自 INCR，多个实例之间唯一且递增。日期部分取**各实例本机时间**，实例之间时钟不一致时，跨天或跨小时的边界附近可能出现顺序错乱。
- 带日期的两类 ID 通过一段 Lua 脚本原子地执行 INCR，并在 key 没有过期时间时设置 EXPIRE，不会残留永久 key。
- length 是**最小位数**：序号不足时左补零，超出时保留完整序号（ID 变长但不会重复）。需要定长编号时，length 要大于每个周期（不过期的类型则是整个生命周期）最大量的位数。

## 4. 生成代码时的规则

**Do**
- 引入 `autoId-redis` 后直接注入 `IAutoIdService`。
- import 路径写 `com.mcst.easyfk.autoId.api.IAutoIdService`。
- 每个业务使用独立的 category；按"峰值 × 安全系数"来确定 length。纯自增类型尤其要给足位数（比如 12 位以上）。
- 需要真正全局唯一的长期主键时，优先使用雪花算法或数据库主键，这个组件更适合做可读的业务编号。

**Don't**
- 不要再使用旧包名 `com.mcst.eayfk.autoId.api`（已改为 `easyfk`）。
- 不要引用 `autoId-tradition`（已删除）。

## 5. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | 手册 §4.1 / §6、技术特点 | 引入依赖即生效，通过 `AutoConfiguration.imports` 自动注册 | imports 文件路径是 `resources/spring/...`（缺少 `META-INF/`），里面的类名 `AutoIdRedisConfig` 也与实际的 `RedisAutoIdConfig` 不一致，**自动配置完全不生效**，注入 `IAutoIdService` 会失败 **已修复**：imports 移到 `META-INF/spring/` 并改为 `RedisAutoIdConfig`，引入即自动注册 |
| 2 | 手册 §7.1 | key 为 `{namespace}:{database}:{category}` | 实际为 `AutoIdCache::{category}`（双冒号，不包含 database） |
| 3 | 手册 §3.1 | `datasource`、`database` 两个属性 | `createKeyArgs` 调用的是 `createKeyArgs(getDatabase(), getDatabase(), key, ns)`：**`datasource` 没有被使用**，`database` 的值同时被当作数据源名 **已修复**：`createKeyArgs(getDatasource(), getDatabase(), …)`，两个属性各自生效 |
| 4 | 手册 §7.2 / §9、技术特点 | 左补零；默认 6 位最多支持 999999 | 超过位数时 `padPre` 截断为前 length 位，ID 会**重复**，没有任何报错，"全局唯一"在这种情况下不成立 **已修复**：`padZero` 只左补零，超出位数时保留完整序号，不再截断 |
| 5 | 技术特点 | 原子性保证、严格递增 | INCR 本身是原子的；`autoIdByExpire` 中的 INCR、TTL、EXPIRE 分三步执行，不是原子操作（只影响过期设置）。日期前缀使用本机时钟，多实例时的"严格递增"依赖各实例时钟一致 **已修复**：日期类 ID 改为 Lua 脚本原子执行 INCR + 条件 EXPIRE（TTL 写入脚本文本，不经值序列化器）；日期前缀依赖本机时钟仍属设计限制 |
| 6 | 手册 §2 | `implementation project(':component-autoId:autoId-redis')` | 这是框架仓库内部的写法，业务项目应使用 `com.mcst:autoId-redis` |
| 7 | 源码 | — | `autoId-tradition` 没有源码；`RedisAutoIdConfig` 的 Bean 没有 `@ConditionalOnMissingBean`；接口包名拼写为 `eayfk` **已修复**：删除空模块 `autoId-tradition`（settings.gradle 与目录）；Bean 加 `@ConditionalOnMissingBean`；接口包名改为 `com.mcst.easyfk.autoId.api` |
