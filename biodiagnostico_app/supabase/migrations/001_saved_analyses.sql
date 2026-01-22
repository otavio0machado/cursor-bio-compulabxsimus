-- migration_saved_analyses.sql
-- Tabela para salvar análises e arquivos convertidos por nome/data escolhido pelo usuário

-- 1. Tabela de Análises Salvas
CREATE TABLE IF NOT EXISTS public.saved_analyses (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    
    -- Identificação (escolhida pelo usuário)
    analysis_name text NOT NULL,               -- Nome dado pelo usuário ex: "Janeiro 2026"
    analysis_date date NOT NULL,               -- Data da análise escolhida
    description text,                           -- Descrição opcional
    
    -- Arquivos Originais (URLs do Cloudinary ou paths)
    compulab_file_url text,
    compulab_file_name text,
    simus_file_url text,
    simus_file_name text,
    
    -- Arquivos Convertidos (CSV/Excel gerados)
    converted_compulab_url text,               -- CSV do COMPULAB gerado
    converted_simus_url text,                  -- CSV do SIMUS gerado
    
    -- Relatório PDF
    analysis_report_url text,                  -- PDF da análise gerado
    
    -- Resumo da Análise
    compulab_total double precision DEFAULT 0,
    simus_total double precision DEFAULT 0,
    difference double precision DEFAULT 0,
    missing_patients_count integer DEFAULT 0,
    missing_patients_total double precision DEFAULT 0,
    missing_exams_count integer DEFAULT 0,
    missing_exams_total double precision DEFAULT 0,
    divergences_count integer DEFAULT 0,
    divergences_total double precision DEFAULT 0,
    extra_simus_count integer DEFAULT 0,
    
    -- Metadados
    ai_summary text,                            -- Resumo gerado por IA (se disponível)
    tags text[],                                -- Tags para busca rápida
    status text DEFAULT 'completed',            -- draft, completed, archived
    
    -- Constraint
    CONSTRAINT unique_analysis_name_date UNIQUE(analysis_name, analysis_date)
);

-- 2. Tabela de Detalhes da Análise (itens encontrados)
CREATE TABLE IF NOT EXISTS public.analysis_items (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id uuid NOT NULL REFERENCES public.saved_analyses(id) ON DELETE CASCADE,
    created_at timestamptz DEFAULT now(),
    
    -- Tipo de item
    item_type text NOT NULL, -- 'missing_patient', 'missing_exam', 'divergence', 'extra_simus'
    
    -- Dados do item
    patient_name text,
    exam_name text,
    compulab_value double precision,
    simus_value double precision,
    difference double precision,
    exams_count integer,                        -- Para missing_patient
    
    -- Status de resolução
    is_resolved boolean DEFAULT false,
    resolution_notes text
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_saved_analyses_date ON public.saved_analyses(analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_saved_analyses_name ON public.saved_analyses(analysis_name);
CREATE INDEX IF NOT EXISTS idx_analysis_items_analysis_id ON public.analysis_items(analysis_id);
CREATE INDEX IF NOT EXISTS idx_analysis_items_type ON public.analysis_items(item_type);

-- Habilitar RLS
ALTER TABLE public.saved_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_items ENABLE ROW LEVEL SECURITY;

-- Políticas de acesso público (ajuste conforme necessidade)
DROP POLICY IF EXISTS "Permitir acesso público saved_analyses" ON public.saved_analyses;
CREATE POLICY "Permitir acesso público saved_analyses" ON public.saved_analyses FOR ALL USING (true);

DROP POLICY IF EXISTS "Permitir acesso público analysis_items" ON public.analysis_items;
CREATE POLICY "Permitir acesso público analysis_items" ON public.analysis_items FOR ALL USING (true);

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_saved_analyses_updated_at ON public.saved_analyses;
CREATE TRIGGER update_saved_analyses_updated_at
    BEFORE UPDATE ON public.saved_analyses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
