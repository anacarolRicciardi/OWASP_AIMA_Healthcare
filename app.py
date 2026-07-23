# -*- coding: utf-8 -*-
"""
OWASP AI Maturity Assessment (AIMA) - Healthcare Edition
Streamlit application for assessing AI maturity in medical laboratories and healthcare organizations.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import io
import re
import base64
import requests

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OWASP AIMA Healthcare",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }
.metric-card {
    background: #f0f4f8; border-radius: 8px; padding: 1rem;
    border-left: 4px solid #1976D2; margin-bottom: .5rem;
}
.reg-card {
    background: #fff8e1; border-radius: 8px; padding: 1rem;
    border-left: 4px solid #f57c00; margin-bottom: .5rem;
}
.level-badge {
    display: inline-block; padding: 2px 10px; border-radius: 12px;
    font-size: .8rem; font-weight: 600; margin-left: 8px;
}
.l0  { background:#ffcdd2; color:#b71c1c; }
.l1  { background:#ffe0b2; color:#e65100; }
.l2  { background:#fff9c4; color:#f57f17; }
.l3  { background:#c8e6c9; color:#1b5e20; }
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ─────────────────────────────────────────────────────
def _init():
    defaults = {
        "lang": "pt",
        "org": {"name": "", "type": "Laboratório Médico", "jurisdictions": ["🇧🇷 Brasil"], "date": str(datetime.today().date())},
        "scores": {},       # {domain: {practice: {stream: {level: bool}}}}
        "compliance": {},   # {jurisdiction: {reg: status}}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ── Translations ───────────────────────────────────────────────────────────────
T = {
    "pt": {
        "app_title": "OWASP AIMA Healthcare",
        "app_sub": "Avaliação de Maturidade de IA para Saúde",
        "menu_home": "🏠 Início",
        "menu_assess": "📋 Avaliação AIMA",
        "menu_compliance": "⚖️ Conformidade Regulatória",
        "menu_reports": "📊 Relatórios",
        "menu_settings": "⚙️ Configurações",
        "lang_label": "Idioma",
        "org_name": "Nome da Organização",
        "org_type": "Tipo de Organização",
        "save": "💾 Salvar",
        "saved": "✅ Salvo com sucesso!",
        "maturity_labels": ["Não iniciado", "Nível 1 – Inicial", "Nível 2 – Gerenciado", "Nível 3 – Otimizado"],
        "yes": "Sim", "no": "Não",
        "score": "Pontuação",
        "level": "Nível",
        "domain": "Domínio",
        "practice": "Prática",
        "status": "Status",
        "jurisdiction": "Jurisdição",
        "regulation": "Regulação",
        "priority": "Prioridade",
        "penalty": "Penalidade",
        "export_excel": "📥 Exportar Excel",
        "export_json": "📥 Exportar JSON",
        "generate_report": "📄 Gerar Relatório",
        "not_started": "Não iniciado",
        "in_progress": "Em progresso",
        "compliant": "Conforme",
        "non_compliant": "Não conforme",
        "menu_auto": "🤖 Análise Automática",
        "auto_header": "Análise Automática de Repositório (Beta)",
        "auto_intro": "Cole a URL de um repositório **público** no GitHub. O app busca sinais visíveis no repositório (CI/CD, testes, SECURITY.md, model cards, menções a privacidade/viés/monitoramento) e **sugere** respostas para revisão manual — não é uma pontuação final. Domínios de governança e processo (comitês de ética, políticas internas) não podem ser verificados apenas pelo código. Sujeito ao limite de requisições da API pública do GitHub.",
        "auto_url_label": "URL do repositório",
        "auto_button": "🔎 Analisar repositório",
        "auto_evidence_header": "Sinais encontrados",
        "auto_no_evidence": "Nenhum sinal relevante foi encontrado neste repositório.",
        "auto_apply_button": "✅ Aplicar sugestões à avaliação",
        "auto_suggestions_ready": "sugestões prontas para aplicar (não sobrescrevem respostas já marcadas).",
        "auto_applied_msg": "respostas pré-preenchidas. Revise-as na página Avaliação AIMA.",
        "auto_invalid_url": "URL inválida. Use o formato https://github.com/owner/repo",
    },
    "en": {
        "app_title": "OWASP AIMA Healthcare",
        "app_sub": "AI Maturity Assessment for Healthcare",
        "menu_home": "🏠 Home",
        "menu_assess": "📋 AIMA Assessment",
        "menu_compliance": "⚖️ Regulatory Compliance",
        "menu_reports": "📊 Reports",
        "menu_settings": "⚙️ Settings",
        "lang_label": "Language",
        "org_name": "Organization Name",
        "org_type": "Organization Type",
        "save": "💾 Save",
        "saved": "✅ Saved successfully!",
        "maturity_labels": ["Not started", "Level 1 – Initial", "Level 2 – Managed", "Level 3 – Optimized"],
        "yes": "Yes", "no": "No",
        "score": "Score",
        "level": "Level",
        "domain": "Domain",
        "practice": "Practice",
        "status": "Status",
        "jurisdiction": "Jurisdiction",
        "regulation": "Regulation",
        "priority": "Priority",
        "penalty": "Penalty",
        "export_excel": "📥 Export Excel",
        "export_json": "📥 Export JSON",
        "generate_report": "📄 Generate Report",
        "not_started": "Not started",
        "in_progress": "In progress",
        "compliant": "Compliant",
        "non_compliant": "Non-compliant",
        "menu_auto": "🤖 Automated Scan",
        "auto_header": "Automated Repository Scan (Beta)",
        "auto_intro": "Paste the URL of a **public** GitHub repository. The app looks for visible signals in the repo (CI/CD, tests, SECURITY.md, model cards, mentions of privacy/bias/monitoring) and **suggests** answers for manual review — this is not a final score. Governance/process domains (ethics committees, internal policies) cannot be verified from code alone. Subject to the public GitHub API rate limit.",
        "auto_url_label": "Repository URL",
        "auto_button": "🔎 Scan repository",
        "auto_evidence_header": "Signals found",
        "auto_no_evidence": "No relevant signals were found in this repository.",
        "auto_apply_button": "✅ Apply suggestions to assessment",
        "auto_suggestions_ready": "suggestions ready to apply (won't overwrite answers already checked).",
        "auto_applied_msg": "answers pre-filled. Review them on the AIMA Assessment page.",
        "auto_invalid_url": "Invalid URL. Use the format https://github.com/owner/repo",
    },
    "es": {
        "app_title": "OWASP AIMA Healthcare",
        "app_sub": "Evaluación de Madurez de IA para Salud",
        "menu_home": "🏠 Inicio",
        "menu_assess": "📋 Evaluación AIMA",
        "menu_compliance": "⚖️ Conformidad Regulatoria",
        "menu_reports": "📊 Informes",
        "menu_settings": "⚙️ Configuración",
        "lang_label": "Idioma",
        "org_name": "Nombre de la Organización",
        "org_type": "Tipo de Organización",
        "save": "💾 Guardar",
        "saved": "✅ ¡Guardado con éxito!",
        "maturity_labels": ["No iniciado", "Nivel 1 – Inicial", "Nivel 2 – Gestionado", "Nivel 3 – Optimizado"],
        "yes": "Sí", "no": "No",
        "score": "Puntuación",
        "level": "Nivel",
        "domain": "Dominio",
        "practice": "Práctica",
        "status": "Estado",
        "jurisdiction": "Jurisdicción",
        "regulation": "Regulación",
        "priority": "Prioridad",
        "penalty": "Penalidad",
        "export_excel": "📥 Exportar Excel",
        "export_json": "📥 Exportar JSON",
        "generate_report": "📄 Generar Informe",
        "not_started": "No iniciado",
        "in_progress": "En progreso",
        "compliant": "Conforme",
        "non_compliant": "No conforme",
        "menu_auto": "🤖 Análisis Automático",
        "auto_header": "Análisis Automático de Repositorio (Beta)",
        "auto_intro": "Pegue la URL de un repositorio **público** de GitHub. La app busca señales visibles en el repositorio (CI/CD, tests, SECURITY.md, model cards, menciones a privacidad/sesgo/monitoreo) y **sugiere** respuestas para revisión manual — no es una puntuación final. Los dominios de gobernanza y proceso (comités de ética, políticas internas) no pueden verificarse solo con el código. Sujeto al límite de solicitudes de la API pública de GitHub.",
        "auto_url_label": "URL del repositorio",
        "auto_button": "🔎 Analizar repositorio",
        "auto_evidence_header": "Señales encontradas",
        "auto_no_evidence": "No se encontraron señales relevantes en este repositorio.",
        "auto_apply_button": "✅ Aplicar sugerencias a la evaluación",
        "auto_suggestions_ready": "sugerencias listas para aplicar (no sobrescriben respuestas ya marcadas).",
        "auto_applied_msg": "respuestas prellenadas. Revíselas en la página Evaluación AIMA.",
        "auto_invalid_url": "URL inválida. Use el formato https://github.com/owner/repo",
    },
}

def t(key):
    return T[st.session_state.lang].get(key, key)

# ── OWASP AIMA Domain Data ─────────────────────────────────────────────────────
DOMAINS = {
    "Responsible AI": {
        "icon": "🤝",
        "practices": {
            "Ethical & Societal Impact": {
                "L1": {
                    "A": "Existe consciência inicial sobre implicações éticas e sociais do uso de IA na organização?",
                    "B": "Há discussões informais sobre o impacto social dos sistemas de IA desenvolvidos/usados?"
                },
                "L2": {
                    "A": "Avaliações de impacto ético são realizadas formalmente para sistemas de IA?",
                    "B": "Há políticas documentadas sobre o impacto social e ético da IA?"
                },
                "L3": {
                    "A": "O impacto ético é continuamente monitorado e integrado ao ciclo de vida da IA?",
                    "B": "Há um comitê ou processo formal de revisão ética para todos os projetos de IA?"
                }
            },
            "Transparency & Explainability": {
                "L1": {
                    "A": "Há consciência básica da necessidade de explicabilidade nos sistemas de IA?",
                    "B": "Existe documentação informal sobre como as decisões de IA são tomadas?"
                },
                "L2": {
                    "A": "Processos formais de explicabilidade estão estabelecidos para sistemas críticos de IA?",
                    "B": "A transparência das decisões de IA é comunicada regularmente aos stakeholders?"
                },
                "L3": {
                    "A": "Mecanismos de explicabilidade são continuamente aprimorados e auditados?",
                    "B": "A transparência é um requisito integrado em todos os sistemas de IA?"
                }
            },
            "Fairness & Bias": {
                "L1": {
                    "A": "Há consciência dos riscos de viés nos dados e modelos de IA?",
                    "B": "Alguma análise informal de viés é realizada antes do deployment de modelos?"
                },
                "L2": {
                    "A": "Avaliações formais de fairness e viés são conduzidas em datasets e modelos?",
                    "B": "Estratégias documentadas de mitigação de viés estão implementadas?"
                },
                "L3": {
                    "A": "O monitoramento de fairness é contínuo e integrado ao pipeline de ML?",
                    "B": "Auditorias externas de fairness são realizadas periodicamente?"
                }
            },
        }
    },
    "Governance": {
        "icon": "🏛️",
        "practices": {
            "Strategy & Metrics": {
                "L1": {
                    "A": "Há uma estratégia de IA documentada, mesmo que informalmente?",
                    "B": "Alguma métrica relacionada a iniciativas de IA é rastreada informalmente?"
                },
                "L2": {
                    "A": "A estratégia de IA foi formalmente definida e comunicada aos stakeholders?",
                    "B": "Métricas definidas são revisadas regularmente e comunicadas na organização?"
                },
                "L3": {
                    "A": "A estratégia de IA está integrada à estratégia de negócios mais ampla e refinada iterativamente?",
                    "B": "As métricas são sistematicamente analisadas para impulsionar melhorias e decisões?"
                }
            },
            "Policy & Compliance": {
                "L1": {
                    "A": "Há consciência ou política informal sobre o uso de IA na organização?",
                    "B": "Há consciência básica das necessidades de conformidade relevantes para IA (LGPD, GDPR, etc.)?"
                },
                "L2": {
                    "A": "Uma política formal de IA foi estabelecida e comunicada a todos os stakeholders?",
                    "B": "Os requisitos de conformidade são identificados, documentados e revisados regularmente?"
                },
                "L3": {
                    "A": "A política de IA é aplicada consistentemente e revisada regularmente?",
                    "B": "A gestão de conformidade é aplicada através de mecanismos formais nas operações diárias?"
                }
            },
            "Education & Awareness": {
                "L1": {
                    "A": "Há treinamento informal ou consciência geral sobre riscos de segurança de IA?",
                    "B": "A comunicação sobre riscos de segurança de IA é esporádica ou ad-hoc?"
                },
                "L2": {
                    "A": "Programas formais de treinamento em segurança de IA estão estabelecidos?",
                    "B": "Há comunicação regular sobre boas práticas de segurança de IA em toda a organização?"
                },
                "L3": {
                    "A": "Os programas de treinamento em segurança de IA são atualizados regularmente e obrigatórios?",
                    "B": "Há uma cultura estabelecida de comunicação proativa sobre segurança de IA?"
                }
            },
        }
    },
    "Data Management": {
        "icon": "🗄️",
        "practices": {
            "Data Quality & Integrity": {
                "L1": {
                    "A": "Há consciência básica sobre qualidade e integridade dos dados usados em IA?",
                    "B": "Validações informais de dados são realizadas antes de usar dados em modelos de IA?"
                },
                "L2": {
                    "A": "Padrões formais de qualidade de dados estão definidos e aplicados?",
                    "B": "Processos de validação de integridade de dados são regularmente executados?"
                },
                "L3": {
                    "A": "A qualidade dos dados é continuamente monitorada e aprimorada?",
                    "B": "Há rastreabilidade completa de linhagem de dados para todos os sistemas de IA?"
                }
            },
            "Data Governance & Accountability": {
                "L1": {
                    "A": "Existe responsabilidade informal sobre dados usados em sistemas de IA?",
                    "B": "Há documentação básica sobre fontes e tipos de dados usados?"
                },
                "L2": {
                    "A": "Um framework formal de governança de dados está estabelecido?",
                    "B": "Papéis e responsabilidades para dados de IA estão claramente definidos?"
                },
                "L3": {
                    "A": "A governança de dados é proativamente gerenciada com auditorias regulares?",
                    "B": "Há um catálogo completo de dados com metadados e propriedade documentada?"
                }
            },
            "Data Training": {
                "L1": {
                    "A": "Há consciência básica dos riscos associados a dados de treinamento enviesados?",
                    "B": "Alguma revisão informal de datasets de treinamento é realizada?"
                },
                "L2": {
                    "A": "Processos formais de curadoria e validação de dados de treinamento existem?",
                    "B": "Documentação de datasets de treinamento está estabelecida?"
                },
                "L3": {
                    "A": "O monitoramento de qualidade dos dados de treinamento é contínuo?",
                    "B": "Há processos de re-treinamento com novos dados validados continuamente?"
                }
            },
        }
    },
    "Privacy": {
        "icon": "🔒",
        "practices": {
            "Data Minimization": {
                "L1": {
                    "A": "Há consciência do princípio de minimização de dados para IA?",
                    "B": "Alguma prática informal de limitação de coleta de dados existe?"
                },
                "L2": {
                    "A": "Políticas formais de minimização de dados estão implementadas?",
                    "B": "Processos de anonimização/pseudonimização estão estabelecidos para dados de IA?"
                },
                "L3": {
                    "A": "A minimização de dados é revisada continuamente e auditada?",
                    "B": "Técnicas avançadas como privacy-preserving ML (federated learning, etc.) são avaliadas?"
                }
            },
            "Privacy by Design": {
                "L1": {
                    "A": "Privacy by Design é considerado informalmente no desenvolvimento de sistemas de IA?",
                    "B": "Há consciência básica dos requisitos de LGPD/GDPR para sistemas de IA?"
                },
                "L2": {
                    "A": "Privacy by Design está formalmente integrado ao ciclo de desenvolvimento de IA?",
                    "B": "Avaliações de impacto de privacidade (DPIA) são realizadas para sistemas de IA?"
                },
                "L3": {
                    "A": "Privacy by Design é um requisito integrado e auditado em todos os sistemas de IA?",
                    "B": "DPIAs são realizadas proativamente e os resultados integram melhorias contínuas?"
                }
            },
            "User Control & Transparency": {
                "L1": {
                    "A": "Há consciência básica dos direitos dos titulares de dados (acesso, exclusão, etc.)?",
                    "B": "Algum mecanismo informal de consentimento existe para uso de dados em IA?"
                },
                "L2": {
                    "A": "Mecanismos formais para exercício dos direitos dos titulares estão implementados?",
                    "B": "O consentimento informado para uso de dados em IA é obtido formalmente?"
                },
                "L3": {
                    "A": "Há processos automáticos de atendimento a direitos de titulares de dados?",
                    "B": "Sistemas de gestão de consentimento estão integrados aos sistemas de IA?"
                }
            },
        }
    },
    "Design": {
        "icon": "🎨",
        "practices": {
            "Threat Assessment": {
                "L1": {
                    "A": "Há consciência básica ou identificação informal de ameaças específicas a sistemas de IA?",
                    "B": "Estratégias informais de mitigação de ameaças são ocasionalmente discutidas?"
                },
                "L2": {
                    "A": "Ameaças são sistematicamente identificadas e documentadas para sistemas de IA?",
                    "B": "Estratégias de mitigação documentadas são desenvolvidas e periodicamente revisadas?"
                },
                "L3": {
                    "A": "Avaliação abrangente de ameaças é realizada consistentemente e integrada ao ciclo de IA?",
                    "B": "Estratégias proativas e abrangentes de mitigação são continuamente implementadas?"
                }
            },
            "Security Architecture": {
                "L1": {
                    "A": "Há consciência inicial de segurança no deployment de modelos de IA?",
                    "B": "Verificações informais de conformidade arquitetural são ocasionalmente realizadas?"
                },
                "L2": {
                    "A": "Procedimentos formais para deployment seguro de modelos de IA estão estabelecidos?",
                    "B": "Revisões regulares de conformidade arquitetural são sistematicamente conduzidas?"
                },
                "L3": {
                    "A": "O deployment seguro é continuamente refinado e totalmente integrado?",
                    "B": "A conformidade arquitetural abrangente é proativamente gerenciada e auditada?"
                }
            },
            "Security Requirements": {
                "L1": {
                    "A": "Requisitos de segurança são informalmente identificados ou documentados esporadicamente?",
                    "B": "Processos informais de verificação são ocasionalmente aplicados aos requisitos?"
                },
                "L2": {
                    "A": "Requisitos de segurança estão formalmente documentados e comunicados?",
                    "B": "Procedimentos sistemáticos de verificação são regularmente conduzidos?"
                },
                "L3": {
                    "A": "Requisitos de segurança são continuamente melhorados e integrados em todos os projetos?",
                    "B": "Mecanismos abrangentes de verificação são consistentemente aplicados e auditados?"
                }
            },
        }
    },
    "Implementation": {
        "icon": "⚙️",
        "practices": {
            "Secure Build": {
                "L1": {
                    "A": "Há consciência de segurança básica no desenvolvimento de sistemas de IA?",
                    "B": "Revisões informais de segurança de código são ocasionalmente realizadas?"
                },
                "L2": {
                    "A": "Práticas seguras de desenvolvimento são formalmente estabelecidas para IA?",
                    "B": "Revisões de segurança de código são regularmente realizadas?"
                },
                "L3": {
                    "A": "Práticas seguras de build são continuamente refinadas e integradas ao CI/CD?",
                    "B": "Análise automatizada de segurança de código é integrada ao pipeline de desenvolvimento?"
                }
            },
            "Secure Deployment": {
                "L1": {
                    "A": "Há consciência básica das considerações de segurança no deployment de modelos?",
                    "B": "Verificações informais de segurança são realizadas antes do deployment?"
                },
                "L2": {
                    "A": "Procedimentos formais de deployment seguro estão estabelecidos?",
                    "B": "Verificações sistemáticas de segurança são realizadas antes de cada deployment?"
                },
                "L3": {
                    "A": "O deployment seguro é automatizado e continuamente monitorado?",
                    "B": "Há reversão automática em caso de falhas de segurança detectadas pós-deployment?"
                }
            },
            "Defect Management": {
                "L1": {
                    "A": "Defeitos de segurança são informalmente rastreados?",
                    "B": "Há algum processo informal de resposta a incidentes de segurança?"
                },
                "L2": {
                    "A": "Um processo formal de gerenciamento de defeitos de segurança existe?",
                    "B": "SLAs para resolução de vulnerabilidades de segurança estão definidos?"
                },
                "L3": {
                    "A": "O gerenciamento de defeitos é proativo com métricas de melhoria contínua?",
                    "B": "Há integração com threat intelligence para antecipar novos defeitos?"
                }
            },
        }
    },
    "Verification": {
        "icon": "✅",
        "practices": {
            "Security Testing": {
                "L1": {
                    "A": "Algum teste de segurança informal é realizado em sistemas de IA?",
                    "B": "Há conscientização sobre a necessidade de testes adversariais em modelos de IA?"
                },
                "L2": {
                    "A": "Testes de segurança formais são regularmente realizados em sistemas de IA?",
                    "B": "Testes adversariais (adversarial ML) são incluídos nos processos de verificação?"
                },
                "L3": {
                    "A": "Testes de segurança abrangentes são continuamente realizados e automatizados?",
                    "B": "Testes de red team em sistemas de IA são realizados periodicamente?"
                }
            },
            "Requirement-Based Testing": {
                "L1": {
                    "A": "Testes são informalmente ligados a requisitos de segurança?",
                    "B": "Há alguma cobertura informal de requisitos nos testes?"
                },
                "L2": {
                    "A": "Testes baseados em requisitos de segurança estão formalmente estabelecidos?",
                    "B": "A cobertura de requisitos de segurança nos testes é regularmente medida?"
                },
                "L3": {
                    "A": "Testes baseados em requisitos são abrangentes e automatizados?",
                    "B": "100% dos requisitos críticos de segurança têm cobertura de teste rastreável?"
                }
            },
            "Architecture Assessment": {
                "L1": {
                    "A": "Revisões informais da arquitetura de segurança de IA são realizadas?",
                    "B": "Há consciência básica de potenciais vulnerabilidades arquiteturais em IA?"
                },
                "L2": {
                    "A": "Avaliações formais de arquitetura de segurança são realizadas regularmente?",
                    "B": "As avaliações de arquitetura incluem análise de vetores de ataque específicos de IA?"
                },
                "L3": {
                    "A": "Avaliações de arquitetura são realizadas continuamente e com terceiros independentes?",
                    "B": "Os resultados das avaliações impulsionam melhorias contínuas na arquitetura?"
                }
            },
        }
    },
    "Operations": {
        "icon": "📡",
        "practices": {
            "Incident Management": {
                "L1": {
                    "A": "Há um processo básico para reportar incidentes relacionados a sistemas de IA?",
                    "B": "Incidentes de IA são informalmente documentados?"
                },
                "L2": {
                    "A": "Um plano formal de resposta a incidentes de IA está estabelecido?",
                    "B": "Há procedimentos de notificação de breach/incidente conforme LGPD/GDPR?"
                },
                "L3": {
                    "A": "A gestão de incidentes de IA é integrada ao SOC e continuamente melhorada?",
                    "B": "Simulações de incidentes (tabletop exercises) de IA são realizadas regularmente?"
                }
            },
            "Event Management": {
                "L1": {
                    "A": "Algum monitoramento básico de eventos de sistemas de IA existe?",
                    "B": "Logs de decisões de IA são coletados informalmente?"
                },
                "L2": {
                    "A": "Um sistema formal de monitoramento e logging de eventos de IA está estabelecido?",
                    "B": "Alertas para eventos anômalos em sistemas de IA estão configurados?"
                },
                "L3": {
                    "A": "O monitoramento de eventos de IA é contínuo, automatizado e com alertas em tempo real?",
                    "B": "Análise comportamental de modelos de IA em produção é realizada continuamente?"
                }
            },
            "Operational Management": {
                "L1": {
                    "A": "Há alguma documentação básica sobre operação dos sistemas de IA?",
                    "B": "Procedimentos informais de manutenção e atualização de modelos existem?"
                },
                "L2": {
                    "A": "Processos formais de gestão operacional de sistemas de IA estão estabelecidos?",
                    "B": "Há um processo formal de re-validação após atualizações de modelos?"
                },
                "L3": {
                    "A": "A gestão operacional é proativa com MLOps maduro e integrado?",
                    "B": "Há monitoramento de drift de modelo com retreinamento automático quando necessário?"
                }
            },
        }
    },
}

# ── Regulatory Data ────────────────────────────────────────────────────────────
REGULATIONS = {
    "🇧🇷 Brasil": {
        "color": "#009c3b",
        "regs": {
            "LGPD (Lei 13.709/2018)": {
                "desc": "Lei Geral de Proteção de Dados Pessoais",
                "priority": "Crítica",
                "penalty": "Até R$ 50 milhões por infração ou 2% do faturamento",
                "scope": "Toda IA que processa dados pessoais de pacientes",
                "checklist": [
                    "Mapeamento de dados pessoais processados pela IA",
                    "Base legal definida para cada processamento",
                    "DPIA (Relatório de Impacto) realizado",
                    "DPO (Encarregado) designado e registrado na ANPD",
                    "Contratos com fornecedores de IA adequados",
                    "Processo de atendimento aos direitos dos titulares",
                    "Política de retenção e exclusão de dados",
                    "Notificação de incidentes à ANPD em 72h",
                ],
                "links": ["https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm", "https://www.gov.br/anpd"]
            },
            "CFM 2.228/2019": {
                "desc": "Regulamentação do uso de IA na medicina",
                "priority": "Crítica",
                "penalty": "Suspensão do registro médico / sanções éticas",
                "scope": "Sistemas de IA utilizados em diagnóstico e decisão clínica",
                "checklist": [
                    "Médico responsável identificado para decisões de IA",
                    "IA como ferramenta de apoio (não substituição) ao médico",
                    "Validação clínica documentada do sistema",
                    "Consentimento do paciente para uso de IA",
                    "Registro de auditoria das decisões assistidas por IA",
                ],
                "links": ["https://www.cfm.org.br/index.php?topic=6"]
            },
            "ANVISA RDC 658/2021": {
                "desc": "Software como Dispositivo Médico (SaMD)",
                "priority": "Crítica",
                "penalty": "Interdição do produto, multas e cancelamento do registro",
                "scope": "IA com finalidade diagnóstica ou terapêutica",
                "checklist": [
                    "Classificação do SaMD (Classes I-IV) realizada",
                    "Registro na ANVISA obtido ou em processo",
                    "Plano de gestão de risco (ISO 14971) implementado",
                    "Documentação de validação e verificação",
                    "Monitoramento pós-mercado estabelecido",
                    "Rotulagem e IFU em português",
                ],
                "links": ["https://www.gov.br/anvisa/pt-br/assuntos/noticias-anvisa/2021/anvisa-publica-resolucao-sobre-software-como-dispositivo-medico"]
            },
            "RDC 96/2008": {
                "desc": "Boas Práticas em Tecnologia da Informação",
                "priority": "Alta",
                "penalty": "Interdição, multas e cancelamento de autorização",
                "scope": "Sistemas de informação em saúde",
                "checklist": [
                    "Validação de sistemas computadorizados documentada",
                    "Controles de acesso e segurança implementados",
                    "Backup e recuperação de dados testados",
                    "Rastreabilidade de alterações nos sistemas",
                ],
                "links": ["https://www.gov.br/anvisa/pt-br"]
            },
            "Lei 12.527/2011 (LAI)": {
                "desc": "Lei de Acesso à Informação",
                "priority": "Média",
                "penalty": "Responsabilização funcional e administrativa",
                "scope": "Organizações públicas que usam IA",
                "checklist": [
                    "Transparência nos algoritmos de decisão pública",
                    "Relatórios de impacto disponibilizados",
                    "Canal de solicitação de informações sobre IA",
                ],
                "links": ["https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2011/lei/l12527.htm"]
            },
        }
    },
    "🇪🇺 Europa": {
        "color": "#003399",
        "regs": {
            "GDPR (2016/679)": {
                "desc": "Regulamento Geral de Proteção de Dados",
                "priority": "Crítica",
                "penalty": "Até €20M ou 4% do faturamento global anual",
                "scope": "Toda IA que processa dados de residentes na UE",
                "checklist": [
                    "Base legal para processamento definida (Art. 6/9)",
                    "DPIA realizado para IA de alto risco",
                    "DPO nomeado (se aplicável)",
                    "Direitos dos titulares implementados",
                    "Transferências internacionais adequadas",
                    "Registros de atividades de processamento",
                    "Notificação de breach em 72h à autoridade supervisora",
                ],
                "links": ["https://gdpr.eu/"]
            },
            "EU AI Act (2024/1689)": {
                "desc": "Regulamento Europeu de Inteligência Artificial",
                "priority": "Crítica",
                "penalty": "Até €35M ou 7% do faturamento global; €15M para não conformidade",
                "scope": "Todos os sistemas de IA colocados no mercado da UE",
                "checklist": [
                    "Classificação de risco do sistema de IA (Inaceitável/Alto/Limitado/Mínimo)",
                    "Para IA de Alto Risco: sistema de gestão de qualidade",
                    "Documentação técnica conforme Anexo IV",
                    "Registro no banco de dados da UE (se aplicável)",
                    "Declaração de conformidade emitida",
                    "Supervisão humana garantida",
                    "Robustez, precisão e cibersegurança documentadas",
                ],
                "links": ["https://artificialintelligenceact.eu/"]
            },
            "MDR (2017/745)": {
                "desc": "Regulamento de Dispositivos Médicos",
                "priority": "Crítica",
                "penalty": "Retirada do mercado, multas e responsabilidade civil",
                "scope": "Software de IA com finalidade médica (diagnóstico, monitoramento, tratamento)",
                "checklist": [
                    "Classificação MDR realizada (Classes I-III)",
                    "Notified Body engajada (se Classes IIa, IIb, III)",
                    "Declaração CE emitida",
                    "PMS (Post-Market Surveillance) estabelecido",
                    "PMCF (Clinical Follow-up) implementado",
                    "UDI registrado no EUDAMED",
                ],
                "links": ["https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32017R0745"]
            },
            "IVDR (2017/746)": {
                "desc": "Regulamento de Dispositivos de Diagnóstico In Vitro",
                "priority": "Alta",
                "penalty": "Retirada do mercado e multas por não conformidade",
                "scope": "IA aplicada a diagnóstico in vitro e análises laboratoriais",
                "checklist": [
                    "Classificação IVDR realizada (Classes A-D)",
                    "Performance studies conduzidos",
                    "Rotulagem conforme requisitos IVDR",
                    "Registro no EUDAMED",
                ],
                "links": ["https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32017R0746"]
            },
            "Diretiva NIS2 (2022/2555)": {
                "desc": "Segurança de Redes e Sistemas de Informação",
                "priority": "Alta",
                "penalty": "Até €10M ou 2% do faturamento global",
                "scope": "Operadores de saúde considerados infraestrutura crítica",
                "checklist": [
                    "Medidas de gestão de riscos de cibersegurança",
                    "Planos de resposta a incidentes",
                    "Notificação de incidentes significativos",
                    "Segurança da cadeia de fornecimento",
                ],
                "links": ["https://www.enisa.europa.eu/topics/cybersecurity-policy/nis-directive-new"]
            },
        }
    },
    "🇺🇸 EUA": {
        "color": "#b22234",
        "regs": {
            "HIPAA": {
                "desc": "Health Insurance Portability and Accountability Act",
                "priority": "Crítica",
                "penalty": "Até $1.9M por categoria por ano; $250K criminal",
                "scope": "Toda IA que processa PHI (Protected Health Information)",
                "checklist": [
                    "Business Associate Agreement com fornecedores de IA",
                    "Análise de risco de segurança documentada",
                    "Controles de acesso ao PHI implementados",
                    "Criptografia de PHI em repouso e em trânsito",
                    "Trilha de auditoria de acesso ao PHI",
                    "Plano de resposta a violações",
                    "Treinamento HIPAA para funcionários",
                ],
                "links": ["https://www.hhs.gov/hipaa/index.html"]
            },
            "FDA 21st Century Cures Act / AI SaMD": {
                "desc": "Regulação de Software como Dispositivo Médico pela FDA",
                "priority": "Crítica",
                "penalty": "Warning Letters, recalls, proibição de importação",
                "scope": "IA com finalidade diagnóstica ou terapêutica nos EUA",
                "checklist": [
                    "Determinação 510(k)/PMA/De Novo realizada",
                    "Submissão regulatória à FDA (se aplicável)",
                    "PCCP (Predetermined Change Control Plan) para IA adaptativa",
                    "Vigilância pós-mercado estabelecida",
                    "MDR (Medical Device Reporting) para eventos adversos",
                ],
                "links": ["https://www.fda.gov/medical-devices/software-medical-device-samd"]
            },
            "CCPA / CPRA (California)": {
                "desc": "California Consumer Privacy Act / California Privacy Rights Act",
                "priority": "Alta",
                "penalty": "Até $7.500 por violação intencional; $2.500 não intencional",
                "scope": "Organizações com dados de residentes da Califórnia",
                "checklist": [
                    "Política de privacidade atualizada com direitos CCPA",
                    "Mecanismo 'Do Not Sell or Share My Personal Information'",
                    "Processo para atendimento de solicitações de titulares",
                    "Avaliação de risco para usos de alto risco",
                ],
                "links": ["https://cppa.ca.gov/"]
            },
            "ADA (Americans with Disabilities Act)": {
                "desc": "Garantia de acesso igualitário a sistemas de IA",
                "priority": "Alta",
                "penalty": "Até $75.000 por primeira violação; $150.000 por reincidências",
                "scope": "Sistemas de IA em locais públicos ou serviços de saúde",
                "checklist": [
                    "Acessibilidade do sistema de IA avaliada (WCAG 2.1)",
                    "Alternativas para usuários com deficiências",
                    "Não discriminação algorítmica documentada",
                ],
                "links": ["https://www.ada.gov/"]
            },
            "NIST AI RMF (AI 100-1)": {
                "desc": "Framework de Gestão de Riscos de IA do NIST",
                "priority": "Média",
                "penalty": "Não é lei, mas é referência esperada pela FDA e outros reguladores",
                "scope": "Organizações que desenvolvem ou usam sistemas de IA",
                "checklist": [
                    "Funções GOVERN, MAP, MEASURE, MANAGE implementadas",
                    "Perfil de risco de IA documentado",
                    "Trustworthy AI characteristics avaliadas",
                    "Plano de ação de riscos documentado",
                ],
                "links": ["https://www.nist.gov/system/files/documents/2023/01/26/NIST.AI.100-1.pdf"]
            },
        }
    },
    "🇬🇧 Reino Unido": {
        "color": "#012169",
        "regs": {
            "UK GDPR": {
                "desc": "GDPR adaptado para o Reino Unido pós-Brexit",
                "priority": "Crítica",
                "penalty": "Até £17.5M ou 4% do faturamento global anual",
                "scope": "Toda IA que processa dados pessoais de residentes do RU",
                "checklist": [
                    "UK Representative nomeado (se fora do RU)",
                    "DPIA realizado para IA de alto risco",
                    "Registros de processamento mantidos (ICO)",
                    "Base legal UK GDPR definida",
                ],
                "links": ["https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/"]
            },
            "MHRA SaMD Guidelines": {
                "desc": "Regulação de Software como Dispositivo Médico pela MHRA",
                "priority": "Crítica",
                "penalty": "Retirada do mercado, multas e responsabilidade criminal",
                "scope": "IA com finalidade médica no mercado do Reino Unido",
                "checklist": [
                    "Classificação de dispositivo médico (MHRA) realizada",
                    "Registro no MHRA obtido",
                    "UKCA marking (se aplicável)",
                    "PMS estabelecido para o mercado UK",
                ],
                "links": ["https://www.gov.uk/government/organisations/medicines-and-healthcare-products-regulatory-agency"]
            },
        }
    },
    "🇨🇦 Canadá": {
        "color": "#ff0000",
        "regs": {
            "PIPEDA": {
                "desc": "Personal Information Protection and Electronic Documents Act",
                "priority": "Alta",
                "penalty": "Até CAD $100.000 por infração",
                "scope": "Organizações privadas que coletam dados pessoais",
                "checklist": [
                    "Consentimento significativo obtido",
                    "Dados pessoais protegidos adequadamente",
                    "Indivíduos notificados de violações",
                    "PIPEDA compliance program estabelecido",
                ],
                "links": ["https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/"]
            },
            "PHIPA (Ontario)": {
                "desc": "Personal Health Information Protection Act",
                "priority": "Alta",
                "penalty": "Até CAD $500.000 por organização",
                "scope": "Custodians de informações de saúde em Ontario",
                "checklist": [
                    "Health Information Custodian designado",
                    "Acordos com agentes de informação de saúde",
                    "Notificação de breach implementada",
                ],
                "links": ["https://www.ontario.ca/laws/statute/04p03"]
            },
        }
    },
    "🇦🇺 Austrália": {
        "color": "#00008b",
        "regs": {
            "Privacy Act 1988": {
                "desc": "Lei de Privacidade da Austrália (APPs)",
                "priority": "Alta",
                "penalty": "Até AUD $50M por violações sérias",
                "scope": "Organizações com receita >AUD $3M e agências governamentais",
                "checklist": [
                    "Australian Privacy Principles (APPs) implementados",
                    "Privacy policy atualizada",
                    "NDB Scheme (Notifiable Data Breaches) implementado",
                    "Privacy impact assessment para IA de alto risco",
                ],
                "links": ["https://www.oaic.gov.au/privacy/the-privacy-act"]
            },
            "TGA SaMD": {
                "desc": "Therapeutic Goods Administration - Software como Dispositivo",
                "priority": "Alta",
                "penalty": "Multas e retirada do mercado australiano",
                "scope": "IA com finalidade diagnóstica ou terapêutica na Austrália",
                "checklist": [
                    "Classificação TGA realizada",
                    "Inclusão no ARTG (Australian Register of Therapeutic Goods)",
                    "Monitoramento pós-mercado estabelecido",
                ],
                "links": ["https://www.tga.gov.au/resources/guidance/software-medical-device"]
            },
        }
    },
    "🇯🇵 Japão": {
        "color": "#bc002d",
        "regs": {
            "APPI (Act on Protection of Personal Information)": {
                "desc": "Lei de Proteção de Informações Pessoais",
                "priority": "Alta",
                "penalty": "Até JPY 100M por organizações; ações criminais possíveis",
                "scope": "Organizações que gerenciam informações pessoais no Japão",
                "checklist": [
                    "PPC (Personal Information Protection Commission) reporting",
                    "Consentimento para dados sensíveis de saúde",
                    "Transferências internacionais adequadas",
                    "Medidas de segurança para dados médicos",
                ],
                "links": ["https://www.ppc.go.jp/en/"]
            },
            "PMDA SaMD Guidelines": {
                "desc": "Pharmaceuticals and Medical Devices Agency",
                "priority": "Alta",
                "penalty": "Retirada do mercado japonês",
                "scope": "IA com finalidade médica no Japão",
                "checklist": [
                    "Classificação de dispositivo médico PMDA",
                    "Aprovação de fabricação ou importação",
                    "Estudos de desempenho realizados",
                ],
                "links": ["https://www.pmda.go.jp/english/index.html"]
            },
        }
    },
    "🇸🇬 Singapura": {
        "color": "#ef3340",
        "regs": {
            "PDPA (Personal Data Protection Act)": {
                "desc": "Lei de Proteção de Dados Pessoais de Singapura",
                "priority": "Alta",
                "penalty": "Até SGD $1M por organização",
                "scope": "Organizações que coletam, usam ou divulgam dados pessoais",
                "checklist": [
                    "DPO nomeado e registrado na PDPC",
                    "Política de proteção de dados implementada",
                    "Notificação de data breach à PDPC",
                    "AI Governance Framework da PDPC adotado",
                ],
                "links": ["https://www.pdpc.gov.sg/"]
            },
            "HSA SaMD": {
                "desc": "Health Sciences Authority - Software Médico",
                "priority": "Alta",
                "penalty": "Sanções regulatórias e retirada do produto",
                "scope": "IA com finalidade médica em Singapura",
                "checklist": [
                    "Classificação HSA realizada",
                    "Registro no HSA Product Database",
                    "Clinical evidence estabelecida",
                ],
                "links": ["https://www.hsa.gov.sg/medical-devices"]
            },
        }
    },
    "🇮🇳 Índia": {
        "color": "#ff9933",
        "regs": {
            "DPDP Act 2023": {
                "desc": "Digital Personal Data Protection Act",
                "priority": "Alta",
                "penalty": "Até INR 250 crore (~USD $30M)",
                "scope": "Processamento de dados pessoais digitais na Índia",
                "checklist": [
                    "Consent Manager framework implementado",
                    "Data Fiduciary obrigações cumpridas",
                    "Localização de dados (se aplicável)",
                    "Notificação de breach ao DPBI",
                ],
                "links": ["https://www.meity.gov.in/data-protection-framework"]
            },
            "MDR India 2017": {
                "desc": "Medical Devices Rules - India",
                "priority": "Alta",
                "penalty": "Cancelamento de licença e ação judicial",
                "scope": "Dispositivos médicos e SaMD na Índia",
                "checklist": [
                    "Registro no CDSCO realizado",
                    "Licença de fabricação/importação obtida",
                    "Clinical investigation conforme requisitos",
                ],
                "links": ["https://cdsco.gov.in/opencms/opencms/en/Medical-Device-Diagnostics/"]
            },
        }
    },
}

# ── Helper functions ───────────────────────────────────────────────────────────
def get_domain_score(domain_name):
    """Returns (achieved_levels, max_levels, percentage) for a domain."""
    domain = DOMAINS[domain_name]
    total = 0
    achieved = 0
    scores_ss = st.session_state.scores.get(domain_name, {})
    for practice, levels in domain["practices"].items():
        for level in ["L1", "L2", "L3"]:
            for stream in ["A", "B"]:
                total += 1
                if scores_ss.get(practice, {}).get(level, {}).get(stream, False):
                    achieved += 1
    pct = (achieved / total * 100) if total else 0
    return achieved, total, pct

def maturity_level(pct):
    if pct == 0:
        return 0, "Não iniciado", "l0"
    elif pct < 40:
        return 1, "Nível 1 – Inicial", "l1"
    elif pct < 70:
        return 2, "Nível 2 – Gerenciado", "l2"
    else:
        return 3, "Nível 3 – Otimizado", "l3"

def to_excel():
    """Export assessment + compliance to Excel bytes."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Summary sheet
        rows = []
        for domain_name in DOMAINS:
            ach, tot, pct = get_domain_score(domain_name)
            lvl, lbl, _ = maturity_level(pct)
            rows.append({"Domínio": domain_name, "Respondidas": ach, "Total": tot, "% Completado": round(pct, 1), "Nível de Maturidade": lbl})
        pd.DataFrame(rows).to_excel(writer, sheet_name="Resumo", index=False)

        # Detail sheet
        detail = []
        for domain_name, domain in DOMAINS.items():
            for practice, levels in domain["practices"].items():
                for level in ["L1", "L2", "L3"]:
                    for stream, question in levels[level].items():
                        ans = st.session_state.scores.get(domain_name, {}).get(practice, {}).get(level, {}).get(stream, False)
                        detail.append({"Domínio": domain_name, "Prática": practice, "Nível": level, "Stream": stream, "Questão": question, "Resposta": "Sim" if ans else "Não"})
        pd.DataFrame(detail).to_excel(writer, sheet_name="Avaliação Detalhada", index=False)

        # Compliance sheet
        comp_rows = []
        for jur, data in REGULATIONS.items():
            for reg, info in data["regs"].items():
                status = st.session_state.compliance.get(jur, {}).get(reg, "Não iniciado")
                comp_rows.append({"Jurisdição": jur, "Regulação": reg, "Descrição": info["desc"], "Prioridade": info["priority"], "Penalidade": info["penalty"], "Status": status})
        pd.DataFrame(comp_rows).to_excel(writer, sheet_name="Conformidade", index=False)

    return output.getvalue()

