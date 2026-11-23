# easyfk 3.2.12 API 签名速查索引

> 本目录由 `scripts/gen-api.py` 从该版本源码自动提取，**只放签名与常量值**，不含用法说明。需要“怎么写、为什么、注意事项”时读 [../modules/](../modules/) 下对应的 skill 文档。

## 什么时候读 API 文档

| 场景 | 读这个 |
|---|---|
| 不确定某个类有哪些方法、重载顺序、参数类型 | 本目录对应模块的 `*.api.md` |
| 需要常量 / 枚举的具体取值（错误码、请求头名、枚举 code） | 同上，看「字段 / 常量」「枚举常量」 |
| 需要配置项的完整清单和默认值 | 同上，看文首「配置项（@ConfigurationProperties）」 |
| 需要知道某个注解标在类上还是字段上、有哪些属性 | 同上，注解类型在 `## 包` 下的 `@interface` 条目 |
| 需要知道引入某个模块后哪些类会自动生效 | 同上，「自动配置类（引入即生效）」 |
| 需要判断某个能力是否存在（避免凭记忆编 API） | 先查本目录，查不到就是没有 |

## 模块 → API 文件

| 模块 | 坐标 | 类型数 | 源文件数 | API 文档 | 用法文档 |
|---|---|---|---|---|---|
| easyfk-core | `com.mcst:easyfk-core` | 63 | 63 | [easyfk-core.api.md](easyfk-core.api.md) | [easyfk-core-skill.md](../modules/easyfk-core-skill.md) |
| easyfk-serializer | `com.mcst:serializer-base、com.mcst:serializer-fory` | 10 | 10 | [easyfk-serializer.api.md](easyfk-serializer.api.md) | [easyfk-serializer-skill.md](../modules/easyfk-serializer-skill.md) |
| easyfk-thread | `com.mcst:easyfk-thread` | 24 | 25 | [easyfk-thread.api.md](easyfk-thread.api.md) | [easyfk-thread-skill.md](../modules/easyfk-thread-skill.md) |
| easyfk-queue | `com.mcst:queue-disruptor` | 15 | 15 | [easyfk-queue.api.md](easyfk-queue.api.md) | [easyfk-queue-skill.md](../modules/easyfk-queue-skill.md) |
| easyfk-cache | `com.mcst:easyfk-cache` | 1 | 1 | [easyfk-cache.api.md](easyfk-cache.api.md) | [easyfk-cache-skill.md](../modules/easyfk-cache-skill.md) |
| easyfk-repository | `com.mcst:easyfk-repository` | 16 | 16 | [easyfk-repository.api.md](easyfk-repository.api.md) | [easyfk-repository-skill.md](../modules/easyfk-repository-skill.md) |
| easyfk-service | `com.mcst:service-api、com.mcst:service-base` | 8 | 8 | [easyfk-service.api.md](easyfk-service.api.md) | [easyfk-service-skill.md](../modules/easyfk-service-skill.md) |
| easyfk-remote | `com.mcst:remote-cloud、com.mcst:remote-dubbo` | 12 | 12 | [easyfk-remote.api.md](easyfk-remote.api.md) | [easyfk-remote-skill.md](../modules/easyfk-remote-skill.md) |
| easyfk-web | `com.mcst:web-simple、web-base、web-common、web-prd、web-micro` | 56 | 56 | [easyfk-web.api.md](easyfk-web.api.md) | [easyfk-web-skill.md](../modules/easyfk-web-skill.md) |
| easyfk-authority | `com.mcst:easyfk-authority` | 21 | 21 | [easyfk-authority.api.md](easyfk-authority.api.md) | [easyfk-authority-skill.md](../modules/easyfk-authority-skill.md) |
| easyfk-gateway | `com.mcst:easyfk-gateway` | 9 | 9 | [easyfk-gateway.api.md](easyfk-gateway.api.md) | [easyfk-gateway-skill.md](../modules/easyfk-gateway-skill.md) |
| easyfk-component-db | `com.mcst:db-redis、db-mongo、db-clickhouse` | 47 | 47 | [easyfk-component-db.api.md](easyfk-component-db.api.md) | [easyfk-component-db-skill.md](../modules/easyfk-component-db-skill.md) |
| easyfk-component-cache | `com.mcst:cache-redis、cache-caffeine` | 9 | 9 | [easyfk-component-cache.api.md](easyfk-component-cache.api.md) | [easyfk-component-cache-skill.md](../modules/easyfk-component-cache-skill.md) |
| easyfk-component-autoId | `com.mcst:autoId-api、autoId-redis` | 4 | 4 | [easyfk-component-autoId.api.md](easyfk-component-autoId.api.md) | [easyfk-component-autoId-skill.md](../modules/easyfk-component-autoId-skill.md) |
| easyfk-component-lock | `com.mcst:lock-redisson` | 7 | 7 | [easyfk-component-lock.api.md](easyfk-component-lock.api.md) | [easyfk-component-lock-skill.md](../modules/easyfk-component-lock-skill.md) |
| easyfk-component-orm | `com.mcst:orm-mybatis、orm-flex、orm-hibernate、orm-sharding` | 45 | 45 | [easyfk-component-orm.api.md](easyfk-component-orm.api.md) | [easyfk-component-orm-skill.md](../modules/easyfk-component-orm-skill.md) |
| easyfk-component-mq | `com.mcst:mq-common、mq-rocket、mq-rabbit、mq-kafka` | 33 | 34 | [easyfk-component-mq.api.md](easyfk-component-mq.api.md) | [easyfk-component-mq-skill.md](../modules/easyfk-component-mq-skill.md) |
| easyfk-component-rpc | `com.mcst:rpc-cloud、rpc-dubbo` | 6 | 6 | [easyfk-component-rpc.api.md](easyfk-component-rpc.api.md) | [easyfk-component-rpc-skill.md](../modules/easyfk-component-rpc-skill.md) |
| easyfk-component-chronicle | `com.mcst:chronicle-map、chronicle-queue` | 31 | 36 | [easyfk-component-chronicle.api.md](easyfk-component-chronicle.api.md) | [easyfk-component-chronicle-skill.md](../modules/easyfk-component-chronicle-skill.md) |
| easyfk-component-websocket | `com.mcst:websocket-server、websocket-api` | 34 | 34 | [easyfk-component-websocket.api.md](easyfk-component-websocket.api.md) | [easyfk-component-websocket-skill.md](../modules/easyfk-component-websocket-skill.md) |
| easyfk-component-job | `com.mcst:job-xxl` | 7 | 7 | [easyfk-component-job.api.md](easyfk-component-job.api.md) | [easyfk-component-job-skill.md](../modules/easyfk-component-job-skill.md) |
| easyfk-aeron | `com.mcst:aeron-common、aeron-producer、aeron-consumer、aeron-store、aeron-chronicle、aeron-codec-*、aeron-compression-*、aeron-metrics-micrometer、aeron-spring-boot-starter` | 130 | 143 | [easyfk-aeron.api.md](easyfk-aeron.api.md) | [easyfk-aeron-skill.md](../modules/easyfk-aeron-skill.md) |
| aeron-cluster | `com.mcst:aeron-cluster-core、aeron-cluster-client、aeron-cluster-spring-boot-starter` | 76 | 97 | [aeron-cluster.api.md](aeron-cluster.api.md) | [aeron-cluster-skill.md](../modules/aeron-cluster-skill.md) |
| etcd-cluster | `com.mcst:etcd-cluster-api、etcd-cluster-core、etcd-cluster-spring-boot-starter` | 40 | 51 | [etcd-cluster.api.md](etcd-cluster.api.md) | [etcd-cluster-skill.md](../modules/etcd-cluster-skill.md) |
| easyfk-log | `—` | 0 | 0 | 无 Java API | [easyfk-log-skill.md](../modules/easyfk-log-skill.md) |
| easyfk-component-ds | `—` | 0 | 0 | 无 Java API | [easyfk-component-ds-skill.md](../modules/easyfk-component-ds-skill.md) |
| easyfk-component-infra | `—` | 0 | 0 | 无 Java API | [easyfk-component-infra-skill.md](../modules/easyfk-component-infra-skill.md) |
| easyfk-dependencies | `—` | 0 | 0 | 无 Java API | [easyfk-dependencies-skill.md](../modules/easyfk-dependencies-skill.md) |

