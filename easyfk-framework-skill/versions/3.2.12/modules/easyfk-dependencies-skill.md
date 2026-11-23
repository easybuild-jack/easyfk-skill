# easyfk-dependencies Skill 参考文档（第三方组件）

> 所属项目：`easyfk-dependencies`（独立 Gradle 工程，`java-platform` + `allowDependencies()`）
> 坐标：`com.mcst:easyfk-dependencies:3.2.12`
> 依据：`settings.gradle`（version catalog）、`build.gradle`（platform + constraints）、base / component / aeron / aeron-cluster 各模块 `build.gradle`；对齐 `dependencies开发手册.md`、`dependencies特点说明.md`。
> 「生效版本」是引入本 BOM 后用 Gradle 离线解析得到的实际版本（Spring Boot 平台与 BOM 约束同时生效时，Gradle 取较高者）。
> 本文只汇总**第三方组件**；`com.mcst` 内部模块见各模块 skill 文档，坐标问题见文末「复查记录」。

---

## 1. 工作机制

- `build.gradle` 先以 `api platform(...)` 导入三个框架级 BOM，再在 `constraints {}` 里逐个 `api(libs.bundles.xxx)` / `api(libs.xxx)` 输出版本约束。
- **只有进了 `constraints` 的别名才会被约束**。catalog 里定义了但没进任何 bundle、也没单独 `api(libs.xxx)` 的库，下游拿到的是 Spring Boot 平台的版本，或者根本没有版本。新增别名时必须同时放进某个 bundle。
- BOM 版本低于 Spring Boot 管理的版本时不起作用（Gradle 取较高者），所以 BOM 里的版本应不低于 Boot 的版本。
- BOM 只提供版本，不引入依赖；下游必须显式声明依赖坐标（不写版本）。
- 下游写法：`implementation platform('com.mcst:easyfk-dependencies:3.2.12')`；Maven 用 `<dependencyManagement>` + `<type>pom</type><scope>import</scope>`。

## 2. 框架级 BOM

| catalog 别名 | 坐标 | 版本 | 关键传递版本（实际解析） |
|---|---|---|---|
| `springboot` | `org.springframework.boot:spring-boot-dependencies` | 3.2.12 | Spring Boot 3.2.12、Jackson 2.15.4、Logback 1.4.14、SLF4J 2.0.16、Micrometer 1.12.13、Netty 4.1.115.Final、Hibernate 6.4.10.Final、MongoDB Driver 4.11.5、Kafka 3.6.2、Spring Kafka 3.1.10、RabbitMQ amqp-client 5.19.0、commons-pool2 2.12.0、SnakeYAML 2.2、JUnit 5.10.5、Mockito 5.7.0、Awaitility 4.2.2 |
| `springcloud` | `org.springframework.cloud:spring-cloud-dependencies` | 2023.0.5 | spring-cloud-commons 4.1.5、Gateway 4.1.6、OpenFeign 4.1.4、LoadBalancer |
| `springcloudalibaba` | `com.alibaba.cloud:spring-cloud-alibaba-dependencies` | 2023.0.3.3 | Nacos Client 2.4.2、Sentinel 1.8.8、Seata 2.1.0（groupId 已是 `org.apache.seata`） |

这三个 BOM 的版本组合（Boot 3.2.x / Cloud 2023.0.x / SCA 2023.0.x）是官方配套关系，升级时要三者一起升。

## 3. 第三方组件清单（按领域）

「使用方」指 easyfk 框架内直接 `api`/`implementation` 该库的模块；写「无」表示 BOM 只提供版本，框架没有封装，业务项目可以直接引用。

### 3.1 基础库（bundle `base`）

| 别名 | 坐标 | BOM 版本 | 生效版本 | 使用方 | 说明 |
|---|---|---|---|---|---|
| `fastjson2` | `com.alibaba.fastjson2:fastjson2` | 2.0.58 | 2.0.58 | easyfk-core | JSON 工具 |
| `hutool` | `cn.hutool:hutool-all` | 5.8.40 | 5.8.40 | easyfk-core | 通用工具集（全量包） |
| `swaggerAnnotations` | `io.swagger.core.v3:swagger-annotations` | 2.2.36 | 2.2.36 | easyfk-core | OpenAPI 3 注解 |
| `slf4j-api` | `org.slf4j:slf4j-api` | 2.0.16 | 2.0.16 | easyfk-core | 与 Boot 一致 |
| `caffeine` | `com.github.ben-manes.caffeine:caffeine` | 3.2.2 | 3.2.2 | easyfk-authority、cache-caffeine | **高于** Boot 自带的 3.1.8 |
| `kryo` | `com.esotericsoftware:kryo` | 5.6.2 | 5.6.2 | db-redis（`KryoRedisSerializer`） | 二进制序列化 |
| `lombok` | `org.projectlombok:lombok` | 1.18.38 | 1.18.38 | 所有工程（compileOnly + annotationProcessor） | 高于 Boot 的 1.18.36 |
| `jasypt` | `com.github.ulisesbocchio:jasypt-spring-boot-starter` | 3.0.5 | 未在本地解析 | 无 | 配置加密 |
| `sms4j` | `org.dromara.sms4j:sms4j-spring-boot-starter` | 3.3.5 | 3.3.5 | 无 | 短信聚合 |

