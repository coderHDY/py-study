-- 在 Supabase SQL Editor 中执行（维度须与后端 EMBEDDING_DIM / 向量列一致，当前默认 512）
create extension if not exists vector;

create table if not exists rag_chunks (
  id bigserial primary key,
  content text not null,
  metadata jsonb default '{}'::jsonb,
  embedding vector(512)
);

-- 后端须使用 service_role 密钥（SUPABASE_SERVICE_ROLE_KEY），才会绕过 RLS。
-- 若误用 anon 会报：new row violates row-level security policy。
-- 若表仅在服务端访问、从不把密钥暴露给浏览器，可取消下一行注释以关闭本表 RLS（不推荐与 anon 同用）：
-- alter table rag_chunks disable row level security;

-- 有数据后再建索引更稳妥；数据量少时也可省略，用顺序扫描
-- create index if not exists rag_chunks_embedding_idx
--   on rag_chunks using ivfflat (embedding vector_cosine_ops) with (lists = 100);

create or replace function match_rag_chunks(
  query_embedding vector(512),
  match_count int default 5
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
  order by c.embedding <=> query_embedding
  limit greatest(match_count, 1);
$$;

create or replace function truncate_rag_chunks()
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  truncate table rag_chunks restart identity;
end;
$$;
