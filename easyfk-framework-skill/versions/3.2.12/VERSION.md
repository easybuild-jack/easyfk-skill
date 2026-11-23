# EasyFK 3.2.12 版本说明

> 适用：项目导入的 BOM 为 `com.mcst:easyfk-dependencies:3.2.12`。
> 本目录是 3.2.12 源码对应的文档快照：`modules/` 为对照源码复查过的模块 skill 文档，`api/` 为脚本从源码提取的签名速查，`manuals/` 为使用手册副本（清单见 `manuals.txt`）。下文出现的版本号只对 3.2.12 有效。

## 1. 技术基线

| 项 | 版本 / 约定 |
|---|---|
| JDK | 21（`-parameters` 编译参数，SpEL 依赖它） |
| Spring Boot / Cloud / Cloud Alibaba | 3.2.12 / 2023.0.5 / 2023.0.3.3（三者配套，只能一起升） |
| Web 容器 | Undertow（web-simple 排除了 Tomcat），jakarta 命名空间 |
| 关键三方 | MyBatis-Plus 3.5.14、Redisson 3.40.2、fastjson2 2.0.58、Hutool 5.8.40、mapstruct-plus 1.5.0、Dubbo 3.3.5、RocketMQ starter 2.3.4、xxl-job 3.2.0、Knife4j 4.5.0、Fory 1.3.0、Aeron 1.52.1、jetcd 0.8.6（shaded）、Seata 2.1.0（`org.apache.seata`） |

完整第三方清单与生效版本见 [easyfk-dependencies-skill.md](modules/easyfk-dependencies-skill.md)。项目里实际生效的版本以 Gradle / Maven 解析出的依赖树为准。

## 2. 构建参数

`SKILL.md` §8 模板中引用的变量，在本版本下取值如下（写入业务项目的 `gradle.properties`）：

```properties
easyfkVersion=3.2.12
mapstructPlusVersion=1.5.0
lombokMapstructBindingVersion=0.2.0
```

Lombok、`spring-boot-configuration-processor` 由 BOM 管理，通过 `annotationProcessor platform(...)` 取得版本，不单独写。

## 3. 本版本的注意事项

- 缓存只使用 `cache-redis` 与 `cache-caffeine`；本 skill 未收录的组件不要在新代码中使用。
- **`cache-mult`（XXL-CACHE 多级缓存）与 `db-influx`（InfluxDB 时序库）已下线**：两个版本快照都不再收录，`modules/`、`api/`、`manuals/` 中相关内容均已移除；多级缓存用 `LocalCacheManager` + `ICacheService` 自行组合，时序库自行引入 `influxdb-client-java`。
- 已删除、不要引用的坐标：`easyfk-doc`、`easyfk-lock`、`easyfk-mq`、`easyfk-resource`、`resource-*`、`lock-zk`、`tool-http`、`tool-excel`、`component-autoId`、`gateway-gateway`、`doc-micro`、`storage-chronicle`、`datasource-druid`、`ws-api`、`ws-server`、`autoId-tradition`。
- `orm-sharding` 依赖的 ShardingSphere 5.2.1 与 Boot 3.2 管理的 SnakeYAML 2.x 存在兼容风险，详见 [orm](modules/easyfk-component-orm-skill.md)。
- Chronicle 使用 EA（预览）版本，见 [chronicle](modules/easyfk-component-chronicle-skill.md)。
- 文档覆盖范围：module-dependencies 只在 `SKILL.md` 中做概要说明；aeron-coord、easyfk-flink 未纳入。

## 4. 快照修订记录

以下修改只在本快照中做过，源码仓库里的原手册未改；用 `-Force` 重新拷贝 `manuals/` 前需要先在原手册中同步这些修改，否则会丢失。`modules/` 不受影响（脚本从不覆盖）；`api/` 是生成物，源码变了重跑脚本覆盖即可，不需要手工修，也不在此记录。

| 文件 | 修改 |
|---|---|
| `manuals/easyfk-dependencies/dependencies开发手册.md` | 删除 cache-mult、xxl-cache、xxl-mq 相关行；删除 `db-influx`、`influxdb-client-java` 坐标行，`database` / `cache` bundle 行同步去掉这两个模块 |
| `manuals/easyfk-component/易架构组件项目说明文档.md` | 删除 cache-mult、mq-xxl 相关行与小节；删除 `db-influx` 的表格行、场景行与整节，架构图去掉这两个模块名 |
| `manuals/easyfk-component/component-lock/lock-redisson/lock-redisson开发手册.md` | 配置前缀改为 `easyfk.config.lock.redisson` |
| `manuals.txt` | 移除 cache-mult 开发手册 |

> **后续变更：`cache-mult` 与 `db-influx` 下线。** 这两个子模块已不再使用，两个版本快照都不再收录：
> `gen-api.py` 用 `REMOVED_MODULES` 统一裁剪（cache 14 → 9 类型、db 55 → 47 类型），`api/INDEX.md` 增加「已下线的子模块」一节；
> `modules/easyfk-component-cache-skill.md` 删掉文首的 cache-mult 说明，`modules/easyfk-component-db-skill.md` 删掉 db-influx 整章并重排章节号；
> `manuals/` 与 `manuals.txt` 中对应的手册与过时行也已清理。此前"cache-mult 用法指向 3.5.16 文档"的说法作废。

