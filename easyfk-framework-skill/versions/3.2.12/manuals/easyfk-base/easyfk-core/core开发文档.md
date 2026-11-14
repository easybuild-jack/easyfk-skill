# easyfk-core 开发文档

## 1. 模块概述

`easyfk-core` 是 EasyFK 框架的**核心基础模块**，为所有上层模块提供统一的数据模型、注解体系、构建器、上下文管理、异常处理、函数式编程工具和通用工具类。该模块是整个框架的底层基石，不依赖任何其他 EasyFK 模块。

---

## 2. 模块依赖

| 依赖 | 方式 | 说明 |
|---|---|---|
| `spring-boot-starter` | `api` | Spring Boot 核心 |
| `spring-boot-starter-test` | `api` | 测试支持 |
| `spring-boot-configuration-processor` | `api` | 配置处理器 |
| `spring-boot-starter-aop` | `api` | AOP 支持 |
| `spring-boot-starter-validation` | `api` | 参数校验 |
| `jackson-databind/core/annotations` | `api` | JSON 序列化（Jackson） |
| `fastjson2` | `api` | JSON 序列化（FastJSON2） |
| `hutool-all` | `api` | Hutool 工具集 |
| `swagger-annotations` (v3) | `api` | OpenAPI 文档注解 |
| `slf4j-api` | `api` | 日志门面 |
| `mapstruct-plus-spring-boot-starter` | `api` | 高性能对象映射 |

---

## 3. 包结构

```
com.mcst.easyfk.core
├── annotation/               # 注解定义（12个）
├── builders/                 # 构建器（6个）
├── constants/                # 常量定义（4个）
├── context/                  # 线程上下文（3个）
├── dto/                      # 数据传输对象
│   ├── login/                  - 登录相关 DTO
│   ├── page/                   - 分页相关 DTO
│   ├── request/                - 请求相关 DTO
│   ├── response/               - 响应相关 DTO
│   └── validation/             - 校验结果 DTO
├── exception/                # 异常定义
├── function/                 # 函数式接口
└── utils/                    # 工具类
    ├── common/                 - 通用工具
    ├── date/                   - 日期工具
    ├── expression/             - 表达式工具
    └── returns/                - 返回值工具
```

---

## 4. 注解体系

### 4.1 数据标识类注解

| 注解 | 目标 | 说明 |
|---|---|---|
| `@PrimaryKey` | 字段 | 主键字段标识 |
| `@PrimaryField` | 字段 | 主要字段标识 |
| `@SerializableClass` | 类 | 标记需要强制注册到序列化组件的类 |

### 4.2 查询条件类注解

| 注解 | 目标 | 说明 | 属性 |
|---|---|---|---|
| `@BetweenField` | 字段 | 标记为 BETWEEN 查询条件字段 | - |
| `@BetweenStart` | 字段 | BETWEEN 范围起始字段 | `field` - 取值字段名 |
| `@BetweenEnd` | 字段 | BETWEEN 范围截止字段 | `field` - 取值字段名 |
| `@AssistConditionField` | 字段 | SQL 辅助查询条件（分页、排序等） | - |

### 4.3 唯一性校验类注解

| 注解 | 目标 | 说明 | 属性 |
|---|---|---|---|
| `@SingleUniqueField` | 字段 | 单字段唯一校验 | `repetitionMsg` - 重复提示语 |
| `@CombUniqueField` | 字段 | 组合字段唯一校验 | `combinationField` - 组合字段名, `repetitionMsg` - 重复提示语 |

### 4.4 业务功能类注解

| 注解 | 目标 | 说明 | 属性 |
|---|---|---|---|
| `@SignField` | 字段 | 需要参与签名计算的字段 | - |
| `@ForbiddenField` | 字段 | 禁止操作的字段 | `value` |
| `@EnumValueAnnotation` | 字段 | 枚举值自动填充 | `enumClass`, `field`, `methodName` |
| `@DataFilterField` | 字段 | SaaS 数据过滤条件 | `mapOperatorFiled`, `type`(0单选/1多选) |

---

## 5. 数据模型（DTO）

### 5.1 响应模型

#### BaseResult\<T\> —— 内部调用结果

```java
BaseResult<T>
├── success: Boolean      // 是否成功
├── data: T               // 数据
├── msg: String           // 消息
└── code: String          // 状态码
```