### 3.2 日志与链路（bundle `logging`、`skywalking`）

| 别名 | 坐标 | BOM 版本 | 生效版本 | 使用方 | 说明 |
|---|---|---|---|---|---|
| `logbackEncoder` | `net.logstash.logback:logstash-logback-encoder` | 8.0 | 8.0 | log-logback | JSON 日志编码器；已实测可在 Logback 1.4.14 上运行，但会把 Jackson 传递提升到 **2.17.2** |
| `skywalkingLog4j2` | `org.apache.skywalking:apm-toolkit-log4j-2.x` | 9.5.0 | 未在本地解析 | 无 | SkyWalking traceId 注入 |
| `skywalkingLogback` | `org.apache.skywalking:apm-toolkit-logback-1.x` | 9.5.0 | 未在本地解析 | 无 | 同上 |

日志实现本身（`spring-boot-starter-logging` / `spring-boot-starter-log4j2`）由 Boot 管理，分别被 log-logback / log-log4j2 引入。

### 3.3 数据库驱动与客户端（bundle `database`、`datasource`、`mybatis`、`clickhouse`）

| 别名 | 坐标 | BOM 版本 | 生效版本 | 使用方 | 说明 |
|---|---|---|---|---|---|
| `mysql` | `com.mysql:mysql-connector-j` | 9.4.0 | 9.4.0 | db-mysql | **高于** Boot 自带的 8.3.0 |
| `postgresql` | `org.postgresql:postgresql` | 42.7.8 | 42.7.8 | db-postgresql | 高于 Boot 自带的 42.6.2 |
| `influxdb` | `com.influxdb:influxdb-client-java` | 7.3.0 | 7.3.0 | **无（模块已下线）** | InfluxDB 2.x 客户端（Flux）；`db-influx` 已下线，别名仍留在 BOM 里但没有任何 easyfk 模块引用 |
| `clickhouse` | `com.clickhouse:clickhouse-jdbc` | 0.9.4 | 0.9.4 | db-clickhouse | 配合 HttpClient5 传输 |
| `client5` | `org.apache.httpcomponents.client5:httpclient5` | 5.2.3 | 5.2.3 | db-clickhouse | 与 Boot 一致 |
| `client5Core` | `org.apache.httpcomponents.core5:httpcore5` | 5.2.5 | 5.2.5 | db-clickhouse | 与 Boot 一致 |
| `druid` | `com.alibaba:druid-spring-boot-3-starter` | 1.2.27 | 未在本地解析 | ds-druid | Boot 3 专用 starter |
| `shardingJDBC` | `org.apache.shardingsphere:shardingsphere-jdbc-core-spring-boot-starter` | 5.2.1 | 5.2.1 | orm-sharding | 与 SnakeYAML 2.2 不兼容，见复查记录 |
| `mybatis-plus` | `com.baomidou:mybatis-plus-spring-boot3-starter` | 3.5.14 | 3.5.14 | orm-mybatis | 另外自带 `mybatis-plus-jsqlparser:3.5.14` |
| `mybatis-dynamic` | `com.baomidou:dynamic-datasource-spring-boot3-starter` | 4.3.0 | 4.3.0 | 无 | 多数据源切换 |

Redis（`spring-boot-starter-data-redis` + Lettuce + `commons-pool2`）、JPA/Hibernate、MongoDB（`spring-boot-starter-data-mongodb`，driver-sync 4.11.5）均由 Boot 管理，分别被 db-redis、orm-hibernate、db-mongo 引入。

### 3.4 缓存与分布式锁（bundle `cache`；单独约束 `redisson`）

| 别名 | 坐标 | BOM 版本 | 生效版本 | 使用方 | 说明 |
|---|---|---|---|---|---|
| `redisson` | `org.redisson:redisson` | 3.40.2 | 3.40.2 | lock-redisson | 核心包，不是 Boot starter |

