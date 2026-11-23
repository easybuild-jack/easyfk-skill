# Chronicle Map 组件使用手册

本手册基于易用性与极致性能并重的原则编写，旨在帮助开发者快速了解、接入和使用 `chronicle-map`。本文从业务使用者视角出发，教你**什么场景下用什么功能，怎么用才能达到最高性能**，让你一看就会，精确定位。

---

## 1. 组件特点与定位

`chronicle-map` 是基于 OpenHFT Chronicle Map 深度封装的本地持久化高性能 K-V（键值对）存储组件。

### 核心特点
- **堆外内存（Off-Heap）**：数据脱离 JVM 堆内存，直接存储在系统物理内存或内存文件映射（MMap）中，**彻底告别海量缓存导致的垃圾回收（GC）停顿**。
- **自动持久化机制**：数据绑定在本地文件系统上，应用崩溃或重启后瞬间恢复，不需要从远端中心拉取重放。
- **并发级别极高**：利用多段锁/细粒度锁的底层并发结构，轻松承受单机每秒数十万至上百万次的读写并发。
- **类型极度严谨**：防污染注册体系，同一 `mapName` 在创建时被赋予特定 K-V 类型后，后续任何携带不同类型的创建/复用动作（`initMap` / `getOrCreateMap`），以及同名重复注册，都会在运行时立即被框架拦截并快速失败（Fail-Fast），死守内存安全。

### 面向业务的区别？（与远端 MQ / 分布式缓存的区别）
- **绝非分布式 Redis 等效替代品**：没有原生分布式网络通信与主从同步副本功能。如果你需要跨物理机的集群广播状态或全网强一致性协调，请优先选用远端 Redis。它致力于解决**单机器内**无网络开销传输的极限低延迟读写通信。
- **为什么不用普通的 JVM `ConcurrentHashMap`？**：除了数据可以跨崩溃恢复、跨重启生存外；`chronicle-map` 的体积突破了 JVM 内存参数上限的钳制约束。你可以狂存上百 GB 数据且不对 GC 线程带来丝毫阻塞。

---

## 2. 适用与不适用场景

### 十分推荐使用的场景：
* **极高频金融行情或系统状态表存取**：需要承载一秒数十万次的微秒级跳动更新。
* **业务需要重启免预热的超重型缓存池**：千万级数据量的核心商户大对象，发版重启业务时绝不可以接受从关系型数据库读档预热造成服务真空期的场景。
* **极致低延迟本地流式校验路由**：每次调用链必须必读的（如黑历史检测/动态频控列表）黑白名单路由。

### 请避免使用的场景：
* **强诉求需要跨所有云物理机实例实时清空的全局 Session 池**。
* **数据量极小（仅几 KB）且无关痛痒即便丢失也无所谓的枚举键值列表**。
* **要求非常复杂深入的 JSON 内部字段多条件组合提取或全文模糊查询**：此库本质是硬核的 K-V 全哈希定点精准查验引擎。

---

## 3. 基础接入方式（一看就会）

为了保障日常使用过程中的平滑与开箱即用，通过调用统筹网关 `ChronicleMapTemplate`，所有的内存底层指针切分技术和锁处理已被彻底透明封装！

### 3.1 引入使用
```java
@Resource
private ChronicleMapTemplate chronicleMapTemplate;
```

### 3.2 像 Map 一样日常无忧存取（普通业务使用）
```java
// 未通过 YAML 声明时，先初始化 Map
chronicleMapTemplate.initMap("userCache", String.class, UserInfo.class);

// 写入数据
chronicleMapTemplate.put("userCache", "UID001", userInfo);

// 读取数据：
UserInfo result = chronicleMapTemplate.get("userCache", "UID001");
```

### 3.3 （防坑预警！）容量参数预定义
无论是原生类型还是复杂映射，底层内存管理系统在划拨磁盘槽位时极其需要得知“这块饼可能要做多大”。如果你在程序里只管往里塞而没给明确的预估上限，在它撑饱扩容做物理位移时将严重吃掉性能。
**推荐操作是在应用级的初始化配置 YAML 中明示规格：**
```yaml
easyfk:
  config:
    chronicle:
      map:
        maps:
          - map-name: userCache
            key-type: java.lang.String
            value-type: com.biz.UserInfo
            max-entries: 1000000    # 大概估算最多能装多少条数据（重要！）
            average-value-size: 800 # 预估单个序列化对象落位后的平均字节数，稍微多留宽裕（极度重要！）
```

