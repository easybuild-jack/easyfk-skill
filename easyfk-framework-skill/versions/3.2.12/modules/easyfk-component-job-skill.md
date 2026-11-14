# easyfk-component-job Skill 参考文档

> 模块：`easyfk-component/component-job`（job-xxl）
> 坐标：`com.mcst:job-xxl`（catalog 别名 `job-xxl`，也在 `xxl` bundle 中）
> 依据：job-xxl 源码 + `XXL-JOB组件使用手册.md`、`易架构组件项目说明文档.md` §3.9
> 文档与源码不一致时 **以源码为准**，差异见文末「复查记录」。

---

## 1. 模块定位

- 依赖：`api com.xuxueli:xxl-job-core:3.2.0`；`compileOnly easyfk-core`（运行时由应用提供 core，内部使用 hutool `HttpRequest` 与 Jackson `ObjectMapper`）。
- 作用：
  1. 按 `xxl.job.*` 配置创建 `XxlJobSpringExecutor`（执行器，内嵌 HTTP 服务，默认端口 9999）；
  2. 扫描 `@XxlJobHandler` 类中的 `@XxlJob` 方法，读取 `@JobConfig(desc, cron)`；
  3. 可选：启动时调用调度中心接口自动创建执行器组与任务。
- 任务的执行仍是 xxl-job 原生机制：所有 Spring Bean 中的 `@XxlJob` 方法都会被 `XxlJobSpringExecutor` 注册，与是否标注 `@XxlJobHandler` 无关；`@XxlJobHandler` 只影响“自动初始化”。

---

## 2. 自动配置

`XxlJobConfig`（`@AutoConfiguration`，**无开关、无条件**，引入即生效）：

| Bean | 说明 |
|---|---|
| `xxlJobExecutor`（`XxlJobSpringExecutor`） | 校验 `admin.addresses`、`executor.app-name`、`executor.app-title` 非空，否则抛 `IllegalArgumentException` |
| `InitService`（`CommandLineRunner`） | 应用启动完成后执行初始化或打印扫描结果 |
| `XxlJobScanner`（`BeanPostProcessor`，非 static @Bean） | 收集 `@XxlJobHandler` 类的任务信息 |

- 都没有 `@ConditionalOnMissingBean`，无法替换。
- `xxl.job.admin`、`xxl.job.executor`、`xxl.job.init` 三个配置对象有默认实例：缺少 `admin.addresses`、`executor.app-name`、`executor.app-title` 时抛校验错误 `IllegalArgumentException`；缺少 `init` 段时按 `NONE` 处理。

---

## 3. 配置（前缀 `xxl.job`）

```yaml
xxl:
  job:
    admin:
      addresses: http://xxl-job-admin:8080/xxl-job-admin   # 必填；多个地址逗号分隔，自动初始化依次尝试
      access-token: default_token                          # 默认 default_token，需与调度中心一致；自动初始化请求也通过 XXL-JOB-ACCESS-TOKEN 头携带
    executor:
      app-name: order-service-executor                     # 必填
      app-title: 订单服务                                   # 必填（框架自定义校验）
      address:                                             # 可选，优先级最高；"ip:port" 会自动补 http://
      ip:                                                  # 可选，默认自动获取
      port: 9999                                           # 可选，不填时 xxl-job 默认 9999
      log-path: /data/applogs/xxl-job/jobhandler           # 可选，不填用 xxl-job 默认值
      log-retention-days: 7
    init:
      init-type: NONE                                      # NONE（默认）/ CREATE / UPDATE
      group-save-path: /jobgroup/initSave                  # 以下三个为定制版调度中心的接口路径，可按实际修改
      job-save-path: /jobinfo/initSave
      job-update-path: /jobinfo/initUpdate
```
- `address` 必须是 `[http(s)://]ip:port` 形式（按 URI 解析，取 host 与 port）；无法解析或缺少端口时抛 `IllegalArgumentException`。
- 只配置 `ip` 与 `port` 两者时才会拼出 `address`；只配其一时由 xxl-job 自动处理。
- 执行器端口必须能被调度中心访问；容器 / K8s 环境通常需要显式配置 `address` 或 `ip`。

---

## 4. 定义任务

