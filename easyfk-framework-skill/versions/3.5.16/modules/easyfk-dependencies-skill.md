# easyfk-dependencies Skill 参考文档（第三方组件）

> 所属项目：`easyfk-dependencies`（独立 Gradle 工程，`java-platform` + `allowDependencies()`）
> 坐标：`com.mcst:easyfk-dependencies:3.5.16`
> 依据：`settings.gradle`（version catalog）、`build.gradle`（platform + constraints）、base / component / aeron / aeron-cluster / etcd-cluster 各模块 `build.gradle`；对齐 `dependencies开发手册.md`、`dependencies特点说明.md`。
> 版本列取自 catalog 的声明值。**实际解析版本可能更高**：Spring Boot / Cloud / SCA 平台与 BOM 约束同时生效时 Gradle 取较高者。要确认项目里的实际版本，以 `gradle dependencies` 结果为准。
> 本文只汇总**第三方组件**；`com.mcst` 内部模块见各模块 skill 文档，坐标问题见文末「复查记录」。

---

## 1. 工作机制

- `build.gradle` 先以 `api platform(...)` 导入三个框架级 BOM，再在 `constraints {}` 里逐个 `api(libs.bundles.xxx)` / `api(libs.xxx)` 输出版本约束。
- **只有进了 `constraints` 的别名才会被约束**。catalog 里定义了但没进任何 bundle、也没单独 `api(libs.xxx)` 的库，下游拿到的是 Spring Boot 平台的版本，或者根本没有版本。新增别名时必须同时放进某个 bundle。
- BOM 版本低于 Spring Boot 管理的版本时不起作用（Gradle 取较高者），所以 BOM 里的版本应不低于 Boot 的版本。
- BOM 只提供版本，不引入依赖；下游必须显式声明依赖坐标（不写版本）。
- 下游写法：`implementation platform('com.mcst:easyfk-dependencies:3.5.16')`；Maven 用 `<dependencyManagement>` + `<type>pom</type><scope>import</scope>`。
- 本版本把 `easyfk-aeron` / `aeron-cluster` / `etcd-cluster` 的坐标和它们的第三方运行时（Aeron / Agrona / SBE / LZ4 / Zstd）也纳入了 BOM，独立工程不再自己写死版本。

## 2. 框架级 BOM

| catalog 别名 | 坐标 | 版本 | 说明 |
|---|---|---|---|
| `springboot` | `org.springframework.boot:spring-boot-dependencies` | 3.5.16 | 决定 Jackson 2.x、Logback、SLF4J、Micrometer、Netty 4.1、Hibernate、Kafka、SnakeYAML、JUnit 等的版本 |
| `springcloud` | `org.springframework.cloud:spring-cloud-dependencies` | 2025.0.3 | Gateway、OpenFeign、LoadBalancer、Commons |
| `springcloudalibaba` | `com.alibaba.cloud:spring-cloud-alibaba-dependencies` | 2025.0.0.0 | Nacos Client、Sentinel、Seata（groupId 为 `org.apache.seata`） |

这三个 BOM 的版本组合（Boot 3.5.x / Cloud 2025.0.x / SCA 2025.0.x）是官方配套关系，升级时要三者一起升。具体传递版本不在本文逐个列（随 Boot 补丁变化），需要时查 `spring-boot-dependencies` 对应版本的 `spring-boot-dependencies.pom`。

## 3. 第三方组件清单（按领域）

「使用方」指 easyfk 框架内直接 `api`/`implementation` 该库的模块；写「无」表示 BOM 只提供版本，框架没有封装，业务项目可以直接引用。

### 3.1 基础库（bundle `base`）

