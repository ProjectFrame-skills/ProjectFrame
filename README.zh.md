# ProjectFrame

[English](README.md) · [한국어](README.ko.md)

**让已批准的项目目标与重要条件持续进入实际实现、上下文压缩后的恢复和后续工作。** ProjectFrame 是 Codex skill，连接 SpecFrame 的完整需求与用户批准、SynFrame 的学习/探索/比较/选择、所选 skills 的准备与交接、实现中的观察与 planning-with-files 记录，以及逐项验证和最终用户验收。产品实现由所选实现 skills 负责。

## 安装

npm 安装器需要 **Node.js 18+**，辅助程序需要 **Python 3.11+**。先检查 PATH，再检查支持的 Homebrew 路径；可用 `PROJECTFRAME_PYTHON` 指定解释器。

```sh
npm install -g projectframe-cli
projectframe install
```

也可运行 `npx --yes projectframe-cli install`。默认目标为 `$CODEX_HOME/skills/projectframe`，否则为 `~/.codex/skills/projectframe`。可用 `--destination /绝对路径/skills/projectframe` 更改。

相同文件直接复用。若已有安装不同，安装器会停止：先检查差异，再使用 `--replace`。明确替换时，旧目录保存在 skills 目录旁的 `.projectframe-backups` 中。其他 skill 目录和符号链接目标会被拒绝。

本包仅包含 ProjectFrame。协调宿主仍须按各自契约检查和准备独立的 **SpecFrame、SynFrame、planning-with-files**，以及实际选定的实现 skills，并保留用户修改。npm 安装不会自动安装全部候选 skills、修改 hook 配置或授予信任。

## 使用

在新的 Codex Desktop 或 CLI 对话中指定目标与项目：

```text
$projectframe
请在 /项目/绝对路径 中创建或改进程序。
```

新工作即使已有需求，也从 SpecFrame 开始。完整结果获得实际用户批准后交给 SynFrame；到实际实现边界才启用该任务的计划、发现和进度记录。恢复时明确指定同一项目与任务，先检查已有实际效果，再复用有效结果。可随时查询当前阶段、实际结果、剩余问题和下一步。

## 原生恢复连接

已安装的 `scripts/codex_hook.py config` 生成绑定实际路径与文件 hash 的定义。请 Codex 按[连接契约](skills/projectframe/references/interface.md)仅合并 ProjectFrame 的条目并保留其他配置，再通过原生 `/hooks` 审查并信任准确的定义。定义文件存在不等于已经激活。

`bind --project ... --task ... --session ...` 绑定准确任务与实际拥有它的会话。另一个对话恢复前必须先确认旧执行者已停止并检查剩余效果。压缩后宿主仍须实际读取当前原文与记录，并将条件用于后续实现。连接器不会解析对话历史或执行记录中的命令。

当前生成的启动命令面向 POSIX。macOS 上 Desktop 与 CLI 的观察分别记录；未据此证明 Windows/Linux 全部原生行为或一般时间/成本收益。提醒在宿主可交付的执行点输出，不能强制保证准确墙钟时间，实际延迟与支持空缺应保留。

## 更新

```sh
projectframe update
```

先更新全局 npm CLI，再运行新安装器。已有文件不同仍会停止；检查后可用 `projectframe update --replace` 保留备份并替换，也可传入自定义目标。adapter/helper 文件变化需要重新生成定义并实际审查信任。更新 CLI 本身不会激活 hooks 或替换项目状态。

## 开发与证据范围

```sh
npm test
python3 -m unittest discover -s tests -p test_projectframe.py -v
npm pack --dry-run
```

公开内容仅为 skill、协调/hook 辅助程序、安装器和结构检查。确定性检查不证明所有目标的语义质量、所有宿主的自动恢复、比较成本收益或实际最终用户验收。私人协议、对话、运行状态与验证历史不在发行包中。
