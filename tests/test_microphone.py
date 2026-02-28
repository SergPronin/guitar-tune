#!/usr/bin/env python3
"""
Быстрый тест: проверка, слышит ли микрофон гитару.
"""

import sys
import os

libs_paths = [
    os.path.join(os.path.dirname(__file__), 'libs_py313'),
    os.path.join(os.path.dirname(__file__), 'libs')
]
for lib_path in libs_paths:
    if os.path.exists(lib_path):
        sys.path.insert(0, lib_path)

import numpy as np
import sounddevice as sd
import time

print("=" * 70)
print("БЫСТРЫЙ ТЕСТ МИКРОФОНА")
print("=" * 70)
print()
print("Сейчас программа будет слушать микрофон 10 секунд.")
print("Дерните струну на гитаре несколько раз.")
print()
print("Начинаю через 2 секунды...")
time.sleep(2)

sample_rate = 44100
blocksize = 2048
max_rms = 0.0
samples_received = 0

def audio_callback(indata, frames, time_info, status):
    global max_rms, samples_received
    
    audio_data = indata[:, 0].copy() if len(indata.shape) > 1 else indata.copy().flatten()
    rms = np.sqrt(np.mean(audio_data ** 2))
    
    if rms > max_rms:
        max_rms = rms
    
    samples_received += 1
    
    # Визуальный индикатор уровня
    bars = int(rms * 500)
    bar_str = '█' * min(bars, 50)
    
    print(f"\r[{samples_received:4d}] RMS: {rms:.6f} | {bar_str:<50}", end='', flush=True)

print("\n🎤 СЛУШАЮ МИКРОФОН (10 секунд)...")
print("-" * 70)

try:
    stream = sd.InputStream(
        samplerate=sample_rate,
        blocksize=blocksize,
        channels=1,
        callback=audio_callback,
        dtype=np.float32
    )
    
    stream.start()
    time.sleep(10)
    stream.stop()
    stream.close()
    
except Exception as e:
    print(f"\n\n❌ ОШИБКА: {e}")
    print("\n💡 РЕШЕНИЕ:")
    print("   Дайте разрешение на микрофон:")
    print("   macOS: Системные настройки → Конфиденциальность → Микрофон")
    sys.exit(1)

print("\n" + "-" * 70)
print("\n📊 РЕЗУЛЬТАТЫ:")
print(f"   Блоков получено: {samples_received}")
print(f"   Максимальный RMS: {max_rms:.6f}")
print()

if max_rms < 0.001:
    print("❌ ОЧЕНЬ НИЗКИЙ УРОВЕНЬ")
    print("   Микрофон не слышит звук.")
    print()
    print("   Что делать:")
    print("   1. Проверьте, работает ли микрофон (откройте QuickTime/Photo Booth)")
    print("   2. Играйте ГРОМЧЕ на гитаре")
    print("   3. Поднесите микрофон ближе к гитаре (10-20 см)")
elif max_rms < 0.01:
    print("⚠️  НИЗКИЙ УРОВЕНЬ")
    print("   Микрофон слышит звук, но слишком тихо для тюнера.")
    print()
    print("   Что делать:")
    print("   1. Играйте ГРОМЧЕ")
    print("   2. Микрофон ближе к гитаре")
    print("   3. Или измените порог в main.py: noise_threshold=0.005")
else:
    print("✅ ОТЛИЧНО!")
    print("   Уровень сигнала достаточный для работы тюнера.")
    print()
    print("   Запустите тюнер:")
    print("   python3.13 main.py")

print()
print("=" * 70)
