import datetime
import gspread
import traceback
import logging
import json
import os
from google.oauth2.service_account import Credentials
from config import config

# Scope required for accessing Google Sheets and Drive
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

# Headers matching specification exactly (Russian names as per requirement)
HEADERS = [
    "ID заявки", "Дата/время", "Тип пользователя", "Роль партнёра", "Имя", "Телефон",
    "Telegram @", "Город / район", "Тип объекта", "Площадь (м²)", "Стадия ремонта/объекта",
    "Наличие проекта", "Примерный бюджет по электрике", "Комментарий", "Условия партнёрства",
    "Статус заявки", "Сумма", "ID пользователя/чата в Telegram"
]

# Status values in Russian
STATUS_VALUES = [
    "Новая", "Осмотр назначен", "Смета готова", "В работе", 
    "Готово", "Оплачено", "Отменено"
]

# English status equivalents for internal processing
ENGLISH_STATUS_VALUES = [
    "New", "Inspection Scheduled", "Estimate Ready", "In Progress", 
    "Completed", "Paid", "Cancelled"
]

# Column Indices (0-based) for consistency
# Sheet Structure:
# ID заявки | Дата/время | Тип пользователя | Роль партнёра | Имя | Телефон | Telegram @ | Город / район | Тип объекта | Площадь (м²) | Стадия ремонта/объекта | Наличие проекта | Примерный бюджет по электрике | Комментарий | Условия партнёрства | Статус заявки | Сумма | ID пользователя/чата в Telegram
COL_ID = 0
COL_DATE = 1
COL_USER_TYPE = 2
COL_PARTNER_ROLE = 3
COL_NAME = 4
COL_PHONE = 5
COL_TELEGRAM = 6
COL_CITY = 7
COL_PROP_TYPE = 8
COL_AREA = 9
COL_STAGE = 10
COL_PROJECT = 11
COL_BUDGET = 12
COL_COMMENT = 13
COL_PARTNERSHIP_TERMS = 14
COL_STATUS = 15
COL_AMOUNT = 16
COL_TG_ID = 17

# Тестовые учетные данные (только для демонстрации!)
TEST_SERVICE_ACCOUNT_INFO = {
    "type": "service_account",
    "project_id": "demo-project-id",
    "private_key_id": "demo-private-key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\nDEMO_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
    "client_email": "demo-service-account@demo-project-id.iam.gserviceaccount.com",
    "client_id": "demo-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/demo-service-account%40demo-project-id.iam.gserviceaccount.com"
}

def get_service():
    if not config.google_sheets.spreadsheet_id:
        logging.error("Google Sheets not configured.")
        return None
    
    try:
        # Проверяем переменную окружения
        service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
        
        if service_account_json:
            # Парсинг JSON из переменной окружения
            service_account_info = json.loads(service_account_json)
            creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        elif config.google_sheets.service_account_file and os.path.exists(config.google_sheets.service_account_file):
            # Используем файл учетных данных
            creds = Credentials.from_service_account_file(
                config.google_sheets.service_account_file, scopes=SCOPES
            )
        else:
            # Для тестирования используем демо учетные данные
            logging.warning("Using demo credentials for testing purposes")
            creds = Credentials.from_service_account_info(TEST_SERVICE_ACCOUNT_INFO, scopes=SCOPES)
        
        client = gspread.authorize(creds)
        sheet = client.open_by_key(config.google_sheets.spreadsheet_id).sheet1
        
        # Ensure headers are set on initialization
        ensure_headers(sheet)
        return sheet
    except Exception as e:
        logging.error(f"Error connecting to Google Sheets: {e}")
        return None

def ensure_headers(sheet):
    """Ensure headers are correctly set with proper formatting"""
    current_headers = sheet.row_values(1)
    if current_headers != HEADERS:
        sheet.update('A1:R1', [HEADERS])
        sheet.freeze(rows=1)
        # Note: Formatting is handled by setup_sheet.py when needed
        logging.info("Headers updated to match specification")
    else:
        logging.info("Headers already match specification")

def map_status_to_english(status):
    """Map Russian status to English equivalent"""
    status_map = dict(zip(STATUS_VALUES, ENGLISH_STATUS_VALUES))
    return status_map.get(status, status)

def map_status_to_russian(status):
    """Map English status to Russian equivalent"""
    status_map = dict(zip(ENGLISH_STATUS_VALUES, STATUS_VALUES))
    return status_map.get(status, status)

