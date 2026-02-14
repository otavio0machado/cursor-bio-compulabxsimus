# 🩺 Instruções: Finalizar Sistema de Hematologia

## 📋 PASSO 1: Executar SQL no Supabase Dashboard

### Como acessar:
1. Acesse [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Selecione seu projeto
3. No menu lateral esquerdo, clique em **SQL Editor**
4. Clique em **New Query**

### SQL a executar:

Copie e cole o código abaixo no SQL Editor e clique em **RUN**:

```sql
-- =====================================================
-- FIX: Corrigir RLS das tabelas de Hematologia
-- =====================================================

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
```

### Resultado esperado:
Você deve ver a mensagem: **"Success. No rows returned"**

---

## ✅ PASSO 2: Verificar se as tabelas existem

Ainda no SQL Editor, execute esta query para verificar:

```sql
SELECT
    tablename
FROM
    pg_tables
WHERE
    schemaname = 'public'
    AND tablename LIKE 'hematology%';
```

**Resultado esperado:** Deve listar 3 tabelas:
- `hematology_qc_parameters`
- `hematology_qc_measurements`
- `hematology_bio_records`

### ⚠️ Se as tabelas NÃO existirem:

Execute primeiro a migration completa do arquivo `supabase_migration_hematology_qc.sql` antes do fix acima.

---

## 📝 PASSO 3: Commits no Git

Os commits serão feitos automaticamente pelo assistente após você confirmar a execução do SQL.

---

## 🧪 PASSO 4: Testar no App

Após os commits:

1. Acesse o app: `http://localhost:3000`
2. Navegue para: **ProIn > Outros Registros > Hematologia**
3. Teste:
   - ✅ Cadastrar novo parâmetro (RBC, modo INTERVALO)
   - ✅ Registrar medição
   - ✅ Ver tabela de medições
   - ✅ Gerar PDF

---

## 📊 O que foi implementado:

### Funcionalidades:
- ✅ CQ por **Intervalo** (min/max fixo)
- ✅ CQ por **Percentual** (tolerância % do alvo)
- ✅ Analitos de hematologia: RBC, HGB, HCT, WBC, PLT, RDW, MPV
- ✅ Registro Bio x Controle Interno
- ✅ Tabelas interativas com filtros
- ✅ Geração de PDF com gráficos
- ✅ Validação automática (APROVADO/REPROVADO)

### Arquitetura:
- ✅ 3 tabelas no Supabase
- ✅ 1 função RPC (stored procedure)
- ✅ 1 VIEW resolvida (cálculos pré-computados)
- ✅ RLS permissivo (consistente com outras tabelas QC)
- ✅ Service layer (`hematology_qc_service.py`)
- ✅ State management (`qc_state.py`)
- ✅ UI components (`hemato_qc_tab.py`)

---

## 🎯 Próximos Passos (após finalizar):

1. **Outras áreas laboratoriais:**
   - Imunologia
   - Parasitologia
   - Microbiologia
   - Uroanálise

2. **Agentes IA (n8n):**
   - The Parser (normalização de arquivos)
   - The Matchmaker (conciliação semântica)
   - The Forensic Auditor (detecção de anomalias)

---

**Desenvolvido com ❤️ para Biodiagnóstico**
