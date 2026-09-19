# 🔐 Authentication API

Endpoints handled by `/routes/auth.py` for handling user onboarding, tokens, and sessions.

---

## 📌 User Registration

* **Endpoint:** `POST /api/auth/register`
* **Access Control:** Public
* **Payload Request (`schemas/users.py`):**
  ```json
  {
    "email": "user@example.com",
    "password": "strongpassword123",
    "full_name": "John Doe"
  }
  ```

---

## 📌 Token Generation (Login)

* **Endpoint:** `POST /api/auth/token`
* **Access Control:** Public
* **Response Payload (`schemas/token.py`):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```