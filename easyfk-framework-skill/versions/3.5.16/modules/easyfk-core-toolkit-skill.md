# easyfk-core 工具类与第三方工具库 Skill 参考文档

> 所属项目：`easyfk-base`　模块：`easyfk-core`（`com.mcst:easyfk-core:3.5.16`）
> 依据：`easyfk-core/src/main/java` 全部工具类源码、`easyfk-core/build.gradle`，以及 base / component 源码中对第三方工具类的实际用法统计。
> 目的：规定开发时"某类需求该用哪个工具"，**框架已有的必须用框架的，不允许重复造轮子**。各工具类的行为细节见 [easyfk-core-skill.md](easyfk-core-skill.md) 第 6、8、9、10 节，本文不重复。

---

## 1. 选用优先级

1. **easyfk-core 的工具类**（第 2 节）。
2. 框架没有时，用 **core 已传递的第三方库中指定的那一个**（第 3、4 节），不要另找同类库。
3. 前两者都没有时，用 JDK（`java.time`、`java.util.Objects`、Stream）。
4. **禁止**在业务项目里新建与第 2 节功能重叠的 `XxxUtil`；确实缺少通用能力时，应补到框架里，而不是在业务里各写一份。
5. **禁止**为工具类需求新增第三方依赖（如 Guava、commons-lang3、Gson、Joda-Time、ModelMapper、Dozer），core 已传递的库足够覆盖。

## 2. easyfk-core 工具类清单

包前缀统一为 `com.mcst.easyfk.core`。

