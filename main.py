import asyncio
import logging
import sys
import time

from aiogram.exceptions import TelegramRetryAfter, TelegramAPIError
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
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Webhook deleted successfully")
    except Exception as e:
        logging.warning(f"Could not delete webhook: {e}")

    print("Bot started!")
    
    # Start polling task in background
    asyncio.create_task(poller.start_status_polling(bot))
    
    # Retry mechanism for polling
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        try:
            await dp.start_polling(bot)
            break  # If successful, break out of retry loop
        except TelegramRetryAfter as e:
            retry_count += 1
            wait_time = e.retry_after
            logging.warning(f"Rate limited. Waiting {wait_time} seconds before retry {retry_count}/{max_retries}")
            await asyncio.sleep(wait_time)
        except TelegramAPIError as e:
            retry_count += 1
            logging.error(f"Telegram API error: {e}. Retry {retry_count}/{max_retries}")
            await asyncio.sleep(5)  # Wait 5 seconds before retry
        except Exception as e:
            retry_count += 1
            logging.error(f"Unexpected error: {e}. Retry {retry_count}/{max_retries}")
            await asyncio.sleep(5)  # Wait 5 seconds before retry
    
    if retry_count >= max_retries:
        logging.error("Max retries exceeded. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped!")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)