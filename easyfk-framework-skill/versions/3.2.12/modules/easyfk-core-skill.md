# easyfk-core Skill 参考文档

> 所属项目：`easyfk-base`　坐标：`com.mcst:easyfk-core:3.2.12`　根包：`com.mcst.easyfk.core`
> 依据：源码逐文件复查（63 个类），并对齐 `core开发文档.md`、`core特点介绍.md`、`核心模块说明.md` 5.1、`EasyFK框架开发手册.md` 3.1。
> 本文以**源码为准**；原文档与源码不一致之处见文末「复查记录」。

---

## 1. 模块定位与使用时机

`easyfk-core` 是 EasyFK 最底层模块，不依赖任何其他 EasyFK 模块，被所有上层模块依赖。它只提供**契约与工具**，不提供自动配置（没有 `@Configuration`、没有 `spring.factories` / `AutoConfiguration.imports`）。

适用场景（Skill 触发词）：
- 定义 DTO / 请求参数 / 响应结构（`BaseDto`、`BasicParam`、`ResponseResult`、`BaseResult`、`PageResult`）
- 构建 Controller 返回值、Service 内部返回值、分页结果（`RRBuilder`、`BRBuilder`、`PRBuilder`）
- 构建查询/修改请求给 Service 层（`SRPBuilder`、`MRPBuilder`）
- 抛业务异常、定义错误码枚举（`BusinessException`、`BEBuilder`、`BaseErrorEnum`）
- 读取当前登录用户、请求头、TraceId（`UserDataContext`、`RequestHeaderContext`、`TraceIdContext`）
- 对象转换、反射、判空、分割、枚举、日期、国际化、SpEL 工具

**注解只是元数据**：core 只定义注解，读取注解并产生行为的是上层模块（见 §5）。

---

## 2. 引入方式

```groovy
dependencies {
    implementation platform('com.mcst:easyfk-dependencies:3.2.12')
    implementation 'com.mcst:easyfk-core'
    // 使用 @AutoMapper 对象映射时需要注解处理器
    annotationProcessor 'io.github.linpeilie:mapstruct-plus-processor:1.5.0'
}
```

通过 `api` 传递给使用方的依赖：`spring-boot-starter`、`spring-boot-starter-aop`、`spring-boot-starter-validation`、`spring-boot-configuration-processor`（均排除 `spring-boot-starter-logging`）、Jackson、`fastjson2`、`hutool-all`、`swagger-annotations`(v3)、`slf4j-api`、`mapstruct-plus-spring-boot-starter`。

- **不再传递 `spring-boot-starter-test`**（已改为 `testImplementation`）。业务项目写测试必须自行声明 `testImplementation 'org.springframework.boot:spring-boot-starter-test'`。
- 日志实现不在 core 中，需引入 `easyfk-log` 的 `log-logback` 或 `log-log4j2`。
- 运行要求：JDK 21、Spring Boot 3.x（`jakarta.*`）。

---

## 3. 包结构速查

| 包 | 内容 |
|---|---|
| `annotation` | 10 个注解：`@PrimaryKey` `@PrimaryField` `@SerializableClass` `@BetweenStart` `@BetweenEnd` `@AssistConditionField` `@SingleUniqueField` `@CombUniqueField` `@SignField` `@ForbiddenField` |
| `builders` | `RRBuilder` `BRBuilder` `PRBuilder` `SRPBuilder` `MRPBuilder` `OBJBuilder` `BEBuilder` |
| `constants` | `ReturnCodeConstant` `RequestHeaderConstant` `CharacterConstant` `FileType` |
| `context` | `UserDataContext` `RequestHeaderContext` `TraceIdContext` |
| `dto` | `BaseDto`；`login`（`LoginUser` `LoginResult` `UserData`）；`page`（`PageSearch` `PageResult`）；`request`（`BasicParam` `SearchRequest` `ModifyRequest` `BatchBasicReq` `BatchActionReq` `DisableFieldReq` `DisableActionParam` `RequestHeaders`）；`response`（`BaseResult` `ResponseResult`）；`validation`（`ValidationResult`） |
| `exception` | `BusinessException` `BaseErrorEnum` `ValidateException` |
| `function` | `EFunction` `FunctionExecutor` `ThrowingSupplier` |
| `utils.common` | `EmptyUtil` `TransformUtil` `MapStructConvertUtil` `MyBeanUtils` `ReflectUtil` `FunctionColumnToStringUtil` `StringUtil` `SplitUtil` `EnumUtils` `OrderNoUtil` `I18NUtil` `DisableUtil` `Exception2ResultUtil` |
| `utils.date` / `utils.expression` / `utils.returns` | `LocalDateUtil` / `ExpressionUtil` / `ReturnErrorUtil` |