| 用途 | 类 | 主要方法 | 关键约定 |
|---|---|---|---|
| 判空 / 空值抛异常 | `utils.common.EmptyUtil` | `isEmpty` / `isNotEmpty`（Object、String、List、数组、Map 重载）、`isEmptyChars` / `isNotEmptyChars`、`isNullChars`、`isUndefinedOrNull`、`emptyThrowException(v, msg)` / `(v, code, msg)`、`allFieldIsEmpty` | 空白字符串算空；数字 0 不算空；`"null"`/`"undefined"` 只有 `*Chars` 系列算空 |
| 驼峰 / 下划线、首字母大小写、中文判断 | `utils.common.StringUtil`（继承 Spring `StringUtils`） | `camelToUnderline`、`underlineToCamel`、`upperFirstChar`、`lowerFirstChar`、`isChinese`，以及继承来的 Spring `StringUtils` 全部方法 | `underlineToCamel` 不做小写化（`USER_NAME` → `USERNAME`），输入应为小写下划线；空串返回 null |
| 字符串分割并转类型 | `utils.common.SplitUtil` | `split(str)`（`,` `，` 空白 `/` `;` 一次全拆）、`split(str, seps...)`、`splitAndConvert(str, Cls[, seps...])` | 结果为空时返回 **null**，不是空 List |
| DTO / PO / VO 对象转换 | `utils.common.TransformUtil` | `transformObj`、`transformList`、`transformPageResult`、`transformToMap`、`transformFromMap` | 优先 MapStruct-Plus，失败或非 Spring 环境降级为 Bean 拷贝 |
| 部分字段拷贝（更新场景） | `utils.common.MapStructConvertUtil` | `copyValue(src, target, forceNullFields...)`（字符串或 `EFunction`）、`copyValue(src, target, (s, t) -> {})`、`convert`、`convertList`、`convertPage` | 源字段为 null 不覆盖；强制置空的字段显式列出；转换器不可用时抛 `IllegalStateException` |
| 非 null 属性拷贝（不依赖 MapStruct） | `utils.common.MyBeanUtils` | `copyBean(src, Cls)`（新建实例，跳过 null）、`copyPropertiesNotNull(src, target, ignore...)` | 优先用 `TransformUtil` / `MapStructConvertUtil`；这里是兜底实现 |
| 反射：字段、注解、实例化 | `utils.common.ReflectUtil` | `getFields` / `getAllFields` / `getAllFieldsByCutOff`、`getFieldByFieldName`、`hasField`、`get/setValueByFieldName`、`get/setValueByField`、`getFieldsByAnnotation`、`getFieldNameByAnnotation`、`getValueByAnnotation`、`getFieldAndValueByAnnotation[NotNull]`、`getFieldTypeByAnnotation`、`createInstance`、`createInstanceAndSetValue` | `ClassValue` 缓存；找不到注解字段返回 null；返回的数组是缓存本身，不得修改 |
| Lambda 取字段名 | `function.EFunction` + `utils.common.FunctionColumnToStringUtil` | `columnToString(User::getName)`、`columnToString(EFunction[])` | 只接受 getter 方法引用；写成 `u -> u.getName()` 返回 null |
| 枚举按 value / code 查找 | `utils.common.EnumUtils` | `getEnumByValue`、`getNameByValue(cls, v[, method])`、`getEnumByCode`、`getNameByCode(cls, c[, method])`、`getValueByCode`、`getEnumBySubCode`、`getSubTextBySubCode` | 枚举需提供 public `getValue()` / `getCode()`；数值按数值比较，`"1"` ≠ `1` |
| 日期时间格式化、转换、区间 | `utils.date.LocalDateUtil` | 三个格式常量（`DATE_FORMATTER` / `TIME_FORMATTER` / `DATETIME_FORMATTER`）、`getLocalDate[Time][String]`、`string2LocalDate[Time]`、`localDate[Time]ToString`、`date2LocalDate[Time]`、`localDateTime2Date`、`dayStartTime` / `dayEndTime`、`firstDayOfWeek` / `lastDayOfWeek`、`firstDayOfMonth` / `lastDayOfMonth`、`getIntervalDays`、`between`、`isLocalDate` / `isLocalDateTime` | 固定 `yyyy-MM-dd` / `HH:mm:ss` / `yyyy-MM-dd HH:mm:ss`，系统时区 |
| 国际化消息 | `utils.common.I18NUtil` | `getMessage(code[, path][, args])`、`getMessage(code, locale, path, args)`、`getLocale()` | 默认 `i18n/messages`；语言取请求头 `Language`；key 不存在返回 code |
| SpEL 解析（切面 key） | `utils.expression.ExpressionUtil` | `parse(expr, method, args)`、`parse(expr, method, args, Cls)` | 需要 `-parameters` 编译参数 |
| 单 JVM 单号 | `utils.common.OrderNoUtil` | `get18/22/27OrderNumber([prefix[, upperCase]])` | **只保证单 JVM 不重复**，不能作分布式主键或对外单号 |
| 批量启用 / 禁用对象构造 | `utils.common.DisableUtil` | `createObjListByDisableAction(DisableActionParam)` | 参数缺失、无主键时抛 `IllegalArgumentException` |
| 业务异常转返回体 | `utils.common.Exception2ResultUtil` | `createResponseByBizException(e)`、`createResultByBizException(e)` | 自动解析 `i18nCode` |
| 按返回类型构造失败结果 | `utils.returns.ReturnErrorUtil` | `returnError(returnType, code, msg)` | 返回类型不是 `BaseResult` / `ResponseResult` 时抛 `RuntimeException`；供切面使用 |
| 条件 / 判空分支执行 | `function.FunctionExecutor` | `isTrueOrFalse`、`isTrueFun`、`presentOrElse`、`notEmptyFun`、`emptyThrowFun`（6 个重载）、`actionFun`、`predicate` | "空"按 `EmptyUtil.isEmpty` |
| 可抛受检异常的 Supplier | `function.ThrowingSupplier` | `get() throws E` | lock-redisson `RLockTemplate` 使用 |
| 返回值 / 分页 / 请求构建 | `builders.*` | `RRBuilder`、`BRBuilder`、`PRBuilder`、`SRPBuilder`、`MRPBuilder`、`OBJBuilder`、`BEBuilder` | 见 core skill 第 6 节 |
| 线程上下文 | `context.*` | `UserDataContext`、`RequestHeaderContext`、`TraceIdContext` | 见 core skill 第 8 节 |
| 常量 | `constants.*` | `RequestHeaderConstant`、`CharacterConstant`、`ReturnCodeConstant`、`FileType` | 请求头名、通用字符不要再写字面量 |

## 3. core 传递的第三方库（`api` 依赖）

业务项目引入 `easyfk-core` 后，以下库全部在编译 classpath 上，**不需要也不允许再单独声明同类库**。

