import asyncio
from bot import bot, dp
from database import create_table

async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())