# ProjectFrame — Whole Project Coordination · Implementation Continuity · Recovery & Acceptance

**English** · [한국어](README.ko.md) · [简体中文](README.zh.md)

[![npm](https://img.shields.io/npm/v/projectframe-cli?color=cb3837)](https://www.npmjs.com/package/projectframe-cli)
![Skill](https://img.shields.io/badge/skill-ProjectFrame-2563eb)
![Python](https://img.shields.io/badge/python-3.11%2B-3776ab?logo=python&logoColor=white)
![Runtime](https://img.shields.io/badge/runtime-standard%20library%20%2B%20SQLite-16a34a)
![Checks](https://github.com/ProjectFrame-skills/ProjectFrame/actions/workflows/verify.yml/badge.svg)

## Prerequisites

| Program | When it is required |
|---|---|
| Codex app or CLI | The AI host that runs `$projectframe`, with skills, local file access and permission to execute Python. Installing the npm package alone does not provide an AI host. |
| [Python 3.11+](https://www.python.org/downloads/) | Required for installation and coordination/recovery helpers. They use Python's standard library, including [sqlite3](https://docs.python.org/3/library/sqlite3.html); no pip package or separate database server is required. |
| [Node.js 18+](https://nodejs.org/en/download), with npm | Required for the npm installation route and the `projectframe` command. Use a currently supported Node.js LTS release. npm is normally included with Node.js. |

**Required for the npm route:** Codex + Node.js/npm + Python.

```bash
node --version
npm --version
python3 --version
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

On Windows, use `python` or `py -3` if that is your Python command. `PROJECTFRAME_PYTHON` selects an existing executable; it does not install Python. Official AI hosts are Codex Desktop and CLI. The current generated hook launcher targets POSIX; Windows/Linux native behavior has not been verified. Task-specific tools and service permissions depend on the actual goal.

### Python discovery and installation errors

The npm CLI checks `python3`/`python` on PATH (`py -3` on Windows), then supported Homebrew prefixes and installed `python@…` formulae on macOS/Linux. Homebrew is optional; the CLI does not install Python or edit PATH.

`PROJECTFRAME_PYTHON` selects one executable. A bad path or version is reported without silently selecting another interpreter. Errors distinguish a missing executable, an old version, permission denial, a failed/timed-out Python check and an installer failure.

After installing the global CLI, select a known Python directly if necessary:

```bash
PROJECTFRAME_PYTHON="/absolute/path/to/python3" projectframe install
```

## 🚀 Global installation with npm

```bash
npm install -g projectframe-cli@latest
projectframe install
```

The first command installs the global CLI; the second installs the actual skill. Check the CLI with `projectframe --version`. Invoke `$projectframe` in a new Codex conversation after installation.

**Carry a project's approved goals and important conditions through implementation, compaction and resumption.** ProjectFrame coordinates [SpecFrame](https://github.com/ProjectFrame-skills/SpecFrame), [SynFrame](https://github.com/ProjectFrame-skills/SynFrame), implementation skills and planning-with-files. The implementing skills do the product work; the coordinating host checks actual results and whether later work uses the current conditions.

## Features

| Capability | What it does |
|---|---|
| Full-scope requirements | Connects SpecFrame's whole-result review and actual user approval. |
| Method selection | Preserves SynFrame's learning, discovery, comparison, composition and adoption responsibilities. |
| Skill preparation and handoff | Checks selected skills, prerequisites, current conditions and actual receipt/application. |
| Implementation continuity | Observes returned results and maintains the exact task's planning-with-files records. |
| Recovery | Restores current sources, ownership and pending effects before dependent work. |
| Progress and control | Reports important events and running progress, preserving actual delays and interruptions. |
| Validation and acceptance | Compares each requirement with actual evidence before final user acceptance. |

## Installation

The CLI has no additional npm dependencies. Helpers use Python's standard library and SQLite. No dedicated model API key or reasoning server is required; the host supplies tools and permissions.

The default destination is `$CODEX_HOME/skills/projectframe`, or `~/.codex/skills/projectframe`. For another location:

```bash
projectframe install --destination /absolute/path/to/skills/projectframe
```

Or install without a global CLI:

```bash
npx --yes projectframe-cli@latest install
```

An identical installation is reused. If it differs, the installer stops: inspect the differences before using `projectframe install --replace` with the same path options. Explicit replacement preserves the previous directory under `.projectframe-backups` next to the skills directory. Foreign skill folders and symlink destinations are refused.

This package contains ProjectFrame only. The coordinating host must also check and prepare **SpecFrame**, **SynFrame**, **planning-with-files** and the actually selected implementation skills under their own contracts, preserving user edits. Installing this package does not automatically install those components, change hook configuration or grant hook trust.

## Update

```bash
projectframe update
```

Updates the global npm CLI to the latest version, then runs its new skill installer. Use the same `CODEX_HOME`; pass the same `--destination` when you installed to a custom location. Custom locations are not remembered automatically.

The same local-change protection applies. After inspecting differences, use `projectframe update --replace` with the same destination options to preserve a backup and replace the skill. Changed adapter/helper bytes require regenerated hook definitions and native review/trust. Updating the CLI alone does not activate hooks or replace project state.

If an older CLI does not recognize `update`, run the two global installation commands above once. If npm updates but skill installation fails, fix the reported issue and run `projectframe install` with the same path options; inspect differences before adding `--replace`.

| Command | Purpose |
|---|---|
| `projectframe install` | Install the bundled skill. |
| `projectframe update` | Update both the global CLI and installed skill. |
| `projectframe --version` | Display the CLI version. |
| `projectframe --help` | Display commands and options. |

## Usage

### 1. Start a new project

```text
$projectframe
Build a program in /absolute/path/to/project.
Clarify the full requirements, then carry the approved conditions through implementation and validation.
```

New work starts with SpecFrame, including when existing requirements are supplied. After actual whole-result approval, SynFrame selects the method. Implementation activates the task's planning records.

### 2. Improve an existing project

```text
$projectframe
Improve the program in /absolute/path/to/project.
Preserve the existing customer data and confirmed access rules while clarifying and implementing the changes.
```

Existing behavior and valid answers are reused; affected requirements, selection and handoff are reviewed by their responsible skills.

### 3. Resume saved work

```text
$projectframe
Resume task task-id in /absolute/path/to/project.
Read its current requirements, decisions and implementation records, and inspect pending effects before continuing.
```

Identify the same project and task explicitly. Another conversation must first verify the previous actor stopped. Valid effects are inspected and reused rather than blindly repeated. Ask for the current stage, actual results, remaining problems or next action at any time. These examples are README usage, not runtime presets.

## How it works

```text
SpecFrame → actual user approval → SynFrame → selected skills and handoff
                                                   ↓
Implementation ↔ observation and planning-with-files records
       ↓                         ↕
Validation → final acceptance   recovery → continued actual work
```

The host owns judgments, actual observation and downstream consumption. Helpers store declared coordination facts and check structural boundaries; file presence or a successful tool does not prove understanding or implementation quality.

## State and context cost

Requirements and approval remain with SpecFrame; method/adoption remains with SynFrame. Coordination state lives in the project's `.projectframe/state.sqlite`; the exact task's `task_plan.md`, `findings.md` and `progress.md` hold derivative implementation records. After compaction, read required original content and inspect current effects before continuing.

Saved records, hashes and receipts do not establish semantic continuity by themselves. General time/token/cost improvements have not been established. Progress reminders run at host safe points and cannot guarantee exact wall-clock UI delivery; delays and support gaps remain visible.

## Advanced usage

Use the installed [skill entrypoint](skills/projectframe/SKILL.md), [operating contract](skills/projectframe/references/operating-contract.md) and [coordination/connection interface](skills/projectframe/references/interface.md). Ordinary users do not need to write state directly.

For a read-only status query, resolve the helper from the installed skill and identify the exact task:

```bash
python3 /absolute/path/to/skills/projectframe/scripts/projectframe.py   --project /absolute/path/to/project --task task-id status
```

### Native recovery connection

The installed `scripts/codex_hook.py config` generates concrete definitions for the actual paths and hashes. Ask Codex to follow the connection interface and merge **only ProjectFrame's entries**, preserving unrelated hooks and settings. Review and trust the exact definitions through Codex's native `/hooks` flow. Prepared definitions are not activated hooks.

`bind --project ... --task ... --session ...` connects an exact task and its actual owning session. The bridge reads current task/source/plan locations; it does not parse transcripts or execute commands stored in planning text. After compaction, the host still reads required originals and checks actual effects. Desktop and CLI observations were checked separately on macOS; they do not establish every platform's native behavior.

## Development and validation

```bash
npm test
python3 -m unittest discover -s tests -p test_projectframe.py -v
npm pack --dry-run
```

```text
skills/projectframe/         Skill, contracts and coordination/recovery helpers
cli/projectframe.mjs         npm command and Python installer bridge
cli/python.mjs               Python discovery and diagnostics
cli/update.mjs               Latest npm CLI and skill update
tools/install.py             Protected installation and backups
tests/                       Reproducible structural and installer checks
.github/workflows/verify.yml Python/Node checks and isolated installation
```

Deterministic tests do not prove general semantic quality, automatic recovery on every host, comparative cost savings or actual user acceptance. Project-specific agreements, conversations, state and private validation history are excluded from this distribution.

## Troubleshooting

- **Command not found:** check your npm global executable path and reopen the terminal; use the `npx` installation route if needed.
- **Skill not visible:** check the installation path and `SKILL.md`, then invoke it in a new conversation.
- **Python cannot be used:** follow the CLI diagnostic or set `PROJECTFRAME_PYTHON` to a verified Python 3.11+ executable.
- **Install/update stops on differences:** inspect local changes, then use the same command and path options with `--replace` if replacement is appropriate. The previous directory is backed up.
- **Recovery does not run:** check the host's exact hook trust, task/session binding and installed paths. Read current sources before dependent work; do not infer recovery from a definition file.
- **State missing, damaged or owned by another actor:** preserve the gap, confirm the intended project/task and previous actor's status, and recover from actual evidence without overwriting another task.

README organization follows [SpecFrame](https://github.com/ProjectFrame-skills/SpecFrame) and [SynFrame](https://github.com/ProjectFrame-skills/SynFrame); behavior and installation details describe ProjectFrame.

## Release automation

Main pushes and pull requests run the existing runtime, CLI, package and isolated-install checks with Python3.11/Node18 and Python3.13/Node24. Run **Publish release** manually for a test-and-package preflight; it does not publish.

For a stable release, update `package.json`, commit to `main`, wait for verification, then push a matching `v<version>` tag. The release workflow verifies the tag belongs to `main`, repeats verification, packs the distribution, publishes the exact tarball through npm trusted publishing, and attaches artifacts to a GitHub release. Failed checks stop publishing. A retry skips an already-published npm version only when its integrity matches exactly.

Maintainer setup: register the package's npm trusted publisher for this repository, workflow **publish.yml**, environment **npm**, with direct publishing allowed. The GitHub `npm` environment permits `v*` tags. No long-lived npm publishing token is stored in GitHub. Agensi packages, where present, are built as release assets; marketplace review remains separate.
