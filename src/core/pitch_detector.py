"""
Модуль определения базовой частоты (Pitch Detection) с использованием автокорреляции.
"""

import sys
import os

# Добавляем локальные папки libs в путь поиска модулей
libs_paths = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'libs_py313'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'libs')
]
for lib_path in libs_paths:
    if os.path.exists(lib_path):
        sys.path.insert(0, lib_path)

import numpy as np
from typing import Optional


class PitchDetector:
    """Класс для определения основной частоты звукового сигнала."""
    
    def __init__(self, sample_rate: int = 44100, noise_threshold: float = 0.01):
        """
        Инициализация детектора питча.
        
        Args:
            sample_rate: частота дискретизации в Гц
            noise_threshold: порог RMS для фильтрации шума (0.0 - 1.0)
        """
        self.sample_rate = sample_rate
        self.noise_threshold = noise_threshold
        
        # Диапазон частот для гитары (примерно E2 - E5)
        self.min_frequency = 60.0
        self.max_frequency = 400.0
    
    def calculate_rms(self, audio_data: np.ndarray) -> float:
        """
        Вычисляет RMS (Root Mean Square) для оценки громкости сигнала.
        
        Args:
            audio_data: массив аудиоданных
            
        Returns:
            значение RMS
        """
        return np.sqrt(np.mean(audio_data ** 2))
    
    def autocorrelation(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Вычисляет автокорреляционную функцию сигнала.
        
        Args:
            audio_data: массив аудиоданных
            
        Returns:
            массив автокорреляции
        """
        # Нормализация сигнала
        audio_data = audio_data - np.mean(audio_data)
        
        # Вычисление автокорреляции через FFT (быстрее)
        fft = np.fft.rfft(audio_data, n=len(audio_data) * 2)
        acf = np.fft.irfft(fft * np.conj(fft))
        acf = acf[:len(audio_data)]
        
        # Нормализация
        if acf[0] > 0:
            acf = acf / acf[0]
        
        return acf
    
    def detect_pitch_autocorrelation(self, audio_data: np.ndarray) -> Optional[float]:
        """
        Определяет основную частоту с использованием метода автокорреляции.
        
        Args:
            audio_data: массив аудиоданных
            
        Returns:
            частота в Гц или None, если не удалось определить
        """
        # Проверка на шум
        rms = self.calculate_rms(audio_data)
        if rms < self.noise_threshold:
            return None
        
        # Вычисляем автокорреляцию
        acf = self.autocorrelation(audio_data)
        
        # Определяем диапазон поиска пиков на основе min/max частоты
        min_period = int(self.sample_rate / self.max_frequency)
        max_period = int(self.sample_rate / self.min_frequency)
        
        if max_period >= len(acf):
            max_period = len(acf) - 1
        
        if min_period >= max_period:
            return None
        
        # Ищем первый значимый пик после нулевой задержки
        acf_slice = acf[min_period:max_period]
        
        if len(acf_slice) == 0:
            return None
        
        # Находим максимум
        peak_index = np.argmax(acf_slice)
        peak_value = acf_slice[peak_index]
        
        # Проверяем, что пик достаточно выраженный
        if peak_value < 0.3:
            return None
        
        # Период в сэмплах
        period = peak_index + min_period
        
        # Интерполяция для более точного определения периода
        if 0 < peak_index < len(acf_slice) - 1:
            # Параболическая интерполяция
            alpha = acf_slice[peak_index - 1]
            beta = acf_slice[peak_index]
            gamma = acf_slice[peak_index + 1]
            
            p = 0.5 * (alpha - gamma) / (alpha - 2 * beta + gamma)
            period = peak_index + min_period + p
        
        # Вычисляем частоту
        frequency = self.sample_rate / period
        
        # Проверяем, что частота в допустимом диапазоне
        if self.min_frequency <= frequency <= self.max_frequency:
            return frequency
        
        return None
    
    def detect_pitch(self, audio_data: np.ndarray) -> Optional[float]:
        """
        Основной метод для определения питча.
        
        Args:
            audio_data: массив аудиоданных (mono, float32)
            
        Returns:
            частота в Гц или None
        """
        if len(audio_data) == 0:
            return None
        
        # Используем автокорреляцию
        return self.detect_pitch_autocorrelation(audio_data)


if __name__ == '__main__':
    # Тестирование модуля с синтетическим сигналом
    print("Тест детектора питча с синтетическими сигналами:\n")
    
    detector = PitchDetector(sample_rate=44100)
    
    # Генерируем тестовые сигналы для разных нот
    test_frequencies = [82.41, 110.0, 146.83, 196.0, 246.94, 329.63]
    duration = 0.1  # 100 мс
    
    for target_freq in test_frequencies:
        # Генерация синусоиды
        t = np.linspace(0, duration, int(detector.sample_rate * duration))
        signal = 0.5 * np.sin(2 * np.pi * target_freq * t)
        
        # Определение частоты
        detected_freq = detector.detect_pitch(signal)
        
        if detected_freq:
            error = abs(detected_freq - target_freq)
            print(f"Цель: {target_freq:.2f} Гц -> Обнаружено: {detected_freq:.2f} Гц (ошибка: {error:.2f} Гц)")
        else:
            print(f"Цель: {target_freq:.2f} Гц -> Не обнаружено")
    
    # Тест с шумом
    print("\n\nТест с низким уровнем сигнала (шум):")
    noise = np.random.normal(0, 0.005, int(detector.sample_rate * duration))
    detected_freq = detector.detect_pitch(noise)
    print(f"Результат для шума: {detected_freq}")
