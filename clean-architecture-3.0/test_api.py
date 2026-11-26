"""Quick end-to-end validation of JWT auth + user CRUD."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
passed = 0

def check(label, response, expected_status):
    global passed
    ok = response.status_code == expected_status
    symbol = "PASS" if ok else "FAIL"
    print(f"  [{symbol}] {label} -> {response.status_code} (expected {expected_status})")
    if not ok:
        print(f"         Body: {response.text[:200]}")
        raise AssertionError(f"FAILED: {label}")
    passed += 1

print("=== Auth Tests ===")
# 1. Register
r = client.post("/auth/register", json={"username": "alice", "password": "secret123"})
check("Register new user", r, 201)
token = r.json()["access_token"]
print(f"         Token: {token[:40]}...")

# 2. Duplicate register
r = client.post("/auth/register", json={"username": "alice", "password": "other123"})
check("Duplicate register (409)", r, 409)

# 3. Login
r = client.post("/auth/login", json={"username": "alice", "password": "secret123"})
check("Login correct password", r, 200)
login_token = r.json()["access_token"]

# 4. Login wrong password
r = client.post("/auth/login", json={"username": "alice", "password": "wrong"})
check("Login wrong password (401)", r, 401)

# 5. Login non-existent user
r = client.post("/auth/login", json={"username": "nobody", "password": "x"})
check("Login non-existent user (401)", r, 401)

print("\n=== Protected Routes (using JWT) ===")
AUTH = {"Authorization": f"Bearer {login_token}"}

# 6. Access without token
r = client.get("/users/")
check("GET /users/ without token (401)", r, 401)

# 7. Access with invalid token
r = client.get("/users/", headers={"Authorization": "Bearer fake.token.here"})
check("GET /users/ with bad token (401)", r, 401)

# 8. Create user with valid JWT
r = client.post("/users/", json={"name": "Alice", "email": "alice@example.com"}, headers=AUTH)
check("POST /users/ with JWT (201)", r, 201)

# 9. List users
r = client.get("/users/", headers=AUTH)
check("GET /users/ with JWT (200)", r, 200)

# 10. Get single user
r = client.get("/users/1", headers=AUTH)
check("GET /users/1 with JWT (200)", r, 200)

# 11. Delete user
r = client.delete("/users/1", headers=AUTH)
check("DELETE /users/1 with JWT (200)", r, 200)

# 12. Get deleted user
r = client.get("/users/1", headers=AUTH)
check("GET /users/1 after delete (404)", r, 404)

print("\n=== Public Routes ===")
# 13. Root
r = client.get("/")
check("GET / (public, 200)", r, 200)

# 14. Health
r = client.get("/health")
check("GET /health (public, 200)", r, 200)

print(f"\n✅ All {passed} tests passed!")
