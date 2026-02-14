-- =====================================================
-- Migration: Outras Áreas Laboratoriais (CQ por Intervalo/Percentual)
-- Áreas: Imunologia, Parasitologia, Microbiologia, Uroanálise
-- Executar no SQL Editor do Supabase Dashboard
-- =====================================================

-- ========================
-- NOTA: Reutilizamos os ENUMs já criados pela hematologia
-- hematology_qc_mode ('INTERVALO', 'PERCENTUAL')
-- hematology_qc_status ('APROVADO', 'REPROVADO')
-- ========================


-- =====================================================
-- 1. IMUNOLOGIA
-- =====================================================

-- Tabela de Parâmetros
CREATE TABLE IF NOT EXISTS immunology_qc_parameters (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    analito         TEXT NOT NULL,
    equipamento     TEXT,
    lote_controle   TEXT,
    nivel_controle  TEXT,

    modo            hematology_qc_mode NOT NULL,
    alvo_valor      NUMERIC NOT NULL CHECK (alvo_valor > 0),

    min_valor       NUMERIC,
    max_valor       NUMERIC,
    tolerancia_percentual NUMERIC,

    is_active       BOOLEAN NOT NULL DEFAULT true,
    user_id         UUID REFERENCES auth.users(id),

    CONSTRAINT chk_immunology_intervalo CHECK (
        modo <> 'INTERVALO' OR (
            min_valor IS NOT NULL AND max_valor IS NOT NULL
            AND min_valor <= max_valor AND tolerancia_percentual IS NULL
        )
    ),
    CONSTRAINT chk_immunology_percentual CHECK (
        modo <> 'PERCENTUAL' OR (
            tolerancia_percentual IS NOT NULL AND tolerancia_percentual > 0
            AND tolerancia_percentual <= 100 AND min_valor IS NULL AND max_valor IS NULL
        )
    )
);