### 3.5 消息队列（bundle `mq`）

| 别名 | 坐标 | BOM 版本 | 生效版本 | 使用方 | 说明 |
|---|---|---|---|---|---|
| `rocketMq` | `org.apache.rocketmq:rocketmq-spring-boot-starter` | 2.3.4 | 2.3.4 | mq-rocket | |
Kafka（`spring-kafka` 3.1.10 / `kafka-clients` 3.6.2）与 RabbitMQ（`spring-boot-starter-amqp`）由 Boot 管理；mq-kafka 额外写死了 `kafka-streams:3.6.2`，mq-common 写死了 `protobuf-java` / `protobuf-java-util:4.28.2`。

### 3.6 微服务与 RPC（bundle `rpc`；其余由 Cloud / SCA BOM 管理）

| 别名 | 坐标 | BOM 版本 | 生效版本 | 使用方 | 说明 |
|---|---|---|---|---|---|
| `dubbo` | `org.apache.dubbo:dubbo-spring-boot-starter` | 3.3.5 | 3.3.5 | rpc-dubbo | remote-dubbo 另以 compileOnly 写死 `dubbo:3.3.5` |
| `dubboRegistry` | `org.apache.dubbo:dubbo-registry-nacos` | 3.3.5 | 3.3.5 | rpc-dubbo | |

由 SCA BOM 管理（catalog 中没有别名）：`spring-cloud-starter-alibaba-nacos-discovery`（registry-nacos）、`-nacos-config`（config-nacos）、`-sentinel` + `sentinel-datasource-nacos` + `sentinel-parameter-flow-control`（protect-sentinel）、`-seata`（transaction-seata）。
由 Cloud BOM 管理：`spring-cloud-starter-gateway`（easyfk-gateway）、`spring-cloud-starter-openfeign` + `spring-cloud-loadbalancer`（rpc-cloud）。

### 3.7 任务调度（bundle `xxl`）

| 别名 | 坐标 | BOM 版本 | 生效版本 | 使用方 |
|---|---|---|---|---|
| `xxlJob` | `com.xuxueli:xxl-job-core` | 3.2.0 | 3.2.0 | job-xxl |

### 3.8 本地存储（bundle `storage`）

| 别名 | 坐标 | BOM 版本 | 生效版本 | 使用方 | 说明 |
|---|---|---|---|---|---|
| `chronicleMap` | `net.openhft:chronicle-map` | 3.27ea1 | 3.27ea1 | chronicle-map、aeron-chronicle（间接） | **EA（预览）版本** |
| `chronicleQueue` | `net.openhft:chronicle-queue` | 5.27ea10 | 5.27ea10 | chronicle-queue | **EA 版本**；模块另写死 `net.openhft:affinity:3.23.3` |

Chronicle 在 JDK 21 上运行需要额外的 `--add-opens/--add-exports` JVM 参数，详见 chronicle skill 文档。

### 3.9 文档、对象映射与工具（bundle `doc`、`mapstruct`、`tools`）

| 别名 | 坐标 | BOM 版本 | 生效版本 | 使用方 | 说明 |
|---|---|---|---|---|---|
| `knife4j` | `com.github.xiaoymin:knife4j-openapi3-jakarta-spring-boot-starter` | 4.5.0 | 4.5.0 | doc-knife4j | 基于 springdoc，Jakarta 版本 |
| `mapstruct-plus` | `io.github.linpeilie:mapstruct-plus-spring-boot-starter` | 1.5.0 | 1.5.0 | easyfk-core | base 的注解处理器另用 `mapstruct-plus-processor:1.5.0` + `lombok-mapstruct-binding:0.2.0`（定义在 base 自己的 catalog） |
| `okhttp` | `com.squareup.okhttp3:okhttp` | 4.12.0 | 4.12.0 | 无 | 与 Boot 一致 |
| `easyexcel` | `com.alibaba:easyexcel` | 4.0.3 | 未在本地解析 | 无 | 原 tool-excel 模块已不存在 |

### 3.10 微信生态（bundle `wxJava`，版本变量 `wxJava = 4.8.0`）

| 别名 | 坐标 | 版本 | 使用方 |
|---|---|---|---|
| `wxJavaMiniApp` | `com.github.binarywang:wx-java-miniapp-spring-boot-starter` | 4.8.0 | 无 |
| `wxJavaMp` | `com.github.binarywang:wx-java-mp-spring-boot-starter` | 4.8.0 | 无 |
| `wxJavaPay` | `com.github.binarywang:wx-java-pay-spring-boot-starter` | 4.8.0 | 无 |
| `wxJavaCp` | `com.github.binarywang:wx-java-cp-spring-boot-starter` | 4.8.0 | 无 |

