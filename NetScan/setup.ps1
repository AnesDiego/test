# NetScan Pro - Setup Script (PowerShell)
# Execute este script para configurar rapidamente o projeto

Write-Host "🚀 NetScan Pro - Configuração Inicial" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado. Instale Python 3.9+" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "📦 Criando ambiente virtual..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "🔧 Ativando ambiente virtual..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📚 Instalando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Criando arquivo .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  IMPORTANTE: Configure o arquivo .env com suas credenciais!" -ForegroundColor Red
}

# Create necessary directories
Write-Host "📁 Criando diretórios necessários..." -ForegroundColor Yellow
if (-not (Test-Path "data")) { New-Item -ItemType Directory -Path "data" }
if (-not (Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" }
if (-not (Test-Path "ssl")) { New-Item -ItemType Directory -Path "ssl" }

Write-Host ""
Write-Host "✅ Configuração inicial concluída!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
Write-Host "1. Configure o arquivo .env com suas credenciais" -ForegroundColor White
Write-Host "2. Configure o Firebase e baixe o service account key" -ForegroundColor White
Write-Host "3. Execute: python app.py (para desenvolvimento)" -ForegroundColor White
Write-Host "4. Para produção, use: gunicorn app:app" -ForegroundColor White
Write-Host ""
Write-Host "🔗 URLs importantes:" -ForegroundColor Cyan
Write-Host "   - Site: http://localhost:5000" -ForegroundColor White
Write-Host "   - API: http://localhost:5000/api/<ip>" -ForegroundColor White
Write-Host "   - Admin: http://localhost:5000/admin/dashboard?admin_key=YOUR_KEY" -ForegroundColor White
