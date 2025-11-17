# AI Documentation Enricher

Sistema CLI em Python que analisa documentações de API (PDF, JSON, Postman Collection, TXT, OpenAPI), valida campos usando OpenAI, testa endpoints reais para descobrir padrões, e gera uma Postman Collection enriquecida com exemplos, comentários e regras de negócio descobertas.

## 🚀 Funcionalidades

- **Múltiplos formatos suportados**: PDF, JSON, Postman Collection, OpenAPI/Swagger, TXT/Markdown
- **Análise com IA**: Usa OpenAI GPT-4 para validar campos, tipos e descobrir regras ocultas
- **Testes de API reais**: Faz requisições reais para descobrir comportamentos e validações
- **Detecção de padrões**: Identifica padrões entre inputs e outputs, regras de negócio implícitas
- **Saída enriquecida**: Gera duas saídas complementares:
  - **Postman Collection** completa com tipos, validações, exemplos e testes
  - **Resumo em texto simples** (arquivo `_RESUMO.txt`) explicando a API de forma acessível
    - Visão geral das operações
    - Fluxos principais de uso
    - Regras de negócio em linguagem clara
    - Estrutura de dados simplificada
    - Guia de tratamento de erros

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Chave de API da OpenAI
- (Opcional) Acesso à API que será documentada

## 🔧 Instalação

### Setup Rápido (3 passos):

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar OpenAI
cp .env.example .env
# Edite .env e adicione sua chave da OpenAI

# 3. Pronto!
python main.py
```

📖 **Guia completo de setup**: Veja [`SETUP.md`](SETUP.md)

### Conteúdo do `.env`:
```
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4
```

**Como obter chave OpenAI**: https://platform.openai.com/api-keys

## 📖 Uso

### 🚀 Modo Ultra-Simples (Recomendado)

**Apenas 2 passos:**

```bash
# 1. Coloque seu arquivo na pasta input/
cp sua-documentacao.pdf input/

# 2. Execute
python main.py
```

**PRONTO!** 🎉 O programa faz tudo automaticamente:
- ✅ Detecta o arquivo
- ✅ Analisa com IA
- ✅ Gera resultados em `output/`

Arquivos gerados:
- `output/sua-documentacao.postman_collection.json` ← Para Postman
- `output/sua-documentacao_RESUMO.txt` ← Para ler

📘 **Guia detalhado**: [MODO_SIMPLES.md](MODO_SIMPLES.md)

---

### 🎯 Modo CLI (Para quem prefere linha de comando)

```bash
# Com auto-detecção
python cli.py analyze

# Especificando arquivos
python cli.py analyze --input arquivo.pdf --output resultado.json
```

---

### 🔧 Modo Avançado (Para Usuários Experientes)

#### Comando Básico

```bash
python cli.py analyze --input <arquivo_entrada> --output <arquivo_saida>
```

#### Exemplos de Uso

#### 1. Analisar documentação PDF

```bash
python cli.py analyze \
  --input docs/api-documentation.pdf \
  --output enriched-api.postman_collection.json
```

#### 2. Analisar Postman Collection existente

```bash
python cli.py analyze \
  --input original.postman_collection.json \
  --output enriched.postman_collection.json
```

#### 3. Analisar com testes reais de API

```bash
python cli.py analyze \
  --input api-spec.json \
  --output result.postman_collection.json \
  --test-api \
  --base-url https://api.example.com
```

#### 4. Com autenticação

```bash
python cli.py analyze \
  --input docs.pdf \
  --output output.json \
  --test-api \
  --base-url https://api.example.com \
  --auth-token "Bearer seu-token-aqui"
```

#### 5. Analisar OpenAPI/Swagger

```bash
python cli.py analyze \
  --input openapi.yaml \
  --output enriched.postman_collection.json \
  --collection-name "My Enriched API"
```

#### 6. Apenas parsing (sem IA)

```bash
python cli.py analyze \
  --input collection.json \
  --output parsed.json \
  --no-ai
