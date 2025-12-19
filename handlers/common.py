from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import texts
from states.client_states import ClientFSM
from states.partner_states import PartnerFSM

router = Router()

@router.message(F.text == texts.MENU_CONTACTS)
async def contacts_handler(message: Message, state: FSMContext):
    # Get user data to determine if user is client or partner
    user_data = await state.get_data()
    user_type = user_data.get("user_type")
    
    # Check user type and show appropriate contacts
    if user_type == "partner":
        await message.answer(texts.CONTACTS_PARTNER_TEXT)
    elif user_type == "client":
        await message.answer(texts.CONTACTS_CLIENT_TEXT)
    else:
        # Default to client text if no user type is set
        await message.answer(texts.CONTACTS_CLIENT_TEXT)

@router.message(F.text == texts.MENU_HELP)
async def help_handler(message: Message):
    await message.answer(texts.HELP_TEXT, parse_mode="HTML")
