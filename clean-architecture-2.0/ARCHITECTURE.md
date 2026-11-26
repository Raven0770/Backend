# FastAPI Layered Architecture — Developer Guide

This project is a minimal, production-style **FastAPI** backend built to demonstrate **Clean Layered Architecture** without any database or heavy third-party dependencies.

It implements five distinct architectural layers plus shared schemas and dependency injection:

1. **Middleware** (`app/middleware/auth.py`)
2. **Router Layer** (`app/routers/`)
3. **Controller Layer** (`app/controllers/`)
4. **Repository Layer** (`app/repositories/`)
5. **Resource Layer** (`app/resources/`)

*(Supporting modules: `app/schemas/` for data contracts, `app/dependencies.py` for Dependency Injection wiring, `app/config.py` for configuration, and `app/main.py` as the composition root.)*

---

## 1. Request & Dependency Flow

Every HTTP request travels **top-to-bottom** through the layers, while dependencies are **inverted** via interfaces (`Protocol`) and FastAPI's `Depends(...)`:

```text
  HTTP Client
       │
       ▼
┌───────────────────────────────────────────────────────────┐
│ 1. Middleware (app/middleware/auth.py)                    │
│    • Intercepts EVERY request before routing              │
│    • Skips public paths (/, /health, /docs, /openapi.json)│
│    • Checks "Authorization: Bearer <token>"               │
│    • Returns 401 immediately if invalid                   │
│    • Attaches UserContext to request.state.user           │
└──────────────────────────┬────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────┐
│ 2. Router Layer (app/routers/item_router.py)              │
│    • Matches URL path + HTTP method                       │
│    • Validates JSON body with Pydantic (ItemCreate)       │
│    • Resolves dependencies via app/dependencies.py        │
│    • Calls Controller method and returns HTTP response    │
└──────────────────────────┬────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────┐
│ 3. Controller Layer (app/controllers/item_controller.py)  │
│    • Enforces business rules (trimming, duplicate check)  │
│    • Raises domain errors (ItemNotFoundError,             │
│      DuplicateItemError) — knows NOTHING about HTTP       │
│    • Calls ItemRepository interface                       │
└──────────────────────────┬────────────────────────────────┘
                           │  (depends on ItemRepository Protocol)
                           ▼
┌───────────────────────────────────────────────────────────┐
│ 4. Repository Layer (app/repositories/item_repository.py) │
│    • Translates domain operations into storage operations │
│    • Converts raw storage records -> ItemResponse schemas │
│    • Today: InMemoryItemRepository                        │
│    • Tomorrow: SqlItemRepository (swap in dependencies.py)│
└──────────────────────────┬────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────┐
│ 5. Resource Layer (app/resources/memory_resource.py)      │
│    • Owns the raw backing data store / connection         │
│    • Managed by FastAPI lifespan (connect / disconnect)   │
│    • Today: Python dict + ID counter                      │
│    • Tomorrow: SQLAlchemy Engine / DB Connection Pool     │
└───────────────────────────────────────────────────────────┘
```

### Key Architectural Principle: Dependency Direction

- **Outer layers depend on inner contracts, never on storage details.**
- `ItemController` only knows about `ItemRepository` (a `Protocol`), **not** `InMemoryItemRepository` and **not** `MemoryResource`.
- Because `app/dependencies.py` wires `InMemoryItemRepository(MemoryResource)` into `ItemController`, swapping in a real database tomorrow requires **zero edits** to routers or controllers.

---

## 2. Layer-by-Layer Deep Dive

### Layer 1: Middleware (`app/middleware/auth.py`)

- **What it does:** Runs globally around every HTTP request before any route handler executes.
- **How it works here:**
  - `AuthMiddleware` subclasses Starlette's `BaseHTTPMiddleware` and overrides `dispatch(request, call_next)`.
  - Public routes listed in `settings.public_paths` (`/`, `/health`, `/docs`, `/redoc`, `/openapi.json`) and `OPTIONS` preflight requests are forwarded immediately with `await call_next(request)`.
  - Protected routes must send `Authorization: Bearer demo-secret-token` (or `admin-secret-token`).
  - If missing/invalid, the middleware short-circuits the pipeline and returns a `401 Unauthorized` `JSONResponse` directly—the Router and Controller are never called.
  - If valid, it stores `UserContext(username=..., token=...)` on `request.state.user`, calls `await call_next(request)`, and appends an `X-Authenticated-User` header to the outgoing response.
- **What it MUST NOT do:** Execute heavy business logic or query business entities directly when avoidable.

