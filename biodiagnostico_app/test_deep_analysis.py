"""
Testes Unitários para Análise Profunda (Deep Analysis)

Testa as funções:
- analyze_patient_count_difference
- detect_repeated_exams
- calculate_difference_breakdown
- generate_executive_summary
"""
import unittest
import pandas as pd
from decimal import Decimal
from biodiagnostico_app.utils.analysis_module import (
    analyze_patient_count_difference,
    detect_repeated_exams,
    calculate_difference_breakdown,
    generate_executive_summary,
    run_deep_analysis,
)


class TestPatientCountDifference(unittest.TestCase):
    """Testes para análise de diferença de quantidade de pacientes"""
    
    def test_extra_patients_in_compulab(self):
        """Testa detecção de pacientes extras no COMPULAB"""
        # Dados de teste
        compulab_data = pd.DataFrame({
            'Paciente': ['PACIENTE A', 'PACIENTE B', 'PACIENTE C', 'PACIENTE D', 'PACIENTE E'],
            'Nome_Exame': ['HEMOGRAMA', 'HEMOGRAMA', 'GLICOSE', 'CREATININA', 'COLESTEROL'],
            'Codigo_Exame': ['1234', '1234', '5678', '9012', '3456'],
            'Valor': [50.00, 50.00, 30.00, 40.00, 60.00]
        })
        
        simus_data = pd.DataFrame({
            'Paciente': ['PACIENTE A'],
            'Nome_Exame': ['HEMOGRAMA'],
            'Codigo_Exame': ['1234'],
            'Valor': [50.00]
        })
        
        result = analyze_patient_count_difference(compulab_data, simus_data)
        
        # Verificações
        self.assertEqual(result['compulab_count'], 5)
        self.assertEqual(result['simus_count'], 1)
        self.assertEqual(result['difference'], 4)
        self.assertEqual(result['extra_patients_count'], 4)
        self.assertEqual(result['extra_patients_value'], 180.00)  # 50+30+40+60
        self.assertTrue(result['has_extra_in_compulab'])
        self.assertFalse(result['has_extra_in_simus'])
        
    def test_extra_patients_in_simus(self):
        """Testa detecção de pacientes extras no SIMUS"""
        compulab_data = pd.DataFrame({
            'Paciente': ['PACIENTE A'],
            'Nome_Exame': ['HEMOGRAMA'],
            'Codigo_Exame': ['1234'],
            'Valor': [50.00]
        })
        
        simus_data = pd.DataFrame({
            'Paciente': ['PACIENTE A', 'PACIENTE B', 'PACIENTE C'],
            'Nome_Exame': ['HEMOGRAMA', 'GLICOSE', 'CREATININA'],
            'Codigo_Exame': ['1234', '5678', '9012'],
            'Valor': [50.00, 30.00, 40.00]
        })
        
        result = analyze_patient_count_difference(compulab_data, simus_data)
        
        self.assertEqual(result['compulab_count'], 1)
        self.assertEqual(result['simus_count'], 3)
        self.assertEqual(result['difference'], -2)
        self.assertEqual(len(result['extra_patients_simus']), 2)
        
    def test_equal_patients(self):
        """Testa quando ambos têm os mesmos pacientes"""
        compulab_data = pd.DataFrame({
            'Paciente': ['PACIENTE A', 'PACIENTE B'],
            'Nome_Exame': ['HEMOGRAMA', 'GLICOSE'],
            'Codigo_Exame': ['1234', '5678'],
            'Valor': [50.00, 30.00]
        })
        
        simus_data = pd.DataFrame({
            'Paciente': ['PACIENTE A', 'PACIENTE B'],
            'Nome_Exame': ['HEMOGRAMA', 'GLICOSE'],
            'Codigo_Exame': ['1234', '5678'],
            'Valor': [50.00, 30.00]
        })
        
        result = analyze_patient_count_difference(compulab_data, simus_data)
        
        self.assertEqual(result['difference'], 0)
        self.assertEqual(result['extra_patients_count'], 0)
        self.assertEqual(result['extra_patients_value'], 0.0)


