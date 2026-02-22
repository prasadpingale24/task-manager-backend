import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_signup_functional(client: AsyncClient):
    payload = {
        "email": "functional@example.com",
        "password": "testpassword123",
        "full_name": "Functional Tester",
        "role": "MANAGER"
    }
    response = await client.post("/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data

@pytest.mark.asyncio
async def test_login_and_me_functional(client: AsyncClient):
    # 1. Signup
    signup_payload = {
        "email": "me_test@example.com",
        "password": "testpassword123",
        "full_name": "Me Tester",
        "role": "MEMBER"
    }
    await client.post("/auth/signup", json=signup_payload)
    
    # 2. Login
    login_payload = {
        "email": signup_payload["email"],
        "password": signup_payload["password"]
    }
    login_response = await client.post("/auth/login", json=login_payload)
    assert login_response.status_code == 200
    token_data = login_response.json()
    token = token_data["access_token"]
    
    # 3. Get /me
    headers = {"Authorization": f"Bearer {token}"}
    me_response = await client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == signup_payload["email"]
    assert me_data["role"] == signup_payload["role"]

@pytest.mark.asyncio
async def test_project_lifecycle_functional(client: AsyncClient):
    # 1. Signup & Login
    signup_payload = {
        "email": "project_api@example.com",
        "password": "testpassword123",
        "full_name": "API Tester",
        "role": "MANAGER"
    }
    await client.post("/auth/signup", json=signup_payload)
    login_response = await client.post("/auth/login", json={
        "email": signup_payload["email"], "password": signup_payload["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create Project
    project_payload = {"name": "API Project", "description": "Created via API"}
    create_response = await client.post("/projects/", json=project_payload, headers=headers)
    assert create_response.status_code == 201
    project_id = create_response.json()["id"]
    
    # 3. List Projects
    list_response = await client.get("/projects/", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1
    
    # 4. Delete Project
    delete_response = await client.delete(f"/projects/{project_id}", headers=headers)
    assert delete_response.status_code == 204
    
    # 5. Verify Deletion
    get_response = await client.get(f"/projects/{project_id}", headers=headers)
    assert get_response.status_code == 404
