-- Migracao: Criar tabela de Exames do CQ (gerenciavel pelo usuario)
-- Data: 2026-02-07
-- Descricao: Substitui a lista hardcoded ALLOWED_QC_EXAMS por uma tabela dinamica

CREATE TABLE IF NOT EXISTS public.qc_exams (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    name text NOT NULL UNIQUE,
    display_order int NOT NULL DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamptz DEFAULT now()
);

-- Indices
CREATE INDEX IF NOT EXISTS idx_qc_exams_active ON public.qc_exams(is_active);
CREATE INDEX IF NOT EXISTS idx_qc_exams_order ON public.qc_exams(display_order);

-- RLS
ALTER TABLE public.qc_exams ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir acesso publico qc_exams" ON public.qc_exams;
CREATE POLICY "Permitir acesso publico qc_exams" ON public.qc_exams FOR ALL USING (true);

-- Seed com os exames atuais (mesma ordem do ALLOWED_QC_EXAMS original)
INSERT INTO public.qc_exams (name, display_order) VALUES
    ('GLICOSE', 1),
    ('COLESTEROL TOTAL', 2),
    ('TRIGLICERIDEOS', 3),
    ('UREIA', 4),
    ('CREATININA', 5),
    ('ACIDO URICO', 6),
    ('GOT', 7),
    ('GPT', 8),
    ('GAMA GT', 9),
    ('FOSFATASE ALCALINA', 10),
    ('AMILASE', 11),
    ('CREATINOFOSFOQUINASE', 12),
    ('COLESTEROL HDL', 13),
    ('COLESTEROL LDL', 14)
ON CONFLICT (name) DO NOTHING;

-- Garantir que colunas cv e status existem em qc_records (para persistir status corretamente)
ALTER TABLE public.qc_records ADD COLUMN IF NOT EXISTS cv double precision DEFAULT 0;
ALTER TABLE public.qc_records ADD COLUMN IF NOT EXISTS status text DEFAULT 'OK';
