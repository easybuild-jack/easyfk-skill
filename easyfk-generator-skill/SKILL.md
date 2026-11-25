---
name: easyfk-generator-skill
description: >-
  用 CLI 生成项目：EasyFK 后端走 efg（JDK 21），EasyBuild Admin 中后台前端走 easybuild-admin（Node 18.17+，Next.js 16）。先确认生成意图（建哪条线、什么业务、新建还是改造已有）和必要参数，再执行 CLI 并核对产物。
  红线：意图不明确先问，不许用 -y 生成占位项目；项目文件只由 CLI 生成，AI 只准备参数、执行命令、核对结果，不手写 pom、源码、页面或配置；前端 CLI 连续失败才允许从 GitHub 拉模板兜底并告知用户，后端没有兜底路径。
  适用：新建 easyfk 后端项目、生成项目骨架、按表生成 Entity/Mapper/业务代码、刷新 DTO/Param、安装或升级 efg、efg 报错排查；新建 EasyBuild Admin 管理后台、Next.js admin 前端、前端脚手架。不负责写业务代码（dev）、框架模块（framework）、反推（reverse）。关键词：easyfk、efg、easybuild-admin、scaffold、Next.js admin、CRUD。
---

# 项目生成：后端 efg / 前端 easybuild-admin

本 skill 管两件事，对应两个不同的 CLI，**不要混用**：

| 要建什么 | CLI | 运行时前提 | 本文位置 |
|---|---|---|---|
| EasyFK 后端项目（Java / Spring / Maven） | `efg` | JDK 21 | §0–§5 |
| EasyBuild Admin 中后台前端项目（Next.js 16 / React 19） | `easybuild-admin` | Node.js ≥ 18.17（开发建议 ≥ 20.9） | §6 |

两者唯一的共同点：**项目文件由对应 CLI 生成，AI 只准备参数、执行命令、核对产物。**

原始细节看 `reference/` 下的两份原版手册（未改动）：后端 [cli使用手册.md](reference/cli使用手册.md)，前端 [前端脚手架使用手册.md](reference/前端脚手架使用手册.md)。本文只留「做决定和动手时必须知道的」，冲突时以本文实测过的步骤为准。CLI 换版本时，把新发布包根目录同名的 `cli使用手册.md` 拷过来覆盖即可。

本 skill 属于 easyfk-skill 套件，四个 skill 平级、互相按名称引用：

| skill | 管什么 |
|---|---|
| easyfk-framework-skill | 框架有什么：模块、能力、类名、配置前缀、版本快照 |
| easyfk-dev-skill | 代码怎么写：分层、命名、文档、自检、复核（仅 EasyFK 后端 Java） |
| easyfk-reverse-skill | 已有系统是什么样：从代码反推业务与架构报告 |
| easyfk-generator-skill（本 skill） | 项目怎么建出来：后端走 efg（装 CLI → 问参数 → 写 generator.yml → 核对产物）；前端走 easybuild-admin（问参数 → npx 生成 → 核对 package.json） |

## 生成前：先确认意图（前后端通用）

**没确认要生成什么，就不要生成。** 后端、前端一样：先确认意图 → 再确认参数 → 最后才跑 CLI。不允许「先跑一条命令看看」：`-y` 会直接生成一个占位项目，错了就是半套目录和一次重来。

### 意图明确的四条判据

| 判据 | 要回答 | 不明确的后果 |
|---|---|---|
| 建哪条线 | EasyFK 后端，还是 EasyBuild Admin 前端？ | 用错 CLI，产物完全不对 |
| 建什么业务 | 项目做什么、给谁用？ | 描述、后端 `project-type` / `app-type`、菜单权限都要返工 |
| 新建还是改已有 | 从零建独立项目，还是在现有项目里加东西？ | 已有项目被当成新项目生成，覆盖或留下半套目录 |
| 落在哪 | 父目录 + 项目名（英文小写）？ | 建错位置，或目录重名 |

缺哪条问哪条，一次问完，不要分几轮挤。能从上下文推断的先推断再复述给用户确认，不要默认；推断不出来的直接问。用户明确说「你定就行」时，把推断结果和将用的默认值列出来说明后再生成，不要静默套默认值。

### 常见歧义，先问再动

| 用户说法 | 先确认什么 |
|---|---|
| 「建个管理后台」「建个中后台」 | 是 EasyBuild Admin 前端（Next.js），还是 EasyFK 后端的 BMS 应用？两者 CLI 不同 |
| 「用 easyfk 建个项目」 | 是后端，但 `project-type`、业务、包名仍要问 |
| 「生成个项目骨架就行」 | 只要骨架（`efg -p`），还是完整业务代码？有没有可用的数据库和表？ |
| 「在这里加个模块 / 页面」 | 不是新建项目：后端按 §0.3 场景 C 加表，前端按模板 `docs/开发文档.md` 加页面，都不跑脚手架 |
| 「名字随便」「你看着办」 | 项目名就是目录名 / 包名，必须给具体值；可以给建议，但要用户确认 |

### 已有项目先停一下

当前目录或用户指定的目录里已经有工程（`pom.xml` / `build.gradle`，或 `package.json` 带 easyfk / EasyBuild 特征）时，**默认不是新建**：先读现状、问清是加功能还是重建，再决定走哪条。不要为了「生成」去覆盖已有目录。

