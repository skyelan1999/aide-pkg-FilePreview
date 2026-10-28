"""Fixed-target loopback gateway; the renderer stays on an egress-isolated network."""
from http.server import HTTPServer,BaseHTTPRequestHandler
import http.client,json,os,hmac
TOKEN=os.environ.get("FILE_PREVIEW_TOKEN", "")
if len(TOKEN)<32:raise SystemExit("Private renderer token required")
class Proxy(BaseHTTPRequestHandler):
 def log_message(self,*_):pass
 def forward(self):
  if not hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+TOKEN):
   body=b'{"error":"Unauthorized"}';self.send_response(401);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body);return
  try:
   if self.path not in ('/health','/render'):raise ValueError('Unknown route')
   size=int(self.headers.get('Content-Length','0'))
   if not 0<=size<23*1024*1024:raise ValueError('Request budget exceeded')
   data=self.rfile.read(size) if size else None
   upstream=http.client.HTTPConnection('renderer',8765,timeout=70)
   upstream.request(self.command,self.path,body=data,headers={'Authorization':self.headers.get('Authorization',''),'Content-Type':'application/json'})
   r=upstream.getresponse();body=r.read(8*1024*1024+1)
   if len(body)>8*1024*1024:raise ValueError('Response budget exceeded')
   status=r.status;upstream.close()
  except Exception:status,body=502,json.dumps({'error':'Renderer unavailable or request rejected; check engine logs/settings'}).encode()
  self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 do_GET=forward
 do_POST=forward
HTTPServer(('0.0.0.0',8765),Proxy).serve_forever()
