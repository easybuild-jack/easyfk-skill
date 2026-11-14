# 01 项目类型与结构

## 1. 先认项目

动手前先看清这几件事，后面所有写法都以它为准：

1. 根构建文件里的模块列表（Gradle 看 `settings.gradle`，Maven 看根 `pom.xml` 的 `<modules>`）。
2. 每个模块的依赖（`build.gradle` / `pom.xml`）：用的是哪种 ORM、Cloud 还是 Dubbo、`web-prd` 还是 `web-micro`。
3. 找一个和本次需求最像的已有实体，把它从 Controller 到 Mapper 的全套类读一遍，记下包路径、类名后缀、Bean 注册方式、Controller 路径和权限注解的写法。
4. `src/main/resources` 下的 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`、Mapper XML、i18n 文件的位置。

从零开发、还没有工程时跳过本节，直接看 §2。

新代码和第 3 步找到的同类代码保持一致。项目里一个同类都没有、又看不出约定时，按本文 §2 的参考结构写，并在回复里说明。

## 2. 参考结构（普通数据库业务项目）

easyfk 的业务项目有下面四种结构。Maven 和 Gradle 的结构相同，只是构建文件不同。

- **已有项目**（通常由人先建好）：先按模块列表认出是哪一种，再按对应的结构放代码。以项目现状为准，不为了贴合参考结构去拆或合模块。
- **从零开发**：先和用户确定用哪一种，用户没有偏好时按规模给建议：中小项目、内部工具用单模块；要区分管理后台和客户端、以后可能拆成服务的用 sc；要同时提供 Cloud 和 Dubbo 的用 smart；要以 jar 给多个项目复用的业务模块用组件化。确定后按下面对应的参考结构建工程，构建照 §2.5；同时按新项目出文档（[10-docs.md](10-docs.md) §3、§5），第一批需求的主题叫「初版」，模块划分写进 `初版-架构图.md`。

| 形态 | 模块列表的特征 | 对应 easyfk-framework-skill §3 |
|---|---|---|
| 单模块（single） | 只有一个模块，没有子模块 | 单体 |
| 基础多模块（sc） | `-api`、`-server`、`-prd`（下分 `-prd-bms`、`-prd-client`） | 单体或微服务 |
| 多栈（smart） | `-api`、`-server`、`-sc`（下分 `-sc-client`、`-sc-provider`）、`-prd`（下分 `-prd-bms`、`-prd-client`） | 多栈微服务 |
| 组件化（如通用业务模块 auth） | 在 smart 的基础上把 ORM 拆成 `-orm-api` + `-orm-plus/flex/hibernate`，远程拆成 cloud / dubbo 各一对 | 可复用业务模块 |

### 2.1 单模块（single）

一个模块包含全部代码，依赖 `web-prd` + ORM（如 `orm-mybatis`）。分层只靠包：

```
<base>
├── api            IXxxApi
│   ├── dto / param / request / response / vo
├── server
│   ├── service / service.impl     IXxxService / XxxServiceImpl
│   ├── impl                       XxxApiServerImpl
│   ├── repository / repository.impl   IXxxRepository / XxxMybatisRepository
│   ├── persistence.model / persistence.mapper   Entity / Mapper
│   ├── config / enums / properties
└── controller     XxxController、XxxBmsController
resources/mappings/XxxMapper.xml
```

单模块项目不要为了「规范」拆成多模块；也不要再按 controller、service、dao 建子模块。

### 2.2 基础多模块（sc）

| 模块 | 放什么 | 主要依赖 |
|---|---|---|
| `<proj>-api` | `IXxxApi`、模型类；有远程调用时还放 Feign 契约和消费方 | `service-api`（有远程时加 `remote-cloud`，`compileOnly openfeign`、`spring-web`） |
| `<proj>-server` | Service、ApiServerImpl、Repository、Entity、Mapper、Mapper XML | `<proj>-api`，ORM |
| `<proj>-prd/<proj>-prd-bms` | 管理后台的 Controller | `<proj>-api`，`web-prd` |
| `<proj>-prd/<proj>-prd-client` | 客户端（App、小程序、H5 等 C 端）的 Controller | `<proj>-api`，`web-prd` |

`-prd` 只依赖 `-api`，不依赖 `-server`：和 server 打在一起就是单体；`-prd` 单独部署时，引入远程实现就变成接口层（BFF）。

### 2.3 多栈（smart）

| 模块 | 放什么 | 主要依赖 |
|---|---|---|
| `<proj>-api` | `IXxxApi`、模型类 | `service-api` |
| `<proj>-server` | Service、ApiServerImpl、Repository、Entity、Mapper、Mapper XML、Bean 配置 | `<proj>-api`，ORM |
| `<proj>-sc/<proj>-sc-client` | Feign 契约、消费方 `XxxApiScImpl`、远程配置属性和配置类 | `<proj>-api`，`remote-cloud`、`rpc-cloud`，`compileOnly spring-web` |
| `<proj>-sc/<proj>-sc-provider` | 提供方 `XxxRemoteImpl` | `<proj>-sc-client`、`<proj>-server`，`web-micro` |
| `<proj>-prd/<proj>-prd-bms` | 管理后台的 Controller | `<proj>-api`，`web-prd` |
| `<proj>-prd/<proj>-prd-client` | 客户端的 Controller | `<proj>-api`，`web-prd` |

同一个 `IXxxApi` 有本地（server）和远程（sc-client）两个实现，`-prd` 依赖哪一个就用哪一个，Controller 代码不变。需要 Dubbo 时，按同样的方式加 `-dubbo-client` / `-dubbo-provider`（或项目已有的命名）。

包路径：

| 包 | 放什么 |
|---|---|
| `<base>.api` / `.api.dto` / `.api.param` / `.api.request` / `.api.response` | Api 接口和模型 |
| `<base>.server.service` / `.service.impl` / `.server.impl` | Service / Service 实现 / ApiServerImpl |
| `<base>.server.repository` / `.repository.impl` | Repository 接口 / 实现 |
| `<base>.server.persistence.model` / `.persistence.mapper` | Entity / Mapper |
| `<base>.server.config` / `.enums` / `.properties` | Bean 配置 / 枚举 / 配置属性 |
| `<base>.sc.client.api` / `.sc.client.impl` / `.sc.client.config` / `.sc.client.properties` | Feign 契约 / 消费方 / 配置类 / 远程配置属性 |
| `<base>.sc.provider` | 提供方 |
| `<base>.controller` | Controller（bms 和 client 两个模块都用这个包） |

`resources/mappings/XxxMapper.xml` 放在 server 模块。

### 2.4 组件化（auth）

要以 jar 形式给多个项目复用的业务模块用这种结构。下面以 auth 为例：

| 模块（`<mod>` 为模块名） | 放什么 | 主要依赖 |
|---|---|---|
| `<mod>-api` | `IXxxApi`、Dto / Param / Req / EditReq / Resp / VO。给本服务和调用方共用 | `com.mcst:service-api`，`compileOnly com.mcst:easyfk-core` |
| `<mod>-orm/<mod>-orm-api` | `IXxxRepository` 接口 | `com.mcst:easyfk-repository` |
| `<mod>-orm/<mod>-orm-plus` | Entity、Mapper、Mapper XML、Repository 实现、ORM 配置类 | `<mod>-orm-api`，`com.mcst:orm-mybatis` |
| `<mod>-server` | `IXxxService` 与实现、`XxxApiServerImpl`、错误码枚举、配置属性类、Bean 配置类 | `<mod>-api`、`<mod>-orm-api`，`com.mcst:service-base`，`compileOnly spring-tx` |
| `<mod>-prd` | Controller 与 Controller 配置类 | `<mod>-api`，`com.mcst:web-prd` |
| `<mod>-remote/<mod>-cloud-api` | Feign 契约 `IXxxRemote`、消费方 `XxxApiScImpl`、远程配置属性 | `com.mcst:remote-cloud`，`compileOnly spring-cloud-starter-openfeign` |
| `<mod>-remote/<mod>-cloud-provider` | 提供方 `XxxRemoteImpl` | `<mod>-cloud-api`、`<mod>-server`，`com.mcst:web-micro` |
| `<mod>-remote/<mod>-dubbo-api` | Dubbo 契约 `IXxxRemote`、消费方 `XxxApiDubboImpl` | `com.mcst:remote-dubbo` |
| `<mod>-remote/<mod>-dubbo-provider` | 提供方 `XxxRemoteImpl` 与导出配置 | `<mod>-dubbo-api`、`<mod>-server`，`com.mcst:web-micro`、`com.mcst:rpc-dubbo` |

依赖方向：`prd → api`；`server → api、orm-api`；`orm-plus → orm-api`；`provider → server、remote-api`。`api` 不依赖 `server` 和 `orm`；Service 不依赖 `orm-plus`，只依赖 `orm-api` 里的 Repository 接口，换 ORM 时换实现模块即可。

包路径以 `com.mcst.module.auth` 为根（`<base>`）：

| 包 | 放什么 |
|---|---|
| `<base>.api` | `IXxxApi` |
| `<base>.api.dto` / `.param` / `.request` / `.response` / `.vo` | Dto / Param / Req、EditReq / Resp / 其他入参出参 |
| `<base>.orm.repository` | `IXxxRepository` |
| `<base>.orm.plus.persistence.model` / `.mapper` | Entity / Mapper |
| `<base>.orm.plus.repository.impl` | `XxxMybatisRepository` |
| `<base>.orm.plus.config` | ORM 层 Bean 配置 |
| `<base>.server.service` / `.service.impl` | `IXxxService` / `XxxServiceImpl` |
| `<base>.server.impl` | `XxxApiServerImpl` |
| `<base>.server.config` / `.enums` / `.properties` | Bean 配置 / 错误码等枚举 / 配置属性类 |
| `<base>.controller` | Controller |
| `<base>.remote` | `IXxxRemote` |
| `<base>.remote.impl` / `.remote.provider.impl` | 消费方 `XxxApiScImpl`、`XxxApiDubboImpl` / 提供方 `XxxRemoteImpl` |

### 2.5 构建约定

- `easyfk-dependencies` 已经管理的依赖（easyfk 模块和 BOM 里的第三方库）**不写版本号**；BOM 里没有的自己写版本，在根构建文件集中锁定。引入 BOM：`implementation platform("com.mcst:easyfk-dependencies:<版本>")`，用通用业务模块时再加 `com.mcst:module-dependencies`。BOM 的写法见 easyfk-framework-skill §8。
- 框架 jar 包只在 CNB Maven 私服上，需要仓库地址和访问令牌才能下载。从零开发时项目构建文件要声明私服仓库，令牌放用户本地（`~/.m2/settings.xml` 或 `~/.gradle/gradle.properties`），不写进项目；地址、令牌和配置示例见 easyfk-framework-skill §8.1。
- 注解处理器：`lombok`、`mapstruct-plus-processor`、`lombok-mapstruct-binding`、`spring-boot-configuration-processor`，编译参数加 `-Amapstruct.plus.nullValuePropertyMappingStrategy=IGNORE` 和 `-parameters`。处理器版本以 `versions/<版本>/VERSION.md` 的构建参数为准。
- 新加依赖前先查 easyfk-framework-skill 有没有现成模块，见 SKILL.md §1。

## 3. 新增一个实体要建哪些文件

以实体 `Order`、表 `t_order` 为例。项目里没有的层（比如没有 Dubbo）就跳过；项目把几个模块合在一起的，放进对应的包。

| 层 | 文件 | 规则 |
|---|---|---|
| 模型 | `OrderDto`、`OrderParam`、`OrderReq`、`OrderEditReq`、`OrderResp` | [02-model.md](02-model.md) |
| 持久层 | `Order`、`OrderMapper`、`IOrderRepository`、`OrderMybatisRepository`，ORM 配置里注册 Repository | [03-persistence.md](03-persistence.md) |
| 建表 | 项目有 SQL 脚本目录时补建表语句：主键 `varchar(36)`，唯一字段加唯一索引 | [03-persistence.md](03-persistence.md) |
| Service | `IOrderService`、`OrderServiceImpl`，配置里注册 | [04-service.md](04-service.md) |
| Api | `IOrderApi`、`OrderApiServerImpl`，配置里注册 | [05-api.md](05-api.md) |
| Controller | 管理后台 `OrderBmsController`，客户端需要时再加 `OrderController` | [06-controller.md](06-controller.md) |
| Remote | Cloud：`IOrderRemote`、`OrderRemoteImpl`、`OrderApiScImpl`；Dubbo：`IOrderRemote`、`OrderRemoteImpl`、`OrderApiDubboImpl`，以及导出和注册配置 | [07-remote.md](07-remote.md) |
| 错误与文案 | 错误码枚举加项；多语言项目在每个语言的 i18n 文件里加 key | [08-error.md](08-error.md) |

用户只要求其中一部分（比如只要后端接口，不要 Remote）时，只建要求的部分，在回复里列出没建的。

## 4. 架构类项目

组件、SDK、starter、中间件、引擎、框架底层这类偏架构层的项目，模块由本 skill 设计，不套用本文 §2 的四种业务结构，见 [11-architecture.md](11-architecture.md)。

这类项目里如果也有数据库 CRUD 部分（如配置管理、流水查询），那部分按本文 §3 和 02 ~ 08 的分层规范写。