| 别名 | 坐标 | 版本 | 使用方 | 说明 |
|---|---|---|---|---|
| `fastjson2` | `com.alibaba.fastjson2:fastjson2` | 2.0.66 | easyfk-core | 代码中手动 JSON 处理 |
| `hutool` | `cn.hutool:hutool-all` | 5.8.48 | easyfk-core | 通用工具集（全量包） |
| `swaggerAnnotations` | `io.swagger.core.v3:swagger-annotations` | 2.2.55 | easyfk-core | OpenAPI 3 注解；与 springdoc 2.10 使用的 swagger-core 对齐 |
| `slf4j-api` | `org.slf4j:slf4j-api` | 2.0.18 | easyfk-core | 日志门面 |
| `caffeine` | `com.github.ben-manes.caffeine:caffeine` | 3.2.4 | easyfk-authority、cache-caffeine | **高于** Boot 自带版本 |
| `kryo` | `com.esotericsoftware:kryo` | 5.7.1 | db-redis（`KryoRedisSerializer`） | 二进制序列化 |
| `lombok` | `org.projectlombok:lombok` | 1.18.46 | 所有工程（compileOnly + annotationProcessor） | 注意：component / aeron 的 catalog 写的是 1.18.48，见 §4 |
| `jasypt` | `com.github.ulisesbocchio:jasypt-spring-boot-starter` | 4.0.4 | 无 | 配置加密（4.x 为 Boot 3 版本） |
| `sms4j` | `org.dromara.sms4j:sms4j-spring-boot-starter` | 3.3.5 | 无 | 短信聚合 |

### 3.2 日志与链路（bundle `logging`、`skywalking`）

| 别名 | 坐标 | 版本 | 使用方 | 说明 |
|---|---|---|---|---|
| `logbackEncoder` | `net.logstash.logback:logstash-logback-encoder` | 8.1 | log-logback | JSON 日志编码器；8.x 要求 Jackson 2.17+ / Logback 1.5+，Boot 3.5 基线满足 |
| `skywalkingLog4j2` | `org.apache.skywalking:apm-toolkit-log4j-2.x` | 9.8.0 | 无 | SkyWalking traceId 注入 |
| `skywalkingLogback` | `org.apache.skywalking:apm-toolkit-logback-1.x` | 9.8.0 | 无 | 同上 |

日志实现本身（`spring-boot-starter-logging` / `spring-boot-starter-log4j2`）由 Boot 管理，分别被 log-logback / log-log4j2 引入。

### 3.3 数据库驱动与客户端（bundle `database`、`datasource`、`mybatis`、`clickhouse`）

| 别名 | 坐标 | 版本 | 使用方 | 说明 |
|---|---|---|---|---|
| `mysql` | `com.mysql:mysql-connector-j` | 9.7.0 | db-mysql | 高于 Boot 自带版本 |
| `postgresql` | `org.postgresql:postgresql` | 42.7.14 | db-postgresql | 高于 Boot 3.5.16 管理的 42.7.11，修 GHSA-rhp9-mr79-r74h、GHSA-f64h-wr5q-3qf3 |
| `influxdb` | `com.influxdb:influxdb-client-java` | 8.0.0 | **无（模块已下线）** | 3.5.16 起框架不再提供 `db-influx` 模块，别名仍留在 BOM 里但没有任何 easyfk 模块引用；8.x 要求 OkHttp 4.x（见下） |
| `okhttp` | `com.squareup.okhttp3:okhttp` | 4.12.1 | 无（influx 传递，已无模块使用） | 固定 4.x：influxdb-client 8.0.0 调用了 OkHttp 5 已删除的内部 API；`db-influx` 下线后这条约束仅对仍自行引入 influxdb-client 的业务生效 |
| `clickhouse` | `com.clickhouse:clickhouse-jdbc` | 0.10.0 | db-clickhouse | 0.11.x 依赖 httpclient5 5.6 / httpcore5 5.4，高于 Boot 3.5 基线，故停在 0.10.0 |
| `client5` | `org.apache.httpcomponents.client5:httpclient5` | 5.5.2 | db-clickhouse | 与 Boot 3.5 一致 |
| `client5Core` | `org.apache.httpcomponents.core5:httpcore5` | 5.3.6 | db-clickhouse | 与 Boot 3.5 一致 |
| `druid` | `com.alibaba:druid-spring-boot-3-starter` | 1.2.28 | ds-druid | Boot 3 专用 starter |
| `shardingJDBC` | `org.apache.shardingsphere:shardingsphere-jdbc-core-spring-boot-starter` | 5.2.1 | **已废弃**（`orm-sharding` 不再引用） | starter 自 5.3.0 起停发，5.2.1 是最后版本，且与 Boot 3.5 的 SnakeYAML 2.x 不兼容。`orm-sharding` 已改为自带 `shardingsphere-jdbc:5.5.3` 一组构件。**但该坐标仍在 `database` bundle 里**，引入 `libs.bundles.database` 会把它带回来，见 §6 复查记录 |
| `mybatis-plus` | `com.baomidou:mybatis-plus-spring-boot3-starter` | 3.5.18.1 | orm-mybatis | 3.5.18 起 ActiveRecord `Model`、`ServiceImpl` 迁到 `com.baomidou.mybatisplus.spring.*` 包 |
| `mybatis-dynamic` | `com.baomidou:dynamic-datasource-spring-boot3-starter` | 4.6.0 | 无 | 多数据源切换 |
| `mybatis-flex` | `com.mybatis-flex:mybatis-flex-spring-boot3-starter` | 1.11.8 | orm-flex | 本版本起由 BOM 管理（上一版在模块里写死 1.11.4） |

