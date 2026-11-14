# easyfk-dependencies 使用手册

## 1. 简介

`easyfk-dependencies` 是 EasyFK 体系的**统一依赖版本管理平台**（BOM），发布坐标为：

```
com.mcst:easyfk-dependencies
```

引入该 BOM 后，下游业务项目无需逐一声明依赖版本号，即可获得经过验证的、一致的依赖版本基线，避免多项目间版本漂移与冲突。

**核心价值：**

- 统一管控 EasyFK 内部模块、Spring 生态及常用第三方库的版本。
- 下游项目只需引入一个 BOM 坐标，按需声明依赖即可，无需关心版本号。
- 升级时只需更新 BOM 版本，所有受管依赖自动对齐。

> **JDK 要求**：Spring Boot 3.x 要求 JDK 17+，请确保项目编译与运行环境满足此要求。

## 2. 快速接入

> 以下示例中 `${easyfk.version}` 代表实际使用的 BOM 版本号，请替换为项目所需的具体版本。

### 2.1 Gradle 项目

在 `build.gradle` 中通过 `platform` 引入 BOM：

```gradle
repositories {
    // 配置公司私服地址（根据实际情况修改）
    maven { url 'https://your-nexus-host/repository/maven-public/' }
}

dependencies {
    // 引入 BOM，统一版本管理
    implementation platform('com.mcst:easyfk-dependencies:${easyfk.version}')

    // 之后引入依赖无需写版本号
    implementation 'com.mcst:easyfk-core'
    implementation 'com.mcst:service-base'
    implementation 'com.mcst:web-common'
}
```

如果需要强制所有传递依赖也受 BOM 约束，可使用 `enforcedPlatform`：

```gradle
dependencies {
    implementation enforcedPlatform('com.mcst:easyfk-dependencies:${easyfk.version}')
}
```

**Gradle Kotlin DSL** 写法：

```kotlin
dependencies {
    implementation(platform("com.mcst:easyfk-dependencies:${easyfk.version}"))

    implementation("com.mcst:easyfk-core")
    implementation("com.mcst:service-base")
}
```

### 2.2 Maven 项目

