# libraries

Empty shelf. Reserved for compiled, importable Python modules built from /matrices and /indices.

- `ladder.py`, `ladder_load.py`, `ladder_schema.sql`: the ladder (datasets → registries → matrices → indices → codices). Breaks each source on the datasets shelf into elementary pieces, rebuilds it from those pieces alone, and loads it into Neon. Run by `.github/workflows/ladder.yml`.
