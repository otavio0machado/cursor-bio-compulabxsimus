
import os
import sys

# Ensure we can import the app modules
sys.path.append(os.getcwd())

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

try:
    from biodiagnostico_app.biodiagnostico_app.utils.ai_analysis import generate_ai_analysis
    from biodiagnostico_app.biodiagnostico_app.config import Config
except ImportError:
    # Try alternative path if running from root
    try:
        sys.path.append(os.path.join(os.getcwd(), 'biodiagnostico_app'))
        from biodiagnostico_app.utils.ai_analysis import generate_ai_analysis
        from biodiagnostico_app.config import Config
    except ImportError as e:
        print(f"Error importing modules: {e}")
        sys.exit(1)

api_key = Config.GEMINI_API_KEY
print(f"Testing with API Key from Config: {api_key[:4]}..." if api_key else "Testing with NO API Key")

# Dummy data
compulab_total = 1000.0
simus_total = 900.0
compulab_count = 10
simus_count = 9
comparison_results = {
    'missing_patients': [{'id': '1'}],
    'missing_exams': [{'patient': 'Test Patient', 'exam_name': 'GLICOSE', 'value': 100.0}],
    'value_divergences': []
}
breakdown = {
    'missing_patients_total': 100.0,
    'missing_exams_total': 100.0,
    'divergences_total': 0.0,
    'explained_total': 100.0,
    'residual': 0.0
}

print("\n--- Starting AI Analysis Test ---")
result, error = generate_ai_analysis(
    compulab_total,
    simus_total,
    compulab_count,
    simus_count,
    comparison_results,
    breakdown,
    api_key
)

if error:
    print(f"\n[ERROR] Error occurred: {error}")
else:
    print("\n[SUCCESS] AI Analysis Success!")
    print("Response preview:")
    print("-" * 40)
    print(result[:200] + "...")
    print("-" * 40)
