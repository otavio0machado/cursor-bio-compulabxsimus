-- =====================================================
-- Migration: Hematologia CQ por Intervalo / Percentual
-- Executar no SQL Editor do Supabase Dashboard
-- =====================================================

-- ========================
-- 1. ENUM TYPES
-- ========================

DO $$ BEGIN
    CREATE TYPE hematology_qc_mode AS ENUM ('INTERVALO', 'PERCENTUAL');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE hematology_qc_status AS ENUM ('APROVADO', 'REPROVADO');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


-- ========================
-- 2. TABELA DE PARÂMETROS (REGRAS)
-- ========================

CREATE TABLE IF NOT EXISTS hematology_qc_parameters (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    analito         TEXT NOT NULL,                          -- RBC, HGB, HCT, WBC, PLT, RDW, MPV ...
    equipamento     TEXT,
    lote_controle   TEXT,
    nivel_controle  TEXT,

    modo            hematology_qc_mode NOT NULL,
    alvo_valor      NUMERIC NOT NULL CHECK (alvo_valor > 0),

    -- Modo INTERVALO
    min_valor       NUMERIC,
    max_valor       NUMERIC,

    -- Modo PERCENTUAL
    tolerancia_percentual NUMERIC,

    is_active       BOOLEAN NOT NULL DEFAULT true,
    user_id         UUID REFERENCES auth.users(id),

    -- ==========================================
    -- CONSTRAINTS DE INTEGRIDADE POR MODO
    -- ==========================================
    CONSTRAINT chk_intervalo CHECK (
        modo <> 'INTERVALO'
        OR (
            min_valor IS NOT NULL
            AND max_valor IS NOT NULL
            AND min_valor <= max_valor
            AND tolerancia_percentual IS NULL
        )
    ),
    CONSTRAINT chk_percentual CHECK (
        modo <> 'PERCENTUAL'
        OR (
            tolerancia_percentual IS NOT NULL
            AND tolerancia_percentual > 0
            AND tolerancia_percentual <= 100
            AND min_valor IS NULL
            AND max_valor IS NULL
        )
    )
);


-- ========================
-- 3. ÍNDICES — PARÂMETROS
-- ========================

CREATE INDEX IF NOT EXISTS idx_hqc_params_user_analito_active
    ON hematology_qc_parameters (user_id, analito, is_active);

CREATE INDEX IF NOT EXISTS idx_hqc_params_user_full_match
    ON hematology_qc_parameters (user_id, analito, equipamento, lote_controle, nivel_controle, is_active);


-- ========================
-- 4. TRIGGER updated_at
-- ========================

CREATE OR REPLACE FUNCTION trg_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_updated_at ON hematology_qc_parameters;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON hematology_qc_parameters
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();


-- ========================
-- 5. TABELA DE MEDIÇÕES (LANÇAMENTOS)
-- ========================

CREATE TABLE IF NOT EXISTS hematology_qc_measurements (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    data_medicao    DATE NOT NULL,
    analito         TEXT NOT NULL,
    valor_medido    NUMERIC NOT NULL,

    parameter_id    UUID NOT NULL REFERENCES hematology_qc_parameters(id),
    modo_usado      hematology_qc_mode NOT NULL,
    min_aplicado    NUMERIC NOT NULL,
    max_aplicado    NUMERIC NOT NULL,
    status          hematology_qc_status NOT NULL,

    observacao      TEXT,
    user_id         UUID REFERENCES auth.users(id)
);


-- ========================
-- 6. ÍNDICES — MEDIÇÕES
-- ========================

CREATE INDEX IF NOT EXISTS idx_hqc_meas_user_date
    ON hematology_qc_measurements (user_id, data_medicao DESC);

CREATE INDEX IF NOT EXISTS idx_hqc_meas_user_analito_date
    ON hematology_qc_measurements (user_id, analito, data_medicao DESC);

CREATE INDEX IF NOT EXISTS idx_hqc_meas_user_status_date
    ON hematology_qc_measurements (user_id, status, data_medicao DESC);


-- ========================
-- 7. VIEW RESOLVIDA (parâmetros com min/max/% sempre calculados)
-- ========================

CREATE OR REPLACE VIEW v_hematology_qc_parameters_resolved AS
SELECT
    p.*,
    -- min_calc / max_calc: sempre preenchidos
    CASE
        WHEN p.modo = 'INTERVALO' THEN p.min_valor
        ELSE p.alvo_valor * (1 - p.tolerancia_percentual / 100.0)
    END AS min_calc,
    CASE
        WHEN p.modo = 'INTERVALO' THEN p.max_valor
        ELSE p.alvo_valor * (1 + p.tolerancia_percentual / 100.0)
    END AS max_calc,
    -- percentual_equivalente: sempre preenchido
    CASE
        WHEN p.modo = 'PERCENTUAL' THEN p.tolerancia_percentual
        ELSE CASE
            WHEN p.alvo_valor > 0 THEN
                GREATEST(
                    ABS(p.max_valor - p.alvo_valor),
                    ABS(p.alvo_valor - p.min_valor)
                ) / p.alvo_valor * 100.0
            ELSE 0
        END
    END AS percentual_equivalente
