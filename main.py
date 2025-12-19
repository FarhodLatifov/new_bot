import asyncio
import logging
import sys

from loader import dp, bot
from handlers import start, client, partner, common, my_requests
from utils import poller

async def main() -> None:
    # Register routers
    dp.include_router(start.router)
    dp.include_router(common.router)
    dp.include_router(my_requests.router)
    dp.include_router(client.router)
    dp.include_router(partner.router)

    # Delete webhook/drop pending updates to prevent spam on restart
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("Bot started!")
    
    # Start polling task in background
    asyncio.create_task(poller.start_status_polling(bot))
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped!")
