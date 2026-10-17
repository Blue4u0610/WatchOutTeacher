import {spawnSync} from 'node:child_process';
import {existsSync} from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
const venv=path.join(root,'.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python');
const python=process.env.COURSE_ASSIST_TEST_PYTHON || (existsSync(venv)?venv:process.platform==='win32'?'python':'python3');
const result=spawnSync(python,process.argv.slice(2),{stdio:'inherit',env:{...process.env,PYTHONUTF8:'1'}});
if(result.error) console.error(result.error.message);
process.exit(result.status ?? 1);