| 库 | 版本（BOM 生效） | 框架内用途 | 业务可直接使用的范围 |
|---|---|---|---|
| `spring-boot-starter`（spring-core / context / beans） | Boot 3.5.16 | 容器、`BeanUtils`、`StringUtils`、SpEL | `org.springframework.util.*` 中 `StopWatch`、`AntPathMatcher`、`DigestUtils`、`FileCopyUtils`、`ClassUtils` 等 core 没有覆盖的能力 |
| `spring-boot-starter-aop`（AspectJ） | Boot 3.5.16 | 框架切面 | 自定义切面 |
| `spring-boot-starter-validation`（Hibernate Validator，`jakarta.validation`） | Boot 3.5.16 | 请求参数校验 | 入参校验一律用 `jakarta.validation` 注解 + `@Validated` |
| `spring-boot-configuration-processor` | Boot 3.5.16 | `@ConfigurationProperties` 元数据 | 只在编译期起作用，不要在代码中引用 |
| Jackson（`jackson-databind` / `core` / `annotations`） | 2.19.x（随 Boot 3.5.16 管理） | **Spring MVC 出入参序列化**（web-prd / web-micro 配置的 `ObjectMapper`，含 `JavaTimeModule`）、Redis `SmartRedisSerializer` | DTO 上控制 HTTP 序列化格式的注解（`@JsonFormat`、`@JsonIgnore`、`@JsonProperty`） |
| `fastjson2` | 2.0.66 | 代码中手动序列化 / 解析：MQ 消息、WebSocket 消息、Feign 错误解码、Redis `FastJson2RedisSerializer`、web-prd Controller 请求日志 | **代码里手动处理 JSON 一律用 `com.alibaba.fastjson2.JSON` / `JSONObject`** |
| `hutool-all` | 5.8.48 | 见下表 | 见第 4 节 |
| `swagger-annotations`（OpenAPI 3） | 2.2.55 | DTO 文档注解 | `@Schema`、`@Operation`、`@Tag` |
| `slf4j-api` | 2.0.18 | 日志门面 | 日志一律用 Lombok `@Slf4j` |
| `mapstruct-plus-spring-boot-starter` | 1.5.3 | `TransformUtil` 的高性能路径 | 源类加 `@AutoMapper(target = X.class)`；不要直接注入 `Converter`，统一走 `TransformUtil` / `MapStructConvertUtil` |
| Lombok | 1.18.46（compileOnly，由各工程自行声明） | 全框架 | `@Data`、`@Builder`、`@Accessors(chain = true)`、`@Slf4j` |

- 表内版本是 **BOM 约束值**；`swagger-annotations` 2.2.55 与 springdoc 2.10.0 使用的 swagger-core 对齐（3.x 基于 Jackson 3 / Jakarta EE 11，不能在 Boot 3.5 上用）。
- `mapstruct-plus-processor` 与 `lombok-mapstruct-binding` 不在 BOM 里，定义在 `easyfk-base` 自己的 catalog（`mapstructProcessor` / `lombokMapstruct`，1.5.3 / 0.2.0），业务工程需要自己声明注解处理器。

框架源码中实际使用到的 Hutool 类（以下即为"Hutool 允许使用清单"的依据）：

| Hutool 类 | 框架中的使用位置 | 用途 |
|---|---|---|
| `cn.hutool.core.util.IdUtil` | authority、web-base、web-prd、repository、db-redis、mq-* | `fastSimpleUUID()`（token、锁值、资源 ID）、`randomUUID()`（TraceId）、`getSnowflakeNextId/Str()`（消息 ID、雪花主键） |
| `cn.hutool.crypto.digest.DigestUtil`、`HMac`、`HmacAlgorithm`、`cn.hutool.crypto.SecureUtil` | gateway、web-prd、websocket | 摘要、HMAC 签名 |
| `cn.hutool.core.bean.BeanUtil`、`copier.CopyOptions` | core `TransformUtil` / `EmptyUtil`、repository、db-redis | Bean ↔ Map（框架内部） |
| `cn.hutool.core.collection.CollUtil`、`map.MapUtil`、`util.ArrayUtil` | core、repository、service-base | 集合、Map、数组构造与操作 |
| `cn.hutool.core.convert.Convert` | core `SplitUtil` | 类型转换 |
| `cn.hutool.core.util.StrUtil`、`ObjectUtil` | core、web-prd | 字符串格式化、通用对象操作 |
| `cn.hutool.extra.spring.SpringUtil` | core `MapStructConvertUtil`、serializer-fory | 静态获取 Spring Bean |
| `cn.hutool.http.HttpRequest` / `HttpResponse` | job-xxl | 调用外部 HTTP 接口 |
| `cn.hutool.jwt.*` | web-base `JwtManager` | JWT（只在框架内部使用） |