#### ResponseResult\<T\> —— 统一 API 响应

```java
ResponseResult<T>
├── code: String          // OK/ERROR/UN_LOGIN/UN_AUTH/PARAM_ERROR/BUSYNESS
├── count: Long           // 总条数（分页用）
├── msg: String           // 提示消息
├── data: T               // 数据
└── traceId: String       // 链路追踪 ID
```

### 5.2 请求模型

#### BasicParam —— 基础查询参数

| 字段 | 类型 | 说明 |
|---|---|---|
| `top` | Integer | TOP N 查询 |
| `page` | Integer | 当前页数 |
| `limit` | Integer | 查询条数 |
| `totalCount` | Boolean | 是否查询总数 |
| `ascFields` | String | 升序排序字段 |
| `descFields` | String | 降序排序字段 |
| `searchKeyWord` | String | 搜索关键字 |
| `start` / `stop` | String | 时序数据库范围 |

#### SearchRequest\<T\> —— 查询请求封装

| 字段 | 类型 | 说明 |
|---|---|---|
| `parmaObj` | T | 查询条件对象 |
| `pageSearch` | PageSearch | 分页参数 |
| `selectFields` | String[] | 选择查询的字段 |
| `nullFields` | String[] | 为空的字段条件 |
| `inParams` | Map\<String, List\<?\>\> | IN 条件 |
| `likeFields` | String[] | 模糊查询字段 |
| `notFields` | String[] | 不等于字段 |
| `gThanFields` / `lThanFields` | String[] | 大于/小于字段 |
| `gThanOrEqualFields` / `lThanOrEqualFields` | String[] | 大于等于/小于等于字段 |
| `multipleFields` | String[] | 多选字段 |

#### ModifyRequest\<T\> —— 操作请求封装

| 字段 | 类型 | 说明 |
|---|---|---|
| `idList` | List\<?\> | ID 列表 |
| `parmaObj` | T | 操作参数对象 |
| `paramList` | List\<T\> | 列表参数 |
| `enableNullFields` | String[] | 可以为空的字段 |

#### BatchBasicReq\<PK\> —— 批量操作基础请求

| 字段 | 类型 | 说明 |
|---|---|---|
| `ids` | PK | 对象 ID，多个用逗号分隔 |

### 5.3 分页模型

#### PageSearch —— 分页查询参数

| 字段 | 类型 | 说明 |
|---|---|---|
| `page` | Integer | 当前页数 |
| `limit` | Integer | 每页条数 |
| `totalCount` | Boolean | 是否查询总数 |

#### PageResult\<T\> —— 分页结果

| 字段 | 类型 | 说明 |
|---|---|---|
| `total` | Long | 总记录数 |
| `rows` | List\<T\> | 当前页数据 |

### 5.4 登录模型

#### LoginUser —— 登录用户基本信息

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | String | 名称 |
| `userType` | String | 用户类型（platform/customer/agent/merchant） |
| `dataCachedKey` | String | 数据缓存 Key |
| `authCachedKey` | String | 权限缓存 Key |

#### UserData —— 当前登录用户完整信息

| 字段 | 类型 | 说明 |
|---|---|---|
| `userId` | String | 用户 ID |
| `accountId` | String | 账户 ID |
| `name` / `phone` / `nickname` / `avatar` | String | 基本信息 |
| `type` | String | 用户类型 |
| `groupId` / `groupName` | String | 分组信息 |
| `departmentId` / `departmentName` | String | 部门信息 |
| `agentId` / `agentName` | String | 代理商信息 |
| `merchantId` / `merchantName` | String | 商户信息 |
| `orgId` / `orgName` | String | 组织信息 |
| `extendData` | Map\<String, Object\> | 扩展数据 |
| `bizType` | Set\<String\> | 业务类型集合 |
| `dataCachedKey` / `authCachedKey` | String | 缓存 Key |

---

## 6. 构建器（Builders）

### 6.1 BRBuilder —— BaseResult 构建器

```java
// 链式构建
BRBuilder.<String>builder(true).data("token").msg("成功").build();

// 快捷方法
BRBuilder.successResult();
BRBuilder.successResult(data);
BRBuilder.failResult();
BRBuilder.failResult("错误消息", "ERROR_CODE");
```

