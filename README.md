# 🚀 ProductivityHub — Productivity & Language Learning Platform

A fully self-hosted, Docker-containerized platform combining task management, notes, spaced repetition flashcards, AI/ML analytics, and language learning from YouTube videos.

---

## ✨ Features

- **Task Management** — Kanban board with priority, categories, deadlines & filtering
- **Notes** — Rich grid-based notes with tags and full-text search
- **Flashcards** — Spaced repetition using the SM-2 algorithm
- **Language Learning** — Extract vocabulary from YouTube transcripts (English & Korean NLP)
- **ML Analytics** — scikit-learn powered productivity insights & recommendations
- **Email Notifications** — SMTP + APScheduler for reminders and daily summaries
- **Google Calendar** — MCP integration for task-to-event sync
- **Dark Mode** — Tailwind CSS dark theme with toggle

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5 + Tailwind CSS (CDN) + Alpine.js + Plotly |
| Backend | Python FastAPI (async) |
| Database | PostgreSQL 16 + Redis 7 |
| ML/Analytics | scikit-learn, pandas, plotly |
| NLP | spaCy, NLTK, KoNLPy |
| YouTube | youtube-transcript-api |
| Email | smtplib + APScheduler |
| Deployment | Docker + Docker Compose |

---

## 📋 Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)

---

## ⚡ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/MUHAMMEDQULIYEV/MUHAMMEDQULIYEV.git
cd MUHAMMEDQULIYEV

# 2. Configure environment
cp .env.example .env
# Edit .env to set SMTP credentials, secret key, etc.

# 3. Start everything
docker compose up --build

# Or in detached mode:
make up
```

- **Frontend**: http://localhost:3000
- **API Docs** (Swagger): http://localhost:5000/docs
- **Health Check**: http://localhost:5000/api/health

---

## 🧑‍💻 Development (without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/productivity"
export REDIS_URL="redis://localhost:6379"

# Run migrations
alembic upgrade head

# Start API server
uvicorn main:app --reload --port 5000
```

### Frontend

The frontend is pure HTML/CSS/JS — no build step required.

```bash
# Serve with any static file server, e.g.:
cd frontend/src
python -m http.server 3000
```

---

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql+asyncpg://postgres:postgres@db:5432/productivity` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379` |
| `SECRET_KEY` | App secret key (min 32 chars) | *(required)* |
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USER` | SMTP username / email | *(optional)* |
| `SMTP_PASSWORD` | SMTP password / app password | *(optional)* |
| `GOOGLE_CLIENT_ID` | Google OAuth2 client ID | *(optional)* |
| `GOOGLE_CLIENT_SECRET` | Google OAuth2 client secret | *(optional)* |
| `NGROK_AUTHTOKEN` | ngrok auth token for tunneling | *(optional)* |
| `DEFAULT_USER_EMAIL` | Email for the default user | `user@example.com` |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                  │
│  │   Frontend   │    │   Backend    │                  │
│  │  Nginx :3000 │───▶│ FastAPI :5000│                  │
│  │  HTML/JS/CSS │    │   (async)    │                  │
│  └──────────────┘    └──────┬───────┘                  │
│                             │                           │
│                    ┌────────┴────────┐                  │
│                    │                 │                   │
│             ┌──────▼──────┐  ┌──────▼──────┐           │
│             │ PostgreSQL  │  │    Redis    │           │
│             │    :5432    │  │    :6379    │           │
│             └─────────────┘  └─────────────┘           │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Makefile Commands

```bash
make up        # Build and start all services (detached)
make down      # Stop all services
make logs      # Follow logs from all services
make migrate   # Run database migrations
make shell-db  # Open PostgreSQL shell
make reset-db  # Destroy data volumes and restart fresh
make test      # Run backend tests
```

---

## 🌐 ngrok (Optional — Public Tunneling)

To expose your local instance publicly:

```bash
# Install ngrok: https://ngrok.com/download
# Set NGROK_AUTHTOKEN in .env

ngrok http 3000
```

---

## 📅 Google Calendar Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project and enable the **Google Calendar API**
3. Create OAuth 2.0 credentials (Web Application)
4. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`
5. Use the `/api/calendar/sync` endpoint after completing OAuth flow

---

## 🌐 Socials

[![LinkedIn](https://img.shields.io/badge/LinkedIn-%230077B5.svg?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/muhammadquliyev)
[![Email](https://img.shields.io/badge/Email-D14836?logo=gmail&logoColor=white)](mailto:quliyevmuhammad405@gmail.com)

<!-- Proudly created with GPRM (https://gprm.itsvg.in) -->