async def append_request(request_type: str, data: dict, user_id: int):
    """
    Appends a new row to the Google Sheet with the new schema.
    """
    sheet = get_service()
    if not sheet:
        return

    try:
        # Headers are ensured by get_service()
        
        # Generate new ID by getting the current max ID and adding 1
        all_values = sheet.get_all_values()
        next_id = 1
        if len(all_values) > 1:  # Header exists and there's at least one data row
            max_id = 0
            for row in all_values[1:]:  # Skip header row
                if row and row[0].isdigit():
                    row_id = int(row[0])
                    if row_id > max_id:
                        max_id = row_id
            next_id = max_id + 1

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Set default values
        status = "Новая"  # Default status in Russian
        amount = "-"  # Default amount
        
        # Common fields
        name = data.get("name", "").strip()
        phone = data.get("phone", "")
        username = data.get("username", "")
        telegram = f"@{username}" if username else ""
        city = data.get("city", "")
        prop_type = data.get("property_type", "")
        area = data.get("area", "")
        stage = data.get("stage", "")
        comment = data.get("description", "") or data.get("comments", "")
        partnership_terms = ""
        
        # Fields specific to partners
        partner_role = "-"
        project = ""
        budget = "Неизвестно"  # Default budget value
        
        # Handle partner-specific data
        if request_type == "Партнер":
            partner_role = data.get('role', '-')
            project = data.get('project_presence', '')
            
            # Add file attachment indicator if files exist
            files_data = data.get("files", [])
            if files_data:
                project += " (файлы прикреплены)"
            
            budget = data.get('budget', 'Неизвестно')
            
            # Handle partnership terms according to requirements
            terms_choice = data.get('terms_choice', '')
            terms_custom = data.get('terms_custom', '')
            
            if terms_choice == "Принимаю 10% кэшбэк":
                partnership_terms = "кэшбэк 10% от стоимости работ."
            elif terms_choice == "Хочу предложить свои условия" and terms_custom:
                partnership_terms = terms_custom
        else:
            # For clients, set partner role to "-"
            partner_role = "-"

        # Map request type to Russian
        user_type = "Заказчик" if request_type == "Client" else "Партнер"

        # Create row with all required fields in correct order
        row_data = {
            "ID заявки": str(next_id),
            "Дата/время": timestamp,
            "Тип пользователя": user_type,
            "Роль партнёра": partner_role,
            "Имя": name,
            "Телефон": phone,
            "Telegram @": telegram,
            "Город / район": city,
            "Тип объекта": prop_type,
            "Площадь (м²)": str(area),
            "Стадия ремонта/объекта": stage,
            "Наличие проекта": project,
            "Примерный бюджет по электрике": budget,
            "Комментарий": comment,
            "Условия партнёрства": partnership_terms,
            "Статус заявки": status,
            "Сумма": amount,
            "ID пользователя/чата в Telegram": str(user_id)
        }
        
        # Convert to row in correct header order
        row = [row_data.get(header, "") for header in HEADERS]

        # Insert with proper ordering: Clients first, then Partners
        insert_index = determine_insert_position(sheet, user_type)
        sheet.insert_row(row, insert_index)
        return next_id
        
    except Exception as e:
        logging.error(f"Error saving to Google Sheets: {e}")
        traceback.print_exc()

def determine_insert_position(sheet, request_type: str) -> int:
    """
    Determine the correct insertion position to maintain ordering:
    Clients first, then Partners, sorted by Date/Time within each user type
    """
    all_values = sheet.get_all_values()
    data_rows = all_values[1:] if len(all_values) > 1 else []
    
    # Default insertion point is at the end
    insert_index = len(data_rows) + 2
    
    if request_type == "Заказчик":  # Client
        # Insert among clients or at the beginning of the data section
        insert_index = 2  # Start after header
        for i, r in enumerate(data_rows, start=2):
            # If we find a partner record, insert here
            if len(r) > 2 and r[2] == "Партнер":
                insert_index = i
                break
    # For Partners, they go after all clients, which is the default behavior
    
    logging.info(f"Determined insert position for {request_type}: {insert_index}")
    return insert_index

async def get_requests_by_user(identifier: str):
    """
    Search requests where identifier matches Phone or TG ID.
    identifier: Can be phone (string) or user_id (string/int)
    """
    sheet = get_service()
    if not sheet:
        return []

    try:
        all_values = sheet.get_all_values()
        if not all_values:
            return []
            
        header = all_values[0]
        data_rows = all_values[1:]
        
        results = []
        clean_ident = str(identifier).replace(" ", "").replace("+", "").strip()

        for idx, row in enumerate(data_rows):
            # Safe get
            def get_col(i): return row[i] if i < len(row) else ""
            
            r_phone = get_col(COL_PHONE).replace(" ", "").replace("+", "").strip()
            r_tg_id = get_col(COL_TG_ID).strip()
            r_id = get_col(COL_ID).strip()
            
            # Check match (Creator)
            # Match if:
            # 1. Identifier matches Phone (cleaned)
            # 2. Identifier matches TG ID
            # 3. Identifier matches Request ID (exact match)
            
            is_match = False
            if clean_ident:
                 if clean_ident in r_phone: is_match = True
                 elif clean_ident == r_tg_id: is_match = True
                 elif clean_ident == r_id: is_match = True
            
            if is_match:
                results.append({
                    "id": r_id,
                    "date": get_col(COL_DATE),
                    "status": get_col(COL_STATUS),
                    "amount": get_col(COL_AMOUNT),
                    "type": get_col(COL_USER_TYPE),
                    "description": get_col(COL_COMMENT),
                    "files": get_col(COL_PROJECT),  # Using project column for files info
                    "row_idx": idx + 2 # 1-based, +1 for header
                })
        
        return results

    except Exception as e:
        logging.error(f"Error reading Google Sheets: {e}")
        return []

