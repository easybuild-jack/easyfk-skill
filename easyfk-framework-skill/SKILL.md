---
name: easyfk-framework-skill
description: EasyFK（易架构，groupId com.mcst）Java 企业级框架的能力地图：框架由哪些工程和模块组成、每个模块提供什么能力、解决什么问题、按需求该选哪个模块，以及框架自带的工具类与已引入的第三方工具库（Hutool、fastjson2、Jackson、MapStruct-Plus 等）清单，避免重复造轮子。覆盖 web / 网关 / 鉴权 / ORM / Redis / MongoDB / ClickHouse / 缓存 / 分布式锁 / 业务编号 / MQ / RPC / 线程池 / Disruptor / Fory 序列化 / Chronicle / WebSocket / XXL-JOB / Nacos / Sentinel / Seata / Knife4j / Aeron / aeron-cluster / etcd-cluster / 通用业务模块，并按项目所用的 easyfk 版本加载对应的文档快照。仅在识别到 easyfk 的项目中使用：构建文件引入了 easyfk- 开头的组件坐标（如 easyfk-dependencies），或源码包名以 com.mcst 开头；从零新建时用户明确要求按 easyfk 建也算。识别不到就不使用。用户要求维护 easyfk-skill 套件本身时（升级到新的 easyfk 版本、对齐某个模块的修改）也使用本 skill，按 maintenance.md 执行。
---

# EasyFK 框架能力地图

## 0. 如何使用

本 skill 回答三个问题：**框架有哪些能力和模块、各自解决什么问题、某个需求该用哪个模块或工具**。具体类怎么写（Controller、Service 分层写法、返回值、异常等编码规范）不在本 skill 范围内，由开发规范 skill **easyfk-dev-skill** 负责；从代码反推业务和架构由 **easyfk-reverse-skill** 负责；新建工程、按库表生成 Entity 和分层代码由 **easyfk-generator-skill** 调 `efg` CLI 完成（AI 不手写工程文件）；某个模块的详细用法读该模块的 skill 文档。

本 skill 和上面三个同属 easyfk-skill 套件（仓库 `https://github.com/easybuild-jack/easyfk-skill.git`），安装后是 skills 目录第一层的四个平级目录。要写代码、反推或生成工程而另外三个没装时，按 easyfk-dev-skill 的「套件安装检查」安装；easyfk-dev-skill 也没有时，克隆上面的仓库，运行仓库根目录的 `install.ps1 -Target <skills 目录>`（Windows）或 `sh install.sh <skills 目录>`（macOS / Linux）把四个一起装上。安装失败时告诉用户，不凭记忆套编码规范。

本文件只写跨版本不变的内容，**不含任何具体版本号**。依赖版本、配置项、模块用法随 easyfk 版本变化，放在 `versions/<easyfk版本>/` 的快照中。

用户要求维护本套件（如“把 easyfk-skill 升级到 <新版本>，源码在 <目录>”、“<模块> 改了，对齐 skill”）时，不走下面的项目识别，直接读本 skill 目录下的 [maintenance.md](maintenance.md) 按其流程执行。

### 0.0 确认是 easyfk 项目（最先做）

从项目本身判断：构建文件引入了 `easyfk-` 开头的组件坐标（如 `easyfk-dependencies`），或源码包名以 `com.mcst` 开头，就使用本 skill；识别不到就不使用，不用本文的模块、类名和配置前缀回答。细则同 easyfk-dev-skill 的「项目识别」。

### 0.1 确定项目的 easyfk 版本（每次先做）

easyfk 版本即项目导入的 BOM `com.mcst:easyfk-dependencies:<版本>` 的版本，按顺序查找：

1. `gradle.properties` 中的 `easyfkVersion`（或其他被 BOM 坐标引用的变量）；
2. `build.gradle` / `build.gradle.kts` 中 `platform("com.mcst:easyfk-dependencies:<版本>")`；
3. `gradle/libs.versions.toml`、`settings.gradle` 的 version catalog；
4. `pom.xml` 的 `<dependencyManagement>`。

找不到时先问用户，不要默认使用最新版本。新建项目时由用户指定版本，未指定则使用 [versions/index.md](versions/index.md) 中标为"当前最新"的版本。

