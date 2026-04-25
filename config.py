import os
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("TG_BOT_TOKEN не найден в .env файле")