import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync, existsSync, rmSync, symlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
const root = fileURLToPath(new URL('../', import.meta.url));
const cli = join(root, 'cli/projectframe.mjs');
const version = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8')).version;
const run = (args, env = process.env) => spawnSync(process.execPath, [cli, ...args], { encoding: 'utf8', env });

test('help/version need no Python and rejected arguments never install', () => {
  const env = { ...process.env, PROJECTFRAME_PYTHON: '/missing-python' };
  assert.equal(run(['--help'], env).status, 0);
  assert.equal(run(['--version'], env).stdout.trim(), version);
  for (const args of [['unknown'], ['install','--destination'], ['install','--replace','--replace'], ['install','--bad'], ['install','--destination','-bad'], ['--version','--replace']]) {
    assert.equal(run(args, env).status, 2, JSON.stringify(args));
  }
  assert.equal(run(['install'], env).status, 1);
});

test('actual install reuses identical bytes, refuses implicit changes, backs up explicit replacement and protects other skills', () => {
  const folder = mkdtempSync(join(tmpdir(), 'projectframe npm '));
  try {
    const destination = join(folder, 'skills/projectframe');
    const flags = ['--destination', destination];
    const first = run(['install', ...flags]); assert.equal(first.status, 0, first.stderr);
    const installed = JSON.parse(first.stdout);
    assert.equal(installed.files, 6);
    assert.ok(existsSync(join(destination, 'scripts/projectframe.py')));
    const second = run(['install', ...flags]); assert.equal(second.status, 0, second.stderr);
    assert.equal(JSON.parse(second.stdout).unchanged, true);
    const marker = join(destination, 'custom.txt'); writeFileSync(marker, 'keep these exact bytes\r\n');
    const refused = run(['install', ...flags]); assert.notEqual(refused.status, 0);
    assert.match(refused.stderr, /inspect local changes/);
    assert.equal(readFileSync(marker, 'utf8'), 'keep these exact bytes\r\n');
    const replaced = run(['install', '--replace', ...flags]); assert.equal(replaced.status, 0, replaced.stderr);
    const updated = JSON.parse(replaced.stdout);
    assert.deepEqual(installed.sha256, updated.sha256);
    assert.equal(readFileSync(join(updated.backup, 'custom.txt'), 'utf8'), 'keep these exact bytes\r\n');
    writeFileSync(join(destination, 'SKILL.md'), 'another skill');
    assert.notEqual(run(['install', ...flags, '--replace']).status, 0);
    assert.equal(readFileSync(join(destination, 'SKILL.md'), 'utf8'), 'another skill');
    if (process.platform !== 'win32') {
      const linked = join(folder, 'linked'); symlinkSync(destination, linked);
      assert.notEqual(run(['install','--destination', linked,'--replace']).status, 0);
    }
    assert.equal(existsSync(join(folder, 'hooks.json')), false);
  } finally { rmSync(folder, { recursive: true, force: true }); }
});
