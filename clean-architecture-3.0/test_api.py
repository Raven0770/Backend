"""Quick end-to-end validation of the API."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
AUTH = {"Authorization": "Bearer my-secret-token-123"}

# Test 1: Root (public, no auth)
r = client.get("/")
print(f"GET /           -> {r.status_code} {r.json()}")
assert r.status_code == 200

# Test 2: Users without auth (should fail 401)
r = client.get("/users/")
print(f"GET /users/ (no auth) -> {r.status_code}")
assert r.status_code == 401

# Test 3: Create user with auth
r = client.post("/users/", json={"name": "Alice", "email": "alice@example.com"}, headers=AUTH)
print(f"POST /users/    -> {r.status_code} {r.json()}")
assert r.status_code == 201

# Test 4: Duplicate email (should fail 409)
r = client.post("/users/", json={"name": "Bob", "email": "alice@example.com"}, headers=AUTH)
print(f"POST /users/ (dup) -> {r.status_code}")
assert r.status_code == 409

# Test 5: List users
r = client.get("/users/", headers=AUTH)
print(f"GET /users/     -> {r.status_code} {r.json()}")
assert r.status_code == 200

# Test 6: Get user by id
r = client.get("/users/1", headers=AUTH)
print(f"GET /users/1    -> {r.status_code} {r.json()}")
assert r.status_code == 200

# Test 7: Delete user
r = client.delete("/users/1", headers=AUTH)
print(f"DELETE /users/1 -> {r.status_code} {r.json()}")
assert r.status_code == 200

# Test 8: Get deleted user (should 404)
r = client.get("/users/1", headers=AUTH)
print(f"GET /users/1 (deleted) -> {r.status_code}")
assert r.status_code == 404

print("\n✅ All 8 tests passed!")
