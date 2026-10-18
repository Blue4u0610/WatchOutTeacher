"""Opt-in paid/quota-consuming Gemini integration check using synthetic course data."""
import json
import sys
import tempfile
import threading
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'bridge'))
from gemini import GeminiProvider
from host import Host

provider=GeminiProvider()
status=provider.detect(refresh=True)
if not status['available']: raise SystemExit(status['message']+' '+status['authentication'])
evidence={'cli_version':status['version'],'requested_model':'gemini-3.8-flash-medium','cases':[]}
with tempfile.TemporaryDirectory(prefix='watchoutteacher-live-') as d:
    host=Host(Path(d),providers={'gemini':provider})
    try:
        host.store.save_settings({'primary':'gemini','fallback':False,'gemini_model':'gemini-3.8-flash-medium','timeout':120})
        result=host.ask({'selection':'What is 2 + 2? A: 3 B: 4 C: 5','context':'Choose one answer: What is 2 + 2? A: 3 B: 4 C: 5','context_complete':True},threading.Event(),'gemini-live-math')
        assert '4' in result['answer'] and result['basis']=='general_knowledge',result
        evidence['cases'].append({'case':'arithmetic','result':result})
        cid=host.store.create('Synthetic Gemini test')['settings']['active_course']
        host.store.add(cid,'gemini-fixture.md',{'units':[{'number':1,'kind':'text','text':'In the fictional Lumen protocol, Violet is the ready state. Amber means waiting. This definition applies only to this exercise.'}],'warnings':[]})
        result=host.ask({'selection':'In the Lumen protocol, what color means ready? A: Amber B: Violet','context':'Choose one answer. In the Lumen protocol, what color means ready? A: Amber B: Violet','context_complete':True},threading.Event(),'gemini-live-course')
        assert 'violet' in result['answer'].lower() and result['basis'] in ['course_material','mixed'],result
        assert any(s['document']=='gemini-fixture.md' for s in result['sources']),result
        evidence['cases'].append({'case':'course_reference','result':result})
    finally: host.cleanup()
output=Path(__file__).resolve().parents[1]/'test-results/gemini-live.json'
output.parent.mkdir(exist_ok=True)
output.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':[c['case'] for c in evidence['cases']], 'evidence':str(output)},ensure_ascii=False))
