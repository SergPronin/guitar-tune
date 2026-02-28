"""
Главный модуль для тестирования ядра гитарного тюнера (консольная версия).
"""

import sys
import os

# Добавляем локальные папки libs в путь поиска модулей
# Для разных версий Python могут быть разные папки
libs_paths = [
    os.path.join(os.path.dirname(__file__), 'libs_py313'),
    os.path.join(os.path.dirname(__file__), 'libs')
]
for lib_path in libs_paths:
    if os.path.exists(lib_path):
        sys.path.insert(0, lib_path)

import time
import numpy as np
from config import TuningConfig
from pitch_detector import PitchDetector
from audio_engine import AudioEngine


class GuitarTunerCore:
    """Ядро гитарного тюнера (без GUI)."""
    
    def __init__(self, tuning_name: str = 'Standard'):
        """
        Инициализация тюнера.
        
        Args:
            tuning_name: название строя
        """
        self.tuning_name = tuning_name
        self.sample_rate = 44100
        self.blocksize = 2048
        
        # Инициализируем компоненты
        self.pitch_detector = PitchDetector(
            sample_rate=self.sample_rate,
            noise_threshold=0.01
        )
        self.audio_engine = AudioEngine(
            sample_rate=self.sample_rate,
            blocksize=self.blocksize,
            channels=1
        )
        
        self.is_running = False
        
        # Буфер для сглаживания результатов
        self.frequency_buffer = []
        self.buffer_size = 3
        
        # Счетчики для отладки
        self.audio_blocks_received = 0
        self.frequencies_detected = 0
        self.last_rms = 0.0
    
    def process_audio(self, audio_data: np.ndarray):
        """
        Обрабатывает аудиоданные и определяет частоту.
        
        Args:
            audio_data: массив аудиоданных
        """
        self.audio_blocks_received += 1
        
        # Вычисляем RMS для отладки
        self.last_rms = np.sqrt(np.mean(audio_data ** 2))
        
        # Каждые 10 блоков показываем уровень сигнала, если ничего не детектится
        if self.audio_blocks_received % 10 == 0 and self.frequencies_detected == 0:
            print(f"\r[Отладка] Уровень сигнала: {self.last_rms:.6f} (порог: 0.01) | Блоков: {self.audio_blocks_received}", end='', flush=True)
        
        # Определяем частоту
        frequency = self.pitch_detector.detect_pitch(audio_data)
        
        if frequency is None:
            return
        
        self.frequencies_detected += 1
        
        if frequency is None:
            return
        
        # Добавляем в буфер для сглаживания
        self.frequency_buffer.append(frequency)
        if len(self.frequency_buffer) > self.buffer_size:
            self.frequency_buffer.pop(0)
        
        # Вычисляем среднюю частоту
        avg_frequency = np.mean(self.frequency_buffer)
        
        # Находим ближайшую ноту
        note_name, target_freq, cents = TuningConfig.find_closest_note(
            avg_frequency, 
            self.tuning_name
        )
        
        # Визуальное представление
        self.display_tuning_info(note_name, avg_frequency, target_freq, cents)
    
    def display_tuning_info(self, note: str, current_freq: float, target_freq: float, cents: float):
        """
        Выводит информацию о настройке в консоль.
        
        Args:
            note: название ноты
            current_freq: текущая частота
            target_freq: целевая частота
            cents: отклонение в центах
        """
        # Определяем статус настройки
        if abs(cents) <= 5:
            status = "✓ НАСТРОЕНА"
            status_color = "\033[92m"  # зеленый
        elif cents > 0:
            status = "↑ ПЕРЕТЯНУТА"
            status_color = "\033[91m"  # красный
        else:
            status = "↓ НЕДОТЯНУТА"
            status_color = "\033[91m"  # красный
        
        # Визуальная шкала от -50 до +50 центов
        scale_width = 50
        center = scale_width // 2
        
        # Ограничиваем центы для отображения
        display_cents = max(-50, min(50, cents))
        position = int(center + (display_cents / 50) * center)
        position = max(0, min(scale_width - 1, position))
        
        # Создаем шкалу
        scale = ['-'] * scale_width
        scale[center] = '|'
        scale[position] = '●'
        scale_str = ''.join(scale)
        
        # Вывод
        reset_color = "\033[0m"
        print(f"\r{status_color}{status}{reset_color} | "
              f"Нота: {note} | "
              f"Частота: {current_freq:.2f} Гц (цель: {target_freq:.2f} Гц) | "
              f"Отклонение: {cents:+.1f} центов | "
              f"[{scale_str}]", end='', flush=True)
    
    def start(self):
        """Запускает тюнер."""
        if self.is_running:
            print("Тюнер уже запущен")
            return
        
        print(f"Запуск гитарного тюнера...")
        print(f"Строй: {self.tuning_name}")
        print(f"Целевые ноты: {', '.join([note for note, _ in TuningConfig.get_tuning(self.tuning_name)])}")
        print("\nПроверка аудиоустройств...")
        
        # Проверяем доступность микрофона
        try:
            device_info = self.audio_engine.get_default_input_device()
            if device_info:
                print(f"✓ Микрофон найден: {device_info.get('name', 'Unknown')}")
            else:
                print("⚠️  ВНИМАНИЕ: Микрофон не найден!")
                print("   Дайте разрешение на микрофон в Системных настройках")
                print("   macOS: Системные настройки → Конфиденциальность → Микрофон\n")
        except Exception as e:
            print(f"⚠️  Ошибка доступа к микрофону: {e}")
            print("   Запустите: python3.13 diagnose_audio.py для диагностики\n")
        
        print("\nИграйте на гитаре, чтобы начать настройку...")
        print("Нажмите Ctrl+C для выхода")
        print("(Если тюнер не реагирует - уровень сигнала будет показан ниже)\n")
        
        self.is_running = True
        self.audio_engine.start(processing_callback=self.process_audio)
    
    def stop(self):
        """Останавливает тюнер."""
        if not self.is_running:
            return
        
        self.is_running = False
        self.audio_engine.stop()
        print("\n\nТюнер остановлен")
    
    def change_tuning(self, tuning_name: str):
        """
        Меняет строй.
        
        Args:
            tuning_name: название строя
        """
        if tuning_name in TuningConfig.get_tuning_names():
            self.tuning_name = tuning_name
            print(f"\nСтрой изменен на: {tuning_name}")
        else:
            print(f"\nНеизвестный строй: {tuning_name}")


