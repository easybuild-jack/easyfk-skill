# easyfk-service API 签名速查（easyfk 3.2.12）

> 坐标：`com.mcst:service-api、com.mcst:service-base`　源码：`easyfk-base/easyfk-service/service-api`、`easyfk-base/easyfk-service/service-base`
> 由 `scripts/gen-api.py` 从 8 个源文件自动提取，共 8 个类型、56 个方法/构造器、1 个字段/枚举常量。
> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。用法、配置示例和注意事项看 [../modules/easyfk-service-skill.md](../modules/easyfk-service-skill.md)。
> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。

## 类型索引

- `com.mcst.easyfk.service.api`：[IBaseApi](#ibaseapi)、[IBaseFluxApi](#ibasefluxapi)、[IBaseFluxService](#ibasefluxservice)、[IBaseService](#ibaseservice)
- `com.mcst.easyfk.service.base`：[BaseApiServiceImpl](#baseapiserviceimpl)
- `com.mcst.easyfk.service.util`：[SearchRequestUtil](#searchrequestutil)、[ServiceUtil](#serviceutil)、[UserDataFiltrationUtil](#userdatafiltrationutil)

## 包 `com.mcst.easyfk.service.api`

### IBaseApi

`public interface IBaseApi<T extends Serializable, PK extends Serializable, R extends Serializable>`

**方法**

```java
T queryById(PK id)  // 根据Id值查询
T queryByIdOptimize(PK id, String[] selectColumns)  // 根据Id值查询
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

### IBaseFluxApi

`public interface IBaseFluxApi<T extends Serializable, R extends Serializable>`

**方法**

```java
BaseResult<?> save(ModifyRequest<R> param)  // 保存
List<T> queryList(SearchRequest<R> param)  // 查询列表
long count(SearchRequest<R> param)  // 查询总数
PageResult<T> queryByPage(SearchRequest<R> param)  // 分页查询
BaseResult<?> delete(ModifyRequest<R> param)  // 删除指定时间范围内的数据
```

### IBaseFluxService

`public interface IBaseFluxService<T extends Serializable, R extends Serializable>`

**方法**

```java
BaseResult<?> save(ModifyRequest<R> param)  // 保存
List<T> queryList(SearchRequest<R> param)  // 查询列表
long count(SearchRequest<R> param)  // 查询总数
PageResult<T> queryByPage(SearchRequest<R> param)  // 分页查询
BaseResult<?> delete(ModifyRequest<R> param)  // 删除指定时间范围内的数据
```

### IBaseService

`public interface IBaseService<T extends Serializable, PK extends Serializable, R extends Serializable>`

**方法**

```java
T queryById(PK id, String... selectColumns)  // 根据Id值查询
T queryOneByField(String field, Object value, String... selectColumns)  // 根据字段和值查询一条数据
List<T> queryList(SearchRequest<R> param)  // 据条件查询数据
T queryOne(SearchRequest<R> param)  // 据条件查询数据
long count(SearchRequest<R> param)  // 根据条件查询总数
boolean exists(SearchRequest<R> param)  // 根据条件查询记录是否存在
PageResult<T> queryByPage(SearchRequest<R> condition)  // 分页查询
BaseResult<?> save(ModifyRequest<R> param)  // 保存数据
PK insertAndReturnId(R param)  // 插入数据并返回ID
BaseResult<?> delete(ModifyRequest<R> param)  // 根据StringId 删除数据
```

## 包 `com.mcst.easyfk.service.base`

### BaseApiServiceImpl

`public abstract class BaseApiServiceImpl<I extends IBaseService<T, PK, R>, T extends Serializable, PK extends Serializable, R extends Serializable> implements IBaseApi<T, PK, R>`　BaseApi Service 层抽象实现：所有方法委派给泛型 I 对应的 Service Bean，容器中缺少该 Bean 时启动失败

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

## 包 `com.mcst.easyfk.service.util`

### SearchRequestUtil

`public class SearchRequestUtil`　SearchRequest工具类

**方法**

```java
static <T> void addInConditionForRequest(SearchRequest<T> request, EFunction<T, ?> field, List<?> valueList)  // 对SearchRequest中 参数对象的某个属性进行 in 查询条件处理
static <T> void addEqConditionForRequest(SearchRequest<T> request, Class<T> tClass, EFunction<T, ?> field, Object value)
```

### ServiceUtil

`public class ServiceUtil`

**方法**

```java
static <T extends Serializable, PK extends Serializable, R extends Serializable> BaseResult<?> save(ModifyRequest<R> request, IBaseRepository<T, PK> baseRepository, Class<T> tClass)
static <T extends Serializable, PK extends Serializable, R extends Serializable> BaseResult<?> delete(ModifyRequest<R> request, IBaseRepository<T, PK> baseRepository, Class<T> tClass)
static <T extends Serializable, PK extends Serializable, R extends Serializable> PK insertAndReturnId(R paramObj, IBaseRepository<T, PK> baseRepository, Class<T> tClass)
static <T extends Serializable, R extends Serializable> ModifyRequest<T> convertRequest(ModifyRequest<R> request, Class<T> tClass)
```

### UserDataFiltrationUtil

`public class UserDataFiltrationUtil`　注解：`@SuppressWarnings("unused")`　操作者数据过滤工具类

**方法**

```java
static <T> void setSaasData(ModifyRequest<T> modifyRequest, EFunction<T, ?> saasField, EFunction<UserData, ?> userField)
static <T> void setSaasData(ModifyRequest<T> modifyRequest, Map<EFunction<T, ?>, EFunction<UserData, ?>> fieldMap)
static <T> void saasDataFiltration(SearchRequest<T> searchRequest, Class<T> tClass, EFunction<T, ?> saasField, EFunction<UserData, ?> userSassIdField)
static <T> void saasDataFiltration(SearchRequest<T> searchRequest, Class<T> tClass, Map<EFunction<T, ?>, EFunction<UserData, ?>> fieldMap)  // 根据操作者信息过滤查询请求的数据 此方法用于根据操作者的类型和字段映射，过滤查询请求中的数据 它通过比较操作者类型和映射字段的值，来决定是否在查询请求中添加相等条件
static <T> void dataInFiltration(SearchRequest<T> searchRequest, EFunction<T, ?> saasField, EFunction<UserData, ?> userField)
static <T> void dataInFiltration(SearchRequest<T> searchRequest, Map<EFunction<T, ?>, EFunction<UserData, ?>> fieldMap)  // 执行数据过滤操作，根据给定的搜索请求和字段映射 此方法旨在根据操作者数据中的字段值，对搜索请求进行条件过滤 它通过检查操作者字段值是否存在于给定的ALL常量数组中来决定是否添加过滤条件 如果操作者字段值为空或存在于ALL…
```