---

### Layer 2: Router Layer (`app/routers/health_router.py`, `app/routers/item_router.py`)

- **What it does:** Acts as the HTTP boundary (transport layer).
- **Responsibilities:**
  - Declares HTTP verbs (`@router.get`, `@router.post`, `@router.delete`), paths (`/items`, `/items/{item_id}`), status codes (`201`, `204`), and `response_model` serialization.
  - Uses `Depends(...)` to receive an `ItemController` and the current `UserContext`.
  - Attaches `HTTPBearer(auto_error=False)` on `item_router` so Swagger UI (`/docs`) displays the **Authorize** button for entering your Bearer token.
- **What it MUST NOT do:** Contain business rules (like checking duplicate names) or touch dictionaries/SQL queries directly.

---

### Layer 3: Controller Layer (`app/controllers/item_controller.py`)

- **What it does:** Implements application use cases and business logic.
- **How it works here:**
  - `ItemController` receives an `ItemRepository` via constructor injection (`__init__`).
  - `create_item(payload, user)` normalizes whitespace, checks if an item with the same name already exists (`DuplicateItemError`), and delegates creation to `self._repository.create(...)` using `user.username`.
  - `get_item(item_id)` and `delete_item(item_id)` raise `ItemNotFoundError` if the item is missing.
- **Why custom exceptions instead of `HTTPException`?**
  - Keeping `ItemController` free of `fastapi.HTTPException` makes business logic **transport-agnostic**—you can unit-test `ItemController` in plain Python or call it from a CLI/worker without an HTTP server.
  - `app/main.py` registers `@app.exception_handler` functions to map `ItemNotFoundError -> 404` and `DuplicateItemError -> 409` at the HTTP boundary.

---

### Layer 4: Repository Layer (`app/repositories/item_repository.py`)

- **What it does:** Abstracts **how** and **where** data is stored behind a clean interface.
- **How it works here:**
  - `ItemRepository` is a Python `Protocol` defining the required methods: `list_all`, `get_by_id`, `get_by_name`, `create`, and `delete`.
  - `InMemoryItemRepository` accepts `MemoryResource` and implements those methods against `self._resource.records`, converting raw `dict` entries into typed `ItemResponse` objects.
- **Why this matters:** The Repository acts as an anti-corruption boundary. Raw database rows (or in-memory dicts) never leak up into the Controller or Router.

---

### Layer 5: Resource Layer (`app/resources/memory_resource.py`)

- **What it does:** Owns the actual backing storage engine, client, or connection lifecycle.
- **How it works here:**
  - `MemoryResource` holds the in-memory dictionary (`_records`), sequential ID generator (`next_id()`), and `connect()` / `disconnect()` lifecycle methods.
  - On app startup, FastAPI's `lifespan` in `app/main.py` instantiates `MemoryResource`, calls `connect()` (which seeds 2 sample items), and stores it on `app.state.memory_resource`. On shutdown, it calls `disconnect()`.
- **Terminology Note (Resource vs. Schema):**
  - In some frameworks, "resource" refers to REST payload shapes (e.g., JSON fields). Here, payload shapes live in `app/schemas/item_schema.py` (Pydantic DTOs), while `app/resources/` represents the **infrastructure/data resource** (today: in-memory store; tomorrow: SQL/NoSQL database pool or external API client).

---

### Supporting Glue: Dependency Injection (`app/dependencies.py`) & Composition Root (`app/main.py`)

- **`app/dependencies.py`** connects the layers for each request:
  ```text
  get_memory_resource(request)
         │
         ▼
  get_item_repository(resource)  ──► returns InMemoryItemRepository(resource)
         │
         ▼
  get_item_controller(repo)      ──► returns ItemController(repo)
  ```
- **`app/main.py`** wires everything together in `create_app()`:
  1. Configures `lifespan` for Resource startup/shutdown.
  2. Attaches `AuthMiddleware`.
  3. Registers domain exception handlers (`404`, `409`).
  4. Mounts `health_router` and `item_router` (under `/api/v1`).

---

## 3. Libraries, Classes & Functions Used (What & Why)

This project intentionally uses **only 2 external runtime packages** (`fastapi` and `uvicorn`), plus standard libraries bundled with Python and FastAPI (`starlette`, `pydantic`).

### A. FastAPI (`fastapi`)

