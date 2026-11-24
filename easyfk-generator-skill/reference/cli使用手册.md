# EasyFK Generator CLI 使用手册

> 一次配置，一条命令，全自动生成。

---

## 环境要求

- **JDK 21** 或更高版本（[下载地址](https://adoptium.net/zh-CN/)）

---

## 安装

解压 `efg-3.5.16.zip`，进入 `efg-3.5.16` 目录：

**Windows：** 双击 `install.bat`

**macOS / Linux：**

```bash
chmod +x install && ./install
```

> 也可以直接指定发布包下载地址，脚本会下载、解压并校验后安装：
> `DOWNLOAD_URL=https://你的仓库/efg-3.5.16.zip sh install.sh`

安装完成后**重新打开终端**，输入 `efg -V` 验证：

```
easyfk-generator 3.5.16
```

> **安装位置**：Windows — `%USERPROFILE%\.easyfk-gen`；macOS / Linux — `~/.easyfk-gen`。
> 安装脚本会自动将该目录加入用户 PATH，并在目录中放置 `efg` 启动脚本、`easyfk-generator-3.5.16-cli.jar` 与 `lib/` 依赖目录。

### 发布包内容

| 文件 | 说明 |
|------|------|
| `easyfk-generator-3.5.16-cli.jar` | 生成器主程序（模板已加密内置，不含明文模板） |
| `lib/mysql-connector-j-*.jar` | MySQL 驱动，按需加载；可自行替换版本 |
| `generator.yml.example` | 配置样例，等同于 `efg init` 生成的内容 |
| `CHECKSUMS.txt` | 全部文件的 SHA-256，安装脚本会逐个校验，不一致则中止安装 |
| `install*` / `uninstall*` | 安装与卸载脚本 |
| `cli使用手册.md` | 本手册 |

### 数据库驱动

MySQL 驱动因授权（GPLv2）原因不并入主程序，而是以独立 jar 放在 `lib/` 目录，安装后的启动脚本已把 `lib/*` 挂到 classpath：

```
java -cp "<安装目录>/easyfk-generator-3.5.16-cli.jar:<安装目录>/lib/*" com.mcst.easyfk.generator.cli.GeneratorCli
```

- 需要其它数据库驱动时，把对应 jar 丢进 `lib/` 即可，无需修改脚本
- 若驱动缺失，执行需要连库的操作会明确提示「缺少数据库驱动 xxx：请把对应驱动 jar 放入安装目录的 lib/ 目录」
- PostgreSQL 驱动已内置，开箱可用

---

## 卸载

**Windows：** 双击 `uninstall.bat`

**macOS / Linux：**

```bash
chmod +x uninstall && ./uninstall
```

---

## 快速上手

### 第一步：生成配置模板

```bash
efg init
```

当前目录会生成 `generator.yml`，用编辑器打开填入项目信息和数据库配置。

### 第二步：执行生成

```bash
efg
```

搞定！在 `project-dir` 指定的目录下已生成完整项目。

---

## 命令参考

### 基本语法

```
efg [选项]
efg init [-o 文件名]
```

### 生成命令

| 命令 | 说明 |
|------|------|
| `efg` | 全量生成（项目骨架 + Entity + 业务代码 + 自动装配） |
| `efg -p` | 仅生成项目骨架 |
| `efg -m` | 仅生成 Entity + Mapper |
| `efg -s` | 仅生成业务代码（Repository / Service / API / Remote / Controller） |
| `efg -a` | 仅生成自动装配配置 |
| `efg -d` | 仅刷新 DTO 和 Param（表结构变更后使用） |

### 组合使用

Flag 可以组合，按需选择：

| 命令 | 说明 |
|------|------|
| `efg -pm` | 项目骨架 + Entity + Mapper |
| `efg -sa` | 业务代码 + 自动装配配置 |
| `efg -pms` | 项目骨架 + Entity + 业务代码 |

### 其他选项

| 选项 | 说明 |
|------|------|
| `-c <文件>` | 指定配置文件路径（默认读取当前目录 `generator.yml`） |
| `-fv <版本>` | 覆盖配置文件中的框架版本，可选 `3.2.12` / `3.5.16`（优先级高于 `generator.yml`） |
| `-h, --help` | 查看帮助 |
| `-V, --version` | 查看版本 |

### init 子命令

| 命令 | 说明 |
|------|------|
| `efg init` | 在当前目录生成 `generator.yml` 配置模板 |
| `efg init -o my-config.yml` | 指定输出文件名 |

> 如果目标文件已存在，`efg init` 会提示警告并退出，不会覆盖已有文件。

`efg init` 生成的模板内容如下：

```yaml
# ============================================================
#  EasyFK Generator 配置文件
#  使用方式：efg (在 generator.yml 所在目录执行)
# ============================================================

easyfk:
  config:
    generator:
      # ==================== 项目配置 ====================
      project:
        # [必填] 项目输出目录
        project-dir: D:\workspace\projects
        # [必填] Maven groupId
        group-id: com.example
        # [必填] 项目名称
        project-name: my-app
        # [必填] 项目包根路径
        base-package: com.example.myapp

        # 项目类型: single(单体项目) / micro_prd(产品层项目) / microservice(微服务项目) / smart(智能型项目) / smart_orm(智能型项目+ORM抽离)
        project-type: single
        # 构建工具: maven / gradle
        build-type: maven
        # ORM 框架: NONE / MYBATIS / MYBATIS_FLEX / HIBERNATE
        orm-type: NONE
        # PRD 层策略: none(不生成) / single(单一) / separation(分离: client + bms)
        prd-type: single
        # 日志框架: LOGBACK / LOG4J2
        log-type: LOGBACK
        # 框架版本
        framework-version: 3.5.16
        # 项目版本
        project-version: 1.0.0-SNAPSHOT
        # [项目类型为 single / micro_prd，或 prd-type 为 single 时必填] 应用类型: BMS(后台管理端) / CLIENT(面向C端)
        app-type:
        # 是否引入 auth 权限模块 (true/false)
        include-auth: false

      # ==================== 代码配置 ====================
      code:
        # [必填] 模块名称
        module-name: myapp
        # 作者信息
        author: eb-jack
        # 数据库类型: MYSQL / POSTGRE_SQL / ORACLE / ORACLE_12C / MARIADB / SQL_SERVER / ...
        db-type: MYSQL
        # [必填] 数据库短连接 (host:port/database)
        db-short-url: localhost:3306/my_database
        # 数据库用户名
        db-user: root
        # 数据库密码
        db-pwd: your_password
        # ---------- 表配置 ----------
        # 忽略表前缀 (支持多个，多个使用英文逗号分隔)
        # table-prefix: base_,auth_
        # 从数据库读取的表名 (逗号分隔，会自动解析表结构)
        db-tables: product,order

        # ---------- 手动定义 Model (可选) ----------
        # 除 db-tables 自动解析外，也可手动定义
        # model-list:
        #   - model-name: Product
        #     model-desc: 商品信息
        #     # id-type: String
        #     # only-repository: false
        #     # create-controller: true
        #   - model-name: Order
        #     model-desc: 订单信息
```

---

## 配置文件说明

执行 `efg init` 生成的 `generator.yml` 分为两大部分：**项目配置（project）** 和 **代码配置（code）**。

### 项目配置（project）

```yaml
easyfk.config.generator.project:
```

| 配置项 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `project-dir` | **是** | - | 项目输出目录，生成的项目会放在该目录下。例：`D:\workspace\projects` 或 `/home/user/projects` |
| `group-id` | **是** | - | Maven groupId，例：`com.example` |
| `project-name` | **是** | - | 项目名称，会作为项目根目录名和各子模块名的前缀。例：`my-app` |
| `base-package` | **是** | - | Java 包根路径，所有生成的代码都在此包下。例：`com.example.myapp` |
| `artifact-id` | 否 | 同 `project-name` | Maven artifactId，不填则默认取 `project-name` 的值 |
| `project-type` | 否 | `smart` | 项目架构类型，决定生成的项目结构 |
| | | | `single` — 单体项目，所有代码在一个工程中 |
| | | | `micro_prd` — 产品层项目，仅生成启动类+配置，通过 RPC 调用后端微服务，无 ORM/业务代码 |
| | | | `microservice` — 微服务项目，生成 API + Server + PRD 模块，支持一种 RPC |
| | | | `smart` — 智能型项目，同时生成 Spring Cloud 和 Dubbo 两套 RPC 通道 |
| | | | `smart_orm` — 智能型项目，ORM 层抽离为独立 `-orm` 模块，同时生成 MyBatis-Plus / MyBatis-Flex / Hibernate 多套实现 |
| `rpc-type` | 否 | `NONE` | RPC 类型，`microservice` 或 `micro_prd` 架构时生效（`micro_prd` 时必选） |
| | | | `NONE` — 不使用 RPC |
| | | | `cloud` — Spring Cloud Feign |
| | | | `dubbo` — Apache Dubbo |
| `build-type` | 否 | `maven` | 构建工具类型 |
| | | | `maven` — 生成 pom.xml |
| | | | `gradle` — 生成 build.gradle / settings.gradle |
| `gradle-type` | 否 | `groovy` | Gradle DSL 类型，仅 `build-type: gradle` 时生效 |
| | | | `groovy` — Groovy DSL (build.gradle) |
| | | | `kotlin` — Kotlin DSL (build.gradle.kts) |
| `orm-type` | 否 | `NONE` | ORM 框架类型 |
| | | | `NONE` — 不使用 ORM 框架 |
| | | | `MYBATIS` — MyBatis-Plus |
| | | | `MYBATIS_FLEX` — MyBatis-Flex |
| | | | `HIBERNATE` — Hibernate (JPA) |
| `orm-modules` | 否 | 全部 | 仅 `project-type: smart_orm` 时生效。ORM 实现模块列表（`MYBATIS` / `MYBATIS_FLEX` / `HIBERNATE`），不填默认生成全部 |
| `prd-type` | 否 | `none` | 前端对接层（Controller）策略 |
| | | | `none` — 不生成 Controller 层 |
| | | | `single` — 生成单一 PRD 项目，所有 Controller 集中 |
| | | | `separation` — 分离式：prd-client（C端）+ prd-bms（B端管理后台） |
| `log-type` | 否 | `LOGBACK` | 日志框架：`LOGBACK` 或 `LOG4J2` |
| `framework-version` | 否 | `3.5.16` | 目标框架版本，可选 `3.2.12` / `3.5.16`。决定 BOM 坐标、Lombok / mapstruct-plus / mybatis-flex 版本与 MyBatis-Plus 实体父类包名 |
| `project-version` | 否 | `1.0.0-SNAPSHOT` | 生成项目的版本号 |
| `controller-auto-config` | 否 | `false` | 是否为 Controller 层生成 Spring Boot AutoConfiguration |
| `app-type` | 条件必填 | - | 应用类型，决定模块 PRD 依赖的变体。`BMS` — 后台管理端；`CLIENT` — 面向 C 端。**当 `project-type` 为 `single` / `micro_prd`，或 `prd-type` 为 `single` 时必填** |
| `include-auth` | 否 | `false` | 是否引入 auth 权限模块。设为 `true` 时会自动在生成的项目中引入 auth 模块相关依赖 |

### 代码配置（code）

```yaml
easyfk.config.generator.code:
```

#### 基本配置

| 配置项 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `module-name` | **是** | - | 模块名称，用于生成配置类名、远程调用 serviceId 等。例：`myapp` |
| `author` | 否 | `eb-jack` | 代码注释中的作者信息 |
| `spring-annotation` | 否 | `true` | 是否在生成的类上添加 Spring 注解（如 `@Repository`、`@Service`） |
| `extends-supper-class` | 否 | `true` | Entity 是否继承框架基类（基类提供 deleted、insertTime、lastUpdateTime 字段） |

#### 数据库连接

| 配置项 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `db-type` | 否 | `MYSQL` | 数据库类型。可选值见下方「支持的数据库类型」 |
| `db-short-url` | **是**★ | - | 数据库短连接地址，格式：`host:port/database`。例：`localhost:3306/my_db`。★ 仅在使用 `db-tables` 时必填 |
| `db-user` | 否 | `root` | 数据库用户名 |
| `db-pwd` | **是**★ | - | 数据库密码。★ 仅在使用 `db-tables` 时必填 |

**支持的数据库类型（db-type）：**

| 值 | 数据库 | 值 | 数据库 |
|---|---|---|---|
| `MYSQL` | MySQL | `MARIADB` | MariaDB |
| `POSTGRE_SQL` | PostgreSQL | `ORACLE` | Oracle |
| `ORACLE_12C` | Oracle 12c+ | `SQL_SERVER` | SQL Server |
| `SQL_SERVER2005` | SQL Server 2005 | `DM` | 达梦 |
| `KINGBASE_ES` | 人大金仓 | `GAUSS` | GaussDB |
| `OCEAN_BASE` | OceanBase | `CLICK_HOUSE` | ClickHouse |
| `DB2` | IBM DB2 | `H2` | H2 |
| `HSQL` | HSQLDB | `SQLITE` | SQLite |
| `PHOENIX` | Apache Phoenix | `GBASE` | 南大通用 GBase |
| `OSCAR` | 神通 OSCAR | `SYBASE` | Sybase |
| `XU_GU` | 虚谷 | `FIREBIRD` | Firebird |
| `OTHER` | 其他 | | |

#### 表配置

| 配置项 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `table-prefix` | 否 | - | 忽略表前缀，支持多个前缀使用英文逗号分隔。例：配置 `base_,auth_`，表 `base_product` → 类 `Product`，表 `auth_role` → 类 `Role` |
| `db-tables` | 否 | - | 需要从数据库读取结构的表名，逗号分隔。例：`product,order,user_info`。配置后会自动连接数据库解析字段 |

#### 手动定义 Model（可选）

除了 `db-tables` 自动解析，也可以手动定义模型：

```yaml
model-list:
  - model-name: Product         # [必填] 模型名称（大驼峰），对应生成的类名
    model-desc: 商品信息         # 模型描述，用于代码注释
    table-name: base_product    # 数据库表名（不填则自动根据 model-name + 主前缀 推导）
    id-type: String             # 主键类型：String（默认）或 Long
    id-is-auto: false           # 主键是否自增（默认 false，使用 UUID）
    super-class: com.mcst...    # Entity 父类全路径（有默认值，一般不用改）
    only-repository: false      # 是否只生成 Repository 层，不生成 Service/Controller
    create-controller: true     # 是否为该 Model 生成 Controller
    table-prefix: base_,auth_   # 单独指定该 Model 的忽略表前缀（覆盖全局 table-prefix）
    forbidden-filed: field1,field2  # 需要排除的字段，逗号分隔，生成时会跳过这些字段
    model-resource-sort: 10100  # 该 Model 的资源权限排序值
```

> `db-tables` 和 `model-list` 可以同时使用。`db-tables` 会先生成基础模型，`model-list` 会按 `table-name` 优先、`model-name` 次之的规则覆盖这些基础模型；未匹配项会作为独立手工模型追加。

#### 资源权限配置（可选）

用于在 Controller 接口上自动生成资源权限注解，与 EasyFK 框架权限体系对接：

| 配置项 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `create-resource-annotation` | 否 | `false` | 是否生成资源权限注解 |
| `resource-group` | 否 | - | 资源所属分组名称 |
| `resource-name` | 否 | - | 资源权限名称 |
| `resource-id` | 否 | - | 资源权限 ID |
| `resource-path` | 否 | - | 资源权限指向的前端路由路径 |
| `resource-sort` | 否 | `10000` | 资源组权限排序值 |
| `module-resource-sort` | 否 | `10000` | 当前模块资源排序基础值 |
| `increment-star` | 否 | `100` | 多个 Model 排序时的自增步长 |

> 以上资源权限配置也可以在 `model-list` 中为每个 Model 单独指定（字段名相同），单独指定的值优先于全局配置。

---

## 典型使用场景

### 场景一：从零创建新项目

```bash
mkdir my-project && cd my-project
efg init                # 生成配置模板
# 编辑 generator.yml
efg                     # 全量生成
```

### 场景二：已有项目新增业务表

```bash
# 修改 generator.yml 中 db-tables，添加新表名
efg -m                  # 生成新表的 Entity + Mapper
efg -s                  # 生成对应的业务代码
```

### 场景三：数据库表结构变更

```bash
efg -d                  # 仅刷新 DTO 和 Param，不影响其他代码
```

### 场景四：创建产品层项目（MICRO_PRD）

```bash
mkdir mall-prd && cd mall-prd
efg init                # 生成配置模板
# 编辑 generator.yml：设置 project-type: micro_prd, rpc-type: cloud, app-type: CLIENT
efg -p                  # 生成项目骨架
efg -s                  # 生成启动类和配置文件
# 手动引入业务模块的 API 依赖，编写 Controller
```

### 场景五：使用不同配置文件

```bash
efg -c dev-generator.yml        # 开发环境
efg -c prod-generator.yml -m    # 生产环境，仅生成 Model
```

---

## 完整配置示例

以下是 `generator.yml` 配置文件的完整示例，覆盖不同架构和典型场景。

### 单体项目（最小配置）

```yaml
easyfk:
  config:
    generator:
      project:
        project-dir: D:\workspace\projects
        group-id: com.example
        project-name: my-app
        base-package: com.example.myapp
        project-type: single
        app-type: BMS
      code:
        module-name: myapp
        model-list:
          - model-name: Product
            model-desc: 商品信息
          - model-name: Order
            model-desc: 订单信息
```

### 产品层项目（MICRO_PRD）

```yaml
easyfk:
  config:
    generator:
      project:
        project-dir: D:\workspace\projects
        group-id: com.example
        project-name: mall-prd
        base-package: com.example.mall.prd
        project-type: micro_prd
        rpc-type: cloud
        app-type: CLIENT
        framework-version: 3.5.16
      code:
        module-name: mall
```

> **MICRO_PRD 项目不需要数据库配置和 model-list**，因为它不生成任何业务代码。生成后手动在 pom.xml / build.gradle 中引入需要调用的微服务 API 模块依赖，编写 Controller 通过 RPC 远程调用后端服务。
>
> **注意**：MICRO_PRD 项目的 `rpc-type` 为必选项，必须指定为 `cloud` 或 `dubbo`。`orm-type` 和 `prd-type` 会被忽略（强制为 NONE）。

### 微服务项目（Spring Cloud）

```yaml
easyfk:
  config:
    generator:
      project:
        project-dir: D:\workspace\projects
        group-id: com.example
        project-name: order-service
        base-package: com.example.order
        project-type: microservice
        rpc-type: cloud
        prd-type: single
        build-type: gradle
        app-type: CLIENT
        framework-version: 3.5.16
      code:
        module-name: order
        author: 开发者
        db-type: MYSQL
        db-short-url: localhost:3306/order_db
        db-user: root
        db-pwd: 123456
        db-tables: t_order,t_order_item
        table-prefix: t_
```

### 微服务项目（Dubbo）

```yaml
easyfk:
  config:
    generator:
      project:
        project-dir: D:\workspace\projects
        group-id: com.example
        project-name: user-service
        base-package: com.example.user
        project-type: microservice
        rpc-type: dubbo
        prd-type: separation
        build-type: maven
        app-type: BMS
        framework-version: 3.5.16
      code:
        module-name: user
        db-type: POSTGRE_SQL
        db-short-url: localhost:5432/user_db
        db-user: postgres
        db-pwd: 123456
        db-tables: user_info,user_address
        model-list:
          - model-name: UserInfo
            model-desc: 用户信息
            forbidden-filed: status
          - model-name: UserAddress
            model-desc: 收货地址
```

### 智能型项目（SMART）

```yaml
easyfk:
  config:
    generator:
      project:
        project-dir: D:\workspace\projects
        group-id: com.mcst
        project-name: trading
        base-package: com.mcst.trading
        project-type: smart
        prd-type: separation
        build-type: gradle
        gradle-type: groovy
        orm-type: MYBATIS
        log-type: LOGBACK
        app-type: BMS
        framework-version: 3.5.16
        project-version: 1.0.0-SNAPSHOT
        controller-auto-config: true
      code:
        module-name: trading
        author: 开发团队
        spring-annotation: true
        db-type: MYSQL
        db-short-url: 192.168.1.100:3306/trading_db
        db-user: root
        db-pwd: secure_password
        table-prefix: t_
        db-tables: t_product,t_order,t_order_item,t_payment
        model-list:
          - model-name: Product
            model-desc: 商品
          - model-name: Order
            model-desc: 订单
          - model-name: OrderItem
            model-desc: 订单明细
            only-repository: true
          - model-name: Payment
            model-desc: 支付记录
            create-controller: false
```

### 智能型项目 + ORM 抽离（SMART_ORM）

`smart_orm` 在 `smart` 的基础上，将 ORM 层抽离为独立的 `-orm` 父模块：

- `-orm-api`：Repository 接口契约，不依赖任何 ORM 框架；
- `-orm-plus` / `-orm-flex` / `-orm-hibernate`：各 ORM 的实体、Mapper、Repository 实现与自动装配配置；
- server 模块只依赖 `-orm-api`，编译期不绑定具体 ORM，运行时按 classpath 中引入的 orm 实现模块自动选择。

```yaml
easyfk:
  config:
    generator:
      project:
        project-dir: D:\workspace\projects
        group-id: com.mcst
        project-name: trading
        base-package: com.mcst.trading
        project-type: smart_orm
        prd-type: separation
        build-type: gradle
        gradle-type: groovy
        orm-type: NONE
        # 不填默认生成全部：MYBATIS / MYBATIS_FLEX / HIBERNATE
        # 可按需选配，例如只生成 MyBatis-Plus 与 Hibernate：
        # orm-modules:
        #   - MYBATIS
        #   - HIBERNATE
        log-type: LOGBACK
        app-type: BMS
        framework-version: 3.5.16
        project-version: 1.0.0-SNAPSHOT
      code:
        module-name: trading
        author: 开发团队
        db-type: MYSQL
        db-short-url: 192.168.1.100:3306/trading_db
        db-user: root
        db-pwd: secure_password
        table-prefix: t_
        db-tables: t_product,t_order
```

> **说明**：`smart_orm` 模式默认对 server / orm / remote / prd 全模块生成 Spring Boot 自动装配配置（等价于始终执行 `-a`），生成结果与模块化示例项目结构一致。

### 从数据库自动解析表结构

```yaml
easyfk:
  config:
    generator:
      project:
        project-dir: D:\workspace\projects
        group-id: com.example
        project-name: my-app
        base-package: com.example.myapp
        project-type: single
        app-type: BMS
      code:
        module-name: myapp
        db-type: MYSQL
        db-short-url: localhost:3306/my_database
        db-user: root
        db-pwd: 123456
        table-prefix: base_
        db-tables: base_product,base_category,base_brand
```

**工作原理：**
1. 生成器通过 JDBC 连接数据库
2. 使用 `DatabaseMetaData` 获取表结构（字段名、类型、注释、主键等）
3. 按 `table-prefix` 自动去除忽略前缀（如配置 `base_,auth_` 时，`base_product` → `Product`）
4. 将下划线字段名转为驼峰命名（`product_name` → `productName`）
5. 按类型映射规则转换 Java 类型
6. 读取字段注释作为 `@Schema` 和 `@Column` 的描述

### 带资源权限注解的配置

```yaml
easyfk:
  config:
    generator:
      project:
        project-dir: D:\workspace\projects
        group-id: com.mcst
        project-name: user
        base-package: com.mcst.user
        project-type: smart
        prd-type: separation
        build-type: gradle
        app-type: BMS
      code:
        module-name: user
        db-short-url: localhost:3306/user_db
        db-pwd: 123456
        create-resource-annotation: true
        resource-group: userManagement
        resource-id: userManagement
        resource-name: 用户管理
        resource-path: /user
        resource-sort: 80000
        module-resource-sort: 10000
        increment-star: 100
        model-list:
          - model-name: UserInfo
            model-desc: 会员
          - model-name: UserAddress
            model-desc: 收货地址
          - model-name: UserAccount
            model-desc: 账号
```

**排序值自动计算：**
- UserInfo: `modelResourceSort = 10000 + 100 = 10100`
- UserAddress: `modelResourceSort = 10000 + 200 = 10200`
- UserAccount: `modelResourceSort = 10000 + 300 = 10300`

---

## 常见问题

**Q: 提示"找不到 java"**

请安装 JDK 21：https://adoptium.net/zh-CN/

**Q: 生成的代码会覆盖我手动修改的文件吗？**

不会。Entity 和 DTO 会更新（跟随数据库结构），但 Mapper、Repository、Service、Controller 等文件使用"不存在才创建"策略，已有文件不会被覆盖。

**Q: 支持哪些数据库？**

MySQL、PostgreSQL、Oracle、MariaDB、SQL Server、达梦、人大金仓、GaussDB、OceanBase、ClickHouse、DB2、H2、SQLite、GBase、OSCAR、Sybase、Firebird 等 23 种数据库。完整列表见上方「支持的数据库类型」表格。

**Q: 配置文件格式和 Spring Boot 的 application.yml 一样吗？**

完全一致。如果你已有 Spring Boot 项目中的生成器配置，直接复制过来即可。

**Q: `efg init` 会覆盖已有的配置文件吗？**

不会。如果目标文件已存在，`efg init` 会提示警告并退出，不覆盖。

**Q: 安装目录在哪里？如何完全卸载？**

安装目录为 Windows `%USERPROFILE%\.easyfk-gen`、macOS / Linux `~/.easyfk-gen`。运行卸载脚本（`uninstall.bat` 或 `./uninstall`）会自动删除该目录并清理 PATH。macOS / Linux 卸载后需手动删除 shell 配置文件（如 `~/.zshrc`）中的 PATH 行。
