# easyfk-serializer Skill 参考文档

> 所属项目：`easyfk-base`　子模块：`serializer-base`、`serializer-fory`
> 坐标：`com.mcst:serializer-base:3.5.16`、`com.mcst:serializer-fory:3.5.16`
> 依据：两个子模块全部源码（12 个文件），对齐 `fory序列化使用手册.md`、`fory序列化特点.md`、`核心模块说明.md`。
> 以源码为准；差异见文末「复查记录」。

---

## 1. 模块定位

| 子模块 | 职责 |
|---|---|
| `serializer-base` | 抽象层：配置 `SerializerProperties`、SPI 接口 `SerializerClassRegister`、启动时扫描 `@SerializableClass` 并分发给所有注册器的 `SerializerInitializer` |
| `serializer-fory` | 实现层：基于 **Apache Fory 1.7.8**（`org.apache.fory:fory-core`，版本写死在模块 `build.gradle`）的静态工具类 `ForySerializer`，加上 SPI 实现 `ForySerializerClassRegister` |

依赖关系：`serializer-fory` → `serializer-base` → `easyfk-core`（core 是 `compileOnly`，需要由应用自行提供）。

适用场景：缓存值、消息体、本地持久化（Chronicle）、RPC 载荷等**进程间的 Java 对象二进制编码**。框架内的使用方有 chronicle-map、chronicle-queue、mq-kafka、aeron-codec-fory。

**不适用于**：对外 HTTP JSON 接口（用 Jackson / fastjson2），以及反序列化来源不可信的数据（见 §6 安全）。

---

## 2. 引入与自动配置

```groovy
implementation platform('com.mcst:easyfk-dependencies:3.5.16')
implementation 'com.mcst:easyfk-core'
implementation 'com.mcst:serializer-fory'      // 会传递 serializer-base 和 fory-core
```

两个自动配置都通过 `META-INF/spring/...AutoConfiguration.imports` 加载，**没有开关**，引入即生效（`pre-register` 只影响是否做启动扫描，见 §3）：

| 自动配置 | 注册的 Bean |
|---|---|
| `SerializerAutoConfiguration` | `SerializerProperties`、`SerializerInitializer` |
| `ForySerializerAutoConfiguration` | `ForySerializerProperties`、`ForySerializerClassRegister` |

`ForySerializer` 是静态工具类，初始化有两种方式：

- **Spring 环境（默认）**：第一次调用时，通过 Hutool `SpringUtil` 从容器中获取上面两个配置 Bean 并构建 Fory 实例。Hutool 5.8.48 自带 Boot 3 的 AutoConfiguration 声明，`@SpringBootApplication` 应用中会自动注册 `SpringUtil`。容器未启动（main 方法、普通单元测试、Bean 构造器中提前调用）时会抛 `IllegalStateException`，提示改用手动初始化。
- **非 Spring 环境**：在首次使用前调用 `ForySerializer.init(SerializerProperties, ForySerializerProperties)`（后者可为 null，使用默认配置）。重复调用或已被懒加载初始化后再调用会抛 `IllegalStateException`；`ForySerializer.isInitialized()` 可查询状态。非 Spring 环境没有启动扫描，需要把 `SerializerProperties.preRegister` 设为 false（按需注册），或自行调用 `registerAll`。

初始化失败**不会缓存失败状态**：每次调用都会重新尝试，并抛出带原始原因（cause）的 `IllegalStateException`；问题排除后（例如容器启动完成）即可恢复。初始化成功后**配置**不再重新读取（运行期改配置不生效），但**类注册表**可以继续变化——新增注册会按完整注册表重建 Fory 实例并整体替换，进行中的调用继续用旧实例（见 §4）。

初始化时还会**固定类加载器**（取初始化线程的上下文类加载器，Spring 环境取容器 ClassLoader）。按类名还原类型、JIT 编译都依赖它，所以业务类必须在这个 ClassLoader 可见；热部署、多个类加载器共存的环境要留意。

---

## 3. 配置

```yaml
easyfk:
  config:
    serializer:
      pre-register: true          # 默认 true，启动时扫描 @SerializableClass 并注册
      cross-language: false       # 默认 false。为 true 时额外构建 XLANG 实例
      scan-packages:              # 固定扫描 com.mcst，业务包必须在这里追加
        - com.example.order
      fory:
        compatible-mode: SCHEMA_CONSISTENT   # 不传 SchemaMode 时的默认模式：SCHEMA_CONSISTENT / COMPATIBLE
        require-class-registration: true     # 默认 true，未注册的类不能序列化/反序列化（见 §6）
```

