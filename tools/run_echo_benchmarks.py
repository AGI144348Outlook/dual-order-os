"""Preserve diagnostic failures as evidence; runner success is not all-capabilities success."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from benchmarks.diagnostics import run as baseline_run
from benchmarks.branch_diagnostics import run as branch_run
from tools.check_branch_components import verify


def main():
    out=ROOT/'reports/echo-benchmarks';out.mkdir(parents=True,exist_ok=True)
    baseline=json.loads((out/'baseline.json').read_text())
    current=baseline_run();extended=branch_run()
    (out/'after-branch-import.json').write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n')
    (out/'branch-components.json').write_text(json.dumps(extended,ensure_ascii=False,indent=2)+'\n')
    before={(c['group'],c['name']):c['status'] for c in baseline['cases']}
    after={(c['group'],c['name']):c['status'] for c in current['cases']}
    changes=[{'group':g,'name':n,'before':before.get((g,n)),'after':status}
             for (g,n),status in after.items() if before.get((g,n))!=status]
    summary={'verified_recovered_source_files':verify(),'baseline':baseline['summary'],
             'same_baseline_tasks_after_import':current['summary'],'changed_baseline_outcomes':changes,
             'additional_bounded_language_tasks':extended['summary'],
             'interpretation':'Regression tests and constrained diagnostic cases. Original failures remain visible; no standardized intelligence score or general-language claim.'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
