# CAROL - AI Maturity Assessment

## Descrição do projeto

Avaliação de maturidade em IA com modelo responsável, guias de implementação e material prático para conduzir assessorias e auditorias.

Este repositório reúne conteúdo e orientações sobre princípios responsáveis, governança, dados, privacidade, design, implementação, verificação e operações de IA. O objetivo é ajudar organizações a avaliar, melhorar e formalizar a maturidade de seus processos e sistemas de inteligência artificial.

## App público

A versão pública do app está disponível em:

https://owasp-aima-healthcare.streamlit.app/

Qualquer pessoa pode acessar este link no navegador para usar a aplicação.

## Project description

With the growing interest and adoption of AI technologies, it’s critical to establish a framework that organizations can use to measure and enhance their AI maturity levels.

In recent months, several AI Maturity Models have emerged, including the MITRE AI Framework, which highlights the need for structured AI assessments. Building on this momentum, we are developing the OWASP AI Maturity Assessment (AIMA), using the Software Assurance Maturity Model (SAMM) as a foundation.

Mission Statement: The OWASP AI Maturity Assessment (AIMA) aims to be the premier framework that enables organizations to assess, analyze, and improve the security and responsible usage of AI technologies. Like OWASP SAMM, AIMA will be technology and process agnostic, delivering a risk-driven approach that guides organizations in managing AI systems throughout their entire lifecycle.

## Como usar

1. Acesse o app público pelo link acima.
2. Navegue pelos domínios de avaliação de maturidade: Responsabilidade, Governança, Dados, Privacidade, Design, Implementação, Verificação e Operações.
3. Use as worksheets para registrar análises e recomendações.

## Privacidade e segurança

- Este app não usa banco de dados nem armazena dados em um servidor: nome da organização, respostas e status de conformidade existem apenas na sessão do navegador (`st.session_state`) enquanto a aba estiver aberta.
- Nenhum dado é enviado a terceiros; `gatherUsageStats` está desativado (`.streamlit/config.toml`).
- Exports (Excel/JSON) são gerados sob demanda e baixados diretamente pelo navegador do usuário — nada fica retido no servidor.
- Em produção, `client.showErrorDetails = "none"` evita expor stack traces internos a quem usa o app.
- A **Análise Automática de Repositório (Beta)** só faz chamadas de leitura à API pública do GitHub (`api.github.com`), nunca busca uma URL arbitrária informada pelo usuário (a URL é validada e só o `owner/repo` extraído é usado), e nunca executa código do repositório analisado — apenas busca padrões de texto em nomes de arquivos e em README/SECURITY.md.
- Para reportar uma vulnerabilidade, veja [SECURITY.md](SECURITY.md).

## Implantar sua própria instância (Streamlit Community Cloud)

1. Faça um fork deste repositório para sua conta do GitHub.
2. Em [share.streamlit.io](https://share.streamlit.io), clique em **New app** e aponte para `app.py` na branch `main`.
3. Em **Settings → Sharing**, confirme que a visibilidade está definida como **"This app is public"** (e não restrita a e-mails específicos) — só assim qualquer pessoa consegue acessar o link sem login.
4. O deploy usa `requirements.txt` (dependências do app) automaticamente; `requirements-scripts.txt` é usado apenas pelo script interno de geração de PDF da documentação e não é necessário para o app público.

### App "dormindo" (sleep) no plano gratuito

No plano gratuito do Streamlit Community Cloud, o app entra em modo de espera após um período sem visitas — o primeiro visitante vê uma tela pedindo para "acordar" o app (isso **não é um problema de permissão/login**, é o comportamento normal do free tier). Este repositório inclui `.github/workflows/keep_alive.yml`, que faz um ping automático no app a cada 10 minutos para reduzir a chance de visitantes verem essa tela.

## Contribuição

Para contribuir:

1. Faça um fork deste repositório ou clone diretamente se você tiver acesso.
2. Edite o conteúdo em `source/latest` ou `source/v1`.
3. Abra um pull request com as mudanças.

## Meetings & Collaboration
### Google Calendar
* [View team calendar](https://calendar.google.com/calendar/u/1/embed?src=c_458f602f307256f02c38571b298cc5c093eba023073d80f013953482e051312a@group.calendar.google.com&ctz=Europe/Berlin&csspa=1)
 * [iCal Link](https://calendar.google.com/calendar/ical/c_458f602f307256f02c38571b298cc5c093eba023073d80f013953482e051312a%40group.calendar.google.com/public/basic.ics)

### Recurring Meetings
- **Bi-weekly Brainstorming**: Every 2 Wednesday at 6:00 – 7:00pm CET ([Google Meet Link](https://meet.google.com/sek-zwkd-woc))

### Slack Channel  
- Join the Discussion on the OWASP Slack Channel [#project-aima](https://owasp.slack.com/archives/C089K6KFZMG)

## Start contributing
* [CONTENT](https://github.com/OWASP/www-project-ai-maturity-assessment/tree/main/source/latest)

Here is the official [OWASP AIMA project page](https://owasp.org/www-project-ai-maturity-assessment/)

---

## Mobile app frontend

A simple Expo-based mobile frontend for the OWASP AIMA Healthcare project was added in `mobile-app/`. It includes:

- A home screen with app title and description
- Section cards for the main maturity domains
- A button to open the public Streamlit app

To run locally:

```bash
cd mobile-app
npm install
npx expo start
```
