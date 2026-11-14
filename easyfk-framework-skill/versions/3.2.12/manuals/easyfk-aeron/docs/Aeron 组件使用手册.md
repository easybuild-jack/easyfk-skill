# Aeron 组件使用手册（easyfk-aeron）

> 面向 **业务开发工程师** 的一站式使用手册。看完这一篇即可独立完成「引依赖 → 发消息 → 收消息 → 上生产」的全流程，不必再翻多篇文档。
>
> **推荐接入方式：Spring Boot 服务直接用 `aeron-spring-boot-starter`**（见 [§5](#5-5-分钟快速上手spring-boot-starter推荐主线) / [§17](#17-spring-boot-starter-完全指南)），业务代码只写 `@Autowired Producer` + `@AeronTopic`。非 Spring 或需要底层掌控时再走核心 SDK（[§6](#6-快速上手核心-sdk--非-spring)）。
>
> 本手册整合了原《Spring Boot 接入指南》《发送端使用手册》《接收端使用手册》，并**以仓库当前源码为准**校订了坐标 / 包名 / 配置前缀等信息（包名 `com.mcst.aeron.*`，配置前缀 `easyfk.config.aeron`）。**组件版本由框架 BOM 统一管理，引入模块时无需指定版本号。** 深入某个专题时，可再跳转文末[相关文档](#20-相关文档)。

---

## 目录

1. [组件是什么 / 解决什么问题](#1-组件是什么--解决什么问题)
2. [适用场景与选型](#2-适用场景与选型)
3. [整体架构与模块地图](#3-整体架构与模块地图)
4. [环境要求与坐标](#4-环境要求与坐标)
5. [5 分钟快速上手（Spring Boot Starter，推荐主线）](#5-5-分钟快速上手spring-boot-starter推荐主线)
6. [快速上手（核心 SDK / 非 Spring）](#6-快速上手核心-sdk--非-spring)
7. [核心概念](#7-核心概念)
8. [Driver 模块（接入 Aeron）](#8-driver-模块接入-aeron)
9. [Producer 模块（发送端）](#9-producer-模块发送端)
10. [Consumer 模块（接收端）](#10-consumer-模块接收端)
11. [Codec 模块（序列化）](#11-codec-模块序列化)
12. [Compression 模块（压缩）](#12-compression-模块压缩)
13. [按 key 分片与静态分组消费](#13-按-key-分片与静态分组消费)
14. [Outbox 模块（先持久化再转发）](#14-outbox-模块先持久化再转发)
15. [Metrics 模块（监控）](#15-metrics-模块监控)
16. [Chronicle 模块（状态物化）](#16-chronicle-模块状态物化)
17. [Spring Boot Starter 完全指南](#17-spring-boot-starter-完全指南)
18. [配置项完整参考](#18-配置项完整参考)
19. [常见问题 / 排查手册（FAQ）](#19-常见问题--排查手册faq)
20. [相关文档](#20-相关文档)

---

## 1. 组件是什么 / 解决什么问题

`easyfk-aeron` 是基于 [Aeron](https://github.com/aeron-io/aeron) 的**超低时延消息广播 SDK**，把「一个发送方 → N 个接收方」的消息投递封装成简单、类型安全的 Java API。它面向对**延迟**敏感、消息量大的场景（行情、订单流、事件广播）。

在 Spring Boot 项目中，**推荐通过 `aeron-spring-boot-starter` 接入**：业务方零样板（`@Autowired Producer` + `@AeronTopic`），driver / bean / 生命周期全托管。核心 SDK 保持 0 Spring 依赖，作为底层与非 Spring 场景的接入方式。

**它做什么：**

- 把业务对象序列化成紧凑的二进制帧，通过 Aeron 的 IPC（共享内存）/ UDP 单播 / UDP 多播（MDC）发出去，接收端自动反序列化回业务对象。
- 提供背压策略、按 key 分片、静态分组消费、去重、压缩、监控等生产必需能力。
- 可选叠加 **Outbox（先落盘再转发）** 保证「生产侧不丢」，以及 **Chronicle** 把事件流物化成持久化 KV 状态表。

**它不做什么（边界）：**

- **不持久化消息、不做 ack、不做 replay**。这是纯 fan-out 广播语义 —— 掉线 / 晚加入的接收方收不到历史消息。需要这些能力请用 Kafka / Pulsar / RocketMQ，或 Aeron Archive / Cluster。
- Outbox 保证的是「发送方发出去前先落盘、失败能重发」，**不是**「给消费方补历史」。

**核心特征：**

| 特征 | 说明 |
|---|---|
| 超低时延 | IPC 亚微秒级、UDP 微秒级 |
| 0 Spring 依赖内核 | 核心 SDK 不依赖 Spring；starter 是可选层 |
| 多序列化 | JSON / Protobuf / SBE / Fory / 自定义 codec |
| 跨语言 wire 协议 | 帧布局有明确规约，可与 Go / C++ / .NET / Rust 互通 |
| 按 key 分片 | 同 key 严格 FIFO，跨 key 并行提升吞吐 |

---

## 2. 适用场景与选型

### 2.1 典型场景

| 场景 | 推荐搭配 |
|---|---|
| 同机进程间高频广播（行情分发、撮合→风控） | `ipc` 通道 + `INLINE` + `BUSY_SPIN` |
| 单机内多线程/单 JVM 解耦 | `ipc` 通道 + 默认配置 |
| 跨主机点对点 | `udpUnicast` |
| 一发多收、订阅方动态加入（行情 fan-out 核心场景） | `udpMdc` |
| 订单流按客户保序、又要并行提吞吐 | 多 partition 分片 + 按 key `send` |
| 下游多实例分摊消费 | 静态分组消费（`partitionAssignment`） |
| 账务/行情快照「发送侧绝不能丢」 | Outbox（`outbox.enabled=true`）+ consumer 端去重 |
| 事件流 → 可查询状态表 | Chronicle 状态物化 |

### 2.2 什么时候**不**该用本组件

需要以下任一能力时，应改用成熟 broker（Kafka / Pulsar / RocketMQ）：

- 消费方掉线后需要**补历史 / replay**；
- 消费端**ack + 重投**、消费位点持久化；
- **自动 rebalance**（本组件是静态分组，扩缩容需改配置重启）；
- 跨实例**全局有序**。

---

## 3. 整体架构与模块地图

### 3.1 数据流

```
                                            ┌─────────────┐
业务对象 ──► Codec 编码 ──► (可选)压缩 ──► 成帧 ──►│  Aeron 传输  │──► 成帧解析 ──► (可选)解压 ──► 去重 ──► Codec 解码 ──► 业务 handler
   Producer 侧                              │ ipc/udp/mdc │                        Consumer 侧
                                            └─────────────┘
```

一条消息在线上是一帧（frame）：`40 字节 frame header + topic 字节 + payload 字节`。header 里带 codecId / compressionId / 128-bit msgId / 发送时间戳等。详见 [aeron 协议说明](aeron协议说明.md)。

### 3.2 模块清单

包名统一为 `com.mcst.aeron.*`。所有模块坐标 `com.mcst:<module>`，**版本由框架 BOM 统一管理，引依赖时不写版本号**。

| 模块 | 作用 | 什么时候引 |
|---|---|---|
| `aeron-common` | 帧协议、Codec/Compression 接口、config、partition、metrics SPI | 传递依赖，一般不用直接引 |
| `aeron-driver` | 接入 Aeron MediaDriver（`DriverManager`） | 必引（内核路径） |
| `aeron-producer` | 发送端 `AeronProducer` | 发消息就引 |
| `aeron-consumer` | 接收端 `AeronConsumer` | 收消息就引 |
| `aeron-codec-json` | Jackson JSON codec | 需要 JSON 时 |
| `aeron-codec-protobuf` | Protobuf codec | 需要 Protobuf 时 |
| `aeron-codec-sbe` | SBE codec 框架 | 需要 SBE 时 |
| `aeron-codec-fory` | Apache Fory 二进制 codec（POJO 即用） | 需要零配置 POJO / 跨语言时 |
| `aeron-compression-lz4` | LZ4 压缩 | 需要压缩、速度优先 |
| `aeron-compression-zstd` | Zstd 压缩 | 需要压缩、压缩率优先 |
| `aeron-store` | 通用 store-and-forward WAL 内核 | Outbox 传递依赖 |
| `aeron-producer-outbox` | Outbox（先落盘再转发）装饰器 | 需要「生产侧不丢」时 |
| `aeron-metrics-micrometer` | Micrometer 指标适配 | 需要 Prometheus/Grafana 时 |
| `aeron-chronicle` | 事件流 → Chronicle Map 状态物化 | 需要可查询状态表时 |
| `aeron-spring-boot-starter` | Spring Boot 自动装配（可选层） | 用 Spring Boot 且想少写样板 |
| `aeron-examples` | 可运行示例 | 学习 / 参考 |

### 3.3 两种接入姿势

- **Spring Boot Starter（推荐主线，业务方默认走这条）**：`@Autowired Producer` + `@AeronTopic`，driver 启停 / bean 装配 / 健康检查 / 优雅停机全托管。见 [§5](#5-5-分钟快速上手spring-boot-starter推荐主线)、[§17](#17-spring-boot-starter-完全指南)。
- **核心 SDK（手写 builder / 非 Spring）**：0 Spring 依赖，完全掌控 bean 生命周期与线程；starter 底层用的就是它。见 [§6](#6-快速上手核心-sdk--非-spring)、[§8~§14](#8-driver-模块接入-aeron)。

> 两条路径产出的 `AeronProducer` / `AeronConsumer` 完全等价，可混用。§8~§16 的模块细节（Driver/Producer/Consumer/Codec/压缩/分片/Outbox…）**两种姿势通用**：用 starter 时，这些能力通过 [§17](#17-spring-boot-starter-完全指南) 的 yaml 配置暴露，底层语义与核心 SDK 一致。

---

## 4. 环境要求与坐标

| 项 | 要求 |
|---|---|
| JDK | **21+**（项目 `sourceCompatibility = 21`） |
| Aeron | 1.52.1（由本组件传递） |
| Spring Boot（仅用 starter 时） | **≥ 2.6.13**（starter 启动期由 `SpringBootVersionCheck.requireAtLeast("2.6.13")` 校验，无上限；同时提供 `spring.factories` 与 `AutoConfiguration.imports`，兼容 Boot 2.x / 3.x） |
| Maven 坐标 | `group = com.mcst`；**版本由框架 BOM 统一管理，引模块不指定版本** |

### 4.1 JVM 启动参数（必须）

JDK 21+ 跑 Aeron / Agrona 必须开放反射，否则启动即崩：

```
--add-opens java.base/java.lang=ALL-UNNAMED
--add-opens java.base/java.lang.reflect=ALL-UNNAMED
--add-opens java.base/java.io=ALL-UNNAMED
--add-opens java.base/java.nio=ALL-UNNAMED
--add-opens java.base/java.util.zip=ALL-UNNAMED
--add-opens java.base/sun.nio.ch=ALL-UNNAMED
--add-opens java.base/jdk.internal.misc=ALL-UNNAMED
```

放到业务进程的 `JAVA_OPTS` / Gradle `applicationDefaultJvmArgs` / Dockerfile `ENTRYPOINT`。

### 4.2 依赖引入

**核心 SDK（发送端最小依赖）：**

```groovy
dependencies {
    implementation 'com.mcst:aeron-driver'
    implementation 'com.mcst:aeron-producer'   // 收端换成 aeron-consumer

    // 按需选 codec（不引就只能发 byte[] / String）
    implementation 'com.mcst:aeron-codec-json'
    implementation 'com.mcst:aeron-codec-fory'
    // implementation 'com.mcst:aeron-codec-protobuf'
    // implementation 'com.mcst:aeron-codec-sbe'

    // 按需选压缩
    // implementation 'com.mcst:aeron-compression-lz4'
    // implementation 'com.mcst:aeron-compression-zstd'

    // 核心 SDK 只传递 slf4j-api，不带日志实现：非 Spring 项目自行加一个（如 runtimeOnly 'ch.qos.logback:logback-classic'）；
    // Spring Boot / easyfk 项目已自带 Logback，不要再加 slf4j-simple 等第二个 SLF4J 实现
}
```

**Spring Boot Starter：**

```groovy
dependencies {
    implementation 'com.mcst:aeron-spring-boot-starter'
    implementation 'com.mcst:aeron-codec-fory'   // 触发零配置 POJO 默认兜底

    // 可选监控
    // implementation 'com.mcst:aeron-metrics-micrometer'
    // implementation 'org.springframework.boot:spring-boot-starter-actuator'
}
```

> starter 通过 `api` 传递带入 `aeron-driver` / `aeron-producer` / `aeron-consumer` / `aeron-common` / `aeron-producer-outbox`；codec / compression / micrometer 不绑定，业务按需引。所有 Spring 坐标在 starter 里是 `compileOnly`，不会污染业务方的 Spring BOM。

---

## 5. 5 分钟快速上手（Spring Boot Starter，推荐主线）

> **这是业务服务接入本组件的推荐方式。** 引 starter 后，driver 启停 / bean 装配 / `@AeronTopic` 订阅 / 健康检查 / 优雅停机全部自动托管，业务代码只写 `@Autowired Producer` 发 + `@AeronTopic` 收。完整能力见 [§17](#17-spring-boot-starter-完全指南)。

单进程 IPC，一个 producer 发，一个 `@AeronTopic` 收。

**① 依赖（Gradle）：**

```groovy
dependencies {
    implementation 'com.mcst:aeron-spring-boot-starter'
    implementation 'com.mcst:aeron-codec-fory'   // 触发零配置 POJO 默认兜底
}
```

同时确保业务进程带上 [§4.1 的 JVM `--add-opens` 参数](#41-jvm-启动参数必须)。

**② `application.yml`：**

```yaml
easyfk:
  config:
    aeron:
      driver:                          # 单 driver 简化路径
        embedded: true
        aeron-dir: /dev/shm/aeron-demo
        dir-delete-on-start: true      # 开发期单进程 OK；生产/多 JVM 同机务必 false
```

**③ 订阅端：**

```java
import com.mcst.aeron.spring.annotation.AeronTopic;
import com.mcst.aeron.consumer.MessageContext;
import org.springframework.stereotype.Component;

@Component
public class DemoSubscriber {

    @AeronTopic(value = "demo.ping", payloadType = byte[].class)
    public void onPing(byte[] payload, MessageContext ctx) {
        System.out.println("got " + ctx.topic() + " size=" + payload.length);
    }
}
```

**④ 发送端：**

```java
import com.mcst.aeron.producer.Producer;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class DemoSender {

    @Autowired
    private Producer producer;          // 推荐按接口注入（兼容 outbox）

    public void sendOnce() {
        producer.send("demo.ping", "hello".getBytes());
    }
}
```

启动时 driver 随 bean 就绪，starter 在生命周期早期完成 `@AeronTopic` 订阅注册并启动 poll 线程；关闭时按 `consumer → producer → driver` 反向优雅停机。`/actuator/health` 自带 `aeron` 子项。

> ⚠️ `@PostConstruct` / `ContextRefreshedEvent` 执行时订阅可能尚未建立、poll 线程尚未启动，此时本进程发消息本进程的 listener 可能收不到。需要"启动即发"请放到 `ApplicationRunner` 或 `ApplicationReadyEvent` 里。

> 想要一份把 driver / producer / consumer / codec / metrics / shutdown 全列齐的**完整可复制 `application.yml`**，见 [§17.0 一分钟接入](#170-一分钟接入完整依赖--配置--代码)。

---

## 6. 快速上手（核心 SDK / 非 Spring）

> 不使用 Spring、或需要完全掌控 bean 生命周期与线程模型时走这条路径（starter 底层用的就是它）。两条路径产出的 `AeronProducer` / `AeronConsumer` 完全等价、可混用。

同进程 IPC，一发一收。**发送端：**

```java
import com.mcst.aeron.driver.DriverConfig;
import com.mcst.aeron.driver.DriverManager;
import com.mcst.aeron.producer.AeronProducer;

import java.nio.charset.StandardCharsets;

try (DriverManager driver = DriverManager.embedded(DriverConfig.defaults());
     AeronProducer producer = AeronProducer.builder().driver(driver).build()) {

    while (!producer.isConnected()) Thread.sleep(20);   // 等接收方接进来
    producer.send("demo.ping", "hello".getBytes(StandardCharsets.UTF_8));
}
```

**接收端：**

```java
import com.mcst.aeron.consumer.AeronConsumer;
import com.mcst.aeron.driver.DriverConfig;
import com.mcst.aeron.driver.DriverManager;

import java.nio.charset.StandardCharsets;

try (DriverManager driver = DriverManager.embedded(DriverConfig.defaults());
     AeronConsumer consumer = AeronConsumer.builder().driver(driver).build()) {

    consumer.subscribe("demo.ping", byte[].class, (payload, ctx) -> {
        System.out.printf("topic=%s  latency=%dus  body=%s%n",
                ctx.topic(), ctx.latencyMicros(),
                new String(payload, StandardCharsets.UTF_8));
    });
    consumer.start();          // 启动 poll 线程后才开始消费

    Thread.sleep(60_000);      // 实际服务里换成业务的等待逻辑
}
```

**仓库内直接跑现成示例：**

```bash
./gradlew :aeron-examples:run                    # IPC ping/pong（默认 IpcPingPong）
./gradlew :aeron-examples:runJsonDemo            # IPC + JSON codec
./gradlew :aeron-examples:runForyDemo            # IPC + Fory codec
./gradlew :aeron-examples:runSbeMarketDataDemo   # IPC + 手写 SBE 行情
./gradlew :aeron-examples:runUdpProducer         # UDP MDC producer
./gradlew :aeron-examples:runUdpConsumer         # UDP MDC consumer
./gradlew :aeron-examples:runShardedBroadcastDemo # 4 分片 + 静态分组消费
./gradlew :aeron-examples:runChronicleStateDemo  # 事件流物化到 Chronicle Map
```

对应源码在 `aeron-examples/src/main/java/com/mcst/aeron/examples/`：`IpcPingPong` / `JsonIpcDemo` / `ForyIpcDemo` / `MarketDataSbeDemo` / `UdpFanOut` / `ShardedBroadcastDemo` / `ChronicleStateDemo`，跨语言快速开始在 `xlang/` 子包。

---

## 7. 核心概念

| 概念 | 含义 |
|---|---|
| **Driver** | 接入 Aeron MediaDriver 的句柄（`DriverManager`）。embedded = JVM 内启 driver；external = 连外部独立 driver 进程。 |
| **Topic** | 消息主题字符串。字符集 `[A-Za-z0-9.\-_]`，长度 1..255 字节，精确匹配（V1 不支持通配符）。 |
| **Channel（通道）** | Aeron URI，决定传输方式：`aeron:ipc` / `aeron:udp?endpoint=...` / MDC。 |
| **streamId** | 同一 channel 上区分不同流的 id；两端必须一致（默认 `baseStreamId=1001`）。 |
| **Partition（分片）** | `channels` 列表的下标即 partitionId。单元素=纯 fan-out；多元素=按 key 分片。 |
| **Codec** | 业务对象 ↔ 字节的序列化器，每种类型注册一个；两端类型必须一致。 |
| **msgId** | 每帧携带的 128-bit 消息 id，用于 consumer 去重 + 业务 trace。 |
| **背压（backpressure）** | Aeron 拥塞/无订阅方时 `tryClaim` 返回负值，producer 按策略处理。 |

---

## 8. Driver 模块（接入 Aeron）

`DriverManager`（`aeron-driver`）是所有收发的前置。

### 8.1 两种模式

```java
// 模式 A：嵌入 Driver（当前 JVM 内启动 MediaDriver，最简单）
DriverManager driver = DriverManager.embedded(DriverConfig.defaults());

// 模式 B：外挂 Driver（连接独立运行的 aeron-driver 进程，多 JVM 共用）
DriverManager driver = DriverManager.external("/dev/shm/aeron");
```

| 场景 | 推荐 |
|---|---|
| 单 JVM、demo、单机服务 | `embedded` |
| 同机多 JVM（producer 与 consumer 分进程） | `external`，或各自 `embedded` + 不同 `aeronDir` |
| 容器化、运维独立部署 | `external` 连 sidecar |

`DriverManager` 公开方法：`aeronClient()`（底层 `io.aeron.Aeron`）、`aeronDir()`、`isEmbedded()`、`close()`。

### 8.2 `DriverConfig` 字段

`DriverConfig.defaults()` 或 `DriverConfig.builder()`：

| Builder 方法 | 默认 | 说明 |
|---|---|---|
| `aeronDir(String)` | `null`（Aeron 选 OS 默认目录） | MediaDriver 共享目录 |
| `threadingMode(ThreadingMode)` | `SHARED` | `SHARED` / `SHARED_NETWORK` / `DEDICATED`（低延迟首选）/ `INVOKER`；仅 embedded 生效 |
| `driverIdleStrategy(IdleStrategyType)` | `null`（Aeron 内置退避） | driver 线程空转策略；仅 embedded 生效 |
| `dirDeleteOnStart(boolean)` | `true` | **多 JVM 同机务必置 false** |
| `dirDeleteOnShutdown(boolean)` | `true` | 关闭时是否删目录 |
| `driverTimeoutMs(long)` | `10_000` | driver 超时 |

### 8.3 同机多 JVM 共享 aeronDir（重要）

同机两个 JVM 若都用 embedded：必须用**不同的** `aeronDir`，且**不要**开 `dirDeleteOnStart`，否则后启动的 driver 擦掉先启动的目录导致其瞬间崩溃。

```java
DriverConfig cfg = DriverConfig.builder()
        .aeronDir("/dev/shm/aeron-svc1")
        .dirDeleteOnStart(false)
        .dirDeleteOnShutdown(false)
        .build();
DriverManager driver = DriverManager.embedded(cfg);
```

---

## 9. Producer 模块（发送端）

### 9.1 三步走

```
DriverManager ──► AeronProducer ──► producer.send(topic, payload)
  (1) 接入 Aeron    (2) 构造 publication    (3) 写一帧
```

```java
AeronProducer producer = AeronProducer.builder()
        .driver(driver)                                  // 必填；driver 由调用方负责关闭
        // .ownDriver(driver)                            // 或：托管 driver，producer.close() 连带关闭
        .config(ProducerConfig.builder()
                .channels(ChannelSpec.ipc())             // 默认单 partition IPC
                .baseStreamId(1001)
                .build())
        .codec(JsonCodec.forType(Order.class))           // 注册业务类型 codec，可多次调
        .compression(Lz4Compression.INSTANCE)            // 可选
        .metrics(myProducerMetrics)                      // 可选
        .build();
```

### 9.2 发送 API

```java
// 不指定 key（内置 snowflake 生成 msgId）
long pos = producer.send("orders.new", order);

// 显式 key：同 key 严格 FIFO（多 partition 下保序的唯一手段）
producer.send("orders.new", customerId, order);

// 业务自带 128-bit msgId（订单号 / trace id）
producer.send("orders.new", order, traceIdHigh, traceIdLow);
producer.send("orders.new", customerId, order, traceIdHigh, traceIdLow);

// 同 topic 批量发（topic 编码/校验只走一次缓存路径）
producer.sendAll("orders.new", List.of(o1, o2, o3));               // 不给 key：跨消息可能落不同 partition
producer.sendAll("orders.new", customerId, List.of(o1, o2, o3));   // 同 key：全部进同一 partition、保 FIFO
```

返回值：`send` 成功返回 ≥0（直发是 Aeron 写入 position，Outbox 是 WAL 序号，**只判符号别比数值**），按背压策略丢弃返回 `-1`；`sendAll` 返回成功条数。

> ⚠️ 多 partition + 不给 key 时按 `NoKeyStrategy`（默认 `ROUND_ROBIN`）逐条独立选 partition，跨消息不保 FIFO。要保序请传 key。

### 9.3 通道选择

```java
ChannelSpec.ipc();                          // 同机零拷贝共享内存
ChannelSpec.ipcUntethered();                // 仅订阅端：脱钩慢订阅，不顶住 publication
ChannelSpec.udpUnicast("10.0.0.5:40456");   // 1→1 网点
ChannelSpec.udpMdc("224.0.1.1", 40456);     // 1→N，订阅方动态加入
```

| 通道 | 时延 | 跨进程 | 跨主机 | 适用 |
|---|---|---|---|---|
| `ipc()` | 亚微秒 | 同 driver | 否 | 同机进程间 / 同 JVM |
| `ipcUntethered()` | 亚微秒 | 同 driver | 否 | 同机 fan-out，且允许慢订阅自己丢帧 |
| `udpUnicast` | 微秒 | 是 | 是 | 点对点 |
| `udpMdc` | 微秒 | 是 | 是 | 多订阅者 fan-out（核心场景） |

producer 与 consumer 必须用**同样长度的 `channels` 列表 + 同一 `baseStreamId`**，否则 partition 配不齐会静默丢消息（starter 启动期会 warn）。

> **`ipcUntethered()` 只对订阅端有意义。** Aeron 默认 tethered：publication 的写入上限取**最慢订阅**的位置，一个活着但不消费的订阅会顶住所有订阅者，最终把 producer 逼进背压。untethered 订阅落后超过窗口时由 driver 摘除、稍后从最新位置重新加入——**它自己丢帧，不连累别人**。
>
> 它只改 tether 行为，不改传输端点：partition / streamId 展开时仍按 `aeron:ipc` 计算（`ChannelSpec.transportUri()`），所以 producer 用 `ipc()`、consumer 用 `ipcUntethered()` 仍落在同一批 `(channel, streamId)` 上。代价是**慢订阅会真的丢消息**，只适合可丢的快照 / 行情类订阅，不要用在有 at-least-once 语义要求的链路上。

### 9.4 背压策略与错误处理

`ProducerConfig.builder().backpressure(...).backpressureRetries(100)`：

| 策略 | transient 背压 | terminal 时 | 适用 |
|---|---|---|---|
| `RETRY_THEN_FAIL`（默认） | 退避重试 N 次后抛 `BackpressureException` | 抛 `PublicationTerminalException` | 折中默认，业务可感知 |
| `BLOCK` | 自旋 idle 直到塞进去（业务线程**无限阻塞**） | 抛 `PublicationTerminalException` | 绝不丢且能容忍阻塞 |
| `FAIL` | 一次失败立刻抛 `BackpressureException` | 抛 `PublicationTerminalException` | 请求-响应同步链路 |
| `DROP_NEWEST` | 静默丢当前消息 + `metrics.onDropped` | 同 transient | 行情快照「宁丢勿堵」 |

异常层次：

```
AeronMqException                     // 运行期总基类
├── BackpressureException            // tryClaim 负值
│   └── PublicationTerminalException // publication 已死，需重建 producer
├── CodecException                   // encode 失败 / 未注册 codec
├── CompressionException             // 压缩失败
└── FrameDecodeException             // 帧畸形（一般在 consumer 端）
```

典型 catch：

```java
try {
    producer.send(topic, payload);
} catch (PublicationTerminalException e) {
    // publication 已死：关旧 producer，重建一个（嵌入 driver 模式 driver 也要重起）
    rebuildProducer();
} catch (BackpressureException e) {
    // 订阅者跟不上：重试 / 降级 / 入 outbox
    log.warn("backpressure on {}: {}", topic, e.aeronResult());
} catch (AeronMqException e) {
    // codec / frame too large / producer closed 等
    log.error("send failed on {}", topic, e);
}
```

### 9.5 帧大小上限

单帧（`40 字节 header + topic + payload`）不得超过 `publication.maxPayloadLength()`（多 partition 取各 publication 的最小值）。**本 SDK 走 `tryClaim`，整帧必须落进单个 MTU 分片，不会被 Aeron 自动 fragment**，所以真正的上限是 `mtu − 32`，而不是 term buffer 长度：

```
AeronMqException: frame size 12345678 exceeds publication.maxPayloadLength 1376 (调大 mtu、开启压缩或拆分消息)
```

应对（按优先级）：

1. **调大 MTU**（首选）：核心 SDK 用 `DriverConfig.builder().mtuLength(8192)`（UDP）/ `.ipcMtuLength(8192)`；starter 配 `driver.mtu-length: 8KB` / `driver.ipc-mtu-length: 8KB`（§18.2）。约束：32 的倍数、上限 `65504`；UDP 超过 1500 会触发 IP 分片，需网络支持 jumbo frames，IPC 无此顾虑可放心调大。
2. 外部 driver（`embedded=false`）时在 driver 侧配 `aeron.mtu.length` / `aeron.ipc.mtu.length`，并保证**双端 driver 配置一致**。
3. 业务侧分块（SDK 不自动 fragment）。

### 9.6 线程模型（重要）

`AeronProducer` 底层是 `ExclusivePublication`，**single-writer**：

- `send` / `sendAll` / `close` **必须由同一线程调用**。
- 并发发送：业务侧串行化（单线程 + 队列），或每个发送线程各自 `build()` 一个 producer 实例（共享同一 driver）。
- `close()` 必须 happens-after 所有 send。`isConnected()` 可任意线程读。
- producer 实例本身可被多 service 引用，但发送动作要串行。

### 9.7 消息 id

每帧带 128-bit msgId，用于去重 + trace：默认内置 snowflake（`.messageIdGenerator(myGenerator)` 可替换）；或每次发送显式传 `idHigh/idLow`。配合 consumer 端 dedup 使用效果最佳（见 [§10.6](#106-去重dedup)）。

---

## 10. Consumer 模块（接收端）

### 10.1 四步走

```
DriverManager ──► AeronConsumer ──► subscribe(topic, type, handler) ──► start()
```

```java
AeronConsumer consumer = AeronConsumer.builder()
        .driver(driver)                                     // 必填
        .config(ConsumerConfig.builder()
                .channels(ChannelSpec.ipc())                // 必须与 producer 等长
                .baseStreamId(1001)                         // 必须与 producer 对齐
                .deliveryMode(DeliveryMode.RING_BUFFER_POOL)// 默认
                .workerThreads(4)
                .dedupWindow(1 << 16)                       // 64k 槽位去重（每 partition 独立）
                .maxDecompressedBytes(16 * 1024 * 1024)
                .build())
        .codec(JsonCodec.forType(Order.class))
        .metrics(myConsumerMetrics)
        .build();

consumer.subscribe("orders.new", Order.class, (order, ctx) -> {
    log.info("got {} latency={}us", order, ctx.latencyMicros());
});
consumer.start();
```

约束：

- **重复订阅同一 topic 抛 `IllegalStateException`**（一个 topic 一个 handler）。
- `payloadType` 必须已注册 codec，否则 `subscribe` 抛 `AeronMqException: no codec registered for payload type X`。
- `subscribe` 可在 `start` 前后调用；运行期动态加订阅支持（V1 不支持单 topic 退订）。

### 10.2 多 topic / 多类型

一个 consumer 可订阅 N 个 topic，同 codec 可注册多种类型（Protobuf 同 wire id 靠 `payloadType` 派发）：

```java
consumer.subscribe("orders.new",  Order.class,      orderHandler);
consumer.subscribe("trades.tick", Trade.class,      tradeHandler);
consumer.subscribe("orders.pb",   OrderProto.class, orderPbHandler);
```

### 10.3 消息回调与 `MessageContext`

```java
@FunctionalInterface
public interface MessageHandler<T> {
    void onMessage(T payload, MessageContext ctx);
}
```

`MessageContext` 字段：

| 方法 | 含义 |
|---|---|
| `topic()` | 帧上的 topic 名 |
| `partition()` | 消息所在 partitionId；单 partition 恒为 0 |
| `msgIdHigh()` / `msgIdLow()` | 128-bit msgId |
| `timestampNanos()` | producer 写入时刻（墙钟纳秒） |
| `codecId()` | wire codec id（一般不用看） |
| `compressionId()` | 压缩算法 id；0=未压缩 |
| `latencyMicros()` | 收到时刻 − 发送时刻（µs）；负数/时钟漂移返回 0 |

> `latencyMicros()` 用两端墙钟相减：同机 IPC µs 级可信；**跨主机受 NTP/PTP 漂移影响**，只作粗略观测，别当 SLO。

### 10.4 Dispatcher 选型：INLINE vs RING_BUFFER_POOL

| 模式 | handler 线程 | 适用 | 风险 |
|---|---|---|---|
| `INLINE` | poll 线程直接调 | handler 极快（纯内存/转发/计数） | handler 阻塞 = poll 阻塞 = 整路时延堆高 |
| `RING_BUFFER_POOL`（默认） | 业务 worker 线程池 | handler 有 I/O / DB / RPC / 重 CPU | 队列满 → `onDispatchDropped` |

```java
ConsumerConfig.builder()
        .deliveryMode(DeliveryMode.RING_BUFFER_POOL)
        .workerThreads(8)                 // 多 worker → handler 必须线程安全
        .ringBufferCapacity(65536)        // 默认，底层 ArrayBlockingQueue
        .build();
```

handler 抛异常被 SDK 拦截（上报 `metrics.onError`），不传染 poll 循环。

### 10.5 poll 线程空转策略（`idleStrategy`）

延迟与 CPU 占用的核心旋钮。**每个被订阅的 partition 各起一个 poll 线程、各占一个 IdleStrategy 实例。**

| 取值 | 空闲行为 | 唤醒延迟 | 空闲 CPU | 典型场景 |
|---|---|---|---|---|
| `BUSY_SPIN` | 忙等 + `onSpinWait` | 最低（亚 µs） | 100%（占满一核） | **行情 / 低延迟首选** |
| `NO_OP` | 纯忙等 | 最低 | 100% | 极致延迟 + 核绑定 |
| `YIELDING` | `Thread.yield()` | 低 | 高 | 核数紧张的折中 |
| `BACKOFF`（默认） | spin→yield→park（park 上限 ~1ms） | 中 | 低 | 通用折中 |
| `SLEEPING` | 固定 sleep（1ms） | 高 | 最低 | 吞吐/省电优先 |

高级：`AeronConsumer.Builder.idleStrategySupplier(...)` 注入自定义策略工厂（优先级高于枚举），**必须每次返回新实例**：

```java
.idleStrategySupplier(() -> new BackoffIdleStrategy(
        1000, 100, 1, java.util.concurrent.TimeUnit.MICROSECONDS.toNanos(50)))
```

### 10.6 去重（dedup）

消息可能因 Aeron retransmit 或链路异常收到多次。基于 128-bit msgId 的环形去重：

```java
ConsumerConfig.builder()
        .dedupWindow(0)         // 0 = 关闭（默认）
        .dedupWindow(1 << 16)   // 64k 槽位
        .build();
```

- 必须是 `0`（关）或 **≥2 的 2 的幂**。
- **每个 partition 独立一个 deduper**：内存 ≈ `dedupWindow × partitionCount × 16 字节`。
- 命中丢弃 + `metrics.onDuplicate`，handler 不被调用；「近窗口防抖」语义，不保证强幂等。
- ⚠️ **producer 开了 Outbox 时投递是 at-least-once，consumer 端务必开 dedup 且窗口足够大**。

### 10.7 INLINE 零分配：`reuseInlineContext`

高频行情 + 零分配 codec（SBE flyweight）+ INLINE 下，每条 `new MessageContext` 会成为 GC 来源：

```java
ConsumerConfig.builder()
        .deliveryMode(DeliveryMode.INLINE)
        .idleStrategy(IdleStrategyType.BUSY_SPIN)
        .reuseInlineContext(true)    // 默认 false
        .build();
```

> 契约：开启后 `ctx` **只在本次回调期间有效**，回调返回后被下一条覆盖。**不要保存引用**；需要就拷字段值。仅 `INLINE` 生效，`RING_BUFFER_POOL` 忽略。

### 10.8 解压输出上限（zip-bomb 防护）

`maxDecompressedBytes`（默认 16 MiB，下界 1024）限制单条解压后上限，超出丢帧 + `metrics.onError`。按业务最大合法消息大小留 2-4x buffer。

### 10.9 异常与自动丢帧

以下都上报 `metrics.onError`、不抛进 handler：帧畸形 `FrameDecodeException`、`CodecException`（no codec for wire id / type mismatch）、`CompressionException`（未引压缩 jar / zip-bomb）、codec.decode 抛异常。dedup 命中 → `onDuplicate`；`RING_BUFFER_POOL` 队列满 → `onDispatchDropped`。

### 10.10 线程模型

```
Aeron MediaDriver → poll 线程(aeronmq-poll-*)：取 fragment→解帧→dedup→解压→decode→入 dispatcher
                       ├─ INLINE：handler 在本线程直接跑
                       └─ RING_BUFFER_POOL：入队 → worker 线程池(aeronmq-worker-*) 跑 handler
```

`RING_BUFFER_POOL` + `workerThreads>1` 时可能并发回调同一 handler，handler 必须线程安全。

---

## 11. Codec 模块（序列化）

producer/consumer 端必须为每种业务类型注册**一致**的 codec。

### 11.1 内置（无需额外依赖）

| Codec | wire id | 用途 |
|---|---|---|
| `RawBytesCodec.INSTANCE` | 0 | `byte[]`，已默认注册 |
| `StringCodec.INSTANCE` | 4 | UTF-8 `String`，已默认注册 |

### 11.2 独立模块

| Codec | wire id | 依赖 | 工厂 API |
|---|---|---|---|
| JSON | 3 | `aeron-codec-json` | `JsonCodec.forType(T.class)` / `JsonCodec.builder(T.class).objectMapper(m).build()` |
| Protobuf | 2 | `aeron-codec-protobuf` | `new ProtobufCodec<>(Msg.class)` / `ProtobufCodec.builder(Msg.class).extensionRegistry(r).build()` |
| SBE | 1 | `aeron-codec-sbe` | `SbeCodec.fixedLength(T.class, len, T::encode, T::decode)` / `SbeCodec.varLength(T.class, T::maxBytes, T::encode, T::decode)` |
| Fory | 5 | `aeron-codec-fory` | `ForyCodec.forType(T.class)` / `ForyCodec.builder(T.class).crossLanguage(true).typeId(101).build()` |

```java
.codec(JsonCodec.forType(Order.class))
.codec(new ProtobufCodec<>(OrderProto.class))
.codec(SbeCodec.fixedLength(Quote.class, 28, Quote::encode, Quote::decode))
.codec(ForyCodec.forType(Trade.class))
```

### 11.3 同 codec 多类型

每种业务类型**必须**注册独立实例（Protobuf 尤其常踩，同 wire id 靠 `payload.getClass()` 派发）：

```java
.codec(new ProtobufCodec<>(OrderProto.class))
.codec(new ProtobufCodec<>(TradeProto.class))
```

### 11.4 自定义 codec

实现 `com.mcst.aeron.common.codec.Codec<T>`，wire id 从 `100`（`CodecIds.FIRST_USER_DEFINED`）起选：

```java
public final class MyCodec implements Codec<MyDto> {
    public byte codecId() { return 100; }
    public Class<MyDto> type() { return MyDto.class; }
    public int encodedLength(MyDto v) { ... }
    public int encode(MyDto v, MutableDirectBuffer buf, int off) { ... }
    public MyDto decode(DirectBuffer buf, int off, int len) { ... }
}
```

### 11.5 Fory 嵌套 POJO 注意

`ForyCodec.forType(T)` 只注册主类型。含嵌套字段（`List<LineItem>`、引用其它 POJO）时首次 send 抛 `class LineItem is not registered with Fory`，改用 builder 显式注册：

```java
ForyCodec.builder(Order.class)
        .register(LineItem.class)
        .register(Address.class)
        .build();
```

**跨 JVM type 一致性**：producer 与 consumer 的 `T` 必须是字面同一 class（全限定名一致）。推荐把 broadcast POJO 抽到独立 `xxx-domain.jar`，双方引同一坐标。跨语言互通须用 XLANG 模式（`crossLanguage(true)` + 协商 typeId/typeName）。

---

## 12. Compression 模块（压缩）

producer 一旦配压缩，所有 payload 走压缩路径；consumer 端**无需配置**，按帧 header 的 compressionId 自动选解压器（`ServiceLoader` 自动注册 classpath 上的实现）。

```java
import com.mcst.aeron.compression.lz4.Lz4Compression;
import com.mcst.aeron.compression.zstd.ZstdCompression;
import com.mcst.aeron.common.compression.DeflateCompression;

.compression(Lz4Compression.INSTANCE)        // 速度优先
.compression(new ZstdCompression(3))          // 压缩率折中（level 3 官方 baseline）
.compression(DeflateCompression.INSTANCE)     // 仅 JDK，无 native
```

| 算法 | wire id | 速度 | 压缩率 | 依赖 |
|---|---|---|---|---|
| `LZ4` | 1 | 极快 | 中 | `aeron-compression-lz4`（含 native） |
| `ZSTD` | 2 | 快 | 高 | `aeron-compression-zstd`（含 native） |
| `DEFLATE` | 3 | 慢 | 中 | `aeron-common` 内置 |

**何时不开**：payload 已是紧凑二进制（SBE / 短 Protobuf），或时延敏感且 payload < 几百字节。

> consumer 端漏引对应压缩 jar，收到压缩帧会报 `CompressionException: no compression registered for wire id N`（`DEFLATE` 由 `aeron-common` 自带，不会缺）。

---

## 13. 按 key 分片与静态分组消费

> 本节即分片 / 静态分组消费的完整用法。底层路由 / partition 展开 / 分配校验以代码为准，见 `com.mcst.aeron.common.partition` 包（`Partitioner` / `PartitionLayout` / `Cluster`）。

### 13.1 为什么分片

| 痛点 | 分片如何解 |
|---|---|
| 单 publication 写入吞吐打满 | N 个 publication 并行，吞吐 N× |
| 同 key（customerId/instrumentId）要严格 FIFO 又不想全局串行 | 同 key 同 partition 保 FIFO；跨 key 并行 |
| 下游想组内分摊又不想引 broker | 静态分组消费 |

### 13.2 4 partition 同 key 保序（核心 SDK）

```java
ProducerConfig cfg = ProducerConfig.builder()
        .channels(ChannelSpec.ipc(), ChannelSpec.ipc(),
                  ChannelSpec.ipc(), ChannelSpec.ipc())   // partition 0~3
        .baseStreamId(1001)
        // 多 partition 默认 partitioner=MURMUR3、noKeyStrategy=ROUND_ROBIN，可省略
        .build();

try (AeronProducer p = AeronProducer.builder().driver(driver).config(cfg).build()) {
    while (!p.isAllConnected()) Thread.sleep(20);   // 注意是 isAllConnected
    p.send("orders.new", customerA, order1);   // customerA 全进同一 partition、严格 FIFO
    p.send("orders.new", customerA, order2);
    p.send("orders.new", customerB, order3);   // customerB 可能落另一 partition、与 A 并行
}
```

`NoKeyStrategy`（不给 key 时）：`ROUND_ROBIN`（默认，均匀分摊）/ `FIRST`（永远 partition 0，牺牲并行保序）/ `TOPIC_HASH`（同 topic 落同一 partition）。

> IPC 退化：4 个 `ChannelSpec.ipc()` 自动退化成「同 channelUri + streamId 错开 [1001..1004]」，两端必须配同样的 `channels` 列表。

### 13.3 静态分组消费

`isConnected` 语义：`isConnected()`=至少一个 partition 接通；`isAllConnected()`=全部接通；`isConnected(int)`=单个；`partitionCount()`=总数。

consumer 端订全部（默认）或订子集：

```java
// 实例 #1：订 partition 0,1
ConsumerConfig.builder()
        .channels(ipc, ipc, ipc, ipc)
        .partitionAssignment(Set.of(0, 1))
        .groupId("billing")           // 仅 metrics tag
        .build();

// 实例 #2：订 partition 2,3
ConsumerConfig.builder()
        .channels(ipc, ipc, ipc, ipc)
        .partitionAssignment(Set.of(2, 3))
        .groupId("billing")
        .build();
```

多组 fan-out：billing 组全订、audit 组内 2 实例对半分摊 —— 跨组独立、组内静态分摊。

### 13.4 部署期校验（推荐）

```java
import com.mcst.aeron.common.partition.Cluster;

Cluster.validateAssignments(
    List.of(Set.of(0, 1), Set.of(2, 3)),
    /* partitionCount = */ 4
);  // 违反"完全覆盖 + 互不重叠"立即抛 IllegalArgumentException
```

参考完整可运行示例 `ShardedBroadcastDemo`（`./gradlew :aeron-examples:runShardedBroadcastDemo`）。

---

## 14. Outbox 模块（先持久化再转发）

模块 `aeron-producer-outbox`（默认不引/不开，零开销）。在 `AeronProducer` 前加一层 Store-and-Forward WAL 装饰器：`send` 先写本地磁盘 WAL 并按持久化等级落盘，再由后台单线程转发器重发到 Aeron，**失败原地重试、绝不跳过**；进程崩溃重启从 checkpoint 续发（携带**相同 msgId**，consumer 端去重实现幂等 at-least-once）。

### 14.1 边界

| | |
|---|---|
| ✅ 保证 | `send` 返回 ⇒ 消息已持久化，最终一定被交给 Aeron（哪怕瞬时失败/崩溃重启） |
| ✅ 保证 | 同 key 严格 FIFO；幂等（同 msgId + consumer dedup） |
| ❌ 不保证 | 已掉线/晚加入的 consumer 一定收到（那是 Archive / Cluster 范畴） |

一句话：Outbox 解决「**生产侧不丢**」，不是「消费侧补历史」。

### 14.2 核心 SDK 用法

```java
implementation 'com.mcst:aeron-producer-outbox'
```

```java
import com.mcst.aeron.producer.outbox.*;

OutboxConfig outboxCfg = OutboxConfig.builder()
        .enabled(true)                          // 默认 false
        .walDir("/var/lib/myapp/aeron-wal")     // enabled 时必填
        .fsyncPolicy(FsyncPolicy.INTERVAL)      // 持久化等级
        .build();

AeronProducer raw = AeronProducer.builder()
        .driver(driver)
        .codec(JsonCodec.forType(Order.class))
        .build();

Producer producer = OutboxProducer.wrap(
        raw, outboxCfg,
        CodecRegistry.withDefaults(),
        MessageIdGenerator.snowflake(),
        OutboxMetrics.noop(),
        /*ownsDelegate*/ true);                 // close 时连带关 raw

try (AutoCloseable c = (AutoCloseable) producer) {
    producer.send("orders.new", customerId, order);   // 先落盘，再由后台转发器发出
}
```

> ⚠️ 包装后**不要**再直接调 `raw` 发送（底层 publication 的唯一 writer 是 outbox 转发器线程）。

### 14.3 配置项（`OutboxConfig`）

| 方法 | 默认 | 说明 |
|---|---|---|
| `enabled(boolean)` | `false` | `false` 时 `wrap` 直通底层 producer |
| `walDir(String)` | `aeron-store-wal` | WAL 目录，enabled 时必填 |
| `fsyncPolicy(FsyncPolicy)` | `INTERVAL` | 持久化等级（见下） |
| `flushIntervalMillis(long)` | `100` | `INTERVAL` fsync 周期（ms） |
| `storeType(OutboxStoreType)` | `SEGMENTED` | `SEGMENTED`（边发边回收）/ `SINGLE_FILE` |
| `segmentBytes(long)` | `64 MiB` | 单段滚动大小（仅 SEGMENTED），≥1024 |
| `checkpointEveryRecords(int)` | `1` | 每成功转发 N 条持久化一次进度 |
| `forwarderIdleParkNanos(long)` | 1ms | 转发器空闲 park |
| `forwardRetryBackoffNanos(long)` | 1ms | 转发瞬时失败重试退避 |
| `drainOnCloseMillis(long)` | `5000` | close 时最多等转发器排空的时长 |

**持久化等级 `FsyncPolicy`**：`PER_RECORD`（每条 fsync，最强、延迟最高，金融核心账务）/ `INTERVAL`（默认，丢失窗口≤一周期，行情快照）/ `OS_BUFFERED`（从不显式 fsync，最弱）。进程正常退出三者都不丢，区别只在突发断电时。

### 14.4 毒丸防护

开启后 `send` 在**落盘前**校验 frame 大小，超界当场抛 `OutboxException`、绝不写 WAL，避免转发器对超大消息永久重试阻塞队列。

### 14.5 注意事项

- 底层 producer 必须实现 `EncodedFrameSender`（`AeronProducer` 已实现），否则 `wrap` 抛 `IllegalArgumentException`。
- 投递变为 **at-least-once + 幂等**，consumer 端务必开 dedup。
- 优雅关闭：先排空 WAL（`drainOnCloseMillis`）再停；超时残余保留磁盘，下次续发。
- WAL CRC 损坏：转发器停机 + `onError`，数据保留待人工介入，不静默丢。

（Spring Boot 下无需手写 `wrap`，见 [§17.7](#177-outbox先持久化再转发)。）

---

## 15. Metrics 模块（监控）

SDK 对发送/接收/背压/丢弃/去重/错误以及 outbox 落盘/转发/积压都埋了 SPI 钩子（`ProducerMetrics` / `ConsumerMetrics` / `OutboxMetrics`，默认 noop）。引 `aeron-metrics-micrometer` 即可零/少代码接 Prometheus/Grafana/Datadog。

**核心 SDK 手动接入：**

```java
implementation 'com.mcst:aeron-metrics-micrometer'
```

```java
AeronProducer.builder().metrics(new MicrometerProducerMetrics(meterRegistry)).build();
AeronConsumer.builder().metrics(new MicrometerConsumerMetrics(meterRegistry)).build();
OutboxProducer.wrap(delegate, cfg, reg, idGen, new MicrometerOutboxMetrics(meterRegistry), true);
```

指标清单：

| 指标 | 类型 | 标签 | 含义 |
|---|---|---|---|
| `aeron.producer.sent` / `.sent.bytes` | counter | `partition` | 成功发送条数/字节 |
| `aeron.producer.backpressure.retries` / `.dropped` / `.errors` | counter | `partition` | 背压重试/丢弃/错误 |
| `aeron.consumer.received` / `.received.bytes` | counter | `group`,`partition` | 收到条数/字节 |
| `aeron.consumer.latency` | timer(p50/p99/p99.9) | `group`,`partition` | 端到端延迟 |
| `aeron.consumer.duplicates` / `.errors` / `.dispatch.dropped` | counter | `group`,`partition` | 去重/错误/队列丢弃 |
| `aeron.outbox.backlog.bytes` | gauge | — | WAL 未转发积压（**重点告警项**） |
| `aeron.outbox.persisted` / `.persisted.bytes` / `.forwarded` / `.forward.retries` / `.recovered` / `.errors` | counter | — | outbox 链路计数 |

> **基数安全**：故意**不**按 topic 打标签（行情 topic 基数可能上千会打爆 Prometheus），只按有界的 `partition` / 低基数 `group`。完整清单/告警 PromQL 见 [监控指南](监控指南.md)。

---

## 16. Chronicle 模块（状态物化）

模块 `aeron-chronicle`：把 Aeron 事件流（changelog）**物化**成持久化的 Chronicle Map KV 状态表 —— 订阅一个 topic 的事件，按 key upsert / 按 tombstone 删除，得到一份可查询、可重启恢复的最新状态视图。

适用：需要「事件流 + 可随时按 key 查最新值」的场景（如持仓表、订单快照表）。

**编程式一行绑定：**

```java
StateMaterializer<TradeEvent, String, TradeState> materializer =
        StateMaterializer.<TradeEvent, String, TradeState>builder()
            .map(chronicleMap)                       // 目标 ConcurrentMap（通常 Chronicle Map）
            .key(e -> e.getSymbol())
            .value(e -> toState(e))
            .tombstoneWhen(e -> e.isDeleted())       // 可选：何时删 key
            .versionedBy(s -> s.getVersion())        // 可选：旧版本跳过；参数是存储值 TradeState（不是事件），V 必须带版本字段
            .build();

consumer.subscribe("trades.events", TradeEvent.class, materializer);
```

**Spring Boot 下**：声明 `AeronChronicleBindingSpec` bean，`AeronChronicleAutoConfiguration` 会在启动期（早于 `AeronLifecycle`）自动解析 Chronicle Map 与 Consumer 并完成绑定。相关配置：`easyfk.config.aeron.chronicle.enabled`（默认 `true`），Chronicle Map 本身走 `easyfk.config.chronicle.map.*`。完整用法见 [Aeron Chronicle 状态存储指南](Aeron%20Chronicle%20状态存储指南.md)，可运行示例 `ChronicleStateDemo`。

---

## 17. Spring Boot Starter 完全指南

`@Autowired Producer` + `@AeronTopic`，driver 启停 / bean 装配 / 健康检查 / shutdown 顺序全托管。配置前缀 `easyfk.config.aeron`（与公司框架其它模块 `easyfk.config.*` 对齐）。

> 三步就能用：**① 引依赖 → ② 写 `application.yml` → ③ `@Autowired Producer` 发 + `@AeronTopic` 收**。下面 §17.0 给一份可直接复制的完整配置与最小工程；§17.1 起再按主题拆解。

### 17.0 一分钟接入：完整依赖 + 配置 + 代码

**① 依赖（Gradle）：**

```groovy
dependencies {
    implementation 'com.mcst:aeron-spring-boot-starter'
    implementation 'com.mcst:aeron-codec-fory'                    // 触发零配置 POJO 默认兜底

    // 可选：监控
    implementation 'com.mcst:aeron-metrics-micrometer'
    implementation 'org.springframework.boot:spring-boot-starter-actuator'
}
```

Maven：

```xml
<!-- 版本由框架 BOM 统一管理，无需 <version> -->
<dependency>
    <groupId>com.mcst</groupId>
    <artifactId>aeron-spring-boot-starter</artifactId>
</dependency>
<dependency>
    <groupId>com.mcst</groupId>
    <artifactId>aeron-codec-fory</artifactId>
</dependency>
```

> 别忘了 [§4.1 的 JVM `--add-opens` 参数](#41-jvm-启动参数必须)，否则 Aeron 在 JDK 21+ 启动即崩。

**② 完整 `application.yml`（单 driver，开箱即用，含全部常用项及默认值注释）：**

```yaml
easyfk:
  config:
    aeron:
      enabled: true                         # 全局开关（默认 true）
      # default-driver: default              # 单 driver 可省略；多 driver 必填

      codec:
        default-codec: fory                  # 未注册 POJO 兜底：fory（默认）| none
      metrics:
        enabled: true                        # Micrometer 指标开关（默认 true）
      shutdown:
        timeout: 30s                         # 优雅停机总超时（默认 30s）

      driver:                                # ← 单 driver 用单数 driver
        embedded: true                       # JVM 内启 MediaDriver（默认 true）
        aeron-dir: /dev/shm/aeron-app        # MediaDriver 共享目录
        dir-delete-on-start: false           # 多 JVM 同机务必 false（默认 false）
        dir-delete-on-shutdown: true
        threading-mode: SHARED               # SHARED | SHARED_NETWORK | DEDICATED | INVOKER
        # driver-idle-strategy: BACKOFF        # 仅 embedded 生效

        producer:
          enabled: true
          channels:                          # 单元素=纯 fan-out；多元素=按 key 分片
            - aeron:ipc
          base-stream-id: 1001               # 必须与 consumer 一致
          no-key-strategy: ROUND_ROBIN       # ROUND_ROBIN | FIRST | TOPIC_HASH
          backpressure:
            strategy: RETRY_THEN_FAIL        # BLOCK | DROP_NEWEST | FAIL | RETRY_THEN_FAIL
            retries: 100
          # outbox: { enabled: false }         # 需要"生产侧不丢"时开，见 §17.7

        consumer:
          enabled: true
          channels:                          # 必须与 producer.channels 等长
            - aeron:ipc
          base-stream-id: 1001               # 必须与 producer 一致
          delivery-mode: RING_BUFFER_POOL    # INLINE | RING_BUFFER_POOL
          worker-threads: 1
          ring-buffer-capacity: 65536
          fragment-limit: 16
          dedup-window: 0                    # 0=关闭；开 outbox 时务必开且 >0
          idle-strategy: BACKOFF             # BUSY_SPIN | NO_OP | YIELDING | BACKOFF | SLEEPING
          reuse-inline-context: false
          max-decompressed-bytes: 16MB

# 可选：暴露 actuator 健康检查
management:
  endpoints:
    web:
      exposure:
        include: health,prometheus
```

**③ 发送 + 订阅（无需任何 codec 代码，Fory 自动兜底）：**

```java
// —— 业务 POJO（producer / consumer 两端必须是同一个 class，建议放共享 domain jar）——
public class TradeTick {
    private String symbol; private double price; private long qty;
    public TradeTick() {}                                   // Fory 反序列化需无参构造
    public TradeTick(String s, double p, long q) { symbol=s; price=p; qty=q; }
    // getters / setters ...
}

// —— 发送 ——
@Service
public class TickPublisher {
    @Autowired private Producer producer;                   // 按接口注入（兼容 outbox）

    public void publish(String sym, double p, long q) {
        producer.send("ticks.aapl", new TradeTick(sym, p, q));
    }
}

// —— 订阅 ——
@Component
public class TickSubscriber {
    @AeronTopic(value = "ticks.aapl", payloadType = TradeTick.class)
    public void onTick(TradeTick tick, MessageContext ctx) {
        log.info("got {} @ {} latency={}us", tick.getSymbol(), tick.getPrice(), ctx.latencyMicros());
    }
}
```

完事。启动即自动装配 driver / producer / consumer，注册 `@AeronTopic` 订阅并启动 poll 线程；`/actuator/health` 自带 `aeron` 子项。

> ⚠️ 想「启动即发」请放到 `ApplicationRunner` / `ApplicationReadyEvent`，不要放 `@PostConstruct`（那时订阅可能还没建好）。

### 17.1 单 driver（开发 / 多数业务）

```yaml
easyfk:
  config:
    aeron:
      driver:                          # 单数 driver
        embedded: true
        aeron-dir: /dev/shm/aeron-app
        dir-delete-on-start: false
        producer:
          channels: [aeron:ipc]        # 单元素=纯 fan-out；多元素=按 key 分片
          base-stream-id: 1001
          backpressure:
            strategy: RETRY_THEN_FAIL
            retries: 100
        consumer:
          channels: [aeron:ipc]        # 必须与 producer.channels 等长
          base-stream-id: 1001
          delivery-mode: RING_BUFFER_POOL
          worker-threads: 1
```

注入：

```java
@Autowired Producer producer;          // 推荐接口类型（兼容 outbox）
@Autowired AeronConsumer consumer;     // 一般不直接用，@AeronTopic 已够
@Autowired DriverManager driverManager;
```

### 17.2 多 driver（一进程接多链路）

`easyfk.config.aeron.drivers`（复数 Map），driver name 作为 Bean 后缀：

```yaml
easyfk:
  config:
    aeron:
      default-driver: ipc-local        # 多 driver 必填；决定 aeronProducer 等无后缀 alias 指向哪个 driver（@AeronTopic 仍须写 driver）
      drivers:
        ipc-local:
          embedded: true
          aeron-dir: /dev/shm/aeron-ipc
          producer: { channels: [aeron:ipc] }
          consumer: { channels: [aeron:ipc] }
        udp-prod:
          embedded: false              # 挂外部 driver
          aeron-dir: /var/lib/aeron-prod
          producer:
            channels: ["aeron:udp?endpoint=10.0.1.5:40123"]
          consumer:
            enabled: false             # 这个 driver 只发不收
```

> **互斥**：`driver`（单数）与 `drivers`（复数）不能同时配。
> **driver name 规范**：`[a-zA-Z][a-zA-Z0-9_-]{0,31}`，不合法/重复由 `DriverNameValidator` 抛异常。

按 driver 注入（用 `@AeronDriver(原始名)`）：

```java
@Autowired @AeronDriver("udp-prod") private Producer udpProducer;
@Autowired @AeronDriver("ipc-local") private Producer ipcProducer;
```

Bean 命名：单 driver 为 `aeronProducer` / `aeronConsumer` / `aeronDriverManager` / `aeronCodecRegistry`；多 driver 为 `<name>_<driverNameCamel>`（`ipc-local`→`ipcLocal`）+ 默认 driver 的 alias。

> starter 内部所有「批量收集 bean」处（生命周期停机 / 健康探针）**只看 `aeron*` 前缀 bean**，业务方自定义 `Producer`/`Consumer` 实现不被托管，互不干扰。

### 17.3 channel 写法（IPC / UDP / MDC）

每个 channel 是一个 Aeron URI 字符串：

```yaml
drivers:
  udp:
    producer: { channels: ["aeron:udp?endpoint=10.0.1.5:40123"] }
    consumer: { channels: ["aeron:udp?endpoint=10.0.1.5:40123"] }
  mdc:
    producer: { channels: ["aeron:udp?control=224.0.1.1:40456|control-mode=dynamic"] }
    consumer: { channels: ["aeron:udp?endpoint=224.0.1.1:40456"] }
```

支持 `aeron:ipc` / `aeron:ipc?tether=false`（**仅 consumer**）/ `aeron:udp?endpoint=host:port` / MDC；IPv6 必须保留方括号 `[::1]:40456`。

**脱钩慢订阅**（语义见 §9.3）：

```yaml
drivers:
  local:
    producer: { channels: [aeron:ipc] }
    consumer: { channels: ["aeron:ipc?tether=false"] }
```

两端 URI 字符串不同但**不会**错位：streamId 按去掉 `tether` 后的传输端点 URI 展开，producer 的 partition 0 与 consumer 的 partition 0 都落在 `baseStreamId`。producer 侧配 `tether=false` 会在启动期直接抛 `IllegalStateException`（该参数对 publication 无意义）。

### 17.4 订阅：`@AeronTopic`

标注 `@Component` 类里的方法，starter 用 `LambdaMetafactory` 绑定为 `MessageHandler` 并自动 subscribe。

```java
@Component
public class TradeSubscriber {

    @AeronTopic(value = "trades.new", payloadType = Trade.class)
    public void onTrade(Trade t, MessageContext ctx) {
        log.info("got {} seq={}", t, ctx.msgIdLow());
    }

    @AeronTopic(value = "trades.delete", payloadType = TradeKey.class)
    public void onDelete(TradeKey k) { repo.delete(k); }   // 1 参数也行

    // 多 driver 场景 driver 必填
    @AeronTopic(driver = "udp-prod", value = "audit.events", payloadType = AuditEvent.class)
    public void onAudit(AuditEvent e) { auditService.persist(e); }
}
```

方法签名约束（不符合装配期抛 `IllegalStateException`）：返回 `void`；1 或 2 参 `(T payload)` 或 `(T payload, MessageContext ctx)`；第一参 assignable from `payloadType()`；第二参严格是 `com.mcst.aeron.consumer.MessageContext`；public 或 package-private、非 static、非 abstract、不 throws checked。

### 17.5 Codec 注册（starter）

**方式 A：`@Bean Codec<T>` 自动扫描（推荐）**

```java
@Configuration
public class CodecConfig {
    @Bean public Codec<Trade> tradeCodec() { return ForyCodec.forType(Trade.class); }
    @Bean public Codec<AuditEvent> auditCodec() { return JsonCodec.forType(AuditEvent.class); }
}
```

**方式 B：yaml 显式声明**

```yaml
easyfk:
  config:
    aeron:
      codecs:
        - class-name: com.mcst.aeron.codec.fory.ForyCodec
          factory-method: forType
          factory-args: [com.your.app.OrderProto]
          drivers: [ipc-local]         # 省略 = 所有 driver
```

同 `payloadType` 在 A+B 双路都注册会启动失败（要求只选一种）。

**方式 C：零配置 POJO（默认 Fory 兜底）**

classpath 有 `aeron-codec-fory` + `easyfk.config.aeron.codec.default-codec=fory`（默认）时，未注册的 POJO 自动 `ForyCodec.forType(T)` 兜底，全程零 codec 代码。设为 `none` 则严格模式：未注册类型启动期 fail-fast 抛 `CodecException`（跨语言/强校验场景用）。嵌套 POJO 仍需显式 builder 注册（见 [§11.5](#115-fory-嵌套-pojo-注意)）。

### 17.6 只发不收 / 只收不发

两层开关：全局 `easyfk.config.aeron.producer.enabled` / `consumer.enabled`（优先级高），per-driver `drivers.<n>.producer.enabled` / `consumer.enabled`。

```yaml
# 纯发送服务：一行关掉所有接收侧
easyfk: { config: { aeron: { consumer: { enabled: false }, driver: { embedded: true } } } }
```

> **Fail-fast 防呆**：consumer 关了却残留 `@AeronTopic`，`AeronLifecycle.start()` 会一次列出所有残留方法并报错（避免「listener 看上去存在却永不被调用」的 hidden bug）。修复三选一：打开 consumer / 删 listener / component scan 排除。

### 17.7 Outbox（先持久化再转发）

无需手写 `wrap(...)`，加一行 `outbox.enabled: true`：

```yaml
easyfk:
  config:
    aeron:
      driver:
        producer:
          channels: [aeron:ipc]
          outbox:
            enabled: true
            wal-dir: /var/lib/myapp/aeron-wal   # 留空则自动用 aeron-store-wal/<driver>
            fsync-policy: INTERVAL              # PER_RECORD | INTERVAL | OS_BUFFERED
            store-type: SEGMENTED              # SEGMENTED | SINGLE_FILE
```

> ⚠️ 开启后该 driver 的 producer bean 运行时类型是 `OutboxProducer`（实现 `Producer` 但**非** `AeronProducer`），**务必按 `Producer` 接口注入**，用 `AeronProducer` 具体类型会注入失败。投递变 at-least-once，consumer 端务必开 `dedup-window`。`OutboxMetrics` 在引 `aeron-metrics-micrometer` + Actuator 后由 starter 自动注册并拾取。

### 17.8 压缩（starter）

发送侧通过 `@Bean CompressionCodec` 开启，starter 自动接上：

```java
@Bean public CompressionCodec compression() { return Lz4Compression.INSTANCE; }
```

多 driver 各自不同压缩：注册多个 bean，bean name 命名为 driver 名（`@Bean("udp-prod")`）。consumer 端无需配置。

### 17.9 Actuator 健康检查

引 `spring-boot-starter-actuator` 后自动注册 `aeron` HealthIndicator（`/actuator/health`）：

- **DOWN**：任一 driver 的 Aeron client 为 null 或 closed。
- **UP**：所有 driver Aeron client 在线；`producer.isConnected()` **不参与** UP/DOWN（subscriber 未接入是常态，不能因此让探针变红触发 K8s 重启）。

禁用：`management.health.aeron.enabled=false`。

### 17.10 生命周期 / shutdown

`AeronLifecycle` 实现 `SmartLifecycle`，phase = `Integer.MIN_VALUE + 1000`（多数组件之前启动、之后关闭）。

- **启动顺序**：driver → producer/codecRegistry → consumer（`consumer.start()` 最后，确保 `@AeronTopic` 都绑好）。
- **关闭顺序**：consumer → producer → driver（相反，避免 driver 关了 producer 还在 send）。
- **超时**：`easyfk.config.aeron.shutdown.timeout`（默认 30s），超时记 error 后放行 Spring shutdown，避免容器 hang。
- 不要在同一 context 内做 stop→立即 start 的「热重启」；完整重启走应用重启。

（Chronicle 的 `AeronChronicleLifecycle` phase = `MIN_VALUE + 500`，早于 `AeronLifecycle` 启动。）

---

## 18. 配置项完整参考

前缀 `easyfk.config.aeron`。所有默认值与核心 SDK `ProducerConfig`/`ConsumerConfig`/`DriverConfig` 常量对齐（唯一例外：starter 的 `dir-delete-on-start` 默认 `false`，SDK builder 默认 `true`）。

### 18.1 顶层

| Path | 默认 | 说明 |
|---|---|---|
| `enabled` | `true` | 全局开关，false 不装配任何 Bean |
| `default-driver` | 单 driver 自动 / 多 driver 必填 | 多 driver 时决定无后缀 alias（`aeronProducer` / `aeronConsumer` / `aeronDriverManager` / `aeronCodecRegistry`）指向哪个 driver；`@AeronTopic` 在多 driver 下仍必须写 `driver` |
| `producer.enabled` | `true` | **全局** producer 子系统开关 |
| `consumer.enabled` | `true` | **全局** consumer 子系统开关 |
| `codec.default-codec` | `fory` | 未注册 POJO 兜底：`fory` / `none` |
| `metrics.enabled` | `true` | Micrometer 指标开关 |
| `shutdown.timeout` | `30s` | 停机总超时 |

### 18.2 driver（`driver.*` 或 `drivers.<n>.*`）

| Path | 默认 | 说明 |
|---|---|---|
| `embedded` | `true` | 是否 JVM 内启 MediaDriver |
| `aeron-dir` | OS 默认 | MediaDriver 共享目录 |
| `dir-delete-on-start` | `false` | **多 JVM 同机务必 false** |
| `dir-delete-on-shutdown` | `true` | 关闭是否删目录 |
| `driver-timeout-ms` | `10000` | driver 超时 |
| `threading-mode` | `SHARED` | `SHARED`/`SHARED_NETWORK`/`DEDICATED`/`INVOKER`；仅 embedded |
| `driver-idle-strategy` | Aeron 默认 | 仅 embedded |
| `mtu-length` | Aeron 默认 `1408` | UDP 通道 MTU，决定单帧上限（`maxPayloadLength = mtu − 32`）；32 的倍数、≤ `65504`；仅 embedded |
| `ipc-mtu-length` | Aeron 默认 | IPC 通道 MTU，语义同上；IPC 无网络分片顾虑可放心调大；仅 embedded |

### 18.3 producer（`...producer.*`）

| Path | 默认 | 说明 |
|---|---|---|
| `enabled` | `true` | per-driver producer 开关 |
| `channels` | `[aeron:ipc]` | partition 列表，下标即 partitionId；**不接受** `aeron:ipc?tether=false` |
| `base-stream-id` | `1001` | 与 consumer 必须一致 |
| `partitioner` | 自动 | `MURMUR3` / `SINGLETON`（按 partitionCount 自动选） |
| `no-key-strategy` | `ROUND_ROBIN` | `ROUND_ROBIN`/`FIRST`/`TOPIC_HASH` |
| `backpressure.strategy` | `RETRY_THEN_FAIL` | `BLOCK`/`DROP_NEWEST`/`FAIL`/`RETRY_THEN_FAIL` |
| `backpressure.retries` | `100` | 仅 RETRY_THEN_FAIL 用 |
| `outbox.enabled` | `false` | 开启 store-and-forward（见 §17.7） |
| `outbox.wal-dir` | `aeron-store-wal/<driver>` | 留空自动隔离；多写者不可共用 |
| `outbox.fsync-policy` | `INTERVAL` | `PER_RECORD`/`INTERVAL`/`OS_BUFFERED` |
| `outbox.flush-interval-millis` | `100` | INTERVAL fsync 周期 |
| `outbox.store-type` | `SEGMENTED` | `SEGMENTED`/`SINGLE_FILE` |
| `outbox.segment-bytes` | `64MiB` | 单段大小（仅 SEGMENTED） |
| `outbox.checkpoint-every-records` | `1` | 每 N 条持久化转发进度 |
| `outbox.drain-on-close-millis` | `5000` | close 排空超时 |

### 18.4 consumer（`...consumer.*`）

| Path | 默认 | 说明 |
|---|---|---|
| `enabled` | `true` | per-driver consumer 开关 |
| `channels` | `[aeron:ipc]` | 必须与 producer.channels 等长；可用 `aeron:ipc?tether=false` 脱钩慢订阅 |
| `base-stream-id` | `1001` | 与 producer 一致 |
| `partition-assignment` | 缺省（订全部） | 本实例订阅的 partition 子集 |
| `group-id` | 无 | 仅作 metrics tag |
| `delivery-mode` | `RING_BUFFER_POOL` | `INLINE`/`RING_BUFFER_POOL` |
| `worker-threads` | `1` | POOL 模式 worker 数 |
| `ring-buffer-capacity` | `65536` | dispatch 队列容量 |
| `fragment-limit` | `16` | poll 每次最多解码消息数 |
| `dedup-window` | `0` | 0 关闭；每 partition 独立 deduper |
| `idle-strategy` | `BACKOFF` | `BUSY_SPIN`/`NO_OP`/`YIELDING`/`BACKOFF`/`SLEEPING` |
| `reuse-inline-context` | `false` | INLINE 下复用 ctx 消除分配 |
| `max-decompressed-bytes` | `16MiB` | 防 zip-bomb |

---

## 19. 常见问题 / 排查手册（FAQ）

### 发送/接收不通

**发出去 consumer 没收到？** 依次查：
1. `producer.isConnected()` 是否 true（false = 还没 subscriber 接进来）；
2. consumer 是否 `start()`；
3. `channels` 长度与 `baseStreamId` 两端是否完全一致；
4. 两端 codec 类型是否一致（`subscribe` 的 type == `send` 的 `payload.getClass()`）；
5. UDP MDC：网卡/防火墙/路由是否放通组播；
6. 加日志：`metrics` 用 `InMemoryConsumerMetrics` 看 `onError`/`onDuplicate`/`onReceived`。

**收到部分、部分丢？** 看 `metrics.onError`（type mismatch/decode fail）、`onDuplicate`（dedup 窗口太小误判）、`onDispatchDropped`（worker 队列满，增 `worker-threads`/`ring-buffer-capacity`）。

**发送端持续 `BackpressureException`，但订阅方一切正常？** 多半是**慢订阅顶住了 publication**：Aeron 默认 tethered，写入上限取最慢订阅的位置，一个活着但不消费（worker 卡住 / handler 慢 / 断点）的订阅会把所有订阅者一起拖住。排查顺序：
1. 看订阅侧 poll 线程是否真在转（`idle-strategy`、handler 是否阻塞在 IO/DB）；
2. 确认是不是**同机 IPC fan-out，且允许慢订阅自己丢帧**——是则订阅端换 `aeron:ipc?tether=false`（§9.3）；untethered 订阅落后超窗口会被 driver 摘除、从最新位置重新加入，它自己丢帧不连累别人；
3. 不允许丢消息的链路上别用 `tether=false`，只能扩 consumer 侧吞吐（增 `worker-threads` / `ring-buffer-capacity`）或降流速。

### 常见异常

| 现象 | 原因 / 处理 |
|---|---|
| `CodecException: no codec registered for type X` | 漏注册 codec；按 §11 注册 |
| `AeronMqException: frame size N exceeds ... M` | 单帧超过 `mtu − 32`；调大 `driver.mtu-length` / `driver.ipc-mtu-length`（§9.5、§18.2）或业务分块；调 `term-buffer-length` 无效 |
| `BackpressureException` 频发 | 订阅者跟不上：增 worker / 增 `ring-buffer-capacity` / 降流速 / 换策略（能丢 `DROP_NEWEST`，不能丢 `BLOCK`） |
| `PublicationTerminalException` | publication 终态；关旧 producer 重建（嵌入 driver 也重起） |
| `CompressionException: no compression registered for wire id N` | consumer 端漏引压缩 jar；按 §12 加依赖 |
| `class X is not registered with Fory` | Fory 嵌套 POJO；用 builder 显式 register（§11.5） |
| `invalid aeron uri`（IPv6） | 方括号：`[::1]:40456`，别写成 `::1:40456` |
| `... tether=false only applies to subscriptions` | producer.channels 里写了 `aeron:ipc?tether=false`；改回 `aeron:ipc`（§17.3） |
| 同机两 JVM 一个崩溃 | 共用 `aeronDir` + `dirDeleteOnStart=true`；用不同目录 + 关掉（§8.3） |

### Spring Boot 相关

| 现象 | 处理 |
|---|---|
| `driver and drivers are mutually exclusive` | 单/多 driver 二选一（§17.1/§17.2） |
| `NoUniqueBeanDefinitionException`（多 driver） | 用 `@AeronDriver("name")` 显式限定 |
| 开 outbox 后 `@Autowired AeronProducer` 注入失败 | 改按 `Producer` 接口注入（§17.7） |
| 容器 shutdown 卡 30s | `shutdown.timeout` 兜底；开 debug 查 `AeronLifecycle.stop()` 定位卡住的 bean |
| consumer 关了却报残留 `@AeronTopic` | 打开 consumer / 删 listener / component scan 排除（§17.6） |

### 语义/设计

**mutable POJO send 后改字段影响 wire 吗？** 不会，所有内置 codec 在 send 期间立即完成 encode。

**多线程发消息怎么写？** 单线程+队列串行化，或每线程各自 build 一个 producer（共享 driver）。**不要**多线程裸调同一 `producer.send`。

**动态加/删订阅？** 加：运行期任意 `subscribe`。删：V1 不支持单 topic 退订，handler 内按业务过滤或重建 consumer。

**订几百个 topic？** SDK 不限；几十~几百个性能无差异，几千个建议拆 consumer 实例。

---

## 20. 相关文档

以下为 `docs/` 目录下现存的配套专题文档；分片、Outbox、生命周期等更深的实现细节**以代码为准**（对应模块见 [§3.2 模块清单](#32-模块清单)）。

- [aeron 协议说明](aeron协议说明.md) —— wire 帧字节布局基线
- [序列化 Codec 接入指南](序列化Codec接入指南.md) —— SBE / Fory 等 codec 详解
- [监控指南](监控指南.md) —— 指标清单 / 标签设计 / 告警 PromQL
- [Aeron Chronicle 状态存储指南](Aeron%20Chronicle%20状态存储指南.md) —— 事件流物化为 Chronicle Map 状态表
- [跨语言互通指南](跨语言互通指南.md) —— Go / C++ / .NET / Rust 与本组件互通

> 分片 / 静态分组消费、Outbox（先持久化再转发）、Metrics SPI 等能力的完整用法已并入本手册（§13 / §14 / §15）；底层契约请直接参考对应源码模块（`aeron-common` / `aeron-store` / `aeron-producer-outbox` / `aeron-metrics-micrometer`）。
