# 常用提示词目录

用于集中常用 Prompt，建议按场景维护，例如：

- `coding.md`：代码生成/重构
- `review.md`：代码评审
- `debug.md`：故障排查
- `docs.md`：文档生成

可直接在本目录新增对应文件并持续迭代。

```text
code review
# 模板（变量版）
请根据 ${SOURCE_BRANCH} 审查 ${TARGET_BRANCH} 上的更改，并重点做 ${ANALYSIS_FOCUS} 的对比分析。

# 变量说明
# SOURCE_BRANCH: 源分支/基准分支（如 dev、main）
# TARGET_BRANCH: 待审查分支（如 feature/model-provider-separator）
# ANALYSIS_FOCUS: 对比分析维度（如 功能正确性、回归风险、性能影响、测试覆盖）

# 用法示例
请根据 dev 审查 feature/model-provider-separator 上的更改，并重点做 功能正确性、回归风险、测试覆盖 的对比分析。
```
