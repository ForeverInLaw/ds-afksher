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
voice_client = None
reconnect_task = None
target_channel_id = CHANNEL_ID

async def clear_activity():
    """Очищает активность (статус)"""
    try:
        if client.is_ready() and not client.is_closed():
            await client.change_presence(activity=None)
            logger.info(f'✅ Активность очищена')
    except Exception as e:
        logger.error(f'❌ Ошибка при очистке активности: {e}')

async def connect_to_voice_channel(channel, retry_count=0, max_retries=10):
    """Подключается к голосовому каналу с повторными попытками"""
    global voice_client
    
    if retry_count >= max_retries:
        logger.error(f'❌ Достигнуто максимальное количество попыток подключения ({max_retries})')
        logger.warning('⚠️ Возможно, Discord блокирует voice подключения для selfbot')
        return None
    
    try:
        if voice_client and voice_client.is_connected():
            if voice_client.channel.id == channel.id:
                logger.debug('🔗 Уже подключен к этому каналу')
                return voice_client
            
            logger.info('🔄 Отключаюсь от старого voice соединения...')
            await voice_client.disconnect(force=True)
            await asyncio.sleep(2)
        
        await asyncio.sleep(retry_count * 2)
        
        voice_client = await channel.connect(timeout=60.0, reconnect=False, self_deaf=True, self_mute=False)
        logger.info(f'✅ Успешно подключился к голосовому каналу: {channel.name}')
        return voice_client
        
    except discord.ClientException as e:
        if "Already connected" in str(e):
            logger.debug('ℹ️ Уже подключен к voice каналу')
            return voice_client
        
        wait_time = min(2 ** retry_count, 60)
        logger.warning(f'⚠️ Ошибка подключения (попытка {retry_count + 1}/{max_retries}): {e}')
        logger.info(f'⏳ Повтор через {wait_time} секунд...')
        await asyncio.sleep(wait_time)
        return await connect_to_voice_channel(channel, retry_count + 1, max_retries)
    
    except discord.errors.ConnectionClosed as e:
        if e.code == 4006:
            wait_time = min(3 ** retry_count, 120)
            logger.warning(f'⚠️ Voice session invalid (4006), попытка {retry_count + 1}/{max_retries}')
            logger.info(f'⏳ Ожидание {wait_time} секунд перед повтором...')
            await asyncio.sleep(wait_time)
            return await connect_to_voice_channel(channel, retry_count + 1, max_retries)
        else:
            wait_time = min(2 ** retry_count, 60)
            logger.error(f'❌ Voice WebSocket закрыт с кодом {e.code} (попытка {retry_count + 1}/{max_retries})')
            logger.info(f'⏳ Повтор через {wait_time} секунд...')
            await asyncio.sleep(wait_time)
            return await connect_to_voice_channel(channel, retry_count + 1, max_retries)
        
    except Exception as e:
        wait_time = min(2 ** retry_count, 60)
        logger.error(f'❌ Неожиданная ошибка при подключении (попытка {retry_count + 1}/{max_retries}): {e}')
        logger.info(f'⏳ Повтор через {wait_time} секунд...')
        await asyncio.sleep(wait_time)
        return await connect_to_voice_channel(channel, retry_count + 1, max_retries)

async def monitor_voice_connection():
    """Мониторит voice соединение и переподключается при разрыве"""
    global voice_client
    
    await client.wait_until_ready()
    
    if not target_channel_id:
        return
    
    await asyncio.sleep(5)
    
    while not client.is_closed():
        try:
            should_reconnect = False
            
            if voice_client is None:
                should_reconnect = True
            elif not voice_client.is_connected():
                should_reconnect = True
            
            if should_reconnect:
                logger.warning('⚠️ Voice соединение потеряно. Переподключаюсь...')
                
                channel = client.get_channel(target_channel_id)
                if channel and isinstance(channel, discord.VoiceChannel):
                    voice_client = await connect_to_voice_channel(channel)
                    if voice_client:
                        logger.info('✅ Voice соединение восстановлено')
                else:
                    logger.error(f'❌ Не могу найти voice канал с ID {target_channel_id}')
            
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f'❌ Ошибка в мониторе voice соединения: {e}')
            await asyncio.sleep(30)

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
    await asyncio.sleep(1)

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
            if not client.is_ready() or client.is_closed():
                logger.debug('⏸️ Клиент не готов, пропускаю обновление активности')
                await asyncio.sleep(10)
                continue
            
            elapsed = datetime.now() - start_time
            minutes = int(elapsed.total_seconds() / 60)
            
            time_str = format_time(minutes)
            activity_text = f"афкшу уже {time_str}"
            
            if ACTIVITY_TYPE == 'playing':
                activity = discord.Game(name=activity_text)
                logger.info(f'✏️ Активность обновлена: Играет в "{activity_text}"')
            elif ACTIVITY_TYPE == 'streaming':
                activity = discord.Streaming(name=activity_text, url="https://twitch.tv/afk")
                logger.info(f'✏️ Активность обновлена: Стримит "{activity_text}"')
            else:
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
        except discord.ConnectionClosed:
            logger.warning('⚠️ Соединение закрыто, жду восстановления...')
            await asyncio.sleep(30)
        except Exception as e:
            logger.error(f'❌ Ошибка при обновлении активности: {e}')
            await asyncio.sleep(60)

@client.event
async def on_ready():
    global start_time, voice_client, reconnect_task
    
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
                    logger.info('🎤 Это голосовой канал - пытаюсь подключиться...')
                    logger.warning('⚠️ Voice подключения для selfbot могут быть ограничены Discord')
                    
                    voice_client = await connect_to_voice_channel(channel)
                    
                    if voice_client:
                        logger.info('🔊 Статус: В ГОЛОСОВОМ КАНАЛЕ')
                        
                        if reconnect_task is None or reconnect_task.done():
                            reconnect_task = client.loop.create_task(monitor_voice_connection())
                            logger.info('🔄 Запущен мониторинг voice соединения')
                    else:
                        logger.warning('⚠️ Не удалось подключиться к voice каналу')
                        logger.info('ℹ️ Бот продолжит работу без voice подключения')
                    
                    client.loop.create_task(update_activity())
                    logger.info('⏰ Запущен таймер обновления активности')
                    
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

async def cleanup():
    """Очистка ресурсов перед завершением"""
    global voice_client, reconnect_task
    
    logger.info('🔄 Начинаю очистку...')
    
    if reconnect_task and not reconnect_task.done():
        reconnect_task.cancel()
        logger.info('✅ Мониторинг voice соединения остановлен')
    
    if voice_client and voice_client.is_connected():
        try:
            await voice_client.disconnect(force=True)
            logger.info('✅ Отключен от voice канала')
        except Exception as e:
            logger.error(f'❌ Ошибка при отключении от voice: {e}')
    
    await clear_activity()
    
    if not client.is_closed():
        await client.close()
        logger.info('✅ Соединение с Discord закрыто')

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
        await cleanup()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('⛔ Получен сигнал завершения (Ctrl+C)')
        logger.info('👋 Выключение бота...')
    finally:
        logger.info('✅ Бот остановлен')
