# Echo relation-operation learning trial

Ran actual Echo AlgorithmMatrix.bandit_select, record_outcome and checkpoint_generation from pinned genesis-documentary engine b9a2299820651f0bcc700de4de943f3c70b8c91e. This is supervised symbolic routing, not neural fine-tuning. 1920 trials across 16 supplied task cues; 1344 exploratory failures externally corrected; final frozen best-route evaluation 16/16 versus untrained first-arm baseline 1/16. The high exploratory error count matters: final exploitation accuracy does not describe online training accuracy.

Relations: is-a, part-of, has-part, made-of, has-property, performs, undergoes, used-for, can-be-used-for, located-in, causes, enables, before, after, equivalent, opposite. Each maps to an explicit supplied sentence frame. Evidence is required; conditional relations require conditions, comparisons require criteria. Missing data yields unresolved. Only explicitly provided inverse rules execute. Unknown task cues return unresolved route; there is no arbitrary default on unfamiliar requests.

Ten unit checks passed, including all 16 sentence frames, evidence and condition requirements, comparison scope, possibility versus actuality, inverse restrictions, unknown relation/task handling and native collapse-guard rejection. Evaluation changes entity names but retains training task cues; it establishes task-to-operation routing and not free language understanding or transfer to unseen paraphrases. Synthetic facts and frames are supplied, not discovered. No claim of biological truth validation or full grammar correctness. Learned history, corrections and full per-task evaluation are included.

Next: curated natural language examples with separate paraphrase/domain holdouts; relation type/role validators, property values and temporal conditions; integrate cards into native grammar-guide/Mirror output and lexical I/O. Complete history can be restored into AlgorithmMatrix.history using tuple(relation,task) keys from learned-routing.json.

Run from package root:
python3 Algorithms/relation-training/train_relations.py
python3 -m unittest discover -s Algorithms/relation-training -v
