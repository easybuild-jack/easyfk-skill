# easyfk-component-chronicle API 签名速查（easyfk 3.5.16）

> 坐标：`com.mcst:chronicle-map、chronicle-queue`　源码：`easyfk-component/component-chronicle/chronicle-map`、`easyfk-component/component-chronicle/chronicle-queue`
> 由 `scripts/gen-api.py` 从 36 个源文件自动提取，共 31 个类型、258 个方法/构造器、76 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-component-chronicle-skill.md](../modules/easyfk-component-chronicle-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 配置项（@ConfigurationProperties）

### `easyfk.config.chronicle.map` ← ChronicleMapProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `default-path` | `String` | `"./chronicle-maps"` | 默认存储路径 |
| `default-max-entries` | `long` | `100000L` | 默认最大条目数 |
| `default-average-key-size` | `double` | `64.0` | 默认平均键大小（字节） |
| `default-average-value-size` | `double` | `1024.0` | 默认平均值大小（字节） |
| `default-file-extension` | `String` | `".dat"` | 默认持久化文件扩展名 |
| `persistence-enabled` | `boolean` | `true` | 是否启用持久化（总开关）。关闭时所有 Map（含声明式与编程式显式 filePath）均为纯内存。 |
| `recover-on-startup` | `boolean` | `true` | 是否在启动时恢复数据 |
| `compression-enabled` | `boolean` | `false` | 是否启用压缩 |
| `apply-average-sizes` | `boolean` | `true` | 是否应用平均大小参数（averageKeySize/averageValueSize） |
| `fixed-size-optimization-enabled` | `boolean` | `true` | 是否启用固定尺寸类型优化（对于 Long/Integer/Double/Float/Short/Byte/Character/Boolean 不设置平均大小） |
| `fory-marshaller-enabled` | `boolean` | `true` | 未显式指定是否使用 Fory 时，是否按值类型自动识别（默认 true）。 开启时 Chronicle 原生类型（基本类型及包装类、String、byte[]、BytesMarshallable、java.* 下的 Se… |
| `fory-schema-mode` | `SchemaMode` | `—` | Fory 序列化模式，null 表示沿用 serializer-fory 的全局默认。 CONSISTENT 体积小、速度快；COMPATIBLE 容忍字段增删，但每条记录都要处理字段元数据， 读写更慢、堆分配更多… |
| `put-returns-null` | `boolean` | `false` | put 是否返回 null 而不是旧值。 Map 契约要求 put 返回旧值，而堆外存储为此必须额外反序列化出一个完整对象再丢弃—— 这份开销落在段更新锁内，是写路径上最大的一笔无谓分配… |
| `remove-returns-null` | `boolean` | `false` | remove 是否返回 null 而不是被删除的值。理由同 putReturnsNull。 |
| `maps` | `List<ChronicleMapDefinedInfo>` | `—` | 自定义 Chronicle Map 配置集合 |

### `easyfk.config.storage.queue` ← ChronicleQueueProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `default-path` | `String` | `"./chronicle-queues"` | 默认存储路径 |
| `default-roll-cycle` | `String` | `"FAST_DAILY"` | 默认滚动周期（FAST_DAILY, FAST_HOURLY, FIVE_MINUTELY, TEN_MINUTELY, TWENTY_MINUTELY, HALF_HOURLY, WEEKLY 等） |
| `default-block-size` | `long` | `0` | 默认块大小（字节），0 表示使用 Chronicle Queue 默认值 |
| `create-directories-on-startup` | `boolean` | `true` | 是否在启动时预创建队列目录 |
| `fory-schema-mode` | `SchemaMode` | `SchemaMode.COMPATIBLE` | Fory 消息默认序列化模式，默认 COMPATIBLE（容忍字段增删，适合持久化消息）。 两种模式字节流互不兼容，已有队列数据不可中途切换；可在单队列 fory-schema-mode 覆写。 |
| `queues` | `List<ChronicleQueueDefinedInfo>` | `—` | 自定义 Chronicle Queue 配置集合 |
| `listener` | `Listener` | `new Listener()` | listener 默认配置 |
| `cleanup` | `Cleanup` | `new Cleanup()` | 队列滚动文件清理配置（位点感知） |


## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `chronicle-map` | `com.mcst.easyfk.chronicle.map.config.ChronicleMapAutoConfiguration` |
| `chronicle-queue` | `com.mcst.easyfk.chronicle.queue.config.ChronicleQueueAutoConfiguration` |
| `chronicle-queue` | `com.mcst.easyfk.chronicle.queue.cleanup.ChronicleQueueCleanupAutoConfiguration` |

## 类型索引

- `com.mcst.easyfk.chronicle.map.config`：[ChronicleMapAutoConfiguration](#chroniclemapautoconfiguration)、[ChronicleMapDefinedInfo](#chroniclemapdefinedinfo)
- `com.mcst.easyfk.chronicle.map.manager`：[ChronicleMapManager](#chroniclemapmanager)
- `com.mcst.easyfk.chronicle.map.marshaller`：[ForyBytesMarshaller](#forybytesmarshaller)
- `com.mcst.easyfk.chronicle.map.properties`：[ChronicleMapProperties](#chroniclemapproperties)
- `com.mcst.easyfk.chronicle.map.template`：[ChronicleMapTemplate](#chroniclemaptemplate)
- `com.mcst.easyfk.chronicle.queue.cleanup`：[ChronicleQueueCleanupAutoConfiguration](#chroniclequeuecleanupautoconfiguration)、[ChronicleQueueCleanupTask](#chroniclequeuecleanuptask)
- `com.mcst.easyfk.chronicle.queue.config`：[ChronicleQueueAutoConfiguration](#chroniclequeueautoconfiguration)、[ChronicleQueueDefinedInfo](#chroniclequeuedefinedinfo)
- `com.mcst.easyfk.chronicle.queue.enums`：[TailerStartStrategy](#tailerstartstrategy)
- `com.mcst.easyfk.chronicle.queue.listener`：[ChronicleQueueListener](#chroniclequeuelistener)、[ChronicleQueueListenerBeanPostProcessor](#chroniclequeuelistenerbeanpostprocessor)、[ChronicleQueueListenerDaemonMode](#chroniclequeuelistenerdaemonmode)、[ChronicleQueueListenerErrorHandler](#chroniclequeuelistenererrorhandler)、[ChronicleQueueListenerErrorMessage](#chroniclequeuelistenererrormessage)
    [ChronicleQueueListenerFailurePolicy](#chroniclequeuelistenerfailurepolicy)、[ChronicleQueueListenerIdleMode](#chroniclequeuelisteneridlemode)、[ChronicleQueueListenerMetrics](#chroniclequeuelistenermetrics)、[ChronicleQueueListenerQueueMetrics](#chroniclequeuelistenerqueuemetrics)、[ChronicleQueueListenerRegistry](#chroniclequeuelistenerregistry)
    [ChronicleQueueListenerRetryBackoffMode](#chroniclequeuelistenerretrybackoffmode)、[ChronicleQueueListenerState](#chroniclequeuelistenerstate)、[ChronicleQueueListenerStatus](#chroniclequeuelistenerstatus)、[ChronicleQueueMessageFormat](#chroniclequeuemessageformat)、[LoggingChronicleQueueListenerErrorHandler](#loggingchroniclequeuelistenererrorhandler)
- `com.mcst.easyfk.chronicle.queue.manager`：[ChronicleQueueManager](#chroniclequeuemanager)
- `com.mcst.easyfk.chronicle.queue.properties`：[ChronicleQueueProperties](#chroniclequeueproperties)
- `com.mcst.easyfk.chronicle.queue.template`：[ChronicleQueueConsumer](#chroniclequeueconsumer)、[ChronicleQueuePublisher](#chroniclequeuepublisher)、[ChronicleQueueTemplate](#chroniclequeuetemplate)

## 包 `com.mcst.easyfk.chronicle.map.config`

### ChronicleMapAutoConfiguration

`public class ChronicleMapAutoConfiguration`　注解：`@Slf4j` `@AutoConfiguration` `@EnableConfigurationProperties(ChronicleMapProperties.class)`　Chronicle Map 自动配置类 Manager 在启动时创建并初始化声明式 Map，配置错误会让应用启动失败。

**方法**

```java
@Bean @ConditionalOnMissingBean ChronicleMapManager chronicleMapManager(ChronicleMapProperties chronicleMapProperties)
@Bean @ConditionalOnMissingBean ChronicleMapTemplate chronicleMapTemplate(ChronicleMapManager chronicleMapManager)
```

### ChronicleMapDefinedInfo

`public class ChronicleMapDefinedInfo`　Lombok：`@Data`　Chronicle Map 定义信息

**字段 / 常量**

```java
String mapName  // Map 名称
String filePath  // 存储文件路径
Long maxEntries  // 最大条目数（可选，未配置则使用全局默认）
Double averageKeySize  // 平均键大小（字节）（可选，未配置则使用全局默认）
Double averageValueSize  // 平均值大小（字节）（可选，未配置则使用全局默认）
boolean persistenceEnabled = true  // 是否启用持久化
boolean compressionEnabled = false  // 是否启用压缩
Class<?> keyType = String.class  // 键的类型
Class<?> valueType = Object.class  // 值的类型
String fileExtension  // 文件扩展名（可选，未配置则使用全局默认）
Boolean applyAverageSizes  // 是否应用平均大小参数（可选，未配置则使用全局默认）
Boolean fixedSizeOptimizationEnabled  // 是否启用固定尺寸类型优化（可选，未配置则使用全局默认）
Boolean useForyMarshaller  // 是否使用 Fory Marshaller 序列化（可选，未配置则使用全局默认）
SchemaMode forySchemaMode  // Fory 序列化模式（可选，未配置则使用全局默认）
Boolean putReturnsNull  // put 是否返回 null 而不是旧值（可选，未配置则使用全局默认）。 开启可省去写路径上一次完整的旧值反序列化，详见全局同名配置。
Boolean removeReturnsNull  // remove 是否返回 null 而不是被删除的值（可选，未配置则使用全局默认）
```

## 包 `com.mcst.easyfk.chronicle.map.manager`

### ChronicleMapManager

`public class ChronicleMapManager implements DisposableBean, AutoCloseable`　注解：`@Slf4j`　Chronicle Map 管理器 - 优化版本 针对读取高性能场景优化，使用读写锁减少锁竞争 实现 DisposableBean 接口，支持 Spring 容器优雅停机

**构造器**

```java
ChronicleMapManager(ChronicleMapProperties properties)
```

**方法**

```java
void registerMap(String mapName, ChronicleMap<?, ?> map)  // 注册已创建的 Chronicle Map 实例。
<K, V> void registerMap(String mapName, ChronicleMap<?, ?> map, Class<K> keyType, Class<V> valueType)  // 注册已创建的 Chronicle Map 实例，并记录键值类型。
@SuppressWarnings("unchecked") <K, V> ChronicleMap<K, V> getMap(String mapName)  // 获取已存在的 Chronicle Map，不存在返回 null。
@SuppressWarnings("unchecked") <K, V> ChronicleMap<K, V> getOrCreateMap(String mapName, Class<K> keyType, Class<V> valueType)  // 获取或创建 Chronicle Map。 使用 ConcurrentHashMap.computeIfAbsent 保证线程安全…
@SuppressWarnings("unchecked") <K, V> ChronicleMap<K, V> getOrCreateForyMap(String mapName, Class<K> keyType, Class<V> valueType)  // 获取或创建 Chronicle Map（使用 Fory Marshaller 序列化值）。 值类型可以是任意业务对象，序列化由 ForyBytesMarshaller 透明处理。
@SuppressWarnings("unchecked") <K, V> ChronicleMap<K, V> getOrCreateForyMap(String mapName, Class<K> keyType, Class<V> valueType, long maxEntries, double avgKeySize, double avgValueSize, String filePath)  // 获取或创建 Chronicle Map（使用 Fory Marshaller + 自定义参数）。
@SuppressWarnings("unchecked") <K, V> ChronicleMap<K, V> getOrCreateMap(String mapName, Class<K> keyType, Class<V> valueType, long maxEntries, double avgKeySize, double avgValueSize, String filePath)  // 获取或创建 Chronicle Map（带自定义参数），Fory 与 3 参数版本一致按全局开关 + 值类型自动识别。
@SuppressWarnings("unchecked") <K, V> ChronicleMap<K, V> getOrCreateMap(String mapName, Class<K> keyType, Class<V> valueType, Boolean useForyMarshaller, long maxEntries, double avgKeySize, double avgValueSize, String filePath)  // 获取或创建 Chronicle Map（带自定义参数并显式指定是否使用 Fory）。
@SuppressWarnings({"rawtypes", "unchecked"}) ChronicleMap<?, ?> registerConfiguredMap(ChronicleMapDefinedInfo mapInfo)  // 按 Spring 配置创建并注册 Map。声明式与编程式创建共用相同的持久化恢复策略。
boolean containsMap(String mapName)  // 检查 Chronicle Map 是否存在
Set<String> getMapNames()  // 获取所有 Chronicle Map 名称
String getMapStats(String mapName)  // 获取 Chronicle Map 统计信息
boolean removeMap(String mapName)  // 移除 Chronicle Map
void closeAll()  // 关闭所有 Chronicle Map
void destroy()
void close()
```

## 包 `com.mcst.easyfk.chronicle.map.marshaller`

### ForyBytesMarshaller

`public class ForyBytesMarshaller<T> implements SizedWriter<T>, SizedReader<T>`　注解：`@Slf4j`　基于 Fory 的 Chronicle Map 序列化桥接器。 实现零拷贝序列化与反序列化，复用 MemoryBuffer 避免中间对象的分配…

**构造器**

```java
ForyBytesMarshaller(Class<T> type)
ForyBytesMarshaller(Class<T> type, SchemaMode schemaMode)
```

**方法**

```java
long size(T toWrite)
void write(Bytes<?> out, long size, T toWrite)
T read(Bytes<?> in, long size, T using)
```

## 包 `com.mcst.easyfk.chronicle.map.properties`

### ChronicleMapProperties

`public class ChronicleMapProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.chronicle.map")`　Chronicle Map 配置属性

**字段 / 常量**

```java
String defaultPath = "./chronicle-maps"  // 默认存储路径
long defaultMaxEntries = 100000L  // 默认最大条目数
double defaultAverageKeySize = 64.0  // 默认平均键大小（字节）
double defaultAverageValueSize = 1024.0  // 默认平均值大小（字节）
String defaultFileExtension = ".dat"  // 默认持久化文件扩展名
boolean persistenceEnabled = true  // 是否启用持久化（总开关）。关闭时所有 Map（含声明式与编程式显式 filePath）均为纯内存。
boolean recoverOnStartup = true  // 是否在启动时恢复数据
boolean compressionEnabled = false  // 是否启用压缩
boolean applyAverageSizes = true  // 是否应用平均大小参数（averageKeySize/averageValueSize）
boolean fixedSizeOptimizationEnabled = true  // 是否启用固定尺寸类型优化（对于 Long/Integer/Double/Float/Short/Byte/Character/Boolean 不设置平均大小）
boolean foryMarshallerEnabled = true  // 未显式指定是否使用 Fory 时，是否按值类型自动识别（默认 true）。 开启时 Chronicle 原生类型（基本类型及包装类、String、byte[]、BytesMarshallable、java.* 下的 Se…
SchemaMode forySchemaMode  // Fory 序列化模式，null 表示沿用 serializer-fory 的全局默认。 CONSISTENT 体积小、速度快；COMPATIBLE 容忍字段增删，但每条记录都要处理字段元数据， 读写更慢、堆分配更多…
boolean putReturnsNull = false  // put 是否返回 null 而不是旧值。 Map 契约要求 put 返回旧值，而堆外存储为此必须额外反序列化出一个完整对象再丢弃—— 这份开销落在段更新锁内，是写路径上最大的一笔无谓分配…
boolean removeReturnsNull = false  // remove 是否返回 null 而不是被删除的值。理由同 putReturnsNull。
List<ChronicleMapDefinedInfo> maps  // 自定义 Chronicle Map 配置集合
```

## 包 `com.mcst.easyfk.chronicle.map.template`

### ChronicleMapTemplate

`public record ChronicleMapTemplate(ChronicleMapManager chronicleMapManager)`　注解：`@Slf4j` `@SuppressWarnings("unused")`　Chronicle Map 模板类，提供常用操作方法。

**构造参数（record 组件）**

```java
ChronicleMapManager chronicleMapManager
```

**方法**

```java
long size(String mapName)
boolean isEmpty(String mapName)
void clear(String mapName)
String getStats(String mapName)
boolean mapExists(String mapName)
Set<String> getAllMapNames()
Set<?> keySet(String mapName)
@SuppressWarnings("unchecked") <K, V> V put(String mapName, K key, V value)
<K, V> V get(String mapName, K key)
<K, V> Map<K, V> getAll(String mapName, Collection<K> keys)  // 批量按 key 集合查询 value，一次性返回 key -> value 映射。
<K, V> void getAll(String mapName, Collection<K> keys, BiConsumer<K, V> action)  // 批量按 key 集合查询 value，流式回调消费（不返回集合，不在堆内堆积全部 value）。
<K, V> void getAllParallel(String mapName, Collection<K> keys, BiConsumer<K, V> action)  // 批量按 key 集合查询 value，多线程并行回调消费（不返回集合）。
<K, V> V getOrDefault(String mapName, K key, V defaultValue)
@SuppressWarnings("unchecked") <K, V> V putIfAbsent(String mapName, K key, V value)
<K, V> V remove(String mapName, K key)
<K, V> boolean remove(String mapName, K key, V value)
<K, V> V replace(String mapName, K key, V value)
<K, V> boolean replace(String mapName, K key, V oldValue, V newValue)
<K, V> boolean containsKey(String mapName, K key)
<K, V> void putAll(String mapName, Map<K, V> data)
@SuppressWarnings("unchecked") <K, V> V computeIfAbsent(String mapName, K key, Function<? super K, ? extends V> mappingFunction)
<K, V> V computeIfPresent(String mapName, K key, BiFunction<? super K, ? super V, ? extends V> remappingFunction)
<K, V> V getUsing(String mapName, K key, V using)
<K, V extends BytesMarshallable> void putMarshallable(String mapName, K key, V value)
<K, V extends BytesMarshallable> V getMarshallable(String mapName, K key)
<K, V extends BytesMarshallable> V getUsingMarshallable(String mapName, K key, V using)
<K, V extends BytesMarshallable> V removeMarshallable(String mapName, K key)
<K, V extends WriteMarshallable> void putWriteMarshallable(String mapName, K key, V value)
<K, V> void initMap(String mapName, Class<K> keyType, Class<V> valueType)  // 按全局 foryMarshallerEnabled（默认 true）与值类型自动选择序列化方式：业务 POJO 自动使用 Fory， Chronicle 原生类型走原生序列化…
<K, V> void initForyMap(String mapName, Class<K> keyType, Class<V> valueType)
<K, V> void initForyMap(String mapName, Class<K> keyType, Class<V> valueType, long maxEntries, double avgValueSize)
@Deprecated <K, V> void ensureForyMap(String mapName, Class<K> keyType, Class<V> valueType)
@Deprecated <K, V> void ensureForyMap(String mapName, Class<K> keyType, Class<V> valueType, long maxEntries, double avgValueSize)
<K, V> void getWithLock(String mapName, K key, Consumer<V> action)
<K, V> void updateWithLock(String mapName, K key, Consumer<V> action)  // 持有写锁读取 value，执行 action 修改后写回 map。 对于序列化型 value（Fory / BytesMarshallable 等普通 POJO），value().get() 返回的是堆上反序列化副本…
@Deprecated <K, V> V put(String mapName, Class<K> keyType, Class<V> valueType, K key, V value)
@Deprecated <K, V> V get(String mapName, Class<K> keyType, Class<V> valueType, K key)
@Deprecated <K, V> V getOrDefault(String mapName, Class<K> keyType, Class<V> valueType, K key, V defaultValue)
@Deprecated <K, V> V putIfAbsent(String mapName, Class<K> keyType, Class<V> valueType, K key, V value)
@Deprecated <K, V> V remove(String mapName, Class<K> keyType, Class<V> valueType, K key)
@Deprecated <K, V> boolean remove(String mapName, Class<K> keyType, Class<V> valueType, K key, V value)
@Deprecated <K, V> V replace(String mapName, Class<K> keyType, Class<V> valueType, K key, V value)
@Deprecated <K, V> boolean replace(String mapName, Class<K> keyType, Class<V> valueType, K key, V oldValue, V newValue)
@Deprecated <K, V> boolean containsKey(String mapName, Class<K> keyType, Class<V> valueType, K key)
@Deprecated <K, V> void putAll(String mapName, Class<K> keyType, Class<V> valueType, Map<K, V> data)
@Deprecated <K, V> V computeIfAbsent(String mapName, Class<K> keyType, Class<V> valueType, K key, Function<? super K, ? extends V> mappingFunction)
@Deprecated <K, V> V computeIfPresent(String mapName, Class<K> keyType, Class<V> valueType, K key, BiFunction<? super K, ? super V, ? extends V> remappingFunction)
@Deprecated <K, V> long size(String mapName, Class<K> keyType, Class<V> valueType)
@Deprecated <K, V> boolean isEmpty(String mapName, Class<K> keyType, Class<V> valueType)
@Deprecated <K, V> void clear(String mapName, Class<K> keyType, Class<V> valueType)
@Deprecated <K, V> Set<K> keySet(String mapName, Class<K> keyType, Class<V> valueType)
@Deprecated <K, V> V getUsing(String mapName, Class<K> keyType, Class<V> valueType, K key, V using)
@Deprecated <K, V extends BytesMarshallable> void putMarshallable(String mapName, Class<K> keyType, Class<V> valueType, K key, V value)
@Deprecated <K, V extends BytesMarshallable> V getMarshallable(String mapName, Class<K> keyType, Class<V> valueType, K key)
@Deprecated <K, V extends BytesMarshallable> V getUsingMarshallable(String mapName, Class<K> keyType, Class<V> valueType, K key, V using)
@Deprecated <K, V extends BytesMarshallable> V removeMarshallable(String mapName, Class<K> keyType, Class<V> valueType, K key)
@Deprecated <K, V extends WriteMarshallable> void putWriteMarshallable(String mapName, Class<K> keyType, Class<V> valueType, K key, V value)
@Deprecated <K, V> void getWithLock(String mapName, Class<K> keyType, Class<V> valueType, K key, Consumer<V> action)
@Deprecated <K, V> void updateWithLock(String mapName, Class<K> keyType, Class<V> valueType, K key, Consumer<V> action)
```

## 包 `com.mcst.easyfk.chronicle.queue.cleanup`

### ChronicleQueueCleanupAutoConfiguration

`public class ChronicleQueueCleanupAutoConfiguration`　注解：`@Slf4j` `@AutoConfiguration(after = ChronicleQueueAutoConfiguration.class)` `@ConditionalOnBean(ChronicleQueueManager.class)`　清理任务使用组件私有的单线程调度器，不使用 @EnableScheduling， 避免开启清理后意外激活业务中原本未启用的 @Scheduled 任务…

**方法**

```java
@Bean(name = "chronicleQueueCleanupTask") @ConditionalOnMissingBean(ChronicleQueueCleanupTask.class) ChronicleQueueCleanupTask chronicleQueueCleanupTask(ChronicleQueueManager queueManager, ChronicleQueueProperties properties, ObjectProvider<ChronicleQueueListenerRegistry> listenerRegistryProvider)
@Bean(name = "chronicleQueueCleanupScheduler") @ConditionalOnMissingBean(name = "chronicleQueueCleanupScheduler") CleanupScheduler chronicleQueueCleanupScheduler(ChronicleQueueCleanupTask task, ChronicleQueueProperties properties)  // 按配置周期执行 runOnce()（fixedDelay 语义）.
```

#### ChronicleQueueCleanupAutoConfiguration.CleanupScheduler

`public static final class CleanupScheduler implements SmartLifecycle`　组件私有调度器，随 Spring 生命周期启动/停止。

**方法**

```java
synchronized void start()
synchronized void stop()
boolean isRunning()
```

### ChronicleQueueCleanupTask

`public class ChronicleQueueCleanupTask`　注解：`@Slf4j`

**构造器**

```java
ChronicleQueueCleanupTask(ChronicleQueueManager queueManager, ChronicleQueueProperties properties, ObjectProvider<ChronicleQueueListenerRegistry> listenerRegistryProvider)
```

**方法**

```java
void runOnce()  // 调度入口。由自动装配的私有调度器 CleanupScheduler 周期调用。 异常被吞掉以保证调度永远不丢轮，单队列错误不影响其它队列。
```

## 包 `com.mcst.easyfk.chronicle.queue.config`

### ChronicleQueueAutoConfiguration

`public class ChronicleQueueAutoConfiguration`　注解：`@Slf4j` `@AutoConfiguration` `@EnableConfigurationProperties(ChronicleQueueProperties.class)`　Chronicle Queue 自动配置类 Manager 在启动时创建（并按 create-directories-on-startup 预创建声明的队列）。

**方法**

```java
@Bean @ConditionalOnMissingBean ChronicleQueueManager chronicleQueueManager(ChronicleQueueProperties chronicleQueueProperties)
@Bean @ConditionalOnMissingBean ChronicleQueueTemplate chronicleQueueTemplate(ChronicleQueueManager chronicleQueueManager)
@Bean @ConditionalOnMissingBean ChronicleQueueListenerErrorHandler chronicleQueueListenerErrorHandler()
@Bean @ConditionalOnMissingBean ChronicleQueueListenerRegistry chronicleQueueListenerRegistry(ChronicleQueueTemplate chronicleQueueTemplate, ChronicleQueueListenerErrorHandler errorHandler, ChronicleQueueProperties chronicleQueueProperties, Environment environment)
@Bean @ConditionalOnMissingBean static ChronicleQueueListenerBeanPostProcessor chronicleQueueListenerBeanPostProcessor(ObjectProvider<ChronicleQueueListenerRegistry> registryProvider)  // static 方法：BPP 需在普通 Bean 之前创建，不能因此提前实例化本配置类及其依赖。
```

### ChronicleQueueDefinedInfo

`public class ChronicleQueueDefinedInfo`　Lombok：`@Data`　Chronicle Queue 定义信息

**字段 / 常量**

```java
String queueName  // 队列名称（唯一标识）
String path  // 存储路径（可选，未配置则使用 defaultPath + queueName）
String rollCycle  // 滚动周期（可选，未配置则使用全局默认） 可选值：FAST_DAILY, FAST_HOURLY, FIVE_MINUTELY, TEN_MINUTELY, TWENTY_MINUTELY, HALF_HOURLY, WE…
long blockSize = 0  // 块大小（字节）（可选，0 表示使用全局默认）
SchemaMode forySchemaMode  // Fory 消息序列化模式（可选，未配置则使用全局 fory-schema-mode）
CleanupOverride cleanup  // 单队列 cleanup 覆写（可选，所有字段未设置时使用全局 easyfk.config.storage.queue.cleanup.* 配置）
```

#### ChronicleQueueDefinedInfo.CleanupOverride

`public static class CleanupOverride`　Lombok：`@Data`　单队列覆写：所有字段都是 boxed/nullable 类型，未设置即"沿用全局默认"， 仅显式设值的字段会替换全局默认。

**字段 / 常量**

```java
Boolean enabled  // 单队列开关：true 启用（全局关闭时也生效），false 跳过；为 null 则跟随全局 enabled。
Duration retention  // 单队列保留时长，覆盖全局 retention。
Integer reserveCyclesBeforeHead  // 单队列 writer 端额外保留 cycle 数，覆盖全局值。
Boolean requireListenerPosition  // 单队列 listener 位点未就绪时是否放弃，覆盖全局值。
Boolean allConsumersTracked  // 是否确认该队列所有需保护的消费者均已被跟踪。
List<String> protectedConsumerIds  // 需要清理任务保护的额外 NamedTailer ID。 用于进程重启后尚未重新打开、或绕过框架 API 创建的持久化消费者。
```

## 包 `com.mcst.easyfk.chronicle.queue.enums`

### TailerStartStrategy

`public enum TailerStartStrategy`　Tailer 读取起始策略 控制 Tailer 首次定位时的起始位置，类似 Kafka 的 auto.offset.reset 概念…

**枚举常量**

```java
START  // 从头开始：首次定位到队列起始位置 适用于数据重放、全量回溯场景
END  // 从尾开始：首次定位到队列末尾，只读取之后新写入的消息 适用于实时监控、只关心最新数据的场景
RESUME  // 恢复位置（默认）：恢复上次读取位置，首次使用时从队列头部开始 类似 Kafka auto.offset.reset=earliest
RESUME_LATEST  // 恢复位置或最新：恢复上次读取位置，首次使用时从队列末尾开始（只消费新消息） 类似 Kafka auto.offset.reset=latest，适合新加入的消费者不想回溯历史数据
```

## 包 `com.mcst.easyfk.chronicle.queue.listener`

### ChronicleQueueListener

`public @interface ChronicleQueueListener`　注解：`@Documented` `@Target(ElementType.METHOD)` `@Retention(RetentionPolicy.RUNTIME)`　Chronicle Queue 监听注解。

**方法**

```java
String queue()  // 队列名称。
String consumerId() default ""  // 消费者标识（必填，支持 ${...} 占位符）。 它是持久化消费位点的 NamedTailer ID，修改它等于新建一个消费者；留空会在启动时抛异常。
ChronicleQueueMessageFormat format() default ChronicleQueueMessageFormat.AUTO  // 消息读取方式。
TailerStartStrategy startStrategy() default TailerStartStrategy.RESUME  // 监听器启动时的起始消费策略。
ChronicleQueueListenerIdleMode idleMode() default ChronicleQueueListenerIdleMode.DEFAULT  // 空闲时的等待策略。
long idleTimeMs() default -1L  // 空闲等待时长，单位毫秒。 仅在 PARK 和 SLEEP 模式下生效。
String threadName() default ""  // 监听线程名称。 留空时由框架自动生成。
ChronicleQueueListenerDaemonMode daemonMode() default ChronicleQueueListenerDaemonMode.DEFAULT  // 是否将监听线程设置为 daemon。
int maxRetries() default -1  // 单条消息处理失败后的最大重试次数。 0 表示不重试。
long retryDelayMs() default -1L  // 每次重试之间的等待时间，单位毫秒。
ChronicleQueueListenerRetryBackoffMode retryBackoffMode() default ChronicleQueueListenerRetryBackoffMode.DEFAULT  // 重试等待时间的退避策略。
long maxRetryDelayMs() default -1L  // 重试等待时间的最大值，单位毫秒。 0 表示不限制最大值。
String errorQueue() default ""  // 失败消息转发的目标队列名称。 留空表示不转发。
ChronicleQueueListenerFailurePolicy failurePolicy() default ChronicleQueueListenerFailurePolicy.DEFAULT  // 重试耗尽后的处理策略（读取/反序列化失败同样适用）。 STOP 会把位点回退到失败消息并停止 listener，重新 start 或应用重启后会再次投递该消息。
int batchSize() default -1  // 批量监听时一次拉取的消息数量。 1 表示单条监听。
```

### ChronicleQueueListenerBeanPostProcessor

`public class ChronicleQueueListenerBeanPostProcessor implements BeanPostProcessor, SmartInitializingSingleton`　扫描并注册 @ChronicleQueueListener。 BPP 本身不依赖 Registry / Template / Manager（只持有 ObjectProvider），扫描到的方法先暂存…

**构造器**

```java
ChronicleQueueListenerBeanPostProcessor(ObjectProvider<ChronicleQueueListenerRegistry> registryProvider)
```

**方法**

```java
Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException
void afterSingletonsInstantiated()
```

### ChronicleQueueListenerDaemonMode

`public enum ChronicleQueueListenerDaemonMode`　listener 线程类型。

**枚举常量**

```java
DEFAULT  // 使用全局默认配置。
DAEMON  // 使用 daemon 线程。
USER_THREAD  // 使用普通用户线程。
```

### ChronicleQueueListenerErrorHandler

`public interface ChronicleQueueListenerErrorHandler`　Chronicle Queue 监听异常处理器。

**方法**

```java
void handle(String queueName, String consumerId, Method listenerMethod, Throwable throwable)  // 处理监听器执行异常。
```

### ChronicleQueueListenerErrorMessage

`public record ChronicleQueueListenerErrorMessage(String queueName, String consumerId, String listenerMethod, String threadName, ChronicleQueueMessageFormat format, boolean batch, int batchSize, String payloadType, Object payload, String errorMessage, String stackTrace, long failedAt)`　监听器失败消息封装。

**构造参数（record 组件）**

```java
String queueName
String consumerId
String listenerMethod
String threadName
ChronicleQueueMessageFormat format
boolean batch
int batchSize
String payloadType
Object payload
String errorMessage
String stackTrace
long failedAt
```

### ChronicleQueueListenerFailurePolicy

`public enum ChronicleQueueListenerFailurePolicy`　监听器处理失败后的策略。

**枚举常量**

```java
DEFAULT
CONTINUE  // 记录失败信息后，继续消费后续消息。
STOP  // 记录失败信息后，停止当前监听器。
```

### ChronicleQueueListenerIdleMode

`public enum ChronicleQueueListenerIdleMode`　监听器空闲等待策略。

**枚举常量**

```java
DEFAULT
BUSY_SPIN  // 空转，不主动让出 CPU。
YIELD  // 让出当前时间片。
PARK  // 使用 parkNanos 短暂停顿。
SLEEP  // 使用 sleep 暂停。
```

### ChronicleQueueListenerMetrics

`public record ChronicleQueueListenerMetrics(boolean enabled, int totalListeners, int newListeners, int startingListeners, int runningListeners, int pausedListeners, int stoppedListeners, int failedListeners, long totalConsumedCount, long totalRetryCount, long totalErrorCount)`　监听器聚合指标快照。

**构造参数（record 组件）**

```java
boolean enabled
int totalListeners
int newListeners
int startingListeners
int runningListeners
int pausedListeners
int stoppedListeners
int failedListeners
long totalConsumedCount
long totalRetryCount
long totalErrorCount
```

### ChronicleQueueListenerQueueMetrics

`public record ChronicleQueueListenerQueueMetrics(String queueName, int totalListeners, int runningListeners, int pausedListeners, int failedListeners, long totalConsumedCount, long totalRetryCount, long totalErrorCount)`　单个队列的监听器聚合指标。

**构造参数（record 组件）**

```java
String queueName
int totalListeners
int runningListeners
int pausedListeners
int failedListeners
long totalConsumedCount
long totalRetryCount
long totalErrorCount
```

### ChronicleQueueListenerRegistry

`public class ChronicleQueueListenerRegistry implements SmartInitializingSingleton, DisposableBean`　注解：`@Slf4j`　监听注册表，负责注册、统一启动和状态查询。

**构造器**

```java
ChronicleQueueListenerRegistry(ChronicleQueueTemplate chronicleQueueTemplate, ChronicleQueueListenerErrorHandler errorHandler, ChronicleQueueProperties properties)
ChronicleQueueListenerRegistry(ChronicleQueueTemplate chronicleQueueTemplate, ChronicleQueueListenerErrorHandler errorHandler, ChronicleQueueProperties properties, @Nullable Environment environment)
```

**方法**

```java
void register(String beanName, Object bean, Method method, ChronicleQueueListener annotation)
List<ChronicleQueueListenerStatus> getListenerStatuses()
ChronicleQueueListenerStatus getListenerStatus(String queueName, String consumerId)
ChronicleQueueListenerMetrics getListenerMetrics()
List<ChronicleQueueListenerQueueMetrics> getQueueListenerMetrics()
ChronicleQueueListenerQueueMetrics getQueueListenerMetrics(String queueName)
boolean pause(String queueName, String consumerId)
boolean resume(String queueName, String consumerId)
boolean stop(String queueName, String consumerId)
boolean start(String queueName, String consumerId)
void afterSingletonsInstantiated()
void destroy()
```

### ChronicleQueueListenerRetryBackoffMode

`public enum ChronicleQueueListenerRetryBackoffMode`　重试等待时间的退避策略。

**枚举常量**

```java
DEFAULT
FIXED  // 每次重试都使用固定等待时间。
LINEAR  // 每次重试按线性递增等待时间。
EXPONENTIAL  // 每次重试按指数递增等待时间。
```

### ChronicleQueueListenerState

`public enum ChronicleQueueListenerState`　监听容器运行状态。

**枚举常量**

```java
NEW  // 已创建，但还未启动。
STARTING  // 正在启动监听线程。
RUNNING  // 正常运行中。
PAUSED  // 已暂停，不再继续拉取消息。
STOPPED  // 已停止。
FAILED  // 因异常进入失败状态。
```

### ChronicleQueueListenerStatus

`public record ChronicleQueueListenerStatus(String queueName, String consumerId, String threadName, ChronicleQueueMessageFormat format, ChronicleQueueListenerState state, long consumedCount, long retryCount, long errorCount, long lastConsumeTime, long lastErrorTime, String lastErrorMessage)`　监听器运行状态快照。 queueName: 队列名称 consumerId: 消费者标识 threadName: 监听线程名称 format: 监听消息格式 state: 当前运行状态 consumedCount: 成功…

**构造参数（record 组件）**

```java
String queueName
String consumerId
String threadName
ChronicleQueueMessageFormat format
ChronicleQueueListenerState state
long consumedCount
long retryCount
long errorCount
long lastConsumeTime
long lastErrorTime
String lastErrorMessage
```

### ChronicleQueueMessageFormat

`public enum ChronicleQueueMessageFormat`　Chronicle Queue 监听器消息格式。

**枚举常量**

```java
AUTO  // 按方法参数类型自动推断。
TEXT  // 按文本读取。
BYTES  // 按字节数组读取。
MARSHALLABLE  // 按 BytesMarshallable 读取。
FORY  // 按 Fory 反序列化读取。
WIRE  // 直接将 Wire 回调给监听方法。
```

### LoggingChronicleQueueListenerErrorHandler

`public class LoggingChronicleQueueListenerErrorHandler implements ChronicleQueueListenerErrorHandler`　注解：`@Slf4j`　默认监听异常处理器，仅记录日志。

**方法**

```java
void handle(String queueName, String consumerId, Method listenerMethod, Throwable throwable)
```

## 包 `com.mcst.easyfk.chronicle.queue.manager`

### ChronicleQueueManager

`public class ChronicleQueueManager implements DisposableBean`　注解：`@Slf4j`　Chronicle Queue 管理器。 负责队列的创建、获取、关闭以及版本变更跟踪。

**构造器**

```java
ChronicleQueueManager(ChronicleQueueProperties properties)
```

**方法**

```java
void registerQueue(String queueName, ChronicleQueue queue)
ChronicleQueue getQueue(String queueName)
ChronicleQueue getExistingQueue(String queueName)  // 获取队列：本进程未打开但磁盘上已存在队列目录（例如由其他进程创建）时打开它； 目录不存在时返回 null，不会创建新队列。
String resolveQueuePath(String queueName)  // 队列目录：单队列 path 优先，否则 /。
SchemaMode getForySchemaMode(String queueName)  // 队列 Fory 消息的序列化模式：单队列配置优先，否则全局配置，均未配置时为 COMPATIBLE。
ChronicleQueue getOrCreateQueue(String queueName)
ChronicleQueue getOrCreateQueue(String queueName, String path, String rollCycle, long blockSize)
ExcerptAppender getAppender(String queueName)
ExcerptTailer createTailer(String queueName)
@Deprecated ExcerptTailer createTailer(String queueName, String tailerId)
ExcerptTailer createTailer(String queueName, String tailerId, NamedTailerLease lease)
void registerNamedTailer(String queueName, String tailerId)
Set<String> getNamedTailerIds(String queueName)
NamedTailerLease acquireNamedTailerLease(String queueName, String tailerId)
boolean isCleanupFileNamingSupported(String queueName)
java.util.concurrent.locks.Lock cleanupExclusiveLock(String queueName)
java.util.concurrent.locks.Lock tailerPositionLock(String queueName)
boolean containsQueue(String queueName)
Set<String> getQueueNames()
Set<String> getDefinedQueueNames()
ChronicleQueueDefinedInfo getDefinedInfo(String queueName)  // 返回该队列的 ChronicleQueueDefinedInfo（如配置了 easyfk.config.storage.queue.queues）…
void setCleanupOverride(String queueName, ChronicleQueueDefinedInfo.CleanupOverride override)  // 用代码方式钉死单个队列的 cleanup 覆写——适合"业务硬性参数不希望散落到 yml"的场景. 同名 DefinedInfo 不存在时自动创建一条仅含 cleanup 的最小条目…
long getQueueEpoch(String queueName)
boolean removeQueue(String queueName)
void closeAll()
void destroy()
```

#### ChronicleQueueManager.NamedTailerLease

`public static final class NamedTailerLease implements AutoCloseable`

**方法**

```java
synchronized void close()
```

## 包 `com.mcst.easyfk.chronicle.queue.properties`

### ChronicleQueueProperties

`public class ChronicleQueueProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.storage.queue")`　Chronicle Queue 配置属性

**字段 / 常量**

```java
String defaultPath = "./chronicle-queues"  // 默认存储路径
String defaultRollCycle = "FAST_DAILY"  // 默认滚动周期（FAST_DAILY, FAST_HOURLY, FIVE_MINUTELY, TEN_MINUTELY, TWENTY_MINUTELY, HALF_HOURLY, WEEKLY 等）
long defaultBlockSize = 0  // 默认块大小（字节），0 表示使用 Chronicle Queue 默认值
boolean createDirectoriesOnStartup = true  // 是否在启动时预创建队列目录
SchemaMode forySchemaMode = SchemaMode.COMPATIBLE  // Fory 消息默认序列化模式，默认 COMPATIBLE（容忍字段增删，适合持久化消息）。 两种模式字节流互不兼容，已有队列数据不可中途切换；可在单队列 fory-schema-mode 覆写。
List<ChronicleQueueDefinedInfo> queues  // 自定义 Chronicle Queue 配置集合
Listener listener = new Listener()  // listener 默认配置
Cleanup cleanup = new Cleanup()  // 队列滚动文件清理配置（位点感知）
```

#### ChronicleQueueProperties.Listener

`public static class Listener`　Lombok：`@Data`

**字段 / 常量**

```java
boolean enabled = true  // 是否启用 listener 自动启动
ChronicleQueueListenerIdleMode defaultIdleMode = ChronicleQueueListenerIdleMode.PARK  // 默认空闲策略
long defaultIdleTimeMs = 10L  // 默认空闲等待毫秒数
int defaultMaxRetries = 0  // 默认最大重试次数
long defaultRetryDelayMs = 100L  // 默认重试间隔毫秒数
ChronicleQueueListenerRetryBackoffMode defaultRetryBackoffMode = ChronicleQueueListenerRetryBackoffMode.FIXED  // 默认重试退避策略
long defaultMaxRetryDelayMs = 1000L  // 默认最大重试等待时间
ChronicleQueueListenerFailurePolicy defaultFailurePolicy = ChronicleQueueListenerFailurePolicy.CONTINUE  // 默认失败策略
int defaultBatchSize = 1  // 默认批量大小
boolean defaultDaemon = true  // 默认是否使用 daemon 线程
```

#### ChronicleQueueProperties.Cleanup

`public static class Cleanup`　Lombok：`@Data`　Chronicle Queue 滚动文件清理配置.

**字段 / 常量**

```java
boolean enabled = false  // 全局默认开关，默认关闭——框架不擅自删用户数据，由业务方显式开启。 单队列 cleanup.enabled 设置后优先于此值（全局关闭时单队列 true 仍会清理该队列）。
Duration checkInterval = Duration.ofHours(2)  // 调度间隔（fixedDelay 语义），默认 2 小时. 支持 ISO-8601 Duration（如 PT30M）和 Spring Boot 简写（如 1h, 30m）。
Duration initialDelay = Duration.ofMinutes(5)  // 任务首次执行的初始延迟，默认 5 分钟. 给应用启动 + listener 持久化首个位点留缓冲时间。
Duration retention = Duration.ofHours(2)  // 默认保留时长——文件 lastModified 早于"当前时间 - 该值"才允许删，默认 2 小时.
int reserveCyclesBeforeHead = 1  // writer 端额外保留的 cycle 数（除当前 cycle 外再多保留 N 个邻近 cycle），默认 1. 对低频通道意义重大：FAST_HOURLY 下 1 表示至少保留过去 1 小时的数据。
boolean requireListenerPosition = true  // 当某 listener 的 NamedTailer 还未持久化消费位点（index ≤ 0）时是否放弃整轮清理. 默认 true，确保 listener 启动慢时不丢早期数据…
boolean allConsumersTracked = false  // 是否确认所有需要保护的消费者都由本框架跟踪，或已列入 protected-consumer-ids。 默认 false…
```

## 包 `com.mcst.easyfk.chronicle.queue.template`

### ChronicleQueueConsumer

`public class ChronicleQueueConsumer implements AutoCloseable`　注解：`@Slf4j` `@SuppressWarnings("unused")`　队列消费者。 缓存一个 Tailer，用于连续读取消息。公开操作串行化，保证同一 named tailer 不会被多个线程并发推进，并使 close() 能可靠释放底层资源。

**构造器**

```java
ChronicleQueueConsumer(ChronicleQueueManager chronicleQueueManager, String queueName, String consumerId, boolean createIfMissing)
```

**方法**

```java
synchronized String consumeText()
synchronized String consumeText(TailerStartStrategy strategy)
synchronized boolean consumeText(StringBuilder destination)
synchronized <T> T consumeDocument(Function<Wire, T> reader)
synchronized <T> T consumeDocument(TailerStartStrategy strategy, Function<Wire, T> reader)
synchronized boolean poll(Consumer<Wire> reader)
synchronized boolean poll(TailerStartStrategy strategy, Consumer<Wire> reader)
synchronized List<String> consumeTextBatch(int maxCount)
synchronized List<String> consumeTextBatch(int maxCount, TailerStartStrategy strategy)
synchronized <T> List<T> consumeDocumentBatch(int maxCount, Function<Wire, T> reader)
synchronized <T> List<T> consumeDocumentBatch(int maxCount, TailerStartStrategy strategy, Function<Wire, T> reader)
synchronized byte[] consumeBytes()
synchronized byte[] consumeBytes(TailerStartStrategy strategy)
synchronized int consumeBytes(byte[] buffer)
synchronized List<byte[]> consumeBytesBatch(int maxCount)
synchronized List<byte[]> consumeBytesBatch(int maxCount, TailerStartStrategy strategy)
synchronized boolean consume(BytesMarshallable destination)
synchronized boolean consume(TailerStartStrategy strategy, BytesMarshallable destination)
synchronized <T> T consumeFory(Class<T> clazz)  // 按队列配置的 SchemaMode（默认 COMPATIBLE）读取 Fory 消息。
synchronized <T> T consumeFory(TailerStartStrategy strategy, Class<T> clazz)
synchronized <T> T consumeFory(TailerStartStrategy strategy, Class<T> clazz, SchemaMode schemaMode)  // 按指定 SchemaMode 读取 Fory 消息，null 表示使用队列配置；必须与写入端一致。
synchronized <T> List<T> consumeForyBatch(int maxCount, Class<T> clazz)
synchronized <T> List<T> consumeForyBatch(int maxCount, TailerStartStrategy strategy, Class<T> clazz)
synchronized <T> List<T> consumeForyBatch(int maxCount, TailerStartStrategy strategy, Class<T> clazz, SchemaMode schemaMode)
synchronized byte[] consumeForyPayload()  // 读取一条 Fory 消息的原始字节（不反序列化），队列无新消息返回 null。
synchronized List<byte[]> consumeForyPayloadBatch(int maxCount)
synchronized void toEnd()
synchronized void toStart()
synchronized boolean moveToIndex(long index)
synchronized long index()
synchronized long lastReadStartIndex()  // 最近一次读取操作（单条或批量）读到的第一条消息的 index；最近一次读取未读到消息时为 -1。
synchronized boolean rewindToLastRead()  // 把位点回退到最近一次读取的第一条消息，下次读取（含重启后的同名 NamedTailer）会重新读到它。
synchronized void close()
```

### ChronicleQueuePublisher

`public class ChronicleQueuePublisher implements AutoCloseable`　注解：`@Slf4j` `@SuppressWarnings("unused")`　队列发布器。 缓存一个 Appender，队列重建后重新创建。公开操作串行化，确保共享发布器不会并发使用 Chronicle Queue 的非线程安全 Appender，并且 close() 能可靠释放资源。

**构造器**

```java
ChronicleQueuePublisher(ChronicleQueueManager chronicleQueueManager, String queueName)
```

**方法**

```java
synchronized long publishText(String text)
synchronized long publishDocument(Consumer<WireOut> writer)
synchronized long publishKeyValue(String key, String value)
synchronized long publishBytes(byte[] data)
synchronized long publishFory(Object value)  // 按队列配置的 SchemaMode（默认 COMPATIBLE）写入 Fory 消息。
synchronized long publishFory(Object value, SchemaMode schemaMode)  // 按指定 SchemaMode 写入 Fory 消息，读取端必须使用相同模式。
synchronized long publish(BytesMarshallable value)
synchronized long lastIndex()
synchronized void close()
```

### ChronicleQueueTemplate

`public class ChronicleQueueTemplate implements DisposableBean`　注解：`@Slf4j` `@SuppressWarnings("unused")`　Chronicle Queue 模板。 保留原有的简单接口，并在内部复用发布器和消费者。

**构造器**

```java
ChronicleQueueTemplate(ChronicleQueueManager chronicleQueueManager)
```

**方法**

```java
ChronicleQueuePublisher openPublisher(String queueName)
ChronicleQueuePublisher publisher(String queueName)
ChronicleQueueConsumer openConsumer(String queueName, String consumerId)
ChronicleQueueConsumer stream(String queueName, String consumerId)
ChronicleQueueConsumer openConsumer(String queueName)
long writeText(String queueName, String text)
long writeDocument(String queueName, Consumer<WireOut> writer)
long writeKeyValue(String queueName, String key, String value)
String readText(String queueName, String tailerId)
String readText(String queueName, String tailerId, TailerStartStrategy strategy)
boolean readText(String queueName, String tailerId, StringBuilder destination)
<T> T readDocument(String queueName, String tailerId, Function<Wire, T> reader)
<T> T readDocument(String queueName, String tailerId, TailerStartStrategy strategy, Function<Wire, T> reader)
List<String> readTextBatch(String queueName, String tailerId, int maxCount)
List<String> readTextBatch(String queueName, String tailerId, int maxCount, TailerStartStrategy strategy)
<T> List<T> readDocumentBatch(String queueName, String tailerId, int maxCount, Function<Wire, T> reader)
<T> List<T> readDocumentBatch(String queueName, String tailerId, int maxCount, TailerStartStrategy strategy, Function<Wire, T> reader)
String peekLastText(String queueName)
String peekFirstText(String queueName)
String peekTextAtIndex(String queueName, long index)
void toEnd(String queueName, String tailerId)
void toStart(String queueName, String tailerId)
boolean moveToIndex(String queueName, String tailerId, long index)
long getTailerIndex(String queueName, String tailerId)
ExcerptAppender getAppender(String queueName)
ExcerptTailer createTailer(String queueName)
@Deprecated ExcerptTailer createTailer(String queueName, String tailerId)
ChronicleQueue getQueue(String queueName)
ChronicleQueue getOrCreateQueue(String queueName)
boolean queueExists(String queueName)
Set<String> getAllQueueNames()
long writeBytes(String queueName, byte[] data)
byte[] readBytes(String queueName, String tailerId)
byte[] readBytes(String queueName, String tailerId, TailerStartStrategy strategy)
int readBytes(String queueName, String tailerId, byte[] buffer)
List<byte[]> readBytesBatch(String queueName, String tailerId, int maxCount)
List<byte[]> readBytesBatch(String queueName, String tailerId, int maxCount, TailerStartStrategy strategy)
byte[] peekLastBytes(String queueName)
byte[] peekFirstBytes(String queueName)
byte[] peekBytesAtIndex(String queueName, long index)
long writeFory(String queueName, Object value)  // 按队列配置的 SchemaMode（单队列 fory-schema-mode > 全局，默认 COMPATIBLE）写入 Fory 消息。
long writeFory(String queueName, Object value, SchemaMode schemaMode)  // 按指定 SchemaMode 写入 Fory 消息，读取端必须使用相同模式。
SchemaMode getForySchemaMode(String queueName)  // 队列 Fory 消息实际使用的默认 SchemaMode。
long writeObject(String queueName, BytesMarshallable value)
boolean readObject(String queueName, String tailerId, BytesMarshallable destination)
<T> T readFory(String queueName, String tailerId, Class<T> clazz)
<T> T readFory(String queueName, String tailerId, TailerStartStrategy strategy, Class<T> clazz)
<T> T readFory(String queueName, String tailerId, TailerStartStrategy strategy, Class<T> clazz, SchemaMode schemaMode)
<T> List<T> readForyBatch(String queueName, String tailerId, int maxCount, Class<T> clazz)
<T> List<T> readForyBatch(String queueName, String tailerId, int maxCount, TailerStartStrategy strategy, Class<T> clazz)
<T> List<T> readForyBatch(String queueName, String tailerId, int maxCount, TailerStartStrategy strategy, Class<T> clazz, SchemaMode schemaMode)
<T> T peekLastFory(String queueName, Class<T> clazz)
<T> T peekLastFory(String queueName, Class<T> clazz, SchemaMode schemaMode)
<T> T peekFirstFory(String queueName, Class<T> clazz)
<T> T peekFirstFory(String queueName, Class<T> clazz, SchemaMode schemaMode)
<T> T peekForyAtIndex(String queueName, long index, Class<T> clazz)
<T> T peekForyAtIndex(String queueName, long index, Class<T> clazz, SchemaMode schemaMode)
void clearSharedResources()
@Deprecated void clearCurrentThreadResources()
void destroy()
```
