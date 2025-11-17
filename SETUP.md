# ⚙️ Setup - Configuração Inicial

Guia rápido para configurar o AI Documentation Enricher.

---

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Conta OpenAI com créditos

---

## 🚀 Setup em 3 Passos

### 1️⃣ Instalar Dependências

```bash
cd documenter
pip install -r requirements.txt
```

**O que será instalado:**
- openai (API OpenAI)
- requests (requisições HTTP)
- click (CLI)
- pdfplumber (leitura de PDF)
- python-dotenv (variáveis de ambiente)
- rich (interface colorida)
- jsonschema (validação)
- pyyaml (YAML)

### 2️⃣ Configurar OpenAI

```bash
# Copiar arquivo de exemplo
cp .env.example .env
```

**Editar o arquivo `.env`:**

Abra o arquivo `.env` com qualquer editor de texto e modifique:

```
OPENAI_API_KEY=your_openai_api_key_here  ← Substitua pela sua chave
OPENAI_MODEL=gpt-4                        ← Mantenha assim
```

**Como obter sua chave OpenAI:**

1. Acesse: https://platform.openai.com/api-keys
2. Faça login na sua conta OpenAI
3. Clique em "Create new secret key"
4. Copie a chave gerada
5. Cole no arquivo `.env`

**Exemplo:**
```
OPENAI_API_KEY=sk-proj-abc123def456...
OPENAI_MODEL=gpt-4
```

### 3️⃣ Testar Instalação

```bash
# Teste com arquivo de exemplo
cp examples/sample_openapi.yaml input/
python main.py
```

Se tudo estiver correto, você verá:
```
🚀 AI Documentation Enricher
✓ Arquivo encontrado: sample_openapi.yaml
✓ Saída: sample_openapi.postman_collection.json
...
```

---

## ✅ Verificação

### Verificar se Python está instalado:

```bash
python --version
# ou
python3 --version
```

Deve mostrar Python 3.8 ou superior.

### Verificar se pip está instalado:

```bash
pip --version
# ou
pip3 --version
```

### Verificar dependências instaladas:

```bash
pip list | grep -E "openai|requests|click|pdfplumber|rich"
```

Deve mostrar as bibliotecas instaladas.

### Verificar configuração:

```bash
# Arquivo .env existe?
ls -la .env

# Conteúdo está correto?
cat .env
```

---

## 🐛 Resolução de Problemas

### Problema: "pip: command not found"

**Solução:**
```bash
# No Ubuntu/Debian:
sudo apt install python3-pip

# No macOS:
brew install python3

# No Windows:
# Baixe Python em python.org e reinstale marcando "Add to PATH"
```

### Problema: "ModuleNotFoundError: No module named 'openai'"

**Solução:**
```bash
pip install -r requirements.txt
# ou
pip3 install -r requirements.txt
```

### Problema: "OPENAI_API_KEY not found"

**Solução:**
1. Verifique se o arquivo `.env` existe:
   ```bash
   ls .env
   ```
2. Se não existir, crie:
   ```bash
   cp .env.example .env
   ```
3. Edite `.env` e adicione sua chave OpenAI

### Problema: "Permission denied" ao executar

**Solução:**
```bash
chmod +x main.py
python main.py
```

### Problema: Erro ao ler PDF

**Solução:**
```bash
# Instalar dependências do sistema (Ubuntu/Debian):
sudo apt install libpoppler-cpp-dev

# No macOS:
brew install poppler
```

---

## 🔒 Segurança

### ⚠️ IMPORTANTE:

1. **NUNCA** commite o arquivo `.env` no Git
2. **NUNCA** compartilhe sua chave OpenAI
3. O `.env` já está no `.gitignore`
4. Use chaves com permissões limitadas

### Rotação de Chaves:

Se você acha que sua chave foi exposta:

1. Acesse https://platform.openai.com/api-keys
2. Revogue a chave antiga
3. Crie uma nova chave
4. Atualize o arquivo `.env`

---

## 🌐 Ambiente Virtual (Recomendado)

Para evitar conflitos com outras bibliotecas Python:

### Criar ambiente virtual:

```bash
# Linux/Mac:
python3 -m venv venv
source venv/bin/activate

# Windows:
python -m venv venv
venv\Scripts\activate
```

### Instalar dependências no ambiente virtual:

```bash
pip install -r requirements.txt
```

### Desativar ambiente virtual:

```bash
deactivate
```

---

## 📦 Estrutura Após Setup

```
documenter/
├── .env              ← Suas configurações (não commitar!)
├── .env.example      ← Exemplo (commitar)
├── input/            ← Coloque arquivos aqui
├── output/           ← Resultados aparecem aqui
├── main.py           ← Execute este arquivo
├── requirements.txt  ← Dependências
└── venv/            ← Ambiente virtual (opcional)
```

---

## ✨ Pronto para Usar!

Após o setup, você pode usar assim:

```bash
# 1. Coloque arquivo
cp seu-arquivo.pdf input/

# 2. Execute
python main.py

# 3. Pegue resultados
ls output/
```

---

## 🎓 Próximos Passos

1. ✅ Setup completo
2. 📖 Leia: `COMO_USAR.md`
3. 🚀 Execute: `python main.py`
4. 🎉 Aproveite!

---

## 📞 Precisa de Ajuda?

- **Instalação Python**: https://www.python.org/downloads/
- **OpenAI API**: https://platform.openai.com/docs
- **Documentação**: Veja `README.md`
- **Guia Simples**: Veja `MODO_SIMPLES.md`

---

**Setup concluído? Execute: `python main.py` 🚀**

