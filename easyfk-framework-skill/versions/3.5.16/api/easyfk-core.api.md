# easyfk-core API 签名速查（easyfk 3.5.16）

> 坐标：`com.mcst:easyfk-core`　源码：`easyfk-base/easyfk-core`
> 由 `scripts/gen-api.py` 从 63 个源文件自动提取，共 63 个类型、267 个方法/构造器、140 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-core-skill.md](../modules/easyfk-core-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 类型索引

- `com.mcst.easyfk.core.annotation`：[AssistConditionField](#assistconditionfield)、[BetweenEnd](#betweenend)、[BetweenStart](#betweenstart)、[CombUniqueField](#combuniquefield)、[ForbiddenField](#forbiddenfield)
    [PrimaryField](#primaryfield)、[PrimaryKey](#primarykey)、[SerializableClass](#serializableclass)、[SignField](#signfield)、[SingleUniqueField](#singleuniquefield)
- `com.mcst.easyfk.core.builders`：[BEBuilder](#bebuilder)、[BRBuilder](#brbuilder)、[MRPBuilder](#mrpbuilder)、[OBJBuilder](#objbuilder)、[PRBuilder](#prbuilder)
    [RRBuilder](#rrbuilder)、[SRPBuilder](#srpbuilder)
- `com.mcst.easyfk.core.constants`：[CharacterConstant](#characterconstant)、[FileType](#filetype)、[RequestHeaderConstant](#requestheaderconstant)、[ReturnCodeConstant](#returncodeconstant)
- `com.mcst.easyfk.core.context`：[RequestHeaderContext](#requestheadercontext)、[TraceIdContext](#traceidcontext)、[UserDataContext](#userdatacontext)
- `com.mcst.easyfk.core.dto`：[BaseDto](#basedto)
- `com.mcst.easyfk.core.dto.login`：[LoginResult](#loginresult)、[LoginUser](#loginuser)、[UserData](#userdata)
- `com.mcst.easyfk.core.dto.page`：[PageResult](#pageresult)、[PageSearch](#pagesearch)
- `com.mcst.easyfk.core.dto.request`：[BasicParam](#basicparam)、[BatchActionReq](#batchactionreq)、[BatchBasicReq](#batchbasicreq)、[DisableActionParam](#disableactionparam)、[DisableFieldReq](#disablefieldreq)
    [ModifyRequest](#modifyrequest)、[RequestHeaders](#requestheaders)、[SearchRequest](#searchrequest)
- `com.mcst.easyfk.core.dto.response`：[BaseResult](#baseresult)、[ResponseResult](#responseresult)
- `com.mcst.easyfk.core.dto.validation`：[ValidationResult](#validationresult)
- `com.mcst.easyfk.core.exception`：[BaseErrorEnum](#baseerrorenum)、[BusinessException](#businessexception)、[ValidateException](#validateexception)
- `com.mcst.easyfk.core.function`：[EFunction](#efunction)、[FunctionExecutor](#functionexecutor)、[ThrowingSupplier](#throwingsupplier)
- `com.mcst.easyfk.core.utils.common`：[DisableUtil](#disableutil)、[EmptyUtil](#emptyutil)、[EnumUtils](#enumutils)、[Exception2ResultUtil](#exception2resultutil)、[FunctionColumnToStringUtil](#functioncolumntostringutil)
    [I18NUtil](#i18nutil)、[MapStructConvertUtil](#mapstructconvertutil)、[MyBeanUtils](#mybeanutils)、[OrderNoUtil](#ordernoutil)、[ReflectUtil](#reflectutil)
    [SplitUtil](#splitutil)、[StringUtil](#stringutil)、[TransformUtil](#transformutil)
- `com.mcst.easyfk.core.utils.date`：[LocalDateUtil](#localdateutil)
- `com.mcst.easyfk.core.utils.expression`：[ExpressionUtil](#expressionutil)
- `com.mcst.easyfk.core.utils.returns`：[ReturnErrorUtil](#returnerrorutil)

## 包 `com.mcst.easyfk.core.annotation`

### AssistConditionField

`public @interface AssistConditionField`　注解：`@Retention(RetentionPolicy.RUNTIME)` `@Target(ElementType.FIELD)` `@Documented`

_标记注解，无属性。_

### BetweenEnd

`public @interface BetweenEnd`　注解：`@Retention(RetentionPolicy.RUNTIME)` `@Target(value = {ElementType.FIELD})`

**方法**

```java
String field()  // 取值的字段名称
```

### BetweenStart

`public @interface BetweenStart`　注解：`@Retention(RetentionPolicy.RUNTIME)` `@Target(value = {ElementType.FIELD})`

**方法**

```java
String field()  // 取值的字段名称
```

### CombUniqueField

`public @interface CombUniqueField`　注解：`@Retention(RetentionPolicy.RUNTIME)` `@Target(ElementType.FIELD)` `@Documented`　组合唯一 字段注解

**方法**

```java
String combinationField()  // 组合的 字段
String repetitionMsg()  // 重复时的提示语
```

### ForbiddenField

`public @interface ForbiddenField`　注解：`@Retention(RetentionPolicy.RUNTIME)` `@Target(ElementType.FIELD)` `@Documented`　单个唯一 字段注解

**方法**

```java
String value()
```

### PrimaryField

`public @interface PrimaryField`　注解：`@Retention(RetentionPolicy.RUNTIME)` `@Target({ElementType.FIELD})`　主要字段注解

**方法**

```java
String value() default ""
```

### PrimaryKey

`public @interface PrimaryKey`　注解：`@Retention(RetentionPolicy.RUNTIME)` `@Target({ElementType.FIELD})`　主键字段标识

**方法**

```java
String value() default ""
```

### SerializableClass

`public @interface SerializableClass`　注解：`@Target(ElementType.TYPE)` `@Retention(RetentionPolicy.RUNTIME)` `@Documented`　标记需要强制注册到 序列化组件 的类，以获得最佳性能

_标记注解，无属性。_

### SignField

`public @interface SignField`　注解：`@Retention(RetentionPolicy.RUNTIME)` `@Target(ElementType.FIELD)` `@Documented`

_标记注解，无属性。_

### SingleUniqueField

`public @interface SingleUniqueField`　注解：`@Retention(RetentionPolicy.RUNTIME)` `@Target(ElementType.FIELD)` `@Documented`　单个唯一 字段注解

**方法**

```java
String repetitionMsg()  // 重复时的提示语
```

## 包 `com.mcst.easyfk.core.builders`

### BEBuilder

`public record BEBuilder(BusinessException businessException)`　BusinessExceptionBuilder 创建 BusinessException 对象

**构造参数（record 组件）**

```java
BusinessException businessException
```

**方法**

```java
static BEBuilder builder()
static BEBuilder builder(String message)
static BusinessException exception(String message)
static BusinessException exception(String message, String errorCode)
static BusinessException exceptionByI18n(String message, String i18nCode)
static BusinessException exceptionByI18n(String message, String i18nCode, Object... args)
static BusinessException exceptionByI18n(String message, String i18nCode, String msgPath)
static BusinessException exceptionByI18n(String message, String i18nCode, String msgPath, Object... args)
BEBuilder errCode(String errCode)
BEBuilder i18nCode(String i18nCode)
BEBuilder msgPath(String msgPath)
BEBuilder args(Object... args)
BusinessException build()
```

### BRBuilder

`public record BRBuilder<T>(BaseResult<T> result)`　BaseResultBuilder

**构造参数（record 组件）**

```java
BaseResult<T> result
```

**方法**

```java
static <T> BRBuilder<T> builder()
static <T> BRBuilder<T> builder(boolean success)
static <T> BaseResult<T> result(boolean success, T data, String msg, String code)
static <T> BaseResult<T> successResult()
static <T> BaseResult<T> successResult(T data)
static <T> BaseResult<T> successResult(T data, String msg)
static <T> BaseResult<T> successResult(T data, String msg, String code)
static <T> BaseResult<T> failResult()
static <T> BaseResult<T> failResult(T data)
static <T> BaseResult<T> failResult(T data, String msg)
static <T> BaseResult<T> failResult(T data, String msg, String code)
static <T> BaseResult<T> failResult(String msg, String code)
BRBuilder<T> success(boolean success)
BRBuilder<T> success()
BRBuilder<T> fail()
BRBuilder<T> data(T data)
BRBuilder<T> code(String code)
BRBuilder<T> msg(String msg)
BaseResult<T> build()
```

### MRPBuilder

`public record MRPBuilder<T>(ModifyRequest<T> request)`　ModifyRequestParamBuilder 操作类接口请求参数封装对象

**构造参数（record 组件）**

```java
ModifyRequest<T> request
```

**方法**

```java
static <T> MRPBuilder<T> builder()
static <T> MRPBuilder<T> builder(ModifyRequest<T> request)
static <T> ModifyRequest<T> buildRequest(T param)
static <T> ModifyRequest<T> buildRequest(Object param, Class<T> tClass)
static <T> ModifyRequest<T> buildRequest(List<T> paramList)
static <T> ModifyRequest<T> buildRequest(List<?> paramList, Class<T> tClass)
MRPBuilder<T> param(T param)
MRPBuilder<T> paramList(List<T> paramList)
MRPBuilder<T> ids(Object... ids)
MRPBuilder<T> ids(List<?> idList)
@SafeVarargs final MRPBuilder<T> enableNullFields(EFunction<T, ?>... fields)
MRPBuilder<T> enableNullFields(String[] enableNullFields)
ModifyRequest<T> build()
```

### OBJBuilder

`public class OBJBuilder<T>`　Object对象封装构建

**方法**

```java
static <T> OBJBuilder<T> builder(T request)
static <T> OBJBuilder<T> builder(Class<T> tClass)
OBJBuilder<T> setFieldValue(EFunction<T, ?> field, Object Value)
T build()
```

### PRBuilder

`public record PRBuilder<T>(PageResult<T> result)`　PageResultBuilder 分页结果对象的构造器

**构造参数（record 组件）**

```java
PageResult<T> result
```

**方法**

```java
static <T> PRBuilder<T> builder()
static <T> PageResult<T> result(Long total, List<T> rows)
PRBuilder<T> total(Long total)  // 构建分页结果对象的总记录数
PRBuilder<T> rows(List<T> rows)  // 构建分页结果对象的分页数据信息
PRBuilder<T> pageData(Long total, List<T> rows)  // 构建分页结果对象的总记录数和分页数据信息
PageResult<T> build()  // 返回分页结果对象信息
```

### RRBuilder

`public class RRBuilder`　ResponseResultBuilder

**方法**

```java
static ResponseResult<?> buildFailByException(Exception e)
static <T> ResponseResult<T> buildBodyByBaseResult(BaseResult<T> result)
static <T> ResponseResult<List<T>> buildBodyByPageResult(PageResult<T> result)
static <T> ResponseResult<List<T>> buildSuccessListBody(List<T> data)
static <T> ResponseResult<T> buildSuccessBody()
static <T> ResponseResult<T> buildSuccessBody(T data)
static <T> ResponseResult<List<T>> buildSuccessPageBody(Long count, List<T> data)
static <T> ResponseResult<T> buildFailedBody()
static <T> ResponseResult<T> buildFailedBody(String msg)
static <T> ResponseResult<T> buildFailedBody(String code, String msg)
```

### SRPBuilder

`public class SRPBuilder<T>`　SearchRequestParamBuilder 查询类接口请求参数封装对象

**构造器**

```java
SRPBuilder(SearchRequest<T> request)
```

**方法**

```java
static <T> SRPBuilder<T> builder()
static <T> SRPBuilder<T> builder(SearchRequest<T> request)
static <T> SearchRequest<T> buildRequest(T example)
SRPBuilder<T> example(T example)
SRPBuilder<T> pageAndExample(PageSearch pageSearch, T example)
SRPBuilder<T> page(PageSearch pageSearchInfo)
@SafeVarargs final SRPBuilder<T> selectFields(EFunction<T, ?>... fields)
@SafeVarargs final SRPBuilder<T> nullFields(EFunction<T, ?>... fields)
@SafeVarargs final SRPBuilder<T> likeFields(EFunction<T, ?>... fields)
final SRPBuilder<T> in(EFunction<T, ?> field, List<?> values)
@SafeVarargs final SRPBuilder<T> notFields(EFunction<T, ?>... fields)
SearchRequest<T> build()
```

## 包 `com.mcst.easyfk.core.constants`

### CharacterConstant

`public interface CharacterConstant`

**字段 / 常量**

```java
String UNKNOWN = "unknown"
String UNDEFINED = "undefined"
String NULL = "null"
String HASH = "#"  // # 号
String STAR = "*"  // 星号
String JAR = "jar"
char UNDERLINE_CHAR = '_'  // 字符型下划线
String UNDERLINE_VARCHAR = "_"  // 字符串型下划线
String SLASH = "/"  // 正斜杠
String DOT = "."  // 点
String COMMA_DELIMITERS = ","  // 英文逗号分隔符
String STATIC_WITH = "/static/"
String[] STATIC_URL = {".css", ".js", ".ico", ".gif", ".html", ".htm", ".jpg", ".png", ".bmp", ".jpeg", ".swf", ".apk", ".tif", ".flv", ".svg", ".map", ".mp4", ".avi"}
String DATABASE_TYPE_MYSQL = "mysql"
String DATABASE_TYPE_MONGO = "mongo"
```

### FileType

`public enum FileType`

**枚举常量**

```java
IMAGE  // 图片
FILE  // 文件
VIDEO  // 音、视频
```

### RequestHeaderConstant

`public interface RequestHeaderConstant`

**字段 / 常量**

```java
String REQUEST_NONCE = "Request-Nonce"
String REQUEST_TOKEN = "Request-Token"
String ACCESS_TOKEN = "Access-Token"
String TIMESTAMP = "Timestamp"
String RESET_SIGN = "Reset-Sign"
String SIGN_VERSION = "Sign-Version"
String SIGN_BODY = "Sign-Body"
String APP_ID = "App-Id"
String API_TIMESTAMP = "Api-Timestamp"
String API_NONCE = "Api-Nonce"
String API_SIGN = "Api-Sign"
String API_BODY = "Api-Body"
String DEVICE_NO = "Device-No"
String CLIENT_TYPE = "Client-Type"
String LANGUAGE = "Language"
String TRACE_ID = "TRACE_ID"
```

### ReturnCodeConstant

`public interface ReturnCodeConstant`

**字段 / 常量**

```java
String SUCCESS = "OK"  // 处理成功
String ERROR = "ERROR"  // 处理失败
String UN_LOGIN = "UN_LOGIN"  // 未登录
String UN_AUTH = "UN_AUTH"  // 无权限
String PARAM_ERROR = "PARAM_ERROR"  // 参数错误
String BUSYNESS = "BUSYNESS"  // 系统繁忙
```

## 包 `com.mcst.easyfk.core.context`

### RequestHeaderContext

`public class RequestHeaderContext`

**方法**

```java
static RequestHeaders getRequestHeaders()
static void setRequestHeaders(RequestHeaders requestHeaders)
static void remove()
```

### TraceIdContext

`public class TraceIdContext`　链路追踪ID上下文管理器 提供线程级别的TraceId存储和管理功能，支持父子线程间的TraceId传递 使用InheritableThreadLocal确保子线程能够继承父线程的TraceId

**方法**

```java
static String getTraceId()  // 获取当前线程的TraceId
static void setTraceId(String traceId)  // 设置当前线程的TraceId TraceId会自动传递给子线程
static void remove()  // 清理当前线程的TraceId 建议在线程结束前调用此方法，防止内存泄漏
static void executeWithCleanup(Runnable runnable)  // 清理当前线程的TraceId并执行指定的操作 确保在操作完成后TraceId被正确清理
static boolean hasTraceId()  // 判断当前线程是否存在TraceId
static String getTraceIdOrDefault(String defaultValue)  // 获取当前线程的TraceId，如果不存在则返回默认值
static String getRequiredTraceId()  // 获取当前线程的非空TraceId
```

### UserDataContext

`public class UserDataContext`　登录上下文类，用于管理当前线程的登录用户信息。

**方法**

```java
static UserData getUserData()  // 获取当前线程的登录用户信息。
static void setUserData(UserData loginUser)  // 设置当前线程的登录用户信息。
static void remove()  // 移除当前线程的登录用户信息。
```

## 包 `com.mcst.easyfk.core.dto`

### BaseDto

`public class BaseDto implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)` `@NoArgsConstructor` `@AllArgsConstructor` `@SuperBuilder`　注解：`@SerializableClass`

**字段 / 常量**

```java
@Schema(description = "新增时间", hidden = true) LocalDateTime insertTime
@Schema(description = "最后更新时间", hidden = true) LocalDateTime lastUpdateTime
```

## 包 `com.mcst.easyfk.core.dto.login`

### LoginResult

`public class LoginResult implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)` `@NoArgsConstructor` `@AllArgsConstructor` `@Builder`　注解：`@SerializableClass`

**字段 / 常量**

```java
List<String> limits
String headImage
Boolean success  // 是否成功，true 表示成功
LoginUser loginUser
String msg
Map<String, Object> extendData  // 扩展数据
```

**构造器**

```java
LoginResult(LoginUser loginUser)
LoginResult(Boolean success, String msg)
```

### LoginUser

`public class LoginUser implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)` `@NoArgsConstructor` `@AllArgsConstructor` `@Builder`　注解：`@SerializableClass`

**字段 / 常量**

```java
String name  // 名称
String userType  // 用户类型 platform 后台管理系统用户 customer C端会员用户 agent 代理商用户 merchant 商户用户
String loginToken  // 登录缓存Token
```

### UserData

`public class UserData implements Serializable`　Lombok：`@Data` `@NoArgsConstructor` `@AllArgsConstructor` `@Builder` `@Accessors(chain = true)`　注解：`@SerializableClass`　当前登录用户信息，包括C端用户和后台管理系统用户

**字段 / 常量**

```java
String userId  // 用户ID
String accountId
String name  // 姓名
String phone  // 手机号
String type  // 类型 platform 后台管理系统用户 customer C端会员用户 agent 代理商用户 merchant 商户用户
String accountType  // 账号类型
String nickname  // 昵称
String avatar  // 头像
String thirdAccount  // 第三方账号
Integer thirdType  // （0：微信，1：QQ，2：微博）
String groupId  // 分组ID
String groupName  // 分组名称
String departmentId  // 部门ID
String departmentName  // 部门名称
String agentId  // 代理商ID
String agentName  // 代理商名称
String merchantId  // 商户ID
String merchantName  // 商户名称
String orgId  // 组织ID
String orgName  // 组织名称
Map<String, Object> extendData  // 扩展数据
Set<String> bizType  // 业务类型
String loginToken  // 登录令牌
```

## 包 `com.mcst.easyfk.core.dto.page`

### PageResult

`public class PageResult<T> implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)` `@NoArgsConstructor` `@AllArgsConstructor` `@Builder`　注解：`@SerializableClass`　分页查询结果集封装对象

**字段 / 常量**

```java
Long total  // 总记录数
List<T> rows  // 每页的数据
```

### PageSearch

`public class PageSearch implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)` `@NoArgsConstructor` `@AllArgsConstructor` `@Builder`　注解：`@SerializableClass` `@Schema(description = "分页查询数据封装对象")`

**字段 / 常量**

```java
@Schema(description = "当前页数", name = "page", requiredMode = Schema.RequiredMode.REQUIRED) Integer page
@Schema(description = "每页查询条数", name = "limit", requiredMode = Schema.RequiredMode.REQUIRED) Integer limit
@Schema(description = "是否查询总数", name = "totalCount", hidden = true) Boolean totalCount
```

**构造器**

```java
PageSearch(Integer page, Integer limit)
```

## 包 `com.mcst.easyfk.core.dto.request`

### BasicParam

`public class BasicParam implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)` `@NoArgsConstructor` `@AllArgsConstructor` `@SuperBuilder`　注解：`@SerializableClass`

**字段 / 常量**

```java
@AssistConditionField @Schema(description = "TOP", name = "top") Integer top  // TOP
@AssistConditionField @Schema(description = "当前页数", name = "page") Integer page  // 当前页数
@AssistConditionField @Schema(description = "查询条数", name = "limit") Integer limit  // 查询条数
@AssistConditionField @Schema(description = "是否查询总数", name = "totalCount") Boolean totalCount  // 是否查询总数
@AssistConditionField @Schema(description = "升序排序字段", name = "ascFields") String ascFields  // 升序排序字段
@AssistConditionField @Schema(description = "降序排序字段", name = "descFields") String descFields  // 降序排序字段
@AssistConditionField @Schema(description = "搜索关键字", name = "searchKeyWord") String searchKeyWord  // keyword
@AssistConditionField @Schema(description = "时序数据库范围起始", name = "start") String start
@AssistConditionField @Schema(description = "时序数据库范围截止", name = "stop") String stop
```

### BatchActionReq

`public class BatchActionReq<PK extends Serializable> extends BatchBasicReq<PK>`　Lombok：`@EqualsAndHashCode(callSuper = true)` `@Data` `@Accessors(chain = true)` `@NoArgsConstructor` `@AllArgsConstructor` `@SuperBuilder`　注解：`@SerializableClass`

**字段 / 常量**

```java
@Schema(description = "备注") String remark
```

### BatchBasicReq

`public class BatchBasicReq<PK extends Serializable> implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)` `@NoArgsConstructor` `@AllArgsConstructor` `@SuperBuilder`　注解：`@SerializableClass`

**字段 / 常量**

```java
@Schema(description = "对象ID，多个ID用逗号分隔", requiredMode = Schema.RequiredMode.REQUIRED) @NotNull(message = "ids不可为空") PK ids
```

### DisableActionParam

`public class DisableActionParam<T> implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)` `@NoArgsConstructor` `@AllArgsConstructor` `@Builder`　注解：`@SerializableClass`

**字段 / 常量**

```java
DisableFieldReq disableFieldReq
EFunction<T, ?> valueField  // 需禁用的字段
EFunction<T, ?> idField  // id字段
Class<T> tClass
```

**构造器**

```java
DisableActionParam(DisableFieldReq disableFieldReq)
```

### DisableFieldReq

`public class DisableFieldReq implements Serializable`　Lombok：`@Data` `@NoArgsConstructor` `@AllArgsConstructor` `@Builder` `@Accessors(chain = true)`　注解：`@SerializableClass`

**字段 / 常量**

```java
@NotBlank(message = "ids不可为空") @Schema(name = "ids", description = "ids") String ids  // ids
@NotNull(message = "value不可为空") @Schema(name = "value", description = "值") Integer value  // 值
```

### ModifyRequest

`public class ModifyRequest<T> implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)` `@NoArgsConstructor` `@AllArgsConstructor` `@Builder`　注解：`@SerializableClass`　操作类接口请求参数封装对象

**字段 / 常量**

```java
List<?> idList  // ID列表
T parmaObj  // 参数
List<T> paramList  // 列表类型参数
String[] enableNullFields  // 可以为空的字段
```

### RequestHeaders

`public class RequestHeaders implements Serializable`　Lombok：`@Data` `@NoArgsConstructor` `@AllArgsConstructor` `@Builder` `@Accessors(chain = true)`　注解：`@SerializableClass`

**字段 / 常量**

```java
@SignField String resetSign  // 重放签名
@SignField Long timestamp  // 时间戳
String language  // 语言
String accessToken  // 用户token类似session id
String loginToken  // 登录缓存token
String requestNonce  // 一次性随机字符数据，用于重放控制
String requestToken  // 请求token，用于控制表单重复提交验证
String deviceNo  // 客户端唯一设备号，一般用户APP客户端
String clientType  // 客户端类型，如IOS，Android，PC，MIN等
```

### SearchRequest

`public class SearchRequest<T> implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)` `@NoArgsConstructor` `@AllArgsConstructor` `@Builder`　注解：`@SerializableClass`　查询类接口请求参数封装对象

**字段 / 常量**

```java
T parmaObj
PageSearch pageSearch  // 分页对象
String[] selectFields  // 选择需要查询的字段
String[] nullFields  // 为空的字段
Map<String, List<?>> inParams  // in 条件字段
String[] likeFields  // 模糊 字段
String[] notFields  // 不等于字段
String[] gThanFields  // 大于 字段
String[] lThanFields  // 小于 字段
String[] gThanOrEqualFields  // 大于等于 字段
String[] lThanOrEqualFields  // 小于等于 字段
String[] multipleFields  // 多选字段
```

## 包 `com.mcst.easyfk.core.dto.response`

### BaseResult

`public class BaseResult<T> implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)` `@NoArgsConstructor` `@AllArgsConstructor` `@Builder`　注解：`@SerializableClass`

**字段 / 常量**

```java
Boolean success  // 是否成功，true 表示成功
T data
String msg
String code
```

### ResponseResult

`public class ResponseResult<T> implements Serializable`　Lombok：`@Data` `@NoArgsConstructor` `@AllArgsConstructor` `@Builder` `@Accessors(chain = true)`　注解：`@SerializableClass` `@Schema(description = "响应对象信息")`

**字段 / 常量**

```java
@Schema(description = "code信息，OK表示请求处理成功，UN_LOGIN表示登录过期，UN_AUTH表示无权限," + "PARAM_ERROR表示参数验证失败，BUSY表示服务器繁忙，ERROR" + "表示错误，具体错误信息为msg", name = "code") String code
@Schema(description = "总条数，分页查询时用到", name = "count") Long count
@Schema(description = "提示消息", name = "msg") String msg
@Schema(description = "数据信息，在请求失败情况下，data可能不返回", name = "data") T data
@Schema(description = "日志跟踪ID，用于日志查询，无实际业务意义", name = "traceId") String traceId
```

## 包 `com.mcst.easyfk.core.dto.validation`

### ValidationResult

`public class ValidationResult implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)`　注解：`@SerializableClass`

**字段 / 常量**

```java
boolean success  // 是否验证成功，true，表示成功
String message  // 错误信息
```

## 包 `com.mcst.easyfk.core.exception`

### BaseErrorEnum

`public interface BaseErrorEnum`

**方法**

```java
String getCode()  // 获取Code
void setCode(String code)  // 设置Code
String getMessage()  // 获取Message
void setMessage(String message)  // 设置Code
```

### BusinessException

`public class BusinessException extends RuntimeException`　Lombok：`@EqualsAndHashCode(callSuper = true)` `@Data` `@Accessors(chain = true)`　统一业务异常

**字段 / 常量**

```java
String errorCode  // 错误码，系统级别的错误码
String errorMsg  // 错误信息，系统级别的错误信息，用于错误排查
String i18nCode  // 国际化错误码
String msgPath  // 国际化消息配置文件路径
Object[] args  // 错误信息参数
```

**构造器**

```java
BusinessException(BaseErrorEnum errorEnum)
BusinessException(String errCode, String message)
BusinessException(String message)
BusinessException()
```

**方法**

```java
Throwable fillInStackTrace()
```

### ValidateException

`public class ValidateException extends RuntimeException`

**构造器**

```java
ValidateException()
ValidateException(String message)
```

## 包 `com.mcst.easyfk.core.function`

### EFunction

`public interface EFunction<T, R> extends Function<T, R>, Serializable`　注解：`@FunctionalInterface`

_无 public 成员。_

### FunctionExecutor

`public class FunctionExecutor`　函数执行器工具类，提供各种函数式编程的便捷方法 包括条件分支处理、空值检查、异常处理等功能

**方法**

```java
static void isTrueOrFalse(boolean b, Runnable trueFun, Runnable falseFun)  // 条件分支处理
static <T> void presentOrElse(T obj, Consumer<? super T> consumer, Runnable emptyFun)  // 空值与非空值分支处理
static <T> void emptyThrowFun(T obj, String message, String code, Consumer<T> consumer)  // 执行函数，值为空是抛出业务异常
static <T, R> R emptyThrowFun(Function<T, R> function, T obj, String message, String code)  // 执行函数，参数为空抛出业务异常
static <T, R> R emptyThrowFun(Function<T, R> function, T obj, String message, String code, Supplier<R> supplier)  // 执行函数，参数为空抛出业务异常
static <T, U, R> R emptyThrowFun(BiFunction<T, U, R> function, T obj, U u, String message, String code)  // 执行函数，参数为空抛出业务异常
static <T, U, R> R emptyThrowFun(BiFunction<T, U, R> function, T obj, U u, String message, String code, Supplier<R> supplier)  // 执行函数，参数为空抛出业务异常
static <T> void emptyThrowFun(T obj, String message, Consumer<T> consumer)  // 执行函数，值为空时抛出业务异常
static <T> void notEmptyFun(T obj, Consumer<T> consumer)  // 值不为空时才处理
static <T, R> R actionFun(Function<T, R> function, T obj, Supplier<R> supplier)  // 执行函数，如果参数为空或函数结果为null则返回默认值
static <T, U, R> R actionFun(BiFunction<T, U, R> function, T obj, U u, Supplier<R> supplier)  // 执行双参数函数，如果任一参数为空或函数结果为null则返回默认值
static <T> void isTrueFun(boolean value, T obj, Consumer<T> consumer)  // 条件为true时执行消费者函数
static <T> void predicate(T obj, Predicate<T> predicate, Consumer<T> consumer)  // 根据断言条件执行消费者函数
static void isTrueFun(boolean value, Runnable runnable)  // 条件为true时执行函数
```

### ThrowingSupplier

`public interface ThrowingSupplier<T, E extends Exception>`　注解：`@FunctionalInterface`

**方法**

```java
T get() throws E
```

## 包 `com.mcst.easyfk.core.utils.common`

### DisableUtil

`public class DisableUtil`

**方法**

```java
static <T> List<T> createObjListByDisableAction(DisableActionParam<T> disableActionParam)  // 根据禁用操作参数创建对象列表 该方法用于根据提供的禁用操作参数，创建一个对象列表，其中对象的指定字段被设置为禁用值 主要用于在用户界面的禁用操作中，根据用户选择的记录ID和禁用值，创建相应的对象实例
```

### EmptyUtil

`public class EmptyUtil`　对"空"的判断公共方法

**方法**

```java
static void emptyThrowException(Object value, String message)  // 值为空时抛出业务异常
static void emptyThrowException(Object value, String code, String message)  // 值为空时抛出业务异常
static <T> boolean isNotEmpty(Object value)  // 判断Object是否不为空,先判断是否不为null，为null返回false;不为null 继续判断toString()是否不为空
static <T> boolean isNotEmpty(List<T> lists)  // 判断list是否不为空
static <T> boolean isNotEmpty(T[] data)  // 判断数组是否不为空
static boolean isNotEmpty(String data)  // 判断字符串是否不为空
@SuppressWarnings("rawtypes") static boolean isNotEmpty(Map data)  // 判断Map是否不为空
static boolean isNotUndefinedChars(String value)  // 判断字符串不能为空，且不能为“undefined”，主要是在js选择后验证，可以调用此方法
static boolean isNotNullChars(String value)  // 判断字符串不能为空，且不能为“null”，主要是在js选择后验证，可以调用此方法
static boolean isNotEmptyChars(String value)  // 判断字符串不能为空，且不能为“null”和“undefined”，主要是在js选择后验证，可以调用此方法
static <T> boolean isEmpty(List<T> lists)  // 判断list是否为空
static <T> boolean isEmpty(T[] data)  // 判断数组是否为空
static boolean isEmpty(String data)  // 判断字符串是否为空
@SuppressWarnings("rawtypes") static boolean isEmpty(Map data)  // 判断Map是否为空
static boolean isUndefinedOrNull(String value)  // 判断字符串为空，或为“undefined”，主要是在js选择后验证，可以调用此方法
static boolean isNullChars(String value)  // 判断字符串为空，或为“null”，主要是在js选择后验证，可以调用此方法
static boolean isEmptyChars(String value)  // 判断字符串为空，或为“null”和“undefined”，主要是在js选择后验证，可以调用此方法
static boolean isEmpty(Object value)  // 判断Object是否为空,优化版本避免不必要的toString()调用
static boolean allFieldIsEmpty(Object obj)
```

### EnumUtils

`public class EnumUtils`　注解：`@SuppressWarnings("all")` `@Slf4j`　枚举工具类（JDK 21 优化版本） 提供高效的枚举查找和转换功能，支持MethodHandle缓存机制 使用现代Java特性提升性能和安全性

**方法**

```java
static <E extends Enum<?>> E valueOf(Class<E> enumClass, Object value, MethodHandle methodHandle)  // 值映射为枚举（JDK 21 优化版本，使用MethodHandle）
static <E extends Enum<?>> E valueOf(Class<E> enumClass, Object value, Method method)  // 值映射为枚举（向后兼容的Method版本）
static <E extends Enum<E>> E getEnumByValue(final Class<E> enumClass, Object value)  // 根据枚举值获取枚举（性能优化版本）
static <E extends Enum<E>> String getNameByValue(Class<E> enumClass, Object value)  // 根据枚举值获取枚举名称（性能优化版本）
static <E extends Enum<E>> String getNameByValue(Class<E> enumClass, Object value, String methodName)  // 根据枚举值获取指定方法的返回值（JDK 21 优化版本）
static <E extends Enum<E>> E getEnumByCode(final Class<E> enumClass, Object value)  // 根据code值获取enum对象（性能优化版本）
static <E extends Enum<E>> String getNameByCode(Class<E> enumClass, Object code)  // 根据code值获取枚举名称（性能优化版本）
static <E extends Enum<E>> String getNameByCode(Class<E> enumClass, Object code, String methodName)  // 根据code值获取指定方法的返回值（JDK 21 优化版本）
static <E extends Enum<E>> Object getValueByCode(Class<E> enumClass, Object code)  // 根据枚举code获取枚举值（JDK 21 优化版本）
static <E extends Enum<E>> E getEnumBySubCode(final Class<E> enumClass, Object value)  // 根据子code值获取enum对象（性能优化版本）
static <E extends Enum<E>> String getSubTextBySubCode(final Class<E> enumClass, Object value)  // 根据子code值获取子text（JDK 21 优化版本）
```

### Exception2ResultUtil

`public class Exception2ResultUtil`

**方法**

```java
static ResponseResult<?> createResponseByBizException(BusinessException e)
static BaseResult<?> createResultByBizException(BusinessException e)
```

### FunctionColumnToStringUtil

`public class FunctionColumnToStringUtil`　注解：`@Slf4j`　Lambda表达式转换成字符串 高性能实现，使用ConcurrentHashMap和WeakReference确保并发安全和内存效率

**方法**

```java
static <T> String columnToString(EFunction<T, ?> fn)  // 转换方法引用为属性名
static <T> String[] columnToString(EFunction<T, ?>[] fn)
static SerializedLambda getSerializedLambda(Serializable fn)  // 获取Lambda表达式的序列化形式 通过反射调用writeReplace方法获取SerializedLambda
static void clearCache()  // 清理缓存（用于测试或内存管理）
```

### I18NUtil

`public class I18NUtil`　国际化工具类 提供多语言消息获取和语言环境处理功能

**方法**

```java
static String getMessage(String code)  // 获取默认路径下的本地化消息
static String getMessage(String code, String path)  // 获取指定路径下的本地化消息
static String getMessage(String code, Object[] args)  // 获取默认路径下带参数的本地化消息
static String getMessage(String code, String path, Object[] args)  // 获取指定路径下带参数的本地化消息
static String getMessage(String code, Locale locale, String path, Object[] args)  // 获取指定语言环境下的本地化消息（核心方法）
static void clearCache()  // 清理缓存（可用于测试或内存管理）
static Locale getLocale()  // 获取当前请求的语言环境 从请求头中获取语言信息并转换为Locale对象
static Locale getLocale(String language)  // 根据语言字符串创建Locale对象 支持格式："zh"、"zh_CN"等
```

### MapStructConvertUtil

`public class MapStructConvertUtil`　注解：`@Slf4j` `@SuppressWarnings("unused")`　MapStruct转换工具类 提供高性能的对象转换功能，使用MapStruct进行转换 支持对象、列表、分页结果的转换 支持自定义转换逻辑 强烈建议使用MapStruct进行转换，性能更好，类型安全

**方法**

```java
static Converter getConverterOrNull()  // 获取转换器，不可用时返回 null Spring 容器尚未启动（或非 Spring 环境）时返回 null，容器启动后再次调用即可获取； 容器中没有 Converter Bean 时始终返回 null。
static boolean isAvailable()  // MapStruct-Plus 转换器当前是否可用
static Converter getConverter()  // 获取转换器
static <O, S> O convert(S source, Class<O> targetClass)
static <T> T convert(Map<String, Object> source, Class<T> targetClass)
static <T> T convert(Map<String, Object> map, Class<T> targetType, Consumer<T> beanConsumer)
static <S, T> List<T> convertList(List<S> sourceList, Class<T> targetClass)
static <S, T> PageResult<T> convertPage(PageResult<S> source, Class<T> targetClass)
static <S, T> T copyValue(S source, T target, String... forceNullFields)  // 对象值拷贝 (字符串反射版) 默认规则：源对象字段为 Null 时，不拷贝（保持目标对象原值）。 特殊规则：通过 forceNullFields 指定的字段，如果源对象中为 Null，则强制覆盖目标对象为 Null。
@SafeVarargs static <S, T> T copyValue(S source, T target, EFunction<T, ?>... forceNullFields)  // 对象值拷贝 (Lambda 无反射版) 默认规则：源对象字段为 Null 时，不拷贝（保持目标对象原值）。 特殊规则：通过 forceNullFields 指定的字段，如果源对象中为 Null…
static <S, T> T copyValue(S source, T target, BiConsumer<S, T> customHandler)  // 对象值拷贝 (Lambda 无反射版) 性能更好，类型安全。适用于编译期已知的特殊处理字段。
```

### MyBeanUtils

`public class MyBeanUtils extends BeanUtils`　反射的Utils函数集合.扩展自spring BeanUtils 不推荐使用，请使用 MapStructConvertUtil 进行高性能转换工具

**方法**

```java
static <T> T copyBean(Object ori, Class<T> cls)  // 从一个对象中拷贝属性值，该属性在两个对象中名称相同且类型也相同
static void copyPropertiesNotNull(Object source, Object target, String... ignoreProperties)  // 只拷贝源对象中值不为 null 的同名属性，目标对象对应属性保持原值
```

### OrderNoUtil

`public class OrderNoUtil`

**方法**

```java
static String get18OrderNumber(String prefix)  // 生成一个18位的订单号，基于给定的前缀。 这是一个重载函数，调用的是另一个带有布尔值参数的版本。
static String get18OrderNumber(String prefix, boolean upperCase)  // 生成一个18位的订单号，可选择是否将前缀转换为大写。
static String get22OrderNumber(String prefix)  // 生成22位订单号的同步方法。 这是一个简化的版本，调用了另一个带有额外参数的同名方法，将布尔值参数默认设置为true。
static String get22OrderNumber(String prefix, boolean upperCase)  // 生成一个带有前缀的22位订单号。
static String get27OrderNumber(String prefix)  // 生成27位订单号的同步方法。 这是一个简化的版本，调用了另一个带有额外参数的版本。
static String get27OrderNumber(String prefix, boolean upperCase)  // 生成带有前缀的27位订单编号。 如果提供的前缀非空，会根据upperCase参数决定是否将其转换为大写后，与生成的27位订单编号拼接。
static String get27OrderNumber()  // 生成一个27位的订单号：17位时间戳(yyyyMMddHHmmssSSS) + 5位毫秒内序列 + 5位随机数。 单 JVM 内唯一，每毫秒最多 100000 个，超出时借用下一毫秒。
static String get22OrderNumber()  // 生成一个22位的订单号：17位时间戳(yyyyMMddHHmmssSSS) + 5位毫秒内序列。 单 JVM 内唯一，每毫秒最多 100000 个，超出时借用下一毫秒。
static String get18OrderNumber()  // 生成一个18位的订单号：17位时间戳(yyyyMMddHHmmssSSS) + 1位毫秒内序列。 单 JVM 内唯一，每毫秒最多 10 个，超出时借用下一毫秒（高并发下时间部分会领先于真实时间）。
```

### ReflectUtil

`public class ReflectUtil`　注解：`@SuppressWarnings("all")`

**方法**

```java
static void clearAllCaches()  // 清理所有缓存，释放内存 建议在应用关闭或需要释放内存时调用
static void clearCacheForClass(Class<?> clazz)  // 清理指定类的相关缓存
static String getCacheStats()  // 获取缓存统计信息
static Field[] getFields(Object obj)  // 只获取本类的所有属性
static Field[] getFields(Class<?> clazz)  // 只获取本类的所有属性（使用缓存优化） 返回的是缓存数组本身，调用方不得修改其内容
static Field[] getAllFields(Object obj)  // 获取本类及所有父类的所有属性，不包括Object类的属性
static Field[] getAllFields(Class<?> clazz)  // 获取本类及所有父类的所有属性，不包括Object类的属性（使用缓存优化） 返回的是缓存数组本身，调用方不得修改其内容
static Field[] getAllFieldsByCutOff(Object obj, Class<?> cutOffClass)  // 获取本类及父类的所有属性，这个父类获取到指定的类（cutOffClass），不包括cutOffClass类的属性
static Field[] getAllFieldsByCutOff(Class<?> clazz, Class<?> cutOffClass)  // 获取本类及父类的所有属性，这个父类获取到指定的类（cutOffClass），不包括cutOffClass类的属性
static Field getFieldByFieldName(Object obj, String fieldName)  // 根据字段名获取属性，包含父类属性（使用缓存优化）
static Field getFieldByFieldName(Class<?> clazz, String fieldName)  // 根据字段名获取属性，包含父类属性（使用缓存优化） 子类与父类存在同名字段时返回子类字段
static Object getValueByFieldName(Object obj, String fieldName)  // 根据字段名获取字段值（使用缓存优化）
static Object getValueByField(Object obj, Field field)  // 根据字段对象获取字段值，调用方已持有 Field 时应优先使用此方法，避免再按名字查一次
static void setValueByFieldName(Object obj, String fieldName, Object value)  // 按字段名给对象赋值
static void setValueByField(Object obj, Field field, Object value)
static void setValueByFieldName(Object obj, Map<String, Object> valueMap) throws SecurityException, IllegalArgumentException, IllegalAccessException
static boolean hasField(Class<?> clazz, String fieldName)  // 判断一个类是否拥有某个属性字段（使用缓存优化）
static Object getValueByAnnotation(Object obj, Class<?> annotationClass)  // 根据一个注解获得一个类中标识这个注解的字段的值，只获取一个（使用缓存优化）
static String[] getFieldNameByAnnotation(Class<?> clazz, Class<?> annotationClass)
static Field[] getFieldsByAnnotation(Class<?> clazz, Class<?> annotationClass)
static Field[] getFieldsByAnnotation(Object obj, Class<?> annotationClass)
static Map<String, Object> getFieldAndValueByAnnotation(Object object, Class<?> annotationClass)
static Map<String, Object> getFieldAndValueByAnnotationNotNull(Object object, Class<?> annotationClass)  // 获取带有指定注解的字段名和非空值的映射（使用缓存优化）
static Class<?> getFieldTypeByAnnotation(Class<?> clazz, Class<?> annotationClass)
static Class<?> getFieldTypeByFieldName(Object obj, String fieldName)
static <T> T createInstance(Class<T> cls)
static <T> T createInstanceAndSetValue(Class<T> cls, Map<String, Object> valueMap)
static <T> T createInstanceAndSetValue(Class<T> cls, String fieldName, Object value)
```

### SplitUtil

`public class SplitUtil`　字符串分割工具类（性能优化版本） 提供高效的字符串分割和类型转换功能

**方法**

```java
static List<String> split(String value)  // 字符串分割 - 使用默认分隔符（英文逗号、中文逗号、空格、斜杠） 自动去除分割后为空的字符串和前后空格
static <T> List<T> splitAndConvert(String value, Class<T> clazz)  // 字符串分割并转换为指定类型（性能优化版本）
static <T> List<T> splitAndConvert(String value, Class<T> clazz, String... separators)  // 字符串分割并转换为指定类型 - 自定义分隔符（性能优化版本）
static List<String> split(String value, String... separators)  // 字符串分割 - 自定义分隔符（性能优化版本） 根据指定分隔符进行分割，自动去除分割后为空的字符串和前后空格
```

### StringUtil

`public class StringUtil extends StringUtils`　注解：`@Slf4j` `@SuppressWarnings("all")`　字符串处理工具类（性能优化版本） 继承自Spring StringUtils，提供额外的字符串处理功能

**方法**

```java
static String upperFirstChar(String str)  // 把字符串第一个字母转成大写（性能优化版本）
static String lowerFirstChar(String str)  // 把字符串第一个字母转成小写（性能优化版本）
static String underlineToCamel(String param)  // 下划线转驼峰（性能优化版本，支持缓存）
static String camelToUnderline(String param)  // 驼峰格式字符串转换为下划线格式字符串（性能优化版本，支持缓存）
static boolean isChinese(String strName)  // 完整的判断中文汉字和符号（内存优化版本）
```

### TransformUtil

`public class TransformUtil`　注解：`@Slf4j`　统一对象转换工具类 优先使用MapStruct进行转换，如果不支持或转换器不可用（非 Spring 环境、容器未启动），则使用Bean拷贝进行转换

**方法**

```java
static <T> List<T> transformList(List<?> sourceList, Class<T> tClass)  // 使用Stream和Bean拷贝进行列表转换
static <T> T transformObj(Object obj, Class<T> tClass)  // 单对象Bean拷贝转换
static <T, P> PageResult<T> transformPageResult(PageResult<P> source, Class<T> tClass)  // 分页结果转换
static Map<String, Object> transformToMap(Object obj)  // 对象转Map 使用hutool BeanUtil进行转换
static <T> T transformFromMap(Map<String, Object> map, Class<T> tClass)  // Map转对象 优先使用MapStruct进行转换，如果转换失败，则使用hutool BeanUtil进行转换
```

## 包 `com.mcst.easyfk.core.utils.date`

### LocalDateUtil

`public class LocalDateUtil`

**字段 / 常量**

```java
static final DateTimeFormatter TIME_FORMATTER = DateTimeFormatter.ofPattern("HH:mm:ss")
static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd")
static final DateTimeFormatter DATETIME_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
```

**方法**

```java
static LocalTime getLocalTime()  // 获取当前系统时间
static LocalDate getLocalDate()  // 获取当前系统日期
static LocalDateTime getLocalDateTime()  // 获取当前系统日期时间
static String getLocalTimeString()  // 获取当前系统时间字符串
static String getLocalDateString()  // 获取当前系统日期字符串
static String getLocalDateTimeString()  // 获取当前系统日期时间字符串
static String localDateToString(LocalDate date)
static String localDateTimeToString(LocalDateTime date)
static LocalTime string2LocalTime(String time)  // 字符串转LocalTime
static LocalDate string2LocalDate(String date)  // 字符串转LocalDate
static LocalDateTime string2LocalDateTime(String dateTime)  // 字符串转LocalDateTime
static LocalDateTime date2LocalDateTime(Date date)  // Date转LocalDateTime
static LocalDate date2LocalDate(Date date)  // Date转LocalDate
static LocalTime date2LocalTime(Date date)  // Date转LocalDate
static Date localDateTime2Date(LocalDateTime localDateTime)  // LocalDateTime转换为Date
static boolean between(String start, String end)  // 当前时间是否在指定区间内
static LocalDateTime dayStartTime(LocalDate date)  // 一天开始时间
static LocalDateTime dayEndTime(LocalDate date)  // 一天结束时间
static LocalDate firstDayOfWeek(LocalDate date)  // 获取指定日期的周一日期
static LocalDate lastDayOfWeek(LocalDate date)  // 获取指定日期的周日日期
static LocalDate firstDayOfMonth(LocalDate date)  // 获取指定日期所在月的第一天
static LocalDate lastDayOfMonth(LocalDate date)  // 获取指定日期所在月的最后一天
static int getIntervalDays(LocalDate startDate, LocalDate endDate)  // 获取两个日期相差的天数 绝对值
static boolean isLocalDate(String str)
static boolean isLocalDateTime(String str)
```

## 包 `com.mcst.easyfk.core.utils.expression`

### ExpressionUtil

`public class ExpressionUtil`　SpEL表达式解析工具类 提供基于Spring Expression Language的表达式解析功能，支持高性能缓存优化

**方法**

```java
static String parse(String key, Method method, Object[] args)  // 解析SpEL表达式并返回字符串结果
static <T> T parse(String key, Method method, Object[] args, Class<T> resultType)  // 解析SpEL表达式并返回指定类型的结果
static void clearCache()  // 清理缓存（用于测试或内存管理）
```

## 包 `com.mcst.easyfk.core.utils.returns`

### ReturnErrorUtil

`public class ReturnErrorUtil`

**方法**

```java
static Object returnError(Class<?> returnType, String errorCode, String errorMsg)
```
