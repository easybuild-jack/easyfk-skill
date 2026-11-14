# easyfk-log Skill 参考文档

> 所属项目：`easyfk-base`　子模块：`log-logback`、`log-log4j2`　坐标：`com.mcst:log-logback:3.2.12` / `com.mcst:log-log4j2:3.2.12`
> 依据：两个子模块的 `build.gradle`（没有 Java 源码和资源文件），并对齐 `核心模块说明.md` 5.2、`EasyFK框架开发手册.md` 3.7、`dependencies开发手册.md`、代码生成器的日志模板、TraceId 写入 MDC 的源码。

---

## 1. 模块定位

`easyfk-log` 是**纯依赖封装**，没有类、没有自动配置、也没有默认日志配置文件。它只做一件事：让业务项目通过引入一个坐标来选定日志实现。

- 框架其余模块（core、web-simple、gateway 等）引入 Spring Boot starter 时都**排除了 `spring-boot-starter-logging`**，所以只引入 easyfk 模块的应用**没有任何日志实现**。必须在两个子模块中选一个引入。
- 业务代码统一面向 SLF4J 编程（Lombok `@Slf4j`），切换实现时不用改代码。

| 子模块 | 传递的依赖 |
|---|---|
| `log-logback` | `spring-boot-starter-logging`（含 `logback-classic`、`log4j-to-slf4j`、`jul-to-slf4j` 桥接，不做排除），以及 `logstash-logback-encoder`（BOM 管理版本 8.0） |
| `log-log4j2` | `spring-boot-starter-log4j2` |

---

## 2. 引入方式（二选一）

```groovy
dependencies {
    implementation platform('com.mcst:easyfk-dependencies:3.2.12')
    implementation 'com.mcst:log-logback'      // 或者：implementation 'com.mcst:log-log4j2'
}
```

```xml
<dependency>
    <groupId>com.mcst</groupId>
    <artifactId>log-logback</artifactId>
</dependency>
```

`easyfk-dependencies` 中还提供了 `logging` bundle（log4j2 + logback + encoder），**不要整体引入**，否则两个实现会同时出现在 classpath 上。

---

## 3. 规则

1. **只能引入一个**：同时引入 `log-logback` 和 `log-log4j2` 时，SLF4J 会提示存在多个 provider。如果最终选中的不是 logback，Spring Boot 会抛 `LoggerFactory is not a Logback LoggerContext but Logback is on the classpath`，导致启动失败。
2. **业务项目自己引入的 Spring Boot starter 也要排除默认 logging**，写法与框架一致：
   ```groovy
   implementation('org.springframework.boot:spring-boot-starter-data-redis') {
       exclude group: 'org.springframework.boot', module: 'spring-boot-starter-logging'
   }
   ```
   选择 log4j2 时，这一条是**必须**的，否则 logback 会被重新带进来。选择 logback 时，被带进来的是同一个 starter，问题不大，但建议保持一致。
3. **选择 logback 时**：log-logback 保留了 starter 自带的 `log4j-to-slf4j` 桥接包，直接使用 Log4j2 API 的三方库日志会经 SLF4J 进入 logback。不要再额外引入 `log4j-core` 或 `log4j-slf4j2-impl`，它们会与 logback 冲突。
4. 日志配置文件需要业务项目自己提供。代码生成器生成的项目使用 `logging.config: file:config/${logName}.xml`，配置文件放在运行目录的 `config/` 下。

---

## 4. TraceId 输出

框架把 TraceId 同时写入 `TraceIdContext` 和 SLF4J **MDC**，MDC key 是 `TRACE_ID`（对应 `RequestHeaderConstant.TRACE_ID`）：

| 写入方 | 场景 |
|---|---|
| web-base `ContextDataManager` | HTTP 请求进入时写入，请求结束时 `MDC.clear()` |
| easyfk-thread `TraceIdPropagator`（`CustomTaskExecutor`、调度池、重试池、监控线程） | 任务执行前写入，结束后恢复执行线程原值；定时/监控任务无上游 traceId 时每次执行生成新值 |
| queue-disruptor `GenericWorkHandler` | 投递时捕获，消费期间写入，处理完移除 |
| rpc-dubbo `DubboFilter` | Dubbo 调用链传递 |