class TestRepeatedExamsDetection(unittest.TestCase):
    """Testes para detecção de exames repetidos"""
    
    def test_repeated_exams_in_compulab(self):
        """Testa detecção de exames repetidos no COMPULAB"""
        compulab_data = pd.DataFrame({
            'Paciente': ['PACIENTE A', 'PACIENTE A', 'PACIENTE A', 'PACIENTE B'],
            'Nome_Exame': ['HEMOGRAMA', 'HEMOGRAMA', 'GLICOSE', 'CREATININA'],
            'Codigo_Exame': ['1234', '1234', '5678', '9012'],
            'Valor': [50.00, 50.00, 30.00, 40.00]
        })
        
        simus_data = pd.DataFrame({
            'Paciente': ['PACIENTE A', 'PACIENTE B'],
            'Nome_Exame': ['HEMOGRAMA', 'CREATININA'],
            'Codigo_Exame': ['1234', '9012'],
            'Valor': [50.00, 40.00]
        })
        
        result = detect_repeated_exams(compulab_data, simus_data)
        
        self.assertTrue(result['has_repeated'])
        self.assertEqual(result['total_types'], 1)  # HEMOGRAMA repetido
        self.assertEqual(result['total_repeated_count'], 1)  # 1 ocorrência extra
        self.assertEqual(result['total_repeated_value'], 50.00)
        
    def test_repeated_exams_in_both_systems(self):
        """Testa detecção de exames repetidos em ambos os sistemas"""
        compulab_data = pd.DataFrame({
            'Paciente': ['PACIENTE A', 'PACIENTE A'],
            'Nome_Exame': ['HEMOGRAMA', 'HEMOGRAMA'],
            'Codigo_Exame': ['1234', '1234'],
            'Valor': [50.00, 50.00]
        })
        
        simus_data = pd.DataFrame({
            'Paciente': ['PACIENTE B', 'PACIENTE B'],
            'Nome_Exame': ['GLICOSE', 'GLICOSE'],
            'Codigo_Exame': ['5678', '5678'],
            'Valor': [30.00, 30.00]
        })
        
        result = detect_repeated_exams(compulab_data, simus_data)
        
        self.assertTrue(result['has_repeated'])
        self.assertEqual(result['total_types'], 2)  # HEMOGRAMA + GLICOSE
        self.assertEqual(result['total_repeated_count'], 2)
        self.assertEqual(result['total_repeated_value'], 80.00)  # 50 + 30
        
    def test_no_repeated_exams(self):
        """Testa quando não há exames repetidos"""
        compulab_data = pd.DataFrame({
            'Paciente': ['PACIENTE A', 'PACIENTE B'],
            'Nome_Exame': ['HEMOGRAMA', 'GLICOSE'],
            'Codigo_Exame': ['1234', '5678'],
            'Valor': [50.00, 30.00]
        })
        
        simus_data = pd.DataFrame({
            'Paciente': ['PACIENTE A', 'PACIENTE B'],
            'Nome_Exame': ['HEMOGRAMA', 'GLICOSE'],
            'Codigo_Exame': ['1234', '5678'],
            'Valor': [50.00, 30.00]
        })
        
        result = detect_repeated_exams(compulab_data, simus_data)
        
        self.assertFalse(result['has_repeated'])
        self.assertEqual(result['total_types'], 0)
        self.assertEqual(result['total_repeated_value'], 0.0)


