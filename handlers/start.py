from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

import texts
from keyboards import reply
from states.client_states import ClientFSM
from states.partner_states import PartnerFSM

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(texts.WELCOME_MESSAGE, reply_markup=reply.get_start_kb())

@router.message(F.text == texts.MENU_NEW_REQUEST)
async def new_request_handler(message: Message, state: FSMContext):
    # Show Client/Partner selection
    await message.answer("Выберите тип заявки:", reply_markup=reply.get_role_selection_kb())

# Legacy entry points need to remain reachable from the Role Selection menu
@router.message(F.text == texts.CLIENT_START_MSG)
async def client_start(message: Message, state: FSMContext):
    await state.set_state(ClientFSM.name)
    await state.update_data(user_type="client")
    await message.answer(texts.CLIENT_NAME, reply_markup=None)

@router.message(F.text == texts.PARTNER_START_MSG)
async def partner_start(message: Message, state: FSMContext):
    await state.set_state(PartnerFSM.role)
    await state.update_data(user_type="partner")
    await message.answer(texts.PARTNER_ROLE, reply_markup=reply.get_partner_role_kb())
