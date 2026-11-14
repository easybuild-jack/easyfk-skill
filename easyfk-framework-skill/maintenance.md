# easyfk-skill 套件维护流程

> **读者**：本套件的作者本人。维护指的是让 skill 跟上 easyfk 框架的演进——升级到新版本、对齐某个模块的改动，需要 easyfk 源码和框架内部知识，只有作者能做。
>
> **使用方不需要看本文**。业务项目的开发者接入或更新 skill，只要重新克隆仓库跑一次 `install.ps1` / `install.sh`，方法见根目录 [README](../README.md)。

作者要求维护本套件时按本文执行，例如：

- “把 easyfk-skill 升级到 3.5.16，源码在 D:\codespace\framework\easyfk_3.5.16” → 流程 A（框架升级版本）
- “component-cache 改了，对齐一下 skill”、“3.2.12 的 orm 模块加了配置项，更新 skill” → 流程 B（同一版本里模块改了）

直接对 AI 说这两类话即可，AI 会从套件目录的实际位置拼出绝对路径执行，套件目录移到哪里都可以。模块 skill 文档只保存在 `versions/<版本>/modules/`，没有别处的源稿，修改直接改那里。

## 0. 要维护的文件

```
easyfk-skill/
├── README.md                        使用方看的介绍：能力、安装、用法（不写维护方法）
├── install.ps1 / install.sh         安装脚本，新增或改名 skill 时同步修改
├── easyfk-framework-skill/
│   ├── SKILL.md                     跨版本不变的能力地图（§2、§4、§5、§6、§7 随模块增减更新）
│   ├── maintenance.md               本文件
│   ├── versions/index.md            已收录版本与路由规则
│   ├── versions/<版本>/             VERSION.md、manuals.txt、modules/、manuals/
│   └── scripts/sync-references.ps1  新建版本快照的同步脚本
├── easyfk-dev-skill/                SKILL.md、rules/*.md
└── easyfk-reverse-skill/            SKILL.md
```

## 1. 路径规则（先做）

**所有命令和文件引用一律使用绝对路径，不使用相对路径，不依赖当前工作目录。** 套件目录可能被移到任何位置，下文的 `<套件目录>`、`<源码目录>` 都要先解析成绝对路径再拼接。

