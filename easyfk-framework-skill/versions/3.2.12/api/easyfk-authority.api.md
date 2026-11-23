# easyfk-authority API 签名速查（easyfk 3.2.12）

> 坐标：`com.mcst:easyfk-authority`　源码：`easyfk-base/easyfk-authority`
> 由 `scripts/gen-api.py` 从 21 个源文件自动提取，共 21 个类型、46 个方法/构造器、72 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-authority-skill.md](../modules/easyfk-authority-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 配置项（@ConfigurationProperties）

### `easyfk.config.login` ← LoginCacheProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `cache-type` | `String` | `"database"` | 缓存类型,redis,database(普通数据库，如mysql/postgresql等) 默认database |
| `live-time` | `Integer` | `2 * 60` | 缓存时间，单位分钟，默认2小时 |


## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `easyfk-authority` | `com.mcst.easyfk.authority.config.UserAuthConfigure` |

## 类型索引

- `com.mcst.easyfk.authority`：[IAuthResourceApi](#iauthresourceapi)、[IRefreshUserLoginRecord](#irefreshuserloginrecord)
- `com.mcst.easyfk.authority.annotation`：[AuthResource](#authresource)、[LoginResource](#loginresource)、[ResourceController](#resourcecontroller)
- `com.mcst.easyfk.authority.config`：[UserAuthConfigure](#userauthconfigure)
- `com.mcst.easyfk.authority.constant`：[ResourceSecurityLevel](#resourcesecuritylevel)
- `com.mcst.easyfk.authority.dto`：[AuthResourceDto](#authresourcedto)
- `com.mcst.easyfk.authority.enums`：[ResourceCategory](#resourcecategory)、[UserTypeEnum](#usertypeenum)
- `com.mcst.easyfk.authority.manager`：[RedisUserDataManagerImpl](#redisuserdatamanagerimpl)、[UserDataManager](#userdatamanager)
- `com.mcst.easyfk.authority.param`：[AuthResourceParam](#authresourceparam)
- `com.mcst.easyfk.authority.properties`：[LoginCacheProperties](#logincacheproperties)
- `com.mcst.easyfk.authority.request`：[AuthResourceReq](#authresourcereq)
- `com.mcst.easyfk.authority.response`：[AuthResourceResp](#authresourceresp)
- `com.mcst.easyfk.authority.vo`：[RefreshUserLoginVo](#refreshuserloginvo)、[RoleListVo](#rolelistvo)、[TreeNode](#treenode)、[UserAuth](#userauth)、[UserAuthResources](#userauthresources)

## 包 `com.mcst.easyfk.authority`

### IAuthResourceApi

`public interface IAuthResourceApi extends IBaseApi<AuthResourceResp, String, AuthResourceReq>`

**方法**

```java
ResponseResult<List<AuthResourceResp>> authorityResourceList()  // 权限资源列表数据,获取系统所有权限类型的资源
ResourceSecurityLevel checkUriSecurityLevel(String url)  // 检查当前url 的访问权限
void saveResourceByBath(List<AuthResourceReq> list)  // 批量添加
List<AuthResourceResp> getPlatformAuthResources(String type, Integer defaultStatus)  // 获取平台端资源
```

### IRefreshUserLoginRecord

`public interface IRefreshUserLoginRecord`　刷新用户登录记录过期时间接口

**方法**

```java
void refreshUserLoginRecord(RefreshUserLoginVo refreshUserLoginVo)  // 刷新用户登录记录过期时间
```

## 包 `com.mcst.easyfk.authority.annotation`

### AuthResource

`public @interface AuthResource`　注解：`@Target({ElementType.METHOD, ElementType.TYPE})` `@Retention(RetentionPolicy.RUNTIME)`

**方法**

```java
String id()
String pId() default ""
String name()  // 资源名称
String title() default ""  // 资源名称简写，用于权限分配页面展示
String actionCode() default ""  // 功能Code
int rootStatus() default 0  // 是否是跟目录
String pName() default ""  // 上级资源名称
ResourceCategory category() default ResourceCategory.menu  // 资源类型，menu 菜单，action 功能
int sort() default 0
String path() default ""  // 前端页面路径
String remark() default ""
String icon() default ""  // icon信息
String unPassMsg() default ""  // 无权限时的提示
String typeFlag() default "all"  // 类型标识 例如：system等，表示该资源属于系统/企业等，用于处理各个平台端资源归类
String defaultFlag() default "all"  // 默认类型 system /labor等，表示该资源是否是系统/企业等各平台端的默认资源
```

### LoginResource

`public @interface LoginResource`　注解：`@Target({ElementType.METHOD})` `@Retention(RetentionPolicy.RUNTIME)`　需要登录才能访问注解

**方法**

```java
String value() default ""
```

### ResourceController

`public @interface ResourceController`　注解：`@Target({ElementType.TYPE})` `@Retention(RetentionPolicy.RUNTIME)`　资源Controller 注解

**方法**

```java
String group() default "default"  // 组标识，作用是初始化时可以针对组进行初始化，实现增量初始化
String id() default ""
String name() default ""  // 资源名称
String title() default ""
String path() default ""  // 前端页面路径
int sort() default 0
String remark() default ""
String icon() default ""  // icon信息
String typeFlag() default "all"  // 类型标识 例如：all所有/system等，表示该资源属于系统/企业等，用于处理各个平台端资源归类
```

## 包 `com.mcst.easyfk.authority.config`

### UserAuthConfigure

`public class UserAuthConfigure`　注解：`@AutoConfiguration` `@EnableConfigurationProperties(LoginCacheProperties.class)`

**方法**

```java
@Bean @ConditionalOnMissingBean(UserDataManager.class) @ConditionalOnProperty(name = "easyfk.config.login.cache-type", havingValue = "redis") UserDataManager userAuthManager()
```

## 包 `com.mcst.easyfk.authority.constant`

### ResourceSecurityLevel

`public enum ResourceSecurityLevel`

**枚举常量**

```java
LOGIN  // 需要登录
AUTHORITY  // 需要权限
UNIMPEDED  // 过滤不拦截
```

## 包 `com.mcst.easyfk.authority.dto`

### AuthResourceDto

`public class AuthResourceDto implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)` `@NoArgsConstructor` `@SuperBuilder`　注解：`@AutoMapper(target = AuthResourceResp.class)`

**字段 / 常量**

```java
@PrimaryKey String resourceId
String name  // 名称
String icon  // icon
String url  // 资源URL
String pid  // 父资源ID
String pname  // 父资源名称
String title  // 标题
String category  // 资源类型，menu 菜单，action 功能
String remark  // 备注
Integer sort  // 排序
String path  // 前端路由地址
String actionCode  // 资源路径
String unPassMsg  // 无权限时的提示
Integer resourceLevel  // 资源等级，0：无需验证，1：需要登录，2：需要权限
Integer rootStatus  // 根目录标识，0：否，1：是
String groupCode  // 分组
String typeFlag  // 类型标识 例如：all所有/system等，表示该资源属于系统/企业等，用于处理各个平台端资源归类
String defaultFlag  // 默认类型 all所有/system/labor等，表示该资源是否是系统/企业等各平台端的默认资源
```

## 包 `com.mcst.easyfk.authority.enums`

### ResourceCategory

`public enum ResourceCategory`

**枚举常量**

```java
menu  // 菜单
action  // 功能
normal  // 普通
```

### UserTypeEnum

`public enum UserTypeEnum`

**枚举常量**

```java
Platform("platform")  // 平台用户
Agent("agent")  // 代理商
Merchant("merchant")  // 商户
Customer("customer")  // C端会员用户
```

**字段 / 常量**

```java
@Getter final String value
```

**构造器**

```java
UserTypeEnum(String value)
```

## 包 `com.mcst.easyfk.authority.manager`

### RedisUserDataManagerImpl

`public class RedisUserDataManagerImpl implements UserDataManager`　注解：`@Slf4j` `@SuppressWarnings("unused")`　用户数据管理器实现类

**方法**

```java
BaseResult<?> loginOut(UserData userData)
BaseResult<Boolean> checkAuth(String loginToken, String path)  // 校验结果：success 恒为 true（缓存异常直接抛出），data 表示是否有权限；没有权限数据视为无权限（data=false）
void refreshUserToken(LoginUser loginUser)
UserAuth getUserAuth(String loginToken)
BaseResult<String> cacheLoginData(UserData userData, UserAuth userAuth)
UserData getUserData(LoginUser loginUser)
BaseResult<?> offLineUser(String userId, String type)
```

### UserDataManager

`public interface UserDataManager`　用户数据管理器接口

**方法**

```java
BaseResult<?> loginOut(UserData userData)  // 退出登录时清除 UserAuth 缓存
BaseResult<Boolean> checkAuth(String loginToken, String path)  // 检测权限
void refreshUserToken(LoginUser loginUser)  // 刷新用户权限缓存时间
UserAuth getUserAuth(String loginToken)  // 获取当前用户 UserAuth
BaseResult<String> cacheLoginData(UserData userData, UserAuth userAuth)  // 缓存登录数据
UserData getUserData(LoginUser loginUser)  // 获取用户数据
BaseResult<?> offLineUser(String userId, String type)  // 强制下线用户
```

## 包 `com.mcst.easyfk.authority.param`

### AuthResourceParam

`public class AuthResourceParam extends BasicParam`　Lombok：`@Data` `@Accessors(chain = true)` `@EqualsAndHashCode(callSuper = true)` `@NoArgsConstructor` `@SuperBuilder`

**字段 / 常量**

```java
@PrimaryKey String resourceId
String name  // 名称
String icon  // icon
String url  // 资源URL
String pid  // 父资源ID
String pname  // 父资源名称
String title  // 标题
String category  // 资源类型，menu 菜单，action 功能
String remark  // 备注
Integer sort  // 排序
String path  // 前端路由地址
String actionCode  // 资源路径
String unPassMsg  // 无权限时的提示
Integer resourceLevel  // 资源等级，0：无需验证，1：需要登录，2：需要权限
Integer rootStatus  // 根目录标识，0：否，1：是
String groupCode  // 分组
String typeFlag  // 类型标识 例如：all所有/system等，表示该资源属于系统/企业等，用于处理各个平台端资源归类
String defaultFlag  // 默认类型 all所有/system/labor等，表示该资源是否是系统/企业等各平台端的默认资源
```

## 包 `com.mcst.easyfk.authority.properties`

### LoginCacheProperties

`public class LoginCacheProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.login")`

**字段 / 常量**

```java
String cacheType = "database"  // 缓存类型,redis,database(普通数据库，如mysql/postgresql等) 默认database
Integer liveTime = 2 * 60  // 缓存时间，单位分钟，默认2小时
```

## 包 `com.mcst.easyfk.authority.request`

### AuthResourceReq

`public class AuthResourceReq extends AuthResourceParam`　Lombok：`@Data` `@Accessors(chain = true)` `@EqualsAndHashCode(callSuper = true)` `@NoArgsConstructor` `@SuperBuilder`　注解：`@AutoMapper(target = AuthResourceDto.class)`

_无 public 成员。_

## 包 `com.mcst.easyfk.authority.response`

### AuthResourceResp

`public class AuthResourceResp extends AuthResourceDto`　Lombok：`@Data` `@Accessors(chain = true)` `@EqualsAndHashCode(callSuper = true)` `@NoArgsConstructor` `@SuperBuilder`

_无 public 成员。_

## 包 `com.mcst.easyfk.authority.vo`

### RefreshUserLoginVo

`public class RefreshUserLoginVo implements Serializable`　Lombok：`@Data` `@Builder` `@AllArgsConstructor` `@NoArgsConstructor`

**字段 / 常量**

```java
String loginToke  // 登录令牌
LocalDateTime expireTime  // 新的过期时间
```

### RoleListVo

`public class RoleListVo extends BaseDto`　Lombok：`@Data` `@EqualsAndHashCode(callSuper = true)` `@Accessors(chain = true)`

**字段 / 常量**

```java
String name  // 名称
Integer status  // 状态，0：启用，1：禁用
String type  // 扩展类型
String limits  // 权限信息
```

### TreeNode

`public class TreeNode implements Serializable`　Lombok：`@Data` `@NoArgsConstructor` `@Accessors(chain = true)`

**字段 / 常量**

```java
List<TreeNode> children
String title
String id
String href
boolean checked
boolean spread
```

### UserAuth

`public class UserAuth implements Serializable`　Lombok：`@Data` `@Accessors(chain = true)` `@NoArgsConstructor()`　Bms 用户权限数据缓存对象

**字段 / 常量**

```java
Boolean supperUser = Boolean.FALSE  // 超级管理员
List<AuthResourceDto> resources
List<String> urls
```

### UserAuthResources

`public class UserAuthResources implements Serializable`　Lombok：`@Data` `@NoArgsConstructor` `@Accessors(chain = true)`

**字段 / 常量**

```java
String resourceId
String name
String title
String icon
String path
List<String> actions
List<UserAuthResources> children
Integer sort
```