---

## 4. 数据模型

所有 DTO 统一使用 Lombok：`@Data @Accessors(chain = true) @NoArgsConstructor @AllArgsConstructor`，加 `@Builder`；有继承关系的（`BaseDto`、`BasicParam`、`BatchBasicReq`、`BatchActionReq`）使用 `@SuperBuilder`。子类继承时也要用 `@SuperBuilder` 和 `@EqualsAndHashCode(callSuper = true)`。

### 4.1 响应

| 类 | 字段 | 用途 |
|---|---|---|
| `ResponseResult<T>` | `code` `count` `msg` `data` `traceId` | Controller 返回给客户端 |
| `BaseResult<T>` | `success`(Boolean) `data` `msg` `code` | Service / RPC 内部调用结果 |
| `PageResult<T>` | `total`(Long) `rows`(List) | 分页数据 |

`ReturnCodeConstant`：`SUCCESS="OK"`、`ERROR="ERROR"`、`UN_LOGIN`、`UN_AUTH`、`PARAM_ERROR`、`BUSYNESS`。

### 4.2 请求

- `BasicParam`：查询参数基类，字段 `top` `page` `limit` `totalCount` `ascFields` `descFields` `searchKeyWord` `start` `stop`，全部标注 `@AssistConditionField`，不会被当作等值查询条件。业务查询参数类应继承它。
- `SearchRequest<T>`：`parmaObj`（注意拼写是 parma）、`pageSearch`、`selectFields`、`nullFields`、`inParams`(Map<String, List<?>>)、`likeFields`、`notFields`、`gThanFields`、`lThanFields`、`gThanOrEqualFields`、`lThanOrEqualFields`、`multipleFields`。
- `ModifyRequest<T>`：`idList`、`parmaObj`、`paramList`、`enableNullFields`（更新时允许置空的字段）。
- `PageSearch`：`page`、`limit`、`totalCount`；构造器 `new PageSearch(page, limit)`。
- `BatchBasicReq<PK>`：`ids`（`@NotNull`，多个用逗号分隔）；`BatchActionReq<PK>` 额外有 `remark`。
- `DisableFieldReq`：`ids`(String, `@NotBlank`)、`value`(Integer, `@NotNull`)。
- `RequestHeaders`：`resetSign` `timestamp`（这两个带 `@SignField`）、`language` `accessToken` `loginToken` `requestNonce` `requestToken` `deviceNo` `clientType`。

### 4.3 登录

- `LoginUser`：`name`、`userType`（platform / customer / agent / merchant）、`loginToken`。由业务登录代码通过 web-base 的 `JwtManager.createJwtByObject(loginUser)` 写进 JWT；请求进来时 web-base 的 `ContextDataManager` 再把它解析回 `LoginUser`。
- `UserData`：`userId` `accountId` `name` `phone` `type` `accountType` `nickname` `avatar` `thirdAccount` `thirdType` `groupId/Name` `departmentId/Name` `agentId/Name` `merchantId/Name` `orgId/Name` `extendData` `bizType` `loginToken`。
- `LoginResult`：`success` `loginUser` `msg` `limits` `headImage` `extendData`；构造器 `new LoginResult(loginUser)`（success=true）、`new LoginResult(false, "msg")`。

### 4.4 BaseDto

只有 `insertTime`、`lastUpdateTime` 两个字段（`@Schema(hidden = true)`）。core **不负责赋值**，由 ORM 组件的 `AutoSetValueHandler`（orm-mybatis / orm-flex / orm-hibernate）在保存时自动填充。

---

## 5. 注解：定义在 core，行为在上层

所有注解都作用在字段上（`@SerializableClass` 作用在类上）。下表中"生效位置"一列是源码中实际读取该注解的位置。

