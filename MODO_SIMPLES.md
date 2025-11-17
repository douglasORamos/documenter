# 🚀 MODO SIMPLES - Para Não-Técnicos

Guia super simplificado para usar o AI Documentation Enricher.

---

## ⚡ USO EM 2 PASSOS

### 1️⃣ Coloque seu arquivo na pasta `input/`

Copie ou mova seu arquivo de documentação para dentro da pasta `input/`:

```bash
# No Windows (File Explorer):
# Arraste e solte seu arquivo na pasta "input"

# No Mac/Linux (Terminal):
cp seu-arquivo.pdf input/
```

**Formatos aceitos:**
- PDF
- JSON
- Postman Collection
- OpenAPI/Swagger
- Texto (.txt)
- Markdown (.md)

---

### 2️⃣ Execute

Abra o terminal e digite:

```bash
python main.py
```

**PRONTO! SÓ ISSO!** 🎉

O programa vai:
- ✅ Detectar automaticamente seu arquivo
- ✅ Perguntar se quer testar a API (opcional)
- ✅ Analisar com Inteligência Artificial
- ✅ Mostrar o progresso em tempo real
- ✅ Gerar os documentos enriquecidos
- ✅ Informar onde estão os resultados

Os resultados estarão na pasta `output/`:
- `seu-arquivo.postman_collection.json` ← Para o Postman
- `seu-arquivo_RESUMO.txt` ← Para ler e entender

Abra a pasta `output/` e você encontrará:

**📦 Arquivo Postman Collection** (`.postman_collection.json`)
- Para importar no Postman
- Contém todos os endpoints
- Com exemplos e testes

**📄 Arquivo Resumo** (`_RESUMO.txt`)
- Para ler e entender a API
- Em linguagem simples
- Sem termos técnicos complexos

---

## 📋 PASSO A PASSO COMPLETO

### Passo 1: Preparar o Ambiente (uma vez só)

```bash
# 1. Instalar Python (se não tiver)
# Baixe em: https://www.python.org/downloads/

# 2. Abrir terminal na pasta do projeto

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar OpenAI
# Copie o arquivo .env.example para .env
# Edite .env e adicione sua chave da OpenAI
```

### Passo 2: Usar (sempre que quiser analisar)

```bash
# 1. Coloque arquivo em input/
cp meu-documento.pdf input/

# 2. Execute
python main.py

# É só isso! Os resultados estarão em output/
```

---

## 🎯 EXEMPLO COMPLETO

Vamos analisar uma documentação de API em PDF:

```bash
# 1. Coloque o PDF na pasta input
cp "Documentação API Clientes.pdf" input/

# 2. Execute
python main.py

# Você verá algo como:
# 🚀 AI Documentation Enricher
# ✓ Arquivo encontrado: Documentação API Clientes.pdf
# ✓ Saída: Documentação API Clientes.postman_collection.json
# 
# Deseja testar a API real? [y/N]: n
#
# 1/6 📄 Lendo documentação... ✓
# 2/6 🤖 Analisando com IA... ✓
# 3/6 ⊘ Testes pulados
# 4/6 ⊘ Padrões pulados
# 5/6 📦 Gerando Collection... ✓
# 6/6 📄 Gerando resumo... ✓
#
# ✅ Análise Concluída!

# Os arquivos estão em output/
```

Na pasta `output/` você terá:
- `Documentação API Clientes.postman_collection.json`
- `Documentação API Clientes_RESUMO.txt`

---

## 📖 LENDO OS RESULTADOS

### Resumo em Texto (`.txt`)

Abra com qualquer editor de texto (Notepad, TextEdit, etc.)

Você verá seções como:

```
VISÃO GERAL
Esta API permite trabalhar com os seguintes recursos:
• CLIENTES: criar, consultar, atualizar, remover

OPERAÇÕES DISPONÍVEIS
1. Criar novo cliente
   Dados necessários: nome, email, telefone
   Retorna: id, nome, email, data_cadastro
...
```

**Para que serve?**
- Entender rapidamente o que a API faz
- Compartilhar com a equipe
- Base para documentação

### Postman Collection (`.json`)

**Para importar no Postman:**

1. Abra o Postman
2. Clique em "Import" (botão no canto superior esquerdo)
3. Clique em "Upload Files"
4. Selecione o arquivo `.postman_collection.json`
5. Clique em "Import"

**Pronto!** Agora você pode testar a API diretamente no Postman.

---

## ❓ PERGUNTAS FREQUENTES

### P: Posso colocar múltiplos arquivos em input/?

**R:** Coloque apenas um arquivo por vez. O sistema processa o primeiro arquivo encontrado.

### P: Preciso apagar o arquivo de input/ depois?

**R:** Não é necessário, mas recomendamos mover para outra pasta para organizar.

### P: E se eu quiser especificar o nome do arquivo de saída?

**R:** Use o modo avançado:
```bash
python cli.py analyze --input meu-arquivo.pdf --output meu-nome-personalizado.json
```

### P: Preciso ter internet?

**R:** Sim, o sistema usa a API da OpenAI que requer internet.

### P: Quanto custa?

**R:** Você precisa de uma conta OpenAI com créditos. O custo varia mas é geralmente baixo (centavos por análise).

### P: Funciona em qualquer idioma?

**R:** Sim! A documentação pode estar em qualquer idioma.

### P: E se der erro?

**R:** Verifique:
1. Se o arquivo está realmente na pasta `input/`
2. Se o arquivo não está corrompido
3. Se a chave da OpenAI está configurada no arquivo `.env`
4. Se tem internet

---

## 🎓 DICAS

### ✅ Organize seus arquivos

```
meu-projeto/
├── input/           ← Coloque aqui para processar
├── output/          ← Resultados aparecem aqui
└── arquivo/         ← Depois mova para organizar
    ├── processados/
    └── resultados/
```

### ✅ Teste com o exemplo primeiro

Antes de processar seus arquivos, teste com o exemplo:

```bash
cp examples/sample_openapi.yaml input/
python cli.py analyze
```

### ✅ Leia o resumo primeiro

O arquivo `_RESUMO.txt` é mais fácil de entender. Comece por ele!

### ✅ Compartilhe o resumo

O arquivo de resumo é perfeito para enviar para:
- Gerentes
- Clientes
- Equipe não-técnica
- Documentação inicial

---

## 🆘 PRECISA DE AJUDA?

### Comandos úteis:

```bash
# Ver ajuda
python cli.py --help
python cli.py analyze --help

# Ver informações sobre um arquivo (sem processar)
python cli.py info input/seu-arquivo.pdf

# Processar sem usar IA (mais rápido, menos detalhado)
python cli.py analyze --no-ai
```

### Veja mais documentação:

- `README.md` - Documentação completa
- `QUICKSTART.md` - Guia rápido
- `TEST_COMMANDS.md` - Comandos avançados

---

## ✨ RESUMO

**Para usar é MUITO simples:**

```bash
# 1. Coloque arquivo em input/
# 2. Execute: python main.py
```

**SÓ ISSO! 🎉**

Os resultados aparecem automaticamente em `output/`

---

**Dúvidas? Problemas? Sugestões?**

Abra uma issue no GitHub ou consulte a documentação completa.

---

*Última atualização: 2024*

