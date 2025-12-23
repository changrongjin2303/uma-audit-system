import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        # Project ID 10
        url = "http://localhost:8000/api/v1/reports/project/10/preview"
        response = await client.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            # Check guidance_price_materials (Table 2)
            guidance_materials = data.get('guidance_price_materials', [])
            print(f"Guidance Price Materials Count: {len(guidance_materials)}")
            print("IDs:", [item['id'] for item in guidance_materials])
        else:
            print(response.text)

if __name__ == "__main__":
    asyncio.run(main())
