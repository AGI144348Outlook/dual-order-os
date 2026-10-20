# Echo working-card artifacts

See [the demos guide](../README.md). Open `index.html` as a standalone file, or serve its directory using a static server. No build is needed to try the checked-in artifact.

Original code: `../../libraries/echo_sentence_cards.py`, `../../libraries/echo_question_tags.py`, `../../libraries/catalog_box.py`, and `../../libraries/echo_timeline.py`.

Only the sentence and question prototypes execute in the optional Pyodide mode. Timeline display always uses the browser renderer; its private dataset is produced by the Python chronology indexer, not a browser-based model.