---

## 4. 高级使用姿势：如何选用不妥协的序列化方式

基于不同的场景速度极限需求，我们整理了三种差异化落盘引擎手法：

### 模式一：极简原生对象存取（对所有人都友好）
如果你要存的只是一些诸如 `String`, `Long`, `Double` 等无需反射开支拆包的原生标志。直接就地使用：
```java
chronicleMapTemplate.initMap("indicatorMap", String.class, Double.class);
chronicleMapTemplate.put("indicatorMap", "cpu_usage", 82.5);
```

### 模式二：Fory 序列化（非常适合追求全自动化但又想要性能红利的懒汉）
**业务痛点**：我有嵌套了两层关联 List 或者 Map 集合的复杂商品 DTO 实例，走标准 Java 序列化系统会慢死，我自己又不想手写指针逻辑。
**解决办法**：打开全局开关（**默认关闭**），启用**智能推断引流（Fory Marshaller）**：
```yaml
easyfk:
  config:
    chronicle:
      map:
         fory-marshaller-enabled: true 
```
配置开启后保持你的普通 `template.put / get` 的业务写法不动。系统会自动识别值类型：`String`、`byte[]`、基本类型包装类、`BytesMarshallable` 实现类以及 `java.*` 包内的 `Serializable` 类型仍走 Chronicle Map 原生序列化，其余自定义业务对象自动送入 Fory 极速序列化通道。
**性能提示**：写入链路基于 `ThreadLocal<MemoryBuffer>` 池化复用，序列化过程不产生临时 `byte[]` 分配；读取时 Fory 需要反序列化生成结果对象（属于必要分配，无法通过 `getUsing` 规避，见第 5 节说明）。

### 模式三：绝对原生物理指针 `BytesMarshallable`（针对撮合级、百万笔结算账务处理系统的性能狂人）
**场景痛点**：我是绝对纯粹的超高频金融机器或交易风控队列，不仅要最快，我还想要自行全控字段存放排序。
**特殊操作**：你的目标对象必须严格执行官方 `BytesMarshallable` 指示级读写契约：
```java
public class MarketTicker implements BytesMarshallable {
    double price;
    
    @Override
    public void writeMarshallable(BytesOut bytes) {
        bytes.writeDouble(price);  // 面向操作系统的 C 风格裸指写入
    }
    
    @Override
    public void readMarshallable(BytesIn bytes) {
        price = bytes.readDouble();
    }
}
```
此时你哪怕开启了前文的全局配置，框架探针也会立马识破这是你的性能专属护城河，让出所有前置解析！以最高速直接与 C 接口进行数据传输。

---

## 5. 进阶杀招：通过对象池根除提取分配代价（Zero-GC读取）

假设你已经在上述步骤解决了存入时序列化慢的问题，但别忘了在 `UserInfo obj = template.get(..)` 这个瞬间，堆上的新生代又被划掉了一块去生造这个 `obj`，在几十万并发扫频的高压下这也是不折不扣的老年代杀手！

**终极抗压法宝的介入：使用 `getUsing()` 覆盖原位复写。**

你只需外部持有生命期比你循环周期长的容器对象，剩下的只要告知系统，让系统拿着现成的盘子把内存中捞出来的内容直接盖在同一个对象的对应位点属性中（俗称对象填充）。

```java
// 全局（或者当前线程内）长期持活的载体壳
private final MarketTicker bufferTicker = new MarketTicker();

public void loopFetchData() {
    // 数据像倒模一样，被底层内存游标精确定位复印在了 bufferTicker 本尊上。
    // 程序结束本次访问后的代价是：对系统造成的GC新申请压力为0！
chronicleMapTemplate.getUsing("tickerMap", "APPL", bufferTicker);
    
    System.out.println("拿捏精准零分配数据：" + bufferTicker.getPrice());
}
```

**适用边界（重要）**：原位填充依赖值类型自身支持复用，即 `BytesMarshallable` 实现类（复用字段回填）或 OpenHFT value-interface 类型。**对走 Fory 序列化的普通 POJO，`getUsing` 的 `using` 参数不生效**——Fory 反序列化每次都会生成新对象并作为返回值返回，效果等同于 `get`。需要 Zero-GC 读取的热点链路，请让值对象实现 `BytesMarshallable`（见模式三）。

