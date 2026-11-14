# AutoId-Redis 开发手册

## 1. 模块概述

`autoId-redis` 是 EasyFK 框架中基于 Redis 的分布式自增 ID 生成组件。该模块利用 Redis 的原子自增（INCR）特性，提供全局唯一、有序递增的 ID 生成能力，支持纯数字自增 ID、日期前缀自增 ID、日期小时前缀自增 ID 三种生成模式，适用于订单号、流水号、业务编码等场景。

## 2. 依赖引入

在项目的 `build.gradle` 中添加依赖：

```gradle
dependencies {
    implementation project(':component-autoId:autoId-redis')
}
```

该模块会自动传递引入以下依赖：
- `autoId-api` — 自增 ID 服务接口定义
- `db-redis` — EasyFK Redis 操作组件

## 3. 配置说明

### 3.1 配置属性

所有配置项统一在 `easyfk.config.autoid.redisson` 前缀下。

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `datasource` | String | `RedisConstants.DEFAULT_DATASOURCE` | Redis 数据源名称 |
| `database` | String | `RedisConstants.DEFAULT_DATABASE` | Redis 数据库名称 |

### 3.2 配置示例

```yaml
easyfk:
  config:
    autoid:
      redisson:
        datasource: default
        database: default
```

大多数场景下，使用默认配置即可，无需额外配置。

## 4. 使用方式

### 4.1 注入服务

引入依赖后，`IAutoIdService` 会通过 Spring Boot 自动配置自动注册为 Bean，直接注入即可使用。

```java
@Service
public class OrderService {

    @Resource
    private IAutoIdService autoIdService;
}
```

### 4.2 三种 ID 生成模式

#### 模式一：纯数字自增 ID

生成全局递增的纯数字 ID，默认 6 位，不足前补零。

```java
// 生成默认6位自增ID，如：000001、000002、000110
String id = autoIdService.createIncrementId();

// 按分类生成自增ID（不同分类独立计数）
String orderId = autoIdService.createIncrementId("order");
String userId = autoIdService.createIncrementId("user");

// 指定ID长度，如8位：00000001
String id = autoIdService.createIncrementId(8);

// 按分类 + 指定长度
String orderId = autoIdService.createIncrementId("order", 10);
```

**输出示例：**

| 调用 | 输出 |
|------|------|
| `createIncrementId()` | `000001` |
| `createIncrementId()` | `000002` |
| `createIncrementId("order")` | `000001` |
| `createIncrementId(8)` | `00000001` |

#### 模式二：日期 + 自增 ID

生成 `yyyyMMdd` 日期前缀 + 自增序号的 ID，每日自动归零重新计数，缓存有效期 25 小时。

```java
// 默认6位序号：20260227000001
String id = autoIdService.createDateIncrementId();

// 按分类生成
String orderId = autoIdService.createDateIncrementId("order");

// 指定序号长度，如8位：2026022700000001
String id = autoIdService.createDateIncrementId(8);

// 按分类 + 指定长度
String orderId = autoIdService.createDateIncrementId("order", 10);
```

**输出示例：**

| 调用 | 输出格式 | 示例 |
|------|----------|------|
| `createDateIncrementId()` | `yyyyMMdd` + 6位序号 | `20260227000001` |
| `createDateIncrementId(8)` | `yyyyMMdd` + 8位序号 | `2026022700000001` |

#### 模式三：日期小时 + 自增 ID

生成 `yyyyMMddHH` 日期小时前缀 + 自增序号的 ID，每小时自动归零重新计数，缓存有效期 65 分钟。

```java
// 默认6位序号：2026022714000001
String id = autoIdService.createDateHourIncrementId();

// 按分类生成
String orderId = autoIdService.createDateHourIncrementId("order");

// 指定序号长度
String id = autoIdService.createDateHourIncrementId(8);

// 按分类 + 指定长度
String orderId = autoIdService.createDateHourIncrementId("order", 10);
```

**输出示例：**

| 调用 | 输出格式 | 示例 |
|------|----------|------|
| `createDateHourIncrementId()` | `yyyyMMddHH` + 6位序号 | `2026022714000001` |
| `createDateHourIncrementId(8)` | `yyyyMMddHH` + 8位序号 | `202602271400000001` |

## 5. API 参考