```java
import com.mcst.easyfk.job.xxl.annotation.JobConfig;
import com.mcst.easyfk.job.xxl.annotation.XxlJobHandler;
import com.xxl.job.core.context.XxlJobHelper;
import com.xxl.job.core.handler.annotation.XxlJob;

@Slf4j
@XxlJobHandler(author = "张三")        // 含 @Component
public class OrderJobHandler {

    @XxlJob("orderTimeoutCloseJob")    // JobHandler 名称，全局唯一
    @JobConfig(desc = "超时订单关闭", cron = "0 0/5 * * * ?")
    public void closeTimeoutOrders() {
        String param = XxlJobHelper.getJobParam();
        int shardIndex = XxlJobHelper.getShardIndex();
        int shardTotal = XxlJobHelper.getShardTotal();
        try {
            // 业务逻辑：按分片处理，保证幂等
            XxlJobHelper.handleSuccess();
        } catch (Exception e) {
            log.error("超时订单关闭失败", e);
            XxlJobHelper.handleFail(e.getMessage());
        }
    }
}
```
- 幂等要以**业务主键**判断，而不是每次执行新生成的随机 ID，例如：

```java
for (Order order : orderMapper.listTimeout(shardIndex, shardTotal)) {
    // 状态条件更新：只有仍处于待支付的订单会被关闭，重复执行无副作用
    int rows = orderMapper.closeIfUnpaid(order.getId());
    if (rows == 0) {
        XxlJobHelper.log("订单 {} 已处理，跳过", order.getId());
    }
}
```
- `@JobConfig` 可省略：此时描述 = 方法名，cron = `0/5 * * * * ?`（每 5 秒）。
- `@JobConfig.cron` 只用于自动初始化时写入调度中心；`NONE` 模式下没有任何作用，调度周期以调度中心配置为准。
- 扫描基于 `bean.getClass().getDeclaredMethods()`，按类的全限定名归组，不同包下的同名处理类互不覆盖。

---

## 5. 自动初始化（init-type = CREATE / UPDATE）

启动完成后（`CommandLineRunner`），所有请求都带 `XXL-JOB-ACCESS-TOKEN: {admin.access-token}` 头，并对 `admin.addresses` 中的地址依次尝试，取第一个 HTTP 200 的响应：
1. `POST {address}{init.group-save-path}`（默认 `/jobgroup/initSave`；form：`appname`、`title`=app-title、`addressType=0`），响应 `code==200` 时 `content` 作为 groupId；
2. 对每个扫描到的任务 `POST {address}{init.job-save-path}`（默认 `/jobinfo/initSave`），提交受管字段（`jobGroup`、`jobDesc`、`scheduleType=CRON`、`scheduleConf`、`executorHandler`）以及创建时的默认值：`executorRouteStrategy=ROUND`、`misfireStrategy=DO_NOTHING`、`executorBlockStrategy=SERIAL_EXECUTION`、`executorTimeout=0`、`executorFailRetryCount=0`、`author`=@XxlJobHandler.author（取不到注解时 `noAuthor`）；
3. `UPDATE` 模式下若响应 `content.status == 1` 且带 `id`，再调用 `POST {address}{init.job-update-path}`（默认 `/jobinfo/initUpdate`），**只提交 `id` 与受管字段（描述、cron、handler、group）**，不提交路由、阻塞、超时、重试、负责人等。

注意：
- xxl-job 3.2.0 标准调度中心**没有** `initSave` / `initUpdate` 接口，标准的 `/jobgroup/save`、`/jobinfo/add`、`/jobinfo/update` 需要登录态（accessToken 只用于执行器 RPC 的 `/api/*`）。CREATE/UPDATE 模式**必须配合定制版调度中心**，接口路径可通过 `init.*-path` 调整。
- 定制版的 update 接口需按“部分更新”实现：只覆盖请求中出现的字段，保留调度中心中手动调整的其他策略；否则未提交字段可能被置空。
- 任意一步失败只记录日志，不影响启动。

---

## 6. 生成代码时的规则

### Do
- 配置 `xxl.job.admin.addresses`、`xxl.job.executor.app-name`、`xxl.job.executor.app-title`；需要自动初始化时再配置 `xxl.job.init`。
- 只需任务调度时引用 `libs.job-xxl`（或 `xxl` bundle，现仅含 xxl-job-core 与 job-xxl）。
- 任务类使用 `@XxlJobHandler(author = "...")`，任务方法同时写 `@XxlJob("唯一名")` 和 `@JobConfig(desc, cron)`。
- 在任务内部捕获异常并调用 `XxlJobHelper.handleFail(...)`；用 `XxlJobHelper.log(...)` 输出调度中心可见日志。
- 任务实现幂等（以业务主键 / 时间窗口去重），大数据量使用分片 + 分页。
- 使用标准调度中心时保持 `init-type: NONE`，在调度中心手工维护执行器与任务。