### 确认之后

意图确认了再走各自动作：后端 §1 问参数 → §2 写 `generator.yml` → §3 执行；前端 §6.2 问参数 → §6.3 执行。参数没确认也不跑 CLI（红线第 6 条）。

## 红线（不可越过）

1. **意图不明确不生成。** 建哪条线、什么业务、新建还是改已有、落在哪，这四条没问清就先问（见上一节）；不许用 `-y` 生成默认占位项目来「试试」，也不许边生成边补问。
2. **项目文件只能由对应 CLI 生成。** 后端只认 `efg`，前端只认 `easybuild-admin`。不手写 `pom.xml` / `build.gradle`、不 `mkdir src/main/java`、不写 `XxxController.java`；也不手写 `next.config.mjs`、页面、组件、`package.json` 冒充脚手架产物（§6.7 降级时改 `package.json` 元信息除外）。
3. **AI 只写 CLI 的输入。** 后端是 `generator.yml`，前端是命令行参数；脚本、jar、模板目录都不是 AI 该造的东西，也不在 CLI 之外用脚本「补齐」缺失文件。
4. **生成失败就承认失败。** 先按对照表（后端 §4.2、前端 §6.6）定位，能改参数再重跑；改不了就如实说明「卡在哪一步、缺什么」。前端 CLI 连续失败才允许按 §6.7 从 GitHub 拉模板，且必须告诉用户；后端没有降级路径，不许手工拼工程。
5. **后端没有可用的表结构，就只能出骨架。** 实测：没有数据库或拿不到 `db-tables` 的字段时，CLI 在生成 Dto/Param 阶段会报 `modelInfo.fieldList` 为空并退出码 1，业务代码一行都出不来。这时只能 `efg -p` 生成骨架，并明确告知用户业务代码需要数据库或表结构。
6. **不要在用户没确认参数前就跑全量生成。** 参数错一次会留下半套目录，清理比重生成麻烦。前端尤其如此：项目名同时是目录名和 `package.json.name`，错了只能重建。

## 0. 后端起步：查环境、查安装、定场景

> §0–§5 只讲 **EasyFK 后端**。要建 EasyBuild Admin 中后台前端项目，直接跳到 §6——不需要 JDK、不需要 `efg`、也不写 `generator.yml`。

### 0.1 环境检查（JDK 21）

```bash
java -version    # 需要 21 或更高
```

- 没有 Java 或版本低于 21：停下来，让用户装 JDK 21（<https://adoptium.net/zh-CN/>），不要尝试装 JDK 或改 `JAVA_HOME`。
- 装完 `java -version` 还是旧版本，多半是 PATH 里旧 JDK 在前，提示用户调整。

### 0.2 安装状态检查与安装

**先查是否已装：**

```bash
efg -V
# 期望输出：easyfk-generator 3.5.16
```

`efg` 不在 PATH 时先看安装目录（Windows `%USERPROFILE%\.easyfk-gen`，macOS / Linux `~/.easyfk-gen`）：目录里有 `efg.bat` / `efg` 说明装过但当前会话 PATH 没生效，直接用绝对路径调用即可，不必重装。已装但版本不是 3.5.16 时，按下面重装一次（`-fv` 只改生成的目标框架版本，不会换 CLI 版本）。

**没装就装**（发布包：<https://easyfk.oss-cn-beijing.aliyuncs.com/file/efg-3.5.16.zip>，约 25 MB）。安装会写用户 PATH，执行前在回复里说一句「装到 `~/.easyfk-gen`」。

macOS / Linux：

```bash
curl -L -o /tmp/efg.zip https://easyfk.oss-cn-beijing.aliyuncs.com/file/efg-3.5.16.zip
unzip -q /tmp/efg.zip -d /tmp          # 得到 /tmp/efg-3.5.16
sh /tmp/efg-3.5.16/install
```

Windows（PowerShell）：

```powershell
Invoke-WebRequest -Uri https://easyfk.oss-cn-beijing.aliyuncs.com/file/efg-3.5.16.zip -OutFile "$env:TEMP\efg.zip"
Expand-Archive -Path "$env:TEMP\efg.zip" -DestinationPath $env:TEMP -Force   # 得到 %TEMP%\efg-3.5.16
powershell -ExecutionPolicy Bypass -File "$env:TEMP\efg-3.5.16\install.ps1"
```

- **Windows 不要用 `install.bat`**：它末尾有 `pause`，在非交互终端会挂住。用 `install.ps1`。
- 安装脚本做四件事：检查 Java → 解压发布包 → 拷 jar 和 `lib/` 到安装目录并生成 `efg.bat` / `efg` 启动脚本 → 把安装目录写进用户 PATH（Windows 写用户 PATH，*nix 写 shell profile）。
- **不要用 shell 手工拷 jar 代替安装**：启动脚本里的 classpath 是安装脚本生成的，路径写错就是 `ClassNotFoundException`。
- 手册里写「安装脚本会按 `CHECKSUMS.txt` 逐个校验」，3.5.16 的包里其实没有这个文件、脚本也不做校验，别去找它。

**验证（安装脚本不会给当前会话注入新 PATH，直接用绝对路径验证）：**

