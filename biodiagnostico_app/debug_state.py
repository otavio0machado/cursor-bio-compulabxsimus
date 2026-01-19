import os
import sys

# Add the project directory to path
sys.path.append(os.path.join(os.getcwd(), 'biodiagnostico_app'))

try:
    from biodiagnostico_app.state import State
except ImportError:
    sys.path.append(os.getcwd())
    from biodiagnostico_app.state import State

print("Instantiating State...")
s = State()

print("Checking unique_exam_names...")
try:
    exams = s.unique_exam_names
    print(f"Type: {type(exams)}")
    print(f"Length: {len(exams)}")
    print(f"First 5 exams: {exams[:5]}")
    
    if len(exams) == 0:
        print("❌ ERROR: List is empty! This should be impossible.")
    else:
        print("✅ List has items.")

except Exception as e:
    print(f"❌ Exception accessing property: {e}")