### 0.2 按版本读取文档

1. 打开 [versions/index.md](versions/index.md)，定位 `versions/<版本>/`：精确命中直接使用；没有对应快照时用不高于项目版本的最近快照，并告诉用户"差异以项目实际源码和 BOM 为准"。
2. 读该目录的 `VERSION.md`：技术基线（JDK、Spring、三方库版本）、构建参数、本版本注意事项、文档索引。
3. 用到某个模块时，读该版本 `modules/` 中对应的 skill 文档（已逐行对照源码复查）。本文中出现的 `xxx-skill.md` 都指这个目录下的文件。
4. 需要**精确签名**——方法重载、参数顺序、返回类型、常量与枚举取值、配置项默认值、注解属性、引入后自动生效的配置类——时，读该版本 `api/` 下对应的 `*.api.md`（入口 `versions/<版本>/api/INDEX.md`，文件与模块一一对应）。这类文件由脚本从源码提取，只列签名不含用法；**按需只读相关类的段落，不要整份读**。
5. 需要完整配置项或示例时，再读该版本 `manuals/` 中的使用手册。

**可信度顺序：项目实际依赖的源码 > `api/*.api.md`（签名）与 `modules/*-skill.md`（用法）> `manuals/*`。**

不凭记忆写类名、方法名和配置项：`modules/` 里没写、`api/` 里查不到的，就是框架没有。

## 1. 定位与原则

1. **不重复造轮子**：需求先对照 §4、§5、§6；框架已有的能力必须用框架的，不在业务项目里另写一份，也不为同类需求引入新的第三方库。框架确实缺少的通用能力，补到框架里。
2. **统一技术底层**：第三方版本只由 BOM `com.mcst:easyfk-dependencies` 管理，业务项目只写 BOM 的版本；升级通过升级 easyfk 版本统一进行。
3. **统一架构**：项目形态从 §3 的四种中选；配置统一在 `easyfk.config.*` 前缀下。

## 2. 框架全景

| 工程 | 定位 | 包含 |
|---|---|---|
| `easyfk-dependencies` | 第三方版本 BOM | Spring Boot / Cloud / Cloud Alibaba 三个平台 BOM + 全部第三方库版本约束 + easyfk 自身模块坐标 |
| `easyfk-base` | 框架底座 | 核心类型与工具、日志、序列化、线程池、进程内队列、缓存抽象、Repository / Service 抽象、RPC 契约、Web、鉴权、网关 |
| `easyfk-component` | 中间件组件 | 数据库与 Redis、缓存实现、分布式锁、业务编号、ORM、连接池、MQ、RPC、Chronicle、WebSocket、定时任务、微服务基础设施 |
| `easyfk-aeron` | 低时延消息（独立工程） | Aeron 发布订阅、多种 codec、压缩、监控、状态存储、Spring Boot starter |
| `aeron-cluster` | Raft 复制状态机（独立工程） | 集群核心、客户端、starter、测试工具 |
| `etcd-cluster` | 分布式协调（独立工程） | 选主、Fence、成员注册、共享状态、starter |
| `module-dependencies` | 通用业务模块 BOM | 权限、登录记录、用户、短信、字典、订单、支付等可复用业务模块 |

跨版本不变的技术约定：jakarta 命名空间；Web 容器 Undertow；编译必须带 `-parameters`；Spring Boot / Cloud / Cloud Alibaba 是配套版本，只能随 easyfk 版本一起升。具体版本见对应 `VERSION.md`。

## 3. 支持的项目形态

| 形态 | 适用 | 典型模块组合 |
|---|---|---|
| 单体 | 中小项目、内部工具 | web-prd + 日志 + ORM + 数据库驱动 + cache-redis |
| 接口层（BFF） | C 端 / 管理后台接口层，本身无业务、无 DB | web-prd + rpc-cloud 或 rpc-dubbo |
| 微服务 | 标准微服务，单一 RPC 技术栈 | 服务端 web-micro + ORM + remote-cloud 或 remote-dubbo；注册 / 配置用 nacos；入口 easyfk-gateway |
| 多栈微服务 | 大型平台，同时支持 Cloud 与 Dubbo | 同一套业务接口同时提供 Cloud 与 Dubbo 实现，调用方只依赖业务接口，换依赖包即可在本地 / Feign / Dubbo 间切换 |