```bash
"$HOME/.easyfk-gen/efg" -V                      # macOS / Linux
"%USERPROFILE%\.easyfk-gen\efg.bat" -V          # Windows（Git Bash 用 /c/Users/<用户>/.easyfk-gen/efg.bat）
```

输出 `easyfk-generator 3.5.16` 才算装好。要让 `efg` 在终端里直接可用，提示用户重开终端。

**安装失败的常见原因：**

| 现象 | 处理 |
|---|---|
| `未检测到 Java` | 回到 §0.1 装 JDK 21 |
| 下载 404 / 超时 | 确认 URL 完整；公司网络需代理时提示用户，不自己改代理配置 |
| `未找到 unzip` | macOS/Linux 装 unzip；Windows 用 `Expand-Archive` |
| 装完 `efg -V` 仍找不到命令 | PATH 未生效，用绝对路径；或用户 PATH 没写入，重跑安装脚本并检查输出 |

### 0.3 定场景（决定后面问什么、跑哪条命令）

| 场景 | 判据 | 走哪条 |
|---|---|---|
| A. 从零新建项目，要完整业务代码 | 用户要「建个项目做 XX 业务」 | 需要数据库 + 表名 → §1 全量参数 → `efg` |
| B. 只要项目骨架 | 用户只要工程结构，或暂时没有数据库 | 不需要数据库 → `efg -p` |
| C. 已有项目加表 | 项目已存在（有 `easyfk-` 坐标或 `com.mcst` 包名）且要加实体 | 改 `db-tables` → `efg -m` 然后 `efg -s` |
| D. 表结构变更 | 表改了字段，要同步 DTO / Param | `efg -d` |
| E. 新建中后台前端项目 | 要建 EasyBuild Admin / 管理后台 / Next.js 后台前端 | 跳过本节，走 §6 |

C、D 是在已有项目上补代码，`project-dir` / `project-name` / `base-package` 必须与现有项目一致，先读现有 `pom.xml` 或 `build.gradle` 取准，不要新建目录。

## 1. 问清要生成什么（参数）

先过「生成前：先确认意图」：建哪条线、什么业务、新建还是改已有、落在哪都清楚了，再来问参数。意图不清就问意图，别拿参数问题绕过去。

原则：**能推断的先推断并复述，只问缺的、且会影响结构的项；一次问完，不一轮一轮挤牙膏。** 用 IDE 的提问工具一次问 3~4 个，最多两轮。

先做一遍推断再开口：用户说「建个订单微服务」→ `project-type: microservice`、`rpc-type` 二选一；用户在某个仓库里说「加张表」→ 走场景 C，直接读现有配置；用户给了 `com.foo.order` 这类包名 → `group-id`、`base-package` 基本能定。

下面只列「必须问到的」，其余字段（`artifact-id`、`gradle-type`、`controller-auto-config`、资源权限的 `resource-*`、`model-list` 各字段）和每个字段的默认值，查 [手册的「配置文件说明」](reference/cli使用手册.md)。

### 1.1 必问项（项目配置）

| 要问的 | 字段 | 说明 |
|---|---|---|
| 生成什么类型的项目 | `project-type` | 见 §1.2，**必须显式写**：不写时 CLI 默认 `smart`，和用户预期常常不符 |
| 项目输出到哪 | `project-dir` | 父目录，生成结果是 `<project-dir>/<project-name>` |
| 项目名 | `project-name` | 同时是根目录名和子模块名前缀 |
| Maven 坐标 | `group-id`、`base-package` | 不确定时按 `com.<公司>.<项目>` 提方案让用户确认 |
| 模块名 | `module-name` | 用于生成配置类名、serviceId，通常等于项目名去掉连字符 |

### 1.2 项目类型与连带必填项

| `project-type` | 是什么 | 连带必填 / 注意 |
|---|---|---|
| `single` | 单体项目，所有代码在一个工程 | `app-type` 必填 |
| `micro_prd` | 产品层，只有启动类+配置，通过 RPC 调后端 | `rpc-type` 必填；不生成任何业务代码，不用问数据库和表 |
| `microservice` | 微服务，API + Server + PRD 模块 | `rpc-type` 建议明确（`cloud` / `dubbo`），不写默认 `NONE` |
| `smart` | 智能型，同时生成 Spring Cloud 和 Dubbo 两套通道 | 项目类型缺省值就是它，容易「没说就中招」 |
| `smart_orm` | 智能型 + ORM 层抽离成独立 `-orm` 模块 | 可用 `orm-modules` 选 `MYBATIS` / `MYBATIS_FLEX` / `HIBERNATE`，不写全生成 |

`app-type`（`BMS` 后台管理 / `CLIENT` 面向 C 端）在 `project-type` 为 `single`、`micro_prd`，或 `prd-type: single` 时必填——生成前一定要有值。

### 1.3 其余技术选型（可给默认值让用户确认）

