import asyncio
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from utils import google_sheets
import texts

# Store valid previous states to compare against
# Structure: {request_id: "status_string"}
previous_statuses = {}
# Store previous full data to detect any changes, not just status
previous_full_data = {}

async def start_status_polling(bot: Bot):
    """
    Periodically checks Google Sheets for status changes and notifies users.
    Also detects any data changes in the spreadsheet.
    """
    logging.info("Starting status poller...")
    global previous_statuses, previous_full_data
    
    # Initial fetch to populate state without notifying
    initial_data = await google_sheets.get_all_requests_status()
    previous_statuses = {k: v['status'] for k, v in initial_data.items()}
    previous_full_data = initial_data.copy()
    
    while True:
        try:
            await asyncio.sleep(60) # Poll every 60 seconds
            
            current_data = await google_sheets.get_all_requests_status()
            
            for req_id, data in current_data.items():
                new_status = data['status']
                old_status = previous_statuses.get(req_id)
                
                # Check for status change
                if old_status and new_status != old_status:
                    # Status changed!
                    # Notify user if we have their TG ID
                    tg_id = data.get('tg_id')
                    if tg_id and tg_id.isdigit():
                        try:
                            # Extract additional information for the notification
                            comment = data.get('desc', 'нет')
                            if not comment:
                                comment = 'нет'
                            
                            # For estimate link, we'll check if there are files
                            estimate_link = data.get('files', 'не заполнено')
                            if not estimate_link:
                                estimate_link = 'не заполнено'
                            
                            # Map Russian status to English for notification
                            english_status = google_sheets.map_status_to_english(new_status)
                            
                            # Construct message using the specification template:
                            # "Your request #<Request ID> status has changed to: <New Status>.
                            # Comment: <Comment from the table, if any>.
                            # Estimate: <Link or note if field filled>"
                            message = f"Статус вашей заявки #{req_id} изменён на: {english_status}.\nКомментарий: {comment}.\nСмета: {estimate_link}"
                             
                            await bot.send_message(int(tg_id), message)
                            logging.info(f"Notified user {tg_id} about status change for req {req_id}")
                        except TelegramAPIError as e:
                            logging.error(f"Failed to notify user {tg_id} via Telegram: {e}")
                        except Exception as e:
                            logging.error(f"Failed to notify user {tg_id}: {e}")
                
                # Check for any data changes (not just status)
                old_data = previous_full_data.get(req_id)
                if old_data and data != old_data:
                    # Any data changed - log it
                    logging.info(f"Data changed for request {req_id}")
                    # We could implement additional notifications or actions here if needed
                    
                # Update state
                previous_statuses[req_id] = new_status
                previous_full_data[req_id] = data.copy()
                
        except Exception as e:
            logging.error(f"Error in poller loop: {e}")
            await asyncio.sleep(60) # Wait before retry