各形态的工程拆分与分层写法属于开发规范，见 easyfk-dev-skill。

## 4. 模块能力清单

坐标均为 `com.mcst:<artifact>`，版本由 BOM 管理。表中「文档」列是该模块的用法文档（`modules/`）；**精确签名、常量取值、配置项默认值**查同版本 `api/` 下同名的 `*.api.md`。

### 4.1 easyfk-base（底座）

| 模块 | 提供的能力 | 解决的问题 | 文档 |
|---|---|---|---|
| `easyfk-core` | 统一返回体与分页结构及其构建器、业务异常与错误码规范、线程上下文（当前用户、请求头、TraceId）、通用工具类（§6）、国际化、SpEL 解析 | 全项目共用一套基础类型和工具，不再各写 `Result`、`XxxUtil` | `easyfk-core-skill.md`、`easyfk-core-toolkit-skill.md` |
| `log-logback` / `log-log4j2` | 统一日志配置、TraceId 输出、JSON 日志 | 日志格式与链路追踪一致（二选一） | `easyfk-log-skill.md` |
| `serializer-base` / `serializer-fory` | 基于 Fory 的高性能二进制序列化与类注册 | 跨进程、存储场景的高效序列化 | `easyfk-serializer-skill.md` |
| `easyfk-thread` | 按用途划分的命名线程池（IO 密集、CPU 密集、通用、异步、调度），自动透传 TraceId | 统一线程池管理，异步任务日志可追踪 | `easyfk-thread-skill.md` |
| `queue-disruptor` | 基于 Disruptor 的进程内高性能队列 | 进程内高吞吐生产消费（不持久化，不保证不丢） | `easyfk-queue-skill.md` |
| `easyfk-cache` | 缓存抽象接口 `ICacheService` | 业务与框架组件面向统一缓存接口编程，实现可替换 | `easyfk-cache-skill.md` |
| `easyfk-repository` | 统一 Repository 抽象与条件构建器，屏蔽 ORM 差异 | 换 ORM 不改业务代码；通用 CRUD 不再手写 | `easyfk-repository-skill.md` |
| `service-api` / `service-base` | 通用 CRUD Service 基类、唯一性校验、多租户数据过滤 | 标准增删改查与校验开箱即用 | `easyfk-service-skill.md` |
| `remote-cloud` / `remote-dubbo` | RPC 契约基类，同一套接口对应 Feign 与 Dubbo | 服务间契约统一，可切换 RPC 技术栈 | `easyfk-remote-skill.md` |
| `web-prd` | 对外 HTTP 服务：签名防重放、登录与权限拦截、幂等、CORS、全局异常处理、统一序列化 | 对外接口的安全与通用处理不用自己写 | `easyfk-web-skill.md` |
| `web-micro` | 网关后的内部服务：还原用户与链路上下文、全局异常处理，不做鉴权 | 内部微服务轻量接入 | `easyfk-web-skill.md` |
| `easyfk-authority` | 登录态管理、登录与权限注解（随 web 传递） | 登录鉴权与接口权限控制 | `easyfk-authority-skill.md` |
| `easyfk-gateway` | 基于 Spring Cloud Gateway 的统一网关：鉴权、签名校验、上下文透传 | 微服务统一入口 | `easyfk-gateway-skill.md` |

### 4.2 easyfk-component（中间件组件）

