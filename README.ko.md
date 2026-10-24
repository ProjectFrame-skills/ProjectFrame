# ProjectFrame — 프로젝트 전체 조율 · 구현 맥락 유지 · 복구와 수용

[English](README.md) · **한국어** · [简体中文](README.zh.md)

[![npm](https://img.shields.io/npm/v/projectframe-cli?color=cb3837)](https://www.npmjs.com/package/projectframe-cli)
![Skill](https://img.shields.io/badge/skill-ProjectFrame-2563eb)
![Python](https://img.shields.io/badge/python-3.11%2B-3776ab?logo=python&logoColor=white)
![Runtime](https://img.shields.io/badge/runtime-standard%20library%20%2B%20SQLite-16a34a)
![Checks](https://github.com/ProjectFrame-skills/ProjectFrame/actions/workflows/verify.yml/badge.svg)

## 필수 프로그램

| 프로그램 | 필요한 경우 |
|---|---|
| Codex 앱 또는 CLI | `$projectframe`을 실행할 AI 호스트입니다. skills·로컬 파일 접근·Python 실행 권한이 필요하며 npm 패키지만으로 AI 호스트가 제공되지는 않습니다. |
| [Python 3.11 이상](https://www.python.org/downloads/) | 설치와 조율·복구 보조 기능에 필요합니다. [sqlite3](https://docs.python.org/3/library/sqlite3.html)를 포함한 Python 표준 라이브러리를 사용하며 pip 패키지나 별도 데이터베이스 서버는 필요하지 않습니다. |
| [Node.js 18 이상](https://nodejs.org/en/download) + npm | npm 설치 방식과 `projectframe` 명령에 필요합니다. 현재 지원되는 Node.js LTS 버전을 권장하며 npm은 보통 Node.js와 함께 설치됩니다. |

**npm 방식 필수 프로그램:** Codex + Node.js/npm + Python.

```bash
node --version
npm --version
python3 --version
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

Windows에서 Python 명령이 `python` 또는 `py -3`라면 해당 명령을 사용하세요. `PROJECTFRAME_PYTHON`은 이미 설치된 실행 파일을 선택하며 Python을 설치해 주지는 않습니다. 공식 AI 호스트는 Codex 데스크톱과 CLI입니다. 현재 생성 hook launcher는 POSIX용이며 Windows/Linux native 동작은 검증하지 않았습니다. 작업별 추가 도구·서비스 권한은 실제 목표에 따라 달라집니다.

### Python 자동 탐색과 설치 오류

npm CLI는 PATH의 `python3`·`python`을 먼저 확인합니다(Windows는 `py -3`도 확인). macOS/Linux에서는 지원하는 Homebrew 경로와 설치된 `python@…`도 탐색합니다. Homebrew는 선택사항이며 Python을 자동 설치하거나 PATH를 수정하지 않습니다.

`PROJECTFRAME_PYTHON`을 지정하면 해당 실행 파일만 사용합니다. 잘못된 경로·버전일 때 다른 Python으로 조용히 바꾸지 않습니다. 오류는 실행 파일 없음·버전 부족·권한 거부·Python 검사 실패/시간 초과·설치 프로그램 실패를 구분합니다.

전역 CLI 설치 후 필요하면 확인한 Python 경로를 직접 지정할 수 있습니다.

```bash
PROJECTFRAME_PYTHON="/absolute/path/to/python3" projectframe install
```

## 🚀 npm으로 전역 설치

```bash
npm install -g projectframe-cli@latest
projectframe install
```

첫 명령은 전역 CLI를, 두 번째 명령은 실제 skill을 설치합니다. `projectframe --version`으로 CLI 설치를 확인하고 새 Codex 대화에서 `$projectframe`을 호출하세요.

**승인한 목표와 중요한 조건을 실제 구현·대화 압축·재개까지 이어주는 Codex skill입니다.** [SpecFrame](https://github.com/ProjectFrame-skills/SpecFrame), [SynFrame](https://github.com/ProjectFrame-skills/SynFrame), 구현 skills와 planning-with-files를 연결합니다. 제품 구현은 선택한 구현 skill이 맡으며 조율 호스트는 실제 결과와 후속 작업의 조건 반영을 확인합니다.

## 주요 기능

| 기능 | 하는 일 |
|---|---|
| 전체 범위 요구사항 | SpecFrame의 전체 검토와 실제 사용자 승인을 연결합니다. |
| 방법 선택 | SynFrame의 학습·탐색·비교·조합·채택 책임을 유지합니다. |
| skill 준비와 인계 | 선택 skill·전제·현재 조건과 실제 수신·적용을 확인합니다. |
| 구현 맥락 유지 | 반환된 결과를 관측하고 정확한 작업의 planning-with-files 기록을 유지합니다. |
| 복구 | 의존 작업 전 현재 원문·소유권·남은 효과를 복원합니다. |
| 진행과 제어 | 중요 사건과 실행 중 진행을 안내하고 실제 지연·중단을 보존합니다. |
| 검증과 수용 | 요구별 실제 증거를 대조한 뒤 최종 사용자 확인을 받습니다. |

## 설치

CLI는 추가 npm 의존성이 없고 보조 기능은 Python 표준 라이브러리와 SQLite를 사용합니다. 전용 모델 API 키나 추론 서버는 필요하지 않으며 호스트가 도구와 권한을 제공합니다.

기본 위치는 `$CODEX_HOME/skills/projectframe` 또는 `~/.codex/skills/projectframe`입니다. 경로를 직접 지정할 수도 있습니다.

```bash
projectframe install --destination /absolute/path/to/skills/projectframe
```

전역 CLI 없이 설치할 수도 있습니다.

```bash
npx --yes projectframe-cli@latest install
```

같은 파일이면 재사용합니다. 기존 설치가 다르면 멈추므로 차이를 확인한 뒤 같은 경로 옵션으로 `projectframe install --replace`를 사용하세요. 명시적으로 교체하면 이전 폴더를 skills 폴더 옆 `.projectframe-backups`에 보존합니다. 다른 skill 폴더와 심볼릭 링크 목적지는 거부합니다.

이 패키지는 ProjectFrame만 포함합니다. 조율 호스트는 **SpecFrame·SynFrame·planning-with-files**와 실제 선택한 구현 skills를 각 계약에 따라 확인·준비하고 사용자 수정을 보존해야 합니다. npm 설치만으로 이 구성 요소, hook 설정이나 신뢰 승인이 자동 적용되지는 않습니다.

## 업데이트

```bash
projectframe update
```

최신 npm 버전으로 전역 CLI를 갱신한 뒤 새 버전의 설치 도구로 실제 skill도 갱신합니다. 기존과 같은 `CODEX_HOME`을 사용하고 설치 경로를 직접 지정했다면 `update`에도 같은 `--destination`을 넘기세요. 사용자 지정 경로를 자동으로 기억하지는 않습니다.

기존 파일이 다르면 동일한 보호 정책으로 멈춥니다. 차이를 확인한 뒤 같은 경로 옵션의 `projectframe update --replace`로 백업을 보존하며 교체할 수 있습니다. adapter/helper 파일이 바뀌면 hook 정의 재생성과 실제 신뢰 검토가 필요합니다. CLI 업데이트만으로 hook 활성화나 프로젝트 상태 교체를 수행하지 않습니다.

이전 CLI에서 `update`를 인식하지 못하면 위의 전역 설치 명령 두 개를 한 번 실행하세요. npm 갱신 후 skill 설치만 실패했다면 안내된 문제를 해결하고 같은 경로 옵션으로 `projectframe install`을 실행하세요. 차이를 확인한 뒤 필요한 경우에만 `--replace`를 추가합니다.

| 명령 | 역할 |
|---|---|
| `projectframe install` | 패키지에 포함된 skill 설치 |
| `projectframe update` | 전역 CLI와 실제 skill 업데이트 |
| `projectframe --version` | CLI 버전 확인 |
| `projectframe --help` | 명령과 옵션 확인 |

## 사용법

### 1. 새로운 프로젝트 시작

```text
$projectframe
/프로젝트/절대경로에 프로그램을 만들고 싶어.
전체 요구사항을 구체화하고 승인한 조건을 구현과 검증까지 이어가줘.
```

신규 진행은 기존 명세가 있어도 SpecFrame부터 시작합니다. 전체 결과의 실제 승인 후 SynFrame이 방법을 선택하고 실제 구현 경계에서 해당 작업의 계획 기록을 가동합니다.

### 2. 기존 프로젝트 개선

```text
$projectframe
/프로젝트/절대경로의 프로그램을 개선해줘.
기존 고객 데이터와 확정된 접근 정책은 유지하면서 변경할 요구사항을 구체화하고 구현해줘.
```

기존 동작과 유효 답변을 재사용하고 영향을 받는 요구사항·선택·인계를 담당 skill에서 검토합니다.

### 3. 저장된 작업 이어가기

```text
$projectframe
/프로젝트/절대경로의 task-id 작업을 이어가줘.
현재 요구사항·결정·구현 기록을 읽고 남은 효과를 확인한 뒤 계속해줘.
```

같은 프로젝트와 작업을 명시합니다. 다른 대화에서 이어갈 때는 이전 실행 주체가 멈췄는지 먼저 확인합니다. 실제 효과를 먼저 확인해 유효한 결과를 재사용하고 현재 단계·실제 결과·문제·다음 작업을 조회할 수 있습니다. 이 사례는 README 사용법이며 운영 프리셋이 아닙니다.

## 작동 구조

```text
SpecFrame → 실제 사용자 승인 → SynFrame → 선택 skills 준비와 인계
                                              ↓
실제 구현 ↔ 관측·planning-with-files 기록
    ↓                   ↕
검증 → 최종 수용      복구 → 실제 작업 지속
```

호스트는 판단·실제 관측·후속 소비를 담당합니다. 보조 기능은 선언된 조율 사실을 저장하고 구조 경계를 검사하며 파일 존재나 도구 성공만으로 이해·구현 품질을 입증하지 않습니다.

## 상태와 컨텍스트 비용

요구사항·승인은 SpecFrame에, 방법·채택은 SynFrame에 유지합니다. 조율 상태는 프로젝트의 `.projectframe/state.sqlite`에, 파생 구현 기록은 정확한 작업의 `task_plan.md`·`findings.md`·`progress.md`에 유지합니다. 압축 후 필요한 원문을 실제로 읽고 현재 효과를 확인한 뒤 계속합니다.

저장 기록·hash·영수증만으로 의미 보존을 입증하지 않습니다. 일반 시간·토큰·비용 개선은 입증하지 않았습니다. 안내는 호스트의 실행 가능 시점에 전달되므로 정확한 시각을 강제 보장하지 않으며 실제 지연·지원 공백을 남깁니다.

## 고급 사용

[skill 진입점](skills/projectframe/SKILL.md), [전체 운영 계약](skills/projectframe/references/operating-contract.md), [조율·연결 인터페이스](skills/projectframe/references/interface.md)를 따릅니다. 일반 사용자는 상태를 직접 작성할 필요가 없습니다.

읽기 전용 상태 조회 시 설치된 skill에서 보조 코드 경로를 확인하고 정확한 작업을 지정합니다.

```bash
python3 /absolute/path/to/skills/projectframe/scripts/projectframe.py   --project /absolute/path/to/project --task task-id status
```

### 압축·재개 연결

설치된 `scripts/codex_hook.py config`는 실제 경로와 파일 hash에 맞는 정의를 생성합니다. Codex에게 연결 인터페이스에 따라 다른 hook·설정을 보존하며 **ProjectFrame 항목만** 병합하도록 요청하고 네이티브 `/hooks`에서 정확한 정의를 검토·신뢰 승인하세요. 생성 파일만으로 활성화가 완료되지는 않습니다.

`bind --project ... --task ... --session ...`는 정확한 작업과 실제 소유 세션을 연결합니다. bridge는 현재 작업·원문·계획 위치를 읽으며 대화 이력을 파싱하거나 기록 속 명령을 실행하지 않습니다. 압축 후에도 호스트는 필요한 원문과 실제 효과를 확인합니다. macOS의 Desktop/CLI 관측을 구분해 확인했으며 모든 플랫폼의 native 동작으로 확대하지 않습니다.

## 개발 및 검증

```bash
npm test
python3 -m unittest discover -s tests -p test_projectframe.py -v
npm pack --dry-run
```

```text
skills/projectframe/         skill·계약·조율/복구 보조 기능
cli/projectframe.mjs         npm 명령과 Python 설치 도구 연결
cli/python.mjs               Python 탐색과 오류 안내
cli/update.mjs               최신 npm CLI와 skill 업데이트
tools/install.py             보호 설치와 백업
tests/                       재현 가능한 구조·설치 검사
.github/workflows/verify.yml Python/Node 검사와 격리 설치
```

구조 검사가 모든 목표의 의미 품질·모든 환경의 자동 복구·비용 절감·실제 사용자 수용을 입증하지 않습니다. 개인 합의·대화·실행 상태·비공개 검증 이력은 배포하지 않습니다.

## 문제 해결

- **명령을 찾지 못함:** npm 전역 실행 경로를 확인하고 터미널을 다시 열거나 `npx` 설치 방식을 사용하세요.
- **skill이 보이지 않음:** 설치 위치와 `SKILL.md`를 확인하고 새 대화에서 호출하세요.
- **Python을 사용할 수 없음:** CLI 오류 안내를 따르거나 확인한 Python 3.11 이상 실행 파일을 `PROJECTFRAME_PYTHON`으로 지정하세요.
- **설치·업데이트가 차이 때문에 멈춤:** 사용자 수정을 확인하고 교체가 적절하면 같은 명령·경로 옵션에 `--replace`를 추가하세요. 이전 폴더는 백업합니다.
- **복구가 실행되지 않음:** 정확한 hook 신뢰·작업/세션 바인딩·설치 경로를 확인하세요. 의존 작업 전 현재 원문을 읽고 정의 파일만으로 복구 성공을 판단하지 마세요.
- **상태 없음·손상·다른 실행 주체 소유:** 공백을 보존하고 의도한 프로젝트/작업과 이전 실행 주체 상태를 확인하세요. 다른 작업을 덮어쓰지 않고 실제 증거로 복구합니다.

README는 [SpecFrame](https://github.com/ProjectFrame-skills/SpecFrame)·[SynFrame](https://github.com/ProjectFrame-skills/SynFrame)의 구성을 따르며 동작·설치 안내는 ProjectFrame 구현을 기준으로 작성했습니다.
