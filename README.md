# easyfk-skill

EasyFK（易架构）的 AI Skill 套件，仓库：[easyfk-skill.git](https://github.com/easybuild-jack/easyfk-skill.git)。套件里有三个平级的 skill，分工不同、互相按名称引用：

| skill | 管什么 | 什么时候触发 |
|---|---|---|
| [easyfk-framework-skill](easyfk-framework-skill/SKILL.md) | 框架有什么：工程与模块、能力、需求选型、工具类、组合约束，按 easyfk 版本路由到文档快照 | 查框架能力、选模块、查配置前缀 |
| [easyfk-dev-skill](easyfk-dev-skill/SKILL.md) | 怎么写：分层、命名、各层写法、架构类项目、文档、自检 | 写代码、新建项目或模块、写需求设计计划 |
| [easyfk-reverse-skill](easyfk-reverse-skill/SKILL.md) | 怎么反推：从代码还原业务分析报告和架构分析报告 | 梳理已有项目、补流程图架构图 |

三个 skill 只在识别到 easyfk 的项目中使用：构建文件引入了 `easyfk-` 开头的组件坐标，或源码包名以 `com.mcst` 开头。识别不到就不使用。

## 安装

三个 skill 必须是 skills 目录**第一层**的平级目录，嵌套在 `easyfk-skill/` 下通常不会被识别。用安装脚本一次装三个：

```
git clone --depth 1 https://github.com/easybuild-jack/easyfk-skill.git
powershell -ExecutionPolicy Bypass -File easyfk-skill/install.ps1 [-Target <skills 目录>]   # Windows
sh easyfk-skill/install.sh [<skills 目录>]                                                # macOS / Linux
```

- 目标目录默认 `~/.cursor/skills`（个人全局）；装到某个项目用 `<项目>/.cursor/skills`；Claude Code 用 `~/.claude/skills`。
- 已有的同名目录先删再装；发现改名前的旧版 `easyfk-skill`（`name: easyfk-skill`）会一并移除。
- 更新：重新克隆并运行安装脚本。

## 框架 jar 包仓库

easyfk 不开源但可免费使用，jar 包只发布在腾讯 CNB 的 Maven 私服上，需要在本地配置仓库和访问令牌才能下载：

- 仓库地址：`https://maven.cnb.cool/jackorg/easybuild/-/packages/`
- 用户名：`cnb`，访问令牌：`a16k9BILdyo166eyeyja7Old60H`（外部访客令牌 `eb-guest`，只能下载）

Maven `settings.xml` 和 Gradle 的完整配置示例见 [easyfk-framework-skill/SKILL.md](easyfk-framework-skill/SKILL.md) §8.1。

## 目录结构

```
easyfk-skill/
├── README.md                 本文件
├── install.ps1 / install.sh  安装脚本
├── easyfk-framework-skill/   框架能力地图 + 版本快照（versions/<版本>/）
│   ├── maintenance.md        套件维护流程（升级版本、对齐模块修改）
│   └── scripts/              快照同步脚本
├── easyfk-dev-skill/         开发规范，rules/ 下按层拆分
└── easyfk-reverse-skill/     反推
```

## 维护

维护流程写在 [easyfk-framework-skill/maintenance.md](easyfk-framework-skill/maintenance.md) 里，直接对 AI 说即可，例如：

- 把 easyfk-skill 升级到 3.5.16，源码在 D:\codespace\framework\easyfk_3.5.16
- 3.2.12 的 component-cache 改了，源码在 D:\codespace\framework\easyfk_3.2.12，对齐 skill

AI 会从套件目录的实际位置拼出绝对路径执行，套件目录移到哪里都可以。模块 skill 文档只保存在 `easyfk-framework-skill/versions/<版本>/modules/`，直接在那里修改。
