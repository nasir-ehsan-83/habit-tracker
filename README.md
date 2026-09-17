# 🌐 Habit Tracker Service

A professional-grade backend for tracking daily habits, built with **FastAPI**, **MongoDB**, and **Redis**. This project showcases asynchronous architecture, clean code principles, JWT authentication, and comprehensive system monitoring.

## 📑 Table of Contents

* [Project Overview](#-project-overview)
* [Tech Stack](#-tech-stack)
* [Project Structure](#-project-structure)
* [Getting Started](#-getting-started)
* [Monitoring & Logs](#-monitoring--logs)
* [Testing](#-testing)
* [CI/CD](#-cicd)
* [Author & Support](#-author--support)

## 📊 Project Overview

**Habit Tracker** is a modular backend application designed for high-concurrency environments. It manages daily habits with an emphasis on data integrity, security, and performance.

### Key Features:

* 🔐 **Advanced Auth:** JWT Authentication with strict Access/Refresh token rotation and expiration management.
* 🛡️ **RBAC:** Multi-level access control (Standard User / Admin).
* ⚡ **Performance:** Fully asynchronous I/O powered by FastAPI and Motor.
* 🚀 **Caching & Sessions:** Redis-backed caching and rate-limiting storage for high-throughput scenarios.
* 🚏 **Security:** Integrated Rate Limiting (SlowAPI) to mitigate brute-force and DoS risks.
* 📄 **Pagination:** Robust logic for handling large datasets via skip/limit filters.
* 🗄️ **Schema Integrity:** Type-safe modeling using Beanie ODM and Pydantic v2.
* ✅ **Automated Testing:** Full test suite with isolated MongoDB and Redis services.

> 📘 **Note:** The CS Fundamentals Lab (algorithms & data structures) previously included in this repository has been moved to a separate repository to keep each project focused and independently maintainable.

## 🛠 Tech Stack

* **Framework:** Python 3.12+, FastAPI, Beanie-ODM, Pydantic v2
* **Database:** MongoDB 7.0+
* **Cache / Session Store:** Redis 7.2+
* **Infrastructure:** Docker, Docker Compose
* **Security:** JWT (python-jose), Bcrypt (passlib), SlowAPI
* **Logging:** Structured Rotating File Logging
* **CI/CD:** GitHub Actions (Lint, Test)

## 📁 Project Structure

````text
habit-tracker/
├── app/                        # FastAPI Application
│   ├── config/                 # Settings & Logging Setup
│   ├── core/                   # Security & JWT Logic
│   ├── db/                     # Database Initialization
│   ├── dependencies/           # Auth & Role Guards
│   ├── models/                 # Beanie (MongoDB) Models
│   ├── routes/                 # API Endpoints (Habits, Users, Auth)
│   ├── schemas/                # Pydantic Validation Schemas
│   ├── services/               # Core Business Logic
│   ├── utils/                  # Enums, Limiters & Pagination
│   └── main.py                 # App Entry Point
├── logs/                       # Rotating Log Files (Generated)
├── tests/                      # Automated Test Suite
├── .github/workflows/          # CI/CD Pipelines
├── Dockerfile                  # API Containerization
├── docker-compose.yaml         # Multi-container Orchestration
├── pyproject.toml              # Ruff / Black Configuration
└── run.py                      # Custom Execution Script

🚀 Getting Started

### Installation

**Clone & Enter:**

```bash
git clone https://github.com/nasir-ehsan-83/habit-tracker.git
cd habit-tracker
````

**Run with Docker (Recommended):**

```bash
docker-compose up --build
```

**Manual Setup:**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

## 📝 Monitoring & Logs

The system features a Professional Logging Engine located in the `/logs` directory (outside the app core for security). It automatically rotates files when they reach 5MB.

* `security_audit.log`: Tracks login attempts and token expirations (Warning level).
* `errors.log`: Captures system exceptions and database failures (Error level).
* `critical.log`: High-priority infrastructure alerts.

## 🧪 Testing

We maintain high reliability through rigorous unit testing. Tests run against isolated MongoDB and Redis instances.

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term

# Test specific module
pytest tests/api/test_auth.py
```

## 🚀 CI/CD

This project uses GitHub Actions for continuous integration:

* ✅ **Lint:** ruff + black (non-blocking for WIP code)
* 🧪 **Test:** pytest with MongoDB & Redis service containers
* 📊 **Coverage:** (coming soon)

See `.github/workflows/ci.yaml` for details.

## 👨‍💻 Author

**Nasir Ahmad Ehsan**

Backend Engineer & AI Enthusiast

Specialized in FastAPI, Rust, and Scalable Systems.

GitHub: @nasir-ehsan-83

## ⭐ Support

If this architecture helped your workflow, please consider giving it a ⭐ on GitHub!
