# Quick Start Guide

Guia rápido para começar a usar o AI Documentation Enricher.

## Instalação Rápida

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar OpenAI
cp .env.example .env
# Edite .env e adicione: OPENAI_API_KEY=sua_chave_aqui

# 3. Pronto para usar!
```

📖 **Setup completo**: Veja [`SETUP.md`](SETUP.md) para guia detalhado

## 🚀 Primeiro Uso (MODO ULTRA-SIMPLES)

### ⚡ 2 Passos Apenas:

#### 1️⃣ Coloque seu arquivo na pasta `input/`

```bash
# Copie sua documentação para a pasta input
cp sua-documentacao.pdf input/
```

#### 2️⃣ Execute

```bash
python main.py
```

**PRONTO! É só isso! 🎉**

O programa vai:
- ✅ Detectar automaticamente seu arquivo
- ✅ Analisar com IA
- ✅ Gerar os resultados em `output/`
- ✅ Mostrar o que foi feito

---

### 🔧 Modo Alternativo (com CLI)

Se preferir usar a linha de comando tradicional:

```bash
python cli.py analyze
```

---

## 🔧 Modo Avançado (Opcional)

Se você preferir especificar os caminhos manualmente:

### 1. Analisar um arquivo de exemplo

```bash
python cli.py analyze \
  --input examples/sample_openapi.yaml \
  --output my-first-collection.json
```

### 2. Ver informações sobre um arquivo

```bash
python cli.py info examples/sample_openapi.yaml
```

### 3. Analisar sua própria documentação

```bash
python cli.py analyze \
  --input /caminho/para/sua/documentacao.pdf \
  --output resultado.postman_collection.json \
  --collection-name "Minha API"
```

## Testando com API Real

### Modo Simples (com auto-detecção)

```bash
# 1. Coloque o arquivo em input/
cp sua-doc.pdf input/

# 2. Execute com testes de API
python cli.py analyze \
  --test-api \
  --base-url https://api.sua-empresa.com \
  --auth-token "seu-token-aqui"

# 3. Resultados em output/
```

### Modo Avançado (especificando tudo)

```bash
python cli.py analyze \
  --input sua-doc.pdf \
  --output enriched.json \
  --test-api \
  --base-url https://api.sua-empresa.com \
  --auth-token "seu-token-aqui"
```

## Importando no Postman

1. Abra o Postman
2. Click em "Import"
3. Selecione o arquivo `.postman_collection.json` gerado
4. Explore a collection enriquecida!

## O Que Você Verá

O sistema gera **DOIS ARQUIVOS** na pasta `output/`:

### 📦 Postman Collection (`.postman_collection.json`)
Para desenvolvedores - arquivo técnico com:
- ✅ Todos os endpoints documentados
- ✅ Tipos de dados validados
- ✅ Campos obrigatórios identificados
- ✅ Exemplos de requisições
- ✅ Múltiplos exemplos de resposta
- ✅ Regras de negócio descobertas
- ✅ Validações e constraints
- ✅ Testes automatizados
- ✅ Comentários detalhados

### 📄 Resumo em Texto (`_RESUMO.txt`)
Para todos - explicação simples com:
- ✅ Visão geral da API
- ✅ Operações em linguagem clara
- ✅ Fluxos de uso passo a passo
- ✅ Regras de negócio simplificadas
- ✅ Estrutura de dados explicada
- ✅ Guia de tratamento de erros

## Próximos Passos

- Leia o [README.md](README.md) completo
- Experimente diferentes tipos de documentação
- Ajuste os prompts em `analyzer.py` para seu caso de uso
- Explore as opções do CLI com `python cli.py --help`

## Troubleshooting

### Erro de API Key

```
Configuration Error: OPENAI_API_KEY not found
```

**Solução**: Crie arquivo `.env` com `OPENAI_API_KEY=sua_chave`

### Erro ao parsear PDF

```
Error parsing PDF
```

**Solução**: Verifique se o PDF não está protegido ou use outro formato

### Quer ajuda?

- Consulte o README.md
- Verifique os exemplos em `examples/`
- Abra uma issue no GitHub

---

**Pronto para começar! 🚀**