## 5. 文档索引

可信度顺序：源码 > `api/*.api.md`（签名）与 `modules/*-skill.md`（用法）> `manuals/*`。手册中有过时 API（尤其 `EasyFK框架开发手册.md` §3、§4、§6 的代码示例），差异已列在各 skill 文档末尾的「复查记录」中，冲突时按 skill 文档写。

### 5.1 模块 skill 文档（`modules/`，已对照源码复查，优先阅读）

| 范围 | 文档 |
|---|---|
| 核心 | [core](modules/easyfk-core-skill.md)、[工具类选用](modules/easyfk-core-toolkit-skill.md)、[log](modules/easyfk-log-skill.md)、[serializer](modules/easyfk-serializer-skill.md)、[thread](modules/easyfk-thread-skill.md)、[queue](modules/easyfk-queue-skill.md) |
| 数据与服务 | [cache 接口](modules/easyfk-cache-skill.md)、[repository](modules/easyfk-repository-skill.md)、[service](modules/easyfk-service-skill.md)、[remote](modules/easyfk-remote-skill.md) |
| Web 与安全 | [web](modules/easyfk-web-skill.md)、[authority](modules/easyfk-authority-skill.md)、[gateway](modules/easyfk-gateway-skill.md) |
| 组件 | [db](modules/easyfk-component-db-skill.md)、[cache](modules/easyfk-component-cache-skill.md)、[autoId](modules/easyfk-component-autoId-skill.md)、[lock](modules/easyfk-component-lock-skill.md)、[orm](modules/easyfk-component-orm-skill.md)、[ds](modules/easyfk-component-ds-skill.md)、[mq](modules/easyfk-component-mq-skill.md)、[rpc](modules/easyfk-component-rpc-skill.md)、[chronicle](modules/easyfk-component-chronicle-skill.md)、[websocket](modules/easyfk-component-websocket-skill.md)、[job](modules/easyfk-component-job-skill.md)、[infra](modules/easyfk-component-infra-skill.md) |
| 依赖 | [dependencies（第三方组件与版本）](modules/easyfk-dependencies-skill.md) |
| 独立工程 | [easyfk-aeron](modules/easyfk-aeron-skill.md)、[aeron-cluster](modules/aeron-cluster-skill.md)、[etcd-cluster](modules/etcd-cluster-skill.md) |

### 5.2 API 签名速查（`api/`，脚本从源码提取，查精确签名用）

入口：[api/INDEX.md](api/INDEX.md)。每个模块一份，内容为 public / protected 成员签名、常量与枚举取值、`@ConfigurationProperties` 配置项（含默认值）、`@interface` 属性、自动配置类清单。只查签名，用法仍看 `modules/`。

| 模块 | API | 模块 | API |
|---|---|---|---|
| core（含 toolkit） | [core](api/easyfk-core.api.md) | 组件 db | [db](api/easyfk-component-db.api.md) |
| serializer | [serializer](api/easyfk-serializer.api.md) | 组件 cache | [cache](api/easyfk-component-cache.api.md) |
| thread | [thread](api/easyfk-thread.api.md) | 组件 autoId | [autoId](api/easyfk-component-autoId.api.md) |
| queue | [queue](api/easyfk-queue.api.md) | 组件 lock | [lock](api/easyfk-component-lock.api.md) |
| cache 抽象 | [cache](api/easyfk-cache.api.md) | 组件 orm | [orm](api/easyfk-component-orm.api.md) |
| repository | [repository](api/easyfk-repository.api.md) | 组件 mq | [mq](api/easyfk-component-mq.api.md) |
| service | [service](api/easyfk-service.api.md) | 组件 rpc | [rpc](api/easyfk-component-rpc.api.md) |
| remote | [remote](api/easyfk-remote.api.md) | 组件 chronicle | [chronicle](api/easyfk-component-chronicle.api.md) |
| web | [web](api/easyfk-web.api.md) | 组件 websocket | [websocket](api/easyfk-component-websocket.api.md) |
| authority | [authority](api/easyfk-authority.api.md) | 组件 job | [job](api/easyfk-component-job.api.md) |
| gateway | [gateway](api/easyfk-gateway.api.md) | 独立工程 aeron | [aeron](api/easyfk-aeron.api.md) |
| 独立工程 aeron-cluster | [aeron-cluster](api/aeron-cluster.api.md) | 独立工程 etcd-cluster | [etcd-cluster](api/etcd-cluster.api.md) |

`easyfk-log`、`easyfk-component-ds`、`easyfk-component-infra`、`easyfk-dependencies` 没有自有 Java API（纯配置或依赖聚合），原因见 [api/INDEX.md](api/INDEX.md)。`easyfk-aeron`、`aeron-cluster`、`etcd-cluster` 是独立仓库，生成时需与本版本源码检出在同一目录下；`aeron-examples` 不参与提取。

