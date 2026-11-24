# easyfk-skill 套件维护流程

> **读者**：本套件的作者本人。维护指的是让 skill 跟上 easyfk 框架的演进——升级到新版本、对齐某个模块的改动，需要 easyfk 源码和框架内部知识，只有作者能做。
>
> **使用方不需要看本文**。业务项目的开发者接入或更新 skill，只要重新克隆仓库跑一次 `install.ps1` / `install.sh`，方法见根目录 [README](../README.md)。

作者要求维护本套件时按本文执行，例如：

- “把 easyfk-skill 升级到 3.5.16，源码在 D:\codespace\framework\easyfk_3.5.16” → 流程 A（框架升级版本）
- “component-cache 改了，对齐一下 skill”、“3.2.12 的 orm 模块加了配置项，更新 skill” → 流程 B（同一版本里模块改了）
- “补一下 3.2.12 的 API 文档”、“API 文档缺了 xxx 模块” → 流程 C（只补 / 重生成 API 文档）

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
│   ├── versions/<版本>/             VERSION.md、manuals.txt、modules/、api/、manuals/
│   └── scripts/
│       ├── sync-references.ps1      新建版本快照：复制上一版 modules/、拷贝使用手册
│       └── gen-api.py               从该版本源码生成 api/（签名、常量、配置项、自动配置类）
├── easyfk-dev-skill/                SKILL.md、rules/*.md
├── easyfk-reverse-skill/            SKILL.md
└── easyfk-generator-skill/          SKILL.md（调 efg CLI 建工程，AI 不手写工程文件）
```

## 1. 路径规则（先做）

**所有命令和文件引用一律使用绝对路径，不使用相对路径，不依赖当前工作目录。** 套件目录可能被移到任何位置，下文的 `<套件目录>`、`<源码目录>` 都要先解析成绝对路径再拼接。

1. **定位套件目录**：取本文件所在目录（easyfk-framework-skill）的上一级目录，如果其中同时有 `install.ps1`、`README.md` 和 `easyfk-framework-skill`、`easyfk-dev-skill`、`easyfk-reverse-skill`、`easyfk-generator-skill` 四个目录，它就是 `<套件目录>`。否则当前读到的是已安装的副本（如 `~/.cursor/skills` 下），**不要改副本**（重新安装会被覆盖），先问用户套件源目录（easyfk-skill 仓库或其工作副本）的绝对路径。
2. **确定源码目录**：用户没给对应版本 easyfk 源码目录的绝对路径时先问，不要猜。源码目录必须正好是该版本（如该版本 git tag 的检出），根目录下应有 `easyfk-dependencies` 等工程目录。
3. 下文路径以 `\` 书写；在 macOS / Linux 上换成 `/`。

## 2. 约束

- 只改 `<套件目录>` 下的文件；不改已安装的副本，不改 easyfk 源码。
- 不编译、不构建、不运行项目；读源码只为复查文档。
- 以源码为准；源码与手册冲突时按源码写，并记入模块文档末尾的「复查记录」。
- 模块 skill 文档只有快照里这一份（`<套件目录>\easyfk-framework-skill\versions\<版本>\modules\`），直接修改；同步脚本从不覆盖 `modules\`。
- `versions\<版本>\api\` 是**生成物**，由 `scripts\gen-api.py` 从源码提取，不要手工编辑；签名不对就改脚本或重跑。`modules\` 里写的签名与 `api\` 冲突时，以 `api\`（源码）为准并修正 `modules\`。
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
   - 移除的模块：删除对应文件，并清理其他文档中指向它的链接。整个子模块下线时（如 `cache-mult`、`db-influx`，两个版本快照都已移除），删掉该文档里对应的整章并重排后续章节号，在文首加一行"<版本> 起已下线"，复查记录里留一行说明；`manuals.txt` 中对应的手册行也一并删掉。
   - 模块改名：重命名文件，同步更新所有引用。
   - 文档末尾有「复查记录」的，更新为本次的差异；没有的，有差异时补一节。
5. **生成 API 文档**：`versions\<新版本>\api\` 由脚本从源码重新生成，不要从旧版本拷贝（`sync-references.ps1` 也不复制它）。
   ```
   python "<套件目录>\easyfk-framework-skill\scripts\gen-api.py" --version <新版本> --repo-root "<源码目录>"
   ```
   脚本按文件顶部 `MODULES` 映射表逐个模块扫描 `src/main/java`，输出 `<模块>.api.md` 与 `INDEX.md`。模块有增减或改名时先改映射表（以及 `NO_SOURCE_NOTE` 里"没有 Java API"的说明）；新增模块在映射表中没有对应目录时会跳过并打印 `(none)`，需要补。**下线的子模块不要从 `MODULES` 里删**——写进顶部 `REMOVED_MODULES = {"子模块目录名", …}`，脚本生成时自动裁掉它的源码目录与坐标说明，并在 `INDEX.md` 里生成「已下线的子模块」一节。这样任何版本重新生成都不会把它带回来；真要恢复时从集合里删掉即可。`easyfk-aeron`、`aeron-cluster`、`etcd-cluster` 是独立仓库，要先检出到 `<源码目录>` 下（目录名与映射表一致），否则这三份会被跳过。生成后抽查 2～3 个模块：类型数是否与该目录下 `public class/interface/enum/record` 的条数一致、常用类的重载是否齐全、`@ConfigurationProperties` 的配置项和默认值是否正确（prefix 写成常量引用时脚本会自动解析）。
6. **写 `versions\<新版本>\VERSION.md`**：参照旧版本 `VERSION.md` 的结构，写技术基线（JDK、Spring Boot / Cloud / Cloud Alibaba、关键三方版本，从 `<源码目录>` 的 BOM 读取）、构建参数（`easyfkVersion` 等）、本版本注意事项、**与上一版的差异**（新增或移除的模块、改名的配置项、变化的用法、需要业务项目改动的地方）、快照修订记录（只在快照中改过的手册）、文档索引（链接必须都能打开，含 `api/` 一节）。
7. **登记**：在 `versions\index.md` 中加入新版本并标为“当前最新”，旧版本改为“维护中”。
8. **更新能力地图**：有模块增减或能力变化时，同步修改 `<套件目录>\easyfk-framework-skill\SKILL.md` 的 §2 框架全景、§4 模块能力清单、§5 需求选型、§6 工具能力清单、§7 组合约束。
9. **检查另外两个 skill**：在 `<套件目录>\easyfk-dev-skill\`（`SKILL.md`、`rules\*.md`）和 `<套件目录>\easyfk-reverse-skill\SKILL.md` 中搜索它们写死的类名、注解、基类、配置前缀和模块坐标（如 `BaseRemoteImpl`、`DubboBaseRemoteImpl`、`@JobConfig`、`@XxlJobHandler`、`Processor`、`IngestQueueManager`、`@AeronTopic`、`ClusterStateMachine`、`LeaderElection`、`easyfk.config.*`），对照新版本源码确认是否仍然存在、用法是否变化。变化时写成“<版本> 起改为 …”，保留旧版本的写法，不要直接删掉，因为旧版本项目仍在用。
10. **自检**：
   - `versions\<新版本>\` 下所有 Markdown 链接都能打开，没有指向 `versions\<旧版本>\` 的链接。
   - `modules\` 中没有残留旧版本独有的类名、配置项和版本号。
   - `versions\<旧版本>\` 未被修改。
   - `SKILL.md` 中没有出现具体版本号。

## 4. 流程 B：同一版本里模块改了

变量：`<版本>` 是模块所在的 easyfk 版本（用户没说时问，或从 `<源码目录>` 的 `gradle.properties` / BOM 读取）；`<源码目录>` 是该版本源码的绝对路径。

1. 确定涉及的模块，读 `<套件目录>\easyfk-framework-skill\versions\<版本>\modules\<模块名>-skill.md`。
2. 对照 `<源码目录>` 中该模块的源码和手册逐项核对（同流程 A 第 4 步），直接修改文档，更新「复查记录」。
3. **重生成 API 文档**：模块的类、方法、常量或配置项有变化时，按流程 A 第 5 步重跑 `gen-api.py`（整个版本重生成即可，脚本是幂等的）。
4. 模块的使用手册也改了时：确认它在 `versions\<版本>\manuals.txt` 中；先看 `versions\<版本>\VERSION.md`「快照修订记录」，其中列出的手册修改要先同步到 `<源码目录>` 的原手册，否则会丢失；然后重新拷贝手册：
   ```
   powershell -ExecutionPolicy Bypass -File "<套件目录>\easyfk-framework-skill\scripts\sync-references.ps1" -Version <版本> -RepoRoot "<源码目录>" -Force
   ```
5. 新增或移除了模块、换了推荐选型：同步修改 `SKILL.md` 的 §2、§4、§5、§6、§7，以及 `VERSION.md` 的注意事项和文档索引（含 `api/` 表）。
6. 影响写法规范（分层、基类、注解、配置前缀）时：同流程 A 第 9 步检查 easyfk-dev-skill 和 easyfk-reverse-skill。
7. 自检：改过的文档中的链接都能打开，其他文档中引用到改动内容的地方已同步。

## 5. 流程 C：只补 / 重生成 API 文档

用于"完善 API 文档"这类只动 `api/` 的请求，不动 `modules/`、`manuals/`、`VERSION.md` 正文。

变量：`<版本>`、`<源码目录>` 同流程 B。

1. 检查 `<套件目录>\easyfk-framework-skill\scripts\gen-api.py` 顶部的 `MODULES`：模块清单、坐标说明、源码目录是否覆盖本次要补的范围；`NO_SOURCE_NOTE` 是否仍然准确。
2. 重跑脚本（见流程 A 第 5 步）。脚本只覆盖 `versions\<版本>\api\`，不会碰 `modules/`。
3. 抽查：`INDEX.md` 的模块表是否覆盖 `modules/` 下所有模块（缺的要么补映射，要么写进 `NO_SOURCE_NOTE`）；任一模块的类型数与源码 `public` 类型数一致；配置项表非空。
4. 链接自检：`api/*.api.md` 文首回链 `../modules/<模块>-skill.md` 是否存在；`VERSION.md` §5.2 的表格与 `api/INDEX.md` 是否一致。
5. 源码不在本版本检出中的模块无法生成（aeron、aeron-cluster、etcd-cluster 是独立仓库，需分别检出到 `<源码目录>` 下，目录名与脚本 `MODULES` 映射表一致）。确实拿不到源码时，在脚本的 `NO_SOURCE_NOTE` 里写明原因，不要凭手册手写签名。

## 6. 完成后回复用户

- 改了哪些文件（列 `<套件目录>` 下的绝对路径），模块增减和关键差异的摘要。
- 没能确认的地方（源码中找不到依据、手册与源码冲突未定的），逐条列出。
- 提醒：改动在 `<套件目录>` 中，需要提交推送到套件仓库；各机器重新运行 `<套件目录>\install.ps1`（或 `install.sh`）后才生效。
