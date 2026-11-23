# easyfk-authority 开发文档

## 1. 模块概述

`easyfk-authority` 是 EasyFK 框架的**权限管理基础模块**，提供了注解驱动的权限资源定义、用户权限缓存管理、资源安全级别控制等核心能力。该模块作为权限体系的基础层，定义了通用的数据结构、注解和接口规范，供上层业务模块依赖和扩展。

---

## 2. 模块依赖

| 依赖模块 | 依赖方式 | 说明 |
|---|---|---|
| `easyfk-core` | `compileOnly` | 核心模块，提供基础 DTO、工具类、上下文等 |
| `easyfk-cache` | `api` | 缓存模块，提供 `ICacheService` 缓存服务 |
| `easyfk-service:service-api` | `api` | 服务层 API，提供 `IBaseApi` 等基础接口 |

**build.gradle:**
```groovy
dependencies {
    compileOnly project(':easyfk-core')
    api project(':easyfk-cache')
    api project(':easyfk-service:service-api')
}
```

---

## 3. 包结构

```
com.mcst.easyfk.authority
├── annotation/           # 权限注解
│   ├── AuthResource        - 权限资源注解（标注方法或类）
│   ├── LoginResource       - 登录资源注解（标注方法）
│   └── ResourceController  - 资源控制器注解（标注类）
├── config/               # 自动配置
│   └── UserAuthConfigure   - Spring Boot 自动配置类
├── constant/             # 常量
│   └── ResourceSecurityLevel - 资源安全级别枚举
├── dto/                  # 数据传输对象
│   └── AuthResourceDto     - 权限资源 DTO
├── enums/                # 枚举
│   ├── ResourceCategory    - 资源类别枚举
│   └── UserTypeEnum        - 用户类型枚举
├── manager/              # 管理器
│   └── UserDataManager     - 用户数据与权限缓存管理器
├── param/                # 参数对象
│   └── AuthResourceParam   - 权限资源查询参数
├── properties/           # 配置属性
│   └── AuthProperties      - 权限配置属性
├── request/              # 请求对象
│   └── AuthResourceReq     - 权限资源请求对象
├── response/             # 响应对象
│   └── AuthResourceResp    - 权限资源响应对象
├── vo/                   # 值对象
│   ├── RoleListVo          - 角色列表
│   ├── TreeNode            - 通用树节点
│   ├── UserAuth            - 用户权限缓存对象
│   └── UserAuthResources   - 用户权限资源树形结构
└── IAuthResourceApi        # 权限资源 API 接口
```

---

## 4. 注解使用指南

### 4.1 @ResourceController

**作用：** 标注在 Controller 类上，声明该控制器为权限资源控制器。

**适用目标：** `ElementType.TYPE`（类）

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `group` | String | `"default"` | 组标识，支持增量初始化时按组操作 |
| `id` | String | `""` | 控制器资源 ID |
| `name` | String | `""` | 资源名称 |
| `title` | String | `""` | 标题 |
| `path` | String | `""` | 前端页面路径 |
| `sort` | int | `0` | 排序权重 |
| `remark` | String | `""` | 备注说明 |
| `icon` | String | `""` | 图标信息 |
| `typeFlag` | String | `"all"` | 类型标识，用于多平台资源归类 |

**使用示例：**
```java
@ResourceController(
    id = "user-mgmt",
    name = "用户管理",
    title = "用户管理",
    path = "/system/user",
    icon = "user",
    typeFlag = "system"
)
@RestController
@RequestMapping("/api/user")
public class UserController {
    // ...
}
```

### 4.2 @AuthResource

**作用：** 标注在方法或类上，声明需要权限验证的资源。

**适用目标：** `ElementType.METHOD`、`ElementType.TYPE`

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `id` | String | *必填* | 资源 ID |
| `name` | String | *必填* | 资源名称 |
| `pId` | String | `""` | 父资源 ID |
| `pName` | String | `""` | 上级资源名称 |
| `title` | String | `""` | 资源名称简写，权限分配页面展示用 |
| `actionCode` | String | `""` | 功能 Code |
| `category` | ResourceCategory | `menu` | 资源类型：`menu`/`action`/`normal` |
| `rootStatus` | int | `0` | 是否根目录：0-否，1-是 |
| `sort` | int | `0` | 排序 |
| `path` | String | `""` | 前端页面路径 |
| `remark` | String | `""` | 备注 |
| `icon` | String | `""` | 图标信息 |
| `unPassMsg` | String | `""` | 无权限时的提示信息 |
| `typeFlag` | String | `"all"` | 类型标识，多平台资源归类 |
| `defaultFlag` | String | `"all"` | 默认类型标识，平台端默认资源 |

