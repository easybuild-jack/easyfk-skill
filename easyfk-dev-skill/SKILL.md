---
name: easyfk-dev-skill
description: >-
  EasyFK（易架构）项目的开发规范：告诉 AI 在 easyfk 项目里怎样规范地写业务代码。要用任何能力时先查 easyfk-framework-skill 有没有现成模块，能满足就用；写能工作的最少实现（YAGNI、先复用、修 bug 改根因），遵守阿里开发规范，日志和注释用中文。
  普通数据库业务项目按分层写：模型（Dto/Param/Req/EditReq/Resp）→ 持久层（Entity/Mapper/Repository，MyBatis-Plus，String UUID 主键）→ Service → Api / ApiServerImpl → Controller → Remote（Cloud / Dubbo），异常默认用错误码枚举、多语言时用 i18n；已有项目先读现有结构和同类代码照写，从零开发时先和用户确定用 single / sc / smart / 组件化中的哪种结构再建工程。架构类项目（为业务开发服务、偏架构层的组件、SDK、starter、中间件、引擎、框架底层，不是普通数据库应用）按 rules/11-architecture.md 定模块拆分、包结构、线程模型与状态、热路径与 GC、确定性、对外契约兼容、自动配置和依赖版本，要给别人接入的必须写使用说明文档。
  文档按改动大小决定：小改动和 bug 修复不新建文档；重大调整先写需求、分析、计划，放 docs/requirement、docs/design、docs/plan；流程图、时序图、架构图按需用 Mermaid 画；项目级迭代记录按时间倒序。项目说明文档（docs/<项目名>项目说明.md）开头先写明项目定位：业务项目（直接实现业务规则、业务方会直接对它提需求，如用户、订单、风控）还是组件项目（本身不处理业务，为业务项目提供通用能力或数据流转，如 data-agent、aeron-cluster、mq-kafka、db-redis），组件项目必须写清服务对象；正文固定五节：背景、需求、功能、模块设计及划分、业务数据依赖，业务数据依赖列清本项目依赖、自管理、对外提供了哪些业务数据（如行情数据、仓位数据）及各自的来源、代码位置和变更影响。定位和依赖清单只如实登记事实，一次需求变更涉及哪些项目由上层总管 skill 分派，本项目收到任务后再核是否属于自己的职责、要不要改、改哪些。新需求开发和复杂变更做完，要另起一个没参与开发的独立子 agent，拿需求和设计复核代码，小 bug 修复不做；复核后按 plan 文档顶部固定的状态值更新任务状态，供上层总管查看进展。写完先自检。
  识别到 easyfk 项目时全量使用：构建文件引入了 easyfk- 开头的组件坐标（如 easyfk-dependencies），或源码包名以 com.mcst 开头；从零新建时用户明确要求按 easyfk 建也算。识别不到时只使用与框架无关的通用规范——最少实现、阿里规范、日志注释、文档与计划、自检与复核，不参考任何 easyfk 内容，并提醒用户能力会打折。开工前先按正文「项目识别」确认。在这类项目中新增或修改 Controller、Service、Api、Repository、Mapper、Entity、Dto、Remote、Feign、Dubbo、异常、i18n、配置类，开发组件、SDK、starter、中间件、引擎、框架底层、Aeron、aeron-cluster、Disruptor、热路径、自动配置，新建项目或模块、写需求、设计、计划、迭代记录、维护业务数据依赖、复核代码、更新计划状态、画图、代码自检时使用。
---

# EasyFK 开发规范

本 skill 管「**怎么写**」：分层、命名、每层的写法、文档和自检。框架「**有什么**」（模块、能力、工具类、配置前缀、依赖坐标）不在这里，以 **easyfk-framework-skill** 为准。

本 skill 属于 easyfk-skill 套件，套件里三个 skill 分工不同、互相按名称引用：

| skill | 管什么 |
|---|---|
| easyfk-framework-skill | 框架有什么：模块、能力、选型、工具类、版本快照 |
| easyfk-dev-skill（本 skill） | 怎么写：分层、命名、文档、自检 |
| easyfk-reverse-skill | 怎么反推：从代码还原业务分析报告和架构分析报告 |

下文的 `<framework>` 指第 0 节第 1 步找到的 easyfk-framework-skill 目录。

## 0. 先做四件事