FROM hematology_qc_parameters p;


-- ========================
-- 8. RPC — Registrar medição com consistência total
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
    -- ============================
    -- Buscar parâmetro ativo (mais específico primeiro)
    -- ============================
    SELECT *
    INTO v_param
    FROM hematology_qc_parameters
    WHERE analito    = p_analito
      AND is_active  = true
    ORDER BY
        -- prioridade: match mais específico
        (CASE WHEN equipamento    IS NOT NULL AND equipamento    = p_equipamento    THEN 1 ELSE 0 END
       + CASE WHEN lote_controle  IS NOT NULL AND lote_controle  = p_lote_controle  THEN 1 ELSE 0 END
       + CASE WHEN nivel_controle IS NOT NULL AND nivel_controle = p_nivel_controle THEN 1 ELSE 0 END) DESC,
        created_at DESC
    LIMIT 1;

    IF v_param IS NULL THEN
        RAISE EXCEPTION 'Nenhum parâmetro ativo encontrado para o analito "%" do usuário corrente. Cadastre um parâmetro antes de registrar medições.', p_analito;
    END IF;

    -- ============================
    -- Calcular min/max conforme modo
    -- ============================
    IF v_param.modo = 'INTERVALO' THEN
        v_min := v_param.min_valor;
        v_max := v_param.max_valor;
    ELSE  -- PERCENTUAL
        v_min := v_param.alvo_valor * (1 - v_param.tolerancia_percentual / 100.0);
        v_max := v_param.alvo_valor * (1 + v_param.tolerancia_percentual / 100.0);
    END IF;

    -- ============================
    -- Calcular status
    -- ============================
    IF p_valor_medido >= v_min AND p_valor_medido <= v_max THEN
        v_status := 'APROVADO';
    ELSE
        v_status := 'REPROVADO';
    END IF;

    -- ============================
    -- Inserir medição
    -- ============================
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

    -- ============================
    -- Retornar resultado
    -- ============================
    RETURN json_build_object(
        'measurement_id',  v_meas_id,
        'status',          v_status::TEXT,
        'min_aplicado',    v_min,
        'max_aplicado',    v_max,
        'parametro_id',    v_param.id
    );
END;
$$;


-- ========================
-- 9. RLS (Row Level Security) — Permissivo (consistente com demais tabelas QC)
-- ========================

ALTER TABLE hematology_qc_parameters ENABLE ROW LEVEL SECURITY;
ALTER TABLE hematology_qc_measurements ENABLE ROW LEVEL SECURITY;

-- Parâmetros: acesso total para autenticados
DROP POLICY IF EXISTS "Users manage own hqc_parameters" ON hematology_qc_parameters;
CREATE POLICY "Authenticated full access hqc_parameters"
    ON hematology_qc_parameters FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- Medições: acesso total para autenticados
DROP POLICY IF EXISTS "Users manage own hqc_measurements" ON hematology_qc_measurements;
CREATE POLICY "Authenticated full access hqc_measurements"
    ON hematology_qc_measurements FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);


-- ========================
-- 10. QUERIES DE TESTE QA
-- ========================

