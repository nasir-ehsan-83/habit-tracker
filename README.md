# 🌐 Habit Tracker Service & Algorithm Lab

A professional-grade backend ecosystem built with **FastAPI** and **MongoDB**, featuring a production-ready **Habit Tracking API** integrated with a high-performance **CS Fundamentals Lab**. This project showcases asynchronous architecture, clean code principles, and comprehensive system monitoring.

## 📑 Table of Contents
- [Project Overview](#-project-overview)
- [System Architecture](#-system-architecture)
- [CS Fundamentals Lab](#-cs-fundamentals-lab)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Monitoring & Logs](#-monitoring--logs)
- [Testing](#-testing)
- [Author & Support](#-author--support)

## 📊 Project Overview

The **Habit Tracker** is a modular backend application designed for high-concurrency environments. It manages daily habits with an emphasis on data integrity and security.

### Key Features:
* 🔐 **Advanced Auth:** JWT Authentication with strict Access/Refresh token rotation and expiration management.
* 🛡️ **RBAC:** Multi-level access control (Standard User / Admin).
* ⚡ **Performance:** Fully asynchronous I/O powered by FastAPI and Motor.
* 🚏 **Security:** Integrated Rate Limiting (SlowAPI) to mitigate brute-force and DoS risks.
* 📄 **Pagination:** Robust logic for handling large datasets via skip/limit filters.
* 🗄️ **Schema Integrity:** Type-safe modeling using Beanie ODM and Pydantic v2.

## 📘 CS Fundamentals Lab

A dedicated library of high-performance implementations of core computer science concepts, optimized for educational and practical use.

* **Algorithms:** Production-grade implementations of Quick Sort, Merge Sort, and Binary Search with focus on \(O(n \log n)\) efficiency.
* **Data Structures:** Custom-built Stacks, Queues, Linked Lists, and Tree Traversal algorithms designed for minimal memory overhead.

## 🛠 Tech Stack

* **Framework:** Python 3.12+, FastAPI, Beanie-ODM, Pydantic v2
* **Database:** MongoDB 7.0+
* **Infrastructure:** Docker, Docker Compose
* **Security:** JWT (python-jose), Bcrypt (passlib), SlowAPI
* **Logging:** Structured Rotating File Logging

## 📁 Project Structure

```text
habit-tracker-service/
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
├── data_structure_algorithm/   # CS Fundamentals Module
├── logs/                       # Rotating Log Files (Generated)
├── tests/                      # Automated Test Suite
├── Dockerfile                  # API Containerization
├── docker-compose.yaml         # Multi-container Orchestration
└── run.py                      # Custom Execution Script
```

## 🚀 Getting Started

### Installation
1. **Clone & Enter:**
   ```bash
   git clone https://github.com
   cd habit-tracker-service
   ```

2. **Run with Docker (Recommended):**
   ```bash
   docker-compose up --build
   ```

3. **Manual Setup:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python run.py
   ```

## 📝 Monitoring & Logs

The system features a **Professional Logging Engine** located in the `/logs` directory (outside the app core for security). It automatically rotates files when they reach 5MB.

*   `security_audit.log`: Tracks login attempts and token expirations (Warning level).
*   `errors.log`: Captures system exceptions and database failures (Error level).
*   `critical.log`: High-priority infrastructure alerts.

## 🧪 Testing
We maintain high reliability through rigorous unit testing.

```bash
# Run all tests
pytest

# Test specific module
pytest data_structure_algorithm/tests/test_sorting.py
```

## 👨‍💻 Author
**Nasir Ahmad Ehsan**
* Backend Engineer & AI Enthusiast
* Specialized in FastAPI, Rust, and Scalable Systems.
* GitHub: [@nasir-ehsan-83](https://github.com)

## ⭐ Support
If this architecture helped your workflow, please consider giving it a ⭐ on GitHub!