| Symbol | Where Used | What It Is | Why It Is Used Here |
| :--- | :--- | :--- | :--- |
| `FastAPI` | `app/main.py` | Main ASGI application class. | Serves as the root web application, handles routing, OpenAPI doc generation (`/docs`), lifespan hooks, and exception handlers. |
| `APIRouter` | `app/routers/*.py` | Modular route group container. | Splits endpoints by feature (`health_router`, `item_router`) instead of dumping all routes into `main.py`. |
| `Depends` | `app/dependencies.py`, `app/routers/*.py` | FastAPI's Dependency Injection marker. | Automatically resolves and injects `MemoryResource -> ItemRepository -> ItemController` and `UserContext` per request, making layers decoupled and easy to swap. |
| `HTTPException` | `app/dependencies.py` | Standard HTTP error exception. | Raised in `get_current_user` as a safeguard if `request.state.user` is missing, returning a clean `401` JSON response. |
| `Request` | `app/dependencies.py`, `app/main.py` | Represents the incoming HTTP request. | Used in `dependencies.py` to read `request.app.state.memory_resource` and `request.state.user`. |
| `Response` | `app/routers/item_router.py` | Represents a raw HTTP response. | Returned directly on `DELETE` (`204 No Content`) where no JSON body should be sent. |
| `status` | `app/dependencies.py`, `app/main.py`, `app/routers/item_router.py` | Named HTTP status code constants (e.g., `HTTP_201_CREATED`, `HTTP_404_NOT_FOUND`). | Avoids magic numbers and improves readability. |
| `HTTPBearer` | `app/routers/item_router.py` | FastAPI OpenAPI security helper for `Authorization: Bearer <token>`. | Adds the **Authorize** button in Swagger UI (`/docs`) so you can test protected endpoints in the browser. (`auto_error=False` leaves actual enforcement to `AuthMiddleware`.) |
| `@app.exception_handler` | `app/main.py` | Decorator registering custom exception-to-response translators. | Keeps `ItemController` HTTP-agnostic while automatically converting `ItemNotFoundError` (`404`) and `DuplicateItemError` (`409`) into JSON error responses. |

### B. Starlette (`starlette` — bundled inside FastAPI)

FastAPI is built on top of Starlette for low-level ASGI HTTP handling.

| Symbol | Where Used | What It Is | Why It Is Used Here |
| :--- | :--- | :--- | :--- |
| `BaseHTTPMiddleware` | `app/middleware/auth.py` | Base class for request/response middleware. | Gives a simple `async def dispatch(request, call_next)` hook to intercept every request before routing and modify responses on the way out. |
| `RequestResponseEndpoint` | `app/middleware/auth.py` | Type alias for the `call_next` coroutine function. | Provides strict type checking for `call_next` in `dispatch`. |
| `starlette.requests.Request` | `app/middleware/auth.py` | ASGI request wrapper. | Lets middleware read `request.url.path`, `request.method`, `request.headers`, and write `request.state.user`. |
| `starlette.responses.Response` | `app/middleware/auth.py` | Base HTTP response type. | Used as the return type annotation of `dispatch` and to add the `X-Authenticated-User` response header. |
| `JSONResponse` | `app/middleware/auth.py`, `app/main.py` | Serializes a Python dict into an `application/json` HTTP response. | Used by `AuthMiddleware` to return `401` immediately and by exception handlers in `main.py` to return `404` / `409`. |

### C. Pydantic (`pydantic` — bundled inside FastAPI)

| Symbol | Where Used | What It Is | Why It Is Used Here |
| :--- | :--- | :--- | :--- |
| `BaseModel` | `app/schemas/item_schema.py` | Data validation and serialization base class. | Automatically validates incoming JSON (`ItemCreate`), enforces types, generates OpenAPI schemas, and serializes outgoing objects (`ItemResponse`, `MessageResponse`). |
| `Field` | `app/schemas/item_schema.py` | Metadata and validation constraint descriptor. | Enforces `min_length`, `max_length`, defaults, and example values shown in `/docs`. |

### D. Uvicorn (`uvicorn`)

| Tool | Where Used | What It Is | Why It Is Used Here |
| :--- | :--- | :--- | :--- |
| `uvicorn` | CLI command (`uvicorn app.main:app --reload`) | Lightning-fast ASGI web server. | FastAPI defines *how* requests are handled, while Uvicorn opens the TCP socket, parses HTTP traffic, and runs FastAPI's async event loop. |

### E. Python Standard Library Utilities

