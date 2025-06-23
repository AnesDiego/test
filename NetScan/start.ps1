# NetScan Pro - Inicialização Rápida
# Execute este script após configurar o .env

param(
    [switch]$Dev,
    [switch]$Prod,
    [switch]$Test,
    [switch]$Install,
    [string]$AdminKey
)

Write-Host ""
Write-Host "🌐 NetScan Pro - Plataforma de Inteligência de Rede" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

if ($Install) {
    Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
    try {
        python -m pip install -r requirements.txt
        Write-Host "✅ Dependências instaladas!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Erro na instalação. Verifique se Python está instalado." -ForegroundColor Red
        Write-Host "💡 Veja INSTALACAO_WINDOWS.md para ajuda" -ForegroundColor Yellow
        exit 1
    }
}

if ($Test) {
    Write-Host "🧪 Executando testes do sistema..." -ForegroundColor Yellow
    & ".\test_system.ps1"
    exit
}

# Verificar se .env existe
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Arquivo .env não encontrado!" -ForegroundColor Yellow
    Write-Host "📝 Criando .env a partir do exemplo..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Arquivo .env criado!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔧 IMPORTANTE: Configure o arquivo .env antes de continuar!" -ForegroundColor Red
    Write-Host "   Edite o arquivo e configure suas credenciais:" -ForegroundColor White
    Write-Host "   - ADMIN_SECRET_KEY (para acessar estatísticas)" -ForegroundColor White
    Write-Host "   - FIREBASE_PROJECT_ID (se quiser analytics)" -ForegroundColor White
    Write-Host ""
    Write-Host "📖 Veja INSTALACAO_WINDOWS.md para instruções detalhadas" -ForegroundColor Cyan
    
    $response = Read-Host "Deseja abrir o .env agora? (s/n)"
    if ($response -eq "s" -or $response -eq "S") {
        notepad .env
    }
    Write-Host "Reinicie este script após configurar o .env" -ForegroundColor Yellow
    exit
}

# Mostrar informações importantes
Write-Host ""
Write-Host "📋 Informações do Sistema:" -ForegroundColor Cyan
Write-Host "  • Site Principal: http://localhost:5000" -ForegroundColor White
Write-Host "  • API Endpoint: http://localhost:5000/api/<ip>" -ForegroundColor White

# Verificar se tem admin key configurada
try {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "ADMIN_SECRET_KEY=([^\r\n]+)") {
        $adminKey = $matches[1]
        if ($adminKey -and $adminKey -ne "sua-chave-administrativa-ultra-secreta-netscan-2025") {
            Write-Host "  • Dashboard Admin: http://localhost:5000/admin/dashboard?admin_key=$adminKey" -ForegroundColor Magenta
            Write-Host "    📊 Acesse suas estatísticas privadas de usuários!" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  Configure ADMIN_SECRET_KEY no .env para ver estatísticas" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "  ⚠️  Configure ADMIN_SECRET_KEY no .env para ver estatísticas" -ForegroundColor Yellow
}

Write-Host ""

if ($Dev) {
    Write-Host "🚀 Iniciando em modo DESENVOLVIMENTO..." -ForegroundColor Green
    Write-Host "   (Com debug ativado e recarregamento automático)" -ForegroundColor Cyan
    Write-Host ""
    $env:FLASK_ENV = "development"
    $env:FLASK_DEBUG = "1"
    python app.py
} elseif ($Prod) {
    Write-Host "🏭 Iniciando em modo PRODUÇÃO..." -ForegroundColor Green
    Write-Host "   (Otimizado para performance)" -ForegroundColor Cyan
    Write-Host ""
    
    # Verificar se gunicorn está instalado
    try {
        python -c "import gunicorn" 2>$null
        if ($LASTEXITCODE -eq 0) {
            gunicorn --bind 0.0.0.0:8080 --workers 2 --threads 2 app:app
        } else {
            Write-Host "📦 Instalando Gunicorn..." -ForegroundColor Yellow
            python -m pip install gunicorn
            gunicorn --bind 0.0.0.0:8080 --workers 2 --threads 2 app:app
        }
    } catch {
        Write-Host "⚠️  Gunicorn não disponível, usando Flask built-in server" -ForegroundColor Yellow
        $env:FLASK_ENV = "production"
        python app.py
    }
} else {
    Write-Host "💡 Opções disponíveis:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  .\start.ps1 -Dev       # Modo desenvolvimento" -ForegroundColor White
    Write-Host "  .\start.ps1 -Prod      # Modo produção" -ForegroundColor White
    Write-Host "  .\start.ps1 -Test      # Executar testes" -ForegroundColor White
    Write-Host "  .\start.ps1 -Install   # Instalar dependências" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 Iniciando em modo padrão (desenvolvimento)..." -ForegroundColor Green
    
    Start-Sleep -Seconds 2
    
    $env:FLASK_ENV = "development"
    $env:FLASK_DEBUG = "1"
    python app.py
}