## 4. 需求 → 工具对照（必须遵守）

| 需求 | 必须使用 | 不要使用 |
|---|---|---|
| 判断字符串 / 集合 / Map / 数组 / 对象是否为空 | `EmptyUtil.isEmpty` / `isNotEmpty` | `StrUtil.isBlank`、`ObjectUtil.isEmpty`、`CollUtil.isEmpty`、`CollectionUtils.isEmpty`、`StringUtils.hasText`、手写 `x == null \|\| x.isEmpty()` |
| 前端传来的 `"null"` / `"undefined"` 判空 | `EmptyUtil.isEmptyChars` / `isNotEmptyChars` | 手写字符串比较 |
| 值为空时抛业务异常 | `EmptyUtil.emptyThrowException(v, code, msg)`、`FunctionExecutor.emptyThrowFun(...)` | Spring `Assert`、Hutool `Assert`、`Objects.requireNonNull`（它们抛的不是 `BusinessException`，不带错误码） |
| 驼峰 ↔ 下划线、首字母大小写 | `StringUtil.camelToUnderline` / `underlineToCamel` / `upperFirstChar` / `lowerFirstChar` | `StrUtil.toCamelCase` / `toUnderlineCase` / `upperFirst`、`StringUtils.capitalize` |
| 拆分 ids、标签等逗号分隔字符串 | `SplitUtil.split` / `splitAndConvert` | `String.split`、`StrUtil.split`、手写正则 |
| 其它字符串操作（格式化、截取、填充、拼接） | Hutool `StrUtil`（core 没有） | commons-lang3 `StringUtils`、自写 `StringUtils` |
| 基本类型转换 | Hutool `Convert` | 自写 `parseXxx` 工具 |
| DTO ↔ PO ↔ VO 转换 | `TransformUtil.transformObj` / `transformList` / `transformPageResult` | `BeanUtil.copyProperties`、Spring `BeanUtils.copyProperties`、`MyBeanUtils.copyBean`、手写逐个 setter、ModelMapper、Dozer |
| 更新时把请求对象的非空字段拷到已有对象 | `MapStructConvertUtil.copyValue(src, target[, forceNullFields])` | 手写 if 非空再 set |
| Bean ↔ Map | `TransformUtil.transformToMap` / `transformFromMap` | 直接调用 `BeanUtil.beanToMap` / `toBean` |
| 反射读写字段、按注解找字段 | `com.mcst.easyfk.core.utils.common.ReflectUtil` | `cn.hutool.core.util.ReflectUtil`、Spring `ReflectionUtils`、手写 `getDeclaredField` |
| 字段名字符串（查询条件、排序、强制置空字段） | `EFunction` 方法引用（`User::getName`） | 字符串字面量字段名 |
| 枚举按 value / code 反查 | `com.mcst.easyfk.core.utils.common.EnumUtils` | Hutool `EnumUtil`、在每个枚举里手写 `of(code)` 遍历 |
| 日期时间 | `java.time.*` + `LocalDateUtil`（标准格式和常用边界计算） | `java.util.Date` 新代码、`SimpleDateFormat`、Hutool `DateUtil`、Joda-Time、自定义格式常量 |
| HTTP 接口出入参的 JSON 格式 | Jackson 注解（`@JsonFormat` 等） | fastjson2 `@JSONField`（Spring MVC 不认） |
| 代码中手动序列化 / 解析 JSON | fastjson2 `JSON.toJSONString` / `JSON.parseObject` / `JSONObject` | Hutool `JSONUtil`、Gson、`new ObjectMapper()` |
| 全局唯一主键 | ORM 主键策略或 component-autoId（`autoId-redis`） | `OrderNoUtil`、`System.currentTimeMillis()` 拼接 |
| UUID / 临时唯一串（token、锁值、请求 ID） | Hutool `IdUtil.fastSimpleUUID()` | `UUID.randomUUID().toString().replace("-", "")` |
| 雪花 ID（消息 ID 等） | Hutool `IdUtil.getSnowflakeNextId()` / `getSnowflakeNextIdStr()` | 自写雪花算法 |
| 业务单号（单实例） | `OrderNoUtil.get22OrderNumber(prefix)` | 自写时间戳 + 随机数 |
| MD5 / SHA / HMAC 摘要与签名 | Hutool `DigestUtil`、`HMac`、`SecureUtil` | 手写 `MessageDigest`、commons-codec |
| 配置项加密 | Jasypt（BOM 已管理，需显式引入 `jasypt-spring-boot-starter`） | 自写加解密配置 |
| JWT 签发与校验 | web-base `JwtManager`（框架登录链路） | 直接使用 Hutool `JWTUtil`、jjwt |
| 静态获取 Spring Bean | Hutool `SpringUtil.getBean` | 自写 `ApplicationContextAware` 持有类 |
| 集合、Map、数组构造与操作 | Hutool `CollUtil`、`MapUtil`、`ArrayUtil` 或 JDK Stream | Guava、commons-collections |
| 微服务之间调用 | rpc-cloud（OpenFeign）或 rpc-dubbo | 手写 HTTP 调用 |
| 调用外部 HTTP 接口 | Hutool `HttpRequest` / `HttpUtil`（已在 classpath） | 为此新增 OkHttp、RestTemplate 包装工具 |
| 参数校验 | `jakarta.validation` 注解 + `@Validated` | 在 Controller / Service 里手写 if 校验格式 |
| 国际化文本 | `I18NUtil.getMessage` | 自建 `MessageSource` 工具 |
| 注解切面中解析 SpEL key | `ExpressionUtil.parse` | 自建 `SpelExpressionParser` 工具 |
| 返回结果、分页结果、业务异常 | `RRBuilder` / `BRBuilder` / `PRBuilder` / `BEBuilder` / `BusinessException` | 自定义 `Result`、`R`、`PageVO` 等返回类 |
| 当前用户、请求头、TraceId | `UserDataContext` / `RequestHeaderContext` / `TraceIdContext` | 自己从 `HttpServletRequest` 解析 token 或请求头 |
| 线程池、异步任务 | easyfk-thread 的执行器（自动传递 TraceId） | `Executors.newXxx`、裸 `new Thread` |
| 日志 | Lombok `@Slf4j` + slf4j 占位符 `{}` | `System.out`、`printStackTrace`、字符串拼接日志 |

