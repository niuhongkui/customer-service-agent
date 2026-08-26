# 02: 检索模块支持精排参数

**What to build:** 检索函数支持通过参数接收 reranker 实例，传入时对召回结果进行 cross-encoder 精排重排序，不传时保持现有行为完全不变。添加精排过程的调试日志。

**Blocked by:** 01: 添加精排配置字段

**Status:** ready-for-agent

- [ ] `retrieve()` 函数新增可选参数 `reranker: SentenceTransformerRerank | None = None`
- [ ] 当 `reranker` 不为 `None` 时，在 score 过滤之后调用 `reranker.postprocess_nodes(nodes)` 进行精排
- [ ] 精排后根据 `rerank_top_n` 截断结果数量
- [ ] 精排后按精排分数降序排列
- [ ] 当 `reranker` 为 `None` 时，行为与现有逻辑完全一致（向后兼容）
- [ ] 添加调试日志：`[RERANK] 召回 {N} 条 → 精排后保留 {M} 条`
- [ ] 召回结果为 0 条时，跳过精排直接返回空列表
- [ ] 召回结果数少于 `rerank_top_n` 时，精排后保留全部召回结果
- [ ] 现有测试通过（不传 reranker 时行为不变）
