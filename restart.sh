#!/bin/bash
# Скрипт для перезапуска бота

cd "$(dirname "$0")"

echo "🔄 Перезапуск бота..."
./stop.sh
sleep 2
./start.sh
