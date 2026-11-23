# easyfk-remote API 签名速查（easyfk 3.2.12）

> 坐标：`com.mcst:remote-cloud、com.mcst:remote-dubbo`　源码：`easyfk-base/easyfk-remote/remote-cloud`、`easyfk-base/easyfk-remote/remote-dubbo`
> 由 `scripts/gen-api.py` 从 12 个源文件自动提取，共 12 个类型、102 个方法/构造器、8 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-remote-skill.md](../modules/easyfk-remote-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 类型索引

- `com.mcst.easyfk.remote.dubbo`：[DubboBaseApiRemoteImpl](#dubbobaseapiremoteimpl)、[DubboBaseFluxApiRemoteImpl](#dubbobasefluxapiremoteimpl)、[DubboBaseFluxRemoteImpl](#dubbobasefluxremoteimpl)、[DubboBaseRemoteImpl](#dubbobaseremoteimpl)、[IDubboBaseFluxRemote](#idubbobasefluxremote)
    [IDubboBaseRemote](#idubbobaseremote)
- `com.mcst.easyfk.remote.sc`：[BaseApiRemoteImpl](#baseapiremoteimpl)、[BaseFluxApiRemoteImpl](#basefluxapiremoteimpl)、[BaseFluxRemoteImpl](#basefluxremoteimpl)、[BaseRemoteImpl](#baseremoteimpl)、[IBaseFluxRemote](#ibasefluxremote)
    [IBaseRemote](#ibaseremote)

## 包 `com.mcst.easyfk.remote.dubbo`

### DubboBaseApiRemoteImpl

`public class DubboBaseApiRemoteImpl<I extends IDubboBaseRemote<T, PK, R>, T extends Serializable, PK extends Serializable, R extends Serializable> implements IBaseApi<T, PK, R>`　BaseApi SpringCloud 层抽象实现

**字段 / 常量**

```java
@DubboReference I dubboBaseRemote
```

**方法**

```java
T queryByIdOptimize(PK id, String[] selectColumns)
T queryById(PK id)
List<T> queryList(SearchRequest<R> param)
T queryOne(SearchRequest<R> param)
long count(SearchRequest<R> param)
boolean exists(SearchRequest<R> param)
PageResult<T> queryByPage(SearchRequest<R> condition)
BaseResult<?> save(ModifyRequest<R> param)
PK insertAndReturnId(R param)
BaseResult<?> delete(ModifyRequest<R> param)
T queryOneByField(String field, Object value)
T queryOneByFieldOptimize(String field, Object value, String[] selectColumns)
```

### DubboBaseFluxApiRemoteImpl

`public class DubboBaseFluxApiRemoteImpl<I extends IDubboBaseFluxRemote<T, R>, T extends Serializable, R extends Serializable> implements IBaseFluxApi<T, R>`　BaseApi SpringCloud 层抽象实现

**字段 / 常量**

```java
@DubboReference I dubboBaseFluxRemote
```

**方法**

```java
List<T> queryList(SearchRequest<R> param)
long count(SearchRequest<R> param)
PageResult<T> queryByPage(SearchRequest<R> condition)
BaseResult<?> save(ModifyRequest<R> param)
BaseResult<?> delete(ModifyRequest<R> param)
```

### DubboBaseFluxRemoteImpl

`public class DubboBaseFluxRemoteImpl<I extends IBaseFluxService<T, R>, T extends Serializable, R extends Serializable> implements IDubboBaseFluxRemote<T, R>`

**字段 / 常量**

```java
@Autowired I baseFluxService
```

**方法**

```java
PageResult<T> queryByPage(SearchRequest<R> condition)
BaseResult<?> save(ModifyRequest<R> param)
List<T> queryList(SearchRequest<R> param)
long count(SearchRequest<R> param)
BaseResult<?> delete(ModifyRequest<R> param)
```

### DubboBaseRemoteImpl

`public class DubboBaseRemoteImpl<I extends IBaseService<T, PK, R>, T extends Serializable, PK extends Serializable, R extends Serializable> implements IDubboBaseRemote<T, PK, R>`

**字段 / 常量**

```java
@Autowired I baseService
```

**方法**

```java
T queryByIdOptimize(PK id, String[] selectColumns)
T queryById(PK id)
List<T> queryList(SearchRequest<R> param)
T queryOne(SearchRequest<R> param)
long count(SearchRequest<R> param)
boolean exists(SearchRequest<R> param)
PageResult<T> queryByPage(SearchRequest<R> condition)
BaseResult<?> save(ModifyRequest<R> param)
PK insertAndReturnId(R param)
BaseResult<?> delete(ModifyRequest<R> param)
T queryOneByField(String field, Object value)
T queryOneByFieldOptimize(String field, Object value, String[] selectColumns)
```

### IDubboBaseFluxRemote

`public interface IDubboBaseFluxRemote<T extends Serializable, R extends Serializable>`　springcloud remote基类

**方法**

```java
List<T> queryList(SearchRequest<R> param)  // 据条件查询数据
long count(SearchRequest<R> param)  // 根据条件查询总数
PageResult<T> queryByPage(SearchRequest<R> condition)  // 分页查询
BaseResult<?> save(ModifyRequest<R> param)  // 保存数据
BaseResult<?> delete(ModifyRequest<R> param)  // 根据StringId 删除数据
```

### IDubboBaseRemote

`public interface IDubboBaseRemote<T extends Serializable, PK extends Serializable, R extends Serializable>`　springcloud remote基类

**方法**

```java
T queryByIdOptimize(PK id, String[] selectColumns)  // queryByIdOptimize
T queryById(PK id)  // 根据Id值查询
T queryOneByField(String field, Object value)  // 根据字段和值查询一条数据
T queryOneByFieldOptimize(String field, Object value, String[] selectColumns)  // 根据字段和值查询一条数据
List<T> queryList(SearchRequest<R> param)  // 据条件查询数据
T queryOne(SearchRequest<R> param)  // 据条件查询数据
long count(SearchRequest<R> param)  // 根据条件查询总数
boolean exists(SearchRequest<R> param)  // 根据条件查询记录是否存在
PageResult<T> queryByPage(SearchRequest<R> condition)  // 分页查询
BaseResult<?> save(ModifyRequest<R> param)  // 保存数据
PK insertAndReturnId(R param)  // 保存数据并返回ID
BaseResult<?> delete(ModifyRequest<R> param)  // 根据StringId 删除数据
```

## 包 `com.mcst.easyfk.remote.sc`

### BaseApiRemoteImpl

`public class BaseApiRemoteImpl<I extends IBaseRemote<T, PK, R>, T extends Serializable, PK extends Serializable, R extends Serializable> implements IBaseApi<T, PK, R>`　BaseApi SpringCloud 层抽象实现

**字段 / 常量**

```java
@Autowired I baseScRemote
```

**方法**

```java
T queryByIdOptimize(PK id, String[] selectColumns)
T queryById(PK id)
List<T> queryList(SearchRequest<R> param)
T queryOne(SearchRequest<R> param)
long count(SearchRequest<R> param)
boolean exists(SearchRequest<R> param)
PageResult<T> queryByPage(SearchRequest<R> condition)
BaseResult<?> save(ModifyRequest<R> param)
PK insertAndReturnId(R param)
BaseResult<?> delete(ModifyRequest<R> param)
T queryOneByField(String field, Object value)
T queryOneByFieldOptimize(String field, Object value, String[] selectColumns)
```

### BaseFluxApiRemoteImpl

`public class BaseFluxApiRemoteImpl<I extends IBaseFluxRemote<T, R>, T extends Serializable, R extends Serializable> implements IBaseFluxApi<T, R>`　BaseApi SpringCloud 层抽象实现

**字段 / 常量**

```java
@Autowired I baseFluxRemote
```

**方法**

```java
List<T> queryList(SearchRequest<R> param)
long count(SearchRequest<R> param)
PageResult<T> queryByPage(SearchRequest<R> condition)
BaseResult<?> save(ModifyRequest<R> param)
BaseResult<?> delete(ModifyRequest<R> param)
```

### BaseFluxRemoteImpl

`public class BaseFluxRemoteImpl<I extends IBaseFluxService<T, R>, T extends Serializable, R extends Serializable> implements IBaseFluxRemote<T, R>`

**字段 / 常量**

```java
@Autowired I baseFluxService
```

**方法**

```java
PageResult<T> queryByPage(SearchRequest<R> condition)
BaseResult<?> save(ModifyRequest<R> param)
List<T> queryList(SearchRequest<R> param)
long count(SearchRequest<R> param)
BaseResult<?> delete(ModifyRequest<R> param)
```

### BaseRemoteImpl

`public class BaseRemoteImpl<I extends IBaseService<T, PK, R>, T extends Serializable, PK extends Serializable, R extends Serializable> implements IBaseRemote<T, PK, R>`

**字段 / 常量**

```java
@Autowired I baseService
```

**方法**

```java
T queryByIdOptimize(PK id, String[] selectColumns)
T queryById(PK id)
List<T> queryList(SearchRequest<R> param)
T queryOne(SearchRequest<R> param)
long count(SearchRequest<R> param)
boolean exists(SearchRequest<R> param)
PageResult<T> queryByPage(SearchRequest<R> condition)
BaseResult<?> save(ModifyRequest<R> param)
PK insertAndReturnId(R param)
BaseResult<?> delete(ModifyRequest<R> param)
T queryOneByField(String field, Object value)
T queryOneByFieldOptimize(String field, Object value, String[] selectColumns)
```

### IBaseFluxRemote

`public interface IBaseFluxRemote<T extends Serializable, R extends Serializable>`　springcloud remote基类

**方法**

```java
@PostMapping(value = "/queryList", consumes = MediaType.APPLICATION_JSON_VALUE) List<T> queryList(@RequestBody SearchRequest<R> param)  // 据条件查询数据
@PostMapping(value = "/count", consumes = MediaType.APPLICATION_JSON_VALUE) long count(@RequestBody SearchRequest<R> param)  // 根据条件查询总数
@PostMapping(value = "/queryByPage", consumes = MediaType.APPLICATION_JSON_VALUE) PageResult<T> queryByPage(@RequestBody SearchRequest<R> condition)  // 分页查询
@PostMapping(value = "/save", consumes = MediaType.APPLICATION_JSON_VALUE) BaseResult<?> save(@RequestBody ModifyRequest<R> param)  // 保存数据
@PostMapping(value = "/delete", consumes = MediaType.APPLICATION_JSON_VALUE) BaseResult<?> delete(@RequestBody ModifyRequest<R> param)  // 根据StringId 删除数据
```

### IBaseRemote

`public interface IBaseRemote<T extends Serializable, PK extends Serializable, R extends Serializable>`　springcloud remote基类

**方法**

```java
@GetMapping("/queryByIdOptimize") T queryByIdOptimize(@RequestParam("id") PK id, @RequestParam("selectColumns") String[] selectColumns)  // queryByIdOptimize
@GetMapping("/queryById") T queryById(@RequestParam("id") PK id)  // 根据Id值查询
@GetMapping("/queryOneByField") T queryOneByField(@RequestParam("field") String field, @RequestParam("value") Object value)  // 根据字段和值查询一条数据
@GetMapping("/queryOneByFieldOptimize") T queryOneByFieldOptimize(@RequestParam("field") String field, @RequestParam("value") Object value, @RequestParam("selectColumns") String[] selectColumns)  // 根据字段和值查询一条数据
@PostMapping(value = "/queryList", consumes = MediaType.APPLICATION_JSON_VALUE) List<T> queryList(@RequestBody SearchRequest<R> param)  // 据条件查询数据
@PostMapping(value = "/queryOne", consumes = MediaType.APPLICATION_JSON_VALUE) T queryOne(@RequestBody SearchRequest<R> param)  // 据条件查询数据
@PostMapping(value = "/count", consumes = MediaType.APPLICATION_JSON_VALUE) long count(@RequestBody SearchRequest<R> param)  // 根据条件查询总数
@PostMapping(value = "/exists", consumes = MediaType.APPLICATION_JSON_VALUE) boolean exists(@RequestBody SearchRequest<R> param)  // 根据条件查询记录是否存在
@PostMapping(value = "/queryByPage", consumes = MediaType.APPLICATION_JSON_VALUE) PageResult<T> queryByPage(@RequestBody SearchRequest<R> condition)  // 分页查询
@PostMapping(value = "/save", consumes = MediaType.APPLICATION_JSON_VALUE) BaseResult<?> save(@RequestBody ModifyRequest<R> param)  // 保存数据
@PostMapping(value = "/insertAndReturnId", consumes = MediaType.APPLICATION_JSON_VALUE) PK insertAndReturnId(@RequestBody R param)  // 保存数据并返回ID
@PostMapping(value = "/delete", consumes = MediaType.APPLICATION_JSON_VALUE) BaseResult<?> delete(@RequestBody ModifyRequest<R> param)  // 根据StringId 删除数据
```
