# EasyFK 框架开发手册

**版本：3.5.16**  
**更新日期：2025-11**

---

## 目录

- [1. 框架简介](#1-框架简介)
- [2. 快速开始](#2-快速开始)
  - [2.1 环境要求](#21-环境要求)
  - [2.2 Maven 项目配置](#22-maven-项目配置)
  - [2.3 Gradle 项目配置](#23-gradle-项目配置)
- [3. 核心模块详解](#3-核心模块详解)
  - [3.1 easyfk-core](#31-easyfk-core)
  - [3.2 easyfk-repository](#32-easyfk-repository)
  - [3.3 easyfk-service](#33-easyfk-service)
  - [3.4 easyfk-web](#34-easyfk-web)
  - [3.5 easyfk-authority](#35-easyfk-authority)
  - [3.6 easyfk-cache](#36-easyfk-cache)
  - [3.7 easyfk-log](#37-easyfk-log)
  - [3.8 easyfk-queue](#38-easyfk-queue)
  - [3.9 easyfk-thread](#39-easyfk-thread)
  - [3.10 easyfk-remote](#310-easyfk-remote)
  - [3.11 easyfk-gateway](#311-easyfk-gateway)
  - [3.12 easyfk-ws](#312-easyfk-ws)
- [4. 开发指南](#4-开发指南)
  - [4.1 创建标准业务服务](#41-创建标准业务服务)
  - [4.2 数据查询与分页](#42-数据查询与分页)
  - [4.3 异步任务处理](#43-异步任务处理)
  - [4.4 权限控制](#44-权限控制)
  - [4.5 消息推送](#45-消息推送)
- [5. 配置参考](#5-配置参考)
- [6. 最佳实践](#6-最佳实践)
- [7. 常见问题](#7-常见问题)
- [8. 附录](#8-附录)

---

## 1. 框架简介

**EasyFK Base** 是一个全面的 Spring Boot 微服务框架（版本 3.5.16），由 12 个核心模块组成，为构建可扩展的分布式应用提供基础服务。它包含数据访问、业务逻辑、缓存、异步处理、安全和服务间通信的抽象。

### 1.1 核心特性

- ✅ **分层架构**：清晰的模块依赖层次，从核心到业务层逐层构建
- ✅ **数据访问**：统一的 Repository 抽象，支持多数据库
- ✅ **高性能异步**：基于 LMAX Disruptor 的内存队列，纳秒级延迟
- ✅ **线程池增强**：自动监控、动态调优、TraceId 透传
- ✅ **权限管理**：基于注解的 RBAC 权限控制
- ✅ **实时通信**：完整的 WebSocket 支持，订阅/推送机制
- ✅ **服务通信**：支持 Dubbo 和 Spring Cloud 两种 RPC 方式
- ✅ **生产就绪**：内置监控、日志、异常处理等生产级特性

### 1.2 技术栈

- **Java 版本**：Java 21
- **Spring Boot**：3.5.16
- **构建工具**：Gradle 8.x / Maven 3.x
- **核心依赖**：Jackson、FastJSON2、Hutool、Lombok

### 1.3 模块架构

```
easyfk-core (基础层 - 无依赖)
    ↓
    ├─→ easyfk-repository (数据访问层)
    ├─→ easyfk-cache (缓存抽象)
    ├─→ easyfk-log (日志基础设施)
    ├─→ easyfk-queue (异步队列系统)
    ├─→ easyfk-thread (线程池管理)
    ├─→ easyfk-gateway (网关过滤器)
    │
    ├─→ easyfk-authority (授权与 RBAC)
    │   └─→ easyfk-service (业务逻辑层)
    │       └─→ easyfk-repository
    │
    ├─→ easyfk-web (HTTP/REST 层)
    │   ├─→ easyfk-service
    │   ├─→ easyfk-authority
    │   └─→ web-* 子模块 (base, common, micro, prd, simple)
    │
    ├─→ easyfk-remote (服务间通信)
    │   ├─→ remote-dubbo (二进制 RPC)
    │   └─→ remote-cloud (基于 HTTP 的 RPC)
    │
    └─→ easyfk-ws (WebSocket 实时通信)
        ├─→ ws-api (接口与 DTO)
        └─→ ws-server (实现)
```

---

## 2. 快速开始

### 2.1 环境要求

- **JDK**：21 或更高版本
- **构建工具**：Gradle 8.x 或 Maven 3.8+
- **IDE**：IntelliJ IDEA 2023+ 或 Eclipse 2023+
- **数据库**：根据需要选择（MySQL、PostgreSQL 等）

### 2.2 Maven 项目配置

#### 2.2.1 创建单体项目

在 `pom.xml` 中添加以下配置：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.yourcompany</groupId>
    <artifactId>your-project</artifactId>
    <version>1.0.0</version>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
        <java.version>21</java.version>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
        <framework.version>3.5.16</framework.version>
    </properties>

    <!-- 依赖管理 -->
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>com.mcst</groupId>
                <artifactId>easyfk-dependencies</artifactId>
                <version>${framework.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <!-- 项目依赖 -->
    <dependencies>
        <!-- Lombok -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <scope>compile</scope>
        </dependency>
        
        <!-- Spring Boot 配置处理器 -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-configuration-processor</artifactId>
            <scope>compile</scope>
        </dependency>
        
        <!-- 日志模块 -->
        <dependency>
            <groupId>com.mcst</groupId>
            <artifactId>log-logback</artifactId>
        </dependency>
        
        <!-- 核心模块 -->
        <dependency>
            <groupId>com.mcst</groupId>
            <artifactId>easyfk-core</artifactId>
        </dependency>
        
        <!-- 根据需要添加其他模块 -->
        <!-- Repository 模块 -->
        <!-- <dependency>
            <groupId>com.mcst</groupId>
            <artifactId>easyfk-repository</artifactId>
        </dependency> -->
        
        <!-- Web 模块 -->
        <!-- <dependency>
            <groupId>com.mcst</groupId>
            <artifactId>easyfk-web-common</artifactId>
        </dependency> -->
    </dependencies>
</project>
```

### 2.3 Gradle 项目配置

#### 2.3.1 单体项目配置

**settings.gradle** 文件：

```gradle
rootProject.name = 'your-project'

dependencyResolutionManagement.versionCatalogs {
    libs {
        library("easyfkDependencies", "com.mcst:easyfk-dependencies:3.5.16")
        library('lombok', 'org.projectlombok:lombok:1.18.46')
        library('processor', 'org.springframework.boot:spring-boot-configuration-processor:3.5.16')
    }
}
```

**build.gradle** 文件：

```gradle
// 指定项目版本号和group
version = '1.0.0'
group = 'com.yourcompany'
description = '您的项目描述'

apply plugin: 'java-library'
apply plugin: 'maven-publish'

java {
    sourceCompatibility = JavaVersion.VERSION_21
    targetCompatibility = JavaVersion.VERSION_21
    withSourcesJar()
}

[compileJava, compileTestJava]*.options*.encoding = 'UTF-8'

dependencies {
    // 依赖管理
    implementation platform(libs.easyfkDependencies)
    
    // Lombok 和注解处理器
    compileOnly libs.lombok
    testCompileOnly libs.lombok
    annotationProcessor(libs.lombok, libs.processor)
    testAnnotationProcessor(libs.lombok, libs.processor)
    
    // EasyFK 核心模块
    api('com.mcst:easyfk-core')
    
    // 日志模块
    api('com.mcst:log-logback')
    
    // 根据需要添加其他模块
    // Repository 模块
    // api('com.mcst:easyfk-repository')
    
    // Web 模块
    // api('com.mcst:easyfk-web-common')
    
    // 线程池模块
    // api('com.mcst:easyfk-thread')
    
    // 队列模块
    // api('com.mcst:queue-disruptor')
}

test {
    enabled(true)
}
```

#### 2.3.2 聚合项目配置

**根目录 build.gradle** 文件：

```gradle
// 所有项目通用配置
allprojects {
    // 指定项目版本号和group
    version = '1.0.0'
    group = 'com.yourcompany'

    apply plugin: 'java-library'
    apply plugin: 'maven-publish'
    
    java {
        sourceCompatibility = JavaVersion.VERSION_21
        targetCompatibility = JavaVersion.VERSION_21
        withSourcesJar()
    }

    [compileJava, compileTestJava]*.options*.encoding = 'UTF-8'
}

// 子项目通用配置
subprojects {
    dependencies {
        implementation platform(libs.dependencies)
        compileOnly libs.lombok
        testCompileOnly libs.lombok
        annotationProcessor(libs.lombok, libs.processor)
        testAnnotationProcessor(libs.lombok, libs.processor)
    }
}
```

**settings.gradle** 文件：

```gradle
rootProject.name = 'your-parent-project'

dependencyResolutionManagement.versionCatalogs {
    libs {
        library("dependencies", "com.mcst:easyfk-dependencies:3.5.16")
        library('lombok', 'org.projectlombok:lombok:1.18.46')
        library('processor', 'org.springframework.boot:spring-boot-configuration-processor:3.5.16')
    }
}

// 包含子模块
include 'your-module-1'
include 'your-module-2'
```

---

## 3. 核心模块详解

### 3.1 easyfk-core

**核心基础模块**，提供框架的基础抽象和工具类，无外部依赖。

#### 3.1.1 主要组件

**DTO 基类：**
- `BaseDto`：所有数据传输对象的基类，自动管理 `insertTime` 和 `lastUpdateTime`
- `BaseResult`：统一响应结果封装
- `ResponseResult<T>`：泛型响应结果
- `PageResult<T>`：分页结果
- `SearchRequest`：查询请求
- `ModifyRequest`：修改请求

**上下文管理（ThreadLocal）：**
- `TraceIdContext`：链路追踪 ID 管理
- `RequestHeaderContext`：请求头上下文
- `UserDataContext`：用户数据上下文

**请求对象：**
- `RequestHeaders`：请求头信息
- `UserData`：用户数据
- `LoginUser`：登录用户信息
- `UserAuth`：用户权限信息

**注解：**
- `@PrimaryKey`：主键标识
- `@SingleUniqueField`：单字段唯一性
- `@CombUniqueField`：组合字段唯一性
- `@DataFilterField`：数据过滤字段
- `@BetweenField`：范围查询字段
- `@SignField`：签名字段

**响应构建器（流式 API）：**
- `PRBuilder`：分页响应构建器
- `BRBuilder`：基础响应构建器
- `MRPBuilder`：修改响应构建器
- `SRPBuilder`：搜索响应构建器

**工具类：**
- `StringUtil`：字符串工具
- `EmptyUtil`：空值判断
- `SplitUtil`：字符串分割
- `TransformUtil`：类型转换
- `ReflectUtil`：反射工具
- `I18NUtil`：国际化工具
- `ExpressionUtil`：表达式工具

#### 3.1.2 使用示例

**定义 DTO：**

```java
import com.mcst.easyfk.core.dto.BaseDto;
import com.mcst.easyfk.core.annotation.PrimaryKey;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
public class UserDto extends BaseDto {
    
    @PrimaryKey
    private Long id;
    
    private String username;
    
    private String email;
    
    private Integer status;
    
    // insertTime 和 lastUpdateTime 由 BaseDto 自动管理
}
```

**构建响应结果：**

```java
import com.mcst.easyfk.core.dto.response.ResponseResult;
import com.mcst.easyfk.core.builder.BRBuilder;

@Service
public class UserService {
    
    public ResponseResult<UserDto> getUser(Long id) {
        UserDto user = userRepository.findById(id);
        
        if (user == null) {
            return BRBuilder.<UserDto>builder()
                .fail("用户不存在")
                .build();
        }
        
        return BRBuilder.<UserDto>builder()
            .success(user)
            .build();
    }
}
```

**使用上下文：**

```java
import com.mcst.easyfk.core.context.TraceIdContext;
import com.mcst.easyfk.core.context.UserDataContext;

@Service
public class OrderService {
    
    public void createOrder() {
        // 获取 TraceId
        String traceId = TraceIdContext.getTraceId();
        
        // 获取当前用户信息
        UserData userData = UserDataContext.getUserData();
        
        log.info("TraceId: {}, User: {}", traceId, userData.getUserId());
    }
}
```

### 3.2 easyfk-repository

**数据访问层模块**，提供统一的数据库访问抽象。

#### 3.2.1 主要组件

**核心接口：**
- `IBaseRepository<T, PK>`：泛型 Repository 接口

**查询构建：**
- `SearchCondition`：查询条件
- `RangeCondition`：范围条件
- `SCBuilder`：查询条件构建器（流式 API）

**注解：**
- `@AutoUpdateTime`：自动更新时间
- `@DefaultValueOnSave`：保存时设置默认值

**工具类：**
- `ConditionUtil`：条件工具
- `RepositoryUtil`：Repository 工具
- `SelectFieldUtil`：字段选择工具
- `ModelSetFieldDefaultValueUtil`：模型字段默认值工具

#### 3.2.2 使用示例

**定义 Repository：**

```java
import com.mcst.easyfk.repository.IBaseRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserRepository extends IBaseRepository<UserEntity, Long> {
    // 继承基础的 CRUD 方法，可添加自定义方法
}
```

**使用查询构建器：**

```java
import com.mcst.easyfk.repository.builder.SCBuilder;
import com.mcst.easyfk.repository.condition.SearchCondition;
import com.mcst.easyfk.repository.enums.RangeConditionType;

@Service
public class UserService {
    
    @Resource
    private UserRepository userRepository;
    
    public List<UserEntity> searchUsers(String keyword, Integer status, 
                                       LocalDateTime startTime, LocalDateTime endTime) {
        // 构建查询条件
        SearchCondition condition = SCBuilder.builder()
            .addLikeCondition("username", keyword)
            .addEqCondition("status", status)
            .addRangeCondition("createTime", 
                RangeConditionType.BETWEEN, 
                startTime, 
                endTime)
            .setPageNo(1)
            .setPageSize(10)
            .setOrderBy("createTime DESC")
            .build();
        
        return userRepository.queryBySc(condition);
    }
}
```

**分页查询：**

```java
import com.mcst.easyfk.core.dto.response.PageResult;

@Service
public class UserService {
    
    @Resource
    private UserRepository userRepository;
    
    public PageResult<UserEntity> queryUsersPage(int pageNo, int pageSize) {
        SearchCondition condition = SCBuilder.builder()
            .setPageNo(pageNo)
            .setPageSize(pageSize)
            .build();
        
        PageResult<UserEntity> pageResult = userRepository.queryPageBySc(condition);
        return pageResult;
    }
}
```

### 3.3 easyfk-service

**业务逻辑层模块**，提供服务层抽象和基础实现。

#### 3.3.1 模块结构

**service-api（接口定义）：**
- `IBaseService<T, PK, R>`：核心服务接口
- `IBaseApi<T, PK, R>`：API 服务接口（扩展 IBaseService）
- `IBaseFluxService`：响应式服务接口
- `IBaseFluxApi`：响应式 API 服务接口

**service-base（实现）：**
- `BaseApiServiceImpl`：基础实现类
- `SearchRequestUtil`：搜索请求工具
- `ServiceUtil`：服务工具
- `UserDataFiltrationUtil`：用户数据过滤工具

#### 3.3.2 使用示例

**定义服务接口：**

```java
import com.mcst.easyfk.service.api.IBaseApi;

public interface IUserService extends IBaseApi<UserDto, Long, UserResp> {
    // 继承基础方法，添加自定义方法
    ResponseResult<UserDto> getUserByUsername(String username);
}
```

**实现服务：**

```java
import com.mcst.easyfk.service.base.BaseApiServiceImpl;
import org.springframework.stereotype.Service;

@Service
public class UserServiceImpl 
    extends BaseApiServiceImpl<UserDto, Long, UserResp> 
    implements IUserService {
    
    @Resource
    private UserRepository userRepository;
    
    @Override
    public ResponseResult<UserDto> getUserByUsername(String username) {
        UserEntity entity = userRepository.findByUsername(username);
        
        if (entity == null) {
            return BRBuilder.<UserDto>builder()
                .fail("用户不存在")
                .build();
        }
        
        UserDto dto = TransformUtil.transform(entity, UserDto.class);
        
        return BRBuilder.<UserDto>builder()
            .success(dto)
            .build();
    }
}
```

### 3.4 easyfk-web

**Web 层模块**，提供 HTTP/REST 基础设施。

#### 3.4.1 子模块

- **web-base**：JWT 认证（`JwtManager`）、上下文管理
- **web-common**：CORS、拦截器、安全、异常处理
- **web-micro**：微服务专用配置和异常处理
- **web-prd**：生产环境配置
- **web-simple**：简化配置变体

#### 3.4.2 关键组件

- `JwtProperties`：JWT 配置
- `CorsProperties`：跨域配置
- `InterceptProperties`：拦截器配置
- `SecurityProperties`：安全配置
- `ApiAuthProperties`：API 调用鉴权配置（OpenAPI 风格）
- `ApiAuthFilter`：API 调用鉴权过滤器（最高层，最先执行）
- `ApiSignUtil`：API 调用鉴权签名工具（HMAC-SHA256）
- `IApiClientStore`：API 调用方存储接口（可自定义实现）
- `CheckIgnoreSecurityUriUtil`：安全忽略 URI 工具
- `InterceptorExcludeUriUtil`：拦截器排除 URI 工具

#### 3.4.3 配置示例

**application.yml 配置：**

```yaml
easyfk:
  config:
    web:
      # JWT 配置
      jwt:
        secret: "your-strong-secret"       # 签名密钥（默认提供框架密钥，生产必须覆盖）
        salt: "your-strong-salt"           # 签名盐值，与 secret 共同派生签名密钥（生产必须覆盖）
        expires-second: 10800              # Token 有效期（秒），默认 3 小时
        allowed-algorithms: HS256          # 签名算法白名单，防 alg=none 攻击
      
      # CORS 配置
      cors:
        open: true
        cors-domain: "https://yourdomain.com"   # 逗号分隔多个域名
        allowed-method: "GET,POST,PUT,DELETE"
        allowed-header: "*"
        allow-credentials: true
      
      # 安全配置
      security:
        open: true
        sign-key: "your-sign-key"
        sign-version: v1                  # v1=MD5 兼容存量；v2=HMAC-SHA256 推荐升级
        timeout: 150s
        ignore-uri:
          - /public/**
          - /health
          - /actuator/**
      
      # API 调用鉴权（OpenAPI 风格，默认关闭）
      api-auth:
        open: false
        timeout: 150s
        ignore-uri:
          - /health
        clients:
          - app-id: partner-app
            secret: "partner-secret-xxxx"
            allowed-uris:
              - /order/**
```

**控制器示例：**

```java
import org.springframework.web.bind.annotation.*;
import com.mcst.easyfk.core.dto.response.ResponseResult;

@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @Resource
    private IUserService userService;
    
    @GetMapping("/{id}")
    public ResponseResult<UserDto> getUser(@PathVariable Long id) {
        return userService.getById(id);
    }
    
    @PostMapping
    public ResponseResult<UserDto> createUser(@RequestBody UserDto userDto) {
        return userService.save(userDto);
    }
    
    @PutMapping("/{id}")
    public ResponseResult<UserDto> updateUser(@PathVariable Long id, 
                                              @RequestBody UserDto userDto) {
        userDto.setId(id);
        return userService.update(userDto);
    }
    
    @DeleteMapping("/{id}")
    public ResponseResult<Void> deleteUser(@PathVariable Long id) {
        return userService.deleteById(id);
    }
}
```

#### 3.4.4 Web 安全增强（2026-08）

`easyfk-web` 在 JWT、接口防重放、重复提交、幂等与 SQL 注入方面内置了安全能力（主要位于 `web-prd` 与 `web-base`），用法如下。

**JWT 安全配置（web-base）：**

```yaml
easyfk:
  config:
    web:
      jwt:
        secret: "your-strong-secret"       # 签名密钥（默认提供框架密钥，生产必须覆盖）
        salt: "your-strong-salt"           # 签名盐值，与 secret 共同派生签名密钥（生产必须覆盖）
        expires-second: 10800              # Token 有效期（秒），默认 3 小时
        allowed-algorithms: HS256         # 算法白名单，防止 alg=none 算法混淆攻击
```

- `JwtManager` 现在强制验签 + 校验过期；伪造/篡改/过期 Token 均被拒绝
- 未更换密钥的项目存量 Token 仍有效；更换密钥后需重新登录

**签名防重放（web-prd）：**

```yaml
easyfk:
  config:
    web:
      security:
        open: true                        # 开启签名 + 防重放
        sign-key: "your-sign-key"         # 验签密钥
        sign-version: v1                  # v1=MD5 兼容存量；v2=HMAC-SHA256 推荐升级
        timeout: 150s                     # 时间戳新鲜度窗口 + Nonce 防重放 TTL
        ignore-uri:
          - /health
```

- Nonce 占用为原子操作（Redis `SET NX EX`），并发相同 Nonce 仅一个放行，重复返回 `API_AGAIN`
- v2 签名绑定 Method/URI/请求体摘要，可防参数篡改；默认 v1 不影响存量客户端
- `Timestamp` 头为**可选**：客户端不传则不校验新鲜度（签名原文按空串），兼容客户端时钟偏差；传入则校验格式与新鲜度，超窗返回 `EXPIRED`

**默认鉴权（web-prd）：**

```yaml
easyfk:
  config:
    web:
      intercept:
        auth-type: 1                    # 0=只检测登录；1=检测登录并校验权限
        require-auth-by-default: true   # 未标注注解的接口默认要求登录（防止漏标裸奔）
```

- `@AuthResource` 支持标注在方法或类上，类级对整个控制器生效，无权限返回 `UN_AUTH`

**接口调用鉴权（OpenAPI 风格，web-prd）：**

安全级调用方认证，与 BMS 用户权限解耦——调用方凭 `App-Id + Secret` 签名访问接口，开启后所有接口默认要求调用方鉴权：

```yaml
easyfk:
  config:
    web:
      api-auth:
        open: true
        timeout: 150s
        ignore-uri: [/health]
        clients:
          - app-id: partner-app
            secret: "partner-secret-xxxx"
            allowed-uris: [/order/**]     # 为空表示全部
```

```java
// 客户端签名（服务端 ApiSignUtil 验证）
String sign = ApiSignUtil.sign(appId, timestamp, nonce,
        "POST", "/order/create", bodyHash, secret);
// 请求头：App-Id / Api-Nonce / Api-Timestamp / Api-Body / Api-Sign
```

错误码：`API_CLIENT_MISSING`、`API_CLIENT_INVALID`、`API_CLIENT_DISABLED`、`API_SIGN_ERROR`、`API_UNAUTHORIZED`、`API_AGAIN` 等。详见 [web-prd 开发文档](easyfk-web/web-prd/web-prd开发手册.md) 第 20 章。

**表单重复提交（web-prd）：**

```java
// 1. 下发一次性令牌
String token = RequestTokenUtil.issue(cacheService, userId, 300);

// 2. 提交接口标注注解（请求携带 Request-Token 头）
@PostMapping("/order/submit")
@RequestToken(verify = true, ttlSeconds = 300)
public ResponseResult<?> submit(@RequestBody OrderSubmitVO vo) { ... }
```

重复提交返回 `REQUEST_AGAIN`。

**接口幂等（web-prd）：**

```java
@PostMapping("/payment/create")
@Idempotent(key = "#args[0].orderNo", ttlSeconds = 60, onDuplicateFail = true)
public ResponseResult<?> createPayment(@RequestBody PaymentCreateVO param) { ... }
```

同幂等键在窗口内只执行一次，重复请求返回 `IDEMPOTENT_ERROR`；业务异常自动释放幂等键允许重试。幂等键支持 SpEL 并自动带用户维度。

**SQL 注入防范：**

- 入口：`ControllerAspect` 对 `SearchRequest` 字段名/关键词做白名单校验，非法返回参数错误
- 构建：`ConditionUtil` 模糊/关键词条件全部参数化，不再拼接 SQL
- 兜底：ORM 层对排序/分组/select 列名校验，`customConditionSql` 拒绝分号/注释/DDL/DML

详细说明、客户端签名示例与完整配置见 [web-prd 开发文档](easyfk-web/web-prd/web-prd开发手册.md) 第 7/15~19 章。

### 3.5 easyfk-authority

**权限管理模块**，提供基于注解的 RBAC 权限控制。

#### 3.5.1 主要组件

**资源管理：**
- `IAuthResourceApi`：权限资源 API
- `AuthResourceDto`：权限资源 DTO
- `AuthResourceReq`：权限资源请求
- `AuthResourceResp`：权限资源响应

**用户授权：**
- `UserAuth`：用户权限信息
- `UserAuthResources`：用户授权资源
- `UserDataManager`：用户数据管理器

**注解：**
- `@ResourceController`：资源控制器标识
- `@LoginResource`：登录资源标识
- `@AuthResource`：权限资源标识

#### 3.5.2 使用示例

**定义权限控制器：**

```java
import com.mcst.easyfk.authority.annotation.ResourceController;
import com.mcst.easyfk.authority.annotation.AuthResource;
import com.mcst.easyfk.authority.annotation.LoginResource;

@RestController
@RequestMapping("/api/orders")
@ResourceController(name = "订单管理")
public class OrderController {
    
    @GetMapping("/{id}")
    @LoginResource
    public ResponseResult<OrderDto> getOrder(@PathVariable Long id) {
        return orderService.getById(id);
    }
    
    @PostMapping
    @AuthResource(id = "order:create", name = "创建订单", actionCode = "order:create")
    public ResponseResult<OrderDto> createOrder(@RequestBody OrderDto orderDto) {
        return orderService.save(orderDto);
    }
    
    @DeleteMapping("/{id}")
    @AuthResource(id = "order:delete", name = "删除订单", actionCode = "order:delete",
            unPassMsg = "需要管理员权限")
    public ResponseResult<Void> deleteOrder(@PathVariable Long id) {
        return orderService.deleteById(id);
    }
}
```

### 3.6 easyfk-cache

**缓存抽象模块**，提供统一的缓存接口。

#### 3.6.1 主要组件

- `ICacheService`：缓存服务接口
- 支持命名空间隔离
- 支持 TTL（过期时间）

#### 3.6.2 使用示例

```java
import com.mcst.easyfk.cache.ICacheService;

@Service
public class ProductService {
    
    @Resource
    private ICacheService cacheService;
    
    private static final String NAMESPACE = "product";
    
    public ProductDto getProduct(Long id) {
        String key = "product:" + id;
        
        // 尝试从缓存获取
        ProductDto cached = cacheService.getObject(NAMESPACE, key, ProductDto.class);
        if (cached != null) {
            return cached;
        }
        
        // 从数据库查询
        ProductDto product = productRepository.findById(id);
        
        // 写入缓存，60秒过期
        cacheService.cacheObject(NAMESPACE, key, product, 60L);
        
        return product;
    }
}
```

### 3.7 easyfk-log

**日志模块**，提供可插拔的日志实现。

#### 3.7.1 子模块

- **log-logback**：基于 Logback 的实现
- **log-log4j2**：基于 Log4j2 的实现

#### 3.7.2 使用方式

**添加依赖（Maven）：**

```xml
<!-- 选择 Logback -->
<dependency>
    <groupId>com.mcst</groupId>
    <artifactId>log-logback</artifactId>
</dependency>

<!-- 或选择 Log4j2 -->
<!-- <dependency>
    <groupId>com.mcst</groupId>
    <artifactId>log-log4j2</artifactId>
</dependency> -->
```

**使用 SLF4J API：**

```java
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class OrderService {
    
    public void processOrder(Long orderId) {
        log.info("开始处理订单: {}", orderId);
        
        try {
            // 业务逻辑
            log.debug("订单详情: {}", orderDetails);
        } catch (Exception e) {
            log.error("处理订单失败: {}", orderId, e);
        }
    }
}
```

### 3.8 easyfk-queue

**高性能异步队列模块**，基于 LMAX Disruptor 实现。

#### 3.8.1 主要特性

- 超低延迟（纳秒级）
- 支持多生产者模式
- 多种等待策略
- 工作窃取与基于哈希的分片
- 优雅关闭

#### 3.8.2 使用示例

**1. 定义处理器：**

```java
import com.mcst.easyfk.queue.disruptor.api.Processor;
import org.springframework.stereotype.Component;

@Component("auditQueue")
public class AuditProcessor implements Processor<AuditEvent> {
    
    @Override
    public void process(AuditEvent event) throws Exception {
        // 处理审计事件（必须线程安全）
        log.info("审计事件: 用户={}, 操作={}", 
                 event.getUserId(), event.getAction());
        
        // 持久化到数据库
        auditRepository.save(event);
    }
}
```

**2. 配置队列（application.yml）：**

```yaml
easyfk:
  config:
    queue:
      disruptor:
        bufferSize: 65536         # RingBuffer 大小（2的幂）
        workers: 4                # 每队列工作线程数（消费线程总数 = 队列数 × 本值）
        producerType: MULTI       # SINGLE | MULTI，默认 MULTI
                                  # SINGLE 仅在确证单一投递线程时可用，否则会静默丢事件
        waitStrategy: BLOCKING    # BLOCKING | YIELDING | BUSY_SPIN
        
        queues:
          auditQueue:
            bufferSize: 32768
            workers: 3
            producerType: MULTI
            waitStrategy: YIELDING
            thread:
              namePrefix: "audit-"
              daemon: true
              priority: 5
```

**3. 发送事件：**

```java
import com.mcst.easyfk.queue.disruptor.core.IngestQueueManager;

@Service
public class UserService {
    
    @Resource
    private IngestQueueManager queueManager;
    
    public void updateUser(UserDto user) {
        // 更新用户
        userRepository.update(user);
        
        // 异步记录审计日志
        AuditEvent event = new AuditEvent(user.getId(), "UPDATE_USER");
        queueManager.send("auditQueue", event);
    }
}
```

### 3.9 easyfk-thread

**线程池管理模块**，提供增强的线程池功能。

#### 3.9.1 主要特性

- TraceId/MDC 自动透传
- 实时监控与统计
- 动态调优（自动扩缩容）
- 异步监控模式
- I/O 密集型和 CPU 密集型线程池
- 可配置的拒绝策略
- 重试机制

#### 3.9.2 配置示例

**application.yml 配置：**

```yaml
easyfk:
  config:
    thread:
      pool:
        # 通用线程池配置
        common-pool-args:
          core-pool-size: 4
          max-pool-size: 8
          queue-capacity: 200
          keep-alive-seconds: 60
          thread-name-prefix: common-thread-
          rejected-execution-handler: CALLER_RUNS  # ABORT/CALLER_RUNS/DISCARD/DISCARD_OLDEST
        
        # I/O密集型线程池
        create-io-intensive-pool: true
        io-intensive-pool-args:
          core-pool-size: 16         # CPU核心数 × 2
          max-pool-size: 32          # CPU核心数 × 4
          queue-capacity: 200
          keep-alive-seconds: 120
          rejected-execution-handler: CALLER_RUNS
        
        # CPU密集型线程池
        create-cpu-intensive-pool: true
        cpu-intensive-pool-args:
          core-pool-size: 9          # CPU核心数 + 1
          max-pool-size: 9
          queue-capacity: 50
          keep-alive-seconds: 60
          rejected-execution-handler: ABORT
        
        # 监控与动态调优
        monitor:
          enabled: true
          auto-discovery: true
          auto-start: true
          default-config:
            enabled: true
            async-monitoring-enabled: true
            monitoring-interval: PT30S
            cooldown-period: PT2M
            min-core-pool-size: 2
            max-core-pool-size: 20
            scale-up-step: 2
            scale-down-step: 1
            high-load-threshold: 80.0
            low-load-threshold: 30.0
```

#### 3.9.3 使用示例

**1. 使用通用线程池：**

```java
import com.mcst.easyfk.thread.CustomTaskExecutor;

@Service
public class OrderService {
    
    @Resource(name = "commonTaskExecutor")
    private CustomTaskExecutor executor;
    
    public void processOrderAsync(Long orderId) {
        executor.execute(() -> {
            // TraceId 自动透传
            processOrder(orderId);
        });
    }
}
```

**2. 使用 I/O 密集型线程池：**

```java
@Service
public class DataService {
    
    @Resource(name = "ioIntensiveTaskExecutor")
    private CustomTaskExecutor ioExecutor;
    
    // 批量查询数据库
    public List<User> batchQueryUsers(List<Long> userIds) {
        List<CompletableFuture<User>> futures = userIds.stream()
            .map(id -> CompletableFuture.supplyAsync(() -> {
                return userRepository.findById(id);
            }, ioExecutor))
            .toList();
        
        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
        return futures.stream().map(CompletableFuture::join).toList();
    }
}
```

**3. 使用 CPU 密集型线程池：**

```java
@Service
public class ImageService {
    
    @Resource(name = "cpuIntensiveTaskExecutor")
    private CustomTaskExecutor cpuExecutor;
    
    // 批量图像处理
    public void processBatchImages(List<byte[]> images) {
        images.forEach(imageData -> 
            cpuExecutor.execute(() -> {
                byte[] processed = imageProcessor.resize(imageData, 800, 600);
                imageStorage.save(processed);
            })
        );
    }
}
```

**4. 使用重试机制：**

```java
import com.mcst.easyfk.thread.retry.RetryExecutor;
import com.mcst.easyfk.thread.retry.RetryConfig;
import com.mcst.easyfk.thread.retry.BackoffStrategy;

@Service
public class PaymentService {
    
    @Resource
    private RetryExecutor retryExecutor;
    
    // 同步重试
    public void processPayment(Order order) {
        RetryConfig config = RetryConfig.builder()
            .maxRetries(3)
            .baseDelayMs(500)
            .backoffStrategy(BackoffStrategy.LINEAR)
            .build();
        
        try {
            retryExecutor.execute(config, () -> {
                paymentClient.pay(order);
                return null;
            });
        } catch (Exception e) {
            log.error("支付失败", e);
        }
    }
    
    // 异步重试
    public void sendNotificationAsync(String userId, String message) {
        RetryConfig config = RetryConfig.builder()
            .maxRetries(5)
            .baseDelayMs(1000)
            .backoffStrategy(BackoffStrategy.EXPONENTIAL)
            .build();
        
        retryExecutor.executeAsync(config, 
            () -> {
                notificationClient.send(userId, message);
                return null;
            },
            new RetryCallback<Void>() {
                @Override
                public void onSuccess(Void result, int attempt) {
                    log.info("通知发送成功，尝试次数: {}", attempt);
                }
                
                @Override
                public void onFinalFailure(Exception e, int totalAttempts) {
                    log.error("通知发送最终失败，总尝试: {}", totalAttempts, e);
                }
            }
        );
    }
}
```

### 3.10 easyfk-remote

**服务间通信模块**，支持多种 RPC 方式。

#### 3.10.1 子模块

- **remote-dubbo**：基于 Dubbo 的二进制 RPC
- **remote-cloud**：基于 HTTP 的 RPC（Spring Cloud）

#### 3.10.2 主要接口

- `IBaseRemote<T, PK, R>`：同步远程调用接口
- `IBaseFluxRemote`：异步远程调用接口

#### 3.10.3 使用示例

**定义远程服务接口：**

```java
import com.mcst.easyfk.remote.IBaseRemote;

public interface IUserRemoteService extends IBaseRemote<UserDto, Long, UserResp> {
    ResponseResult<UserDto> getUserByUsername(String username);
}
```

**Dubbo 实现：**

```java
import com.mcst.easyfk.remote.dubbo.DubboBaseRemoteImpl;
import org.apache.dubbo.config.annotation.DubboService;

@DubboService
public class UserRemoteServiceImpl 
    extends DubboBaseRemoteImpl<UserDto, Long, UserResp> 
    implements IUserRemoteService {
    
    @Resource
    private IUserService userService;
    
    @Override
    public ResponseResult<UserDto> getUserByUsername(String username) {
        return userService.getUserByUsername(username);
    }
}
```

**消费端：**

```java
import org.apache.dubbo.config.annotation.DubboReference;

@Service
public class OrderService {
    
    @DubboReference
    private IUserRemoteService userRemoteService;
    
    public void createOrder(OrderDto order) {
        // 远程调用用户服务
        ResponseResult<UserDto> userResult = 
            userRemoteService.getUserByUsername(order.getUsername());
        
        if (userResult.isSuccess()) {
            UserDto user = userResult.getData();
            // 处理订单逻辑
        }
    }
}
```

### 3.11 easyfk-gateway

**API 网关过滤模块**，提供网关层的请求/响应过滤。

#### 3.11.1 主要组件

- `ICustomGatewayFilter`：自定义网关过滤器接口
- `IExtendGatewayFilter`：扩展网关过滤器接口
- `RequestGatewayFilter`：请求网关过滤器
- `GatewayFilterConfigure`：网关过滤器配置
- `FailRequestUtil`：失败请求工具

#### 3.11.2 使用示例

```java
import com.mcst.easyfk.gateway.ICustomGatewayFilter;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

@Component
public class CustomAuthFilter implements ICustomGatewayFilter {
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        // 自定义认证逻辑
        String token = exchange.getRequest().getHeaders().getFirst("Authorization");
        
        if (token == null || !isValidToken(token)) {
            return FailRequestUtil.fail(exchange, 401, "未授权");
        }
        
        return chain.filter(exchange);
    }
    
    @Override
    public int getOrder() {
        return 100;  // 过滤器优先级
    }
    
    private boolean isValidToken(String token) {
        // Token 验证逻辑
        return true;
    }
}
```

### 3.12 easyfk-ws

**WebSocket 实时通信模块**，提供完整的 WebSocket 支持。

#### 3.12.1 主要特性

- 连接管理（认证、会话、多设备）
- 订阅机制（频道 + 产品）
- 消息推送（单用户、批量、广播）
- 心跳检测
- 策略模式扩展

#### 3.12.2 配置示例

**application.yml 配置：**

```yaml
easyfk:
  config:
    ws:
      # WebSocket 基础配置
      path: /ws
      must-login: false
      sub-save-type: local       # local | distributed
      allow-cross-origin: true
      enable-sock-js: true
      session-timeout-seconds: 1800
      heartbeat-interval-seconds: 30
      max-subscriptions-per-user: 100
      message-buffer-size: 8192
      
      # 跨域来源白名单（allow-cross-origin=true 时生效）
      allowed-origins:
        - "https://yourdomain.com"
      
      # 性能配置
      performance:
        batch-threshold: 100
        core-pool-size: 10
        max-pool-size: 50
        queue-capacity: 1000
        keep-alive-seconds: 60
```

#### 3.12.3 使用示例

**1. 实现事件处理器：**

```java
import com.mcst.easyfk.ws.server.handler.EventHandler;
import com.mcst.easyfk.ws.param.WsUserOptParam;
import com.mcst.easyfk.core.dto.response.BaseResult;

@Component
public class MyEventHandler implements EventHandler {
    
    @Override
    public BaseResult<?> handleUserEvent(WsUserOptParam param) {
        String eventType = param.getEventType();
        String userSessionId = param.getUserSessionId();
        Map<String, Object> eventData = param.getEventData();
        
        log.info("处理事件: 用户={}, 类型={}", userSessionId, eventType);
        
        switch (eventType) {
            case "subscribe":
                return handleSubscribe(param);
            case "unsubscribe":
                return handleUnsubscribe(param);
            default:
                return BaseResult.success();
        }
    }
    
    @Override
    public void clearUserSubscriptions(String userSessionId) {
        log.info("清理用户订阅: {}", userSessionId);
    }
    
    private BaseResult<?> handleSubscribe(WsUserOptParam param) {
        // 订阅逻辑
        return BaseResult.success("订阅成功");
    }
    
    private BaseResult<?> handleUnsubscribe(WsUserOptParam param) {
        // 取消订阅逻辑
        return BaseResult.success("取消订阅成功");
    }
}
```

**2. 推送消息：**

```java
import com.mcst.easyfk.ws.api.IPushWsMsgApi;
import com.mcst.easyfk.ws.param.PushWsMessageParam;

@Service
public class NotificationService {
    
    @Resource
    private IPushWsMsgApi pushWsMsgApi;
    
    // 推送给指定用户
    public void notifyUser(Long userId, String message) {
        PushWsMessageParam param = new PushWsMessageParam();
        param.setUserSessionId(userId.toString());
        param.setChannel("notification");
        param.setData(Map.of("message", message));
        
        pushWsMsgApi.pushMessage(param);
    }
    
    // 推送给订阅用户
    public void notifySubscribers(String channel, String category, Map<String, Object> data) {
        PushWsMessageParam param = new PushWsMessageParam();
        param.setChannel(channel);
        param.setCategory(category);
        param.setData(data);
        
        pushWsMsgApi.pushMessage(param);
    }
}
```

**3. 订阅管理：**

```java
import com.mcst.easyfk.ws.server.manager.LocalSubManager;

@Service
public class SubscriptionService {
    
    @Resource
    private LocalSubManager localSubManager;
    
    // 订阅
    public void subscribe(String userSessionId, String channel, String category) {
        boolean success = localSubManager.subscribe(channel, category, userSessionId);
        if (success) {
            log.info("订阅成功: {}:{}:{}", userSessionId, channel, category);
        }
    }
    
    // 获取订阅者
    public Set<String> getSubscribers(String channel, String category) {
        return localSubManager.getSubscribers(channel, category);
    }
}
```

---

## 4. 开发指南

### 4.1 创建标准业务服务

以创建用户管理服务为例，展示完整的开发流程。

#### 4.1.1 定义实体类

```java
import com.mcst.easyfk.core.dto.BaseDto;
import com.mcst.easyfk.core.annotation.PrimaryKey;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
public class UserDto extends BaseDto {
    
    @PrimaryKey
    private Long id;
    
    private String username;
    
    private String email;
    
    private String phone;
    
    private Integer status;  // 0-禁用, 1-启用
    
    private String avatar;
}
```

#### 4.1.2 定义 Repository

```java
import com.mcst.easyfk.repository.IBaseRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserRepository extends IBaseRepository<UserEntity, Long> {
    
    UserEntity findByUsername(String username);
    
    UserEntity findByEmail(String email);
}
```

#### 4.1.3 定义服务接口

```java
import com.mcst.easyfk.service.api.IBaseApi;
import com.mcst.easyfk.core.dto.response.ResponseResult;

public interface IUserService extends IBaseApi<UserDto, Long, UserResp> {
    
    /**
     * 根据用户名查询用户
     */
    ResponseResult<UserDto> getUserByUsername(String username);
    
    /**
     * 注册新用户
     */
    ResponseResult<UserDto> register(UserDto userDto);
    
    /**
     * 更新用户状态
     */
    ResponseResult<Void> updateStatus(Long userId, Integer status);
}
```

#### 4.1.4 实现服务

```java
import com.mcst.easyfk.service.base.BaseApiServiceImpl;
import com.mcst.easyfk.core.builder.BRBuilder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class UserServiceImpl 
    extends BaseApiServiceImpl<UserDto, Long, UserResp> 
    implements IUserService {
    
    @Resource
    private UserRepository userRepository;
    
    @Override
    public ResponseResult<UserDto> getUserByUsername(String username) {
        if (StringUtil.isEmpty(username)) {
            return BRBuilder.<UserDto>builder()
                .fail("用户名不能为空")
                .build();
        }
        
        UserEntity entity = userRepository.findByUsername(username);
        if (entity == null) {
            return BRBuilder.<UserDto>builder()
                .fail("用户不存在")
                .build();
        }
        
        UserDto dto = TransformUtil.transform(entity, UserDto.class);
        return BRBuilder.<UserDto>builder()
            .success(dto)
            .build();
    }
    
    @Override
    @Transactional(rollbackFor = Exception.class)
    public ResponseResult<UserDto> register(UserDto userDto) {
        // 参数校验
        if (StringUtil.isEmpty(userDto.getUsername())) {
            return BRBuilder.<UserDto>builder()
                .fail("用户名不能为空")
                .build();
        }
        
        // 检查用户名是否已存在
        UserEntity existing = userRepository.findByUsername(userDto.getUsername());
        if (existing != null) {
            return BRBuilder.<UserDto>builder()
                .fail("用户名已存在")
                .build();
        }
        
        // 保存用户
        UserEntity entity = TransformUtil.transform(userDto, UserEntity.class);
        userRepository.save(entity);
        
        UserDto result = TransformUtil.transform(entity, UserDto.class);
        return BRBuilder.<UserDto>builder()
            .success(result)
            .build();
    }
    
    @Override
    @Transactional(rollbackFor = Exception.class)
    public ResponseResult<Void> updateStatus(Long userId, Integer status) {
        UserEntity entity = userRepository.findById(userId);
        if (entity == null) {
            return BRBuilder.<Void>builder()
                .fail("用户不存在")
                .build();
        }
        
        entity.setStatus(status);
        userRepository.update(entity);
        
        return BRBuilder.<Void>builder()
            .success()
            .build();
    }
}
```

#### 4.1.5 创建控制器

```java
import com.mcst.easyfk.authority.annotation.ResourceController;
import com.mcst.easyfk.authority.annotation.AuthResource;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
@ResourceController(name = "用户管理")
public class UserController {
    
    @Resource
    private IUserService userService;
    
    @GetMapping("/{id}")
    @AuthResource(name = "查询用户", code = "user:view")
    public ResponseResult<UserDto> getUser(@PathVariable Long id) {
        return userService.getById(id);
    }
    
    @GetMapping("/username/{username}")
    @AuthResource(name = "按用户名查询", code = "user:view")
    public ResponseResult<UserDto> getUserByUsername(@PathVariable String username) {
        return userService.getUserByUsername(username);
    }
    
    @PostMapping("/register")
    public ResponseResult<UserDto> register(@RequestBody UserDto userDto) {
        return userService.register(userDto);
    }
    
    @PostMapping
    @AuthResource(name = "创建用户", code = "user:create")
    public ResponseResult<UserDto> createUser(@RequestBody UserDto userDto) {
        return userService.save(userDto);
    }
    
    @PutMapping("/{id}")
    @AuthResource(name = "更新用户", code = "user:update")
    public ResponseResult<UserDto> updateUser(@PathVariable Long id, 
                                              @RequestBody UserDto userDto) {
        userDto.setId(id);
        return userService.update(userDto);
    }
    
    @PutMapping("/{id}/status")
    @AuthResource(name = "更新用户状态", code = "user:update")
    public ResponseResult<Void> updateStatus(@PathVariable Long id, 
                                             @RequestParam Integer status) {
        return userService.updateStatus(id, status);
    }
    
    @DeleteMapping("/{id}")
    @AuthResource(name = "删除用户", code = "user:delete")
    public ResponseResult<Void> deleteUser(@PathVariable Long id) {
        return userService.deleteById(id);
    }
}
```

### 4.2 数据查询与分页

#### 4.2.1 复杂查询

```java
@Service
public class OrderService {
    
    @Resource
    private OrderRepository orderRepository;
    
    public PageResult<OrderEntity> searchOrders(OrderSearchRequest request) {
        SearchCondition condition = SCBuilder.builder()
            // 等值查询
            .addEqCondition("status", request.getStatus())
            // 模糊查询
            .addLikeCondition("orderNo", request.getOrderNo())
            // IN 查询
            .addInCondition("userId", request.getUserIds())
            // 范围查询
            .addRangeCondition("createTime", 
                RangeConditionType.BETWEEN,
                request.getStartTime(),
                request.getEndTime())
            // 大于等于
            .addRangeCondition("totalAmount",
                RangeConditionType.GE,
                request.getMinAmount())
            // 分页
            .setPageNo(request.getPageNo())
            .setPageSize(request.getPageSize())
            // 排序
            .setOrderBy("createTime DESC, id DESC")
            .build();
        
        return orderRepository.queryPageBySc(condition);
    }
}
```

#### 4.2.2 动态查询条件

```java
public PageResult<ProductEntity> searchProducts(ProductSearchRequest request) {
    SCBuilder builder = SCBuilder.builder();
    
    // 动态添加条件
    if (StringUtil.isNotEmpty(request.getName())) {
        builder.addLikeCondition("name", request.getName());
    }
    
    if (request.getCategoryId() != null) {
        builder.addEqCondition("categoryId", request.getCategoryId());
    }
    
    if (request.getMinPrice() != null) {
        builder.addRangeCondition("price", 
            RangeConditionType.GE, 
            request.getMinPrice());
    }
    
    if (request.getMaxPrice() != null) {
        builder.addRangeCondition("price", 
            RangeConditionType.LE, 
            request.getMaxPrice());
    }
    
    SearchCondition condition = builder
        .setPageNo(request.getPageNo())
        .setPageSize(request.getPageSize())
        .setOrderBy("createTime DESC")
        .build();
    
    return productRepository.queryPageBySc(condition);
}
```

### 4.3 异步任务处理

#### 4.3.1 异步执行任务

```java
@Service
public class ReportService {
    
    @Resource(name = "ioIntensiveTaskExecutor")
    private CustomTaskExecutor ioExecutor;
    
    @Resource
    private IngestQueueManager queueManager;
    
    // 方式1：使用线程池
    public void generateReportAsync(Long reportId) {
        ioExecutor.execute(() -> {
            // 生成报表
            Report report = generateReport(reportId);
            // 保存到文件
            saveReportToFile(report);
        });
    }
    
    // 方式2：使用 Disruptor 队列
    public void generateReportByQueue(Long reportId) {
        ReportTask task = new ReportTask(reportId);
        queueManager.send("reportQueue", task);
    }
}
```

#### 4.3.2 批量异步处理

```java
@Service
public class BatchService {
    
    @Resource(name = "ioIntensiveTaskExecutor")
    private CustomTaskExecutor ioExecutor;
    
    // 批量处理，并行执行
    public void batchProcess(List<Long> ids) {
        List<CompletableFuture<Void>> futures = ids.stream()
            .map(id -> CompletableFuture.runAsync(() -> {
                processItem(id);
            }, ioExecutor))
            .toList();
        
        // 等待所有任务完成
        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
        
        log.info("批量处理完成，共 {} 条", ids.size());
    }
}
```

### 4.4 权限控制

#### 4.4.1 基于注解的权限控制

```java
import com.mcst.easyfk.authority.annotation.LoginResource;
import com.mcst.easyfk.authority.annotation.ResourceController;
import com.mcst.easyfk.authority.annotation.AuthResource;

@RestController
@RequestMapping("/api/admin/settings")
@ResourceController(name = "系统设置")
public class SettingsController {
    
    @GetMapping
    @LoginResource
    public ResponseResult<SettingsDto> getSettings() {
        return settingsService.getSettings();
    }
    
    @PutMapping
    @AuthResource(id = "settings:update", name = "修改设置", actionCode = "settings:update",
            unPassMsg = "需要管理员权限")
    public ResponseResult<Void> updateSettings(@RequestBody SettingsDto settings) {
        return settingsService.updateSettings(settings);
    }
}
```

#### 4.4.2 编程式权限检查

```java
@Service
public class OrderService {
    
    public ResponseResult<OrderDto> deleteOrder(Long orderId) {
        // 获取当前用户
        UserData userData = UserDataContext.getUserData();
        
        // 获取订单
        OrderEntity order = orderRepository.findById(orderId);
        if (order == null) {
            return BRBuilder.<OrderDto>builder()
                .fail("订单不存在")
                .build();
        }
        
        // 权限检查：只能删除自己的订单
        if (!order.getUserId().equals(userData.getUserId())) {
            return BRBuilder.<OrderDto>builder()
                .fail("无权删除该订单")
                .build();
        }
        
        orderRepository.deleteById(orderId);
        return BRBuilder.<OrderDto>builder()
            .success()
            .build();
    }
}
```

### 4.5 消息推送

#### 4.5.1 推送给指定用户

```java
@Service
public class NotificationService {
    
    @Resource
    private IPushWsMsgApi pushWsMsgApi;
    
    public void notifyUser(Long userId, String title, String content) {
        PushWsMessageParam param = new PushWsMessageParam();
        param.setUserSessionId(userId.toString());
        param.setChannel("notification");
        param.setData(Map.of(
            "title", title,
            "content", content,
            "timestamp", System.currentTimeMillis()
        ));
        
        pushWsMsgApi.pushMessage(param);
    }
}
```

#### 4.5.2 推送给订阅用户

```java
@Service
public class MarketService {
    
    @Resource
    private IPushWsMsgApi pushWsMsgApi;
    
    // 推送行情数据
    public void pushMarketData(String symbol, BigDecimal price) {
        PushWsMessageParam param = new PushWsMessageParam();
        param.setChannel("market");
        param.setCategory(symbol);
        param.setData(Map.of(
            "symbol", symbol,
            "price", price,
            "timestamp", System.currentTimeMillis()
        ));
        
        pushWsMsgApi.pushMessage(param);
    }
}
```

---

## 5. 配置参考

### 5.1 完整配置示例

```yaml
spring:
  application:
    name: your-application
  datasource:
    url: jdbc:mysql://localhost:3306/your_database?useUnicode=true&characterEncoding=utf8&useSSL=false
    username: root
    password: your_password
    driver-class-name: com.mysql.cj.jdbc.Driver

easyfk:
  config:
    # Web 配置
    web:
      jwt:
        secret: "your-strong-secret"       # 签名密钥（默认提供框架密钥，生产必须覆盖）
        salt: "your-strong-salt"           # 签名盐值，与 secret 共同派生签名密钥（生产必须覆盖）
        expires-second: 10800              # Token 有效期（秒），默认 3 小时
        allowed-algorithms: HS256          # 签名算法白名单，防 alg=none 攻击
      cors:
        open: true
        cors-domain: "https://yourdomain.com"   # 逗号分隔多个域名
        allowed-method: "GET,POST,PUT,DELETE,OPTIONS"
        allowed-header: "*"
        allow-credentials: true
      security:
        open: true
        sign-key: "your-sign-key"
        sign-version: v1                  # v1=MD5 兼容存量；v2=HMAC-SHA256 推荐升级
        timeout: 150s
        ignore-uri:
          - /public/**
          - /health
          - /actuator/**
      # API 调用鉴权（OpenAPI 风格，默认关闭）
      api-auth:
        open: false
        timeout: 150s
        ignore-uri:
          - /health
        clients:
          - app-id: partner-app
            secret: "partner-secret-xxxx"
            allowed-uris:
              - /order/**
    
    # 线程池配置
    thread:
      pool:
        common-pool-args:
          core-pool-size: 4
          max-pool-size: 8
          queue-capacity: 200
          rejected-execution-handler: CALLER_RUNS
        create-io-intensive-pool: true
        io-intensive-pool-args:
          core-pool-size: 16
          max-pool-size: 32
        create-cpu-intensive-pool: true
        cpu-intensive-pool-args:
          core-pool-size: 9
          max-pool-size: 9
        monitor:
          enabled: true
          auto-discovery: true
          auto-start: true
          default-config:
            enabled: true
            async-monitoring-enabled: true
            monitoring-interval: PT30S
    
    # 队列配置
    queue:
      disruptor:
        bufferSize: 65536
        workers: 4
        producerType: MULTI
        waitStrategy: BLOCKING
        queues:
          auditQueue:
            bufferSize: 32768
            workers: 3
    
    # WebSocket 配置
    ws:
      path: /ws
      must-login: false
      sub-save-type: local
      allow-cross-origin: true
      session-timeout-seconds: 1800
      heartbeat-interval-seconds: 30

logging:
  level:
    root: INFO
    com.mcst.easyfk: DEBUG
    com.yourcompany: DEBUG
```

---

## 6. 最佳实践

### 6.1 代码规范

1. **DTO 命名**：统一使用 `XxxDto` 后缀
2. **Service 接口**：使用 `IXxxService` 命名
3. **Service 实现**：使用 `XxxServiceImpl` 命名
4. **Controller 命名**：使用 `XxxController` 命名
5. **Repository 命名**：使用 `XxxRepository` 命名

### 6.2 异常处理

```java
@Service
public class UserService {
    
    public ResponseResult<UserDto> getUser(Long id) {
        try {
            UserEntity entity = userRepository.findById(id);
            if (entity == null) {
                return BRBuilder.<UserDto>builder()
                    .fail("用户不存在")
                    .build();
            }
            
            UserDto dto = TransformUtil.transform(entity, UserDto.class);
            return BRBuilder.<UserDto>builder()
                .success(dto)
                .build();
                
        } catch (Exception e) {
            log.error("查询用户失败: id={}", id, e);
            return BRBuilder.<UserDto>builder()
                .fail("系统错误，请稍后重试")
                .build();
        }
    }
}
```

### 6.3 事务管理

```java
@Service
public class OrderService {
    
    @Transactional(rollbackFor = Exception.class)
    public ResponseResult<OrderDto> createOrder(OrderDto orderDto) {
        // 1. 创建订单
        OrderEntity order = TransformUtil.transform(orderDto, OrderEntity.class);
        orderRepository.save(order);
        
        // 2. 扣减库存
        productService.deductStock(orderDto.getProductId(), orderDto.getQuantity());
        
        // 3. 创建支付记录
        paymentService.createPayment(order.getId(), orderDto.getTotalAmount());
        
        // 如果任何步骤失败，所有操作都会回滚
        
        OrderDto result = TransformUtil.transform(order, OrderDto.class);
        return BRBuilder.<OrderDto>builder()
            .success(result)
            .build();
    }
}
```

### 6.4 缓存使用

```java
@Service
public class ProductService {
    
    @Resource
    private ICacheService cacheService;
    
    private static final String CACHE_NAMESPACE = "product";
    private static final long CACHE_TTL = 300L; // 5分钟
    
    public ProductDto getProduct(Long id) {
        String key = "product:" + id;
        
        // 1. 尝试从缓存获取
        ProductDto cached = cacheService.getObject(
            CACHE_NAMESPACE, key, ProductDto.class);
        if (cached != null) {
            return cached;
        }
        
        // 2. 从数据库查询
        ProductEntity entity = productRepository.findById(id);
        if (entity == null) {
            return null;
        }
        
        ProductDto dto = TransformUtil.transform(entity, ProductDto.class);
        
        // 3. 写入缓存
        cacheService.cacheObject(CACHE_NAMESPACE, key, dto, CACHE_TTL);
        
        return dto;
    }
    
    // 更新后清除缓存
    @Transactional(rollbackFor = Exception.class)
    public void updateProduct(ProductDto productDto) {
        productRepository.update(productDto);
        
        // 清除缓存
        String key = "product:" + productDto.getId();
        cacheService.delete(CACHE_NAMESPACE, key);
    }
}
```

### 6.5 日志规范

```java
@Slf4j
@Service
public class OrderService {
    
    public void processOrder(Long orderId) {
        log.info("开始处理订单: orderId={}", orderId);
        
        try {
            OrderEntity order = orderRepository.findById(orderId);
            
            log.debug("订单详情: {}", order);
            
            // 业务逻辑
            processOrderLogic(order);
            
            log.info("订单处理成功: orderId={}", orderId);
            
        } catch (BusinessException e) {
            log.warn("订单处理失败: orderId={}, reason={}", orderId, e.getMessage());
            throw e;
        } catch (Exception e) {
            log.error("订单处理异常: orderId={}", orderId, e);
            throw new RuntimeException("订单处理失败", e);
        }
    }
}
```

### 6.6 线程池选择

**选择线程池的原则：**

1. **I/O 密集型任务**（数据库、网络、文件）→ `ioIntensiveTaskExecutor`
2. **CPU 密集型任务**（计算、加密、图像）→ `cpuIntensiveTaskExecutor`
3. **混合型或不确定任务** → `commonTaskExecutor`

```java
@Service
public class TaskService {
    
    @Resource(name = "ioIntensiveTaskExecutor")
    private CustomTaskExecutor ioExecutor;
    
    @Resource(name = "cpuIntensiveTaskExecutor")
    private CustomTaskExecutor cpuExecutor;
    
    // I/O密集型：数据库查询
    public void queryData() {
        ioExecutor.execute(() -> {
            List<Data> data = dataRepository.findAll();
            // 处理数据
        });
    }
    
    // CPU密集型：数据加密
    public void encryptData(String data) {
        cpuExecutor.execute(() -> {
            String encrypted = encryptionService.encrypt(data);
            // 保存结果
        });
    }
}
```

### 6.7 异步队列使用

```java
// 1. 定义处理器
@Component("orderProcessor")
public class OrderProcessor implements Processor<Order> {
    
    @Override
    public void process(Order order) throws Exception {
        // 处理订单（必须线程安全）
        processOrder(order);
    }
}

// 2. 发送到队列
@Service
public class OrderService {
    
    @Resource
    private IngestQueueManager queueManager;
    
    public void submitOrder(Order order) {
        // 保存订单
        orderRepository.save(order);
        
        // 异步处理
        queueManager.send("orderProcessor", order);
    }
}
```

---

## 7. 常见问题

### 7.1 框架使用问题

**Q: 如何选择合适的 web 子模块？**

A: 根据部署场景选择：
- `web-common`：通用场景
- `web-micro`：微服务场景
- `web-prd`：生产环境
- `web-simple`：简化配置

**Q: 如何处理跨域问题？**

A: 在配置文件中启用 CORS：

```yaml
easyfk:
  config:
    web:
      cors:
        open: true
        cors-domain: "http://localhost:3000"
        allow-credentials: false
```

**Q: TraceId 如何自动传递？**

A: 使用 `CustomTaskExecutor` 会自动传递 TraceId，无需手动处理。

### 7.2 线程池问题

**Q: 线程池参数不配置会怎样？**

A:
- `core-pool-size` 不配置：自动使用 CPU 核心数
- `max-pool-size` 不配置：自动设置为核心线程数的 1.5 倍
- `rejected-execution-handler` 不配置：默认使用 CALLER_RUNS

**Q: 如何选择拒绝策略？**

A:
- **CALLER_RUNS**：默认，适合大多数场景
- **ABORT**：关键业务，需要立即感知过载
- **DISCARD**：非关键任务，可容忍丢失
- **DISCARD_OLDEST**：实时数据，新数据更重要

### 7.3 队列问题

**Q: 队列满了怎么办？**

A: 使用 `trySend` 方法，配合超时和降级策略：

```java
boolean success = queueManager.trySend("myQueue", event, 10, TimeUnit.MILLISECONDS);
if (!success) {
    // 降级处理：记录日志、持久化、告警等
    handleQueueFull(event);
}
```

**Q: 如何避免循环依赖？**

A: 在 Processor 中使用 `IngestQueueManager` 而不是 `IngestQueueRegistry`：

```java
@Component("myProcessor")
public class MyProcessor implements Processor<MyData> {
    
    @Resource
    private IngestQueueManager queueManager;  // ✅ 正确
    
    // @Resource
    // private IngestQueueRegistry registry;  // ❌ 会导致循环依赖
}
```

### 7.4 数据库问题

**Q: 如何支持多数据源？**

A: 框架支持多数据库，通过配置数据源实现：

```yaml
spring:
  datasource:
    primary:
      url: jdbc:mysql://localhost:3306/db1
      username: root
      password: password
    secondary:
      url: jdbc:mysql://localhost:3306/db2
      username: root
      password: password
```

### 7.5 WebSocket 问题

**Q: 如何实现分布式 WebSocket？**

A: 配置 Redis 作为订阅管理：

```yaml
easyfk:
  config:
    ws:
      sub-save-type: distributed  # 使用分布式模式
```

**Q: 推送消息失败怎么办？**

A: 检查：
1. 用户是否在线
2. 是否已订阅对应频道
3. 网络连接是否正常

---

## 8. 附录

### 8.1 构建命令

**Gradle 命令：**

```bash
# 构建整个项目
./gradlew build

# 清理构建
./gradlew clean build

# 构建特定模块
./gradlew :your-module:build

# 运行测试
./gradlew test

# 查看依赖树
./gradlew dependencies

# 发布到本地 Maven 仓库
./gradlew publishToMavenLocal
```

**Maven 命令：**

```bash
# 构建项目
mvn clean install

# 跳过测试
mvn clean install -DskipTests

# 运行测试
mvn test

# 查看依赖树
mvn dependency:tree

# 安装到本地仓库
mvn install
```

### 8.2 版本管理

**框架版本：** 3.5.16

**依赖版本：**
- Spring Boot: 3.5.16
- Java: 21
- Lombok: 1.18.46
- LMAX Disruptor: 4.0

### 8.3 模块清单

| 模块 | 说明 | 依赖 |
|------|------|------|
| easyfk-core | 核心基础模块 | 无 |
| easyfk-repository | 数据访问层 | easyfk-core |
| easyfk-service | 业务逻辑层 | easyfk-repository |
| easyfk-web | Web 层 | easyfk-service |
| easyfk-authority | 权限管理 | easyfk-core |
| easyfk-cache | 缓存抽象 | easyfk-core |
| easyfk-log | 日志模块 | easyfk-core |
| easyfk-queue | 异步队列 | easyfk-core |
| easyfk-thread | 线程池管理 | easyfk-core |
| easyfk-remote | 服务间通信 | easyfk-core |
| easyfk-gateway | 网关过滤 | easyfk-core |
| easyfk-ws | WebSocket | easyfk-core |

### 8.4 联系与支持

- **官方文档**：参考各模块的 CLAUDE.md 文件
- **技术支持**：com.mcst
- **问题反馈**：通过项目 Issue 提交

---

**文档结束**

本手册持续更新中，请关注版本号和更新日期。

