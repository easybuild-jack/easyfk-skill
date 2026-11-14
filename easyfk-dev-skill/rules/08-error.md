# 08 异常与错误码

业务失败一律抛 `BusinessException`，由框架的全局异常处理（`PrdExceptionHandler` 等）转成 `ResponseResult` 失败响应。HTTP 状态码约定见 `modules/easyfk-web-skill.md` §5.8：`BusinessException` 返回 200 + 异常的错误码，参数校验失败返回 400 + `PARAM_ERROR`。

默认用**错误码枚举**；项目需要多语言时用 **i18n**。先看项目里已有的写法，已经有错误码枚举或 i18n 文件的，往里加，不另建一套。

## 1. 错误码枚举（默认）

每个业务模块一个枚举，放在 `<mod>-server` 的 `<base>.server.enums` 包，实现 `BaseErrorEnum`：

```java
@Getter
@Setter
@AllArgsConstructor
public enum OrderErrorEnum implements BaseErrorEnum {
    ID_REQUIRED("ORDER_0001", "订单ID不能为空"),
    ORDER_NOT_FOUND("ORDER_0002", "订单不存在"),
    ORDER_IN_USE("ORDER_0003", "订单已有明细，不能删除"),
    ORDER_SHIPPED("ORDER_0004", "订单已发货，不能取消");

    private String code;
    private String message;
}
```

```java
OrderDto order = this.orderRepository.queryById(orderId);
if (order == null) {
    throw new BusinessException(OrderErrorEnum.ORDER_NOT_FOUND);
}
```

- `BaseErrorEnum` 要求 `getCode`、`setCode`、`getMessage`、`setMessage` 四个方法，所以枚举上要有 `@Setter`。字段不要声明成 `final`。
- 错误码格式：`<模块大写>_<四位序号>`，同一模块内不重复，只追加不改号。项目已有编码规则时照项目的。
- `message` 是给最终用户看的中文提示，说清楚哪里不对、该怎么做，不暴露表名、SQL、堆栈。
- 不要用框架保留的错误码（`UN_LOGIN`、`UN_AUTH`、`PARAM_ERROR`、`BUSYNESS`、`ERROR` 以及 `ErrorRequest` 里的码），它们会被映射成 401 / 403 / 400 / 503。
- 临时、一次性的提示也可以直接 `BEBuilder.exception("提示", "错误码")`，但同一个错误在两处以上出现时就进枚举。

## 2. i18n（项目需要多语言时）

### 2.1 消息文件

放在提供该模块的 jar 的 `src/main/resources/i18n/` 下，文件名 `<模块>Message_<语言>.properties`，UTF-8 编码：

```
i18n/tradeMessage_zh_CN.properties
i18n/tradeMessage_en_US.properties
```

```properties
OrderNotFound=订单不存在
OrderShipped=订单{0}已发货，不能取消
```

- key 用大驼峰英文，说清是哪个错误（`OrderNotFound`），不用数字。
- 每个语言文件的 key 要一样多。新增 key 时所有语言文件一起加。
- 带参数的用 `{0}`、`{1}` 占位。
- 路径常量放在模块的枚举或常量类里（如 auth 的 `AuthEnum.I18N_PATH("i18n/authMessage")`），不在代码里到处写字符串。

### 2.2 抛出

```java
throw BEBuilder.exceptionByI18n("订单不存在", "OrderNotFound", TradeConstant.I18N_PATH);

throw BEBuilder.exceptionByI18n("订单已发货，不能取消", "OrderShipped", TradeConstant.I18N_PATH, orderNo);
```

参数顺序：**默认消息、i18n key、消息文件路径、占位参数**。

- 第一个参数是找不到翻译时的默认消息，写中文原文，不能写 key。
- 第二个参数是 key，第三个参数是文件路径（不带语言后缀和 `.properties`）。不传路径时用框架默认的 `i18n/messages`，业务模块的 key 不在那里，所以**业务模块必须传路径**。
- 语言取自请求头的语言字段，没有时按 `zh_CN`。
- key 在文件里找不到时，返回给前端的消息就是 key 本身。写完对照消息文件检查一遍 key 的拼写。
- 不传路径、只传一个字符串占位参数时（`exceptionByI18n(msg, key, orderNo)`），这个参数会匹配到「路径」那个重载，被当成文件路径。这也是必须传路径的原因。
- 还要带错误码时用 builder：`BEBuilder.builder("订单不存在").errCode("ORDER_0002").i18nCode("OrderNotFound").msgPath(TradeConstant.I18N_PATH).build()`。

## 3. 参数校验异常

- 必填、格式、长度等能用注解表达的，写在模型上用 `jakarta.validation` 注解（见 [02-model.md](02-model.md)），框架会返回 400 + `PARAM_ERROR`。
- 注解表达不了的业务校验，在 Service 方法开头检查，不满足时抛 `BusinessException`。

## 4. 不要这样做

- `throw new RuntimeException("...")` 或抛 `Exception` 表达业务失败。它们会变成 500 + 系统错误提示，用户看不到原因。
- Service 返回 `null` 或 `false` 表示失败，让上层去猜原因。
- `catch` 异常后只打日志不处理，或吞掉异常返回成功。必须 `catch` 时，要么转换成 `BusinessException` 往上抛（把原异常写进日志），要么有明确的降级逻辑。
- 把 `BEBuilder.exceptionByI18n` 的参数写反，比如 `exceptionByI18n("OrderNotFound", PATH)`：这样 key 被当成消息、路径被当成 key，翻译永远不生效。
