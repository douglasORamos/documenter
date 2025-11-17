# 🚀 COMO USAR - Guia Definitivo

## ⚡ USO ULTRA-SIMPLES (2 Passos)

### 1️⃣ Coloque seu arquivo na pasta `input/`

Arraste ou copie sua documentação para a pasta `input/`:

```bash
# No terminal:
cp minha-documentacao.pdf input/

# Ou simplesmente arraste o arquivo para a pasta input/
```

### 2️⃣ Execute

```bash
python main.py
```

**PRONTO! É SÓ ISSO! 🎉**

---

## 📖 O Que Acontece

Quando você executa `python main.py`, o programa:

1. ✅ Detecta automaticamente seu arquivo em `input/`
2. ✅ Pergunta se você quer testar a API (opcional)
3. ✅ Analisa com Inteligência Artificial (OpenAI GPT-4)
4. ✅ Mostra o progresso em tempo real
5. ✅ Gera 2 arquivos em `output/`:
   - `.postman_collection.json` → Para importar no Postman
   - `_RESUMO.txt` → Para ler e entender a API

---

## 📦 Formatos Aceitos

O sistema aceita estes formatos de documentação:

- ✅ **PDF** - Documentos PDF
- ✅ **JSON** - Arquivos JSON genéricos
- ✅ **Postman Collection** - Collections do Postman (.json)
- ✅ **OpenAPI/Swagger** - Specs OpenAPI (.json ou .yaml)
- ✅ **TXT** - Arquivos de texto simples
- ✅ **Markdown** - Arquivos .md

---

## 🎯 Exemplo Prático

```bash
# 1. Coloque seu arquivo
cp "API Documentation.pdf" input/

# 2. Execute
python main.py

# Saída visual:
# ╭─────────────────────────────────────────╮
# │ 🚀 AI Documentation Enricher            │
# │                                         │
# │ Analisador de Documentação de API      │
# ╰─────────────────────────────────────────╯
#
# Como usar:
# 1. ✅ Coloque seu arquivo na pasta input/
# 2. ✅ Execute este programa
# 3. ✅ Pegue os resultados em output/
#
# ► Procurando arquivo em input/...
# ✓ Arquivo encontrado: API Documentation.pdf
# ✓ Saída: API Documentation.postman_collection.json
#
# Opções:
# Deseja testar a API real? [y/N]: n
#
# ══════════════════════════════════════════
# Iniciando Análise...
# ══════════════════════════════════════════
#
# 1/6 📄 Lendo documentação...
#       ✓ Encontrados 5 endpoints
#
# 2/6 🤖 Analisando com IA...
#       (Isso pode levar alguns minutos)
#       ✓ Análise de IA completa
#
# 3/6 ⊘ Testes de API pulados
# 4/6 ⊘ Detecção de padrões pulada
#
# 5/6 📦 Gerando Postman Collection...
#       ✓ Collection salva
#
# 6/6 📄 Gerando resumo...
#       ✓ Resumo salvo
#
# ══════════════════════════════════════════
# ╭─────────────────────────────────────────╮
# │ ✅ Análise Concluída com Sucesso!       │
# │                                         │
# │ Arquivos gerados em output/:            │
# │                                         │
# │ 📦 API Documentation.postman_collection.json
# │    → Postman Collection completa        │
# │                                         │
# │ 📄 API Documentation_RESUMO.txt         │
# │    → Resumo em linguagem simples        │
# │                                         │
# │ Total de endpoints: 5                   │
# ╰─────────────────────────────────────────╯
```

---

## 📂 Estrutura de Pastas

```
documenter/
├── input/              ← Coloque documentos aqui
│   ├── README.md       (instruções)
│   └── seu-arquivo.*   ← Seu arquivo
│
├── output/             ← Resultados aparecem aqui
│   ├── README.md       (instruções)
│   ├── *.postman_collection.json  ← Para Postman
│   └── *_RESUMO.txt    ← Para ler
│
└── main.py            ← Execute este arquivo
```

---

## 🎓 Opções Avançadas

### Testar API Real

Se você quiser que o sistema teste a API real:

```bash
python main.py

# Quando perguntar:
# Deseja testar a API real? [y/N]: y
# URL base da API: https://api.example.com
# Token de autenticação (opcional): seu-token-aqui
```

O sistema fará requisições reais para descobrir padrões!

### Modo CLI (Avançado)

Se preferir especificar tudo manualmente:

```bash
# Com auto-detecção
python cli.py analyze

# Especificando tudo
python cli.py analyze \
  --input arquivo.pdf \
  --output resultado.json \
  --test-api \
  --base-url https://api.com \
  --auth-token "token"
```

