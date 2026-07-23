# 🚀 Deployment Rápido

## 1️⃣ **Streamlit Cloud** (Recomendado - 1 clique)

```bash
# Apenas faça push para GitHub
git push origin main

# Depois acesse: https://share.streamlit.io
# Clique "New app" e selecione este repositório
```

**Resultado:** Seu app em produção em ~2 minutos
- URL: `https://seu-app.streamlit.app`
- Gratuito e sem infraestrutura

---

## 2️⃣ **Docker Localmente**

```bash
# Build
docker build -t aima-healthcare .

# Run
docker run -p 8501:8501 aima-healthcare

# Acesse: http://localhost:8501
```

---

## 3️⃣ **Railway** (Alternativa com mais recursos)

```bash
# Instale Railway CLI
npm install -g @railway/cli

# Faça login
railway login

# Deploy
railway link
railway up

# URL pública criada automaticamente
```

---

## 📋 Pré-requisitos

- ✅ GitHub account
- ✅ Git configurado localmente
- ✅ Python 3.9+ (para testes locais)

---

## 📖 Documentação Completa

Veja [DEPLOYMENT.md](./DEPLOYMENT.md) para todas as opções de publicação, configurações avançadas e troubleshooting.

---

## ⚡ Quick Links

| Plataforma | Tempo Setup | Custo | Link |
|-----------|-----------|------|------|
| Streamlit Cloud | 2 min | Gratuito | https://streamlit.io/cloud |
| Railway | 5 min | Freemium | https://railway.app |
| Docker + DigitalOcean | 10 min | ~$5/mês | https://www.digitalocean.com |
| AWS Lightsail | 15 min | ~$5/mês | https://lightsail.aws.amazon.com |

---

**Sua app está pronta para ir ao ar! 🎉**