| 注解 | 属性 | 生效位置 / 实际行为 |
|---|---|---|
| `@PrimaryKey` | `value` | repository `RepositoryUtil`、各 ORM Util：识别主键；`DisableUtil` 默认取它作为 id 字段 |
| `@PrimaryField` | `value` | repository `SelectFieldUtil`：默认查询字段 |
| `@SingleUniqueField` | `repetitionMsg`（必填） | repository `RepositoryUtil`：保存前做单字段唯一校验 |
| `@CombUniqueField` | `combinationField`、`repetitionMsg`（必填） | repository `RepositoryUtil`：组合唯一校验 |
| `@BetweenStart` / `@BetweenEnd` | `field`（必填，指向被比较的实体字段名） | repository `ConditionUtil`：生成范围条件 |
| `@AssistConditionField` | 无 | repository `SCBuilder`：不作为查询条件 |
| `@SignField` | 无 | 标记参与签名的请求头字段 |
| `@SerializableClass` | 无 | serializer-base `SerializerInitializer` 扫描后预注册到序列化器 |
| `@ForbiddenField` | `value`（必填） | 只被代码生成器按文本扫描，运行时无行为 |
原有的 `@EnumValueAnnotation`、`@DataFilterField`、`@BetweenField` 在整个仓库（base、component、generator）中既无使用也无处理代码，已删除。代码生成器识别的是文本标记 `@BetweenConditionField`，与已删除的 `@BetweenField` 无关。生成代码时不要再使用这三个注解。

```java
@Data
@EqualsAndHashCode(callSuper = true)
@SuperBuilder
@NoArgsConstructor
public class UserQuery extends BasicParam {
    @BetweenStart(field = "insertTime")
    private LocalDateTime insertTimeStart;
    @BetweenEnd(field = "insertTime")
    private LocalDateTime insertTimeEnd;
    private Integer status;
}

@Data
public class UserEntity extends BaseDto {
    @PrimaryKey
    private Long id;
    @SingleUniqueField(repetitionMsg = "手机号已存在")
    private String phone;
    @CombUniqueField(combinationField = "orgId", repetitionMsg = "同一组织下账号重复")
    private String account;
    private String orgId;
}
```

---

## 6. 构建器

### 6.1 RRBuilder → `ResponseResult`（Controller 返回）

```java
RRBuilder.buildSuccessBody();                       // code=OK, msg=请求处理成功, count=0
RRBuilder.buildSuccessBody(data);                   // data 为空时不设置 data
RRBuilder.buildSuccessListBody(list);               // list 为空时 msg=暂无数据, data=[]
RRBuilder.buildSuccessPageBody(total, rows);        // 设置 count
RRBuilder.buildBodyByPageResult(pageResult);        // pageResult/rows 为空时返回 count=0, data=[]
RRBuilder.buildBodyByBaseResult(baseResult);        // success → OK / ERROR，带 msg、data；success 为 null 时自动拆箱抛 NPE
RRBuilder.buildFailedBody();                        // code=ERROR, msg=请求处理失败
RRBuilder.buildFailedBody("消息");
RRBuilder.buildFailedBody("ERROR_CODE", "消息");     // 注意：code 在前
RRBuilder.buildFailByException(e);                  // code=PARAM_ERROR；BindingResult 取第一个字段错误，ValidationException 取 message
```

所有方法都会自动写入 `TraceIdContext.getTraceId()`。

### 6.2 BRBuilder → `BaseResult`（Service 内部）

```java
BRBuilder.successResult();  BRBuilder.successResult(data);  BRBuilder.successResult(data, msg);  BRBuilder.successResult(data, msg, code);
BRBuilder.failResult();     BRBuilder.failResult(data);     BRBuilder.failResult(data, msg);     BRBuilder.failResult(data, msg, code);
BRBuilder.failResult("消息", "CODE");                // 注意：msg 在前，与 RRBuilder 相反；无错误码时写 failResult("消息", null)
                                                    // 单参 failResult("消息") 命中的是 failResult(T data)，消息进了 data、msg 为空
BRBuilder.result(success, data, msg, code);
BRBuilder.<User>builder().success().data(u).msg("ok").build();   // success(boolean) / success() / fail() 都不带业务参数
```

### 6.3 PRBuilder → `PageResult`

```java
PRBuilder.result(total, rows);
PRBuilder.<User>builder().total(100L).rows(list).build();
PRBuilder.<User>builder().pageData(total, rows).build();
```

### 6.4 SRPBuilder → `SearchRequest`

```java
SearchRequest<UserDto> req = SRPBuilder.buildRequest(query);  // query 是 BasicParam 时，page 和 limit 都非空才设置分页；totalCount 默认 true

SearchRequest<UserDto> req2 = SRPBuilder.<UserDto>builder()
        .example(dto)                                  // 或 .pageAndExample(pageSearch, dto)
        .page(new PageSearch(1, 20))
        .selectFields(UserDto::getName, UserDto::getPhone)
        .likeFields(UserDto::getName)
        .nullFields(UserDto::getDeletedAt)
        .notFields(UserDto::getType)
        .in(UserDto::getStatus, new ArrayList<>(List.of(0, 1)))
        .build();
req2.setGThanFields(new String[]{"age"});              // 大于/小于类条件没有构建器方法，直接 set
```