在 `pom.xml` 的 `<dependencyManagement>` 中以 BOM 方式引入：

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.mcst</groupId>
            <artifactId>easyfk-dependencies</artifactId>
            <version>${easyfk.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

之后在 `<dependencies>` 中引入具体依赖时无需声明版本号：

```xml
<dependencies>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>easyfk-core</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>service-base</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>web-common</artifactId>
    </dependency>
</dependencies>
```

## 3. BOM 管控范围

### 3.1 框架级 BOM

本 BOM 内部已引入以下框架级 BOM，下游项目**无需重复引入**：

- `spring-boot-dependencies`
- `spring-cloud-dependencies`
- `spring-cloud-alibaba-dependencies`

### 3.2 EasyFK 核心模块

| 坐标（artifactId） | 说明 |
| --- | --- |
| `easyfk-core` | 核心基础模块 |
| `easyfk-authority` | 权限模块 |
| `easyfk-thread` | 线程管理模块 |
| `easyfk-cache` | 缓存抽象模块 |
| `easyfk-repository` | 数据仓储模块 |

### 3.3 EasyFK 服务模块

| 坐标 | 说明 |
| --- | --- |
| `service-api` | 服务 API 定义 |
| `service-base` | 服务基础模块 |

### 3.4 EasyFK Web 模块

| 坐标 | 说明 |
| --- | --- |
| `web-common` | Web 公共模块 |
| `web-micro` | 微服务 Web 模块 |
| `web-prd` | 生产环境 Web 模块 |
| `web-base` | Web 基础模块 |
| `web-simple` | 简单 Web 模块 |

### 3.5 数据库与数据源

| 坐标 | 说明 |
| --- | --- |
| `com.mcst:db-mysql` | EasyFK MySQL 封装 |
| `com.mcst:db-postgresql` | EasyFK PostgreSQL 封装 |
| `com.mcst:db-redis` | EasyFK Redis 封装 |
| `com.mcst:db-mongo` | EasyFK MongoDB 封装 |
| `com.mcst:db-influx` | EasyFK InfluxDB 封装 |
| `com.mcst:db-clickhouse` | EasyFK ClickHouse 封装 |
| `com.mysql:mysql-connector-j` | MySQL 驱动 |
| `org.postgresql:postgresql` | PostgreSQL 驱动 |
| `com.influxdb:influxdb-client-java` | InfluxDB 客户端 |
| `com.alibaba:druid-spring-boot-3-starter` | Druid 连接池（Boot 3） |
| `com.mcst:ds-druid` | EasyFK Druid 依赖聚合 |
| `org.apache.shardingsphere:shardingsphere-jdbc-core-spring-boot-starter` | ShardingSphere 分库分表 |

### 3.6 ORM 框架

| 坐标 | 说明 |
| --- | --- |
| `com.mcst:orm-mybatis` | EasyFK MyBatis 封装 |
| `com.mcst:orm-flex` | EasyFK MyBatis-Flex 封装 |
| `com.mcst:orm-hibernate` | EasyFK Hibernate 封装 |
| `com.mcst:orm-sharding` | EasyFK 分片 ORM 封装 |
| `com.baomidou:mybatis-plus-spring-boot3-starter` | MyBatis-Plus |
| `com.baomidou:dynamic-datasource-spring-boot3-starter` | 动态数据源 |

### 3.7 缓存

| 坐标 | 说明 |
| --- | --- |
| `com.mcst:cache-redis` | Redis 缓存实现 |
| `com.mcst:cache-caffeine` | Caffeine 缓存实现 |
| `com.github.ben-manes.caffeine:caffeine` | Caffeine |
| `org.redisson:redisson` | Redisson |

### 3.8 分布式锁

| 坐标 | 说明 |
| --- | --- |
| `com.mcst:lock-redisson` | Redisson 分布式锁 |

### 3.9 消息队列

| 坐标 | 说明 |
| --- | --- |
| `com.mcst:mq-common` | MQ 公共模块 |
| `com.mcst:mq-kafka` | Kafka 实现 |
| `com.mcst:mq-rocket` | RocketMQ 实现 |
| `com.mcst:mq-rabbit` | RabbitMQ 实现 |
| `org.apache.rocketmq:rocketmq-spring-boot-starter` | RocketMQ Starter |
### 3.10 微服务组件

| 坐标 | 说明 |
| --- | --- |
| `com.mcst:registry-nacos` | Nacos 注册中心 |
| `com.mcst:config-nacos` | Nacos 配置中心 |
| `com.mcst:protect-sentinel` | Sentinel 流量防护 |
| `com.mcst:easyfk-gateway` | 网关模块 |
| `com.mcst:rpc-cloud` | Spring Cloud RPC |
| `com.mcst:rpc-dubbo` | Dubbo RPC |
| `com.mcst:remote-cloud` | Cloud 远程调用 |
| `com.mcst:remote-dubbo` | Dubbo 远程调用 |
| `com.mcst:transaction-seata` | Seata 分布式事务 |
| `org.apache.dubbo:dubbo-spring-boot-starter` | Dubbo Starter |
| `org.apache.dubbo:dubbo-registry-nacos` | Dubbo Nacos 注册 |

### 3.11 日志

| 坐标 | 说明 |
| --- | --- |
| `com.mcst:log-log4j2` | EasyFK Log4j2 封装 |
| `com.mcst:log-logback` | EasyFK Logback 封装 |
| `net.logstash.logback:logstash-logback-encoder` | Logstash 日志编码器 |
| `org.apache.skywalking:apm-toolkit-log4j-2.x` | SkyWalking Log4j2 |
| `org.apache.skywalking:apm-toolkit-logback-1.x` | SkyWalking Logback |

### 3.12 文档 / API

| 坐标 | 说明 |
| --- | --- |
| `com.mcst:doc-knife4j` | EasyFK Knife4j 封装 |
| `com.github.xiaoymin:knife4j-openapi3-jakarta-spring-boot-starter` | Knife4j OpenAPI3 |
| `io.swagger.core.v3:swagger-annotations` | Swagger 注解 |

### 3.13 工具与扩展

| 坐标 | 说明 |
| --- | --- |
| `com.mcst:autoId-api` | 自增 ID 接口 |
| `com.mcst:autoId-redis` | 自增 ID Redis 实现 |
| `com.mcst:job-xxl` | XXL-Job 封装 |
| `com.xuxueli:xxl-job-core` | XXL-Job |
| `io.github.linpeilie:mapstruct-plus-spring-boot-starter` | MapStruct Plus |
| `com.alibaba:easyexcel` | EasyExcel |
| `com.squareup.okhttp3:okhttp` | OkHttp |

### 3.14 第三方基础库

| 坐标 | 说明 |
| --- | --- |
| `com.alibaba.fastjson2:fastjson2` | FastJSON2 |
| `com.esotericsoftware:kryo` | Kryo 序列化 |
| `org.slf4j:slf4j-api` | SLF4J API |
| `org.projectlombok:lombok` | Lombok |
| `cn.hutool:hutool-all` | Hutool 工具集 |
| `com.github.ulisesbocchio:jasypt-spring-boot-starter` | Jasypt 配置加密 |
| `io.swagger.core.v3:swagger-annotations` | Swagger 注解 |
| `org.dromara.sms4j:sms4j-spring-boot-starter` | 短信聚合 |

### 3.15 WebSocket

| 坐标 | 说明 |
| --- | --- |
| `com.mcst:websocket-api` | WebSocket API |
| `com.mcst:websocket-server` | WebSocket 服务端 |

### 3.16 存储组件

| 坐标 | 说明 |
| --- | --- |
| `com.mcst:queue-disruptor` | Disruptor 队列 |
| `com.mcst:chronicle-map` | Chronicle Map 封装 |
| `com.mcst:chronicle-queue` | Chronicle Queue 封装 |
| `net.openhft:chronicle-map` | Chronicle Map |
| `net.openhft:chronicle-queue` | Chronicle Queue |

### 3.17 微信开发

| 坐标 | 说明 |
| --- | --- |
| `com.github.binarywang:wx-java-miniapp-spring-boot-starter` | 小程序 |
| `com.github.binarywang:wx-java-mp-spring-boot-starter` | 公众号 |
| `com.github.binarywang:wx-java-pay-spring-boot-starter` | 微信支付 |
| `com.github.binarywang:wx-java-cp-spring-boot-starter` | 企业微信 |

### 3.18 ClickHouse

| 坐标 | 说明 |
| --- | --- |
| `com.clickhouse:clickhouse-jdbc` | ClickHouse JDBC |
| `org.apache.httpcomponents.client5:httpclient5` | HttpClient5 |
| `org.apache.httpcomponents.core5:httpcore5` | HttpCore5 |

### 3.19 序列化

| 坐标 | 说明 |
| --- | --- |
| `com.mcst:serializer-base` | 序列化抽象 |
| `com.mcst:serializer-fory` | Apache Fory 序列化实现 |

### 3.20 Aeron

| 坐标 | 说明 |
| --- | --- |
| `com.mcst:aeron-common`、`aeron-store` | 公共模型与存储 |
| `com.mcst:aeron-codec-sbe` / `-protobuf` / `-json` / `-fory` | 编解码 |
| `com.mcst:aeron-compression-lz4` / `-zstd` | 压缩 |
| `com.mcst:aeron-driver`、`aeron-producer`、`aeron-producer-outbox`、`aeron-consumer` | 驱动与收发 |
| `com.mcst:aeron-metrics-micrometer`、`aeron-chronicle`、`aeron-spring-boot-starter` | 监控、持久化、Starter |
| `com.mcst:aeron-cluster-core`、`aeron-cluster-client`、`aeron-cluster-spring-boot-starter`、`aeron-cluster-test` | Aeron Cluster（`-test` 仅 `testImplementation`） |
| `com.mcst:etcd-cluster-api`、`etcd-cluster-core`、`etcd-cluster-spring-boot-starter` | etcd 集群协调（core 为 shaded 包，内含重定位的 jetcd/grpc/netty） |

## 4. 典型使用场景

### 4.1 单体 Web 应用

**Gradle：**

```gradle
dependencies {
    implementation platform('com.mcst:easyfk-dependencies:${easyfk.version}')

    implementation 'com.mcst:easyfk-core'
    implementation 'com.mcst:web-base'
    implementation 'com.mcst:orm-mybatis'
    implementation 'com.mcst:db-mysql'
    implementation 'com.mcst:cache-redis'
    implementation 'com.mcst:log-logback'

    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
}
```

**Maven：**

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.mcst</groupId>
            <artifactId>easyfk-dependencies</artifactId>
            <version>${easyfk.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>easyfk-core</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>web-base</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>orm-mybatis</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>db-mysql</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>cache-redis</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>log-logback</artifactId>
    </dependency>
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <scope>provided</scope>
    </dependency>
</dependencies>
```

### 4.2 微服务应用（Nacos + Dubbo）

**Gradle：**

```gradle
dependencies {
    implementation platform('com.mcst:easyfk-dependencies:${easyfk.version}')

    implementation 'com.mcst:easyfk-core'
    implementation 'com.mcst:web-micro'
    implementation 'com.mcst:service-base'
    implementation 'com.mcst:registry-nacos'
    implementation 'com.mcst:config-nacos'
    implementation 'com.mcst:rpc-dubbo'
    implementation 'com.mcst:protect-sentinel'
    implementation 'com.mcst:orm-mybatis'
    implementation 'com.mcst:db-mysql'
    implementation 'com.mcst:cache-redis'
    implementation 'com.mcst:doc-knife4j'
}
```

**Maven：**

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.mcst</groupId>
            <artifactId>easyfk-dependencies</artifactId>
            <version>${easyfk.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>easyfk-core</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>web-micro</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>service-base</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>registry-nacos</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>config-nacos</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>rpc-dubbo</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>protect-sentinel</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>orm-mybatis</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>db-mysql</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>cache-redis</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>doc-knife4j</artifactId>
    </dependency>
</dependencies>
```

### 4.3 网关服务

**Gradle：**

```gradle
dependencies {
    implementation platform('com.mcst:easyfk-dependencies:${easyfk.version}')

    implementation 'com.mcst:easyfk-gateway'
    implementation 'com.mcst:registry-nacos'
    implementation 'com.mcst:config-nacos'
    implementation 'com.mcst:protect-sentinel'
}
```

**Maven：**

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.mcst</groupId>
            <artifactId>easyfk-dependencies</artifactId>
            <version>${easyfk.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>easyfk-gateway</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>registry-nacos</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>config-nacos</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mcst</groupId>
        <artifactId>protect-sentinel</artifactId>
    </dependency>
</dependencies>
```

### 4.4 仅使用第三方库（不依赖 EasyFK 封装）

BOM 同样管控了大量第三方依赖版本，即使不使用 EasyFK 模块也可以直接引用：

**Gradle：**

```gradle
dependencies {
    implementation platform('com.mcst:easyfk-dependencies:${easyfk.version}')

    implementation 'com.baomidou:mybatis-plus-spring-boot3-starter'
    implementation 'com.alibaba:druid-spring-boot-3-starter'
    implementation 'com.mysql:mysql-connector-j'
    implementation 'org.redisson:redisson'
    implementation 'cn.hutool:hutool-all'
}
```

**Maven：**

```xml
<dependencies>
    <dependency>
        <groupId>com.baomidou</groupId>
        <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
    </dependency>
    <dependency>
        <groupId>com.alibaba</groupId>
        <artifactId>druid-spring-boot-3-starter</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mysql</groupId>
        <artifactId>mysql-connector-j</artifactId>
    </dependency>
    <dependency>
        <groupId>org.redisson</groupId>
        <artifactId>redisson</artifactId>
    </dependency>
    <dependency>
        <groupId>cn.hutool</groupId>
        <artifactId>hutool-all</artifactId>
    </dependency>
</dependencies>
```

## 5. 版本覆盖

如果下游项目需要使用与 BOM 不同的版本，可以显式声明版本号进行覆盖。

**Gradle：**

```gradle
dependencies {
    implementation platform('com.mcst:easyfk-dependencies:${easyfk.version}')

    // 显式覆盖版本
    implementation 'cn.hutool:hutool-all:5.x.x'
}
```

**Maven：**

```xml
<dependencies>
    <dependency>
        <groupId>cn.hutool</groupId>
        <artifactId>hutool-all</artifactId>
        <version>5.x.x</version>
    </dependency>
</dependencies>
```

> **注意**：非必要不建议覆盖 BOM 版本，以保持团队依赖一致性。如确需覆盖，请验证兼容性。

## 6. 依赖分组速查

BOM 内部将依赖按领域进行了分组，以下列出各分组及其包含的主要依赖，便于按需选择：

| 分组 | 包含的主要依赖 |
| --- | --- |
| **base** | sms4j、fastjson2、caffeine、kryo、slf4j-api、jasypt、lombok、hutool、swagger-annotations |
| **serializer** | serializer-base、serializer-fory |
| **logging** | log-log4j2、log-logback、logstash-logback-encoder |
| **skywalking** | skywalking-log4j2、skywalking-logback |
| **database** | db-influx、db-redis、db-mongo、db-mysql、db-postgresql、db-clickhouse、influxdb-client、postgresql、shardingsphere |
| **datasource** | druid-spring-boot-3-starter、ds-druid |
| **orm** | orm-flex、orm-hibernate、orm-mybatis、orm-sharding |
| **mybatis** | mybatis-plus-starter、mysql-connector、dynamic-datasource |
| **cache** | cache-redis、cache-caffeine |
| **lock** | lock-redisson |
| **mq** | mq-kafka、mq-rocket、mq-rabbit、mq-common、rocketmq-starter |
| **microservice** | registry-nacos、config-nacos、protect-sentinel、easyfk-gateway |
| **rpc** | rpc-cloud、rpc-dubbo、dubbo-starter、dubbo-registry-nacos、remote-cloud、remote-dubbo |
| **transaction** | transaction-seata |
| **xxl** | xxl-job、job-xxl |
| **tools** | autoId-api、autoId-redis、okhttp、easyexcel |
| **doc** | doc-knife4j、knife4j-starter |
| **easyfkCore** | easyfk-authority、easyfk-core、easyfk-cache、easyfk-thread、easyfk-repository |
| **easyfkService** | service-api、service-base |
| **easyfkWeb** | web-common、web-micro、web-prd、web-base、web-simple |
| **mapstruct** | mapstruct-plus-starter |
| **wxJava** | wx-java-miniapp、wx-java-mp、wx-java-pay、wx-java-cp |
| **clickhouse** | clickhouse-jdbc、httpclient5、httpcore5 |
| **websocket** | websocket-api、websocket-server |
| **storage** | queue-disruptor、chronicle-map、chronicle-queue（EasyFK 封装与 OpenHFT 原始包） |
| **aeron** | aeron-* 全部 EasyFK Aeron 模块与 aeron-cluster-* |
| **etcdCluster** | etcd-cluster-api、etcd-cluster-core、etcd-cluster-spring-boot-starter |

## 7. 常见问题

### Q1：引入 BOM 后是否会把所有依赖都加到项目中？

不会。BOM 只声明版本约束，不引入实际依赖。只有在 `dependencies` 中显式声明的依赖才会被加入项目，BOM 仅负责提供版本号。

### Q2：BOM 中已包含 Spring Boot / Cloud BOM，项目还需要单独引入吗？

不需要。`easyfk-dependencies` 内部已引入 `spring-boot-dependencies`、`spring-cloud-dependencies` 和 `spring-cloud-alibaba-dependencies`，下游项目引入本 BOM 即可获得这些框架的版本管控。

### Q3：Gradle 中 `platform` 和 `enforcedPlatform` 有什么区别？

- `platform`：声明版本建议，下游仍可通过显式声明或传递依赖覆盖版本。
- `enforcedPlatform`：强制使用 BOM 中的版本，即使传递依赖带来了更高版本也会被降级。

### Q4：Maven 项目中如何同时使用 Spring Boot parent 和本 BOM？

使用 Spring Boot 作为 parent 时，将本 BOM 放在 `<dependencyManagement>` 中以 `import` 方式引入即可。对于同一依赖，`<dependencyManagement>` 中先声明的优先生效，可根据需要调整 BOM 的声明顺序。

### Q5：如何查看当前 BOM 管控的具体版本号？

- **Gradle 项目**：执行 `./gradlew dependencies` 查看解析后的完整依赖树及版本。
- **Maven 项目**：执行 `mvn dependency:tree` 或 `mvn help:effective-pom` 查看实际生效的版本。

### Q6：私服地址如何配置？

本 BOM 发布在公司私服中，需要在构建配置中添加私服仓库地址：

**Gradle**（`build.gradle` 或 `settings.gradle`）：

```gradle
repositories {
    maven { url 'https://your-nexus-host/repository/maven-public/' }
}
```

**Maven**（`pom.xml` 或 `settings.xml`）：

```xml
<repositories>
    <repository>
        <id>company-nexus</id>
        <url>https://your-nexus-host/repository/maven-public/</url>
    </repository>
</repositories>
```
