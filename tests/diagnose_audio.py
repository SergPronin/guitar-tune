#!/usr/bin/env python3
"""
Диагностика проблем с микрофоном и аудиоустройствами.
"""

import sys
import os

# Добавляем локальные папки libs
libs_paths = [
    os.path.join(os.path.dirname(__file__), 'libs_py313'),
    os.path.join(os.path.dirname(__file__), 'libs')
]
for lib_path in libs_paths:
    if os.path.exists(lib_path):
        sys.path.insert(0, lib_path)

import sounddevice as sd
import numpy as np

print("=" * 70)
print("ДИАГНОСТИКА АУДИО")
print("=" * 70)
print()

# 1. Проверка доступных устройств
print("1. Проверка аудиоустройств...")
try:
    devices = sd.query_devices()
    if devices:
        print("\n📋 Найденные устройства:")
        print(devices)
    else:
        print("\n❌ Аудиоустройства не найдены!")
except Exception as e:
    print(f"\n❌ Ошибка при получении списка устройств: {e}")

print("\n" + "-" * 70)

# 2. Проверка устройства ввода по умолчанию
print("\n2. Проверка устройства ввода по умолчанию...")
try:
    input_device = sd.query_devices(kind='input')
    print(f"\n✓ Устройство ввода найдено:")
    print(input_device)
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    print("\n💡 РЕШЕНИЕ:")
    print("   1. Проверьте, подключен ли микрофон")
    print("   2. Дайте разрешение на доступ к микрофону:")
    print("      macOS: Системные настройки → Конфиденциальность → Микрофон")
    print("      Разрешите доступ для Terminal или Python")

print("\n" + "-" * 70)

# 3. Попытка захвата аудио
print("\n3. Попытка захвата аудио (2 секунды)...")
try:
    print("   Издайте звук в микрофон...")
    
    duration = 2  # секунды
    sample_rate = 44100
    
    # Захват
    recording = sd.rec(int(duration * sample_rate), 
                       samplerate=sample_rate, 
                       channels=1, 
                       dtype='float32')
    sd.wait()  # Ждем окончания
    
    # Анализ
    rms = np.sqrt(np.mean(recording ** 2))
    max_val = np.max(np.abs(recording))
    
    print(f"\n✓ Захват успешен!")
    print(f"   RMS (громкость): {rms:.6f}")
    print(f"   Максимум: {max_val:.6f}")
    
    if rms < 0.001:
        print("\n⚠️  ПРЕДУПРЕЖДЕНИЕ: Очень низкий уровень сигнала!")
        print("   Возможные причины:")
        print("   • Микрофон не работает")
        print("   • Микрофон отключен в настройках")
        print("   • Нет звука (говорите громче)")
    elif rms < 0.01:
        print("\n⚠️  Уровень сигнала низкий (но работает)")
        print("   Рекомендуется играть громче на гитаре")
    else:
        print("\n✓ Уровень сигнала хороший!")
    
except Exception as e:
    print(f"\n❌ Ошибка при захвате: {e}")
    print("\n💡 РЕШЕНИЕ:")
    print("   Дайте разрешение на доступ к микрофону:")
    print("   macOS: Системные настройки → Конфиденциальность → Микрофон")

print("\n" + "=" * 70)
print("ИТОГИ ДИАГНОСТИКИ")
print("=" * 70)
print()

# Итоговая рекомендация
try:
    devices = sd.query_devices()
    input_device = sd.query_devices(kind='input')
    
    if devices and input_device:
        print("✅ Аудиосистема работает корректно")
        print("\nЕсли тюнер не реагирует на звук:")
        print("  1. Убедитесь, что играете достаточно громко")
        print("  2. Микрофон должен быть близко к гитаре (10-20 см)")
        print("  3. Глушите соседние струны")
        print("  4. Играйте чистые ноты (не аккорды)")
    else:
        print("❌ Аудиосистема недоступна")
        print("\n💡 ДЕЙСТВИЯ:")
        print("  1. Проверьте подключение микрофона")
        print("  2. Дайте разрешение на микрофон в Системных настройках")
        print("  3. Перезапустите Terminal после дачи разрешения")
        
except:
    print("❌ Проблемы с доступом к аудио")
    print("\nДайте разрешение на микрофон и перезапустите программу")

print()
