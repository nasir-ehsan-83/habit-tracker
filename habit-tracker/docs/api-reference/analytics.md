# 📊 Analytics & Streaks API Reference

Exposes calculated summary telemetry for checking performance milestones.

---

## 📌 Fetch Active Performance Summary

* **Endpoint:** `GET /api/v1/analytics/summary`
* **Access Level:** Private User
* **Response Shape:**
  ```json
  {
    "total_habits_tracked": 12,
    "global_completion_rate": "84.5%",
    "longest_active_streak": 28
  }
  ```

---

## 📌 Fetch Specific Habit Progress

* **Endpoint:** `GET /api/v1/analytics/habits/{id}`
* **Description:** Extracts raw data graphs, frequency peaks, and active streaks for a specific habit identity node.