### 6.2 RRBuilder —— ResponseResult 构建器

```java
// 成功响应
RRBuilder.buildSuccessBody();
RRBuilder.buildSuccessBody(data);
RRBuilder.buildSuccessPageBody(count, dataList);
RRBuilder.buildSuccessListBody(dataList);

// 失败响应
RRBuilder.buildFailedBody("错误消息");
RRBuilder.buildFailedBody("ERROR_CODE", "错误消息");

// BaseResult 转 ResponseResult
RRBuilder.buildBodyByBaseResult(baseResult);

// 分页结果转响应
RRBuilder.buildBodyByPageResult(pageResult);

// 异常转响应
RRBuilder.buildFailByException(exception);
```

### 6.3 PRBuilder —— PageResult 构建器

```java
PRBuilder.result(total, rows);
PRBuilder.<User>builder().total(100L).rows(userList).build();
```

### 6.4 SRPBuilder —— SearchRequest 构建器

```java
// 从 BasicParam 自动构建（自动提取分页参数）
SRPBuilder.buildRequest(queryParam);

// 链式构建（类型安全的 Lambda 字段引用）
SRPBuilder.<UserDto>builder()
    .example(queryParam)
    .page(new PageSearch(1, 20))
    .likeFields(UserDto::getName, UserDto::getPhone)
    .in(UserDto::getStatus, Arrays.asList(0, 1))
    .nullFields(UserDto::getDeletedAt)
    .notFields(UserDto::getType)
    .selectFields(UserDto::getName, UserDto::getPhone)
    .build();
```

### 6.5 MRPBuilder —— ModifyRequest 构建器

```java
// 单对象操作
MRPBuilder.buildRequest(userDto);
MRPBuilder.buildRequest(reqObj, UserDto.class);  // 自动类型转换

// 批量操作
MRPBuilder.buildRequest(userDtoList);

// 链式构建
MRPBuilder.<UserDto>builder()
    .param(userDto)
    .ids("id1", "id2", "id3")
    .enableNullFields(UserDto::getAvatar, UserDto::getNickname)
    .build();
```

### 6.6 OBJBuilder —— 通用对象构建器

```java
// 通过 Lambda 引用设置字段值
UserDto user = OBJBuilder.builder(UserDto.class)
    .setFieldValue(UserDto::getName, "张三")
    .setFieldValue(UserDto::getPhone, "13800138000")
    .build();
```

---

## 7. 线程上下文（Context）

### 7.1 UserDataContext —— 用户数据上下文

```java
UserDataContext.setUserData(userData);     // 设置当前线程用户数据
UserData data = UserDataContext.getUserData(); // 获取当前线程用户数据
UserDataContext.remove();                  // 清理
```

### 7.2 RequestHeaderContext —— 请求头上下文

```java
RequestHeaderContext.setRequestHeaders(headers);
RequestHeaders h = RequestHeaderContext.getRequestHeaders();
RequestHeaderContext.remove();
```

### 7.3 TraceIdContext —— 链路追踪上下文

使用 `InheritableThreadLocal`，支持父子线程传递。

```java
TraceIdContext.setTraceId("trace-001");
String traceId = TraceIdContext.getTraceId();
boolean has = TraceIdContext.hasTraceId();
String safe = TraceIdContext.getTraceIdOrDefault("N/A");
String required = TraceIdContext.getRequiredTraceId(); // 不存在时抛异常

// 安全执行（自动清理）
TraceIdContext.executeWithCleanup(() -> {
    // 业务逻辑
});

TraceIdContext.remove();
```

---

## 8. 异常体系

### 8.1 BusinessException —— 统一业务异常

| 字段 | 类型 | 说明 |
|---|---|---|
| `errorCode` | String | 系统级错误码 |
| `errorMsg` | String | 系统级错误信息 |
| `i18nCode` | String | 国际化错误码 |
| `msgPath` | String | 国际化配置文件路径 |
| `args` | Object[] | 错误信息参数 |

**特点：** `fillInStackTrace()` 返回 `this`，不填充堆栈轨迹，提高性能。

```java
// 使用枚举
throw new BusinessException(MyErrorEnum.USER_NOT_FOUND);
// 使用 code + message
throw new BusinessException("USER_001", "用户不存在");
// 仅 message
throw new BusinessException("操作失败");
```