- 构建器提供的方法：`example`、`pageAndExample`、`page`、`selectFields`、`likeFields`、`nullFields`、`notFields`、`in`。`gThan*`、`lThan*`、`multipleFields` 需要直接调用 `SearchRequest` 的 setter。
- 同一字段调用两次 `in(...)` 时，第二次会 `addAll` 到第一次传入的 List 上。如果第一次传的是 `List.of` / `Arrays.asList` 这类不可变 List，会抛 `UnsupportedOperationException`。需要追加时，第一次请传可变 List。

### 6.5 MRPBuilder → `ModifyRequest`

```java
MRPBuilder.buildRequest(dto);                          // parmaObj
MRPBuilder.buildRequest(req, UserDto.class);           // 先 TransformUtil.transformObj 转换
MRPBuilder.buildRequest(dtoList);                      // paramList
MRPBuilder.buildRequest(reqList, UserDto.class);
MRPBuilder.<UserDto>builder()
        .param(dto)
        .ids("1", "2")                                  // 或 .ids(idList)
        .enableNullFields(UserDto::getAvatar)           // 更新时允许把该字段置空
        .build();
```

### 6.6 OBJBuilder / BEBuilder

```java
UserDto u = OBJBuilder.builder(UserDto.class)          // 需要无参构造
        .setFieldValue(UserDto::getName, "张三")        // 字段不存在时抛 RuntimeException("构建对象属性值错误")
        .build();

throw BEBuilder.exception("用户不存在");
throw BEBuilder.exception("用户不存在", "USER_404");                       // message 在前
throw BEBuilder.exceptionByI18n("用户不存在", "user.not.found", args);
throw BEBuilder.exceptionByI18n("用户不存在", "user.not.found", "i18n/user", args);
throw BEBuilder.builder("msg").errCode("E1").i18nCode("k").msgPath("p").args(a).build();
```

---

## 7. 异常

```java
public enum UserError implements BaseErrorEnum {
    USER_NOT_FOUND("USER_001", "用户不存在");

    private String code;
    private String message;

    UserError(String code, String message) { this.code = code; this.message = message; }

    @Override public String getCode() { return code; }
    @Override public void setCode(String code) { this.code = code; }          // 接口强制要求 setter
    @Override public String getMessage() { return message; }
    @Override public void setMessage(String message) { this.message = message; }
}

throw new BusinessException(UserError.USER_NOT_FOUND);     // errorCode + errorMsg
throw new BusinessException("USER_001", "用户不存在");      // (code, message)
throw new BusinessException("操作失败");                    // 只有 errorMsg，errorCode 为 null
```

- `BusinessException` 继承 `RuntimeException`，`fillInStackTrace()` 返回 `this`，所以**没有堆栈**。需要排查位置时，请在日志里记录业务上下文。
- 字段：`errorCode` `errorMsg` `i18nCode` `msgPath` `args`，支持链式 setter。
- `Exception2ResultUtil.createResponseByBizException(e)` / `createResultByBizException(e)`：把异常转换为 `ResponseResult` / `BaseResult`。`errorMsg` 为空时消息为 `"业务异常！"`。设置了 `i18nCode` 时优先取国际化消息；**key 不存在时返回 key 本身**。
- `ReturnErrorUtil.returnError(returnType, code, msg)`：returnType 是 `BaseResult` / `ResponseResult` 时构造失败对象，否则抛 `RuntimeException`。
- `ValidateException`：普通运行时异常，只有 message。

---

## 8. 线程上下文

| 上下文 | 存储 | 由谁写入 |
|---|---|---|
| `UserDataContext` | `ThreadLocal<UserData>` | web-base `ContextDataManager`（解析 JWT 后写入） |
| `RequestHeaderContext` | `ThreadLocal<RequestHeaders>` | web-prd / web-micro 的 `RequestBaseFilter`，gateway 的 `RequestGatewayFilter` |
| `TraceIdContext` | `InheritableThreadLocal<String>` | web-base `ContextDataManager`、easyfk-thread `CustomTaskExecutor`、rpc-dubbo `DubboFilter` |

```java
UserData user = UserDataContext.getUserData();        // 未登录接口、异步线程中可能为 null，必须判空
RequestHeaders h = RequestHeaderContext.getRequestHeaders();
String traceId = TraceIdContext.getTraceIdOrDefault("N/A");
TraceIdContext.hasTraceId();
TraceIdContext.getRequiredTraceId();                   // 不存在时抛 IllegalStateException
TraceIdContext.setTraceId(id);                         // null 或空白抛 IllegalArgumentException，会自动 trim
TraceIdContext.executeWithCleanup(() -> { ... });      // finally 中 remove
```