| 问什么 | 字段 | 默认建议 |
|---|---|---|
| 构建工具 | `build-type`（+ gradle 时 `gradle-type`） | `maven`；用户项目是 Gradle 就用 `gradle` + `groovy` |
| ORM | `orm-type` | 常规业务用 `MYBATIS`（MyBatis-Plus）；不需要 ORM 用 `NONE` |
| Controller 层 | `prd-type` | 有前端对接用 `single`；要分 C 端和后台用 `separation`；纯服务用 `none` |
| RPC 框架 | `rpc-type` | 微服务：`cloud`（Feign）或 `dubbo` |
| 权限模块 | `include-auth` | 后台管理类项目常要 `true` |
| 框架版本 | `framework-version` | 默认 `3.5.16`（可选 `3.2.12`，与本次装的 CLI 版本无关，可被 `-fv` 覆盖） |
| 日志框架 | `log-type` | `LOGBACK` |

### 1.4 业务代码必问：数据库与表

场景 A（以及 C、D）必须问到，否则业务代码生成不出来：

| 字段 | 说明 |
|---|---|
| `db-type` | `MYSQL` / `POSTGRE_SQL` / `ORACLE` / `MARIADB` / `SQL_SERVER` / `DM` / `KINGBASE_ES` / `GAUSS` / `OCEAN_BASE` / `CLICK_HOUSE` 等 |
| `db-short-url` | 短连接 `host:port/database`，不带 `jdbc:` 前缀 |
| `db-user`、`db-pwd` | 密码含特殊字符时用引号包住 |
| `db-tables` | 要生成代码的表名，逗号分隔。**这里是业务代码的唯一字段来源** |
| `table-prefix` | 生成类名时忽略的前缀，多个用逗号分隔（`t_`、`base_,auth_`） |

- 用户说不清表名：让他给出库名，用数据库客户端只读查一下 `information_schema.tables` 列出来再确认（**只读，不改库**）。
- 用户暂时没有可用数据库：退到场景 B，只 `efg -p`，说明业务代码等库就绪后再跑 `efg -m` / `efg -s`。
- 驱动：MySQL 驱动已随包装进 `lib/`；PostgreSQL 驱动内置；其它数据库要把对应驱动 jar 放进 `<安装目录>/lib/`。CLI 提示「缺少数据库驱动 xxx」时按这个办，不要改 classpath。

### 1.5 `model-list` 的正确定位

`model-list` 用来在 `db-tables` 基础上**覆盖元数据**：`model-desc`、`only-repository`、`create-controller`、`forbidden-filed`、`table-name`，以及资源权限那几个字段。

**不要用 `model-list` 代替数据库**：实测只给 `model-list`（哪怕带 `field-list`）而不给 `db-tables` 时，CLI 在 Dto/Param 阶段报 `modelInfo.fieldList` 为空并退出码 1，一条业务代码都生成不出来。需要新表就去建表或用已有表。

## 2. 写 generator.yml

- 目录里还没有配置时，先跑 `efg init` 生成模板（已存在时 CLI 只警告、不覆盖，退出码仍是 0），再按 §1 的答案改；已有配置就直接改。
- 用 `-c <文件>` 指定配置时，文件名随便，但**必须在配置文件所在目录执行**，或在 `-c` 里给绝对路径。
- 配置格式和 Spring Boot 的 `application.yml` 一致，缩进对层级：`easyfk.config.generator.project` 和 `easyfk.config.generator.code`。
- 手册「完整配置示例」一节给了 8 套配置：single 最小配置、micro_prd、microservice（Cloud）、microservice（Dubbo）、smart、smart_orm、从库解析表结构、带资源权限，照着改比从零拼快；本文 §1 只保证问全必填项。

最小可用的 `single` 配置（字段含义见 §1）：

```yaml
easyfk:
  config:
    generator:
      project:
        project-dir: D:/workspace/projects   # 父目录
        group-id: com.example
        project-name: demo-app
        base-package: com.example.demo
        project-type: single
        app-type: BMS
        build-type: maven
        orm-type: MYBATIS
        prd-type: single
        framework-version: 3.5.16
      code:
        module-name: demo
        db-type: MYSQL
        db-short-url: 127.0.0.1:3306/demo_db
        db-user: root
        db-pwd: "123456"
        table-prefix: t_
        db-tables: t_product,t_order
```

- Windows 路径在 YAML 里用正斜杠 `D:/workspace/projects` 最稳。
- 项目类型为 `micro_prd` 时不写 `code.db-*` 和 `db-tables`，写了也会被忽略。

## 3. 执行生成

跑之前最后过一遍：意图（建哪条线、什么业务、新建还是改已有）和参数都确认过了；有一条没确认就停下来问，不要「先跑一遍看看」。

按场景选命令，一次只跑需要的：

| 命令 | 作用 |
|---|---|
| `efg` | 全量：骨架 + Entity/Mapper + 业务代码 + 自动装配 |
| `efg -p` | 只骨架（不需要数据库） |
| `efg -m` | 只 Entity + Mapper |
| `efg -s` | 只业务代码（Repository / Service / API / Remote / Controller） |
| `efg -a` | 只自动装配配置 |
| `efg -d` | 只刷新 DTO 和 Param（表结构变更后） |
| `efg -pms` / `-pm` / `-sa` | 组合执行 |
| `efg -c other.yml` | 指定配置文件 |
| `efg -fv 3.2.12` | 覆盖目标框架版本（优先于配置文件） |

