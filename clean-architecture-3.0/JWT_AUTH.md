# 🔐 JWT Authentication & Register/Login — Developer Guide

A step-by-step explanation of how JWT authentication, user registration,
and login are implemented in this project, written for developers who are
seeing these concepts for the first time.

---

## Table of Contents

1. [What Is JWT?](#1-what-is-jwt)
2. [What Is bcrypt?](#2-what-is-bcrypt)
3. [What Is CORS?](#3-what-is-cors)
4. [New Project Structure](#4-new-project-structure)
5. [Step-by-Step: How Register Works](#5-step-by-step-how-register-works)
6. [Step-by-Step: How Login Works](#6-step-by-step-how-login-works)
7. [Step-by-Step: How JWT Middleware Works](#7-step-by-step-how-jwt-middleware-works)
8. [File-by-File Walkthrough](#8-file-by-file-walkthrough)
   - [utils/security.py](#81-utilssecuritypy--the-toolbox)
   - [models/auth.py](#82-modelsauthpy--data-shapes)
   - [repositories/auth_repository.py](#83-repositoriesauth_repositorypy--data-storage)
   - [services/auth_service.py](#84-servicesauth_servicepy--business-logic)
   - [controllers/auth_controller.py](#85-controllersauth_controllerpy--http-bridge)
   - [routers/auth_router.py](#86-routersauth_routerpy--url-endpoints)
   - [middleware/auth.py](#87-middlewareauthpy--the-gate)
   - [main.py](#88-mainpy--wiring-it-all)
9. [Libraries Used & Why](#9-libraries-used--why)
10. [How to Test (curl examples)](#10-how-to-test-curl-examples)
11. [Common Questions](#11-common-questions)

---

## 1. What Is JWT?

**JWT** (JSON Web Token, pronounced "jot") is a compact, self-contained string
that carries information ("claims") and is digitally signed to prove it hasn't
been tampered with.

### A JWT has 3 parts separated by dots:

```
eyJhbGciOiJI...   .   eyJzdWIiOiJh...   .   SflKxwRJSM...
│                      │                      │
│  HEADER              │  PAYLOAD             │  SIGNATURE
│  (algorithm info)    │  (your data)         │  (proof of authenticity)
```

### Decoded example:

```json
// HEADER
{
  "alg": "HS256",    // signing algorithm
  "typ": "JWT"       // token type
}

// PAYLOAD (the "claims")
{
  "sub": "alice",           // subject — who this token is for
  "exp": 1700000000         // expiration — Unix timestamp
}

// SIGNATURE
HMACSHA256(
  base64(header) + "." + base64(payload),
  "your-secret-key"
)
```

### Why use JWT instead of a hardcoded token?

| Hardcoded Token | JWT |
|---|---|
| Same token for everyone | Each user gets their own token |
| Never expires | Has an expiration time (`exp` claim) |
| Cannot carry data | Carries data like username, roles |
| Must be stored in a list on the server | Server only needs the secret key to verify |
| Anyone who sees it can use it forever | Expires after a set time |

> [!NOTE]
> **"Stateless" authentication**: The server doesn't need to store tokens in a
> database. It can verify any token just by checking the signature with the
> secret key. That's the main advantage of JWT over session-based auth.

---

## 2. What Is bcrypt?

**bcrypt** is a password hashing algorithm designed specifically for passwords.

### Why not just store plain passwords?

If your database leaks, every user's password is exposed. Hashing is
**one-way** — you can go from password → hash, but not from hash → password.

### Why bcrypt instead of SHA-256 or MD5?

| Feature | MD5 / SHA-256 | bcrypt |
|---|---|---|
| Speed | Extremely fast (billions/sec) | Intentionally slow (~100ms) |
| Salt | You must add it yourself | Built-in automatic salting |
| Brute-force resistance | Weak (too fast) | Strong (adjustable cost factor) |
| Purpose | General hashing | Password hashing |

### How bcrypt works in this project:

```python
# Registration — hash the password before storing
import bcrypt

password = "secret123"
salt = bcrypt.gensalt()                              # random salt
hashed = bcrypt.hashpw(password.encode(), salt)      # → b'$2b$12$LJ3...'

# Login — verify the password against the stored hash
bcrypt.checkpw(password.encode(), hashed)            # → True
bcrypt.checkpw("wrong".encode(), hashed)             # → False
```

> [!IMPORTANT]
> **Never store passwords in plain text.** Always hash them.
> **Never write your own hashing.** Use a battle-tested library like bcrypt.

---

## 3. What Is CORS?

**CORS** (Cross-Origin Resource Sharing) is a browser security feature.

### The problem it solves:

```
Your React app:   http://localhost:3000
Your FastAPI:     http://localhost:8000
                  ↑ different port = different "origin"
```

Browsers block JavaScript from calling a different origin by default.
CORS headers tell the browser: "It's okay, I trust this origin."

### How it's configured in `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Which origins can call your API
    allow_credentials=True,     # Allow cookies/auth headers
    allow_methods=["*"],        # Allow all HTTP methods
    allow_headers=["*"],        # Allow all custom headers
)
```

### CORS vs Auth — They are different concerns:

| CORS | Auth Middleware |
|---|---|
| "Which **websites** can talk to me?" | "Which **users** can access this endpoint?" |
| Answers the browser's preflight `OPTIONS` request | Checks the `Authorization` header |
| Configured in `main.py` (app-level) | Defined in `middleware/auth.py` |
| Uses FastAPI's built-in `CORSMiddleware` | Uses custom `JWTAuthMiddleware` |

> [!TIP]
> CORS only matters for browsers. Tools like `curl` or Postman ignore CORS
> entirely. That's why you can `curl` an API without CORS issues.

---

## 4. New Project Structure

```
app/
├── main.py                            # UPDATED — CORS + JWT middleware
│
├── utils/                             # NEW ✨
│   ├── __init__.py
│   └── security.py                    # JWT + bcrypt helper functions
│
├── models/
│   ├── user.py                        # (unchanged)
│   └── auth.py                        # NEW ✨ — Auth request/response schemas
│
├── repositories/
│   ├── user_repository.py             # (unchanged)
│   └── auth_repository.py             # NEW ✨ — In-memory account storage
│
├── services/
│   ├── user_service.py                # (unchanged)
│   └── auth_service.py                # NEW ✨ — Register & login logic
│
├── controllers/
│   ├── user_controller.py             # (unchanged)
│   └── auth_controller.py             # NEW ✨ — Auth HTTP bridge
│
├── routers/
│   ├── user_router.py                 # (unchanged)
│   └── auth_router.py                 # NEW ✨ — /auth/register, /auth/login
│
└── middleware/
    └── auth.py                        # UPDATED — Dummy token → JWT verification
```

### What changed vs. the original:

| File | Change |
|---|---|
| `middleware/auth.py` | Replaced dummy token check with JWT decode |
| `main.py` | Added CORS middleware, included auth router |
| `requirements.txt` | Added `PyJWT` and `bcrypt` |
| Everything in the `auth_*` files | Brand new |
| `utils/security.py` | Brand new |
| All `user_*` files | **Zero changes** (that's clean architecture working!) |

---

## 5. Step-by-Step: How Register Works

Here's what happens when a client calls `POST /auth/register`:

```
Client sends:
{
    "username": "alice",
    "password": "secret123"
}
```

```
Step 1 → CORS Middleware
         Adds CORS headers. Passes request along.

Step 2 → JWT Auth Middleware
         Path is "/auth/register" → it's in PUBLIC_PATHS → skip auth.

Step 3 → Router (auth_router.py)
         URL matches POST /auth/register
         FastAPI validates JSON body against RegisterRequest schema:
           - username: at least 3 chars? ✅
           - password: at least 6 chars? ✅
         Calls controller.register(body)

Step 4 → Controller (auth_controller.py)
         Calls service.register(data)
         Wraps result in TokenResponse

Step 5 → Service (auth_service.py)
         Business rule: Does username "alice" already exist?
           → Asks repository: repo.exists("alice") → False ✅
         Hashes the password:
           "secret123" → "$2b$12$LJ3m4ys..."  (bcrypt)
         Stores the account:
           repo.create("alice", "$2b$12$LJ3m4ys...")
         Creates a JWT token:
           payload = {"sub": "alice", "exp": <30 min from now>}
           token = jwt.encode(payload, SECRET_KEY, "HS256")
         Returns: {"access_token": "eyJhbG...", "message": "Account created"}

Step 6 → Repository (auth_repository.py)
         Stores in memory:
           self._accounts["alice"] = {
               "username": "alice",
               "hashed_password": "$2b$12$LJ3m4ys..."
           }

Step 7 → Response flows back:
         Repository → Service → Controller → Router → Middleware → Client

Client receives:
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "message": "Account created successfully"
}
```

---

## 6. Step-by-Step: How Login Works

```
Client sends:
{
    "username": "alice",
    "password": "secret123"
}
```

```
Step 1 → CORS Middleware → pass through
Step 2 → JWT Auth Middleware → "/auth/login" is public → skip auth
Step 3 → Router → validates body against LoginRequest

Step 4 → Service (auth_service.py)
         Find the account:
           repo.find_by_username("alice")
           → {"username": "alice", "hashed_password": "$2b$12$LJ3..."}
         Verify the password:
           bcrypt.checkpw("secret123", "$2b$12$LJ3...")
           → True ✅
         Create JWT token:
           token = create_access_token({"sub": "alice"})
         Return: {"access_token": "eyJhbG...", "message": "Login successful"}

Step 5 → Controller wraps in TokenResponse
Step 6 → Client receives the token
```

### What if the password is wrong?

```
Step 4 → Service
         bcrypt.checkpw("wrongpass", "$2b$12$LJ3...")
         → False ❌
         Raise HTTPException(401, "Invalid username or password")
```

> [!IMPORTANT]
> Notice we say "Invalid username **or** password" — not "Invalid password".
> This is a security best practice: don't tell attackers which part is wrong.

---

## 7. Step-by-Step: How JWT Middleware Works

After login, the client includes the JWT in every request:

```
GET /users/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

```
Step 1 → CORS Middleware → adds headers, passes through

Step 2 → JWT Auth Middleware (middleware/auth.py)
         Path "/users/" → NOT in PUBLIC_PATHS → check auth

         Read header: "Bearer eyJhbGciOi..."
         Extract token: "eyJhbGciOi..."

         Decode the token:
           jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

           JWT library does 3 things:
             a) Splits: header.payload.signature
             b) Re-signs header.payload with SECRET_KEY
                → matches the signature? ✅ (not tampered)
             c) Checks "exp" claim
                → still in the future? ✅ (not expired)

           Returns: {"sub": "alice", "exp": 1700000000}

         Attach user to request:
           request.state.current_user = "alice"

         Call call_next(request) → passes to router

Step 3 → Router → Controller → Service → Repository
         (normal CRUD flow)

Step 4 → Response flows back through middleware to client
```

### What if the token is expired?

```
Step 2 → jwt.decode() checks "exp" claim
         1700000000 < current time?
         → Yes → raises jwt.ExpiredSignatureError
         → decode_access_token() catches it, returns None
         → Middleware returns 401: "Invalid or expired token"
```

### What if the token is tampered with?

```
Step 2 → jwt.decode() re-signs header.payload with SECRET_KEY
         → computed signature ≠ token's signature
         → raises jwt.InvalidTokenError
         → 401 Unauthorized
```

---

## 8. File-by-File Walkthrough

### 8.1. `utils/security.py` — The Toolbox

This file contains **pure utility functions** — no HTTP, no business logic.

```python
# --- Password Hashing ---

def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")
```

| Line | What it does |
|---|---|
| `bcrypt.gensalt()` | Generates a random salt (22 characters of randomness) |
| `.encode("utf-8")` | Converts the string to bytes (bcrypt works with bytes) |
| `bcrypt.hashpw(...)` | Combines salt + password → produces the hash |
| `.decode("utf-8")` | Converts bytes back to string for easy storage |

```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )
```

`bcrypt.checkpw()` extracts the salt from the stored hash, re-hashes the plain
password with that same salt, and checks if they match. You never compare
passwords directly — you always re-hash and compare hashes.

```python
# --- JWT ---

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

| Line | What it does |
|---|---|
| `data.copy()` | Don't mutate the original dict |
| `datetime.now(timezone.utc)` | Current time in UTC |
| `timedelta(minutes=30)` | Token expires 30 minutes from now |
| `to_encode["exp"] = expire` | Add the expiration claim |
| `jwt.encode(...)` | Sign the payload and produce the JWT string |

```python
def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None     # token was valid but has expired
    except jwt.InvalidTokenError:
        return None     # token is malformed or signature doesn't match
```

> [!NOTE]
> `algorithms=[ALGORITHM]` (with an **s**) is a list because `jwt.decode()` can
> accept multiple algorithms. We pass a list with just `"HS256"` to be explicit
> about what we accept — this prevents "algorithm confusion" attacks.

---

### 8.2. `models/auth.py` — Data Shapes

```python
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"     # always "bearer" for JWT
    message: str
```

**Why `token_type: str = "bearer"`?**
The OAuth2 standard says you should tell the client what kind of token this is.
"Bearer" means "whoever bears (carries) this token is authenticated." The client
then sends it as: `Authorization: Bearer <token>`.

---

### 8.3. `repositories/auth_repository.py` — Data Storage

```python
class AuthRepository:
    def __init__(self):
        self._accounts: dict[str, dict] = {}     # {"alice": {...}, "bob": {...}}

    def find_by_username(self, username: str) -> dict | None: ...
    def create(self, username: str, hashed_password: str) -> dict: ...
    def exists(self, username: str) -> bool: ...
```

Stores accounts in a dict. The key is the username, the value is a dict with
`username` and `hashed_password`. To upgrade to a database, you only change
this file.

---

### 8.4. `services/auth_service.py` — Business Logic

This is where the **rules** live:

**Register:**
1. Check if username already exists → 409 Conflict
2. Hash the password → store in repository
3. Create a JWT token → return it

**Login:**
1. Find the account by username → not found? → 401
2. Verify password with bcrypt → wrong? → 401
3. Create a JWT token → return it

---

### 8.5. `controllers/auth_controller.py` — HTTP Bridge

Thin layer — calls the service and wraps the result in a Pydantic model:

```python
def register(self, data: RegisterRequest) -> TokenResponse:
    result = self._service.register(data)
    return TokenResponse(**result)
```

---

### 8.6. `routers/auth_router.py` — URL Endpoints

```python
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", status_code=201)    # POST /auth/register
@router.post("/login")                         # POST /auth/login
```

Both are `POST` because they send sensitive data (passwords) in the request
body, not in the URL. `GET` would put the password in the URL, which gets
logged in browser history and server logs.

---

### 8.7. `middleware/auth.py` — The Gate

**Key changes from the dummy version:**

| Old (Dummy) | New (JWT) |
|---|---|
| `DUMMY_TOKEN = "my-secret-token-123"` | Removed — no hardcoded token |
| `token != DUMMY_TOKEN` | `decode_access_token(token)` returns `None` |
| No user identity | `request.state.current_user = payload["sub"]` |

**`PUBLIC_PATHS` now includes auth endpoints:**
```python
PUBLIC_PATHS = {
    "/",  "/health",  "/docs",  "/redoc",  "/openapi.json",
    "/auth/register",   # ← NEW
    "/auth/login",      # ← NEW
}
```

**`request.state`** is Starlette's way to attach arbitrary data to a request.
After the middleware sets `request.state.current_user = "alice"`, any downstream
code can read it. This avoids decoding the token twice.

---

### 8.8. `main.py` — Wiring It All

```python
# Middleware order matters! Last added = runs first.
app.add_middleware(CORSMiddleware, ...)   # Runs first (outermost)
app.add_middleware(JWTAuthMiddleware)     # Runs second (inner)
```

```
Request  →  CORS Middleware  →  JWT Middleware  →  Router
Response ←  CORS Middleware  ←  JWT Middleware  ←  Router
```

**Why CORS runs first?**
The browser sends an `OPTIONS` preflight request before the actual request.
CORS middleware must handle it and respond *before* the JWT middleware tries to
check for a token (which the preflight request won't have).

---

## 9. Libraries Used & Why

### New libraries added (only 2):

| Library | Install | What | Why |
|---|---|---|---|
| **PyJWT** | `pip install PyJWT` | Encode/decode JSON Web Tokens | Lightweight JWT library (~100 KB). Creates signed tokens and verifies them. |
| **bcrypt** | `pip install bcrypt` | Hash and verify passwords | Industry standard. Intentionally slow to resist brute-force. Auto-salts passwords. |

### Already included (from FastAPI/Starlette):

| Import | Why |
|---|---|
| `CORSMiddleware` from `fastapi.middleware.cors` | Handles browser cross-origin requests. Built into FastAPI, no extra install. |
| `BaseHTTPMiddleware` from `starlette.middleware.base` | Base class for custom middleware. Part of Starlette (which FastAPI includes). |
| `request.state` from Starlette's `Request` | Carry data (like current user) from middleware to route handlers. |

### Total project dependencies:

```
fastapi          — The web framework
uvicorn[standard] — The ASGI server
PyJWT            — JWT tokens
bcrypt           — Password hashing
```

That's it. Four packages.

---

## 10. How to Test (curl examples)

### Register a new user
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123"}'
```
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "message": "Account created successfully"
}
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123"}'
```
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "message": "Login successful"
}
```

### Use the token to access protected routes
```bash
# Copy the access_token from the login response
TOKEN="eyJhbGciOiJIUzI1NiIs..."

curl http://localhost:8000/users/ \
  -H "Authorization: Bearer $TOKEN"
```

### Without a token (should fail)
```bash
curl http://localhost:8000/users/
```
```json
{
  "detail": "Missing or malformed Authorization header. Expected: 'Bearer <your-jwt-token>'"
}
```

### With an expired/invalid token
```bash
curl http://localhost:8000/users/ \
  -H "Authorization: Bearer fake.token.here"
```
```json
{
  "detail": "Invalid or expired token. Please log in again."
}
```

---

## 11. Common Questions

### Why is auth in a separate file from the user CRUD?

**Separation of concerns.** Authentication (who are you?) and user management
(CRUD on user profiles) are different domains. They have their own models,
repositories, services, controllers, and routers — following the same layered
pattern. This makes each one independently testable and replaceable.

### Why not put JWT logic directly in the middleware?

The middleware's job is to **gate requests** — not to create tokens or manage
users. Token creation belongs in the service layer. The middleware only *reads*
and *verifies* tokens. This keeps each layer focused on one responsibility.

### Why is the secret key hardcoded?

For learning only! In production, use environment variables:

```python
import os
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-dev-key")
```

### How do I add roles (admin, user)?

Add a `role` field to the account, include it in the JWT payload, and check it
in the middleware or service:

```python
# In auth_service.py → register:
token = create_access_token({"sub": username, "role": "user"})

# In middleware/auth.py:
role = payload.get("role")
if request.url.path.startswith("/admin") and role != "admin":
    return JSONResponse(status_code=403, content={"detail": "Forbidden"})
```

### How do I add refresh tokens?

Create a second token type with a longer expiry (e.g., 7 days). When the access
token expires, the client sends the refresh token to get a new access token
without re-entering their password. Store refresh tokens in the repository so
you can revoke them.

> [!TIP]
> **Next steps for learning:**
> - Add a `GET /auth/me` endpoint that returns the current user's info (read from `request.state.current_user`).
> - Add roles and permissions.
> - Move `SECRET_KEY` to an environment variable using `python-dotenv`.
> - Add refresh tokens.
> - Connect to a real database (only the repository files change!).
