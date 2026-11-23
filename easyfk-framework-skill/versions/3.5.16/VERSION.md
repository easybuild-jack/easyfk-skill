# EasyFK 3.5.16 版本说明

> 适用：项目导入的 BOM 为 `com.mcst:easyfk-dependencies:3.5.16`。
> 本目录是 3.5.16 源码对应的文档快照：`modules/` 为对照源码复查过的模块 skill 文档，`api/` 为脚本从源码提取的签名速查，`manuals/` 为使用手册副本（清单见 `manuals.txt`）。下文出现的版本号只对 3.5.16 有效。

## 1. 技术基线

| 项 | 版本 / 约定 |
|---|---|
| JDK | 21（源码 `sourceCompatibility` / `targetCompatibility = 21`）；业务工程编译必须带 `-parameters`，框架的 SpEL 与参数名解析依赖它 |
| Spring Boot / Cloud / Cloud Alibaba | 3.5.16 / 2025.0.3 / 2025.0.0.0（三者配套，只能一起升） |
| Web 容器 | Undertow（web-simple 排除了 Tomcat），jakarta 命名空间 |
| 关键三方 | MyBatis-Plus 3.5.18.1、MyBatis-Flex 1.11.8、ShardingSphere 5.5.3、Redisson 3.52.0、fastjson2 2.0.66、Hutool 5.8.48、mapstruct-plus 1.5.3、Dubbo 3.3.7、RocketMQ starter 2.3.6、xxl-job 3.3.0、Knife4j 4.5.0 + springdoc 2.10.0、Fory 1.7.8、Aeron 1.54.2 / Agrona 2.7.1 / SBE 1.42.0、jetcd 0.8.8（shaded）、Seata 2.x（`org.apache.seata`，随 SCA 传递）、Chronicle 2026.2 / 2026.8、Druid 1.2.28、Lombok 1.18.46 |

完整第三方清单与「为什么停在这个版本」的说明见 [easyfk-dependencies-skill.md](modules/easyfk-dependencies-skill.md)。项目里实际生效的版本以 Gradle / Maven 解析出的依赖树为准。

## 2. 构建参数

`SKILL.md` §8 模板中引用的变量，在本版本下取值如下（写入业务项目的 `gradle.properties`）：

```properties
easyfkVersion=3.5.16
mapstructPlusVersion=1.5.3
lombokMapstructBindingVersion=0.2.0
```

Lombok、`spring-boot-configuration-processor` 由 BOM 管理，通过 `annotationProcessor platform(...)` 取得版本，不单独写。

## 3. 从 3.2.12 升级时的差异

这一节是升级必读。3.5.16 不只是版本号变化，下面几项会直接导致编译失败或启动失败。

