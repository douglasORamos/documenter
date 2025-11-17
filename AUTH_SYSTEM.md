# 🔐 Sistema de Autenticação - Documentação Completa

## ✅ Implementado

Sistema completo de autenticação e classificação de operações para testes seguros.

---

## 🎯 Funcionalidades

### 1. **Detecção Automática de Autenticação**

O sistema detecta automaticamente o método de autenticação da documentação:

- ✅ Bearer Token
- ✅ Basic Auth (username/password)
- ✅ API Key (header ou query)
- ✅ OAuth 2.0
- ✅ WS-Security (SOAP)

### 2. **Credenciais em input/credentials.json**

Coloque suas credenciais em `input/credentials.json`:

```json
{
  "auth_type": "bearer",
  "credentials": {
    "token": "seu-token-aqui"
  }
}
```

### 3. **Classificação Inteligente de Operações**

**IA identifica operações de PRODUÇÃO** pelo nome e descrição:

- ✅ `gravarProposta` → PRODUÇÃO (cria proposta real)
- ✅ `digitarContrato` → PRODUÇÃO (registra contrato)
- ✅ `aprovarProposta` → PRODUÇÃO (aprova definitivamente)
- ✅ `buscarProposta` → LEITURA (apenas consulta)

### 4. **Controle de Operações de Produção**

Config no `.env`:

```bash
ENABLE_PRODUCTION_OPERATIONS=false
```

Quando `false`, pula automaticamente operações que:
- Criam dados reais
- Aprovam/efetivam
- Modificam produção
- Deletam permanentemente

---

## 📁 Estrutura de Arquivos

```
input/
├── sua-documentacao.pdf           ← Documentação
└── credentials.json              ← Credenciais (criar a partir do .example)

.env
ENABLE_PRODUCTION_OPERATIONS=false  ← Controle de produção
```

---

## 🚀 Como Usar

### Passo 1: Criar Credenciais

```bash
# Copiar exemplo
cp input/credentials.json.example input/credentials.json

# Editar input/credentials.json
{
  "auth_type": "bearer",
  "credentials": {
    "token": "SEU_TOKEN_REAL_AQUI"
  }
}
```

### Passo 2: Configurar Produção

No arquivo `.env`:

```bash
ENABLE_PRODUCTION_OPERATIONS=false  ← Não testa produção (SEGURO)
# ou
ENABLE_PRODUCTION_OPERATIONS=true   ← Testa TUDO (CUIDADO!)
```

### Passo 3: Executar

```bash
python main.py --test-api --base-url https://api.exemplo.com
```

### Output Esperado:

```
✓ Auth method: bearer
✓ Credentials from: input/credentials.json
⚠ Production DISABLED: 3 safe, 4 skipped

📋 Classificação:

LEITURA (testadas):
✓ buscarProposta
✓ consultarStatus  
✓ listarClientes

PRODUÇÃO (puladas):
⚠ gravarProposta - Cria proposta real
⚠ digitarContrato - Registra contrato
⚠ aprovarProposta - Aprova definitivamente
⚠ criarCliente - Cria cliente permanente

Testando 3 operações seguras...
```

---

## 🔒 Tipos de Autenticação Suportados

### 1. Bearer Token

**credentials.json:**
```json
{
  "auth_type": "bearer",
  "credentials": {
    "token": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

**Usado para**: APIs modernas, JWT

### 2. Basic Auth

**credentials.json:**
```json
{
  "auth_type": "basic",
  "credentials": {
    "username": "seu-usuario",
    "password": "sua-senha"
  }
}
```

**Usado para**: APIs legadas, sistemas internos

### 3. API Key

**credentials.json:**
```json
{
  "auth_type": "api_key",
  "credentials": {
    "key": "sua-api-key-123",
    "header": "X-API-Key",
    "location": "header"
  }
}
```

**Usado para**: APIs públicas, serviços cloud

### 4. OAuth 2.0

**credentials.json:**
```json
{
  "auth_type": "oauth",
  "credentials": {
    "access_token": "seu-access-token"
  }
}
```

**Usado para**: Integrações sociais, APIs corporativas

### 5. SOAP WS-Security

**credentials.json:**
```json
{
  "auth_type": "soap_security",
  "credentials": {
    "username": "usuario-ws",
    "password": "senha-ws"
  }
}
```

**Usado para**: Web Services SOAP bancários, governamentais

---

## 🎯 Classificação de Operações

### Como a IA Identifica

**Operações de PRODUÇÃO** (risco ALTO):

Palavras-chave no nome/descrição:
- **Criar**: gravar, criar, inserir, salvar, cadastrar, digitar, registrar
- **Aprovar**: aprovar, confirmar, efetivar, finalizar, concluir
- **Modificar**: atualizar (permanente), modificar, alterar
- **Deletar**: deletar, remover, excluir, cancelar

**Exemplos PRODUÇÃO**:
- `gravarProposta` - "grava" indica criação
- `digitarContrato` - "digitar" indica registro permanente
- `aprovarProposta` - "aprovar" indica ação definitiva
- `criarCliente` - "criar" indica novo registro
- `excluirDados` - "excluir" indica remoção

**Operações SEGURAS** (risco BAIXO):

Palavras-chave:
- buscar, consultar, listar, obter, verificar, validar
- search, get, list, find, check, validate

**Exemplos SEGURAS**:
- `buscarProposta` - apenas leitura
- `consultarStatus` - apenas consulta
- `listarClientes` - apenas lista
- `validarCPF` - validação sem persistir

---

## ⚙️ Configuração

### .env

```bash
# OpenAI (modelo econômico)
OPENAI_API_KEY=sua_chave
OPENAI_MODEL=gpt-3.5-turbo

