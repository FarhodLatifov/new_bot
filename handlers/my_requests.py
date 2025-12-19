import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest

import texts
from utils import google_sheets
from keyboards import reply

router = Router()

class MyRequestsFSM(StatesGroup):
    waiting_for_phone = State()

@router.message(F.text == texts.MENU_MY_REQUESTS)
async def my_requests_handler(message: Message, state: FSMContext):
    # Try to find by TG ID first
    requests = await google_sheets.get_requests_by_user(str(message.from_user.id))
    
    if requests:
        await show_requests_list(message, requests)
    else:
        # Ask for phone if not found by TG ID (or just as a fallback/search feature)
        # Spec says: "After pressing, the user enters a phone number or ID."
        await state.set_state(MyRequestsFSM.waiting_for_phone)
        await message.answer("Введите номер телефона или ID заявки для поиска:")

@router.message(MyRequestsFSM.waiting_for_phone)
async def search_requests_handler(message: Message, state: FSMContext):
    query = message.text.strip()
    requests = await google_sheets.get_requests_by_user(query)
    
    if requests:
        await state.clear()
        await show_requests_list(message, requests)
    else:
        await message.answer("Заявки не найдены. Попробуйте еще раз или вернитесь в меню.", reply_markup=reply.get_start_kb())
        # Keep state active to allow retry

@router.message(F.text == "🔄 Обновить")
async def refresh_requests_handler(message: Message):
    """Refresh and show the latest requests data"""
    requests = await google_sheets.get_requests_by_user(str(message.from_user.id))
    
    if requests:
        await show_requests_list(message, requests)
    else:
        await message.answer("У вас пока нет заявок.", reply_markup=reply.get_start_kb())

async def show_requests_list(message: Message, requests: list):
    text = "📂 <b>Ваши заявки:</b>\n\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    
    for req in requests:
        # Display: Request number, Type, Status, Date, Amount
        req_id = req['id']
        req_type = req['type']
        status = req['status']
        # Format date from YYYY-MM-DD HH:MM:SS to DD.MM.YYYY
        date_raw = req['date']
        if ' ' in date_raw:
            date_part = date_raw.split(' ')[0]
            if '-' in date_part:
                date_parts = date_part.split('-')
                date_formatted = f"{date_parts[2]}.{date_parts[1]}.{date_parts[0]}"
            else:
                date_formatted = date_part
        else:
            date_formatted = date_raw
            
        amount = req['amount'] or ""
        if amount:
            # Add spaces as thousand separators
            try:
                amount_num = int(amount.replace(' ', ''))
                amount_formatted = f"{amount_num:,}".replace(',', ' ')
                amount_text = f" | сумма: {amount_formatted}"
            except:
                amount_text = f" | сумма: {amount}"
        else:
            amount_text = ""
        
        # Format according to requirements:
        # «Заявка #123 | тип: Партнёр | статус: Смета готова | дата: 17.12.2025 | сумма: 150 000 (если есть) | [Детали]»
        row_text = f"Заявка #{req_id} | тип: {req_type} | статус: {status} | дата: {date_formatted}{amount_text}"
        text += f"{row_text}\n"
        
        # Add button for details
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=f"[Детали]", callback_data=f"req_details_{req_id}")
        ])
        
    # Add refresh button
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_requests")
    ])
        
    await message.answer(text, reply_markup=kb)