`pre-register` 的两种模式：

- `true`（默认）：启动时由 `SerializerInitializer` 扫描并批量注册。
- `false`（按需注册）：配置 Bean 照常创建，只是跳过启动扫描。
- 两种模式下，调用方显式给出的顶层类型都会被自动补注册：序列化时注册对象自身的类，带 `Class` 的反序列化重载注册目标类。不带 `Class` 的反序列化无法预知类型，读端需提前注册（`@SerializableClass` 或 `register` / `registerAll`）。开启 `require-class-registration` 时，对象内嵌的自定义字段类型不会被自动注册，仍需提前注册。
- 自动补注册的类按类名哈希分配 typeId，与扫描注册使用同一规则；若与已注册类的 typeId 冲突会抛异常，此时请给它加 `@SerializableClass` 走启动期批量注册（冲突时顺延）。

---

## 4. 类注册

```java
@SerializableClass            // easyfk-core 注解
@Data
public class OrderCacheDto implements Serializable {
    private Long id;
    private String orderNo;
}
```

- 启动时 `SerializerInitializer` 扫描 `com.mcst` 和 `scan-packages` 下标注了 `@SerializableClass` 的类，然后调用 `ForySerializer.registerAll`：先按全限定类名排序，再根据类名哈希分配 typeId（256～32766），哈希冲突时顺延。
- 扫描器沿用 Spring 组件扫描的规则：**接口、抽象类、非静态内部类不会被扫描到**。
- 已注册的类在字节流中写入 typeId。默认 `require-class-registration: true`，未注册的自定义类（包括作为字段出现的类型）在序列化和反序列化时都会**抛异常**；JDK 常用类型（String、集合、时间等）由 Fory 内置注册，不受影响。关闭该开关后未注册的类写入完整类名，可以序列化但体积更大、速度更慢，且有安全风险。
- **读写两端必须注册同一批类**。写端注册了而读端没注册，读端看到 typeId 时无法还原类型。跨服务共享缓存或消息时，两边的 DTO 都要加 `@SerializableClass`，并且都在扫描范围内。
- typeId 只取决于类名，所以不同服务只要注册了同一个类，得到的 typeId 就相同。只有在发生哈希冲突时，顺延后的结果才和"本进程注册了哪些类"有关。
- 手动注册：`ForySerializer.register(Cls)`（遇到哈希冲突时**抛异常**，会提示改用 `registerAll`）、`ForySerializer.registerAll(classes)`（先按类名排序，冲突时自动顺延）。
- **首次使用之后再注册新类是允许的**：注册表变化时框架按完整注册表重建 Fory 实例并整体替换（日志 `Fory registration changed after instances were in use, rebuilding instances`），期间正在执行的序列化继续用旧实例，不会读到半成品。重建有成本，高频路径上应尽量在启动期注册完（`@SerializableClass`）。
- 顶层类型自动补注册：序列化时对象自身的类、带 `Class` 的反序列化目标类，即使没预注册也会在首次使用时补注册（打 WARN 并重建实例）；字节流里出现的**嵌套自定义类型**仍需预注册。

---

## 5. API

```java
import com.mcst.easyfk.serializer.fory.ForySerializer;
import com.mcst.easyfk.serializer.fory.SchemaMode;

byte[] bytes = ForySerializer.serialize(dto);                                  // 默认模式
OrderCacheDto a = ForySerializer.deserialize(bytes, OrderCacheDto.class);       // 推荐带 Class
Object b = ForySerializer.deserialize(bytes);

byte[] rpc   = ForySerializer.serialize(dto, SchemaMode.CONSISTENT);           // RPC / 同版本传输
byte[] cache = ForySerializer.serialize(dto, SchemaMode.COMPATIBLE);           // 缓存 / 持久化，允许字段增删
OrderCacheDto c = ForySerializer.deserialize(cache, OrderCacheDto.class, SchemaMode.COMPATIBLE);

OrderCacheDto copy = ForySerializer.deepCopy(dto);                             // 也可以传 SchemaMode
```

**SchemaMode 规则**：

| 模式 | 特点 | 用于 |
|---|---|---|
| `CONSISTENT`（`SCHEMA_CONSISTENT`） | 不写字段元信息，体积最小、速度最快，要求两端类结构完全一致 | RPC、同版本部署、生命周期短的消息 |
| `COMPATIBLE` | 写入字段元信息，允许增删字段 | Redis 缓存、本地文件、长期保存的消息 |