def main():
    """Главная функция для запуска тестовой версии тюнера."""
    
    print("=" * 70)
    print("ГИТАРНЫЙ ТЮНЕР (КОНСОЛЬНАЯ ВЕРСИЯ)")
    print("=" * 70)
    print()
    
    # Показываем доступные строи
    print("Доступные строи:")
    for i, tuning_name in enumerate(TuningConfig.get_tuning_names(), 1):
        notes = ', '.join([note for note, _ in TuningConfig.get_tuning(tuning_name)])
        print(f"  {i}. {tuning_name}: {notes}")
    
    print()
    
    # Выбор строя
    try:
        choice = input("Выберите строй (1-3) или нажмите Enter для Standard: ").strip()
        if choice:
            tuning_index = int(choice) - 1
            tuning_names = TuningConfig.get_tuning_names()
            if 0 <= tuning_index < len(tuning_names):
                selected_tuning = tuning_names[tuning_index]
            else:
                selected_tuning = 'Standard'
        else:
            selected_tuning = 'Standard'
    except (ValueError, KeyboardInterrupt):
        selected_tuning = 'Standard'
    
    print()
    
    # Создаем и запускаем тюнер
    tuner = GuitarTunerCore(tuning_name=selected_tuning)
    
    try:
        tuner.start()
        
        # Бесконечный цикл (пока не нажат Ctrl+C)
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\nОстановка тюнера...")
    
    finally:
        tuner.stop()
        print("Программа завершена")


if __name__ == '__main__':
    main()
