# 🗄️ Database & Storage Layer

This project implements a hybrid storage architecture leveraging **MongoDB** for persistent document-oriented state and **Redis** for ephemeral, low-latency utility storage.

---

## 🍃 MongoDB & Beanie ODM Initialization

The persistent storage lifecycle is managed inside `app/db/database.py` during FastAPI application startup. **Beanie** synchronizes Pydantic definitions directly with the physical storage engine.

```python
# app/db/database.py overview
from motor.motor_asyncio import AsyncMotorClient
from beanie import init_beanie

async def init_db():
    # Asynchronous handshake with target MongoDB container
    client = AsyncMotorClient(MONGO_URL)
    await init_beanie(database = client[DB_NAME], document_models=[...])
```

### Key Behaviors:
* **Auto-Indexing:** Beanie automatically builds unique indices (such as unique constraints on `User.email`) defined in your models on runtime.
* **No Migration Fatigue:** Document changes are matched seamlessly on startup without running clumsy database migration frameworks.

---

## ⚡ Redis Utilities

Handled within `app/db/redis.py`, Redis provides highly efficient key-value processing for transient components:
1. **API Rate Limiting (`utils/limiter.py`):** Protects routes from brute-force authentication attacks and endpoint exhaustion.
2. **Token Blacklisting:** Safely registers invalid or logged-out JWT hashes until their original expiration deadline passes.
