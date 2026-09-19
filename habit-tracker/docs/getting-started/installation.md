# 📥 Installation & Setup Guide

Follow these steps to clone the repository and spin up both the FastAPI application and the MongoDB instance on your local machine.

---

## 📋 Prerequisites

Before starting, ensure you have the following tools installed on your operating system:
* **Python 3.12+** (Project environment uses Python 3.14 features)
* **Docker & Docker Compose** (Highly recommended for database orchestration)
* **Git** 

---

## 🛠️ Step 1: Clone the Repository

Clone the project from GitHub and navigate directly into the workspace root:

```bash
git clone https://github.com
cd habit-tracker
```

---

## 🐳 Step 2: The Fast Track (Docker Compose)

The easiest way to boot the ecosystem without configuring anything manually is using Docker Compose. It spins up MongoDB 7.0 (with Linux kernel bypass configurations), Redis, and your FastAPI app simultaneously.

1. Create your local configuration file from the template:
   ```bash
   cp .env.example .env
   ```
2. Build and launch the container cluster:
   ```bash
   sudo docker compose up --build -d
   ```
3. Verify all services are healthy:
   ```bash
   sudo docker ps
   ```

The API will now be listening live at `http://127.0.0.1:8000`.

---

## 💻 Step 3: Manual Local Development

If you prefer running the Python process directly on your host machine while keeping MongoDB in a container, follow this workflow:

### 1. Boot up MongoDB via Docker
Run the database while feeding it the necessary environment flags to avoid modern Linux kernel memory allocation failures:
```bash
sudo docker run -d --name habit-tracker-mongo \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=mongo_secret_pass \
  -e USER=root \
  mongo:7.0
```

### 2. Setup the Python Virtual Environment
Initialize your local `venv`, activate it, and pull down the project dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Start the Application Server
Run the entry point script to bind Uvicorn locally:
```bash
python3 run.py
```