# ── Automated repository scan (heuristic, read-only, best-effort) ──────────────
# Only ever calls api.github.com, constructed from a regex-validated owner/repo -
# never fetches a user-supplied URL directly, to avoid SSRF. No fetched content
# is ever executed; it is only pattern-matched as text.
GITHUB_URL_RE = re.compile(
    r"^https?://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$"
)

AUTO_SCAN_KEYWORDS = {
    "kw_fairness": ["fairness", "bias", "fairlearn", "aif360", "viés", "equidade"],
    "kw_privacy": ["gdpr", "lgpd", "privacy", "privacidade", "dpia"],
    "kw_explainability": ["explainab", "interpretab", "shap", "lime", "transparên"],
    "kw_monitoring": ["monitoring", "prometheus", "grafana", "sentry", "observability", "monitoramento"],
    "kw_threat_model": ["threat model", "threat-model", "ameaça", "stride"],
}

AUTO_SCAN_RULES = [
    ("Implementation", "Secure Build", "L1", "A", "security_scanning"),
    ("Implementation", "Secure Build", "L1", "B", "has_tests"),
    ("Implementation", "Secure Build", "L3", "B", "security_scanning"),
    ("Implementation", "Secure Deployment", "L1", "A", "has_dockerfile"),
    ("Implementation", "Secure Deployment", "L1", "B", "ci_workflows"),
    ("Verification", "Security Testing", "L1", "A", "has_tests"),
    ("Verification", "Security Testing", "L2", "A", "security_scanning"),
    ("Verification", "Requirement-Based Testing", "L1", "B", "has_tests"),
    ("Operations", "Incident Management", "L1", "A", "has_security_md"),
    ("Operations", "Incident Management", "L1", "B", "has_security_md"),
    ("Operations", "Event Management", "L1", "A", "kw_monitoring"),
    ("Governance", "Policy & Compliance", "L1", "A", "kw_privacy"),
    ("Governance", "Strategy & Metrics", "L1", "B", "ci_workflows"),
    ("Privacy", "Privacy by Design", "L1", "A", "has_privacy_doc"),
    ("Privacy", "Privacy by Design", "L1", "B", "kw_privacy"),
    ("Responsible AI", "Transparency & Explainability", "L1", "A", "has_model_card"),
    ("Responsible AI", "Transparency & Explainability", "L1", "B", "kw_explainability"),
    ("Responsible AI", "Fairness & Bias", "L1", "A", "kw_fairness"),
    ("Design", "Threat Assessment", "L1", "A", "kw_threat_model"),
]


