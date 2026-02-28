"""
Быстрый тест аудио-движка (3 секунды).
"""

import sys
import os

# Добавляем локальные папки libs в путь поиска модулей
libs_paths = [
    os.path.join(os.path.dirname(__file__), 'libs_py313'),
    os.path.join(os.path.dirname(__file__), 'libs')
]
for lib_path in libs_paths:
    if os.path.exists(lib_path):
        sys.path.insert(0, lib_path)

import time
import numpy as np
from audio_engine import AudioEngine

print("Тест аудио-движка:\n")

# Показываем доступные устройства
AudioEngine.list_audio_devices()

print("\n\nУстройство ввода по умолчанию:")
device_info = AudioEngine.get_default_input_device()
if device_info:
    print(device_info)
else:
    print("Не удалось получить информацию об устройстве ввода")

# Простой тест захвата (3 секунды)
print("\n\nЗапуск захвата на 3 секунды...")
print("Издайте звук в микрофон для проверки...\n")

engine = AudioEngine()

def simple_callback(audio_data):
    rms = np.sqrt(np.mean(audio_data ** 2))
    if rms > 0.01:
        print(f"Звук обнаружен! RMS: {rms:.4f}")

try:
    engine.start(processing_callback=simple_callback)
    time.sleep(3)
except Exception as e:
    print(f"Ошибка: {e}")
finally:
    engine.stop()
    print("\nТест завершен")