- 业务代码一般只读不写。自己创建线程或线程池时，需要手动设置并在结束时 `remove()`。推荐直接使用 easyfk-thread 的执行器，它会自动传递 TraceId。
- `InheritableThreadLocal` 只在**创建线程时**复制父线程的值。复用的线程池线程会保留旧的 TraceId，不能指望自动继承。

---

## 9. 函数式工具

`EFunction<T, R>` 等于 `Function` 加 `Serializable`。所有"按 Lambda 取字段名"的 API 都以它为参数，内部通过 `FunctionColumnToStringUtil.columnToString` 实现。

- **只能传 getter 方法引用**（`User::getName`、`User::isEnabled`）。写成 `u -> u.getName()` 时 implMethodName 是 `lambda$xxx`，会返回 `null` 并打 warn 日志。
- 规则：去掉 `get` / `is` 前缀后首字母小写。Lombok 为 `Boolean isDeleted` 生成的 getter 是 `getIsDeleted`，对应字段名 `isDeleted`；为 `boolean deleted` 生成的是 `isDeleted()`，对应字段名 `deleted`。

`FunctionExecutor`（function 参数为 null 时抛 `IllegalArgumentException`；"为空"按 `EmptyUtil.isEmpty` 判断）：

| 方法 | 行为 |
|---|---|
| `isTrueOrFalse(b, trueRun, falseRun)` | if / else |
| `isTrueFun(b, runnable)`、`isTrueFun(b, obj, consumer)` | 条件为真时执行 |
| `presentOrElse(obj, consumer, emptyRun)` | 非空时消费，否则执行 emptyRun |
| `notEmptyFun(obj, consumer)` | 非空时消费 |
| `emptyThrowFun(obj, message, consumer)` | 为空时抛 `BusinessException(message)` |
| `emptyThrowFun(obj, message, code, consumer)` | 为空时抛 `BusinessException(code, message)`；**参数顺序是 message 在前** |
| `emptyThrowFun(function, obj, message, code[, supplier])`、`emptyThrowFun(biFunction, obj, u, message, code[, supplier])` | 校验后执行函数，结果为 null 时取 supplier |
| `actionFun(function, obj, supplier)`、`actionFun(biFunction, obj, u, supplier)` | 参数为空或结果为 null 时返回 supplier |
| `predicate(obj, predicate, consumer)` | 断言为真时消费 |

`ThrowingSupplier<T, E extends Exception>`：可以抛受检异常的 Supplier。

---

## 10. 工具类要点

### EmptyUtil
- `isEmpty(Object)`：null、空白字符串、空集合、空 Map、空数组都算空；其他对象按 `toString().trim()` 判断。数字 `0` 不算空。
- 字符串 `"null"` / `"undefined"` **不算空**。处理前端传来的值时，请用 `isEmptyChars` / `isNotEmptyChars`（`isNullChars`、`isUndefinedOrNull`、`isNotNullChars`、`isNotUndefinedChars` 也可用）。
- `emptyThrowException(value, message)`、`emptyThrowException(value, code, message)`：抛 `BusinessException`。
- `allFieldIsEmpty(obj)`：所有可读属性都为空时返回 true。

### TransformUtil / MapStructConvertUtil / MyBeanUtils
- `TransformUtil.transformObj(obj, Cls)`、`transformList(list, Cls)`、`transformPageResult(page, Cls)`、`transformFromMap(map, Cls)`、`transformToMap(obj)`。
- 策略：优先使用 mapstruct-plus `Converter`。失败时降级到 `MyBeanUtils.copyBean`（Objenesis 实例化，跳过 null 属性），并把这对类型缓存为"不支持"，之后不再尝试 MapStruct。
- 空值约定：`transformObj(null)` 返回 null；`transformList(空)` 返回新的空 ArrayList；`transformPageResult(null)` 返回 null。
- 想走 MapStruct 高性能路径，需要在源类上加 `@AutoMapper(target = Target.class)`，并配置 `mapstruct-plus-processor` 注解处理器。
- **非 Spring 环境自动降级**：`MapStructConvertUtil` 懒加载 `Converter`（`getConverterOrNull()` / `isAvailable()` / `getConverter()`）。Spring 容器未启动或非 Spring 环境（单元测试、main 方法）时，`TransformUtil` 直接走 Bean 拷贝（`transformFromMap` 走 Hutool `BeanUtil.toBean`），且不会把类型对写入"不支持"缓存，容器启动后恢复使用 MapStruct。容器中没有 `Converter` Bean 时打一次 WARN，之后始终走 Bean 拷贝。
- 直接调用 `MapStructConvertUtil.convert*` / `copyValue` 时，转换器不可用会抛 `IllegalStateException`，没有降级。
- `MapStructConvertUtil.copyValue(source, target, forceNullFields...)`：源字段为 null 时默认不覆盖目标字段。`forceNullFields`（字符串或 `EFunction`）中列出的字段，在源值为 null 时会强制把目标字段置为 null。`copyValue(source, target, (s, t) -> {...})` 在拷贝后执行自定义回调。"null 不覆盖"依赖编译参数 `-Amapstruct.plus.nullValuePropertyMappingStrategy=IGNORE`（easyfk-base 已配置），业务项目需要保持一致。