- Windows 控制台是 GBK，日志里会看到乱码。先 `export JAVA_OPTS="-Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8"` 再跑（`efg.bat` / `efg` 会把 `JAVA_OPTS` 透传给 java），输出才读得懂。
- 判定成功看三样：**退出码 0**、输出里有 `[完成] 代码生成成功！`、`<project-dir>/<project-name>` 下有产物。只看到「生成项目成功」不代表业务代码成功——那只是骨架。
- 同一个配置重跑是安全的：Entity / DTO 会更新，Mapper / Repository / Service / Controller 已存在就不覆盖。

## 4. 核对产物（不要把「跑过了」当成「生成对了」）

### 4.1 成功判据

```bash
# 退出码
efg; echo "exit=$?"        # 期望 exit=0

# 产物（全量）
ls "<project-dir>/<project-name>"                 # pom.xml（或 build.gradle）+ config/ + src/
ls "<project-dir>/<project-name>/config"          # application*.yml、logback.xml

# 业务代码（single 项目，一个表一套）
find "<project-dir>/<project-name>/src/main/java" -name "*.java" | sort
```

只跑 `-p` 时产物只有 `pom.xml`（或 `build.gradle`）和空的 `src/main`、`src/test`，**没有** `config/` 和 java 文件——这是正常的，别当成失败。

`single` + 一张表（`orm-type: MYBATIS`、`prd-type: single`）实测 13 个类，目录结构：

```
<project-name>/                               全量生成后
├── pom.xml / build.gradle
├── config/                                   application*.yml、logback.xml
└── src/main/java/<base-package>/
    ├── XxxServerApp.java                     启动类
    ├── api/                                  I<Model>Service、dto/、param/、request/、response/
    ├── controller/                           <Model>Controller
    └── service/                              impl/、persistence/mapper/、persistence/model/、repository/
```

微服务 / 智能型项目多出 `-api`、`-server`、`-prd`（`separation` 时还有 `-client`、`-bms`）、`-orm*` 等模块目录，按 `project-type` 核对模块是否齐全。

类数按选型增减：`prd-type: none` 没有 Controller，`orm-type: NONE` 没有 Entity 和 Mapper / Repository。少的是不是你选的组合，先对一遍再下结论。

### 4.2 失败对照

| 输出 / 现象 | 原因 | 处理 |
|---|---|---|
| `modelInfo.fieldList` 为空、`生成DtoAndParam失败` | 没拿到表结构：`db-tables` 为空、表名不存在，或只写了 `model-list` | 确认库连得上、表名拼对；补 `db-tables` 重跑 |
| `缺少数据库驱动 xxx` | `lib/` 里没有对应驱动 | 把驱动 jar 放进 `<安装目录>/lib/`，不要改脚本 |
| 连库报 `Access denied` / `Connection refused` | 账号、密码或地址不对；库没起 | 让用户核对连接信息，不猜密码 |
| `OrmType 为 NONE，跳过 Model 生成` | `orm-type: NONE` | 要 Entity/Repository 就设 `MYBATIS`（或 `MYBATIS_FLEX` / `HIBERNATE`） |
| 只有 `pom.xml`、没有 java 业务代码 | 只跑了 `-p` | 按场景补 `efg -m` + `efg -s` |
| `文件已存在` 类警告 | `efg init` 目标文件已在 | 不用处理；要换名用 `-o` |
| `找不到 java` | JDK 没装或 PATH 不对 | 回 §0.1 |

失败时**不要**手工补生成的类凑数。改配置重跑，或把具体报错和缺失项报给用户。

## 5. 交接（后端项目）

生成完成后，用几句话交代清楚：生成了哪个项目、放在哪、哪些模块、下一步该做什么。

- **写业务代码**：转 easyfk-dev-skill，按它的分层和自检规范改生成的类。
- **加表**：改 `db-tables` 后 `efg -m`，再 `efg -s`。
- **表改字段**：`efg -d` 刷 DTO / Param；Entity 用 `efg -m` 重跑（会更新）。
- **框架类名、配置前缀、依赖坐标拿不准**：查 easyfk-framework-skill，不凭记忆写。
- **已有项目要搞清楚现状**：转 easyfk-reverse-skill 反推。

## 6. 建 EasyBuild Admin 中后台前端项目（easybuild-admin）

本节是**前端专用**，和 §0–§5 的后端流程没有交集：不查 JDK、不装 `efg`、不写 `generator.yml`、不碰 `db-tables`、不读 `pom.xml`。

生成的是 Next.js 16 + React 19 + TypeScript 6 + Tailwind CSS 4 + Shadcn/ui 的中后台模板：菜单与权限由后端接口下发，内置零后端本地 Mock，装完依赖就能 `yarn dev` 跑通 CRUD。

### 6.1 环境检查（Node，不是 JDK）

```bash
node -v              # ≥ 18.17（CLI 的 engines）；开发建议 ≥ 20.9
corepack --version
yarn --version       # 可能是 1.22.x，先别管，见 6.5
```

- Node 低于 18.17：停下来让用户升级，不要自己装 Node；18.17–20.8 能生成，但模板开发要求 ≥ 20.9，建议一并升级。
- `corepack` 不在（Node 25+ 已不再内置）：`npm i -g corepack`，再继续。
- 需要能访问 `github.com`（下载模板）和 `registry.npmjs.org`（npx 拉 CLI）。公司网络要走代理时提示用户配 `HTTPS_PROXY` / npm 代理，不要静默改配置。
- CLI 不用预装，`npx --yes` 会临时拉取。先确认可用：

