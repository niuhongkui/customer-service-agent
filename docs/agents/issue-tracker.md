# 问题跟踪器

本仓库使用 **GitHub Issues** 作为问题跟踪器。

## 配置

- **平台**：GitHub
- **CLI 工具**：`gh`
- **仓库**：`niuhongkui/customer-service-agent`
- **PR 作为请求入口**：关闭（默认）

## 工作流

与问题跟踪器交互的技能：

- `to-tickets`：将规格说明/任务转换为 GitHub Issue
- `triage`：读取未分类 Issue 并应用标签和分配
- `to-spec`：读取 Issue 并生成规格说明文档

## 约定

- Issue 使用 GitHub 标准 Issue 模板
- 标签通过 `docs/agents/triage-labels.md` 中的分类标签词汇表管理