---

## 6. 全面功能导览表 (开发时随时查阅)

**总体约定**：新增写入方法（`put` / `putIfAbsent` / `putAll` / `computeIfAbsent`）在 Map 未创建时**快速失败**（抛 `IllegalStateException`）；读取与"作用于已有条目"的方法（`get` / `getAll` / `containsKey` / `size` / `remove` / `replace` / `computeIfPresent` 等）在 Map 未创建时宽松返回（`null` / 空集合 / `false` / `0`），不会抛异常。

| 你的诉求 | 推荐使用的 API方法 | 提示说明 |
|---|---|---|
| **初始化普通 Map** | `initMap(mapName, keyClz, valClz)` | 未通过 YAML 声明时先调用一次 |
| **初始化 Fory Map** | `initForyMap(mapName, keyClz, valClz)` / 带 `maxEntries, avgValueSize` 重载 | 强制值走 Fory 序列化（不依赖全局开关的自动识别） |
| **存数据** | `put(mapName, key, val)` | Map 不存在时快速失败 |
| **拿回抛出** | `get(mapName, key)` | 会在 JVM 中反序列化实体，若高并发轮询应当避免 |
| **批量查询（小批量）** | `getAll(mapName, keys)` | 返回 `LinkedHashMap`（按入参顺序）；未命中的 key 不出现在结果中；适合几千以内 |
| **批量查询（大批量）** | `getAll(mapName, keys, action)` | 流式回调逐条消费，堆内不堆积全部 value，几十万至百万级 key 防 OOM 首选 |
| **批量查询（并行）** | `getAllParallel(mapName, keys, action)` | 基于公共 ForkJoinPool 并发回调，`action` 必须线程安全；小批量勿用 |
| **读取不申请新对象** | `getUsing(...)` / `getUsingMarshallable(...)` | 仅对 `BytesMarshallable` / value-interface 类型生效；**Fory 序列化的 POJO 不支持原位填充**（见第 5 节） |
| **条件性原子创建** | `putIfAbsent(...)`、`computeIfAbsent(...)` | 基于内置多段锁严抓控制，避免写抢占 |
| **原子读-改-写** | `updateWithLock(mapName, key, action)` | 写锁内读出 value → 执行 action 修改 → 写回，整个过程原子；`getWithLock` 为只读版 |
| **删除与替换** | `remove(...)`、`replace(...)` | 均提供带期望值的 CAS 版重载（`remove(k, v)` / `replace(k, old, new)`） |
| **探寻与计步** | `containsKey(...)`、`size(mapName)` | 注意 `size` 会引发小规模遍历扫库 |
| **搜集所有索引** | `keySet(mapName)` | 可取出所有注册存局内的键。但在海量元素大盘中切勿当成热点检索器滥用，极具消耗且容易出现扫描阻滞。 |
| **Map 生命周期查询** | `mapExists(mapName)`、`getAllMapNames()`、`getStats(mapName)` | 管理与巡检用途 |

---

## 7. 配置项完整参照（与代码一致）

全局配置（前缀 `easyfk.config.chronicle.map`）：

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `default-path` | `./chronicle-maps` | 持久化文件默认目录 |
| `default-max-entries` | `100000` | 默认最大条目数 |
| `default-average-key-size` | `64.0` | 默认平均键大小（字节） |
| `default-average-value-size` | `1024.0` | 默认平均值大小（字节） |
| `default-file-extension` | `.dat` | 持久化文件扩展名 |
| `persistence-enabled` | `true` | 全局持久化开关（关闭后所有 Map 均为纯内存，per-map 配置也无法开启） |
| `recover-on-startup` | `true` | 文件存在且没有其他遵循伴生锁协议的活跃使用者时，执行 `recoverPersistedTo` 完整性校验和脏锁清理 |
| `apply-average-sizes` | `true` | 是否应用平均键/值大小参数 |
| `fixed-size-optimization-enabled` | `true` | 定长类型（`Long`/`Integer`/`Double` 等包装类）不设置平均大小 |
| `fory-marshaller-enabled` | `true` | 未显式指定时按值类型自动识别是否用 Fory（见第 4 节模式二） |
| `fory-schema-mode` | 无（沿用 serializer-fory 全局默认） | `CONSISTENT` 体积小、速度快；`COMPATIBLE` 容忍字段增删但每条记录都要处理字段元数据，读写更慢、堆分配更多。两种模式字节流互不兼容，已有持久化文件不可中途切换 |
| `put-returns-null` | `false` | 见下方「写入性能开关」 |
| `remove-returns-null` | `false` | 见下方「写入性能开关」 |
| `maps` | 无 | 声明式 Map 定义列表，见下表 |

