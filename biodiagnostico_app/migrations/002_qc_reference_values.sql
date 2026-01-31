-- Migração: Criar tabela de Valores Referenciais do CQ
-- Data: 2026-01-30
-- Descrição: Permite cadastrar valores-alvo e tolerâncias de CV% por exame

-- Tabela de Valores Referenciais de CQ
CREATE TABLE IF NOT EXISTS public.qc_reference_values (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),

    -- Identificação
    name text NOT NULL,                          -- Nome dado pelo usuário (ex: "Kit ControlLab Jan/2026")
    exam_name text NOT NULL,                     -- Nome canônico do exame

    -- Validade
    valid_from date NOT NULL,                    -- Início da validade
    valid_until date,                            -- Fim da validade (NULL = sem prazo)

    -- Valores de Referência
    target_value double precision NOT NULL,      -- Valor-alvo (média)
    cv_max_threshold double precision DEFAULT 10.0,   -- CV% máximo aceito (acima = precisa calibrar)

    -- Informações do Material de Controle
    lot_number text,
    manufacturer text,
    level text DEFAULT 'Normal',
    notes text,

    -- Status
    is_active boolean DEFAULT true,

    -- Constraint para evitar duplicatas
    CONSTRAINT unique_ref_exam_level_date UNIQUE(exam_name, level, valid_from)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_qc_ref_exam ON public.qc_reference_values(exam_name);
CREATE INDEX IF NOT EXISTS idx_qc_ref_active ON public.qc_reference_values(is_active);
CREATE INDEX IF NOT EXISTS idx_qc_ref_valid_from ON public.qc_reference_values(valid_from DESC);

-- RLS (Row Level Security)
ALTER TABLE public.qc_reference_values ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir acesso publico qc_reference_values" ON public.qc_reference_values;
CREATE POLICY "Permitir acesso publico qc_reference_values" ON public.qc_reference_values FOR ALL USING (true);

-- Adicionar colunas na tabela qc_records existente para rastreabilidade
ALTER TABLE public.qc_records
ADD COLUMN IF NOT EXISTS reference_id uuid REFERENCES public.qc_reference_values(id),
ADD COLUMN IF NOT EXISTS needs_calibration boolean DEFAULT false;

-- Índice para rastreabilidade
CREATE INDEX IF NOT EXISTS idx_qc_records_reference ON public.qc_records(reference_id);

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_qc_reference_values_updated_at ON public.qc_reference_values;
CREATE TRIGGER update_qc_reference_values_updated_at
    BEFORE UPDATE ON public.qc_reference_values
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
