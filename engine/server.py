"""File Preview renderer. AGPL-3.0-or-later; optional process with PyMuPDF/LibreOffice/Chromium."""
import base64, hashlib, hmac, io, json, math, os, subprocess, sys, tempfile, zipfile
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
MAX_INPUT=16*1024*1024
EXTS={'.pdf','.docx','.pptx','.xlsx','.png','.jpg','.jpeg','.webp','.gif','.bmp','.tif','.tiff','.md','.markdown','.html','.htm','.txt','.svg'}
def validate(a):
 name=a.get('name','');ext=Path(name).suffix.lower()
 if ext not in EXTS:raise ValueError('Unsupported file format')
 data=base64.b64decode(a.get('dataBase64',''),validate=True)
 if not data or len(data)>MAX_INPUT:raise ValueError('Input budget exceeded')
 pages=a.get('pages',[1]);dpi=a.get('dpi',120)
 if not isinstance(pages,list) or not 1<=len(pages)<=4 or len(set(pages))!=len(pages) or any(type(p)!=int or p<1 or p>500 for p in pages):raise ValueError('Select 1–4 distinct pages, 1–500')
 if type(dpi)!=int or not 72<=dpi<=180:raise ValueError('DPI 72–180 required')
 c=a.get('crop')
 if c is not None:
  if not isinstance(c,dict) or any(type(c.get(k)) not in (int,float) or not math.isfinite(c[k]) for k in ('x','y','width','height')):raise ValueError('Invalid crop')
  if c['x']<0 or c['y']<0 or c['width']<=0 or c['height']<=0 or c['x']+c['width']>1 or c['y']+c['height']>1:raise ValueError('Crop outside page')
 return data,ext,pages,dpi,c

def render(a):
 import pymupdf as fitz
 from PIL import Image
 data,ext,pages,dpi,crop=validate(a)
 warnings=[];method='';versions={'pymupdf':fitz.VersionBind}
 with tempfile.TemporaryDirectory(prefix='file-preview-') as temp:
  root=Path(temp);src=root/('input'+ext);src.write_bytes(data)
  if ext in {'.docx','.pptx','.xlsx'}:
   with zipfile.ZipFile(io.BytesIO(data)) as z:
    items=z.infolist()
    if len(items)>4000 or sum(i.file_size for i in items)>64*1024*1024:raise ValueError('Office expanded budget exceeded')
    if any('vbaproject' in i.filename.lower() for i in items):raise ValueError('Macros are not supported')
   # Strip external relationships in the temporary conversion copy. Keep the
   # original bytes/hash untouched; removed assets are explicitly disclosed.
   import xml.etree.ElementTree as ET
   clean=io.BytesIO();removed=0
   with zipfile.ZipFile(io.BytesIO(data)) as zin, zipfile.ZipFile(clean,'w',zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
     content=zin.read(item)
     if item.filename.endswith('.rels'):
      ET.register_namespace('', 'http://schemas.openxmlformats.org/package/2006/relationships')
      tree=ET.fromstring(content);changed=False
      for relation in list(tree):
       if relation.get('TargetMode','').lower()=='external':tree.remove(relation);removed+=1;changed=True
      if changed:content=ET.tostring(tree,encoding='utf-8',xml_declaration=True)
     zout.writestr(item.filename,content)
   src.write_bytes(clean.getvalue())
   if removed:warnings.append('External Office relationships removed from conversion copy: '+str(removed))
   profile=root/'profile';profile.mkdir()
   (profile/'user').mkdir()
   (profile/'user'/'registrymodifications.xcu').write_text('''<?xml version="1.0"?><oor:items xmlns:oor="http://openoffice.org/2001/registry"><item oor:path="/org.openoffice.Office.Common/Security/Scripting"><prop oor:name="MacroSecurityLevel" oor:op="fuse"><value>3</value></prop></item></oor:items>''')
   r=subprocess.run(['libreoffice','-env:UserInstallation='+profile.as_uri(),'--headless','--nologo','--nodefault','--norestore','--convert-to','pdf','--outdir',str(root),str(src)],capture_output=True,timeout=45)
   pdf=root/'input.pdf'
   if r.returncode or not pdf.exists():raise ValueError('Office conversion failed; encrypted/corrupt/unsupported files are not previewed')
   doc=fitz.open(pdf);method='LibreOffice PDF conversion'
   versions['libreoffice']=subprocess.check_output(['libreoffice','--version'],timeout=5).decode().strip()
   warnings.append('Converted Office print pagination; fonts, formulas, charts and layout may differ from Microsoft Office. No original changes.')
   if ext=='.xlsx':warnings.append('Pages follow spreadsheet print layout, not individual sheet numbers. Formula values are renderer results, not verified calculations.')
  elif ext in {'.html','.htm','.md','.markdown','.txt','.svg'}:
   from playwright.sync_api import sync_playwright
   import html,markdown
   text=data.decode('utf-8-sig')
   if ext in {'.md','.markdown'}:text=markdown.markdown(text,extensions=['tables','fenced_code'])
   if ext=='.txt':text='<pre>'+html.escape(text)+'</pre>'
   text='<html><head><meta charset="utf-8"><style>body{font:14px sans-serif;overflow-wrap:anywhere}img,svg{max-width:100%}pre{white-space:pre-wrap}@page{size:A4;margin:15mm}</style></head><body>'+text+'</body></html>'
   blocked=[]
   with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    context=browser.new_context(java_script_enabled=False,offline=True,service_workers='block')
    def reject(route):
     blocked.append(route.request.url.split(':',1)[0]);route.abort()
    context.route('**/*',reject)
    page=context.new_page();page.set_content(text,wait_until='load',timeout=15000);page.emulate_media(media='print')
    pdf=page.pdf(print_background=True,prefer_css_page_size=True);browser.close()
   doc=fitz.open(stream=pdf,filetype='pdf');method='Chromium offline print'
   versions['chromium']=subprocess.check_output(['/usr/bin/chromium','--version'],timeout=5).decode().strip()
   warnings.append('Scripts, remote resources and relative file assets are blocked. Supply self-contained embedded images/fonts. This is print layout, not an interactive app screenshot.')
   if blocked:warnings.append('Blocked resource requests: '+str(len(blocked)))
  elif ext=='.pdf':
   doc=fitz.open(stream=data,filetype='pdf');method='PDF page raster'
  else:
   Image.MAX_IMAGE_PIXELS=20_000_000
   with Image.open(io.BytesIO(data)) as im:
    if im.width*im.height>20_000_000:raise ValueError('Image input pixel budget exceeded')
    im.seek(0);im=im.convert('RGB');buf=io.BytesIO();im.save(buf,format='PNG')
   imgdoc=fitz.open(stream=buf.getvalue(),filetype='png');doc=fitz.open(stream=imgdoc.convert_to_pdf(),filetype='pdf');imgdoc.close();method='Image first-frame raster'
   if ext in {'.gif','.tif','.tiff','.webp'}:warnings.append('Only the first image frame is previewed; this is not animation/video playback.')
  try:
   if doc.needs_pass:raise ValueError('Password-protected files are not supported')
   total=len(doc)
   if total>500:raise ValueError('Document exceeds 500-page preview budget')
   if any(p>total for p in pages):raise ValueError('Requested page outside document; total='+str(total))
   result=[];used=0
   for n in pages:
    page=doc[n-1];rect=page.rect
    if crop:rect=fitz.Rect(rect.x0+rect.width*crop['x'],rect.y0+rect.height*crop['y'],rect.x0+rect.width*(crop['x']+crop['width']),rect.y0+rect.height*(crop['y']+crop['height']))
    if rect.width<=0 or rect.height<=0:raise ValueError('Invalid page dimensions')
    zoom=min(dpi/72,1600/max(rect.width,rect.height),math.sqrt(3_500_000/(rect.width*rect.height)))
    pix=page.get_pixmap(matrix=fitz.Matrix(zoom,zoom),clip=rect,alpha=False,colorspace=fitz.csRGB)
    jpeg=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);b=io.BytesIO();jpeg.save(b,format='JPEG',quality=88);raw=b.getvalue();used+=len(raw)
    if used>4*1024*1024:raise ValueError('Rendered image byte budget exceeded; request fewer pages')
    result.append({'mediaType':'image/jpeg','dataBase64':base64.b64encode(raw).decode(),'sha256':hashlib.sha256(raw).hexdigest(),'page':n,'width':pix.width,'height':pix.height,'crop':crop})
   return {'protocol':'plugin-tool-images-v1','renderer':method,'rendererVersions':versions,'totalPages':total,'pagesRead':pages,'coverageComplete':set(pages)==set(range(1,total+1)) and crop is None,'warnings':warnings,'images':result}
  finally:doc.close()

