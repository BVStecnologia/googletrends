#!/bin/bash

echo "🚀 Iniciando Google Trends API..."
echo ""
echo "📊 A API estará disponível em:"
echo "   http://localhost:8000"
echo ""
echo "📖 Documentação interativa:"
echo "   http://localhost:8000/docs"
echo ""
echo "⚠️  Nota: Google Trends tem rate limiting. Use com moderação."
echo ""

cd "$(dirname "$0")"
python main_improved.py