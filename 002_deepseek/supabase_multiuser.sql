-- 多设备用户隔离：客户端生成 user_id（X-Client-User-Id），RAG 片段与会话按 user_id 隔离。
-- 在 Supabase SQL Editor 中执行（若已有旧表，按注释做迁移）

create extension if not exists vector;

-- ========== 全局应用配置（所有用户共用性格/名字等，与原先 sessions.json 里 config 一致）==========
create table if not exists pumpkin_app_config (
  id text primary key default 'default',
  config jsonb not null default '{}'::jsonb,
  updated_at timestamptz default now()
);

insert into pumpkin_app_config (id, config)
values (
  'default',
  '{
    "name": "南瓜小助手",
    "personality": "You are a helpful assistant. 你是一个友好的AI南瓜智能伴侣。"
  }'::jsonb
)
on conflict (id) do nothing;

-- ========== 会话（每用户独立）==========
create table if not exists pumpkin_sessions (
  user_id text not null,
  id text not null,
  title text not null default '新会话',
  messages jsonb not null default '[]'::jsonb,
  updated_at timestamptz default now(),
  primary key (user_id, id)
);

create index if not exists pumpkin_sessions_user_updated_idx
  on pumpkin_sessions (user_id, updated_at desc);

-- ========== RAG 向量片段（带 user_id）==========
-- 若表已存在且无 user_id，执行：
-- alter table rag_chunks add column if not exists user_id text not null default '';
-- 然后建议：delete from rag_chunks where user_id = ''; 或回填后再改 default

create table if not exists rag_chunks (
  id bigserial primary key,
  user_id text not null default '',
  content text not null,
  metadata jsonb default '{}'::jsonb,
  embedding vector(384)
);

-- 已有表时仅补列（与上面 create 二选一场景）
alter table rag_chunks add column if not exists user_id text not null default '';

create index if not exists rag_chunks_user_id_idx on rag_chunks (user_id);

-- 按用户相似度检索（务必与后端 RPC 参数一致）
create or replace function match_rag_chunks(
  query_embedding vector(384),
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

-- 旧的全表 truncate 可保留给运维；应用侧按 user_id 删除，不用此 RPC 亦可
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
