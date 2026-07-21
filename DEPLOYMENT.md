# 📱 Guia de Publicação - OWASP AIMA Healthcare

Seu aplicativo Streamlit já está pronto para ser publicado! Escolha a plataforma que melhor atende suas necessidades.

---

## 🚀 Opção 1: Streamlit Cloud (Recomendado - Gratuito)

A forma mais simples e rápida de publicar seu app.

### Passo a passo:

1. **Commit e push seu código para GitHub**
   ```bash
   git add .
   git commit -m "Prepare app for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Crie uma conta em Streamlit Cloud**
   - Acesse: https://streamlit.io/cloud
   - Clique em "Sign up with GitHub"
   - Autorize a conexão com seu GitHub

3. **Implante seu app**
   - Clique em "New app" em https://share.streamlit.io
   - Selecione seu repositório: `anacarolRicciardi/OWASP_AIMA_Healthcare`
   - Branch: `main`
   - Main file path: `app.py`
   - Clique em "Deploy"

4. **Seu app estará disponível em:**
   ```
   https://owasp-aima-healthcare.streamlit.app
   ```
   (O nome exato será gerado automaticamente)

### Benefícios:
✅ Gratuito  
✅ URL pública automática  
✅ HTTPS incluído  
✅ Redeploy automático ao fazer push  
✅ Sem configuração de servidor  
✅ Ideal para prototipagem e demos  

### Limitações:
- Recursos limitados (1 GB RAM, 1 CPU)
- Armazenamento de sessão em memória (não persistente)
- Bom para até ~50 usuários simultâneos

---

## 🐳 Opção 2: Docker + Heroku/Railway/Render (Gratuito-Pago)

Para mais controle e escalabilidade.

### Criar Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Criar .dockerignore:
```
.git
.gitignore
__pycache__
*.pyc
.DS_Store
.env
```

### Deploy em Railway (Recomendado):

1. Acesse: https://railway.app
2. Clique em "New Project" → "Deploy from GitHub"
3. Autorize e selecione `anacarolRicciardi/OWASP_AIMA_Healthcare`
4. Railway detectará o Dockerfile automaticamente
5. Configure a variável de ambiente:
   ```
   PORT=8501
   ```
6. Deploy completo em ~2-3 minutos

**URL do seu app:** `https://seu-projeto.railway.app`

---

## ☁️ Opção 3: Deployment em Cloud Provider (Mais robusto)

### Google Cloud Run:
```bash
# 1. Fazer login no Google Cloud
gcloud auth login

# 2. Fazer build e deploy
gcloud run deploy owasp-aima-healthcare \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### AWS Lightsail:
1. Crie uma instância Lightsail (Linux + Docker)
2. SSH e clone o repositório
3. Execute: `docker build -t aima . && docker run -p 8501:8501 aima`

### DigitalOcean App Platform:
1. Conecte seu GitHub
2. Selecione o repositório
3. Configure como "Streamlit App"
4. Deploy automático

---

## 🔧 Configuração de Produção

### Adicionar variáveis de ambiente seguras:

Crie um arquivo `.streamlit/secrets.toml` (não commitado):
```toml
[database]
url = "postgresql://..."

[api]
key = "seu-api-key"
```

### Melhorar performance:

Adicione ao `requirements.txt`:
```
gunicorn>=21.0.0
python-dotenv>=1.0.0
```

### Monitoramento:

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

---

## 🌐 Configurar domínio customizado

### Para Streamlit Cloud:
1. Acesse https://share.streamlit.io/
2. Vá em "Settings" do seu app
3. Adicione seu domínio personalizado

### Para Railway/Heroku:
1. Compre domínio em: Namecheap, GoDaddy, etc.
2. Configure os registros DNS (CNAME ou A)
3. Aponte para o seu app

---

## ✅ Checklist de Publicação

- [ ] Todos os requirements.txt incluídos
- [ ] Variáveis sensíveis em `.streamlit/secrets.toml`
- [ ] `.gitignore` configurado corretamente
- [ ] README.md com instruções de uso
- [ ] App testado localmente: `streamlit run app.py`
- [ ] Git push final: `git push origin main`
- [ ] Plataforma escolhida e configurada
- [ ] URL pública funcionando
- [ ] Compartilhar URL com stakeholders

---

## 🆘 Troubleshooting

### "ModuleNotFoundError"
→ Adicione todas as dependências ao `requirements.txt`

### "AttributeError: module 'streamlit' has no attribute..."
→ Atualize Streamlit: `pip install --upgrade streamlit`

### Sessão não persiste após reload
→ Use `@st.cache_data` e `@st.cache_resource` para cache

### Lentidão no carregamento
→ Aumente recursos ou use Streamlit Cloud Premium

---

## 📊 Próximos passos

1. **Análise de dados**: Integre banco de dados para armazenar avaliações
2. **Autenticação**: Adicione login com Google/GitHub
3. **Relatórios em PDF**: Use `reportlab` ou `weasyprint`
4. **API RESTful**: Exponha dados via FastAPI/Flask
5. **Mobile**: Empacote com React Native/Flutter

---

**Precisa de ajuda? Abra uma issue no GitHub ou consulte a documentação:**
- 📖 [Streamlit Docs](https://docs.streamlit.io/)
- 🐳 [Docker Docs](https://docs.docker.com/)
- 🚀 [Railway Docs](https://docs.railway.app/)
