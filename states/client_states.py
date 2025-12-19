from aiogram.fsm.state import State, StatesGroup

class ClientFSM(StatesGroup):
    name = State()
    phone = State()
    username = State()
    city = State()
    property_type = State()
    area = State()
    stage = State()
    description = State()
