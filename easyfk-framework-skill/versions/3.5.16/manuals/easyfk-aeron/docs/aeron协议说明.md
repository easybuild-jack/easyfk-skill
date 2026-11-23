# Aeron 广播协议说明（Wire Protocol + Codec 接入）

> 本文档整合了原 `aeron协议说明.md` / `SBE接入指南.md` / `Protobuf接入指南.md` / `Fory接入指南.md`，
> 并**以代码为准**重新对齐（package、Maven 坐标、版本号、时间戳来源等均按当前实现修正）。
> 面向：本 SDK 使用者、以及需要字节级对齐的跨语言 SDK 实现者（Go / C++ / .NET / Rust 等）。

Java 端权威实现位于 `aeron-common` 模块的 `com.mcst.aeron.common.*` 包，本文所有类名、常量、行为均可在源码中逐条核对（见文末 §15「参考 Java 实现」）。

---

## 0. 工程坐标与版本（对齐 `settings.gradle` / `build.gradle`）

- Maven group：`com.mcst`，version：`3.5.16`（见根 `build.gradle` 的 `allprojects`）
- Java：21（`sourceCompatibility = VERSION_21`）
- 关键依赖版本（统一由 `easyfk-dependencies` 的版本目录 + BOM 约束管理，本工程 `settings.gradle` 只保留坐标别名、不声明版本）：

| 依赖 | 坐标 | 版本 |
|---|---|---|
| Aeron | `io.aeron:aeron-*` | `1.54.2` |
| Agrona | `org.agrona:agrona` | `2.7.1` |
| SBE 工具 | `uk.co.real-logic:sbe-tool` | `1.42.0` |
| Protobuf | `com.google.protobuf:protobuf-java` | `4.36.2` |
| LZ4 | `at.yawk.lz4:lz4-java` | `1.14.0` |
| Zstd | `com.github.luben:zstd-jni` | `1.5.7-28` |
| Fory | 经 `com.mcst:serializer-fory` 引入（BOM `com.mcst:easyfk-dependencies:3.5.16` 管理版本） | 随 BOM |

模块地图（`settings.gradle` 的 `include`）：

```
aeron-common              wire 帧协议 + Codec/Compression SPI + DEFLATE 内置压缩 + 分片
aeron-codec-sbe           泛型 SbeCodec 适配框架（不含业务 schema）
aeron-codec-protobuf      泛型 ProtobufCodec 适配 protobuf-java
aeron-codec-json          JSON codec
aeron-codec-fory          ForyCodec（依赖 com.mcst:serializer-fory）
aeron-compression-lz4     LZ4 压缩
aeron-compression-zstd    ZSTD 压缩
aeron-driver / aeron-producer / aeron-consumer / aeron-producer-outbox
aeron-metrics-micrometer / aeron-chronicle / aeron-store
aeron-examples            可运行示例  /  aeron-spring-boot-starter  自动装配
```

> JVM 启动参数需沿用本 SDK 标准 `--add-opens` 列表（见根 `build.gradle` 的 `test.jvmArgs`），Aeron / Agrona 在 JDK 21+ 上需要这些反射开关。

---

## 1. Wire 帧协议 — V1

每条消息是一个独立的 Aeron fragment。fragment 的 payload 由三段组成：

```
+---------------------+----------------+----------------+
| 40-byte fixed header | topic (UTF-8)  | payload bytes  |
+---------------------+----------------+----------------+
```

- **不分片**：单条消息必须能装进 `Publication.maxPayloadLength()`，超过即由 SDK 拒发；不依赖 Aeron 自身的 fragment 重组。
- **不持久化、不 ack、不 replay**：纯 fan-out broadcast。
- 接收端按 frame header 的 `TOPIC` 字段做精确匹配过滤，不订阅的 topic 直接丢弃，但仍会经过 magic / length 校验。

### 1.1 分片 / 分组**不进 wire**

"按 key 分片"和"静态分组消费"是**部署期拓扑维度**，不写进任何 frame 字段：

| 概念 | 在哪体现 | 在 wire 上吗？ |
|---|---|---|
| `partitionId` / `partitionCount` | 部署配置 `channels[]` 长度 + 下标 | **否**（partition 身份由它走的 `(channelUri, streamId)` 元组隐式承载） |
| `key`（Partitioner 路由用） | producer 内存对象 | **否**（路由结果是 partition 选择本身，对端无需知道原始 key） |
| `groupId`（静态分组消费） | consumer 配置，仅作 metrics tag | **否** |
| `partitionAssignment` | consumer 配置，仅决定本实例订哪些 stream | **否** |

⇒ **跨语言 SDK 实现分片 / 分组对 wire 没有任何影响**。用法见 [`Aeron 组件使用手册.md`](Aeron%20组件使用手册.md) §13，展开规则以 `com.mcst.aeron.common.partition.PartitionLayout` 源码为准，跨语言互通矩阵见 §1.10。

---

## 2. 字节序与对齐

- **字节序：little-endian**。所有多字节整数字段（uint16 / uint32 / int64 等）均以小端写入。
  - Java 端 `org.agrona.MutableDirectBuffer` 默认使用 native byte order。本 SDK 运行在 x86 / ARM 等小端平台上，`putInt/putShort/putLong` 即写小端；跨语言实现必须统一锁定为 little-endian，不能依赖对端 native。
- **不做对齐填充**：除已有的 2 字节 `PADDING` 字段外，没有 8-byte / cache-line 对齐要求，topic 与 payload 紧接 header。

---

## 3. Fixed Header（40 字节）

字段布局与 `com.mcst.aeron.common.frame.FrameProtocol` 常量一一对应：

