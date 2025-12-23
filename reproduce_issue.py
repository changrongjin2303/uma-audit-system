import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        url = "http://localhost:8000/api/v1/analysis/10/priced-materials-analysis"
        response = await client.get(url, params={"limit": 1000})
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total in response: {data['total']}")
            print(f"Number of results in response: {len(data['results'])}")
            print("Results IDs:", [item['material_id'] for item in data['results']])
        else:
            print(response.text)

if __name__ == "__main__":
    asyncio.run(main())
