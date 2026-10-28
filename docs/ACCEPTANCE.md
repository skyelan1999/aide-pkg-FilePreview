# File Preview 0.1.0 acceptance — 2026-10-28

## Verified locally

- macOS ARM64 Docker Desktop; independently built optional renderer, LibreOffice, Chromium, Noto CJK fonts and pinned Python packages. No dependencies added to Aide core image.
- Four Node tests passed: tool/schema boundaries, pages/crop/path budgets, actual HTTP snapshot-byte forwarding, source hashes, revoked source escaped snapshot rejection, and remote renderer endpoint refusal.
- Seven synthetic formats passed the actual Docker renderer: two-page PDF, two-page DOCX, two-slide PPTX, XLSX print page, quadrant PNG, Markdown and HTML. Checks cover page order, total/selected page coverage, crop, image hashes, invalid pages and token rejection.
- All seven formats then passed through the **installed ZIP in a real isolated Aide process**, native source API, settings, scheduler and workbench tool calls. Original hashes matched; returned images were actual nonempty rasters. Crop and host image capability passed. Fixture port 18499, never 9999; source data is synthetic.
- Browser workbench uses a test parent carrying real authenticated host calls over pinned upstream HTTPS, not a mock source API. Actual Word pages and Chinese text, PPT slides, source browsing, page coverage and top-right quadrant crop were displayed. English guide, 390px narrow layout, Escape closure, invalid-page error and clearing previous images on file/parameter/source changes passed. This is not a full Aide installation/settings UI acceptance.
- Companion host Go tests include an actual Aide tool loop and controlled provider endpoint: the next provider request contains real image_url parts matching the returned raster. Text tool ledgers do not contain base64; invalid MIME/digest/content, expiry and unsupported vision models are checked. Existing plugin plans and attachment tests also passed. Repository quick gate passed.

## Important boundaries

The actual installed plugin was also exercised through a real Aide task and a loopback-only controlled provider: each image-bearing model request carried exactly the two expected Word-page JPEG hashes. This uses the actual Docker renderer, not a prefilled image fixture.

No paid/live model request was made. Controlled provider wire checks establish image transport, **not** semantic accuracy of a real vision model. Browser images were visually inspected by the development assistant. No external user documents, real SSH/SFTP server or Windows-native renderer was used. Windows/macOS Docker support is a target; macOS ARM64 Docker was tested locally, Linux AMD64 is covered separately by CI before publication.

Office is a LibreOffice conversion copy and may paginate differently from Microsoft Office. XLSX is print-page rendering, not sheet-grid parity or formula verification. HTML is offline print with scripts and external assets disabled. Only selected pages/crops count as coverage.

The host companion PR is https://github.com/skyelan1999/aide/pull/555 . Aide builds without plugin-tool-images-v1 cannot deliver these images to AI; marketplace feature admission prevents unsupported installation. This plugin does not itself upgrade Aide or deploy 9999.

## Reproducibility

Synthetic fixture writer: scripts/create-fixtures.py. Actual renderer checks: scripts/verify-engine.py. Installed-host checks: scripts/native-acceptance.cjs, refusing containers without the dedicated acceptance label. Temporary credentials, original fixture bytes and screenshots stay in ignored .agent-state; no user or private data is shipped. Release proof binds the final ZIP/source/CI. Final publication status belongs to the GitHub Release and marketplace deployment, not this local receipt.
