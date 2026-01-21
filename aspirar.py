import os
import re

def check_files():
    # Caminhos relativos ao diretório do app
    base_dir = "biodiagnostico_app/biodiagnostico_app"
    files_to_check = [
        "styles.py",
        "state.py",
        "pages/analise.py",
        "pages/proin.py",
        "components/ui.py"
    ]
    
    print("=== ASPIRADOR: RELATÓRIO DE PROGRESSO ===")
    
    for rel_path in files_to_check:
        full_path = os.path.join(base_dir, rel_path)
        if not os.path.exists(full_path):
            print(f"[ERROR] Arquivo não encontrado: {rel_path}")
            continue
            
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Detectar hexadecimais (exceto em styles.py onde são tokens)
        hex_matches = re.findall(r'#[0-9a-fA-F]{6}', content)
        if rel_path == "styles.py":
            # Em styles.py permitimos hexadecimais, mas contamos quantos
            print(f"[OK] {rel_path}: {len(hex_matches)} tokens de cor definidos.")
        else:
            if hex_matches:
                print(f"[AVISO] {rel_path}: Detectados {len(hex_matches)} hexadecimais manuais.")
            else:
                print(f"[PURIFICADO] {rel_path}: Sem hexadecimais manuais.")
        
        # Detectar class_name (Tailwind)
        tailwind_matches = re.findall(r'class_name=["\']', content)
        if tailwind_matches:
            print(f"[DÍVIDA] {rel_path}: Detectados {len(tailwind_matches)} usos de class_name (Tailwind).")
        else:
            print(f"[PURIFICADO] {rel_path}: Sem Tailwind (Design System nativo).")
        
        # Detectar tamanho
        lines = content.count('\n') + 1
        if lines > 1500:
            print(f"[ALERTA] {rel_path}: Arquivo gigante ({lines} linhas). Sugere-se modularizar.")
        else:
            print(f"[OK] {rel_path}: Tamanho aceitável ({lines} linhas).")
        print("-" * 40)

if __name__ == "__main__":
    check_files()
