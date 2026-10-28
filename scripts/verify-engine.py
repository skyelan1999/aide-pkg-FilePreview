"""Exercise the running optional Docker renderer with synthetic fixtures only."""
from pathlib import Path
import base64,json,urllib.request,urllib.error,hashlib
root=Path('.agent-state/fixtures');out=Path('.agent-state/rendered');out.mkdir(parents=True,exist_ok=True)
token=Path('.file-preview-engine.env').read_text().strip().split('=',1)[1]
def req(route,value=None,auth=True):
 r=urllib.request.Request('http://127.0.0.1:18510'+route,data=None if value is None else json.dumps(value).encode(),headers={'Authorization':'Bearer '+(token if auth else 'invalid'),'Content-Type':'application/json'})
 with urllib.request.urlopen(r,timeout=80) as response:return json.load(response)
health=req('/health');assert health['ok']
try:req('/health',auth=False);raise AssertionError('Unauthorized accepted')
except urllib.error.HTTPError as e:assert e.code==401
receipts=[]
for name in ['two-pages.pdf','sample.docx','sample.pptx','sample.xlsx','quadrants.png','sample.md','sample.html']:
 data=(root/name).read_bytes();result=req('/render',{'name':name,'dataBase64':base64.b64encode(data).decode(),'pages':[1],'dpi':120})
 assert result['pagesRead']==[1] and len(result['images'])==1
 im=result['images'][0];raw=base64.b64decode(im['dataBase64']);assert hashlib.sha256(raw).hexdigest()==im['sha256'];assert im['width']>100 and im['height']>100
 (out/(name+'.jpg')).write_bytes(raw)
 if name in ['two-pages.pdf','sample.docx','sample.pptx']:assert result['totalPages']==2 and result['coverageComplete'] is False
 receipts.append({'name':name,'totalPages':result['totalPages'],'renderer':result['renderer'],'imageBytes':len(raw),'warnings':result['warnings']})
 print(name, result['totalPages'], 'PASS')
a={'name':'two-pages.pdf','dataBase64':base64.b64encode((root/'two-pages.pdf').read_bytes()).decode(),'pages':[2,1],'crop':{'x':.5,'y':0,'width':.5,'height':.5},'dpi':180};r=req('/render',a);assert r['pagesRead']==[2,1] and all(i['crop']==a['crop'] for i in r['images']);assert not r['coverageComplete']
for pages in [[3],[1,1],[1,2,3,4,5]]:
 try:req('/render',{**a,'pages':pages});raise AssertionError('Invalid page request accepted')
 except urllib.error.HTTPError as e:assert e.code==422
Path('.agent-state/engine-acceptance.json').write_text(json.dumps({'formats':receipts,'cropAndOrder':'PASS','unauthorized':'PASS','pageBounds':'PASS'},ensure_ascii=False,indent=2))
print('Seven formats, page bounds, crop, page order, source/image fingerprints and auth PASS')
