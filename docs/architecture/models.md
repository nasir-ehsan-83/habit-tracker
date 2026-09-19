# 💎 Document Models (Beanie ODM Schema)

All persistent collections reside within `app/models/`. These models extend Pydantic schemas into real transactional MongoDB documents.

---

## 👤 User Model (`users.py`)
Encapsulates account profiles, security scopes, and role hierarchies.

* **Unique Constraints:** `email` (Indexed)
* **Relations:** One-to-Many connection mapping toward individual user settings.

---

## 🎯 Habit Model (`habits.py`)
Defines the concrete recurring targets created by an individual user.

```text
├── id: PydanticObjectId
├── user_id: Link[User] (Foreign key reference)
├── title: str
├── description: str
└── frequency: Enum (Daily, Weekly)
```

---

## 📈 Track Model (`tracks.py`)
Acts as a historical, append-only log record of habit executions. Every singular execution of a habit adds a new, immutable transaction entry into this collection.

---

## 🔥 Streak Model (`streaks.py`)
Maintains calculated running totals for user performance tracking:
* **`current_streak`**: Consecutive completions currently active.
* **`longest_streak`**: Historical all-time high score for benchmarking user discipline.
