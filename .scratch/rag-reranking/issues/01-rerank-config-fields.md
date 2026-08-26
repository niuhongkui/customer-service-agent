# 01: 添加精排配置字段

**What to build:** 在应用配置模块中新增 reranking 相关的三个配置字段，支持通过环境变量覆盖，为后续精排功能提供配置基础。纯配置变更，不引入任何行为变化。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] 在 Settings 类中新增 `rerank_model: str` 字段，默认值 `"BAAI/bge-reranker-large"`
- [ ] 在 Settings 类中新增 `rerank_top_n: int` 字段，默认值 `3`
- [ ] 在 Settings 类中新增 `rerank_enabled: bool` 字段，默认值 `True`
- [ ] 三个字段均可通过 `CSA_` 前缀环境变量覆盖（`CSA_RERANK_MODEL`、`CSA_RERANK_TOP_N`、`CSA_RERANK_ENABLED`）
- [ ] 现有单元测试和集成测试全部通过，无行为变化
