# easyfk-component-rpc API 签名速查（easyfk 3.5.16）

> 坐标：`com.mcst:rpc-cloud、rpc-dubbo`　源码：`easyfk-component/component-rpc/rpc-cloud`、`easyfk-component/component-rpc/rpc-dubbo`
> 由 `scripts/gen-api.py` 从 6 个源文件自动提取，共 6 个类型、8 个方法/构造器、0 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-component-rpc-skill.md](../modules/easyfk-component-rpc-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 自动配置类（引入即生效）

来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

| 子模块 | 自动配置类 |
|---|---|
| `rpc-cloud` | `com.mcst.easyfk.rpc.springcloud.config.FeignConfigure` |
| `rpc-dubbo` | `com.mcst.easyfk.rpc.dubbo.config.DubboConfig` |

## 类型索引

- `com.mcst.easyfk.rpc.dubbo.config`：[DubboConfig](#dubboconfig)
- `com.mcst.easyfk.rpc.dubbo.filter`：[DubboFilter](#dubbofilter)
- `com.mcst.easyfk.rpc.dubbo.invoker`：[DubboDirectInvoker](#dubbodirectinvoker)
- `com.mcst.easyfk.rpc.springcloud.config`：[FeignConfigure](#feignconfigure)
- `com.mcst.easyfk.rpc.springcloud.exception`：[FeignErrorDecoder](#feignerrordecoder)
- `com.mcst.easyfk.rpc.springcloud.interceptor`：[FeignClientInterceptor](#feignclientinterceptor)

## 包 `com.mcst.easyfk.rpc.dubbo.config`

### DubboConfig

`public class DubboConfig`　注解：`@AutoConfiguration`

**方法**

```java
@Bean @ConditionalOnMissingBean DubboDirectInvoker dubboDirectInvoker()
```

## 包 `com.mcst.easyfk.rpc.dubbo.filter`

### DubboFilter

`public class DubboFilter implements Filter`　注解：`@Slf4j` `@Activate(group = {CommonConstants.CONSUMER, CommonConstants.PROVIDER}, order = -1000)`

**方法**

```java
Result invoke(Invoker<?> invoker, Invocation invocation) throws RpcException
```

## 包 `com.mcst.easyfk.rpc.dubbo.invoker`

### DubboDirectInvoker

`public class DubboDirectInvoker`　注解：`@Slf4j`　基于 Dubbo 直连（direct url）的通用调用器。 提供两种调用模式： Generic 模式：无需依赖接口与模型类字节码…

**方法**

```java
Object invokeGeneric(String interfaceName, String host, int port, String methodName, String[] paramTypes, Object[] args, String group, String version, Integer timeoutMs, Integer retries)  // 使用 GenericService 进行通用调用，支持方法重载。 参数说明： interfaceName：接口全限定名（例如："com.example.DemoService"）…
<T> Object invokeTyped(Class<T> interfaceClass, String host, int port, String methodName, Class<?>[] parameterTypes, Object[] args, String group, String version, Integer timeoutMs, Integer retries) throws Exception  // 使用强类型引用 + 反射进行调用。 参数说明： interfaceClass：接口 Class（例如：IProcessorRemote.class）。 host/port：提供者直连地址。 methodName：方法名…
```

## 包 `com.mcst.easyfk.rpc.springcloud.config`

### FeignConfigure

`public class FeignConfigure`　注解：`@AutoConfiguration`

**方法**

```java
@Bean @ConditionalOnMissingBean(ErrorDecoder.class) FeignErrorDecoder feignErrorDecoder()
@Bean FeignClientInterceptor feignClientInterceptor()
```

## 包 `com.mcst.easyfk.rpc.springcloud.exception`

### FeignErrorDecoder

`public class FeignErrorDecoder implements ErrorDecoder`　注解：`@Slf4j`　Feign 错误解码：响应体为框架 BaseResult 且 code 不是系统错误时还原为 BusinessException， 其余情况（无响应体、非 JSON、缺少 code、系统错误）统一返回国际化的系统错误

**方法**

```java
Exception decode(String methodKey, Response response)
```

## 包 `com.mcst.easyfk.rpc.springcloud.interceptor`

### FeignClientInterceptor

`public class FeignClientInterceptor implements RequestInterceptor`　透传 TRACE_ID，以及 RequestHeaderContext 中的 Access-Token、Language（web-micro RequestBaseFilter 读取的请求头）…

**方法**

```java
void apply(RequestTemplate requestTemplate)
```
