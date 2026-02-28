"""
Константы для графического интерфейса гитарного тюнера.
"""

# Цветовая палитра
COLOR_BG_DARK = "#1a1a1a"
COLOR_BG_MEDIUM = "#2d2d2d"
COLOR_ACCENT = "#00d4ff"
COLOR_GREEN = "#00ff88"
COLOR_YELLOW = "#ffcc00"
COLOR_ORANGE = "#ff8800"
COLOR_RED = "#ff4444"
COLOR_TEXT_DIM = "#666666"
COLOR_TEXT_NORMAL = "#cccccc"

# Размеры окна
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700

# Размеры шрифтов
FONT_SIZE_TITLE = 12
FONT_SIZE_NOTE = 100
FONT_SIZE_FREQUENCY = 18
FONT_SIZE_CENTS = 24
FONT_SIZE_BUTTON = 16
FONT_SIZE_STATUS = 13
FONT_SIZE_SIGNAL = 10

# Параметры аудио
SAMPLE_RATE = 44100
BLOCKSIZE = 2048
NOISE_THRESHOLD = 0.01

# Параметры сглаживания
CENTS_BUFFER_SIZE = 8
FREQUENCY_BUFFER_SIZE = 3
ANIMATION_SPEED = 0.3  # 0-1

# Параметры обновления GUI
GUI_UPDATE_INTERVAL = 30  # мс (примерно 33 FPS)

# Пороги настройки (в центах)
THRESHOLD_PERFECT = 5    # ≤5 центов = идеально
THRESHOLD_ALMOST = 10    # 5-10 центов = почти

# Параметры визуальной шкалы
METER_SEGMENTS = 51      # -50 до +50
METER_HEIGHT = 140
SEGMENT_HEIGHT = 25
