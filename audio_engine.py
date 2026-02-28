"""
Модуль захвата аудио с микрофона в реальном времени.
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

import numpy as np
import sounddevice as sd
from typing import Optional, Callable
import queue
import threading


class AudioEngine:
    """Класс для работы с аудиопотоком."""
    
    def __init__(
        self, 
        sample_rate: int = 44100, 
        blocksize: int = 2048,
        channels: int = 1
    ):
        """
        Инициализация аудио-движка.
        
        Args:
            sample_rate: частота дискретизации в Гц
            blocksize: размер блока данных (chunk)
            channels: количество каналов (1 = моно, 2 = стерео)
        """
        self.sample_rate = sample_rate
        self.blocksize = blocksize
        self.channels = channels
        
        self.audio_queue = queue.Queue()
        self.stream: Optional[sd.InputStream] = None
        self.is_running = False
        
        # Callback для обработки данных
        self.processing_callback: Optional[Callable[[np.ndarray], None]] = None
    
    def audio_callback(self, indata, frames, time_info, status):
        """
        Callback-функция, вызываемая при получении новых аудиоданных.
        
        Args:
            indata: входные аудиоданные
            frames: количество фреймов
            time_info: информация о времени
            status: статус потока
        """
        if status:
            print(f"Статус аудио: {status}")
        
        # Копируем данные в очередь для обработки
        audio_data = indata[:, 0].copy() if self.channels > 1 else indata.copy().flatten()
        
        try:
            self.audio_queue.put_nowait(audio_data)
        except queue.Full:
            pass
    
    def start(self, processing_callback: Optional[Callable[[np.ndarray], None]] = None):
        """
        Запускает захват аудио.
        
        Args:
            processing_callback: функция для обработки аудиоданных
        """
        if self.is_running:
            print("Аудио-движок уже запущен")
            return
        
        self.processing_callback = processing_callback
        self.is_running = True
        
        # Создаем поток для захвата
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            blocksize=self.blocksize,
            channels=self.channels,
            callback=self.audio_callback,
            dtype=np.float32
        )
        
        self.stream.start()
        
        # Запускаем поток обработки
        if self.processing_callback:
            self.processing_thread = threading.Thread(target=self._process_audio, daemon=True)
            self.processing_thread.start()
        
        print(f"Аудио-движок запущен (sample rate: {self.sample_rate} Гц, block size: {self.blocksize})")
    
    def _process_audio(self):
        """Обработка аудиоданных в отдельном потоке."""
        while self.is_running:
            try:
                audio_data = self.audio_queue.get(timeout=0.1)
                if self.processing_callback:
                    self.processing_callback(audio_data)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Ошибка обработки аудио: {e}")
    
    def stop(self):
        """Останавливает захват аудио."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        print("Аудио-движок остановлен")
    
    def get_audio_data(self, timeout: float = 0.1) -> Optional[np.ndarray]:
        """
        Получает следующий блок аудиоданных из очереди.
        
        Args:
            timeout: время ожидания в секундах
            
        Returns:
            массив аудиоданных или None
        """
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    @staticmethod
    def list_audio_devices():
        """Выводит список доступных аудиоустройств."""
        try:
            print("Доступные аудиоустройства:")
            devices = sd.query_devices()
            if devices:
                print(devices)
            else:
                print("Аудиоустройства не найдены")
        except Exception as e:
            print(f"Ошибка при получении списка устройств: {e}")
    
    @staticmethod
    def get_default_input_device():
        """Возвращает информацию об устройстве ввода по умолчанию."""
        try:
            return sd.query_devices(kind='input')
        except Exception as e:
            print(f"Ошибка при получении устройства ввода: {e}")
            return None


if __name__ == '__main__':
    # Тестирование модуля
    print("Тест аудио-движка:\n")
    
    # Показываем доступные устройства
    AudioEngine.list_audio_devices()
    
    print("\n\nУстройство ввода по умолчанию:")
    print(AudioEngine.get_default_input_device())
    
    # Простой тест захвата (без обработки)
    print("\n\nЗапуск захвата на 3 секунды...")
    engine = AudioEngine()
    
    def simple_callback(audio_data):
        rms = np.sqrt(np.mean(audio_data ** 2))
        if rms > 0.01:
            print(f"RMS: {rms:.4f}")
    
    try:
        engine.start(processing_callback=simple_callback)
        import time
        time.sleep(3)
    except KeyboardInterrupt:
        print("\nПрервано пользователем")
    finally:
        engine.stop()
