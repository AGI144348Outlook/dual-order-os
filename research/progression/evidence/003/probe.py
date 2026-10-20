import sys,json
from pathlib import Path
sys.path.insert(0,'/tmp/echo-tsadi-index')
from index_source import build_index,GlyphRootEntry
out={'method':'Unmodified Dual Order OS index. Experimental root/sense labels and TEST_ONLY opcodes have no assigned glyph semantics. No persistent index or repository code changes.'}
i=build_index();old=[(e.root,e.sense,i.glyph_for_root_sense(e.root,e.sense)) for e in i.entries]
a=GlyphRootEntry('test-module-a','experimental attachment A','צ','TEST_ONLY')
b=GlyphRootEntry('test-module-b','experimental attachment B','ץ','TEST_ONLY')
i.add(a);i.add(b)
out['separate_forms']={'צ':[e.root for e in i.roots_for_glyph('צ')],'ץ':[e.root for e in i.roots_for_glyph('ץ')],'reverse_a':i.glyph_for_root_sense(a.root,a.sense),'reverse_b':i.glyph_for_root_sense(b.root,b.sense)}
assert out['separate_forms']['reverse_a']=='צ' and out['separate_forms']['reverse_b']=='ץ'
c=GlyphRootEntry('test-module-c','experimental attachment C','צ','TEST_ONLY');i.add(c)
out['additive_expansion']={'original_four_preserved':all(i.glyph_for_root_sense(r,s)==g for r,s,g in old),'tsadi_entries':len(i.roots_for_glyph('צ')),'sofit_entries':len(i.roots_for_glyph('ץ'))}
assert out['additive_expansion']=={'original_four_preserved':True,'tsadi_entries':2,'sofit_entries':1}
i.add(GlyphRootEntry(a.root,a.sense,'ץ','TEST_ONLY_CONFLICT'))
out['conflicting_registration']={'reverse_result':i.glyph_for_root_sense(a.root,a.sense),'forward_tsadi_still_contains_old_mapping':any(e.root==a.root and e.sense==a.sense for e in i.roots_for_glyph('צ')),'conflict_rejected':False}
j=build_index();entry=GlyphRootEntry('test-repeat','same sense','צ','TEST_ONLY');j.add(entry);j.add(entry)
out['duplicate_registration']={'rows':len(j.roots_for_glyph('צ')),'deduplicated':len(j.roots_for_glyph('צ'))==1}
k=build_index();x=GlyphRootEntry('test-mutate','same sense','צ','TEST_ONLY');k.add(x);x.glyph='ץ'
out['external_mutation']={'lookup_under_old_glyph_reports':[e.glyph for e in k.roots_for_glyph('צ')],'reverse_result':k.glyph_for_root_sense(x.root,x.sense),'lookup_under_new_glyph_rows':len(k.roots_for_glyph('ץ'))}
out['unsupported_contracts']=['explicit parent/child attachment','versioned profiles','write permissions','conflict rejection','transactional commit','persistent serialization','root/sense correction or removal']
Path('/tmp/echo-tsadi-index/results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2))