| 偏移 | 长度 | 字段 | 常量 | 类型 | 说明 |
|---:|---:|---|---|---|---|
| 0 | 4 | `MAGIC` | `OFFSET_MAGIC` | bytes | wire 上为 ASCII `'A','E','M','Q'`；用 LE `int32` 读取得到 `MAGIC = 0x514D4541` |
| 4 | 1 | `VERSION` | `OFFSET_VERSION` | uint8 | 当前 = `VERSION_V1 = 0x01` |
| 5 | 1 | `FLAGS` | `OFFSET_FLAGS` | uint8 | bit0 = `FLAG_BATCH`(0x01, 保留)；bit1 = `FLAG_COMPRESSED`(0x02) |
| 6 | 1 | `CODEC` | `OFFSET_CODEC` | uint8 | payload 编码格式 wire id，见 §4 |
| 7 | 1 | `COMPRESSION` | `OFFSET_COMPRESSION` | uint8 | 压缩算法 wire id，见 §5；`0` 表示未压缩 |
| 8 | 2 | `TOPIC_LEN` | `OFFSET_TOPIC_LEN` | uint16 LE | topic UTF-8 字节长度，实际允许 `0..255`（见 §3.5） |
| 10 | 2 | `PADDING` | `OFFSET_PADDING` | uint16 | 固定填 0，预留对齐 |
| 12 | 4 | `PAYLOAD_LEN` | `OFFSET_PAYLOAD_LEN` | uint32 LE | payload 字节长度（**压缩后**，即 wire 上紧跟 topic 的字节数） |
| 16 | 8 | `TIMESTAMP_NS` | `OFFSET_TIMESTAMP_NS` | int64 LE | producer 写入时的 epoch 纳秒，见 §3.6 |
| 24 | 8 | `MSG_ID_HIGH` | `OFFSET_MSG_ID_HIGH` | int64 LE | 128-bit 消息 id 的高 64 位 |
| 32 | 8 | `MSG_ID_LOW` | `OFFSET_MSG_ID_LOW` | int64 LE | 128-bit 消息 id 的低 64 位 |

`HEADER_LENGTH = 40`，字段总长固定 40 字节。

### 3.1 MAGIC 校验

接收端按 LE int32 读取 offset 0..3，期望值 `0x514D4541`；不等即视为非法 frame，丢弃（`FrameDecoder.decodeHeader` 抛 `FrameDecodeException`）。

### 3.2 VERSION

仅支持 `0x01`。`FrameDecoder` 遇到任何非 `0x01` 的值直接拒帧。未来引入新版本时 producer 必须能与 consumer 协商。

### 3.3 FLAGS

| bit | 名称 | 常量 | 说明 |
|---:|---|---|---|
| 0 | `BATCH` | `FLAG_BATCH = 0x01` | 保留，V1 消息粒度已是最小单位，不会置位 |
| 1 | `COMPRESSED` | `FLAG_COMPRESSED = 0x02` | `COMPRESSION != 0` 时 `FrameEncoder` **自动**同步置位（见下）；consumer 以 `COMPRESSION` 字节为准 |
| 2..7 | — | — | 必须为 0 |

> 实现细节：`FrameEncoder.encodeHeaderAndTopic` 计算 `effectiveFlags = compressionId != 0 ? (flags | FLAG_COMPRESSED) : flags`，即压缩标志由编码器根据 `compressionId` 强制置位，业务方无需手工设置。

### 3.4 PADDING

`FrameEncoder` 固定写 0；解码端不强制校验，但跨语言实现也不应填非零内容（便于未来扩展）。

### 3.5 长度字段上限

- `TOPIC_LEN` wire 字段宽度为 uint16（硬上限 `TOPIC_LEN_FIELD_MAX = 0xFFFF`），但 SDK 统一约束 `≤ 255`（`MAX_TOPIC_LENGTH = 255`）。`FrameEncoder.validateLengths` 写入端拒绝超限，`FrameDecoder` 读到 `topicLength > 255` 也拒帧。
- `PAYLOAD_LEN` wire 字段宽度为 uint32，SDK 端校验 `0 ≤ payloadLen ≤ MAX_PAYLOAD_LENGTH`，其中
  `MAX_PAYLOAD_LENGTH = Integer.MAX_VALUE - HEADER_LENGTH - TOPIC_LEN_FIELD_MAX`
  （即 `Integer.MAX_VALUE - 40 - 0xFFFF`），避免 `frameLength = 40 + topicLen + payloadLen` 在 32-bit signed 加法上回绕。
- 实际单条消息上限进一步受 Aeron `Publication.maxPayloadLength()` 约束，producer 发送前自检并拒发超大消息。

### 3.6 TIMESTAMP_NS（时间源已对齐代码）

由 `com.mcst.aeron.common.time.WallClock.epochNanos()` 生成，实现为：

```java
Instant now = Instant.now();
return now.getEpochSecond() * 1_000_000_000L + now.getNano();
```

- 这是 **wall-clock（墙钟）epoch 纳秒**，不是 `System.nanoTime()`（单调时钟，跨进程不可比）。
- 采用 `Instant.now()` 而非旧的 `System.currentTimeMillis() * 1_000_000L`，在 JDK 9+ 上可获得 **µs 级**（部分平台 ns 级）分辨率，而非毫秒级假精度。
- producer / consumer 必须用同一时间源做端到端延迟计算；跨机场景需 NTP/PTP 同步，负值或异常大值应视为时钟未同步信号。

---

## 4. Codec ID（`com.mcst.aeron.common.codec.CodecIds`）

| ID | 常量 | 名称 | 跨语言推荐 | 说明 |
|---:|---|---|:---:|---|
| 0 | `RAW` | RAW | ✅ 首选 | payload 即 raw `byte[]`，无序列化层（`RawBytesCodec`） |
| 1 | `SBE` | SBE | ✅ 双必选（低延迟首选） | Simple Binary Encoding；`aeron-codec-sbe` + 业务 schema codegen，见 §7 |
| 2 | `PROTOBUF` | PROTOBUF | ✅ 双必选（兼容现存业务） | Protocol Buffers；`aeron-codec-protobuf` + 业务 schema codegen，见 §8 |
| 3 | `JSON` | JSON | ✅ 可用 | UTF-8 JSON（`aeron-codec-json`，默认 Jackson）；双端字段命名需一致 |
| 4 | `STRING` | STRING | ✅ 首选 | UTF-8 字符串，无长度前缀、无 BOM（`StringCodec`） |
| 5 | `FORY` | FORY | ❌ 仅 Java 内部 | Apache Fory；`aeron-codec-fory`，见 §9。XLANG 模式 wire 可跨语言，但本 SDK 跨语言不实施 |
| 6..99 | — | — | — | 未来内置 codec 预留 |
| 100..255 | `FIRST_USER_DEFINED=100` 起 | 用户自定义 | 业务侧决定 | 业务方实现 `Codec` SPI 时使用 |

> **跨语言策略**：本 SDK 跨语言互通采用 **SBE + Protobuf 双必选**：SBE 适合新业务 / 行情广播 / 低延迟；Protobuf 适合兼容现存业务 / 通用 RPC 风格 / 更广语言生态。两者并存、按场景分工；Fory 仅 Java 内部。选型细节见 §6。

Consumer 收到帧后**不是**直接用 `CODEC` 字节查 codec，而是按订阅声明的业务 type 派发，`CODEC` 仅做 cross check —— 原理见 §4.1。

### 4.1 派发主键：业务 type，不是 wire CODEC（核心契约）

出自 `Codec.java` 的 SPI javadoc 与 `CodecRegistry` 实现：

