# EasyFK Fory 序列化组件使用手册

本文档以 `serializer-fory` 当前代码为准。模块基于 Apache Fory `1.7.8`，提供 Java 模式序列化、可选的 XLANG 模式、类预注册和可复用缓冲区 API。

## 1. 环境与依赖

- Java：21
- Apache Fory：1.7.8
- Spring Boot：由 EasyFK 依赖平台统一管理
- Maven 坐标：`com.mcst:serializer-fory:3.5.16`

Gradle：

```gradle
dependencies {
    implementation 'com.mcst:serializer-fory:3.5.16'
}
```

模块通过 Spring Boot 自动配置加载，并依赖 `serializer-base` 提供的 `SerializerProperties`。`ForySerializer` 虽然是静态工具类，但初始化时会通过 `SpringUtil` 从 Spring 容器获取该配置，因此不能在 Spring 容器准备完成前调用。

## 2. 配置

```yaml
easyfk:
  config:
    serializer:
      # 默认 true；启动时扫描并预注册 @SerializableClass
      pre-register: true
      # 默认 false；是否创建 XLANG Fory 实例
      cross-language: false
      # 除固定扫描的 com.mcst 外，追加扫描的业务包
      scan-packages:
        - com.example.project.dto
      fory:
        # 不传 SchemaMode 参数时使用的默认模式，默认 SCHEMA_CONSISTENT
        # 可选：SCHEMA_CONSISTENT / COMPATIBLE
        compatible-mode: SCHEMA_CONSISTENT
        # 默认 true；字节流中出现的未注册类型会被拒绝（安全策略），见 5.4
        require-class-registration: true
```

配置在 `ForySerializer` 第一次使用时读取并缓存，运行期间修改不会重建底层实例。

### 2.2 Schema 模式与动态切换

组件在初始化时会**同时构建两个 Java 模式实例**，调用方可在每次调用时通过 `SchemaMode` 参数动态选择，而不必用配置写死：

| `SchemaMode` | 底层 `CompatibleMode` | 特点 | 推荐场景 |
|---|---|---|---|
| `CONSISTENT` | `SCHEMA_CONSISTENT` | 不写字段元信息，体积最小、速度最快；要求两端 schema 完全一致 | RPC 等同版本部署、生命周期短的传输 |
| `COMPATIBLE` | `COMPATIBLE` | 写入字段元信息，容忍字段增删 | 缓存 / 持久化等数据比代码活得久、需要 schema 演进 |

```java
import com.mcst.easyfk.serializer.fory.SchemaMode;

// RPC：一致模式
byte[] rpc = ForySerializer.serialize(dto, SchemaMode.CONSISTENT);
UserDto a = ForySerializer.deserialize(rpc, UserDto.class, SchemaMode.CONSISTENT);

// 缓存：兼容模式
byte[] cache = ForySerializer.serialize(dto, SchemaMode.COMPATIBLE);
UserDto b = ForySerializer.deserialize(cache, UserDto.class, SchemaMode.COMPATIBLE);

// 不传 SchemaMode → 使用配置的默认模式（默认 SCHEMA_CONSISTENT）
byte[] def = ForySerializer.serialize(dto);
```

> **重要纪律**：两种模式产出的字节流**互不兼容**，且字节里不含模式标识，框架无法自动识别。**用哪种模式写，就必须用哪种模式读**——建议 RPC 链路统一走 `CONSISTENT`、缓存链路统一走 `COMPATIBLE`，不要交叉。
>
> `compatible-mode` 配置仅决定“不传参”时的默认模式，并不再限制只能使用一种模式。

### 2.1 类预注册

`pre-register` 默认为 `true`。启动时会扫描以下范围内带有 `@SerializableClass` 的类：

1. 固定包 `com.mcst`；
2. `scan-packages` 配置的附加包。

```java
import com.mcst.easyfk.core.annotation.SerializableClass;

@SerializableClass
public class UserDto {
    private Long id;
    private String name;
    // getter/setter
}
```

预注册类在 Java 模式下使用根据全限定类名计算的整型类型 ID，范围为 256～32766；XLANG 开启时，还会以 `Class.getSimpleName()` 注册跨语言类型名。

> 当前实现限制：不要直接配置 `pre-register: false`。`SerializerAutoConfiguration` 与 `ForySerializerAutoConfiguration` 都受该属性控制，关闭后 `SerializerProperties` Bean 也不会自动创建，首次调用 `ForySerializer` 会初始化失败。只有应用自行提供 `SerializerProperties` Bean 时，代码中的运行时注册分支才可用。

## 3. 基础 API

导入工具类：

```java
import com.mcst.easyfk.serializer.fory.ForySerializer;
```

### 3.1 字节数组

```java
byte[] data = ForySerializer.serialize(userDto);

UserDto restored = ForySerializer.deserialize(data, UserDto.class);

Object restoredObject = ForySerializer.deserialize(data);
```