-- Tabela de Medições
CREATE TABLE IF NOT EXISTS immunology_qc_measurements (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    data_medicao    DATE NOT NULL,
    analito         TEXT NOT NULL,
    valor_medido    NUMERIC NOT NULL,

    parameter_id    UUID NOT NULL REFERENCES immunology_qc_parameters(id),
    modo_usado      hematology_qc_mode NOT NULL,
    min_aplicado    NUMERIC NOT NULL,
    max_aplicado    NUMERIC NOT NULL,
    status          hematology_qc_status NOT NULL,

    observacao      TEXT,
    user_id         UUID REFERENCES auth.users(id)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_imqc_params_user_analito ON immunology_qc_parameters(user_id, analito, is_active);
CREATE INDEX IF NOT EXISTS idx_imqc_meas_user_date ON immunology_qc_measurements(user_id, data_medicao DESC);
CREATE INDEX IF NOT EXISTS idx_imqc_meas_user_analito ON immunology_qc_measurements(user_id, analito, data_medicao DESC);

-- Trigger updated_at
DROP TRIGGER IF EXISTS set_updated_at ON immunology_qc_parameters;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON immunology_qc_parameters
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();

-- RPC
CREATE OR REPLACE FUNCTION immunology_register_qc_measurement(
    p_data_medicao DATE, p_analito TEXT, p_valor_medido NUMERIC,
    p_equipamento TEXT DEFAULT NULL, p_lote_controle TEXT DEFAULT NULL,
    p_nivel_controle TEXT DEFAULT NULL, p_observacao TEXT DEFAULT NULL
)
RETURNS JSON LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE
    v_param RECORD; v_min NUMERIC; v_max NUMERIC;
    v_status hematology_qc_status; v_meas_id UUID;
BEGIN
    SELECT * INTO v_param FROM immunology_qc_parameters
    WHERE analito = p_analito AND is_active = true
    ORDER BY (
        CASE WHEN equipamento IS NOT NULL AND equipamento = p_equipamento THEN 1 ELSE 0 END +
        CASE WHEN lote_controle IS NOT NULL AND lote_controle = p_lote_controle THEN 1 ELSE 0 END +
        CASE WHEN nivel_controle IS NOT NULL AND nivel_controle = p_nivel_controle THEN 1 ELSE 0 END
    ) DESC, created_at DESC LIMIT 1;

    IF v_param IS NULL THEN
        RAISE EXCEPTION 'Nenhum parâmetro ativo para o analito "%". Cadastre um parâmetro primeiro.', p_analito;
    END IF;

    IF v_param.modo = 'INTERVALO' THEN
        v_min := v_param.min_valor; v_max := v_param.max_valor;
    ELSE
        v_min := v_param.alvo_valor * (1 - v_param.tolerancia_percentual / 100.0);
        v_max := v_param.alvo_valor * (1 + v_param.tolerancia_percentual / 100.0);
    END IF;

    v_status := CASE WHEN p_valor_medido >= v_min AND p_valor_medido <= v_max
                THEN 'APROVADO'::hematology_qc_status
                ELSE 'REPROVADO'::hematology_qc_status END;

    INSERT INTO immunology_qc_measurements (
        data_medicao, analito, valor_medido, parameter_id, modo_usado,
        min_aplicado, max_aplicado, status, observacao, user_id
    ) VALUES (
        p_data_medicao, p_analito, p_valor_medido, v_param.id, v_param.modo,
        v_min, v_max, v_status, p_observacao, auth.uid()
    ) RETURNING id INTO v_meas_id;

    RETURN json_build_object(
        'measurement_id', v_meas_id, 'status', v_status::TEXT,
        'min_aplicado', v_min, 'max_aplicado', v_max, 'parametro_id', v_param.id
    );
END; $$;

-- RLS
ALTER TABLE immunology_qc_parameters ENABLE ROW LEVEL SECURITY;
ALTER TABLE immunology_qc_measurements ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Authenticated full access imqc_parameters" ON immunology_qc_parameters;
CREATE POLICY "Authenticated full access imqc_parameters" ON immunology_qc_parameters
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Authenticated full access imqc_measurements" ON immunology_qc_measurements;
CREATE POLICY "Authenticated full access imqc_measurements" ON immunology_qc_measurements
    FOR ALL TO authenticated USING (true) WITH CHECK (true);


-- =====================================================
-- 2. PARASITOLOGIA
-- =====================================================

-- Tabela de Parâmetros
CREATE TABLE IF NOT EXISTS parasitology_qc_parameters (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    analito         TEXT NOT NULL,
    equipamento     TEXT,
    lote_controle   TEXT,
    nivel_controle  TEXT,

    modo            hematology_qc_mode NOT NULL,
    alvo_valor      NUMERIC NOT NULL CHECK (alvo_valor > 0),

    min_valor       NUMERIC,
    max_valor       NUMERIC,
    tolerancia_percentual NUMERIC,

    is_active       BOOLEAN NOT NULL DEFAULT true,
    user_id         UUID REFERENCES auth.users(id),

    CONSTRAINT chk_parasitology_intervalo CHECK (
        modo <> 'INTERVALO' OR (
            min_valor IS NOT NULL AND max_valor IS NOT NULL
            AND min_valor <= max_valor AND tolerancia_percentual IS NULL
        )
    ),
    CONSTRAINT chk_parasitology_percentual CHECK (
        modo <> 'PERCENTUAL' OR (
            tolerancia_percentual IS NOT NULL AND tolerancia_percentual > 0
            AND tolerancia_percentual <= 100 AND min_valor IS NULL AND max_valor IS NULL
        )
    )
);

-- Tabela de Medições
CREATE TABLE IF NOT EXISTS parasitology_qc_measurements (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    data_medicao    DATE NOT NULL,
    analito         TEXT NOT NULL,
    valor_medido    NUMERIC NOT NULL,

    parameter_id    UUID NOT NULL REFERENCES parasitology_qc_parameters(id),
    modo_usado      hematology_qc_mode NOT NULL,
    min_aplicado    NUMERIC NOT NULL,
    max_aplicado    NUMERIC NOT NULL,
    status          hematology_qc_status NOT NULL,

    observacao      TEXT,
    user_id         UUID REFERENCES auth.users(id)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_paqc_params_user_analito ON parasitology_qc_parameters(user_id, analito, is_active);
CREATE INDEX IF NOT EXISTS idx_paqc_meas_user_date ON parasitology_qc_measurements(user_id, data_medicao DESC);
CREATE INDEX IF NOT EXISTS idx_paqc_meas_user_analito ON parasitology_qc_measurements(user_id, analito, data_medicao DESC);

-- Trigger updated_at
DROP TRIGGER IF EXISTS set_updated_at ON parasitology_qc_parameters;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON parasitology_qc_parameters
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();

-- RPC
CREATE OR REPLACE FUNCTION parasitology_register_qc_measurement(
    p_data_medicao DATE, p_analito TEXT, p_valor_medido NUMERIC,
    p_equipamento TEXT DEFAULT NULL, p_lote_controle TEXT DEFAULT NULL,
    p_nivel_controle TEXT DEFAULT NULL, p_observacao TEXT DEFAULT NULL
)
RETURNS JSON LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE
    v_param RECORD; v_min NUMERIC; v_max NUMERIC;
    v_status hematology_qc_status; v_meas_id UUID;
BEGIN
    SELECT * INTO v_param FROM parasitology_qc_parameters
    WHERE analito = p_analito AND is_active = true
    ORDER BY (
        CASE WHEN equipamento IS NOT NULL AND equipamento = p_equipamento THEN 1 ELSE 0 END +
        CASE WHEN lote_controle IS NOT NULL AND lote_controle = p_lote_controle THEN 1 ELSE 0 END +
        CASE WHEN nivel_controle IS NOT NULL AND nivel_controle = p_nivel_controle THEN 1 ELSE 0 END
    ) DESC, created_at DESC LIMIT 1;

    IF v_param IS NULL THEN
        RAISE EXCEPTION 'Nenhum parâmetro ativo para o analito "%". Cadastre um parâmetro primeiro.', p_analito;
    END IF;

    IF v_param.modo = 'INTERVALO' THEN
        v_min := v_param.min_valor; v_max := v_param.max_valor;
    ELSE
        v_min := v_param.alvo_valor * (1 - v_param.tolerancia_percentual / 100.0);
        v_max := v_param.alvo_valor * (1 + v_param.tolerancia_percentual / 100.0);
    END IF;

    v_status := CASE WHEN p_valor_medido >= v_min AND p_valor_medido <= v_max
                THEN 'APROVADO'::hematology_qc_status
                ELSE 'REPROVADO'::hematology_qc_status END;

    INSERT INTO parasitology_qc_measurements (
        data_medicao, analito, valor_medido, parameter_id, modo_usado,
        min_aplicado, max_aplicado, status, observacao, user_id
    ) VALUES (
        p_data_medicao, p_analito, p_valor_medido, v_param.id, v_param.modo,
        v_min, v_max, v_status, p_observacao, auth.uid()
    ) RETURNING id INTO v_meas_id;

    RETURN json_build_object(
        'measurement_id', v_meas_id, 'status', v_status::TEXT,
        'min_aplicado', v_min, 'max_aplicado', v_max, 'parametro_id', v_param.id
    );
END; $$;

-- RLS
ALTER TABLE parasitology_qc_parameters ENABLE ROW LEVEL SECURITY;
ALTER TABLE parasitology_qc_measurements ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Authenticated full access paqc_parameters" ON parasitology_qc_parameters;
CREATE POLICY "Authenticated full access paqc_parameters" ON parasitology_qc_parameters
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Authenticated full access paqc_measurements" ON parasitology_qc_measurements;
CREATE POLICY "Authenticated full access paqc_measurements" ON parasitology_qc_measurements
    FOR ALL TO authenticated USING (true) WITH CHECK (true);


-- =====================================================
-- 3. MICROBIOLOGIA
-- =====================================================

-- Tabela de Parâmetros
CREATE TABLE IF NOT EXISTS microbiology_qc_parameters (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    analito         TEXT NOT NULL,
    equipamento     TEXT,
    lote_controle   TEXT,
    nivel_controle  TEXT,

    modo            hematology_qc_mode NOT NULL,
    alvo_valor      NUMERIC NOT NULL CHECK (alvo_valor > 0),

    min_valor       NUMERIC,
    max_valor       NUMERIC,
    tolerancia_percentual NUMERIC,

    is_active       BOOLEAN NOT NULL DEFAULT true,
    user_id         UUID REFERENCES auth.users(id),

    CONSTRAINT chk_microbiology_intervalo CHECK (
        modo <> 'INTERVALO' OR (
            min_valor IS NOT NULL AND max_valor IS NOT NULL
            AND min_valor <= max_valor AND tolerancia_percentual IS NULL
        )
    ),
    CONSTRAINT chk_microbiology_percentual CHECK (
        modo <> 'PERCENTUAL' OR (
            tolerancia_percentual IS NOT NULL AND tolerancia_percentual > 0
            AND tolerancia_percentual <= 100 AND min_valor IS NULL AND max_valor IS NULL
        )
    )
);

-- Tabela de Medições
CREATE TABLE IF NOT EXISTS microbiology_qc_measurements (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    data_medicao    DATE NOT NULL,
    analito         TEXT NOT NULL,
    valor_medido    NUMERIC NOT NULL,

    parameter_id    UUID NOT NULL REFERENCES microbiology_qc_parameters(id),
    modo_usado      hematology_qc_mode NOT NULL,
    min_aplicado    NUMERIC NOT NULL,
    max_aplicado    NUMERIC NOT NULL,
    status          hematology_qc_status NOT NULL,

    observacao      TEXT,
    user_id         UUID REFERENCES auth.users(id)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_miqc_params_user_analito ON microbiology_qc_parameters(user_id, analito, is_active);
CREATE INDEX IF NOT EXISTS idx_miqc_meas_user_date ON microbiology_qc_measurements(user_id, data_medicao DESC);
CREATE INDEX IF NOT EXISTS idx_miqc_meas_user_analito ON microbiology_qc_measurements(user_id, analito, data_medicao DESC);

-- Trigger updated_at
DROP TRIGGER IF EXISTS set_updated_at ON microbiology_qc_parameters;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON microbiology_qc_parameters
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();

-- RPC
CREATE OR REPLACE FUNCTION microbiology_register_qc_measurement(
    p_data_medicao DATE, p_analito TEXT, p_valor_medido NUMERIC,
    p_equipamento TEXT DEFAULT NULL, p_lote_controle TEXT DEFAULT NULL,
    p_nivel_controle TEXT DEFAULT NULL, p_observacao TEXT DEFAULT NULL
)
RETURNS JSON LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE
    v_param RECORD; v_min NUMERIC; v_max NUMERIC;
    v_status hematology_qc_status; v_meas_id UUID;
BEGIN
    SELECT * INTO v_param FROM microbiology_qc_parameters
    WHERE analito = p_analito AND is_active = true
    ORDER BY (
        CASE WHEN equipamento IS NOT NULL AND equipamento = p_equipamento THEN 1 ELSE 0 END +
        CASE WHEN lote_controle IS NOT NULL AND lote_controle = p_lote_controle THEN 1 ELSE 0 END +
        CASE WHEN nivel_controle IS NOT NULL AND nivel_controle = p_nivel_controle THEN 1 ELSE 0 END
    ) DESC, created_at DESC LIMIT 1;

    IF v_param IS NULL THEN
        RAISE EXCEPTION 'Nenhum parâmetro ativo para o analito "%". Cadastre um parâmetro primeiro.', p_analito;
    END IF;

    IF v_param.modo = 'INTERVALO' THEN
        v_min := v_param.min_valor; v_max := v_param.max_valor;
    ELSE
        v_min := v_param.alvo_valor * (1 - v_param.tolerancia_percentual / 100.0);
        v_max := v_param.alvo_valor * (1 + v_param.tolerancia_percentual / 100.0);
    END IF;

    v_status := CASE WHEN p_valor_medido >= v_min AND p_valor_medido <= v_max
                THEN 'APROVADO'::hematology_qc_status
                ELSE 'REPROVADO'::hematology_qc_status END;

    INSERT INTO microbiology_qc_measurements (
        data_medicao, analito, valor_medido, parameter_id, modo_usado,
        min_aplicado, max_aplicado, status, observacao, user_id
    ) VALUES (
        p_data_medicao, p_analito, p_valor_medido, v_param.id, v_param.modo,
        v_min, v_max, v_status, p_observacao, auth.uid()
    ) RETURNING id INTO v_meas_id;

    RETURN json_build_object(
        'measurement_id', v_meas_id, 'status', v_status::TEXT,
        'min_aplicado', v_min, 'max_aplicado', v_max, 'parametro_id', v_param.id
    );
END; $$;

-- RLS
ALTER TABLE microbiology_qc_parameters ENABLE ROW LEVEL SECURITY;
ALTER TABLE microbiology_qc_measurements ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Authenticated full access miqc_parameters" ON microbiology_qc_parameters;
CREATE POLICY "Authenticated full access miqc_parameters" ON microbiology_qc_parameters
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Authenticated full access miqc_measurements" ON microbiology_qc_measurements;
CREATE POLICY "Authenticated full access miqc_measurements" ON microbiology_qc_measurements
    FOR ALL TO authenticated USING (true) WITH CHECK (true);


-- =====================================================
-- 4. UROANÁLISE
-- =====================================================

-- Tabela de Parâmetros
CREATE TABLE IF NOT EXISTS urine_qc_parameters (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    analito         TEXT NOT NULL,
    equipamento     TEXT,
    lote_controle   TEXT,
    nivel_controle  TEXT,

    modo            hematology_qc_mode NOT NULL,
    alvo_valor      NUMERIC NOT NULL CHECK (alvo_valor > 0),

    min_valor       NUMERIC,
    max_valor       NUMERIC,
    tolerancia_percentual NUMERIC,

    is_active       BOOLEAN NOT NULL DEFAULT true,
    user_id         UUID REFERENCES auth.users(id),

    CONSTRAINT chk_urine_intervalo CHECK (
        modo <> 'INTERVALO' OR (
            min_valor IS NOT NULL AND max_valor IS NOT NULL
            AND min_valor <= max_valor AND tolerancia_percentual IS NULL
        )
    ),
    CONSTRAINT chk_urine_percentual CHECK (
        modo <> 'PERCENTUAL' OR (
            tolerancia_percentual IS NOT NULL AND tolerancia_percentual > 0
            AND tolerancia_percentual <= 100 AND min_valor IS NULL AND max_valor IS NULL
        )
    )
);

-- Tabela de Medições
CREATE TABLE IF NOT EXISTS urine_qc_measurements (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    data_medicao    DATE NOT NULL,
    analito         TEXT NOT NULL,
    valor_medido    NUMERIC NOT NULL,

    parameter_id    UUID NOT NULL REFERENCES urine_qc_parameters(id),
    modo_usado      hematology_qc_mode NOT NULL,
    min_aplicado    NUMERIC NOT NULL,
    max_aplicado    NUMERIC NOT NULL,
    status          hematology_qc_status NOT NULL,

    observacao      TEXT,
    user_id         UUID REFERENCES auth.users(id)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_urqc_params_user_analito ON urine_qc_parameters(user_id, analito, is_active);
CREATE INDEX IF NOT EXISTS idx_urqc_meas_user_date ON urine_qc_measurements(user_id, data_medicao DESC);
CREATE INDEX IF NOT EXISTS idx_urqc_meas_user_analito ON urine_qc_measurements(user_id, analito, data_medicao DESC);

-- Trigger updated_at
DROP TRIGGER IF EXISTS set_updated_at ON urine_qc_parameters;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON urine_qc_parameters
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();

-- RPC
CREATE OR REPLACE FUNCTION urine_register_qc_measurement(
    p_data_medicao DATE, p_analito TEXT, p_valor_medido NUMERIC,
    p_equipamento TEXT DEFAULT NULL, p_lote_controle TEXT DEFAULT NULL,
    p_nivel_controle TEXT DEFAULT NULL, p_observacao TEXT DEFAULT NULL
)
RETURNS JSON LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE
    v_param RECORD; v_min NUMERIC; v_max NUMERIC;
    v_status hematology_qc_status; v_meas_id UUID;
BEGIN
    SELECT * INTO v_param FROM urine_qc_parameters
    WHERE analito = p_analito AND is_active = true
    ORDER BY (
        CASE WHEN equipamento IS NOT NULL AND equipamento = p_equipamento THEN 1 ELSE 0 END +
        CASE WHEN lote_controle IS NOT NULL AND lote_controle = p_lote_controle THEN 1 ELSE 0 END +
        CASE WHEN nivel_controle IS NOT NULL AND nivel_controle = p_nivel_controle THEN 1 ELSE 0 END
    ) DESC, created_at DESC LIMIT 1;

    IF v_param IS NULL THEN
        RAISE EXCEPTION 'Nenhum parâmetro ativo para o analito "%". Cadastre um parâmetro primeiro.', p_analito;
    END IF;

    IF v_param.modo = 'INTERVALO' THEN
        v_min := v_param.min_valor; v_max := v_param.max_valor;
    ELSE
        v_min := v_param.alvo_valor * (1 - v_param.tolerancia_percentual / 100.0);
        v_max := v_param.alvo_valor * (1 + v_param.tolerancia_percentual / 100.0);
    END IF;

    v_status := CASE WHEN p_valor_medido >= v_min AND p_valor_medido <= v_max
                THEN 'APROVADO'::hematology_qc_status
                ELSE 'REPROVADO'::hematology_qc_status END;

    INSERT INTO urine_qc_measurements (
        data_medicao, analito, valor_medido, parameter_id, modo_usado,
        min_aplicado, max_aplicado, status, observacao, user_id
    ) VALUES (
        p_data_medicao, p_analito, p_valor_medido, v_param.id, v_param.modo,
        v_min, v_max, v_status, p_observacao, auth.uid()
    ) RETURNING id INTO v_meas_id;

    RETURN json_build_object(
        'measurement_id', v_meas_id, 'status', v_status::TEXT,
        'min_aplicado', v_min, 'max_aplicado', v_max, 'parametro_id', v_param.id
    );
END; $$;

-- RLS
ALTER TABLE urine_qc_parameters ENABLE ROW LEVEL SECURITY;
ALTER TABLE urine_qc_measurements ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Authenticated full access urqc_parameters" ON urine_qc_parameters;
CREATE POLICY "Authenticated full access urqc_parameters" ON urine_qc_parameters
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Authenticated full access urqc_measurements" ON urine_qc_measurements;
CREATE POLICY "Authenticated full access urqc_measurements" ON urine_qc_measurements
    FOR ALL TO authenticated USING (true) WITH CHECK (true);


-- =====================================================
-- VERIFICAÇÃO FINAL
-- =====================================================

-- Rodar esta query para verificar se todas as tabelas foram criadas:
/*
SELECT tablename FROM pg_tables
WHERE schemaname = 'public'
AND (
    tablename LIKE 'immunology%'
    OR tablename LIKE 'parasitology%'
    OR tablename LIKE 'microbiology%'
    OR tablename LIKE 'urine%'
)
ORDER BY tablename;
*/