```bash
npx --yes easybuild-admin@1.2.0 --version    # 期望输出 1.2.0
```

> 手册头部写「适用范围 CLI 1.1.0」，那是发布时没同步的版本号；`--json` 从 **1.2.0** 才有，所以一律锁 `@1.2.0`（2026-11-25 实测 npm 最新即 1.2.0）。不锁版本时 npx 可能拿到别的版本，JSON 契约会变。

### 6.2 问清参数（一次问完，最多两轮）

先过「生成前：先确认意图」——前端最容易出的错，是把「建个管理后台」直接当成 EasyBuild Admin 前端。确认确实是前端、业务清楚、新建还是改已有，再问下面的参数。

| 必问 | 参数 | 规则 / 默认 |
|---|---|---|
| 项目名 | `[project-name]` | **必须英文小写**，同时是目录名和 `package.json.name`。只允许小写字母、数字、`-` `_` `.` `~`，不能以 `_` / `.` 开头，长度 ≤ 214；中文名不行，让用户给英文或拼音名。目录名就是这个值，改不了的 |
| 项目描述 | `-d` | 中文可以，写进 `package.json.description`。用户没想好就给一句「XX 管理后台」让他确认 |
| 生成到哪 | 执行目录 | CLI 在**当前目录**下建 `<项目名>/`，所以先 `cd <父目录>`。问清父目录（默认当前工作区） |
| 包管理器 | `--pm` | 只接受 `yarn` / `pnpm` / `npm`，默认 `yarn`。**模板锁 `yarn@4.7.0`**，选 npm/pnpm 会留下 yarn.lock 又不删；建议保持 yarn，用户坚持再照办并提醒 |
| 模板版本 | `--repo ...#ref` | 默认解析最新正式 Release（当前 `v1.0.0`）。要可复现就显式锁 `#v1.0.0`；要跟开发分支就把 ref 换成实际分支名。不指定也能用，但产物会随 Release 漂移 |
| 是否初始化 Git | `--skip-git` | Agent 环境建议跳过（缺 `user.name` / `user.email` 会让首次提交失败）；要仓库时去掉该参数，或建好后自己 `git init` |
| 是否立即装依赖 | `--skip-install` | Agent 建议跳过，自己装便于控制超时与日志（CLI 默认 5 分钟超时）。交给 CLI 装时去掉该参数 |

推断规则同 §1：能从上下文推的先推、复述给用户确认，只问缺的。**项目名和输出目录必须由用户确认**，不要自己编一个。一次问 3~5 项，别一轮一轮挤：项目名（英文小写，同时决定目录名）、项目描述、放到哪个父目录、包管理器（默认 yarn）、模板版本（默认最新 Release）、要不要 Git / 现在装依赖。

### 6.3 执行（Agent 标准写法）

Agent 的 shell 不是 TTY，必须把参数给全，并加 `--json -y`：`--json` 隐含非交互，`-y` 兜住默认值。少给参数会直接以 `NON_INTERACTIVE` 退出 1。

跑之前最后过一遍：意图（建哪条线、什么业务、新建还是改已有）和参数都确认过了；有一条没确认就停下来问，不要「先跑一遍看看」。

创建动作要**真的执行**这条命令，不能只把命令贴给用户让他自己跑（用户明确说自己跑除外）。

```bash
cd <父目录>
npx --yes easybuild-admin@1.2.0 <项目名> \
  -d "<项目描述>" \
  --pm yarn \
  --repo easybuild-jack/easybuild-admin-front#v1.0.0 \
  --skip-git --skip-install \
  --json -y
```

- 上面的 `\` 是 bash 写法；Windows PowerShell 就写成一整行，不要用 `\` 续行。
- 两个 yes 别搞混：`npx --yes` 跳过 npx 自己的安装确认，`-y` 跳过脚手架的交互，都要带上。
- PowerShell 里 `#` 必须紧贴仓库名（`...front#v1.0.0`），中间加空格会被当成注释，后面的参数全丢。
- `-d` 的描述含空格或中文标点时用双引号包住。
- stdout **只有一行 JSON**（成功失败都输出），进度条与提示在 `--json` 下全部静默。
- 退出码 `0` 成功、`1` 失败；但真正的处理依据是 JSON 里的 `error.code`。
- 成功输出实测（v1.0.0 模板 + CLI 1.2.0）：

```json
{"ok":true,"cliVersion":"1.2.0","project":{"name":"my-app","path":"D:\\work\\my-app","description":"我的管理后台"},"template":{"repo":"easybuild-jack/easybuild-admin-front","ref":"v1.0.0","source":"custom-ref"},"git":{"skipped":true,"initialized":false,"committed":false},"dependencies":{"skipped":true,"installed":false,"packageManager":"yarn"},"durationMs":1193}
```

PowerShell 解析（stderr 丢掉，只取最后一行，避免 npm 提示混进 JSON）：

```powershell
$line = npx --yes easybuild-admin@1.2.0 my-app -d "我的管理后台" --pm yarn --repo easybuild-jack/easybuild-admin-front#v1.0.0 --skip-git --skip-install --json -y 2>$null | Select-Object -Last 1
$r = $line | ConvertFrom-Json
if ($r.ok) { $r.project.path } else { "$($r.error.code): $($r.error.message)" }
```

