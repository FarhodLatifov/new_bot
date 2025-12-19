import gspread
from google.oauth2.service_account import Credentials
from gspread_formatting import *
from config import config

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

def init_sheet():
    creds = Credentials.from_service_account_file(
        config.google_sheets.service_account_file, scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(config.google_sheets.spreadsheet_id).sheet1
    return sheet

def ensure_headers(sheet):
    """Check and set headers with formatting"""
    current_headers = sheet.row_values(1)
    if current_headers != HEADERS:
        sheet.update('A1:R1', [HEADERS])
        sheet.freeze(rows=1)
        fmt = cellFormat(
            textFormat=textFormat(bold=True),
            horizontalAlignment='CENTER',
            backgroundColor=color(0.9, 0.9, 0.9)
        )
        format_cell_range(sheet, 'A1:R1', fmt)
        # Set column widths for better display
        widths = [100, 150, 120, 150, 150, 120, 120, 150, 120, 100, 180, 150, 150, 200, 200, 150, 100, 200]
        for i, w in enumerate(widths, start=1):
            set_column_width(sheet, gspread.utils.rowcol_to_a1(1, i)[0], w)
        print("Headers fixed and formatted.")
    else:
        print("Headers already match specification.")

def append_request(sheet, data: dict):
    """
    Append a request to the sheet with proper ordering:
    Clients first, then Partners, sorted by Date/Time within each user type
    """
    ensure_headers(sheet)  # Check and fix headers before adding
    
    # Create row with all required fields in correct order
    row = [data.get(header, "") for header in HEADERS]
    
    # Get all existing data
    all_values = sheet.get_all_values()
    data_rows = all_values[1:] if len(all_values) > 1 else []
    
    # Default insertion point is at the end
    insert_index = len(data_rows) + 2
    
    # Logic for insertion: Clients first, then Partners
    user_type = data.get("Тип пользователя", "")
    if user_type == "Заказчик":  # Client
        # Insert among clients or at the beginning of the data section
        insert_index = 2  # Start after header
        for i, r in enumerate(data_rows, start=2):
            # If we find a partner record, insert here
            if len(r) > 2 and r[2] == "Партнер":
                insert_index = i
                break
    
    sheet.insert_row(row, insert_index)
    print(f"Заявка добавлена в строку {insert_index}.")

def setup_google_sheet():
    """Initialize the Google Sheet with proper headers and formatting"""
    try:
        sheet = init_sheet()
        ensure_headers(sheet)
        print("Google Sheet successfully initialized with proper headers and formatting!")
        return True
    except Exception as e:
        print(f"Error initializing Google Sheet: {e}")
        return False

if __name__ == "__main__":
    # Initialize the sheet without any mock data
    if setup_google_sheet():
        print("Setup completed successfully!")
    else:
        print("Setup failed!")