- `codecId()` 是 wire 字段，只标 codec **家族**（PROTOBUF / SBE / JSON / STRING / RAW / FORY），同一家族里多个业务 type **共享同一个 wire id**。
- `type()` 是 Java 类型，绑定到具体业务消息类；一个 codec instance 服务一种 type。
- Consumer 端派发以 `sub.payloadType()`（订阅时声明的 `Class<T>`）为主键查 byType 表，**不是**用 wire `CODEC`。
- wire `CODEC` 仅用作 cross check：命中的 codec 的 `codecId()` 必须等于帧上 `CODEC`，否则视为 producer/consumer 配对错误 → 丢消息 + `metrics.onError`。

这样才能支持"同 wire 家族、多业务 type 混发"（典型如 protobuf / SBE）。如果错误地用 `CODEC` 当派发主键，注册第二个同家族 type 会静默覆盖第一个 —— 这是跨语言实现最容易踩的 P0 坑（详见 §7.3 / §8.4）。

---

## 5. Compression ID（`com.mcst.aeron.common.compression.CompressionIds`）

压缩 SPI 是 `CompressionCodec`（`id()` / `maxCompressedLength` / `compress` / `decompress`）。压缩走 staging 路径：producer 先把 payload 编码到中间数组、压缩后再 `putBytes` 到 Aeron claim buffer；consumer 先解压到中间数组，再交给 `codec.decode`。

| ID | 常量 | 名称 | 跨语言难度 | 实现类 | 说明 |
|---:|---|---|:---:|---|---|
| 0 | `NONE` | NONE | 🟢 无 | — | 未压缩，payload 字节即业务字节 |
| 1 | `LZ4` | LZ4 | 🔴 高 | `aeron-compression-lz4` / `Lz4Compression` | 基于 lz4-java；wire payload 头部多 4 字节 LE 长度前缀，见 §5.1。跨语言对端必须用 lz4 **block** API 而非 frame API |
| 2 | `ZSTD` | ZSTD | 🟢 低 | `aeron-compression-zstd` / `ZstdCompression` | 基于 zstd-jni；标准 zstd frame format（自带 magic + 原始长度），跨语言库直接互通 |
| 3 | `DEFLATE` | DEFLATE | 🟡 中 | `aeron-common`（内置）/ `DeflateCompression` | JDK `Deflater(nowrap=true)`，raw deflate stream。跨语言对端必须用 `flate`（无 zlib header）而非 `zlib` |

`COMPRESSION == 0` 时 wire payload 直接是业务字节；`!= 0` 时是压缩字节流，且 `FLAG_COMPRESSED` 被同步置位（见 §3.3）。

### 5.1 LZ4 内部约定（对齐 `Lz4Compression`）

LZ4 块压缩本身不携带原始长度。本实现在 wire payload 头部固定加 4 字节 LE `uint32` `originalLength`，紧跟 lz4 块字节：

```
+----------------+--------------------+
| 4-byte LE len  | lz4 block bytes    |
+----------------+--------------------+
```

- `originalLength` 是**未压缩**字节数，consumer 据此预分配 dst buffer 并防 zip-bomb（超 `dstCapacity` 抛 `CompressionException`）。
- `PAYLOAD_LEN`（frame header 字段）= `4 + lz4 block bytes`，即 wire 上总字节数。
- 解压用 `LZ4FastDecompressor`（已知 originalLength），要求 `read == compressedLen`，否则报错。

### 5.2 ZSTD 内部约定

直接是 zstd frame format 字节（含 zstd magic / header / 原始长度等元信息）。consumer 通过 zstd-jni 取原始长度。`PAYLOAD_LEN` = zstd frame 总字节数。

### 5.3 DEFLATE 内部约定

raw deflate stream（`nowrap=true`，无 zlib header / Adler32）。原始长度由解压器流式 inflate 边解边推；实现端对累计输出做上限保护。

---

## 6. Codec 选型（SBE / Protobuf / Fory / JSON）

| 维度 | SBE | Protobuf | Fory（JAVA 模式） | JSON |
|---|---|---|---|---|
| 编码方式 | 编译期 codegen，纯偏移读写 | 编译期 codegen + 运行时序列化 | 运行时反射 + JIT | 运行时反射 |
| 单条编解码延迟 | ~50 ns | ~200 ns | ~50~200 ns | ~2 µs |
| GC 压力 | 极低（zero-copy wrap） | 中（builder / 中间对象） | 低 | 高 |
| schema 演进 | `blockLength`+`version`（约束更严） | 字段号管理，很灵活 | Fory 自家 schema evolution | 字段名匹配，无强 schema |
| 需 schema 文件 | 是（`.xml` codegen） | 是（`.proto` codegen） | 否（POJO 即可） | 否 |
| 跨语言 | ✅ Java/C++/C#/Go/Rust | ✅ 10+ 语言 | ❌ 仅 Java（XLANG 可跨，本 SDK 不实施） | ✅ 全语言（命名/精度易踩坑） |
| 适用 | 高频行情 / 撮合 / tick / 新业务低延迟 | 既有业务 / 通用 RPC / 跨语言交换 | 纯 Java 零配置 POJO | 调试 / 与 web 前端共享 |

**结论**：

| 场景 | 推荐 |
|---|---|
| 已有大量 Protobuf 业务消息，想接广播 SDK | **Protobuf**（§8） |
| 新业务、低延迟广播 / 行情 / tick 全推 | **SBE**（§7） |
| 纯 Java、不关心跨语言、想零配置接入 | **Fory**（§9） |
| 调试 / 与 web 前端共享格式 | **JSON** |

一个 producer / consumer 实例可以同时注册多种 codec，按 `payload.getClass()` 自动派发；wire 上靠 `CODEC` 区分家族，同家族多 type 靠订阅 type 区分（§4.1）：

```java
AeronProducer producer = AeronProducer.builder()
    .driver(dm)
    .codec(SbeCodec.fixedLength(Quote.class, 32, encoder, decoder))  // CODEC=1
    .codec(ProtobufCodec.forType(OrderProto.class))                  // CODEC=2
    .build();

producer.send("md.quote.aapl", new Quote("AAPL", ...));   // SBE 路径
producer.send("orders.new",    OrderProto.newBuilder()...); // Protobuf 路径
```

---

## 7. SBE codec 接入（`aeron-codec-sbe` / `SbeCodec`）

`aeron-codec-sbe` 只提供**泛型 SbeCodec 适配框架**，本身不含任何业务 schema、不跑 sbe-tool。Schema 治理建议放在业务公司独立的 `sbe-schemas` repo。`SbeCodec.codecId()` 恒为 `CodecIds.SBE`（=1）。