def _parse_github_url(url):
    match = GITHUB_URL_RE.match(url.strip()) if url else None
    if not match:
        return None
    return match.group("owner"), match.group("repo")


def _gh_get(url, token):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.get(url, headers=headers, timeout=10)


def scan_github_repo(owner, repo, token=None):
    """Best-effort, read-only scan of a public GitHub repo for AIMA-relevant signals.
    Returns (signals: dict, evidence: list[str], error: str | None).
    """
    base = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        info = _gh_get(base, token)
    except requests.exceptions.RequestException:
        return {}, [], "Não foi possível conectar ao GitHub. Tente novamente mais tarde."

    if info.status_code == 404:
        return {}, [], "Repositório não encontrado (verifique se é público e a URL está correta)."
    if info.status_code == 403:
        return {}, [], "Limite de requisições da API do GitHub atingido. Tente novamente em alguns minutos."
    if info.status_code != 200:
        return {}, [], f"Erro ao acessar o repositório (HTTP {info.status_code})."

    info_json = info.json()
    if info_json.get("private"):
        return {}, [], "Repositórios privados não são suportados por esta análise."

    default_branch = info_json.get("default_branch", "main")

    try:
        tree = _gh_get(f"{base}/git/trees/{default_branch}?recursive=1", token)
    except requests.exceptions.RequestException:
        return {}, [], "Não foi possível ler os arquivos do repositório."

    if tree.status_code != 200:
        return {}, [], f"Erro ao listar arquivos do repositório (HTTP {tree.status_code})."

    paths = [
        item["path"].lower()
        for item in tree.json().get("tree", [])[:5000]
        if item.get("type") == "blob"
    ]

    def has(*needles):
        return any(any(n in p for n in needles) for p in paths)

    signals = {}
    evidence = []

    checks = [
        ("ci_workflows", (".github/workflows/",), "CI/CD detectado (.github/workflows/)"),
        ("security_scanning", ("codeql", "bandit", "snyk", "trivy", "semgrep", "dependabot"),
         "Scanner de segurança de código detectado (CodeQL/Bandit/Snyk/etc.)"),
        ("has_tests", ("tests/", "test_", "_test.py"), "Diretório/arquivos de teste automatizado detectados"),
        ("has_security_md", ("security.md",), "SECURITY.md presente (processo de reporte de vulnerabilidades)"),
        ("has_dockerfile", ("dockerfile",), "Dockerfile presente (deployment padronizado)"),
        ("has_model_card", ("model_card", "model-card", "datasheet"), "Model card / datasheet presente (transparência do modelo)"),
        ("has_privacy_doc", ("privacy.md", "dpia"), "Documentação de privacidade presente"),
    ]
    for key, needles, label in checks:
        if has(*needles):
            signals[key] = True
            evidence.append(label)

    # Keyword search in README / SECURITY.md content (best-effort, capped)
    for fname in ("readme.md", "security.md"):
        matches = [p for p in paths if p == fname or p.endswith("/" + fname)]
        if not matches:
            continue
        try:
            content_resp = _gh_get(f"{base}/contents/{matches[0]}", token)
        except requests.exceptions.RequestException:
            continue
        if content_resp.status_code != 200:
            continue
        data = content_resp.json()
        if data.get("encoding") != "base64":
            continue
        try:
            text = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")[:20000].lower()
        except (ValueError, TypeError):
            continue

        for key, needles in AUTO_SCAN_KEYWORDS.items():
            if signals.get(key):
                continue
            if any(kw in text for kw in needles):
                signals[key] = True
                evidence.append(f"Menção a \"{key.replace('kw_', '')}\" encontrada em {matches[0].upper()}")

    return signals, evidence, None


