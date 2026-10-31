-- The ladder schema as it exists in Neon (project purple-thunder-44046403, schema "ladder").
-- Kept here as the record of the tables the loader writes to, and used by the tests to
-- build a throwaway copy. The loader never runs this against Neon.
--
-- Every table is append-only: rows can be added, never changed or removed.

create schema if not exists ladder;

create or replace function public.forbid_change() returns trigger language plpgsql as
$$ begin raise exception '% is append-only: rows can be added, never changed or removed', TG_TABLE_NAME; end $$;

-- rung 1: datasets, the source exactly as found, with where it came from
create table ladder.dataset (
  id text primary key,
  provenance jsonb not null,
  sha256 text not null,
  chars integer not null,
  text text,
  note text
);

-- rung 2: registries, one row per elementary piece; identical pieces share one row
create table ladder.registry (
  piece_id text primary key,   -- "<kind>:<number>", e.g. statement:0042
  kind text not null,
  text text not null
);

-- rung 5: codices, the assembly; each segment points at one registry piece
create table ladder.codex (
  id text primary key,
  dataset_id text not null references ladder.dataset(id),
  format text not null check (format in ('prose', 'json'))
);

create table ladder.codex_segment (
  codex_id text not null references ladder.codex(id),
  pos integer not null,
  piece_id text not null references ladder.registry(piece_id),
  primary key (codex_id, pos)
);

-- rung 4: indices that are stored rather than computed
create table ladder.index_term (
  name text not null,
  piece_id text not null references ladder.registry(piece_id),
  primary key (name, piece_id)
);

create trigger dataset_append_only before update or delete on ladder.dataset for each row execute function forbid_change();
create trigger registry_append_only before update or delete on ladder.registry for each row execute function forbid_change();
create trigger codex_append_only before update or delete on ladder.codex for each row execute function forbid_change();
create trigger codex_segment_append_only before update or delete on ladder.codex_segment for each row execute function forbid_change();
create trigger index_term_append_only before update or delete on ladder.index_term for each row execute function forbid_change();

-- rung 3: matrices, content-first, computed from the registry
create view ladder.matrix as
  select r.kind, r.piece_id, r.text, count(s.*) as occurrences, array_agg(distinct s.codex_id) as codices
  from ladder.registry r join ladder.codex_segment s using (piece_id)
  where r.kind <> all (array['glue', 'shape'])
  group by r.kind, r.piece_id, r.text;

-- rung 4: lookup-first indices, computed
create view ladder.index_by_source as
  select c.dataset_id, s.piece_id, r.kind
  from ladder.codex c join ladder.codex_segment s on s.codex_id = c.id join ladder.registry r using (piece_id)
  where r.kind <> all (array['glue', 'shape'])
  group by c.dataset_id, s.piece_id, r.kind;

-- climbing back up: prose codices reassembled from their pieces
create view ladder.rebuild_prose as
  select c.id as codex_id, string_agg(r.text, '' order by s.pos) as text
  from ladder.codex c join ladder.codex_segment s on s.codex_id = c.id join ladder.registry r using (piece_id)
  where c.format = 'prose'
  group by c.id;
