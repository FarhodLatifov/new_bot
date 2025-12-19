import json
import os
import sys

# Load messages from JSON file
try:
    with open('messages.json', 'r', encoding='utf-8') as f:
        _data = json.load(f)
except Exception as e:
    print(f"Error loading messages.json: {e}")
    sys.exit(1)

globals().update(_data)

# Messages
WELCOME_MESSAGE = _data.get("WELCOME_MESSAGE", "")
CLIENT_START_MSG = _data.get("CLIENT_START_MSG", "") # Keep as logic id, label in Menu
PARTNER_START_MSG = _data.get("PARTNER_START_MSG", "")

# Contact and Help Messages
CONTACTS_CLIENT_TEXT = _data.get("CONTACTS_CLIENT_TEXT", "")
CONTACTS_PARTNER_TEXT = _data.get("CONTACTS_PARTNER_TEXT", "")
HELP_TEXT = _data.get("HELP_TEXT", "") 

# Main Menu
MENU_NEW_REQUEST = "📝 Новые заявки"
MENU_MY_REQUESTS = "👤 Мои заявки"
MENU_CONTACTS = "📞 Контакты"
MENU_HELP = "❓ Помощь"

CONTACTS_MSG = """
📞 <b>Наши контакты:</b>
Телефон: +7 (XXX) XXX-XX-XX
Email: info@example.com
Сайт: example.com
"""

HELP_MSG = """
❓ <b>Помощь</b>
Используйте меню для навигации.
Для проверки статуса заявок нажмите "👤 Мои заявки".
"""

# Client Flow
CLIENT_NAME = _data.get("CLIENT_NAME", "")
CLIENT_PHONE = _data.get("CLIENT_PHONE", "")
CLIENT_USERNAME = _data.get("CLIENT_USERNAME", "")
CLIENT_CITY = _data.get("CLIENT_CITY", "")
CLIENT_PROPERTY_TYPE = _data.get("CLIENT_PROPERTY_TYPE", "")
CLIENT_AREA = _data.get("CLIENT_AREA", "")
CLIENT_STAGE = _data.get("CLIENT_STAGE", "")
CLIENT_DESCRIPTION = _data.get("CLIENT_DESCRIPTION", "")
CLIENT_COMPLETE = _data.get("CLIENT_COMPLETE", "")

# Partner Flow
PARTNER_ROLE = _data.get("PARTNER_ROLE", "")
PARTNER_NAME = _data.get("PARTNER_NAME", "")
PARTNER_PHONE = _data.get("PARTNER_PHONE", "")
PARTNER_USERNAME = _data.get("PARTNER_USERNAME", "")
PARTNER_CITY = _data.get("PARTNER_CITY", "")
PARTNER_PROPERTY_TYPE = _data.get("PARTNER_PROPERTY_TYPE", "")
PARTNER_AREA = _data.get("PARTNER_AREA", "")
PARTNER_STAGE = _data.get("PARTNER_STAGE", "")
PARTNER_PROJECT_AVAILABILITY = _data.get("PARTNER_PROJECT_AVAILABILITY", "")
PARTNER_PROJECT_UPLOAD = _data.get("PARTNER_PROJECT_UPLOAD", "")
PARTNER_BUDGET = _data.get("PARTNER_BUDGET", "")
PARTNER_COMMENTS = _data.get("PARTNER_COMMENTS", "")

PARTNER_TERMS_INTRO = _data.get("PARTNER_TERMS_INTRO", "")
PARTNER_TERMS_ACCEPT = _data.get("PARTNER_TERMS_ACCEPT", "")
PARTNER_TERMS_CUSTOM = _data.get("PARTNER_TERMS_CUSTOM", "")
PARTNER_TERMS_DESCRIBE = _data.get("PARTNER_TERMS_DESCRIBE", "")
PARTNER_COMPLETE = _data.get("PARTNER_COMPLETE", "")

# Buttons
BTN_APARTMENT = _data.get("BTN_APARTMENT", "")
BTN_HOUSE = _data.get("BTN_HOUSE", "")
BTN_COMMERCIAL = _data.get("BTN_COMMERCIAL", "")

BTN_RENOVATION_NOT_STARTED = _data.get("BTN_RENOVATION_NOT_STARTED", "")
BTN_ROUGH_STAGE = _data.get("BTN_ROUGH_STAGE", "")
BTN_FINISHING_STAGE = _data.get("BTN_FINISHING_STAGE", "")
BTN_FINISHED = _data.get("BTN_FINISHED", "")

BTN_DESIGNER = _data.get("BTN_DESIGNER", "")
BTN_FOREMAN = _data.get("BTN_FOREMAN", "")
BTN_REALTOR = _data.get("BTN_REALTOR", "")
BTN_DEVELOPER = _data.get("BTN_DEVELOPER", "")
BTN_PLUMBER = _data.get("BTN_PLUMBER", "")
BTN_OTHER = _data.get("BTN_OTHER", "")

BTN_PARTNER_STAGE_PROJECT = _data.get("BTN_PARTNER_STAGE_PROJECT", "")
BTN_PARTNER_STAGE_ROUGH = _data.get("BTN_PARTNER_STAGE_ROUGH", "")
BTN_PARTNER_STAGE_FINISHING = _data.get("BTN_PARTNER_STAGE_FINISHING", "")
BTN_PARTNER_STAGE_FINISHED = _data.get("BTN_PARTNER_STAGE_FINISHED", "")

BTN_YES_PROJECT = _data.get("BTN_YES_PROJECT", "")
BTN_PLAN_SCHEME = _data.get("BTN_PLAN_SCHEME", "")
BTN_NO_PROJECT = _data.get("BTN_NO_PROJECT", "")

BTN_BUDGET_UP_TO_100 = _data.get("BTN_BUDGET_UP_TO_100", "")
BTN_BUDGET_100_300 = _data.get("BTN_BUDGET_100_300", "")
BTN_BUDGET_300_800 = _data.get("BTN_BUDGET_300_800", "")
BTN_BUDGET_800_PLUS = _data.get("BTN_BUDGET_800_PLUS", "")
BTN_BUDGET_UNKNOWN = _data.get("BTN_BUDGET_UNKNOWN", "")

RESPONSE_HOURS = _data.get("RESPONSE_HOURS", 24)

# Statuses
STATUS_NEW = _data.get("STATUS_NEW", "Новая")
STATUS_INSPECTION = _data.get("STATUS_INSPECTION", "Осмотр назначен")
STATUS_ESTIMATE = _data.get("STATUS_ESTIMATE", "Смета готова")
STATUS_IN_PROGRESS = _data.get("STATUS_IN_PROGRESS", "В работе")
STATUS_COMPLETED = _data.get("STATUS_COMPLETED", "Готово")
STATUS_PAID = _data.get("STATUS_PAID", "Оплачено")
STATUS_CANCELLED = _data.get("STATUS_CANCELLED", "Отменено")

# Notification Messages
MSG_STATUS_CHANGED = _data.get("MSG_STATUS_CHANGED", "")
MSG_ESTIMATE_READY = _data.get("MSG_ESTIMATE_READY", "")
MSG_INSPECTION_SCHEDULED = _data.get("MSG_INSPECTION_SCHEDULED", "")
MSG_IN_PROGRESS = _data.get("MSG_IN_PROGRESS", "")
MSG_COMPLETED = _data.get("MSG_COMPLETED", "")
MSG_PAID = _data.get("MSG_PAID", "")
MSG_CANCELLED = _data.get("MSG_CANCELLED", "")
