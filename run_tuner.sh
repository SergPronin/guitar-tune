#!/bin/bash

# Скрипт для быстрого запуска гитарного тюнера

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                        ГИТАРНЫЙ ТЮНЕР                              ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.10+"
    exit 1
fi

echo "✓ Python найден: $(python3 --version)"
echo ""

# Проверка зависимостей
echo "Проверка зависимостей..."
python3 -c "import numpy, scipy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Не установлены numpy или scipy"
    echo "Установите: pip install numpy scipy"
    exit 1
fi
echo "✓ NumPy и SciPy установлены"

python3 -c "import sys; sys.path.insert(0, 'libs'); import sounddevice" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠ SoundDevice не найден"
    echo "Установка в локальную папку libs..."
    pip3 install sounddevice --target ./libs
fi
echo "✓ SoundDevice установлен"
echo ""

# Запуск тюнера
echo "Запуск гитарного тюнера..."
echo ""

# Используем python3.10, если доступен, иначе python3
if command -v python3.10 &> /dev/null; then
    python3.10 main.py
else
    python3 main.py
fi
