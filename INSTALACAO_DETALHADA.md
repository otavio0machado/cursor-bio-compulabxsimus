# 📋 Guia Detalhado de Instalação e Uso

## ⚠️ Problema Comum: "streamlit não é reconhecido"

Se você recebeu a mensagem de erro `streamlit : O termo 'streamlit' não é reconhecido`, siga estes passos:

---

## 🔧 PASSO 1: Verificar Python

1. Abra o **PowerShell** ou **Prompt de Comando**
2. Digite:
```bash
py --version
```
ou
```bash
python --version
```

**Se aparecer a versão** (ex: Python 3.11.x): ✅ Python está instalado  
**Se aparecer erro**: Você precisa instalar o Python primeiro

---

## 📦 PASSO 2: Instalar Dependências

### Opção A: Usando o arquivo batch (mais fácil)

1. **Clique duas vezes** no arquivo `run_app.bat`
2. O script instalará automaticamente tudo que precisa

### Opção B: Instalação manual

1. Abra o **PowerShell** ou **Prompt de Comando**
2. Navegue até a pasta do projeto:
```bash
cd "C:\Users\otavio\Desktop\cursor bio compulabxsimus"
```

3. Instale as dependências usando um destes comandos:

**Opção 1 (recomendada):**
```bash
py -m pip install -r requirements.txt
```

**Opção 2:**
```bash
python -m pip install -r requirements.txt
```

**Opção 3 (se as anteriores não funcionarem):**
```bash
python3 -m pip install -r requirements.txt
```

4. Aguarde a instalação terminar (pode levar alguns minutos)

---

## 🚀 PASSO 3: Iniciar o Aplicativo

### Método 1: Usando o arquivo batch (mais fácil)

1. **Clique duas vezes** no arquivo `run_app.bat`
2. Aguarde alguns segundos
3. O navegador abrirá automaticamente

### Método 2: Via linha de comando

1. Abra o **PowerShell** ou **Prompt de Comando**
2. Navegue até a pasta:
```bash
cd "C:\Users\otavio\Desktop\cursor bio compulabxsimus"
```

3. Execute um destes comandos:

**Opção 1 (recomendada):**
```bash
py -m streamlit run app.py
```

**Opção 2:**
```bash
python -m streamlit run app.py
```

**Opção 3:**
```bash
python3 -m streamlit run app.py
```

4. Você verá uma mensagem como:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
```

5. O navegador abrirá automaticamente. Se não abrir, copie o link `http://localhost:8501` e cole no navegador.

---

## 🎯 PASSO 4: Usar o Aplicativo

1. **No navegador**, você verá a interface do aplicativo
2. Na **barra lateral esquerda**:
   - Clique em **"Browse files"** no campo **COMPULAB.pdf**
   - Selecione o arquivo PDF do COMPULAB
   - Clique em **"Browse files"** no campo **SIMUS.pdf**
   - Selecione o arquivo PDF do SIMUS
   - Clique no botão **"🔍 Analisar"** (botão azul)

3. Aguarde alguns segundos enquanto processa

4. Os resultados aparecerão automaticamente!

---

## ❓ Solução de Problemas

### Problema: "py não é reconhecido"

**Solução:**
- Tente usar `python` ao invés de `py`
- Ou instale o Python Launcher para Windows

### Problema: "pip não é reconhecido"

**Solução:**
- Use `py -m pip` ao invés de apenas `pip`
- Ou `python -m pip`

### Problema: Erro ao instalar dependências

**Solução:**
1. Atualize o pip primeiro:
```bash
py -m pip install --upgrade pip
```

2. Depois instale as dependências:
```bash
py -m pip install -r requirements.txt
```

### Problema: O navegador não abre automaticamente

**Solução:**
1. Veja a URL no terminal (geralmente `http://localhost:8501`)
2. Copie e cole no navegador manualmente

### Problema: Erro ao processar PDFs

**Solução:**
- Verifique se os PDFs são do COMPULAB e SIMUS
- Certifique-se de que os arquivos não estão corrompidos
- Tente com outros PDFs para testar

### Problema: Porta 8501 já está em uso

**Solução:**
1. Feche outras instâncias do Streamlit
2. Ou use uma porta diferente:
```bash
py -m streamlit run app.py --server.port 8502
```

---

## 📝 Comandos Rápidos de Referência

```bash
# Verificar Python
py --version

# Instalar dependências
py -m pip install -r requirements.txt

# Iniciar aplicativo
py -m streamlit run app.py

# Parar aplicativo
# Pressione Ctrl+C no terminal
```

---

## ✅ Checklist de Verificação

Antes de começar, verifique:

- [ ] Python está instalado (`py --version` funciona)
- [ ] Você está na pasta correta do projeto
- [ ] As dependências foram instaladas (`py -m pip list` mostra streamlit)
- [ ] Os PDFs estão disponíveis para upload
- [ ] Nenhum firewall está bloqueando a porta 8501

---

## 🆘 Ainda com Problemas?

Se nada funcionar, tente:

1. **Reinstalar tudo:**
```bash
py -m pip uninstall streamlit pandas plotly pdfplumber -y
py -m pip install -r requirements.txt
```

2. **Usar ambiente virtual (opcional, mais avançado):**
```bash
py -m venv venv
venv\Scripts\activate
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

3. **Verificar se o arquivo app.py existe:**
```bash
dir app.py
```

---

**Boa sorte! Se ainda tiver problemas, me avise! 🚀**