/*
-- Testar constraint: alvo_valor = 0 deve falhar
INSERT INTO hematology_qc_parameters (analito, modo, alvo_valor, min_valor, max_valor, user_id)
VALUES ('RBC', 'INTERVALO', 0, 4.0, 5.5, auth.uid());
-- Esperado: ERROR (CHECK alvo_valor > 0)

-- Testar constraint: INTERVALO sem min/max deve falhar
INSERT INTO hematology_qc_parameters (analito, modo, alvo_valor, user_id)
VALUES ('RBC', 'INTERVALO', 4.5, auth.uid());
-- Esperado: ERROR (CHECK chk_intervalo)

-- Testar constraint: PERCENTUAL sem tolerancia deve falhar
INSERT INTO hematology_qc_parameters (analito, modo, alvo_valor, user_id)
VALUES ('RBC', 'PERCENTUAL', 4.5, auth.uid());
-- Esperado: ERROR (CHECK chk_percentual)

-- Testar constraint: PERCENTUAL com min/max deve falhar
INSERT INTO hematology_qc_parameters (analito, modo, alvo_valor, tolerancia_percentual, min_valor, max_valor, user_id)
VALUES ('RBC', 'PERCENTUAL', 4.5, 5, 4.0, 5.0, auth.uid());
-- Esperado: ERROR (CHECK chk_percentual)

-- Inserir parâmetro INTERVALO válido
INSERT INTO hematology_qc_parameters (analito, modo, alvo_valor, min_valor, max_valor, user_id)
VALUES ('RBC', 'INTERVALO', 4.5, 4.0, 5.5, auth.uid());

-- Inserir parâmetro PERCENTUAL válido
INSERT INTO hematology_qc_parameters (analito, modo, alvo_valor, tolerancia_percentual, user_id)
VALUES ('HGB', 'PERCENTUAL', 14.0, 5, auth.uid());

-- Verificar VIEW
SELECT analito, modo, alvo_valor, min_calc, max_calc, percentual_equivalente
FROM v_hematology_qc_parameters_resolved
WHERE user_id = auth.uid() AND is_active = true;

-- Testar RPC: valor dentro do range => APROVADO
SELECT hematology_register_qc_measurement(
    CURRENT_DATE, 'RBC', 4.8
);

-- Testar RPC: valor igual ao min => APROVADO (limítrofe)
SELECT hematology_register_qc_measurement(
    CURRENT_DATE, 'RBC', 4.0
);

-- Testar RPC: valor igual ao max => APROVADO (limítrofe)
SELECT hematology_register_qc_measurement(
    CURRENT_DATE, 'RBC', 5.5
);

-- Testar RPC: valor fora => REPROVADO
SELECT hematology_register_qc_measurement(
    CURRENT_DATE, 'RBC', 6.0
);

-- Testar RPC: analito sem parâmetro => ERRO
SELECT hematology_register_qc_measurement(
    CURRENT_DATE, 'INEXISTENTE', 1.0
);
-- Esperado: RAISE EXCEPTION

-- Verificar medições
SELECT * FROM hematology_qc_measurements
WHERE user_id = auth.uid()
ORDER BY data_medicao DESC;
*/

-- =====================================================================
-- PARTE 2: Tabela Bio x Controle Interno (Hematologia)
-- =====================================================================

CREATE TABLE IF NOT EXISTS public.hematology_bio_records (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),

    -- Datas e identificadores
    data_bio date NOT NULL,
    data_pad date,
    registro_bio text,
    registro_pad text,
    modo_ci text NOT NULL DEFAULT 'bio',  -- 'bio', 'intervalo', 'porcentagem'

    -- Valores Biodiagnostico
    bio_hemacias numeric,
    bio_hematocrito numeric,
    bio_hemoglobina numeric,
    bio_leucocitos numeric,
    bio_plaquetas numeric,
    bio_rdw numeric,
    bio_vpm numeric,

    -- Valores Controle Interno (modo bio)
    pad_hemacias numeric,
    pad_hematocrito numeric,
    pad_hemoglobina numeric,
    pad_leucocitos numeric,
    pad_plaquetas numeric,
    pad_rdw numeric,
    pad_vpm numeric,

    -- Valores Controle Interno (modo intervalo)
    ci_min_hemacias numeric,
    ci_max_hemacias numeric,
    ci_min_hematocrito numeric,
    ci_max_hematocrito numeric,
    ci_min_hemoglobina numeric,
    ci_max_hemoglobina numeric,
    ci_min_leucocitos numeric,
    ci_max_leucocitos numeric,
    ci_min_plaquetas numeric,
    ci_max_plaquetas numeric,
    ci_min_rdw numeric,
    ci_max_rdw numeric,
    ci_min_vpm numeric,
    ci_max_vpm numeric,

    -- Valores Controle Interno (modo porcentagem)
    ci_pct_hemacias numeric,
    ci_pct_hematocrito numeric,
    ci_pct_hemoglobina numeric,
    ci_pct_leucocitos numeric,
    ci_pct_plaquetas numeric,
    ci_pct_rdw numeric,
    ci_pct_vpm numeric,

    -- Segurança (user_id opcional, RLS permissivo — consistente com demais tabelas QC)
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,

    CONSTRAINT chk_modo_ci CHECK (modo_ci IN ('bio', 'intervalo', 'porcentagem'))
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_hbio_data ON public.hematology_bio_records(data_bio DESC);

-- RLS — permissivo (consistente com qc_records, reagent_lots, etc.)
ALTER TABLE public.hematology_bio_records ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "hematology_bio_records_select" ON public.hematology_bio_records;
DROP POLICY IF EXISTS "hematology_bio_records_insert" ON public.hematology_bio_records;
DROP POLICY IF EXISTS "hematology_bio_records_delete" ON public.hematology_bio_records;

CREATE POLICY "Authenticated full access hematology_bio_records"
    ON public.hematology_bio_records FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);
