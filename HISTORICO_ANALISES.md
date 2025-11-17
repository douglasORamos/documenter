# 📚 Histórico de Análises

## ✅ Funcionalidade Implementada

Cada análise agora cria uma **pasta separada** em `output/`, preservando todo o histórico!

---

## 📁 Estrutura

### Antes (Sobrescrevia):

```
output/
├── api.postman_collection.json  ← Sobrescrito a cada execução
├── api_RESUMO.txt                ← Perdido
└── api_ESTATISTICAS.txt          ← Perdido
```

❌ Perdia análises anteriores

### Agora (Preserva):

```
output/
├── minha-api_20241112_163000/
│   ├── minha-api.postman_collection.json
│   ├── minha-api_RESUMO.txt
│   ├── minha-api_ESTATISTICAS.txt
│   └── minha-api_CONTEXTO.txt
│
├── minha-api_20241112_170000/
│   ├── minha-api.postman_collection.json  ← Nova versão
│   ├── minha-api_RESUMO.txt
│   ├── minha-api_ESTATISTICAS.txt
│   └── minha-api_CONTEXTO.txt
│
└── README.md
```

✅ **Mantém todo o histórico!**

---

## 🎯 Formato da Pasta

```
{nome_do_arquivo}_{YYYYMMDD_HHMMSS}/
```

**Exemplo**:
- `API-Crefaz_20241112_164719/`
- `CartaoBeneficio_20241113_093045/`
- `minha-api_20241115_141230/`

**Componentes**:
- Nome do arquivo original (sem extensão)
- Data: YYYYMMDD (Ano/Mês/Dia)
- Hora: HHMMSS (Hora/Minuto/Segundo)

---

## 💡 Casos de Uso

### 1. Comparar Versões

```bash
# Analisar v1
cp api-v1.pdf input/
python main.py
# → output/api-v1_20241112_100000/

# Analisar v2 (depois)
cp api-v2.pdf input/
python main.py
# → output/api-v2_20241112_110000/

# Comparar
diff output/api-v1_*/RESUMO.txt output/api-v2_*/RESUMO.txt
```

### 2. Múltiplas Análises do Mesmo Arquivo

```bash
# Primeira análise
python main.py
# → output/minha-api_20241112_090000/

# Segunda análise (configuração diferente)
# .env: ENABLE_PRODUCTION_OPERATIONS=true
python main.py
# → output/minha-api_20241112_090030/

# Histórico preservado!
```

### 3. Auditoria

```bash
# Ver todas as análises
ls -lt output/

# Encontrar análise específica
find output/ -name "*20241112*"

# Ver evolução
for dir in output/minha-api_*/; do
  echo "=== $dir ==="
  cat "$dir"/*_ESTATISTICAS.txt | grep "Total"
done
```

---

## 🗂️ Organização

### Listar Análises:

```bash
# Por data (mais recente primeiro)
ls -lt output/

# Por nome
ls -1 output/
```

### Limpar Antigas:

```bash
# Manter apenas últimas 5 análises
cd output/
ls -t | tail -n +6 | xargs rm -rf
```

### Arquivar:

```bash
# Mover para arquivo morto
mkdir arquivo/
mv output/minha-api_2024110*/ arquivo/
```

---

## ✅ Benefícios

1. ✅ **Histórico Completo**
   - Todas as análises salvas
   - Nada é perdido
   - Fácil comparar

2. ✅ **Rastreabilidade**
   - Timestamp em cada pasta
   - Sabe quando foi gerado
   - Auditável

3. ✅ **Experimentação**
   - Teste diferentes configs
   - Compare resultados
   - Sem medo de perder dados

4. ✅ **Organização**
   - Uma pasta por análise
   - Fácil navegar
   - Fácil arquivar

---

## 📊 Exemplo Real

```bash
# Executar 3 vezes ao longo do dia:

# 09:00
python main.py
# → output/API-Crefaz_20241112_090000/

# 14:30  
python main.py
# → output/API-Crefaz_20241112_143000/

# 18:00
python main.py
# → output/API-Crefaz_20241112_180000/

# Resultado:
output/
├── API-Crefaz_20241112_090000/  ← Manhã
├── API-Crefaz_20241112_143000/  ← Tarde
├── API-Crefaz_20241112_180000/  ← Noite (mais recente)
└── README.md

✅ Todas as 3 análises preservadas!
```

---

## 🎯 Melhores Práticas

### Manter Organizado:

```bash
# Criar estrutura
output/
├── 2024-11/              ← Por mês
│   ├── api-v1_...
│   └── api-v2_...
├── 2024-12/
│   └── ...
└── README.md
```

### Limpar Periodicamente:

```bash
# Manter apenas do último mês
find output/ -type d -mtime +30 -exec rm -rf {} \;
```

---

## ✨ Resumo

**Funcionalidade**:
- ✅ Cada análise → nova pasta
- ✅ Formato: `{nome}_{timestamp}/`
- ✅ 4 arquivos por pasta
- ✅ Histórico preservado
- ✅ Zero perda de dados

**Status**: Implementado e Testado ✅

---

**Agora você tem histórico completo de todas as análises! 📚**