- 不要用 `-y` 不带 `--json`：输出是给人看的横幅，解析不了。
- 不要指望交互提问：非 TTY 下 CLI 会直接报错退出，不会卡住（这是设计，不是故障）。
- Windows PowerShell 5.1 的坑：`Get-Content` 默认按 ANSI 读文件，直接读 `package.json` 里的中文会乱码、甚至 `ConvertFrom-Json` 报「字符串未终止」——加 `-Encoding utf8`，或用 `[System.IO.File]::ReadAllText($path, [Text.Encoding]::UTF8)`。原生命令的 stdout 若中文乱码，先把 `[Console]::OutputEncoding` 设为 UTF-8 再调用。
- 判定成败只看 `ok` / `error.code` / 路径是否存在，不要拿控制台里中文是否好看当依据。

### 6.4 核对产物（「跑过了」≠「生成对了」）

1. 退出码 `0` 且 `ok: true`；
2. `project.path` 是预期目录，且真实存在；
3. `package.json` 的 `name` = 项目名、`description` = 描述、`version` = `0.1.0`（CLI 会把版本重置）；
4. 模板结构在位（v1.0.0 实测）：

```text
<项目名>/
├── package.json                name / description / version 已替换
├── next.config.mjs、tsconfig.json、tailwind.config.ts、components.json
├── .env.development / .env.test / .env.production
├── src/
│   ├── app/                    layout.tsx、page.tsx、login/、api/[...slug]/、示例业务页
│   ├── api/                    http.ts + 按模块拆的接口
│   ├── components/             ui/、custom/、layout/
│   ├── config/                 api-url.ts、routes.ts、site.ts、login/login-config.ts…
│   ├── mock/                   本地 Mock 引擎与数据
│   └── store/、hooks/、lib/、types/、styles/
├── docs/开发文档.md、docs/项目说明文档.md
└── README*.md、CHANGELOG.md、yarn.lock
```

5. `package.json` 的 `packageManager` 仍是 `yarn@4.7.0`（`--pm` 只影响 CLI 的安装命令与提示，不改这里）；`dependencies.next` 是 16.x、`react` 是 19.x。

`dependencies.installed: false` **不是**失败：`ok` 仍为 true，项目已经建好，自己按 6.5 装。

### 6.5 装依赖、启动

项目锁 Yarn 4，而本机全局 `yarn` 往往是 1.22（经典版，实测这台机器就是 1.22.22）。**不要直接 `yarn install`**，那会让 Yarn 1 去装 Yarn 4 的工程。用 corepack 指定版本，并且不碰全局：

```bash
cd <项目路径>
corepack yarn --version    # 期望 4.7.0（corepack 读 packageManager 字段）
corepack yarn install
corepack yarn dev          # http://localhost:4000，Mock 账号 admin / 12345
```

- 想让终端里直接敲 `yarn` 就是 4.7.0，由用户自己执行 `corepack enable`：它会覆盖全局 yarn shim，属于改用户环境，先说明再动；没权限（`EPERM`）就继续用 `corepack yarn ...`。
- 首次 corepack 会下载 Yarn 4.7.0，慢是正常的，别打断。
- 依赖装失败不影响项目产物：重跑 `corepack yarn install` 或换源，不要删了重建项目。
- 默认走本地 Mock（`.env.development` 的 `NEXT_PUBLIC_API_URL=/api`）；连真实后端用 `corepack yarn dev:test`（`.env.test` 默认 `http://localhost:5001/api`，对应 `easybuild-admin-api`）。
- `dev` 是常驻进程：在对话里跑要放后台，别让命令把会话卡住；起没起来看 `http://localhost:4000` 是否可访问。
- 用户坚持 npm/pnpm：项目里 `packageManager` 与 `yarn.lock` 都是 yarn 的，混装会多出第二份锁文件；建议仍用 yarn，或先和用户确认再改。

### 6.6 失败对照

| `error.code` / 现象 | 原因 | 处理 |
|---|---|---|
| `NON_INTERACTIVE` | 参数没给全还想交互（`--json` 或非 TTY） | 补齐 `project-name`、`-d`、`--pm`，加 `-y` |
| `INVALID_PROJECT_NAME` | 名字不合 npm 包名规则（中文、大写、空格、`../`） | 换英文小写名，不要用路径 |
| `DIR_EXISTS` | 目标目录已存在；`-y` / 非交互下不覆盖 | **不要删用户目录**：换项目名，或问清后由用户自己清理 |
| `DOWNLOAD_FAILED` | GitHub 不通、代理没配、`#ref` 不存在、仓库私有 | 重试 1~2 次；确认 `#v1.0.0` 拼写；查代理；仍失败 → 6.7 |
| `TEMPLATE_INVALID` | 下载到的不是本模板（缺 `package.json`） | 换回默认 `--repo easybuild-jack/easybuild-admin-front` |
| `INVALID_ARGS` | `--pm` 只能是 yarn / pnpm / npm | 改正重跑 |
| `UNEXPECTED` | 其他异常（磁盘、权限、进程占用） | 看 `error.message`；Windows「目录删不掉」多半是编辑器或进程占用 |
| `npx` 拉不到 CLI | npm registry 不通 / 本地缓存旧版本 | `npx --yes easybuild-admin@1.2.0 --version` 显式锁版本；仍不行查 registry 与代理，必要时 `npm i -g easybuild-admin@1.2.0` |

