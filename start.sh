#!/bin/bash
# Скрипт для запуска бота в фоновом режиме

cd "$(dirname "$0")"

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Запуск бота с nohup
nohup python3 bot.py > bot.log 2>&1 &
echo $! > bot.pid

echo "✅ Бот запущен в фоновом режиме"
echo "📝 PID: $(cat bot.pid)"
echo "📋 Логи: tail -f bot.log"
echo "🛑 Остановить: kill $(cat bot.pid)"
