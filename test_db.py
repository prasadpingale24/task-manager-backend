import asyncio
import asyncpg
from urllib.parse import quote_plus
import os

async def test():
    user = "postgres"
    password = quote_plus("postgres26845@psp")
    host = "localhost"
    port = "5432"
    database = "task_manager_test"
    
    url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    print(f"Testing URL: {url}")
    try:
        conn = await asyncpg.connect(url)
        print("SUCCESS")
        await conn.close()
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test())