### 7.1 推荐工程组织

```
company-sbe-schemas/          ← 独立 repo：src/main/sbe/*.xml + sbe-tool codegen + 发 jar
aeron-broadcast/              ← 本 SDK：aeron-codec-sbe（泛型，不含业务 schema）
market-data-publisher/        ← 业务应用：依赖 company-sbe-schemas + aeron-codec-sbe
```

单独 repo 的理由：跨业务复用（broadcast / FIX gateway / 归档 / 离线分析共享一份 schema）、生命周期与 SDK 解耦、统一治理（CODEOWNERS / 版本 / 跨语言生成同步）。

### 7.2 Schema 示例 + codegen

`marketdata.xml`（注意根元素**必须**显式 `byteOrder="littleEndian"`，见 §7.6）：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sbe:messageSchema xmlns:sbe="http://fixprotocol.io/2016/sbe"
                   package="com.company.sbe.market"
                   id="1" version="0" semanticVersion="1.0"
                   byteOrder="littleEndian">
    <types>
        <composite name="messageHeader">
            <type name="blockLength" primitiveType="uint16"/>
            <type name="templateId"  primitiveType="uint16"/>
            <type name="schemaId"    primitiveType="uint16"/>
            <type name="version"     primitiveType="uint16"/>
        </composite>
        <type name="symbolType" primitiveType="char" length="8"/>
    </types>
    <sbe:message name="Quote" id="1">
        <field name="symbol" id="1" type="symbolType"/>
        <field name="price"  id="2" type="int64"/>
        <field name="qty"    id="3" type="int32"/>
    </sbe:message>
</sbe:messageSchema>
```

`company-sbe-schemas/build.gradle` 用 `JavaExec` 跑 sbe-tool（版本对齐本 SDK 的 **1.42.x**）：

```groovy
plugins { id 'java-library' }
repositories { mavenCentral() }
dependencies {
    api 'org.agrona:agrona:2.7.1'
    runtimeOnly 'uk.co.real-logic:sbe-tool:1.42.0'
}
def generatedSrc = layout.buildDirectory.dir('generated/sbe').get().asFile
sourceSets.main.java.srcDirs += generatedSrc
tasks.register('generateSbe', JavaExec) {
    classpath = configurations.runtimeClasspath
    mainClass = 'uk.co.real_logic.sbe.SbeTool'
    systemProperties = [
        'sbe.output.dir'      : generatedSrc.absolutePath,
        'sbe.target.language' : 'Java',
        'sbe.validation.xsd'  : '/sbe.xsd'
    ]
    args = fileTree('src/main/sbe').matching { include '*.xml' }.collect { it.absolutePath }
}
tasks.named('compileJava') { dependsOn 'generateSbe' }
```

### 7.3 业务应用接入

```groovy
dependencies {
    implementation 'com.mcst:aeron-producer:3.5.16'
    implementation 'com.mcst:aeron-consumer:3.5.16'
    implementation 'com.mcst:aeron-codec-sbe:3.5.16'
    implementation 'com.company:company-sbe-schemas:1.0.0'   // 你公司 schema jar
}
```

Producer 注册 + send（业务 POJO 不必与 schema 字段一一对应）：

```java
record Quote(String symbol, long price, int qty) {}

AeronProducer producer = AeronProducer.builder()
    .driver(dm)
    .codec(SbeCodec.fixedLength(
        Quote.class,
        MessageHeaderEncoder.ENCODED_LENGTH + QuoteEncoder.BLOCK_LENGTH,   // 编译期常量
        (q, buf, off) -> {                                                // SbeEncoderOp
            QuoteEncoder enc = new QuoteEncoder();
            MessageHeaderEncoder hdr = new MessageHeaderEncoder();
            enc.wrapAndApplyHeader(buf, off, hdr)
               .price(q.price()).qty(q.qty()).symbol(q.symbol());
            return MessageHeaderEncoder.ENCODED_LENGTH + enc.encodedLength();
        },
        (buf, off, len) -> {                                              // SbeDecoderOp
            MessageHeaderDecoder hdr = new MessageHeaderDecoder().wrap(buf, off);
            QuoteDecoder dec = new QuoteDecoder().wrap(
                buf, off + hdr.encodedLength(), hdr.blockLength(), hdr.version());
            return new Quote(dec.symbol(), dec.price(), dec.qty());
        }))
    .build();

producer.send("md.l1.aapl", new Quote("AAPL", 187_42L, 100));
```

Consumer 用**同一份 codec 注册**，`subscribe` 时声明 `payloadType`（派发主键，见 §4.1）：

```java
AeronConsumer consumer = AeronConsumer.builder()
    .driver(dm)
    .codec(MarketDataCodecs.quoteCodec())   // 与 producer 相同
    .build();
