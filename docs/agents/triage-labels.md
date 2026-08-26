# 分类标签

`triage` 技能使用的标准标签词汇表。

| 标签名 | 用途 |
|--------|------|
| `needs-triage` | Issue 尚未被分类 |
| `needs-info` | Issue 需要更多信息才能处理 |
| `ready-for-agent` | Issue 已就绪，可交由 Agent 处理 |
| `ready-for-human` | Issue 已就绪，需交由人类审核/处理 |
| `wontfix` | Issue 不会修复 |

## 用法

- `triage` 从跟踪器读取 Issue 时会自动应用这些标签
- 使用 `ready-for-agent` 标记适合自主 Agent 处理的任务
- 使用 `ready-for-human` 标记需要人类判断或审核的任务