## 4. 不受 BOM 管理、由模块写死版本的第三方库

升级这些库要改对应模块的 `build.gradle` 或该工程自己的 catalog，改 BOM 不起作用。

| 坐标 | 版本 | 所在模块 |
|---|---|---|
| `org.apache.fory:fory-core` | 1.3.0 | easyfk-base / serializer-fory |
| `com.lmax:disruptor` | 4.0.0 | easyfk-base / queue-disruptor |
| `org.apache.dubbo:dubbo` | 3.3.5（compileOnly） | easyfk-base / remote-dubbo |
| `net.openhft:affinity` | 3.23.3 | easyfk-component / chronicle-queue |
| `org.apache.kafka:kafka-streams` | 3.6.2 | easyfk-component / mq-kafka |
| `com.google.protobuf:protobuf-java`、`protobuf-java-util` | 4.28.2 | easyfk-component / mq-common |
| `com.baomidou:mybatis-plus-jsqlparser` | 3.5.14 | easyfk-component / orm-mybatis |
| `com.mybatis-flex:mybatis-flex-spring-boot3-starter` | 1.11.4 | easyfk-component / orm-flex |
| `com.google.guava:guava` | 32.1.3-jre | easyfk-component / db-clickhouse |
| `io.aeron:aeron-all` / `aeron-driver` / `aeron-client` | 1.52.1 | easyfk-aeron 自有 catalog |
| `io.aeron:aeron-archive` / `aeron-cluster` | 1.52.1 | aeron-cluster 自有 catalog |
| `org.agrona:agrona` | 2.5.0 | easyfk-aeron、aeron-cluster 自有 catalog |
| `uk.co.real-logic:sbe-tool` | 1.39.0 | easyfk-aeron / aeron-codec-sbe |
| `com.google.protobuf:protobuf-java` | 4.28.2 | easyfk-aeron / aeron-codec-protobuf |
| `at.yawk.lz4:lz4-java` | 1.11.1 | easyfk-aeron / aeron-compression-lz4 |
| `com.github.luben:zstd-jni` | 1.5.7-11 | easyfk-aeron / aeron-compression-zstd |
| `io.micrometer:micrometer-core` | 1.8.13（catalog，Boot 2.6 兼容基线）→ 在 BOM 下实际解析为 1.12.13 | easyfk-aeron / aeron-metrics-micrometer、aeron-spring-boot-starter |

## 5. 生成代码时的规则

**Do**
- 下游工程先写 `implementation platform('com.mcst:easyfk-dependencies:3.2.12')`，之后第三方依赖**不写版本号**。
- 优先引用 easyfk 封装模块（如 `com.mcst:db-mysql`、`com.mcst:lock-redisson`），它们已经带上了对应的第三方库；只有确实不需要 easyfk 封装时才直接引第三方坐标。
- Druid 使用 `com.alibaba:druid-spring-boot-3-starter`；MyBatis-Plus 使用 `mybatis-plus-spring-boot3-starter`；动态数据源使用 `dynamic-datasource-spring-boot3-starter`（都是 Boot 3 专用 artifact）。
- MongoDB 使用 `spring-boot-starter-data-mongodb`（或直接依赖 `com.mcst:db-mongo`）。
- Seata 相关类的包名以 `org.apache.seata` 为准（SCA 2023.0.3.x 已切换到 Apache Seata 2.x）。
- 需要固定某个版本时，在业务工程里显式写版本号覆盖；要求所有传递依赖也被压到 BOM 版本时用 `enforcedPlatform`。

**Don't**
- 不要为 BOM 已管理的库再写版本号，避免和平台版本冲突。
- 不要引入 `org.mongodb:mongo-java-driver`（3.x 旧版），它与 Boot 管理的 4.x driver 包名重叠、版本冲突。
- 不要引入 Boot 2 时代的 artifact：`druid-spring-boot-starter`、`mybatis-plus-boot-starter`、`dynamic-datasource-spring-boot-starter`、`knife4j-openapi3-spring-boot-starter`（非 jakarta 版）。
- 不要在 BOM 里新增低于 Spring Boot 管理版本的约束，也不要只在 catalog 定义别名却不放进 bundle，这两种写法都不生效。
- 不要在 Boot 3 工程里使用 ShardingSphere 5.2.1 的 YAML 配置方式（SnakeYAML 2.x 不兼容），见 orm skill 文档。
- 不要依赖 Chronicle 的 EA 版本做长期生产承诺，升级前先确认有对应的正式版。
- 不要引用已删除的 `com.mcst` 坐标：`easyfk-doc`、`easyfk-lock`、`easyfk-mq`、`easyfk-resource`、`resource-*`、`lock-zk`、`tool-http`、`tool-excel`、`component-autoId`、`gateway-gateway`、`doc-micro`、`storage-chronicle`、`datasource-druid`、`ws-api`、`ws-server`。
- 自增 ID 依赖写 `com.mcst:autoId-api` / `com.mcst:autoId-redis`，ClickHouse 写 `com.mcst:db-clickhouse`，网关写 `com.mcst:easyfk-gateway`。

