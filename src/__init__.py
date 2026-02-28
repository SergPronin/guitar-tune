"""
Гитарный тюнер.
Профессиональное приложение для настройки гитары в реальном времени.
"""

__version__ = '1.0.0'
__author__ = 'Guitar Tuner Team'

from src.core import TuningConfig, PitchDetector, AudioEngine

__all__ = ['TuningConfig', 'PitchDetector', 'AudioEngine']