class TestDifferenceBreakdown(unittest.TestCase):
    """Testes para cálculo da explicação da diferença"""
    
    def test_fully_explained_difference(self):
        """Testa quando a diferença é totalmente explicada"""
        compulab_total = 1000.00
        simus_total = 800.00
        
        analysis_results = {
            "summary": {
                "missing_in_simus_total": 200.00,
                "missing_in_compulab_total": 0.0,
                "divergences_total": 0.0
            }
        }
        
        patient_analysis = {
            "extra_patients_value": 200.00
        }
        
        repeated_analysis = {
            "total_repeated_value": 0.0
        }
        
        result = calculate_difference_breakdown(
            compulab_total,
            simus_total,
            analysis_results,
            repeated_analysis,
            patient_analysis
        )
        
        self.assertEqual(result['gross_difference'], 200.00)
        self.assertEqual(result['total_explained'], 200.00)
        self.assertAlmostEqual(result['residual'], 0.0, places=2)
        self.assertTrue(result['is_fully_explained'])
        self.assertEqual(result['percent_explained'], 100.0)
        
    def test_partially_explained_difference(self):
        """Testa quando a diferença é parcialmente explicada"""
        compulab_total = 1000.00
        simus_total = 700.00
        
        analysis_results = {
            "summary": {
                "missing_in_simus_total": 150.00,
                "missing_in_compulab_total": 0.0,
                "divergences_total": 50.00
            }
        }
        
        patient_analysis = {
            "extra_patients_value": 150.00
        }
        
        repeated_analysis = {
            "total_repeated_value": 0.0
        }
        
        result = calculate_difference_breakdown(
            compulab_total,
            simus_total,
            analysis_results,
            repeated_analysis,
            patient_analysis
        )
        
        self.assertEqual(result['gross_difference'], 300.00)
        self.assertEqual(result['total_explained'], 200.00)  # 150 pacientes + 50 divergências
        self.assertEqual(result['residual'], 100.00)
        self.assertFalse(result['is_fully_explained'])
        self.assertAlmostEqual(result['percent_explained'], 66.67, places=1)
        
    def test_with_repeated_exams(self):
        """Testa quando há exames repetidos"""
        compulab_total = 1000.00
        simus_total = 750.00
        
        analysis_results = {
            "summary": {
                "missing_in_simus_total": 200.00,
                "missing_in_compulab_total": 0.0,
                "divergences_total": 0.0
            }
        }
        
        patient_analysis = {
            "extra_patients_value": 200.00
        }
        
        repeated_analysis = {
            "total_repeated_value": 50.00
        }
        
        result = calculate_difference_breakdown(
            compulab_total,
            simus_total,
            analysis_results,
            repeated_analysis,
            patient_analysis
        )
        
        self.assertEqual(result['gross_difference'], 250.00)
        self.assertEqual(result['explained_components']['repeated_exams']['value'], 50.00)
        
    def test_formula_steps(self):
        """Testa se os passos da fórmula são gerados corretamente"""
        compulab_total = 1000.00
        simus_total = 700.00
        
        analysis_results = {
            "summary": {
                "missing_in_simus_total": 200.00,
                "missing_in_compulab_total": 50.00,
                "divergences_total": 50.00
            }
        }
        
        patient_analysis = {
            "extra_patients_value": 200.00
        }
        
        repeated_analysis = {
            "total_repeated_value": 0.0
        }
        
        result = calculate_difference_breakdown(
            compulab_total,
            simus_total,
            analysis_results,
            repeated_analysis,
            patient_analysis
        )
        
        steps = result['formula_steps']
        self.assertTrue(len(steps) >= 5)
        self.assertIn("Diferença Bruta", steps[0])
        self.assertIn("Pacientes apenas COMPULAB", steps[1])
        

class TestExecutiveSummary(unittest.TestCase):
    """Testes para geração do resumo executivo"""
    
    def test_critical_status(self):
        """Testa geração de resumo com status crítico"""
        compulab_total = 10000.00
        simus_total = 7000.00
        
        patient_analysis = {
            "extra_patients_count": 10,
            "extra_patients_value": 2000.00
        }
        
        repeated_analysis = {
            "total_repeated_count": 5,
            "total_repeated_value": 500.00
        }
        
        difference_breakdown = {
            "residual": 500.00,
            "percent_explained": 75.0,
            "is_fully_explained": False
        }
        
        result = generate_executive_summary(
            compulab_total,
            simus_total,
            patient_analysis,
            repeated_analysis,
            difference_breakdown
        )
        
        self.assertEqual(result['status'], 'critical')
        self.assertIn('key_metrics', result)
        self.assertIn('critical_findings', result)
        self.assertIn('recommendations', result)
        self.assertTrue(len(result['critical_findings']) > 0)
        
    def test_ok_status(self):
        """Testa geração de resumo com status ok"""
        compulab_total = 10000.00
        simus_total = 9950.00
        
        patient_analysis = {
            "extra_patients_count": 0,
            "extra_patients_value": 0.0
        }
        
        repeated_analysis = {
            "total_repeated_count": 0,
            "total_repeated_value": 0.0
        }
        
        difference_breakdown = {
            "residual": 0.50,
            "percent_explained": 99.0,
            "is_fully_explained": True
        }
        
        result = generate_executive_summary(
            compulab_total,
            simus_total,
            patient_analysis,
            repeated_analysis,
            difference_breakdown
        )
        
        self.assertEqual(result['status'], 'ok')
        
    def test_key_metrics(self):
        """Testa se as métricas principais são calculadas corretamente"""
        compulab_total = 10000.00
        simus_total = 8000.00
        
        patient_analysis = {
            "extra_patients_count": 0,
            "extra_patients_value": 0.0
        }
        
        repeated_analysis = {
            "total_repeated_count": 0,
            "total_repeated_value": 0.0
        }
        
        difference_breakdown = {
            "residual": 0.0,
            "percent_explained": 100.0,
            "is_fully_explained": True
        }
        
        result = generate_executive_summary(
            compulab_total,
            simus_total,
            patient_analysis,
            repeated_analysis,
            difference_breakdown
        )
        
        metrics = result['key_metrics']
        self.assertEqual(metrics['faturamento_compulab'], 10000.00)
        self.assertEqual(metrics['faturamento_simus'], 8000.00)
        self.assertEqual(metrics['diferenca_liquida'], 2000.00)
        self.assertEqual(metrics['diferenca_percentual'], 25.0)
        
    def test_action_items(self):
        """Testa se os itens de ação são gerados corretamente"""
        compulab_total = 10000.00
        simus_total = 7000.00
        
        patient_analysis = {
            "extra_patients_count": 5,
            "extra_patients_value": 1500.00
        }
        
        repeated_analysis = {
            "total_repeated_count": 3,
            "total_repeated_value": 300.00
        }
        
        difference_breakdown = {
            "residual": 200.00,
            "percent_explained": 90.0,
            "is_fully_explained": False
        }
        
        result = generate_executive_summary(
            compulab_total,
            simus_total,
            patient_analysis,
            repeated_analysis,
            difference_breakdown
        )
        
        action_items = result.get('action_items', [])
        self.assertTrue(len(action_items) >= 2)
        
        # Verifica se há item para pacientes extras
        has_patient_action = any('paciente' in item['action'].lower() for item in action_items)
        self.assertTrue(has_patient_action)


