# ProjectFrame — 完整项目协调 · 实现上下文延续 · 恢复与验收

[English](README.md) · [한국어](README.ko.md) · **简体中文**

[![npm](https://img.shields.io/npm/v/projectframe-cli?color=cb3837)](https://www.npmjs.com/package/projectframe-cli)
![Skill](https://img.shields.io/badge/skill-ProjectFrame-2563eb)
![Python](https://img.shields.io/badge/python-3.11%2B-3776ab?logo=python&logoColor=white)
![Runtime](https://img.shields.io/badge/runtime-standard%20library%20%2B%20SQLite-16a34a)
![Checks](https://github.com/ProjectFrame-skills/ProjectFrame/actions/workflows/verify.yml/badge.svg)

## 所需软件

| 软件 | 何时需要 |
|---|---|
| Codex 应用或 CLI | 运行 `$projectframe` 的 AI 宿主，需要支持 skills、本地文件访问和 Python 执行权限。仅安装 npm 包不会提供 AI 宿主。 |
| [Python 3.11+](https://www.python.org/downloads/) | 安装及协调/恢复辅助程序需要。使用包含 [sqlite3](https://docs.python.org/3/library/sqlite3.html) 的 Python 标准库，不需要 pip 包或独立数据库服务器。 |
| [Node.js 18+](https://nodejs.org/en/download)，含 npm | npm 安装方式和 `projectframe` 命令需要。建议使用仍受支持的 Node.js LTS 版本；npm 通常随 Node.js 安装。 |

**npm 方式所需软件：** Codex + Node.js/npm + Python。

```bash
node --version
npm --version
python3 --version
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

Windows 上如使用 `python` 或 `py -3`，请替换相应命令。`PROJECTFRAME_PYTHON` 选择已有解释器，不负责安装 Python。正式 AI 宿主为 Codex Desktop 和 CLI。当前生成的 hook 启动命令面向 POSIX；尚未验证 Windows/Linux 原生行为。额外工具与服务权限取决于实际目标。

### Python 自动查找与安装错误

npm CLI 先检查 PATH 中的 `python3`/`python`（Windows 还检查 `py -3`），再检查 macOS/Linux 上支持的 Homebrew 路径和已安装的 `python@…`。Homebrew 不是必需项；CLI 不会安装 Python 或修改 PATH。

`PROJECTFRAME_PYTHON` 显式选择一个可执行文件。路径或版本错误时会报错，不会悄悄更换解释器。错误区分文件不存在、版本过旧、权限拒绝、Python 检查失败/超时以及安装程序失败。

全局 CLI 安装后，必要时可指定已确认的 Python 路径：

```bash
PROJECTFRAME_PYTHON="/absolute/path/to/python3" projectframe install
```

## 🚀 通过 npm 全局安装

```bash
npm install -g projectframe-cli@latest
projectframe install
```

第一条命令安装全局 CLI，第二条命令安装实际 skill。用 `projectframe --version` 检查 CLI，随后在新的 Codex 对话中调用 `$projectframe`。

**让已批准的项目目标与重要条件持续进入实际实现、上下文压缩后的恢复和后续工作。** ProjectFrame 连接 [SpecFrame](https://github.com/ProjectFrame-skills/SpecFrame)、[SynFrame](https://github.com/ProjectFrame-skills/SynFrame)、实现 skills 和 planning-with-files。产品工作由所选实现 skills 执行，协调宿主检查实际结果及后续工作是否采用当前条件。

## 主要功能

| 功能 | 作用 |
|---|---|
| 完整范围需求 | 连接 SpecFrame 的完整审查和实际用户批准。 |
| 方法选择 | 保留 SynFrame 的学习、探索、比较、组合和采纳责任。 |
| skill 准备与交接 | 检查所选 skills、前提、当前条件及实际接收/应用。 |
| 实现上下文延续 | 观察返回结果并维护准确任务的 planning-with-files 记录。 |
| 恢复 | 在依赖工作前恢复当前原文、所有权及待检查效果。 |
| 进度与控制 | 提供重要事件和运行进度，保留实际延迟与中断。 |
| 验证与验收 | 对照各项需求与实际证据，再取得最终用户验收。 |

## 安装

CLI 无额外 npm 依赖，辅助程序仅用 Python 标准库和 SQLite。不需要专用模型 API key 或推理服务器，工具和权限由宿主提供。

默认目标为 `$CODEX_HOME/skills/projectframe`，否则为 `~/.codex/skills/projectframe`。也可明确指定：

```bash
projectframe install --destination /absolute/path/to/skills/projectframe
```

也可不安装全局 CLI：

```bash
npx --yes projectframe-cli@latest install
```

相同文件直接复用。已有安装不同时会停止；检查差异后，用相同路径选项运行 `projectframe install --replace`。明确替换时，旧目录保存在 skills 目录旁的 `.projectframe-backups` 中。其他 skill 目录和符号链接目标会被拒绝。

本包仅含 ProjectFrame。协调宿主还须按各自契约检查和准备 **SpecFrame、SynFrame、planning-with-files** 及实际选定的实现 skills，并保留用户修改。npm 安装不会自动安装这些组件、修改 hook 配置或授予信任。

## 更新

```bash
projectframe update
```

先将全局 npm CLI 更新到最新版，再运行新版本安装器更新实际 skill。使用相同 `CODEX_HOME`；若自定义过目标，请传入相同 `--destination`。自定义路径不会自动记忆。

已有文件不同时仍会停止。检查差异后，可用带相同目标选项的 `projectframe update --replace` 保留备份并替换。adapter/helper 文件变化需要重新生成 hook 定义并实际审查信任。更新 CLI 本身不会激活 hooks 或替换项目状态。

旧 CLI 不识别 `update` 时，先执行上面的两条全局安装命令。npm 更新成功但 skill 安装失败时，解决提示的问题，再用相同路径选项运行 `projectframe install`；检查差异后仅在需要时添加 `--replace`。

| 命令 | 用途 |
|---|---|
| `projectframe install` | 安装包中包含的 skill。 |
| `projectframe update` | 更新全局 CLI 与实际 skill。 |
| `projectframe --version` | 查看 CLI 版本。 |
| `projectframe --help` | 查看命令与选项。 |

## 使用方法

### 1. 开始新项目

```text
$projectframe
请在 /项目/绝对路径 中创建程序。
明确完整需求，再把批准的条件延续到实现和验证。
```

新工作即使已有需求，也从 SpecFrame 开始。完整结果获得实际批准后，由 SynFrame 选择方法；到实际实现边界再启用该任务的计划记录。

### 2. 改进现有项目

```text
$projectframe
请改进 /项目/绝对路径 中的程序。
保留已有客户数据和确认的访问规则，同时明确并实现变更需求。
```

复用已有行为和有效回答，由负责的 skill 审查受影响需求、选择与交接。

### 3. 继续已保存工作

```text
$projectframe
请继续 /项目/绝对路径 中的 task-id 任务。
读取当前需求、决定与实现记录，检查待确认效果后再继续。
```

明确同一项目与任务。另一对话恢复前须确认旧执行者已停止。先检查实际效果再复用有效结果，避免盲目重复。可随时查询当前阶段、实际结果、问题或下一步。这些示例是 README 用法，不是运行预设。

## 工作结构

```text
SpecFrame → 实际用户批准 → SynFrame → 所选 skills 准备与交接
                                              ↓
实际实现 ↔ 观察与 planning-with-files 记录
    ↓                    ↕
验证 → 最终验收        恢复 → 继续实际工作
```

宿主负责判断、实际观察与后续采用。辅助程序保存已声明协调事实并检查结构边界；文件存在或工具成功本身不证明理解或实现质量。

## 状态与上下文成本

需求与批准保留在 SpecFrame，方法与采纳保留在 SynFrame。协调状态位于项目的 `.projectframe/state.sqlite`；准确任务的 `task_plan.md`、`findings.md` 和 `progress.md` 保存派生实现记录。压缩后实际读取必要原文并检查当前效果，再继续工作。

保存记录、hash 和回执本身不证明语义连续性。一般时间/token/成本收益尚未证实。提醒在宿主可交付时输出，不能强制保证准确墙钟时间，实际延迟与支持空缺应保留。

## 高级用法

遵循 [skill 入口](skills/projectframe/SKILL.md)、[完整运行契约](skills/projectframe/references/operating-contract.md)及[协调/连接接口](skills/projectframe/references/interface.md)。普通用户无需直接编写状态。

只读状态查询应从已安装 skill 确定辅助程序路径，并指定准确任务：

```bash
python3 /absolute/path/to/skills/projectframe/scripts/projectframe.py   --project /absolute/path/to/project --task task-id status
```

### 原生恢复连接

已安装的 `scripts/codex_hook.py config` 按实际路径与文件 hash 生成具体定义。请 Codex 遵循连接接口，保留其他 hooks/设置，**仅合并 ProjectFrame 条目**。通过原生 `/hooks` 审查并信任准确的定义。定义存在不等于已激活。

`bind --project ... --task ... --session ...` 绑定准确任务与实际拥有它的会话。连接器读取当前任务/原文/计划位置，不解析对话历史或执行记录中的命令。压缩后宿主仍须读取必要原文并检查实际效果。macOS 的 Desktop/CLI 观察分别确认，不能据此推广至所有平台的原生行为。

## 开发与验证

```bash
npm test
python3 -m unittest discover -s tests -p test_projectframe.py -v
npm pack --dry-run
```

```text
skills/projectframe/         skill、契约和协调/恢复辅助程序
cli/projectframe.mjs         npm 命令与 Python 安装器连接
cli/python.mjs               Python 查找与错误提示
cli/update.mjs               最新 npm CLI 与 skill 更新
tools/install.py             受保护安装与备份
tests/                       可复现结构与安装检查
.github/workflows/verify.yml Python/Node 检查及隔离安装
```

确定性检查不证明所有目标的语义质量、所有宿主的自动恢复、比较成本收益或实际用户验收。私人协议、对话、运行状态与验证历史不在发行包中。

## 常见问题

- **找不到命令：** 检查 npm 全局可执行路径并重新打开终端，或使用 `npx` 安装方式。
- **看不到 skill：** 检查安装位置与 `SKILL.md`，在新对话中调用。
- **无法运行 Python：** 按 CLI 提示处理，或用 `PROJECTFRAME_PYTHON` 指定已确认的 Python 3.11+ 可执行文件。
- **安装/更新因差异停止：** 检查本地修改，适合替换时在相同命令与路径选项后加入 `--replace`。旧目录会备份。
- **恢复未运行：** 检查准确 hook 信任、任务/会话绑定和安装路径。在依赖工作前读取当前原文，不凭定义文件认定恢复成功。
- **状态缺失、损坏或由其他执行者拥有：** 保留空缺，确认目标项目/任务和旧执行者状态；依实际证据恢复，不覆盖其他任务。

README 结构遵循 [SpecFrame](https://github.com/ProjectFrame-skills/SpecFrame) 和 [SynFrame](https://github.com/ProjectFrame-skills/SynFrame)，行为与安装细节以 ProjectFrame 实现为准。