| 模块 | 提供的能力 | 解决的问题 | 文档 |
|---|---|---|---|
| `db-redis` | Redis 读写、发布订阅、多种序列化器，支持动态多数据源 | 非缓存类 Redis 数据访问 | `easyfk-component-db-skill.md` |
| `db-mongo` / `db-clickhouse` | MongoDB、ClickHouse 接入 | 文档库、分析库 | `easyfk-component-db-skill.md` |
| `db-mysql` / `db-postgresql` | 关系库驱动 | 与 ORM 搭配使用 | `easyfk-component-db-skill.md` |
| `cache-redis` | `ICacheService` 的默认实现 + Spring Cache 注解缓存 | 分布式缓存；框架内防重、幂等、鉴权等组件依赖它 | `easyfk-component-cache-skill.md` |
| `cache-caffeine` | 进程内本地缓存管理器，可选 Spring Cache 注解缓存 | 本地缓存 | `easyfk-component-cache-skill.md` |
| `lock-redisson` | 基于 Redisson 的分布式锁模板 | 业务互斥 | `easyfk-component-lock-skill.md` |
| `autoId-api` / `autoId-redis` | 基于 Redis 的可读业务编号 | 订单号等业务单号 | `easyfk-component-autoId-skill.md` |
| `orm-mybatis`（默认）/ `orm-flex` / `orm-hibernate` / `orm-sharding` | Repository 抽象的四种 ORM 实现 | 关系库访问（只能启用一个） | `easyfk-component-orm-skill.md` |
| `ds-druid` | Druid 连接池 | 连接池与监控 | `easyfk-component-ds-skill.md` |
| `mq-common` + `mq-rocket` / `mq-rabbit` / `mq-kafka` | 统一的消息发送与消费抽象，延迟、顺序消息 | 异步解耦、可靠消息 | `easyfk-component-mq-skill.md` |
| `rpc-cloud` / `rpc-dubbo` | OpenFeign / Dubbo 调用接入，自动透传 TraceId、Access-Token、Language | 微服务间调用 | `easyfk-component-rpc-skill.md` |
| `chronicle-map` / `chronicle-queue` | 堆外持久化 KV、单机持久化顺序队列 | 低 GC 大容量本地数据（不能跨机器） | `easyfk-component-chronicle-skill.md` |
| `websocket-server` / `websocket-api` | WebSocket 接入服务；业务方通过 api 推送 | 服务端主动推送 | `easyfk-component-websocket-skill.md` |
| `job-xxl` | XXL-JOB 执行器封装，可自动注册任务 | 分布式定时任务（必须有调度中心） | `easyfk-component-job-skill.md` |
| `config-nacos` / `registry-nacos` / `protect-sentinel` / `transaction-seata` / `doc-knife4j` | 纯依赖聚合，使用官方配置 | 配置中心、注册中心、限流熔断、分布式事务、接口文档 | `easyfk-component-infra-skill.md` |

> 多级缓存（`cache-mult`）与 InfluxDB（`db-influx`）两个子模块已下线，各版本快照都不再收录（`modules/`、`api/`、`manuals/` 中均已移除）。需要多级缓存时用 `cache-caffeine` + `cache-redis` 自行组合，需要时序库时自行引入 `influxdb-client-java`；遇到旧代码里的这两个坐标，按"框架已不提供"处理。

### 4.3 独立工程

| 模块 | 提供的能力 | 解决的问题 | 文档 |
|---|---|---|---|
| `aeron-spring-boot-starter` 及 producer / consumer / codec / compression / metrics 等子模块 | Aeron 发布订阅（UDP / IPC），SBE、Protobuf、Fory 等 codec，LZ4 / Zstd 压缩，监控，Chronicle 状态存储 | 超低时延广播（行情、撮合）；只做 fan-out，不持久化 | `easyfk-aeron-skill.md` |
| `aeron-cluster-spring-boot-starter` / `aeron-cluster-client` | 基于 Aeron Cluster 的 Raft 复制状态机 | 多副本强一致、确定性状态机 | `aeron-cluster-skill.md` |
| `etcd-cluster-spring-boot-starter` | 选主、Fence（防旧主复活覆盖）、成员注册、少量强一致共享状态 | 分布式协调 | `etcd-cluster-skill.md` |

### 4.4 通用业务模块

`module-dependencies` BOM 下提供权限、登录记录、用户、短信、字典、订单、支付等业务模块，按 `<业务>-api / -server / -prd-client / -prd-bms / -cloud-* / -dubbo-* / -orm-*` 拆分。**开发业务功能前先查这里是否已有，再决定自研。**

## 5. 需求 → 模块选型