失败先按表处理。**不要**为了让命令「成功」去手写模板文件，也不要把 `dependencies.installed: false` 当成创建失败。

### 6.7 兜底：CLI 实在起不来，才从 GitHub 拉模板

本 skill 的规则是「必须用 CLI 创建」，所以这条路是**最后手段**。只有同时满足下面条件才走，并且**必须在回复里说明**：哪一步失败、`error.code` 是什么、已降级为 git clone。

- 已排除参数、目录、权限问题（错误码 `DOWNLOAD_FAILED` / `TEMPLATE_INVALID`，或 npx 根本装不上 CLI）；
- 已重试 ≥ 2 次，并试过显式版本、换 registry / 代理；
- 告知用户（一句话即可，不必等回复）。

```bash
git clone --depth 1 --branch v1.0.0 https://github.com/easybuild-jack/easybuild-admin-front.git <项目名>
cd <项目名>
rm -rf .git          # 模板历史与 origin 不属于新项目；要仓库再 git init
# 手工改 package.json：name=<项目名>、description=<描述>、version=0.1.0
```

- 删 `.git` 在 Windows PowerShell 里用 `Remove-Item -Recurse -Force .git`（`rm -rf` 是 bash 写法）。
- 拉到的内容与 CLI 产物同源（同一 tag），差别只在 CLI 会做的元信息替换（`name` / `description` / `version` 重置），必须自己补；
- 拉完仍按 6.4 核对、6.5 安装启动；
- 不要因为「clone 更快」就跳过 CLI——CLI 能跑通时必须用 CLI。

### 6.8 生成后必改与交接

生成的项目带示例业务（品牌、`base` / `commodity` / `order` 等示例页、示例接口），正式开发前按模板文档清理。重点（v1.0.0 实测，与手册第 7.3 节略有出入）：

1. `package.json` 的 `name` / `version`（CLI 已改好，二次确认）；
2. 三个 `.env*` 的接口地址：`NEXT_PUBLIC_API_URL`、`NEXT_PUBLIC_UPLOAD_API_URL`，以及 `NEXT_PUBLIC_ENV`（设为 `production` 时本地 Mock 自动返回 404）；
3. `src/config/api-url.ts` 的 `API_URLS`：示例业务路径都在这里，按真实后端改；
4. 删示例页面：`src/app/` 下除 `auth/`、`login/`、`api/` 和根 `layout.tsx` / `page.tsx` 之外的业务目录（`base`、`commodity`、`order`、`businesses`、`customer`、`operation`、`storage`、`system`），以及 `src/api/`、`src/types/`、`src/mock/modules/` 中对应文件；
5. `src/config/routes.ts` 的 `iconMap` / `colorMap`：按后端下发的 `resourceId` 配图标与颜色，没配的落到默认值；
6. 品牌信息：`src/config/site.ts`（站点名、标题、描述、URL）与 `src/config/login/login-config.ts`（登录页 brand / tagline）。`layout.tsx` 读的是 `site.ts`；**别再找 `public/favicon.ico`**，v1.0.0 没有 `public/`，图标由 `src/app/icon.tsx` / `apple-icon.tsx` / `opengraph-image.tsx` 生成。

删完跑一次 `npx next typegen && npx tsc --noEmit`，把 `src/mock` 菜单与 `API_URLS` 里残留的示例引用一起清掉，否则类型检查会报找不到模块。

交接时说清：项目名、路径、模板版本、依赖是否已装、启动方式。后续写前端业务代码按项目内 `docs/开发文档.md` 的「新增业务模块 6 步 SOP」走（类型 → API → 页面三件套 → 菜单图标 → Mock/后端菜单 → `npx next typegen && npx tsc --noEmit`）。本 skill 不代写页面；`easyfk-dev-skill` 只管 EasyFK 后端 Java 代码，不要拿它的分层规则套 Next.js。

## 套件安装检查

本 skill 属于 easyfk-skill 套件，四个 skill 放在同一个仓库 `https://github.com/easybuild-jack/easyfk-skill.git`，安装后是 skills 目录第一层的四个平级目录。

1. **查找**：按顺序找含 `SKILL.md` 且 `name` 对得上的目录，找到就停：本 skill 所在目录的同级 → 项目下的 `.cursor/skills/`、`.claude/skills/` → 用户目录下的 `~/.cursor/skills/`、`~/.claude/skills/`。
2. **安装**：找不到时，把仓库克隆到临时目录，用安装脚本装到本 skill 所在的 skills 目录（找不到本 skill 的目录时装到 `~/.cursor/skills/`），安装前在回复里说一句装到哪里：

   ```
   git clone --depth 1 https://github.com/easybuild-jack/easyfk-skill.git <临时目录>/easyfk-skill
   powershell -ExecutionPolicy Bypass -File <临时目录>/easyfk-skill/install.ps1 -Target <skills 目录>   # Windows
   sh <临时目录>/easyfk-skill/install.sh <skills 目录>                                              # macOS / Linux
   ```

3. **注意区分两个安装**：这是装 AI skill；`efg` 命令本身按 §0.2 单独装，两者互不替代。
