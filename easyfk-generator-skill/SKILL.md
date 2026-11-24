---
name: easyfk-generator-skill
description: >-
  用 EasyFK Generator（CLI 命令 efg）创建 EasyFK 项目：先检查本机 JDK 21、检查 efg 是否已安装，没装就从发布包地址下载、解压、安装并用 efg -V 验证；然后问清用户要生成什么类型的项目（项目类型、坐标、构建工具、ORM、PRD/应用类型、RPC、数据库与表），写成 generator.yml，调 efg 生成，最后核对产物。
  红线：项目代码一律由 CLI 生成。AI 不手写 pom.xml / build.gradle、不建 src 目录、不自己拼 Entity/Service/Controller 之类的文件；CLI 报错就改配置参数重跑或如实报告用户，不允许绕过 CLI 造文件冒充「已生成」。
  在新建 easyfk 项目、生成项目骨架、脚手架、初始化工程、已有项目按库里表生成 Entity/Mapper/业务代码、表结构变更后刷新 DTO 和 Param、安装或升级 efg、efg 命令报错排查时使用。不负责写业务代码（那是 easyfk-dev-skill）、不负责讲框架有哪些模块（easyfk-framework-skill）、不负责反推已有系统（easyfk-reverse-skill）。
---

# EasyFK 项目生成

本 skill 只管一件事：**把 `efg` 这个 CLI 装好，把参数问清楚，让它把项目生成出来，再核对产物。**

完整参数表、各架构的配置示例、支持的数据库类型这些原始细节，看随包发布的 [reference/cli使用手册.md](reference/cli使用手册.md)（原版手册，未改动）。本文只留「做决定和动手时必须知道的」，两者冲突时以本文实测过的步骤为准。CLI 换版本时，把新发布包根目录同名的 `cli使用手册.md` 拷过来覆盖即可。

本 skill 属于 easyfk-skill 套件，四个 skill 平级、互相按名称引用：

| skill | 管什么 |
|---|---|
| easyfk-framework-skill | 框架有什么：模块、能力、类名、配置前缀、版本快照 |
| easyfk-dev-skill | 代码怎么写：分层、命名、文档、自检、复核 |
| easyfk-reverse-skill | 已有系统是什么样：从代码反推业务与架构报告 |
| easyfk-generator-skill（本 skill） | 项目怎么建出来：装 efg → 问参数 → 写 generator.yml → 调 CLI → 核对产物 |

## 红线（不可越过）

1. **项目文件只能由 `efg` 生成。** 不手写 `pom.xml` / `build.gradle`、不 `mkdir src/main/java`、不自己写 `XxxController.java` 冒充生成结果，也不在 `efg` 之外用脚本「补齐」缺失的类。
2. **AI 只写 `generator.yml` 和处理命令。** 配置是 CLI 的输入，脚本、jar、源码目录都不是。
3. **生成失败就承认失败。** 失败时按 §4 的对照表定位，能改配置再重跑；改不了就如实说明「卡在哪一步、缺什么」，不给用户一个看起来像成功的结果。
4. **没有可用的表结构，就只能出骨架。** 实测：没有数据库或拿不到 `db-tables` 的字段时，CLI 在生成 Dto/Param 阶段会报 `modelInfo.fieldList` 为空并退出码 1，业务代码一行都出不来。这时只能 `efg -p` 生成骨架，并明确告知用户业务代码需要数据库或表结构。
5. **不要在用户没确认参数前就跑全量生成。** 参数错一次会留下半套目录，清理比重生成麻烦。

## 0. 先做三件事：查环境、查安装、定场景

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

C、D 是在已有项目上补代码，`project-dir` / `project-name` / `base-package` 必须与现有项目一致，先读现有 `pom.xml` 或 `build.gradle` 取准，不要新建目录。

## 1. 问清要生成什么（参数）

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

## 5. 交接

生成完成后，用几句话交代清楚：生成了哪个项目、放在哪、哪些模块、下一步该做什么。

- **写业务代码**：转 easyfk-dev-skill，按它的分层和自检规范改生成的类。
- **加表**：改 `db-tables` 后 `efg -m`，再 `efg -s`。
- **表改字段**：`efg -d` 刷 DTO / Param；Entity 用 `efg -m` 重跑（会更新）。
- **框架类名、配置前缀、依赖坐标拿不准**：查 easyfk-framework-skill，不凭记忆写。
- **已有项目要搞清楚现状**：转 easyfk-reverse-skill 反推。

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