### ReflectUtil
- 使用 `ClassValue` 按类缓存字段（类卸载时自动释放）。`getAllFields` 包含父类字段，子类字段排在前面；同名字段解析为子类字段。
- `getFields` / `getAllFields` / `getAllFieldsByCutOff(cls, stopClass)`（不包含 stopClass 本身的字段）、`getFieldByFieldName`、`hasField`、`getValueByFieldName`、`getValueByField`、`setValueByFieldName`、`setValueByField`、`getFieldsByAnnotation`、`getFieldNameByAnnotation`、`getValueByAnnotation`（取第一个匹配字段的值）、`getFieldAndValueByAnnotation`（TreeMap，包含 null 值）、`getFieldAndValueByAnnotationNotNull`、`getFieldTypeByAnnotation`、`createInstance`、`createInstanceAndSetValue`、`clearAllCaches`、`clearCacheForClass`、`getCacheStats`。
- 返回值约定：找不到注解字段时返回 **null（不是空数组）**；`setValueByFieldName` 在字段不存在时抛 `IllegalArgumentException`，但 `setValueByField` 遇到类型不匹配等错误**只打日志不抛异常**；`createInstance` 失败时返回 null。

### StringUtil（继承 `org.springframework.util.StringUtils`）
`underlineToCamel`、`camelToUnderline`（处理连续大写：`userIDCard` 转为 `user_id_card`）、`upperFirstChar`、`lowerFirstChar`（空串返回 null）、`isChinese`。

### SplitUtil
- `split(str)`：同时按 `,` `，` 空白 `/` `;` `\t` 分割并 trim，去掉空项。
- `split(str, seps...)`：只按指定分隔符分割。
- `splitAndConvert(str, Integer.class[, seps...])`：使用 Hutool `Convert` 转换类型。
- **输入为空或分割结果为空时返回 `null`，不是空 List**，遍历前必须判空。

### EnumUtils
枚举需要提供 **public** 方法：`getValue()`、`getCode()`，可选 `getSubCode()` / `getSubText()`。
- `getEnumByValue` / `getNameByValue(cls, v[, methodName])` / `getEnumByCode` / `getNameByCode(cls, c[, methodName])` / `getValueByCode` / `getEnumBySubCode` / `getSubTextBySubCode`。
- `getNameBy*` 不传 methodName 时返回的是 `enum.name()`（常量名），不是中文描述；要取描述，请传 `methodName`（如 `"getName"`）。
- 匹配规则：`Number` 之间按数值比较（`1` 与 `1L` 相等）；**字符串 `"1"` 与数字 `1` 不相等**。找不到时返回 null。

### OrderNoUtil（谨慎使用）
- 组成：`get18OrderNumber()` = 17 位时间戳（`yyyyMMddHHmmssSSS`）+ 1 位毫秒内序列；`get22OrderNumber()` = 17 位 + 5 位序列；`get27OrderNumber()` = 17 位 + 5 位序列 + 5 位随机数。带 prefix 的重载会额外加上前缀长度，默认把前缀转为大写。
- 单调逻辑时钟：同一毫秒内序列递增，序列耗尽（18 位每毫秒 10 个，22/27 位每毫秒 100000 个）或时钟回拨时借用下一毫秒，因此**单 JVM 内不重复**，但高并发下时间部分可能领先于真实时间。
- 唯一性只限单 JVM，多实例部署会重复，**不能作为分布式单号或跨实例的数据库唯一键**。需要全局唯一 ID 时，请使用 component-autoId（如 autoId-redis）。