consumer.subscribe("md.l1.aapl", Quote.class, (q, ctx) -> {
    System.out.println(q.symbol() + " " + q.price());
});
consumer.start();
```

> 多 type 派发 P0：每个业务 type 都要注册独立 codec，`subscribe` 时声明各自 `payloadType`。同一 consumer 实例上一个 topic 只能绑一个 `payloadType`；多 type 共享 topic 时业务方需自建一个按 `templateId` 派发的组合 codec，或拆到不同 topic。

### 7.4 SDK API（`SbeCodec`）

| 工厂方法 | 用途 | 性能特征 |
|---|---|---|
| `SbeCodec.fixedLength(type, totalLength, encoder, decoder)` | 业务消息总字节数固定（schema 编译期常量） | `encodedLength` 返回常量零开销，`encode` 直写 claim buffer，零拷贝 |
| `SbeCodec.varLength(type, maxLengthFn, encoder, decoder)` | 含 var-data / repeating group | 双重序列化（先到 ThreadLocal scratch 量长度，再写 claim buffer），~2x CPU |

业务方在 `SbeEncoderOp<T>` / `SbeDecoderOp<T>` lambda 里完整负责 wire 字节（含 messageHeader），框架透明。两条实现都会事后校验实际写入字节数与"声明字节数"一致，不一致抛 `CodecException`（AeronProducer abort claim + `metrics.onError`）。

### 7.5 fixedLength 的越界告警（重要）

- `fixedLength` 是默认选择（Quote / Trade / Tick / OrderAck / Fill 天然定长）。
- ⚠️ `totalLength` **必须**与 lambda 实际写入字节数完全一致。**写少**：框架事后抛 `CodecException`，claim 已 commit 的字节变 padding（OK）；**写多**：越界写入下一帧无法回滚（`claim.abort()` 救不回越界字节，wire 数据破坏）。框架的字节数校验只是事后 best-effort 监控，不能阻止内存破坏。schema 升级（`BLOCK_LENGTH` 变了）务必同步更新常量。
- `varLength` 的 `maxLengthFn` 给宽松上界（真实最大值 1.2~1.5x 即可），算小抛 `CodecException`，算大只多占点 ThreadLocal 内存。
- **线程约束**：varLength 用静态 ThreadLocal 在 `encodedLength → encode` 之间传长度，要求同线程内两次调用紧邻，中间不得触发另一个 SbeCodec 的 `encodedLength`（SDK 内部 `AeronProducer.doSend` 已保证）。

### 7.6 schema 演化 + byteOrder 强约束

- 加非必需字段 → bump `schemaVersion`，新字段标 `sinceVersion` / `presence="optional"`；老 consumer 靠 `blockLength` 截断不读新字段，新 consumer 收老帧按 version 走默认值。任意端先升级都 OK。
- 改字段类型 / 改长度 → bump `schemaId`，所有 producer / consumer **同步升级**（不兼容）。
- 删字段：SBE 不支持，只能改 `deprecated`。
- **byteOrder 强制 `littleEndian`**：SBE 出现在 `PAYLOAD` 段，必须与 frame header 字节序一致。sbe-tool 缺省即 littleEndian，但缺省是软约束，被误改成 `bigEndian` 会导致数值字段全乱（symbol 因是 ASCII 看起来"部分通"，极难诊断）。建议 CI 加 lint：schema XML 缺 `byteOrder="littleEndian"` 或写成 `bigEndian` 直接 fail。
- 跨语言双端必须用**同一份 schema XML** codegen，不能一端 v1 另一端 v2 自由演化；decoder lambda 里用 `MessageHeaderDecoder.version()` 区分版本；升级推荐**先升所有 consumer，再升 producer**。

---

## 8. Protobuf codec 接入（`aeron-codec-protobuf` / `ProtobufCodec`）

`aeron-codec-protobuf` 提供 `ProtobufCodec<T extends MessageLite>` 适配 protobuf-java（本 SDK 对齐版本 **4.36.2**），本身不含业务 `.proto`、不跑 `protoc`。Schema 治理放在业务公司独立的 `proto-schemas` repo。`ProtobufCodec.codecId()` 恒为 `CodecIds.PROTOBUF`（=2）。

### 8.1 推荐工程组织 + schema

```
company-proto-schemas/     ← 独立 repo：src/main/proto/**/*.proto + protobuf-gradle-plugin
aeron-broadcast/           ← 本 SDK：aeron-codec-protobuf（泛型，不含业务 schema）
trading-publisher/         ← 业务应用：依赖 company-proto-schemas + aeron-codec-protobuf
```

`marketdata/quote.proto`（强烈建议双端固定 `proto3`）：

```protobuf
syntax = "proto3";
package company.marketdata;
option java_package        = "com.company.proto.marketdata";
option java_multiple_files = true;
option go_package          = "github.com/your-company/proto-schemas/gen/go/marketdata;marketdata";

message QuoteProto {
    string symbol = 1;
    int64  price  = 2;   // 价格 × 100，避免浮点
    int32  qty    = 3;
}
message TradeProto {
    string symbol  = 1;
    int64  price   = 2;
    int64  qty     = 3;
    uint32 side    = 4;   // 0 = buy, 1 = sell
    int64  exec_ns = 5;
}
```

`company-proto-schemas/build.gradle`（protoc 版本对齐本 SDK 的 **4.36.2**）：

```groovy
plugins {
    id 'java-library'
    id 'com.google.protobuf' version '0.9.4'
}
repositories { mavenCentral() }
dependencies {
    api 'com.google.protobuf:protobuf-java:4.36.2'
}
protobuf {
    protoc { artifact = 'com.google.protobuf:protoc:4.36.2' }
    generateProtoTasks { all().each { it.builtins { java {} } } }
}
```

### 8.2 业务应用接入

```groovy
dependencies {
    implementation 'com.mcst:aeron-producer:3.5.16'
    implementation 'com.mcst:aeron-consumer:3.5.16'
    implementation 'com.mcst:aeron-codec-protobuf:3.5.16'
    implementation 'com.company:company-proto-schemas:1.0.0'
}
```

```java
AeronProducer producer = AeronProducer.builder()
    .driver(dm)
    // ⚠️ 每个 protobuf type 必须注册独立 codec 实例（见 §8.4）
    .codec(ProtobufCodec.forType(QuoteProto.class))
    .codec(ProtobufCodec.forType(TradeProto.class))
    .build();

producer.send("md.l1.aapl",
    QuoteProto.newBuilder().setSymbol("AAPL").setPrice(18742L).setQty(100).build());

AeronConsumer consumer = AeronConsumer.builder()
    .driver(dm)
    .codec(ProtobufCodec.forType(QuoteProto.class))   // 与 producer 完全相同
    .codec(ProtobufCodec.forType(TradeProto.class))
    .build();

// ⚠️ subscribe 必须明确声明 payloadType（不是按 wire CODEC 派发）
consumer.subscribe("md.l1.aapl", QuoteProto.class, (q, ctx) ->
    System.out.println("quote: " + q.getSymbol() + " " + q.getPrice()));
consumer.start();
```

同 topic 多 type：一个 topic 在 consumer 端只能绑一个 `payloadType`。要么每 topic 单 type（推荐，`md.quote.aapl` / `md.trade.aapl`），要么业务方定义 `oneof` envelope（`MarketEvent { oneof body { QuoteProto quote = 1; TradeProto trade = 2; } }`），本 SDK 只看见 `MarketEvent`，consumer 内部判 `getBodyCase()`。

### 8.3 SDK API（`ProtobufCodec`）

| 工厂方法 | 用途 |
|---|---|
| `ProtobufCodec.forType(Class<T>)` | 标准接入；反射调 `T.parser()`，结果进 `ConcurrentMap` cache，每 type 仅反射一次 |
| `ProtobufCodec.builder(T).parser(p).build()` | 显式注入 `Parser<T>`，跳过反射（lite runtime / 自定义 parser） |
| `ProtobufCodec.builder(T).extensionRegistry(reg).build()` | 自定义 extension registry（proto2 extensions 场景） |

- `encodedLength(value)` → `value.getSerializedSize()`。
- `encode` **zero-copy 优先**（对齐代码 `encode` 三分支）：
  - heap buffer（`buffer.byteArray() != null`）→ `CodedOutputStream.newInstance(heap, abs, size)` 直写底层数组，0 拷贝；
  - direct buffer（`buffer.byteBuffer() != null`）→ 对 `ByteBuffer` 视图 `newInstance(view)`，0 拷贝；
  - 纯裸地址 → ThreadLocal scratch（256 B 起，按需 ×2；超 1 MiB 用一次性数组），再 `putBytes`。
- `decode` 镜像同样三分支。`abs = buffer.wrapAdjustment() + offset`。

### 8.4 多 type 派发（P0，再三强调）

```java
// ❌ 错误：以为 wire CODEC=2 派发，注册一个就够 → 发 TradeProto 抛 CodecException
producer.codec(ProtobufCodec.forType(OrderProto.class));