# Controle de Produção
ENABLE_PRODUCTION_OPERATIONS=false  ← RECOMENDADO: false

# Timeout
DEFAULT_TIMEOUT=30
MAX_RETRIES=3
```

### input/credentials.json

```json
{
  "auth_type": "bearer",
  "credentials": {
    "token": "TOKEN_REAL_AQUI"
  }
}
```

---

## 🛡️ Segurança

### ✅ Boas Práticas:

1. **NUNCA commite** `input/credentials.json`
2. **Sempre use** `ENABLE_PRODUCTION_OPERATIONS=false` em produção
3. **Revise** as operações classificadas antes de testar
4. **Use ambiente de teste** quando possível

### ⚠️ Avisos:

```
⚠ PULANDO OPERAÇÃO DE PRODUÇÃO: gravarProposta
   Risco: HIGH
   Motivo: Cria proposta real no banco de dados
   Config: ENABLE_PRODUCTION_OPERATIONS=false
```

### 📋 Arquivo .gitignore:

```gitignore
# Credentials (protegido)
input/credentials.json
credentials.json
```

---

## 📊 Exemplos de Classificação

### API Bancária (SOAP):

```
Operações Classificadas:

🔍 LEITURA/CONSULTA (Safe - Testadas):
✓ buscarLimiteSaque - Consulta limite disponível
✓ buscarSimulacao - Simula parcelas
✓ ObtemProfissões - Lista profissões
✓ ValidaSeJaPossuiContaCartao - Valida existência

⚠ PRODUÇÃO/CRIAÇÃO (Risky - Puladas):
⚠ gravarPropostaCartao - CRIA PROPOSTA REAL EM PRODUÇÃO
   Risco: HIGH
   Efeitos: creates_data, permanent, production
```

### API REST:

```
Operações Classificadas:

🔍 LEITURA (Safe):
✓ GET /propostas - Lista propostas
✓ GET /propostas/{id} - Consulta proposta
✓ GET /clientes - Lista clientes

⚠ PRODUÇÃO (Risky):
⚠ POST /propostas - Cria nova proposta
⚠ POST /propostas/{id}/aprovar - Aprova proposta
⚠ DELETE /clientes/{id} - Remove cliente
```

---

## 💻 Uso Prático

### Teste Seguro (Apenas Leitura):

```bash
# 1. Config
ENABLE_PRODUCTION_OPERATIONS=false

# 2. Credenciais
cat > input/credentials.json << 'EOF'
{
  "auth_type": "bearer",
  "credentials": {"token": "token-ambiente-dev"}
}
EOF

# 3. Executar
python main.py --test-api --base-url https://api-dev.empresa.com

# Resultado:
✓ Testa apenas buscar/consultar/listar
⚠ Pula gravar/criar/aprovar/deletar
```

### Teste Completo (COM Produção - Cuidado!):

```bash
# 1. Config
ENABLE_PRODUCTION_OPERATIONS=true  ← CUIDADO!

# 2. Usar ambiente de TESTE
python main.py --test-api --base-url https://api-TESTE.empresa.com

# Resultado:
✓ Testa TUDO incluindo operações de produção
⚠ Use apenas em ambiente de teste!
```

---

## 📖 Documentação Relacionada

- `input/credentials.json.example` - Exemplos de credenciais
- `SOAP_SUPPORT.md` - Suporte SOAP
- `COMO_USAR.md` - Guia geral

---

## 🎉 Benefícios

1. ✅ **Seguro** - Não cria dados em produção por acidente
2. ✅ **Inteligente** - IA identifica operações perigosas
3. ✅ **Automático** - Detecta auth e classifica
4. ✅ **Flexível** - Suporta múltiplos tipos de auth
5. ✅ **Rastreável** - Logs claros do que foi pulado

---

**Sistema de autenticação e classificação: 100% funcional! 🔐**