Redis（`spring-boot-starter-data-redis` + Lettuce + `commons-pool2`）、JPA/Hibernate、MongoDB（`spring-boot-starter-data-mongodb`）均由 Boot 管理，分别被 db-redis、orm-hibernate、db-mongo 引入。

### 3.4 缓存与分布式锁（bundle `cache`；单独约束 `redisson`）

| 别名 | 坐标 | 版本 | 使用方 | 说明 |
|---|---|---|---|---|
| `redisson` | `org.redisson:redisson` | 3.52.0 | lock-redisson | 核心包，不是 Boot starter；**刻意停在 3.x**：4.x 依赖 Netty 4.2，Boot 3.5 基线是 Netty 4.1 |

### 3.5 消息队列（bundle `mq`）

| 别名 | 坐标 | 版本 | 使用方 | 说明 |
|---|---|---|---|---|
| `rocketMq` | `org.apache.rocketmq:rocketmq-spring-boot-starter` | 2.3.6 | mq-rocket | |
| `protobuf` / `protobufUtil` | `com.google.protobuf:protobuf-java` / `-util` | 4.36.2 | mq-common、aeron-codec-protobuf、fory 相关模块 | 单独约束，供多个模块共用 |

Kafka（`spring-kafka` / `kafka-clients` / `kafka-streams`）与 RabbitMQ（`spring-boot-starter-amqp`）由 Boot 管理；mq-kafka 的 `kafka-streams` 本版本起不再写死版本，跟随 Boot。

### 3.6 微服务与 RPC（bundle `rpc`；其余由 Cloud / SCA BOM 管理）

| 别名 | 坐标 | 版本 | 使用方 | 说明 |
|---|---|---|---|---|
| `dubbo` | `org.apache.dubbo:dubbo-spring-boot-starter` | 3.3.7 | rpc-dubbo | remote-dubbo 另以 compileOnly 写死 `dubbo:3.3.7` |
| `dubboRegistry` | `org.apache.dubbo:dubbo-registry-nacos` | 3.3.7 | rpc-dubbo | |

由 SCA BOM 管理（catalog 中没有别名）：`spring-cloud-starter-alibaba-nacos-discovery`（registry-nacos）、`-nacos-config`（config-nacos）、`-sentinel` + `sentinel-datasource-nacos` + `sentinel-parameter-flow-control`（protect-sentinel）、`-seata`（transaction-seata）。
由 Cloud BOM 管理：`spring-cloud-starter-gateway`（easyfk-gateway）、`spring-cloud-starter-openfeign` + `spring-cloud-loadbalancer`（rpc-cloud）。

