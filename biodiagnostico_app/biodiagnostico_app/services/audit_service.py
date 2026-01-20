"""
Serviço de Histórico de Auditorias
Laboratório Biodiagnóstico
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from .supabase_client import supabase

class AuditService:
    """Operações de banco de dados para Resumos de Auditoria"""
    
    @staticmethod
    async def save_audit_summary(data: Dict[str, Any]) -> Dict[str, Any]:
        """Salva resumo de uma análise no banco de dados"""
        if not supabase:
            return {}
            
        try:
            # Tabela audit_summaries (deve ser criada no Supabase)
            # colunas: created_at, compulab_total, simus_total, missing_exams_count, 
            # divergences_count, missing_patients_count, ai_summary (text)
            
            db_data = {
                "compulab_total": data.get("compulab_total", 0.0),
                "simus_total": data.get("simus_total", 0.0),
                "missing_exams_count": data.get("missing_exams_count", 0),
                "divergences_count": data.get("divergences_count", 0),
                "missing_patients_count": data.get("missing_patients_count", 0),
                "ai_summary": data.get("ai_summary", "")[:500] # Limitar tamanho
            }
            
            response = supabase.table("audit_summaries").insert(db_data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            err_msg = str(e)
            if "PGRST205" in err_msg or "audit_summaries" in err_msg:
                print("--- AVISO: TABELA 'audit_summaries' NÃO ENCONTRADA NO SUPABASE ---")
                print("Para corrigir, execute este SQL no Painel do Supabase:")
                print("""
                CREATE TABLE public.audit_summaries (
                    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
                    created_at timestamptz DEFAULT now(),
                    compulab_total double precision,
                    simus_total double precision,
                    missing_exams_count integer,
                    divergences_count integer,
                    missing_patients_count integer,
                    ai_summary text
                );
                ALTER TABLE public.audit_summaries ENABLE ROW LEVEL SECURITY;
                CREATE POLICY \"Permitir acesso público\" ON public.audit_summaries FOR ALL USING (true);
                """)
            else:
                print(f"Erro ao salvar resumo de auditoria: {e}")
            return {}

    @staticmethod
    async def get_audit_history(limit: int = 12) -> List[Dict[str, Any]]:
        """Busca histórico de resumos de auditoria"""
        if not supabase:
            return []
        try:
            response = supabase.table("audit_summaries")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Erro ao buscar histórico de auditoria: {e}")
            return []

    @staticmethod
    async def get_latest_audit_summary() -> Optional[Dict[str, Any]]:
        """Busca o resumo da última análise realizada"""
        if not supabase:
            return None
            
        try:
            response = supabase.table("audit_summaries")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
                
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Erro ao buscar último resumo: {e}")
            return None

    @staticmethod
    async def get_patient_history(patient_name: str, exam_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Busca histórico de um paciente no Supabase"""
        if not supabase:
            return []
        try:
            query = supabase.table("patient_history").select("*").eq("patient_name", patient_name)
            if exam_name:
                query = query.eq("exam_name", exam_name)
            response = query.order("created_at", desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Erro ao buscar histórico do paciente {patient_name}: {e}")
            return []

    @staticmethod
    async def save_divergence_resolution(data: Dict[str, Any]) -> Dict[str, Any]:
        """Salva a resolução/decisão sobre uma divergência"""
        if not supabase:
            return {}
        try:
            # upsert baseado em patient_name e exam_name (necessário UNIQUE no banco)
            db_data = {
                "patient_name": data.get("patient_name"),
                "exam_name": data.get("exam_name"),
                "last_value": data.get("last_value"),
                "status": data.get("status", "resolvido"),
                "notes": data.get("notes", "")
            }
            response = supabase.table("patient_history").upsert(
                db_data, on_conflict="patient_name,exam_name"
            ).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            print(f"Erro ao salvar resolução: {e}")
            return {}

    @staticmethod
    async def get_resolutions() -> Dict[str, str]:
        """Busca todas as resoluções ativas para mapeamento no estado"""
        if not supabase:
            return {}
        try:
            response = supabase.table("patient_history").select("patient_name, exam_name, status").execute()
            # Retorna um dict {(paciente, exame): status}
            return { (r["patient_name"], r["exam_name"]): r["status"] for r in response.data }
        except Exception as e:
            err_msg = str(e)
            if "PGRST205" in err_msg or "patient_history" in err_msg:
                print("--- AVISO: TABELA 'patient_history' NÃO ENCONTRADA NO SUPABASE ---")
                print("Para corrigir, execute este SQL no Painel do Supabase:")
                print("""
                CREATE TABLE public.patient_history (
                    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
                    created_at timestamptz DEFAULT now(),
                    patient_name text NOT NULL,
                    exam_name text NOT NULL,
                    status text,
                    last_value double precision,
                    notes text,
                    UNIQUE(patient_name, exam_name)
                );
                ALTER TABLE public.patient_history ENABLE ROW LEVEL SECURITY;
                CREATE POLICY "Permitir acesso público" ON public.patient_history FOR ALL USING (true);
                """)
            else:
                print(f"Erro ao buscar resoluções: {e}")
            return {}
