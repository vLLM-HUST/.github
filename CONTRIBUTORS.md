# Contributor Identity & Methodology

本文档记录 vLLM-HUST 组织贡献者排行榜的统计方法、人员身份、账号归并规则和 GitHub 映射表。

## 身份信息的唯一事实来源

`profile/people.json` 是人员身份的唯一事实来源，维护一个人对应的中文名、英文名、
GitHub 主账号、历史账号、Git author、邮箱、身份、单位、导师和页面分类信息。

- `aliases`、`git_names`、`emails` 只负责把多个提交身份归并为同一个人。
- `profiles.vllm_hust` 记录该人员在 vLLM-HUST 中的身份、参与方向、导师以及属于
  核心成员、参与人员、工程师/助理或外部贡献者的关系。
- `.mailmap` 是 Git 工具层的兼容映射，不是人员档案的替代品。
- `profile/core_contributors.json` 和网站中的同名数据都是生成结果，不应手工维护。
- 身份变更后应运行 `--profiles-only`，并验证组织档案与网站快照完全一致。

### 近期确认的人员信息

| 人员 | Canonical GitHub | 已归并身份 | 身份/单位 | 指导老师 | 页面分类 |
| --- | --- | --- | --- | --- | --- |
| 田景远 | [CubeLander](https://github.com/CubeLander) | Jingyuan Tian、Jingyuan、Fletcher Tian、Flecther Tian | 实习生 | 张书豪 | 按核心仓库真实贡献判定 |
| 匡明轩 | [sad-and-bad1231](https://github.com/sad-and-bad1231) | MingXuan Kuang、Sadboineedluv；`1648910756@qq.com`、`2976582520@qq.com` | 团队成员 | 张书豪 | 按核心仓库真实贡献判定 |
| 马俊豪 | [kms12425](https://github.com/kms12425) | kms12425-ctrl、Jun Hao Ma、JunHao Ma | 学生 | 张书豪 | 按核心仓库真实贡献判定 |
| sunYangGitHub | [sunYangGitHub](https://github.com/sunYangGitHub) | sunyang、sunYangGitHub | 外校实习生 | 张书豪 | 参与人员 |
| luoxiaohei | [luoxiaohei](https://github.com/luoxiaohei) | `luoxiaohei@ppio.com`、`luoxiaohei@gitlab.paigod.work` | 派欧云工程师 | — | 工程师/助理 |
| 张俊辉 | [junhuizhang-boop](https://github.com/junhuizhang-boop) | Junhui Zhang、`junhui.zhang@novita.ai` | 派欧云工程师 | — | 工程师/助理 |

未获得中文姓名时保留已确认的 GitHub 主账号作为公开名称，不根据邮箱或用户名猜测
实名。后续获得实名后只更新 `profile/people.json`，再由脚本同步生成数据。

## Git author 合并规则 (`.mailmap`)

组织同时使用 `.mailmap` 规范化 Git author 身份。以下为当前兼容映射：

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
| luoxiaohei | luoxiaohei@ppio.com, luoxiaohei@gitlab.paigod.work | 与 moonandlife 使用不同邮箱；已确认为派欧云工程师 |
| Jeffrey (Huawei) | jeffrey.wangsheng@huawei.com | 华为员工，非 Jeffrey Wang (moonandlife) |
| Jeffrey Li | jeffrey-dot-li@users.noreply.github.com | 另一位 Jeffrey，非 moonandlife |

## 课题组人员 GitHub 身份对照

下表是 `profile/people.json` 的人可读快照。主账号用于页面链接；其他 GitHub
账号或提交作者身份作为 canonical person 的别名归并，不会产生重复人员。只有
经 GitHub 验证可访问的主账号才生成页面链接，提交作者身份不等同于 GitHub 账号。

### 主要成员

| 姓名 | GitHub 主账号 | 其他账号/提交身份 | 备注 |
| --- | --- | --- | --- |
| 张书豪 | [ShuhaoZhangTony](https://github.com/ShuhaoZhangTony) | chooper26、QixinZhang26、qixinzhang2601 | 同一人 |
| 张睿诚 | [KimmoZAG](https://github.com/KimmoZAG) | — | — |
| 刘俊 | [iliujunn](https://github.com/iliujunn) | — | — |
| 李昶吾 | [Li-changwu](https://github.com/Li-changwu) | — | — |
| 李旭恒 | [sssarrior](https://github.com/sssarrior) | — | — |
| 高鸿儒 | [hongrugao](https://github.com/hongrugao) | — | — |
| 曹哲 | [xmdhb](https://github.com/xmdhb) | — | — |
| 彭浩然 | [Tkhkrnx](https://github.com/Tkhkrnx) | — | — |
| 王明琪 | [MingqiWang-coder](https://github.com/MingqiWang-coder) | mingqiwang682-boop | 同一人 |
| 杨锦昀 | [Yang-YJY](https://github.com/Yang-YJY) | — | — |
| 王子澳 | [ZeroJustMe](https://github.com/ZeroJustMe) | — | — |
| 张森磊 | [zslchase](https://github.com/zslchase) | — | — |
| 陈彦博 | [cybber695](https://github.com/cybber695) | — | — |
| 朱鑫材 | [Pygone](https://github.com/Pygone) | — | — |
| 陈德斌 | [pluviophile-chen](https://github.com/pluviophile-chen) | — | — |
| 王杰 | [WMASTER123](https://github.com/WMASTER123) | — | — |
| 李庚 | [Anjiangy](https://github.com/Anjiangy) | — | 沿用此前用户确认的账号映射 |
| 宋功轩 | 待确认 | — | 已确认成员，尚未确认 GitHub ID |
| 彭成 | 待确认 | — | 已确认成员，尚未确认 GitHub ID |
| 高西岭 | [XilingGao](https://github.com/XilingGao) | Coisinixixi | 同一人 |
| 王胜 | [moonandlife](https://github.com/moonandlife) | — | — |
| 程月甲 | [SuccinctPaul](https://github.com/SuccinctPaul) | — | — |
| 龙斌 | — | — | 已确认无 GitHub ID |
| 毛言粲 | [yancanmao](https://github.com/yancanmao) | — | — |

### 实习及补充成员

| 姓名 | GitHub 主账号 | 其他账号/提交身份 | 备注 |
| --- | --- | --- | --- |
| 马俊豪 | [kms12425](https://github.com/kms12425) | kms12425-ctrl | 同一人 |
| 万瑞鹏 | [wrp-wrp](https://github.com/wrp-wrp) | — | — |
| 杜雨枫 | [LuckyWindovo](https://github.com/LuckyWindovo) | — | — |
| 匡明轩 | [sad-and-bad1231](https://github.com/sad-and-bad1231) | Sadboineedluv（提交身份） | 本次名单写作“况明轩”；暂沿用此前多次确认的姓名 |
| 周雨桐 | [FirmamentumX](https://github.com/FirmamentumX) | — | — |
| 董君瑶 | [carsontung666](https://github.com/carsontung666) | — | — |
| 田景远 | [CubeLander](https://github.com/CubeLander) | — | — |
| 赵建军 | [curryzjj](https://github.com/curryzjj) | Jianjun Zhao | 沿用此前确认的中文名 |
| 邱瑞杰 | [Jerry01020](https://github.com/Jerry01020) | — | — |
| 雷欣妍 | [leixy2004](https://github.com/leixy2004) | — | — |
| 路庆浩 | [Luqhhh](https://github.com/Luqhhh) | — | — |

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
| 田景远 | [CubeLander](https://github.com/CubeLander) | 人工确认；实习生，指导老师张书豪 |
| pygone | [Pygone](https://github.com/Pygone) | noreply |
| aly16-k | [aly16-k](https://github.com/aly16-k) | noreply |
| 刘世锋 | [Remygred](https://github.com/Remygred) | 人工确认；华科大三实习生，指导老师张书豪 |
| 曹哲 | [xmdhb](https://github.com/xmdhb) | 人工确认；即将入学的研究生，指导老师张书豪 |
| 李庚 | [Anjiangy](https://github.com/Anjiangy) | 人工确认；马上入学的华科研究生，指导老师张书豪 |
| 杜忠承 | [dzcixy](https://github.com/dzcixy) | 人工确认；学生，指导老师黄禹 |
| 徐晨曦 | [xsun2001](https://github.com/xsun2001) | 外部贡献者；港科大（广州），流水线并行解码与均衡微批调度 |
| 匡明轩 | [sad-and-bad1231](https://github.com/sad-and-bad1231) | 人工确认；Sadboineedluv / MingXuan Kuang 为同一人，指导老师张书豪 |
| 马俊豪 | [kms12425](https://github.com/kms12425) | 人工确认；kms12425-ctrl / JunHao Ma 为同一人，指导老师张书豪 |
| sunYangGitHub | [sunYangGitHub](https://github.com/sunYangGitHub) | 人工确认；外校实习生，指导老师张书豪 |
| luoxiaohei | [luoxiaohei](https://github.com/luoxiaohei) | 人工确认；派欧云工程师 |
| 张俊辉 | [junhuizhang-boop](https://github.com/junhuizhang-boop) | 人工确认；派欧云工程师 |
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
