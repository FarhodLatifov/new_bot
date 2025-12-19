from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

import texts
from keyboards import reply
from states.client_states import ClientFSM
from utils import notifications, google_sheets
from config import config

router = Router()

@router.message(ClientFSM.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(ClientFSM.phone)
    await message.answer(texts.CLIENT_PHONE)

@router.message(ClientFSM.phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(ClientFSM.username)
    await message.answer(texts.CLIENT_USERNAME)

@router.message(ClientFSM.username)
async def process_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await state.set_state(ClientFSM.city)
    await message.answer(texts.CLIENT_CITY)

@router.message(ClientFSM.city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(ClientFSM.property_type)
    await message.answer(texts.CLIENT_PROPERTY_TYPE, reply_markup=reply.get_client_property_kb())

@router.message(ClientFSM.property_type)
async def process_property_type(message: Message, state: FSMContext):
    await state.update_data(property_type=message.text)
    await state.set_state(ClientFSM.area)
    await message.answer(texts.CLIENT_AREA, reply_markup=ReplyKeyboardRemove())

@router.message(ClientFSM.area)
async def process_area(message: Message, state: FSMContext):
    await state.update_data(area=message.text)
    await state.set_state(ClientFSM.stage)
    await message.answer(texts.CLIENT_STAGE, reply_markup=reply.get_client_stage_kb())

@router.message(ClientFSM.stage)
async def process_stage(message: Message, state: FSMContext):
    await state.update_data(stage=message.text)
    await state.set_state(ClientFSM.description)
    await message.answer(texts.CLIENT_DESCRIPTION, reply_markup=ReplyKeyboardRemove())

@router.message(ClientFSM.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    
    # Save to Google Sheets
    await google_sheets.append_request("Client", data, message.from_user.id)
    
    # Notify Owner
    await notifications.notify_owner_client(data)
    
    # Notify User
    await message.answer(texts.CLIENT_COMPLETE.format(hours=texts.RESPONSE_HOURS))
    await state.clear()
