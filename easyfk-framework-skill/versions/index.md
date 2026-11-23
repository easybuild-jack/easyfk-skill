# EasyFK 版本快照索引

| easyfk 版本 | 状态 | 说明 |
|---|---|---|
| [3.5.16](3.5.16/VERSION.md) | 维护中（当前最新） | JDK 21 / Boot 3.5.16 / Cloud 2025.0.3 / SCA 2025.0.0.0；MyBatis-Plus 3.5.18.1 包名迁移、ShardingSphere 5.5.3 驱动方式、springdoc 2.10.0 强制升级、Fory 1.7.8 重写、Aeron 1.54.2。**`cache-mult` 与 `db-influx` 两个子模块下线**（两个版本快照均不再收录文档与 API）。升级必读 `VERSION.md` §3 |
| [3.2.12](3.2.12/VERSION.md) | 维护中 | JDK 21 / Boot 3.2.12 / Cloud 2023.0.5 / SCA 2023.0.3.3；首个快照。同样不含已下线的 `cache-mult`、`db-influx` |

规则：

- 项目的 easyfk 版本 = 导入的 BOM `com.mcst:easyfk-dependencies:<版本>` 的版本。
- 版本精确命中时只读对应目录；没有对应快照时，用不高于项目版本的最近快照，并提示用户差异以项目实际源码和 BOM 为准；项目版本低于所有快照时同样提示，不要套用新版本的用法。
- 只保留维护中的版本；停止维护的快照从本表和目录中移除。
- 新增版本：以上一版快照为起点生成新快照并对照该版本源码复查模块文档（见 `maintenance.md` 流程 A），用 `scripts/gen-api.py` 从该版本源码生成 `api/`，补写 `VERSION.md`（技术基线、构建参数、与上一版的差异、快照修订记录），再在本表登记。
- 每个版本目录都有 `modules/`（用法）与 `api/`（签名速查）两套文档：查"怎么写"读 `modules/`，查"确切签名 / 常量 / 配置项默认值"读 `api/`。