## 5. 同名类陷阱（import 时必须核对包名）

| 简单类名 | 框架类（应使用） | 容易误导入的同名或近名类 |
|---|---|---|
| `ReflectUtil` | `com.mcst.easyfk.core.utils.common.ReflectUtil` | `cn.hutool.core.util.ReflectUtil` |
| `EnumUtils` | `com.mcst.easyfk.core.utils.common.EnumUtils` | `cn.hutool.core.util.EnumUtil` |
| `StringUtil` | `com.mcst.easyfk.core.utils.common.StringUtil` | `org.springframework.util.StringUtils`、`cn.hutool.core.util.StrUtil` |
| `ValidateException` | `com.mcst.easyfk.core.exception.ValidateException` | `cn.hutool.core.exceptions.ValidateException`、`jakarta.validation.ValidationException` |
| `BusinessException` | `com.mcst.easyfk.core.exception.BusinessException` | 各第三方库自带的同名异常 |
| `MyBeanUtils` / `TransformUtil` | 框架类 | `cn.hutool.core.bean.BeanUtil`、`org.springframework.beans.BeanUtils` |

## 6. 框架没有、需要时按此选择

| 能力 | 选择 | 说明 |
|---|---|---|
| 字符串格式化、截取、模板 | Hutool `StrUtil.format` 等 | core 只有命名转换和判空 |
| 文件、IO、压缩 | Hutool `FileUtil`、`IoUtil`、`ZipUtil` 或 Spring `FileCopyUtils` | — |
| 正则 | Hutool `ReUtil` 或 JDK `Pattern`（预编译为常量） | — |
| 数值精确计算 | JDK `BigDecimal` / Hutool `NumberUtil` | — |
| 计时 | Spring `StopWatch` | — |
| 路径匹配 | Spring `AntPathMatcher` | — |
| Excel | `com.alibaba:easyexcel`（BOM 已管理，需显式引入） | — |

## 7. 生成代码时的规则