def map_signals_to_scores(signals):
    suggestions = {}
    applied_rules = []
    for domain, practice, level, stream, sig_key in AUTO_SCAN_RULES:
        if signals.get(sig_key):
            suggestions.setdefault(domain, {}).setdefault(practice, {}).setdefault(level, {})[stream] = True
            applied_rules.append((domain, practice, level, stream))
    return suggestions, applied_rules


def apply_auto_suggestions(suggestions):
    count = 0
    for domain, practices in suggestions.items():
        st.session_state.scores.setdefault(domain, {})
        for practice, levels in practices.items():
            st.session_state.scores[domain].setdefault(practice, {})
            for level, streams in levels.items():
                st.session_state.scores[domain][practice].setdefault(level, {})
                for stream, value in streams.items():
                    if value and not st.session_state.scores[domain][practice][level].get(stream):
                        st.session_state.scores[domain][practice][level][stream] = True
                        count += 1
    return count

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://owasp.org/assets/images/logo.png", width=120)
    st.markdown("## OWASP AIMA Healthcare")
    st.caption(t("app_sub"))

    st.divider()

    lang_choice = st.selectbox(t("lang_label"), ["Português", "English", "Español"])
    st.session_state.lang = {"Português": "pt", "English": "en", "Español": "es"}[lang_choice]

    st.divider()

    page = st.radio("Navegação", [
        t("menu_home"), t("menu_assess"), t("menu_auto"), t("menu_compliance"),
        t("menu_reports"), t("menu_settings")
    ])

    # Mini progress
    if any(st.session_state.scores.values()):
        st.divider()
        st.caption("Progresso geral")
        total_ach = sum(get_domain_score(d)[0] for d in DOMAINS)
        total_max = sum(get_domain_score(d)[1] for d in DOMAINS)
        st.progress(total_ach / total_max if total_max else 0)
        st.caption(f"{total_ach}/{total_max} questões respondidas")

    st.divider()
    st.caption("v1.0 · [GitHub](https://github.com/OWASP/www-project-ai-maturity-assessment)")

