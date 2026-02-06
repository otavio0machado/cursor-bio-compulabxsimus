-- =====================================================
-- Migration: Criar tabelas de Reagentes, Manutenções e Pós-Calibração
-- Executar no SQL Editor do Supabase Dashboard
-- =====================================================

-- 1. Tabela de Lotes de Reagentes
CREATE TABLE IF NOT EXISTS reagent_lots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    lot_number TEXT NOT NULL,
    expiry_date TEXT,
    quantity TEXT,
    manufacturer TEXT,
    storage_temp TEXT,
    current_stock NUMERIC DEFAULT 0,
    estimated_consumption NUMERIC DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Tabela de Registros de Manutenção
CREATE TABLE IF NOT EXISTS maintenance_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipment TEXT NOT NULL,
    type TEXT NOT NULL,
    date TEXT NOT NULL,
    next_date TEXT,
    technician TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Tabela de Registros Pós-Calibração
CREATE TABLE IF NOT EXISTS post_calibration_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    qc_record_id UUID REFERENCES qc_records(id) ON DELETE CASCADE,
    date TEXT NOT NULL,
    exam_name TEXT NOT NULL,
    original_value NUMERIC DEFAULT 0,
    original_cv NUMERIC DEFAULT 0,
    post_calibration_value NUMERIC DEFAULT 0,
    post_calibration_cv NUMERIC DEFAULT 0,
    target_value NUMERIC DEFAULT 0,
    analyst TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_reagent_lots_name ON reagent_lots(name);
CREATE INDEX IF NOT EXISTS idx_reagent_lots_expiry ON reagent_lots(expiry_date);
CREATE INDEX IF NOT EXISTS idx_maintenance_records_equipment ON maintenance_records(equipment);
CREATE INDEX IF NOT EXISTS idx_maintenance_records_date ON maintenance_records(date);
CREATE INDEX IF NOT EXISTS idx_post_calibration_qc_record ON post_calibration_records(qc_record_id);

-- Habilitar RLS (Row Level Security) - ajuste conforme sua política
ALTER TABLE reagent_lots ENABLE ROW LEVEL SECURITY;
ALTER TABLE maintenance_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE post_calibration_records ENABLE ROW LEVEL SECURITY;

-- Política permissiva para usuários autenticados (ajuste conforme necessário)
CREATE POLICY "Authenticated users can manage reagent_lots"
    ON reagent_lots FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Authenticated users can manage maintenance_records"
    ON maintenance_records FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Authenticated users can manage post_calibration_records"
    ON post_calibration_records FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);
