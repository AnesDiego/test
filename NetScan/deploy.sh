#!/bin/bash

# NetScan Pro - Deploy Script for Firebase
# Make sure you have Firebase CLI installed: npm install -g firebase-tools

set -e

echo "🚀 NetScan Pro - Deploy para Firebase"
echo "=================================="

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI não encontrado. Instale com: npm install -g firebase-tools"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Arquivo .env não encontrado. Copie .env.example para .env e configure."
    exit 1
fi

# Install dependencies
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Set production environment
export FLASK_ENV=production

# Build static assets (if needed)
echo "🔨 Preparando assets..."

# Deploy to Firebase
echo "🚀 Fazendo deploy para Firebase..."
firebase deploy --only hosting,functions,firestore

echo "✅ Deploy concluído com sucesso!"
echo "🌐 Seu site está disponível em: https://YOUR-PROJECT-ID.web.app"
echo ""
echo "📊 Para acessar as análises de usuário (admin):"
echo "   https://YOUR-PROJECT-ID.web.app/admin/dashboard?admin_key=YOUR_ADMIN_KEY"
echo ""
echo "🔐 Lembre-se de configurar suas variáveis de ambiente no Firebase Console:"
echo "   - ADMIN_SECRET_KEY"
echo "   - OPENWEATHER_API_KEY"
echo "   - Outras configurações necessárias"