# ── HOME PAGE ──────────────────────────────────────────────────────────────────
if page == t("menu_home"):
    st.markdown(f"# 🏥 {t('app_title')}")
    st.markdown(f"### {t('app_sub')}")
    st.markdown("""
    Aplicação baseada no **[OWASP AI Maturity Assessment (AIMA)](https://owasp.org/www-project-ai-maturity-assessment/)**,
    adaptada para laboratórios médicos e organizações de saúde com foco em conformidade regulatória global.
    """)
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Domínios AIMA", len(DOMAINS), help="8 domínios do framework OWASP AIMA")
    col2.metric("Jurisdições", len(REGULATIONS), help="Regiões cobertas")
    total_regs = sum(len(v["regs"]) for v in REGULATIONS.values())
    col3.metric("Regulações", total_regs, help="Regulamentações mapeadas")
    col4.metric("Níveis de Maturidade", "3", help="Inicial → Gerenciado → Otimizado")

    st.divider()
    st.markdown("## 8 Domínios OWASP AIMA")
    cols = st.columns(4)
    for idx, (domain_name, domain) in enumerate(DOMAINS.items()):
        ach, tot, pct = get_domain_score(domain_name)
        lvl, lbl, css = maturity_level(pct)
        with cols[idx % 4]:
            st.markdown(f"""
            <div class="metric-card">
                <b>{domain['icon']} {domain_name}</b><br>
                <small>{len(domain['practices'])} práticas · {tot} questões</small><br>
                <span class="level-badge {css}">{lbl}</span>
                <br><small>{pct:.0f}% completo</small>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    ## Como usar

    | Etapa | Ação |
    |-------|------|
    | 1 | **Configurações** → Informe sua organização e jurisdições de operação |
    | 2 | **Avaliação AIMA** → Responda Sim/Não para cada prática e nível |
    | 3 | **Conformidade Regulatória** → Marque o status de cada regulação |
    | 4 | **Relatórios** → Visualize dashboards e exporte para Excel/JSON |
    """)

