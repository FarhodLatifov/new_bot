from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import texts

def get_start_kb() -> ReplyKeyboardMarkup:
    """
    Returns the new main menu keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.MENU_NEW_REQUEST)],
            [KeyboardButton(text=texts.MENU_MY_REQUESTS)],
            [KeyboardButton(text=texts.MENU_CONTACTS), KeyboardButton(text=texts.MENU_HELP)]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_role_selection_kb() -> ReplyKeyboardMarkup:
    """
    Selection between Client and Partner for "New Request" flow
    """
    builder = ReplyKeyboardBuilder()
    builder.button(text=texts.CLIENT_START_MSG)
    builder.button(text=texts.PARTNER_START_MSG)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def get_client_property_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for text in [texts.BTN_APARTMENT, texts.BTN_HOUSE, texts.BTN_COMMERCIAL]:
        builder.button(text=text)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_client_stage_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    items = [
        texts.BTN_RENOVATION_NOT_STARTED,
        texts.BTN_ROUGH_STAGE,
        texts.BTN_FINISHING_STAGE,
        texts.BTN_FINISHED
    ]
    for text in items:
        builder.button(text=text)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_partner_role_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    roles = [
        texts.BTN_DESIGNER, texts.BTN_FOREMAN, texts.BTN_REALTOR,
        texts.BTN_DEVELOPER, texts.BTN_PLUMBER, texts.BTN_OTHER
    ]
    for role in roles:
        builder.button(text=role)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_partner_property_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    # Same as client but with "Other"? Spec says: Apartment, House, Commercial, Other
    items = [texts.BTN_APARTMENT, texts.BTN_HOUSE, texts.BTN_COMMERCIAL, texts.BTN_OTHER]
    for text in items:
        builder.button(text=text)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_partner_stage_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    items = [
        texts.BTN_PARTNER_STAGE_PROJECT,
        texts.BTN_PARTNER_STAGE_ROUGH,
        texts.BTN_PARTNER_STAGE_FINISHING,
        texts.BTN_PARTNER_STAGE_FINISHED
    ]
    for text in items:
        builder.button(text=text)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_partner_project_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    items = [texts.BTN_YES_PROJECT, texts.BTN_PLAN_SCHEME, texts.BTN_NO_PROJECT]
    for text in items:
        builder.button(text=text)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_partner_budget_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    items = [
        texts.BTN_BUDGET_UNKNOWN
    ]
    for text in items:
        builder.button(text=text)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_partner_terms_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=texts.PARTNER_TERMS_ACCEPT)
    builder.button(text=texts.PARTNER_TERMS_CUSTOM)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_done_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Готово")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    
