#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { findPython } from './python.mjs';
import { updateSkill } from './update.mjs';

const root = new URL('../', import.meta.url);
const metadata = JSON.parse(readFileSync(new URL('package.json', root), 'utf8'));
const args = process.argv.slice(2);
const help = `ProjectFrame ${metadata.version}

Usage:
  projectframe install [--destination /absolute/path/to/skills/projectframe] [--replace]
  projectframe update [--destination /absolute/path/to/skills/projectframe] [--replace]
  projectframe --version
  projectframe --help

Installs the bundled Codex skill. Identical installations are reused.
Changed installations require inspection and --replace; previous bytes are backed up.
Does not alter hook configuration/trust or install other skills.
Requires Python 3.11+. Set PROJECTFRAME_PYTHON to choose an explicit interpreter.
Automatically checks Homebrew Python locations on macOS/Linux after PATH.
Default: CODEX_HOME/skills/projectframe, or ~/.codex/skills/projectframe
`;

function main() {
  if (args.length === 0 || (args.length === 1 && ['--help', '-h'].includes(args[0]))) {
    console.log(help); return 0;
  }
  if (args.length === 1 && ['--version', '-v'].includes(args[0])) {
    console.log(metadata.version); return 0;
  }
  let valid = ['install', 'update'].includes(args[0]);
  const seen = new Set();
  for (let i = 1; i < args.length; i++) {
    const flag = args[i];
    if (seen.has(flag)) valid = false;
    seen.add(flag);
    if (flag === '--destination') {
      const value = args[++i];
      if (!value || value.startsWith('-')) valid = false;
    } else if (flag !== '--replace') valid = false;
  }
  if (!valid) { console.error(`Invalid arguments.\n${help}`); return 2; }
  let python;
  try { python = findPython('PROJECTFRAME_PYTHON'); }
  catch (error) { console.error(error.message); return 1; }
  if (args[0] === 'update') return updateSkill(metadata.name, 'projectframe', args.slice(1));
  const result = spawnSync(python.command, [...python.prefix, fileURLToPath(new URL('tools/install.py', root)),
    ...args.slice(1)], { windowsHide: true, stdio: 'inherit' });
  if (result.error) { console.error(`Could not start the skill installer: ${result.error.message}`); return 1; }
  if (result.status !== 0) console.error(`Skill installer failed (${result.signal ? `signal ${result.signal}` : `exit ${result.status}`}). See the installer error above.`);
  return result.status ?? 1;
}

process.exitCode = main();
