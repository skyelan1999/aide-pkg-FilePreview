# File Preview 0.1.0

User-approved scope: an independent public plugin for background file preview and visual review; public marketplace distribution after acceptance. Generic image-result transport belongs in Aide; all renderer design and implementation stays here. No 9999 or private research modifications.

## Behavior

- Sources: current authorized local/SSH workspace and visible references via Aide's source snapshot API. One relative file per render, at most 16 MiB.
- Formats: PDF; converted DOCX/PPTX/XLSX print pages; PNG/JPEG/GIF/WebP/BMP/TIFF first frames; self-contained UTF-8 Markdown, HTML, SVG and text print layout.
- Default page 1; select 1–4 distinct pages from documents up to 500 pages. Normalized crop supports closer inspection. Images bounded to 1600 px longest side and 4 MiB total JPEG output.
- Evidence: original source SHA-256, selected pages, actual total pages, crop, renderer/version and conversion warnings. Never imply unread pages were reviewed.
- UI: browse authorized sources, file path, pages, DPI, crop, visible results and usage guide in Chinese/English. No foreground application control.
- AI: file_preview_render returns structured image parts. Aide plugin-tool-images-v1 validates/routs rasters into a vision-capable request after all corresponding tool replies. Text-only hosts/models cannot claim visual inspection. Rendering is distinct from model inspection.
- Runtime: optional isolated Docker renderer and token-authenticated fixed-target loopback gateway, separate from Aide's image. No runtime downloads during a tool call. Browser scripts/network and Office external relationships disabled for conversion. No host workspace mount into renderer.

## Acceptance

Synthetic PDF, DOCX, PPTX, XLSX, PNG, Markdown and HTML through real renderer; page bounds, crop, auth, cleanup and original hash checks. Real Aide install, source reads, tool bridge and workbench page. Controlled multimodal provider wire test verifies actual images, without claiming a real vision-model semantic evaluation. No private documents or paid provider calls.

## Exclusions

Native Office pixel identity, formula correctness, OCR, automatic repairs, robot/video/CAD rendering, interactive HTML script execution, external assets/fonts, password-protected inputs and Windows host-native renderer. Office and Compare remain independent; no private implementation reused. Heavy engines are not added to core. Future format providers need explicit contracts and tests.