**使用示例：**
```java
@AuthResource(
    id = "user-list",
    name = "用户列表",
    pId = "user-mgmt",
    category = ResourceCategory.menu,
    path = "/system/user/list"
)
@GetMapping("/list")
public ResponseResult<List<UserResp>> list() {
    // ...
}

@AuthResource(
    id = "user-add",
    name = "新增用户",
    pId = "user-mgmt",
    category = ResourceCategory.action,
    actionCode = "user:add"
)
@PostMapping("/add")
public ResponseResult<?> add(@RequestBody UserReq req) {
    // ...
}
```

### 4.3 @LoginResource

**作用：** 标注在方法上，声明该接口需要登录后才能访问（无需特定权限）。

**适用目标：** `ElementType.METHOD`

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `value` | String | `""` | 预留扩展字段 |

**使用示例：**
```java
@LoginResource
@GetMapping("/profile")
public ResponseResult<UserProfile> getProfile() {
    // 仅需登录即可访问，无需权限验证
}
```

---

## 5. 核心组件详解

### 5.1 UserDataManager —— 用户数据与权限管理器

`UserDataManager` 是模块的核心管理类，负责用户权限数据的缓存读写和权限校验。

**缓存空间：**
- `User_Auth` —— 存储用户的权限数据（`UserAuth`）
- `User_Data` —— 存储用户的基本数据（`UserData`）

#### 5.1.1 方法列表

| 方法 | 返回值 | 说明 |
|---|---|---|
| `loginOut()` | `BaseResult<?>` | 退出登录，清除当前用户的 Auth 和 Data 缓存 |
| `checkAuth(String cacheKey, String path)` | `BaseResult<Boolean>` | 校验用户是否拥有指定路径的权限 |
| `refreshUserAuth(LoginUser loginUser)` | `void` | 刷新用户缓存的过期时间（剩余 <=600秒时延长10分钟） |
| `getUserAuth(String cacheKey)` | `UserAuth` | 通过缓存 Key 获取用户权限对象 |
| `cacheUserAuth(UserAuth userAuth)` | `BaseResult<String>` | 缓存权限对象，返回生成的缓存 Token |
| `cacheUserData(UserData userData)` | `BaseResult<String>` | 缓存用户数据对象，返回生成的缓存 Token |
| `getUserData(LoginUser loginUser)` | `UserData` | 通过登录信息获取用户数据 |

#### 5.1.2 权限校验流程

```
checkAuth(cacheKey, path)
    │
    ├─ 1. 从缓存获取 UserAuth
    │     └─ 不存在 → 返回 false（未登录/缓存过期）
    │
    ├─ 2. 判断是否超级管理员
    │     └─ 是 → 直接通过
    │
    └─ 3. 检查用户 URL 列表是否包含目标路径
          ├─ 包含 → 返回 true（有权限）
          └─ 不包含 → 返回 false（无权限）
```

#### 5.1.3 缓存续期策略

当用户活跃时，系统会自动检查缓存剩余时间：
- 若 `User_Data` 或 `User_Auth` 缓存剩余时间 **<= 600 秒**（10分钟），自动延长 **10 分钟**
- 若缓存已永久过期（expire <= 0），不进行续期

### 5.2 IAuthResourceApi —— 权限资源 API 接口

继承自 `IBaseApi<AuthResourceResp, String, AuthResourceReq>`，提供权限资源的 CRUD 及扩展能力。

| 方法 | 返回值 | 说明 |
|---|---|---|
| `authorityResourceList()` | `ResponseResult<List<AuthResourceResp>>` | 获取系统中所有"权限类型"的资源列表 |
| `checkUriSecurityLevel(String url)` | `ResourceSecurityLevel` | 判断指定 URL 的安全级别 |
| `saveResourceByBath(List<AuthResourceReq> list)` | `void` | 批量保存权限资源 |
| `getPlatformAuthResources(String type, Integer defaultStatus)` | `List<AuthResourceResp>` | 获取指定平台类型的权限资源 |

---

## 6. 数据模型

### 6.1 AuthResourceDto —— 权限资源 DTO

