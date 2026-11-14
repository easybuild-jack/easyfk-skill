# XXL-JOB 组件使用手册

## 一、组件介绍

XXL-JOB 组件是 EasyFK 框架中用于集成 XXL-JOB 分布式任务调度平台的组件，提供了简化的任务注册、配置和自动初始化功能。

### 主要功能

- **注解驱动**：通过简单的注解即可定义定时任务
- **自动扫描**：自动扫描并注册带有 `@XxlJobHandler` 注解的任务处理器
- **自动初始化**：支持自动在 XXL-JOB Admin 中创建和更新任务
- **配置灵活**：支持通过配置文件进行任务调度配置

## 二、快速开始

### 2.1 添加依赖

在项目的 `build.gradle` 中添加依赖：

```gradle
dependencies {
    implementation 'com.mcst:job-xxl:3.2.12'
}
```

### 2.2 配置文件

在 `application.yml` 中添加 XXL-JOB 相关配置：

```yaml
xxl:
  job:
    # 管理端配置
    admin:
      addresses: http://localhost:8080/xxl-job-admin  # XXL-JOB Admin 地址
      accessToken: default_token                       # 访问令牌
    
    # 执行器配置
    executor:
      appName: your-app-name                           # 执行器名称（必填）
      appTitle: 您的应用名称                            # 执行器标题（必填）
      address: localhost:9999                          # 执行器地址（必填）
      logPath: /data/applogs/xxl-job                   # 日志路径（可选）
      logRetentionDays: 7                              # 日志保留天数（默认7天）
    
    # 初始化配置
    init:
      initType: CREATE  # 初始化模式：NONE/CREATE/UPDATE
```

#### 初始化模式说明

- **NONE**：不进行自动初始化，需要手动在 XXL-JOB Admin 中配置任务
- **CREATE**：只会创建新任务，不会更新已存在的任务
- **UPDATE**：创建新任务并且会更新已存在的任务配置

### 2.3 创建任务处理器

#### 基本用法

```java
package com.example.job;

import com.mcst.easyfk.job.xxl.annotation.JobConfig;
import com.mcst.easyfk.job.xxl.annotation.XxlJobHandler;
import com.xxl.job.core.handler.annotation.XxlJob;
import lombok.extern.slf4j.Slf4j;

/**
 * 示例任务处理器
 */
@Slf4j
@XxlJobHandler(author = "张三")
public class DemoJobHandler {

    /**
     * 简单定时任务示例
     */
    @XxlJob("demoJobHandler")
    @JobConfig(
        desc = "示例定时任务",
        cron = "0/10 * * * * ?"  // 每10秒执行一次
    )
    public void demoJob() {
        log.info("执行示例定时任务");
        // 业务逻辑
    }

    /**
     * 带参数的定时任务示例
     */
    @XxlJob("paramJobHandler")
    @JobConfig(
        desc = "带参数的定时任务",
        cron = "0 0/1 * * * ?"  // 每分钟执行一次
    )
    public void paramJob() {
        String param = XxlJobHelper.getJobParam();
        log.info("接收到的参数: {}", param);
        // 使用参数进行业务处理
    }

    /**
     * 分片任务示例
     */
    @XxlJob("shardingJobHandler")
    @JobConfig(
        desc = "分片任务示例",
        cron = "0 0/5 * * * ?"  // 每5分钟执行一次
    )
    public void shardingJob() {
        // 获取分片参数
        int shardIndex = XxlJobHelper.getShardIndex();
        int shardTotal = XxlJobHelper.getShardTotal();
        
        log.info("分片参数: 当前分片序号 = {}, 总分片数 = {}", shardIndex, shardTotal);
        
        // 根据分片参数处理业务
        // 例如：根据 shardIndex 处理不同的数据分片
    }
}
```

## 三、核心注解说明

### 3.1 @XxlJobHandler

**作用**：标识一个类为 XXL-JOB 任务处理器，继承了 `@Component` 的功能，会被 Spring 自动扫描和注册。

