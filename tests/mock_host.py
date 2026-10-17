"""Test-only entry point. Production host never exposes a mock-provider setting."""
import json
import os
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'bridge'))
import host
from common import AppError
RealHost=host.Host
class Fake:
    def detect(self,refresh=False):return {'provider':'codex','installed':True,'available':True,'message':'TEST MOCK','version':'mock','authentication':'mock'}
    def models(self,cancel=None):return {'models':[{'id':'test-model','name':'Test Model','efforts':['low','medium','high'],'default_effort':'medium'}],'message':'TEST MOCK catalog'}
    def answer(self,prompt,model,cancel,timeout,effort=''):
        data=json.loads(prompt.split('\nDATA:\n')[1]); q=data['selected_text']
        if 'WAIT_FOR_DISCONNECT' in q:
            Path(os.environ['COURSE_ASSIST_DATA']).parent.joinpath('ask.pending').write_text('ready')
            cancel.wait(30)
        else:
            cancel.wait(.7 if '2 + 2' in q else .25)
        if cancel.is_set(): raise AppError('cancelled','cancelled')
        sources=data['excerpts']
        answer='B — Violet' if 'Lumen' in q else 'B — 4'
        return {'answer':answer,'explanation_en':'This is a simulated test answer, not a live model response.','sources':[{'source_id':sources[0]['source_id']}] if sources else [],'basis':'course_material' if sources else 'general_knowledge','needs_more_context':False}
class TestHost(RealHost):
    def __init__(self):
        Path(os.environ['COURSE_ASSIST_DATA']).parent.joinpath('host.pid').write_text(str(os.getpid()))
        super().__init__(providers={'codex':Fake(),'claude':Fake()})
host.Host=TestHost
sys.exit(host.main())
