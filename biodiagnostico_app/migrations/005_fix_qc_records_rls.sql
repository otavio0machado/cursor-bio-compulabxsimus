-- Migracao: Desabilitar RLS na tabela qc_records
-- Data: 2026-02-08
-- Descricao: A tabela qc_records nao precisa de RLS pois o app usa
--            a chave anon do Supabase. Manter RLS desabilitado para
--            garantir acesso livre a leitura e escrita.

-- Desabilitar RLS (a tabela nunca teve RLS habilitado originalmente)
ALTER TABLE public.qc_records DISABLE ROW LEVEL SECURITY;

-- Limpar policy caso exista (nao sera necessaria sem RLS)
DROP POLICY IF EXISTS "Permitir acesso publico qc_records" ON public.qc_records;