| 需求 | 用这个 | 配置前缀 |
|---|---|---|
| 直接对外的 HTTP 服务（单体 / BFF） | `web-prd` | `easyfk.config.web.*`、`easyfk.config.aspect.controller` |
| 网关后的内部微服务 | `web-micro` | `easyfk.config.web.jwt` / `intercept` |
| 统一网关 | `easyfk-gateway` + `cache-redis` + 注册中心 | `easyfk.config.gateway`、`easyfk.config.web.security` / `intercept` |
| 登录态、权限控制 | `easyfk-authority` + `cache-redis` | `easyfk.config.login` |
| 日志 | `log-logback` **或** `log-log4j2` | `logging.config` |
| 关系库 | `orm-mybatis`（默认）/ `orm-flex` / `orm-hibernate` + `db-mysql` / `db-postgresql`，连接池 `ds-druid` | `spring.datasource.*` |
| 分库分表 | `orm-sharding`（使用前先看 `VERSION.md` 的兼容性提示） | ShardingSphere 官方配置 |
| Redis 非缓存数据 | `db-redis` | `spring.data.redis`、`easyfk.config.db.redis` |
| MongoDB / ClickHouse | `db-mongo` / `db-clickhouse` | `easyfk.config.db.clickhouse` |
| 分布式缓存 | `cache-redis` | `easyfk.config.cache.redis` |
| 本地缓存 | `cache-caffeine` | `easyfk.config.cache.caffeine` |
| 分布式锁 | `lock-redisson` | `easyfk.config.lock.redisson` |
| 可读业务编号 | `autoId-redis` | `easyfk.config.autoid.redisson` |
| 主键、UUID、雪花 ID | ORM 主键策略；Hutool `IdUtil` | — |
| 消息队列 | `mq-rocket` / `mq-rabbit` / `mq-kafka`（需打开对应 `enable-*` 开关） | `easyfk.config.mq.rocket` / `rabbit` / `kafka` |
| 微服务调用 | `rpc-cloud` 或 `rpc-dubbo`，契约 `remote-cloud` / `remote-dubbo` | `easyfk.config.remote.<模块>` |
| 线程池、异步、调度 | `easyfk-thread` | `easyfk.config.thread.pool` |
| 进程内高性能队列 | `queue-disruptor` | `easyfk.config.queue.disruptor` |
| 二进制序列化 | `serializer-fory` | `easyfk.config.serializer` |
| 单机持久化 KV / 顺序队列 | `chronicle-map` / `chronicle-queue` | `easyfk.config.chronicle.map`、`easyfk.config.storage.queue` |
| WebSocket 推送 | `websocket-server`（接入服务）+ `websocket-api`（业务方） | `easyfk.config.websocket` |
| 定时任务 | `job-xxl` | `xxl.job` |
| 配置中心 / 注册中心 / 限流 / 分布式事务 / 接口文档 | `config-nacos` / `registry-nacos` / `protect-sentinel` / `transaction-seata` / `doc-knife4j` | `spring.cloud.*`、`knife4j.*` |
| 超低时延广播 | `aeron-spring-boot-starter` + codec（如 `aeron-codec-fory`） | `easyfk.config.aeron` |
| 强一致复制状态机 | `aeron-cluster-spring-boot-starter` / `aeron-cluster-client` | `easyfk.config.aeron.cluster` |
| 选主、成员注册、少量强一致状态 | `etcd-cluster-spring-boot-starter` | `easyfk.config.cluster` |
| 通用业务功能 | `module-dependencies` 下的业务模块 | 见各业务模块 |

### 5.1 易混场景

| 场景 | 选择 | 不要选 |
|---|---|---|
| 需要持久化、ack、重投、回放的消息 | component-mq | easyfk-aeron（只做 fan-out，不持久化） |
| 同机进程间持久化顺序队列 | chronicle-queue | queue-disruptor（内存，不保证不丢） |
| 业务互斥锁 | lock-redisson | etcd 选主、aeron-cluster |
| "只有主节点执行" + 旧主复活防覆盖 | etcd-cluster 选主 + Fence | redisson 锁 |
| 多副本确定性状态机 | aeron-cluster | etcd 共享状态（只放少量状态） |
| 配置中心 / 服务注册 | config-nacos / registry-nacos | etcd-cluster |
| 业务缓存读写 | cache-redis | 直接用 db-redis 拼 key（db-redis 用于非缓存类 Redis 数据） |
| 全局唯一长期主键 | ORM 主键策略 / 雪花 ID | autoId-redis、core 的 `OrderNoUtil`（只保证单 JVM） |