// ✅ 正确：每个 protobuf type 都注册独立 codec 实例
producer.codec(ProtobufCodec.forType(OrderProto.class));
producer.codec(ProtobufCodec.forType(TradeProto.class));
```

wire `CODEC = 2` 只标 **Protobuf 家族**，不区分 message type；派发主键用订阅声明的 `Class<T>`（见 §4.1）。跨语言 SDK 同理：Go 用 `reflect.Type`、C++ 用模板参数、Rust 用 `TypeId`，`CODEC=2` 只做 cross check。

### 8.5 schema 演化（proto3 向后兼容）

| 变更 | 兼容性 | 注意 |
|---|---|---|
| 加新字段（新字段号） | ✅ | 老 consumer 当 unknown 字段（默认丢弃） |
| 删字段 | ⚠️ | 字段号**绝不能复用**，建议 `.proto` 里 `reserved N;` 占位 |
| 改字段类型 | ❌ | 改名 + 新字段号 + 旧字段 `reserved` |
| 改字段名 | ✅ wire 兼容 | wire 只看字段号，但生成的 getter/setter 名变了，业务代码要改 |
| singular ↔ repeated | ❌ | wire 解码失败 |

跨语言额外约束：不复用字段号；不假设字段顺序；新字段必须有合理默认（老 consumer 看不到新字段）。

### 8.6 与压缩的组合 + FAQ 摘录

- Protobuf wire 已是紧凑二进制，短消息（< 256 B）通常不值得再压缩；> 1 KB 大消息（含大量 repeated）可叠加 LZ4 / ZSTD（`producer.compression(...)` 或 `send(topic, value, CompressionIds.LZ4)`）。
- gRPC 的 `.proto` 可直接复用（`ProtobufCodec` 只关心 `MessageLite`），但本 SDK 不解读 `service` / `rpc`。
- 字段命名 snake_case vs camelCase **不影响** wire（wire 只有字段号，没字段名）。
- 本 SDK 严格按 protobuf 官方 wire format，不识别任何第三方 framing（length-prefix delimited 等）。
- lite runtime（`optimize_for = LITE_RUNTIME`）下 `T.parser()` 反射可能不可用，走 `builder(T).parser(LiteMsg.parser()).build()`。

---

## 9. Fory codec 接入（`aeron-codec-fory` / `ForyCodec`）

`aeron-codec-fory` 提供基于 [Apache Fory](https://fory.apache.org/) 的高性能序列化 codec。模块依赖 `com.mcst:serializer-fory`（由 BOM `com.mcst:easyfk-dependencies:3.5.16` 引入 Apache Fory 运行时），底层用 `org.apache.fory.*`。`ForyCodec.codecId()` 恒为 `CodecIds.FORY`（=5）。

**选 Fory 的场景**：业务模型是 POJO、不想拉 `.proto`/`.xml` codegen、要 Protobuf 量级性能又要"零 schema 文件"开发体验，且是 Java 内部传输。**不选**：需与不引入 Fory 的外部系统对接（用 JSON/Protobuf）、纳秒级延迟敏感（用 SBE）。

### 9.1 引入依赖

```groovy
dependencies {
    implementation 'com.mcst:aeron-codec-fory:3.5.16'
    // 同时已引入 aeron-producer / aeron-consumer / aeron-driver
}
```

Fory 运行时经 `com.mcst:serializer-fory` 传递引入；本 codec 自身 **0 Spring 依赖**。JVM 启动参数沿用 SDK 标准 `--add-opens` 列表，Fory 自身不需要额外开关。

### 9.2 三种基本用法

**单类型（JAVA 模式，最简）** —— 主类型必须有无参构造供 Fory 反射实例化：

```java
public class Trade {
    public String symbol; public int qty; public double price; public List<String> tags;
    public Trade() {}
    public Trade(String s, int q, double p, List<String> t) { symbol=s; qty=q; price=p; tags=t; }
}

ForyCodec<Trade> codec = ForyCodec.forType(Trade.class);   // 等价 builder(...).build()
AeronProducer producer = AeronProducer.builder().driver(dm).codec(codec).build();
AeronConsumer consumer = AeronConsumer.builder().driver(dm).codec(codec).build();
```

**嵌套自定义类型（JAVA 模式，多注册）** —— 嵌套自定义 POJO 都要显式 `register`：

```java
ForyCodec<Bundle> codec = ForyCodec.builder(Bundle.class)
        .register(Order.class)
        .register(Address.class)
        .build();
```

> JAVA 模式下 Fory 按注册顺序分配内部 typeId：**producer / consumer 端必须按完全相同的顺序 register 完全相同的一组类**，否则 wire 不兼容、反序列化抛异常。JDK 标准类型（`String` / `Integer` / `List` / `Map` / …）由 Fory 自动注册。

**跨语言（XLANG 模式）** —— 每个 register 必须显式提供 typeId 或 typeName：

```java
ForyCodec<Order> codec = ForyCodec.builder(Order.class)
        .crossLanguage(true)
        .typeId(1001)                                 // 主类型必填 typeId 或 typeName
        .register(OrderItem.class, 1002)              // 每个嵌套类型也要稳定 typeId
        .register(Address.class, "company.Address")   // 也支持 typeName
        .build();