### Don't
- 不要在没有 xxl-job 调度中心的服务中引入 job-xxl（无开关，缺配置会启动失败）。
- 不要依赖省略 `@JobConfig` 时的默认 cron（每 5 秒）。
- 不要对标准 xxl-job-admin 开启 CREATE/UPDATE（接口不存在）；定制版 update 接口不是部分更新时，不要在手动调整过策略的任务上使用 `UPDATE`。
- 不要在任务中生成随机 ID 做幂等判断。
- 不要给 `executor.address` 加路径。

---

## 7. 复查记录

| # | 文档位置 | 文档描述 | 源码实际 |
|---|---|---|---|
| 1 | 使用手册 §2.2 | `executor.address` 必填 | 可选；未配置时由 `ip`/`port` 或 xxl-job 自动获取 |
| 2 | 使用手册 §2.2 / §6.2 | 不配置时默认 `NONE` 模式 | `init`、`admin`、`executor` 对象默认为 null；缺少 `xxl.job.init` 段时 `InitService` NPE，应用启动失败；缺少 admin/executor 段时 NPE 而不是文档所说的校验错误 **已修复**：三个配置对象默认初始化，缺少 init 段按 NONE 处理，缺少必填项时抛校验错误 |
| 3 | 使用手册 §6.1 / §10.2 | 在 XXL-JOB Admin 中创建/更新执行器组与任务 | 调用 `/jobgroup/initSave`、`/jobinfo/initSave`、`/jobinfo/initUpdate`，标准 xxl-job-admin 无这些接口（推断，未运行验证），且请求不带 accessToken **已修复**：请求携带 `XXL-JOB-ACCESS-TOKEN` 头；三个接口路径可通过 `xxl.job.init.group-save-path/job-save-path/job-update-path` 配置。xxl-job 3.2.0 标准调度中心确实没有这些接口（标准管理接口需要登录态），CREATE/UPDATE 需配合定制版调度中心 |
| 4 | 使用手册 §6.2 UPDATE | 自动更新已存在任务的配置（Cron、描述等） | 更新时以固定默认值整体覆盖（路由 ROUND、阻塞 SERIAL、重试 0、超时 0 等），会冲掉调度中心中的手动修改 **已修复**：更新请求只提交 `id` 与 @JobConfig 管理的字段（描述、cron、handler、group），默认策略只在创建时提交；调度中心 update 接口需按部分更新处理（定制接口无法先查询已有任务，已在文档说明） |
| 5 | 使用手册 §9.1 第 3 条 | 任务方法须同时添加 `@XxlJob` 和 `@JobConfig` | `@JobConfig` 可选，缺省时 desc=方法名、cron=`0/5 * * * * ?` |
| 6 | 使用手册 §3.3 | `cron` 为任务的 Cron 配置 | 只在 CREATE/UPDATE 自动初始化时写入调度中心，NONE 模式下不起作用 |
| 7 | 使用手册 §8.3 | 幂等示例使用 `UUID.randomUUID()` 作为 taskId 判断是否执行过 | 每次执行生成新 ID，判断永远为“未执行”，示例无法实现幂等 |
| 8 | 使用手册 §2.3 示例 | 直接使用 `XxlJobHelper` | 示例缺少 `com.xxl.job.core.context.XxlJobHelper` 的 import |
| 9 | 源码 | — | 自动初始化把 `admin.addresses` 原样拼接 URL，多个地址时请求失败；`executor.address` 带路径时端口解析抛 `NumberFormatException` **已修复**：自动初始化依次尝试多个 admin 地址；`executor.address` 按 URI 解析 host/port，格式错误抛明确的 `IllegalArgumentException` |
| 10 | 源码 | — | 扫描结果按类 SimpleName 存储，不同包同名类互相覆盖；`InitService.toCamelCase` 未被使用 **已修复**：扫描结果以类全限定名为 key；删除未使用的 `toCamelCase` |
| 11 | 源码 / 构建 | — | `job-xxl/bin/main` 下残留 IDE 编译输出（含 imports 文件），不影响 Gradle 构建 **已修复**：已删除 `job-xxl/bin`（未纳入 git 的 IDE 输出） |
| 12 | easyfk-dependencies `xxl` bundle | 混入了与任务调度无关的库 | **已修复**：`xxl` bundle 只保留 `xxlJob`、`job-xxl` |
