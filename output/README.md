# 📤 Pasta OUTPUT

Os arquivos gerados aparecerão aqui em subpastas automaticamente.

Cada análise cria uma nova pasta para manter histórico:
```
output/
├── minha-api_20241112_163000/
│   ├── *.postman_collection.json
│   ├── *_RESUMO.txt
│   ├── *_ESTATISTICAS.txt
│   └── *_CONTEXTO.txt
├── minha-api_20241112_170000/
│   └── ... (análise mais recente)
└── README.md
```

## O que você encontrará aqui:

Após executar `python main.py` ou `python cli.py analyze`, você terá **4 arquivos**:

### 1. 📦 Postman Collection (`.postman_collection.json`)
Arquivo técnico completo para importar no Postman com:
- Todos os endpoints/operações documentados
- Exemplos de requisições e respostas
- Testes automatizados
- Validações e regras descobertas
- **Para SOAP**: XML com SOAP Envelope
- **Para REST**: JSON bodies

### 2. 📄 Resumo em Texto (`_RESUMO.txt`)
Explicação em linguagem simples com:
- Visão geral da API/Web Service
- Operações disponíveis
- Fluxos de uso passo a passo
- Regras de negócio
- Estrutura de dados
- Guia de erros
- **Adaptado** ao tipo de API (SOAP ou REST)

### 3. 📊 Estatísticas (`_ESTATISTICAS.txt`)
Métricas e números da análise:
- Total de endpoints/operações
- Tipos de campos identificados
- Padrões descobertos
- Resultados de testes (se executados)

### 4. 🧠 Contexto de Execução (`_CONTEXTO.txt`)
Conhecimento acumulado durante a análise:
- Termos do domínio extraídos
- Campos e tipos identificados
- Regras de negócio descobertas
- Namespaces (para SOAP)
- Validações encontradas
- **Usado para reduzir custos de IA**

## Como usar os arquivos:

### Postman Collection:
1. Abra o Postman
2. Clique em "Import"
3. Selecione o arquivo `.postman_collection.json`
4. Explore!

### Resumo TXT:
1. Abra com qualquer editor de texto
2. Leia para entender a API
3. Compartilhe com a equipe

## Exemplo de saída:

```
output/
  ├── api-documentation.postman_collection.json  ← Para desenvolvedores
  └── api-documentation_RESUMO.txt              ← Para todos
```

## 🎯 Dica:

O resumo em texto é perfeito para:
- Compartilhar com gerentes e stakeholders
- Entender rapidamente a API
- Documentação inicial do projeto
- Base para criar manuais

