# 📅 Habits API Reference

Manages CRUD execution for routine items. All operations below require an active JSON Web Token injected into the HTTP Request Header.

---

## 📌 Create a New Habit

* **Endpoint:** `POST /api/habits/`
* **Security:** Authenticated (`current_user`)
* **Request Payload (`schemas/habits.py`):**
  ```json
  {
    "title": "Drink Water",
    "description": "3 Liters daily",
    "frequency": "DAILY"
  }
  ```

---

## 📌 List All User Habits

* **Endpoint:** `GET /api/habits/`
* **Query Parameters:** Supports `page` and `limit` pagination helpers managed by `utils/pagination.py`.
* **Response:** Returns an array containing the user's active habit structures.
