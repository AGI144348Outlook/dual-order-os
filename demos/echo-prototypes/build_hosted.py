"""Produce external-script assets for a strict-CSP Cloudflare demo host."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OUT=HERE/'hosted';OUT.mkdir(exist_ok=True)
modules=['libraries/catalog_box.py','libraries/echo_sentence_cards.py','libraries/echo_question_tags.py']
data={'catalog':json.loads((ROOT/'libraries/algorithms/mapped-combinations/catalog.json').read_text()),'python':{p:(ROOT/p).read_text() for p in modules}}
data['python']['python_bridge.py']=(HERE/'python_bridge.py').read_text();(OUT/'data.json').write_text(json.dumps(data,ensure_ascii=False))
js=(HERE/'engine.mjs').read_text().replace('export ','')+'\n'+(HERE/'timeline.mjs').read_text().replace('export ','')+'\n'+(HERE/'ui.js').read_text().replace("JSON.parse($('demo-data').textContent)","await (await fetch('./data.json')).json()")+'\n'+(HERE/'timeline-ui.js').read_text()
(OUT/'app.js').write_text(js)
css=(HERE/'style.css').read_text()+"\n#timeline-canvas{width:100%;height:180px;touch-action:none;border-radius:12px;background:#edf4ed}#runtime{max-width:350px}#tag,#ask{margin-top:16px}#answer-output{margin-top:18px}\n"
(OUT/'style.css').write_text(css)
body=(HERE/'body.html').read_text()
import re
body=re.sub(r' style="[^"]*"','',body)
body=body.replace('<footer>','<footer><p><a href="https://group-canvas-tower.agi144348.workers.dev/files.html" target="_blank" rel="noopener">Open your private file cabinet ↗</a> · In “Conversation timeline · Echo index”, download echo-conversation-timeline.json, then load it in the timeline tab.</p>')
(OUT/'index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Echo · Working cards and timeline</title><link rel="stylesheet" href="./style.css"><script type="module" src="./app.js"></script></head><body>'+body+'</body></html>')
print('Hosted assets built; no conversation data included.')
