# Chhoti Duniya: instructions for Claude

Read `README.md` first. It is the full maintenance guide: how the app works, the monthly refresh
procedure, the tests, and the decisions already made with the owner.

Rules for any change:

1. The catalog is edited only in `tools/catalog.py`, then written into `index.html` with `python3 tools/catalog.py`. Never hand-edit the CATALOG block.
2. Run both tests before pushing: `python3 tools/ui_test.py` and `python3 tools/sim_test.py`. Both must end with `0 failed`.
3. Bump `CFG.version` in `index.html` and add a line to the change log in `README.md`.
4. GitHub Pages serves the `main` branch, so a push to `main` is the deploy. After pushing, load the live link and confirm `__cd.cfg.version` in the browser.
5. The owner is non-technical and does not test builds by hand. Test it yourself, then tell him plainly what you could not test.
6. Every new video must pass the gates in README section 5. The owner's phone state (history, settings) lives in the phone's localStorage under `cd_v1`; do not change that key or its shape without a migration.