### 8.2 BaseErrorEnum —— 错误枚举接口

业务模块实现此接口定义错误码枚举：

```java
public enum MyErrorEnum implements BaseErrorEnum {
    USER_NOT_FOUND("USER_001", "用户不存在");
    // ...
}
```

### 8.3 ValidateException —— 校验异常

简单的运行时校验异常。

---

## 9. 函数式编程

### 9.1 EFunction\<T, R\> —— 可序列化函数接口

继承 `Function<T, R>` 和 `Serializable`，支持 Lambda 表达式转字段名。

```java
// 类型安全的字段引用
EFunction<UserDto, String> nameRef = UserDto::getName;
String fieldName = FunctionColumnToStringUtil.columnToString(nameRef); // "name"
```

### 9.2 FunctionExecutor —— 函数执行器

| 方法 | 说明 |
|---|---|
| `isTrueOrFalse(bool, trueFun, falseFun)` | 条件分支处理 |
| `presentOrElse(obj, consumer, emptyFun)` | 空值/非空值分支 |
| `emptyThrowFun(obj, msg, consumer)` | 为空抛异常，不为空执行 |
| `notEmptyFun(obj, consumer)` | 值不为空时执行 |
| `actionFun(function, obj, supplier)` | 执行函数，空时返回默认值 |
| `isTrueFun(bool, runnable)` | 条件为 true 时执行 |
| `predicate(obj, predicate, consumer)` | 断言条件执行 |

### 9.3 ThrowingSupplier\<T, E\> —— 可抛异常的 Supplier

```java
ThrowingSupplier<String, IOException> supplier = () -> readFile();
```

---

## 10. 工具类

### 10.1 EmptyUtil —— 空值判断工具

```java
EmptyUtil.isEmpty(value);          // 支持 String/List/Map/Array/Object
EmptyUtil.isNotEmpty(value);
EmptyUtil.allFieldIsEmpty(obj);    // 判断对象所有字段是否为空
EmptyUtil.emptyThrowException(value, "不能为空"); // 为空抛 BusinessException
EmptyUtil.isNotEmptyChars(str);    // 排除 "null" 和 "undefined"
```

### 10.2 TransformUtil —— 对象转换工具

优先使用 MapStruct，失败时自动降级到 BeanUtils 拷贝。

```java
UserResp resp = TransformUtil.transformObj(dto, UserResp.class);
List<UserResp> list = TransformUtil.transformList(dtoList, UserResp.class);
PageResult<UserResp> page = TransformUtil.transformPageResult(pageResult, UserResp.class);
Map<String, Object> map = TransformUtil.transformToMap(obj);
UserDto dto = TransformUtil.transformFromMap(map, UserDto.class);
```

### 10.3 MapStructConvertUtil —— MapStruct 转换工具

```java
UserResp resp = MapStructConvertUtil.convert(dto, UserResp.class);
List<UserResp> list = MapStructConvertUtil.convertList(dtoList, UserResp.class);

// 拷贝值（Lambda 指定强制置空字段）
MapStructConvertUtil.copyValue(source, target, UserDto::getAvatar);

// 自定义回调
MapStructConvertUtil.copyValue(source, target, (s, t) -> {
    if (s.getStatus() == null) t.setStatus(0);
});
```

### 10.4 ReflectUtil —— 反射工具类

提供高性能、缓存优化的反射操作：

```java
Field[] fields = ReflectUtil.getAllFields(clazz);           // 获取所有字段（含父类）
Object value = ReflectUtil.getValueByFieldName(obj, "name");// 获取字段值
ReflectUtil.setValueByFieldName(obj, "name", "张三");       // 设置字段值
Field[] annotated = ReflectUtil.getFieldsByAnnotation(clazz, PrimaryKey.class);
T instance = ReflectUtil.createInstanceAndSetValue(clazz, valueMap);
```

### 10.5 StringUtil —— 字符串工具

```java
StringUtil.underlineToCamel("user_name");   // "userName"
StringUtil.camelToUnderline("userName");     // "user_name"
StringUtil.upperFirstChar("name");          // "Name"
StringUtil.lowerFirstChar("Name");          // "name"
StringUtil.isChinese("中文");               // true
```

### 10.6 SplitUtil —— 字符串分割工具