| # | 变化 | 影响 / 处理 |
|---|---|---|
| 1 | **MyBatis-Plus 3.5.14 → 3.5.18.1，包名迁移** | `Model`（ActiveRecord）与 `ServiceImpl` 从 `com.baomidou.mybatisplus.extension.*` 迁到 `com.baomidou.mybatisplus.spring.*`。业务代码里 `extends Model<T>` / `extends ServiceImpl<M,T>` 的 import 必须改，见 [orm](modules/easyfk-component-orm-skill.md) |
| 2 | **orm-sharding 从 starter 5.2.1 改为 `ShardingSphereDriver` + 5.5.3** | `spring.shardingsphere.*` 配置前缀废弃，改为规则文件 + `jdbc:shardingsphere:classpath:xxx.yaml`；单表需 `!SINGLE` 声明、广播表改为 `!BROADCAST`。**不是零改动升级**，见 [orm](modules/easyfk-component-orm-skill.md) §5 |
| 3 | **Knife4j 4.5.0 自带的 springdoc 2.3.0 在 Boot 3.5 上启动失败** | BOM 已强制 `springdoc 2.10.0`，业务工程不要手工降级；`/v3/api-docs` 相关配置不变，见 [infra](modules/easyfk-component-infra-skill.md) |
| 4 | **Fory 1.3.0 → 1.7.8，`ForySerializer` 重写** | 注册后需重建 `Fory` 实例；虚拟线程与平台线程使用不同的实例策略；固定 ClassLoader，见 [serializer](modules/easyfk-serializer-skill.md) |
| 5 | **Aeron 1.52.1 → 1.54.2、Agrona 2.5.0 → 2.7.1** | 第三方版本改由 BOM 的 `aeronRuntime` bundle 统一约束，独立工程 catalog 不再写版本。`easyfk-aeron` 与 `aeron-cluster` **必须同版本**，见 [aeron](modules/easyfk-aeron-skill.md)、[aeron-cluster](modules/aeron-cluster-skill.md) |
| 6 | **Spring Cloud 2023.0.5 → 2025.0.3、SCA 2023.0.3.3 → 2025.0.0.0** | Nacos / Sentinel / Seata 的传递版本随之变化；Seata 用 `org.apache.seata.*`，旧的 `io.seata.*` 需批量替换，见 [infra](modules/easyfk-component-infra-skill.md) |
| 7 | **xxl-job 3.2.0 → 3.3.0** | 停在 3.3.0（3.3.1+ 基于 Spring Boot 4 / Spring 7）。`xxl.job.*` 前缀与 `@XxlJob` 机制不变，见 [job](modules/easyfk-component-job-skill.md) |
| 8 | **Chronicle 从 EA 预览版转为 GA 日历版本** | `chronicle-map 2026.2` / `chronicle-queue 2026.8` / `affinity 2026.2`，JDK 21 仍需 `--add-opens`，见 [chronicle](modules/easyfk-component-chronicle-skill.md) |
| 9 | **`cache-mult`（XXL-CACHE 多级缓存）与 `db-influx`（InfluxDB）两个子模块下线** | 这两个子模块已不再使用，两个版本快照都不再收录：`modules/` 的用法章节、`api/` 的签名（`XxlCacheFactory` / `InfluxDBConfig` / `BaseFluxRepositoryImpl` / `FluxSearchCondition` 等）与 `manuals/` 手册全部移除。多级缓存改用 `LocalCacheManager` + `ICacheService` 自行组合；时序库自行引入 `influxdb-client-java`。BOM 里的 `influxdb`、`xxl-cache-core` 别名仍在，但没有 easyfk 模块引用，见 [dependencies](modules/easyfk-dependencies-skill.md) |
| 10 | **Redisson 停在 3.52.0** | 4.x 依赖 Netty 4.2，Boot 3.5 基线是 Netty 4.1。不要在业务工程里升到 4.x |

## 4. 本版本的注意事项

- 缓存只有 `cache-redis`（`ICacheService` 唯一实现 + `RedisCacheManager`）与 `cache-caffeine`（本地缓存）两个子模块；`cache-mult` 与 `db-influx` 已下线，不要再引用其坐标与类名。
- 已删除、不要引用的坐标：`easyfk-doc`、`easyfk-lock`、`easyfk-mq`、`easyfk-resource`、`resource-*`、`lock-zk`、`tool-http`、`tool-excel`、`component-autoId`、`gateway-gateway`、`doc-micro`、`storage-chronicle`、`datasource-druid`、`ws-api`、`ws-server`、`autoId-tradition`。
- `orm-sharding` 的 5.5.3 驱动方式要求**物理表先建好**（启动时加载真实表元数据），且分片算法里 `MOD` / `HASH_MOD` 等自动算法只能配在 `autoTables` 上。
- `doc-knife4j` 的 Knife4j 4.5.0 自身未跟进 Boot 3.5，只有 `doc.html` 静态页面可用；UI 兼容有问题时改用 `springdocWebmvcApi` + `springdocWebmvcUi`。
- 文档覆盖范围：module-dependencies 只在 `SKILL.md` 中做概要说明；aeron-coord、easyfk-flink 未纳入。

