# easyfk-component-autoId API 签名速查（easyfk 3.2.12）

> 坐标：`com.mcst:autoId-api、autoId-redis`　源码：`easyfk-component/component-autoId/autoId-api`、`easyfk-component/component-autoId/autoId-redis`
> 由 `scripts/gen-api.py` 从 4 个源文件自动提取，共 4 个类型、25 个方法/构造器、2 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-component-autoId-skill.md](../modules/easyfk-component-autoId-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 配置项（@ConfigurationProperties）

### `easyfk.config.autoid.redisson` ← RedisAutoIdProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `datasource` | `String` | `RedisConstants.DEFAULT_DATASOURCE` |  |
| `database` | `String` | `RedisConstants.DEFAULT_DATABASE` |  |


## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `autoId-redis` | `com.mcst.easyfk.autoId.redis.config.RedisAutoIdConfig` |

## 类型索引

- `com.mcst.easyfk.autoId.api`：[IAutoIdService](#iautoidservice)
- `com.mcst.easyfk.autoId.redis`：[AutoIdRedisServiceImpl](#autoidredisserviceimpl)
- `com.mcst.easyfk.autoId.redis.config`：[RedisAutoIdConfig](#redisautoidconfig)
- `com.mcst.easyfk.autoId.redis.properties`：[RedisAutoIdProperties](#redisautoidproperties)

## 包 `com.mcst.easyfk.autoId.api`

### IAutoIdService

`public interface IAutoIdService`

**方法**

```java
String createIncrementId()  // 创建自增ID
String createIncrementId(String category)  // 根据分类创建自增ID
String createIncrementId(int length)  // 创建指定长度的自增ID
String createIncrementId(String category, int length)  // 根据分类和长度创建自增ID
String createDateIncrementId()  // 创建基于日期的自增ID
String createDateIncrementId(String category)  // 根据分类创建基于日期的自增ID
String createDateIncrementId(String category, Integer length)  // 根据分类和长度创建基于日期的自增ID
String createDateIncrementId(Integer length)  // 创建指定长度的基于日期的自增ID
String createDateHourIncrementId()  // 创建基于日期和小时的自增ID
String createDateHourIncrementId(String category)  // 根据分类创建基于日期和小时的自增ID
String createDateHourIncrementId(Integer length)  // 创建指定长度的基于日期和小时的自增ID
String createDateHourIncrementId(String category, Integer length)  // 根据分类和长度创建基于日期和小时的自增ID
```

## 包 `com.mcst.easyfk.autoId.redis`

### AutoIdRedisServiceImpl

`public class AutoIdRedisServiceImpl implements IAutoIdService`　注解：`@SuppressWarnings("unused")`

**方法**

```java
String createIncrementId()
String createIncrementId(String category)
String createIncrementId(int length)
String createIncrementId(String category, int length)
String createDateIncrementId()
String createDateIncrementId(String category)
String createDateIncrementId(String category, Integer length)
String createDateIncrementId(Integer length)
String createDateHourIncrementId()
String createDateHourIncrementId(String category)
String createDateHourIncrementId(Integer length)
String createDateHourIncrementId(String category, Integer length)
```

## 包 `com.mcst.easyfk.autoId.redis.config`

### RedisAutoIdConfig

`public class RedisAutoIdConfig`　注解：`@AutoConfiguration` `@EnableConfigurationProperties(RedisAutoIdProperties.class)`

**方法**

```java
@Bean @ConditionalOnMissingBean(IAutoIdService.class) IAutoIdService autoIdService()
```

## 包 `com.mcst.easyfk.autoId.redis.properties`

### RedisAutoIdProperties

`public class RedisAutoIdProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.autoid.redisson")`

**字段 / 常量**

```java
String datasource = RedisConstants.DEFAULT_DATASOURCE
String database = RedisConstants.DEFAULT_DATABASE
```
