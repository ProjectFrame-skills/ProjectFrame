# ProjectFrame

[English](README.md) · [简体中文](README.zh.md)

**승인한 목표와 중요한 조건을 실제 구현·대화 압축·재개까지 이어주는 Codex skill입니다.** SpecFrame의 전체 요구 정의와 사용자 승인, SynFrame의 학습·탐색·비교·선택, 선택 skill 준비·인계, 구현 중 관측·planning-with-files 기록·후속 소비, 복구와 최종 검증·사용자 수용을 연결합니다. 제품 구현은 선택된 구현 skill이 맡습니다.

## 설치

npm 설치 도구에는 **Node.js 18 이상**, 보조 기능에는 **Python 3.11 이상**이 필요합니다. PATH와 지원하는 Homebrew 경로에서 Python을 찾으며, 필요하면 `PROJECTFRAME_PYTHON`에 실행 파일 경로를 지정합니다.

```sh
npm install -g projectframe-cli
projectframe install
```

전역 CLI 설치 없이 `npx --yes projectframe-cli install`도 사용할 수 있습니다. 기본 위치는 `$CODEX_HOME/skills/projectframe` 또는 `~/.codex/skills/projectframe`입니다. `--destination /절대경로/skills/projectframe`으로 변경합니다.

같은 파일이면 재사용합니다. 기존 설치가 다르면 멈추므로 차이를 확인한 뒤 `--replace`를 사용하세요. 명시적으로 교체하면 이전 폴더를 skills 폴더 옆 `.projectframe-backups`에 보존합니다. 다른 skill 폴더와 심볼릭 링크 목적지는 거부합니다.

이 패키지는 ProjectFrame만 포함합니다. 조율 호스트는 별도 구성인 **SpecFrame·SynFrame·planning-with-files**와 실제 선택한 구현 skills를 각 계약에 따라 확인·준비해야 합니다. 기존 사용자 수정도 보존합니다. npm 설치만으로 다른 모든 skills, hook 설정이나 신뢰 승인이 자동 적용되지는 않습니다.

## 사용

새 Codex 데스크톱 또는 CLI 대화에서 프로젝트와 목표를 지정합니다.

```text
$projectframe
/프로젝트/절대경로의 프로그램을 만들거나 개선해줘.
```

신규 진행은 기존 명세가 있어도 SpecFrame부터 시작합니다. 전체 결과의 실제 승인 후 SynFrame으로 연결하고, 실제 구현 경계에서 작업별 계획·발견·진행 기록을 가동합니다. 재개할 때는 같은 프로젝트와 작업을 명시합니다. 이전 효과를 먼저 확인해 재사용하고, 현재 단계·실제 결과·문제·다음 작업을 조회할 수 있습니다.

## 압축·재개 연결

설치된 `scripts/codex_hook.py config`는 현재 경로와 파일 hash에 맞는 hook 정의를 생성합니다. Codex에게 [연결 계약](skills/projectframe/references/interface.md)에 따라 기존 설정의 다른 항목을 보존하며 ProjectFrame 정의만 병합하도록 요청하고, 네이티브 `/hooks`에서 정확한 정의를 검토·신뢰 승인하세요. 생성된 파일만으로 활성화가 완료되지는 않습니다.

`bind --project ... --task ... --session ...`는 해당 작업의 실제 소유 세션과 연결합니다. 다른 대화에서 재개할 때는 이전 실행 주체의 종료·남은 효과를 먼저 확인해야 합니다. 압축 후에도 호스트는 현재 원문과 기록을 실제로 읽고 다음 구현에 적용합니다. 대화 이력을 파싱하거나 기록 속 명령을 실행하는 방식이 아닙니다.

현재 생성 launcher는 POSIX용이며 macOS의 Desktop/CLI 관측을 구분해 확인했습니다. Windows/Linux 전체 native 실행이나 일반 비용·시간 개선은 입증하지 않았습니다. 안내는 호스트의 실행 가능 시점에 전달되므로 정확한 시각을 강제 보장하지 않으며 실제 지연·지원 공백을 남겨야 합니다.

## 업데이트

```sh
projectframe update
```

최신 전역 npm CLI를 받은 뒤 새 설치 도구를 실행합니다. 기존 파일이 다르면 동일한 보호 정책으로 멈춥니다. 차이를 확인한 뒤 `projectframe update --replace`로 백업을 보존하며 교체할 수 있습니다. 사용자 지정 위치도 전달할 수 있습니다. adapter/helper 파일이 바뀌면 hook 정의 재생성과 실제 신뢰 검토가 필요합니다. CLI 업데이트만으로 hook 활성화나 프로젝트 상태 교체를 수행하지 않습니다.

## 검증과 공개 범위

```sh
npm test
python3 -m unittest discover -s tests -p test_projectframe.py -v
npm pack --dry-run
```

공개 내용은 skill·연결 보조 기능·설치 도구·구조 검사입니다. 구조 검사가 모든 목표의 의미 품질·모든 환경의 복구·비용 절감·실제 최종 사용자 수용을 입증하지 않습니다. 개인 합의·대화·실행 상태·비공개 검증 이력은 배포하지 않습니다.
