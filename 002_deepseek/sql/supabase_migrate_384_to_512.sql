-- 将 rag_chunks 从 vector(384) 升级为 vector(512)，与当前后端默认 EMBEDDING_DIM=512 一致。
-- 在 Supabase → SQL Editor 中整段执行（会清空 RAG 表内所有向量，需重新上传建库）。

truncate table rag_chunks restart identity;

alter table rag_chunks
  alter column embedding type vector(512);

create or replace function match_rag_chunks(
  query_embedding vector(512),
  match_count int default 5,
  filter_user_id text default ''
)
returns table (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language sql
stable
as $$
  select
    c.id,
    c.content,
    c.metadata,
    (1 - (c.embedding <=> query_embedding))::float as similarity
  from rag_chunks c
  where c.user_id = filter_user_id
  order by c.embedding <=> query_embedding
  limit greatest(match_count, 1);
$$;