```

XLANG 模式下：每个 register **必须**显式提供 `typeId`/`typeName`，否则 `build()` 抛 `IllegalStateException`（错误信息会提示主类型该用 `.typeId()/.typeName()`、关联类型该用 `register(Class,int/String)`）；typeId/typeName 必须两端一致；注册顺序无关（按 typeId 寻址）；wire 符合 Apache Fory XLANG protocol。typeId 推荐 **≥ 100**，避开 Fory 内置保留区。

### 9.3 API（`ForyCodec` / `Builder`）

| 入口 | 说明 |
|---|---|
| `ForyCodec.forType(Class<T>)` | JAVA 模式 + 仅一个主类型，等价 `builder(...).build()` |
| `ForyCodec.builder(Class<T>)` | 链式配置，主类型固定 index 0 |
| `.crossLanguage(boolean)` | 默认 false（JAVA 模式）；true 切 XLANG |
| `.typeId(int)` / `.typeName(String)` | 给主类型加稳定 id/name（XLANG 必填一种；JAVA 模式也可用于稳定寻址） |
| `.register(Class)` | 追加关联类型；XLANG 模式 `build()` 会拒绝（缺 typeId/typeName） |
| `.register(Class, int)` / `.register(Class, String)` | 追加关联类型 + typeId/typeName |
| `.build()` | XLANG 模式校验所有类已有 typeId/typeName，缺则抛 `IllegalStateException` |
| `.codecId()` → `byte` | 恒返回 `CodecIds.FORY`（=5） |
| `.type()` → `Class<T>` | 主业务类型 |
| `.isCrossLanguage()` → `boolean` | 当前是否 XLANG 模式（排错用） |

> 重复 `register` 同一个 class 会抛 `IllegalStateException("class already registered")`。

### 9.4 关键设计

- **线程模型**：内部用 `ThreadSafeFory`（Fory 实例池），同一 codec 可多线程并发 encode/decode（producer 多实例共享 OK，consumer 多 worker 并发 decode OK）。
- **性能**：Fory Java 端 `serialize` 始终返回 `byte[]`，无 zero-copy 到外部 buffer 的公开 API；本 codec 遵循 SDK `Codec` 双调用契约（`encodedLength → encode`），与 JsonCodec / `SbeCodec.varLength` 同款双重序列化（~2x Fory baseline），但仍显著快于 Jackson JSON。首次 encode 触发 Fory JIT 生成 codec class（百毫秒级），稳态后单条亚微秒级。
- **异常包装**：Fory 内部 `RuntimeException`（未注册类、null 拒绝等）被包成 `CodecException`；decode 后若类型不匹配（`!type.isInstance(raw)`）也抛 `CodecException`，通常意味着两端 register 顺序/class 集合不一致。
- **wire 跨语言警告**：JAVA / XLANG 两种模式 wire `CODEC` 都是 5，**仅靠帧头无法区分模式**；跨语言互通只能用 XLANG。两端 codec 模式必须一致（JAVA 模式两端 register 顺序一致；XLANG 模式两端 typeId/typeName 一致），不一致时 `CODEC` cross check 拦不住（都是 5），会在 Fory 反序列化时抛 `CodecException`。

### 9.5 桥接外部 Fory 封装（可选）

若业务侧已有 Fory 静态封装层（如 Spring Boot 自动装配 + 注解扫描注册中心，暴露 `XxxSerializer.serialize/deserialize` 静态方法），可写一个适配 `Codec<T>` 的小桥复用既有注册中心，无需再走 `ForyCodec.Builder`：

```java
public final class ExternalForyAdapterCodec<T> implements Codec<T> {
    private final Class<T> type;
    public ExternalForyAdapterCodec(Class<T> type) { this.type = type; }
    @Override public byte codecId() { return CodecIds.FORY; }
    @Override public Class<T> type() { return type; }
    @Override public int encodedLength(T value) { return ForySerializer.serialize(value).length; }
    @Override public int encode(T value, MutableDirectBuffer buf, int off) {
        byte[] bytes = ForySerializer.serialize(value);
        if (buf.capacity() - off < bytes.length)
            throw new CodecException("buffer too small for " + type.getName());
        buf.putBytes(off, bytes, 0, bytes.length);
        return bytes.length;
    }
    @Override public T decode(DirectBuffer buf, int off, int len) {
        byte[] tmp = new byte[len];
        buf.getBytes(off, tmp, 0, len);
        return ForySerializer.deserialize(tmp, type);
    }
}
```

注意：桥会把外部封装依赖（含 Spring）引入你的应用（不影响本 SDK 0 Spring 性质）；`ForyCodec` 与该桥的 wire 互通取决于外部封装内部用 JAVA 还是 XLANG 模式，需先与其维护方对齐；桥过来默认 `CODEC=5`，与 `ForyCodec` 共占一个 wire 家族，consumer 端按业务 `Class<T>` 派发不冲突。

### 9.6 可跑示例

`aeron-examples/src/main/java/com/mcst/aeron/examples/ForyIpcDemo.java`：

```bash
./gradlew :aeron-examples:runForyDemo
```

输出的 `latency=N us` 是**端到端 wall-clock** 时延（`producer.send` 到 consumer handler 回调），受 Aeron poll / IPC ring buffer 调度影响，**不是纯 codec 编解码延迟**；首条偏高还叠加 Fory JIT 首次生成 codec class 的开销。

---

## 10. Message ID（128-bit）

由 producer 生成，consumer 仅做 dedup 比对、不解释语义。Java 默认实现 `SnowflakeMessageIdGenerator`（`aeron-producer`）的字段布局：

```
high 64 bits: [41-bit epoch ms][1-bit reserved][22-bit per-ms sequence]
low  64 bits: [16-bit nodeId  ][48-bit process random salt           ] XOR low_seq
```

- 高 64 位：41-bit ms + 22-bit sequence（`SEQ_BITS=22`，`TS_SHIFT=23`），同一进程内 `2^22 = 4_194_304` IDs/ms 内不撞；用尽则 spin 等下一毫秒（`waitNextMillis`）。时钟回退时停在 `lastMs` 不退步。
- 低 64 位：16-bit nodeId（默认由 hostname FNV-1a hash + pid + `SecureRandom` 三路熵 XOR 取低 16 位）+ 48-bit `SecureRandom` salt，`low = lowSalt ^ ((sequence << 32) | sequence)`。可用 `new SnowflakeMessageIdGenerator(int nodeId)` 显式指定 nodeId（如 K8s pod ordinal）获得零碰撞保证。
- 内部用 `synchronized` 保证单一真值源；producer single-writer 模型下无锁竞争。

跨语言 SDK 不必复刻这套布局，**只要保证 128-bit 在合理时间窗内全局不撞**即可（UUIDv7 / TSID / 中心化生成都行）。Consumer 只把 (high, low) 当 16 字节 opaque key 做 dedup。

---

## 11. 解码器必须实现的校验（对齐 `FrameDecoder.decodeHeader`）

按出现顺序：

1. `length < 40`（`HEADER_LENGTH`）→ 拒帧（header 不完整）；
2. `MAGIC != 0x514D4541` → 拒帧；
3. `VERSION != 0x01` → 拒帧；
4. `PAYLOAD_LEN < 0` 或 `PAYLOAD_LEN > MAX_PAYLOAD_LENGTH` → 拒帧；
5. `TOPIC_LEN > 255`（`MAX_TOPIC_LENGTH`）→ 拒帧；
6. `40 + TOPIC_LEN + PAYLOAD_LEN > length` → 拒帧；
7. 解码 topic、按**订阅 type**（`sub.payloadType()`，不是 `CODEC`）查 codec、按 `COMPRESSION` 查解压器；任一找不到 → 丢消息 + `metrics.onError`，**不**抛进 user handler；
8. 命中的 codec 必须满足 `codec.codecId() == 帧上 CODEC`，否则视为 producer/consumer codec 配对错误，丢消息 + `metrics.onError`，不抛进 user handler。

> Java 端上述 1..6 由 `FrameDecoder` 抛 `FrameDecodeException`；7..8 由 consumer 派发层处理。`FrameHeader` 是可复用对象，`decodeHeader` 填充后由消费路径读取 `codecId()/compressionId()/topicOffset()/payloadOffset()` 等。

---

## 12. 编码器必须保证（对齐 `FrameEncoder`）

- 写 header 前自检 `frameLength <= Publication.maxPayloadLength()`，超限抛业务异常（不让 Aeron 退神秘错误码）；
- `COMPRESSION != 0` 时 `FLAG_COMPRESSED` 由编码器**自动**置位（`effectiveFlags`）；
- `PADDING` 写 0；
- topic 字节经字符集校验（`Topic.validateAndEncode`，见 §13）后再写入；
- `validateLengths` 校验 `topicLength ∈ [0,255]`、`payloadLength ∈ [0, MAX_PAYLOAD_LENGTH]`，越界抛 `IllegalArgumentException`；
- 同一帧所有字段在 `tryClaim → commit` 期间一次性写完，失败时用 Aeron `BufferClaim.abort()` 撤回，不暴露残帧。

`FrameEncoder` 提供 `encode(...)`（一次写完 header+topic+payload）与 `encodeHeaderAndTopic(...)`（只写 header+topic，payload 由调用方写到 `offset + HEADER_LENGTH + topicLength` 起，用于 zero-copy 直写 claim buffer；AeronProducer 主路径走后者）。

---

## 13. Topic 编码（`com.mcst.aeron.common.topic.Topic`）

- 字符集：`[A-Za-z0-9.\-_]`，**纯 ASCII**（`Topic.isAllowed`）。
- 长度：`1..255`（`MAX_LENGTH_BYTES = 255`），字符集为 ASCII 故 byte 数 == char 数；`validateAndEncode` 逐字符转 byte。
- 不支持 wildcard / 通配符，consumer 端按字节精确匹配。
- 空 topic（`TOPIC_LEN == 0`）：`FrameDecoder.decodeTopic` 返回 `""`，但 `Topic.validate` 拒绝空 topic（producer 端不会发出），默认订阅集合不会命中。
- 禁止非 ASCII（中文 / emoji / `/` / `:` 等）：保证 byte length == char length；避开 Aeron channel URI 转义冲突；保证日志 / Prometheus label 可读。

---

## 14. 兼容性策略

- **breaking 变更必须升 VERSION 字段**，旧 consumer 看到非 `0x01` 直接拒帧；
- 新增 `CODEC` / `COMPRESSION`（仍在保留段内）不算 breaking，旧 consumer 找不到注册表项即丢消息 + metrics；
- `FLAGS` 高 6 位预留，不允许 producer 置位，未来扩展由新 VERSION 接管；
- `PADDING` 字段未来可能改成新字段，不破坏 V1 现有 40 字节布局总长。

### 14.1 分片跨语言互通矩阵

由 §1.1，分片 / 分组完全不进 wire：

| 场景 | 是否互通 | 注意点 |
|---|---|---|
| Java 多 partition producer ↔ Java 多 partition consumer | ✓ | 两端 `channels` / `baseStreamId` 完全一致 |
| Java 多 partition producer ↔ 跨语言单 partition consumer | ✓ | 跨语言端只接入其中一个 partition，各 partition 由部署期约定覆盖 |
| Java 单 partition producer ↔ 跨语言单 partition consumer | ✓ | 等价纯单流 fan-out |
| 跨语言 producer ↔ Java 多 partition consumer | ✓ | 跨语言端写入对应 partition 的 `(channelUri, streamId)` |

**关键不变量**：跨语言 SDK 实现分片时必须复刻 `PartitionLayout` 的展开规则与 `Murmur3Partitioner` 的字节级哈希语义，否则同 key 在两端会被路由到不同 partition。

---

## 15. 参考 Java 实现

均在 `com.mcst.aeron.*` 包下：

- 字段常量：`aeron-common` `com.mcst.aeron.common.frame.FrameProtocol`
- 写入：`com.mcst.aeron.common.frame.FrameEncoder`
- 读取：`com.mcst.aeron.common.frame.FrameDecoder` / `FrameHeader`
- topic 校验：`com.mcst.aeron.common.topic.Topic`
- Codec SPI / id：`com.mcst.aeron.common.codec.Codec` / `CodecIds` / `CodecRegistry` / `RawBytesCodec` / `StringCodec`
- Compression SPI / id：`com.mcst.aeron.common.compression.CompressionCodec` / `CompressionIds` / `DeflateCompression`；`Lz4Compression`（`aeron-compression-lz4`）；`ZstdCompression`（`aeron-compression-zstd`）
- 时间源：`com.mcst.aeron.common.time.WallClock`
- 消息 id：`com.mcst.aeron.producer.internal.SnowflakeMessageIdGenerator`
- codec 适配：`com.mcst.aeron.codec.sbe.SbeCodec`、`com.mcst.aeron.codec.protobuf.ProtobufCodec`、`com.mcst.aeron.codec.fory.ForyCodec`
- 分片：`com.mcst.aeron.common.partition.{Partitioner, Murmur3Partitioner, NoKeyStrategy, PartitionLayout, Cluster}`
- 示例：`aeron-examples`（`ForyIpcDemo` / `JsonIpcDemo` / `MarketDataSbeDemo` / `UdpFanOut` / `IpcPingPong` / `ShardedBroadcastDemo` / `WireSampleExporter` / `xlang/*`）

### 相关文档

- [`跨语言互通指南.md`](跨语言互通指南.md)：跨语言实现 checklist + 常见坑清单
- [`Aeron 组件使用手册.md`](Aeron%20组件使用手册.md)：producer / consumer / 分片（§13）/ Spring Boot 自动装配（§17）完整用法
- [Apache Fory 官方文档](https://fory.apache.org/docs/) / [protobuf 官方 encoding spec](https://protobuf.dev/programming-guides/encoding/)