带 `Class<T>` 的重载通过 `Class.cast()` 检查反序列化结果类型，并且会在读取前确保该类已注册（见 5.3），因此在动态注册模式下应优先使用它，而不是不带类型的 `deserialize(data)`。

> 上述及后续所有序列化 / 反序列化 API 均提供一个额外的 `SchemaMode` 参数重载（如 `serialize(obj, SchemaMode.COMPATIBLE)`、`deserialize(bytes, UserDto.class, SchemaMode.COMPATIBLE)`）。不带该参数时使用配置的默认模式，详见 2.2。

### 3.2 深拷贝

```java
UserDto copy = ForySerializer.deepCopy(userDto);

// 也可指定模式
UserDto copy2 = ForySerializer.deepCopy(userDto, SchemaMode.COMPATIBLE);
```

该方法直接调用 Fory 的 `copy` API。代码未对其与“序列化后再反序列化”的性能差异作固定保证。

### 3.3 MemoryBuffer

```java
import org.apache.fory.memory.MemoryBuffer;
import org.apache.fory.memory.MemoryUtils;

MemoryBuffer buffer = MemoryUtils.buffer(4096);
ForySerializer.serialize(userDto, buffer);

buffer.readerIndex(0);
UserDto restored = ForySerializer.deserialize(buffer, UserDto.class);
```

`serialize(Object, MemoryBuffer)` 从缓冲区当前的 `writerIndex` 继续写入，不会替调用方重置索引；需要覆盖原数据时，应先自行设置 `writerIndex(0)`。反序列化从当前 `readerIndex` 读取。

## 4. 回调式缓冲区 API

### 4.1 BiConsumer

```java
ForySerializer.serialize(userDto, (data, length) -> {
    output.write(data, 0, length);
});
```

回调收到内部 `MemoryBuffer` 的堆数组和有效长度。该数组由当前线程复用，只能在回调执行期间使用；不得保存引用、异步使用或修改有效数据。若需要长期持有，请在回调内复制。

### 4.2 Consumer

```java
ForySerializer.serialize(userDto, data -> {
    service.process(data);
});
```

此重载等价于 `processor.accept(ForySerializer.serialize(obj))`，回调收到长度精确的独立数组，回调结束后可以安全持有，但会产生一次数组分配和复制。

### 4.3 ByteProcessor

```java
import com.mcst.easyfk.serializer.fory.ByteProcessor;

ForySerializer.serializeToProcessor(userDto, (data, offset, length) -> {
    output.write(data, offset, length);
});
```

当前实现传入的 `offset` 为 `0`，`length` 为有效数据长度。底层数组的生命周期约束与 `BiConsumer` 重载相同。

内部缓冲区初始为 4 KiB。当前线程缓存的缓冲区若扩容到 1 MiB 以上，会在本次调用结束后替换为新的 4 KiB 缓冲区。回调内发生嵌套序列化时，内层调用会借用独立缓冲区，避免覆盖外层数据。

## 5. 类注册

### 5.1 手动注册

```java
ForySerializer.register(UserDto.class);
```

该方法注册 Java 模式类型；如果 XLANG 已开启，也会同时注册 XLANG 类型。传入 `null` 时直接返回。

### 5.2 批量注册

```java
ForySerializer.registerAll(List.of(UserDto.class, OrderDto.class));
```

批量注册会过滤 `null`、去重，并按类的全限定名排序。若两个类计算出相同的 Java 类型 ID，批量注册会向后查找可用 ID；单个 `register` 或运行时注册遇到同类冲突时会抛出 `IllegalStateException`，错误信息会提示预先调用 `registerAll`。

启动时的预注册（`ForySerializerClassRegister`）走的就是批量注册，因此扫描顺序不会影响类型 ID 的分配结果。

预注册开启时，未标注 `@SerializableClass` 的类不会在启动时注册，首次使用时的行为见 5.4。

### 5.3 读写两端必须注册同一批类

已注册的类在字节流中写入的是整型类型 ID，未注册的类写入的是类名。这意味着**写端注册、读端没注册**时，读端拿到类型 ID 却查不到对应的类，反序列化会失败。典型场景是动态注册模式下，某个进程只读缓存、或重启后先读再写。

为此，带 `Class` 参数的反序列化重载（`deserialize(bytes, Class)`、`deserialize(buffer, Class)`、`deserializeXLang(bytes, Class)`）会在读取前补齐注册。不带 `Class` 的重载无法预知类型，此时请保持 `pre-register: true`，或由调用方在读取前显式调用 `register` / `registerAll`。

### 5.4 首次使用时注册与实例重建

Apache Fory 在实例第一次序列化 / 反序列化 / 拷贝之后会冻结注册，已投入使用的实例不能再注册新类。组件因此维护一份注册表，注册表变化时按完整注册表构建新实例并整体替换，进行中的调用继续使用旧实例，不受影响。

