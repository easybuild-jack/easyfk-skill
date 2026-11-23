# easyfk-component 基础设施类 Skill 参考文档

> 模块：`component-config/config-nacos`、`component-registry/registry-nacos`、`component-doc/doc-knife4j`、`component-protect/protect-sentinel`、`component-transaction/transaction-seata`
> 坐标：`com.mcst:config-nacos`、`com.mcst:registry-nacos`、`com.mcst:doc-knife4j`（catalog 别名 `docKnife4j`）、`com.mcst:protect-sentinel`、`com.mcst:transaction-seata`
> 依据：各模块 `build.gradle` 与源码目录、`easyfk-dependencies/settings.gradle`、Gradle 缓存中的实际解析版本、`易架构组件项目说明文档.md` §3.11–§3.15
> 这 5 个模块**只做依赖聚合，没有任何框架代码、自动配置或配置属性**；用法即对应开源组件的官方用法。下文的配置示例属于 Spring Cloud Alibaba / Knife4j 官方约定（推断，未运行验证），文档与源码不一致时以源码为准，差异见文末「复查记录」。
> job-xxl 有独立实现，见 [easyfk-component-job-skill.md](easyfk-component-job-skill.md)。

---

## 1. 模块总览

| 模块 | 引入的依赖 | 排除项 | 实际版本 |
|---|---|---|---|
| config-nacos | `spring-cloud-starter-alibaba-nacos-config` | `org.yaml`（snakeyaml） | SCA 2025.0.0.0，nacos-client 由 SCA 传递 |
| registry-nacos | `spring-cloud-starter-alibaba-nacos-discovery` | `log4j-to-slf4j`、`spring-boot-starter-logging` | SCA 2025.0.0.0，nacos-client 由 SCA 传递 |
| doc-knife4j | `knife4j-openapi3-jakarta-spring-boot-starter` | — | Knife4j 4.5.0 + springdoc **2.10.0**（BOM 强制覆盖） |
| protect-sentinel | `spring-cloud-starter-alibaba-sentinel`、`sentinel-datasource-nacos`、`sentinel-parameter-flow-control` | — | Sentinel 由 SCA 2025.0.0.0 传递 |
| transaction-seata | `spring-cloud-starter-alibaba-seata` | `log4j-to-slf4j`、`spring-boot-starter-logging` | Seata 2.x（`org.apache.seata`），版本由 SCA 传递 |

- 版本由 `easyfk-dependencies` 统一管理：Spring Boot 3.5.16、Spring Cloud 2025.0.3、Spring Cloud Alibaba 2025.0.0.0、Knife4j 4.5.0。
- 五个模块的 `build.gradle` 与 3.2.12 **完全一致**（`diff` 无差异），版本升级全部来自 BOM 的 platform 切换；本文件中的版本号均为 BOM 约束值，nacos-client / Sentinel / Seata 的具体小版本由 SCA 2025.0.0.0 传递（本机无 Gradle 缓存，未做实际解析验证）。
- 父工程统一加入 lombok 与 `easyfk-dependencies` 平台，不依赖 easyfk-core。
- Jackson 随各 starter 正常传递（版本由 Spring Boot 平台统一管理）；被排除的日志实现、snakeyaml 默认由业务应用的 Spring Boot starter / easyfk-log 提供。

---

## 2. config-nacos

```yaml
spring:
  application:
    name: order-service
  config:
    import:
      - optional:nacos:order-service.yaml          # SCA 2023.x 起必须通过 spring.config.import 引入
      - optional:nacos:common.yaml?group=COMMON_GROUP&refreshEnabled=true
  cloud:
    nacos:
      config:
        server-addr: 127.0.0.1:8848
        namespace: dev
        username: nacos
        password: nacos
        file-extension: yaml
```
- SCA 2023.x 起不再使用 bootstrap.yml；未配置 `spring.config.import` 时启动检查会失败（可用 `spring.cloud.nacos.config.import-check.enabled=false` 关闭）。SCA 2025.0.0.0 沿用该约定。
- 动态刷新：`@ConfigurationProperties` 自动刷新；`@Value` 所在 Bean 需要 `@RefreshScope`。
- easyfk 各组件的配置（`easyfk.config.*`）可以放在 Nacos 中，但多数组件只在启动时读取一次，修改后需重启（推断，未运行验证）。

## 3. registry-nacos

