# 📋 Project Summary — Clean Architecture Demo API

A minimal FastAPI backend built to learn **layered (clean) architecture** with
**JWT authentication**. No database — all data lives in memory. The focus is on
understanding how layers connect, not on building a production system.

---

## What This Project Does

1. **User Management (CRUD)** — Create, list, get, and delete users via a REST API.
2. **Authentication** — Register an account and log in to receive a JWT token.
3. **Protected Routes** — All user endpoints require a valid JWT; auth and health endpoints are public.
4. **Layered Architecture** — Every feature flows through Router → Controller → Service → Repository, keeping concerns separated.

---

## Tech Stack

| Component | Library | Purpose |
|---|---|---|
| Web Framework | FastAPI | HTTP routing, validation, auto-docs |
| Server | Uvicorn | Runs the FastAPI app |
| Auth Tokens | PyJWT | Create & verify JSON Web Tokens |
| Password Hashing | bcrypt | Hash passwords before storage |
| Data Validation | Pydantic | Request/response schemas (bundled with FastAPI) |
| CORS | FastAPI CORSMiddleware | Allow cross-origin requests from browsers |
| Data Storage | Python `dict` | In-memory (swappable with a real DB) |

---

## All Endpoints

### 🟢 Public (no token required)

| Method | Path | Description | Request Body | Response |
|---|---|---|---|---|
| `GET` | `/` | Welcome / root | — | `{"message": "...", "docs": "/docs"}` |
| `GET` | `/health` | Health check | — | `{"status": "ok"}` |
| `POST` | `/auth/register` | Create a new account | `{"username", "password"}` | `{"access_token", "token_type", "message"}` |
| `POST` | `/auth/login` | Log in, get a JWT | `{"username", "password"}` | `{"access_token", "token_type", "message"}` |
| `GET` | `/docs` | Swagger UI (interactive docs) | — | HTML page |
| `GET` | `/redoc` | ReDoc (alternative docs) | — | HTML page |

### 🔒 Protected (requires `Authorization: Bearer <token>`)

| Method | Path | Description | Request Body | Success Response | Error Responses |
|---|---|---|---|---|---|
| `GET` | `/users/` | List all users | — | `[{"id", "name", "email"}, ...]` | 401 Unauthorized |
| `GET` | `/users/{id}` | Get one user | — | `{"id", "name", "email"}` | 401, 404 Not Found |
| `POST` | `/users/` | Create a user | `{"name", "email"}` | `{"id", "name", "email"}` (201) | 401, 409 Conflict |
| `DELETE` | `/users/{id}` | Delete a user | — | `{"message": "User {id} deleted"}` | 401, 404 Not Found |

---

## Quick Start

```bash
# 1. Activate virtual environment
.\venv\Scripts\activate        # Windows
source venv/bin/activate       # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
uvicorn app.main:app --reload --port 8000

# 4. Open interactive docs
# → http://localhost:8000/docs
```

---

## Example Flow (curl)

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123"}'

# Login (copy the access_token from the response)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123"}'

# Use the token on protected routes
TOKEN="<paste-token-here>"

curl -X POST http://localhost:8000/users/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'

curl http://localhost:8000/users/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## Project Files

```
clean-architecture-3.0/
├── app/
│   ├── main.py                    # App entry point, CORS & middleware wiring
│   ├── utils/security.py          # JWT + bcrypt helpers
│   ├── models/
│   │   ├── user.py                # User request/response schemas
│   │   └── auth.py                # Auth request/response schemas
│   ├── repositories/
│   │   ├── user_repository.py     # User data access (in-memory)
│   │   └── auth_repository.py     # Account data access (in-memory)
│   ├── services/
│   │   ├── user_service.py        # User business logic
│   │   └── auth_service.py        # Auth business logic
│   ├── controllers/
│   │   ├── user_controller.py     # User HTTP bridge
│   │   └── auth_controller.py     # Auth HTTP bridge
│   ├── routers/
│   │   ├── user_router.py         # /users/* endpoints
│   │   └── auth_router.py         # /auth/* endpoints
│   └── middleware/
│       └── auth.py                # JWT verification middleware
├── frontend/                      # React frontend with URL-based routing (Vite)
│   ├── src/
│   │   ├── components/            # LoginForm, RegisterForm, Dashboard
│   │   ├── services/api.js        # API fetch wrapper
│   │   └── App.jsx                # BrowserRouter, Routes, ProtectedRoute
│   ├── vite.config.js             # Vite dev server + /api proxy
│   └── package.json               # react, react-dom, react-router-dom
├── requirements.txt
├── ARCHITECTURE.md                # Layered architecture guide
├── JWT_AUTH.md                    # JWT & auth deep-dive guide
├── REACT_FRONTEND.md              # React frontend & URL routing guide
└── SUMMARY.md                    # ← This file
```

---

## Related Docs

- [ARCHITECTURE.md](ARCHITECTURE.md) — How the layers work and why they exist.
- [JWT_AUTH.md](JWT_AUTH.md) — How JWT, bcrypt, CORS, register, and login are implemented.
- [REACT_FRONTEND.md](REACT_FRONTEND.md) — React frontend setup, URL-based routing with react-router-dom, and JWT auth flow.