### IAutoIdService 接口方法

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `createIncrementId()` | — | 6位自增ID | 全局自增 ID |
| `createIncrementId(category)` | 分类名称 | 6位自增ID | 按分类独立计数 |
| `createIncrementId(length)` | ID长度 | 指定长度自增ID | 自定义位数 |
| `createIncrementId(category, length)` | 分类名称, ID长度 | 指定长度自增ID | 分类 + 自定义位数 |
| `createDateIncrementId()` | — | 日期+6位序号 | 每日归零 |
| `createDateIncrementId(category)` | 分类名称 | 日期+6位序号 | 按分类每日归零 |
| `createDateIncrementId(length)` | 序号长度 | 日期+指定长度序号 | 自定义序号位数 |
| `createDateIncrementId(category, length)` | 分类名称, 序号长度 | 日期+指定长度序号 | 分类 + 自定义序号位数 |
| `createDateHourIncrementId()` | — | 日期小时+6位序号 | 每小时归零 |
| `createDateHourIncrementId(category)` | 分类名称 | 日期小时+6位序号 | 按分类每小时归零 |
| `createDateHourIncrementId(length)` | 序号长度 | 日期小时+指定长度序号 | 自定义序号位数 |
| `createDateHourIncrementId(category, length)` | 分类名称, 序号长度 | 日期小时+指定长度序号 | 分类 + 自定义序号位数 |

## 6. 自动配置机制

| 配置类 | 说明 |
|--------|------|
| `RedisAutoIdConfig` | 自动注册 `IAutoIdService` Bean（实现类 `AutoIdRedisServiceImpl`） |

- 通过 Spring Boot `AutoConfiguration.imports` 声明自动配置入口
- 使用 `@EnableConfigurationProperties` 自动绑定配置属性
- 引入依赖即生效，无需手动注册 Bean

## 7. 内部实现说明

### 7.1 Redis Key 结构

| 类型 | Key 格式 | 过期时间 |
|------|----------|----------|
| 纯自增 | `{namespace}:{database}:{category}` | 不过期（永久递增） |
| 日期自增 | `{namespace}:{database}:{category}_yyyyMMdd` | 25 小时 |
| 日期小时自增 | `{namespace}:{database}:{category}_yyyyMMddHH` | 65 分钟 |

- 命名空间固定为 `AutoIdCache`
- 默认 category 为 `AutoIdKey`
- 日期/小时类型的 Key 包含时间戳后缀，过期后自动清理

### 7.2 ID 补零规则

所有生成的序号部分均会左补零到指定位数。例如序号值为 `110`，指定长度为 6，则输出 `000110`。

## 8. 实战示例

### 8.1 订单号生成

```java
@Service
public class OrderService {

    @Resource
    private IAutoIdService autoIdService;

    public String generateOrderNo() {
        // 生成格式：ORD20260227000001
        return "ORD" + autoIdService.createDateIncrementId("order");
    }

    public String generateRefundNo() {
        // 生成格式：REF2026022714000001
        return "REF" + autoIdService.createDateHourIncrementId("refund");
    }
}
```

### 8.2 多业务独立编号

```java
@Service
public class CodeGenerator {

    @Resource
    private IAutoIdService autoIdService;

    public String generateUserCode() {
        // 用户编码：U000001（全局递增，不归零）
        return "U" + autoIdService.createIncrementId("user");
    }

    public String generateInvoiceNo() {
        // 发票号：INV20260227-00000001（日期+8位序号，每日归零）
        String dateId = autoIdService.createDateIncrementId("invoice", 8);
        return "INV" + dateId.substring(0, 8) + "-" + dateId.substring(8);
    }
}
```

## 9. 最佳实践

1. **合理使用分类（category）**：不同业务使用不同分类名，避免 ID 序号空间冲突，如 `"order"`、`"user"`、`"payment"` 等。
2. **选择合适的 ID 模式**：
   - 需要全局唯一递增 → `createIncrementId`
   - 需要按日区分且可读性强 → `createDateIncrementId`
   - 高频业务需要更细粒度归零 → `createDateHourIncrementId`
3. **预估序号长度**：根据业务量预估日/小时最大 ID 数，设置足够的 `length`，避免溢出指定位数。默认 6 位最多支持 999999 条/周期。
4. **确保 Redis 可用性**：该组件依赖 Redis 原子操作，请确保 Redis 服务高可用，避免 ID 生成中断。

## 10. 包结构

```
com.mcst.easyfk.autoId.redis
├── config
│   └── RedisAutoIdConfig.java            # Spring Boot 自动配置类
├── properties
│   └── RedisAutoIdProperties.java        # 配置属性绑定类
└── AutoIdRedisServiceImpl.java           # IAutoIdService 接口的 Redis 实现

com.mcst.easyfk.autoId.api
└── IAutoIdService.java                   # 自增 ID 服务接口定义（autoId-api 模块）
```
