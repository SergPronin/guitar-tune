"""
Конфигурация строев гитары и музыкальные константы.
"""

import math
from typing import Dict, List, Tuple


class TuningConfig:
    """Класс для работы с различными гитарными строями."""
    
    # Эталонная частота A4
    A4_FREQUENCY = 440.0
    
    # Определение строев: название -> список (нота, частота)
    TUNINGS: Dict[str, List[Tuple[str, float]]] = {
        'Standard': [
            ('E2', 82.41),
            ('A2', 110.00),
            ('D3', 146.83),
            ('G3', 196.00),
            ('B3', 246.94),
            ('E4', 329.63)
        ],
        'Half-step down': [
            ('Eb2', 77.78),
            ('Ab2', 103.83),
            ('Db3', 138.59),
            ('Gb3', 185.00),
            ('Bb3', 233.08),
            ('Eb4', 311.13)
        ],
        'Drop D': [
            ('D2', 73.42),
            ('A2', 110.00),
            ('D3', 146.83),
            ('G3', 196.00),
            ('B3', 246.94),
            ('E4', 329.63)
        ]
    }
    
    @staticmethod
    def calculate_frequency(note_offset: int) -> float:
        """
        Вычисляет частоту ноты относительно A4 (440 Гц).
        
        Args:
            note_offset: количество полутонов от A4 (положительное или отрицательное)
            
        Returns:
            частота в Гц
        """
        return TuningConfig.A4_FREQUENCY * math.pow(2, note_offset / 12.0)
    
    @staticmethod
    def calculate_cents(current_freq: float, target_freq: float) -> float:
        """
        Вычисляет отклонение в центах между текущей и целевой частотой.
        
        Args:
            current_freq: текущая частота в Гц
            target_freq: целевая частота в Гц
            
        Returns:
            отклонение в центах (положительное = струна перетянута, отрицательное = недотянута)
        """
        if current_freq <= 0 or target_freq <= 0:
            return 0.0
        return 1200 * math.log2(current_freq / target_freq)
    
    @classmethod
    def get_tuning(cls, tuning_name: str) -> List[Tuple[str, float]]:
        """
        Возвращает список нот и частот для указанного строя.
        
        Args:
            tuning_name: название строя
            
        Returns:
            список кортежей (нота, частота)
        """
        return cls.TUNINGS.get(tuning_name, cls.TUNINGS['Standard'])
    
    @classmethod
    def get_tuning_names(cls) -> List[str]:
        """Возвращает список всех доступных строев."""
        return list(cls.TUNINGS.keys())
    
    @classmethod
    def find_closest_note(cls, frequency: float, tuning_name: str = 'Standard') -> Tuple[str, float, float]:
        """
        Находит ближайшую ноту из заданного строя к измеренной частоте.
        
        Args:
            frequency: измеренная частота в Гц
            tuning_name: название строя
            
        Returns:
            кортеж (название_ноты, целевая_частота, отклонение_в_центах)
        """
        tuning = cls.get_tuning(tuning_name)
        
        if frequency <= 0:
            return ('?', 0.0, 0.0)
        
        # Находим ближайшую ноту по минимальной разнице в центах
        closest_note = None
        min_cents_diff = float('inf')
        
        for note_name, target_freq in tuning:
            cents = cls.calculate_cents(frequency, target_freq)
            abs_cents = abs(cents)
            
            if abs_cents < min_cents_diff:
                min_cents_diff = abs_cents
                closest_note = (note_name, target_freq, cents)
        
        return closest_note if closest_note else ('?', 0.0, 0.0)


if __name__ == '__main__':
    # Тестирование модуля
    print("Доступные строи:")
    for tuning_name in TuningConfig.get_tuning_names():
        print(f"\n{tuning_name}:")
        for note, freq in TuningConfig.get_tuning(tuning_name):
            print(f"  {note}: {freq:.2f} Гц")
    
    # Тест расчета центов
    print("\n\nТест расчета центов:")
    test_freq = 442.0  # A4 немного выше
    target_freq = 440.0
    cents = TuningConfig.calculate_cents(test_freq, target_freq)
    print(f"Частота {test_freq} Гц относительно {target_freq} Гц: {cents:.2f} центов")
    
    # Тест поиска ближайшей ноты
    print("\n\nТест поиска ближайшей ноты:")
    test_frequencies = [82.0, 110.5, 147.0, 200.0]
    for freq in test_frequencies:
        note, target, cents = TuningConfig.find_closest_note(freq, 'Standard')
        print(f"{freq} Гц -> {note} (цель: {target:.2f} Гц, отклонение: {cents:+.2f} центов)")
