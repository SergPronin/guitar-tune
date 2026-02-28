#!/usr/bin/env python3
"""
Гитарный Тюнер Pro
Профессиональное приложение для настройки гитары в реальном времени.

Запуск: python guitar_tuner.py
"""

import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.guitar_tuner_gui import main

if __name__ == '__main__':
    main()
