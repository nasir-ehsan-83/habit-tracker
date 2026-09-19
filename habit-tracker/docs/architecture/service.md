# ⚙️ Services Layer (Core Business Rules)

To keep the web presentation routing decoupled, all core logic transactions must live inside the `app/services/` layer. Routers must never execute complex mutations directly.

---

## 🔄 Execution Workflow Blueprint

```text
[HTTP Client Request] 
      │
      ▼
[Routes Layer (/routes)]  ──► Validates inputs & extracts active JWT session context
      │
      ▼
[Services Layer (/services)] ──► Compiles heavy math, calculations, and updates
      │
      ▼
[Models Layer (/models)] ──► Commits clean payload data down to MongoDB
```

### Core Services Breakdown:
* **`auth_service.py`**: Interacts with `core/security.py` to assert cryptographic password matches and manage JWT lifetimes.
* **`habits_service.py`**: Manages operational logic rules for user targets.
* **`streaks_service.py`**: Evaluates temporal deadlines between `tracks` logs to automatically increment active streaks or reset broken progress metrics.