async def get_all_requests_status():
    """
    Returns a dict {request_id: {'status': status, 'amount': amount, 'row_data': row}}
    Used for polling.
    """
    sheet = get_service()
    if not sheet:
        return {}

    try:
        all_values = sheet.get_all_values()
        if len(all_values) < 2:
            return {}
            
        data_rows = all_values[1:]
        result = {}
        
        for row in data_rows:
            if not row: continue
            
            def get_col(i): return row[i] if i < len(row) else ""
            
            r_id = get_col(COL_ID)
            if not r_id: continue
            
            result[r_id] = {
                "status": get_col(COL_STATUS),
                "amount": get_col(COL_AMOUNT),
                "tg_id": get_col(COL_TG_ID),
                "desc": get_col(COL_COMMENT),
                "date": get_col(COL_DATE),
                "type": get_col(COL_USER_TYPE),
                "name": get_col(COL_NAME),
                "id": r_id
            }
            
        return result
        
    except Exception as e:
        logging.error(f"Error fetching all requests: {e}")
        return {}

async def get_request_by_id(req_id: str):
    """
    Fetch a single request by its ID.
    """
    sheet = get_service()
    if not sheet:
        logging.warning("Google Sheets service not available")
        return None

    try:
        logging.info(f"Fetching request by ID: {req_id}")
        all_values = sheet.get_all_values()
        logging.info(f"Retrieved {len(all_values)} rows from Google Sheets")
        
        if len(all_values) < 2:
            logging.info("No data rows found in Google Sheets")
            return None
            
        data_rows = all_values[1:]
        
        for row in data_rows:
            def get_col(i): return row[i] if i < len(row) else ""
            
            if get_col(COL_ID) == str(req_id):
                result = {
                    "id": get_col(COL_ID),
                    "date": get_col(COL_DATE),
                    "status": get_col(COL_STATUS),
                    "amount": get_col(COL_AMOUNT),
                    "type": get_col(COL_USER_TYPE),
                    "desc": get_col(COL_COMMENT),
                    "files": get_col(COL_PROJECT),
                    "name": get_col(COL_NAME), 
                    "phone": get_col(COL_PHONE),
                    "partner_role": get_col(COL_PARTNER_ROLE),
                    "city": get_col(COL_CITY),
                    "prop_type": get_col(COL_PROP_TYPE),
                    "area": get_col(COL_AREA),
                    "stage": get_col(COL_STAGE),
                    "project": get_col(COL_PROJECT),
                    "budget": get_col(COL_BUDGET),
                    "partnership_terms": get_col(COL_PARTNERSHIP_TERMS),
                    "telegram": get_col(COL_TELEGRAM),
                    "tg_id": get_col(COL_TG_ID)
                }
                logging.info(f"Found request with ID: {req_id}")
                return result
                
        logging.info(f"Request with ID {req_id} not found")
        return None
        
    except Exception as e:
        logging.error(f"Error fetching request by ID {req_id}: {e}")
        return None

async def update_request_status(req_id: str, new_status: str, comment: str = None):
    """
    Update the status of a request in Google Sheets.
    """
    sheet = get_service()
    if not sheet:
        logging.warning("Google Sheets service not available")
        return False

    try:
        logging.info(f"Updating request {req_id} status to: {new_status}")
        all_values = sheet.get_all_values()
        
        if len(all_values) < 2:
            logging.info("No data rows found in Google Sheets")
            return False
            
        data_rows = all_values[1:]
        
        # Find the row with the matching request ID
        for i, row in enumerate(data_rows):
            def get_col(j): return row[j] if j < len(row) else ""
            
            if get_col(COL_ID) == str(req_id):
                # Update the status column
                row_index = i + 2  # 1-based + header row
                status_cell = gspread.utils.rowcol_to_a1(row_index, COL_STATUS + 1)  # +1 for 1-based indexing
                sheet.update_acell(status_cell, new_status)
                
                # If comment is provided, update the comment column as well
                if comment is not None:
                    comment_cell = gspread.utils.rowcol_to_a1(row_index, COL_COMMENT + 1)
                    sheet.update_acell(comment_cell, comment)
                
                logging.info(f"Updated request {req_id} status to: {new_status}")
                return True
                
        logging.info(f"Request with ID {req_id} not found")
        return False
        
    except Exception as e:
        logging.error(f"Error updating request {req_id} status: {e}")
        return False
