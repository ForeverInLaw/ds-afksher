# Discord Userbot - 24/7 Online

Discord userbot для поддержания онлайн-статуса 24/7 в определенном канале на сервере с таймером в активности (статусе).

## ⚠️ ПРЕДУПРЕЖДЕНИЕ

**Использование userbot'ов нарушает Terms of Service Discord и может привести к блокировке аккаунта!**

- Не используйте на основном аккаунте
- Используйте на свой риск
- Рекомендуется создать отдельный тестовый аккаунт

## 📋 Требования

- Python 3.8 или выше
- Токен пользователя Discord

## 🚀 Установка

### 1. Клонируйте проект

```bash
cd ds-afksher
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

### 3. Настройте конфигурацию

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` файл и добавьте свои данные:

```env
DISCORD_TOKEN=ваш_токен_пользователя
CHANNEL_ID=id_канала_для_мониторинга
ACTIVITY_TYPE=playing
```

### Типы активности

Вы можете выбрать один из следующих типов активности через параметр `ACTIVITY_TYPE`:

- `playing` - **Играет в** афкшу уже X минут (по умолчанию)
- `watching` - **Смотрит** афкшу уже X минут
- `listening` - **Слушает** афкшу уже X минут
- `streaming` - **Стримит** афкшу уже X минут
- `competing` - **Соревнуется в** афкшу уже X минут

## 🔑 Как получить токен пользователя

1. Откройте Discord в **браузере** (не в приложении)
2. Нажмите `F12` для открытия DevTools
3. Перейдите во вкладку **Network**
4. Нажмите `Ctrl+R` для перезагрузки страницы
5. Найдите любой запрос к API Discord (например, `messages`)
6. В разделе **Headers** найдите `Authorization` - это ваш токен

**⚠️ НИКОГДА НЕ ДЕЛИТЕСЬ СВОИМ ТОКЕНОМ!**

## 🎯 Как получить Channel ID (опционально)

1. Включите режим разработчика в Discord:
   - Настройки → Расширенные → Режим разработчика
2. Правой кнопкой мыши на канал → Копировать ID

**Примечание:** CHANNEL_ID не обязателен - бот будет работать и показывать таймер активности даже без указания канала. Если указан голосовой канал - бот подключится к нему.

## ▶️ Запуск

```bash
python bot.py
```

При успешном запуске вы увидите:

```
🚀 Запуск Discord Userbot...
⚠️ ПРЕДУПРЕЖДЕНИЕ: Использование userbot нарушает ToS Discord!
🔌 Подключено к Discord WebSocket
==================================================
✅ Бот готов к работе!
👤 Пользователь: YourUsername#1234
🆔 ID: 123456789012345678
📺 Найден канал: CHANNEL (987654321098765432)
📝 Тип канала: VoiceChannel
🎤 Это голосовой канал - подключаюсь...
✅ Успешно подключился к голосовому каналу: CHANNEL
🔊 Статус: В ГОЛОСОВОМ КАНАЛЕ
⏰ Запущен таймер обновления активности
🕐 Время запуска: 2024-01-15 12:00:00
🟢 Статус: ОНЛАЙН
==================================================
⏰ Таймер активности запущен (тип: playing)
✏️ Активность обновлена: Играет в "афкшу уже 0 минут"
```

В Discord вы увидите Rich Presence активность:
- 🎮 **Играет в** афкшу уже 5 минут
- 📺 **Смотрит** афкшу уже 2 часа (если ACTIVITY_TYPE=watching)
- и т.д.


### Вариант 1: PM2 (рекомендуется)

```bash
npm install -g pm2
pm2 start bot.py --name discord-afk --interpreter python3
pm2 save
pm2 startup
```

Управление:
```bash
pm2 status          # Статус
pm2 logs discord-afk  # Логи
pm2 restart discord-afk  # Перезапуск
pm2 stop discord-afk     # Остановка
```

### Вариант 2: nohup (Linux)

```bash
nohup python bot.py > bot.log 2>&1 &
```

### Вариант 3: systemd (Linux)

Создайте файл `/etc/systemd/system/discord-bot.service`:

```ini
[Unit]
Description=Discord Userbot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/ds-afksher
ExecStart=/usr/bin/python3 /path/to/ds-afksher/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Запуск:
```bash
sudo systemctl daemon-reload
sudo systemctl enable discord-bot
sudo systemctl start discord-bot
sudo systemctl status discord-bot
```

## 📁 Структура проекта

```
ds-afksher/
├── bot.py              # Основной файл userbot'а
├── config.py           # Управление конфигурацией
├── .env.example        # Пример конфигурации
├── .gitignore          # Игнорирование файлов
├── requirements.txt    # Зависимости
└── README.md           # Этот файл
```

## 📚 Технологии

- [discord.py-self](https://github.com/dolfies/discord.py-self) - форк discord.py для userbot'ов
- [python-dotenv](https://github.com/theskumar/python-dotenv) - управление переменными окружения

## 📝 Лицензия

Проект создан в образовательных целях. Используйте на свой риск.

## 🤝 Поддержка

При возникновении проблем создайте issue или проверьте:
- Правильность токена и channel ID
- Наличие доступа к каналу
- Версию Python (должна быть 3.8+)
- Установку всех зависимостей
