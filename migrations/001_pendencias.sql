-- migrations/001_pendencias.sql
-- Tabela para guardar perguntas de volta pendentes do classificador.
-- Uma linha por telefone (upsert). TTL aplicado em código (db.py): 15 minutos.
-- Rodar uma única vez no SQL Editor do Supabase.

create table if not exists public.pendencias (
    telefone     text        primary key,
    mensagem     text        not null,
    pergunta     text        not null,
    tentativas   integer     not null default 1,
    responsavel  text,
    created_at   timestamptz not null default now(),
    updated_at   timestamptz not null default now()
);

create index if not exists idx_pendencias_created_at
    on public.pendencias (created_at);

-- Trigger para manter updated_at sincronizado
create or replace function public.touch_pendencias_updated_at()
returns trigger language plpgsql as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists trg_pendencias_updated_at on public.pendencias;
create trigger trg_pendencias_updated_at
    before update on public.pendencias
    for each row
    execute function public.touch_pendencias_updated_at();
