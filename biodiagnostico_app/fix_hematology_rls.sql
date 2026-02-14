-- =====================================================
-- FIX: Corrigir RLS das tabelas de Hematologia
-- Executar no SQL Editor do Supabase Dashboard
-- =====================================================
-- Problema: RLS restritivo (user_id = auth.uid()) rejeita inserts
-- quando o app não envia user_id correto.
-- Solução: Alinhar com o padrão das demais tabelas QC (permissivo).

-- ========================
-- 1. hematology_qc_parameters
-- ========================

-- Tornar user_id nullable
ALTER TABLE hematology_qc_parameters ALTER COLUMN user_id DROP NOT NULL;

-- Trocar RLS para permissivo
DROP POLICY IF EXISTS "Users manage own hqc_parameters" ON hematology_qc_parameters;
DROP POLICY IF EXISTS "Authenticated full access hqc_parameters" ON hematology_qc_parameters;
CREATE POLICY "Authenticated full access hqc_parameters"
    ON hematology_qc_parameters FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);


-- ========================
-- 2. hematology_qc_measurements
-- ========================

-- Tornar user_id nullable
ALTER TABLE hematology_qc_measurements ALTER COLUMN user_id DROP NOT NULL;

-- Trocar RLS para permissivo
DROP POLICY IF EXISTS "Users manage own hqc_measurements" ON hematology_qc_measurements;
DROP POLICY IF EXISTS "Authenticated full access hqc_measurements" ON hematology_qc_measurements;
CREATE POLICY "Authenticated full access hqc_measurements"
    ON hematology_qc_measurements FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);


-- ========================
-- 3. hematology_bio_records
-- ========================

-- Tornar user_id nullable
ALTER TABLE hematology_bio_records ALTER COLUMN user_id DROP NOT NULL;

-- Trocar RLS para permissivo
DROP POLICY IF EXISTS "hematology_bio_records_select" ON hematology_bio_records;
DROP POLICY IF EXISTS "hematology_bio_records_insert" ON hematology_bio_records;
DROP POLICY IF EXISTS "hematology_bio_records_delete" ON hematology_bio_records;
DROP POLICY IF EXISTS "Authenticated full access hematology_bio_records" ON hematology_bio_records;
CREATE POLICY "Authenticated full access hematology_bio_records"
    ON hematology_bio_records FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);


-- ========================
-- 4. Atualizar RPC (remover filtro por user_id)
-- ========================

CREATE OR REPLACE FUNCTION hematology_register_qc_measurement(
    p_data_medicao      DATE,
    p_analito           TEXT,
    p_valor_medido      NUMERIC,
    p_equipamento       TEXT DEFAULT NULL,
    p_lote_controle     TEXT DEFAULT NULL,
    p_nivel_controle    TEXT DEFAULT NULL,
    p_observacao        TEXT DEFAULT NULL
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_param       RECORD;
    v_min         NUMERIC;
    v_max         NUMERIC;
    v_status      hematology_qc_status;
    v_meas_id     UUID;
BEGIN
    SELECT *
    INTO v_param
    FROM hematology_qc_parameters
    WHERE analito    = p_analito
      AND is_active  = true
    ORDER BY
        (CASE WHEN equipamento    IS NOT NULL AND equipamento    = p_equipamento    THEN 1 ELSE 0 END
       + CASE WHEN lote_controle  IS NOT NULL AND lote_controle  = p_lote_controle  THEN 1 ELSE 0 END
       + CASE WHEN nivel_controle IS NOT NULL AND nivel_controle = p_nivel_controle THEN 1 ELSE 0 END) DESC,
        created_at DESC
    LIMIT 1;

    IF v_param IS NULL THEN
        RAISE EXCEPTION 'Nenhum parâmetro ativo encontrado para o analito "%" do usuário corrente. Cadastre um parâmetro antes de registrar medições.', p_analito;
    END IF;

    IF v_param.modo = 'INTERVALO' THEN
        v_min := v_param.min_valor;
        v_max := v_param.max_valor;
    ELSE
        v_min := v_param.alvo_valor * (1 - v_param.tolerancia_percentual / 100.0);
        v_max := v_param.alvo_valor * (1 + v_param.tolerancia_percentual / 100.0);
    END IF;

    IF p_valor_medido >= v_min AND p_valor_medido <= v_max THEN
        v_status := 'APROVADO';
    ELSE
        v_status := 'REPROVADO';
    END IF;

    INSERT INTO hematology_qc_measurements (
        data_medicao, analito, valor_medido,
        parameter_id, modo_usado, min_aplicado, max_aplicado,
        status, observacao, user_id
    ) VALUES (
        p_data_medicao, p_analito, p_valor_medido,
        v_param.id, v_param.modo, v_min, v_max,
        v_status, p_observacao, auth.uid()
    )
    RETURNING id INTO v_meas_id;

    RETURN json_build_object(
        'measurement_id',  v_meas_id,
        'status',          v_status::TEXT,
        'min_aplicado',    v_min,
        'max_aplicado',    v_max,
        'parametro_id',    v_param.id
    );
END;
$$;