class Handler(BaseHTTPRequestHandler):
 def log_message(self,*_):pass
 def respond(self,status,value):
  raw=json.dumps(value).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def authorized(self):return INTERNAL or hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+TOKEN)
 def do_GET(self):
  if not self.authorized():return self.respond(401,{'error':'Unauthorized'})
  if self.path!='/health':return self.respond(404,{'error':'Not found'})
  self.respond(200,{'ok':True,'engineVersion':'0.1.0','formats':sorted(EXTS),'limits':{'inputBytes':MAX_INPUT,'pagesPerCall':4,'maxPages':500,'maxSide':1600},'network':'isolated Docker network; browser offline; scripts disabled'})
 def do_POST(self):
  if not self.authorized():return self.respond(401,{'error':'Unauthorized'})
  if self.path!='/render':return self.respond(404,{'error':'Not found'})
  try:
   size=int(self.headers.get('Content-Length','0'))
   if not 0<size<23*1024*1024:raise ValueError('Request budget exceeded')
   if self.headers.get('Content-Type')!='application/json':raise ValueError('JSON required')
   data=self.rfile.read(size)
   if len(data)!=size:raise ValueError('Incomplete input')
   # Worker receives no renderer token. Its process and temp directory end per request.
   env={k:v for k,v in os.environ.items() if k!='FILE_PREVIEW_TOKEN'}
   r=subprocess.run([sys.executable,__file__,'worker'],input=data,capture_output=True,timeout=60,env=env)
   if r.returncode:raise ValueError(r.stderr.decode()[-600:])
   self.respond(200,json.loads(r.stdout))
  except subprocess.TimeoutExpired:self.respond(422,{'error':'Render timeout; no complete preview produced'})
  except Exception as e:self.respond(422,{'error':str(e)[:700]})
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='worker':
  try:print(json.dumps(render(json.load(sys.stdin))))
  except Exception as e:print(type(e).__name__+': '+str(e),file=sys.stderr);sys.exit(1)
 else:
  TOKEN=os.environ.get('FILE_PREVIEW_TOKEN','')
  INTERNAL=os.environ.get('FILE_PREVIEW_INTERNAL')=='1'
  if not INTERNAL and len(TOKEN)<32:raise SystemExit('FILE_PREVIEW_TOKEN must contain at least 32 characters')
  os.makedirs('/tmp/home',exist_ok=True)
  HTTPServer(('0.0.0.0',8765),Handler).serve_forever()