**属性**：

- `author`：任务负责人，可选，默认为空字符串

**示例**：

```java
@XxlJobHandler(author = "张三")
public class MyJobHandler {
    // ...
}
```

### 3.2 @XxlJob

**作用**：标识一个方法为 XXL-JOB 任务处理方法（XXL-JOB 官方注解）。

**属性**：

- `value`：JobHandler 名称，必填，全局唯一

**示例**：

```java
@XxlJob("myJobHandler")
public void myJob() {
    // 任务逻辑
}
```

### 3.3 @JobConfig

**作用**：为任务方法提供描述信息和 Cron 表达式配置。

**属性**：

- `desc`：任务描述，必填
- `cron`：Cron 表达式，可选，默认为 `"0/5 * * * * ?"` （每5秒执行一次）

**示例**：

```java
@JobConfig(
    desc = "用户数据同步任务",
    cron = "0 0 2 * * ?"  // 每天凌晨2点执行
)
```

## 四、Cron 表达式说明

Cron 表达式格式：`秒 分 时 日 月 周`

### 常用示例

| Cron 表达式            | 说明          |
|---------------------|-------------|
| `0/5 * * * * ?`     | 每5秒执行一次     |
| `0 0/1 * * * ?`     | 每分钟执行一次     |
| `0 0/5 * * * ?`     | 每5分钟执行一次    |
| `0 0 * * * ?`       | 每小时执行一次     |
| `0 0 0 * * ?`       | 每天0点执行一次    |
| `0 0 2 * * ?`       | 每天凌晨2点执行    |
| `0 0 12 * * ?`      | 每天中午12点执行   |
| `0 0 0 1 * ?`       | 每月1号0点执行    |
| `0 0 0 ? * MON`     | 每周一0点执行     |
| `0 0 0 ? * MON-FRI` | 周一到周五每天0点执行 |

### 特殊字符说明

- `*`：表示任意值
- `?`：仅用于日和周，表示不指定值
- `-`：表示范围，如 `MON-FRI`
- `,`：表示列举，如 `MON,WED,FRI`
- `/`：表示增量，如 `0/5` 表示从0开始每隔5个单位

## 五、高级特性

### 5.1 任务参数

在任务方法中可以通过 `XxlJobHelper` 获取任务参数：

```java
@XxlJob("jobWithParam")
@JobConfig(desc = "带参数的任务")
public void jobWithParam() {
    String param = XxlJobHelper.getJobParam();
    // 使用参数
}
```

### 5.2 分片广播

支持大数据量的分片处理：

```java
@XxlJob("shardingJob")
@JobConfig(desc = "分片任务")
public void shardingJob() {
    int shardIndex = XxlJobHelper.getShardIndex();  // 当前分片序号
    int shardTotal = XxlJobHelper.getShardTotal();  // 总分片数
    
    // 根据分片参数处理数据
    for (int i = 0; i < dataList.size(); i++) {
        if (i % shardTotal == shardIndex) {
            // 处理属于当前分片的数据
        }
    }
}
```

### 5.3 任务日志

通过 `XxlJobHelper` 记录任务日志：

```java
@XxlJob("logJob")
@JobConfig(desc = "日志示例任务")
public void logJob() {
    XxlJobHelper.log("开始执行任务");
    
    try {
        // 业务逻辑
        XxlJobHelper.log("任务执行成功");
        XxlJobHelper.handleSuccess();
    } catch (Exception e) {
        XxlJobHelper.log("任务执行失败: " + e.getMessage());
        XxlJobHelper.handleFail();
    }
}
```

### 5.4 手动设置任务结果

```java
@XxlJob("resultJob")
@JobConfig(desc = "结果处理任务")
public void resultJob() {
    try {
        // 业务逻辑
        XxlJobHelper.handleSuccess("任务执行成功");
    } catch (Exception e) {
        XxlJobHelper.handleFail("任务执行失败: " + e.getMessage());
    }
}
```

## 六、自动初始化机制