## 6. 工具能力清单

框架已有的工具能力必须直接使用，不在业务项目里另写 `XxxUtil`，也不为工具需求引入新的第三方库。选用顺序：**easyfk-core 工具类 → core 已传递的第三方库中指定的那个 → JDK**。各工具的方法与行为细节见 `easyfk-core-toolkit-skill.md`、`easyfk-core-skill.md`。

### 6.1 easyfk-core 自带工具（包前缀 `com.mcst.easyfk.core`）

| 能力 | 工具 |
|---|---|
| 判空、空值抛业务异常 | `EmptyUtil` |
| 驼峰 / 下划线、首字母大小写 | `StringUtil` |
| 分隔字符串拆分并转类型 | `SplitUtil` |
| DTO / PO / VO 对象转换、Bean ↔ Map | `TransformUtil` |
| 更新场景的部分字段拷贝 | `MapStructConvertUtil` |
| 反射读写字段、按注解找字段 | `ReflectUtil` |
| 方法引用取字段名 | `EFunction` + `FunctionColumnToStringUtil` |
| 枚举按 value / code 反查 | `EnumUtils` |
| 日期时间格式化、转换、区间 | `LocalDateUtil` |
| 国际化消息 | `I18NUtil` |
| SpEL 解析 | `ExpressionUtil` |
| 单 JVM 业务单号 | `OrderNoUtil` |
| 条件 / 判空分支执行 | `FunctionExecutor` |
| 返回体、分页、请求、异常构建 | `RRBuilder`、`BRBuilder`、`PRBuilder`、`SRPBuilder`、`MRPBuilder`、`BEBuilder` |
| 线程上下文 | `UserDataContext`、`RequestHeaderContext`、`TraceIdContext` |
| 通用常量 | `RequestHeaderConstant`、`CharacterConstant`、`ReturnCodeConstant` 等 |

### 6.2 core 已传递的第三方库（引入 easyfk-core 即在 classpath 上，不要再引同类库）

| 库 | 在框架中的定位 |
|---|---|
| Spring（core / context / AOP / validation） | 容器、切面、`jakarta.validation` 参数校验；`StopWatch`、`AntPathMatcher` 等补充工具 |
| Jackson | **HTTP 出入参序列化**（Spring MVC） |
| fastjson2 | **代码中手动 JSON 处理**（MQ / WebSocket 消息、Redis 序列化等） |
| Hutool | core 没有覆盖的通用能力：`IdUtil`（UUID、雪花 ID）、`DigestUtil` / `HMac` / `SecureUtil`（摘要签名）、`StrUtil`（格式化）、`CollUtil` / `MapUtil` / `ArrayUtil`、`Convert`、`SpringUtil`（静态取 Bean）、`HttpRequest`（调外部 HTTP） |
| MapStruct-Plus | `TransformUtil` 的高性能转换路径 |
| swagger-annotations | OpenAPI 文档注解 |
| SLF4J + Lombok | 日志门面与样板代码 |

BOM 已管理、需要时显式引入：Jasypt（配置加密）、EasyExcel（Excel）、OkHttp、dynamic-datasource（多数据源）、sms4j（短信聚合）、WxJava（微信生态）。

### 6.3 框架没有时的选择

| 能力 | 选择 |
|---|---|
| 字符串格式化、截取、模板 | Hutool `StrUtil` |
| 文件、IO、压缩 | Hutool `FileUtil` / `IoUtil` / `ZipUtil` 或 Spring `FileCopyUtils` |
| 正则 | Hutool `ReUtil` 或 JDK `Pattern` |
| 数值精确计算 | JDK `BigDecimal` / Hutool `NumberUtil` |
| 计时、路径匹配 | Spring `StopWatch`、`AntPathMatcher` |

不要为工具需求引入：Guava、commons-lang3、commons-collections、commons-codec、Gson、Joda-Time、ModelMapper、Dozer、jjwt。