# ── ASSESSMENT PAGE ────────────────────────────────────────────────────────────
elif page == t("menu_assess"):
    st.markdown(f"# {t('menu_assess')}")
    st.info("Responda **Sim** ou **Não** para cada critério. O nível de maturidade é atingido quando todos os critérios daquele nível forem **Sim**.")

    domain_tabs = st.tabs([f"{d['icon']} {name}" for name, d in DOMAINS.items()])

    for tab, (domain_name, domain) in zip(domain_tabs, DOMAINS.items()):
        with tab:
            ach, tot, pct = get_domain_score(domain_name)
            lvl, lbl, css = maturity_level(pct)

            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"## {domain['icon']} {domain_name}")
            with col2:
                st.markdown(f"<span class='level-badge {css}'>{lbl}</span>", unsafe_allow_html=True)
                st.progress(pct / 100)
                st.caption(f"{ach}/{tot}")

            # Ensure nested dict exists
            if domain_name not in st.session_state.scores:
                st.session_state.scores[domain_name] = {}

            for practice_name, levels in domain["practices"].items():
                if practice_name not in st.session_state.scores[domain_name]:
                    st.session_state.scores[domain_name][practice_name] = {}

                with st.expander(f"📌 {practice_name}", expanded=False):
                    for level_key, streams in levels.items():
                        level_num = int(level_key[1])
                        st.markdown(f"**Nível {level_num}**")
                        col_a, col_b = st.columns(2)

                        if level_key not in st.session_state.scores[domain_name][practice_name]:
                            st.session_state.scores[domain_name][practice_name][level_key] = {}

                        with col_a:
                            st.caption("Stream A")
                            key_a = f"{domain_name}__{practice_name}__{level_key}__A"
                            current_a = st.session_state.scores[domain_name][practice_name][level_key].get("A", False)
                            ans_a = st.checkbox(streams["A"], value=current_a, key=key_a)
                            st.session_state.scores[domain_name][practice_name][level_key]["A"] = ans_a

                        with col_b:
                            st.caption("Stream B")
                            key_b = f"{domain_name}__{practice_name}__{level_key}__B"
                            current_b = st.session_state.scores[domain_name][practice_name][level_key].get("B", False)
                            ans_b = st.checkbox(streams["B"], value=current_b, key=key_b)
                            st.session_state.scores[domain_name][practice_name][level_key]["B"] = ans_b

                        st.divider()

