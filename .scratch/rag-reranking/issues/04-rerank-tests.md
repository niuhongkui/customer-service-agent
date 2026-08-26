# 04: 精排功能测试覆盖

**What to build:** 为精排功能添加完整的测试覆盖，包括单元测试、集成测试和边界测试，确保精排逻辑正确且向后兼容。

**Blocked by:** 02: 检索模块支持精排参数, 03: Pipeline 集成精排 + 依赖声明

**Status:** ready-for-agent

- [ ] 单元测试：`retrieve()` 不传 reranker 时行为与现有逻辑一致
- [ ] 单元测试：`retrieve()` 传入 mock reranker 时，调用 `postprocess_nodes()` 并返回精排后的结果
- [ ] 单元测试：精排后结果数量不超过 `rerank_top_n`
- [ ] 单元测试：精排后结果按精排分数降序排列
- [ ] 边界测试：召回 0 条时，跳过精排返回空列表
- [ ] 边界测试：召回数 < `rerank_top_n` 时，精排后保留全部召回结果
- [ ] 集成测试：`RAGPipeline.query()` 在 `rerank_enabled=True` 时端到端精排流程
- [ ] 集成测试：`RAGPipeline.query()` 在 `rerank_enabled=False` 时行为不变
- [ ] 所有新增和现有测试通过
