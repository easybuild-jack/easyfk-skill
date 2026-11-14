# easyfk-authority Skill 参考文档

> 所属项目：`easyfk-base`　模块：`easyfk-authority`（单模块）
> 坐标：`com.mcst:easyfk-authority:3.2.12`
> 依据：全部源码（21 个文件），对齐 `auth开发文档.md`、`auth模块特点.md`、`核心模块说明.md` §5.5，并核对了框架内的调用方：web-base `ContextDataManager`、web-prd `LocalInterceptor`、gateway `RequestGatewayFilter`。
> 以源码为准；差异见文末「复查记录」。

---

## 1. 模块定位

权限体系的基础层，提供以下内容：

- 权限资源注解：`@ResourceController`、`@AuthResource`、`@LoginResource`；
- 资源模型：`AuthResourceDto/Param/Req/Resp`、`UserAuth`、`UserAuthResources`、`TreeNode`、`RoleListVo`；
- 登录态与权限缓存：`UserDataManager` 接口，以及基于 `ICacheService` 的 `RedisUserDataManagerImpl`；
- 契约接口：`IAuthResourceApi`（权限资源服务，由业务方实现）、`IRefreshUserLoginRecord`（续期回调，由业务方实现）。

本模块**不包含**以下内容：注解扫描入库、拦截器（由 web-prd 的 `LocalInterceptor` 和 gateway 的 `RequestGatewayFilter` 负责）、资源持久化。

依赖关系：

| 依赖 | 方式 | 说明 |
|---|---|---|
| `easyfk-core` | `compileOnly` | |
| `easyfk-cache` | `api` | |
| `service-api` | `api` | |
| `caffeine` | `api` | 用于本地的续期节流缓存 |

---

## 2. 自动配置与开关

`AutoConfiguration.imports` 中声明了 `UserAuthConfigure`，它绑定配置类 `LoginCacheProperties`：

```yaml
easyfk:
  config:
    login:
      cache-type: redis     # 默认 database。只有取值为 redis 时才注册 UserDataManager
      live-time: 120        # 登录缓存时长（分钟），默认 120
```

| Bean | 条件 |
|---|---|
| `userAuthManager`（`RedisUserDataManagerImpl`） | `easyfk.config.login.cache-type=redis` 且容器中没有其他 `UserDataManager`（`@ConditionalOnMissingBean(UserDataManager.class)`） |

- 默认情况下（`database`），**容器中没有 `UserDataManager`**（除非业务自行注册）：
  - web-base 的 `ContextDataManager` 会跳过加载 UserData 和续期；
  - web-prd 的 `LocalInterceptor`（`ObjectProvider` 获取）对 `@AuthResource` 接口返回 HTTP 500「权限服务未配置」并记 ERROR 日志；
  - gateway 的 `RequestGatewayFilter`（`required=false` 注入）对 AUTHORITY 级资源判空后拒绝（`UNAUTH`）。
- 需要登录鉴权的服务，必须配置 `cache-type: redis` 并提供 `ICacheService`（引入 `cache-redis`），或者自行注册一个 `UserDataManager` Bean。
- 自定义实现直接注册 `UserDataManager` Bean 即可，默认实现会自动让位（无论 `cache-type` 取值）。

---

## 3. UserDataManager（登录态 / 权限缓存）

```java
public interface UserDataManager {
    BaseResult<String>  cacheLoginData(UserData userData, UserAuth userAuth); // 登录：生成 token 并缓存
    UserData            getUserData(LoginUser loginUser);
    UserAuth            getUserAuth(String loginToken);
    BaseResult<Boolean> checkAuth(String loginToken, String path);
    void                refreshUserToken(LoginUser loginUser);                // 滑动续期
    BaseResult<?>       loginOut(UserData userData);                          // 退出当前 token
    BaseResult<?>       offLineUser(String userId, String type);              // 踢掉该用户的所有 token
}
```

`RedisUserDataManagerImpl` 的行为：

