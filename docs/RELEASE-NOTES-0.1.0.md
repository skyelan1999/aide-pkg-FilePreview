# File Preview v0.1.0 — Preview

First public version of background read-only file preview and raster evidence for Aide.

- PDF, converted DOCX/PPTX/XLSX print pages, images, self-contained Markdown/HTML/SVG/text.
- Select 1–4 pages, crop a normalized region, inspect original SHA-256, actual coverage, renderer/version and conversion warnings.
- Chinese/English workbench, source browsing and setup guidance; no foreground desktop application required.
- Separate optional Docker renderer and authenticated loopback gateway. Heavy dependencies stay outside Aide. Renderer has no outbound network; scripts and external resources disabled. No original-file modifications or automatic repair.
- Real image-result delivery requires companion Aide capability `plugin-tool-images-v1` and a vision model. Older released hosts are rejected by the market capability gate; uploading this ZIP does not patch Aide. Companion PR: https://github.com/skyelan1999/aide/pull/555 . A main merge is not itself a new Aide Release.

Validation: four Node tests; actual ARM64 Docker render of seven synthetic formats; Linux AMD64 renderer/Node 18/22/24 CI; real installed-plugin source/workbench API checks; browser Word/PPT, crop, English/narrow guide and error-state checks. Actual Aide task-loop requests to a controlled loopback provider carried both rendered Word-page image hashes. This is image transport acceptance, not semantic quality acceptance of a paid/live model. See docs/ACCEPTANCE.md and release proof for exact receipts.

Office conversion may differ from Microsoft Office; spreadsheets use print pages and formulas are not certified. HTML print disables scripts/external assets; only embedded resources are supported. Images use first frame. Real SSH/SFTP documents, Windows-native rendering and user-device installation are untested.

Install the ZIP in Aide, extract the same ZIP separately and follow README.md / the in-page How to use guide to build the optional Docker renderer. Python 3 and Docker Compose required for setup; no PowerShell needed. JS wrapper/workbench MIT; engine source AGPL-3.0-or-later, dependency licenses retained. No runtime binaries or private/user data shipped. No Aide version/tag/Release or 9999 deployment included.
