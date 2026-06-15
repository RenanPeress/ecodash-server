# 🌿 EcoDash — Backend API

API REST do sistema de diagnóstico de Green Software. Recebe métricas coletadas pelo script local, calcula o **Score SCI** (Software Carbon Intensity), persiste as análises e expõe endpoints para dashboard, exportação PDF e insights gerados por IA.

---

## 🛠 Stack

| Tecnologia | Versão | Uso |
|---|---|---|
| Python | 3.12 | Linguagem principal |
| Django | 6.0 | Framework web |
| Django REST Framework | 3.16 | API REST |
| SimpleJWT | 5.4 | Autenticação JWT |
| drf-spectacular | 0.29 | Documentação OpenAPI/Swagger |
| WeasyPrint | 65.1 | Geração de relatório PDF |
| Anthropic SDK | ≥0.50 | IA (Claude) — recomendações e chat |
| PostgreSQL / SQLite | — | Banco de dados (prod / dev) |
| Gunicorn + WhiteNoise | — | Servidor e estáticos em produção |

---

## ⚙️ Como Rodar (Desenvolvimento)

```bash
cd ecodash-server

# 1. Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
cp ../.env.example .env         # edite com suas credenciais

# 4. Aplicar migrações
python manage.py migrate

# 5. (Opcional) Criar superusuário para o admin
python manage.py createsuperuser

# 6. Iniciar servidor
python manage.py runserver
```

> API: `http://localhost:8000`
> Swagger UI: `http://localhost:8000/api/docs/`
> Admin Django: `http://localhost:8000/admin/`

---

## 🐳 Como Rodar (Docker)

```bash
docker build -t ecodash-server .
docker run -p 8000:8000 --env-file .env ecodash-server
```

---

## 🔌 Endpoints Principais

Todas as rotas (exceto `signup` e `login`) exigem o header:
```
Authorization: Bearer <access_token>
```

### Autenticação

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/api/auth/signup/` | Cadastro de usuário |
| `POST` | `/api/auth/login/` | Login — retorna access + refresh tokens |
| `POST` | `/api/auth/refresh/` | Renovar access token |

### Script Coletor

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/collector/token/` | Ver token do coletor |
| `POST` | `/api/collector/token/` | Regenerar token |
| `GET` | `/api/collector/download/` | Baixar `ecodash-collector.py` pré-configurado |

### Análises

| Método | Endpoint | Auth | Descrição |
|---|---|---|---|
| `GET` | `/api/analyses/` | JWT / CT | Listar análises do usuário |
| `POST` | `/api/analyses/` | JWT / CT | Criar nova análise |
| `GET` | `/api/analyses/{id}/` | JWT / CT | Detalhar análise |
| `DELETE` | `/api/analyses/{id}/` | JWT / CT | Excluir análise |
| `GET` | `/api/analyses/{id}/export/pdf/` | JWT | Exportar análise como PDF |
| `GET` | `/api/analyses/{id}/recommendations/` | JWT | Recomendações de IA para reduzir o SCI |
| `GET` | `/api/analyses/{id}/summary/` | JWT | Resumo em linguagem natural (IA) |

### Dashboard e IA

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/dashboard/` | Totais, média SCI e distribuição de grades |
| `POST` | `/api/chat/` | Chat com IA sobre as análises do usuário |

> **JWT** = `Authorization: Bearer <token>`
> **CT** = `X-Collector-Token: <token>` (enviado pelo script coletor)

---

## 📁 Estrutura

```
ecodash-server/
├── api/
│   ├── ai/                  # Integração Anthropic (service, prompts, client)
│   ├── models.py            # CollectorToken, Analise
│   ├── views.py             # Lógica de todos os endpoints
│   ├── serializers.py       # Validação e serialização de dados
│   ├── pdf.py               # Geração do relatório PDF (WeasyPrint)
│   ├── authentication.py    # Autenticação por X-Collector-Token
│   └── urls.py              # Rotas da API
├── collector_template.py    # Script Python entregue ao usuário
├── metrics_sci.py           # Cálculo SCI local (para testes)
├── requirements.txt
├── Dockerfile
└── manage.py
```
