from dataclasses import dataclass
from environs import Env

@dataclass
class TgBot:
    token: str
    admin_ids: list[int]

@dataclass
class GoogleSheets:
    service_account_file: str
    spreadsheet_id: str

@dataclass
class Config:
    tg_bot: TgBot
    google_sheets: GoogleSheets

def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMIN_IDS"))),
        ),
        google_sheets=GoogleSheets(
            service_account_file=env.str("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json"),
            spreadsheet_id=env.str("GOOGLE_SPREADSHEET_ID", ""),
        ),
    )

config = load_config()