### 6.1 工作原理

组件启动时会自动完成以下操作：

1. **扫描任务处理器**：扫描所有带有 `@XxlJobHandler` 注解的类
2. **提取任务信息**：提取类中所有带有 `@XxlJob` 注解的方法信息
3. **初始化执行器组**：在 XXL-JOB Admin 中创建/更新执行器组
4. **初始化任务**：根据配置模式创建或更新任务信息

### 6.2 初始化配置

#### NONE 模式（默认）

```yaml
xxl:
  job:
    init:
      initType: NONE
```

- 不进行任何自动初始化
- 需要手动在 XXL-JOB Admin 中配置任务
- 启动时仅扫描并打印任务信息

#### CREATE 模式

```yaml
xxl:
  job:
    init:
      initType: CREATE
```

- 自动创建新任务
- 如果任务已存在，则跳过
- 适用于首次部署或只需创建新任务的场景

#### UPDATE 模式

```yaml
xxl:
  job:
    init:
      initType: UPDATE
```

- 自动创建新任务
- 自动更新已存在任务的配置（Cron表达式、描述等）
- 适用于需要同步任务配置的场景

### 6.3 执行器组配置

执行器组的 `appName` 和 `appTitle` 配置：

```yaml
xxl:
  job:
    executor:
      appName: my-app          # 执行器 AppName（英文）
      appTitle: 我的应用        # 执行器标题（中文）
```

- `appName`：执行器的唯一标识，建议使用英文
- `appTitle`：执行器的显示名称，可以使用中文

## 七、任务监控

### 7.1 查看扫描结果

启动时会在日志中打印扫描结果：

```
==================== XxlJob 扫描结果 ====================
类: DemoJobHandler
  └─ JobHandler: demoJobHandler (方法: demoJob, 描述: 示例定时任务, Cron: 0/10 * * * * ?)
  └─ JobHandler: paramJobHandler (方法: paramJob, 描述: 带参数的定时任务, Cron: 0 0/1 * * * ?)
=====================================================
共扫描到 2 个 JobHandler: [demoJobHandler, paramJobHandler]
```

### 7.2 XXL-JOB Admin 管理

访问 XXL-JOB Admin 管理界面：

1. 登录 XXL-JOB Admin（默认账号：admin/123456）
2. 查看执行器管理：查看已注册的执行器
3. 任务管理：查看、编辑、启动/停止任务
4. 调度日志：查看任务执行历史
5. 执行日志：查看任务详细执行日志

## 八、最佳实践

### 8.1 任务命名规范

```java
@XxlJobHandler(author = "开发者姓名")
public class UserJobHandler {  // 类名：业务模块 + JobHandler
    
    @XxlJob("userDataSyncJob")  // JobHandler名：业务描述 + Job
    @JobConfig(desc = "用户数据同步任务")
    public void syncUserData() {
        // ...
    }
}
```

### 8.2 异常处理

```java
@XxlJob("safeJob")
@JobConfig(desc = "安全的任务处理")
public void safeJob() {
    try {
        // 业务逻辑
        XxlJobHelper.log("业务执行成功");
        XxlJobHelper.handleSuccess();
    } catch (Exception e) {
        log.error("任务执行异常", e);
        XxlJobHelper.log("任务执行失败: " + e.getMessage());
        XxlJobHelper.handleFail(e.getMessage());
    }
}
```

### 8.3 任务幂等性

确保任务可以安全地重复执行：

```java
@XxlJob("idempotentJob")
@JobConfig(desc = "幂等任务")
public void idempotentJob() {
    String taskId = UUID.randomUUID().toString();
    
    // 检查任务是否已执行
    if (isTaskExecuted(taskId)) {
        XxlJobHelper.log("任务已执行，跳过");
        return;
    }
    
    try {
        // 执行业务逻辑
        doBusinessLogic();
        
        // 标记任务已执行
        markTaskExecuted(taskId);
        
        XxlJobHelper.handleSuccess();
    } catch (Exception e) {
        XxlJobHelper.handleFail(e.getMessage());
    }
}
```

