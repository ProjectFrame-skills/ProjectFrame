# ProjectFrame

[한국어](README.ko.md) · [简体中文](README.zh.md)

**Carry a project's approved goals and important conditions through implementation, compaction and resumption.** ProjectFrame is a Codex skill that coordinates SpecFrame, SynFrame, implementation skills and planning-with-files.

It connects whole-scope requirements and actual user approval; knowledge discovery, comparison and adoption; selected-skill preparation and handoff; observed work, persistent implementation records and recovery; and requirement-level validation followed by final user acceptance. The implementing skills do the product work. The coordinating host checks actual results and whether later work uses the current conditions.

## Install

Requires **Node.js 18+** for this npm installer and **Python 3.11+** for the helpers. Python is discovered on PATH, then supported Homebrew locations. Set `PROJECTFRAME_PYTHON` to an explicit executable if needed.

```sh
npm install -g projectframe-cli
projectframe install
```

Or install without a global CLI:

```sh
npx --yes projectframe-cli install
```

The default destination is `$CODEX_HOME/skills/projectframe`, or `~/.codex/skills/projectframe`. Use `--destination /absolute/path/to/skills/projectframe` to choose another location. An identical installation is reused. If it differs, the installer stops: inspect the differences before using `--replace`. Explicit replacement preserves the previous directory under `.projectframe-backups` next to the skills directory. Foreign skill folders and symlink destinations are refused.

This package contains ProjectFrame only. Its workflow also requires **SpecFrame**, **SynFrame** and **planning-with-files**, plus the implementation skills actually selected for the user's project. The coordinating host must check and prepare those components under their own contracts; it must preserve existing user edits. Installing this package does not install every candidate skill, change hook configuration or grant hook trust.

## Use

Start a new Codex Desktop or CLI conversation and invoke the skill with a goal and project:

```text
$projectframe
Build or improve the project in /absolute/path/to/project.
```

New work starts with SpecFrame, including when existing requirements are supplied. After actual whole-result approval, SynFrame selects the method. Implementation activates the task's planning records. To resume, explicitly identify the same project and task; valid effects are inspected and reused rather than blindly repeated. Ask for current stage, actual results, remaining problems or the next action at any time.

## Native recovery connection

The installed `scripts/codex_hook.py` can generate concrete definitions with `config`. Ask Codex to use the installed skill's [connection contract](skills/projectframe/references/interface.md) to generate and merge **only ProjectFrame's entries** with your existing hooks, preserving unrelated entries. Review and trust the exact definitions through Codex's native `/hooks` flow. A prepared definition is not an activated hook.

The bridge must bind an exact project, task and owning session using `bind --project ... --task ... --session ...`. Another conversation must first verify the old actor stopped and restore/take over the identified task. The bridge reads current task/source/plan locations; it does not parse transcripts or execute commands stored in planning text. After compaction, the host still reads the required original content and checks actual effects before continuing.

The current generated launcher targets POSIX hosts. Desktop and CLI observations were checked separately on macOS. Windows/Linux native behavior and general performance gains are not established by these observations. Progress reminders run at host safe points; they cannot guarantee exact wall-clock UI delivery. Delays and support gaps must remain visible.

## Update

```sh
projectframe update
```

This updates the global npm CLI and then runs its new skill installer. The same local-change protection applies. After inspecting differences, use `projectframe update --replace` to preserve a backup and replace the skill. Custom destinations can be passed to either command. Changed adapter/helper bytes require regenerated hook definitions and native review/trust; the installer does not bypass that boundary. Updating the CLI alone does not activate hooks or replace project state.

## Development and scope

```sh
npm test
python3 -m unittest discover -s tests -p test_projectframe.py -v
npm pack --dry-run
```

The repository includes the skill, coordination/hook helpers, installer and structural checks. Deterministic tests do not prove general semantic quality, automatic recovery on every host, comparative cost savings or actual user acceptance. Project-specific agreements, conversations, state and private validation history are not part of this distribution.
