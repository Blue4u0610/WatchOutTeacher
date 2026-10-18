"""Offline verification against the real pinned Gemini CLI bundle. No account or model call."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'bridge'))
from gemini import command, isolation
from providers import environment

cmd=command()
if not cmd: raise SystemExit('Install @google/gemini-cli@0.64.0 before this smoke test')
bundle=Path(cmd[1]).parent
# Test-only introspection of the pinned release, never a production dependency on internals.
def module_containing(marker):
    for path in bundle.glob('chunk-*.js'):
        if marker in path.read_text(encoding='utf-8'): return path.as_uri()
    raise RuntimeError('Pinned Gemini CLI bundle layout changed')
settings_module=module_containing('function loadSettings(workspaceDir')
policy_module=module_containing('async function createPolicyEngineConfig(')
with tempfile.TemporaryDirectory(prefix='watchoutteacher-gemini-') as d:
    p=Path(d);env={**environment(),**isolation(d)}
    home=p/'fixture-home';(home/'.gemini').mkdir(parents=True)
    (home/'.gemini/.env').write_text('GEMINI_API_KEY=must-not-load\n',encoding='utf-8')
    (home/'.gemini/settings.json').write_text(json.dumps({
        'tools':{'core':['run_shell_command'],'discoveryCommand':'must-not-run'},
        'mcp':{'serverCommand':'must-not-run','allowed':['old-server']},
        'hooksConfig':{'enabled':True},'skills':{'enabled':True},
        'experimental':{'enableAgents':True,'autoMemory':True},
        'security':{'auth':{'selectedType':'gemini-api-key'}},
        'context':{'fileName':'GEMINI.md'},'model':{'name':'wrong-model'}
    }),encoding='utf-8')
    env['GEMINI_CLI_HOME']=str(home)
    js='''
import assert from 'node:assert/strict';
const {loadSettings}=await import(SETTINGS_MODULE);
const {createPolicyEngineConfig}=await import(POLICY_MODULE);
const s=loadSettings();
assert.equal(s.isTrusted,true); assert.deepEqual(s.errors,[]);
assert.deepEqual(s.merged.tools.core,[]); assert.equal(s.merged.tools.discoveryCommand,'');
assert.equal(s.merged.hooksConfig.enabled,false); assert.equal(s.merged.skills.enabled,false);
assert.equal(s.merged.experimental.enableAgents,false); assert.equal(s.merged.experimental.autoMemory,false);
assert.equal(s.merged.mcp.serverCommand,'');
assert.equal(s.merged.mcp.allowed.length,1); assert.match(s.merged.mcp.allowed[0],/watchoutteacher-gemini-.*-no-mcp$/);
assert.equal(s.merged.security.auth.selectedType,'oauth-personal');
assert.equal(s.merged.security.auth.enforcedType,'oauth-personal');
assert.equal(s.merged.model.name,'auto'); assert.equal(s.merged.model.maxSessionTurns,2);
assert.equal(s.merged.general.maxAttempts,1); assert.equal(s.merged.telemetry.enabled,false);
assert.match(s.merged.context.fileName,/watchoutteacher-gemini-.*-no-context.md$/);
assert.equal(process.env.GEMINI_API_KEY,undefined);
const policy=await createPolicyEngineConfig({adminPolicyPaths:[process.cwd()+'/deny-tools.toml']},'default',process.cwd()+'/empty',false);
assert(policy.rules.some(r=>r.toolName==='*' && r.decision==='deny' && r.priority===5.999));
console.log('PASS real Gemini CLI: workspace overrides, OAuth, no hooks/tools/agents, MCP allowlist, dotenv isolation and admin deny policy');
'''.replace('SETTINGS_MODULE',json.dumps(settings_module)).replace('POLICY_MODULE',json.dumps(policy_module))
    result=subprocess.run([cmd[0],'--input-type=module','-e',js],cwd=d,env=env,text=True,encoding='utf-8',capture_output=True,timeout=25)
    if result.returncode: raise SystemExit(result.stderr[-5000:])
    print(result.stdout.strip())