### 8.4 大数据量处理

使用分片 + 分批处理：

```java
@XxlJob("bigDataJob")
@JobConfig(desc = "大数据处理任务")
public void bigDataJob() {
    int shardIndex = XxlJobHelper.getShardIndex();
    int shardTotal = XxlJobHelper.getShardTotal();
    
    XxlJobHelper.log("开始处理分片 {}/{}", shardIndex, shardTotal);
    
    int pageSize = 1000;
    int pageNum = 0;
    
    while (true) {
        // 分页查询数据
        List<Data> dataList = queryDataByPage(pageNum, pageSize, shardIndex, shardTotal);
        
        if (dataList.isEmpty()) {
            break;
        }
        
        // 批量处理
        processDataBatch(dataList);
        
        XxlJobHelper.log("处理第 {} 页，共 {} 条记录", pageNum, dataList.size());
        pageNum++;
    }
    
    XxlJobHelper.handleSuccess("处理完成");
}
```

## 九、常见问题

### 9.1 任务未自动注册

**问题**：启动后在 XXL-JOB Admin 中看不到任务

**解决方案**：

1. 检查 `initType` 配置是否为 `NONE`，如果是则需要改为 `CREATE` 或 `UPDATE`
2. 检查任务类是否添加了 `@XxlJobHandler` 注解
3. 检查任务方法是否同时添加了 `@XxlJob` 和 `@JobConfig` 注解
4. 检查 XXL-JOB Admin 地址配置是否正确

### 9.2 任务重复执行

**问题**：任务在短时间内多次执行

**解决方案**：

1. 检查 Cron 表达式是否正确
2. 在 XXL-JOB Admin 中检查任务的调度状态
3. 确保任务具有幂等性

### 9.3 连接 Admin 失败

**问题**：无法连接到 XXL-JOB Admin

**解决方案**：

1. 检查 Admin 地址配置是否正确
2. 检查 Admin 服务是否正常运行
3. 检查网络连接是否正常
4. 检查 `accessToken` 配置是否与 Admin 一致

### 9.4 日志查看不到

**问题**：在 XXL-JOB Admin 中看不到执行日志

**解决方案**：

1. 检查 `logPath` 配置是否正确
2. 确保日志目录有写入权限
3. 使用 `XxlJobHelper.log()` 记录日志

## 十、组件架构

### 10.1 核心类说明

| 类名                 | 说明                      |
|--------------------|-------------------------|
| `XxlJobConfig`     | 组件配置类，负责初始化 XXL-JOB 执行器 |
| `XxlJobProperties` | 配置属性类，映射配置文件中的属性        |
| `XxlJobScanner`    | 任务扫描器，扫描并收集所有任务信息       |
| `InitService`      | 初始化服务，负责自动创建/更新任务       |
| `@XxlJobHandler`   | 任务处理器注解，标识任务处理类         |
| `@JobConfig`       | 任务配置注解，提供任务描述和 Cron 配置  |

### 10.2 工作流程

```
应用启动
    ↓
扫描 @XxlJobHandler 注解的类
    ↓
提取 @XxlJob 方法信息
    ↓
检查 initType 配置
    ↓
初始化执行器组（CREATE/UPDATE模式）
    ↓
批量创建/更新任务（CREATE/UPDATE模式）
    ↓
打印扫描结果
    ↓
等待调度执行
```

## 十一、版本信息

- **组件版本**：3.2.12
- **XXL-JOB 版本**：依赖 `com.xuxueli:xxl-job-core`
- **Java 版本**：Java 21
- **Spring Boot 版本**：兼容 Spring Boot 3.x

## 十二、参考资料

- [XXL-JOB 官方文档](https://www.xuxueli.com/xxl-job/)
- [Cron 表达式生成器](https://cron.qqe2.com/)
- EasyFK 框架文档

---

**更新时间**：2025-11-22  
**作者**：EasyFK 团队