```java
List<String> list = SplitUtil.split("a,b，c d/e");  // ["a","b","c","d","e"]
List<Integer> ids = SplitUtil.splitAndConvert("1,2,3", Integer.class);
```

### 10.7 OrderNoUtil —— 订单号生成工具

```java
OrderNoUtil.get18OrderNumber("PO");   // "PO202602281430001230"
OrderNoUtil.get22OrderNumber("SO");   // 22位订单号
OrderNoUtil.get27OrderNumber("TX");   // 27位订单号
```

### 10.8 EnumUtils —— 枚举工具

```java
MyEnum e = EnumUtils.getEnumByValue(MyEnum.class, "value1");
String name = EnumUtils.getNameByValue(MyEnum.class, "value1");
MyEnum e2 = EnumUtils.getEnumByCode(MyEnum.class, "code1");
```

### 10.9 LocalDateUtil —— 日期时间工具

```java
LocalDateUtil.getLocalDateTimeString();          // "2026-02-28 14:30:00"
LocalDateUtil.string2LocalDateTime("2026-02-28 14:30:00");
LocalDateUtil.localDateTime2Date(localDateTime);
LocalDateUtil.date2LocalDateTime(date);
LocalDateUtil.between("2026-01-01 00:00:00", "2026-12-31 23:59:59");
LocalDateUtil.firstDayOfMonth(LocalDate.now());
LocalDateUtil.getIntervalDays(date1, date2);
```

### 10.10 I18NUtil —— 国际化工具

```java
I18NUtil.getMessage("user.not.found");
I18NUtil.getMessage("user.welcome", new Object[]{"张三"});
I18NUtil.getMessage("error.code", "custom/messages");
Locale locale = I18NUtil.getLocale();  // 从请求头自动获取
```

### 10.11 ExpressionUtil —— SpEL 表达式工具

```java
String result = ExpressionUtil.parse("#userId", method, args);
Integer value = ExpressionUtil.parse("#order.amount", method, args, Integer.class);
```

### 10.12 其他工具

| 工具类 | 说明 |
|---|---|
| `FunctionColumnToStringUtil` | Lambda 方法引用转字段名 |
| `Exception2ResultUtil` | BusinessException 转 ResponseResult/BaseResult |
| `ReturnErrorUtil` | 根据返回类型构建错误结果 |
| `MyBeanUtils` | Bean 拷贝（已建议迁移至 MapStructConvertUtil） |
| `DisableUtil` | 禁用操作对象列表构建 |

---

## 11. 常量定义

### 11.1 ReturnCodeConstant —— 响应状态码

| 常量 | 值 | 说明 |
|---|---|---|
| `SUCCESS` | `"OK"` | 处理成功 |
| `ERROR` | `"ERROR"` | 处理失败 |
| `UN_LOGIN` | `"UN_LOGIN"` | 未登录 |
| `UN_AUTH` | `"UN_AUTH"` | 无权限 |
| `PARAM_ERROR` | `"PARAM_ERROR"` | 参数错误 |
| `BUSYNESS` | `"BUSYNESS"` | 系统繁忙 |

### 11.2 RequestHeaderConstant —— 请求头常量

| 常量 | 值 | 说明 |
|---|---|---|
| `CHAIN_NAME` | `"Chain-Data"` | 网关链路数据 |
| `REQUEST_NONCE` | `"Request-Nonce"` | 防重放随机数 |
| `REQUEST_TOKEN` | `"Request-Token"` | 请求令牌 |
| `ACCESS_TOKEN` | `"Access-Token"` | 访问令牌 |
| `TIMESTAMP` | `"Timestamp"` | 时间戳 |
| `PARAM_SIGN` | `"Param-Sign"` | 参数签名 |
| `RESET_SIGN` | `"Reset-Sign"` | 重放签名 |
| `DEVICE_NO` | `"Device-No"` | 设备号 |
| `CLIENT_TYPE` | `"Client-Type"` | 客户端类型 |
| `LANGUAGE` | `"Language"` | 语言 |
| `TRACE_ID` | `"TRACE_ID"` | 链路追踪 ID |

### 11.3 CharacterConstant —— 字符常量

包含下划线、斜杠、逗号、点号等常用分隔符，静态资源后缀列表，数据库类型标识等。

### 11.4 FileType —— 文件类型枚举

`IMAGE` / `FILE` / `VIDEO`
