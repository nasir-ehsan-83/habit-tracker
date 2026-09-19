# ⚙️ Configuration & Environment Variables

The application relies on environment variables for database handshakes, security algorithms, and third-party interactions. These live inside a `.env` file at the project root.

---

## 📄 Core Variables Breakdown

| Environment Variable | Default Value | Description |
| :--- | :--- | :--- |
| `MONGO_USER` | `admin` | Root username for database authorization. |
| `MONGO_PASSWORD` | `mongo_secret_pass` | Secure password for database authorization. |
| `MONGO_HOST` | `127.0.0.1` | `mongodb` when inside Docker, `127.0.0.1` for local terminal. |
| `MONGO_PORT` | `27017` | Physical networking port for MongoDB. |
| `MONGO_DB` | `habit_tracker_db` | Target MongoDB database namespace. |
| `REDIS_HOST` | `127.0.0.1` | Endpoint address for the in-memory cache/limiter. |
| `JWT_SECRET` | *Auto-generated* | Symmetric cryptographical key used to sign Auth tokens. |
| `JWT_ALGORITHM` | `HS256` | Hashing algorithm for JSON Web Tokens. |

---

## 🔒 Security Best Practices

1. **Production Overrides:** Never reuse the default `mongo_secret_pass` password in production environments.
2. **Git Safeguard:** The `.env` file is strictly ignored by `.gitignore`. Never force commit this file into your version control tree.