# ── AUTOMATED SCAN PAGE ────────────────────────────────────────────────────────
elif page == t("menu_auto"):
    st.markdown(f"# {t('menu_auto')}")
    st.info(t("auto_intro"))

    repo_url = st.text_input(t("auto_url_label"), placeholder="https://github.com/owner/repo")

    if st.button(t("auto_button")):
        parsed = _parse_github_url(repo_url)
        if not parsed:
            st.error(t("auto_invalid_url"))
            st.session_state.pop("auto_scan_evidence", None)
        else:
            owner, repo_name = parsed
            try:
                token = st.secrets.get("github_token", None)
            except Exception:
                token = None
            with st.spinner("..."):
                signals, evidence, error = scan_github_repo(owner, repo_name, token)
            if error:
                st.error(error)
                st.session_state.pop("auto_scan_evidence", None)
            else:
                st.session_state["auto_scan_signals"] = signals
                st.session_state["auto_scan_evidence"] = evidence

    if st.session_state.get("auto_scan_evidence") is not None:
        st.divider()
        st.markdown(f"### {t('auto_evidence_header')}")
        evidence = st.session_state["auto_scan_evidence"]
        if evidence:
            for item in evidence:
                st.markdown(f"- {item}")
        else:
            st.warning(t("auto_no_evidence"))

        suggestions, applied_rules = map_signals_to_scores(st.session_state.get("auto_scan_signals", {}))
        if applied_rules:
            st.caption(f"{len(applied_rules)} {t('auto_suggestions_ready')}")
            if st.button(t("auto_apply_button")):
                count = apply_auto_suggestions(suggestions)
                st.success(f"{count} {t('auto_applied_msg')}")

# ── COMPLIANCE PAGE ────────────────────────────────────────────────────────────
elif page == t("menu_compliance"):
    st.markdown(f"# {t('menu_compliance')}")

    org_jurisdictions = st.session_state.org.get("jurisdictions", [])
    selected_jurs = st.multiselect(
        "Selecione as jurisdições em que sua organização opera:",
        list(REGULATIONS.keys()),
        default=[j for j in org_jurisdictions if j in REGULATIONS] or list(REGULATIONS.keys())[:3]
    )

    status_options = [t("not_started"), t("in_progress"), t("compliant"), t("non_compliant")]

    for jur in selected_jurs:
        jur_data = REGULATIONS[jur]
        if jur not in st.session_state.compliance:
            st.session_state.compliance[jur] = {}

        color = jur_data["color"]
        st.markdown(f"## {jur}")

        for reg_name, reg in jur_data["regs"].items():
            with st.expander(f"**{reg_name}** — {reg['desc']}"):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.markdown(f"**Escopo:** {reg['scope']}")
                    st.markdown(f"**Penalidade:** `{reg['penalty']}`")

                with col2:
                    pri = reg["priority"]
                    color_map = {"Crítica": "🔴", "Alta": "🟠", "Média": "🟡", "Baixa": "🟢"}
                    st.markdown(f"**Prioridade:** {color_map.get(pri, '')} {pri}")

                with col3:
                    curr_status = st.session_state.compliance[jur].get(reg_name, t("not_started"))
                    new_status = st.selectbox(
                        "Status", status_options,
                        index=status_options.index(curr_status) if curr_status in status_options else 0,
                        key=f"comp__{jur}__{reg_name}",
                        label_visibility="collapsed"
                    )
                    st.session_state.compliance[jur][reg_name] = new_status

                st.markdown("**Checklist de implementação:**")
                for item in reg["checklist"]:
                    st.checkbox(f"  {item}", key=f"chk__{jur}__{reg_name}__{item}")

                if reg.get("links"):
                    st.markdown("**Recursos oficiais:** " + " | ".join(f"[Link]({l})" for l in reg["links"]))

        st.divider()

