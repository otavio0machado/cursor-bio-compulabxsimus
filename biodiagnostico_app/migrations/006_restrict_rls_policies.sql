-- Migracao: Restringir politicas RLS para apenas usuarios autenticados
-- Data: 2026-02-08
-- Descricao: Remove acesso 'anon' de todas as tabelas. Apenas 'authenticated' pode acessar.
-- IMPORTANTE: Executar no SQL Editor do Supabase Dashboard.

-- =====================================================
-- 1. qc_records
-- =====================================================
DROP POLICY IF EXISTS "Permitir acesso publico qc_records" ON public.qc_records;
CREATE POLICY "Authenticated full access qc_records" ON public.qc_records
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- =====================================================
-- 2. qc_reference_values
-- =====================================================
DROP POLICY IF EXISTS "Permitir acesso publico qc_reference_values" ON public.qc_reference_values;
DROP POLICY IF EXISTS "Authenticated users can manage qc_reference_values" ON public.qc_reference_values;
CREATE POLICY "Authenticated full access qc_reference_values" ON public.qc_reference_values
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- =====================================================
-- 3. qc_exams
-- =====================================================
DROP POLICY IF EXISTS "Permitir acesso publico qc_exams" ON public.qc_exams;
DROP POLICY IF EXISTS "Authenticated users can manage qc_exams" ON public.qc_exams;
CREATE POLICY "Authenticated full access qc_exams" ON public.qc_exams
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- =====================================================
-- 4. qc_registry_names
-- =====================================================
DROP POLICY IF EXISTS "Permitir acesso publico qc_registry_names" ON public.qc_registry_names;
DROP POLICY IF EXISTS "Authenticated users can manage qc_registry_names" ON public.qc_registry_names;
CREATE POLICY "Authenticated full access qc_registry_names" ON public.qc_registry_names
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- =====================================================
-- 5. reagent_lots
-- =====================================================
DROP POLICY IF EXISTS "Authenticated users can manage reagent_lots" ON public.reagent_lots;
CREATE POLICY "Authenticated full access reagent_lots" ON public.reagent_lots
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- =====================================================
-- 6. maintenance_records
-- =====================================================
DROP POLICY IF EXISTS "Authenticated users can manage maintenance_records" ON public.maintenance_records;
CREATE POLICY "Authenticated full access maintenance_records" ON public.maintenance_records
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- =====================================================
-- 7. post_calibration_records
-- =====================================================
DROP POLICY IF EXISTS "Authenticated users can manage post_calibration_records" ON public.post_calibration_records;
CREATE POLICY "Authenticated full access post_calibration_records" ON public.post_calibration_records
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- =====================================================
-- 8. audit_summaries (tabela legacy)
-- =====================================================
DROP POLICY IF EXISTS "Permitir acesso público audit_summaries" ON public.audit_summaries;
CREATE POLICY "Authenticated full access audit_summaries" ON public.audit_summaries
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- =====================================================
-- 9. patient_history (tabela legacy)
-- =====================================================
DROP POLICY IF EXISTS "Permitir acesso público patient_history" ON public.patient_history;
CREATE POLICY "Authenticated full access patient_history" ON public.patient_history
    FOR ALL TO authenticated USING (true) WITH CHECK (true);
