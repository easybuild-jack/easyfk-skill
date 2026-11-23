# easyfk-component-job API 签名速查（easyfk 3.2.12）

> 坐标：`com.mcst:job-xxl`　源码：`easyfk-component/component-job/job-xxl`
> 由 `scripts/gen-api.py` 从 7 个源文件自动提取，共 7 个类型、13 个方法/构造器、6 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-component-job-skill.md](../modules/easyfk-component-job-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 配置项（@ConfigurationProperties）

### `xxl.job` ← XxlJobProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `admin` | `Admin` | `new Admin()` | 管理端配置 |
| `executor` | `Executor` | `new Executor()` | 执行器配置 |
| `init` | `Init` | `new Init()` | 初始化配置 |


## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `job-xxl` | `com.mcst.easyfk.job.xxl.config.XxlJobConfig` |

## 类型索引

- `com.mcst.easyfk.job.xxl.annotation`：[JobConfig](#jobconfig)、[XxlJobHandler](#xxljobhandler)
- `com.mcst.easyfk.job.xxl.config`：[XxlJobConfig](#xxljobconfig)
- `com.mcst.easyfk.job.xxl.eunms`：[InitMode](#initmode)
- `com.mcst.easyfk.job.xxl.init`：[InitService](#initservice)
- `com.mcst.easyfk.job.xxl.properties`：[XxlJobProperties](#xxljobproperties)
- `com.mcst.easyfk.job.xxl.scanner`：[XxlJobScanner](#xxljobscanner)

## 包 `com.mcst.easyfk.job.xxl.annotation`

### JobConfig

`public @interface JobConfig`　注解：`@Target(ElementType.METHOD)` `@Retention(RetentionPolicy.RUNTIME)` `@Documented`　Job 配置注解 用于为每个 @XxlJob 方法提供描述信息和 Cron 表达式

**方法**

```java
String desc()  // 任务描述
String cron() default "0/5 * * * * ?"  // Cron 表达式 默认每隔5秒执行一次
```

### XxlJobHandler

`public @interface XxlJobHandler`　注解：`@Target(ElementType.TYPE)` `@Retention(RetentionPolicy.RUNTIME)` `@Documented` `@Component`　自定义注解，用于标识包含 XxlJob 方法的类 继承了 @Component 的功能，可以被 Spring 自动扫描和注册

**方法**

```java
String author() default ""  // 作者信息
```

## 包 `com.mcst.easyfk.job.xxl.config`

### XxlJobConfig

`public class XxlJobConfig`　注解：`@Slf4j` `@AutoConfiguration` `@EnableConfigurationProperties(XxlJobProperties.class)`

**方法**

```java
@Bean XxlJobSpringExecutor xxlJobExecutor()
@Bean InitService initService()
@Bean XxlJobScanner xxlJobScanner()
```

## 包 `com.mcst.easyfk.job.xxl.eunms`

### InitMode

`public enum InitMode`

**枚举常量**

```java
NONE
CREATE
UPDATE
```

## 包 `com.mcst.easyfk.job.xxl.init`

### InitService

`public class InitService implements CommandLineRunner`　注解：`@Slf4j`　启动时向调度中心自动创建执行器组与任务 依赖定制版 xxl-job-admin 提供的 initSave / initUpdate 接口（路径见 Init）…

**构造器**

```java
InitService()
```

**方法**

```java
void run(String... args) throws Exception
```

#### InitService.ApiResponse

`public static class ApiResponse`　Lombok：`@Data`　API 响应结果类

**字段 / 常量**

```java
int code
String msg
Object content
Boolean success
```

## 包 `com.mcst.easyfk.job.xxl.properties`

### XxlJobProperties

`public class XxlJobProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "xxl.job")`　XxlJob 自定义配置属性

**字段 / 常量**

```java
Admin admin = new Admin()  // 管理端配置
Executor executor = new Executor()  // 执行器配置
Init init = new Init()  // 初始化配置
```

#### XxlJobProperties.Init

`public static class Init`　Lombok：`@Data`

**字段 / 常量**

```java
InitMode initType = InitMode.NONE  // 初始化方式 默认为 NONE NONE: 不进行初始化 CREATE: 只会创建新任务 UPDATE: 创建新任务并且会更新已存在的任务
String groupSavePath = "/jobgroup/initSave"  // 创建执行器组的接口路径（相对 admin.addresses） 标准 xxl-job-admin 没有该接口，需要定制版调度中心提供
String jobSavePath = "/jobinfo/initSave"  // 创建任务的接口路径（相对 admin.addresses），任务已存在时应返回 content.status=1 与 content.id
String jobUpdatePath = "/jobinfo/initUpdate"  // 更新任务的接口路径（相对 admin.addresses） 只提交 @JobConfig 管理的字段（描述、cron），调度中心需按部分更新处理，保留其余字段
```

#### XxlJobProperties.Admin

`public static class Admin`　Lombok：`@Data`

**字段 / 常量**

```java
String addresses  // 管理端地址
String accessToken = "default_token"  // 访问令牌
```

#### XxlJobProperties.Executor

`public static class Executor`　Lombok：`@Data`

**字段 / 常量**

```java
String appName  // 执行器名称
String appTitle  // 应用标题（用于扩展）
String address  // 执行器地址 格式：http://ip:port 选填，如果填写则使用该地址，否则使用ip和port组合成地址,该配置优先级高于ip和port
String ip  // 执行器IP 选填，默认自动获取
Integer port  // 执行器端口 选填，默认9999
String logPath  // 日志路径
int logRetentionDays = 7  // 日志保存天数
```

## 包 `com.mcst.easyfk.job.xxl.scanner`

### XxlJobScanner

`public class XxlJobScanner implements BeanPostProcessor`　注解：`@Slf4j`　XxlJob 扫描器 用于扫描带有 @XxlJobHandler 注解的类，并提取其中的 @XxlJob 方法信息

**方法**

```java
Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException
ConcurrentMap<String, List<JobInfo>> getAllJobHandlers()  // 获取所有扫描到的 Job 处理器信息
List<JobInfo> getJobHandlersByClass(String className)  // 获取指定类的 Job 处理器信息
List<String> getAllJobHandlerNames()  // 获取所有 JobHandler 名称列表
void printAllJobInfo()  // 打印所有扫描到的 Job 信息
```

#### XxlJobScanner.JobConfigInfo

`public static class JobConfigInfo`　Lombok：`@Data`　Job 配置信息

**字段 / 常量**

```java
String desc
String cron
```

**构造器**

```java
JobConfigInfo(String desc, String cron)
```

#### XxlJobScanner.JobInfo

`public static class JobInfo`　Lombok：`@Data`　Job 信息实体类

**字段 / 常量**

```java
String className  // 类名
String methodName  // 方法名
String jobHandler  // JobHandler 名称
String handlerGroup  // 处理器分组
String handlerDesc  // 处理器描述
String cronExpression  // Cron 表达式
Object bean  // Bean 实例
Method method  // 方法实例
```
