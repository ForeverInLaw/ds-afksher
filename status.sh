#!/bin/bash
# Скрипт для проверки статуса бота

cd "$(dirname "$0")"

if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "✅ Бот работает (PID: $PID)"
        echo ""
        echo "Информация о процессе:"
        ps -p $PID -o pid,cmd,%cpu,%mem,etime
        echo ""
        echo "📋 Последние 10 строк лога:"
        tail -10 bot.log
    else
        echo "❌ Бот не работает (устаревший PID: $PID)"
        rm bot.pid
    fi
else
    echo "❌ Бот не запущен (файл bot.pid не найден)"
fi
