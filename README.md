# Personal AI Agent

> A production-grade, extensible AI Agent platform built with Python and FastAPI, designed to unify productivity tools, developer workflows, and intelligent automation through a modular architecture.
\
---

# Overview

Personal AI Agent is an extensible AI platform that connects multiple services into a single intelligent backend.

Instead of interacting with several independent applications, users interact with one AI-powered platform capable of securely accessing productivity tools, developer services, cloud storage, location services, and external APIs.

The project has been designed with scalability, modularity, maintainability, and fully realized autonomous AI capabilities in mind.

---

# Why This Project?

Modern productivity is fragmented.

A typical workflow requires switching between:

* Gmail
* Google Calendar
* Google Drive
* Google Docs
* Google Sheets
* GitHub
* Google Maps
* Weather services

Personal AI Agent unifies these services behind a single API and delivers a complete foundation for intelligent, context-aware automation.

---

# Features

## Core Infrastructure

* FastAPI backend
* PostgreSQL (Neon)
* Redis
* Celery
* SQLAlchemy 2.0
* Pydantic v2
* Structured logging
* Health monitoring
* Metrics
* CLI
* Production configuration
* Repository pattern
* Dependency Injection

---

## Google Workspace

* Google OAuth 2.0
* Gmail
* Calendar
* Drive
* Docs
* Sheets

---

## Developer Tools

* GitHub Integration (Public Repositories)
* Repository Information
* Branches
* Commits
* Issues
* Pull Requests
* Releases

---

## Utilities

* Weather
* Forecast
* Air Quality
* UV Index
* Google Maps
* Geocoding
* Reverse Geocoding
* Places
* Nearby Search
* Directions
* Distance Matrix
* Timezone

---

## AI Capabilities

* Conversation Management
* Memory Architecture
* Context Snapshots
* Session Management
* Long-Term Memory Infrastructure
* Planner Engine
* Tool Orchestrator
* Browser Automation
* Autonomous Coding Agent
* Multi-Agent Collaboration

---

# Tech Stack

### Backend

* Python
* FastAPI
* SQLAlchemy 2.0
* Pydantic v2
* Celery
* Typer CLI

### Database

* PostgreSQL (Neon)
* Redis

### Integrations

* Google OAuth 2.0
* Gmail API
* Google Calendar API
* Google Drive API
* Google Docs API
* Google Sheets API
* Google Maps Platform API
* GitHub REST API
* OpenWeather API
* OpenAI API

### Development

* Docker
* Pytest
* MyPy
* Ruff

---

# Architecture

```text
                Client
                   │
      ┌────────────┴────────────┐
      │                         │
     CLI                      REST API
      │                         │
      └────────────┬────────────┘
                   │
              FastAPI Backend
                   │
        ┌──────────┴──────────┐
        │                     │
     Services            Repository Layer
        │                     │
        └──────────┬──────────┘
                   │
     PostgreSQL            Redis
                   │
             Celery Workers
                   │
          External Integrations
```

---

# Running Locally

```bash
git clone <repository-url>

cd Personal-AI-Agent

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

python3 -m apps.api.main
```

---

# Environment Variables

Required:

```text
OPENAI_API_KEY
DATABASE_URL
REDIS_URL

GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
GOOGLE_MAPS_API_KEY

GITHUB_TOKEN

WEATHER_API_KEY
```

Never commit your `.env` file.

---

# Testing

```bash
python3 -m pytest -q

python3 -m mypy .

python3 -m ruff check .

python3 -m compileall .
```

---

# Contributing

Contributions are welcome.

If you would like to contribute:

1. Fork the repository.
2. Create a feature branch.
3. Follow the existing project architecture.
4. Ensure all tests pass.
5. Open a Pull Request with a clear description.

Please keep pull requests focused on a single feature or bug fix.

---

# Security

If you discover a security vulnerability, **please do not create a public GitHub issue**.

Instead, contact the maintainer privately with:

* Description of the issue
* Steps to reproduce
* Potential impact
* Suggested mitigation (if available)

Security reports will be handled responsibly and acknowledged after verification.

---

# License

Copyright © 2026 Sayandeep Purkait.

This project is provided under a **Source-Available License**.

You may:

* View the source code
* Fork the repository
* Submit pull requests
* Contribute improvements

You may **not**:

* Repackage or redistribute this project as your own
* Sell or commercially license this project without written permission
* Remove copyright or attribution notices

See the `LICENSE` file for complete terms.

---

# Author

**Sayandeep Purkait**

AI Engineer • Backend Developer • AI Systems Builder

Building scalable software, AI systems, and intelligent automation platforms.