### 3.7 任务调度（bundle `xxl`）

| 别名 | 坐标 | 版本 | 使用方 |
|---|---|---|---|
| `xxlJob` | `com.xuxueli:xxl-job-core` | 3.3.0 | job-xxl |

3.3.1+ 基于 Spring Boot 4 / Spring 7，本版本停在 3.3.0。

### 3.8 本地存储（bundle `storage`）

| 别名 | 坐标 | 版本 | 使用方 | 说明 |
|---|---|---|---|---|
| `chronicleMap` | `net.openhft:chronicle-map` | 2026.2 | chronicle-map、aeron-chronicle（间接） | 已改为正式版本号（上一版是 `3.27ea1` EA） |
| `chronicleQueue` | `net.openhft:chronicle-queue` | 2026.8 | chronicle-queue | 正式版本号（上一版是 `5.27ea10` EA）；模块另写死 `net.openhft:affinity:2026.2` |

Chronicle 在 JDK 21 上运行需要额外的 `--add-opens/--add-exports` JVM 参数，详见 chronicle skill 文档。

### 3.9 文档、对象映射与工具（bundle `doc`、`mapstruct`、`tools`）

| 别名 | 坐标 | 版本 | 使用方 | 说明 |
|---|---|---|---|---|
| `knife4j` | `com.github.xiaoymin:knife4j-openapi3-jakarta-spring-boot-starter` | 4.5.0 | doc-knife4j | 基于 springdoc，Jakarta 版本 |
| `springdoc*`（common / webmvc-api / webmvc-ui / webflux-api / webflux-ui） | `org.springdoc:springdoc-openapi-starter-*` | 2.10.0 | doc-knife4j（传递） | **本版本强制提升**：knife4j 4.5.0 自带的 springdoc 2.3.0 调用了 Spring 6.2 已删除的 `ControllerAdviceBean(Object)`，不提升会在 Boot 3.5 启动失败 |
| `mapstruct-plus` | `io.github.linpeilie:mapstruct-plus-spring-boot-starter` | 1.5.3 | easyfk-core | base 的注解处理器另用 `mapstruct-plus-processor:1.5.3` + `lombok-mapstruct-binding:0.2.0`（定义在 base 自己的 catalog） |
| `okhttp` | `com.squareup.okhttp3:okhttp` | 4.12.1 | 无 | 见 §3.3 |
| `easyexcel` | `com.alibaba:easyexcel` | 4.0.3 | 无 | 原 tool-excel 模块已不存在 |

### 3.10 微信生态（bundle `wxJava`，版本变量 `wxJava = 4.8.0`）

| 别名 | 坐标 | 版本 | 使用方 |
|---|---|---|---|
| `wxJavaMiniApp` | `com.github.binarywang:wx-java-miniapp-spring-boot-starter` | 4.8.0 | 无 |
| `wxJavaMp` | `com.github.binarywang:wx-java-mp-spring-boot-starter` | 4.8.0 | 无 |
| `wxJavaPay` | `com.github.binarywang:wx-java-pay-spring-boot-starter` | 4.8.0 | 无 |
| `wxJavaCp` | `com.github.binarywang:wx-java-cp-spring-boot-starter` | 4.8.0 | 无 |

### 3.11 Aeron / 集群（bundle `aeron`、`aeronRuntime`、`etcdCluster`）