| 缓存空间（ICacheService namespace） | key | value |
|---|---|---|
| `User_Data` | loginToken | `UserData` |
| `User_Auth` | loginToken | `UserAuth` |
| `User_Data_Token` | `{type}_{userId}` | `Set<String>`，该用户所有的 token |
| `User_Data_Token_Lock` | `{type}_{userId}` | 随机串，token 集合读改写锁（TTL 5 秒） |

- **cacheLoginData**：
  1. 生成 `IdUtil.fastSimpleUUID()` 作为 loginToken，并写回 `userData.loginToken`；
  2. 写入 `User_Data`；如果传入了 userAuth，再写入 `User_Auth`。写 `User_Auth` 失败时回滚 `User_Data`；
  3. 把 token 追加到该用户的 token 集合中；追加失败（获取集合锁超时）时回滚 `User_Data`/`User_Auth` 并返回 `success=false`，保证登记过的会话都能被 `offLineUser` 踢出。
  - 返回值的 `data` 就是 loginToken。
  - 业务登录接口通常随后调用 `JwtManager.createJwtByObject(LoginUser)` 生成 JWT，其中 LoginUser 的 `loginToken` 字段就是这个 token。
- **token 集合并发控制**：所有读改写（登录追加、续期刷新 TTL、退出移除、`offLineUser` 清空）都在用户级锁内执行。锁通过 `ICacheService.setIfAbsent` 写入 `User_Data_Token_Lock::{type}_{userId}`（TTL 5 秒，值为随机串），最多重试 50 次、间隔 20ms；释放时校验值相同才删除。锁的原子性依赖缓存实现覆盖原子 `setIfAbsent`（cache-redis 为 SET NX EX；`ICacheService` 默认实现非原子）。
- **checkAuth(token, path)**：

  | 情况 | 返回 |
  |---|---|
  | token 为空或没有 `UserAuth` | `success=true, data=false`（视为无权限） |
  | `supperUser=true` | `success=true, data=true` |
  | 普通用户 | `success=true`，`data` 为 `urls` 非空且 `urls.contains(path)` 的结果 |

  - `success=false` 不再用于表示"无权限"；缓存异常直接抛出，由调用方按拒绝处理。
  - 路径匹配是**精确字符串匹配**，不支持通配符或路径变量。
  - `supperUser`、`urls` 为 null 时按 false / 空列表处理，不会 NPE。
- **refreshUserToken（滑动续期）**：
  1. 先用本地 Caffeine 缓存节流，在下次检查时间之前直接返回。这个缓存按实例生效，最多 10 万条，写入后 1 天过期。
  2. 当 `User_Data` 的剩余 TTL 在 (0, 600] 秒之间时：
     - 把 `User_Data`、`User_Auth` **重置为从当前时间起 live-time 分钟后过期**；
     - 刷新 token 集合的 TTL；
     - 存在 `IRefreshUserLoginRecord` Bean 时回调 `refreshUserLoginRecord(RefreshUserLoginVo{loginToke, expireTime})`。
  - web-base 的 `ContextDataManager` 在每次请求解析 JWT 后调用它；存在 `asyncTaskExecutor` 时会异步执行。
- **IRefreshUserLoginRecord 是可选的**：通过 `ObjectProvider` 获取，没有实现 Bean 时只跳过回调，`User_Data`、`User_Auth` 和 token 集合照常续期。需要记录登录续期（例如登录日志表）时再注册实现。
- **loginOut / offLineUser**：删除 `User_Auth`、`User_Data` 和本地节流记录，并在锁内维护 token 集合。`offLineUser` 获取锁超时返回 `success=false`（未踢出，调用方应重试）。

```java
@Component
public class LoginRecordRefresher implements IRefreshUserLoginRecord {
    @Override public void refreshUserLoginRecord(RefreshUserLoginVo vo) { /* 更新登录记录过期时间 */ }
}
```

---

## 4. 权限资源注解