```yaml
spring:
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
        namespace: dev
        group: DEFAULT_GROUP
```
- 用于 Spring Cloud 服务发现（rpc-cloud 的 OpenFeign、easyfk-gateway 的 `lb://` 路由）。
- Dubbo 注册中心不依赖本模块，由 rpc-dubbo / `dubboRegistry`（`dubbo-registry-nacos`）配置 `dubbo.registry.address=nacos://...`。

## 4. doc-knife4j

```yaml
springdoc:
  api-docs:
    enabled: true
  group-configs:
    - group: default
      paths-to-match: /**
      packages-to-scan: com.example.order.controller
knife4j:
  enable: true
  production: false        # 生产环境设为 true 屏蔽文档
```
- 访问 `/doc.html`；接口描述使用 easyfk-core 已引入的 `io.swagger.v3.oas.annotations`（`@Tag`、`@Operation`、`@Schema`）。
- **springdoc 版本必须 ≥ 2.10.0**：Knife4j 4.5.0 自带 springdoc 2.3.0，它调用了 Spring 6.2 已删除的 `ControllerAdviceBean(Object)` 构造器，在 Boot 3.5 上会启动失败。BOM 已通过 `springdoc` 版本约束把 5 个 `springdoc-openapi-starter-*` 构件统一钉到 2.10.0，业务工程不要再手工降级。
- Knife4j 4.5.0 自身未跟进 Boot 3.5，仅 `doc.html` 静态页面可用；如遇 UI 兼容问题可只用 `springdocWebmvcApi` + `springdocWebmvcUi`（BOM 已暴露这两个别名）。
- easyfk-web 开启接口签名（`easyfk.config.web.security.open=true`）时，`.html/.js/.css` 等静态资源自动跳过，但 `/v3/api-docs/**` 需要加入 `ignore-uri`；需要登录校验的服务还要把文档路径加入排除列表。
- 经 easyfk-gateway 聚合时，网关会把包含 `/v3/api-docs` 的路径改写为 `/v3/api-docs` 并跳过校验（见 easyfk-gateway skill）。

## 5. protect-sentinel

```yaml
spring:
  cloud:
    sentinel:
      transport:
        dashboard: 127.0.0.1:8858
        port: 8719
      eager: true
      datasource:
        flow:
          nacos:
            server-addr: 127.0.0.1:8848
            namespace: dev
            data-id: ${spring.application.name}-flow-rules
            group-id: SENTINEL_GROUP
            data-type: json
            rule-type: flow          # flow / degrade / system / authority / param-flow
```
- Web 接口自动作为资源（webmvc-v6x 适配器）；方法级保护用 `@SentinelResource(value, blockHandler, fallback)`；热点参数限流依赖已引入的 `sentinel-parameter-flow-control`。
- 被限流时默认返回 Sentinel 自带的 429 文本，不经过 easyfk 的统一异常处理；需要统一响应格式时自定义 `BlockExceptionHandler` Bean，返回 `BRBuilder.failResult(...)` 的 JSON。
- Feign 熔断需要 `spring.cloud.openfeign.circuitbreaker.enabled=true`（rpc-cloud 的 fallback 依赖它），Sentinel 通过已引入的 `spring-cloud-circuitbreaker-sentinel` 提供实现。

## 6. transaction-seata

```yaml
seata:
  enabled: true
  application-id: ${spring.application.name}
  tx-service-group: default_tx_group
  service:
    vgroup-mapping:
      default_tx_group: default
  registry:
    type: nacos
    nacos:
      server-addr: 127.0.0.1:8848
      namespace: dev
      group: SEATA_GROUP
  config:
    type: nacos
    nacos:
      server-addr: 127.0.0.1:8848
      namespace: dev
      group: SEATA_GROUP
```
- Seata 2.x 已迁移到 Apache 包名，全局事务注解优先使用 `org.apache.seata.spring.annotation.GlobalTransactional`（推断，未运行验证）；`io.seata.*` 旧包名在 2.x 中已移除，从 3.2.12 升级时需批量替换 import。
- AT 模式需要每个参与库建 `undo_log` 表，数据源默认自动代理（`seata.enable-auto-data-source-proxy=true`）。与 ds-druid、orm-sharding 组合时，需确认只代理一次。
- XID 通过 Seata 自身的 Feign / Dubbo 拦截传播；rpc-dubbo 的 `DubboFilter` 只传 `TRACE_ID`，不负责 XID。

---

## 7. 生成代码时的规则

