# 序列化 Codec 接入指南（SBE / Protobuf / Fory）

本文档整合了本 SDK 三种业务 codec 的接入说明：

- **`aeron-codec-sbe`**：泛型 `SbeCodec` 适配框架，本身不含业务 schema、不跑 sbe-tool
- **`aeron-codec-protobuf`**：泛型 `ProtobufCodec<T extends MessageLite>` 适配 protobuf-java，本身不含业务 `.proto`、不跑 `protoc`
- **`aeron-codec-fory`**：[Apache Fory](https://fory.apache.org/) 高性能多语言序列化的 SDK 端 codec，只依赖 `org.apache.fory:fory-core`，**0 Spring 依赖**

阅读导航：

- 先看 [§0 总览与选型](#0-总览与选型) 决定用哪个 codec
- 再跳到对应章节：[§1 SBE 接入](#1-sbe-接入) / [§2 Protobuf 接入](#2-protobuf-接入) / [§3 Fory 接入](#3-fory-接入)

---

## 0. 总览与选型

### 0.1 四种 codec 一张表

| 维度 | JSON (Jackson) | Protobuf | SBE | Fory (Java 模式) |
|---|---|---|---|---|
| **编码方式** | 运行时反射 + UTF-8 拼装 | 编译期 codegen + 运行时反序列化 | 编译期 codegen，纯偏移读写 | 运行时 JIT 编译 + 类元数据（二进制）|
| **单条编解码延迟** | ~2~10 µs | ~200 ns（典型）| ~50 ns（典型）| ~50~200 ns（典型，JAVA 模式）|
| **GC 压力** | 高（中间字符串）| 中（构造 builder / 中间对象）| 极低（zero-copy wrap）| 低（Fory 内部缓存）|
| **schema 演进** | 字段名匹配，无强 schema | 字段新增向后兼容（很灵活）| `blockLength` + `version` 字段管理向后兼容（约束更严）| Fory 自家 schema evolution，跨次版本兼容 |
| **需不需要业务 schema 文件** | 否（POJO 即可）| 是（`.proto` codegen）| 是（`.xml` codegen）| 否（POJO 即可）|
| **跨语言** | ✅ 全语言原生支持，但字段命名 / 数值精度易踩坑 | ✅ **跨语言双必选**：protoc 官方支持 Java / C++ / Go / Python / C# / Rust / Dart / Ruby / PHP 等 10+ 语言 | ✅ **跨语言双必选**：sbe-tool 官方支持 Java / C++ / C# / Go / Rust | ⚠️ XLANG 模式跨语言；JAVA 模式仅 Java 内部 |
| **schema 治理成本** | 极低（无 schema）| 中（独立 `proto-schemas` repo）| 中-高（独立 `sbe-schemas` repo + XML）| 极低（POJO 即用）|
| **业务方学习曲线** | 极低 | 低（`.proto` 语法直观）| 中-高（XML schema + sbe-tool 工具链）| 极低（POJO）|
| **wire `CODEC_ID`** | 0（`JSON`）| 2（`PROTOBUF`）| 1（`SBE`）| 5（`FORY`）|

### 0.2 场景决策表

| 场景 | 推荐 codec | 跳转 |
|---|---|---|
| 新业务，低延迟广播 / 行情 / tick 全推 / 撮合事件 | **SBE** | [§1](#1-sbe-接入) |
| 已有大量 Protobuf 业务消息（gRPC / Kafka / 配置中心）想接入本广播 SDK | **Protobuf** | [§2](#2-protobuf-接入) |
| 跨语言对端是 Python / C# / Rust / Dart 等 sbe-tool 不直接出 target 的语言 | **Protobuf** | [§2](#2-protobuf-接入) |
| 纯 Java 服务、不关心跨语言、想零配置 POJO 接入 | **Fory** | [§3](#3-fory-接入) |
| 调试场景 / 与 web 前端共享格式 / schemaless 配置 | **JSON** | — |

### 0.3 SBE / Protobuf 是跨语言双必选，不是取舍

本 SDK 跨语言互通的两个必选 codec 是 **SBE** 和 **Protobuf**（详见 [`docs/aeron协议说明.md`](aeron协议说明.md) §4），**并存而非取舍**：

- **Protobuf**：业务方既有协议、向后兼容好、生态成熟，**跨语言场景兼容现存业务的必选项**
- **SBE**：低延迟、零拷贝、强 schema 治理，**新业务低延迟广播的首选项**
- **Fory**：纯 Java 服务的零配置 POJO 兜底（跨语言 binding 生态不稳定，仅 JAVA 内部或与公司其他 Fory 实例 XLANG 互通）

**选 SBE 的典型信号**：

- 单条消息 < 256 字节、定长（行情 Quote / Trade / Tick / OrderAck / Fill）
- 吞吐目标 > 100 万 msg/sec/core
- 延迟预算 < 1 µs/single-hop（包含 codec encode + frame + Aeron 传输 + decode）
- 团队能接受 XML schema + sbe-tool 工具链

**选 Protobuf 的典型信号**：

- 已有 Protobuf 业务消息想接入广播 SDK
- 跨语言对端是 Python / C# / Rust / Dart 等语言
- 消息含 repeated / nested message 复杂结构
- 延迟预算宽松（> 10 µs），吞吐 < 100 万 msg/sec/core

**选 Fory 的典型信号**：

- 业务模型是 POJO，不想/不能拉一份 `.proto` / `.xml` 文件做 codegen
- 想要 Protobuf 量级（或更好）的性能 + 体积，又要保留 JSON 的"零 schema 文件"开发体验
- Java 内部传输（JAVA 模式即可），或与公司其他 Fory 实例互通（XLANG 模式）

### 0.4 多 codec 并存

同一个 producer / consumer 实例可以同时注册多个不同家族的 codec，发送时按 `payload.getClass()` 自动派发，wire 帧上靠 `CODEC_ID` 区分 codec 家族：

```java
AeronProducer producer = AeronProducer.builder()
    .driver(dm)
    .codec(SbeCodec.fixedLength(Quote.class, 28, ...))         // wire CODEC_ID=1
    .codec(ProtobufCodec.forType(OrderProto.class))            // wire CODEC_ID=2
    .codec(ForyCodec.forType(Trade.class))                     // wire CODEC_ID=5
    .build();

producer.send("md.quote.aapl", new Quote("AAPL", ...));        // SBE 路径
producer.send("orders.new",    OrderProto.newBuilder()...);    // Protobuf 路径
producer.send("trades",        new Trade(...));                // Fory 路径
```

> **同一 codec 家族多 type 的派发主键是业务 `Class<T>`，不是 wire `CODEC_ID`**。这是所有家族（SBE / Protobuf / Fory）共同遵循的核心契约，详见各章的「多 type 派发」小节与 [`docs/aeron协议说明.md`](aeron协议说明.md) §4.1。

---

## 1. SBE 接入

`aeron-codec-sbe` 模块只提供 **泛型 SbeCodec 适配框架**，本身不含任何业务消息 schema、不跑 sbe-tool。Schema 治理由业务公司在独立的 `sbe-schemas` repo 维护。

### 1.1 推荐的工程组织（独立 sbe-schemas repo）

```
your-company/
├── company-sbe-schemas/                   ← 独立 repo（推荐）
│   ├── src/main/sbe/
│   │   ├── marketdata.xml                 ← 行情消息（Quote / Trade / Tick / L2Snapshot）
│   │   └── trading.xml                    ← 交易事件（OrderAck / Fill / Cancel）
│   ├── build.gradle                       ← 跑 sbe-tool codegen + 发 jar
│   └── ...                                ← codegen 出来的 Encoder / Decoder
│
├── aeron-broadcast/                       ← 本 SDK
│   ├── aeron-codec-sbe                    ← 泛型 SbeCodec（不含业务 schema）
│   └── ...
│
└── market-data-publisher/                 ← 业务应用
    ├── build.gradle                       ← 同时依赖 company-sbe-schemas + aeron-codec-sbe
    └── src/main/java/.../Publisher.java   ← 用 SbeCodec.fixedLength(...) 注册即可
```

为什么 schema 单独 repo：

- **跨业务复用**：同一份 schema 给 broadcast / FIX gateway / 文件归档 / Python 离线分析共享，避免拷贝。
- **生命周期与 SDK 解耦**：本 broadcast SDK 升级不应影响 schema；schema 字段新增也不该改 SDK。
- **统一治理**：CODEOWNERS / PR review / 版本号 / 跨语言生成同步在一个仓库管理。

### 1.2 Schema 示例（`marketdata.xml`）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sbe:messageSchema xmlns:sbe="http://fixprotocol.io/2016/sbe"
                   package="com.company.sbe.market"
                   id="1" version="0" semanticVersion="1.0"
                   byteOrder="littleEndian">

    <types>
        <composite name="messageHeader" description="SBE 标准头">
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

    <sbe:message name="Trade" id="2">
        <field name="symbol" id="1" type="symbolType"/>
        <field name="price"  id="2" type="int64"/>
        <field name="qty"    id="3" type="int64"/>
        <field name="side"   id="4" type="uint8"/>
    </sbe:message>

</sbe:messageSchema>
```

### 1.3 `company-sbe-schemas` 的 `build.gradle` 集成 sbe-tool

最简单的做法是用 `JavaExec` 直接跑 sbe-tool 的 main：

```groovy
plugins { id 'java-library' }

repositories { mavenCentral() }

dependencies {
    api 'org.agrona:agrona:1.22.0'
    runtimeOnly 'uk.co.real-logic:sbe-tool:1.32.0'
}

def generatedSrc = layout.buildDirectory.dir('generated/sbe').get().asFile

sourceSets.main.java.srcDirs += generatedSrc

tasks.register('generateSbe', JavaExec) {
    group = 'codegen'
    description = 'Generate Java codecs from SBE XML schemas'
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

跑 `./gradlew :company-sbe-schemas:build` 后，`com.company.sbe.market.QuoteEncoder` 等类会出现在 jar 里。

### 1.4 业务应用接入

#### 1.4.1 build.gradle

```groovy
dependencies {
    implementation 'com.mcst:aeron-producer'
    implementation 'com.mcst:aeron-codec-sbe'
    implementation 'com.company:company-sbe-schemas:1.0.0'   // 你公司 schema jar
}
```

#### 1.4.2 Producer 注册 + send

```java
import com.company.sbe.market.MessageHeaderEncoder;
import com.company.sbe.market.QuoteEncoder;
import com.mcst.aeron.codec.sbe.SbeCodec;
import com.mcst.aeron.producer.AeronProducer;

// 业务侧 Quote POJO（不必和 schema 字段一一对应，业务层抽象）
record Quote(String symbol, long price, int qty) {}

AeronProducer producer = AeronProducer.builder()
    .driver(dm)
    .codec(SbeCodec.fixedLength(
        Quote.class,
        MessageHeaderEncoder.ENCODED_LENGTH + QuoteEncoder.BLOCK_LENGTH,    // 8 + 24 = 32
        (q, buf, off) -> {
            // sbe-tool 生成的 Encoder 标准用法
            QuoteEncoder enc = new QuoteEncoder();
            MessageHeaderEncoder hdr = new MessageHeaderEncoder();
            enc.wrapAndApplyHeader(buf, off, hdr)
               .price(q.price())
               .qty(q.qty())
               .symbol(q.symbol());
            return MessageHeaderEncoder.ENCODED_LENGTH + enc.encodedLength();
        },
        (buf, off, len) -> {
            MessageHeaderDecoder hdr = new MessageHeaderDecoder().wrap(buf, off);
            QuoteDecoder dec = new QuoteDecoder().wrap(
                buf, off + hdr.encodedLength(), hdr.blockLength(), hdr.version());
            return new Quote(dec.symbol(), dec.price(), dec.qty());
        }))
    .build();

producer.send("md.l1.aapl", new Quote("AAPL", 187_42L, 100));
```

业务方可以提取一个工具类 `MarketDataCodecs` 把这段 boilerplate 包装好，对业务调用方暴露简洁 API：

```java
public final class MarketDataCodecs {
    public static SbeCodec<Quote> quoteCodec() { /* 上面那段 */ }
    public static SbeCodec<Trade> tradeCodec() { /* 类似 */ }
}

// 业务调用方
producer.codec(MarketDataCodecs.quoteCodec());
producer.codec(MarketDataCodecs.tradeCodec());
```

#### 1.4.3 Consumer 订阅

```java
AeronConsumer consumer = AeronConsumer.builder()
    .driver(dm)
    .codec(MarketDataCodecs.quoteCodec())   // 与 producer 同一份 codec 注册
    .codec(MarketDataCodecs.tradeCodec())
    .build();

consumer.subscribe("md.l1.aapl", Quote.class, (q, ctx) -> {
    // 直接拿到业务对象
    System.out.println(q.symbol() + " " + q.price());
});
consumer.start();
```

### 1.5 SDK API 一览

| 工厂方法 | 用途 | 性能特征 |
|---|---|---|
| `SbeCodec.fixedLength(type, totalLength, encoder, decoder)` | 业务消息总字节数固定（schema 编译期常量） | encodedLength 零开销，encode 一次写入 claim buffer，零拷贝 |
| `SbeCodec.varLength(type, maxLengthFn, encoder, decoder)` | 业务消息含 var-data / repeating group | 双重序列化（先到 ThreadLocal scratch 量长度，再到 claim buffer），~2x CPU |

#### `SbeEncoderOp<T>` / `SbeDecoderOp<T>`

```java
@FunctionalInterface
interface SbeEncoderOp<T> {
    int encode(T value, MutableDirectBuffer buffer, int offset);
}

@FunctionalInterface
interface SbeDecoderOp<T> {
    T decode(DirectBuffer buffer, int offset, int length);
}
```

业务方在 lambda 里完整负责 wire 字节（含 messageHeader），框架完全透明。

### 1.6 性能 / 正确性注意事项

#### 1.6.1 fixedLength 是默认选择

Quote / Trade / Tick / OrderAck / Fill 等 99% 行情 / 交易消息天然定长。**优先用 `fixedLength`**：未启用压缩时 `encode` 直写 Aeron claim buffer，`encodedLength` 直接返回常量，零额外开销。

> ⚠️ **`totalLength` 必须与 lambda 实际写入字节数完全一致**。框架的 `written != totalLength` 检查只是事后 best-effort，写少时 frame 当前位置变 padding（OK），但**写多会越界写入下一帧无法回滚**（`claim.abort()` 救不回越界字节，wire 数据破坏）。schema 升级（`BLOCK_LENGTH` 变了）时务必同步更新业务方传入的常量。

#### 1.6.2 varLength 的 mutation 防护

`varLength` 走 "encodedLength 量长度 → encode 写出" 双调用模式。如果业务 lambda 在两次调用之间修改了 `value` 导致字节数变化，框架抛 `CodecException` 中断 send（防止 frame header 上 `PAYLOAD_LEN` 与实际字节不符）。**业务责任：在同一条 `send()` 调用范围内 payload 不可变**。

#### 1.6.3 maxLengthFn 给宽松上界

`varLength` 工厂的 `maxLengthFn` 是 ThreadLocal scratch 预分配上界，给真实最大值的 1.2~1.5x 即可（多分配的字节短期 GC 回收）。算小了会抛 `CodecException`，算大了只是 ThreadLocal 内存多占点。

#### 1.6.4 schema 升级（version 字段）

SBE 用 messageHeader 里的 `version` 字段做向后兼容：

- 加字段 → bump `schemaVersion`（向后兼容，老 consumer 用 `blockLength` 截断不读新字段）
- 改字段类型 / 删字段 → bump `schemaId`（不向后兼容，所有节点同步升级）

业务方在 decoder lambda 里可以用 `MessageHeaderDecoder.version()` 区分版本走不同分支。

#### 1.6.5 wire codec id

所有 SBE 消息类型在 wire 上 `CODEC_ID = 1`（`CodecIds.SBE`）。同 family 多 type 通过订阅 type 派发，不冲突；详见 `docs/aeron协议说明.md` §4.1 与 `Codec.java` javadoc。

#### 1.6.6 sbe-tool 版本兼容矩阵

SBE wire 由 OMG Simple Binary Encoding spec 标准化，**spec 层面长期稳定**；但跨工具实现的边界处理可能漂移（如 var-data 内部对齐字节、enum encoding 编码细节）。跨语言互通时建议双端锁定到下表中的对齐版本：

| 语言 | 工具 / 库 | 推荐版本 | 备注 |
|---|---|---|---|
| **Java** | `uk.co.real-logic:sbe-tool` | **1.32.x**（本 SDK 当前对齐版本） | 见本章 §1.3 业务方 `company-sbe-schemas` 的 `build.gradle` |
| **C++** | `sbe-tool` （`--target=Cpp`） | 与 Java 端 sbe-tool 同版本 | sbe-tool 一份代码同时支持 Java / C++ / C# / Go / Rust target，本质用同一份 codegen 逻辑 |
| **C#** / .NET | `sbe-tool` （`--target=CSharp`） | 同上 | — |
| **Go** | `sbe-tool` （`--target=Go`） 或社区 `sbe-go-codec` | 与 Java 端 sbe-tool 同主版本 | sbe-tool 1.30+ 原生支持 Go target；若用社区分叉，需 verify wire 兼容 |
| **Rust** | `sbe-tool` （`--target=Rust`） | sbe-tool 1.30+ | Rust target 较新，跨语言重 case 之前先跑黄金 hex 验证 |

**对齐策略**：

1. 在公司 `sbe-schemas` repo 的 `build.gradle` 里**显式锁定 sbe-tool 版本**（`runtimeOnly 'uk.co.real-logic:sbe-tool:1.32.x'`），随业务 schema 一起 commit
2. 跨语言 SDK 用户在自己的工程里**也用同一个 sbe-tool 跑 codegen**（推荐做法：直接调用 schema repo 的 `:generateSbe<Lang>` Gradle task / Makefile target，**而不是**用各语言生态自己 fork 的 sbe binding）
3. 每次 sbe-tool 升级版本，**跨语言双端必须同步升级**；过 [`跨语言互通指南.md`](跨语言互通指南.md) §1 黄金 verify 路径第 5 步（SBE Quote）作为回归
4. 真要回滚 Java 端 sbe-tool 版本时，先 verify 旧版 codegen 出来的 wire 与跨语言对端字节一致再发布

#### 1.6.7 schema XML 必须显式 byteOrder="littleEndian"

SBE schema 允许在 `<sbe:messageSchema>` 根元素写 `byteOrder="littleEndian"` 或 `bigEndian`：

```xml
<sbe:messageSchema xmlns:sbe="http://fixprotocol.io/2016/sbe"
                   package="com.company.sbe.market"
                   id="1" version="0"
                   byteOrder="littleEndian">           <!-- 必须显式写 -->
```

**强制约束**：

- 本 SDK 的 wire 协议（`docs/aeron协议说明.md` §2）统一 little-endian；SBE 出现在 `PAYLOAD` 部分，**必须**与 frame header 字节序一致
- sbe-tool 默认就是 littleEndian（缺省值），但**默认值是"软约束"**，被同事在某次 PR 里改成 `bigEndian` 没人发现 → 一端按 LE 编、另一端按 BE 解 → 所有数值字段全乱（symbol 字段因为是 ASCII 字节序无关，看起来"部分通"，特别难诊断）
- CI 建议加一条 lint：grep schema XML 文件，缺少 `byteOrder="littleEndian"` 或写成 `bigEndian` 的直接 fail（见 `docs/跨语言互通指南.md` §8 第 18 条坑）

#### 1.6.8 schema 演化跨语言双端时序

SBE 用 `messageHeader.version` 字段做向后兼容（§1.6.4 已说明 Java 端机制）。跨语言场景下双端升级时序要遵守：

| 变更类型 | schema 改动 | 双端升级时序 | 说明 |
|---|---|---|---|
| **加非必需字段** | bump `schemaVersion`（如 0 → 1），新字段加 `sinceVersion="1"` | 任意端先升级都 OK | 老 consumer 看 `blockLength` 截断不读新字段；新 consumer 收老帧时 `version == 0`，新字段按 `<presence="optional">` 默认值回退 |
| **改字段类型 / 改长度** | bump `schemaId`（如 1 → 2） | 强制：所有 producer / consumer **同步升级**到新 schema | schemaId 跨版本不兼容；同 wire 帧 `CODEC_ID = 1` 看不出 schema 差异，会被对端按错误布局解读 |
| **删字段** | 不允许（SBE 不支持删字段，只能改成 `deprecated`） | — | 老节点仍按原偏移读 |

**跨语言场景的额外约束**：

1. schema 版本号（`schemaVersion` 字段）必须**双端用同一份 schema XML codegen**，不能 Java 端用 v1、Go 端用 v2 的 schema 自由演化
2. 业务方在 decoder lambda 里**必须**用 `MessageHeaderDecoder.version()` 区分版本走不同分支（特别是含 optional 字段时）；漏处理就会读到垃圾
3. 跨语言双端升级的推荐顺序：**先升所有 consumer（兼容新老 schema），再升 producer**；反之老 consumer 收到新 wire 时按 blockLength 截断丢字段没问题，但若 producer 先升而 consumer 漏跟，新增 required 字段会被解错

### 1.7 SBE 跨语言对齐

> 本节是面向**跨语言 SDK 实现者**（Go / C++ / .NET / Rust SDK 开发者）和**业务方多语言部署**的工程对齐手册。配套阅读 [`docs/跨语言互通指南.md`](跨语言互通指南.md) §3.6。

#### 1.7.1 wire 字节布局

`docs/aeron协议说明.md` 定义了本 SDK 的 wire 帧格式（40 字节 header + topic + payload）。**SBE 字节序列作为整体出现在 `payload` 部分**：

```
+-------------------------+-------------------+---------------------------------------+
| broadcast frame (40 B)  | topic (1..255 B)  | PAYLOAD = SBE messageHeader + body    |
+-------------------------+-------------------+---------------------------------------+
                                              |<--- frame.PAYLOAD_LEN bytes  ------->|
                                              |
                                              +-> +----------------------+----------+
                                                  | messageHeader (8 B)  | body (N) |
                                                  +----------------------+----------+
                                                  | blockLength (u16 LE) |          |
                                                  | templateId  (u16 LE) | 业务字段 |
                                                  | schemaId    (u16 LE) | (sbe-tool |
                                                  | version     (u16 LE) |  生成)   |
                                                  +----------------------+----------+
```

跨语言 SDK 实现端只需：

1. 按 `docs/aeron协议说明.md` 解 broadcast frame header / topic（这一层与 SBE 无关）
2. 拿到 `payload` 字节后，喂给对应语言的 SBE codec（sbe-tool `--target=Cpp/Go/CSharp/Rust` 生成的 `XxxDecoder.wrap(buf, offset, blockLength, version)`）解码
3. 反向：encode 时直接把 sbe-tool 生成的 `XxxEncoder` 的输出（含 messageHeader 整段）写到 broadcast frame 的 `PAYLOAD` 区

#### 1.7.2 Go 端使用示意（伪代码）

假设业务 schema 与 Java 端 §1.4.2 一致（`Quote` fixedLength，messageHeader 8 + body 20 = 28 字节）：

```go
// Step 1: schema codegen（业务方在 sbe-schemas repo 跑）
//   sbe-tool --output-dir=./gen/go --target=Go marketdata.xml
//   生成 quote_encoder.go / quote_decoder.go / message_header.go

import (
    "github.com/your-company/sbe-schemas/gen/go/market"  // codegen 输出
    "github.com/your-company/aeron-broadcast-go/codec"   // 跨语言 SDK 框架（待实现）
)

// Step 2: 业务 type
type Quote struct {
    Symbol string
    Price  int64
    Qty    int32
}

// Step 3: 注册 SBE codec（fixedLength 路径，Go 等价 API）
sbeQuoteCodec := codec.SbeFixedLength[Quote]{
    TotalLength: 28,  // 与 Java 端 totalLength 必须一致
    Encode: func(q Quote, buf []byte) int {
        hdr := market.MessageHeaderEncoder{}
        enc := market.QuoteEncoder{}
        enc.WrapAndApplyHeader(buf, 0, &hdr).
            Price(q.Price).
            Qty(q.Qty).
            PutSymbol(q.Symbol)
        return market.MessageHeaderEncoderLength + enc.EncodedLength()
    },
    Decode: func(buf []byte) Quote {
        hdr := market.MessageHeaderDecoder{}
        hdr.Wrap(buf, 0)
        dec := market.QuoteDecoder{}
        dec.Wrap(buf, hdr.EncodedLength(), hdr.BlockLength(), hdr.Version())
        return Quote{
            Symbol: dec.SymbolAsString(),
            Price:  dec.Price(),
            Qty:    dec.Qty(),
        }
    },
}

producer.Codec(sbeQuoteCodec)
producer.Send("md.l1.aapl", Quote{Symbol: "AAPL", Price: 18742, Qty: 100})

// Step 4: 反向 — Java 发，Go 收
consumer.Subscribe("md.l1.aapl", reflect.TypeOf(Quote{}), func(q Quote, ctx Context) {
    fmt.Printf("%s %d %d\n", q.Symbol, q.Price, q.Qty)
})
```

> Go SDK 接口尚未实现（见仓库根 README "跨语言 SDK 路线图"）。这里仅展示 wire 兼容性目标，真正 API 名称以 Go SDK 实施时为准。

#### 1.7.3 同 codec 家族多业务 type 派发（核心契约，再次强调）

跨语言 SDK 实现端**最容易踩的 P0 坑**：

| 错误实现 | 现象 |
|---|---|
| 用 wire `CODEC_ID` 当 codec 派发主键，注册成 `codecRegistry.byId[1] = QuoteCodec`，第二次 `register(TradeCodec)` 把第一次覆盖 | 同时注册 `Quote` 和 `Trade` 两个 SBE codec 时，只有最后注册的 type 能收到，其他全静默丢失 |
| 用 SBE `templateId` 当 codec 派发主键 | 业务方加新 message type 时忘了在 SDK 注册表里加映射，wire 收到能解但找不到 handler |

**正确做法**（与 Java 端一致）：

- consumer 端 codec 派发主键用 **订阅时声明的业务 type**（Java 端 `Class<T>` / Go 端 `reflect.Type` / C++ 端模板参数 / Rust 端 `TypeId`）
- wire `CODEC_ID = 1` 仅做 cross check：consumer 拿到的 codec instance 的 `codecId()` 必须等于 1，否则 producer / consumer codec 配对错误 → 丢消息 + `metrics.onError`
- SBE `templateId` 在 codec.decode 内部由 sbe-tool 生成的 `MessageHeaderDecoder` 读出，**仅用于多消息共享一个 codec instance 时分发到正确的 sbe-tool 生成 decoder 类**（如业务方写一个 `MarketMessageCodec` 内部按 templateId 派发 Quote/Trade），这是业务侧选项，不是 SDK 强制约束

#### 1.7.4 跨语言互通 verify 清单

按顺序通过即认为 SBE 跨语言互通到位：

| # | 测试 | 期望 |
|---|---|---|
| 1 | 黄金 hex 文件 `docs/wire-samples/sbe-quote-fixed.hex`：Java 端导出 `Quote("AAPL", 18742, 100)` | Go 端用同 schema codegen 解出等值 `Quote` |
| 2 | 反向：Go 端编同样 `Quote("AAPL", 18742, 100)` | wire 字节 bit-for-bit 等于黄金 hex 文件 |
| 3 | 双向 SBE Quote 通过 IPC + RAW transport 互通（[`跨语言互通指南.md`](跨语言互通指南.md) §1 第 5 步） | latency / 字节正确性 |
| 4 | 双向 SBE varLength（如 `OrderBookSnapshot` 含 repeating group）互通 | var-data 跨语言对齐 |
| 5 | 同 transport 同时注册 SBE Quote + SBE Trade 各发一条 | 两端按订阅 type 正确分发，不串 handler（验证 §1.7.3）|
| 6 | schema 升级（v0 加字段到 v1）双端时序兼容 | 老 consumer 收新帧按 blockLength 截断；新 consumer 收老帧按 version 走默认值（验证 §1.6.8）|

---

## 2. Protobuf 接入

`aeron-codec-protobuf` 模块提供 **`ProtobufCodec<T extends MessageLite>`** 适配 protobuf-java，本身不持有任何业务 `.proto` schema、不跑 `protoc`。Schema 治理由业务公司在独立的 `proto-schemas` repo 维护。

### 2.1 推荐的工程组织（独立 proto-schemas repo）

```
your-company/
├── company-proto-schemas/                   ← 独立 repo（推荐）
│   ├── src/main/proto/
│   │   ├── trading/
│   │   │   ├── order.proto                  ← OrderProto / OrderAckProto / FillProto ...
│   │   │   └── execution.proto              ← ExecutionReportProto ...
│   │   ├── marketdata/
│   │   │   ├── quote.proto                  ← QuoteProto / TradeProto ...
│   │   │   └── snapshot.proto               ← OrderBookSnapshotProto ...
│   │   └── common/
│   │       └── header.proto                 ← 公共 envelope / metadata 字段
│   ├── build.gradle                         ← protoc-gen-java 集成
│   └── ...                                  ← codegen 出来的 *Proto.java
│
├── aeron-broadcast/                         ← 本 SDK
│   ├── aeron-codec-protobuf                 ← 泛型 ProtobufCodec（不含业务 schema）
│   └── ...
│
└── trading-publisher/                       ← 业务应用
    ├── build.gradle                         ← 同时依赖 company-proto-schemas + aeron-codec-protobuf
    └── src/main/java/.../Publisher.java     ← 用 ProtobufCodec.forType(OrderProto.class) 注册即可
```

为什么 schema 单独 repo（与 SBE §1.1 同理）：

- **跨业务复用**：同一份 `.proto` 给 broadcast / gRPC service / Kafka topic / 文件归档 / Python 离线分析共享，避免拷贝
- **跨语言一致性**：Java / Go / C++ / Python 各端从**同一 git tag** 拉 schema 跑 `protoc`，避免字段漂移
- **生命周期与 SDK 解耦**：本 broadcast SDK 升级不影响 schema；schema 字段新增也不该改 SDK
- **统一治理**：CODEOWNERS / PR review / 版本号 / 字段编号分配在一个仓库管理

### 2.2 Schema 示例（`marketdata/quote.proto`）

```protobuf
syntax = "proto3";

package company.marketdata;

option java_package         = "com.company.proto.marketdata";
option java_multiple_files  = true;
option java_outer_classname = "QuoteProtos";
option go_package           = "github.com/your-company/proto-schemas/gen/go/marketdata;marketdata";

message QuoteProto {
    string symbol = 1;
    int64  price  = 2;   // 价格 × 100，避免浮点
    int32  qty    = 3;
}

message TradeProto {
    string symbol      = 1;
    int64  price       = 2;
    int64  qty         = 3;
    uint32 side        = 4;   // 0 = buy, 1 = sell
    int64  exec_ns     = 5;   // 撮合时间
}
```

> **强烈建议双端固定使用 `proto3`**（向后兼容更可控；`proto2` 的 `required` / `optional` 语义在跨语言演化时容易出问题）。

### 2.3 `company-proto-schemas` 的 `build.gradle` 集成 protoc

推荐使用 `protobuf-gradle-plugin`（官方维护）：

```groovy
plugins {
    id 'java-library'
    id 'com.google.protobuf' version '0.9.4'
}

repositories { mavenCentral() }

dependencies {
    // protobuf-java 运行时（与本 SDK 当前对齐版本一致：3.25.5）
    api 'com.google.protobuf:protobuf-java:3.25.5'
}

protobuf {
    protoc {
        artifact = 'com.google.protobuf:protoc:3.25.5'
    }
    generateProtoTasks {
        all().each { task ->
            task.builtins {
                java {}
                // 同 repo 同时出 Go target（跨语言对端用同一 git tag 直接拉）
                // 需另装 protoc-gen-go：见 §2.7 跨语言对齐
            }
        }
    }
}
```

跑 `./gradlew :company-proto-schemas:build` 后，`com.company.proto.marketdata.QuoteProto` 等类会出现在 jar 里。

### 2.4 业务应用接入

#### 2.4.1 build.gradle

```groovy
dependencies {
    implementation 'com.mcst:aeron-producer'
    implementation 'com.mcst:aeron-consumer'
    implementation 'com.mcst:aeron-codec-protobuf'
    implementation 'com.company:company-proto-schemas:1.0.0'   // 你公司 schema jar
}
```

#### 2.4.2 Producer 注册 + send

```java
import com.company.proto.marketdata.QuoteProto;
import com.company.proto.marketdata.TradeProto;
import com.mcst.aeron.codec.protobuf.ProtobufCodec;
import com.mcst.aeron.producer.AeronProducer;

AeronProducer producer = AeronProducer.builder()
    .driver(dm)
    // ⚠️ 每个 protobuf type 必须注册独立 codec 实例
    .codec(ProtobufCodec.forType(QuoteProto.class))
    .codec(ProtobufCodec.forType(TradeProto.class))
    .build();

producer.send("md.l1.aapl",
    QuoteProto.newBuilder()
        .setSymbol("AAPL").setPrice(18742L).setQty(100)
        .build());

producer.send("md.l1.aapl",
    TradeProto.newBuilder()
        .setSymbol("AAPL").setPrice(18742L).setQty(50L).setSide(0)
        .build());
```

#### 2.4.3 Consumer 订阅

```java
AeronConsumer consumer = AeronConsumer.builder()
    .driver(dm)
    // 与 producer 端**完全相同的注册**：每个 type 一个独立 codec 实例
    .codec(ProtobufCodec.forType(QuoteProto.class))
    .codec(ProtobufCodec.forType(TradeProto.class))
    .build();

// ⚠️ subscribe 必须明确声明 payloadType（不是按 wire CODEC_ID 派发）
consumer.subscribe("md.l1.aapl", QuoteProto.class, (q, ctx) -> {
    System.out.println("quote: " + q.getSymbol() + " " + q.getPrice());
});

consumer.subscribe("md.l1.aapl", TradeProto.class, (t, ctx) -> {
    // 注意：同一 topic 可同时订阅多个 type 吗？
    // 不能 —— 一个 topic 在 consumer 端只能绑一个 payloadType。
    // 多 type 共享 topic 时，业务方需用 protobuf `oneof` 或 envelope message 包一层
    // （见 §2.4.4）。
});

consumer.start();
```

#### 2.4.4 同 topic 多 type 的两种模式

| 模式 | 做法 | 适用 |
|---|---|---|
| **每 topic 单 type**（推荐） | 一个 topic 一个 message type；不同 type 用不同 topic（如 `md.quote.aapl` / `md.trade.aapl`） | 大多数业务；topic 即 type 的语义清晰，consumer 端 dispatch 简单 |
| **envelope + oneof** | 业务方定义一个 `MarketEvent` envelope，内含 `oneof body { QuoteProto quote = 1; TradeProto trade = 2; }`；本 SDK 只看见 `MarketEvent`，consumer 内部判 `getBodyCase()` 分发 | 必须保序的混合事件流（如撮合事件 + 行情更新都按时间序）|

### 2.5 SDK API 一览

| 工厂方法 | 用途 | 性能特征 |
|---|---|---|
| `ProtobufCodec.forType(Class<T>)` | 标准接入；通过反射调 `T.parser()` 拿 parser | parser 反射结果带 `ConcurrentMap` cache，每个 type 仅反射一次 |
| `ProtobufCodec.builder(T).parser(p).build()` | 显式注入 `Parser<T>`，跳过反射 | 用于 protobuf-lite runtime / 自定义 parser |
| `ProtobufCodec.builder(T).extensionRegistry(reg).build()` | 自定义 extension registry | 用 `.proto` 含 extensions（proto2 风格）的场景 |

#### `ProtobufCodec<T extends MessageLite>`

- `codecId() == 2`（`CodecIds.PROTOBUF`）—— 所有 Protobuf type 共享同一 wire id
- `type()` —— 唯一标识 codec 实例：consumer 端按订阅 type 派发的主键
- `encodedLength(value)` —— 调 `value.getSerializedSize()`
- `encode(value, buffer, offset)` —— **zero-copy 优先**：
  - 如果 `buffer.byteArray() != null`（heap buffer），直接 `CodedOutputStream.newInstance(heap, abs, size)` 写到底层数组，**0 拷贝**
  - 如果 `buffer.byteBuffer() != null`（direct buffer），`CodedOutputStream.newInstance(view)` 写到底层 `ByteBuffer`，**0 拷贝**
  - 否则（纯裸地址）走 ThreadLocal scratch（256 字节起，按需 ×2 增长，超 1 MiB 走一次性数组）
- `decode(buffer, offset, length)` —— 镜像 zero-copy 路径

### 2.6 性能 / 正确性注意事项

#### 2.6.1 zero-copy 路径

只要业务方走 Aeron 默认的 `tryClaim → BufferClaim` 写入（producer 主路径），`MutableDirectBuffer` 是 heap-backed `UnsafeBuffer`，本 codec 自动走 0 拷贝。**业务方不需要做任何配置**。

#### 2.6.2 多 type 派发（P0 警告，再三强调）

```java
// ❌ 错误：以为 codec 用 wire CODEC_ID=2 派发，注册一个就够
producer.codec(ProtobufCodec.forType(OrderProto.class));
// 后面发 TradeProto 会抛 CodecException: no codec for type TradeProto

// ✅ 正确：每个 protobuf type 都要注册独立 codec 实例
producer.codec(ProtobufCodec.forType(OrderProto.class));
producer.codec(ProtobufCodec.forType(TradeProto.class));
producer.codec(ProtobufCodec.forType(FillProto.class));
// 一一对应，向 byType 表注册
```

**Consumer 端同理**：每个用到的 type 都要注册 + `subscribe` 时声明 `payloadType`。

这是因为 wire `CODEC_ID = 2` 只标 **Protobuf 家族**，不区分具体 message type；本 SDK 派发主键用订阅时声明的业务 type（`Class<T>`），不用 wire `CODEC_ID`（否则同 wire id 多 type 会被 byId 静默覆盖，是 Java 端 P0 历史教训，详见 [`docs/aeron协议说明.md`](aeron协议说明.md) §4.1 / [`docs/跨语言互通指南.md`](跨语言互通指南.md) §3.5）。

#### 2.6.3 schema 演化策略（向后兼容）

Protobuf proto3 的字段演化规则（业务方必读）：

| 变更 | 兼容性 | 注意 |
|---|---|---|
| **加新字段**（保留新字段号）| ✅ 向后兼容 | 老 consumer 把新字段当作 unknown 字段（默认丢弃；可在 generator option 打开 preserve unknowns）|
| **删字段** | ⚠️ 兼容但有坑 | 删字段后**字段号绝不能复用**（否则老节点解出来字段被错误填充）。建议在 `.proto` 里加 `reserved 5;` 显式占位 |
| **改字段类型** | ❌ 不兼容 | 必须改字段名 + 新分配字段号 + 旧字段 `reserved` |
| **改字段名** | ✅ wire 兼容 | wire 只看字段号，但**跨语言 codegen 出来 setter / getter 名变了，业务代码要同步改** |
| **改 `optional` ↔ `singular`** | ✅ 兼容（proto3）| proto3 默认 singular；标 `optional` 后能区分"未设置"vs"值是默认值" |
| **改 `singular` ↔ `repeated`** | ❌ 不兼容 | wire 解码会失败 |

跨语言场景的额外约束：

1. **不要复用字段号**：跨语言双端要靠字段号比对 wire 字节，复用号会导致一端解出旧字段值、另一端解出新字段值
2. **不要假设字段顺序**：protobuf 编码不保证字段顺序，跨语言 SDK 解出来的 message 行为应当**与字段顺序无关**
3. **新字段必须有合理默认**：老 consumer 收到新 wire 时看不到新字段，业务逻辑要能处理"字段缺失"

#### 2.6.4 wire codec id

所有 Protobuf 消息类型在 wire 上 `CODEC_ID = 2`（`CodecIds.PROTOBUF`）。同 family 多 type 通过订阅 type 派发，不冲突；详见 [`docs/aeron协议说明.md`](aeron协议说明.md) §4.1 与 `Codec.java` javadoc。

#### 2.6.5 lite runtime 支持

如果业务 `.proto` 用 `option optimize_for = LITE_RUNTIME;` 生成（Android / 极简场景），`T.parser()` 反射可能不可用，需走 builder 显式注入：

```java
ProtobufCodec<LiteMsg> codec = ProtobufCodec.builder(LiteMsg.class)
        .parser(LiteMsg.parser())     // 显式拿 parser 引用
        .build();
```

#### 2.6.6 extension（proto2 风格）

如果业务 `.proto` 用 extensions，需要传 `ExtensionRegistryLite`：

```java
ExtensionRegistryLite reg = ExtensionRegistryLite.newInstance();
MyExtensions.registerAllExtensions(reg);

ProtobufCodec<MsgWithExt> codec = ProtobufCodec.builder(MsgWithExt.class)
        .extensionRegistry(reg)
        .build();
```

否则未知 extension 字节会被当作 unknown fields 丢弃。

#### 2.6.7 与压缩的组合

Protobuf wire 已经是紧凑二进制，**短消息（< 256 B）通常不值得再压缩**（压缩头开销 > 收益）。> 1 KB 的 protobuf 大消息（如带大量 repeated）可叠加 LZ4 / ZSTD：

```java
AeronProducer producer = AeronProducer.builder()
        .driver(driver)
        .codec(new ProtobufCodec<>(BigReport.class))
        .compression(Lz4Compression.INSTANCE)   // 在 builder 上开启，对该 producer 的所有消息生效
        .build();
```

压缩是 producer 级配置，`send` 没有按条指定压缩算法的重载。Spring Boot 下声明 `@Bean CompressionCodec` 即可。详见 [`Aeron 组件使用手册.md`](Aeron%20组件使用手册.md) §12 / §17.8。

### 2.7 Protobuf 跨语言对齐

> 本节是面向**跨语言 SDK 实现者**（Go / C++ / .NET / Rust SDK 开发者）和**业务方多语言部署**的工程对齐手册。配套阅读 [`docs/跨语言互通指南.md`](跨语言互通指南.md) §3.5。

#### 2.7.1 wire 字节布局

```
+-------------------------+-------------------+---------------------------------------+
| broadcast frame (40 B)  | topic (1..255 B)  | PAYLOAD = standard protobuf wire bytes |
+-------------------------+-------------------+---------------------------------------+
                                              |<--- frame.PAYLOAD_LEN bytes  ------->|
```

protobuf wire format 由 [protobuf 官方 spec](https://protobuf.dev/programming-guides/encoding/) 标准化：tag (字段号 << 3 | wire type) + value 字节，递归编码到 message 末尾。本 SDK 在 frame `PAYLOAD` 部分原样写入 `value.toByteArray()` 的输出，跨语言对端原样喂给 protobuf 解析器即可。

#### 2.7.2 protoc 版本兼容矩阵

protobuf wire format 本身**长期稳定**（proto2 / proto3 spec 已固定多年）；但 protoc 工具版本会影响 codegen 出来的 Java / Go / C++ 代码细节（如 unknown fields 处理、生成的 builder 接口等）。

| 语言 | 运行时库 | 推荐版本 | 备注 |
|---|---|---|---|
| **Java** | `com.google.protobuf:protobuf-java` | **3.25.5**（本 SDK 当前对齐版本，见 `gradle/libs.versions.toml`） | protoc 3.25.x codegen，jar runtime 1.x 与 wire 兼容性强 |
| **Go** | `google.golang.org/protobuf`（new API）| v1.34+ | **不要用** `github.com/golang/protobuf`（old API，已 deprecated 多年）|
| **C++** | `libprotobuf` | 3.25.x | 与 Java protoc 同 major 版本 |
| **Python** | `protobuf` PyPI | 4.25+ | protoc Python target |
| **C#** / .NET | `Google.Protobuf` NuGet | 3.25+ | — |
| **Rust** | `prost` 或 `protobuf` crate | prost 0.13+ | prost 是社区主流；`rust-protobuf` 是另一选择 |

**对齐策略**：

1. 在公司 `proto-schemas` repo 的 `build.gradle` 里**显式锁定 protoc 版本**（`protobuf-gradle-plugin` 的 `protoc { artifact = 'com.google.protobuf:protoc:3.25.5' }`），随业务 schema 一起 commit
2. 跨语言对端用对应版本的 protoc：
   - Go：`go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.34.0`
   - Rust：`prost-build` 跟随 prost crate 版本
   - C++：与 Java 端 protoc 同版本
3. 每次升级 protoc 主版本，**跨语言双端必须同步升级**；过 [`docs/跨语言互通指南.md`](跨语言互通指南.md) §1 黄金 verify 路径第 6 步（Protobuf 多 type 派发）作为回归

#### 2.7.3 .proto 文件双端共享（强制契约）

跨语言互通的**第一红线**：**所有语言端必须用同一份 `.proto` 文件**（同 git tag）。常见做法：

| 模式 | 优点 | 缺点 |
|---|---|---|
| **独立 schema repo + git submodule** | 历史清晰，可独立 release | 业务 repo 每次升级需 update submodule |
| **独立 schema repo + 产物分发**（Maven jar / Go module artifact / npm package / PyPI wheel） | 业务 repo 用包管理器统一引入，无 git 操作 | 各语言生态都要发包；release 流程复杂 |
| **拷贝 .proto 到每个业务 repo** | 启动简单 | ❌ **不推荐**：drift 是必然的，跨语言互通失败时无法追溯 |

**强烈建议**：选模式 1 或 2，**绝不**选模式 3。

#### 2.7.4 同 codec 家族多业务 type 派发（P0 警告，再次强调）

跨语言 SDK 实现端**最容易踩的 P0 坑**：

| 错误实现 | 现象 |
|---|---|
| 用 wire `CODEC_ID` 当 codec 派发主键，注册成 `codecRegistry.byId[2] = OrderCodec`，第二次 `register(TradeCodec)` 把第一次覆盖 | 同时注册 `OrderProto` 和 `TradeProto` 两个 Protobuf codec 时，只有最后注册的 type 能收到，其他全静默丢失 |

**正确做法**（与 Java 端一致）：

- consumer 端 codec 派发主键用 **订阅时声明的业务 type**（Java 端 `Class<T>` / Go 端 `reflect.Type` / C++ 端模板参数 / Rust 端 `TypeId`）
- wire `CODEC_ID = 2` 仅做 cross check：consumer 拿到的 codec instance 的 `codecId()` 必须等于 2，否则 producer / consumer codec 配对错误 → 丢消息 + `metrics.onError`

#### 2.7.5 Go 端使用示意（伪代码）

假设业务 schema `quote.proto`（与 §2.2 一致）通过 `protoc-gen-go` 生成到 `gen/go/marketdata` 包：

```go
import (
    "reflect"
    "google.golang.org/protobuf/proto"

    "github.com/your-company/proto-schemas/gen/go/marketdata"
    "github.com/your-company/aeron-broadcast-go/codec"     // 跨语言 SDK 框架（待实现）
)

// Step 1: 注册 Protobuf codec（每个 message type 一个独立实例）
quoteCodec := codec.Protobuf[*marketdata.QuoteProto]{
    NewMessage: func() *marketdata.QuoteProto { return &marketdata.QuoteProto{} },
}
tradeCodec := codec.Protobuf[*marketdata.TradeProto]{
    NewMessage: func() *marketdata.TradeProto { return &marketdata.TradeProto{} },
}

producer.Codec(quoteCodec)
producer.Codec(tradeCodec)

// Step 2: 发送
producer.Send("md.l1.aapl", &marketdata.QuoteProto{
    Symbol: "AAPL", Price: 18742, Qty: 100,
})

// Step 3: 反向 — Java 发，Go 收
consumer.Subscribe("md.l1.aapl",
    reflect.TypeOf((*marketdata.QuoteProto)(nil)),
    func(q *marketdata.QuoteProto, ctx Context) {
        fmt.Printf("%s %d %d\n", q.Symbol, q.Price, q.Qty)
    })
```

跨语言 SDK 实现要点：

1. `codec.Protobuf[*T]` 的 encode 用 `proto.Marshal(value)` 输出**标准 protobuf wire bytes**，与 Java 端 `MessageLite.toByteArray()` 字节完全一致
2. decode 走 `proto.Unmarshal(payload, newMsg)` 即可
3. **codecId 必须返回 `2`**（`PROTOBUF`），与 Java 端 `CodecIds.PROTOBUF` 对齐
4. type registry 必须按业务 type（`reflect.Type` of `*marketdata.QuoteProto`）派发，不是按 wire `CODEC_ID`

> Go SDK 接口尚未实现（见仓库根 README "跨语言 SDK 路线图"）。这里仅展示 wire 兼容性目标，真正 API 名称以 Go SDK 实施时为准。

#### 2.7.6 跨语言互通 verify 清单

按顺序通过即认为 Protobuf 跨语言互通到位：

| # | 测试 | 期望 |
|---|---|---|
| 1 | 黄金 hex 文件 `docs/wire-samples/pb-stringvalue-alice.hex`：Java 端导出 `StringValue("alice")` | Go 端用 `well-known-types/wrapperspb` 解出等值 `*wrapperspb.StringValue{Value:"alice"}` |
| 2 | 黄金 hex 文件 `docs/wire-samples/pb-int64value-30.hex`：Java 端导出 `Int64Value(30)` | Go 端解出等值 `*wrapperspb.Int64Value{Value:30}` |
| 3 | 反向：Go 端编同样 `StringValue("alice")` | wire 字节 bit-for-bit 等于黄金 hex 文件 |
| 4 | 双向业务 `.proto`（如 `QuoteProto`）通过 IPC + RAW transport 互通 | Java prod → Go cons + Go prod → Java cons 都正确 |
| 5 | **同 transport 同时注册 `QuoteProto` + `TradeProto` 各发一条** | 两端按订阅 type 正确分发，不串 handler（验证 §2.7.4）|
| 6 | 加新字段（`.proto` v0 → v1）后老 consumer 兼容性 | 老 consumer 收到新 wire 把新字段当 unknown 字段（按 `optimize_for` 设置或丢或保留）|
| 7 | 双向 LZ4 + Protobuf 大消息（≥10KB） | 验证压缩 wire 约定 + Protobuf 字节互通 |

### 2.8 常见 FAQ

**Q1. 我已经在用 gRPC，可以复用 gRPC 的 `.proto` 文件吗？**

A: 可以。本 SDK 的 `ProtobufCodec` 只关心 `MessageLite` 接口（gRPC 也是基于这套），同一份 `.proto` 同时用于 gRPC RPC 和本广播 SDK 完全没问题。但 **gRPC 自身的 `service` / `rpc` 定义本 SDK 不解读**（本 SDK 是 broadcast 不是 RPC）。

**Q2. 一个 producer 实例能同时发 Protobuf 和 SBE 吗？**

A: 可以。注册多种 codec 即可，发送时按 `payload.getClass()` 自动派发：

```java
AeronProducer producer = AeronProducer.builder()
    .driver(dm)
    .codec(ProtobufCodec.forType(OrderProto.class))       // wire CODEC_ID=2
    .codec(SbeCodec.fixedLength(Quote.class, 28, ...))    // wire CODEC_ID=1
    .build();

producer.send("orders", new OrderProto.Builder()...);    // Protobuf 路径
producer.send("md.quote.aapl", new Quote("AAPL", ...));  // SBE 路径
```

**Q3. Consumer 同一 topic 能同时订阅两个不同 type 吗？**

A: ❌ 不能。同一个 consumer 实例上一个 `topic` 只能绑一个 `payloadType`（订阅表 `sharedSubs` 跨所有 partition 共享一份）。多 type 共享同一 topic 时，业务方需用 `oneof` envelope（见 §2.4.4）；或者把不同 type 拆到不同 topic（推荐）。

**Q4. Protobuf wire 兼容 SnappyProtoStream / proto-over-X 这些第三方变种吗？**

A: 不兼容。本 SDK 严格按 protobuf 官方 wire format，不识别任何第三方 framing（如 length-prefix delimited、newline delimited）。如果你有 length-prefix 的 wire 字节，先剥掉 prefix 再送进本 SDK。

**Q5. 跨语言对端能用 protobuf 1.x 老 wire 吗？**

A: protobuf wire 自 proto1（已 EOL）→ proto2 → proto3 的字节兼容性极强，新 parser 能解所有旧 wire；但**不建议**生产用 proto1。本 SDK 当前 protobuf-java 3.25.5 既兼容 proto2 又兼容 proto3 wire。

**Q6. 字段命名约定（snake_case vs camelCase）会影响跨语言互通吗？**

A: ❌ 不会。protobuf wire 上只有字段号，**没有字段名**。`.proto` 里写 `int32 user_age = 1;` 还是 `int32 userAge = 1;` 对 wire 字节无影响；只是生成的 Java 端 getter 是 `getUserAge()` / Go 端是 `UserAge` 字段。**字段名只影响业务代码，不影响互通**。

**Q7. 我的业务消息很短（< 50 B），Protobuf vs SBE 性能差距实测多大？**

A: 微基准实测（IPC + 单线程）：

- Protobuf encode: ~180 ns / decode: ~220 ns / 单条总开销 ~500 ns（含 frame header）
- SBE fixedLength encode: ~30 ns / decode: ~40 ns / 单条总开销 ~120 ns（含 frame header）
- 差距：~4x。如果你的吞吐目标 < 100 万 msg/sec/core，**Protobuf 完全够用**；> 500 万 msg/sec/core 的极限低延迟（如 tick-by-tick 行情）才需要切 SBE。

---

## 3. Fory 接入

`aeron-codec-fory` 模块提供 [Apache Fory](https://fory.apache.org/) 高性能多语言序列化的 SDK 端 codec 实现。模块只依赖 `org.apache.fory:fory-core`，**0 Spring 依赖**，可以独立用在任何 Java 项目里。

> 如果业务侧已经有 Fory 的静态封装层（例如 Spring Boot 自动装配 + 注解扫描自动注册类的内部组件），可以参考 §3.6 的「桥接外部 Fory 封装」章节，30 行胶水代码就能复用既有注册中心。

### 3.1 引入依赖

`build.gradle`：

```groovy
dependencies {
    implementation 'com.mcst:aeron-codec-fory'
    // 同时已经引入 aeron-producer / aeron-consumer / aeron-driver
}
```

传递依赖 `org.apache.fory:fory-core:0.15.0`（版本号见本 SDK `gradle/libs.versions.toml` 的 `fory` 条目，可被业务方 `dependencyManagement` 覆盖）。

JVM 启动参数沿用本 SDK 标准 `--add-opens` 列表，Fory 自身不需要额外开关。

### 3.2 三种基本用法

#### 3.2.1 单类型（JAVA 模式，最简）

```java
public class Trade {
    public String symbol;
    public int qty;
    public double price;
    public List<String> tags;
    public Trade() {}                            // Fory 反射实例化需要无参构造
    public Trade(String s, int q, double p, List<String> t) {
        symbol = s; qty = q; price = p; tags = t;
    }
}

// Producer / Consumer 两端构同款 codec：
ForyCodec<Trade> codec = ForyCodec.forType(Trade.class);

AeronProducer producer = AeronProducer.builder().driver(dm).codec(codec).build();
AeronConsumer consumer = AeronConsumer.builder().driver(dm).codec(codec).build();
```

#### 3.2.2 嵌套自定义类型（JAVA 模式，多注册）

主类型 `Bundle` 字段里嵌套 `Order` POJO 时，必须**显式 register 嵌套类型**：

```java
ForyCodec<Bundle> codec = ForyCodec.builder(Bundle.class)
        .register(Order.class)         // 嵌套自定义 POJO 都要 register
        .register(Address.class)
        .build();
```

> **producer / consumer 端必须按完全相同的顺序 register 完全相同的一组类**。JAVA 模式下 Fory 按注册顺序分配内部 typeId，顺序不一致会导致 wire 不兼容、反序列化抛异常。

JDK 标准类型（`String` / `Integer` / `Double` / `List` / `Map` / `ArrayList` / …）由 Fory 自动注册，业务方不用管。

#### 3.2.3 跨语言（XLANG 模式）

```java
ForyCodec<Order> codec = ForyCodec.builder(Order.class)
        .crossLanguage(true)
        .typeId(1001)                                 // 主类型必须有稳定 typeId（推荐 ≥ 100）
        .register(OrderItem.class, 1002)              // 每个嵌套类型也都要有稳定 typeId
        .register(Address.class, "company.Address")   // 也支持 typeName
        .build();
```

XLANG 模式下：

- **每个 register 必须显式提供 `typeId` 或 `typeName`**，否则 `build()` 直接抛 `IllegalStateException`（这是为防止跨语言对端找不到类的常见踩坑）
- typeId / typeName **必须在所有语言端保持一致**
- 注册顺序无关（跨语言通过 typeId 寻址，不依赖顺序）
- wire 字节符合 [Apache Fory XLANG protocol](https://fory.apache.org/docs/guide/xlang/)，可被 Python / Go / Rust / C++ 等 Fory 实现反序列化

> **typeId 范围建议**：Apache Fory 把 typeId `0 ~ 32` 留给内置类型（`Types.NONE+1` 之后是 Java 原生内置类型），用户自定义 typeId 推荐 **≥ 100** 起，避免被未来的 Fory 内置 typeId 范围扩张撞到。本 SDK 不强制校验，由 Fory 自身在 `register(Class, int)` 撞内置 typeId 时报错。

### 3.3 API 速查

| 入口 | 适用 | 说明 |
|---|---|---|
| `ForyCodec.forType(Trade.class)` | JAVA 模式 + 仅一个主类型 | 等价 `builder(...).build()` |
| `ForyCodec.builder(Trade.class)` | 所有场景 | 链式配置 |
| `.crossLanguage(boolean)` | Builder | 默认 false（JAVA 模式） |
| `.typeId(int)` | Builder | 给主类型加 typeId，XLANG 模式必填一个 |
| `.typeName(String)` | Builder | 给主类型加 typeName，与 typeId 二选一 |
| `.register(Class)` | Builder | 追加关联类型；XLANG 模式下 `build()` 会拒绝（缺 typeId/typeName） |
| `.register(Class, int)` | Builder | 追加关联类型 + typeId（推荐 ≥ 100，避开 Fory 内置保留区） |
| `.register(Class, String)` | Builder | 追加关联类型 + typeName |
| `.build()` | Builder | XLANG 模式下校验所有类已有 typeId/typeName，缺则抛 `IllegalStateException` 并提示该用哪个重载 |
| `.codecId()` → `byte` | runtime | 始终返回 `CodecIds.FORY` (= 5) |
| `.type()` → `Class<T>` | runtime | 主业务类型 |
| `.isCrossLanguage()` → `boolean` | runtime | 当前是否 XLANG 模式（排错用） |

### 3.4 关键设计与注意事项

#### 3.4.1 线程模型

`ForyCodec` 内部用 `ThreadSafeFory`（Fory 实例池），同一个 codec instance 可被多线程并发 encode/decode：

- producer 端虽然 single-writer，但同进程多 producer 共享同一个 codec 没问题
- consumer 端 RING_BUFFER_POOL 多 worker 并发 decode 也安全

#### 3.4.2 性能特征

- Apache Fory Java 端 `serialize(obj)` 始终返回 `byte[]`，**没有 zero-copy 到外部 buffer 的公开 API**
- 本 codec 遵循 SDK 内 `Codec` SPI 的双调用契约（`encodedLength → tryClaim → encode`），与 `JsonCodec` / `SbeCodec.varLength` 同款**双重序列化**模式，编解码 CPU 是 Fory baseline 的 ~2x；但 Fory 自身在常见 POJO benchmark 下显著快于 Jackson JSON，实际编解码延迟仍远小于 JsonCodec
- 首次 encode 会触发 Fory JIT 生成 codec class（demo 实测百毫秒级），稳态后单条 codec 编解码延迟在亚微秒级
- 注意：端到端 wall-clock latency 还取决于 Aeron poll / IPC ring buffer 调度，不等同于 codec 延迟（demo 输出的 `latency=N us` 是端到端值）

#### 3.4.3 主类型必须有无参构造

Fory 反序列化通过反射实例化对象，POJO **必须**有 `public` 或 `package-private` 的无参构造函数（Record / 不可变类参考 Fory 官方 [Java 高级用法](https://fory.apache.org/docs/guide/java/)）。

#### 3.4.4 wire 跨语言警告

- wire `CODEC_ID` 在 JAVA / XLANG 两种模式下都是 5，**仅靠帧头无法区分模式**
- 跨语言互通**只能用 XLANG 模式**；JAVA 模式 wire 只能 Java 反序列化
- 详见 [`跨语言互通指南.md`](跨语言互通指南.md) §3.7

#### 3.4.5 producer / consumer 配对

- 两端 codec 模式（JAVA / XLANG）必须一致
- JAVA 模式下两端 register 顺序必须一致
- XLANG 模式下两端 typeId / typeName 必须一致
- 不一致时 wire `CODEC_ID` cross check 不会拦截（都是 FORY），会在 Fory 内部反序列化时抛 `CodecException`

### 3.5 完整可跑示例

仓库内 `aeron-examples/src/main/java/com/mcst/aeron/examples/ForyIpcDemo.java`：

```bash
./gradlew :aeron-examples:runForyDemo
```

输出示例：

```
recv  symbol=AAPL qty=100 price=187.42 tags=[nyse, vip]  latency=5000 us
recv  symbol=MSFT qty=50 price=412.10 tags=[nasdaq]  latency=11000 us
recv  symbol=BABA qty=200 price=78.55 tags=[nyse, adr]  latency=11000 us
```

> 上面的 `latency=N us` 是 **端到端 wall-clock** 时延（producer.send 到 consumer.handler 回调），受 Aeron poll / IPC ring buffer 调度影响，**不是纯 codec 编解码延迟**（后者在亚微秒级）。首条偏高还叠加了 Fory JIT 首次生成 codec class 的开销（实测约百毫秒级）。

### 3.6 桥接外部 Fory 封装（可选）

如果业务侧已经有一套 Fory 的静态封装层（典型场景：Spring Boot 自动装配 + `@SerializableClass` 注解扫描的内部组件，对外暴露 `XxxSerializer.serialize(obj)` / `XxxSerializer.deserialize(bytes, type)` 之类的静态方法），不想再通过本 SDK 的 `ForyCodec.Builder` 重复注册一遍，可以写一个适配 `Codec<T>` 的小桥来复用既有注册中心：

```java
package com.your.app.codec;

import com.mcst.aeron.common.codec.Codec;
import com.mcst.aeron.common.codec.CodecIds;
import com.mcst.aeron.common.exception.CodecException;
import com.your.company.serializer.fory.ForySerializer;   // 业务侧既有封装
import org.agrona.DirectBuffer;
import org.agrona.MutableDirectBuffer;

public final class ExternalForyAdapterCodec<T> implements Codec<T> {
    private final Class<T> type;
    public ExternalForyAdapterCodec(Class<T> type) { this.type = type; }

    @Override public byte codecId() { return CodecIds.FORY; }
    @Override public Class<T> type() { return type; }

    @Override public int encodedLength(T value) {
        return ForySerializer.serialize(value).length;
    }
    @Override public int encode(T value, MutableDirectBuffer buf, int off) {
        byte[] bytes = ForySerializer.serialize(value);
        if (buf.capacity() - off < bytes.length) {
            throw new CodecException("buffer too small for " + type.getName());
        }
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

注意：

- 这条桥**会把外部封装的依赖（含 Spring 等）引入到你的应用**，不影响本 SDK 自身的 0 Spring 性质
- 桥过来后 `ForyCodec`（本 SDK 提供）与 `ExternalForyAdapterCodec`（业务自写）的 wire 互通**取决于外部封装内部用的是 `Language.JAVA` 还是 `Language.XLANG` 模式**，必须先与该封装的维护方对齐
- 桥过来后默认 wire `CODEC_ID = 5`，与本 SDK `ForyCodec` 共占一个 wire 家族，consumer 端按业务 `Class<T>` 派发（同 PROTOBUF/SBE/FORY 多 type 派发逻辑），不冲突

---

## 4. 配套文档

- [`aeron协议说明.md`](aeron协议说明.md)：wire 帧格式、Codec ID 表（SBE = 1 / PROTOBUF = 2 / FORY = 5）、§4.1 多 codec 家族 type 派发原理
- [`跨语言互通指南.md`](跨语言互通指南.md)：
  - §1 黄金 verify 路径（第 5 步 SBE Quote / 第 6 步 Protobuf 多 type 派发）
  - §3.5 PROTOBUF / §3.6 SBE / §3.7 FORY 跨语言对齐契约
  - §8 常见坑（Protobuf .proto 漂移、byId 派发陷阱、SBE byteOrder / messageHeader / sbe-tool 版本差异）
- [`Aeron 组件使用手册.md`](Aeron%20组件使用手册.md)：producer / consumer 完整用法（§9 发送、§10 接收、§12 压缩）
- [`wire-samples/`](wire-samples/)：黄金 hex 测试向量（`sbe-quote-fixed.hex` / `pb-stringvalue-alice.hex` / …）
- [`跨语言互通指南.md`](跨语言互通指南.md) §12：端内错误码标准化
- 参考实现：
  - `aeron-codec-sbe/src/main/java/com/mcst/aeron/codec/sbe/SbeCodec.java`
  - `aeron-codec-protobuf/src/main/java/com/mcst/aeron/codec/protobuf/ProtobufCodec.java`
  - `aeron-codec-fory/`（`ForyCodec`）
- 示例：
  - `aeron-examples/src/main/java/com/mcst/aeron/examples/UdpFanOut.java`
  - `aeron-examples/src/main/java/com/mcst/aeron/examples/ForyIpcDemo.java`
- [Apache Fory 官方文档](https://fory.apache.org/docs/)：Fory 自身的高级用法（自定义 serializer、schema 演进、GraalVM 等）
