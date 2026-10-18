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
    return '\n'.join(json.dumps(e) for e in [
        {'event':'init','init':{'agent':gemini.AGENT}},
        {'event':'step_update','step_update':{'step_type':'agent_response','text_delta':'ignored'}},
        {'event':'result','result':{'status':'SUCCESS','response':json.dumps(answer)}}])

class GeminiTests(unittest.TestCase):
    def test_stream_requires_complete_result_and_rejects_tools(self):
        self.assertEqual(gemini.parse_output(stream()),ANSWER)
        for out in [stream().rsplit('\n',1)[0], 'progress\n'+stream(), '[]', stream()+'\n'+stream(),
                    json.dumps({'event':'result','result':{'status':'SUCCESS','response':''}})]:
            with self.assertRaises(AppError): gemini.parse_output(out)
        for step in [{'step_type':'tool'},{'step_type':'agent_response','tool_info':{'name':'view_file'}}]:
            with self.assertRaises(AppError) as caught:
                gemini.parse_output(json.dumps({'event':'step_update','step_update':step})+'\n'+stream())
            self.assertEqual(caught.exception.code,'tool_policy')

    def test_native_command_and_only_gemini_catalog(self):
        with patch('gemini.locate',return_value='/native path/agy.exe'):
            self.assertEqual(gemini.command(),['/native path/agy.exe'])
        self.assertEqual(gemini.parse_models('claude-other\tClaude\ngemini-flash-high\tGemini High'),[{'id':'gemini-flash-high','name':'Gemini High'}])
        with self.assertRaises(AppError): gemini.parse_models('not logged in')

    def test_question_cannot_expand_files_or_run_slash_commands(self):
        provider=gemini.GeminiProvider()
        prompt='/run @/private/file learner@example.com'
        def fake_run(args,d,encoded,cancel,timeout,**kw):
            content=json.loads(encoded)['message']['content']
            self.assertNotIn('@',content)
            self.assertEqual(json.loads(content)['course_task'],prompt)
            self.assertEqual(args[0],'/native/agy')
            self.assertEqual(args[args.index('--model')+1],'gemini-flash-high')
            self.assertIn('--disable-slash-commands',args)
            self.assertNotIn('--continue',args)
            agent=(Path(d)/'.agents/agents'/gemini.AGENT/'agent.md').read_text()
            self.assertIn('excludeDefaultComponents: true',agent)
            self.assertIn('tools: []',agent)
            return stream()
        with patch.object(provider,'detect',return_value={'available':True}),patch('gemini.command',return_value=['/native/agy']),patch('gemini.run',side_effect=fake_run),patch('gemini.check_customizations'):
            self.assertEqual(provider.answer(prompt,'gemini-flash-high',threading.Event(),10),ANSWER)
        for key in ['GEMINI_API_KEY','GOOGLE_API_KEY','GOOGLE_APPLICATION_CREDENTIALS','ANTIGRAVITY_APP_DATA_DIR','NODE_OPTIONS']:
            with patch.dict(os.environ,{key:'must-not-inherit'}): self.assertNotIn(key,environment())

    def test_global_customizations_fail_closed_without_modifying_files(self):
        with tempfile.TemporaryDirectory() as d:
            home=Path(d);root=home/'.gemini/config';root.mkdir(parents=True)
            mcp=root/'mcp_config.json';mcp.write_text('')
            gemini.check_customizations(home)
            hook=root/'hooks.json';hook.write_text('{"fixture":"do not run"}')
            with self.assertRaises(AppError): gemini.check_customizations(home)
            self.assertEqual(hook.read_text(),'{"fixture":"do not run"}')
            hook.unlink();mcp.write_text('{"mcpServers":{"fixture":{}}}')
            with self.assertRaises(AppError): gemini.check_customizations(home)
            mcp.write_text('{}');settings=home/'.gemini/antigravity-cli/settings.json';settings.parent.mkdir();settings.write_text('{"hooks":{}}')
            with self.assertRaises(AppError): gemini.check_customizations(home)

    def test_detection_requires_tested_version_and_live_account_catalog(self):
        with patch('gemini.check_customizations'),patch('gemini.command',return_value=['agy']),patch('gemini.run',side_effect=['1.4.2','gemini-flash-high\tGemini High']):
            self.assertTrue(gemini.GeminiProvider().detect()['available'])
        with patch('gemini.check_customizations'),patch('gemini.command',return_value=['agy']),patch('gemini.run',return_value='1.4.3'):
            self.assertEqual(gemini.GeminiProvider().detect()['code'],'capability')

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