### 写入性能开关：`put-returns-null` / `remove-returns-null`

`Map` 契约要求 `put()` 返回旧值。堆内的 `HashMap` 做这件事几乎免费，但堆外存储必须**把旧值完整反序列化成一个堆对象再交给调用方**——而绝大多数业务代码根本不看这个返回值，于是每写一条就白白产生一份对象图垃圾。更关键的是，这份开销发生在 **Chronicle Map 的段更新锁内**，会直接拉长临界区，加剧跨进程读写竞争。

开启后 `put()` / `remove()` 恒定返回 `null`，跳过这次反序列化。

```yaml
easyfk:
  config:
    chronicle:
      map:
        put-returns-null: true
        remove-returns-null: true
```

两点说明：

1. **这是行为变更。** 开启前请确认调用方没有依赖 `put()` / `remove()` 的返回值。需要旧值时，改用 `template.get()` 先读，或在 `updateWithLock` 的锁闭包内处理。
2. **这是 JVM 级配置，不写入持久化文件头。** 可以只在写入进程开启、读取进程保持默认，不需要重建数据文件，也不影响其他进程。

`maps` 列表内每项可配置（未配置的项回落到全局默认）：

| 配置项 | 说明 |
|---|---|
| `map-name` | Map 名称（必填，不可为空） |
| `key-type` / `value-type` | 键/值类型全限定类名（默认 `java.lang.String` / `java.lang.Object`） |
| `max-entries` | 最大条目数 |
| `average-key-size` / `average-value-size` | 平均键/值大小（字节） |
| `file-path` | 持久化文件完整路径（不配置则为 `default-path/映射名.扩展名`） |
| `file-extension` | 持久化文件扩展名 |
| `persistence-enabled` | 该 Map 是否持久化（默认 `true`，需全局开关同时开启才生效） |
| `apply-average-sizes` | 是否应用平均大小参数 |
| `fixed-size-optimization-enabled` | 是否启用定长类型优化 |
| `use-fory-marshaller` | 强制指定该 Map 是否使用 Fory（不配置则按全局开关自动识别） |
| `fory-schema-mode` | 该 Map 的 Fory 序列化模式 |
| `put-returns-null` / `remove-returns-null` | 该 Map 的写入性能开关，说明见上 |

**命名与类型防护**：同一 `mapName` 重复注册会快速失败；以不同的 K-V 类型复用已存在的 `mapName`（`getOrCreateMap` 场景）也会快速失败，防止类型污染。

---

## 8. 多进程打开与启动恢复

每个持久化 Map 文件都会在同目录生成一个 `<map文件>.lck` 伴生锁文件。该文件只用于进程协调，不存放业务数据：

- 字节 0 是独占“门锁”，用于串行化多个进程的打开和恢复流程。
- 字节 1 是共享“使用锁”，Map 打开期间持续持有，正常关闭时释放；进程崩溃或被强制终止后由操作系统释放。
- 持久化文件已存在、`recover-on-startup=true` 且没有其他活跃使用者时，首个进程执行完整性恢复。
- 已有其他活跃使用者时，新进程跳过恢复并正常打开，避免恢复过程影响其他进程的内存映射。
- `recover-on-startup=false` 只关闭自动恢复，不会关闭伴生锁协调。

**使用边界：**

1. 所有访问同一持久化文件的进程都必须使用支持该伴生锁协议的组件版本。旧版本客户端或直接调用 Chronicle Map API 的代码不会持有使用锁，无法被可靠探测。
2. 同一 JVM 内不要使用多个 `ChronicleMapManager` 打开同一个持久化文件，Java 会对重叠文件锁抛出 `OverlappingFileLockException`。
3. `.lck` 文件可以长期保留，不需要在正常启动或关闭时手工删除；进程运行期间不要删除或替换它。
