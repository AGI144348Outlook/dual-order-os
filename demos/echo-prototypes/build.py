"""Build a standalone, offline-first artifact. Original Python is embedded, not rewritten."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
modules=['libraries/catalog_box.py','libraries/echo_sentence_cards.py','libraries/echo_question_tags.py']
data={'catalog':json.loads((ROOT/'libraries/algorithms/mapped-combinations/catalog.json').read_text()),
      'python':{p:(ROOT/p).read_text() for p in modules}}
data['python']['python_bridge.py']=(HERE/'python_bridge.py').read_text()
js=(HERE/'engine.mjs').read_text().replace('export ','')+'\n'+(HERE/'timeline.mjs').read_text().replace('export ','')+'\n'+(HERE/'ui.js').read_text()+'\n'+(HERE/'timeline-ui.js').read_text()
html='<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#17644e"><title>Echo · Working cards</title><style>'+(HERE/'style.css').read_text()+'</style></head><body>'+(HERE/'body.html').read_text()+'<script id="demo-data" type="application/json">'+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+'</script><script type="module">'+js.replace('</script','<\\/script')+'</script></body></html>\n'
(HERE/'index.html').write_text(html)
print('Built standalone artifact:',len(html.encode()),'bytes')
if __name__=='__main__':pass
