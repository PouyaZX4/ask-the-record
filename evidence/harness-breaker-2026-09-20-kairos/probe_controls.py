"""Independent synthetic control probes; no external requests or real credentials."""
import contextlib, importlib.util, io, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ANSWER='ANSWER: Synthetic unsupported assertion.\nSOURCES: fabricated/path\nEVIDENCE DATE: 2026-09-11\nVERDICT: STANDING\nUNCERTAINTY: No independent verification.'

def run_case(case):
 spec=importlib.util.spec_from_file_location('candidate',ROOT/'ask.py')
 m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
 m.load_keys=lambda:{'SANITY_CONTEXT_TOKEN':'synthetic-token','GEMINI_API_KEY':'synthetic-key'}
 events=[]; model_calls=0
 def fake_post(url,payload,headers,what):
  nonlocal model_calls
  if what=='Gemini':
   model_calls+=1
   if case in ('empty_retrieval','mcp_tool_error') and model_calls==1:
    return {'candidates':[{'content':{'parts':[{'functionCall':{'name':'knowledge_base_read','args':{'paths':['synthetic/path']}}}]}}]}
   answer=ANSWER if case!='empty_uncertainty' else ANSWER.split('UNCERTAINTY:')[0]+'UNCERTAINTY: '
   events.append({'model_received':payload['contents']})
   return {'candidates':[{'content':{'parts':[{'text':answer}]}}]}
  method=payload['method']; name=payload.get('params',{}).get('name')
  events.append({'method':method,'tool':name})
  if case=='http_failure' and method=='initialize':
   raise m.Failure('Synthetic HTTP 401')
  if method=='initialize': return {'result':{}}
  if name=='initial_context': return {'result':{'content':[{'type':'text','text':'Synthetic outline: synthetic/path. No answer is present.'}]}}
  if name=='knowledge_base_read':
   if case=='empty_retrieval': return {'result':{'content':[]}}
   return {'result':{'isError':True,'content':[{'type':'text','text':'Synthetic entry unavailable'}]}}
  raise AssertionError((method,name))
 m.post=fake_post
 old=sys.argv; sys.argv=['ask.py','synthetic question']
 output=io.StringIO()
 try:
  with contextlib.redirect_stdout(output): code=m.main()
 finally: sys.argv=old
 return {'case':case,'exit_code':code,'model_calls':model_calls,'stdout':output.getvalue(),'events':events}
results=[run_case(x) for x in ('empty_retrieval','mcp_tool_error','no_retrieval','empty_uncertainty','http_failure')]
(ROOT/'control-probes.json').write_text(json.dumps(results,indent=2)+'\n')
for r in results:
 print(json.dumps({k:r[k] for k in ('case','exit_code','model_calls','stdout')}))