**Do**
- 写任何工具性代码前先查第 2 节和第 4 节；表中有的直接调用。
- `import` 工具类时核对第 5 节的包名。
- 判空统一 `EmptyUtil`，对象转换统一 `TransformUtil`，字段名统一 `EFunction` 方法引用。
- 手动 JSON 用 fastjson2，HTTP 出入参格式用 Jackson 注解。
- 对 `SplitUtil`、`ReflectUtil.getFieldsByAnnotation` / `getFieldNameByAnnotation` 的返回值先判空。

**Don't**
- 不要在业务项目里新建 `StringUtils`、`DateUtils`、`BeanCopyUtils`、`JsonUtils`、`ReflectUtils`、`EnumUtils`、`IdGenerator` 等与框架重叠的工具类。
- 不要为工具类需求引入 Guava、commons-lang3、commons-collections、commons-codec、Gson、Joda-Time、ModelMapper、Dozer、jjwt。
- 不要用 `OrderNoUtil` 生成分布式主键。
- 不要直接注入 MapStruct-Plus 的 `Converter` 或调用 `BeanUtil.copyProperties` 做 DTO/PO 转换。
- 不要用 Spring / Hutool 的 `Assert` 做业务校验。

## 8. 复查记录

| # | 位置 | 问题 | 处理 |
|---|---|---|---|
| 1 | `EnumUtils` | 日志使用 `{0}` `{1}` 占位符，slf4j 不解析，日志里看不到参数值 | **已修复**：全部改为 `{}` |
| 2 | `EnumUtils.getCachedMethod` | 对实例方法调用 `method.canAccess(null)`，会抛 `IllegalArgumentException`，Method 兜底路径不可用 | **已修复**：改为 `trySetAccessible()` |
| 3 | `MapStructConvertUtil.convert(map, type, consumer)` | 非静态方法，而该类没有实例化入口，外部无法调用 | **已修复**：改为 `static` |
| 4 | `MyBeanUtils.copyPropertiesNotNull` | 名为"拷贝非 null"，实际是拷贝全部属性，第三个参数是忽略列表 | **已修复**：只拷贝源对象中非 null 的属性，第三个参数为额外忽略的属性；唯一调用方 repository `SCBuilder` 的目标对象 `PageSearch` 没有默认值，结果不变 |
| 5 | `DisableUtil.createObjListByDisableAction` | 参数校验异常被 catch 后统一改写为"构建对象属性值错误"，丢失原因；没有主键时静默返回 null | **已修复**：参数错误和缺少主键抛 `IllegalArgumentException`（带具体原因），反射失败抛 `IllegalStateException` 并保留 cause |
| 6 | `EmptyUtil.allFieldIsEmpty` | 属性描述符缓存用 `WeakHashMap`，value 持有 Class 引用，条目永不回收 | **已修复**：改为 `ClassValue`，与 `ReflectUtil` 一致 |
| 7 | `StringUtil.underlineToCamel` | 不做小写化，`USER_NAME` 转为 `USERNAME` | 保留现有行为（框架内列名均为小写下划线），已在第 2 节注明 |
| 8 | `easyfk-core/build.gradle` | `spring-boot-configuration-processor` 以 `api` 传递，注解处理器 jar 会进入下游运行时 classpath | 保留（不调整依赖范围），已在第 3 节注明仅编译期生效 |
| 9 | web-base `JwtManager` | 引入的是 `cn.hutool.core.exceptions.ValidateException`，与 core 的 `ValidateException` 同名 | 框架内部用法正确，已列入第 5 节同名陷阱 |
| 10 | 3.5.16 升级 | 文档原写 fastjson2 2.0.58 / hutool 5.8.40 / swagger-annotations 2.2.36 / slf4j 2.0.16 / mapstruct-plus 1.5.0 / Lombok 1.18.38 / Jackson 2.15.4 | `easyfk-core/build.gradle` 与 3.2.12 相同（全部无版本坐标），版本全部来自 BOM + Boot 3.5.16 平台：fastjson2 → **2.0.66**、hutool-all → **5.8.48**、swagger-annotations → **2.2.55**、slf4j-api → **2.0.18**、mapstruct-plus → **1.5.3**、Lombok → **1.18.46**、Jackson → **2.19.x**。原「引入 log-logback 后 Jackson 变 2.17.2」的说法已失效（encoder 8.1 与 Boot 基线不再互相抬版本） **已更新**：§3 表格已同步 |