| 别名 | 坐标 | 版本 | 说明 |
|---|---|---|---|
| `aeron`（bundle） | `com.mcst:aeron-*`、`aeron-cluster-*` | 3.5.16 | 框架自己的 Aeron 模块坐标（common / store / codec-* / compression-* / driver / producer / producer-outbox / consumer / metrics / chronicle / starter / cluster-core / cluster-client / cluster-starter / cluster-test） |
| `aeronRuntime`（bundle） | `io.aeron:aeron-all` / `-driver` / `-client` / `-archive` / `-cluster`、`org.agrona:agrona`、`uk.co.real-logic:sbe-tool`、`at.yawk.lz4:lz4-java`、`com.github.luben:zstd-jni` | aeron 1.54.2、agrona 2.7.1、sbe 1.42.0、lz4 1.14.0、zstd 1.5.7-28 | **本版本起由 BOM 统一约束**，easyfk-aeron 与 aeron-cluster 共用同一套版本 |
| `etcdCluster`（bundle） | `com.mcst:etcd-cluster-api` / `-core` / `-spring-boot-starter` | 3.5.16 | etcd 集群协调模块坐标；jetcd 由 etcd-cluster 自己的 catalog 管（见 §4） |

## 4. 不受 BOM 管理、由模块写死版本的第三方库

升级这些库要改对应模块的 `build.gradle` 或该工程自己的 catalog，改 BOM 不起作用。

| 坐标 | 版本 | 所在模块 |
|---|---|---|
| `org.apache.fory:fory-core` | 1.7.8 | easyfk-base / serializer-fory |
| `com.lmax:disruptor` | 4.0.0 | easyfk-base / queue-disruptor |
| `org.apache.dubbo:dubbo` | 3.3.7（compileOnly） | easyfk-base / remote-dubbo |
| `net.openhft:affinity` | 2026.2 | easyfk-component / chronicle-queue |
| `com.baomidou:mybatis-plus-jsqlparser` | 3.5.18.1 | easyfk-component / orm-mybatis |
| `org.apache.shardingsphere:shardingsphere-jdbc` + 14 个功能/方言/基础设施构件 | 5.5.3 | easyfk-component / orm-sharding（`def shardingsphereVersion = '5.5.3'`，BOM 里的 `shardingJDBC 5.2.1` 已不再被引用） |
| `com.google.guava:guava` | 33.8.0-jre | easyfk-component / db-clickhouse |
| `org.projectlombok:lombok` | 1.18.46（base / aeron-cluster / etcd-cluster）、1.18.48（component / easyfk-aeron） | 各工程 `settings.gradle` 的 catalog |
| `io.etcd:jetcd-core` | 0.8.8 | etcd-cluster 自有 catalog |
| `io.grpc:grpc-bom` / `io.netty:netty-bom` / `com.google.protobuf:protobuf-bom` / `com.google.api.grpc:proto-google-common-protos` | 1.85.1 / 4.2.20.Final / 4.36.2 / 2.81.0 | etcd-cluster 自有 catalog（只作用于 shaded 包，已重定位） |
| `com.google.guava:guava-bom` / `com.fasterxml.jackson:jackson-bom` / `io.vertx:vertx-core`+`vertx-grpc` | 33.8.0-jre / 2.23.0 / 4.5.36 | etcd-cluster 自有 catalog（shaded 包内对齐；vertx 5.x 与 jetcd 0.8.8 的存根不兼容） |
| `com.xuxueli:xxl-cache-core` | 1.4.0 | **无（模块已下线）**：3.5.16 起 `cache-mult` 不再发布，该版本约束仅保留在 BOM 中（1.5.x 依赖 Jedis 7，与 Boot 3.5 的 Jedis 6.0 冲突） |

Lombok 在两个工程里不一致（1.18.46 / 1.18.48）是现状，不影响编译，业务工程按 BOM 的 1.18.46 走即可。

## 5. 生成代码时的规则

