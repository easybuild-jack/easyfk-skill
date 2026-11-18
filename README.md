# easyfk-skill

**EasyFK（易架构）的 AI Skill 套件**：让 AI 在 EasyFK 项目里知道框架有什么、代码该怎么写、已有系统是怎么运转的。

> ## 先了解 EasyFK，再用这套 skill
>
> 这套 skill 是 [EasyFK 架构](https://www.easybuild.pro/easyfk) 的配套说明书，**脱离 EasyFK 用不了**。它讲的模块坐标、分层写法、配置前缀、类名注解，全部来自 easyfk 框架本身，不是通用的 Spring 经验。
>
> 上手前请先读官网，了解这套架构是什么、有哪些模块：**<https://www.easybuild.pro/easyfk>**

---

## 1. 这套 skill 为什么离不开 EasyFK

[EasyFK（易架构）](https://www.easybuild.pro/easyfk) 是企业级的 Java 技术底座，定位是「一次建设，全局复用」：12 个核心模块、40+ 可插拔组件、统一依赖治理，把所有项目都要重复搭的基础设施（统一返回体、异常、日志、鉴权、ORM、缓存、MQ、线程池……）做成标准化组件，业务项目按需引入即可开工。

配套的 AI skill 之所以必须绑定这套架构，有三个绕不开的原因：

| 原因 | 说明 |
|---|---|
| **框架闭源，能力只存在于框架里** | `com.mcst:*` 的 jar 只发布在私有 Maven 仓库。模块有哪些、类叫什么、注解怎么写、配置前缀是什么，AI 靠通用知识猜不出来，猜错就是编译不过 |
| **编码规范由框架的分层决定** | `Controller → IXxxApi → Service → Repository → Mapper` 这一套（以及 `ApiServerImpl / ApiScImpl / ApiDubboImpl` 的多栈实现）是 EasyFK 的约定，不是普通 Spring 项目的写法 |
| **框架在演进** | 不同 easyfk 版本的类名、配置项、模块增减都不一样。skill 按项目实际依赖的 BOM 版本加载对应快照，写出来的才是这个版本真正能跑的代码 |

所以判断标准很明确——**项目里没有 `easyfk-` 开头的组件坐标、源码包名也不是 `com.mcst` 开头，就不要用这套 skill**。它不是通用 Java 开发助手。

## 2. 它解决什么问题

| 没有 skill 时 | 有 skill 时 |
|---|---|
| AI 不知道框架已经提供了 `Result`、线程池、缓存、锁、业务编号，于是自己写一份，或者随手引入 Guava、commons-lang3 等重复能力 | 先查框架能力地图，有现成模块就按模块文档的类名和配置写，缺什么才补什么 |
| 分层靠猜：Controller 直接注入 Service、跨服务调用不走契约、事务和唯一性校验漏掉 | 按规范逐层写：主键 `String` + UUID、`@Transactional`、`@SingleUniqueField`、契约四件套一次补齐，写完自检 |
| 框架升级后 AI 还在用旧版本的类名和配置前缀 | 从 BOM 读出项目版本，路由到该版本的文档快照，写的就是这个版本的 API |
| 接手一个没人维护的老项目，读代码如读天书 | 从入口反推出两份报告：业务分析报告 + 架构分析报告，含流程图、时序图、高可用方案 |

## 3. 三个 skill 的分工

三个 skill 平级安装、互相按名称引用，一个需求通常由其中一个主导：

| skill | 回答的问题 | 典型触发 |
|---|---|---|
| [easyfk-framework-skill](easyfk-framework-skill/SKILL.md) | 框架**有什么**：工程与模块、每个模块解决什么问题、这个需求该选哪个模块、有哪些现成工具类、配置前缀是什么 | 「要发 MQ 用哪个模块」「有没有现成的对象转换工具」「easyfk 支持分库分表吗」 |
| [easyfk-dev-skill](easyfk-dev-skill/SKILL.md) | 代码**怎么写**：分层、命名、各层写法、事务与异常、架构类项目的模块拆分与线程模型、文档、自检 | 「订单模块加一个取消接口」「按 easyfk 建一个新项目」「写个 starter」 |
| [easyfk-reverse-skill](easyfk-reverse-skill/SKILL.md) | 系统**是什么样**：从现有代码还原业务分析报告和架构分析报告 | 「梳理一下这个老项目的业务流程」「补一张整体架构图」 |

依赖是单向的：写代码前先查框架能力（dev → framework），反推框架调用时也要查框架（reverse → framework）。

## 4. 安装

支持 Cursor、Claude Code 等读取 `SKILL.md` 的 AI 编码工具。三个 skill 必须是 skills 目录**第一层**的平级目录，嵌套在 `easyfk-skill/` 子目录下通常不会被识别。

```bash
git clone --depth 1 https://github.com/easybuild-jack/easyfk-skill.git
```

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File easyfk-skill/install.ps1 [-Target <skills 目录>]
```

```bash
# macOS / Linux
sh easyfk-skill/install.sh [<skills 目录>]
```

- 目标目录默认 `~/.cursor/skills`（个人全局）；只给某个项目装用 `<项目>/.cursor/skills`；Claude Code 用 `~/.claude/skills`。
- 已有的同名目录会先删再装；发现改名前的旧版 `easyfk-skill`（`name: easyfk-skill`）会一并移除。
- 装完重启 IDE 或新开会话生效。**更新**：重新克隆再跑一次安装脚本即可。

## 5. 怎么用

**不需要手动指定 skill。** 在 EasyFK 项目里正常提需求，AI 会先从构建文件（`easyfk-` 坐标）或源码包名（`com.mcst`）认出这是 EasyFK 项目，再按 BOM 版本加载对应文档。识别不到就完全不启用，不会污染普通 Java 项目。

几个实际的说法：

| 你的需求 | 会发生什么 |
|---|---|
| 「订单模块加一个取消接口，要校验状态、记日志」 | 查框架有没有现成能力 → 按分层生成 Controller / Api / Service / Repository 全套 → 自检并说明改了什么 |
| 「这里要削峰，用 MQ 还是 Disruptor？」 | 对比 `mq-*` 与 `queue-disruptor` 的持久化、可靠性差异，给出选型和配置前缀，不自己造队列 |
| 「这个项目要同时支持 Dubbo 和 Feign 两种调用」 | 按多栈微服务形态给出契约与实现拆分方案 |
| 「这个老项目没人维护了，帮我理清业务」 | 找出所有入口（Controller、MQ 消费、XXL-JOB、Aeron、etcd 选主……）→ 输出业务分析报告 + 架构分析报告 |
| 「升级到新版 easyfk，哪些写法要改」 | 对比两版快照，列出改名的配置项、变化的类名，保留旧写法并注明「从哪个版本起改为」 |

## 6. 框架依赖

easyfk **不开源**，但可免费使用。框架的 jar 不发布在 Maven Central 等公共仓库，需要通过官方私有的 Maven 仓库获取。

仓库地址、访问令牌，以及 Maven / Gradle 的具体配置方法，见官网：<https://www.easybuild.pro/easyfk>

这一步是前提：没有配好仓库，`com.mcst:*` 的依赖会一律解析失败（找不到构件或 401）。

## 7. 目录结构

```
easyfk-skill/
├── README.md                 本文件
├── install.ps1 / install.sh  安装脚本
├── easyfk-framework-skill/   框架能力地图 + 版本快照
│   ├── SKILL.md              模块全景、需求选型、工具清单、能力边界、依赖接入
│   ├── maintenance.md        套件自身的维护流程
│   ├── versions/             按 easyfk 版本存放的文档快照
│   │   └── <版本>/           VERSION.md、manuals.txt、modules/、manuals/
│   └── scripts/              快照同步脚本
├── easyfk-dev-skill/         开发规范
│   ├── SKILL.md              总则、分层、命名、自检
│   └── rules/                按层与场景拆分的 11 份规则
└── easyfk-reverse-skill/     从代码反推业务与架构
    └── SKILL.md
```

## 8. 相关链接

- EasyFK 架构介绍：<https://www.easybuild.pro/easyfk>
- EasyFK 文档（开发环境、快速开始）：<https://www.easybuild.pro/docs/reader/dev-env>
- 本仓库：<https://github.com/easybuild-jack/easyfk-skill.git>
