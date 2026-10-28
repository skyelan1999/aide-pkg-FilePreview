"""Deterministic explicit allowlist: no tokens, documents, caches or runtime binaries."""
from pathlib import Path
import zipfile,json,hashlib
root=Path(__file__).resolve().parents[1]
files=['manifest.json','index.js','viewer.html','LICENSE','README.md','THIRD_PARTY_NOTICES.md','docs/PRD.md','docs/ACCEPTANCE.md','docs/RELEASE-NOTES-0.1.0.md','engine/Dockerfile','engine/compose.yaml','engine/server.py','engine/gateway.py','engine/requirements.txt','engine/LICENSE','scripts/setup-engine.py']
version=json.loads((root/'manifest.json').read_text())['version'];out=root/'dist';out.mkdir(exist_ok=True);target=out/f'file-preview-{version}-preview.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for f in files:
  i=zipfile.ZipInfo(f,(2026,10,28,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,(root/f).read_bytes())
digest=hashlib.sha256(target.read_bytes()).hexdigest();(out/'SHA256SUMS').write_text(digest+'  '+target.name+'\n');print(json.dumps({'path':str(target),'bytes':target.stat().st_size,'sha256':digest,'entries':files}))