1. **定位套件目录**：取本文件所在目录（easyfk-framework-skill）的上一级目录，如果其中同时有 `install.ps1`、`README.md` 和 `easyfk-framework-skill`、`easyfk-dev-skill`、`easyfk-reverse-skill` 三个目录，它就是 `<套件目录>`。否则当前读到的是已安装的副本（如 `~/.cursor/skills` 下），**不要改副本**（重新安装会被覆盖），先问用户套件源目录（easyfk-skill 仓库或其工作副本）的绝对路径。
2. **确定源码目录**：用户没给对应版本 easyfk 源码目录的绝对路径时先问，不要猜。源码目录必须正好是该版本（如该版本 git tag 的检出），根目录下应有 `easyfk-dependencies` 等工程目录。
3. 下文路径以 `\` 书写；在 macOS / Linux 上换成 `/`。

## 2. 约束

- 只改 `<套件目录>` 下的文件；不改已安装的副本，不改 easyfk 源码。
- 不编译、不构建、不运行项目；读源码只为复查文档。
- 以源码为准；源码与手册冲突时按源码写，并记入模块文档末尾的「复查记录」。
- 模块 skill 文档只有快照里这一份（`<套件目录>\easyfk-framework-skill\versions\<版本>\modules\`），直接修改；同步脚本从不覆盖 `modules\`。
- `SKILL.md` 只写跨版本不变的内容，不写具体版本号；版本特有的说明写进该版本的 `VERSION.md`。

## 3. 流程 A：框架升级版本

变量：`<旧版本>` 默认取 `<套件目录>\easyfk-framework-skill\versions\index.md` 中标为“当前最新”的版本；`<新版本>`、`<源码目录>` 由用户给出。旧快照保持原样，**不修改 `versions\<旧版本>\` 下任何文件**。

1. **读现状**：`<套件目录>\easyfk-framework-skill\SKILL.md`、`versions\index.md`、`versions\<旧版本>\VERSION.md`、`versions\<旧版本>\manuals.txt`。`versions\<新版本>\` 已存在时先告诉用户，问是继续补全还是停止。
2. **生成新快照**（PowerShell，全部绝对路径）：
   ```
   powershell -ExecutionPolicy Bypass -File "<套件目录>\easyfk-framework-skill\scripts\sync-references.ps1" -Version <新版本> -From <旧版本> -RepoRoot "<源码目录>"
   ```
   脚本把旧版本的 `modules\`、`manuals.txt` 复制到 `versions\<新版本>\`，再按 `manuals.txt` 从 `<源码目录>` 拷贝使用手册。报告缺失手册时：在 `<源码目录>` 中找到改名或移动后的路径并修正 `versions\<新版本>\manuals.txt`，确实删除的就移除该行；新版本新增的手册补进清单；然后加 `-Force` 重跑。
3. **找出模块增减**：对比 `<源码目录>` 的工程与模块（`settings.gradle`、各工程目录、`easyfk-dependencies` 的 BOM 约束）和旧版本 `modules\` 的文档清单，列出新增、移除、改名的模块。
4. **逐份复查模块文档**（工作量最大的一步）：对 `versions\<新版本>\modules\` 下每一份 `*-skill.md`，按文档开头的依据说明（没有时按模块名）找到 `<源码目录>` 中对应模块的源码和手册，逐项核对坐标、类名、注解、接口方法、配置前缀和配置项、默认值、自动配置条件、示例代码，不一致的直接改。文中出现的版本号改成新版本的值。
   - 新增模块：参照同类文档的结构，新建 `<模块名>-skill.md`。
   - 移除的模块：删除对应文件，并清理其他文档中指向它的链接。
   - 模块改名：重命名文件，同步更新所有引用。
   - 文档末尾有「复查记录」的，更新为本次的差异；没有的，有差异时补一节。
5. **写 `versions\<新版本>\VERSION.md`**：参照旧版本 `VERSION.md` 的结构，写技术基线（JDK、Spring Boot / Cloud / Cloud Alibaba、关键三方版本，从 `<源码目录>` 的 BOM 读取）、构建参数（`easyfkVersion` 等）、本版本注意事项、**与上一版的差异**（新增或移除的模块、改名的配置项、变化的用法、需要业务项目改动的地方）、快照修订记录（只在快照中改过的手册）、文档索引（链接必须都能打开）。
6. **登记**：在 `versions\index.md` 中加入新版本并标为“当前最新”，旧版本改为“维护中”。
7. **更新能力地图**：有模块增减或能力变化时，同步修改 `<套件目录>\easyfk-framework-skill\SKILL.md` 的 §2 框架全景、§4 模块能力清单、§5 需求选型、§6 工具能力清单、§7 组合约束。
8. **检查另外两个 skill**：在 `<套件目录>\easyfk-dev-skill\`（`SKILL.md`、`rules\*.md`）和 `<套件目录>\easyfk-reverse-skill\SKILL.md` 中搜索它们写死的类名、注解、基类、配置前缀和模块坐标（如 `BaseRemoteImpl`、`DubboBaseRemoteImpl`、`@JobConfig`、`@XxlJobHandler`、`Processor`、`IngestQueueManager`、`@AeronTopic`、`ClusterStateMachine`、`LeaderElection`、`easyfk.config.*`），对照新版本源码确认是否仍然存在、用法是否变化。变化时写成“<版本> 起改为 …”，保留旧版本的写法，不要直接删掉，因为旧版本项目仍在用。
9. **自检**：
   - `versions\<新版本>\` 下所有 Markdown 链接都能打开，没有指向 `versions\<旧版本>\` 的链接。
   - `modules\` 中没有残留旧版本独有的类名、配置项和版本号。
   - `versions\<旧版本>\` 未被修改。
   - `SKILL.md` 中没有出现具体版本号。

## 4. 流程 B：同一版本里模块改了

变量：`<版本>` 是模块所在的 easyfk 版本（用户没说时问，或从 `<源码目录>` 的 `gradle.properties` / BOM 读取）；`<源码目录>` 是该版本源码的绝对路径。

1. 确定涉及的模块，读 `<套件目录>\easyfk-framework-skill\versions\<版本>\modules\<模块名>-skill.md`。
2. 对照 `<源码目录>` 中该模块的源码和手册逐项核对（同流程 A 第 4 步），直接修改文档，更新「复查记录」。
3. 模块的使用手册也改了时：确认它在 `versions\<版本>\manuals.txt` 中；先看 `versions\<版本>\VERSION.md`「快照修订记录」，其中列出的手册修改要先同步到 `<源码目录>` 的原手册，否则会丢失；然后重新拷贝手册：
   ```
   powershell -ExecutionPolicy Bypass -File "<套件目录>\easyfk-framework-skill\scripts\sync-references.ps1" -Version <版本> -RepoRoot "<源码目录>" -Force
   ```
4. 新增或移除了模块、换了推荐选型：同步修改 `SKILL.md` 的 §2、§4、§5、§6、§7，以及 `VERSION.md` 的注意事项和文档索引。
5. 影响写法规范（分层、基类、注解、配置前缀）时：同流程 A 第 8 步检查 easyfk-dev-skill 和 easyfk-reverse-skill。
6. 自检：改过的文档中的链接都能打开，其他文档中引用到改动内容的地方已同步。

## 5. 完成后回复用户

- 改了哪些文件（列 `<套件目录>` 下的绝对路径），模块增减和关键差异的摘要。
- 没能确认的地方（源码中找不到依据、手册与源码冲突未定的），逐条列出。
- 提醒：改动在 `<套件目录>` 中，需要提交推送到套件仓库；各机器重新运行 `<套件目录>\install.ps1`（或 `install.sh`）后才生效。