0. **确认是 easyfk 项目**，按 [项目识别](#项目识别) 判断。识别到就全量使用；识别不到时只按 [项目识别](#项目识别) 里「可以用」那一组工作——不碰任何 easyfk 内容（模块选型、坐标与私服、类名注解、配置前缀、分层契约写法、版本路由），并在回复里提醒用户能力会打折。
1. **确认套件已安装**：按 [套件安装检查](#套件安装检查) 找到 easyfk-framework-skill；找不到就按那一节安装。没有 git、网络不通或安装失败时，停下来告诉用户，不凭记忆写框架的类名和配置。
2. **确定 easyfk 版本**：按 easyfk-framework-skill 的 §0.1 找到项目的 easyfk 版本，再到 `<framework>/versions/index.md` 定位文档快照。本规范里写的 `modules/xxx-skill.md`，都指 `<framework>/versions/<版本>/modules/` 下的文件。框架 jar 包只在 CNB Maven 私服上，从零开发或依赖拉不下来时按 easyfk-framework-skill §8.1 配置仓库和令牌。
3. **判断项目类型**，决定开工方式（细则见 [rules/01-project.md](rules/01-project.md)）：

| 项目类型 | 开工方式 |
|---|---|
| 普通业务项目（数据库 CRUD 类） | **已有项目**（通常由人先建好）：先按模块列表认出是单模块（single）、基础多模块（sc）、多栈（smart）还是组件化（auth 式）中的哪一种，**再读同类实体的全套代码照着写**。不改结构、不新增模块、不改 Bean 的注册方式。**从零开发**：先和用户确定用四种结构中的哪一种，按 [rules/01-project.md](rules/01-project.md) §2 的参考结构建工程，并按新项目出文档 |
| 架构类项目（为业务开发服务、偏架构层的项目：组件、SDK、starter、中间件、引擎、框架底层，如 `lock-redisson`、`etcd-cluster`、撮合、行情。开发内容不只是数据库业务） | 先确认框架没有同类能力；新项目由本 skill 设计模块拆分和线程模型，先出文档再建工程；已有项目照现有链路改。规范见 [rules/11-architecture.md](rules/11-architecture.md) |

项目的**项目定位**（业务项目 / 组件项目）写在项目说明里，见 [rules/10-docs.md](rules/10-docs.md) §5.1。这里只如实写清自己是什么项目、负责什么、碰了哪些业务数据——一次需求变更涉及哪些项目由上层总管的 skill 分派（不在本套件内），本项目不做这个全局判断，也不自己去猜跟自己有没有关系；但收到分派的任务后要自己核：是不是我的职责、这个改动要不要做、要改哪些地方，不属于自己的说明理由退回。组件项目另有一条底线：不为了业务需求往组件里加业务逻辑，业务规则留在业务项目。

拿不准属于哪一类、或现有结构和本规范冲突又不知道该听谁时，先问用户。

## 1. 组件选型（最高优先级）

要用到某种能力时，先查 easyfk-framework-skill，再决定写不写、引不引。这条压过「自己写一个」和「先加一个新依赖」。

1. 查 easyfk-framework-skill 的需求 → 模块选型（§5）和工具能力清单（§6）。多线程、内存队列、缓存、锁、业务编号、MQ、远程调用、序列化、JSON、Bean 拷贝、日期、加解密都在里面。
2. 有对应模块就读它的 `modules/xxx-skill.md`，对照这次的业务看能不能满足：能力、默认行为、限制。能满足就用文档里的类名和配置。
3. 读完文档仍然满足不了，才新引入组件或自己写。回复里写明缺的是哪一项，以及现有模块为什么不够。

常见的几类：

- 线程池、并行、重试：`easyfk-thread`（`modules/easyfk-thread-skill.md`）。按名称注入预定义池（`ioIntensiveTaskExecutor`、`cpuIntensiveTaskExecutor` 等），或用 `CustomTaskExecutor`，I/O 与计算分开。不要自己 `new ThreadPoolExecutor`。
- 进程内队列：`queue-disruptor`（`modules/easyfk-queue-skill.md`）。消费者实现 `Processor<T>`，生产者用 `IngestQueueManager`。要持久化或重试时用 MQ。
- 缓存、锁、业务编号：分别查 cache、lock、autoId 的模块文档，不在业务里手写 Redis 脚本。

easyfk-framework-skill 写了不要引入的构件和同类库，不要加。

## 2. 总体要求

1. 严格按 easyfk 分层写，不跨层调用，见 §3。任何组件先按 §1 的三步查。
2. 已有项目**照现有代码写**：命名、包路径、Bean 注册方式、返回值风格，以同模块里已有的同类代码为准。本规范给出的是默认写法，现有项目已有统一约定时听项目的；但正确性规则（事务、异常、分层不越级、Remote 契约约束）以本规范为准。现有代码违反这些规则时，本次改到的地方按规范写，没改到的不顺手重构，在回复里提一句。
3. 代码尽量符合《阿里巴巴 Java 开发手册》。先检查条件，不满足就直接结束；主流程放在所有条件成立之后，少用层层嵌套的 if。日志和注释用中文，专业词汇可以用英文。
4. 写能工作的最少实现：不做推测出来的需求，先复用，不加没要求的抽象，修 bug 改根因。细则见 §5。
5. 文档按改动大小决定，见 [rules/10-docs.md](rules/10-docs.md)。小改动不新建文档；重大调整先出文档再写代码。改动让业务数据依赖变了（新增外部数据来源、自管理数据增减、对外提供的数据变了），同步维护项目说明里的「业务数据依赖」一节，见 [rules/10-docs.md](rules/10-docs.md) §5.2。
6. 代码写完先自检（§6）。自检没过，不宣称完成。
7. 复杂改动和新需求开发完成后，另起一个独立子 agent 复核代码（§7），复核通过再更新计划状态。小 bug 修复不走复核。

## 3. 分层规范

本节和 02 ~ 08 管普通数据库业务项目，以及架构类项目里的 CRUD 部分。架构类项目的其余部分看 11。

调用链（一个实体一套）：

```
Controller ──> IXxxApi ──实现──> XxxApiServerImpl（本地）/ XxxApiScImpl（Feign）/ XxxApiDubboImpl（Dubbo）
                                   │
                                   ▼
                              IXxxService ──> IXxxRepository ──> XxxMybatisRepository ──> XxxMapper
```

- Controller 只注入 `IXxxApi`，不注入 Service、Repository、Remote。
- 业务逻辑、事务、唯一性和关联校验放 Service；`ApiServerImpl` 只做转发。
- Service 只依赖 Repository 接口，不依赖 Mapper 和 Entity。
- 跨服务调用只注入对方的 `IXxxApi`，靠换依赖包在本地 / Feign / Dubbo 之间切换。

| 规则文件 | 内容 |
|---|---|
| [01-project.md](rules/01-project.md) | 项目类型、参考结构、包名、新增一个实体要建哪些文件 |
| [02-model.md](rules/02-model.md) | Dto / Param / Req / EditReq / Resp / VO，对象转换，参数校验 |
| [03-persistence.md](rules/03-persistence.md) | Entity、Mapper、XML、Repository 接口与实现（MyBatis-Plus） |
| [04-service.md](rules/04-service.md) | Service 接口与实现：查询、保存、删除、SaaS 数据隔离、事务、自定义条件 |
| [05-api.md](rules/05-api.md) | `IXxxApi` 与 `XxxApiServerImpl`，扩展业务方法 |
| [06-controller.md](rules/06-controller.md) | 标准接口（详情 / 分页 / 新增编辑 / 删除 / 启用禁用 / 下拉）、返回值、权限注解 |
| [07-remote.md](rules/07-remote.md) | Spring Cloud（OpenFeign）与 Dubbo 的契约、提供方、消费方 |
| [08-error.md](rules/08-error.md) | 错误码枚举（默认）与 i18n 异常 |
| [09-config.md](rules/09-config.md) | Bean 注册、配置属性类、自动配置、依赖声明 |
| [10-docs.md](rules/10-docs.md) | 要不要写文档、文档目录、计划文档与状态值、画图、项目说明（含项目定位与业务数据依赖）、迭代记录 |
| [11-architecture.md](rules/11-architecture.md) | 架构类项目（组件、中间件、引擎、框架底层）：开工方式、组件选型、模块拆分、包结构、线程模型与状态、热路径与 GC、确定性、对外契约、自动配置、依赖版本、使用说明、测试与自检 |
| [12-review.md](rules/12-review.md) | 复核：什么时候起子 agent、审哪些项、提示词模板、几轮、结果记在哪 |

ORM 只给 MyBatis-Plus 写法。项目用 MyBatis-Flex 或 Hibernate 时，分层不变，持久层写法读 `modules/easyfk-component-orm-skill.md` 和 `modules/easyfk-repository-skill.md`，并参照项目里已有的实体。

## 4. 命名速查

以实体 `Order`、模块 `trade` 为例（类名前缀跟实体名，包名跟项目现状）：

| 类 | 命名 | 继承 / 实现 |
|---|---|---|
| 数据对象 | `OrderDto` | `extends BaseDto` |
| 参数对象 | `OrderParam` | `extends BasicParam` |
| 请求对象 | `OrderReq` | `extends OrderParam` |
| 编辑对象 | `OrderEditReq` | `extends OrderDto` |
| 响应对象 | `OrderResp` | `extends OrderDto` |
| 实体 | `Order` | `extends BaseMyBatisPlusEntity<Order>` |
| Mapper | `OrderMapper` | `extends BaseMapper<Order>` |
| Repository 接口 | `IOrderRepository` | `extends IBaseRepository<OrderDto, String>` |
| Repository 实现 | `OrderMybatisRepository` | `extends BaseMyBatisRepositoryImpl<OrderMapper, OrderDto, Order, String>` |
| Service | `IOrderService` / `OrderServiceImpl` | `extends IBaseService<OrderResp, String, OrderReq>` |
| Api | `IOrderApi` / `OrderApiServerImpl` | `extends IBaseApi<OrderResp, String, OrderReq>` / `extends BaseApiServiceImpl<IOrderService, OrderResp, String, OrderReq>` |
| Controller | 管理后台 `OrderBmsController` / 客户端 `OrderController` | 路径 `/api/bms/trade/order` / `/api/trade/order` |
| Cloud | `IOrderRemote` / `OrderRemoteImpl` / `OrderApiScImpl` | `IBaseRemote` / `BaseRemoteImpl` / `BaseApiRemoteImpl` |
| Dubbo | `IOrderRemote` / `OrderRemoteImpl` / `OrderApiDubboImpl` | `IDubboBaseRemote` / `DubboBaseRemoteImpl` / `DubboBaseApiRemoteImpl` |

泛型顺序固定：**Resp、主键、Req**（Repository 是 **Dto、主键**）。主键统一 `String`，UUID 生成。

## 5. 开发时

1. 先做组件选型（§1），再写代码。类名、注解、配置前缀以 `modules/xxx-skill.md` 为准，不凭记忆写。
2. 写能工作的最少实现：
   - 先确认这件事要不要做。需求是推测出来的，就不做，用一句话说明。
   - 先读懂再动手：读任务和它涉及的代码，把真实调用链追通，再找最短的改法。
   - 按这个顺序找现成的，找到就停：当前项目里已有的方法和类型 → easyfk 模块与工具类（easyfk-framework-skill §6）→ 标准库和平台能力 → 项目里已经引入的依赖 → 最后才写最少的新代码。
   - 不加没要求的抽象：只有一个实现就不要接口和工厂，不会变的值不做成配置，不为以后预留脚手架。easyfk 分层要求的接口（`IXxxApi`、`IXxxService`、`IXxxRepository`、`IXxxRemote`）按框架写，不算多余。
   - 能删就不加，文件尽量少，改动尽量小。
   - 修 bug 改根因：查出要改的方法有哪些调用方，在它们共用的地方改一次，不在每个调用方各打补丁。
   - 两种写法差不多长时，选边界情况正确的那种。
3. 不另写工具方法，不另引功能重复的依赖：判空用 `EmptyUtil`，拆分用 `SplitUtil`，对象转换用 `TransformUtil`，JSON、日期、加解密等先查 easyfk-framework-skill §6。
4. 代码格式跟随项目已有的格式化配置。本次改动不重排无关代码。
5. 方法里先做条件检查和校验，不满足就 return 或抛异常（见 [08-error.md](rules/08-error.md)），主流程写在检查都通过之后。
6. 日志和注释用中文，类名、方法名、协议、产品名和通用专业词汇（TTL、TraceId、fallback）保留英文。
   - 日志用 Lombok `@Slf4j`，写清发生了什么、对象是谁、结果如何，如 `log.info("订单已取消：orderId={}, operator={}", orderId, operator)`。字段名、错误码、枚举值保持英文。
   - 用占位符 `{}`，不拼字符串；异常日志把异常对象作为最后一个参数传入，不只打 `e.getMessage()`。
   - 已有代码不为改语言单独重写；本次改到的日志和注释按这条写。
7. 注释写给人看，说明作用和流程，不复述代码。
   - 接口写这个方法做什么、给谁用、返回或失败意味着什么。
   - 实现写流程：先做什么、哪一步决定分支、失败怎么处理。
   - 名字已经说清楚的简单方法、getter、一层转发，不加注释。
   - 不写「本方法用于」「值得注意的是」这类空话，不留被注释掉的废代码。
   - 故意留下的简化写一行注释，注明上限和以后怎么换，如 `// 简化：全局锁，吞吐不够时改成按账户加锁`。
8. 回复里先说改了什么，再用几句话说明跳过了什么、什么情况下该补上。

## 6. 写完自检

1. **分层**：Controller 只依赖 `IXxxApi`；Service 不碰 Mapper 和 Entity；跨服务只用 `IXxxApi`；新加的 Bean 按项目现有方式注册了。
2. **规范项**：主键是 `String` + UUID；`Dto` 上有 `@PrimaryKey`；唯一字段有 `@SingleUniqueField` 且数据库有唯一索引；写多张表的方法有 `@Transactional(rollbackFor = Exception.class)`；业务异常用错误码枚举或 i18n，没有直接 `throw new RuntimeException`。
3. **契约同步**：`IXxxApi` 加了方法时，`ApiServerImpl`、`ApiScImpl` / `ApiDubboImpl`、`IXxxRemote`、`RemoteImpl` 都补上了（项目里有哪几种就补哪几种）。
4. **和设计对齐**：有设计文档时，对照 `requirement/`、`design/`、`plan/` 检查主路径、分支、失败处理。对不上就改代码或改文档，不留两边各说各的。小改动没有设计文档时跳过。
5. **必要测试**：用项目已有的测试方式，覆盖主路径、关键分支和失败路径。用户明确说不测试时跳过，并在回复里说明。
6. **性能**：看高并发下会不会成为热点：循环里查库或远程调用、全表查询、`queryList` 没有 `top`、锁和共享可变状态、热路径上频繁创建大对象。能指出具体热点就改；说不出热点，不为性能加缓存、对象池或异步。
7. **有没有多写**：没要求的抽象、重复造的工具、能删的代码，删掉。
8. **业务数据依赖**：这次改动有没有新增外部数据来源、新增或删掉自管理的数据、改变对外提供的数据范围？有就按 [rules/10-docs.md](rules/10-docs.md) §5.2 更新项目说明的「业务数据依赖」一节；没有就在回复里说一句这次不涉及。
9. **架构类项目的补充项**：再按 [11-architecture.md](rules/11-architecture.md) §11 查。
10. 自检结果在回复里写几句：对齐了没有、补了什么测试、性能上改了什么或为什么不用改。

自检通过后按 §7 判断要不要复核；要复核的，复核完再更新计划状态。小改动没有计划文档，在回复里说明完成情况即可。

## 7. 复核（复杂改动必做）

§6 是自己查自己，容易被自己的假设带偏。新需求开发和复杂变更做完后，另起一个**没参与开发**的子 agent 审代码：它手里只有需求和设计，看的是「代码到底有没有做到要求」。规则文件见 [rules/12-review.md](rules/12-review.md)。

1. **什么时候做**：新需求开发、主流程变了、跨多个模块或层、动了对外契约、改了表结构、新增外部依赖。修 bug、改字段默认值、改配置和文案这类小改动不做。
2. **怎么起**：用 IDE 的 subagent / Task 工具或新开会话，不给它本次开发的对话和思考过程，只给仓库路径、需求、设计（含图）、计划、改动文件清单。模板在 [12-review.md](rules/12-review.md) §3。
3. **审什么**：按 [12-review.md](rules/12-review.md) §2 的十项过，核心是需求逐条有没有落点、设计里的分支和失败路径有没有漏、契约和规范有没有少。
4. **怎么处理**：阻断级必须改，改完让同一个子 agent 复审，最多两轮；两轮还卡住就停下来告诉用户卡在哪。建议级自己判断，不采纳的说明原因。子 agent 判错的驳回，最终判断权在自己。
5. **复核完更新计划状态**：按 [rules/10-docs.md](rules/10-docs.md) §3.1 维护 `plan/<主题>-计划.md`——每完成一步勾一步，开发做完改 `待复核`，复核、测试、文档都过了改 `已完成`。上层的总管角色只读这个字段看进展，不要留到最后一次性补。
6. **回复里给结论**：几轮、阻断几条已改、建议几条没采纳和原因，不复述被改代码的细节。

## 项目识别

开工前从项目本身判断一次，同一会话里确认过就不再重复。三个 skill 的适用范围不同：

- **easyfk-framework-skill、easyfk-reverse-skill**：只用于 easyfk 项目，识别不到就不使用、不安装。
- **easyfk-dev-skill**：识别到 easyfk 时全量使用；识别不到时只用下面「可以用」那一组，框架相关的部分全部停用。

识别到下面任意一个 easyfk 特征，就全量使用本套件：

1. **组件坐标以 `easyfk-` 开头**：构建文件里引入了 `easyfk-` 开头的组件，如 `easyfk-dependencies`、`easyfk-core`。Gradle 看根和各模块的 `build.gradle(.kts)`、`settings.gradle`、`gradle/libs.versions.toml`、`gradle.properties`；Maven 看根和各模块的 `pom.xml`。
2. **包名以 `com.mcst` 开头**：项目源码的包名，或 import 的类，以 `com.mcst` 开头。

还没有代码、要从零新建时，用户明确要求按 easyfk 建也算。

**识别不到 easyfk 时**，不是整套都不能用，按两组处理：

| 可以用（与框架无关） | 不能用（依赖 easyfk） |
|---|---|
| 写能工作的最少实现（§5）、阿里开发规范、日志与注释 | 模块选型（§1）、按 BOM 版本路由框架文档（§0 第 2 步） |
| 文档与计划：需求、分析、计划、项目说明、迭代记录、画图（[rules/10-docs.md](rules/10-docs.md)） | 分层与契约写法（§3）；[rules/01-project.md](rules/01-project.md) 到 [rules/09-config.md](rules/09-config.md)、[rules/11-architecture.md](rules/11-architecture.md) 里的具体写法；§4 里来自框架的命名 |
| 自检（§6）、复核（§7）、项目定位与业务数据依赖 | `easyfk-` 坐标、私服配置、框架类名注解与配置前缀 |
| 通用工程判断：事务边界、唯一性、索引、并发与性能、测试 | easyfk-framework-skill、easyfk-reverse-skill 两个 skill |

- 用通用规范时**不要拿 easyfk 的写法往普通项目上套**：不写 `IXxxApi` / `ApiServerImpl` / `IXxxRemote` 这套契约，不引 `com.mcst` 依赖，不去查框架文档。
- **要说清能力打折**：回复里提一句——不用 EasyFK 时本 skill 只剩通用开发规范，框架能力地图、按版本给的确切类名与配置、版本路由这些最有价值的部分用不上；项目本来就不打算用 EasyFK 的话，通用 coding skill 更合适。
- 不安装套件。用户明确要求装，或之后项目引入了 easyfk，再按「套件安装检查」装。

## 套件安装检查

easyfk-framework-skill、easyfk-dev-skill、easyfk-reverse-skill 放在同一个仓库 `https://github.com/easybuild-jack/easyfk-skill.git` 里，安装后是 skills 目录第一层的三个平级目录（嵌套在子目录里通常不会被识别为 skill）。

1. **查找**：按顺序找含 `SKILL.md` 且 `name` 对得上的目录，找到就停：本 skill 所在目录的同级 → 项目下的 `.cursor/skills/`、`.claude/skills/` → 用户目录下的 `~/.cursor/skills/`、`~/.claude/skills/`。
2. **安装**：找不到时，把仓库克隆到临时目录，用安装脚本装到本 skill 所在的 skills 目录（找不到本 skill 的目录时装到 `~/.cursor/skills/`），安装前在回复里说一句装到哪里：

   ```
   git clone --depth 1 https://github.com/easybuild-jack/easyfk-skill.git <临时目录>/easyfk-skill
   powershell -ExecutionPolicy Bypass -File <临时目录>/easyfk-skill/install.ps1 -Target <skills 目录>   # Windows
   sh <临时目录>/easyfk-skill/install.sh <skills 目录>                                              # macOS / Linux
   ```

   脚本会把三个 skill 一起装上，已有的同名目录先删再装。
3. **旧版**：skills 目录里有 `name: easyfk-skill` 的目录时，它是改名前的框架 skill。提醒用户按第 2 步重装，安装脚本会把它移除，避免新旧两份同时生效。
4. **更新**：已安装的不自动更新。项目的 easyfk 版本在 `<framework>/versions/index.md` 里找不到、或用户要求更新时，按第 2 步重新安装。