class TestIntegration(unittest.TestCase):
    """Testes de integração do fluxo completo"""
    
    def test_run_deep_analysis_integration(self):
        """Testa a função integrada run_deep_analysis"""
        # Dados de teste representando o cenário do usuário:
        # - COMPULAB com 4 pacientes extras = R$ 520
        # - Exames repetidos = R$ 600+
        
        compulab_data = pd.DataFrame({
            'Paciente': [
                'PACIENTE COMUM',
                'PACIENTE EXTRA 1', 
                'PACIENTE EXTRA 2',
                'PACIENTE EXTRA 3',
                'PACIENTE EXTRA 4',
                'PACIENTE COM REPETICAO', 'PACIENTE COM REPETICAO', 'PACIENTE COM REPETICAO'  # Exame repetido 3x
            ],
            'Nome_Exame': [
                'HEMOGRAMA',
                'GLICOSE',              # Extra 1
                'COLESTEROL',           # Extra 2
                'TSH',                  # Extra 3
                'T4',                   # Extra 4
                'CREATININA', 'CREATININA', 'CREATININA'  # Repetido
            ],
            'Codigo_Exame': ['1234', '5678', '9012', '1111', '2222', '3333', '3333', '3333'],
            'Valor': [100.0, 130.0, 130.0, 130.0, 130.0, 300.0, 300.0, 300.0]
        })
        
        # PACIENTE COMUM e PACIENTE COM REPETICAO também existem no SIMUS
        simus_data = pd.DataFrame({
            'Paciente': ['PACIENTE COMUM', 'PACIENTE COM REPETICAO'],
            'Nome_Exame': ['HEMOGRAMA', 'CREATININA'],
            'Codigo_Exame': ['1234', '3333'],
            'Valor': [100.0, 300.0]
        })
        
        compulab_total = 1420.00  # Soma dos valores do COMPULAB
        simus_total = 400.00
        
        analysis_results = {
            "summary": {
                "missing_in_simus_total": 0.0,
                "missing_in_compulab_total": 0.0,
                "divergences_total": 0.0
            }
        }
        
        result = run_deep_analysis(
            compulab_data,
            simus_data,
            compulab_total,
            simus_total,
            analysis_results
        )
        
        # Verifica análise de pacientes (4 extras: EXTRA 1, 2, 3, 4)
        self.assertEqual(result['patient_analysis']['extra_patients_count'], 4)
        # Valor dos 4 pacientes extras = 520
        self.assertEqual(result['patient_analysis']['extra_patients_value'], 520.00)
        
        # Verifica exames repetidos (2 repetições do CREATININA = 600)
        self.assertTrue(result['repeated_exams']['total_repeated_count'] >= 2)
        self.assertTrue(result['repeated_exams']['total_repeated_value'] >= 600.00)
        
        # Verifica resumo executivo
        self.assertIn('executive_summary', result['executive_summary'])
        self.assertIn('key_metrics', result['executive_summary'])


def run_tests():
    """Executa todos os testes"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adicionar todas as classes de teste
    suite.addTests(loader.loadTestsFromTestCase(TestPatientCountDifference))
    suite.addTests(loader.loadTestsFromTestCase(TestRepeatedExamsDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestDifferenceBreakdown))
    suite.addTests(loader.loadTestsFromTestCase(TestExecutiveSummary))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
