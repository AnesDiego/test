# 🌐 NetScan Pro - Advanced Network Intelligence Platform

> **Plataforma avançada de inteligência de rede com contador de usuários privado e análise completa de IPs**

![NetScan Pro](https://img.shields.io/badge/NetScan-Pro-00ffcc?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green?style=for-the-badge&logo=flask)
![Firebase](https://img.shields.io/badge/Firebase-Analytics-orange?style=for-the-badge&logo=firebase)

## ✨ Funcionalidades

### 🔍 **Análise de IP Avançada**
- Geolocalização detalhada com múltiplas fontes
- Análise de segurança e detecção de ameaças
- Informações de rede (ISP, ASN, tipo de conexão)
- Dados meteorológicos da localização
- Análise de performance de rede
- Detecção de VPN, Proxy, Tor e Data Centers

### 📊 **Analytics Privados** (NOVO)
- **Contador de usuários completamente privado**
- Dashboard administrativo exclusivo
- Estatísticas detalhadas apenas para o admin
- Dados anonimizados e seguros
- Gráficos interativos em tempo real
- Tracking de países e dispositivos

### 🛡️ **Segurança Avançada**
- Rate limiting automático
- Validação de entrada contra injeções
- Headers de segurança configurados
- Logs de segurança detalhados
- Proteção administrativa com chave secreta

### 🚀 **Pronto para Produção**
- Docker e Docker Compose incluídos
- Nginx como proxy reverso
- SSL/TLS configurado
- Logs estruturados
- Monitoramento de performance
- Deploy no Firebase ou servidor próprio

## 🎯 Como Acessar Suas Estatísticas (Privadas)

Após a configuração, acesse:
```
https://seu-site.com/admin/dashboard?admin_key=SUA_CHAVE_SECRETA
```

**Dados que você pode ver:**
- 📈 Total de visitas de todos os tempos
- 👥 Visitantes únicos por dia/mês
- 🌍 Top países que acessaram
- 📊 Gráficos de tendências
- 🔍 Quantos scans foram realizados
- ⏰ Estatísticas em tempo real

## 🚀 Instalação Rápida

### **Windows (PowerShell)**
```powershell
# 1. Clone o repositório
git clone https://github.com/seu-usuario/netscan-pro

# 2. Entre na pasta
cd netscan-pro

# 3. Execute o setup automático
.\setup.ps1

# 4. Configure o .env com suas credenciais
notepad .env

# 5. Execute o sistema
python app.py
```

### **Linux/Mac**
```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/netscan-pro

# 2. Entre na pasta
cd netscan-pro

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure ambiente
cp .env.example .env
nano .env

# 5. Execute
python app.py
```

## 📋 Pré-requisitos

- **Python 3.9+**
- **Firebase Project** (para analytics)
- **OpenWeather API Key** (opcional, para dados meteorológicos)

## ⚙️ Configuração do Firebase

1. **Crie um projeto** no [Firebase Console](https://console.firebase.google.com)
2. **Ative o Firestore Database**
3. **Baixe o service account key** e salve como `firebase-service-account.json`
4. **Configure o .env** com seu PROJECT_ID

## 🌐 URLs Importantes

| Endpoint | Descrição | Exemplo |
|----------|-----------|---------|
| `/` | Site principal | `http://localhost:5000` |
| `/api/<ip>` | API JSON | `http://localhost:5000/api/8.8.8.8` |
| `/admin/dashboard` | Analytics (PRIVADO) | `http://localhost:5000/admin/dashboard?admin_key=CHAVE` |
| `/export/<ip>` | Exportar análise | `http://localhost:5000/export/8.8.8.8` |

## 🐳 Deploy com Docker

```bash
# Desenvolvimento
docker-compose up -d

# Produção
docker-compose -f docker-compose.prod.yml up -d
```

## 🔥 Deploy no Firebase

```bash
# Instalar Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Deploy
firebase deploy
```

## 📊 Exemplo de Dashboard Admin

Quando você acessar `/admin/dashboard?admin_key=SUA_CHAVE`, verá:

```
📈 Estatísticas Gerais
├── 🎯 Total de Visitas: 1,247
├── 👥 Visitantes Únicos Este Mês: 284
├── 🌍 Top Países: Brasil (45%), EUA (23%), Portugal (12%)
└── 📊 Gráfico de Tendências (Últimos 30 dias)

🔍 Análises Realizadas
├── 🌐 Scans de IP: 892
├── 📡 Chamadas API: 355
└── 📁 Exports: 28
```

## 🛡️ Privacidade e Segurança

### **Dados Coletados (Anonimizados)**
- ✅ Hash do IP (não o IP real)
- ✅ País/região
- ✅ Timestamp da visita
- ✅ Tipo de dispositivo (genérico)

### **Dados NÃO Coletados**
- ❌ IPs reais dos usuários
- ❌ Informações pessoais
- ❌ Histórico detalhado
- ❌ Dados sensíveis

### **Proteções Implementadas**
- 🔒 Firestore rules impedem acesso client-side
- 🔑 Admin key obrigatória para estatísticas
- 🚫 Rate limiting automático
- 📝 Logs de segurança
- 🔐 Dados criptografados em trânsito

## 📁 Estrutura do Projeto

```
NetScan/
├── 📄 app.py                    # Aplicação principal
├── ⚙️ config.py                 # Configurações
├── 🔥 firebase_service.py       # Serviço Firebase
├── 🛡️ security.py               # Middleware de segurança
├── 📊 logging_config.py         # Sistema de logs
├── 🐳 Dockerfile               # Container Docker
├── 🔧 docker-compose.yml       # Orquestração
├── 📋 requirements.txt         # Dependências Python
├── 🌐 nginx.conf               # Configuração Nginx
├── 📁 templates/               # Templates HTML
│   ├── 🏠 index.html
│   ├── 👨‍💼 admin_dashboard.html  # Dashboard privado
│   └── ❌ admin_error.html
├── 📁 static/                  # Arquivos estáticos
├── 📁 functions/               # Firebase Functions
└── 📁 logs/                    # Logs do sistema
```

## 🔧 Comandos Úteis

```bash
# Desenvolvimento
python app.py

# Produção
gunicorn --bind 0.0.0.0:8080 app:app

# Testes
./test_system.ps1

# Ver logs
tail -f logs/netscan.log

# Backup analytics
firebase firestore:export gs://seu-bucket/backup
```

## 📞 Suporte

- 📖 **Documentação completa**: `DEPLOYMENT_GUIDE.md`
- 💻 **Instalação Windows**: `INSTALACAO_WINDOWS.md`
- 🐛 **Issues**: Abra uma issue no GitHub
- 📧 **Email**: seu-email@exemplo.com

## 🤝 Contribuições

Contribuições são bem-vindas! Veja `CONTRIBUTING.md` para detalhes.

## 📄 Licença

Este projeto está sob a licença MIT. Veja `LICENSE` para detalhes.

---

## 🎉 **Novo: Contador de Usuários Privado!**

**Agora você pode ver exatamente quantas pessoas visitaram seu NetScan Pro!**

- 📊 **Dashboard exclusivo** apenas para você
- 📈 **Estatísticas em tempo real** 
- 🌍 **Dados por país** e dispositivo
- 🔒 **Totalmente privado** e seguro
- 📱 **Interface responsiva** para mobile

**Acesse:** `http://seu-site.com/admin/dashboard?admin_key=SUA_CHAVE`

---

<div align="center">

**⭐ Se este projeto te ajudou, deixe uma estrela! ⭐**

**🚀 NetScan Pro - Análise de rede profissional com analytics privados 🚀**

</div>
