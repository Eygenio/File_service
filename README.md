# 📁 File Downloader & Analyzer v1.0.0 — FastAPI + Celery + Redis + PostgreSQL

A service for downloading a catalog of text files from an external API and
calculating digit frequency statistics.
Provides a simple web interface with two pages: download management and file analysis.

---

## ✨ Features

* 🚀 Asynchronous batch file download (up to 3 files per request) with retry on rate‑limiting
* 📊 Statistics calculation: global and per‑file digit frequency (0–9)
* 🌐 Web UI:
  * Download page with "Start Download" button and progress visualization
  * File list page with pagination, selection, and "Calculate" button
* ⚙️ Celery for background download execution and periodic tasks
* 🗄 PostgreSQL for storing file metadata
* 🐳 Full Docker & docker-compose support
* 🧪 Automated tests (unit, e2e, integration)
* 📝 Colored structured logging (colorlog)

---

## 🏗️ Architecture

The project follows **Clean Architecture** principles:

* **domain** – entities (`FileRecord`), abstract repository interfaces
* **application** – services (`DownloadService`, `StatsService`)
* **infrastructure** – repository implementations (SQLAlchemy), external API client, Unit of Work
* **presentation** – FastAPI routers, HTML templates, response schemas
* **config** – Pydantic Settings configuration
* **tasks** – Celery tasks

```
project/
├── src/
│ ├── application/
│ │ ├── services/ # DownloadService, StatsService
│ │ └── constants.py
│ ├── domain/
│ │ ├── entities.py
│ │ └── repositories.py # IFileRepository interface
│ ├── infrastructure/
│ │ ├── clients/ # FileApiClient
│ │ ├── models/ # ORM models
│ │ ├── repositories/ # FileRepository
│ │ └── unit_of_work.py
│ ├── presentation/
│ │ ├── api/routes.py
│ │ ├── schemas/
│ │ ├── templates/ # index.html, files.html
│ │ └── dependencies.py
│ ├── config/ # AppConfig, DatabaseConfig, BrokerConfig
│ ├── db/ # database connection
│ ├── tasks/ # download_task.py
│ ├── app.py # FastAPI application
│ └── celery_app.py # Celery configuration
├── tests/
│ ├── conftest.py
│ ├── unit/
│ │ └── test_stats_service.py
│ ├── e2e/
│ │ └── test_api.py
│ └── integration/
│ └── test_api_flow.py
├── docker-compose.yaml
├── Dockerfile
├── pyproject.toml
└── README.md
```

---

## ⚙️ Stack

* **Python** 3.13
* **FastAPI**
* **Celery** + **Redis**
* **PostgreSQL** + SQLAlchemy 2.0 (async)
* **Jinja2**
* **Pydantic** / **Pydantic Settings**
* **Docker** & **docker-compose**
* **Poetry**
* **Pytest** + **pytest-asyncio**
* **Ruff**, **MyPy**, **Pre-commit**

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/Eygenio/File_service
```

## 2. Create a `.env` file (an example is provided inside the repo).Set the real external API URL in EXTERNAL_API_BASE_URL.:

```
APP__HOST=0.0.0.0
APP__PORT=8000

DB__NAME=database
DB__USER=postgres
DB__PASSWORD=postgres
DB__HOST=db
DB__PORT=5432
DB__DRIVER_NAME=postgresql+asyncpg

BROKER__URL=redis://redis:6379/0
BROKER__RESULT_BACKEND=redis://redis:6379/0

EXTERNAL_API_BASE_URL=http://91.199.149.128:18001

```

## 3. 🐳 Build & run with Docker

```bash
docker-compose build
docker-compose up -d
```

The service will be available at `http://localhost:8000`.

---

## 🧪 Testing

```bash
docker-compose exec app pytest -v
```
Tests are organized into:
* **unit** — service layer unit tests
* **integration** — multi‑endpoint workflow tests
* **e2e** — API endpoint tests with mocked dependencies
*
---

## 🧹 Code Quality

All code quality tools are configured in `pyproject.toml` and `.pre-commit-config.yaml`.

```bash
# Formatting and linting
ruff check . --fix
ruff format .

# Type checking
mypy src
```

Pre-commit hooks run automatically on `git commit`.

---

## 🔐 Security

* The external API is called with a unique `X-Candidate-Id`
* All sensitive settings are kept in `.env`
* Database and Redis are isolated within the Docker network

---
