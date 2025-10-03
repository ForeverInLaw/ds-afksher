import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
ACTIVITY_TYPE = os.getenv('ACTIVITY_TYPE', 'playing').lower()

VALID_ACTIVITY_TYPES = ['playing', 'watching', 'listening', 'streaming', 'competing']

if not DISCORD_TOKEN:
    raise ValueError(
        "DISCORD_TOKEN не найден в переменных окружения!\n"
        "Создайте .env файл и добавьте:\n"
        "DISCORD_TOKEN=ваш_токен"
    )

if CHANNEL_ID:
    try:
        CHANNEL_ID = int(CHANNEL_ID)
    except ValueError:
        print(f"⚠️ CHANNEL_ID должен быть числом. Текущее значение: {CHANNEL_ID}")
        CHANNEL_ID = None

if ACTIVITY_TYPE not in VALID_ACTIVITY_TYPES:
    print(f"⚠️ ACTIVITY_TYPE должен быть одним из: {', '.join(VALID_ACTIVITY_TYPES)}")
    print(f"   Текущее значение: {ACTIVITY_TYPE}. Используется 'playing' по умолчанию.")
    ACTIVITY_TYPE = 'playing'
