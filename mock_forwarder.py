import httpx

MOCK_BASE_URL = "https://4e83a728-67fe-4e6b-a915-d4edb9fdca38.mock.pstmn.io"

async def forward_to_mock(endpoint: str, payload: dict = None, method: str = "POST") -> dict:
    url = f"{MOCK_BASE_URL}{endpoint}"

    try:
        async with httpx.AsyncClient() as client:
            if method == "POST":
                response = await client.post(url, json=payload)
            elif method == "GET":
                response = await client.get(url)
            elif method == "PATCH":
                response = await client.patch(url, json=payload)
            elif method == "DELETE":
                response = await client.delete(url)
            else:
                return {"error": f"Unsupported method: {method}"}

            return response.json()
    except Exception as e:
        return {"error": str(e)}
