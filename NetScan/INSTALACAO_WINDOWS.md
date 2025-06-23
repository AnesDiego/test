# NetScan Pro - Guia de Instalação Windows

## 🐍 1. Instalar Python

### **Opção A: Microsoft Store (Recomendado)**
1. Abra a Microsoft Store
2. Procure por "Python 3.11" ou "Python 3.12"
3. Clique em "Instalar"
4. Aguarde a instalação

### **Opção B: Site Oficial**
1. Vá para https://python.org/downloads
2. Baixe Python 3.11+ para Windows
3. Execute o instalador
4. ⚠️ **IMPORTANTE**: Marque "Add Python to PATH"
5. Clique em "Install Now"

## 🔧 2. Verificar Instalação

Abra o PowerShell e execute:
```powershell
python --version
```

Deve retornar algo como: `Python 3.11.x`

## 📦 3. Instalar Dependências

```powershell
# Navegar para o diretório do projeto
cd "C:\Users\test\Desktop\Zypher\NetScan"

# Instalar dependências
python -m pip install -r requirements.txt
```

## 🔐 4. Configurar Environment

```powershell
# Copiar arquivo de configuração (se ainda não foi feito)
Copy-Item ".env.example" ".env"

# Editar o arquivo .env com suas configurações
notepad .env
```

### **Configurações Obrigatórias no .env:**
```env
# Gere uma chave secreta forte para admin
ADMIN_SECRET_KEY=minha-chave-super-secreta-admin-123456789

# Configure seu projeto Firebase
FIREBASE_PROJECT_ID=seu-projeto-firebase-id

# Configure sua API key do OpenWeather (opcional)
OPENWEATHER_API_KEY=sua-chave-openweather

# Ambiente de produção
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-flask-principal
```

## 🔥 5. Configurar Firebase

### **5.1. Criar Projeto Firebase**
1. Vá para https://console.firebase.google.com
2. Clique em "Criar projeto"
3. Nomeie seu projeto (ex: "netscan-analytics")
4. Ative Google Analytics (opcional)
5. Clique em "Criar projeto"

### **5.2. Ativar Firestore**
1. No console Firebase, vá em "Firestore Database"
2. Clique em "Criar banco de dados"
3. Escolha "Iniciar no modo de produção"
4. Selecione a localização (ex: us-central1)

### **5.3. Configurar Service Account**
1. Vá em "Configurações do projeto" > "Contas de serviço"
2. Clique em "Gerar nova chave privada"
3. Baixe o arquivo JSON
4. Renomeie para `firebase-service-account.json`
5. Coloque na pasta raiz do projeto

### **5.4. Configurar Regras do Firestore**
As regras já estão configuradas em `firestore.rules` para máxima privacidade.

## 🚀 6. Executar o Sistema

### **Desenvolvimento (Recomendado para testes):**
```powershell
python app.py
```

### **Produção:**
```powershell
python -m pip install gunicorn
gunicorn --bind 0.0.0.0:8080 --workers 2 app:app
```

## 🌐 7. Acessar o Sistema

- **Site Principal**: http://localhost:5000
- **Dashboard Admin**: http://localhost:5000/admin/dashboard?admin_key=SUA_CHAVE_ADMIN
- **API**: http://localhost:5000/api/8.8.8.8

## 📊 8. Ver Estatísticas de Usuários

Após configurar o Firebase, acesse:
```
http://localhost:5000/admin/dashboard?admin_key=minha-chave-super-secreta-admin-123456789
```

**Substitua `minha-chave-super-secreta-admin-123456789` pela sua chave do .env**

## 🧪 9. Testar o Sistema

```powershell
# Execute o script de teste
.\test_system.ps1
```

## ❗ Troubleshooting

### **Python não encontrado:**
- Reinstale Python marcando "Add to PATH"
- Reinicie o PowerShell
- Use `py` em vez de `python`

### **Erro de módulos:**
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --force-reinstall
```

### **Firebase não inicializa:**
- Verifique se o arquivo `firebase-service-account.json` está na pasta
- Confirme o PROJECT_ID no .env
- Verifique se o Firestore está ativado

### **Admin dashboard não carrega:**
- Confirme a ADMIN_SECRET_KEY no .env
- Use a URL completa com ?admin_key=SUA_CHAVE
- Verifique os logs em `logs/`

## 🎯 Exemplo de .env Completo

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=minha-chave-flask-super-secreta-12345
DEBUG=False

# Firebase Configuration  
FIREBASE_PROJECT_ID=meu-netscan-projeto
FIREBASE_WEB_API_KEY=AIzaSyB...

# Admin Configuration
ADMIN_SECRET_KEY=admin-ultra-secreto-netscan-2025

# External APIs
OPENWEATHER_API_KEY=sua-chave-openweather-opcional

# Security
ALLOWED_HOSTS=localhost,127.0.0.1,seu-dominio.com
```

## 🎉 Pronto!

Seu NetScan Pro está configurado com:
- ✅ Contador de usuários privado
- ✅ Dashboard administrativo
- ✅ Segurança avançada
- ✅ Logs completos
- ✅ Pronto para produção

**Acesse suas estatísticas privadas em:**
`http://localhost:5000/admin/dashboard?admin_key=SUA_CHAVE`
