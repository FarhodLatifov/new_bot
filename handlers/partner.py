from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

import texts
from keyboards import reply
from states.partner_states import PartnerFSM
from utils import notifications, google_sheets
from config import config

router = Router()

# Step 2.1 Role (Started in start.py, logic continues here)
# We need to catch the answer to Role since start.py only set the state.

@router.message(PartnerFSM.role)
async def process_role(message: Message, state: FSMContext):
    role = message.text
    await state.update_data(role=role)
    
    # If "Другое" is selected, ask for text input
    if role == texts.BTN_OTHER:
        await state.set_state(PartnerFSM.name)
        await message.answer("Пожалуйста, уточните вашу роль:", reply_markup=ReplyKeyboardRemove())
    else:
        await state.set_state(PartnerFSM.name)
        await message.answer(texts.PARTNER_NAME, reply_markup=ReplyKeyboardRemove())

# Step 2.2 Contacts
@router.message(PartnerFSM.name)
async def process_name(message: Message, state: FSMContext):
    # Get current data to check if we're handling "Другое" role
    current_data = await state.get_data()
    current_role = current_data.get('role', '')
    
    # If we were handling "Другое" role, update the role with the custom text
    if current_role == texts.BTN_OTHER:
        await state.update_data(role=message.text)
    
    await state.update_data(name=message.text)
    await state.set_state(PartnerFSM.phone)
    await message.answer(texts.PARTNER_PHONE)

@router.message(PartnerFSM.phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(PartnerFSM.username)
    await message.answer(texts.PARTNER_USERNAME)

@router.message(PartnerFSM.username)
async def process_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await state.set_state(PartnerFSM.city)
    await message.answer(texts.PARTNER_CITY)

# Step 2.3 Object Info
@router.message(PartnerFSM.city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(PartnerFSM.property_type)
    await message.answer(texts.PARTNER_PROPERTY_TYPE, reply_markup=reply.get_partner_property_kb())

@router.message(PartnerFSM.property_type)
async def process_property_type(message: Message, state: FSMContext):
    await state.update_data(property_type=message.text)
    await state.set_state(PartnerFSM.area)
    await message.answer(texts.PARTNER_AREA, reply_markup=ReplyKeyboardRemove())

@router.message(PartnerFSM.area)
async def process_area(message: Message, state: FSMContext):
    await state.update_data(area=message.text)
    await state.set_state(PartnerFSM.stage)
    await message.answer(texts.PARTNER_STAGE, reply_markup=reply.get_partner_stage_kb())

@router.message(PartnerFSM.stage)
async def process_stage(message: Message, state: FSMContext):
    await state.update_data(stage=message.text)
    await state.set_state(PartnerFSM.project_presence)
    await message.answer(texts.PARTNER_PROJECT_AVAILABILITY, reply_markup=reply.get_partner_project_kb())

@router.message(PartnerFSM.project_presence)
async def process_project_presence(message: Message, state: FSMContext):
    answer = message.text
    await state.update_data(project_presence=answer)
    
    if answer == texts.BTN_YES_PROJECT:
        # Request file upload
        await state.set_state(PartnerFSM.project_file)
        await message.answer(texts.PARTNER_PROJECT_UPLOAD, reply_markup=ReplyKeyboardRemove())
    else:
        # Skip to budget
        await state.set_state(PartnerFSM.budget)
        await message.answer(texts.PARTNER_BUDGET, reply_markup=reply.get_partner_budget_kb())

# Handling File Upload
@router.message(PartnerFSM.project_file)
async def process_project_file(message: Message, state: FSMContext):
    # Check for document or photo or "Done" text
    if message.text and message.text.lower() in ["готово", "done", "далее", "next"]:
         # Proceed to budget
        await state.set_state(PartnerFSM.budget)
        await message.answer(texts.PARTNER_BUDGET, reply_markup=reply.get_partner_budget_kb())
        return

    file_info = None
    if message.photo:
        file_info = {'type': 'photo', 'id': message.photo[-1].file_id}
    elif message.document:
        file_info = {'type': 'document', 'id': message.document.file_id}
    
    if file_info:
        data = await state.get_data()
        current_files = data.get('files', [])
        current_files.append(file_info)
        await state.update_data(files=current_files)
        
        # Confirm receipt and ask for more or done
        # We need a keyboard with "Done"
        await message.answer("Файл получен. Отправьте еще файл или нажмите 'Готово'.", reply_markup=reply.get_done_kb())
    else:
        await message.answer("Пожалуйста, отправьте файл/фото или нажмите 'Готово'.")

@router.message(PartnerFSM.budget)
async def process_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await state.set_state(PartnerFSM.comments)
    await message.answer(texts.PARTNER_COMMENTS, reply_markup=ReplyKeyboardRemove())

@router.message(PartnerFSM.comments)
async def process_comments(message: Message, state: FSMContext):
    await state.update_data(comments=message.text)
    await state.set_state(PartnerFSM.terms_choice)
    await message.answer(texts.PARTNER_TERMS_INTRO, reply_markup=reply.get_partner_terms_kb())

# Terms Logic
@router.message(PartnerFSM.terms_choice)
async def process_terms_choice(message: Message, state: FSMContext):
    choice = message.text
    await state.update_data(terms_choice=choice)
    
    if choice == texts.PARTNER_TERMS_CUSTOM:
        await state.set_state(PartnerFSM.terms_custom)
        await message.answer(texts.PARTNER_TERMS_DESCRIBE, reply_markup=ReplyKeyboardRemove())
    else:
        # Accepted 10%
        # Finish flow
        await finish_partner_flow(message, state)

@router.message(PartnerFSM.terms_custom)
async def process_terms_custom(message: Message, state: FSMContext):
    await state.update_data(terms_custom=message.text)
    await finish_partner_flow(message, state)

async def finish_partner_flow(message: Message, state: FSMContext):
    data = await state.get_data()
    
    # Save to Sheets
    await google_sheets.append_request("Партнер", data, message.from_user.id)
    
    # Notify Owner
    files = data.get('files', [])
    await notifications.notify_owner_partner(data, files)
    
    # Notify User
    await message.answer(texts.PARTNER_COMPLETE, reply_markup=ReplyKeyboardRemove())
    await state.clear()
