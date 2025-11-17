# Test Commands - AI Documentation Enricher

Comandos prontos para testar o sistema.

## Pré-requisitos

```bash
# 1. Ativar ambiente virtual
source venv/bin/activate

# 2. Verificar instalação
python cli.py --version

# 3. Ver ajuda
python cli.py --help
python cli.py analyze --help
python cli.py info --help
```

## Testes com Arquivos de Exemplo

### 1. Teste com OpenAPI YAML

```bash
python cli.py analyze \
  --input examples/sample_openapi.yaml \
  --output test-openapi.postman_collection.json \
  --collection-name "Sample API - OpenAPI"
```

**Resultado esperado**: Collection com 4 endpoints (GET /users, POST /users, GET /users/{id})

### 2. Teste com Markdown

```bash
python cli.py analyze \
  --input examples/sample_api_doc.md \
  --output test-markdown.postman_collection.json \
  --collection-name "Sample API - Markdown"
```

**Resultado esperado**: Collection com 5 endpoints extraídos do Markdown

### 3. Ver Informações do Arquivo

```bash
python cli.py info examples/sample_openapi.yaml
python cli.py info examples/sample_api_doc.md
```

**Resultado esperado**: Sumário dos endpoints encontrados

## Testes Sem IA (Modo --no-ai)

Para testar sem consumir créditos da OpenAI:

```bash
python cli.py analyze \
  --input examples/sample_openapi.yaml \
  --output test-no-ai.json \
  --no-ai
```

**Resultado esperado**: Collection básica sem análise de IA

## Testes com API Real (Quando disponível)

### Teste Básico com API

```bash
python cli.py analyze \
  --input examples/sample_openapi.yaml \
  --output test-with-api.json \
  --test-api \
  --base-url https://jsonplaceholder.typicode.com
```

**Nota**: Use uma API de teste pública como JSONPlaceholder

### Teste com Autenticação

```bash
export API_TOKEN="seu-token-aqui"

python cli.py analyze \
  --input sua-doc.json \
  --output enriched.json \
  --test-api \
  --base-url https://api.sua-empresa.com \
  --auth-token "$API_TOKEN"
```

## Validação dos Resultados

### 1. Verificar arquivo gerado

```bash
# Ver tamanho do arquivo
ls -lh *.postman_collection.json

# Ver preview do conteúdo
head -50 test-openapi.postman_collection.json

# Validar JSON
python -m json.tool test-openapi.postman_collection.json > /dev/null && echo "✓ JSON válido"
```

### 2. Contar endpoints na collection

```bash
# Contar items na collection
python -c "import json; data=json.load(open('test-openapi.postman_collection.json')); print(f'Endpoints: {len(data[\"item\"])}')"
```

### 3. Verificar campos específicos

```bash
# Ver nome da collection
python -c "import json; print(json.load(open('test-openapi.postman_collection.json'))['info']['name'])"

# Ver primeiro endpoint
python -c "import json; data=json.load(open('test-openapi.postman_collection.json')); print(data['item'][0]['name'])"
```

## Testes de Performance

### Tempo de execução

```bash
time python cli.py analyze \
  --input examples/sample_openapi.yaml \
  --output perf-test.json
```

### Múltiplos arquivos

```bash
for file in examples/*.yaml examples/*.md; do
  echo "Processing: $file"
  python cli.py analyze \
    --input "$file" \
    --output "output-$(basename ${file%.*}).json"
done
```

## Testes de Erro

### Arquivo inexistente

```bash
python cli.py analyze \
  --input arquivo-que-nao-existe.pdf \
  --output output.json
```

**Resultado esperado**: Erro informando que arquivo não existe

### Sem API key (quando necessário)

```bash
unset OPENAI_API_KEY
python cli.py analyze \
  --input examples/sample_openapi.yaml \
  --output test.json
```

**Resultado esperado**: Erro informando API key não configurada

### Test-api sem base-url

```bash
python cli.py analyze \
  --input examples/sample_openapi.yaml \
  --output test.json \
  --test-api
```

**Resultado esperado**: Erro informando que --base-url é obrigatório

## Importar no Postman

Após gerar a collection:

1. Abra o Postman
2. File → Import
3. Selecione o arquivo `.postman_collection.json`
4. Click em "Import"
5. Explore os endpoints!

## Verificações de Qualidade

### Verificar estrutura da collection

A collection gerada deve ter:

```json
{
  "info": {
    "name": "...",
    "description": "...",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Endpoint name",
      "request": {
        "method": "GET/POST/...",
        "url": {...},
        "description": "..."
      },
      "response": [...]
    }
  ]
}
```

### Verificar enriquecimento

A description de cada request deve conter:

- ✅ Descrição do endpoint
- ✅ Documentação dos campos
- ✅ Tipos de dados
- ✅ Obrigatoriedade
- ✅ Códigos de erro
- ✅ Padrões descobertos (se test-api foi usado)

## Exemplos de Uso Real

### 1. Converter Swagger para Postman

```bash
python cli.py analyze \
  --input sua-api-swagger.yaml \
  --output postman-collection.json \
  --collection-name "Minha API"
```

### 2. Enriquecer Postman Collection existente

```bash
python cli.py analyze \
  --input collection-original.json \
  --output collection-enriquecida.json \
  --test-api \
  --base-url https://api.exemplo.com
```

### 3. Documentar API a partir de PDF

```bash
python cli.py analyze \
  --input documentacao-api.pdf \
  --output api.postman_collection.json \
  --collection-name "API da Documentação PDF"
```

## Troubleshooting

### Problema: Parsing demorado

**Solução**: Use --no-ai para testar parsing primeiro

```bash
python cli.py analyze --input file.pdf --output out.json --no-ai
```

### Problema: Muitos créditos OpenAI consumidos

**Solução**: Use cache implementado ou reduza o tamanho dos prompts

### Problema: API tests falhando

**Solução**: Verifique URL e autenticação

```bash
# Teste manual primeiro
curl https://api.exemplo.com/endpoint
```

## Scripts de Automação

### Processar pasta inteira

```bash
#!/bin/bash
for doc in documentacoes/*; do
  name=$(basename "${doc%.*}")
  python cli.py analyze \
    --input "$doc" \
    --output "collections/${name}.postman_collection.json"
done
```

### Com logging

```bash
python cli.py analyze \
  --input doc.pdf \
  --output out.json \
  2>&1 | tee analysis.log
```

## Checklist de Teste

- [ ] Instalar dependências
- [ ] Configurar .env
- [ ] Testar comando info
- [ ] Testar análise de OpenAPI
- [ ] Testar análise de Markdown
- [ ] Testar com --no-ai
- [ ] Verificar JSON gerado
- [ ] Importar no Postman
- [ ] Verificar enriquecimento
- [ ] Testar com API real (opcional)

## Resultados Esperados

Após executar os testes, você deve ter:

1. ✅ Collections geradas em formato Postman v2.1
2. ✅ JSON válido e bem formatado
3. ✅ Endpoints extraídos corretamente
4. ✅ Descrições enriquecidas com IA
5. ✅ Exemplos de request/response
6. ✅ Testes automatizados incluídos
7. ✅ Documentação de campos completa

## Métricas de Sucesso

- **Tempo de análise**: < 30s para docs pequenos
- **Endpoints extraídos**: 100% dos documentados
- **Qualidade da descrição**: Rica e detalhada
- **Padrões descobertos**: Quando test-api é usado
- **JSON válido**: 100% válido para importar no Postman

---

**Pronto para testar! Execute os comandos acima e explore os resultados.**