| Symbol | Where Used | What It Is | Why It Is Used Here |
| :--- | :--- | :--- | :--- |
| `typing.Protocol` | `app/repositories/item_repository.py` | Structural subtyping interface (duck typing with static type checking). | Defines the `ItemRepository` contract without forcing implementations to inherit from a base class. Any class with matching methods satisfies it. |
| `typing.Annotated` | `app/dependencies.py`, `app/routers/*.py` | Attaches metadata (like `Depends(...)`) to type hints. | Recommended FastAPI style (`Annotated[ItemController, Depends(get_item_controller)]`) so type checkers see the real type while FastAPI sees the dependency provider. |
| `typing.AsyncIterator` | `app/main.py` | Return type annotation for async generators. | Accurately types the `@asynccontextmanager` `lifespan` function. |
| `typing.Any` | `app/resources/memory_resource.py` | Generic value type hint. | Used for the raw untyped dictionary records inside `MemoryResource` before the Repository converts them into `ItemResponse`. |
| `contextlib.asynccontextmanager` | `app/main.py` | Converts an `async def` with `yield` into an async context manager. | Standard FastAPI way to write `lifespan`: code before `yield` runs on startup; code after `yield` runs on shutdown. |
| `dataclasses.dataclass` | `app/config.py` | Lightweight Python class decorator for immutable config (`frozen=True`). | Stores app settings cleanly without needing an extra package like `pydantic-settings`. |
| `os.getenv` | `app/config.py` | Reads environment variables. | Allows overriding the dummy token via `DEMO_AUTH_TOKEN` without editing code. |
| `datetime`, `timezone` | `app/resources/`, `app/repositories/`, `app/schemas/` | Standard date/time library. | Generates UTC timestamps (`datetime.now(timezone.utc)`) for created items. |

---

## 4. Running & Testing the Project

### Start the Server

```bash
uvicorn app.main:app --reload
```

*(If `uvicorn` isn't on your global `PATH`, run `python -m uvicorn app.main:app --reload` using your Python executable.)*

### Try the Endpoints

1. **Public Health Check (no token required):**
   ```bash
   curl http://127.0.0.1:8000/health
   ```
   Returns `200 OK`:
   ```json
   {"status": "healthy", "message": "Backing resource state: connected"}
   ```

2. **Protected Route WITHOUT Token (blocked by `AuthMiddleware`):**
   ```bash
   curl -i http://127.0.0.1:8000/api/v1/items
   ```
   Returns `401 Unauthorized`:
   ```json
   {"detail": "Missing or invalid Authorization header. Expected 'Bearer <token>'."}
   ```

3. **List Items WITH Dummy Token:**
   ```bash
   curl -i http://127.0.0.1:8000/api/v1/items \
     -H "Authorization: Bearer demo-secret-token"
   ```
   Returns `200 OK`, includes response header `X-Authenticated-User: demo-user`, and returns the 2 seeded items.

4. **Create a New Item:**
   ```bash
   curl -X POST http://127.0.0.1:8000/api/v1/items \
     -H "Authorization: Bearer demo-secret-token" \
     -H "Content-Type: application/json" \
     -d '{"name": "SQLite Adapter", "description": "Planned for tomorrow"}'
   ```
   Returns `201 Created` with `"created_by": "demo-user"`.
   Sending the exact same `"name"` again returns `409 Conflict` (enforced by `ItemController`).

5. **Interactive API Docs:**
   Open `http://127.0.0.1:8000/docs` in your browser, click **Authorize**, enter `demo-secret-token`, and try every endpoint visually.

---

## 5. How to Attach a Real Database Tomorrow

Because the layers are separated behind `ItemRepository` and `app/dependencies.py`, adding a real database (SQLite, PostgreSQL, MySQL, etc.) takes **4 clean steps** without touching `ItemController`, `item_router.py`, or `AuthMiddleware`:

1. **Add your DB config** in `app/config.py` (e.g., `database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")`).
2. **Create a DB Resource** in `app/resources/database_resource.py`:
   - Holds the SQLAlchemy `Engine` and `sessionmaker` (or `asyncpg` pool).
   - Implements `connect()` and `disconnect()` and is initialized in `app/main.py` inside `lifespan`.
3. **Create a DB Repository** in `app/repositories/sql_item_repository.py`:
   - Implements the exact same `ItemRepository` protocol (`list_all`, `get_by_id`, `get_by_name`, `create`, `delete`) using a DB session and ORM model, returning `ItemResponse` objects.
4. **Update Dependency Wiring** in `app/dependencies.py`:
   - Swap `get_item_repository` to return `SqlItemRepository(session)` instead of `InMemoryItemRepository(resource)`.

That's it—every route, validation rule, duplicate check, and auth middleware check continues working identically on top of your new database!
