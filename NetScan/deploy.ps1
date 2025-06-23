# NetScan Pro - Deploy Script for Windows (PowerShell)
# Certifique-se de ter o Firebase CLI instalado: npm install -g firebase-tools

Write-Host "🚀 NetScan Pro - Deploy para Firebase" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# Check if Firebase CLI is installed
try {
    firebase --version | Out-Null
    Write-Host "✅ Firebase CLI encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Firebase CLI não encontrado. Instale com: npm install -g firebase-tools" -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ Arquivo .env não encontrado. Copie .env.example para .env e configure." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt

# Set production environment
$env:FLASK_ENV = "production"

# Build static assets (if needed)
Write-Host "🔨 Preparando assets..." -ForegroundColor Yellow

# Deploy to Firebase
Write-Host "🚀 Fazendo deploy para Firebase..." -ForegroundColor Yellow
firebase deploy --only hosting,functions,firestore

Write-Host "✅ Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host "🌐 Seu site está disponível em: https://YOUR-PROJECT-ID.web.app" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Para acessar as análises de usuário (admin):" -ForegroundColor Cyan
Write-Host "   https://YOUR-PROJECT-ID.web.app/admin/dashboard?admin_key=YOUR_ADMIN_KEY" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Lembre-se de configurar suas variáveis de ambiente no Firebase Console:" -ForegroundColor Yellow
Write-Host "   - ADMIN_SECRET_KEY" -ForegroundColor White
Write-Host "   - OPENWEATHER_API_KEY" -ForegroundColor White
Write-Host "   - Outras configurações necessárias" -ForegroundColor White
