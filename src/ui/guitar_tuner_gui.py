"""
Графический интерфейс гитарного тюнера.
Профессиональный минималистичный дизайн с фокусом на процессе настройки.
"""

import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Добавляем локальные библиотеки
libs_paths = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'libs_py313'),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'libs')
]
for lib_path in libs_paths:
    if os.path.exists(lib_path):
        sys.path.insert(0, lib_path)

import customtkinter as ctk
import queue
import numpy as np
from collections import deque

from src.core import TuningConfig, PitchDetector, AudioEngine
from src.ui.constants import *


class GuitarTunerGUI:
    """Профессиональный графический интерфейс гитарного тюнера."""
    
    def __init__(self):
        """Инициализация GUI."""
        
        # Настройка темы
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Создание главного окна
        self.root = ctk.CTk()
        self.root.title("Гитарный Тюнер Pro")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(fg_color=COLOR_BG_DARK)
        
        # Инициализация компонентов ядра
        self.current_tuning = "Standard"
        
        self.pitch_detector = PitchDetector(
            sample_rate=SAMPLE_RATE,
            noise_threshold=NOISE_THRESHOLD
        )
        self.audio_engine = AudioEngine(
            sample_rate=SAMPLE_RATE,
            blocksize=BLOCKSIZE,
            channels=1
        )
        
        # Очередь для передачи данных из аудио-потока в GUI
        self.data_queue = queue.Queue()
        
        # Буферы для сглаживания
        self.cents_buffer = deque(maxlen=CENTS_BUFFER_SIZE)
        self.frequency_buffer = deque(maxlen=FREQUENCY_BUFFER_SIZE)
        
        # Текущие значения для плавной анимации
        self.current_cents = 0.0
        self.target_cents = 0.0
        
        # Флаги и счетчики
        self.is_running = False
        self.audio_blocks_received = 0
        
        # Создание UI
        self.create_ui()
        
        # Обработчик закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_ui(self):
        """Создание элементов интерфейса."""
        self.create_tuning_selector()
        self.create_main_display()
        self.create_tuning_meter()
        self.create_control_panel()
    
    def create_tuning_selector(self):
        """Создание селектора строя."""
        tuning_frame = ctk.CTkFrame(
            self.root,
            fg_color=COLOR_BG_MEDIUM,
            corner_radius=15
        )
        tuning_frame.pack(pady=20, padx=30, fill="x")
        
        # Лейбл "СТРОЙ"
        tuning_label = ctk.CTkLabel(
            tuning_frame,
            text="СТРОЙ",
            font=ctk.CTkFont(size=FONT_SIZE_TITLE, weight="bold"),
            text_color=COLOR_TEXT_DIM
        )
        tuning_label.pack(side="left", padx=20, pady=15)
        
        # Названия строев на русском
        tuning_names_ru = {
            "Standard": "Стандарт",
            "Half-step down": "Полутон ниже",
            "Drop D": "Дроп D"
        }
        
        # Segmented button для выбора строя
        self.tuning_var = ctk.StringVar(value="Standard")
        tuning_selector = ctk.CTkSegmentedButton(
            tuning_frame,
            values=TuningConfig.get_tuning_names(),
            variable=self.tuning_var,
            command=self.on_tuning_change,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_BG_DARK,
            selected_color=COLOR_ACCENT,
            selected_hover_color=COLOR_ACCENT,
            unselected_color=COLOR_BG_DARK,
            unselected_hover_color=COLOR_BG_MEDIUM
        )
        tuning_selector.pack(side="left", padx=20, pady=15, expand=True)
    
    def create_main_display(self):
        """Создание главного дисплея с нотой."""
        display_frame = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )
        display_frame.pack(pady=20, fill="both", expand=True)
        
        # Статус
        self.status_label = ctk.CTkLabel(
            display_frame,
            text="ГОТОВ",
            font=ctk.CTkFont(size=FONT_SIZE_STATUS, weight="bold"),
            text_color=COLOR_TEXT_DIM
        )
        self.status_label.pack(pady=(0, 10))
        
        # Главный лейбл - НОТА
        self.note_label = ctk.CTkLabel(
            display_frame,
            text="—",
            font=ctk.CTkFont(size=FONT_SIZE_NOTE, weight="bold"),
            text_color=COLOR_TEXT_DIM
        )
        self.note_label.pack(pady=5)
        
        # Частота
        self.frequency_label = ctk.CTkLabel(
            display_frame,
            text="— Гц",
            font=ctk.CTkFont(size=FONT_SIZE_FREQUENCY),
            text_color=COLOR_TEXT_DIM
        )
        self.frequency_label.pack(pady=3)
        
        # Отклонение в центах
        self.cents_label = ctk.CTkLabel(
            display_frame,
            text="—",
            font=ctk.CTkFont(size=FONT_SIZE_CENTS, weight="bold"),
            text_color=COLOR_TEXT_DIM
        )
        self.cents_label.pack(pady=5)
    
    def create_tuning_meter(self):
        """Создание визуальной шкалы настройки."""
        meter_frame = ctk.CTkFrame(
            self.root,
            fg_color=COLOR_BG_MEDIUM,
            corner_radius=20,
            height=METER_HEIGHT
        )
        meter_frame.pack(pady=15, padx=40, fill="x")
        meter_frame.pack_propagate(False)
        
        # Заголовок
        meter_title = ctk.CTkLabel(
            meter_frame,
            text="ИНДИКАТОР НАСТРОЙКИ",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLOR_TEXT_DIM
        )
        meter_title.pack(pady=(10, 5))
        
        # Контейнер для шкалы
        scale_container = ctk.CTkFrame(meter_frame, fg_color="transparent")
        scale_container.pack(pady=5, padx=30, fill="x")
        
        # Метки границ (-50, 0, +50)
        marks_frame = ctk.CTkFrame(scale_container, fg_color="transparent")
        marks_frame.pack(fill="x", pady=(0, 5))
        
        left_mark = ctk.CTkLabel(
            marks_frame,
            text="-50",
            font=ctk.CTkFont(size=10),
            text_color=COLOR_TEXT_DIM
        )
        left_mark.pack(side="left")
        
        center_mark = ctk.CTkLabel(
            marks_frame,
            text="0",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLOR_TEXT_NORMAL
        )
        center_mark.pack(side="left", expand=True)
        
        right_mark = ctk.CTkLabel(
            marks_frame,
            text="+50",
            font=ctk.CTkFont(size=10),
            text_color=COLOR_TEXT_DIM
        )
        right_mark.pack(side="right")
        
        # Визуальная шкала из сегментов
        self.meter_segments = []
        segments_frame = ctk.CTkFrame(scale_container, fg_color="transparent")
        segments_frame.pack(fill="x", pady=3)
        
        for i in range(METER_SEGMENTS):
            segment = ctk.CTkFrame(
                segments_frame,
                width=10,
                height=SEGMENT_HEIGHT,
                fg_color=COLOR_BG_DARK,
                corner_radius=2
            )
            segment.pack(side="left", padx=1, expand=True, fill="both")
            self.meter_segments.append(segment)
        
        # Индикатор (стрелка)
        indicator_frame = ctk.CTkFrame(scale_container, fg_color="transparent", height=30)
        indicator_frame.pack(fill="x", pady=(3, 0))
        
        self.indicator_canvas_frame = ctk.CTkFrame(
            indicator_frame,
            fg_color="transparent"
        )
        self.indicator_canvas_frame.pack(fill="x")
        
        self.indicator = ctk.CTkLabel(
            self.indicator_canvas_frame,
            text="▼",
            font=ctk.CTkFont(size=20),
            text_color=COLOR_ACCENT
        )
        self.indicator.place(relx=0.5, rely=0, anchor="n")
    
    def create_control_panel(self):
        """Создание панели управления."""
        control_frame = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )
        control_frame.pack(pady=15, padx=40, fill="x")
        
        # Кнопка запуска/остановки
        self.start_button = ctk.CTkButton(
            control_frame,
            text="НАЧАТЬ НАСТРОЙКУ",
            command=self.toggle_tuner,
            font=ctk.CTkFont(size=FONT_SIZE_BUTTON, weight="bold"),
            width=280,
            height=50,
            corner_radius=25,
            fg_color=COLOR_ACCENT,
            hover_color="#00b8dd",
            text_color="#000000"
        )
        self.start_button.pack(pady=10)
        
        # Индикатор уровня сигнала
        self.signal_label = ctk.CTkLabel(
            control_frame,
            text="",
            font=ctk.CTkFont(size=FONT_SIZE_SIGNAL),
            text_color=COLOR_TEXT_DIM
        )
        self.signal_label.pack(pady=10)
    
    def on_tuning_change(self, choice):
        """Обработчик изменения строя."""
        self.current_tuning = choice
    
    def toggle_tuner(self):
        """Запуск/остановка тюнера."""
        if not self.is_running:
            self.start_tuner()
        else:
            self.stop_tuner()
    
    def start_tuner(self):
        """Запуск тюнера."""
        self.is_running = True
        self.start_button.configure(
            text="ОСТАНОВИТЬ",
            fg_color=COLOR_RED,
            hover_color="#dd3333"
        )
        self.status_label.configure(
            text="СЛУШАЮ...",
            text_color=COLOR_ACCENT
        )
        
        # Запуск аудио-потока
        self.audio_engine.start(processing_callback=self.process_audio)
        
        # Запуск обработки очереди
        self.update_gui()
    
    def stop_tuner(self):
        """Остановка тюнера."""
        self.is_running = False
        self.audio_engine.stop()
        
        # Сброс состояния
        self.audio_blocks_received = 0
        self.cents_buffer.clear()
        self.frequency_buffer.clear()
        self.current_cents = 0.0
        self.target_cents = 0.0
        
        self.start_button.configure(
            text="НАЧАТЬ НАСТРОЙКУ",
            fg_color=COLOR_ACCENT,
            hover_color="#00b8dd"
        )
        self.status_label.configure(
            text="ГОТОВ",
            text_color=COLOR_TEXT_DIM
        )
        self.signal_label.configure(text="")
        
        # Сброс дисплея
        self.note_label.configure(text="—", text_color=COLOR_TEXT_DIM)
        self.frequency_label.configure(text="— Гц", text_color=COLOR_TEXT_DIM)
        self.cents_label.configure(text="—", text_color=COLOR_TEXT_DIM)
        
        # Сброс шкалы
        self.update_meter(0, COLOR_TEXT_DIM)
        self.indicator.configure(text_color=COLOR_TEXT_DIM)
    
    def process_audio(self, audio_data: np.ndarray):
        """
        Обработка аудиоданных (вызывается из отдельного потока).
        
        Args:
            audio_data: массив аудиоданных
        """
        self.audio_blocks_received += 1
        
        # Вычисляем RMS
        rms = np.sqrt(np.mean(audio_data ** 2))
        
        # Определяем частоту
        frequency = self.pitch_detector.detect_pitch(audio_data)
        
        # Отправляем данные в очередь
        try:
            if frequency is None:
                self.data_queue.put_nowait({
                    'type': 'signal_level',
                    'rms': rms,
                    'blocks': self.audio_blocks_received
                })
            else:
                # Сглаживание частоты
                self.frequency_buffer.append(frequency)
                avg_frequency = np.mean(self.frequency_buffer)
                
                # Находим ближайшую ноту
                note_name, target_freq, cents = TuningConfig.find_closest_note(
                    avg_frequency,
                    self.current_tuning
                )
                
                # Сглаживание центов
                self.cents_buffer.append(cents)
                smoothed_cents = np.mean(self.cents_buffer)
                
                self.data_queue.put_nowait({
                    'type': 'note',
                    'note': note_name,
                    'frequency': avg_frequency,
                    'target_frequency': target_freq,
                    'cents': smoothed_cents,
                    'rms': rms,
                    'blocks': self.audio_blocks_received
                })
        except queue.Full:
            pass
    
    def update_gui(self):
        """Обновление GUI из очереди (главный поток)."""
        if not self.is_running:
            return
        
        # Обрабатываем данные из очереди
        try:
            while True:
                data = self.data_queue.get_nowait()
                
                if data['type'] == 'note':
                    self.display_tuning_info(
                        data['note'],
                        data['frequency'],
                        data['target_frequency'],
                        data['cents']
                    )
                    self.update_signal_level(data['rms'], data['blocks'])
                elif data['type'] == 'signal_level':
                    self.update_signal_level(data['rms'], data['blocks'])
        except queue.Empty:
            pass
        
        # Плавная анимация индикатора
        self.animate_indicator()
        
        # Повторяем через интервал
        self.root.after(GUI_UPDATE_INTERVAL, self.update_gui)
    
    def animate_indicator(self):
        """Плавная анимация перемещения индикатора."""
        diff = self.target_cents - self.current_cents
        self.current_cents += diff * ANIMATION_SPEED
        
        # Обновляем позицию индикатора
        cents_clamped = max(-50, min(50, self.current_cents))
        rel_pos = (cents_clamped + 50) / 100.0
        
        self.indicator.place(relx=rel_pos, rely=0, anchor="n")
    
    def update_signal_level(self, rms, blocks):
        """
        Обновление индикатора уровня сигнала.
        
        Args:
            rms: уровень RMS сигнала
            blocks: количество обработанных блоков
        """
        if rms < 0.001:
            self.signal_label.configure(
                text=f"Сигнал: очень слабый • Играйте громче",
                text_color=COLOR_RED
            )
        elif rms < 0.01:
            self.signal_label.configure(
                text=f"Сигнал: слабый • Играйте чуть громче",
                text_color=COLOR_ORANGE
            )
        else:
            self.signal_label.configure(
                text=f"Сигнал: хороший • Блоков: {blocks}",
                text_color=COLOR_GREEN
            )
    
    def display_tuning_info(self, note, current_freq, target_freq, cents):
        """
        Отображение информации о настройке.
        
        Args:
            note: название ноты
            current_freq: текущая частота
            target_freq: целевая частота
            cents: отклонение в центах
        """
        # Устанавливаем целевое значение для анимации
        self.target_cents = cents
        
        # Определяем цвет и статус
        abs_cents = abs(cents)
        
        if abs_cents <= THRESHOLD_PERFECT:
            color = COLOR_GREEN
            status = "НАСТРОЕНА"
            meter_color = COLOR_GREEN
        elif abs_cents <= THRESHOLD_ALMOST:
            color = COLOR_YELLOW
            status = "ПОЧТИ"
            meter_color = COLOR_YELLOW
        else:
            color = COLOR_ORANGE
            status = "СЛИШКОМ ВЫСОКО" if cents > 0 else "СЛИШКОМ НИЗКО"
            meter_color = COLOR_ORANGE
        
        # Обновляем дисплей
        self.note_label.configure(text=note, text_color=color)
        freq_text = f"{current_freq:.1f} Гц"
        self.frequency_label.configure(text=freq_text, text_color=color)
        cents_text = f"{cents:+.1f} центов"
        self.cents_label.configure(text=cents_text, text_color=color)
        self.status_label.configure(text=status, text_color=color)
        
        # Обновляем шкалу и индикатор
        self.update_meter(cents, meter_color)
        self.indicator.configure(text_color=color)
    
    def update_meter(self, cents, color):
        """
        Обновление визуальной шкалы.
        
        Args:
            cents: отклонение в центах
            color: цвет активных сегментов
        """
        cents_clamped = max(-50, min(50, cents))
        center_index = 25
        current_index = int(center_index + cents_clamped / 2)
        
        # Обновляем цвет сегментов
        for i, segment in enumerate(self.meter_segments):
            if i == center_index:
                segment.configure(fg_color=COLOR_TEXT_NORMAL)
            elif abs(i - center_index) <= 2:
                if abs(current_index - center_index) <= 2:
                    segment.configure(fg_color=COLOR_GREEN)
                else:
                    segment.configure(fg_color=COLOR_BG_DARK)
            else:
                if (current_index < center_index and i <= center_index and i >= current_index) or \
                   (current_index > center_index and i >= center_index and i <= current_index):
                    segment.configure(fg_color=color)
                else:
                    segment.configure(fg_color=COLOR_BG_DARK)
    
    def on_closing(self):
        """Обработчик закрытия окна."""
        self.stop_tuner()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Запуск приложения."""
        self.root.mainloop()


def main():
    """Главная функция."""
    try:
        app = GuitarTunerGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