## 6. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | `settings.gradle` | `postgresql` 定义为 42.7.8 | 别名没有进任何 bundle，下游实际拿到 Boot 的 42.6.2 **已修复**：`postgresql` 加入 `database` bundle，生效版本 42.7.8 |
| 2 | `build.gradle` | `api platform(libs.lombok)` | Lombok 是普通 jar，不是 BOM，当作 platform 导入没有意义 **已修复**：删除该行，lombok 仍由 `base` bundle 约束 |
| 3 | `settings.gradle` | `okhttp 4.11.0`、`httpclient5 5.2.1`、`httpcore5 5.2.1` | 低于 Boot 管理的版本，声明不起作用 **已修复**：改为与 Boot 一致的 4.12.0 / 5.2.3 / 5.2.5；`okhttp`、`easyexcel` 从单独约束改为放进 `tools` bundle |
| 4 | `settings.gradle`、手册 §3.5 | `mongo-java-driver 3.12.14` 列为数据源依赖 | 3.x 旧版 uber jar，与 Boot 的 4.x driver 冲突，框架内无人使用 **已修复**：删除别名并移出 `datasource` bundle |
| 5 | `settings.gradle` | `shardingJDBC 5.2.1` | 与 Boot 3.2 的 SnakeYAML 2.2 不兼容；需要 5.4+，本地仓库只有 5.2.1 **未修复**：需联网升级（5.4+ 已取消 Spring Boot Starter，改为 `shardingsphere-jdbc` + YAML 驱动，orm-sharding 需同步改造） |
| 6 | 手册 §3.2、§3.10、§3.12、§3.13、§3.19、§6 | `easyfk-doc`、`easyfk-lock`、`easyfk-mq`、`easyfk-resource`、`resource-*`、`lock-zk`、`tool-http`、`tool-excel`、`component-autoId` | base / component 中不存在这些模块，坐标解析不到 **已修复**：全部从 catalog、bundle、手册中删除；新增 `db-clickhouse`（进 `database`）、`autoId-api` / `autoId-redis`（进 `tools`）、`aeron-store`（进 `aeron`）；别名 `datasource-druid` 改名为 `ds-druid` |
| 7 | 手册 §3.5、§3.13、§4.4、§6 | `druid-spring-boot-starter`、`gateway-gateway`、`doc-micro`、`storage-chronicle` | 与 BOM 不一致 **已修复**：手册按 BOM 现状同步，补充序列化、Aeron 两节和 serializer / aeron 分组；`dependencies特点说明.md` 去掉 ZK |
| 8 | `settings.gradle` | `jasypt`、`skywalking*`、`easyexcel`、`wxJavaCp`、`druid` | 本地离线缓存从未解析过这些坐标（框架内没有模块引用） **保留**：属于给业务方的版本建议，需联网时再做一次解析验证 |
| 9 | `build.gradle` | — | `api(libs.bundles.websocket)` 重复声明了两次 **已修复**：删除重复行 |
| 10 | easyfk-aeron | catalog `micrometer 1.8.13`、测试依赖 `mockito-inline:4.0.0` | Micrometer 1.8.13 是 aeron starter 面向 Boot 2.6.13+ 的刻意基线，在 BOM 下被提升到 1.12.13 属预期，**不改**；`mockito-inline` 4.x 与 Mockito 5.7.0 混用 **已修复**：删除该依赖（Mockito 5 默认 inline mock maker），aeron-spring-boot-starter 189 个测试全部通过 |
| 11 | `log-logback` | `logstash-logback-encoder 8.0` | 8.0 按 Logback 1.5.6 / Jackson 2.17.2 编译，运行时 Logback 为 1.4.14 **已验证**：在 BOM 依赖组合下实测 `LogstashEncoder` 输出正常（MDC、结构化参数、异常栈、调用方信息）；副作用是 Jackson 被传递提升到 2.17.2，本地仓库没有适配 Logback 1.4 的 7.4 版本，暂保留 8.0 |
