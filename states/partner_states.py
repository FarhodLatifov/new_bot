from aiogram.fsm.state import State, StatesGroup

class PartnerFSM(StatesGroup):
    role = State()
    name = State()
    phone = State()
    username = State()
    
    city = State()
    property_type = State()
    area = State()
    stage = State()
    
    project_presence = State()
    project_file = State()  # Conditional: if project is present
    
    budget = State()
    comments = State()
    
    terms_choice = State()
    terms_custom = State() # Conditional: if custom terms proposed
