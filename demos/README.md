# Interactive Echo artifacts

Open [Echo prototypes](echo-prototypes/index.html) after downloading the repository, or download that **single HTML file** and open it in Android Chrome. GitHub's normal file page displays source rather than running HTML. No Python setup or API key is needed for the default browser mode. The downloadable artifact is about 65 KB.

The same file includes four views:

1. **Sentence cards:** generalize/specialize a subject, preserve alternatives, reverse/restore positions, test supported and unsupported inflections, save locally and export a trial.
2. **Questions and evidence:** edit a word sense and supplied category; compare candidate question tags with actual evidence-backed answers, missing facts, contradictions and different events.
3. **Conversation timeline:** pan, pinch/zoom, filter providers, search titles and inspect references. The initial data is explicitly fictional. Load an `echo-conversation-timeline/1` JSON index for real records. The page never uploads that file or sends it to a model.
4. **Algorithm library:** inspect mapped combinations, callable paths and implemented/specification boundaries.

Default mode is a JavaScript counterpart checked against Python-generated fixtures. **Original Python** mode downloads Pyodide 0.26.4 and SQLite on first use, then runs embedded copies of the repository's Python prototypes in an isolated in-memory catalog. It requires internet for runtime downloads. No external model runs. Session state and saved device files may differ between browser addresses; JSON export is the portable record. No transcript content is included in the repository demo.

For repository readers with Python and Node:

```
python demos/echo-prototypes/build.py
python demos/echo-prototypes/make_fixtures.py
node demos/echo-prototypes/tests.mjs
python -m unittest discover -s tests -v
```

A separate browser smoke test uses Playwright and an installed Chrome/Chromium: `python demos/echo-prototypes/browser_test.py --python`. Local browser launch may be restricted by the execution environment; CI records actual browser results.

`python_bridge.py` is an explicit UI adapter over the original modules. `engine.mjs` is the browser counterpart. `timeline.mjs` provides bounded viewport rendering. `build_hosted.py` produces external-script assets for a strict-CSP static host. Neither the UI nor algorithm catalog creates an autonomous dispatcher, learns language, reads pictures, or implements §DSL§ inversion.