两种模式的字节流**互不兼容**，字节里也没有模式标记。用什么模式写，就必须用什么模式读。不同链路应固定使用一种模式，并在代码中显式传参，不要依赖全局默认值。

**零拷贝 / 回调 API**（复用线程内 4 KiB 缓冲区，超过 1 MiB 后自动回收重建；嵌套调用时使用独立缓冲区）：

```java
ForySerializer.serialize(dto, (byte[] buf, Integer len) -> out.write(buf, 0, len));   // buf 是内部数组
ForySerializer.serializeToProcessor(dto, (buf, off, len) -> out.write(buf, off, len)); // off 固定为 0
ForySerializer.serialize(dto, (byte[] exact) -> keep(exact));                         // 复制出一份独立数组，可以持有

MemoryBuffer mb = MemoryUtils.buffer(4096);
ForySerializer.serialize(dto, mb);              // 从当前 writerIndex 继续写，不会重置
mb.readerIndex(0);
OrderCacheDto d = ForySerializer.deserialize(mb, OrderCacheDto.class);
```

`BiConsumer` 和 `ByteProcessor` 回调拿到的数组**只在回调执行期间有效**，不能保存引用或异步使用。

**XLANG 跨语言**（需要配置 `cross-language: true`，否则调用会抛 `UnsupportedOperationException`）：

```java
byte[] x = ForySerializer.serializeXLang(dto);
OrderCacheDto y = ForySerializer.deserializeXLang(x, OrderCacheDto.class);
```

XLANG 使用**简单类名**（如 `OrderCacheDto`）注册类型，跨语言传输的类名必须全局唯一。XLANG 与 Java 模式的 API 不能混用。

**底层实例**：`getJavaFory()` / `getJavaFory(SchemaMode)` / `getXLangFory()`（未开启 XLANG 时返回 null）。返回的是**当前线程类型适用的实例**：平台线程给 `ThreadLocalFory`（每线程独占），虚拟线程给对象池实例（`buildThreadSafeFory`）。因此：
- 不要长期持有返回值、不要缓存到字段里——注册表变化后实例会被替换；
- 不要在平台线程与虚拟线程之间传递这个引用；
- 不要直接在其上 `register`（绕过了框架的注册表与重建逻辑），注册一律走 `ForySerializer.register` / `registerAll`。

**边界行为**：`serialize(null)` 返回空 `byte[]`；回调类重载遇到 null 对象时不执行回调；反序列化 null 或空数组返回 null；带 Class 的重载传 `clazz == null` 时抛 `IllegalArgumentException`；`deepCopy(null)`、`register(null)` 直接返回。序列化过程中的其他异常原样抛出，不做包装。

---

## 6. 约束与安全

- **没有引用追踪**（`withRefTracking(false)`）：对象图中**不能有循环引用**（如 JPA 双向关联、父子互相引用），否则会栈溢出。同一个对象被多处引用时，反序列化后会变成多个副本，对象同一性不再保持。缓存实体前，先转换成扁平的 DTO。
- **默认开启类注册校验**（`require-class-registration: true`）：反序列化只能实例化已注册的类，字节流中写明的其他类会被拒绝。配置为 false 时会打 WARN，此时反序列化可以实例化字节流中写明的**任意类**，存在反序列化攻击风险，只能用于只处理本系统写入数据的场景。即使开启校验，也不建议对外部输入、用户上传内容或不可信的 MQ 消息直接调用 `deserialize`。
- 所有静态方法都是线程安全的，可以在多个线程中并发调用。平台线程用 `ThreadLocalFory`（无竞争，新线程首次使用时创建实例、复用已生成的序列化器，开销百微秒级）；虚拟线程用对象池，避免为每个短命虚拟线程建实例。两者产出的字节流完全一致。
- 类结构发生变化后，用 `CONSISTENT` 模式写入的旧数据无法读取。长期保存的数据一律用 `COMPATIBLE` 模式，升级发布前先清理旧缓存，或者给缓存 key 加上版本号。

---

## 7. 扩展新的序列化实现

实现 `SerializerClassRegister.registerClass(List<Class<?>>)`，并通过 `@AutoConfiguration` 把它注册成 Bean。`SerializerInitializer` 会自动发现所有实现，并在 `pre-register=true` 时把扫描结果分发给它们。

---

## 8. 生成代码时的规则

