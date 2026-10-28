"""Generate a local renderer token once; never starts Docker or edits Aide settings."""
from pathlib import Path
import secrets,os
p=Path(__file__).resolve().parents[1]/'.file-preview-engine.env'
if p.exists():
 print('Existing private .file-preview-engine.env retained. Read its FILE_PREVIEW_TOKEN locally into plugin settings.')
else:
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as f:f.write('FILE_PREVIEW_TOKEN='+secrets.token_urlsafe(36)+'\n')
 print('Created private .file-preview-engine.env. Copy FILE_PREVIEW_TOKEN into plugin settings, never into chat.')
print('Start: docker compose -f engine/compose.yaml up --build -d')
print('Docker Desktop URL: http://host.docker.internal:18510; native Aide: http://127.0.0.1:18510')
