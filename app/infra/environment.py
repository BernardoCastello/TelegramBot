import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN :
    raise RuntimeError("TELEGRAM_TOKEN  não encontrada no .env")


# Open AI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY :
    raise RuntimeError("OPENAI_API_KEY  não encontrada no .env")


# Postgres
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL :
    raise RuntimeError("DATABASE_URL  não encontrada no .env")