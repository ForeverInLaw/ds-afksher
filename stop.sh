#!/bin/bash
# Скрипт для остановки бота

cd "$(dirname "$0")"

if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    echo "⏹️ Остановка бота (PID: $PID)..."
    kill $PID 2>/dev/null
    
    # Ждем завершения
    sleep 2
    
    # Проверяем, завершился ли процесс
    if kill -0 $PID 2>/dev/null; then
        echo "⚠️ Принудительная остановка..."
        kill -9 $PID 2>/dev/null
    fi
    
    rm bot.pid
    echo "✅ Бот остановлен"
else
    echo "❌ Файл bot.pid не найден. Бот не запущен или запущен вручную."
fi
