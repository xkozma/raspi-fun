from tapo import ApiClient
import asyncio
import dotenv
import os
dotenv.load_dotenv()

async def main():
    client = ApiClient(os.getenv("TAPO_NAME"),os.getenv("TAPO_PASSWORD"))
    device = await client.l900(os.getenv("TAPO_IP"))
    await device.off()
    info = await device.get_device_info_json()
    print(f"Device Info: {info}")

# Run the async function
asyncio.run(main())