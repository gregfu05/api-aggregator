import asyncio, os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()  
uri = os.getenv("MONGODB_URI")
dbn = os.getenv("MONGODB_DB")

async def main():
    client = AsyncIOMotorClient(uri)
    print("Pinging:", uri)
    print(await client.admin.command("ping"))
    db = client[dbn]
    await db["__init_check__"].insert_one({"ok": True})
    n = await db["__init_check__"].count_documents({})
    print(f"Connected to DB '{dbn}'. Init docs: {n}")

if __name__ == "__main__":
    asyncio.run(main())