**Do**
- 下游工程先写 `implementation platform('com.mcst:easyfk-dependencies:3.5.16')`，之后第三方依赖**不写版本号**。
- 优先引用 easyfk 封装模块（如 `com.mcst:db-mysql`、`com.mcst:lock-redisson`），它们已经带上了对应的第三方库；只有确实不需要 easyfk 封装时才直接引第三方坐标。
- Druid 使用 `com.alibaba:druid-spring-boot-3-starter`；MyBatis-Plus 使用 `mybatis-plus-spring-boot3-starter`；动态数据源使用 `dynamic-datasource-spring-boot3-starter`（都是 Boot 3 专用 artifact）。
- MongoDB 使用 `spring-boot-starter-data-mongodb`（或直接依赖 `com.mcst:db-mongo`）。
- Seata 相关类的包名以 `org.apache.seata` 为准（SCA 2025.0.x 使用 Apache Seata 2.x）。
- 用 Aeron / aeron-cluster 时**不要**自己指定 Aeron、Agrona 版本，交给 `aeronRuntime` bundle；两个工程共用同一版本，混用会二进制不兼容。
- 需要固定某个版本时，在业务工程里显式写版本号覆盖；要求所有传递依赖也被压到 BOM 版本时用 `enforcedPlatform`。

**Don't**
- 不要为 BOM 已管理的库再写版本号，避免和平台版本冲突。
- 不要引入 `org.mongodb:mongo-java-driver`（3.x 旧版），它与 Boot 管理的 4.x driver 包名重叠、版本冲突。
- 不要引入 Boot 2 时代的 artifact：`druid-spring-boot-starter`、`mybatis-plus-boot-starter`、`dynamic-datasource-spring-boot-starter`、`knife4j-openapi3-spring-boot-starter`（非 jakarta 版）。
- 不要在 BOM 里新增低于 Spring Boot 管理版本的约束，也不要只在 catalog 定义别名却不放进 bundle，这两种写法都不生效。
- 不要在 Boot 3.5 工程里使用 ShardingSphere 5.2.1 的 YAML 配置方式（SnakeYAML 2.x 不兼容），见 orm skill 文档。
- 不要把 Redisson 升到 4.x（Netty 4.2），也不要把 xxl-job 升到 3.3.1+（Boot 4）。
- 不要引用已删除的 `com.mcst` 坐标：`easyfk-doc`、`easyfk-lock`、`easyfk-mq`、`easyfk-resource`、`resource-*`、`lock-zk`、`tool-http`、`tool-excel`、`component-autoId`、`gateway-gateway`、`doc-micro`、`storage-chronicle`、`datasource-druid`、`ws-api`、`ws-server`。
- 自增 ID 依赖写 `com.mcst:autoId-api` / `com.mcst:autoId-redis`，ClickHouse 写 `com.mcst:db-clickhouse`，网关写 `com.mcst:easyfk-gateway`。

## 6. 复查记录

3.2.12 的复查结论（postgresql/okhttp/httpclient5 未进 bundle、lombok 当 platform 导入、mongo-java-driver 3.x、重复声明 bundle 等）在本版本已全部落到 BOM 里，不再复述。下表只记本版本新发现的问题。