注解本身**只是声明**，扫描和入库由业务方（权限中心）实现。实现者通过 `IAuthResourceApi.saveResourceByBath` 写入资源，再由拦截器根据 `checkUriSecurityLevel` 和 `checkAuth` 执行校验。

| 注解 | 目标 | 关键属性（默认值） |
|---|---|---|
| `@ResourceController` | 类 | `group("default")`、`id`、`name`、`title`、`path`、`sort(0)`、`remark`、`icon`、`typeFlag("all")` |
| `@AuthResource` | 方法 / 类 | **`id`、`name` 为必填**；`pId`、`pName`、`title`、`actionCode`、`category(menu)`、`rootStatus(0)`、`sort`、`path`、`remark`、`icon`、`unPassMsg`、`typeFlag("all")`、`defaultFlag("all")` |
| `@LoginResource` | 方法 | `value("")`，表示只要登录即可访问 |

```java
@ResourceController(id = "user-mgmt", name = "用户管理", path = "/system/user", typeFlag = "system")
@RestController
@RequestMapping("/api/user")
public class UserController {

    @AuthResource(id = "user-add", name = "新增用户", pId = "user-mgmt",
                  category = ResourceCategory.action, actionCode = "user:add")
    @PostMapping("/add")
    public BaseResult<?> add(@RequestBody ModifyRequest<UserReq> req) { ... }

    @LoginResource
    @GetMapping("/profile")
    public BaseResult<UserResp> profile() { ... }
}
```

枚举：

| 枚举 | 取值 |
|---|---|
| `ResourceCategory` | `menu` / `action` / `normal` |
| `ResourceSecurityLevel` | `LOGIN` / `AUTHORITY` / `UNIMPEDED` |
| `UserTypeEnum` | `Platform("platform")` / `Agent("agent")` / `Merchant("merchant")` / `Customer("customer")` |

`AuthResourceDto.resourceLevel` 的取值约定：0 表示不需要验证，1 表示需要登录，2 表示需要权限。

---

## 5. IAuthResourceApi（由业务方实现）

```java
public interface IAuthResourceApi extends IBaseApi<AuthResourceResp, String, AuthResourceReq> {
    ResponseResult<List<AuthResourceResp>> authorityResourceList();
    ResourceSecurityLevel checkUriSecurityLevel(String url);
    void saveResourceByBath(List<AuthResourceReq> list);
    List<AuthResourceResp> getPlatformAuthResources(String type, Integer defaultStatus);
}
```

- 数据模型的继承关系：`AuthResourceReq extends AuthResourceParam extends BasicParam`；`AuthResourceResp extends AuthResourceDto`。
- 对象转换由 mapstruct-plus 的 `@AutoMapper` 完成：`Req` 转为 `Dto`，`Dto` 转为 `Resp`。
- 主键是 `resourceId`，标注了 `@PrimaryKey`。

---

## 6. 与其他模块的关系

- **web-base `ContextDataManager`**：解析 JWT 得到 LoginUser，再通过 `getUserData` 写入 `UserDataContext`，并触发 `refreshUserToken`。
- **service-base `UserDataFiltrationUtil`**：根据 `UserData.type` 判断 SaaS 过滤，Platform 和 Customer 类型不做过滤（使用 `UserTypeEnum`）。
- **web-prd `LocalInterceptor`、gateway `RequestGatewayFilter`**：调用 `getUserAuth` 和 `checkAuth` 进行鉴权。

---

## 7. 生成代码时的规则

**应该这样做：**

- 需要登录态的服务，配置 `easyfk.config.login.cache-type: redis`，同时引入 `cache-redis`；需要续期记录时注册 `IRefreshUserLoginRecord`（可选）。
- 自定义登录态存储时直接注册 `UserDataManager` Bean，默认实现自动让位。
- 判断权限只看 `checkAuth` 的 `data`（`success=true` 恒成立）；调用方仍建议按"非 `success=true && data=true` 即拒绝"处理。
- 登录接口的流程为：组装 `UserData`（必须包含 userId、type）和 `UserAuth`（必须包含 urls 与 supperUser），调用 `cacheLoginData`，拿到 token 后放入 `LoginUser.loginToken`，再签发 JWT。
- 权限 URL 使用与请求 URI 完全一致的字符串。
- `@AuthResource` 必须写 `id` 和 `name`，`id` 应全局唯一。

