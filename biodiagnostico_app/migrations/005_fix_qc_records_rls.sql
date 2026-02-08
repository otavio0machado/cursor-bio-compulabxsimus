-- Migracao: Corrigir RLS na tabela qc_records
-- Data: 2026-02-08
-- Descricao: Habilitar RLS com policy para roles anon e authenticated

ALTER TABLE public.qc_records ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Permitir acesso publico qc_records" ON public.qc_records;
CREATE POLICY "Permitir acesso publico qc_records" ON public.qc_records
    FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);
