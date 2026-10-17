import {spawnSync} from 'node:child_process';
import {existsSync} from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
const venv=path.join(root,'.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python');
const python=process.env.COURSE_ASSIST_TEST_PYTHON || (existsSync(venv)?venv:process.platform==='win32'?'python':'python3');
const reportTests=process.env.CI==='true' && process.argv.includes('unittest');
const result=spawnSync(python,process.argv.slice(2),{stdio:reportTests?'pipe':'inherit',encoding:'utf8',env:{...process.env,PYTHONUTF8:'1'}});
if(reportTests) {
 process.stdout.write(result.stdout || '');
 process.stderr.write(result.stderr || '');
 if(result.status!==0) {
  const failure=(result.stderr || result.stdout || 'Python test command failed').slice(-12000);
  console.log('::error::'+failure.replaceAll('%','%25').replaceAll('\r','%0D').replaceAll('\n','%0A'));
 }
}
if(result.error) console.error(result.error.message);
process.exit(result.status ?? 1);