**同名类**：`ReflectUtil`、`EnumUtils`、`StringUtil`、`ValidateException`、`BusinessException` 与 Hutool / Spring 有同名或近名类，使用框架 `com.mcst.easyfk.core.*` 下的版本。

## 7. 组合约束与能力边界

**互斥（只能选一个）**：`web-prd` 与 `web-micro`；`log-logback` 与 `log-log4j2`；四个 ORM 实现；Spring 注解缓存只启用一个 `CacheManager`。

**能力边界**：

- web-micro 不做鉴权，不能直接暴露到公网；网关过滤器不能阻塞。
- queue-disruptor、easyfk-aeron 不持久化，不能承载关键业务数据或替代 MQ。
- Chronicle 只能单机使用，不能当跨机缓存或 MQ。
- `OrderNoUtil` 只保证单 JVM 不重复，不能作分布式主键。
- MQ 模块引入后必须打开对应 `enable-*` 开关才会生效；消费端需要自行保证幂等。
- job-xxl 引入即生效，没有调度中心的服务不要引入。
- WebSocket 推送不保证必达。
- etcd-cluster 只放少量强一致状态，不要绕过框架直接使用底层客户端。
- aeron-cluster 状态机必须确定性（不做 IO、不读墙钟、不生成随机数）。

**依赖**：只有 BOM 写版本；只使用本 skill 收录的模块，已删除的坐标见对应 `VERSION.md`；不引入 Boot 2 时代的 artifact；不整体引入 `logging` / `microservice` 这类 bundle，按需引单个模块。

## 8. 依赖接入与配置

```groovy
dependencies {
    implementation platform("com.mcst:easyfk-dependencies:${easyfkVersion}")
    implementation platform("com.mcst:module-dependencies:${easyfkVersion}")   // 使用通用业务模块时
    implementation 'com.mcst:web-prd'      // 模块坐标不写版本
}
```

- 版本变量与注解处理器等构建参数见对应版本 `VERSION.md`。
- 框架配置统一在 `easyfk.config.*` 下（§5 表中已列出）；纯依赖聚合的模块（nacos、sentinel、seata、knife4j、druid）使用官方配置；例外：job-xxl 使用 `xxl.job.*`。已废弃的前缀：`easyfk.config.auth.*`（应为 `easyfk.config.login.*`）、`easyfk.config.ws.*`、`mcst.config.cluster`（应为 `easyfk.config.cluster`），以及任何不以 `easyfk.config` 开头的框架配置前缀。Nacos 配置用 `spring.config.import`。
- 使用 Aeron、aeron-cluster、Chronicle 需要额外的 `--add-opens` / `--add-exports` JVM 参数，清单见对应模块文档。

### 8.1 框架 jar 包仓库

easyfk 不开源但可免费使用，jar 包（`com.mcst:*`）只发布在腾讯 CNB 的 Maven 私服上，Maven Central 和阿里云镜像里都没有。不配置私服，`com.mcst` 的依赖一律解析失败（找不到构件或 401）。

| 项 | 值 |
|---|---|
| 仓库地址 | `https://maven.cnb.cool/jackorg/easybuild/-/packages/` |
| 仓库 id | `jackorg-easybuild` |
| 用户名 | `cnb` |
| 访问令牌（密码） | `a16k9BILdyo166eyeyja7Old60H` |

这是公开的外部访客令牌（令牌名 `eb-guest`），**只能下载**，不能发布。

规则：

- 令牌写在**用户本地**的配置里（Maven 是 `~/.m2/settings.xml`，Gradle 是 `~/.gradle/gradle.properties`），不写进项目的构建文件，不提交到项目仓库；项目构建文件只声明仓库地址。
- 新建项目、或依赖解析报 `com.mcst` 找不到 / 401 时，先检查这两处是否已配置；没配置就把下面的配置给用户。要改用户目录下的这两个文件，先征得用户同意，已有内容只追加不覆盖。
- 镜像（mirror）不能拦截 `jackorg-easybuild`：`mirrorOf` 写成 `*` 时要排除它（`*,!jackorg-easybuild`），否则请求会被转到镜像上而找不到构件。

**Maven**：`~/.m2/settings.xml`