| 字段 | 类型 | 说明 |
|---|---|---|
| `resourceId` | String | 资源 ID（主键） |
| `name` | String | 名称 |
| `icon` | String | 图标 |
| `url` | String | 资源 URL |
| `pid` | String | 父资源 ID |
| `pname` | String | 父资源名称 |
| `title` | String | 标题 |
| `category` | String | 资源类型：`menu`/`action` |
| `remark` | String | 备注 |
| `sort` | Integer | 排序 |
| `path` | String | 前端路由地址 |
| `actionCode` | String | 功能代码 |
| `unPassMsg` | String | 无权限提示 |
| `resourceLevel` | Integer | 资源等级：0-无需验证，1-需要登录，2-需要权限 |
| `rootStatus` | Integer | 根目录标识：0-否，1-是 |
| `groupCode` | String | 分组代码 |
| `typeFlag` | String | 类型标识（多平台归类） |
| `defaultFlag` | String | 默认类型标识 |

### 6.2 UserAuth —— 用户权限缓存对象

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `supperUser` | Boolean | `false` | 是否超级管理员 |
| `resources` | List\<AuthResourceDto\> | - | 权限资源列表 |
| `urls` | List\<String\> | - | 已授权 URL 列表 |

### 6.3 UserAuthResources —— 用户权限资源树

| 字段 | 类型 | 说明 |
|---|---|---|
| `resourceId` | String | 资源 ID |
| `name` | String | 名称 |
| `title` | String | 标题 |
| `icon` | String | 图标 |
| `path` | String | 路径 |
| `actions` | List\<String\> | 功能操作列表 |
| `children` | List\<UserAuthResources\> | 子资源列表（递归结构） |
| `sort` | Integer | 排序 |

---

## 7. 枚举与常量

### 7.1 ResourceSecurityLevel —— 资源安全级别

| 枚举值 | 说明 |
|---|---|
| `LOGIN` | 需要登录 |
| `AUTHORITY` | 需要权限 |
| `UNIMPEDED` | 不拦截，自由访问 |

### 7.2 ResourceCategory —— 资源类别

| 枚举值 | 说明 |
|---|---|
| `menu` | 菜单资源 |
| `action` | 功能/操作资源 |
| `normal` | 普通资源 |

### 7.3 UserTypeEnum —— 用户类型

| 枚举值 | value | 说明 |
|---|---|---|
| `Platform` | `"platform"` | 平台用户 |
| `Agent` | `"agent"` | 代理商 |
| `Merchant` | `"merchant"` | 商户 |
| `Customer` | `"customer"` | C端会员用户 |

---

## 8. 配置说明

### 8.1 application.yml 配置

```yaml
easyfk:
  config:
    auth:
      live-time: 120   # 权限缓存时间，单位：分钟，默认 120（2小时）
```

### 8.2 自动配置

模块通过 Spring Boot 自动配置机制注册：
- 配置文件：`META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`
- 自动配置类：`UserAuthConfigure`
- 注册的 Bean：
  - `UserDataManager`（条件：容器中不存在时创建）

---

## 9. 数据流转关系

```
Request 层                  Param 层                  DTO 层                   Response 层
AuthResourceReq  ──────→  AuthResourceParam  ──────→  AuthResourceDto  ──────→  AuthResourceResp
  (请求入参)                 (查询参数)                 (数据传输)                (响应出参)
      │                                                      │
      └────── @AutoMapper ──────────────────────────────────→ │
                                                              │
                                              @AutoMapper ────┘──────→ AuthResourceResp
```

对象映射基于 `mapstruct-plus`（`@AutoMapper` 注解），自动完成 DTO 与 Request/Response 之间的转换。

---

## 10. 集成指南

### 10.1 引入依赖

在业务模块的 `build.gradle` 中添加：

```groovy
dependencies {
    implementation project(':easyfk-authority')
}
```

### 10.2 使用权限注解

1. 在 Controller 类上添加 `@ResourceController` 声明资源控制器
2. 在需要权限的方法上添加 `@AuthResource` 声明权限资源
3. 在仅需登录的方法上添加 `@LoginResource`

### 10.3 自定义 UserDataManager

如需自定义用户数据管理逻辑，可通过注册同类型 Bean 覆盖默认实现：

```java
@Configuration
public class CustomAuthConfig {

    @Bean
    public UserDataManager userAuthManager() {
        return new CustomUserDataManager();
    }
}
```

由于 `UserAuthConfigure` 使用了 `@ConditionalOnMissingBean`，自定义 Bean 将优先生效。
