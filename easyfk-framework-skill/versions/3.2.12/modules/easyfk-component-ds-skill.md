# component-ds Skill 参考文档

> 所属项目：`easyfk-component`　子模块：`ds-druid`
> 坐标：`com.mcst:ds-druid:3.2.12`（artifactId 取自 Gradle 项目名）
> 依据：`ds-druid/build.gradle`、BOM `easyfk-dependencies/settings.gradle`；对齐 `易架构组件项目说明文档.md` §3.16 和 `dependencies开发手册.md`（该模块没有独立的手册）。
> 以源码为准；差异见文末「复查记录」。

---

## 1. 模块现状

- 这个模块**没有任何封装代码**，只做依赖聚合：`api('com.alibaba:druid-spring-boot-3-starter')`（版本 1.2.27 由 BOM 管理，不再排除 `org.springframework.boot` 组，Boot 版本由平台统一管理）。
- `druid-spring-boot-3-starter` 是 Druid 官方的 Spring Boot 3 starter，自带 `AutoConfiguration.imports`，因此：
  - `spring.datasource.druid.*` 配置生效；
  - StatViewServlet（监控页面）、WebStatFilter、Spring AOP 监控按 Druid 官方配置开启。
- 父工程 `component-ds/build.gradle` 是空文件，属于正常的聚合父工程，不影响构建。

## 2. 用法

```groovy
implementation 'com.mcst:ds-druid'      // 版本由 easyfk-dependencies 管理
```

```yaml
spring:
  datasource:
    url: jdbc:mysql://...
    username: xxx
    password: xxx
    druid:
      initial-size: 5
      min-idle: 5
      max-active: 20
      stat-view-servlet: {enabled: true, login-username: admin, login-password: ***}
```

- 配置项、监控页面路径（默认 `/druid/*`）均为 Druid 官方约定，没有 easyfk 专属前缀。
- 生产环境开启 stat-view-servlet 时务必设置登录账号，或通过 `allow` 限制来源 IP。

## 3. 生成代码时的规则

**Do**
- 依赖坐标写 `com.mcst:ds-druid`，或直接使用 `com.alibaba:druid-spring-boot-3-starter`。
- 使用 Druid 官方的 `spring.datasource.druid.*` 配置。

**Don't**
- 不要寻找 ds-druid 的 easyfk 专属配置或 Bean，它们不存在。
- 不要再引入面向 Boot 2 的 `druid-spring-boot-starter`。

## 4. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | 组件说明 §3.16 | Druid 连接池与监控：SQL 监控、慢 SQL 分析、连接池统计 | 模块里没有任何配置代码。所依赖的 Boot 2 starter 只有 `spring.factories`，在 Boot 3 下自动配置**不会加载**，监控和 `spring.datasource.druid.*` 配置都不生效 **已修复**：依赖改为 `druid-spring-boot-3-starter`，Druid 官方自动配置与监控在 Boot 3 下生效（模块本身仍无封装代码） |
| 2 | 源码 | — | `ds-druid/src/main/java/com/mcst/Main.java` 是 IDE 模板生成的示例类，会被打包发布；`component-ds/build.gradle` 是空文件 **已修复**：已删除 `Main.java`；空的父工程 `build.gradle` 属正常现象，无需改动 |
| 3 | dependencies 手册、BOM `settings.gradle` | `com.mcst:datasource-druid`（EasyFK Druid 封装），`datasource` bundle 中包含它 | 实际发布的 artifactId 是 `ds-druid`，BOM 中这个坐标**解析不到**；使用 `datasource` bundle 会导致依赖解析失败 **已修复**：BOM 别名改名为 `ds-druid`，指向 `com.mcst:ds-druid`；`druid` 别名指向 `druid-spring-boot-3-starter` |
| 4 | build.gradle | — | 排除了 `org.springframework.boot` 整个 group，所以 starter 带来的 Boot 依赖全部要由业务项目自己提供（Boot 项目本身就有，不影响使用） **已修复**：移除该排除，Boot 依赖正常传递，版本由 Spring Boot 平台统一管理 |