日志格式中使用 `%X{TRACE_ID}` 即可打印。Log4j2 通过 SLF4J 绑定读取的是同一个 MDC，写法也是 `%X{TRACE_ID}`。

### Logback 参考配置（与生成器模板 `log_logback.xml.ftl` 一致）

```xml
<configuration>
    <property name="PATTERN"
              value="%d{yyyy-MM-dd HH:mm:ss.SSS} -%5p ${PID:- } [%15.15thread,%X{TRACE_ID}] --- %-40.40logger{39} [line: %L] : %msg%n"/>
    <appender name="console" class="ch.qos.logback.core.ConsoleAppender">
        <encoder><pattern>${PATTERN}</pattern><charset>UTF-8</charset></encoder>
    </appender>
    <appender name="INFO-FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <encoder><pattern>${PATTERN}</pattern></encoder>
        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <fileNamePattern>logs/app-%d{yyyy-MM-dd}.%i.log</fileNamePattern>
            <maxHistory>30</maxHistory>
            <maxFileSize>64MB</maxFileSize>
        </rollingPolicy>
    </appender>
    <root level="INFO">
        <appender-ref ref="console"/>
        <appender-ref ref="INFO-FILE"/>
    </root>
</configuration>
```

JSON 结构化日志（用于 ELK 采集）：log-logback 已经带了 `logstash-logback-encoder`，把 encoder 换成 `<encoder class="net.logstash.logback.encoder.LogstashEncoder"/>` 即可，MDC 中的 `TRACE_ID` 会自动成为 JSON 字段。框架**不提供**现成的 JSON 配置。

### Log4j2 参考格式

生成器模板 `generator/easyfk-generator/src/main/resources/templates/code/config/log_log4j2.xml.ftl` 的格式：

```xml
<property name="LOG_PATTERN" value="%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread,%X{TRACE_ID}] %-5level %logger{36} - %msg%n"/>
```

---

## 5. 编码规范

```java
@Slf4j
@Service
public class OrderService {
    public void process(Long orderId) {
        log.info("开始处理订单: {}", orderId);            // 使用占位符，不要字符串拼接
        try {
            // ...
        } catch (Exception e) {
            log.error("处理订单失败: {}", orderId, e);     // 异常对象放在最后一个参数
        }
    }
}
```

- `BusinessException` 没有堆栈（见 easyfk-core）。记录业务异常时要带上足够的业务参数，不要指望堆栈定位问题。
- 自己创建的线程不会自动带上 `TRACE_ID`，需要使用 easyfk-thread 的执行器，或者用 `TraceIdPropagator.wrap(...)` 包装任务。

---

## 6. 复查记录

| # | 位置 | 文档描述 | 实际情况 |
|---|---|---|---|
| 1 | 核心模块说明 5.2 | log-logback "原生支持 JSON 格式日志" | 只引入了 encoder 依赖，没有提供 JSON 配置，需要业务项目自行配置 |
| 2 | 核心模块说明 5.2 | "排除 Log4j 相关依赖，避免冲突" | 排除的是整个 `org.apache.logging.log4j` group，包括 `log4j-to-slf4j` 桥接包，使用 Log4j2 API 的三方库日志会丢失 **已修复**：log-logback 不再排除该 group，保留 `log4j-to-slf4j` 桥接 |
| 3 | 框架手册 3.7 | 只说明二选一引入 | 没有提到业务项目自己的 starter 也需要排除 `spring-boot-starter-logging`，也没有说明 `TRACE_ID` 的 MDC 用法 |
| 4 | 生成器模板 `log_log4j2.xml.ftl` | — | 日志格式缺少 `%X{TRACE_ID}`，与 logback 模板不一致 **已修复**：模板格式改为 `[%thread,%X{TRACE_ID}]` |
| 5 | 核心模块说明 四、依赖关系图 | log 依赖 core | log 的两个子模块不依赖任何 easyfk 模块 |
