from aiogram.types import FSInputFile
from loader import bot
from config import config

async def notify_owner_client(data: dict):
    text = (
        "Тип заявки: КЛИЕНТ\n\n"
        f"👤 Имя: {data.get('name')}\n"
        f"📞 Телефон: {data.get('phone')}\n"
        f"✈️ Telegram: {data.get('username')}\n"
        f"🏙 Город / район: {data.get('city')}\n"
        f"🏠 Тип объекта: {data.get('property_type')}\n"
        f"📏 Площадь (м²): {data.get('area')}\n"
        f"🔨 Стадия ремонта: {data.get('stage')}\n"
        f"📝 Задача: {data.get('description')}\n"
    )
    for admin_id in config.tg_bot.admin_ids:
        try:
            await bot.send_message(admin_id, text)
        except Exception as e:
            print(f"Failed to notify admin {admin_id}: {e}")

async def notify_owner_partner(data: dict, files: list = None):
    text = (
        f"💼 Роль партнера: {data.get('role')}\n"
        f"👤 Имя: {data.get('name')}\n"
        f"📞 Телефон: {data.get('phone')}\n"
        f"✈️ Telegram: {data.get('username')}\n\n"
        "🏗 Объект:\n"
        f"🏙 Город / район: {data.get('city')}\n"
        f"🏠 Тип объекта: {data.get('property_type')}\n"
        f"📏 Площадь (м²): {data.get('area')}\n"
        f"🔨 Стадия: {data.get('stage')}\n"
        f"🔌 Наличие проекта: {data.get('project_presence')}\n"
        f"💰 Бюджет: {data.get('budget')}\n"
        f"💬 Комментарии: {data.get('comments')}\n\n"
        "📄 Условия партнёрства:\n"
    )
    
    # Handle partnership terms according to requirements
    terms_choice = data.get('terms_choice', '')
    terms_custom = data.get('terms_custom', '')
    
    if terms_choice == "Принимаю 10% кэшбэк":
        text += "кэшбэк 10% от стоимости работ.\n"
    elif terms_choice == "Хочу предложить свои условия" and terms_custom:
        text += f"{terms_custom}\n"
    else:
        text += f"{terms_choice}\n"
        if terms_custom:
            text += f"{terms_custom}\n"
    
    for admin_id in config.tg_bot.admin_ids:
        try:
            await bot.send_message(admin_id, text)
            if files:
                # files is a list of file_ids (photos/docs)
                # Note: sending file_id directly works if bot has access.
                # If these are new uploads from user, we can forward or send copy.
                # The prompt said "attached files/photos".
                # aiogram send_media_group or loop send_document/photo
                for file_obj in files:
                   # Simplification: just send them assuming they are valid file_ids or inputfiles
                   # Spec says "accept documents or images". We stored them in data['project_files'] potentially?
                   # This function takes 'files' arg.
                   
                   # We need to know content type to use correct method or use send_document for everything?
                   # Photos better as send_photo.
                   # For simplicity, if we stored file_id + type we can route.
                   # For now let's assume valid sending method.
                   
                   # Implementation detail in handler needs to pass struct: {'type': 'photo', 'id': ...}
                   if isinstance(file_obj, dict):
                       if file_obj['type'] == 'photo':
                           await bot.send_photo(admin_id, file_obj['id'])
                       else:
                           await bot.send_document(admin_id, file_obj['id'])
        except Exception as e:
            print(f"Failed to notify admin {admin_id}: {e}")