### Do
- 按需引用单个模块：`libs.config-nacos`、`libs.registry-nacos`、`libs.docKnife4j`、`libs.protect-sentinel`、`libs.transaction-seata`。
- 使用 `spring.config.import` 接入 Nacos 配置；Nacos 地址、命名空间、账号通过环境变量或启动参数注入。
- 为 Sentinel 规则配置 Nacos 数据源，并自定义 `BlockExceptionHandler` 统一响应格式。
- 生产环境设置 `knife4j.production=true`，或只在测试环境引入 doc-knife4j。
- Seata 参与方统一 `tx-service-group`，并建好 `undo_log` 表。

### Don't
- 不要寻找这些模块的 easyfk 专属配置前缀或 Bean，它们不存在。
- 不要使用 bootstrap.yml 接入 Nacos 配置（SCA 2023.x 起默认不再加载）。
- 不要依赖 `libs.bundles.microservice` 来引入全部微服务模块，按需引用单个模块。

---

## 8. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | 组件项目说明 §3.11–§3.15 | config-nacos、registry-nacos、doc-knife4j、protect-sentinel、transaction-seata 为“组件”，提供动态刷新、深度集成、规则持久化、AT/TCC/Saga 等能力 | 5 个模块都只有 `build.gradle` 依赖声明，没有任何框架代码或自动配置，能力全部来自开源组件本身，需按官方方式配置 |
| 2 | 组件项目说明 §3.12 | registry-nacos “与 rpc-dubbo、rpc-cloud 深度集成” | 模块只引入 nacos-discovery starter；Dubbo 使用独立的 `dubbo-registry-nacos`，两者没有框架层的集成代码 |
| 3 | 组件项目说明 §3.14 | 规则持久化到 Nacos | 只引入了 `sentinel-datasource-nacos`（Nacos 读取规则），没有把控制台修改写回 Nacos 的实现，需改造 Dashboard 或直接在 Nacos 中维护规则 |
| 4 | 组件项目说明 §3.15 | 与 orm-sharding 等组件配合使用 | 没有任何适配代码；ShardingSphere 与 Seata 的整合需要业务自行配置 |
| 5 | protect-sentinel / transaction-seata 源码 | — | 两个模块各带一个 IDE 模板生成的 `com.mcst.Main`（打印 Hello），会被打进 jar **已修复**：已删除两个 `Main.java` |
| 6 | registry-nacos / protect-sentinel / transaction-seata `build.gradle` | — | 排除了整个 `com.fasterxml.jackson.core` 组，classpath 上缺少 Jackson 的应用会在运行时报 ClassNotFound（推断，未运行验证） **已修复**：移除三个模块对 `com.fasterxml.jackson.core` 组的排除，Jackson 随 starter 传递，版本由 Boot 平台管理 |
| 7 | easyfk-dependencies `microservice` bundle | 包含 `gateway-gateway`、`doc-micro` | 仓库中不存在这两个模块，引用该 bundle 可能解析失败（推断，未运行验证） **已修复**：bundle 中移除不存在的模块，现为 `registry-nacos`、`config-nacos`、`protect-sentinel`、`easyfk-gateway` |
| 8 | 各模块 | 无使用手册 | 本目录下没有任何 README / 使用手册，本文件第 2–6 节为官方用法摘要 |
| 9 | 3.5.16 升级 | 组件文档未提及 springdoc | Knife4j 4.5.0 自带 springdoc 2.3.0，调用 Spring 6.2 已删除的 `ControllerAdviceBean(Object)`，在 Boot 3.5.16 上启动即失败 **已修复**：BOM 新增 `springdoc = 2.10.0` 版本约束，覆盖 `springdoc-openapi-starter-{common,webmvc-api,webmvc-ui,webflux-api,webflux-ui}` 五个构件 |
| 10 | 3.5.16 升级 | — | 五个模块 `build.gradle` 与 3.2.12 逐字节相同，升级风险全部集中在 SCA 2023.0.3.3 → 2025.0.0.0（Nacos / Sentinel / Seata 的传递版本随之变化），业务侧需回归 Nacos 鉴权与 Seata 包名 |
| 11 | `doc` bundle | — | bundle 中同时列了 `docKnife4j`、`knife4j` 与 5 个 `springdoc-*`，实际 doc-knife4j 已传递 knife4j starter；重复声明不会冲突（同名同版本），但若业务手工引入其他 knife4j 版本会与 `doc` bundle 的 4.5.0 冲突 |
