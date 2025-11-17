#!/bin/bash
# Exemplo de uso simples do AI Documentation Enricher

echo "🚀 AI Documentation Enricher - Modo Simples"
echo "=========================================="
echo ""

# Verificar se há arquivo na pasta input
if [ ! -d "input" ]; then
    echo "❌ Pasta input/ não encontrada"
    exit 1
fi

# Contar arquivos na pasta input (ignorando README)
file_count=$(find input -type f ! -name "README.md" | wc -l)

if [ $file_count -eq 0 ]; then
    echo "❌ Nenhum arquivo encontrado na pasta input/"
    echo ""
    echo "💡 Como usar:"
    echo "1. Coloque um arquivo de documentação na pasta input/"
    echo "2. Execute: bash examples/uso_simples.sh"
    echo ""
    echo "Formatos aceitos: PDF, JSON, Postman Collection, OpenAPI, TXT, Markdown"
    exit 1
fi

echo "✓ Arquivo(s) encontrado(s) na pasta input/"
echo ""

# Executar análise
echo "🤖 Iniciando análise..."
echo ""

python cli.py analyze

# Verificar se funcionou
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Análise concluída com sucesso!"
    echo ""
    echo "📦 Seus resultados estão em: output/"
    echo ""
    echo "Arquivos gerados:"
    ls -lh output/*.json output/*.txt 2>/dev/null | tail -2
    echo ""
    echo "📖 Próximos passos:"
    echo "1. Abra o arquivo _RESUMO.txt para entender a API"
    echo "2. Importe o arquivo .json no Postman"
    echo ""
else
    echo ""
    echo "❌ Erro na análise"
    echo ""
    echo "Verifique:"
    echo "- Se o arquivo .env está configurado com OPENAI_API_KEY"
    echo "- Se o arquivo não está corrompido"
    echo "- Se você tem internet"
    exit 1
fi

