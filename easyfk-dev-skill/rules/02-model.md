# 02 模型层：Dto / Param / Req / EditReq / Resp / VO

模型类都放在 `<mod>-api` 模块，给服务端和调用方共用；单模块项目放在 `api` 包下的 `dto` / `param` / `request` / `response` / `vo`（见 [01-project.md](01-project.md) §2.1）。

## 1. 各对象的职责

| 对象 | 继承 | 职责 | 用在哪 |
|---|---|---|---|
| `XxxDto` | `BaseDto` | 业务数据本身，字段与表一一对应。主键和唯一性注解写在这里 | Repository 的泛型、Service 内部 |
| `XxxParam` | `BasicParam` | 查询参数：业务字段 + 分页、排序、`top`、`searchKeyWord` 等（继承自 `BasicParam`） | 只作为 `XxxReq` 的父类 |
| `XxxReq` | `XxxParam` | 请求对象，Service / Api / Remote 泛型里的 `R` | 查询条件、保存参数 |
| `XxxEditReq` | `XxxDto` | 新增 / 编辑的入参，只给 Controller 用 | `addOrEdit` 的 `@RequestBody` |
| `XxxResp` | `XxxDto` | 返回对象，Service / Api / Remote 泛型里的 `T` | 查询结果 |
| `XxxVO`、`XxxRequest` 等 | 实现 `Serializable` | 不对应表的入参出参，如登录请求、改密码 | 扩展业务方法 |

`BaseDto` 已经带有 `insertTime`、`lastUpdateTime`；`BasicParam` 已经带有 `top`、`page`、`limit`、`ascFields`、`descFields`、`searchKeyWord`、`start`、`stop` 等。子类不要重复声明这些字段。

## 2. 写法

```java
@Data
@EqualsAndHashCode(callSuper = true)
@Accessors(chain = true)
@Schema(description = "订单数据对象")
@AutoMapper(target = OrderResp.class)
public class OrderDto extends BaseDto {

    /**
     * 订单ID
     */
    @PrimaryKey
    @Schema(description = "订单ID")
    private String orderId;

    /**
     * 订单编号
     */
    @SingleUniqueField(repetitionMsg = "订单编号已存在")
    @Schema(description = "订单编号")
    private String orderNo;

    /**
     * 禁用状态 0可用，1禁用
     */
    @Schema(description = "禁用状态 0可用，1禁用")
    private Integer forbiddenFlag;
}
```

```java
@Data
@EqualsAndHashCode(callSuper = true)
@Accessors(chain = true)
@Schema(description = "订单参数对象")
public class OrderParam extends BasicParam {
    @Schema(description = "订单ID")
    private String orderId;

    @Schema(description = "订单编号")
    private String orderNo;

    @Schema(description = "禁用状态 0可用，1禁用")
    private Integer forbiddenFlag;
}

@Data
@EqualsAndHashCode(callSuper = true)
@Accessors(chain = true)
@Schema(description = "订单请求对象")
@AutoMapper(target = OrderDto.class)
public class OrderReq extends OrderParam { }

@Data
@EqualsAndHashCode(callSuper = true)
@Accessors(chain = true)
@Schema(description = "订单编辑对象")
@AutoMapper(target = OrderReq.class)
public class OrderEditReq extends OrderDto { }

@Data
@EqualsAndHashCode(callSuper = true)
@Accessors(chain = true)
@Schema(description = "订单响应对象")
public class OrderResp extends OrderDto { }
```

规则：

- 四个 Lombok / Swagger 注解（`@Data`、`@EqualsAndHashCode(callSuper = true)`、`@Accessors(chain = true)`、`@Schema`）每个模型类都写。
- 字段用包装类型（`Integer`、`Long`、`Boolean`），不用基本类型。保存时 `null` 表示「不更新该字段」，基本类型的默认值会把数据改掉。
- 主键字段 `String`，加 `@PrimaryKey`。`Param` 里要有同名的主键字段，删除、启用禁用靠它定位记录。
- `Dto` 和 `Param` 的业务字段保持同名同类型，否则 `Req → Dto` 转换时会丢字段。新增字段时两边一起加，Entity 也一起加。
- 唯一字段在 `Dto` 上加 `@SingleUniqueField(repetitionMsg = "...")`，组合唯一用 `@CombUniqueField(combinationField = "...", repetitionMsg = "...")`。`repetitionMsg` 写给最终用户看的中文提示，并且要和字段对得上。数据库同时建唯一索引。
- 金额用 `BigDecimal`；时间用项目里已有实体用的类型，没有先例时用 `LocalDateTime`。
- 字段注释写业务含义；状态类字段把每个取值的含义写全（如 `0可用，1禁用`）。

## 3. 对象转换

转换关系靠 MapStruct-Plus 的 `@AutoMapper` 在编译期生成：

```
Entity ──> Dto ──> Resp          （查询：Repository 返回 Dto，Service 转成 Resp）
EditReq ──> Req ──> Dto ──> Entity（保存：Controller 转成 Req，ServiceUtil 转成 Dto，Repository 转成 Entity）
```

- 每一步都要有 `@AutoMapper(target = 下一步.class)`：`Entity → Dto`、`Dto → Resp`、`Req → Dto`、`EditReq → Req`。缺了不会报错，但 `TransformUtil` 会退回反射拷贝并打 warn 日志，性能差，也容易在字段不一致时静默丢值。
- 转换统一用 `TransformUtil.transformObj / transformList / transformPageResult`，Controller 里用 `MRPBuilder.buildRequest(editReq, XxxReq.class)`。不要手写 getter / setter 拷贝，也不要另引 BeanUtils、ModelMapper。
- 字段名不一致又必须转换时，在字段上用 MapStruct-Plus 的 `@AutoMapping(target = "...")`，不在 Service 里手动赋值。最好的做法还是让字段同名。

## 4. 参数校验

- 用 `jakarta.validation` 注解（`@NotBlank`、`@NotNull`、`@Size`、`@Pattern` 等），`message` 写中文。
- 新增编辑的必填校验写在 `Dto` 字段上，Controller 入参写 `@Validated @RequestBody XxxEditReq`。注意编辑时同样会校验，必填字段在编辑时也要传。项目已有 Controller 没有加 `@Validated` 时，跟随项目现状，在 Service 里校验。
- 服务端填充、前端不该传的字段（如 `agentId`、`merchantId`、操作人）用 `@Schema(hidden = true)` 隐藏。
- VO 实现 `Serializable`，跨服务传输的对象都要能序列化。