**不要这样做：**

- 不要使用 `easyfk.config.auth.live-time`（这个前缀不存在），正确的是 `easyfk.config.login.live-time`。
- 不要在使用 `RedisUserDataManagerImpl` 时搭配非原子 `setIfAbsent` 的自定义 `ICacheService`（token 集合锁会失效）。
- 不要把注解当作已经生效的拦截，注解本身不做任何校验。
- 不要在 `urls` 中写通配符。

---

## 8. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | 开发文档 §8.1 | `easyfk.config.auth.live-time` | 配置前缀是 `easyfk.config.login`，属性有 `live-time`（默认 120）和 `cache-type`（默认 `database`） |
| 2 | 开发文档 §3、§8.2，特点 §2.6 | 存在 `AuthProperties`；`UserDataManager` 在 `@ConditionalOnMissingBean` 条件下自动注册，开箱即用 | 实际类名是 `LoginCacheProperties`。只有 `cache-type=redis` 时才注册，且没有 `@ConditionalOnMissingBean`。默认不注册 **已修复**：默认实现增加 `@ConditionalOnMissingBean(UserDataManager.class)`，业务自定义 Bean 会替换它（仍需 `cache-type=redis` 才注册默认实现）。 |
| 3 | 开发文档 §5.1.1 | 方法列表为 `loginOut()`、`refreshUserAuth`、`cacheUserAuth`、`cacheUserData` | 实际为 `loginOut(UserData)`、`refreshUserToken(LoginUser)`、`cacheLoginData(UserData, UserAuth)`；另外新增了 `offLineUser(userId, type)`。`UserDataManager` 是接口，实现类是 `RedisUserDataManagerImpl` |
| 4 | 开发文档 §5.1.3，特点 §2.3 | 剩余时间 ≤600 秒时"延长 10 分钟" | 实际是重置为当前时间 + live-time 分钟，并带有本地 Caffeine 节流 |
| 5 | 开发文档 §5.1.2 | 没有权限数据时返回 false | 实际返回 `success=false`，这与"无权限"（`success=true, data=false`）是两种不同的结果 **已修复**：token 为空或没有权限数据时返回 `success=true, data=false`，与"无权限"语义一致。 |
| 6 | 两份文档 | 未提及 | `IRefreshUserLoginRecord` 是续期回调；因为注入方式是 `@Resource @Lazy`，缺少实现时续期会抛异常 **已修复**：改为 `ObjectProvider` 获取，缺少实现时跳过回调，续期正常完成。 |
| 7 | 两份文档 | 未提及 | 存在 `User_Data_Token` 用户 token 集合，用于 `offLineUser`；它的读改写不是原子操作 **已修复**：读改写在基于 `ICacheService.setIfAbsent` 的用户级锁（`User_Data_Token_Lock`）内执行，登录时登记失败会回滚并返回失败。 |
| 8 | 开发文档 §2 build.gradle | 只列出 3 个依赖 | 还有 `api caffeine` |
| 9 | 开发文档 §10.3 | 用 `return new CustomUserDataManager()` 覆盖默认实现 | 默认实现开启时会产生两个同类型 Bean，需要关闭 `cache-type=redis` **已修复**：同 #2，自定义 `UserDataManager` Bean 直接替换默认实现。 |
| 10 | 源码 | `checkAuth` | `getSupperUser()` 为 null 或 `urls` 为 null 时会 NPE **已修复**：`supperUser` 用 `Boolean.TRUE.equals` 判断，`urls` 为 null 视为无权限。 |
| 11 | 调用方 | gateway `RequestGatewayFilter` | 使用 `required=false` 注入，但调用时没有判空（在 gateway 文档中复查） |
