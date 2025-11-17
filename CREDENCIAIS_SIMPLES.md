# 🔐 Credenciais Ultra-Simples

## 💡 Conceito

**Você só coloca os dados. A IA descobre como usar!**

---

## 📄 Arquivo: input/credentials.json

### Formato Genérico:

```json
{
  "username": "seu-usuario",
  "password": "sua-senha",
  "token": "seu-token-se-tiver",
  "api_key": "sua-chave-se-tiver"
}
```

**Só isso!** A IA analisa a documentação e descobre:
- Qual campo usar
- Como aplicar
- Onde colocar

---

## 🎯 Exemplos Práticos

### Exemplo 1: Só tem Token

```json
{
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Sistema faz**:
- ✓ IA analisa documentação
- ✓ Detecta: "API usa Bearer Token"
- ✓ Aplica: `Authorization: Bearer {token}`

### Exemplo 2: Usuário e Senha

```json
{
  "username": "admin",
  "password": "senha123"
}
```

**Sistema faz**:
- ✓ IA analisa documentação
- ✓ Detecta: "API usa Basic Auth" ou "SOAP WS-Security"
- ✓ Aplica corretamente (Basic ou SOAP)

### Exemplo 3: API Key

```json
{
  "api_key": "sk_live_abc123def456"
}
```

**Sistema faz**:
- ✓ IA analisa documentação
- ✓ Detecta: "API usa X-API-Key header"
- ✓ Aplica: `X-API-Key: {api_key}`

### Exemplo 4: Múltiplos Dados

```json
{
  "username": "user",
  "password": "pass",
  "api_key": "key123"
}
```

**Sistema faz**:
- ✓ IA analisa documentação
- ✓ Decide quais campos usar
- ✓ Ignora os não usados

---

## 🚀 Como Funciona

### 1. Você Cria o Arquivo

```bash
cat > input/credentials.json << 'EOF'
{
  "username": "meu-user",
  "password": "minha-senha"
}
EOF
```

### 2. A IA Analisa

Quando você executa `python main.py`:

```
✓ Credenciais: input/credentials.json
  Campos disponíveis: username, password

🔐 Analisando autenticação da API...
  ✓ Método identificado: basic
  A IA determinou como usar as credenciais

Aplicando Basic Auth com username e password...
```

### 3. Sistema Aplica Automaticamente

A IA:
- Lê a documentação
- Vê que usa Basic Auth
- Pega `username` e `password`
- Codifica em Base64
- Aplica: `Authorization: Basic {base64}`

**Você não fez nada além de colocar os dados!** 🎉

---

## 🎓 Casos de Uso

### Caso 1: API SOAP Bancária

**Documentação diz**: "Usa WS-Security com usuário e senha"

**Você coloca**:
```json
{
  "username": "usuario_ws",
  "password": "senha_ws"
}
```

**IA faz**:
- Detecta: WS-Security
- Gera XML com `<wsse:UsernameToken>`
- Aplica no SOAP Header

### Caso 2: API REST Moderna

**Documentação diz**: "Requer Bearer Token no header Authorization"

**Você coloca**:
```json
{
  "token": "seu-jwt-token-aqui"
}
```

**IA faz**:
- Detecta: Bearer
- Aplica: `Authorization: Bearer {token}`

### Caso 3: API com Chave

**Documentação diz**: "Envie X-API-Key no header"

**Você coloca**:
```json
{
  "api_key": "sua-chave-123"
}
```

**IA faz**:
- Detecta: API Key
- Aplica: `X-API-Key: {api_key}`

---

## 📋 Campos Possíveis

Você pode ter qualquer combinação:

```json
{
  "username": "...",      // Para Basic Auth ou SOAP
  "password": "...",      // Para Basic Auth ou SOAP
  "token": "...",         // Para Bearer Token
  "api_key": "...",       // Para API Key
  "client_id": "...",     // Para OAuth
  "client_secret": "...", // Para OAuth
  "access_token": "..."   // Para OAuth
}
```

**Coloque apenas os que você tem!**

Deixe vazios ou não inclua os que não usar.

---

## 🔒 Segurança

✅ **Protegido pelo .gitignore**:
```gitignore
input/credentials.json  ← NUNCA commitado
```

✅ **Arquivo separado**:
- Não está no código
- Fácil de trocar
- Não é versionado

✅ **Exemplo disponível**:
```bash
cp input/credentials.json.example input/credentials.json
# Edite com seus dados reais
```

---

## 💡 Comparação

### Antes (Complexo):
```json
{
  "auth_type": "bearer",
  "credentials": {
    "token": "xxx"
  }
}
```
❌ Você precisa saber o tipo de auth  
❌ Estrutura específica  
❌ Configuração manual  

### Agora (Simples):
```json
{
  "token": "xxx"
}
```
✅ Só os dados  
✅ IA descobre o resto  
✅ Zero config  

---

## 🎯 Uso Completo

```bash
# 1. Documentação
cp api-banco.pdf input/

# 2. Credenciais (genéricas!)
cat > input/credentials.json << 'EOF'
{
  "username": "usuario_api",
  "password": "senha123"
}
EOF

# 3. Executar
python main.py

# Sistema faz TUDO:
✓ Lê documentação
✓ Detecta tipo de API (SOAP/REST)
✓ Detecta método de auth
✓ Usa credenciais corretamente
✓ Classifica operações
✓ Pula produção
✓ Testa com segurança
```

---

**Zero carga mental! Só jogar o arquivo e as credenciais! 🚀**

