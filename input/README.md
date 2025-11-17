# 📥 Pasta INPUT

Coloque aqui os arquivos que você deseja analisar.

---

## 📄 Documentação

Coloque **um arquivo** de documentação por vez:

- ✅ **PDF** - Documentação em PDF
- ✅ **JSON** - Arquivos JSON genéricos  
- ✅ **Postman Collection** - Collections do Postman
- ✅ **OpenAPI/Swagger** - Especificações OpenAPI (JSON ou YAML)
- ✅ **TXT** - Arquivos de texto
- ✅ **Markdown** - Arquivos .md

---

## 🔐 Credenciais (Opcional)

Se quiser testar a API, crie o arquivo `credentials.json`:

### Formato Ultra-Simples:

```json
{
  "username": "seu-usuario",
  "password": "sua-senha",
  "token": "seu-token-se-tiver",
  "api_key": "sua-chave-se-tiver"
}
```

**A IA descobre automaticamente como usar!**

Você só precisa colocar os dados que tem. Exemplos:

### Exemplo 1: Só tem Token

```json
{
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

A IA detecta: "Essa API usa Bearer Token" e usa automaticamente.

### Exemplo 2: Tem Usuário e Senha

```json
{
  "username": "admin",
  "password": "senha123"
}
```

A IA detecta: "Essa API usa Basic Auth ou SOAP Security" e aplica corretamente.

### Exemplo 3: Tem API Key

```json
{
  "api_key": "sk_live_abc123..."
}
```

A IA detecta: "Essa API usa API Key no header X-API-Key" e configura.

### Exemplo 4: Múltiplos Dados

```json
{
  "username": "user",
  "password": "pass",
  "api_key": "key123",
  "token": "token456"
}
```

A IA analisa a documentação e usa os campos corretos!

---

## 🎯 Como Funciona

1. **Você coloca** dados genéricos no `credentials.json`
2. **A IA analisa** a documentação da API
3. **A IA determina** qual campo usar e como
4. **Sistema aplica** automaticamente nas requisições

**Zero configuração manual! 🎉**

---

## 📋 Arquivo Exemplo

Veja: `credentials.json.example`

Para usar:
```bash
cp credentials.json.example credentials.json
# Edite credentials.json com seus dados reais
```

---

## ⚠️ Importante

- Coloque **apenas um arquivo de documentação** por vez
- O `credentials.json` é **opcional** (só para testar API)
- Nunca commite `credentials.json` (já está no .gitignore)
- Após processar, pode mover os arquivos para organizar

---

## 🚀 Exemplo de Uso

```bash
# 1. Coloque documentação
cp minha-api.pdf input/

# 2. (Opcional) Credenciais genéricas
cat > input/credentials.json << 'EOF'
{
  "username": "meu-user",
  "password": "minha-senha"
}
EOF

# 3. Execute
python main.py

# A IA faz tudo:
# ✓ Detecta tipo de API
# ✓ Detecta método de auth
# ✓ Usa credenciais corretas
# ✓ Classifica operações
# ✓ Testa com segurança
```

---

**Simples assim! Apenas coloque os dados e a IA descobre o resto! 🤖**