## 5. 快照修订记录

以下修改只在本快照中做过，源码仓库里的原手册未改；用 `-Force` 重新拷贝 `manuals/` 前需要先在原手册中同步这些修改，否则会丢失。`modules/` 不受影响（脚本从不覆盖）；`api/` 是生成物，源码变了重跑脚本覆盖即可，不需要手工修，也不在此记录。

| 文件 | 修改 |
|---|---|
| `manuals/easyfk-component/component-lock/lock-redisson/lock-redisson开发手册.md` | 配置前缀 `flopotech.config.lock.redisson` → `easyfk.config.lock.redisson`（5 处），沿用 3.2.12 快照的修正 |
| `manuals.txt` | 移除 `cache-mult-开发手册.md`（`cache-mult` 子模块下线，手册副本一并删除） |
| `manuals/easyfk-dependencies/dependencies开发手册.md` | 删除 `db-influx`、`cache-mult`、`influxdb-client-java` 坐标行，`database` / `cache` bundle 行同步去掉这两个模块 |
| `manuals/easyfk-component/易架构组件项目说明文档.md` | 删除 `cache-mult`、`db-influx` 的表格行、场景行与整节，架构图去掉这两个模块名 |

> 这两份总览手册里的 `xxl-mq` 行仍按仓库原样保留（本框架未使用 xxl-mq，读到可忽略）；`cache-mult`、`db-influx` 相关的行与小节已随模块下线删除。

## 6. 文档索引

可信度顺序：源码 > `api/*.api.md`（签名）与 `modules/*-skill.md`（用法）> `manuals/*`。手册中有过时 API（尤其 `EasyFK框架开发手册.md` §3、§4、§6 的代码示例），差异已列在各 skill 文档末尾的「复查记录」中，冲突时按 skill 文档写。

### 6.1 模块 skill 文档（`modules/`，已对照源码复查，优先阅读）

| 范围 | 文档 |
|---|---|
| 核心 | [core](modules/easyfk-core-skill.md)、[工具类选用](modules/easyfk-core-toolkit-skill.md)、[log](modules/easyfk-log-skill.md)、[serializer](modules/easyfk-serializer-skill.md)、[thread](modules/easyfk-thread-skill.md)、[queue](modules/easyfk-queue-skill.md) |
| 数据与服务 | [cache 接口](modules/easyfk-cache-skill.md)、[repository](modules/easyfk-repository-skill.md)、[service](modules/easyfk-service-skill.md)、[remote](modules/easyfk-remote-skill.md) |
| Web 与安全 | [web](modules/easyfk-web-skill.md)、[authority](modules/easyfk-authority-skill.md)、[gateway](modules/easyfk-gateway-skill.md) |
| 组件 | [db](modules/easyfk-component-db-skill.md)、[cache](modules/easyfk-component-cache-skill.md)、[autoId](modules/easyfk-component-autoId-skill.md)、[lock](modules/easyfk-component-lock-skill.md)、[orm](modules/easyfk-component-orm-skill.md)、[ds](modules/easyfk-component-ds-skill.md)、[mq](modules/easyfk-component-mq-skill.md)、[rpc](modules/easyfk-component-rpc-skill.md)、[chronicle](modules/easyfk-component-chronicle-skill.md)、[websocket](modules/easyfk-component-websocket-skill.md)、[job](modules/easyfk-component-job-skill.md)、[infra](modules/easyfk-component-infra-skill.md) |
| 依赖 | [dependencies（第三方组件与版本）](modules/easyfk-dependencies-skill.md) |
| 独立工程 | [easyfk-aeron](modules/easyfk-aeron-skill.md)、[aeron-cluster](modules/aeron-cluster-skill.md)、[etcd-cluster](modules/etcd-cluster-skill.md) |

### 6.2 API 签名速查（`api/`，脚本从源码提取，查精确签名用）

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

### 6.3 使用手册（`manuals/`，保持仓库原目录结构）

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
