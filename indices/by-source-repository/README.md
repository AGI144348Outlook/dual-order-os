# By source repository

Lookup-first: given a source repository, what is in it and where.

| Repository | What is here |
| --- | --- |
| [echo-green-future/](echo-green-future/) | The inventory of [Echo_Green_Future](https://github.com/AGI144348Outlook/Echo_Green_Future): all 42 branches file by file, sorted into 22 folders (algorithms, logics, schemas, …), each row pointing at its source by branch, path and git fingerprint. Kept in step with that repository's `integration/echo-whole` branch, where the sweeps run. |

`echo-green-future/explorer.html` is a self-contained page for browsing the inventory and sorting any uploaded
files or `.zip` by a category word. Download it and open it in a browser; it needs no server.

The sweep scripts under `echo-green-future/*/sweeps/` read an Echo_Green_Future clone:
`python3 indices/by-source-repository/echo-green-future/logics/sweeps/sweep_1_logics.py <path to Echo_Green_Future clone>`.
Run that way they write into the clone's `inventory/`, not here.
