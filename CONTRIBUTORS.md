# Contributor Identity & Methodology

本文档记录 vLLM-HUST 组织贡献者排行榜的统计方法、身份合并规则和 GitHub 映射表。

## 身份合并规则 (`.mailmap`)

组织使用 `.mailmap` 文件规范化 Git author 身份。以下为当前合并规则：

### Shuhao Zhang

| Git Author | Email | 来源 |
| --- | --- | --- |
| Shuhao Zhang | shuhao_zhang@hust.edu.cn | 主身份 |
| Shuhao / shuhao | shuhao@example.com | 本地开发 |
| shuhao zhang | shuhao_zhang@hust.edu.cn | 大小写变体 |
| Shuhao Zhang (Tony) | shuhao_zhang@hust.edu.cn | 全称变体 |
| IntelliStream | team@intellistream.org | 组织 bot |
| ShuhaoZhangTony | noreply | GitHub Web 编辑 |
| Sage | sage@hust.edu.cn | 短名 |
| chooper26 | tony_zhang@live.com.sg | 旧用户名 |
| Tony | 864832769@qq.com | 历史提交身份 |
| qixinzhang2601 | 420444843@qq.com | 历史 GitHub / 提交身份 |
| my | my@example.com | 临时本地配置 |

### moonandlife (Jeffrey Wang)

| Git Author | Email | 来源 |
| --- | --- | --- |
| moonandlife | moonandlife@qq.com | 主身份 |
| Jeffrey Wang | moonandlife@qq.com | 实名别名（同邮箱） |

### MingqiWang-coder

| Git Author | Email | 来源 |
| --- | --- | --- |
| MingqiWang-coder | mingqiwang@hust.edu.cn | 主身份 |
| MingqiWang-coder | 15751853706@163.com | 备用邮箱 |

### 刘俊 (iliujunn)

| Git Author | Email | 来源 |
| --- | --- | --- |
| iliujunn / Lou Jun | iliujun@msn.com | 刘俊的主提交身份 |
| liu | 99582471+irving11-bkn@users.noreply.github.com | GitHub noreply |

### 刘世锋 (Remygred)

| Git Author | Email | 来源 |
| --- | --- | --- |
| Remygred | 153624059+Remygred@users.noreply.github.com | 刘世锋的主提交身份 |
| Remygred | 2779387088@qq.com | 刘世锋的备用提交邮箱 |

### aly16-k / vllm-hust-quantization

| Git Author | Email | 来源 |
| --- | --- | --- |
| aly16-k | 1427850140k@gmail.com | 主身份 |
| vllm-hust-quantization | 1427850140k@gmail.com | 量化仓库提交（同邮箱） |

## 已确认独立身份

以下用户名虽有一定关联性但经邮箱和提交记录确认为**不同人**：

| 用户名 | Email(s) | 说明 |
| --- | --- | --- |
| luoxiaohei | luoxiaohei@ppio.com, luoxiaohei@gitlab.paigod.work | 与 moonandlife 使用不同邮箱，独立贡献者 |
| Jeffrey (Huawei) | jeffrey.wangsheng@huawei.com | 华为员工，非 Jeffrey Wang (moonandlife) |
| Jeffrey Li | jeffrey-dot-li@users.noreply.github.com | 另一位 Jeffrey，非 moonandlife |

## GitHub 账号映射

通过 noreply 邮箱或公开信息确认的 GitHub 登录名：

| Canonical Name | GitHub Login | 确认方式 |
| --- | --- | --- |
| Shuhao Zhang | [ShuhaoZhangTony](https://github.com/ShuhaoZhangTony) | mailmap + noreply |
| moonandlife | [moonandlife](https://github.com/moonandlife) | noreply |
| MingqiWang-coder | [MingqiWang-coder](https://github.com/MingqiWang-coder) | noreply |
| Xiling Gao | [XilingGao](https://github.com/XilingGao) | email |
| KimmoZAG | [KimmoZAG](https://github.com/KimmoZAG) | noreply |
| 刘俊 | [iliujunn](https://github.com/iliujunn) | 人工确认 |
| Jingyuan Tian | [CubeLander](https://github.com/CubeLander) | noreply |
| pygone | [Pygone](https://github.com/Pygone) | noreply |
| aly16-k | [aly16-k](https://github.com/aly16-k) | noreply |
| 刘世锋 | [Remygred](https://github.com/Remygred) | 人工确认；华科大三实习生，指导老师张书豪 |
| 曹哲 | [xmdhb](https://github.com/xmdhb) | 人工确认；即将入学的研究生，指导老师张书豪 |
| 李庚 | [Anjiangy](https://github.com/Anjiangy) | 人工确认；马上入学的华科研究生，指导老师张书豪 |
| 杜忠承 | [dzcixy](https://github.com/dzcixy) | 人工确认；学生，指导老师黄禹 |
| sad-and-bad1231 | [sad-and-bad1231](https://github.com/sad-and-bad1231) | noreply |
| Raing5Days | [Raing5Days](https://github.com/Raing5Days) | noreply |
| cybber695 | [cybber695](https://github.com/cybber695) | noreply |
| bnellnm | [bnellnm](https://github.com/bnellnm) | noreply |

## 统计方法

### 数据来源

排行榜由 `scripts/update_contributor_leaderboard.py` 自动生成，也可手动运行：

```bash
python scripts/update_contributor_leaderboard.py --workspace-root /path/to/workspace
```

只更新已确认姓名、账号别名、身份和研究/参与方向，而保留上一次真实
Git 统计数据时，可运行：

```bash
python scripts/update_contributor_leaderboard.py \
  --workspace-root /path/to/workspace \
  --profiles-only
```

“组织全仓库”范围在每次运行时从 GitHub 自动发现：计入 vLLM-HUST 下所有公开、未归档、非 GitHub fork 的独立仓库，并额外计入脚本中显式配置了 fork-only 规则的仓库。私有仓库不进入公开榜单；普通外部 fork 只有配置了上游归因规则后才会计入。

### 配置了上游的仓库 (`vllm-hust`, `vllm-ascend-hust`)

- 使用 first-parent 历史隔离本组织合入的 PR 与直接提交
- PR merge commit 的净 diff (`diff-tree`) 归因给 PR 作者（通过 GitHub API 查询）
- 纯上游同步提交（subject 匹配 `sync upstream` / `main2main` / `upgrade vllm` 等模式）排除
- 非 PR 的直接提交仅计入组织成员

### 独立仓库（bidkv、diffspec、benchmark、dev-hub、website 等）

- 使用 `git log --numstat --no-merges --no-renames` 全量统计
- 单次超过 50k 变更行的异常大体积导入排除

### 排除规则

- Bot 账号：dependabot[bot], github-actions[bot], copilot-swe-agent[bot] 等
- 身份规范化：统一通过 `.mailmap` 处理
- 指标：`added + deleted` 为排序依据

## 更新方式

运行脚本后，profile/README.md 中 `<!-- contributor-leaderboard:start -->` 和 `<!-- contributor-leaderboard:end -->` 之间的内容会被自动替换。同时更新 `profile/core_contributors.json` 和 website 数据。
