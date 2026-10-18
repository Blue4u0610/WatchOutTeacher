import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'bridge'))
import gemini
from common import AppError
from providers import answer_with_fallback, environment
from store import Store

ANSWER={'answer':'B — Violet','explanation_en':'The supplied material defines it.','sources':[], 'basis':'general_knowledge','needs_more_context':False}
def stream(answer=ANSWER):
    raw=json.dumps(answer)
    return '\n'.join(json.dumps(e) for e in [{'type':'init','model':'test'},
       {'type':'message','role':'user','content':'ignored'},
       {'type':'message','role':'assistant','content':raw[:20],'delta':True},
       {'type':'message','role':'assistant','content':raw[20:],'delta':True},
       {'type':'result','status':'success'}])

class GeminiTests(unittest.TestCase):
    def test_stream_only_assistant_and_complete_result(self):
        self.assertEqual(gemini.parse_output(stream()),ANSWER)
        for out in [stream().rsplit('\n',1)[0], 'progress\n'+stream(), '[]', stream()+'\n'+json.dumps({'type':'result','status':'error','error':{'message':'quota'}})]:
            with self.assertRaises(AppError): gemini.parse_output(out)
        for kind in ['tool_use','tool_result']:
            with self.assertRaises(AppError) as caught: gemini.parse_output(json.dumps({'type':kind})+'\n'+stream())
            self.assertEqual(caught.exception.code,'tool_policy')

    def test_direct_node_npm_resolution_with_spaces_and_no_shell(self):
        with tempfile.TemporaryDirectory(prefix='gemini npm space ') as d:
            root=Path(d)/'node_modules/@google/gemini-cli';root.mkdir(parents=True)
            (root/'package.json').write_text(json.dumps({'name':'@google/gemini-cli','bin':{'gemini':'entry.js'}}))
            (root/'entry.js').write_text('')
            with patch('gemini.locate',return_value='/trusted/node.exe'),patch('gemini.environment',return_value={'PATH':d}),patch('gemini.shutil.which',return_value=None),patch.dict(os.environ,{},clear=True):
                self.assertEqual(gemini.command(),['/trusted/node.exe',str((root/'entry.js').resolve())])
                (root/'package.json').write_text(json.dumps({'name':'@google/gemini-cli','bin':{'gemini':'../../escape.js'}}))
                self.assertIsNone(gemini.command())

    def test_question_cannot_expand_at_files_and_isolation_parameters(self):
        provider=gemini.GeminiProvider()
        prompt='Question about @/private/file and learner@example.com'
        def fake_run(args,d,encoded,cancel,timeout,**kw):
            self.assertNotIn('@',encoded)
            self.assertEqual(json.loads(encoded)['course_task'],prompt)
            self.assertEqual(args[:2],['node','gemini.js'])
            self.assertEqual(args[args.index('--model')+1],'flash')
            self.assertIn('--admin-policy',args);self.assertIn('--allowed-mcp-server-names',args)
            self.assertEqual(kw['env_overrides']['GEMINI_CLI_TRUST_WORKSPACE'],'true')
            settings=json.loads((Path(d)/'.gemini/settings.json').read_text())
            self.assertEqual(settings['tools']['core'],[])
            self.assertFalse(settings['hooksConfig']['enabled'])
            self.assertEqual(settings['security']['auth']['enforcedType'],'oauth-personal')
            self.assertEqual((Path(d)/'.gemini/.env').read_text(),'')
            return stream()
        with patch.object(provider,'detect',return_value={'available':True}),patch('gemini.command',return_value=['node','gemini.js']),patch('gemini.run',side_effect=fake_run):
            self.assertEqual(provider.answer(prompt,'flash',threading.Event(),10),ANSWER)
        for key in ['GEMINI_API_KEY','GOOGLE_API_KEY','GOOGLE_APPLICATION_CREDENTIALS','GEMINI_CLI_HOME','NODE_OPTIONS']:
            with patch.dict(os.environ,{key:'must-not-inherit'}): self.assertNotIn(key,environment())

    def test_cleanup_is_scoped_to_owned_cache_and_keeps_credentials(self):
        with tempfile.TemporaryDirectory() as d:
            home=Path(d);root=home/'.gemini';root.mkdir()
            workspace=home/'watchoutteacher-gemini-abc';workspace.mkdir()
            slug='watchoutteacher-gemini-abc'
            (root/'projects.json').write_text(json.dumps({'projects':{os.path.normcase(str(workspace.resolve())):slug}}))
            auth=root/'oauth_creds.json';auth.write_text('untouched fixture')
            for kind,owner in [('tmp',str(workspace.resolve())),('history','other-workspace')]:
                cache=root/kind/slug;cache.mkdir(parents=True);(cache/'.project_root').write_text(owner);(cache/'record').write_text('private fixture')
            gemini.cleanup_records(workspace,home)
            self.assertFalse((root/'tmp'/slug).exists());self.assertTrue((root/'history'/slug/'record').exists())
            self.assertEqual(auth.read_text(),'untouched fixture')

    def test_detect_requires_google_cache_and_does_not_open_credentials(self):
        with tempfile.TemporaryDirectory() as d,patch('gemini.Path.home',return_value=Path(d)),patch('gemini.command',return_value=['node','gemini.js']),patch('gemini.run',side_effect=['0.64.0','--output-format --model --extensions --admin-policy --skip-trust --prompt --allowed-mcp-server-names']):
            status=gemini.GeminiProvider().detect()
            self.assertEqual(status['code'],'auth');self.assertFalse(status['available'])

    def test_host_routes_course_excerpts_and_preferences_to_gemini(self):
        from host import Host
        captured=[]
        class Fake:
            def answer(self,prompt,model,cancel,timeout):
                captured.append((prompt,model))
                return {**ANSWER,'basis':'course_material','sources':[{'source_id':'S1'}]}
        with tempfile.TemporaryDirectory() as d:
            host=Host(Path(d),providers={'gemini':Fake()})
            try:
                cid=host.store.create('Gemini fixture')['settings']['active_course']
                host.store.add(cid,'material.md',{'units':[{'number':1,'kind':'text','text':'Lumen means Violet'}],'warnings':[]})
                host.store.save_settings({'primary':'gemini','fallback':False,'gemini_model':'flash','answer_instructions':'Paraphrase the evidence.'})
                result=host.ask({'selection':'What color is Lumen?','context':'A Amber B Violet','context_complete':True},threading.Event(),'fixture')
                self.assertEqual(result['diagnostics']['provider'],'gemini')
                self.assertEqual(result['sources'][0]['document'],'material.md')
                self.assertEqual(captured[0][1],'flash')
                self.assertIn('Paraphrase the evidence.',captured[0][0])
                self.assertIn('Lumen means Violet',captured[0][0])
            finally: host.cleanup()

    def test_explicit_backups_migration_and_three_provider_budget(self):
        calls=[]
        class Fake:
            def __init__(self,name): self.name=name
            def answer(self,prompt,model,cancel,timeout):
                calls.append((self.name,timeout))
                if self.name!='gemini': raise AppError('rate_limit','limited')
                return ANSWER
        providers={n:Fake(n) for n in ['codex','claude','gemini']}
        with self.assertRaises(AppError): answer_with_fallback(providers,'codex',True,'',{},threading.Event(),10,{})
        self.assertEqual([n for n,_ in calls],['codex','claude'])
        calls.clear()
        result=answer_with_fallback(providers,'codex',True,'',{},threading.Event(),10,{},fallback_providers=['gemini'])
        self.assertEqual([n for n,_ in calls],['codex','gemini']);self.assertEqual(result['diagnostics']['provider'],'gemini')
        calls.clear()
        answer_with_fallback(providers,'codex',True,'',{},threading.Event(),10,{},fallback_providers=['codex','claude','gemini'])
        self.assertEqual([n for n,_ in calls],['codex','claude','gemini'])
        self.assertTrue(all(0<t<=6.5 for _,t in calls[:2]))
        with tempfile.TemporaryDirectory() as d:
            store=Store(Path(d));self.assertEqual(store.settings()['fallback_providers'],['codex','claude'])
            store.save_settings({'primary':'gemini','gemini_model':'flash','fallback_providers':[]})
            self.assertEqual(Store(Path(d)).settings()['gemini_model'],'flash')
            for bad in [['gemini','gemini'],['invalid'],None,'codex']:
                with self.assertRaises(AppError): store.save_settings({'fallback_providers':bad})

if __name__=='__main__': unittest.main()
