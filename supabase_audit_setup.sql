-- Script de Configuração para Auditoria de Dados Master
-- Execute este script no SQL Editor do seu Painel Supabase

-- 1. Criar a tabela de logs de auditoria
CREATE TABLE IF NOT EXISTS public.data_audits (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    record_id text NOT NULL,
    table_name text NOT NULL,
    old_value text,
    new_value text,
    action text, -- 'insert', 'update', 'delete'
    user_id uuid, -- Opcional, se houver sistema de login
    consistency_result jsonb -- Armazena o JSON do Oráculo (Structured Output)
);

-- 2. Habilitar Segurança (RLS)
ALTER TABLE public.data_audits ENABLE ROW LEVEL SECURITY;

-- 3. Criar Política de Acesso (Ajuste conforme sua necessidade de segurança)
-- Por enquanto, permite inserção e leitura pública para desenvolvimento
CREATE POLICY "Permitir inserção de logs" ON public.data_audits FOR INSERT WITH CHECK (true);
CREATE POLICY "Permitir leitura de logs" ON public.data_audits FOR SELECT USING (true);

-- 4. Índice para busca rápida por registro
CREATE INDEX IF NOT EXISTS idx_audit_record ON public.data_audits (record_id);

COMMENT ON TABLE public.data_audits IS 'Tabela que armazena logs de auditoria e análises de consistência clínica via IA.';
