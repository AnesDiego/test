# NetScan Pro - Test Script
# Testa as funcionalidades principais do sistema

Write-Host "🧪 NetScan Pro - Teste de Sistema" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Test 1: Import modules
Write-Host "1. Testando imports..." -ForegroundColor Yellow
try {
    python -c "
import sys
sys.path.append('.')
from config import config
from firebase_service import FirebaseService
from security import SecurityMiddleware, validate_ip_input
from logging_config import setup_logging
print('✅ Todos os imports funcionando!')
"
    Write-Host "   ✅ Imports: OK" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Erro nos imports" -ForegroundColor Red
    Write-Host "   Execute: pip install -r requirements.txt" -ForegroundColor Yellow
}

# Test 2: Configuration
Write-Host "2. Testando configuração..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   ✅ Arquivo .env: OK" -ForegroundColor Green
} else {
    Write-Host "   ❌ Arquivo .env não encontrado" -ForegroundColor Red
}

# Test 3: Firebase config
Write-Host "3. Testando configuração Firebase..." -ForegroundColor Yellow
try {
    python -c "
import os
from dotenv import load_dotenv
load_dotenv()
project_id = os.environ.get('FIREBASE_PROJECT_ID')
if project_id and project_id != 'your-firebase-project-id':
    print('✅ Firebase configurado')
else:
    print('⚠️ Firebase precisa ser configurado no .env')
"
} catch {
    Write-Host "   ❌ Erro na configuração Firebase" -ForegroundColor Red
}

# Test 4: Security validation
Write-Host "4. Testando validação de IP..." -ForegroundColor Yellow
try {
    python -c "
from security import validate_ip_input
test_ips = ['8.8.8.8', '192.168.1.1', 'google.com']
for ip in test_ips:
    try:
        result = validate_ip_input(ip)
        print(f'✅ {ip} -> {result}')
    except Exception as e:
        print(f'❌ {ip} -> Error: {e}')
"
} catch {
    Write-Host "   ❌ Erro na validação de IP" -ForegroundColor Red
}

# Test 5: Try running the app
Write-Host "5. Testando inicialização do app..." -ForegroundColor Yellow
Write-Host "   Tentando importar app principal..." -ForegroundColor Cyan
try {
    python -c "
import sys
sys.path.append('.')
from app import app
print('✅ App inicializado com sucesso!')
print(f'✅ Configuração ativa: {app.config.get(\"ENV\", \"development\")}')
"
    Write-Host "   ✅ App: OK" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Erro na inicialização do app" -ForegroundColor Red
    Write-Host "   Verifique as dependências e configurações" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Próximos Passos:" -ForegroundColor Cyan
Write-Host "1. Configure o .env com suas credenciais reais" -ForegroundColor White
Write-Host "2. Configure o Firebase e baixe o service account" -ForegroundColor White
Write-Host "3. Execute: python app.py" -ForegroundColor White
Write-Host "4. Acesse: http://localhost:5000" -ForegroundColor White
Write-Host "5. Admin: http://localhost:5000/admin/dashboard?admin_key=SUA_CHAVE" -ForegroundColor White

Write-Host ""
Write-Host "🔧 Para desenvolvimento rápido:" -ForegroundColor Cyan
Write-Host "   python app.py" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Para produção:" -ForegroundColor Cyan
Write-Host "   gunicorn --bind 0.0.0.0:8080 app:app" -ForegroundColor White