### LocalDateUtil
固定格式：`yyyy-MM-dd`、`HH:mm:ss`、`yyyy-MM-dd HH:mm:ss`，使用系统时区。
`getLocalDate/Time/DateTime[String]`、`localDateToString`、`localDateTimeToString`、`string2LocalDate/Time/DateTime`、`date2LocalDate/Time/DateTime`、`localDateTime2Date`、`between(start, end)`（当前时间严格位于开区间内）、`dayStartTime` / `dayEndTime`、`firstDayOfWeek`（周一）/ `lastDayOfWeek`（周日）、`firstDayOfMonth` / `lastDayOfMonth`、`getIntervalDays`（绝对值）、`isLocalDate` / `isLocalDateTime`。

### I18NUtil
- 默认资源基名 `i18n/messages`，即 classpath 下的 `i18n/messages_zh_CN.properties` 等，UTF-8 编码。
- `getMessage(code)`、`getMessage(code, args)`、`getMessage(code, path)`、`getMessage(code, path, args)`、`getMessage(code, locale, path, args)`；code / path 为空时抛 `IllegalArgumentException`；**找不到 key 时返回 code 本身**。
- 语言取自 `RequestHeaderContext` 中的 `language`（请求头 `Language`），格式为 `en` 或 `en_US`（下划线分隔）；为空或格式错误时默认 `zh_CN`。

### ExpressionUtil
`parse("#order.id", method, args)` 返回 String；`parse(expr, method, args, Cls)` 返回指定类型。依赖方法参数名，编译时需要带 `-parameters`（Spring Boot Gradle 插件默认开启）。常用于自定义注解切面中解析 SpEL key。

### DisableUtil
`createObjListByDisableAction(DisableActionParam)`：根据 `DisableFieldReq.ids` 和 `value` 批量构造"只含 id 和状态字段"的对象，用于批量启用/禁用。不指定 `idField` 时取 `@PrimaryKey` 字段。参数缺失或没有主键时抛 `IllegalArgumentException`（带具体原因），反射赋值失败时抛 `IllegalStateException`（保留 cause）。

---

## 11. 常量

- `RequestHeaderConstant`：`Request-Nonce`、`Request-Token`、`Access-Token`、`Timestamp`、`Reset-Sign`、`Sign-Version`、`Sign-Body`、`App-Id`、`Api-Timestamp`、`Api-Nonce`、`Api-Sign`、`Api-Body`、`Device-No`、`Client-Type`、`Language`、`TRACE_ID`。
- `CharacterConstant`：`UNKNOWN` `UNDEFINED` `NULL` `HASH` `STAR` `JAR` `UNDERLINE_CHAR` `UNDERLINE_VARCHAR` `SLASH` `DOT` `COMMA_DELIMITERS` `STATIC_WITH` `STATIC_URL`（静态资源后缀）`DATABASE_TYPE_MYSQL` `DATABASE_TYPE_MONGO`。
- `FileType`：`IMAGE` / `FILE` / `VIDEO`。

---

## 12. 生成代码时的规则（Do / Don't）

- Controller 返回 `ResponseResult`，用 `RRBuilder`；Service 内部返回 `BaseResult`，用 `BRBuilder`；不要把两者混用。
- 失败参数顺序：`RRBuilder.buildFailedBody(code, msg)`，`BRBuilder.failResult(msg, code)`，`new BusinessException(code, msg)`，`BEBuilder.exception(msg, code)`，`EmptyUtil.emptyThrowException(v, code, msg)`，`FunctionExecutor.emptyThrowFun(v, msg, code, consumer)`。写代码时逐个核对。
- 字段引用一律使用 getter 方法引用，不要写字符串字段名或 lambda 表达式。
- 业务错误用 `BusinessException` / `BEBuilder`，错误码用实现 `BaseErrorEnum` 的枚举（需同时实现 setter）。
- 读取 `UserDataContext` / `RequestHeaderContext` 时必须判空；异步任务里不要依赖这两个上下文。
- 对 `SplitUtil`、`ReflectUtil.getFieldsByAnnotation`、`getFieldNameByAnnotation` 的返回值先判空再使用。
- 前端参数判空用 `isEmptyChars` / `isNotEmptyChars`。
- 不用 `OrderNoUtil` 生成唯一主键或对外单号。
- 依赖 `TransformUtil` 的单元测试不启动 Spring 时会走 Bean 拷贝降级，`@AutoMapper` 的自定义映射不会生效；需要验证 MapStruct 映射时使用 `@SpringBootTest`。
- `MyBeanUtils.copyPropertiesNotNull(src, target, ignore...)` 只拷贝源对象的非 null 属性，第三个参数是额外忽略的属性；DTO/PO 转换仍优先用 `TransformUtil` / `MapStructConvertUtil`。
- 工具类的选用规则（框架有的必须用框架的、第三方库用哪个）见 [easyfk-core-toolkit-skill.md](easyfk-core-toolkit-skill.md)。

