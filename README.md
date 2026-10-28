# File Preview · 文件预览

Public background file-rendering plugin for Aide. Preview pages without opening desktop apps; return actual raster evidence for a vision model to inspect. **0.1.0 is a preview**, not a native Office fidelity guarantee or automatic document repair tool.

## Quick start / 怎么用

1. Install the plugin ZIP in Aide and enable it. The installed JS is self-contained; no npm install.
2. Extract the **same ZIP** to a separate local directory. Install Docker Compose and Python 3, then run at the ZIP root:

```sh
python3 scripts/setup-engine.py
docker compose -f engine/compose.yaml up --build -d
```

Windows Command Prompt may use `python` instead of `python3`; PowerShell is not required. First build downloads official Python/Debian packages, LibreOffice, Chromium, fonts and pinned Python dependencies. Allow approximately 3 GiB disk and 1.5 GiB renderer memory. No ROS/CAD dependency.

3. Copy only the `FILE_PREVIEW_TOKEN` value from the generated private `.file-preview-engine.env` into the plugin's **Renderer token** setting. Do not put it into chat, Git or project files. Setup never edits Aide settings automatically.
4. Set **Renderer URL** according to the **Aide backend**, then reopen the workbench:

| Backend | URL |
| --- | --- |
| macOS/Windows Docker Desktop Aide | `http://host.docker.internal:18510` |
| Native Aide on same machine | `http://127.0.0.1:18510` |
| Linux Docker Aide | Explicitly join its container to `aide-file-preview_gateway`, then use `http://aide-file-preview-gateway-1:8765` |

The Linux network change is an administrator action; this plugin never changes Docker networks automatically. Ports are bound to loopback, not the LAN. The renderer has no outgoing network; a separate fixed-target gateway provides authenticated access.

5. Choose an authorized source, Browse, select a relative file, enter pages such as `1` or `1,2`, then **Render in background**. The page shows actual coverage, original hash, warnings and images. `0.5,0,0.5,0.5` crops the top-right quarter for closer inspection.
6. Stop only this optional engine when finished:

```sh
docker compose -f engine/compose.yaml stop
```

中文：安装 ZIP → 解压同一 ZIP → 运行 setup 和 Docker 命令 → 将本地令牌填入插件设置 → 按后端位置配置服务地址 → 重开工作台，选文件和页码 → 后台渲染。使用指南在工作台右上角。不会打开桌面窗口，不会覆盖原文档，不会自动安装引擎。

## AI tools

- `file_preview_status`: renderer health and actual host image-result capability.
- `file_preview_sources`, `file_preview_browse`: authorized source discovery/browsing.
- `file_preview_render`: source-relative path, `pages` (1–4), `dpi` (72–180), optional normalized `crop` (`x,y,width,height`). Returns source hash, page coverage and real `images` with MIME/base64/digest.

Example request to Aide: “Use File Preview to inspect pages 1 and 2 of docs/report.pdf. Check clipping and table alignment; identify pages/regions, and do not claim unreturned pages were reviewed.”

AI image delivery requires an Aide build supporting **plugin-tool-images-v1** and a configured vision model. Old hosts can display workbench pictures but their text-only tool normalization does not deliver images to AI. The marketplace capability gate rejects unsupported hosts. The companion Aide PR supplies this generic contract; installing this ZIP alone does not patch the host. A pure text model must produce a clear capability error, never a fabricated visual review. Input images may be sent to the user's selected model provider under normal Aide rules; rendering itself stays local. Normal Aide provider-request diagnostics may retain request bodies, including images; image payloads are excluded from ordinary text tool records and serialized message fields.

## Fidelity and coverage

PDF rasterization uses PyMuPDF. Office converts a temporary copy to PDF in LibreOffice: fonts, pagination, charts and calculations may differ from Microsoft Office. XLSX page numbers are **print pages**, not sheet numbers; formulas are not certified. Originals are never changed. Office external relationships are removed only from the conversion copy and disclosed.

HTML/Markdown/SVG/text use Chromium print layout. JavaScript, remote URLs and relative file assets are disabled; use embedded self-contained resources. This is not an interactive webpage screenshot. GIF/TIFF/animated WebP show only first frame. Password-protected inputs, oversized files/pages and invalid crops fail explicitly.

Preview snapshots are per call, carry the source fingerprint and are discarded when authorization/source identity changes. Renderer temp directories are removed after completion. No persistent user-document cache. A newer source version requires a new render. A failed or partial render never counts as visual review.

## Development and licensing

```sh
npm ci --ignore-scripts
npm run build
npm test
python3 scripts/package.py
```

JS wrapper/workbench: MIT. Optional `engine/` source: AGPL-3.0-or-later, uses PyMuPDF under AGPL and separately licensed LibreOffice/Chromium. See THIRD_PARTY_NOTICES.md and engine/LICENSE. No third-party binaries are shipped in the plugin ZIP; Docker builds dependencies separately. Architecture/acceptance remain in this owning repository. No private plugin or MIXSoul code/data is included.
