import discord
import asyncio
import logging
from datetime import datetime, timedelta
from config import DISCORD_TOKEN, CHANNEL_ID, ACTIVITY_TYPE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

client = discord.Client()
start_time = None

async def clear_activity():
    """Очищает активность (статус)"""
    try:
        await client.change_presence(activity=None)
        logger.info(f'✅ Активность очищена')
    except Exception as e:
        logger.error(f'❌ Ошибка при очистке активности: {e}')

def format_time(minutes):
    """Форматирует время в читаемый формат"""
    if minutes < 60:
        if minutes == 0:
            return "0 минут"
        return f"{minutes} минут{'у' if minutes == 1 else 'ы' if 2 <= minutes <= 4 else ''}"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if hours < 24:
        hour_str = f"{hours} час{'а' if 2 <= hours <= 4 else 'ов' if hours > 4 else ''}"
        if remaining_minutes > 0:
            min_str = f"{remaining_minutes} минут{'у' if remaining_minutes == 1 else 'ы' if 2 <= remaining_minutes <= 4 else ''}"
            return f"{hour_str} {min_str}"
        return hour_str
    
    days = hours // 24
    remaining_hours = hours % 24
    day_str = f"{days} день{'дня' if 2 <= days <= 4 else 'дней' if days > 4 else ''}"
    if remaining_hours > 0:
        hour_str = f"{remaining_hours} час{'а' if 2 <= remaining_hours <= 4 else 'ов' if remaining_hours > 4 else ''}"
        return f"{day_str} {hour_str}"
    return day_str

@client.event
async def on_connect():
    logger.info('🔌 Подключено к Discord WebSocket')

@client.event
async def on_disconnect():
    logger.warning('❌ Отключено от Discord WebSocket')
    await clear_activity()

def get_activity_type():
    """Возвращает тип активности Discord по строковому значению"""
    activity_map = {
        'playing': discord.ActivityType.playing,
        'watching': discord.ActivityType.watching,
        'listening': discord.ActivityType.listening,
        'streaming': discord.ActivityType.streaming,
        'competing': discord.ActivityType.competing
    }
    return activity_map.get(ACTIVITY_TYPE, discord.ActivityType.playing)

def get_activity_prefix():
    """Возвращает русский префикс для типа активности"""
    prefix_map = {
        'playing': 'Играет в',
        'watching': 'Смотрит',
        'listening': 'Слушает',
        'streaming': 'Стримит',
        'competing': 'Соревнуется в'
    }
    return prefix_map.get(ACTIVITY_TYPE, 'Играет в')

async def update_activity():
    """Обновляет активность каждую минуту с таймером"""
    global start_time
    await client.wait_until_ready()
    
    start_time = datetime.now()
    logger.info(f'⏰ Таймер активности запущен (тип: {ACTIVITY_TYPE})')
    
    while not client.is_closed():
        try:
            elapsed = datetime.now() - start_time
            minutes = int(elapsed.total_seconds() / 60)
            
            time_str = format_time(minutes)
            activity_text = f"афкшу уже {time_str}"
            
            # Для пользовательских аккаунтов используем разные типы активностей
            if ACTIVITY_TYPE == 'playing':
                # Используем Game для "Играет в..."
                activity = discord.Game(name=activity_text)
                logger.info(f'✏️ Активность обновлена: Играет в "{activity_text}"')
            elif ACTIVITY_TYPE == 'streaming':
                # Для стриминга нужен URL
                activity = discord.Streaming(name=activity_text, url="https://twitch.tv/afk")
                logger.info(f'✏️ Активность обновлена: Стримит "{activity_text}"')
            else:
                # Для остальных типов используем Activity
                activity_type = get_activity_type()
                activity_prefix = get_activity_prefix()
                activity = discord.Activity(type=activity_type, name=activity_text)
                logger.info(f'✏️ Активность обновлена: {activity_prefix} "{activity_text}"')
            
            await client.change_presence(activity=activity)

            
            await asyncio.sleep(60)
            
        except discord.HTTPException as e:
            if e.status == 429:
                logger.warning(f'⚠️ Rate limit: слишком частые изменения активности')
                await asyncio.sleep(300)
            else:
                logger.error(f'❌ Ошибка HTTP при изменении активности: {e}')
                await asyncio.sleep(60)
        except Exception as e:
            logger.error(f'❌ Ошибка при обновлении активности: {e}')
            await asyncio.sleep(60)

@client.event
async def on_ready():
    global start_time
    
    logger.info('=' * 50)
    logger.info(f'✅ Бот готов к работе!')
    logger.info(f'👤 Пользователь: {client.user}')
    logger.info(f'🆔 ID: {client.user.id}')
    
    if CHANNEL_ID:
        try:
            channel = client.get_channel(CHANNEL_ID)
            if channel:
                logger.info(f'📺 Найден канал: {channel.name} ({CHANNEL_ID})')
                logger.info(f'📝 Тип канала: {type(channel).__name__}')
                
                if isinstance(channel, discord.VoiceChannel):
                    logger.info('🎤 Это голосовой канал - подключаюсь...')
                    try:
                        voice_client = await channel.connect()
                        logger.info(f'✅ Успешно подключился к голосовому каналу: {channel.name}')
                        logger.info('🔊 Статус: В ГОЛОСОВОМ КАНАЛЕ')
                        
                        client.loop.create_task(update_activity())
                        logger.info('⏰ Запущен таймер обновления активности')
                    except discord.ClientException as e:
                        logger.error(f'❌ Ошибка подключения к голосовому каналу: {e}')
                    except Exception as e:
                        logger.error(f'❌ Неожиданная ошибка при подключении: {e}')
                elif isinstance(channel, discord.TextChannel):
                    logger.info('💬 Это текстовый канал - бот будет онлайн')
                    client.loop.create_task(update_activity())
                    logger.info('⏰ Запущен таймер обновления активности')
                else:
                    logger.info(f'📌 Тип канала: {type(channel).__name__}')
            else:
                logger.warning(f'⚠️ Канал с ID {CHANNEL_ID} не найден')
        except Exception as e:
            logger.error(f'❌ Ошибка при получении канала: {e}')
    else:
        logger.info('📺 CHANNEL_ID не указан - бот просто будет онлайн')
        client.loop.create_task(update_activity())
        logger.info('⏰ Запущен таймер обновления активности')
    
    logger.info(f'🕐 Время запуска: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    logger.info('🟢 Статус: ОНЛАЙН')
    logger.info('=' * 50)

@client.event
async def on_resumed():
    logger.info('🔄 Сессия восстановлена')

@client.event
async def on_error(event, *args, **kwargs):
    logger.error(f'❌ Ошибка в событии {event}', exc_info=True)

async def main():
    logger.info('🚀 Запуск Discord Userbot...')
    logger.info('⚠️ ПРЕДУПРЕЖДЕНИЕ: Использование userbot нарушает ToS Discord!')
    
    try:
        await client.start(DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error('❌ Ошибка авторизации! Проверьте DISCORD_TOKEN в .env файле')
    except discord.HTTPException as e:
        logger.error(f'❌ HTTP ошибка: {e}')
    except Exception as e:
        logger.error(f'❌ Неожиданная ошибка: {e}', exc_info=True)
    finally:
        logger.info('🔄 Очищаю активность...')
        await clear_activity()
        if not client.is_closed():
            await client.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('⛔ Получен сигнал завершения (Ctrl+C)')
        logger.info('👋 Выключение бота...')
    finally:
        logger.info('✅ Бот остановлен')
