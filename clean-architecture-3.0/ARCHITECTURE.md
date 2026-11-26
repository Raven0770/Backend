# 🏗️ Clean Architecture — FastAPI Layered Backend

A minimal FastAPI project built **purely for learning** how layered (clean)
architecture works. No database, no heavy libraries — just request → response
with a dummy auth middleware sitting in front.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [What Are "Layers" and Why?](#what-are-layers-and-why)
3. [Layer-by-Layer Walkthrough](#layer-by-layer-walkthrough)
   - [Resource Layer (Models)](#1-resource-layer--models)
   - [Repository Layer](#2-repository-layer)
   - [Service Layer](#3-service-layer-business-logic)
   - [Controller Layer](#4-controller-layer)
   - [Router Layer](#5-router-layer)
   - [Middleware Layer](#6-middleware-layer)
   - [Entry Point (main.py)](#7-entry-point--mainpy)
4. [Request Lifecycle — End to End](#request-lifecycle--end-to-end)
5. [Libraries Used & Why](#libraries-used--why)
6. [How to Run](#how-to-run)
7. [How to Test (curl examples)](#how-to-test-curl-examples)
8. [Upgrading to a Real Database](#upgrading-to-a-real-database)

---

## Project Structure

```
clean-architecture-3.0/
├── app/
│   ├── __init__.py
│   ├── main.py                          # ← App entry point
│   │
│   ├── models/                          # ← Resource Layer
│   │   ├── __init__.py
│   │   └── user.py                      #    Pydantic schemas
│   │
│   ├── repositories/                    # ← Repository Layer
│   │   ├── __init__.py
│   │   └── user_repository.py           #    Data access (in-memory dict)
│   │
│   ├── services/                        # ← Service Layer
│   │   ├── __init__.py
│   │   └── user_service.py              #    Business logic
│   │
│   ├── controllers/                     # ← Controller Layer
│   │   ├── __init__.py
│   │   └── user_controller.py           #    HTTP ↔ Service bridge
│   │
│   ├── routers/                         # ← Router Layer
│   │   ├── __init__.py
│   │   └── user_router.py               #    URL endpoints
│   │
│   └── middleware/                       # ← Middleware Layer
│       ├── __init__.py
│       └── auth.py                      #    Dummy token auth
│
├── requirements.txt
└── ARCHITECTURE.md                      # ← You are here
```

---

## What Are "Layers" and Why?

Imagine building a house:

| Concern | House Analogy | Software Layer |
|---|---|---|
| What does the visitor see? | The front door | **Router** |
| Who greets them? | The receptionist | **Controller** |
| Who does the actual work? | The office staff | **Service** |
| Where are the files stored? | The filing cabinet | **Repository** |
| What shape is a file? | The form template | **Model (Resource)** |
| Who checks IDs at the gate? | The security guard | **Middleware** |

**Why separate them?**

- **Single Responsibility** — each layer does exactly one job.
- **Testability** — you can test business logic without spinning up a server.
- **Swappability** — replace the filing cabinet (in-memory → PostgreSQL) without
  rewriting the office staff (service) or the front door (router).

---

## Layer-by-Layer Walkthrough

### 1. Resource Layer — Models

📁 `app/models/user.py`

```python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
```

**What is this?**
These are **Pydantic models** — Python classes that define the shape of your data
and automatically validate it.

**Key concepts:**

| Concept | Meaning |
|---|---|
| `BaseModel` | Pydantic's base class. Any class inheriting it gets auto-validation. |
| `Field(...)` | The `...` means "required". You can add constraints like `min_length`. |
| `UserCreate` | The shape of data the client *sends* (request body). |
| `UserResponse` | The shape of data the server *returns* (response body). |

**Why two separate models?**
- The client should never send an `id` — the server generates it.
- The server should always return an `id` — the client needs it.
- Keeping them separate enforces this boundary.

> [!TIP]
> Pydantic comes **bundled with FastAPI** — you don't install it separately.

---

### 2. Repository Layer

📁 `app/repositories/user_repository.py`

```python
class UserRepository:
    def __init__(self):
        self._storage: dict[int, dict] = {}   # the "database"
        self._next_id: int = 1

    def get_all(self) -> list[dict]:  ...
    def get_by_id(self, user_id: int) -> dict | None:  ...
    def create(self, data: UserCreate) -> dict:  ...
    def delete(self, user_id: int) -> bool:  ...
```

**What is this?**
The repository is the **only layer that touches the data source**. Right now,
the data source is a plain Python dictionary. Tomorrow it could be PostgreSQL,
MongoDB, or a REST call to another service.

**Key design rule:**
> No other layer should know *how* data is stored. They just call
> `repository.get_all()` and get a list back — they don't care if it came from a
> dict, a SQL query, or an API call.

**Why `dict` and not Pydantic models internally?**
Repositories typically return raw data (dicts or ORM objects). The controller or
service converts them to Pydantic models. This keeps the repository free from
any HTTP/API concerns.

---

### 3. Service Layer (Business Logic)

📁 `app/services/user_service.py`

```python
class UserService:
    def __init__(self, repository: UserRepository):
        self._repo = repository

    def create_user(self, data: UserCreate) -> dict:
        # Business rule: no duplicate emails
        for existing in self._repo.get_all():
            if existing["email"] == data.email:
                raise ValueError("Email is already taken")
        return self._repo.create(data)
```

**What is this?**
The service layer holds your **business rules** — the logic that is true
regardless of whether this is a web app, a CLI tool, or a mobile backend.

**Examples of business rules:**
- "A user's email must be unique."
- "Only admins can delete other users."
- "New users get 100 free credits."

**Key design rules:**
- The service **never imports** `Request`, `Response`, or `HTTPException`.
- It raises plain Python exceptions (`ValueError`) — the controller decides
  which HTTP status code that maps to.
- It receives a repository via its constructor (**dependency injection**).

> [!IMPORTANT]
> **Dependency Injection (DI)** means passing dependencies in from outside rather
> than creating them inside. `UserService` doesn't create its own repository — it
> *receives* one. This makes testing trivial: pass a fake repository in tests.

---

### 4. Controller Layer

📁 `app/controllers/user_controller.py`

```python
from fastapi import HTTPException, status

class UserController:
    def __init__(self, service: UserService):
        self._service = service

    def get_user(self, user_id: int) -> UserResponse:
        try:
            user = self._service.get_user(user_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        return UserResponse(**user)
```

**What is this?**
The controller is the **translator** between the HTTP world and the business
world.

| It knows about… | It does NOT know about… |
|---|---|
| `HTTPException`, status codes | How data is stored |
| Pydantic response models | Routing decorators (`@router.get`) |
| Which service method to call | Raw `Request` objects |

**What `HTTPException` does:**
When you `raise HTTPException(status_code=404, detail="...")`, FastAPI
automatically converts it into a JSON response like:

```json
{ "detail": "User with id 99 not found" }
```

with status code `404`. You don't write `return JSONResponse(...)` manually.

**What `UserResponse(**user)` does:**
The `**` operator unpacks the dict `{"id": 1, "name": "Alice", "email": "..."}` into
keyword arguments: `UserResponse(id=1, name="Alice", email="...")`. Pydantic
validates the data and returns a proper response object.

---

### 5. Router Layer

📁 `app/routers/user_router.py`

```python
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    return _controller.get_user(user_id)
```

**What is this?**
The router defines **which URL maps to which function**. It's the thinnest layer
— ideally just one line per endpoint that delegates to the controller.

**Key concepts:**

| Concept | Meaning |
|---|---|
| `APIRouter` | A mini-app that groups related endpoints. The main app includes it later. |
| `prefix="/users"` | Every route in this router starts with `/users`. |
| `tags=["Users"]` | Groups endpoints under "Users" in the Swagger UI docs. |
| `response_model=UserResponse` | Tells FastAPI to validate and serialize the return value as this Pydantic model. |
| `{user_id}` | A **path parameter** — FastAPI extracts it from the URL and passes it as a function argument. |
| `status_code=201` | Overrides the default 200 OK for the create endpoint. 201 means "Created". |

**Wiring (dependency chain):**
```
Repository  →  Service  →  Controller
      ↑ created once at module level in user_router.py
```

```python
_repository = UserRepository()
_service    = UserService(_repository)
_controller = UserController(_service)
```

Each layer receives the layer below it. This is manual dependency injection — 
simple and explicit for learning.

---

### 6. Middleware Layer

📁 `app/middleware/auth.py`

```python
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Check token → reject or proceed
        response = await call_next(request)
        return response
```

**What is middleware?**
Middleware is code that runs on **every single request** before it reaches any
router. It's like a security gate at the building entrance.

**How it works step-by-step:**

```
Client Request
     │
     ▼
┌─────────────────────┐
│   MIDDLEWARE         │  ← checks Authorization header
│   (auth.py)          │
└─────────┬───────────┘
          │  if token valid
          ▼
┌─────────────────────┐
│   ROUTER             │  ← matches URL to function
│   (user_router.py)   │
└─────────┬───────────┘
          │
          ▼
     Controller → Service → Repository
          │
          ▼
┌─────────────────────┐
│   MIDDLEWARE         │  ← can modify the response
│   (auth.py)          │
└─────────┬───────────┘
          │
          ▼
     Client Response
```

**Key concepts:**

| Concept | Meaning |
|---|---|
| `BaseHTTPMiddleware` | A helper from Starlette (FastAPI's foundation) that simplifies writing middleware. |
| `call_next(request)` | Passes the request to the next layer. If you don't call this, the request is blocked. |
| `dispatch()` | The method you override. It receives the request and must return a response. |
| `PUBLIC_PATHS` | A set of paths that skip auth (like `/docs` for the Swagger UI). |

**The dummy token:**
```
Authorization: Bearer my-secret-token-123
```
This is a hardcoded token for learning. In production, you'd use JWTs, OAuth, or
session cookies instead.

---

### 7. Entry Point — main.py

📁 `app/main.py`

```python
from fastapi import FastAPI

app = FastAPI(title="Clean Architecture Demo")

# Register middleware
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(user_router)
```

**What is this?**
The file that creates the FastAPI app and plugs everything together.

| Method | What it does |
|---|---|
| `FastAPI(...)` | Creates the ASGI application instance with metadata for the docs page. |
| `app.add_middleware(...)` | Registers a middleware class. It wraps every request/response cycle. |
| `app.include_router(...)` | Mounts a router's endpoints onto the main app. |

---

## Request Lifecycle — End to End

Here's what happens when you call `POST /users/` with a valid token:

```
1. HTTP Request arrives at uvicorn
   │
2. uvicorn passes it to the FastAPI (ASGI) app
   │
3. MIDDLEWARE (auth.py)
   │  → reads Authorization header
   │  → token matches "my-secret-token-123" ✅
   │  → calls call_next(request)
   │
4. ROUTER (user_router.py)
   │  → URL matches  POST /users/
   │  → FastAPI auto-validates the JSON body against UserCreate
   │  → calls create_user(body)
   │
5. CONTROLLER (user_controller.py)
   │  → calls self._service.create_user(data)
   │  → wraps result in UserResponse
   │
6. SERVICE (user_service.py)
   │  → checks business rules (duplicate email?)
   │  → calls self._repo.create(data)
   │
7. REPOSITORY (user_repository.py)
   │  → adds user to self._storage dict
   │  → returns the new user dict
   │
8. Response travels back up:
   Repository → Service → Controller → Router → Middleware → Client
   │
9. Client receives:
   HTTP 201  {"id": 1, "name": "Alice", "email": "alice@example.com"}
```

---

## Libraries Used & Why

This project uses only **two** external packages:

### 1. FastAPI

```
pip install fastapi
```

| What | Details |
|---|---|
| **What is it?** | A modern, high-performance Python web framework for building APIs. |
| **Why use it?** | Auto-generates interactive API docs (Swagger), auto-validates data with Pydantic, supports async, and is very beginner-friendly. |
| **Built on** | Starlette (for HTTP handling) and Pydantic (for data validation). Both are installed automatically with FastAPI. |

**Things from FastAPI/Starlette we use:**

| Import | From | Purpose |
|---|---|---|
| `FastAPI` | `fastapi` | The main application class |
| `APIRouter` | `fastapi` | Groups related endpoints together |
| `HTTPException` | `fastapi` | Raises an HTTP error that becomes a JSON response |
| `status` | `fastapi` | Constants like `HTTP_404_NOT_FOUND` (more readable than `404`) |
| `Request` | `fastapi` | Represents the incoming HTTP request |
| `JSONResponse` | `fastapi.responses` | Manually return a JSON response (used in middleware) |
| `BaseModel, Field` | `pydantic` | Define and validate data schemas |
| `BaseHTTPMiddleware` | `starlette.middleware.base` | Helper to write middleware as a class |
| `RequestResponseEndpoint` | `starlette.middleware.base` | Type hint for the `call_next` function |

### 2. Uvicorn

```
pip install uvicorn[standard]
```

| What | Details |
|---|---|
| **What is it?** | An ASGI server — the program that actually listens on a port and serves your FastAPI app. |
| **Why use it?** | FastAPI is just code — it needs a server to run. Uvicorn is lightning-fast, recommended by FastAPI's docs, and supports hot-reload for development. |
| **`[standard]`** | Installs optional extras for better performance (like `uvloop` and `httptools`). Not required, but recommended. |

> [!NOTE]
> **ASGI** (Asynchronous Server Gateway Interface) is the modern Python standard
> for async web servers. It's the successor to **WSGI** (used by Flask/Django).
> You don't need to understand ASGI internals — just know that uvicorn is the
> engine that makes FastAPI run.

---

## How to Run

- Create an venv
```bash
python -m venv venv
```

- Activate venv and run 
```bash
# 1. Activate your virtual environment
# Windows:
.\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
uvicorn app.main:app --reload --port 8000
```

| Flag | Meaning |
|---|---|
| `app.main:app` | "In the file `app/main.py`, find the variable called `app`." |
| `--reload` | Auto-restart the server when you save a file (dev only). |
| `--port 8000` | Listen on port 8000 (default is also 8000). |

Then open: **http://localhost:8000/docs** → Interactive Swagger UI (no auth needed).

---

## How to Test (curl examples)

### Health check (no auth)
```bash
curl http://localhost:8000/
```
```json
{"status": "ok", "message": "Clean Architecture Demo is running 🚀"}
```

### Create a user (auth required)
```bash
curl -X POST http://localhost:8000/users/ \
  -H "Authorization: Bearer my-secret-token-123" \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'
```
```json
{"id": 1, "name": "Alice", "email": "alice@example.com"}
```

### List all users
```bash
curl http://localhost:8000/users/ \
  -H "Authorization: Bearer my-secret-token-123"
```

### Get one user
```bash
curl http://localhost:8000/users/1 \
  -H "Authorization: Bearer my-secret-token-123"
```

### Delete a user
```bash
curl -X DELETE http://localhost:8000/users/1 \
  -H "Authorization: Bearer my-secret-token-123"
```

### Without auth (should fail)
```bash
curl http://localhost:8000/users/
```
```json
{"detail": "Missing or malformed Authorization header. Expected: 'Bearer my-secret-token-123'"}
```

---

## Upgrading to a Real Database

The whole point of this architecture is that **adding a database only changes
ONE file** — the repository.

### Step 1: Install a database library

```bash
pip install sqlalchemy asyncpg   # for PostgreSQL
# or
pip install sqlalchemy aiosqlite  # for SQLite
```

### Step 2: Create a database connection module

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```

### Step 3: Replace the repository internals

```python
# app/repositories/user_repository.py  — ONLY this file changes

class UserRepository:
    def __init__(self, db_session):
        self._db = db_session

    def get_all(self):
        return self._db.query(UserModel).all()   # SQLAlchemy query

    def create(self, data):
        user = UserModel(name=data.name, email=data.email)
        self._db.add(user)
        self._db.commit()
        return user
```

**Everything else (service, controller, router, middleware) stays exactly the same.**
That's the power of clean architecture. ✨

---

> [!TIP]
> **Next steps for learning:**
> - Add a `PUT /users/{id}` endpoint to update users.
> - Add a second resource (e.g., `Product`) with its own full layer stack.
> - Replace the dummy token with JWT authentication.
> - Swap the in-memory dict with SQLite using SQLAlchemy.