```

### Ver informações sobre um arquivo

```bash
python cli.py info docs/api-documentation.pdf
```

## 🎯 Opções do CLI

### Comando `analyze`

| Opção | Descrição |
|-------|-----------|
| `--input, -i` | **(Obrigatório)** Arquivo de entrada (PDF, JSON, etc.) |
| `--output, -o` | **(Obrigatório)** Caminho do arquivo Postman Collection de saída |
| `--test-api` | Flag para testar a API com requisições reais |
| `--base-url` | URL base da API (obrigatório se `--test-api` for usado) |
| `--auth-token` | Token de autenticação para requisições |
| `--collection-name` | Nome da Postman Collection gerada |
| `--no-ai` | Pular análise com IA (apenas parse) |

### Comando `info`

```bash
python cli.py info <arquivo>
```

Mostra informações sobre o arquivo de documentação sem fazer análise completa.

## 🏗️ Arquitetura

```
documenter/
├── cli.py                  # Interface de linha de comando
├── config.py              # Gerenciamento de configuração
├── models.py              # Modelos de dados
├── utils.py               # Funções utilitárias
├── analyzer.py            # Integração OpenAI
├── tester.py              # Testador de API
├── patterns.py            # Detector de padrões
├── generator.py           # Gerador Postman Collection
└── parsers/               # Parsers para diferentes formatos
    ├── __init__.py
    ├── base_parser.py
    ├── pdf_parser.py
    ├── json_parser.py
    ├── postman_parser.py
    ├── text_parser.py
    └── openapi_parser.py
```

## 🔄 Fluxo de Execução

1. **Parse**: Extrai informações do arquivo de entrada
2. **Análise IA**: OpenAI analisa e valida campos, tipos e regras
3. **Testes** (opcional): Faz requisições reais para descobrir comportamentos
4. **Detecção de Padrões**: Correlaciona dados e identifica regras ocultas
5. **Geração**: Cria Postman Collection enriquecida

## 📊 O Que a IA Descobre

### Validação de Campos
- Tipos de dados corretos (string, integer, boolean, etc.)
- Obrigatoriedade (required vs optional)
- Restrições (minLength, maxLength, pattern, etc.)
- Valores possíveis (enums)

### Regras de Negócio
- Dependências entre campos
- Validações condicionais
- Regras implícitas não documentadas
- Padrões de entrada/saída

### Comportamento da API
- Códigos de erro e suas causas
- Respostas para diferentes inputs
- Edge cases e validações
- Relacionamentos entre endpoints

## 🧪 Exemplos de Padrões Descobertos

### Padrão de Validação
```
Tipo: validation
Descrição: Campo 'email' deve ser um email válido
Condições:
  - Formato: email
  - Required: true
Confiança: 85%
```

### Padrão Input-Output
```
Tipo: input_output
Descrição: Se campo 'status' = 'active', resposta inclui campo 'active_since'
Condições:
  - status = 'active' → response.active_since presente
  - status = 'inactive' → response.active_since ausente
Confiança: 90%
```

### Padrão de Erro
```
Tipo: error
Descrição: HTTP 409 ocorre quando email já está cadastrado
Condições:
  - Duplicate email → 409 Conflict
Exemplos: [...]
Confiança: 95%
```

## 📄 Formatos de Saída

O sistema gera **dois arquivos complementares**:

### 1. Postman Collection (`.postman_collection.json`)

A Postman Collection técnica e completa inclui:

### Para cada endpoint:
- **Descrição enriquecida** com todas as informações descobertas
- **Request body** com exemplo válido
- **Documentação de campos**:
  - Nome, tipo, obrigatoriedade
  - Descrição detalhada
  - Restrições e validações
  - Valores possíveis
- **Múltiplos exemplos de resposta**:
  - Resposta de sucesso
  - Diferentes códigos de erro
  - Edge cases descobertos
- **Padrões e regras descobertas**
- **Testes automatizados** para Postman

### Variáveis de Collection
- `base_url`: URL base da API
- Outras variáveis conforme necessário

### 2. Resumo em Texto Simples (`_RESUMO.txt`)

Um documento legível e acessível que contém:

#### Visão Geral
- Lista de recursos disponíveis
- Operações principais (criar, consultar, atualizar, remover)
- Propósito geral da API

#### Operações Disponíveis
- Descrição simplificada de cada endpoint
- Dados necessários em linguagem clara
- O que cada operação retorna
- Agrupamento por recurso

#### Fluxos Principais
- Sequências típicas de operações
- Como usar a API passo a passo
- Exemplos de casos de uso comuns

#### Regras e Comportamentos
- Regras de negócio em linguagem simples
- Validações importantes
- Dependências entre operações

#### Estrutura dos Dados
- Campos principais utilizados
- Tipos de dados em linguagem clara
- Descrições não técnicas

#### Tratamento de Erros
- Situações de erro explicadas
- Como interpretar códigos de erro
- Dicas para resolver problemas comuns

**Exemplo de saída**:
```
======================================================================
RESUMO DA API: Minha API
======================================================================