- 需要二进制序列化的 DTO **及其字段中出现的自定义类型**一律加 `@SerializableClass` 并实现 `Serializable`；业务包加入 `easyfk.config.serializer.scan-packages`。
- 调用时显式传 `SchemaMode`：缓存和持久化用 `COMPATIBLE`，RPC 和瞬时消息用 `CONSISTENT`，读写两端保持一致。
- 反序列化优先使用带 `Class` 的重载。
- Spring 环境下不要在 `@PostConstruct`、静态初始化块或容器启动之前调用 `ForySerializer`；非 Spring 环境先调用 `ForySerializer.init(...)`。
- 不要序列化有循环引用的对象；不要反序列化不可信来源的数据；不要为了省事关闭 `require-class-registration`。
- 依赖 `ForySerializer` 的测试使用 `@SpringBootTest`，或在测试初始化时调用 `ForySerializer.init(...)`。

---

## 9. 复查记录

| # | 位置 | 文档描述 | 源码事实 |
|---|---|---|---|
| 1 | 使用手册 §1、特点 §1、核心模块说明 技术栈 | Apache Fory / Fury 0.14.1 | `build.gradle` 引入的是 `org.apache.fory:fory-core`，上一版 1.3.0，**本版本 1.7.8** |
| 2 | 特点 §2.5 | "两个 Fory 实例均启用了 `withRefTracking(true)`" | 三个实例都是 `withRefTracking(false)`（同一节代码示例里也写的是 false，前后矛盾） |
| 3 | 特点 §2.7、§2.11、§5 | `pre-register=false` 会切换到"动态注册模式" | 两个自动配置会同时失效，配置 Bean 缺失，`ForySerializer` 初始化失败；使用手册 §2.1 的限制说明是正确的 **已修复**：自动配置不再受 `pre-register` 控制，`false` 时只跳过启动扫描，改为按需注册 |
| 4 | 特点 §3.1 | 非 Spring 环境"可用（手动初始化）" | 没有手动初始化的 API，只能通过 `SpringUtil` 获取配置 **已修复**：新增 `ForySerializer.init(SerializerProperties, ForySerializerProperties)` 与 `isInitialized()` |
| 5 | 特点 §2.3 | 用 `add()` 原子 check-and-set，不需要加锁 | 实际是先 `contains` 判断，再在 `synchronized` 中注册 |
| 6 | 特点 §3.3 | `ctx.javaFory.register(clazz)` | 实际是 `register(clazz, typeId)`，并且同时注册到两个 Java 实例 |
| 7 | 特点 §4 | Java 17+ | 框架统一要求 Java 21 |
| 8 | 两份文档 | 未提到安全风险 | `requireClassRegistration(false)` 等于允许反序列化任意类，不能用于不可信数据 **已修复**：默认 `require-class-registration: true`，可通过配置关闭（关闭时打 WARN）；调用方显式给出的顶层类型自动补注册，嵌套自定义类型需 `@SerializableClass` |
| 9 | 使用手册 | 未说明初始化失败后的表现 | Holder 初始化失败后不可恢复，后续调用一直抛 `NoClassDefFoundError` **已修复**：改为可重试的懒加载，失败不缓存，每次抛带原始 cause 的 `IllegalStateException` |
| 10 | 使用手册 §2.1 | 扫描 `@SerializableClass` 类 | 接口、抽象类、非静态内部类会被扫描器过滤掉 |
| 11 | `ForySerializer`（3.5.16 重构） | 上一版：实例首次构建后即冻结，注册表不能再变（Fory 在首次序列化后冻结注册） | 本版本拆成 `Settings`（配置，构建一次）+ `ForyContext`（实例，按注册表重建）：`register` / `registerAll` 在实例已使用后仍可调用，会按完整注册表重建并整体替换，进行中的调用用旧实例。**已修复** |
| 12 | `ForySerializer`（3.5.16 新增） | 上一版：`ThreadSafeFory` 单实例，虚拟线程下每线程建实例开销大 | 本版本按线程类型选实现：平台线程 `ThreadLocalFory`，虚拟线程对象池（`buildThreadSafeFory`），两者字节流一致。`getJavaFory()` 返回的是**当前线程适用**的实例，不能长期持有、不能跨线程类型传递 |
| 13 | `ForySerializer`（3.5.16 新增） | 上一版：未固定类加载器 | 本版本在初始化时固定 ClassLoader（初始化线程 TCCL / Spring 容器 ClassLoader），按类名还原与 JIT 都用它；业务类必须在其中可见 |
