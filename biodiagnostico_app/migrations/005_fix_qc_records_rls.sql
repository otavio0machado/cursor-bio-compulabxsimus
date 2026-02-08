-- Migracao: Garantir RLS policy na tabela qc_records
-- Data: 2026-02-08
-- Descricao: Se RLS estiver habilitado em qc_records sem policy,
--            todas as operacoes sao bloqueadas. Esta migracao garante
--            que a policy de acesso publico existe.

-- Habilitar RLS (idempotente)
ALTER TABLE public.qc_records ENABLE ROW LEVEL SECURITY;

-- Criar policy permissiva (permite todas as operacoes)
DROP POLICY IF EXISTS "Permitir acesso publico qc_records" ON public.qc_records;
CREATE POLICY "Permitir acesso publico qc_records" ON public.qc_records
    FOR ALL USING (true) WITH CHECK (true);