Este documento apresenta um resumo simplificado do funcionamento da API,
facilitando o entendimento das principais operações disponíveis.

Total de operações: 5

VISÃO GERAL
----------------------------------------------------------------------

Esta API permite trabalhar com os seguintes recursos:

• USERS: criar, consultar, atualizar, remover

OPERAÇÕES DISPONÍVEIS
----------------------------------------------------------------------

📦 USERS

1. Criar novo users
   Cria um novo usuário no sistema
   Dados necessários: username, email, password
   Retorna: id, username, email, created_at

2. Consultar users
   Lista todos os usuários com paginação
   Retorna: users, pagination
   ...
```

## 🔒 Segurança

- Nunca commite sua chave da OpenAI
- Use `.env` para variáveis sensíveis
- O `.env` está no `.gitignore`
- Para APIs com autenticação, use tokens temporários

## ⚠️ Limitações

- A análise com IA consome créditos da OpenAI
- Testes de API podem acionar rate limits
- PDFs com formatação complexa podem ter problemas de parsing
- Alguns padrões complexos podem não ser detectados automaticamente

## 🛠️ Desenvolvimento

### Estrutura de Classes Principais

#### `DocumentationSource`
Representa a fonte de documentação parseada.

#### `EndpointInfo`
Informações sobre um endpoint (path, method, fields, etc.).

#### `FieldInfo`
Informações sobre um campo (type, required, constraints, etc.).

#### `TestResult`
Resultado de um teste de API.

#### `Pattern`
Padrão descoberto na análise.

### Adicionar Novo Parser

1. Crie um arquivo em `parsers/`
2. Herde de `BaseParser`
3. Implemente `parse()` e `extract_endpoints()`
4. Adicione ao `parsers/__init__.py`

## 📝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📜 Licença

Este projeto está sob a licença MIT.

## 🤝 Suporte

Para questões e suporte:
- Abra uma issue no GitHub
- Consulte a documentação da OpenAI
- Verifique os logs em caso de erros

## 🎯 Roadmap

- [ ] Suporte a mais formatos (RAML, API Blueprint)
- [ ] Cache de análises IA para reduzir custos
- [ ] Interface web para visualização
- [ ] Exportação para outros formatos (Insomnia, etc.)
- [ ] Análise de diferenças entre versões
- [ ] Geração de documentação HTML/Markdown

## 📚 Exemplos Adicionais

### Processar múltiplos arquivos (Modo Simples)

```bash
# Processe um por vez usando a pasta input/
for file in docs/*.pdf; do
  # Move para input
  cp "$file" input/
  
  # Processa
  python cli.py analyze
  
  # Move de volta
  rm "input/$(basename $file)"
done

# Todos os resultados estarão em output/
```

### Processar múltiplos arquivos (Modo Avançado)

```bash
for file in docs/*.pdf; do
  python cli.py analyze \
    --input "$file" \
    --output "output/$(basename ${file%.*}).postman_collection.json"
done
```

### Script de automação

```bash
#!/bin/bash
# analyze-api.sh

API_DOCS="api-docs.pdf"
OUTPUT="enriched-api.postman_collection.json"
API_URL="https://api.example.com"
TOKEN="your-api-token"

python cli.py analyze \
  --input "$API_DOCS" \
  --output "$OUTPUT" \
  --test-api \
  --base-url "$API_URL" \
  --auth-token "$TOKEN" \
  --collection-name "Production API - Enriched"

echo "✓ Analysis complete: $OUTPUT"
```

## 💡 Dicas de Uso

1. **Comece sem testes**: Primeiro analise apenas a documentação
2. **Use testes em staging**: Evite testar em produção
3. **Revise os resultados**: A IA pode cometer erros
4. **Customize prompts**: Modifique `analyzer.py` para seu caso de uso
5. **Cache quando possível**: Evite re-analisar o mesmo conteúdo

## 🔍 Troubleshooting

### Erro: "OPENAI_API_KEY not found"
Configure o arquivo `.env` com sua chave da OpenAI.

### Erro: "Failed to parse PDF"
Verifique se o PDF não está protegido ou corrompido.

### Testes falhando
- Verifique a URL base
- Confirme que a autenticação está correta
- Verifique rate limits da API

### Resultados ruins da IA
- Use GPT-4 em vez de modelos menores
- Forneça documentação mais clara
- Ajuste os prompts em `analyzer.py`

---

**Desenvolvido com ❤️ para melhorar documentações de API**

