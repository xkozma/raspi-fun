from tapo import ApiClient
import asyncio
import dotenv
import os
dotenv.load_dotenv()

async def get_tapo_device():
    client = ApiClient(os.getenv("TAPO_NAME"), os.getenv("TAPO_PASSWORD"))
    device = await client.l900(os.getenv("TAPO_IP"))
    return device

async def turn_on_lights():
    device = await get_tapo_device()
    await device.on()
    return "Lights turned on successfully"

async def turn_off_lights():
    device = await get_tapo_device()
    await device.off()
    return "Lights turned off successfully"

async def get_light_info():
    device = await get_tapo_device()
    info = await device.get_device_info_json()
    return f"Device Info: {info}"

async def main():
    info = await get_light_info()
    print(info)

if __name__ == "__main__":
    asyncio.run(main())