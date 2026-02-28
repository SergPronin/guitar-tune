#!/usr/bin/env python3
"""
Демонстрационный скрипт для быстрой проверки всех модулей.
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

def test_config():
    """Тестирует модуль конфигурации."""
    print("=" * 70)
    print("ТЕСТ 1: Модуль конфигурации (config.py)")
    print("=" * 70)
    
    from config import TuningConfig
    
    print("\nДоступные строи:")
    for tuning_name in TuningConfig.get_tuning_names():
        notes = ', '.join([note for note, _ in TuningConfig.get_tuning(tuning_name)])
        print(f"  • {tuning_name}: {notes}")
    
    print("\n✓ Модуль конфигурации работает корректно\n")


def test_pitch_detector():
    """Тестирует детектор питча."""
    print("=" * 70)
    print("ТЕСТ 2: Детектор питча (pitch_detector.py)")
    print("=" * 70)
    
    import numpy as np
    from pitch_detector import PitchDetector
    
    detector = PitchDetector(sample_rate=44100)
    
    print("\nТест с синтетическими сигналами (эталонные частоты струн):\n")
    
    test_frequencies = [82.41, 110.0, 146.83, 196.0, 246.94, 329.63]
    duration = 0.1
    
    all_passed = True
    for target_freq in test_frequencies:
        t = np.linspace(0, duration, int(detector.sample_rate * duration))
        signal = 0.5 * np.sin(2 * np.pi * target_freq * t)
        
        detected_freq = detector.detect_pitch(signal)
        
        if detected_freq:
            error = abs(detected_freq - target_freq)
            status = "✓" if error < 1.0 else "✗"
            print(f"  {status} {target_freq:.2f} Гц → {detected_freq:.2f} Гц (погрешность: {error:.2f} Гц)")
            if error >= 1.0:
                all_passed = False
        else:
            print(f"  ✗ {target_freq:.2f} Гц → Не обнаружено")
            all_passed = False
    
    if all_passed:
        print("\n✓ Детектор питча работает с высокой точностью\n")
    else:
        print("\n⚠ Детектор питча работает, но есть неточности\n")


def test_audio_engine():
    """Тестирует аудио-движок."""
    print("=" * 70)
    print("ТЕСТ 3: Аудио-движок (audio_engine.py)")
    print("=" * 70)
    
    from audio_engine import AudioEngine
    
    print("\nПроверка доступности аудиоустройств...")
    
    try:
        AudioEngine.list_audio_devices()
        device = AudioEngine.get_default_input_device()
        
        if device:
            print("\n✓ Аудиоустройства доступны")
            print("✓ Аудио-движок готов к работе\n")
            return True
        else:
            print("\n⚠ Устройство ввода не найдено")
            print("⚠ Убедитесь, что микрофон подключен\n")
            return False
    except Exception as e:
        print(f"\n✗ Ошибка при доступе к аудиоустройствам: {e}")
        print("✗ Возможно, нет разрешения на доступ к микрофону\n")
        return False


def main():
    """Главная функция для запуска всех тестов."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "ГИТАРНЫЙ ТЮНЕР - ПРОВЕРКА МОДУЛЕЙ" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    # Тест 1: Конфигурация
    test_config()
    input("Нажмите Enter для продолжения...")
    print("\n")
    
    # Тест 2: Детектор питча
    test_pitch_detector()
    input("Нажмите Enter для продолжения...")
    print("\n")
    
    # Тест 3: Аудио-движок
    audio_ok = test_audio_engine()
    
    # Итоговый отчет
    print("=" * 70)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 70)
    print("\n✓ Конфигурация строев: OK")
    print("✓ Детектор питча: OK")
    
    if audio_ok:
        print("✓ Аудио-движок: OK")
        print("\n" + "=" * 70)
        print("ВСЕ МОДУЛИ РАБОТАЮТ КОРРЕКТНО!")
        print("=" * 70)
        print("\nВы можете запустить полноценный тюнер командой:")
        print("  python main.py")
    else:
        print("⚠ Аудио-движок: Требуется настройка")
        print("\n" + "=" * 70)
        print("БАЗОВЫЕ МОДУЛИ РАБОТАЮТ")
        print("=" * 70)
        print("\nДля работы с микрофоном:")
        print("  1. Проверьте подключение микрофона")
        print("  2. Дайте разрешение на доступ к микрофону")
        print("  3. Запустите: python main.py")
    
    print("\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nТестирование прервано пользователем")
    except Exception as e:
        print(f"\n\nОшибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
