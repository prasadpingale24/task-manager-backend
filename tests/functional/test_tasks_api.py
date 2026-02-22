import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_private_task_isolation_functional(client: AsyncClient):
    # 1. Setup Manager, Member1, Member2
    async def signup_login(email, role):
        s_resp = await client.post("/auth/signup", json={"email": email, "password": "password", "full_name": email, "role": role})
        user_id = s_resp.json()["id"]
        l_resp = await client.post("/auth/login", json={"email": email, "password": "password"})
        return l_resp.json()["access_token"], user_id
    
    m_token, m_id = await signup_login("m@test.com", "MANAGER")
    m1_token, m1_id = await signup_login("m1@test.com", "MEMBER")
    m2_token, m2_id = await signup_login("m2@test.com", "MEMBER")
    
    # 2. Manager creates project and adds members
    p_resp = await client.post("/projects/", json={"name": "P", "description": "desc"}, headers={"Authorization": f"Bearer {m_token}"})
    p_id = p_resp.json()["id"]
    await client.post(f"/projects/{p_id}/members", json={"user_id": m1_id}, headers={"Authorization": f"Bearer {m_token}"})
    await client.post(f"/projects/{p_id}/members", json={"user_id": m2_id}, headers={"Authorization": f"Bearer {m_token}"})
    
    # 3. Member1 creates Private Task
    await client.post("/tasks/", json={"project_id": p_id, "title": "M1 Secret", "description": "top secret", "status": "ACTIVE"}, headers={"Authorization": f"Bearer {m1_token}"})
    
    # 4. Member2 lists tasks
    resp = await client.get(f"/tasks/?project_id={p_id}", headers={"Authorization": f"Bearer {m2_token}"})
    tasks = resp.json()
    # Member2 should see 0 tasks (assuming no common tasks yet)
    assert len(tasks) == 0
    
    # 5. Manager creates Common Task
    await client.post("/tasks/", json={"project_id": p_id, "title": "Team Goal", "description": "desc", "status": "PENDING"}, headers={"Authorization": f"Bearer {m_token}"})
    
    # 6. Member2 lists tasks again
    resp = await client.get(f"/tasks/?project_id={p_id}", headers={"Authorization": f"Bearer {m2_token}"})
    tasks = resp.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Team Goal"
    
@pytest.mark.asyncio
async def test_common_task_status_updates_functional(client: AsyncClient):
    # 1. Setup Manager, Member1
    async def signup_login(email, role):
        s_resp = await client.post("/auth/signup", json={"email": email, "password": "password", "full_name": email, "role": role})
        user_id = s_resp.json()["id"]
        l_resp = await client.post("/auth/login", json={"email": email, "password": "password"})
        return l_resp.json()["access_token"], user_id
    
    m_token, m_id = await signup_login("manager_tasks@test.com", "MANAGER")
    m1_token, m1_id = await signup_login("member_tasks@test.com", "MEMBER")
    
    p_resp = await client.post("/projects/", json={"name": "P", "description": "desc"}, headers={"Authorization": f"Bearer {m_token}"})
    p_id = p_resp.json()["id"]
    await client.post(f"/projects/{p_id}/members", json={"user_id": m1_id}, headers={"Authorization": f"Bearer {m_token}"})
    
    # Manager creates Common Task
    t_resp = await client.post("/tasks/", json={"project_id": p_id, "title": "Shared", "description": "desc", "status": "PENDING"}, headers={"Authorization": f"Bearer {m_token}"})
    t_id = t_resp.json()["id"]
    
    # Member1 updates status
    await client.patch(f"/tasks/{t_id}", json={"status": "COMPLETE"}, headers={"Authorization": f"Bearer {m1_token}"})
    
    # Manager views task
    resp = await client.get(f"/tasks/{t_id}", headers={"Authorization": f"Bearer {m_token}"})
    data = resp.json()
    assert "member_statuses" in data
    assert len(data["member_statuses"]) == 1
    assert data["member_statuses"][0]["status"] == "COMPLETE"