@router.callback_query(F.data.startswith("req_details_"))
async def request_details_handler(callback: CallbackQuery):
    # Acknowledge the callback immediately to prevent timeout
    await callback.answer()
    
    try:
        data = callback.data.split("_")
        # data format example: req_details_{req_id}
        if len(data) < 3:
             await callback.message.answer("Некорректные данные.")
             return
             
        req_id = data[2]
        
        # Use existing utility to search/get
        req_data = await google_sheets.get_request_by_id(req_id)
        
        if not req_data:
            await callback.message.answer("Заявка не найдена или была удалена.")
            return

        # Format details as a short summary
        # Extract just the basic information for a concise view
        details_text = (
            f"📋 <b>Заявка #{req_data['id']}</b>\n"
            f"👤 Тип: {req_data['type']}\n"
            f"📅 Дата: {req_data['date']}\n"
            f"📊 Статус: {req_data['status']}\n"
        )
        
        if req_data.get('amount'):
            details_text += f"💰 Сумма: {req_data['amount']}\n"
            
        # Add name if available
        if req_data.get('name'):
            details_text += f"👨‍💼 Имя: {req_data['name']}\n"
            
        # Add phone if available
        if req_data.get('phone'):
            details_text += f"📞 Телефон: {req_data['phone']}\n"
            
        # Add a short description (first 200 characters)
        if req_data.get('desc'):
            desc = req_data['desc']
            if len(desc) > 200:
                desc = desc[:200] + "..."
            details_text += f"\n📝 <b>Описание:</b>\n{desc}\n"
        
        if req_data.get('files'):
            # Provide info on files
            details_text += f"\n📂 <b>Вложения:</b> Есть вложения\n"
            
        await callback.message.answer(details_text)
        
    except Exception as e:
        logging.error(f"Error handling callback: {e}")
        await callback.message.answer("Ошибка при загрузке данных. Пожалуйста, попробуйте позже.")

@router.callback_query(F.data == "refresh_requests")
async def refresh_callback_handler(callback: CallbackQuery):
    """Handle refresh button press"""
    await callback.answer("Обновление данных...")
    
    try:
        requests = await google_sheets.get_requests_by_user(str(callback.from_user.id))
        
        if requests:
            text = "📂 <b>Ваши заявки (обновлено):</b>\n\n"
            
            kb = InlineKeyboardMarkup(inline_keyboard=[])
            
            for req in requests:
                # Display: Request number, Type, Status, Date, Amount
                req_id = req['id']
                req_type = req['type']
                status = req['status']
                # Format date from YYYY-MM-DD HH:MM:SS to DD.MM.YYYY
                date_raw = req['date']
                if ' ' in date_raw:
                    date_part = date_raw.split(' ')[0]
                    if '-' in date_part:
                        date_parts = date_part.split('-')
                        date_formatted = f"{date_parts[2]}.{date_parts[1]}.{date_parts[0]}"
                    else:
                        date_formatted = date_part
                else:
                    date_formatted = date_raw
                    
                amount = req['amount'] or ""
                if amount:
                    # Add spaces as thousand separators
                    try:
                        amount_num = int(amount.replace(' ', ''))
                        amount_formatted = f"{amount_num:,}".replace(',', ' ')
                        amount_text = f" | сумма: {amount_formatted}"
                    except:
                        amount_text = f" | сумма: {amount}"
                else:
                    amount_text = ""
                
                # Format according to requirements:
                # «Заявка #123 | тип: Партнёр | статус: Смета готова | дата: 17.12.2025 | сумма: 150 000 (если есть) | [Детали]»
                row_text = f"Заявка #{req_id} | тип: {req_type} | статус: {status} | дата: {date_formatted}{amount_text}"
                text += f"{row_text}\n"
                
                # Add button for details
                kb.inline_keyboard.append([
                    InlineKeyboardButton(text=f"[Детали]", callback_data=f"req_details_{req_id}")
                ])
                
            # Add refresh button
            kb.inline_keyboard.append([
                InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_requests")
            ])
            
            # Try to edit the message, but handle the case where content is the same
            try:
                await callback.message.edit_text(text, reply_markup=kb)
            except TelegramBadRequest as e:
                if "message is not modified" in str(e):
                    # Message content hasn't changed, so we don't need to update it
                    logging.info("Message content unchanged, skipping update")
                    pass
                else:
                    # Some other Telegram error
                    raise e
        else:
            await callback.message.answer("У вас пока нет заявок.", reply_markup=reply.get_start_kb())
            
    except Exception as e:
        logging.error(f"Error refreshing requests: {e}")
        await callback.message.answer("Ошибка при обновлении данных. Пожалуйста, попробуйте позже.")