---

## 13. 复查记录（原文档与源码差异，供修订文档）

| # | 位置 | 文档描述 | 源码事实 |
|---|---|---|---|
| 1 | core开发文档 §2 | `spring-boot-starter-test` 是 `api` 依赖 | 已改为 `testImplementation`，不再传递 |
| 2 | core开发文档 §5.4 | `LoginUser` / `UserData` 有 `dataCachedKey`、`authCachedKey` | 实际为 `loginToken`；`UserData` 还有 `accountType`、`thirdAccount`、`thirdType` |
| 3 | core开发文档 §8.2 | `BaseErrorEnum` 示例只有 getter | 接口要求 `setCode` / `setMessage`，不实现则编译失败 |
| 4 | core开发文档 §9.2 | `emptyThrowFun(obj, msg, consumer)` 等签名 | 另有 `(obj, message, code, consumer)` 等 6 个重载；`isTrueFun` 有两个重载 |
| 5 | core开发文档 §6 | 未列出 `BEBuilder`、`SRPBuilder.pageAndExample`、`MRPBuilder.buildRequest(List<?>, Class)` | 均存在 |
| 6 | core开发文档 §10.7、特点 §2.9 | 22 位 = 17 + 5 随机，27 位 = 17 + 10 随机 | 实测 19 位和 24 位；18 位版本高并发下大量重复 **已修复**：位数与方法名一致（17 位时间戳 + 序列[+随机]），单调逻辑时钟保证单 JVM 内不重复 |
| 7 | core开发文档 §11.2 | 请求头常量缺少签名相关项 | 新增 `Sign-Version`、`Sign-Body`、`App-Id`、`Api-*` |
| 8 | 特点 §2.4 | ReflectUtil 使用"六层 WeakHashMap"缓存 | 已改为 `ClassValue`，加 cutOff 的 `ConcurrentHashMap` |
| 9 | 特点 §2.5 | "所有注解均为 RUNTIME，驱动自动化行为" | `@DataFilterField` 没有声明 Retention；`@DataFilterField`、`@EnumValueAnnotation`、`@BetweenField` 没有处理代码；注解共 13 个而不是 12 个 **已修复**：全仓库确认这三个注解无使用、无处理代码，已删除，现有 10 个注解 |
| 10 | 特点 §3.1 | "所有 DTO 都 implements Serializable" | `DisableActionParam`、`DisableFieldReq`、`ValidationResult` 只加了 `@SerializableClass`，没有实现 `Serializable` **已修复**：三个类均已 `implements Serializable` |
| 11 | 框架手册 §3.1.2、§6.2 | `import ...core.builder.BRBuilder`；`BRBuilder...fail("msg")`、`.success(user)` 返回 `ResponseResult`；`TransformUtil.transform(...)` | 包名是 `builders`；`fail()` / `success(boolean)` 不接收业务参数；BRBuilder 返回 `BaseResult`；方法名是 `transformObj` |
| 12 | 框架手册 §3.1.1 | `UserAuth` 属于 core；`BaseDto` 自动管理时间 | `UserAuth` 在 easyfk-authority；时间字段由 ORM 组件的 `AutoSetValueHandler` 填充 |
| 13 | 框架手册 §3.1 | core "无外部依赖" | 通过 `api` 传递 Spring Boot、Hutool、fastjson2、Jackson、mapstruct-plus 等 |
| 14 | 特点 §2.3 | TransformUtil 失败时自动降级 | 非 Spring 环境下抛 `ExceptionInInitializerError`，无法降级 **已修复**：`Converter` 改为懒加载，不可用时 `TransformUtil` 降级为 Bean 拷贝 |

| 15 | 源码 `EnumUtils` | — | 日志使用 `{0}` 占位符，slf4j 无法解析；`getCachedMethod` 对实例方法调用 `canAccess(null)` 会抛异常 **已修复**：占位符改为 `{}`，改用 `trySetAccessible()` |
| 16 | 源码 `MapStructConvertUtil` | — | 非静态的 `convert(map, type, consumer)` 无法调用 **已修复**：改为 `static` |
| 17 | 源码 `MyBeanUtils` / `DisableUtil` / `EmptyUtil` | — | `copyPropertiesNotNull` 名实不符；`DisableUtil` 吞掉原始异常、无主键静默返回 null；`EmptyUtil` 属性缓存 `WeakHashMap` 永不回收 **已修复**：详见 easyfk-core-toolkit-skill.md 复查记录 |
