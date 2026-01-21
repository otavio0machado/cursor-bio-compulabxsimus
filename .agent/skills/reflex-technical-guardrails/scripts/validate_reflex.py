import os
import re
import sys

def check_reflex_errors(directory):
    errors_found = False
    
    # Regex para capturar spacing="...rem" ou spacing=Spacing.
    spacing_pattern = re.compile(r'spacing=["\']\d+(rem|px)["\']|spacing=Spacing\.')
    
    # Regex para capturar columns=["..."]
    grid_list_pattern = re.compile(r'columns=\[.*\]')
    
    # Regex para componentes inexistentes comuns
    deprecated_comps = re.compile(r'rx\.(circle|square|spacer_circle)')

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "styles.py":
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    if spacing_pattern.search(content):
                        print(f"[ERRO] {path}: Uso ilegal de unidades CSS em 'spacing'. Use style={{'gap': ...}}")
                        errors_found = True
                        
                    if grid_list_pattern.search(content):
                        print(f"[ERRO] {path}: Uso de lista em 'columns'. Use dicionário de breakpoints.")
                        errors_found = True
                        
                    if deprecated_comps.search(content):
                        print(f"[ERRO] {path}: Uso de componente depreciado (rx.circle/square).")
                        errors_found = True

                    if "import reflex as rx" not in content:
                        print(f"[ERRO] {path}: Falta o 'import reflex as rx'.")
                        errors_found = True

    if not errors_found:
        print("[OK] Nenhum erro técnico de Reflex detectado.")
    return errors_found

if __name__ == "__main__":
    check_reflex_errors("biodiagnostico_app/biodiagnostico_app")
