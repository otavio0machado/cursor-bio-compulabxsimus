-- Migracao: Criar tabela de Nomes de Registro do CQ
-- Data: 2026-02-07
-- Descricao: Nomes reutilizaveis para registros de referencia (ex: "Kit ControlLab Jan/2026")

CREATE TABLE IF NOT EXISTS public.qc_registry_names (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    name text NOT NULL UNIQUE,
    is_active boolean DEFAULT true,
    created_at timestamptz DEFAULT now()
);

-- Indices
CREATE INDEX IF NOT EXISTS idx_qc_registry_names_active ON public.qc_registry_names(is_active);

-- RLS
ALTER TABLE public.qc_registry_names ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir acesso publico qc_registry_names" ON public.qc_registry_names;
CREATE POLICY "Permitir acesso publico qc_registry_names" ON public.qc_registry_names FOR ALL USING (true);
