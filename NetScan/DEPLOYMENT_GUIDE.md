# NetScan Pro - Guia de Deploy Completo

## 🚀 Melhorias Implementadas para Produção

### **Segurança**
- ✅ Middleware de segurança com rate limiting
- ✅ Validação de entrada contra injeções
- ✅ Headers de segurança configurados
- ✅ Sanitização de saída
- ✅ Área administrativa protegida

### **Contador de Usuários Privado**
- ✅ Integração com Firebase Analytics
- ✅ Tracking anônimo de visitas
- ✅ Dashboard administrativo privado
- ✅ Estatísticas detalhadas apenas para admin
- ✅ Dados completamente privados (sem acesso client-side)

### **Performance e Monitoramento**
- ✅ Sistema de logging completo
- ✅ Monitoramento de performance
- ✅ Cache otimizado
- ✅ Containerização com Docker

### **Infraestrutura**
- ✅ Configuração para múltiplos ambientes
- ✅ Docker e Docker Compose
- ✅ Nginx como proxy reverso
- ✅ SSL/TLS configurado

## 📊 Como Acessar as Estatísticas de Usuários

### **Método 1: Dashboard Web (Recomendado)**
```
https://seu-dominio.com/admin/dashboard?admin_key=SEU_ADMIN_SECRET_KEY
```

### **Método 2: API JSON**
```
https://seu-dominio.com/admin/analytics
Header: X-Admin-Key: SEU_ADMIN_SECRET_KEY
```

### **Dados Disponíveis:**
- Total de visitas de todos os tempos
- Visitantes únicos por mês
- Estatísticas diárias (últimos 30 dias)
- Top países por visitas
- Dados de scans realizados
- Gráficos interativos

## 🔧 Setup Rápido

### **1. Configuração Inicial**
```powershell
# Execute o script de setup
.\setup.ps1
```

### **2. Configure o Firebase**
1. Crie um projeto no Firebase Console
2. Ative Firestore Database
3. Baixe o service account key
4. Configure as variáveis no .env

### **3. Configure as Variáveis de Ambiente**
```env
# Copie .env.example para .env e configure:
FIREBASE_PROJECT_ID=seu-projeto-firebase
ADMIN_SECRET_KEY=sua-chave-admin-super-secreta
OPENWEATHER_API_KEY=sua-chave-openweather
```

## 🐳 Deploy com Docker

### **Desenvolvimento**
```powershell
docker-compose up -d
```

### **Produção**
```powershell
docker-compose -f docker-compose.prod.yml up -d
```

## 🔥 Deploy no Firebase

### **1. Instalar Firebase CLI**
```powershell
npm install -g firebase-tools
```

### **2. Fazer Login**
```powershell
firebase login
```

### **3. Deploy**
```powershell
# Para Windows
.\deploy.ps1

# Para Linux/Mac
./deploy.sh
```

## 📱 URLs Importantes

- **Site Principal:** `https://seu-dominio.com`
- **API:** `https://seu-dominio.com/api/<ip>`
- **Admin Dashboard:** `https://seu-dominio.com/admin/dashboard?admin_key=SUA_CHAVE`
- **Export:** `https://seu-dominio.com/export/<ip>`

## 🔒 Segurança das Estatísticas

### **Proteções Implementadas:**
1. **Firestore Rules:** Dados completamente privados no server-side
2. **Admin Key:** Apenas quem tem a chave secreta pode acessar
3. **IP Restriction:** Configure IPs permitidos no Nginx
4. **Anonimização:** IPs são hasheados, dados pessoais não são coletados
5. **HTTPS Only:** Todas as comunicações criptografadas

### **Dados Coletados (Anonimizados):**
- Hash do IP (não o IP real)
- User-Agent (limitado a 200 chars)
- Referrer (limitado a 200 chars)
- País/região (se detectado)
- Timestamp da visita
- Tipo de scan realizado

### **Dados NÃO Coletados:**
- IPs reais (apenas hash)
- Informações pessoais
- Histórico detalhado de navegação
- Dados sensíveis

## 🚀 Performance em Produção

### **Otimizações Incluídas:**
- Nginx como proxy reverso com cache
- Rate limiting por IP
- Compressão gzip
- Headers de cache otimizados
- Containerização eficiente
- Logging estruturado

### **Monitoramento:**
- Logs de aplicação (`logs/netscan.log`)
- Logs de erro (`logs/errors.log`)
- Logs de segurança (`logs/security.log`)
- Logs de analytics (`logs/analytics.log`)

## 🛠️ Troubleshooting

### **Firebase não inicializa:**
1. Verifique se o service account key está correto
2. Confirme as permissões do Firestore
3. Verifique as variáveis de ambiente

### **Admin dashboard não carrega:**
1. Confirme a ADMIN_SECRET_KEY no .env
2. Verifique se o Firebase está configurado
3. Teste a URL com a chave correta

### **Estatísticas não aparecem:**
1. Verifique se há visitas sendo registradas nos logs
2. Confirme a configuração do Firestore
3. Teste a conexão com Firebase

## 📞 Suporte

Para dúvidas sobre implementação:
1. Verifique os logs em `/logs/`
2. Teste as URLs das APIs
3. Confirme as configurações do Firebase

---

**🎉 Parabéns! Seu NetScan Pro está pronto para produção com tracking completo de usuários!**
