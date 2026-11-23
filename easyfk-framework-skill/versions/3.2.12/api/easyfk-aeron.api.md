# easyfk-aeron API 签名速查（easyfk 3.2.12）

> 坐标：`com.mcst:aeron-common、aeron-producer、aeron-consumer、aeron-store、aeron-chronicle、aeron-codec-*、aeron-compression-*、aeron-metrics-micrometer、aeron-spring-boot-starter`　源码：`easyfk-aeron/aeron-common`、`easyfk-aeron/aeron-driver`、`easyfk-aeron/aeron-producer`、`easyfk-aeron/aeron-producer-outbox`、`easyfk-aeron/aeron-consumer`、`easyfk-aeron/aeron-store`、`easyfk-aeron/aeron-chronicle`、`easyfk-aeron/aeron-codec-fory`、`easyfk-aeron/aeron-codec-json`、`easyfk-aeron/aeron-codec-protobuf`、`easyfk-aeron/aeron-codec-sbe`、`easyfk-aeron/aeron-compression-lz4`、`easyfk-aeron/aeron-compression-zstd`、`easyfk-aeron/aeron-metrics-micrometer`、`easyfk-aeron/aeron-spring-boot-starter`
> 由 `scripts/gen-api.py` 从 143 个源文件自动提取，共 130 个类型、609 个方法/构造器、119 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-aeron-skill.md](../modules/easyfk-aeron-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 配置项（@ConfigurationProperties）

### `easyfk.config.aeron` ← AeronProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `enabled` | `boolean` | `true` | 全局开关；false 不装配任何 Bean（用于排除特定场景）。 |
| `default-driver` | `String` | `—` | 多 driver 场景必填：该 driver 的 producer / consumer / driverManager / codecRegistry bean 额外注册不带后缀的 alias（aeronProduce… |
| `driver` | `DriverProperties` | `—` | 单 driver 简化路径。与 drivers 互斥。 内部会被 normalize 成 drivers.default 统一处理。 |
| `drivers` | `Map<String, DriverProperties>` | `new LinkedHashMap<>()` | 多 driver 完整路径，key = driver name。name 须匹配 [a-zA-Z][a-zA-Z0-9_-]{0,31}. |
| `codecs` | `List<CodecProperties>` | `new ArrayList<>()` | yaml 路径注册的 codec 列表（与 @Bean Codec 自动扫描合并）。 |
| `codec` | `CodecDefaultProperties` | `new CodecDefaultProperties()` | 默认 codec 兜底配置。easyfk.config.aeron.codec.default-codec=fory（默认）时未注册的 POJO 类型自动用 ForyCodec… |
| `shutdown` | `ShutdownProperties` | `new ShutdownProperties()` | 关闭行为配置。 |
| `producer` | `ProducerGlobalProperties` | `new ProducerGlobalProperties()` | 全局 producer 子系统开关。easyfk.config.aeron.producer.enabled=false 时所有 driver 的 AeronProducer bean 都不装配；适合"纯订阅服务"… |
| `consumer` | `ConsumerGlobalProperties` | `new ConsumerGlobalProperties()` | 全局 consumer 子系统开关。easyfk.config.aeron.consumer.enabled=false 时所有 driver 的 AeronConsumer bean 都不装配；适合"纯发送服务"… |


## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `aeron-chronicle` | `com.mcst.aeron.chronicle.spring.AeronChronicleAutoConfiguration` |
| `aeron-spring-boot-starter` | `com.mcst.aeron.spring.autoconfig.AeronAutoConfiguration` |

## 类型索引

- `com.mcst.aeron.chronicle`：[AeronStateBinding](#aeronstatebinding)、[StateMaterializer](#statematerializer)、[StateStoreMetrics](#statestoremetrics)
- `com.mcst.aeron.chronicle.spring`：[AeronChronicleAutoConfiguration](#aeronchronicleautoconfiguration)、[AeronChronicleBindingSpec](#aeronchroniclebindingspec)、[AeronChronicleLifecycle](#aeronchroniclelifecycle)
- `com.mcst.aeron.codec.fory`：[ForyCodec](#forycodec)
- `com.mcst.aeron.codec.json`：[JsonCodec](#jsoncodec)
- `com.mcst.aeron.codec.protobuf`：[ProtobufCodec](#protobufcodec)
- `com.mcst.aeron.codec.sbe`：[SbeCodec](#sbecodec)、[SbeDecoderOp](#sbedecoderop)、[SbeEncoderOp](#sbeencoderop)
- `com.mcst.aeron.common.codec`：[BuiltinCodecProvider](#builtincodecprovider)、[Codec](#codec)、[CodecIds](#codecids)、[CodecProvider](#codecprovider)、[CodecRegistry](#codecregistry)
    [RawBytesCodec](#rawbytescodec)、[StringCodec](#stringcodec)
- `com.mcst.aeron.common.compression`：[CompressionCodec](#compressioncodec)、[CompressionIds](#compressionids)、[CompressionRegistry](#compressionregistry)、[DeflateCompression](#deflatecompression)
- `com.mcst.aeron.common.config`：[BackpressureStrategyType](#backpressurestrategytype)、[ChannelSpec](#channelspec)、[ConsumerConfig](#consumerconfig)、[DeliveryMode](#deliverymode)、[IdleStrategies](#idlestrategies)
    [IdleStrategyType](#idlestrategytype)、[ProducerConfig](#producerconfig)
- `com.mcst.aeron.common.exception`：[AeronMqException](#aeronmqexception)、[CodecException](#codecexception)、[CompressionException](#compressionexception)、[FrameDecodeException](#framedecodeexception)
- `com.mcst.aeron.common.frame`：[FrameDecoder](#framedecoder)、[FrameEncoder](#frameencoder)、[FrameHeader](#frameheader)、[FrameProtocol](#frameprotocol)
- `com.mcst.aeron.common.metrics`：[ConsumerMetrics](#consumermetrics)、[InMemoryConsumerMetrics](#inmemoryconsumermetrics)、[InMemoryProducerMetrics](#inmemoryproducermetrics)、[ProducerMetrics](#producermetrics)
- `com.mcst.aeron.common.partition`：[Cluster](#cluster)、[NoKeyStrategy](#nokeystrategy)、[PartitionLayout](#partitionlayout)、[Partitioner](#partitioner)
- `com.mcst.aeron.common.time`：[WallClock](#wallclock)
- `com.mcst.aeron.common.topic`：[Topic](#topic)
- `com.mcst.aeron.compression.lz4`：[Lz4Compression](#lz4compression)
- `com.mcst.aeron.compression.zstd`：[ZstdCompression](#zstdcompression)
- `com.mcst.aeron.consumer`：[AeronConsumer](#aeronconsumer)、[Consumer](#consumer)、[MessageContext](#messagecontext)、[MessageHandler](#messagehandler)、[MessageIdDeduper](#messageiddeduper)
- `com.mcst.aeron.consumer.internal`：[Dispatcher](#dispatcher)、[InlineDispatcher](#inlinedispatcher)、[PollAgent](#pollagent)、[RingBufferPoolDispatcher](#ringbufferpooldispatcher)、[TopicSubscription](#topicsubscription)
- `com.mcst.aeron.driver`：[DriverConfig](#driverconfig)、[DriverManager](#drivermanager)
- `com.mcst.aeron.metrics.micrometer`：[MicrometerConsumerMetrics](#micrometerconsumermetrics)、[MicrometerOutboxMetrics](#micrometeroutboxmetrics)、[MicrometerProducerMetrics](#micrometerproducermetrics)
- `com.mcst.aeron.producer`：[AeronProducer](#aeronproducer)、[BackpressureException](#backpressureexception)、[EncodedFrameSender](#encodedframesender)、[MessageIdGenerator](#messageidgenerator)、[Producer](#producer)
    [PublicationTerminalException](#publicationterminalexception)
- `com.mcst.aeron.producer.internal`：[BackpressureHandler](#backpressurehandler)、[SnowflakeMessageIdGenerator](#snowflakemessageidgenerator)
- `com.mcst.aeron.producer.outbox`：[FsyncPolicy](#fsyncpolicy)、[OutboxConfig](#outboxconfig)、[OutboxException](#outboxexception)、[OutboxMetrics](#outboxmetrics)、[OutboxProducer](#outboxproducer)
    [OutboxStoreType](#outboxstoretype)
- `com.mcst.aeron.producer.outbox.internal`：[KeyBytes](#keybytes)、[ProducerRecordSender](#producerrecordsender)、[WalCodec](#walcodec)、[WalRecordView](#walrecordview)
- `com.mcst.aeron.spring.annotation`：[AeronConsumerRef](#aeronconsumerref)、[AeronDriver](#aerondriver)、[AeronProducerRef](#aeronproducerref)、[AeronTopic](#aerontopic)
- `com.mcst.aeron.spring.autoconfig`：[AeronAutoConfiguration](#aeronautoconfiguration)、[AeronCodecAutoConfiguration](#aeroncodecautoconfiguration)、[AeronConsumerAutoConfiguration](#aeronconsumerautoconfiguration)、[AeronConsumerFactoryBean](#aeronconsumerfactorybean)、[AeronDriverAutoConfiguration](#aerondriverautoconfiguration)
    [AeronHealthAutoConfiguration](#aeronhealthautoconfiguration)、[AeronMetricsAutoConfiguration](#aeronmetricsautoconfiguration)、[AeronProducerAutoConfiguration](#aeronproducerautoconfiguration)、[AeronProducerFactoryBean](#aeronproducerfactorybean)、[CodecRegistryFactoryBean](#codecregistryfactorybean)
- `com.mcst.aeron.spring.properties`：[AeronProperties](#aeronproperties)、[BackpressureProperties](#backpressureproperties)、[CodecDefaultProperties](#codecdefaultproperties)、[CodecProperties](#codecproperties)、[ConsumerGlobalProperties](#consumerglobalproperties)
    [ConsumerProperties](#consumerproperties)、[DriverProperties](#driverproperties)、[OutboxProperties](#outboxproperties)、[ProducerGlobalProperties](#producerglobalproperties)、[ProducerProperties](#producerproperties)
    [ShutdownProperties](#shutdownproperties)
- `com.mcst.aeron.spring.runtime`：[AeronHealthIndicator](#aeronhealthindicator)、[AeronLifecycle](#aeronlifecycle)、[AeronTopicBeanPostProcessor](#aerontopicbeanpostprocessor)、[SpringBootVersionCheck](#springbootversioncheck)、[TopicMethodBinder](#topicmethodbinder)
- `com.mcst.aeron.spring.support`：[ChannelUriParser](#channeluriparser)、[CodecFactoryResolver](#codecfactoryresolver)、[DefaultCodecFallback](#defaultcodecfallback)、[DriverNameValidator](#drivernamevalidator)
- `com.mcst.aeron.store`：[DurableLog](#durablelog)、[ForwardOutcome](#forwardoutcome)、[FsyncPolicy](#fsyncpolicy)、[RecordSender](#recordsender)、[StoreConfig](#storeconfig)
    [StoreException](#storeexception)、[StoreForwardQueue](#storeforwardqueue)、[StoreMetrics](#storemetrics)、[StoreType](#storetype)
- `com.mcst.aeron.store.internal`：[RecordForwarder](#recordforwarder)、[SegmentedLog](#segmentedlog)、[SingleFileLog](#singlefilelog)、[WalDirGuard](#waldirguard)

## 包 `com.mcst.aeron.chronicle`

### AeronStateBinding

`public final class AeronStateBinding<E, K, V>`　一行式绑定：topic 事件流 → StateMaterializer → 状态表。

**方法**

```java
String topic()
Class<E> eventType()
StateMaterializer<E, K, V> materializer()
static <E, K, V> Builder<E, K, V> builder()
```

#### AeronStateBinding.Builder

`public static final class Builder<E, K, V>`

**方法**

```java
Builder<E, K, V> consumer(Consumer consumer)
Builder<E, K, V> topic(String topic)
Builder<E, K, V> eventType(Class<E> eventType)
Builder<E, K, V> map(ConcurrentMap<K, V> map)
Builder<E, K, V> key(Function<E, K> keyFn)
Builder<E, K, V> value(Function<E, V> valueFn)
Builder<E, K, V> tombstoneWhen(Predicate<E> tombstoneFn)
Builder<E, K, V> versionedBy(ToLongFunction<V> versionFn)
Builder<E, K, V> metrics(StateStoreMetrics metrics)
AeronStateBinding<E, K, V> bind()  // 构建 materializer 并订阅到 consumer。
```

### StateMaterializer

`public final class StateMaterializer<E, K, V> implements MessageHandler<E>`　把订阅到的事件流物化成 KV 状态表（changelog → materialized view）。

**方法**

```java
void onMessage(E event, MessageContext ctx)
ConcurrentMap<K, V> map()  // 物化目标表（只读视角），方便绑定方暴露给查询侧。
static <E, K, V> Builder<E, K, V> builder()
```

#### StateMaterializer.Builder

`public static final class Builder<E, K, V>`

**方法**

```java
Builder<E, K, V> map(ConcurrentMap<K, V> map)  // 目标状态表。生产环境传 Chronicle Map（其实现了 ConcurrentMap）。
Builder<E, K, V> key(Function<E, K> keyFn)  // 从事件提取状态表 key。返回 null 时事件按畸形丢弃。
Builder<E, K, V> value(Function<E, V> valueFn)  // 从事件映射存储值。tombstone 事件不会调用。返回 null 时事件按畸形丢弃。
Builder<E, K, V> tombstoneWhen(Predicate<E> tombstoneFn)  // 可选：判定 delete 事件（如 e.op() == DELETE）。命中时从状态表移除 key。
Builder<E, K, V> versionedBy(ToLongFunction<V> versionFn)  // 可选：开启 last-write-wins。从存储值提取单调版本号（业务版本号 / 序列号 / 事件时间戳均可），仅当新值版本 &gt;= 现值版本才覆盖…
Builder<E, K, V> metrics(StateStoreMetrics metrics)
StateMaterializer<E, K, V> build()
```

### StateStoreMetrics

`public interface StateStoreMetrics`　状态物化指标回调。所有方法可能被 consumer 的 poll 线程或 dispatch worker 线程调用， 实现必须线程安全且不能抛异常、不能阻塞。

**方法**

```java
default void onUpsert(String topic)  // 一条事件成功 upsert 进状态表。
default void onDelete(String topic)  // 一条 tombstone 事件把 key 从状态表删除（key 原本不存在也计入）。
default void onStaleSkipped(String topic)  // 一条事件因版本号低于表内现值被跳过（LWW 防乱序回退）。
default void onMalformed(String topic)  // 一条事件因 key / value 提取结果为 null 等形态问题被丢弃。
static StateStoreMetrics noop()
```

## 包 `com.mcst.aeron.chronicle.spring`

### AeronChronicleAutoConfiguration

`public class AeronChronicleAutoConfiguration`　注解：`@Configuration` `@ConditionalOnClass({ChronicleMapManager.class, Consumer.class})` `@ConditionalOnBean(AeronChronicleBindingSpec.class)` `@ConditionalOnProperty(prefix = "easyfk.config.aeron.chronicle", name = "enabled", havingValue = "true", matchIfMissing = true)` `@AutoConfigureAfter(ChronicleMapAutoConfiguration.class)`　aeron-chronicle 自动装配：业务方注册了 AeronChronicleBindingSpec bean 时…

**方法**

```java
@Bean @ConditionalOnMissingBean AeronChronicleLifecycle aeronChronicleLifecycle()
```

### AeronChronicleBindingSpec

`public final class AeronChronicleBindingSpec<E, K, V>`　Spring 装配用的绑定描述：声明"哪个 topic 的事件物化到哪个 Chronicle Map"。

**方法**

```java
String topic()
Class<E> eventType()
String mapName()
Class<K> keyType()
Class<V> valueType()
Function<E, K> keyFn()
Function<E, V> valueFn()
Predicate<E> tombstoneFn()
ToLongFunction<V> versionFn()
StateStoreMetrics metrics()
boolean foryMarshaller()
Long maxEntries()
Double avgKeySize()
Double avgValueSize()
String filePath()
String driver()
String consumerBeanName()
static <E, K, V> Builder<E, K, V> builder()
```

#### AeronChronicleBindingSpec.Builder

`public static final class Builder<E, K, V>`

**方法**

```java
Builder<E, K, V> topic(String topic)
Builder<E, K, V> eventType(Class<E> eventType)
Builder<E, K, V> mapName(String mapName)
Builder<E, K, V> keyType(Class<K> keyType)
Builder<E, K, V> valueType(Class<V> valueType)
Builder<E, K, V> key(Function<E, K> keyFn)
Builder<E, K, V> value(Function<E, V> valueFn)
Builder<E, K, V> tombstoneWhen(Predicate<E> fn)
Builder<E, K, V> versionedBy(ToLongFunction<V> fn)
Builder<E, K, V> metrics(StateStoreMetrics metrics)
Builder<E, K, V> plainMarshaller()  // 不用 Fory Marshaller（值类型为 String / byte[] / 基本包装类等 Chronicle 原生支持类型时）。
Builder<E, K, V> mapParams(long maxEntries, double avgKeySize, double avgValueSize)  // 可选：map 不存在需要创建时的容量参数（建议优先用 YAML 预配置 map）。
Builder<E, K, V> filePath(String filePath)  // 可选：持久化文件路径；不设则用 chronicle-map 默认路径规则。必须与 mapParams 同时设置。
Builder<E, K, V> driver(String driver)  // 多 driver 时指定 driver 原始名（如 "ipc-a"），按 starter 命名约定解析 consumer bean。
Builder<E, K, V> consumerBeanName(String name)  // 直接点名 consumer bean，优先级高于 driver(String)。
AeronChronicleBindingSpec<E, K, V> build()
```

### AeronChronicleLifecycle

`public class AeronChronicleLifecycle implements SmartLifecycle, ApplicationContextAware`　启动期把所有 AeronChronicleBindingSpec bean 物化为实际绑定： 解析 / 创建 Chronicle Map → 选定 consumer → consumer.subscribe(topic…

**方法**

```java
void setApplicationContext(ApplicationContext applicationContext) throws BeansException
int getPhase()
@SuppressWarnings({"rawtypes", "unchecked"}) void start()
void stop()
boolean isRunning()
```

## 包 `com.mcst.aeron.codec.fory`

### ForyCodec

`public final class ForyCodec<T> implements Codec<T>`　基于 Apache Fory 的 codec，一个实例对应一种主业务类型 + 一组关联类型。

**方法**

```java
static <T> ForyCodec<T> forType(Class<T> type)  // JAVA 模式快捷入口，仅注册主类型一个 class。
static <T> Builder<T> builder(Class<T> type)
byte codecId()
Class<T> type()
boolean isCrossLanguage()  // 当前是否运行在 XLANG 模式，用于排查 wire 不互通时的 sanity check。
int encodedLength(T value)
int encode(T value, MutableDirectBuffer buffer, int offset)
T decode(DirectBuffer buffer, int offset, int length)
```

#### ForyCodec.Builder

`public static final class Builder<T>`

**方法**

```java
Builder<T> crossLanguage(boolean enabled)  // 切跨语言（XLANG）模式；默认 false（JAVA 模式）。
Builder<T> typeId(int id)  // 给主类型补一个稳定 typeId；XLANG 模式必填一种（typeId 或 typeName）。 JAVA 模式也可调用：让两端 register 顺序差异不再决定 wire 兼容性（按显式 typeId 寻址）…
Builder<T> typeName(String name)  // 给主类型补一个稳定 typeName；XLANG 模式必填一种（typeId 或 typeName）。 JAVA 模式同样可用，效果与 typeId(int) 类似（按名字而不是数字稳定寻址）。
Builder<T> register(Class<?> clazz)  // 追加一个关联类型（嵌套 POJO、集合元素类型等）。 JAVA 模式按注册顺序生成内部 typeId；XLANG 模式下若以此重载注册…
Builder<T> register(Class<?> clazz, int id)  // 追加一个关联类型并指定 typeId。
Builder<T> register(Class<?> clazz, String name)  // 追加一个关联类型并指定 typeName。
ForyCodec<T> build()
```

## 包 `com.mcst.aeron.codec.json`

### JsonCodec

`public final class JsonCodec<T> implements Codec<T>`　基于 Jackson 的 JSON codec，一个实例对应一个具体类型。

**构造器**

```java
JsonCodec(Class<T> type)
JsonCodec(Class<T> type, ObjectMapper mapper)
```

**方法**

```java
static <T> JsonCodec<T> forType(Class<T> type)
static <T> Builder<T> builder(Class<T> type)
byte codecId()
Class<T> type()
int encodedLength(T value)
int encode(T value, MutableDirectBuffer buffer, int offset)
T decode(DirectBuffer buffer, int offset, int length)
```

#### JsonCodec.Builder

`public static final class Builder<T>`

**方法**

```java
Builder<T> objectMapper(ObjectMapper mapper)
JsonCodec<T> build()
```

## 包 `com.mcst.aeron.codec.protobuf`

### ProtobufCodec

`public final class ProtobufCodec<T extends MessageLite> implements Codec<T>`　基于 protobuf-java 的 codec，一个实例对应一个具体的 MessageLite 类型。

**构造器**

```java
ProtobufCodec(Class<T> type)
ProtobufCodec(Class<T> type, ExtensionRegistryLite registry)
```

**方法**

```java
static <T extends MessageLite> ProtobufCodec<T> forType(Class<T> type)
static <T extends MessageLite> Builder<T> builder(Class<T> type)
byte codecId()
Class<T> type()
int encodedLength(T value)
int encode(T value, MutableDirectBuffer buffer, int offset)
T decode(DirectBuffer buffer, int offset, int length)
```

#### ProtobufCodec.Builder

`public static final class Builder<T extends MessageLite>`

**方法**

```java
Builder<T> parser(Parser<T> parser)  // 显式提供 parser，跳过 type.parser() 反射，可用于 lite runtime。
Builder<T> extensionRegistry(ExtensionRegistryLite registry)
ProtobufCodec<T> build()
```

## 包 `com.mcst.aeron.codec.sbe`

### SbeCodec

`public abstract class SbeCodec<T> implements Codec<T>`　把 sbe-tool 生成的 Encoder / Decoder 适配成本 SDK 的 Codec。

**方法**

```java
final byte codecId()
final Class<T> type()
static <T> SbeCodec<T> fixedLength(Class<T> type, int totalLength, SbeEncoderOp<T> encoder, SbeDecoderOp<T> decoder)  // 定长消息工厂。totalLength 一般写成 MessageHeaderEncoder.ENCODED_LENGTH + XxxEncoder.BLOCK_LENGTH。
static <T> SbeCodec<T> varLength(Class<T> type, ToIntFunction<T> maxLengthFn, SbeEncoderOp<T> encoder, SbeDecoderOp<T> decoder)  // 变长消息工厂。maxLengthFn 给本 codec 一个"消息总字节数的安全上界"， 用于 ThreadLocal scratch 预分配；上界算小了 framework 抛 CodecException…
```

### SbeDecoderOp

`public interface SbeDecoderOp<T>`　注解：`@FunctionalInterface`　业务方注入的 SBE 反序列化回调：从 buffer[offset..offset+length) 读完整一条 SBE 消息， 返回业务对象…

**方法**

```java
T decode(DirectBuffer buffer, int offset, int length)
```

### SbeEncoderOp

`public interface SbeEncoderOp<T>`　注解：`@FunctionalInterface`　业务方注入的 SBE 序列化回调：把 value 按 SBE wire 字节写到 buffer[offset..]…

**方法**

```java
int encode(T value, MutableDirectBuffer buffer, int offset)
```

## 包 `com.mcst.aeron.common.codec`

### BuiltinCodecProvider

`public final class BuiltinCodecProvider implements CodecProvider`　aeron-common 自带 codec。RawBytesCodec 已经由 minimal() 直接注册， 这里只补 UTF-8 String，避免重复注册触发 wire-id 冲突 warn。

**方法**

```java
Iterable<Codec<?>> codecs()
```

### Codec

`public interface Codec<T>`　Java 对象与 wire 字节的转换 SPI。

**方法**

```java
byte codecId()
Class<T> type()
int encodedLength(T value)
int encode(T value, MutableDirectBuffer buffer, int offset)
T decode(DirectBuffer buffer, int offset, int length)
```

### CodecIds

`public final class CodecIds`　帧头 CODEC 字节的预留值。

**字段 / 常量**

```java
static final byte RAW = 0
static final byte SBE = 1
static final byte PROTOBUF = 2
static final byte JSON = 3
static final byte STRING = 4
static final byte FORY = 5
static final int FIRST_USER_DEFINED = 100  // 业务自定义 codec id 的起点。
```

### CodecProvider

`public interface CodecProvider`　codec 提供器 SPI。一个 provider 可以一次性贡献多个 codec。

**方法**

```java
Iterable<Codec<?>> codecs()  // 返回该 provider 提供的所有 codec。在 registry 初始化时调用一次。
```

### CodecRegistry

`public final class CodecRegistry`　codec 注册表，按 wire id 和 Java 类型双向查。

**方法**

```java
static CodecRegistry minimal()  // 仅注册 RawBytesCodec，不扫 SPI；适合需要完全控制 codec 集合的场景。
static CodecRegistry withDefaults()  // 注册 RawBytesCodec，并通过 ServiceLoader 加载所有 CodecProvider 提供的 codec。
synchronized CodecRegistry register(Codec<?> codec)  // 注册一个 codec。
@SuppressWarnings("unchecked") <T> Codec<T> requireById(byte id)
@SuppressWarnings("unchecked") <T> Codec<T> requireByType(Class<T> type)
boolean containsId(byte id)
boolean containsType(Class<?> type)  // 注意：本方法不触发 fallback resolver，仅查已显式注册的 type。判断 "这个 type 现在有 codec 可用"（含 fallback 候选）请用 try { requireByType(t)…
CodecRegistry setFallbackResolver(Function<Class<?>, Codec<?>> resolver)  // 设置 fallback resolver；传 null 清除。同一 CodecRegistry 上线程安全替换。
Function<Class<?>, Codec<?>> fallbackResolver()  // 仅测试/诊断用。
```

### RawBytesCodec

`public final class RawBytesCodec implements Codec<byte[]>`　把 payload 当作 byte[] 直接搬的 codec。

**字段 / 常量**

```java
static final RawBytesCodec INSTANCE = new RawBytesCodec()
```

**方法**

```java
byte codecId()
Class<byte[]> type()
int encodedLength(byte[] v)
int encode(byte[] value, MutableDirectBuffer buffer, int offset)
byte[] decode(DirectBuffer buffer, int offset, int length)
```

### StringCodec

`public final class StringCodec implements Codec<String>`　UTF-8 字符串 codec。

**字段 / 常量**

```java
static final StringCodec INSTANCE = new StringCodec()
```

**方法**

```java
byte codecId()
Class<String> type()
int encodedLength(String value)
int encode(String value, MutableDirectBuffer buffer, int offset)
String decode(DirectBuffer buffer, int offset, int length)
```

## 包 `com.mcst.aeron.common.compression`

### CompressionCodec

`public interface CompressionCodec`　压缩 SPI。一个实现对应一个 wire id。

**方法**

```java
byte id()  // wire id，写入 frame header 的 COMPRESSION 字节。
int maxCompressedLength(int srcLength)  // 给定输入长度，返回压缩后可能的最大字节数（用于预分配 staging）。
int compress(byte[] src, int srcOffset, int srcLength, MutableDirectBuffer dst, int dstOffset)  // 压缩到目标 buffer，返回实际写入字节数。
int decompress(DirectBuffer src, int srcOffset, int srcLength, MutableDirectBuffer dst, int dstOffset, int dstCapacity)  // 解压到目标 buffer，返回实际写入字节数。
```

### CompressionIds

`public final class CompressionIds`　压缩算法 wire id 常量。0 表示未压缩。

**字段 / 常量**

```java
static final byte NONE = 0
static final byte LZ4 = 1
static final byte ZSTD = 2
static final byte DEFLATE = 3
```

### CompressionRegistry

`public final class CompressionRegistry`　压缩算法注册表，按 wire id 索引。

**方法**

```java
static CompressionRegistry empty()
static CompressionRegistry withDefaults()  // 通过 ServiceLoader 加载所有注册的压缩实现。
synchronized CompressionRegistry register(CompressionCodec codec)  // 注册一个压缩实现。
CompressionCodec requireById(byte id)
boolean containsId(byte id)
```

### DeflateCompression

`public final class DeflateCompression implements CompressionCodec`　基于 JDK java.util.zip Deflate 的压缩，作为内置 baseline；线程安全靠 ThreadLocal。

**字段 / 常量**

```java
static final DeflateCompression INSTANCE = new DeflateCompression()
```

**方法**

```java
static CompressionCodec provider()  // ServiceLoader 入口；返回类型必须是 SPI 接口本身（CompressionCodec）才会被识别。
byte id()
int maxCompressedLength(int srcLength)
int compress(byte[] src, int srcOffset, int srcLength, MutableDirectBuffer dst, int dstOffset)
int decompress(DirectBuffer src, int srcOffset, int srcLength, MutableDirectBuffer dst, int dstOffset, int dstCapacity)
```

## 包 `com.mcst.aeron.common.config`

### BackpressureStrategyType

`public enum BackpressureStrategyType`　producer 遇到背压时的处理策略。

**枚举常量**

```java
BLOCK  // 自旋 idle 直到塞进去。
DROP_NEWEST  // 当前这条直接丢掉。
FAIL  // 抛 BackpressureException。
RETRY_THEN_FAIL  // 重试 N 次仍失败则按 FAIL 抛。
```

### ChannelSpec

`public final class ChannelSpec`　Aeron channel 的描述对象。

**方法**

```java
static ChannelSpec ipc()
static ChannelSpec ipcUntethered()  // 不拴住 publication 的 IPC 订阅（aeron:ipc?tether=false），仅对 subscription 有意义。
static ChannelSpec udpUnicast(String endpoint)
static ChannelSpec udpMdc(String controlHost, int controlPort)
Kind kind()
String controlEndpoint()
String endpoint()
String controlMode()
boolean tethered()
String toAeronUri()  // 交给 Aeron 建 publication / subscription 的完整 URI。
String transportUri()  // 不含 subscription 专属参数的传输端点 URI。两端按它展开 partition， 订阅端加 tether=false 不改变 streamId 分配。
String toString()
```

#### ChannelSpec.Kind

`public enum Kind`

**枚举常量**

```java
IPC
UDP_UNICAST
UDP_MDC
```

### ConsumerConfig

`public final class ConsumerConfig`　consumer 不可变配置。

**字段 / 常量**

```java
static final int DEFAULT_BASE_STREAM_ID = ProducerConfig.DEFAULT_BASE_STREAM_ID
static final int DEFAULT_FRAGMENT_LIMIT = 16
static final int DEFAULT_RING_BUFFER_CAPACITY = 65536
static final int DEFAULT_WORKER_THREADS = 1
static final int DEFAULT_MAX_DECOMPRESSED_BYTES = 16 * 1024 * 1024
```

**方法**

```java
List<ChannelSpec> channels()
int baseStreamId()
Set<Integer> partitionAssignment()  // 不可变；空集合表示订全部 partition。
String groupId()  // 仅作 metrics tag，可能为 null。
int fragmentLimit()
DeliveryMode deliveryMode()
int workerThreads()
int ringBufferCapacity()
int dedupWindow()  // 去重环形窗口大小；0 表示不去重。每个 partition 独立一个 deduper 实例。
int maxDecompressedBytes()  // 解压后单条 payload 的硬上限，超出直接丢弃并报 metrics.onError，防 zip-bomb。
IdleStrategyType idleStrategy()  // poll 线程空转策略；默认 BACKOFF。行情低延迟用 BUSY_SPIN。
boolean reuseInlineContext()  // 是否在 INLINE 模式复用同一个 MessageContext 实例以消除每条消息的分配；默认 false。 开启后传给 handler 的 ctx 仅在 onMessage 回调期间有效，不可长期持有…
int partitionCount()  // partition 总数 = channels().size()。
static Builder builder()
```

#### ConsumerConfig.Builder

`public static final class Builder`

**方法**

```java
Builder channels(List<ChannelSpec> chs)  // Partition 列表；必须与 producer 端的 channels 完全一致才能配齐。
Builder channels(ChannelSpec... chs)
Builder baseStreamId(int id)
Builder partitionAssignment(Set<Integer> a)  // 本 consumer 实例订阅的 partition 子集；null 或空集合表示订全部。 用于静态分组消费：同 group 内多个实例配置不重叠的 assignment 即可分摊流量。
Builder groupId(String id)  // 仅作 metrics tag，不影响 wire / 行为。
Builder fragmentLimit(int n)
Builder deliveryMode(DeliveryMode m)
Builder workerThreads(int n)
Builder ringBufferCapacity(int capacity)  // RING_BUFFER_POOL 模式下 dispatch 队列容量。底层 ArrayBlockingQueue。
Builder dedupWindow(int capacity)
Builder maxDecompressedBytes(int n)
Builder idleStrategy(IdleStrategyType t)  // poll 线程空转策略;默认 BACKOFF(向后兼容)。 行情等低延迟场景设 BUSY_SPIN 消除空闲后的尾延迟尖刺 (代价:每个被订阅 partition 的 poll 线程各占满一个 CPU 核,建议配合核绑定…
Builder reuseInlineContext(boolean v)  // INLINE 模式下复用同一 MessageContext 实例,消除每条消息的 ctx 分配(零分配 codec + 高频行情场景收益最大)。默认 false…
ConsumerConfig build()
```

### DeliveryMode

`public enum DeliveryMode`　consumer 把消息派发给 handler 的方式。

**枚举常量**

```java
INLINE  // 直接在 poll 线程上跑 handler。
RING_BUFFER_POOL  // poll 线程入队，业务线程池消费。
```

### IdleStrategies

`public final class IdleStrategies`　IdleStrategyType → Agrona IdleStrategy 的工厂。

**方法**

```java
static IdleStrategy create(IdleStrategyType type)  // 按枚举创建一个全新的 IdleStrategy。SLEEPING 固定 1ms;需要其它 sleep 时长 / 自定义退避参数时,请在调用方直接 new 对应的 Agrona 策略。
```

### IdleStrategyType

`public enum IdleStrategyType`　consumer poll 线程在"本次没有 fragment 可处理"时的空转策略。

**枚举常量**

```java
BUSY_SPIN  // 纯忙等 + Thread.onSpinWait() 提示。唤醒最快,占满一核。行情低延迟首选。
NO_OP  // 纯忙等,无任何提示。唤醒最快,占满一核;务必配合核绑定使用。
YIELDING  // Thread.yield()。比忙等省一点 CPU,延迟略高。
BACKOFF  // spin → yield → park 逐级退避(park 上限约 1ms)。CPU 友好,空闲后有尾延迟尖刺。默认。
SLEEPING  // 每次固定 sleep(默认 1ms)。最省 CPU,延迟最高;仅适合延迟不敏感的吞吐型消费。
```

### ProducerConfig

`public final class ProducerConfig`　producer 不可变配置。

**字段 / 常量**

```java
static final int DEFAULT_BASE_STREAM_ID = 1001
static final int DEFAULT_BACKPRESSURE_RETRIES = 100
```

**方法**

```java
List<ChannelSpec> channels()
int baseStreamId()
Partitioner partitioner()
NoKeyStrategy noKeyStrategy()
BackpressureStrategyType backpressureStrategy()
int backpressureRetries()
int partitionCount()  // partition 总数 = channels().size()。决策 4：启动期常量。
static Builder builder()
```

#### ProducerConfig.Builder

`public static final class Builder`

**方法**

```java
Builder channels(List<ChannelSpec> chs)  // Partition 列表；第 i 号元素对应 partition i。至少一个元素。
Builder channels(ChannelSpec... chs)  // 等价于 channels(List.of(chs)) 的 varargs 糖。
Builder baseStreamId(int id)  // 起始 streamId；多个 partition 共用同一 channelUri 时（典型 IPC 退化）会从这里 递增分配。详见 PartitionLayout。
Builder partitioner(Partitioner p)  // 显式 partitioner；不设置则单 partition 用 singleton()，多 partition 用 murmur3()。
Builder noKeyStrategy(NoKeyStrategy s)
Builder backpressure(BackpressureStrategyType s)
Builder backpressureRetries(int n)
ProducerConfig build()
```

## 包 `com.mcst.aeron.common.exception`

### AeronMqException

`public class AeronMqException extends RuntimeException`　SDK 内部异常基类。

**构造器**

```java
AeronMqException(String message)
AeronMqException(String message, Throwable cause)
```

### CodecException

`public class CodecException extends AeronMqException`　Codec 编解码失败时抛。

**构造器**

```java
CodecException(String message)
CodecException(String message, Throwable cause)
```

### CompressionException

`public class CompressionException extends AeronMqException`　压缩 / 解压相关失败时抛。

**构造器**

```java
CompressionException(String message)
CompressionException(String message, Throwable cause)
```

### FrameDecodeException

`public class FrameDecodeException extends AeronMqException`　字节解不出合法 frame 时抛。

**构造器**

```java
FrameDecodeException(String message)
FrameDecodeException(String message, Throwable cause)
```

## 包 `com.mcst.aeron.common.frame`

### FrameDecoder

`public final class FrameDecoder`　把 buffer 里的字节按 FrameProtocol 解开。

**方法**

```java
static void decodeHeader(final DirectBuffer buffer, final int offset, final int length, final FrameHeader header)
static String decodeTopic(final DirectBuffer buffer, final FrameHeader header)
```

### FrameEncoder

`public final class FrameEncoder`　把消息按 FrameProtocol 写到 buffer。

**方法**

```java
static int encode(final MutableDirectBuffer buffer, final int offset, final byte flags, final byte codecId, final byte compressionId, final long timestampNanos, final long msgIdHigh, final long msgIdLow, final byte[] topicBytes, final int topicOffset, final int topicLength, final org.agrona.DirectBuffer payload, final int payloadOffset, final int payloadLength)
static void encodeHeaderAndTopic(final MutableDirectBuffer buffer, final int offset, final byte flags, final byte codecId, final byte compressionId, final long timestampNanos, final long msgIdHigh, final long msgIdLow, final byte[] topicBytes, final int topicOffset, final int topicLength, final int payloadLength)  // 只写 header + topic，payload 留给调用方写到 offset + HEADER_LENGTH + topicLength 起。
static int encode(final MutableDirectBuffer buffer, final int offset, final byte flags, final byte codecId, final long timestampNanos, final long msgIdHigh, final long msgIdLow, final String topic, final org.agrona.DirectBuffer payload, final int payloadOffset, final int payloadLength)
```

### FrameHeader

`public final class FrameHeader`　解码后的帧头，可复用。

**方法**

```java
byte version()
byte flags()
byte codecId()
byte compressionId()
int topicLength()
int payloadLength()
long timestampNanos()
long msgIdHigh()
long msgIdLow()
int topicOffset()
int payloadOffset()
int frameLength()
boolean isBatch()
boolean isCompressed()
void reset()
```

### FrameProtocol

`public final class FrameProtocol`　广播帧的字节布局常量。

**字段 / 常量**

```java
static final int MAGIC = 0x514D4541
static final byte VERSION_V1 = 0x01
static final int OFFSET_MAGIC = 0
static final int OFFSET_VERSION = 4
static final int OFFSET_FLAGS = 5
static final int OFFSET_CODEC = 6
static final int OFFSET_COMPRESSION = 7
static final int OFFSET_TOPIC_LEN = 8
static final int OFFSET_PADDING = 10
static final int OFFSET_PAYLOAD_LEN = 12
static final int OFFSET_TIMESTAMP_NS = 16
static final int OFFSET_MSG_ID_HIGH = 24
static final int OFFSET_MSG_ID_LOW = 32
static final int HEADER_LENGTH = 40
static final int MAX_TOPIC_LENGTH = 255  // topic 实际最大字节数。wire 上字段宽度是 uint16（理论可到 0xFFFF），但跨语言 SDK 统一约束到 255…
static final int TOPIC_LEN_FIELD_MAX = 0xFFFF  // topic 字段在 wire 上的硬上限，受 uint16 字段宽度约束；超过此值视为协议格式错误。
static final int MAX_PAYLOAD_LENGTH = Integer.MAX_VALUE - HEADER_LENGTH - TOPIC_LEN_FIELD_MAX
static final byte FLAG_BATCH = 0x01
static final byte FLAG_COMPRESSED = 0x02
```

**方法**

```java
static int frameLength(int topicLen, int payloadLen)
```

## 包 `com.mcst.aeron.common.metrics`

### ConsumerMetrics

`public interface ConsumerMetrics`　Consumer 侧热路径的 metrics 钩子。

**方法**

```java
void onReceived(String topic, int partition, String groupId, int payloadBytes, long endToEndNanos)  // 单条消息已成功 dispatch 到 user handler。
void onDuplicate(String topic, int partition, String groupId)  // 被 deduper 抑制（per-partition deduper 命中）。
void onError(String topic, int partition, String groupId, Throwable error)  // decode / dispatch / decompress / type mismatch 等异常。
default void onDispatchDropped(String topic, int partition, String groupId)  // RING_BUFFER_POOL 模式下 worker 队列满或 dispatcher 已 close，消息被丢弃。
static ConsumerMetrics noop()
```

### InMemoryConsumerMetrics

`public final class InMemoryConsumerMetrics implements ConsumerMetrics`　进程内累加的 consumer metrics 实现。按全局聚合，不区分 topic / partition / groupId。 业务需要细粒度切分时请自行实现 ConsumerMetrics。

**方法**

```java
void onReceived(String topic, int partition, String groupId, int payloadBytes, long endToEndNanos)
void onDuplicate(String topic, int partition, String groupId)
void onError(String topic, int partition, String groupId, Throwable error)
void onDispatchDropped(String topic, int partition, String groupId)
long receivedCount()
long receivedBytes()
long duplicates()
long errors()
long dispatchDropped()
long maxLatencyNanos()
```

### InMemoryProducerMetrics

`public final class InMemoryProducerMetrics implements ProducerMetrics`　进程内累加的 metrics 实现，用于单测、调试或简单 prometheus 反映射。

**方法**

```java
void onSent(String topic, int partition, int payloadBytes)
void onBackpressure(String topic, int partition, int retries)
void onDropped(String topic, int partition)
void onError(String topic, int partition, Throwable error)
long sentCount()
long sentBytes()
long backpressureRetries()
long dropped()
long errors()
long maxPayloadBytes()
```

### ProducerMetrics

`public interface ProducerMetrics`　Producer 侧热路径的 metrics 钩子。

**方法**

```java
void onSent(String topic, int partition, int payloadBytes)  // 单条消息成功写入 publication。
void onBackpressure(String topic, int partition, int retries)  // tryClaim 进入退避 / 重试次数（按消息为粒度上报最终累计 retries）。
void onDropped(String topic, int partition)  // 按 DROP_NEWEST / FAIL 等策略丢弃一条消息。
default void onError(String topic, int partition, Throwable error)  // codec encode / compression / Aeron commit / Partitioner 等非背压异常。
static ProducerMetrics noop()
```

## 包 `com.mcst.aeron.common.partition`

### Cluster

`public final class Cluster`　静态分组消费的拓扑校验工具。

**方法**

```java
static void validateAssignments(List<Set<Integer>> assignments, int partitionCount)  // 校验同一 group 内多实例的 partition 分配。
```

### NoKeyStrategy

`public enum NoKeyStrategy`　Producer 侧 key == null 时如何选 partition 的策略。

**枚举常量**

```java
ROUND_ROBIN  // 按发送计数轮询所有 partition。 各 partition 流量最均匀，但同 topic 不同消息会落到不同 partition， 失去同 topic FIFO 顺序。默认值。
FIRST  // 永远落 partition 0。 同 topic 严格保序（等价于单 partition 部署的退化行为）， 但完全失去多 partition 写入并行度。
TOPIC_HASH  // 按 topic 字节哈希。 同 topic 始终落同一 partition；不同 topic 大致均匀分摊。 适合"每个 topic 都是单独的有序流"的部署。
```

### PartitionLayout

`public final class PartitionLayout`　把"用户配的 channel 列表 + baseStreamId"展开成 N 个唯一的 (channelUri, streamId) 元组——producer 用它建 publication…

**方法**

```java
static List<Slot> expand(List<ChannelSpec> channels, int baseStreamId)  // 展开 channels 列表为 N 个 partition slot。
```

#### PartitionLayout.Slot

`public static final class Slot`　单个 partition 的部署元组。

**方法**

```java
int partitionId()
ChannelSpec channel()
String channelUri()
int streamId()
String toString()
```

### Partitioner

`public interface Partitioner`　Producer 侧的 key → partitionId 路由 SPI。

**方法**

```java
int route(String topic, Object key, int partitionCount)
static Partitioner murmur3()  // 默认实现：MurmurHash3 32-bit，对 key 取 UTF-8 字节后哈希。
static Partitioner singleton()  // 单 partition 部署的零开销路由：永远返回 0，跳过哈希。 Producer 在 partitionCount == 1 时自动选用这个实现。
```

## 包 `com.mcst.aeron.common.time`

### WallClock

`public final class WallClock`　端到端延迟用的墙钟(wall-clock)时间源,producer 与 consumer 必须用同一个,否则两端时钟源 不一致会让 e2e 延迟计算失真。

**方法**

```java
static long epochNanos()  // 自 Unix epoch 起的纳秒数(墙钟)。分辨率取决于平台时钟,通常 µs 级。
```

## 包 `com.mcst.aeron.common.topic`

### Topic

`public final class Topic`　topic 名字校验工具。允许字符 [A-Za-z0-9.\-_]，长度 1..MAX_LENGTH_BYTES。

**字段 / 常量**

```java
static final int MAX_LENGTH_BYTES = 255
```

**方法**

```java
static byte[] validateAndEncode(String topic)  // 校验并按 UTF-8 编码返回字节数组。
static void validate(String topic)
```

## 包 `com.mcst.aeron.compression.lz4`

### Lz4Compression

`public final class Lz4Compression implements CompressionCodec`　基于 lz4-java 的压缩。

**字段 / 常量**

```java
static final Lz4Compression INSTANCE = new Lz4Compression()
```

**构造器**

```java
Lz4Compression()
```

**方法**

```java
static CompressionCodec provider()  // ServiceLoader 入口，必须返回 SPI 接口本身。
byte id()
int maxCompressedLength(int srcLength)
int compress(byte[] src, int srcOffset, int srcLength, MutableDirectBuffer dst, int dstOffset)
int decompress(DirectBuffer src, int srcOffset, int srcLength, MutableDirectBuffer dst, int dstOffset, int dstCapacity)
```

## 包 `com.mcst.aeron.compression.zstd`

### ZstdCompression

`public final class ZstdCompression implements CompressionCodec`　基于 zstd-jni 的压缩。

**字段 / 常量**

```java
static final ZstdCompression INSTANCE = new ZstdCompression()
```

**构造器**

```java
ZstdCompression()
ZstdCompression(int level)
```

**方法**

```java
static CompressionCodec provider()  // ServiceLoader 入口，必须返回 SPI 接口本身。
byte id()
int maxCompressedLength(int srcLength)
int compress(byte[] src, int srcOffset, int srcLength, MutableDirectBuffer dst, int dstOffset)
int decompress(DirectBuffer src, int srcOffset, int srcLength, MutableDirectBuffer dst, int dstOffset, int dstCapacity)
```

## 包 `com.mcst.aeron.consumer`

### AeronConsumer

`public final class AeronConsumer implements Consumer`　Consumer SDK 入口。

**方法**

```java
<T> void subscribe(String topic, Class<T> payloadType, MessageHandler<T> handler)
void start()
void close()  // 关闭顺序：所有 agentRunner → dispatcher（共享）→ 所有 subscription → driver（如果 own）。
int subscribedPartitionCount()  // 本实例实际订阅的 partition 数量（== subscription 数）。
static Builder builder()
```

#### AeronConsumer.Builder

`public static final class Builder`

**方法**

```java
Builder driver(DriverManager driver)
Builder ownDriver(DriverManager driver)
Builder config(ConsumerConfig config)
Builder codec(Codec<?> codec)
Builder codecRegistry(CodecRegistry registry)
Builder compressionRegistry(CompressionRegistry registry)
Builder metrics(ConsumerMetrics metrics)
Builder idleStrategySupplier(Supplier<IdleStrategy> supplier)  // 高级:注入自定义的 poll 线程空转策略工厂,优先级高于 idleStrategy()。
AeronConsumer build()
```

### Consumer

`public interface Consumer extends AutoCloseable`　接收端 API。

**方法**

```java
<T> void subscribe(String topic, Class<T> payloadType, MessageHandler<T> handler)  // 订阅 topic。payloadType 用来在收到消息时挑对应的 codec 解码。
void start()  // 启动 poll 线程开始消费。
void close()
```

### MessageContext

`public final class MessageContext`　收到消息时附带的元信息。

**构造器**

```java
MessageContext(String topic, int partition, long msgIdHigh, long msgIdLow, long timestampNanos, byte codecId, byte compressionId)
MessageContext()  // SDK 内部使用。供 INLINE 复用路径创建的空实例;字段随后由 reset 填充。 业务代码请勿调用。
```

**方法**

```java
void reset(String topic, int partition, long msgIdHigh, long msgIdLow, long timestampNanos, byte codecId, byte compressionId)  // SDK 内部使用,业务代码请勿调用。复用同一实例:用新消息的元信息覆盖所有字段。 仅在 INLINE + reuseInlineContext 路径由 poll 单线程调用(回调同步消费)。
String topic()
int partition()  // 本条消息来自的 partition；单 partition 部署下永远是 0。
long msgIdHigh()
long msgIdLow()
long timestampNanos()
byte codecId()
byte compressionId()  // producer 写入时使用的压缩算法 id；0 表示未压缩。
long latencyMicros()  // 从发送时刻到现在的延迟，单位微秒；若发送方时钟领先本机或字段未填，返回 0 而非负数。
```

### MessageHandler

`public interface MessageHandler<T>`　注解：`@FunctionalInterface`　业务侧处理一条消息。

**方法**

```java
void onMessage(T payload, MessageContext ctx)
```

### MessageIdDeduper

`public final class MessageIdDeduper`　基于环形哈希表的消息 id 去重器，O(1) 检查，无锁。

**构造器**

```java
MessageIdDeduper(int capacity)
```

**方法**

```java
static MessageIdDeduper disabled()  // 创建一个空操作 deduper：所有 checkAndMark 都返回 true。
boolean isEnabled()
boolean isDuplicate(long high, long low)  // 返回 true 表示该 id 在窗口内已经见过（应跳过），false 表示是新消息。 只读不写槽位。 (0,0) 视为占位空槽，永远算"新"。
void mark(long high, long low)  // 把该 id 写入窗口。poll 线程在派发前调用（占位）。
void unmark(long high, long low)  // 条件释放槽位：仅当槽位仍持有该 id 时清为 (0,0) 占位空值。 派发失败路径（队列满 / 已关闭 / handler 抛异常 / drain 丢弃）调用， 使同 msgId 的合法重试不被误判为重复…
boolean checkAndMark(long high, long low)  // 检查并立刻标记。返回 true 表示是新消息（应被处理），false 表示在窗口内已经见过。 (0,0) 视为占位空槽，永远算"新"…
```

## 包 `com.mcst.aeron.consumer.internal`

### Dispatcher

`public interface Dispatcher extends AutoCloseable`　把已解码的消息派发给业务 handler。

**方法**

```java
void dispatch(TopicSubscription sub, Object payload, MessageContext ctx, MessageIdDeduper deduper)  // 派发一条消息。
boolean retainsContextBeyondCall()  // dispatch 返回后,实现是否仍可能持有 / 异步读取传入的 MessageContext。 true(如 RING_BUFFER_POOL):ctx 会入队、被 worker 线程在之后读取, 调用方必须每条传入全…
void close()
```

### InlineDispatcher

`public final class InlineDispatcher implements Dispatcher`　直接在 poll 线程上执行 handler；handler 抛异常按 metrics 上报，不让异常逃回 PollAgent。

**构造器**

```java
InlineDispatcher()
InlineDispatcher(ConsumerMetrics metrics, String groupId)
```

**方法**

```java
void dispatch(TopicSubscription sub, Object payload, MessageContext ctx, MessageIdDeduper deduper)
boolean retainsContextBeyondCall()
void close()
```

### PollAgent

`public final class PollAgent implements Agent, FragmentHandler`　在自己的线程里循环 poll Aeron Subscription，解 frame 后交给 dispatcher。

**构造器**

```java
PollAgent(Subscription subscription, int partition, String groupId, int fragmentLimit, int maxDecompressedBytes, CodecRegistry codecRegistry, CompressionRegistry compressionRegistry, MessageIdDeduper deduper, ConsumerMetrics metrics, Dispatcher dispatcher, ConcurrentMap<String, TopicSubscription> sharedSubs, boolean reuseInlineContext)
```

**方法**

```java
int doWork()
String roleName()
void onFragment(DirectBuffer buffer, int offset, int length, Header aeronHeader)
int partition()
```

### RingBufferPoolDispatcher

`public final class RingBufferPoolDispatcher implements Dispatcher`

**构造器**

```java
RingBufferPoolDispatcher(int workerThreads, int capacity, String namePrefix, ConsumerMetrics metrics, String groupId)
```

**方法**

```java
void dispatch(TopicSubscription sub, Object payload, MessageContext ctx, MessageIdDeduper deduper)
boolean retainsContextBeyondCall()
void close()  // 四阶段关闭： set running=false，让 worker 自己看到信号后排空 queue 自然退出（grace period）…
```

### TopicSubscription

`public final class TopicSubscription`　一个 topic 上的订阅记录：handler 可能针对某个具体 payload 类型。

**构造器**

```java
@SuppressWarnings("unchecked") TopicSubscription(String topic, Class<?> payloadType, MessageHandler<?> handler)
```

**方法**

```java
String topic()
Class<?> payloadType()
MessageHandler<Object> handler()
```

## 包 `com.mcst.aeron.driver`

### DriverConfig

`public final class DriverConfig`　DriverManager 的不可变配置。

**字段 / 常量**

```java
static final long DEFAULT_DRIVER_TIMEOUT_MS = 10_000L
```

**方法**

```java
String aeronDir()
ThreadingMode threadingMode()
IdleStrategyType driverIdleStrategy()  // MediaDriver 各线程(conductor/sender/receiver/shared)的空转策略；null = 用 Aeron 默认。
boolean dirDeleteOnStart()
boolean dirDeleteOnShutdown()
long driverTimeoutMs()
Integer mtuLength()  // UDP 通道 MTU（字节）；null = 用 Aeron 默认（1408，即单帧 payload 上限 1376）。
Integer ipcMtuLength()  // IPC 通道 MTU（字节）；null = 用 Aeron 默认。
static DriverConfig defaults()
static Builder builder()
```

#### DriverConfig.Builder

`public static final class Builder`

**方法**

```java
Builder aeronDir(String aeronDir)
Builder threadingMode(ThreadingMode mode)
Builder driverIdleStrategy(IdleStrategyType t)  // MediaDriver 内部线程(conductor / sender / receiver / shared)的空转策略。 null(默认)沿用 Aeron 自带默认(退避型,空闲会 park)。
Builder dirDeleteOnStart(boolean v)  // 启动时是否清掉 Aeron 工作目录。默认 true，方便单进程开发场景。 同一台机器上多 JVM 共用同一 aeronDir 时务必置 false…
Builder dirDeleteOnShutdown(boolean v)
Builder driverTimeoutMs(long timeoutMs)
Builder mtuLength(Integer mtuLength)  // UDP 通道 MTU（字节）。决定单帧 payload 上限： Publication.maxPayloadLength() = mtu − 32（Aeron 数据帧头）…
Builder ipcMtuLength(Integer ipcMtuLength)  // IPC 通道 MTU（字节），语义同 mtuLength(Integer)。IPC 走共享内存无网络分片顾虑， 单条消息偏大时可放心调大。默认 null 沿用 Aeron 默认。
DriverConfig build()
```

### DriverManager

`public interface DriverManager extends AutoCloseable`　Aeron 客户端及 Media Driver 的生命周期句柄。

**方法**

```java
static DriverManager embedded(DriverConfig config)
static DriverManager external(String aeronDir)
Aeron aeronClient()
String aeronDir()
boolean isEmbedded()
void close()
```

## 包 `com.mcst.aeron.metrics.micrometer`

### MicrometerConsumerMetrics

`public final class MicrometerConsumerMetrics implements ConsumerMetrics`　把 ConsumerMetrics 桥接到 Micrometer。接收数 / 去重 / 错误 / 丢弃计数,以及 端到端延迟直方图(p50/p99/p99.9)都会自动出现在监控系统里。

**构造器**

```java
MicrometerConsumerMetrics(MeterRegistry registry)
MicrometerConsumerMetrics(MeterRegistry registry, Tags commonTags, boolean recordLatency)
```

**方法**

```java
void onReceived(String topic, int partition, String groupId, int payloadBytes, long endToEndNanos)
void onDuplicate(String topic, int partition, String groupId)
void onError(String topic, int partition, String groupId, Throwable error)
void onDispatchDropped(String topic, int partition, String groupId)
```

### MicrometerOutboxMetrics

`public final class MicrometerOutboxMetrics implements OutboxMetrics`　把 OutboxMetrics 桥接到 Micrometer——监控 WAL / 转发 / 崩溃恢复链路。

**构造器**

```java
MicrometerOutboxMetrics(MeterRegistry registry)
MicrometerOutboxMetrics(MeterRegistry registry, Tags commonTags)
```

**方法**

```java
void onPersisted(String topic, int payloadBytes)
void onForwarded(String topic)
void onForwardRetry(String topic)
void onRecovered(String topic)
void onBacklog(long backlogBytes)
void onError(String topic, Throwable error)
```

### MicrometerProducerMetrics

`public final class MicrometerProducerMetrics implements ProducerMetrics`　把 ProducerMetrics 桥接到 Micrometer。一旦把任意 MeterRegistry (Prometheus / OTLP / Datadog / SimpleMeterRegistry ...)交给…

**构造器**

```java
MicrometerProducerMetrics(MeterRegistry registry)
MicrometerProducerMetrics(MeterRegistry registry, Tags commonTags)
```

**方法**

```java
void onSent(String topic, int partition, int payloadBytes)
void onBackpressure(String topic, int partition, int retries)
void onDropped(String topic, int partition)
void onError(String topic, int partition, Throwable error)
```

## 包 `com.mcst.aeron.producer`

### AeronProducer

`public final class AeronProducer implements Producer, EncodedFrameSender`

**方法**

```java
<T> long send(String topic, Object key, T payload)
<T> long send(String topic, Object key, T payload, long msgIdHigh, long msgIdLow)
<T> int sendAll(String topic, Object key, Iterable<T> payloads)
int maxFrameLength()  // EncodedFrameSender 实现：payload 已编码,跳过 codec.encode,其余(路由 / 压缩 / 成帧 / 背压循环) 与 doSend 完全一致…
long sendEncoded(String topic, Object key, byte codecId, byte[] payload, int offset, int length, long msgIdHigh, long msgIdLow)
boolean isConnected()
boolean isAllConnected()
boolean isConnected(int partition)
int partitionCount()
void close()
static Builder builder()
```

#### AeronProducer.Builder

`public static final class Builder`

**方法**

```java
Builder driver(DriverManager driver)
Builder ownDriver(DriverManager driver)  // 把 driver 的生命周期交给 producer，close 时一并关掉。
Builder config(ProducerConfig config)
Builder codec(Codec<?> codec)
Builder codecRegistry(CodecRegistry registry)
Builder messageIdGenerator(MessageIdGenerator generator)
Builder compression(CompressionCodec compression)  // 配置 payload 压缩；不设置则不压缩。
Builder metrics(ProducerMetrics metrics)
AeronProducer build()
```

### BackpressureException

`public class BackpressureException extends AeronMqException`　Aeron 发送失败的统一基类，对应 Publication.tryClaim/offer 返回的负数 result。

**构造器**

```java
BackpressureException(String message, long aeronResult)
```

**方法**

```java
long aeronResult()  // Aeron Publication.tryClaim/offer 返回的负数原因码。
```

### EncodedFrameSender

`public interface EncodedFrameSender`　低层发送 SPI：把已经编码好的 payload 字节连同显式 codecId 与 msgId 直接成帧发送。

**方法**

```java
long sendEncoded(String topic, Object key, byte codecId, byte[] payload, int offset, int length, long msgIdHigh, long msgIdLow)  // 发送一段已编码的 payload 字节。
int maxFrameLength()  // 单条 frame 的最大允许字节数 = 各 partition publication maxPayloadLength 的最小值 (保证消息无论路由到哪个 partition 都不会超界)。
```

### MessageIdGenerator

`public interface MessageIdGenerator`　生成 128 位消息 id 并写入 buffer 指定位置。

**方法**

```java
void writeNext(MutableDirectBuffer buffer, int offset)  // 把下一个 id 的 16 字节写到 buffer 的 offset 位置（高 8 字节在前）。
static MessageIdGenerator snowflake()  // 默认实现：高 64 位 = 41-bit ms + 22-bit per-ms sequence； 低 64 位 = 16-bit nodeId + 48-bit 进程 salt（XOR sequence）…
```

### Producer

`public interface Producer extends AutoCloseable`　发送端 API。

**方法**

```java
default <T> long send(String topic, T payload)  // 发送消息（不指定 key）；按 NoKeyStrategy 选 partition，msgId 由内置生成器分配。
<T> long send(String topic, Object key, T payload)  // 发送消息，按 key 路由 partition；msgId 由内置生成器分配。
default <T> long send(String topic, T payload, long msgIdHigh, long msgIdLow)  // 发送消息（不指定 key），调用方提供 msgId（业务有自己的 id，如订单号 / trace id）。
<T> long send(String topic, Object key, T payload, long msgIdHigh, long msgIdLow)  // 发送消息，按 key 路由 partition；调用方提供 msgId。
default <T> int sendAll(String topic, Iterable<T> payloads)  // 同 topic 批量发送（不指定 key）；循环 send，topic 编码 / 校验只走一次缓存路径。
<T> int sendAll(String topic, Object key, Iterable<T> payloads)  // 同 topic + 同 key 批量发送：所有消息进入同一 partition，保 FIFO。
boolean isConnected()  // 是否至少一个 partition 已经有 subscriber 接通。
boolean isAllConnected()  // 是否所有 partition 都已经有 subscriber 接通。
boolean isConnected(int partition)  // 指定 partition 是否已接通。
int partitionCount()  // Partition 总数。决策 4：启动期常量。
void close()
```

### PublicationTerminalException

`public class PublicationTerminalException extends BackpressureException`　Publication 进入终态（CLOSED、MAX_POSITION_EXCEEDED）时抛出， 调用方不应继续重试这条 producer。

**构造器**

```java
PublicationTerminalException(String message, long aeronResult)
```

## 包 `com.mcst.aeron.producer.internal`

### BackpressureHandler

`public interface BackpressureHandler`　处理 Publication.tryClaim 返回的负数结果。

**方法**

```java
boolean onFailure(long result, int attempt)
default void reset()  // 每条消息进入 tryClaim 循环前调用一次。带状态的退避策略（如 BackoffIdleStrategy） 必须在这里把状态拨回起点，否则前一条消息背压留下的高 backoff 会影响下一条 latency。
static BackpressureHandler of(BackpressureStrategyType type, int retries)
```

### SnowflakeMessageIdGenerator

`public final class SnowflakeMessageIdGenerator implements MessageIdGenerator`　128-bit 消息 id 生成器。

**构造器**

```java
SnowflakeMessageIdGenerator()
SnowflakeMessageIdGenerator(int nodeId)  // 显式 nodeId 用于多进程部署区分；只取低 16 位。
```

**方法**

```java
void writeNext(MutableDirectBuffer buffer, int offset)
```

## 包 `com.mcst.aeron.producer.outbox`

### FsyncPolicy

`public enum FsyncPolicy`　WAL 持久化等级:控制"消息写入 WAL 后多强地保证已落到物理磁盘"。

**枚举常量**

```java
PER_RECORD  // 每条记录 append 后立即 fsync。强一致,延迟最高。金融核心账务类建议用这个。
INTERVAL  // 后台周期 fsync(见 OutboxConfig.flushIntervalMillis)。延迟与安全的折中,默认值。
OS_BUFFERED  // 不显式 fsync,依赖操作系统刷盘。延迟最低,断电有丢失窗口。
```

### OutboxConfig

`public final class OutboxConfig`　OutboxProducer 的不可变配置。

**方法**

```java
boolean enabled()  // 是否开启 Store-and-Forward;默认 false(直通底层 producer)。
String walDir()  // WAL 工作目录;不设默认 DEFAULT_WAL_DIR。多实例必须各自独立。
FsyncPolicy fsyncPolicy()  // 持久化等级;默认 INTERVAL。
long flushIntervalMillis()  // INTERVAL 的 fsync 周期(毫秒);默认 100。
long forwarderIdleParkNanos()  // 转发器无待发记录时的 park 时长(纳秒);默认 1ms。
long forwardRetryBackoffNanos()  // 转发遇到瞬时背压失败后的重试退避(纳秒);默认 1ms。
long drainOnCloseMillis()  // close 时最多等待转发器排空的时长(毫秒);默认 5000。
int checkpointEveryRecords()  // 每成功转发 N 条持久化一次 checkpoint;默认 1(每条)。
OutboxStoreType storeType()  // WAL 存储实现;默认 SEGMENTED。
long segmentBytes()  // 单个 segment 的滚动大小(字节);仅 SEGMENTED 用,默认 64 MiB。
static OutboxConfig disabled()  // 默认配置:不开启。
static Builder builder()
```

#### OutboxConfig.Builder

`public static final class Builder`

**方法**

```java
Builder enabled(boolean enabled)
Builder walDir(String walDir)
Builder fsyncPolicy(FsyncPolicy p)
Builder flushIntervalMillis(long ms)
Builder forwarderIdleParkNanos(long ns)
Builder forwardRetryBackoffNanos(long ns)
Builder drainOnCloseMillis(long ms)
Builder checkpointEveryRecords(int n)
Builder storeType(OutboxStoreType t)
Builder segmentBytes(long bytes)
OutboxConfig build()
```

### OutboxException

`public class OutboxException extends AeronMqException`　Outbox / WAL 相关异常(磁盘 I/O 失败、WAL 损坏不可恢复等)。

**构造器**

```java
OutboxException(String message)
OutboxException(String message, Throwable cause)
```

### OutboxMetrics

`public interface OutboxMetrics`　Outbox 专属指标钩子(与 ProducerMetrics 互补:后者记录真正写入 Aeron 的发送指标, 本接口记录 WAL / 转发 / 恢复层面的事件)。

**字段 / 常量**

```java
OutboxMetrics NOOP = new OutboxMetrics() { }
```

**方法**

```java
default void onPersisted(String topic, int payloadBytes)  // 一条消息成功持久化进 WAL(发送线程)。
default void onForwarded(String topic)  // 一条消息成功从 WAL 转发到 Aeron(转发器线程)。
default void onForwardRetry(String topic)  // 一条消息转发时遇到瞬时背压 / 失败,稍后重试(转发器线程)。
default void onRecovered(String topic)  // 启动时从 WAL 重放(崩溃恢复):一条消息被重新转发。
default void onBacklog(long backlogBytes)  // 当前 WAL 积压字节数(转发器周期上报,便于监控堆积)。
default void onError(String topic, Throwable error)  // WAL / 转发链路上的异常。
static OutboxMetrics noop()
```

### OutboxProducer

`public final class OutboxProducer implements Producer`　在底层 Producer 前面加一层 Store-and-Forward(先持久化再转发) 的装饰器。

**方法**

```java
static Producer wrap(Producer delegate, OutboxConfig config, CodecRegistry codecRegistry, MessageIdGenerator idGenerator, OutboxMetrics metrics, boolean ownsDelegate)  // 根据配置包装 producer。config.enabled()==false 时原样返回 delegate, 不产生任何 WAL / 线程开销。
<T> long send(String topic, Object key, T payload)
<T> long send(String topic, Object key, T payload, long msgIdHigh, long msgIdLow)
<T> int sendAll(String topic, Object key, Iterable<T> payloads)
boolean isConnected()
boolean isAllConnected()
boolean isConnected(int partition)
int partitionCount()
long backlogBytes()  // 当前 WAL 中已落盘但尚未转发到 Aeron 的积压字节数。
void close()
static Builder builder()
```

#### OutboxProducer.Builder

`public static final class Builder`

**方法**

```java
Builder delegate(Producer delegate)
Builder ownDelegate(Producer delegate)  // 把底层 producer 的生命周期交给 outbox,close 时一并关闭。
Builder ownsDelegate(boolean owns)
Builder config(OutboxConfig config)
Builder codecRegistry(CodecRegistry registry)
Builder codec(Codec<?> codec)
Builder messageIdGenerator(MessageIdGenerator generator)
Builder metrics(OutboxMetrics metrics)
OutboxProducer build()
```

### OutboxStoreType

`public enum OutboxStoreType`　WAL 存储实现选择。

**枚举常量**

```java
SEGMENTED  // 分段文件(默认):WAL 拆成固定大小 segment,某段被完整转发后整段删除。 满负载、转发器从不空闲时也能边发边回收磁盘,文件总量约束在"未转发积压 + 至多一个段"。
SINGLE_FILE  // 单文件:append-only,仅在"全部转发完(积压为 0)"那一刻整体截断回收。 实现最简单,适合突发 / 间歇负载;持续满负载下已转发前缀要等空闲间隙才回收。
```

## 包 `com.mcst.aeron.producer.outbox.internal`

### KeyBytes

`public final class KeyBytes`　把路由 key 归约成规范字节表示,规则与 Murmur3Partitioner.hashKey 完全一致。

**字段 / 常量**

```java
static final byte TYPE_NULL = 0
static final byte TYPE_BYTES = 1
static final byte TYPE_STRING = 2
static final byte TYPE_LONG = 3
static final byte TYPE_INTEGER = 4
static final byte TYPE_OTHER = 5
```

**方法**

```java
static byte typeOf(Object key)  // key 的类型标签。
static byte[] toBytes(Object key)  // key 的规范字节表示;null 返回 null。
```

### ProducerRecordSender

`public final class ProducerRecordSender implements RecordSender`　Producer 侧的 RecordSender:把一条 WAL 记录(WalCodec 格式)原样(保持原 codecId / msgId) 通过 sendEncoded 重发到 Aeron。

**构造器**

```java
ProducerRecordSender(EncodedFrameSender sender)
```

**方法**

```java
ForwardOutcome forward(DirectBuffer buffer, int offset, int length)
```

### WalCodec

`public final class WalCodec`　WAL 业务记录的字节布局(不含 DurableLog 实现在外层加的 长度/CRC 框):

**字段 / 常量**

```java
static final int MAGIC = 0x4C574541
static final byte VERSION_V1 = 0x01
static final int OFFSET_MAGIC = 0
static final int OFFSET_VERSION = 4
static final int OFFSET_CODEC_ID = 5
static final int OFFSET_KEY_TYPE = 6
static final int OFFSET_PADDING = 7
static final int OFFSET_MSG_ID_HIGH = 8
static final int OFFSET_MSG_ID_LOW = 16
static final int OFFSET_TOPIC_LEN = 24
static final int OFFSET_KEY_LEN = 26
static final int OFFSET_PAYLOAD_LEN = 28
static final int HEADER_LENGTH = 32
```

**方法**

```java
static int recordLength(int topicLen, int keyLen, int payloadLen)
static int encode(MutableDirectBuffer dst, int offset, byte codecId, byte keyType, long msgIdHigh, long msgIdLow, byte[] topicBytes, byte[] keyBytes, byte[] payload, int payloadOffset, int payloadLength)  // 把一条记录编码进 dst[offset..],返回记录总字节数。
static void decode(WalRecordView view, DirectBuffer src, int offset, int length)  // 把 src[offset..offset+length) 解析进 view;校验 MAGIC / VERSION。
```

### WalRecordView

`public final class WalRecordView`　解码后的 WAL 记录视图,可复用(转发器单线程,每次 WalCodec.decode 覆盖)。

**字段 / 常量**

```java
byte codecId
byte keyType
long msgIdHigh
long msgIdLow
int topicOffset  // topic 字节在源 buffer 内的偏移与长度(UTF-8)。
int topicLength
int keyOffset  // 规范字节 key 在源 buffer 内的偏移与长度;keyLength == 0 表示无 key。
int keyLength
int payloadOffset
int payloadLength
```

## 包 `com.mcst.aeron.spring.annotation`

### AeronConsumerRef

`public @interface AeronConsumerRef`　注解：`@Target({ElementType.FIELD, ElementType.PARAMETER, ElementType.METHOD})` `@Retention(RetentionPolicy.RUNTIME)` `@Documented` `@Qualifier`　注入指定 driver 的 AeronConsumer 的语义化别名。

**方法**

```java
String value()  // Driver name。
```

### AeronDriver

`public @interface AeronDriver`　注解：`@Target({ElementType.FIELD, ElementType.PARAMETER, ElementType.METHOD, ElementType.TYPE, ElementType.ANNOTATION_TYPE})` `@Retention(RetentionPolicy.RUNTIME)` `@Documented` `@Qualifier`　多 driver 场景下注入 DriverManager / AeronProducer / AeronConsumer 的限定符。

**方法**

```java
String value()  // Driver name，须与 yaml easyfk.config.aeron.drivers. 一致。
```

### AeronProducerRef

`public @interface AeronProducerRef`　注解：`@Target({ElementType.FIELD, ElementType.PARAMETER, ElementType.METHOD})` `@Retention(RetentionPolicy.RUNTIME)` `@Documented` `@Qualifier`　注入指定 driver 的 AeronProducer 的语义化别名。

**方法**

```java
String value()  // Driver name。
```

### AeronTopic

`public @interface AeronTopic`　注解：`@Target(ElementType.METHOD)` `@Retention(RetentionPolicy.RUNTIME)` `@Documented`　标注一个 Spring Bean 中的方法为 Aeron topic 订阅处理器。

**方法**

```java
String value()  // 必填：topic 字符串，须通过 com.mcst.aeron.common.topic.Topic#validate 校验。
Class<?> payloadType()  // 必填：业务消息 Java 类型；权威类型声明，方法参数仅供编绑定参考。
String driver() default ""  // 多 driver 场景必填：目标 driver name，须存在于 easyfk.config.aeron.drivers 配置中； 单 driver 场景留空，自动使用唯一 driver。
```

## 包 `com.mcst.aeron.spring.autoconfig`

### AeronAutoConfiguration

`public class AeronAutoConfiguration`　注解：`@Configuration(proxyBeanMethods = false)` `@AutoConfigureAfter(name = { "org.springframework.boot.actuate.autoconfigure.metrics.MetricsAutoConfiguration", "org.springframework.boot.actuate.autoconfigure.metrics.CompositeMeterRegistryAutoConfiguration", "org.springframework.boot.actuate.autoconfigure.metrics.export.simple.SimpleMetricsExportAutoConfiguration" })` `@ConditionalOnClass(name = "org.springframework.boot.SpringApplication")` `@ConditionalOnProperty(prefix = AeronProperties.PREFIX, name = "enabled", havingValue = "true", matchIfMissing = true)` `@EnableConfigurationProperties(AeronProperties.class)` `@Import({ AeronDriverAutoConfiguration.class, AeronCodecAutoConfiguration.class, AeronMetricsAutoConfiguration.class, AeronProducerAutoConfiguration.class, AeronConsumerAutoConfiguration.class, AeronHealthAutoConfiguration.class })`　Aeron starter 主装配入口。

**方法**

```java
@Bean @ConditionalOnMissingBean AeronLifecycle aeronLifecycle(AeronProperties properties)  // 注册全局 AeronLifecycle。业务方可以通过定义自己的 @Bean AeronLifecycle 覆盖默认行为。
```

### AeronCodecAutoConfiguration

`public class AeronCodecAutoConfiguration`　注解：`@Configuration(proxyBeanMethods = false)` `@Import(AeronCodecAutoConfiguration.CodecRegistryRegistrar.class)` `@AutoConfigureAfter(AeronDriverAutoConfiguration.class)`　装配每个 driver 的 CodecRegistry，合并 SPI 默认 + @Bean Codec + yaml 路径。

**字段 / 常量**

```java
static final String REGISTRY_BEAN_PREFIX = "aeronCodecRegistry"
```

#### AeronCodecAutoConfiguration.CodecRegistryRegistrar

`public static class CodecRegistryRegistrar implements ImportBeanDefinitionRegistrar, EnvironmentAware`

**方法**

```java
void setEnvironment(Environment environment)
void registerBeanDefinitions(AnnotationMetadata importingClassMetadata, BeanDefinitionRegistry registry)
```

### AeronConsumerAutoConfiguration

`public class AeronConsumerAutoConfiguration`　注解：`@Configuration(proxyBeanMethods = false)` `@Import(AeronConsumerAutoConfiguration.ConsumerBeanRegistrar.class)` `@AutoConfigureAfter({ AeronDriverAutoConfiguration.class, AeronCodecAutoConfiguration.class, AeronProducerAutoConfiguration.class })`　装配 AeronConsumer Bean（按 driver 名注册）+ AeronTopicBeanPostProcessor。

**字段 / 常量**

```java
static final String CONSUMER_BEAN_PREFIX = "aeronConsumer"
```

#### AeronConsumerAutoConfiguration.ConsumerBeanRegistrar

`public static class ConsumerBeanRegistrar implements ImportBeanDefinitionRegistrar, EnvironmentAware`

**方法**

```java
void setEnvironment(Environment environment)
void registerBeanDefinitions(AnnotationMetadata importingClassMetadata, BeanDefinitionRegistry registry)
```

### AeronConsumerFactoryBean

`public class AeronConsumerFactoryBean implements FactoryBean<AeronConsumer>, ApplicationContextAware, DisposableBean`　为单个 driver 装配一份 AeronConsumer。

**构造器**

```java
AeronConsumerFactoryBean(String driverBeanName, String codecRegistryBeanName, ConsumerProperties props)
```

**方法**

```java
void setApplicationContext(ApplicationContext applicationContext) throws BeansException
Class<?> getObjectType()
boolean isSingleton()
AeronConsumer getObject()
void destroy()
```

### AeronDriverAutoConfiguration

`public class AeronDriverAutoConfiguration`　注解：`@Configuration(proxyBeanMethods = false)` `@Import(AeronDriverAutoConfiguration.DriverBeanRegistrar.class)`　装配 DriverManager Bean（按 driver 名注册）。

**字段 / 常量**

```java
static final String DRIVER_BEAN_PREFIX = "aeronDriverManager"
```

#### AeronDriverAutoConfiguration.DriverBeanRegistrar

`public static class DriverBeanRegistrar implements ImportBeanDefinitionRegistrar, EnvironmentAware`　把 yaml 中每个 driver 注册成独立的 DriverManager Bean。

**方法**

```java
void setEnvironment(Environment environment)
void registerBeanDefinitions(AnnotationMetadata importingClassMetadata, BeanDefinitionRegistry registry)
DriverManager buildDriverManager(DriverProperties props)  // 构造一个 DriverManager。可见性 protected 便于测试 subclass 替换为 stub。
```

### AeronHealthAutoConfiguration

`public class AeronHealthAutoConfiguration`　注解：`@Configuration(proxyBeanMethods = false)` `@ConditionalOnClass(name = "org.springframework.boot.actuate.health.HealthIndicator")` `@ConditionalOnProperty(prefix = "management.health.aeron", name = "enabled", havingValue = "true", matchIfMissing = true)` `@AutoConfigureAfter({ AeronDriverAutoConfiguration.class, AeronProducerAutoConfiguration.class })`　装配 AeronHealthIndicator（Spring Boot Actuator 可选集成）。

**方法**

```java
@Bean @ConditionalOnMissingBean AeronHealthIndicator aeronHealthIndicator(ListableBeanFactory beanFactory)
```

### AeronMetricsAutoConfiguration

`public class AeronMetricsAutoConfiguration`　注解：`@Configuration(proxyBeanMethods = false)` `@ConditionalOnClass({MeterRegistry.class, MicrometerProducerMetrics.class})` `@ConditionalOnBean(MeterRegistry.class)` `@ConditionalOnProperty(prefix = com.mcst.aeron.spring.properties.AeronProperties.PREFIX + ".metrics", name = "enabled", havingValue = "true", matchIfMissing = true)` `@AutoConfigureBefore({ AeronProducerAutoConfiguration.class, AeronConsumerAutoConfiguration.class })`　把 SDK 的 metrics SPI 自动桥接到 Micrometer,实现开箱即用的生产监控。

**方法**

```java
@Bean @ConditionalOnMissingBean(ProducerMetrics.class) ProducerMetrics aeronProducerMetrics(MeterRegistry registry)
@Bean @ConditionalOnMissingBean(ConsumerMetrics.class) ConsumerMetrics aeronConsumerMetrics(MeterRegistry registry)
@Bean @ConditionalOnMissingBean(OutboxMetrics.class) OutboxMetrics aeronOutboxMetrics(MeterRegistry registry)
```

### AeronProducerAutoConfiguration

`public class AeronProducerAutoConfiguration`　注解：`@Configuration(proxyBeanMethods = false)` `@Import(AeronProducerAutoConfiguration.ProducerBeanRegistrar.class)` `@AutoConfigureAfter({AeronDriverAutoConfiguration.class, AeronCodecAutoConfiguration.class})`　装配 AeronProducer Bean（按 driver 名注册）。

**字段 / 常量**

```java
static final String PRODUCER_BEAN_PREFIX = "aeronProducer"
```

#### AeronProducerAutoConfiguration.ProducerBeanRegistrar

`public static class ProducerBeanRegistrar implements ImportBeanDefinitionRegistrar, EnvironmentAware`

**方法**

```java
void setEnvironment(Environment environment)
void registerBeanDefinitions(AnnotationMetadata importingClassMetadata, BeanDefinitionRegistry registry)
```

### AeronProducerFactoryBean

`public class AeronProducerFactoryBean implements FactoryBean<Producer>, ApplicationContextAware, DisposableBean`　为单个 driver 装配一份 AeronProducer。

**构造器**

```java
AeronProducerFactoryBean(String driverBeanName, String codecRegistryBeanName, ProducerProperties props, String driverName)
```

**方法**

```java
void setApplicationContext(ApplicationContext applicationContext) throws BeansException
Class<?> getObjectType()
boolean isSingleton()
Producer getObject()
void destroy()
```

### CodecRegistryFactoryBean

`public class CodecRegistryFactoryBean implements FactoryBean<CodecRegistry>, ApplicationContextAware`　为单个 driver 装配一份 CodecRegistry：合并 SPI 默认 + @Bean Codec + yaml 路径。

**构造器**

```java
CodecRegistryFactoryBean(String driverName, List<CodecProperties> yamlCodecs, CodecDefaultProperties codecDefaults)
```

**方法**

```java
void setApplicationContext(@org.springframework.lang.NonNull ApplicationContext applicationContext) throws BeansException
Class<?> getObjectType()
boolean isSingleton()
CodecRegistry getObject()
```

## 包 `com.mcst.aeron.spring.properties`

### AeronProperties

`public class AeronProperties`　注解：`@ConfigurationProperties(prefix = AeronProperties.PREFIX)`　Aeron starter 顶层配置，对应 yaml prefix easyfk.config.aeron （与公司框架其他模块的 easyfk.config.* 前缀对齐）。

**字段 / 常量**

```java
static final String PREFIX = "easyfk.config.aeron"  // 配置前缀，与框架其他模块的 easyfk.config.* 对齐。
boolean enabled = true  // 全局开关；false 不装配任何 Bean（用于排除特定场景）。
String defaultDriver  // 多 driver 场景必填：该 driver 的 producer / consumer / driverManager / codecRegistry bean 额外注册不带后缀的 alias（aeronProduce…
@NestedConfigurationProperty DriverProperties driver  // 单 driver 简化路径。与 drivers 互斥。 内部会被 normalize 成 drivers.default 统一处理。
Map<String, DriverProperties> drivers = new LinkedHashMap<>()  // 多 driver 完整路径，key = driver name。name 须匹配 [a-zA-Z][a-zA-Z0-9_-]{0,31}.
List<CodecProperties> codecs = new ArrayList<>()  // yaml 路径注册的 codec 列表（与 @Bean Codec 自动扫描合并）。
@NestedConfigurationProperty CodecDefaultProperties codec = new CodecDefaultProperties()  // 默认 codec 兜底配置。easyfk.config.aeron.codec.default-codec=fory（默认）时未注册的 POJO 类型自动用 ForyCodec…
@NestedConfigurationProperty ShutdownProperties shutdown = new ShutdownProperties()  // 关闭行为配置。
@NestedConfigurationProperty ProducerGlobalProperties producer = new ProducerGlobalProperties()  // 全局 producer 子系统开关。easyfk.config.aeron.producer.enabled=false 时所有 driver 的 AeronProducer bean 都不装配；适合"纯订阅服务"…
@NestedConfigurationProperty ConsumerGlobalProperties consumer = new ConsumerGlobalProperties()  // 全局 consumer 子系统开关。easyfk.config.aeron.consumer.enabled=false 时所有 driver 的 AeronConsumer bean 都不装配；适合"纯发送服务"…
```

**方法**

```java
boolean isEnabled()
void setEnabled(boolean enabled)
String getDefaultDriver()
void setDefaultDriver(String defaultDriver)
DriverProperties getDriver()
void setDriver(DriverProperties driver)
Map<String, DriverProperties> getDrivers()
void setDrivers(Map<String, DriverProperties> drivers)
List<CodecProperties> getCodecs()
void setCodecs(List<CodecProperties> codecs)
CodecDefaultProperties getCodec()
void setCodec(CodecDefaultProperties codec)
ShutdownProperties getShutdown()
void setShutdown(ShutdownProperties shutdown)
ProducerGlobalProperties getProducer()
void setProducer(ProducerGlobalProperties producer)
ConsumerGlobalProperties getConsumer()
void setConsumer(ConsumerGlobalProperties consumer)
```

### BackpressureProperties

`public class BackpressureProperties`　背压策略配置。

**方法**

```java
String getStrategy()
void setStrategy(String strategy)
int getRetries()
void setRetries(int retries)
```

### CodecDefaultProperties

`public class CodecDefaultProperties`　默认 codec 兜底配置。对应 yaml 路径：easyfk.config.aeron.codec.*。

**方法**

```java
String getDefaultCodec()
void setDefaultCodec(String defaultCodec)
```

### CodecProperties

`public class CodecProperties`　yaml 路径注册一个 Codec 的描述。

**方法**

```java
String getClassName()
void setClassName(String className)
String getFactoryMethod()
void setFactoryMethod(String factoryMethod)
List<String> getFactoryArgs()
void setFactoryArgs(List<String> factoryArgs)
List<String> getDrivers()
void setDrivers(List<String> drivers)
```

### ConsumerGlobalProperties

`public class ConsumerGlobalProperties`　全局 consumer 子系统开关。对应 yaml 路径：easyfk.config.aeron.consumer.*。

**方法**

```java
boolean isEnabled()
void setEnabled(boolean enabled)
```

### ConsumerProperties

`public class ConsumerProperties`　Aeron consumer 配置（按 driver 隔离）。

**方法**

```java
boolean isEnabled()
void setEnabled(boolean enabled)
List<String> getChannels()
void setChannels(List<String> channels)
int getBaseStreamId()
void setBaseStreamId(int baseStreamId)
Set<Integer> getPartitionAssignment()
void setPartitionAssignment(Set<Integer> partitionAssignment)
String getGroupId()
void setGroupId(String groupId)
String getDeliveryMode()
void setDeliveryMode(String deliveryMode)
int getWorkerThreads()
void setWorkerThreads(int workerThreads)
int getRingBufferCapacity()
void setRingBufferCapacity(int ringBufferCapacity)
int getFragmentLimit()
void setFragmentLimit(int fragmentLimit)
int getDedupWindow()
void setDedupWindow(int dedupWindow)
String getIdleStrategy()
void setIdleStrategy(String idleStrategy)
boolean isReuseInlineContext()
void setReuseInlineContext(boolean reuseInlineContext)
DataSize getMaxDecompressedBytes()
void setMaxDecompressedBytes(DataSize maxDecompressedBytes)
```

### DriverProperties

`public class DriverProperties`　单个 Aeron driver 的配置。

**方法**

```java
boolean isEmbedded()
void setEmbedded(boolean embedded)
String getAeronDir()
void setAeronDir(String aeronDir)
boolean isDirDeleteOnStart()
void setDirDeleteOnStart(boolean dirDeleteOnStart)
boolean isDirDeleteOnShutdown()
void setDirDeleteOnShutdown(boolean dirDeleteOnShutdown)
long getDriverTimeoutMs()
void setDriverTimeoutMs(long driverTimeoutMs)
String getThreadingMode()
void setThreadingMode(String threadingMode)
String getDriverIdleStrategy()
void setDriverIdleStrategy(String driverIdleStrategy)
DataSize getMtuLength()
void setMtuLength(DataSize mtuLength)
DataSize getIpcMtuLength()
void setIpcMtuLength(DataSize ipcMtuLength)
ProducerProperties getProducer()
void setProducer(ProducerProperties producer)
ConsumerProperties getConsumer()
void setConsumer(ConsumerProperties consumer)
```

### OutboxProperties

`public class OutboxProperties`　单个 driver 的 producer "先持久化再转发"(store-and-forward / outbox)配置。

**方法**

```java
boolean isEnabled()
void setEnabled(boolean enabled)
String getWalDir()
void setWalDir(String walDir)
String getFsyncPolicy()
void setFsyncPolicy(String fsyncPolicy)
long getFlushIntervalMillis()
void setFlushIntervalMillis(long flushIntervalMillis)
long getForwarderIdleParkNanos()
void setForwarderIdleParkNanos(long forwarderIdleParkNanos)
long getForwardRetryBackoffNanos()
void setForwardRetryBackoffNanos(long forwardRetryBackoffNanos)
long getDrainOnCloseMillis()
void setDrainOnCloseMillis(long drainOnCloseMillis)
int getCheckpointEveryRecords()
void setCheckpointEveryRecords(int checkpointEveryRecords)
String getStoreType()
void setStoreType(String storeType)
long getSegmentBytes()
void setSegmentBytes(long segmentBytes)
```

### ProducerGlobalProperties

`public class ProducerGlobalProperties`　全局 producer 子系统开关。对应 yaml 路径：easyfk.config.aeron.producer.*。

**方法**

```java
boolean isEnabled()
void setEnabled(boolean enabled)
```

### ProducerProperties

`public class ProducerProperties`　Aeron producer 配置（按 driver 隔离）。

**方法**

```java
boolean isEnabled()
void setEnabled(boolean enabled)
List<String> getChannels()
void setChannels(List<String> channels)
int getBaseStreamId()
void setBaseStreamId(int baseStreamId)
String getPartitioner()
void setPartitioner(String partitioner)
String getNoKeyStrategy()
void setNoKeyStrategy(String noKeyStrategy)
BackpressureProperties getBackpressure()
void setBackpressure(BackpressureProperties backpressure)
OutboxProperties getOutbox()
void setOutbox(OutboxProperties outbox)
```

### ShutdownProperties

`public class ShutdownProperties`　Aeron starter 关闭行为配置。

**方法**

```java
Duration getTimeout()
void setTimeout(Duration timeout)
```

## 包 `com.mcst.aeron.spring.runtime`

### AeronHealthIndicator

`public class AeronHealthIndicator implements HealthIndicator`　Spring Boot Actuator HealthIndicator：汇总所有 Aeron driver / producer 的状态。

**构造器**

```java
AeronHealthIndicator(Map<String, DriverManager> drivers, Map<String, Producer> producers)
```

**方法**

```java
Health health()
```

### AeronLifecycle

`public class AeronLifecycle implements SmartLifecycle, ApplicationContextAware`　控制 Aeron starter 的启动 / 关闭顺序，桥接 Spring 容器生命周期与 SDK 资源。

**构造器**

```java
AeronLifecycle(AeronProperties properties)
```

**方法**

```java
void setApplicationContext(ApplicationContext applicationContext) throws BeansException
int getPhase()
boolean isAutoStartup()
boolean isRunning()
void start()
void stop()
void stop(Runnable callback)
```

### AeronTopicBeanPostProcessor

`public class AeronTopicBeanPostProcessor implements BeanPostProcessor`　扫描容器中所有 bean 的 @AeronTopic 方法，编绑定为 MessageHandler， 暂存到内部列表…

**方法**

```java
Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException
List<PendingBinding> snapshotPending()  // 返回累计编绑定结果的快照，不清空内部列表。
void clearPending()  // 清空内部列表。仅应在所有绑定都已成功移交（subscribe 成功）之后调用。
@Deprecated List<PendingBinding> drainPending()  // 取出累计的编绑定结果并清空内部列表（快照副本）。
```

#### AeronTopicBeanPostProcessor.PendingBinding

`public static final class PendingBinding`　编绑定结果记录。

**字段 / 常量**

```java
final String topic
final String driver
final Class<?> payloadType
final MessageHandler<?> handler
final String beanName
final String methodDesc
```

**构造器**

```java
PendingBinding(String topic, String driver, Class<?> payloadType, MessageHandler<?> handler, String beanName, String methodDesc)
```

### SpringBootVersionCheck

`public final class SpringBootVersionCheck`　启动期校验当前运行时的 Spring Boot 版本在 starter 支持范围内。

**方法**

```java
static void requireAtLeast(String minVersion)  // 要求当前运行时 Spring Boot 版本 &gt;= minVersion；否则抛 IllegalStateException 带 hint 信息。
static void requireRange(String minInclusive, String maxExclusive)  // 要求当前运行时 Spring Boot 版本满足 minInclusive <= current < maxExclusive。
```

### TopicMethodBinder

`public final class TopicMethodBinder`　把一个 @AeronTopic 标注的方法编绑定为 MessageHandler，运行期等同直接调用。

**方法**

```java
@SuppressWarnings("unchecked") static <T> MessageHandler<T> bind(Object bean, Method method, Class<T> payloadType)  // 把 (bean, method) 编绑定为 MessageHandler。
static void validateMethodSignature(Method method, Class<?> payloadType)  // 验证方法签名是否符合 @AeronTopic 契约。
```

## 包 `com.mcst.aeron.spring.support`

### ChannelUriParser

`public final class ChannelUriParser`　把 yaml 中的 raw Aeron channel URI 解析成 ChannelSpec。

**方法**

```java
static ChannelSpec parse(String uri)
```

### CodecFactoryResolver

`public final class CodecFactoryResolver`　把 yaml CodecProperties（class-name + factory-method + factory-args）反射加载为 Codec。

**方法**

```java
static Codec<?> resolve(CodecProperties props, ClassLoader classLoader)  // 按 props 解析并实例化一个 Codec。
```

### DefaultCodecFallback

`public final class DefaultCodecFallback`　解析 easyfk.config.aeron.codec.default-codec（fory / none）为可注入到 CodecRegistry.setFallbackResolver 的 Function。

**方法**

```java
static Function<Class<?>, Codec<?>> resolve(CodecDefaultProperties props, ClassLoader classLoader, String driverName)  // 解析配置 → fallback resolver 函数。
```

### DriverNameValidator

`public final class DriverNameValidator`　校验 AeronProperties 互斥规则 + driver name 合法性，并 normalize 单 driver 简化路径。

**字段 / 常量**

```java
static final Pattern DRIVER_NAME_PATTERN = Pattern.compile("^[a-zA-Z][a-zA-Z0-9_-]{0,31}$")  // 合法 driver name 字符集，须能作为合法 Spring Bean name 后缀。
static final String DEFAULT_DRIVER_NAME = "default"  // 单 driver 路径 normalize 后使用的 name。
```

**方法**

```java
static void validateAndNormalize(AeronProperties props)  // 校验并 normalize；失败抛 IllegalStateException，错误信息带 hint。
static String toCamelCase(String name)  // 把 driver name 转成 camelCase 用于 Bean 后缀，如 ipc-local → ipcLocal。
```

## 包 `com.mcst.aeron.store`

### DurableLog

`public interface DurableLog extends AutoCloseable`　崩溃安全的顺序追加日志 SPI。一条"记录"= 一段不透明的业务字节(引擎不关心其内容)。

**方法**

```java
long append(DirectBuffer record, int offset, int length)  // 追加一条记录并按持久化等级落盘。
boolean peek(RecordHandler handler)  // 读取当前读游标处的记录(若有),交给 handler;不推进游标。
void advance()  // 把读游标推进过当前(最近一次 peek 命中的)记录。必须在 peek 返回 true 后调用。
void checkpoint()  // 把当前读游标位置持久化(checkpoint),崩溃后从此处续发。
void flush()  // 立即 fsync(供 INTERVAL 周期任务或优雅关闭调用)。
long backlogBytes()  // 当前已落盘但尚未转发的积压字节数(写位置 - 读游标)。
void compactIfDrained()  // 当已全部转发完(读游标追上写位置)时压缩 / 回收空间;否则空操作。
void close()
```

### ForwardOutcome

`public enum ForwardOutcome`　forward 的结果,决定转发器对当前记录的处置。

**枚举常量**

```java
SENT  // 已成功交给下游传输:推进读游标,继续下一条。
RETRY  // 瞬时失败(背压 / 缓冲满 / 临时不可达):不推进,退避后原地重试同一条。
TERMINAL  // 终态失败(传输通道不可恢复地关闭):停止转发,数据原样留在 WAL,待下次启动恢复续发。
```

### FsyncPolicy

`public enum FsyncPolicy`　WAL 持久化等级:控制"记录写入 WAL 后多强地保证已落到物理磁盘"。

**枚举常量**

```java
PER_RECORD  // 每条记录 append 后立即 fsync。强一致,延迟最高。
INTERVAL  // 后台周期 fsync。延迟与安全的折中,默认值。
OS_BUFFERED  // 不显式 fsync,依赖操作系统刷盘。延迟最低,断电有丢失窗口。
```

### RecordSender

`public interface RecordSender`　注解：`@FunctionalInterface`　唯一的领域扩展点:把一条 WAL 记录的字节交给真正的下游传输。

**方法**

```java
ForwardOutcome forward(DirectBuffer buffer, int offset, int length)  // 把 buffer[offset..offset+length) 这条记录交给下游。
```

### StoreConfig

`public final class StoreConfig`　StoreForwardQueue 的不可变配置:WAL 目录、持久化等级、存储实现与转发器调参。

**字段 / 常量**

```java
static final String DEFAULT_WAL_DIR = "aeron-store-wal"  // 默认 WAL 目录(相对进程工作目录);多个队列实例务必各自显式指定独立目录,共用会互相损坏。
```

**方法**

```java
String walDir()  // WAL 工作目录;不设默认 DEFAULT_WAL_DIR。多个队列实例必须各自独立。
FsyncPolicy fsyncPolicy()  // 持久化等级;默认 INTERVAL。
long flushIntervalMillis()  // INTERVAL 的 fsync 周期(毫秒);默认 100。
long forwarderIdleParkNanos()  // 转发器无待发记录时的 park 时长(纳秒);默认 1ms。
long forwardRetryBackoffNanos()  // 转发遇到瞬时失败后的重试退避(纳秒);默认 1ms。
long drainOnCloseMillis()  // close 时最多等待转发器排空的时长(毫秒);默认 5000。
int checkpointEveryRecords()  // 每成功转发 N 条持久化一次 checkpoint;默认 1(每条)。
StoreType storeType()  // WAL 存储实现;默认 SEGMENTED。
long segmentBytes()  // 单个 segment 的滚动大小(字节);仅 SEGMENTED 用,默认 64 MiB。
static Builder builder()
```

#### StoreConfig.Builder

`public static final class Builder`

**方法**

```java
Builder walDir(String walDir)
Builder fsyncPolicy(FsyncPolicy p)
Builder flushIntervalMillis(long ms)
Builder forwarderIdleParkNanos(long ns)
Builder forwardRetryBackoffNanos(long ns)
Builder drainOnCloseMillis(long ms)
Builder checkpointEveryRecords(int n)
Builder storeType(StoreType t)
Builder segmentBytes(long bytes)
StoreConfig build()
```

### StoreException

`public class StoreException extends RuntimeException`　Store-and-Forward 内核异常(WAL 磁盘 I/O 失败、WAL 损坏不可恢复等)。

**构造器**

```java
StoreException(String message)
StoreException(String message, Throwable cause)
```

### StoreForwardQueue

`public final class StoreForwardQueue implements AutoCloseable`　通用 Store-and-Forward 队列门面:组装 DurableLog + 后台 RecordForwarder 线程, 提供"先持久化(append)、再由后台可靠转发到 RecordSender"的不丢语义。

**方法**

```java
static StoreForwardQueue start(StoreConfig config, RecordSender sender, StoreMetrics metrics)  // 启动一个队列:创建 WAL、启动后台转发器。
long append(DirectBuffer record, int offset, int length)  // 持久化一条记录(record[offset..offset+length));落盘成功后返回其全局单调序号。 由单一生产线程调用。
long backlogBytes()  // 当前 WAL 中已落盘但尚未转发的积压字节数。
void close()
```

### StoreMetrics

`public interface StoreMetrics`　Store-and-Forward 内核的指标钩子。不带任何领域标签(如 topic)——内核对记录内容不透明, 单转发器全局聚合;需要领域维度打点的上层可在自己的 RecordSender 里另行处理。

**字段 / 常量**

```java
StoreMetrics NOOP = new StoreMetrics() { }
```

**方法**

```java
default void onPersisted(int recordBytes)  // 一条记录成功持久化进 WAL(生产线程);recordBytes 为该条 WAL 记录的字节数。
default void onForwarded()  // 一条记录成功从 WAL 转发到下游(转发器线程,稳态)。
default void onForwardRetry()  // 一条记录转发遇到瞬时失败,稍后重试(转发器线程)。
default void onRecovered()  // 启动时从 WAL 重放(崩溃恢复):一条记录被重新转发。
default void onBacklog(long backlogBytes)  // 当前 WAL 积压字节数(转发器周期上报,便于监控堆积)。
default void onError(Throwable error)  // WAL / 转发链路上的异常(WAL 损坏、终态传输失败等)。
static StoreMetrics noop()
```

### StoreType

`public enum StoreType`　WAL 存储实现选择。

**枚举常量**

```java
SEGMENTED  // 分段文件(默认):WAL 拆成固定大小 segment,某段被完整转发后整段删除。 满负载、转发器从不空闲时也能边发边回收磁盘,文件总量约束在"未转发积压 + 至多一个段"。 底层为内存映射(mmap)实现。
SINGLE_FILE  // 单文件:append-only,仅在"全部转发完(积压为 0)"那一刻整体截断回收。 实现最简单,适合突发 / 间歇负载;持续满负载下已转发前缀要等空闲间隙才回收…
```

## 包 `com.mcst.aeron.store.internal`

### RecordForwarder

`public final class RecordForwarder implements Runnable`　单线程转发器:顺序从 DurableLog 读出记录,交给 RecordSender 投递到下游; 仅当 SENT 才推进读游标,RETRY 原地退避重试、绝不跳过—— 这是"不丢"的核心。记录内容对本类完全不透明。

**构造器**

```java
RecordForwarder(DurableLog log, RecordSender sender, StoreMetrics metrics, long idleParkNanos, long retryBackoffNanos, int checkpointEvery)
```

**方法**

```java
void requestDrain(long drainMillis)  // 请求优雅排空:转发完当前积压后退出,最多等待 drainMillis。
void requestStop()  // 立即请求停止(不保证排空)。
void run()
```

### SegmentedLog

`public final class SegmentedLog implements DurableLog`　分段文件 DurableLog 的 内存映射(mmap) 实现:WAL 被拆成一串 segment 文件 outbox..wal(16 位零填充),每个 segment 在创建时预分配为固定大小并零填充, 然后整段映射进…

**构造器**

```java
SegmentedLog(String walDir, FsyncPolicy fsyncPolicy, long segmentBytes, long flushIntervalMillis)
```

**方法**

```java
long append(DirectBuffer record, int offset, int length)
boolean peek(RecordHandler handler)
void advance()
void checkpoint()
void flush()
long backlogBytes()
void compactIfDrained()
void close()
```

### SingleFileLog

`public final class SingleFileLog implements DurableLog`　基于单个 append-only 文件的 DurableLog 实现(FileChannel 顺序读写)。

**构造器**

```java
SingleFileLog(String walDir, FsyncPolicy fsyncPolicy, long flushIntervalMillis)
```

**方法**

```java
long append(DirectBuffer record, int offset, int length)
boolean peek(RecordHandler handler)
void advance()
void checkpoint()
void flush()
long backlogBytes()
void compactIfDrained()
void close()
```

### WalDirGuard

`public final class WalDirGuard`　进程内 WAL 目录独占守卫。

**方法**

```java
static String normalize(String walDir)  // 把 walDir 归一化成稳定 key(绝对路径 + 规范化,不要求目录已存在),用于占用判定。
static String claim(String walDir)  // 进程内独占占用 walDir。
static void release(String key)  // 解除占用;key 为 null 时为 no-op。
```