# ── REPORTS PAGE ───────────────────────────────────────────────────────────────
elif page == t("menu_reports"):
    st.markdown(f"# {t('menu_reports')}")

    # ── Maturity Radar ──────────────────────────────────────────────────────────
    st.markdown("## Radar de Maturidade AIMA")

    domain_names = list(DOMAINS.keys())
    pcts = [get_domain_score(d)[2] for d in domain_names]

    fig_radar = go.Figure(go.Scatterpolar(
        r=pcts + [pcts[0]],
        theta=domain_names + [domain_names[0]],
        fill="toself",
        fillcolor="rgba(25, 118, 210, 0.2)",
        line=dict(color="#1976D2", width=2),
        name="Maturidade"
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%")),
        showlegend=False,
        height=450,
        margin=dict(t=30, b=30),
    )
    st.plotly_chart(fig_radar, width="stretch")

    st.divider()

    # ── Domain breakdown ────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("## Pontuação por Domínio")
        rows = []
        for domain_name in DOMAINS:
            ach, tot, pct = get_domain_score(domain_name)
            lvl, lbl, _ = maturity_level(pct)
            rows.append({"Domínio": domain_name, "% Completo": round(pct, 1), "Respondidas": f"{ach}/{tot}", "Nível": lbl})
        df = pd.DataFrame(rows)
        st.dataframe(df, width="stretch", hide_index=True)

    with col2:
        st.markdown("## Distribuição de Maturidade")
        level_counts = {"Não iniciado": 0, "Nível 1": 0, "Nível 2": 0, "Nível 3": 0}
        for domain_name in DOMAINS:
            _, _, pct = get_domain_score(domain_name)
            lvl, _, _ = maturity_level(pct)
            if lvl == 0: level_counts["Não iniciado"] += 1
            elif lvl == 1: level_counts["Nível 1"] += 1
            elif lvl == 2: level_counts["Nível 2"] += 1
            else: level_counts["Nível 3"] += 1

        fig_pie = px.pie(
            names=list(level_counts.keys()),
            values=list(level_counts.values()),
            color=list(level_counts.keys()),
            color_discrete_map={"Não iniciado": "#ef9a9a", "Nível 1": "#ffcc80", "Nível 2": "#fff59d", "Nível 3": "#a5d6a7"},
        )
        fig_pie.update_layout(height=320, margin=dict(t=10, b=10))
        st.plotly_chart(fig_pie, width="stretch")

    st.divider()

    # ── Compliance summary ─────────────────────────────────────────────────────
    st.markdown("## Status de Conformidade Regulatória")

    comp_rows = []
    for jur, data in REGULATIONS.items():
        if jur in st.session_state.compliance:
            for reg, info in data["regs"].items():
                status = st.session_state.compliance[jur].get(reg, t("not_started"))
                comp_rows.append({"Jurisdição": jur, "Regulação": reg, "Prioridade": info["priority"], "Status": status})

    if comp_rows:
        comp_df = pd.DataFrame(comp_rows)

        status_color = {
            t("compliant"): "🟢", t("in_progress"): "🟡",
            t("non_compliant"): "🔴", t("not_started"): "⚪"
        }
        comp_df["Status"] = comp_df["Status"].map(lambda s: f"{status_color.get(s, '')} {s}")

        st.dataframe(comp_df, width="stretch", hide_index=True)
    else:
        st.info("Acesse a aba de Conformidade Regulatória para registrar os status.")

    st.divider()

    # ── Priority recommendations ────────────────────────────────────────────────
    st.markdown("## Recomendações Prioritárias")

    low_domains = [(d, get_domain_score(d)[2]) for d in DOMAINS if get_domain_score(d)[2] < 40]
    low_domains.sort(key=lambda x: x[1])
    for domain_name, pct in low_domains[:5]:
        st.error(f"🔴 **{domain_name}** ({pct:.0f}%) — Atenção crítica necessária: maturidade inicial")

    mid_domains = [(d, get_domain_score(d)[2]) for d in DOMAINS if 40 <= get_domain_score(d)[2] < 70]
    mid_domains.sort(key=lambda x: x[1])
    for domain_name, pct in mid_domains[:3]:
        st.warning(f"🟠 **{domain_name}** ({pct:.0f}%) — Oportunidade de melhoria para nível otimizado")

    high_domains = [(d, get_domain_score(d)[2]) for d in DOMAINS if get_domain_score(d)[2] >= 70]
    for domain_name, pct in high_domains:
        st.success(f"🟢 **{domain_name}** ({pct:.0f}%) — Maturidade otimizada atingida")

    st.divider()

    # ── Export ─────────────────────────────────────────────────────────────────
    st.markdown("## Exportar")
    col1, col2 = st.columns(2)

    with col1:
        excel_bytes = to_excel()
        st.download_button(
            t("export_excel"),
            data=excel_bytes,
            file_name=f"AIMA_Healthcare_{datetime.today().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch"
        )

    with col2:
        json_export = {
            "organization": st.session_state.org,
            "assessment_date": str(datetime.today().date()),
            "scores": st.session_state.scores,
            "compliance": st.session_state.compliance,
            "summary": {
                d: {"achieved": get_domain_score(d)[0], "total": get_domain_score(d)[1], "pct": round(get_domain_score(d)[2], 1)}
                for d in DOMAINS
            }
        }
        st.download_button(
            t("export_json"),
            data=json.dumps(json_export, ensure_ascii=False, indent=2),
            file_name=f"AIMA_Healthcare_{datetime.today().strftime('%Y%m%d')}.json",
            mime="application/json",
            width="stretch"
        )

# ── SETTINGS PAGE ─────────────────────────────────────────────────────────────
elif page == t("menu_settings"):
    st.markdown(f"# {t('menu_settings')}")

    st.markdown("## Informações da Organização")
    col1, col2 = st.columns(2)

    with col1:
        org_name = st.text_input(t("org_name"), value=st.session_state.org.get("name", ""))
        st.session_state.org["name"] = org_name

        org_type = st.selectbox(t("org_type"), [
            "Laboratório Médico", "Hospital", "Clínica", "Instituto de Pesquisa",
            "Empresa de Saúde Digital", "Fornecedor de Tecnologia em Saúde", "Outro"
        ], index=["Laboratório Médico", "Hospital", "Clínica", "Instituto de Pesquisa",
                  "Empresa de Saúde Digital", "Fornecedor de Tecnologia em Saúde", "Outro"].index(
            st.session_state.org.get("type", "Laboratório Médico")))
        st.session_state.org["type"] = org_type

    with col2:
        jurisdictions = st.multiselect(
            "Jurisdições de Operação",
            list(REGULATIONS.keys()),
            default=[j for j in st.session_state.org.get("jurisdictions", ["🇧🇷 Brasil"]) if j in REGULATIONS]
        )
        st.session_state.org["jurisdictions"] = jurisdictions

        assess_date = st.date_input("Data da Avaliação", value=datetime.today())
        st.session_state.org["date"] = str(assess_date)

    st.divider()
    st.markdown("## Casos de Uso de IA")
    use_cases = st.multiselect(
        "Quais casos de uso de IA sua organização possui?",
        [
            "Análise de Imagens Médicas (Radiologia/Patologia)",
            "Suporte à Decisão Clínica",
            "Análise Laboratorial / Diagnóstico In Vitro",
            "Predição de Risco / Prognóstico",
            "Genômica e Medicina de Precisão",
            "Monitoramento de Pacientes (IoT/Wearables)",
            "Otimização de Recursos e Fluxo",
            "Triagem e Priorização",
            "Farmacovigilância",
            "Descoberta de Medicamentos",
        ],
        default=st.session_state.org.get("use_cases", [])
    )
    st.session_state.org["use_cases"] = use_cases

    st.divider()

    if st.button(t("save"), width="stretch"):
        st.success(t("saved"))

    st.divider()
    st.markdown("## Reset")
    if st.button("🗑️ Limpar toda a avaliação", type="secondary"):
        st.session_state.scores = {}
        st.session_state.compliance = {}
        st.success("Avaliação limpa. Você pode começar novamente.")

    st.divider()
    st.markdown("""
    ## Sobre
    **OWASP AI Maturity Assessment (AIMA)** — Healthcare Edition
    - Baseado no framework oficial OWASP AIMA v1
    - Conformidade regulatória: Brasil · EU · EUA · UK · Canadá · Austrália · Japão · Singapura · Índia
    - [Projeto OWASP](https://owasp.org/www-project-ai-maturity-assessment/) · [GitHub](https://github.com/OWASP/www-project-ai-maturity-assessment) · [AIMA Toolkit](https://github.com/anacarolRicciardi/www-project-ai-maturity-assessment)
    """)