---

## 📄 Arquivos Gerados

### 1. Postman Collection (`.postman_collection.json`)

**Para**: Desenvolvedores  
**Uso**: Importar no Postman

**Contém**:
- Todos os endpoints documentados
- Exemplos de requisições
- Múltiplos exemplos de resposta
- Testes automatizados
- Validações e regras
- Tipos de dados validados

**Como usar**:
1. Abra o Postman
2. Clique em "Import"
3. Selecione o arquivo `.json`
4. Pronto! Teste os endpoints

### 2. Resumo em Texto (`_RESUMO.txt`)

**Para**: Todos (gerentes, QA, novos devs, etc.)  
**Uso**: Ler para entender a API

**Contém**:
- Visão geral das operações
- Fluxos de uso passo a passo
- Regras de negócio em linguagem simples
- Estrutura de dados explicada
- Guia de tratamento de erros
- Dicas práticas

**Como usar**:
1. Abra com qualquer editor de texto
2. Leia para entender a API
3. Compartilhe com a equipe

---

## ❓ Perguntas Frequentes

### P: Preciso ter internet?

**R:** Sim, o sistema usa a API da OpenAI que requer internet.

### P: Quanto custa?

**R:** Você precisa de uma conta OpenAI com créditos. Geralmente custa centavos por análise.

### P: E se houver múltiplos arquivos em input/?

**R:** O sistema processa o primeiro arquivo encontrado. Coloque apenas um por vez.

### P: Posso processar vários arquivos em sequência?

**R:** Sim! Processe um, mova para outra pasta, coloque o próximo e execute novamente.

### P: Preciso apagar o arquivo de input/ depois?

**R:** Não é necessário, mas recomendamos mover para organizar.

### P: O que fazer com os arquivos gerados?

**R:**
- **Collection JSON**: Importe no Postman
- **Resumo TXT**: Leia, compartilhe, use como base para docs

### P: Como faço o setup inicial?

**R:** Veja o guia completo: `SETUP.md`

Resumo:
```bash
pip install -r requirements.txt
cp .env.example .env
# Edite .env com sua chave OpenAI
```

### P: E se der erro?

**R:** O programa mostra mensagens claras explicando:
- O que deu errado
- Como resolver
- Próximos passos

---

## 🆘 Resolução de Problemas

### Erro: "Nenhum arquivo encontrado"

**Solução**:
1. Verifique se o arquivo está em `input/`
2. Verifique se não é o `README.md`
3. Verifique se tem uma extensão válida

### Erro: "OPENAI_API_KEY not found"

**Solução**:
1. Copie `.env.example` para `.env`
2. Abra `.env` e adicione sua chave:
   ```
   OPENAI_API_KEY=sua_chave_aqui
   ```
3. Salve e execute novamente

### Erro durante análise

**Solução**:
- Verifique se tem internet
- Verifique se o arquivo não está corrompido
- Tente outro formato (ex: PDF → TXT)

---

## 💡 Dicas

### 1. Teste com exemplo primeiro

```bash
cp examples/sample_openapi.yaml input/
python main.py
```

### 2. Leia o resumo primeiro

O arquivo `_RESUMO.txt` é mais fácil de entender. Comece por ele!

### 3. Organize seus arquivos

```
meu-projeto/
├── documentacoes/
│   ├── originais/
│   ├── processados/
│   └── para-processar/  ← Copie daqui para input/
└── resultados/          ← Copie de output/ para aqui
```

### 4. Use em batch

```bash
for doc in documentacoes/*.pdf; do
  cp "$doc" input/
  python main.py
  mv output/* resultados/
done
```

---

## 🎯 Comandos Rápidos

```bash
# Usar (modo simples)
python main.py

# Ver ajuda
python main.py --help
python cli.py --help

# Ver info de arquivo
python cli.py info input/seu-arquivo.pdf

# Modo CLI com auto-detecção
python cli.py analyze

# Modo CLI completo
python cli.py analyze -i file.pdf -o out.json
```

---

## 📚 Mais Documentação

- **`MODO_SIMPLES.md`** - Guia detalhado para não-técnicos
- **`README.md`** - Documentação completa
- **`QUICKSTART.md`** - Início rápido
- **`UPDATES.md`** - Novidades e melhorias
- **`input/README.md`** - Como usar pasta input
- **`output/README.md`** - Como usar arquivos gerados

---

## ✨ Resumo

**Para usar é MUITO simples:**

```
1. Coloque arquivo em input/
2. Execute: python main.py
3. Pegue resultados em output/
```

**SÓ ISSO! 🎉**

---

**Precisa de ajuda? Consulte a documentação ou abra uma issue no GitHub!**

