# Third-party notices

- esbuild 0.25.12 (MIT): development bundler, https://github.com/evanw/esbuild . No esbuild binary shipped.
- Workbench MessagePort client adapted from Aide RViz public MIT host-client source; copyright skyelan1999. Retains source comments and MIT terms.
- PyMuPDF 1.26.5 / MuPDF (AGPL-3.0-or-later): https://pymupdf.readthedocs.io/en/latest/about.html . Used by the optional open-source AGPL engine, not bundled into the MIT JS package.
- LibreOffice (MPL-2.0 and LGPL-3.0+ dual license; other components retain their licenses): https://www.libreoffice.org/about-us/licenses . Debian packages retain /usr/share/doc copyright/source metadata.
- Chromium (BSD-style plus individual component licenses): https://chromium.googlesource.com/chromium/src/+/main/LICENSE . Debian package copyright remains in the built image.
- Playwright Python 1.55.0 (Apache-2.0): https://github.com/microsoft/playwright-python . Uses Debian Chromium; does not download Playwright browsers.
- Pillow 11.3.0 (HPND): https://github.com/python-pillow/Pillow . Markdown 3.9 (BSD-3-Clause): https://github.com/Python-Markdown/markdown . Noto fonts (OFL-1.1): https://github.com/notofonts/noto-cjk . Liberation fonts (OFL-1.1): https://github.com/liberationfonts/liberation-fonts . Installed only in the optional engine image.

The archive includes the complete custom engine/gateway source and reproducible Docker build recipe, but no prebuilt third-party runtime binaries. Engine license is engine/LICENSE. Dependency versions and original upstream sources are listed here and in engine/requirements.txt; normal upstream license obligations remain applicable. The MIT wrapper does not relicense dependencies.