### 5.3 使用手册（`manuals/`，保持仓库原目录结构）

| 范围 | 手册 |
|---|---|
| 总览 | [框架开发手册](manuals/easyfk-base/EasyFK框架开发手册.md)（API 示例多处过时）、[核心模块说明](manuals/easyfk-base/核心模块说明.md)、[组件项目说明](manuals/easyfk-component/易架构组件项目说明文档.md)、[dependencies 开发手册](manuals/easyfk-dependencies/dependencies开发手册.md) |
| base | [core](manuals/easyfk-base/easyfk-core/core开发文档.md)、[thread](manuals/easyfk-base/easyfk-thread/thread开发手册.md)、[disruptor](manuals/easyfk-base/easyfk-queue/queue-disruptor/disruptor使用手册.md)、[fory](manuals/easyfk-base/easyfk-serializer/serializer-fory/fory序列化使用手册.md)、[auth](manuals/easyfk-base/easyfk-authority/auth开发文档.md)、[web-prd](manuals/easyfk-base/easyfk-web/web-prd/web-prd开发手册.md)、[web-micro](manuals/easyfk-base/easyfk-web/web-micro/web-micro开发手册.md)、[gateway](manuals/easyfk-base/easyfk-gateway/gateway开发文档.md) |
| db | [db-redis](manuals/easyfk-component/component-db/db-redis/db-redis开发手册.md)、[db-mongo](manuals/easyfk-component/component-db/db-mongo/db-mongo开发手册.md)、[db-clickhouse](manuals/easyfk-component/component-db/db-clickhouse/db-clickhouse开发手册.md) |
| cache / id / lock | [cache-redis](manuals/easyfk-component/component-cache/cache-redis/cache-redis-开发手册.md)、[cache-caffeine](manuals/easyfk-component/component-cache/cache-caffeine/Cache-Caffeine开发手册.md)、[autoId-redis](manuals/easyfk-component/component-autoId/autoId-redis/AutoId-Redis开发手册.md)、[lock-redisson](manuals/easyfk-component/component-lock/lock-redisson/lock-redisson开发手册.md) |
| orm | [mybatis](manuals/easyfk-component/component-orm/orm-mybatis/orm-mybatis开发手册.md)、[flex](manuals/easyfk-component/component-orm/orm-flex/orm-flex开发手册.md)、[hibernate](manuals/easyfk-component/component-orm/orm-hibernate/orm-hibernate开发手册.md)、[sharding](manuals/easyfk-component/component-orm/orm-sharding/orm-sharding开发手册.md) |
| mq | [mq-rocket](manuals/easyfk-component/component-mq/mq-rocket/mq-rocket开发手册.md)、[RocketMQ 教程](manuals/easyfk-component/component-mq/mq-rocket/RocketMQ使用教程.md)、[mq-rabbit](manuals/easyfk-component/component-mq/mq-rabbit/mq-rabbit开发手册.md)、[RabbitMQ 教程](manuals/easyfk-component/component-mq/mq-rabbit/RabbitMQ使用教程.md)、[mq-kafka](manuals/easyfk-component/component-mq/mq-kafka/mq-kafka使用教程.md) |
| rpc | [rpc-cloud](manuals/easyfk-component/component-rpc/rpc-cloud/rpc-cloud开发手册.md)、[rpc-dubbo](manuals/easyfk-component/component-rpc/rpc-dubbo/rpc-dubbo开发手册.md) |
| 存储 / 推送 / 任务 | [chronicle-map](manuals/easyfk-component/component-chronicle/chronicle-map/chronicle-map使用手册.md)、[chronicle-queue](manuals/easyfk-component/component-chronicle/chronicle-queue/chronicle-queue-使用手册.md)、[websocket](manuals/easyfk-component/component-websocket/websocket-server/websocket开发文档.md)、[websocket 前端对接](manuals/easyfk-component/component-websocket/websocket-server/websocket前端对接文档.md)、[XXL-JOB](manuals/easyfk-component/component-job/job-xxl/XXL-JOB组件使用手册.md) |
| aeron | [使用手册](<manuals/easyfk-aeron/docs/Aeron 组件使用手册.md>)、[Chronicle 状态存储](<manuals/easyfk-aeron/docs/Aeron Chronicle 状态存储指南.md>)、[Codec 接入](manuals/easyfk-aeron/docs/序列化Codec接入指南.md)、[监控](manuals/easyfk-aeron/docs/监控指南.md)、[跨语言互通](manuals/easyfk-aeron/docs/跨语言互通指南.md)、[协议说明](manuals/easyfk-aeron/docs/aeron协议说明.md) |
| 集群 | [aeron-cluster 使用手册](manuals/aeron-cluster/docs/Cluster使用手册.md)、[etcd 集群使用文档](manuals/etcd-cluster/docs/etcd集群使用文档.md) |