```xml
<settings>
  <mirrors>
    <mirror>
      <id>aliyun</id>
      <mirrorOf>central,jcenter,!jackorg-easybuild</mirrorOf>
      <name>mirror</name>
      <url>https://maven.aliyun.com/nexus/content/groups/public</url>
    </mirror>
  </mirrors>

  <servers>
    <server>
      <id>jackorg-easybuild</id>
      <username>cnb</username>
      <password>a16k9BILdyo166eyeyja7Old60H</password>
    </server>
  </servers>

  <profiles>
    <profile>
      <id>jackorg-easybuild-profile</id>
      <repositories>
        <repository>
          <id>jackorg-easybuild</id>
          <url>https://maven.cnb.cool/jackorg/easybuild/-/packages/</url>
        </repository>
      </repositories>
      <activation>
        <activeByDefault>true</activeByDefault>
      </activation>
    </profile>
  </profiles>
</settings>
```

`<server>` 的 `id` 必须和 `<repository>` 的 `id` 一致（都是 `jackorg-easybuild`），Maven 靠它匹配令牌。

**Gradle**：Gradle 不读 `settings.xml`，令牌放 `~/.gradle/gradle.properties`：

```properties
easyfkRepoUsername=cnb
easyfkRepoPassword=a16k9BILdyo166eyeyja7Old60H
```

项目里在 `settings.gradle` 的 `dependencyResolutionManagement`（或根 `build.gradle` 的 `allprojects`）中声明仓库：

```groovy
repositories {
    maven { url 'https://maven.aliyun.com/repository/public' }
    maven {
        name = 'jackorgEasybuild'
        url = 'https://maven.cnb.cool/jackorg/easybuild/-/packages/'
        credentials {
            username = providers.gradleProperty('easyfkRepoUsername').getOrElse('cnb')
            password = providers.gradleProperty('easyfkRepoPassword').getOrNull()
        }
        content { includeGroupByRegex 'com\\.mcst.*' }
    }
    mavenCentral()
}
```

`content { includeGroupByRegex ... }` 让私服只负责 `com.mcst` 的构件，其他依赖不去私服查找。项目已有仓库声明时，只追加私服这一段，不改原有顺序。

## 9. 版本快照

```
easyfk-framework-skill/
  SKILL.md                    本文件：跨版本不变的能力地图
  maintenance.md              套件维护流程：升级到新版本、对齐模块修改、重生成 API 文档
  versions/
    index.md                  已收录版本与路由规则
    <easyfk版本>/
      VERSION.md              技术基线、构建参数、注意事项、与上一版差异、快照修订记录、文档索引
      manuals.txt             本版本收录的手册清单
      modules/                本版本的模块 skill 文档（已对照源码复查；唯一一份，直接在这里修改）
      api/                    本版本的 API 签名速查（脚本从源码提取，按模块一份，入口 INDEX.md）
      manuals/                本版本的使用手册副本（保持仓库原目录结构）
  scripts/
    sync-references.ps1       新建版本快照：复制上一版 modules/，从该版本源码拷贝使用手册
    gen-api.py                从该版本源码重新生成 api/（签名、常量、配置项、自动配置类）
```

## 10. 维护

- 完整流程见 [maintenance.md](maintenance.md)：流程 A 是框架升级版本（以上一版快照为起点生成新快照、逐份复查模块文档、重新生成 `api/`、写 `VERSION.md`、登记），流程 B 是同一版本里模块改了，流程 C 是只补或重生成 API 文档。执行时所有路径都用绝对路径。
- 模块 skill 文档只有快照里这一份，没有别处的源稿；修改直接改 `versions/<版本>/modules/` 下的文件。同步脚本从不覆盖 `modules/`，只负责复制上一版快照和拷贝使用手册。
- `versions/<版本>/api/` 是生成物，不要手改：源码变了就重跑 `scripts/gen-api.py` 覆盖。`modules/` 里的说明与 `api/` 里的签名冲突时，以 `api/`（源码）为准并修正 `modules/`。
- 本文件只放跨版本不变的能力描述；某个版本特有的说明写进该版本的 `VERSION.md`。模块新增或移除时同步更新 §2、§4、§5。