| # | 位置 | 描述 | 源码实际 |
|---|---|---|---|
| 1 | `settings.gradle` | `lombok` 一个 BOM 里只有一个版本 | BOM 是 1.18.46，但 `easyfk-component` 与 `easyfk-aeron` 的 catalog 写 1.18.48，`easyfk-base` / `aeron-cluster` / `etcd-cluster` 写 1.18.46 **未统一**：不影响编译（compileOnly + annotationProcessor），业务工程按 BOM 的 1.18.46 |
| 2 | `settings.gradle` | `springdoc` 为什么单独定义 2.10.0 | knife4j 4.5.0 自带 springdoc 2.3.0，调用了 Spring 6.2 已删除的 `ControllerAdviceBean(Object)`；Boot 3.5 上必须提升到 2.8+ **已修复**：BOM 强制 2.10.0，并把 5 个 springdoc starter 都放进 `doc` bundle |
| 3 | `settings.gradle` | `redisson` 停留在 3.52.0 | 4.x 依赖 Netty 4.2，Boot 3.5 基线是 Netty 4.1 **刻意保留**：注释已写在 catalog 里 |
| 4 | `settings.gradle` | `xxlJob` 停在 3.3.0 | 3.3.1+ 基于 Spring Boot 4 / Spring 7 **刻意保留** |
| 5 | `settings.gradle` | `chronicleMap` / `chronicleQueue` 版本号形如 `2026.2` / `2026.8` | OpenHFT 改用日历版本号，这两个是**正式版**，不再是上一版的 EA（`3.27ea1` / `5.27ea10`）。chronicle skill 文档里"EA 版本"的说法本版本起不再适用 |
| 6 | `settings.gradle` | `clickhouse` 停在 0.10.0 | 0.11.x 依赖 httpclient5 5.6 / httpcore5 5.4，高于 Boot 3.5 的 5.5.2 / 5.3.6 **刻意保留** |
| 7 | `settings.gradle` | `postgresql` 42.7.14 | 高于 Boot 3.5.16 管理的 42.7.11，用于修 GHSA-rhp9-mr79-r74h、GHSA-f64h-wr5q-3qf3，属预期 |
| 8 | `settings.gradle` | `influxdb` 8.0.0 + `okhttp` 4.12.1 | influxdb-client 8.0.0 调用了 OkHttp 5 已删除的 `RealConnection.noNewExchanges` **已修复**：BOM 把 okhttp 固定到 4.12.1 |
| 9 | `mybatis-plus` 3.5.18.1 | ActiveRecord `Model` / `ServiceImpl` 的包 | 由 `com.baomidou.mybatisplus.extension.*` 迁到 `com.baomidou.mybatisplus.spring.*`；框架内 `BaseMyBatisPlusEntity` / `BaseMyBatisPlusSimpleEntity` / `BaseMyBatisRepositoryImpl` 已同步改 import，**业务代码里直接 import 过 `extension.activerecord.Model` / `extension.service.impl.ServiceImpl` 的必须跟着改** |
| 10 | 独立工程 catalog | 上一版：Aeron/Agrona/SBE/LZ4/Zstd 版本写死在 easyfk-aeron、aeron-cluster 各自 catalog | 本版本改为无版本坐标 + BOM `aeronRuntime` 统一约束（aeron 1.54.2 / agrona 2.7.1 / sbe 1.42.0 / lz4 1.14.0 / zstd 1.5.7-28） |
| 11 | `easyfk-aeron` catalog | `micrometer-core` 曾写死 1.8.13（Boot 2.6 兼容基线） | 本版本已删除该写死版本，`aeron-metrics-micrometer` 用无版本坐标，跟随 Boot 3.5 的 Micrometer |
| 12 | `etcd-cluster` catalog | `jetcd` 0.8.6 | 本版本 0.8.8；shaded 包另对齐 grpc 1.85.1 / netty 4.2.20.Final / protobuf 4.36.2，避免 4.1 与 4.2 混装 |
| 13 | `bundle('database', …)` | — | bundle 里仍保留 `shardingJDBC`（`shardingsphere-jdbc-core-spring-boot-starter:5.2.1`），而 `orm-sharding` 已改用自带的 5.5.3 一组构件。业务工程若引入 `libs.bundles.database`，会把停发的 5.2.1 starter 一起带进 classpath，与 5.5.3 的 `shardingsphere-jdbc` 混装 **未修复**：建议 BOM 从 `database` bundle 移除 `shardingJDBC`，只按需引用 `libs.shardingJDBC`（或彻底删掉该别名） |
| 14 | 3.5.16 新增约束 | — | `aeronRuntime` bundle 把 `aeron-all`/`aeron-driver`/`aeron-client`/`aeron-archive`/`aeron-cluster`/`agrona`/`sbe-tool`/`lz4`/`zstd` 收进 BOM，两个独立工程 catalog 里的版本声明已删除（改用无版本坐标）。`springdoc 2.10.0` 也是本版本新增的强制约束 |