`easyfk-core-toolkit`（工具类选用规则）与 `easyfk-core` 是同一批类，签名统一看 [easyfk-core.api.md](easyfk-core.api.md)。

## 已下线的子模块

以下子模块框架已不再提供，`modules/` 用法文档与 `api/` 签名均不收录（源码目录里可能还留有代码，但不要在新项目中使用）：

- `db-influx`
- `cache-mult`

## 没有 Java API 的模块

- **easyfk-log**：`log-logback` / `log-log4j2` 只含日志配置文件，没有 Java API；配置项见 [../modules/easyfk-log-skill.md](../modules/easyfk-log-skill.md)。
- **easyfk-component-ds**：`ds-druid` 只做依赖聚合，没有自有 Java API；使用 Druid 官方配置。
- **easyfk-component-infra**：`config-nacos` / `registry-nacos` / `protect-sentinel` / `transaction-seata` / `doc-knife4j` 只做依赖聚合，没有自有 Java API。
- **easyfk-dependencies**：BOM 工程，只有版本约束，没有 Java API；版本清单见 [../modules/easyfk-dependencies-skill.md](../modules/easyfk-dependencies-skill.md)。

## 生成范围说明

- **easyfk-aeron**：`aeron-examples` 是示例工程，不参与 API 提取；示例用法见模块文档与 `manuals/easyfk-aeron/`。

## 与 modules/ 的关系

| 文档 | 内容 | 可信度 |
|---|---|---|
| `modules/*-skill.md` | 模块定位、引入方式、配置、用法、坑、复查记录 | 已逐行对照源码复查 |
| `api/*.api.md` | 类 / 方法 / 字段 / 枚举常量 / 配置项签名清单 | 脚本从源码提取，签名与源码一致 |
| `manuals/*` | 框架原厂手册 | 有历史过时内容 |

两者冲突时以源码为准，并修正 `modules/` 中的说明（API 文件重新生成即可）。

## 重新生成

源码有改动、或新增版本快照时，在套件目录下执行（Windows 示例）：

```
python scripts/gen-api.py --version 3.2.12 --repo-root "<该版本源码绝对路径>"
```

脚本只读源码，覆盖本目录下的 `*.api.md` 与 `INDEX.md`，不改 `modules/`。
新增或改名模块时，同步修改脚本顶部的 `MODULES` 映射表。

`easyfk-aeron`、`aeron-cluster`、`etcd-cluster` 是各自独立的 Git 仓库，需分别检出到同一个 `repo-root` 下（目录名与映射表一致），否则这三个模块会被跳过。
