-- Script de Configuração do Banco de Dados (Supabase)
-- Execute este script no SQL Editor do seu projeto Supabase para criar as tabelas necessárias.

-- 1. Habilitar extensão UUID (geralmente já vem habilitada)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Tabela de Resumos de Auditoria (audit_summaries)
CREATE TABLE IF NOT EXISTS public.audit_summaries (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    compulab_total double precision,
    simus_total double precision,
    missing_exams_count integer,
    divergences_count integer,
    missing_patients_count integer,
    ai_summary text
);

-- Políticas de Segurança (RLS) para audit_summaries
ALTER TABLE public.audit_summaries ENABLE ROW LEVEL SECURITY;

-- Remover política existente se houver para evitar erro de duplicação ao rodar novamente
DROP POLICY IF EXISTS "Permitir acesso público audit_summaries" ON public.audit_summaries;
CREATE POLICY "Permitir acesso público audit_summaries" ON public.audit_summaries FOR ALL USING (true);


-- 3. Tabela de Histórico de Pacientes / Resoluções (patient_history)
CREATE TABLE IF NOT EXISTS public.patient_history (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    patient_name text NOT NULL,
    exam_name text NOT NULL,
    status text,
    last_value double precision,
    notes text,
    CONSTRAINT unique_patient_exam UNIQUE(patient_name, exam_name)
);

-- Políticas de Segurança (RLS) para patient_history
ALTER TABLE public.patient_history ENABLE ROW LEVEL SECURITY;

-- Remover política existente se houver
DROP POLICY IF EXISTS "Permitir acesso público patient_history" ON public.patient_history;
CREATE POLICY "Permitir acesso público patient_history" ON public.patient_history FOR ALL USING (true);

-- 4. Tabela de Lotes de Reagentes (Caso não exista - baseado no hint do erro)
-- CREATE TABLE IF NOT EXISTS public.reagent_lots ( ... ); 
-- (Não incluído pois o erro era sobre patient_history, mas o hint mencionou reagent_lots, implicando que ela provavalmente existe)

