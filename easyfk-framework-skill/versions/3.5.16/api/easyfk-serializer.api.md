# easyfk-serializer API 签名速查（easyfk 3.5.16）

> 坐标：`com.mcst:serializer-base、com.mcst:serializer-fory`　源码：`easyfk-base/easyfk-serializer/serializer-base`、`easyfk-base/easyfk-serializer/serializer-fory`
> 由 `scripts/gen-api.py` 从 10 个源文件自动提取，共 10 个类型、39 个方法/构造器、8 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-serializer-skill.md](../modules/easyfk-serializer-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 配置项（@ConfigurationProperties）

### `easyfk.config.serializer` ← SerializerProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `pre-register` | `Boolean` | `Boolean.TRUE` | 是否预注册 如果为true，则会在启动时预注册所有需要序列化的类 如果为false，则会在使用时动态注册 |
| `cross-language` | `Boolean` | `Boolean.FALSE` | 是否开启跨语言 如果为true，则会在初始化时创建跨语言的序列化器 |
| `scan-packages` | `List<String>` | `new ArrayList<>()` | 需要扫描的包路径列表 |

### `easyfk.config.serializer.fory` ← ForySerializerProperties

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `compatible-mode` | `CompatibleMode` | `CompatibleMode.SCHEMA_CONSISTENT` | 默认 Schema 模式。 组件同时支持 SCHEMA_CONSISTENT 与 COMPATIBLE 两种模式， 调用方可在每次序列化/反序列化时通过 SchemaMode 参数动态指定… |
| `require-class-registration` | `Boolean` | `Boolean.TRUE` | 是否要求类必须注册后才能序列化/反序列化，默认 true。 关闭后字节流中写明的任意类都可以在反序列化时被实例化，存在反序列化攻击风险， 只有在确定只处理本系统写入的数据时才可以关闭。 |


## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `serializer-base` | `com.mcst.easyfk.serializer.base.config.SerializerAutoConfiguration` |
| `serializer-fory` | `com.mcst.easyfk.serializer.fory.config.ForySerializerAutoConfiguration` |

## 类型索引

- `com.mcst.easyfk.serializer.base`：[SerializerClassRegister](#serializerclassregister)
- `com.mcst.easyfk.serializer.base.config`：[SerializerAutoConfiguration](#serializerautoconfiguration)
- `com.mcst.easyfk.serializer.base.init`：[SerializerInitializer](#serializerinitializer)
- `com.mcst.easyfk.serializer.base.properties`：[SerializerProperties](#serializerproperties)
- `com.mcst.easyfk.serializer.fory`：[ByteProcessor](#byteprocessor)、[ForySerializer](#foryserializer)、[ForySerializerClassRegister](#foryserializerclassregister)、[SchemaMode](#schemamode)
- `com.mcst.easyfk.serializer.fory.config`：[ForySerializerAutoConfiguration](#foryserializerautoconfiguration)
- `com.mcst.easyfk.serializer.fory.properties`：[ForySerializerProperties](#foryserializerproperties)

## 包 `com.mcst.easyfk.serializer.base`

### SerializerClassRegister

`public interface SerializerClassRegister`　序列化类注册器函数接口 用于项目初始化时提供需要注册到序列化器的类， 可通过手动指定或扫描包路径的方式获取类列表

**方法**

```java
default void registerClass(List<Class<?>> classes)
```

## 包 `com.mcst.easyfk.serializer.base.config`

### SerializerAutoConfiguration

`public class SerializerAutoConfiguration`　注解：`@AutoConfiguration` `@EnableConfigurationProperties(SerializerProperties.class)`　序列化器自动配置类 通过 META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports 自动加载…

**方法**

```java
@Bean SerializerInitializer serializerInitializer()  // 注册序列化器初始化器
```

## 包 `com.mcst.easyfk.serializer.base.init`

### SerializerInitializer

`public class SerializerInitializer implements InitializingBean`　注解：`@Slf4j`

**方法**

```java
void afterPropertiesSet() throws Exception
```

## 包 `com.mcst.easyfk.serializer.base.properties`

### SerializerProperties

`public class SerializerProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.serializer")`

**字段 / 常量**

```java
Boolean preRegister = Boolean.TRUE  // 是否预注册 如果为true，则会在启动时预注册所有需要序列化的类 如果为false，则会在使用时动态注册
Boolean crossLanguage = Boolean.FALSE  // 是否开启跨语言 如果为true，则会在初始化时创建跨语言的序列化器
List<String> scanPackages = new ArrayList<>()  // 需要扫描的包路径列表
```

## 包 `com.mcst.easyfk.serializer.fory`

### ByteProcessor

`public interface ByteProcessor`　注解：`@FunctionalInterface`

**方法**

```java
void process(byte[] data, int offset, int length)
```

### ForySerializer

`public class ForySerializer`　注解：`@Slf4j` `@SuppressWarnings("unused")`

**方法**

```java
static void init(SerializerProperties props, ForySerializerProperties foryProps)  // 非 Spring 环境下手动初始化，必须在首次调用其它方法之前执行
static boolean isInitialized()  // 是否已完成初始化
static void serialize(Object obj, MemoryBuffer buffer)
static void serialize(Object obj, MemoryBuffer buffer, SchemaMode mode)
static void serialize(Object obj, BiConsumer<byte[], Integer> processor)
static void serialize(Object obj, BiConsumer<byte[], Integer> processor, SchemaMode mode)
static void serialize(Object obj, Consumer<byte[]> processor)
static void serialize(Object obj, Consumer<byte[]> processor, SchemaMode mode)
static byte[] serialize(Object obj)
static byte[] serialize(Object obj, SchemaMode mode)
static byte[] serializeXLang(Object obj)
static Object deserialize(MemoryBuffer buffer)
static Object deserialize(MemoryBuffer buffer, SchemaMode mode)
static <T> T deserialize(MemoryBuffer buffer, Class<T> clazz)
static <T> T deserialize(MemoryBuffer buffer, Class<T> clazz, SchemaMode mode)
static Object deserialize(byte[] bytes)
static Object deserialize(byte[] bytes, SchemaMode mode)
static <T> T deserialize(byte[] bytes, Class<T> clazz)
static <T> T deserialize(byte[] bytes, Class<T> clazz, SchemaMode mode)
static void serializeToProcessor(Object obj, ByteProcessor processor)
static void serializeToProcessor(Object obj, ByteProcessor processor, SchemaMode mode)
@SuppressWarnings("unchecked") static <T> T deserializeXLang(byte[] bytes)  // XLANG 模式按名字识别类型，读端必须注册过对应的类，否则无法还原。 动态注册模式下请优先使用 deserializeXLang(byte[], Class)。
static <T> T deserializeXLang(byte[] bytes, Class<T> clazz)
static <T> T deepCopy(T obj)
static <T> T deepCopy(T obj, SchemaMode mode)
static void register(Class<?> clazz)
static void registerAll(Collection<Class<?>> classes)
static ThreadSafeFory getJavaFory()  // 返回当前生效、适合当前线程类型的实例（平台线程为 ThreadLocalFory，虚拟线程为对象池）。 注册表变化后实例会被替换，不要长期持有返回值，不要跨线程类型传递，也不要直接在其上注册类
static ThreadSafeFory getJavaFory(SchemaMode mode)
static ThreadSafeFory getXLangFory()  // 未开启跨语言时返回 null，其余约定同 getJavaFory()
```

### ForySerializerClassRegister

`public class ForySerializerClassRegister implements SerializerClassRegister`

**方法**

```java
void registerClass(List<Class<?>> classes)  // 走批量注册：扫描结果的顺序不固定，registerAll 会先按类名排序再分配类型 ID， 保证同一批类在不同进程得到相同的 ID，并在 ID 冲突时顺延而不是让启动失败。
```

### SchemaMode

`public enum SchemaMode`　序列化 Schema 模式，供调用方按场景动态选择。 两种模式产出的字节流互不兼容：反序列化必须使用与序列化时相同的模式。

**枚举常量**

```java
CONSISTENT(CompatibleMode.SCHEMA_CONSISTENT)
COMPATIBLE(CompatibleMode.COMPATIBLE)
```

**字段 / 常量**

```java
final CompatibleMode compatibleMode
```

**构造器**

```java
SchemaMode(CompatibleMode compatibleMode)
```

**方法**

```java
CompatibleMode toCompatibleMode()
static SchemaMode fromCompatibleMode(CompatibleMode compatibleMode)
```

## 包 `com.mcst.easyfk.serializer.fory.config`

### ForySerializerAutoConfiguration

`public class ForySerializerAutoConfiguration`　注解：`@AutoConfiguration` `@EnableConfigurationProperties(ForySerializerProperties.class)`　Fory 序列化器自动配置类 通过 META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports 自动加载…

**方法**

```java
@Bean ForySerializerClassRegister forySerializerClassRegister()  // 注册 Fory 序列化类注册器 该 Bean 会被 SerializerInitializer 自动发现并调用， 用于将扫描到的序列化类注册到 Fory 序列化器中
```

## 包 `com.mcst.easyfk.serializer.fory.properties`

### ForySerializerProperties

`public class ForySerializerProperties`　Lombok：`@Data`　注解：`@ConfigurationProperties(prefix = "easyfk.config.serializer.fory")`

**字段 / 常量**

```java
CompatibleMode compatibleMode = CompatibleMode.SCHEMA_CONSISTENT  // 默认 Schema 模式。 组件同时支持 SCHEMA_CONSISTENT 与 COMPATIBLE 两种模式， 调用方可在每次序列化/反序列化时通过 SchemaMode 参数动态指定…
Boolean requireClassRegistration = Boolean.TRUE  // 是否要求类必须注册后才能序列化/反序列化，默认 true。 关闭后字节流中写明的任意类都可以在反序列化时被实例化，存在反序列化攻击风险， 只有在确定只处理本系统写入的数据时才可以关闭。
```