| `require-class-registration` | 未预注册的顶层类（待序列化对象的类、反序列化目标类、`deepCopy` 的对象类） | 字节流中嵌套的未注册类 |
|---|---|---|
| `true`（默认） | 首次使用时自动分配 typeId 并注册，重建 Java 实例，打印 WARN 日志 | 拒绝，需预注册 |
| `false` | 不注册，按类名写入，不重建 | 按类名写入 / 还原 |

- Fory 内置类型（`String`、`List.of(...)`、`LocalDate` 等 JDK 常用类型）不会触发注册或重建。
- 启动阶段的预注册发生在实例首次构建之前，不会触发重建；首次使用之后再调用 `register` / `registerAll` 增加新类会触发一次重建。
- 重建会重新创建 Fory 实例，各线程之后的首次调用需要重新创建本线程的实例，属于一次性开销。WARN 日志中出现的类建议补上 `@SerializableClass`，让它们在启动时注册。
- 运行时注册时类型 ID 冲突无法自动避让，会抛出 `IllegalStateException`，与 5.2 相同。

## 6. XLANG 跨语言模式

先启用配置：

```yaml
easyfk:
  config:
    serializer:
      cross-language: true
```

调用专用 API：

```java
byte[] data = ForySerializer.serializeXLang(userDto);
UserDto restored = ForySerializer.deserializeXLang(data, UserDto.class);
```

注意事项：

- XLANG 与 Java 模式使用不同的 `ThreadSafeFory` 实例和不同的二进制协议，不要混用两组序列化/反序列化 API。
- XLANG 未开启时调用上述 API，会抛出 `UnsupportedOperationException`。
- EasyFK 显式注册 XLANG 类型时使用 Java 简单类名，例如 `UserDto`。通信对端必须按 Apache Fory 的 XLANG 规则配置兼容的类型映射。
- `deserializeXLang(byte[], Class)` 会在读取前确保该类的 XLANG 类型名已注册，并用 `Class.cast()` 校验结果。
- `deserializeXLang(byte[])` 的泛型类型只用于调用端类型推断，方法内部是未经运行时校验的强制转换；读端未注册过对应类型名时无法还原，动态注册模式下请使用带 `Class` 的重载。

## 7. 边界行为

| 调用 | 当前行为 |
|---|---|
| `serialize(null)` | 返回共享的空 `byte[]` |
| `serialize(null, ...)` | 不写入、不执行回调 |
| `deserialize(null)` 或反序列化空数组 | 返回 `null` |
| 反序列化时 `clazz` 传 `null` | 抛出 `IllegalArgumentException`，先于空数据判断 |
| `deserialize(MemoryBuffer)` 的参数为 `null` 或无剩余数据 | 返回 `null` |
| `deepCopy(null)` | 返回 `null` |
| `register(null)` | 直接返回 |
| `registerAll(null)` 或空集合 | 直接返回 |

序列化、反序列化以及回调抛出的其他异常不会被包装，由调用方处理。

## 8. 实现约束

- 组件同时持有 `CONSISTENT` 与 `COMPATIBLE` 两个 Java 模式实例，另加可选的 XLANG 实例，静态 API 可并发调用。实例在第一次序列化 / 反序列化时才构建。
- 每个实例按调用线程类型选择实现，两者配置与注册表相同，产出的字节流完全一致：
  - 平台线程使用 `ThreadLocalFory`，每个线程独占一个 Fory 实例，无竞争。新线程首次使用时创建实例（复用已生成的序列化器，约百微秒级，每个实例约 20 KB）。
  - 虚拟线程使用 Fory 对象池（`buildThreadSafeFory`），避免为每个短命的虚拟线程创建实例；对象池在首次被虚拟线程使用时才构建。
  - Fory 对象池每次借还都要在相邻槽位上做原子操作，多线程下缓存行争用严重，吞吐几乎不随线程数增长，因此不用于平台线程。
- 类注册会**同时注册到两个 Java 实例**，且使用相同的整型 typeId，保证同一份数据在两种模式间 typeId 一致。
- 各实例均配置为 `withRefTracking(false)`。对象图不要包含循环引用；共享引用在反序列化后也不保证保持对象同一性。
- `requireClassRegistration` 由 `easyfk.config.serializer.fory.require-class-registration` 控制，默认 `true`。
- 实例使用初始化时 Spring 容器的类加载器（非 Spring 环境为初始化线程的上下文类加载器），不受首次调用线程影响。
- `serialize(Object)` 使用 Fory 实例自带的缓冲区，只分配一次结果数组；回调式序列化使用 `ThreadLocal<MemoryBuffer>` 复用缓冲区，不分配结果数组。
- `getJavaFory()` / `getJavaFory(SchemaMode)` 与 `getXLangFory()` 会暴露当前生效、适合当前线程类型的底层实例，适合确有需要的高级用法。注册表变化后实例会被替换，不要长期持有、不要跨线程类型传递，也不要直接在其上注册类。`getJavaFory()` 不带参数时返回默认模式实例；XLANG 未开启时，`getXLangFory()` 返回 `null`。
