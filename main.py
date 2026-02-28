"""
Гитарный тюнер с профессиональным графическим интерфейсом (CustomTkinter).
Дизайн: минималистичный, фокус на процессе настройки, плавная анимация.
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

import customtkinter as ctk
import queue
import numpy as np
from config import TuningConfig
from pitch_detector import PitchDetector
from audio_engine import AudioEngine
from collections import deque


class GuitarTunerGUI:
    """Профессиональный графический интерфейс гитарного тюнера."""
    
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
    
    def __init__(self):
        """Инициализация GUI."""
        
        # Настройка темы
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Создание главного окна
        self.root = ctk.CTk()
        self.root.title("Guitar Tuner Pro")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        self.root.configure(fg_color=self.COLOR_BG_DARK)
        
        # Инициализация компонентов
        self.sample_rate = 44100
        self.blocksize = 2048
        self.current_tuning = "Standard"
        
        self.pitch_detector = PitchDetector(
            sample_rate=self.sample_rate,
            noise_threshold=0.01
        )
        self.audio_engine = AudioEngine(
            sample_rate=self.sample_rate,
            blocksize=self.blocksize,
            channels=1
        )
        
        # Очередь для передачи данных из аудио-потока в GUI
        self.data_queue = queue.Queue()
        
        # Буфер для сглаживания (увеличен для плавности)
        self.cents_buffer = deque(maxlen=8)
        self.frequency_buffer = deque(maxlen=3)
        
        # Текущие значения для плавной анимации
        self.current_cents = 0.0
        self.target_cents = 0.0
        self.animation_speed = 0.3  # Скорость интерполяции (0-1)
        
        # Флаг работы
        self.is_running = False
        
        # Счетчики
        self.audio_blocks_received = 0
        
        # Создание UI
        self.create_ui()
        
        # Обработчик закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_ui(self):
        """Создание элементов интерфейса."""
        
        # Верхняя панель - выбор строя
        self.create_tuning_selector()
        
        # Центральная область - главный индикатор
        self.create_main_display()
        
        # Шкала настройки (визуальный метр)
        self.create_tuning_meter()
        
        # Нижняя панель - управление
        self.create_control_panel()
    
    def create_tuning_selector(self):
        """Создание селектора строя."""
        tuning_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.COLOR_BG_MEDIUM,
            corner_radius=15
        )
        tuning_frame.pack(pady=20, padx=30, fill="x")
        
        # Лейбл "Tuning"
        tuning_label = ctk.CTkLabel(
            tuning_frame,
            text="TUNING",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.COLOR_TEXT_DIM
        )
        tuning_label.pack(side="left", padx=20, pady=15)
        
        # Segmented button для выбора строя
        self.tuning_var = ctk.StringVar(value="Standard")
        tuning_selector = ctk.CTkSegmentedButton(
            tuning_frame,
            values=TuningConfig.get_tuning_names(),
            variable=self.tuning_var,
            command=self.on_tuning_change,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.COLOR_BG_DARK,
            selected_color=self.COLOR_ACCENT,
            selected_hover_color=self.COLOR_ACCENT,
            unselected_color=self.COLOR_BG_DARK,
            unselected_hover_color=self.COLOR_BG_MEDIUM
        )
        tuning_selector.pack(side="left", padx=20, pady=15, expand=True)
    
    def create_main_display(self):
        """Создание главного дисплея с нотой."""
        display_frame = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )
        display_frame.pack(pady=20, fill="both", expand=True)
        
        # Статус (сверху, мелким шрифтом)
        self.status_label = ctk.CTkLabel(
            display_frame,
            text="READY",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.COLOR_TEXT_DIM
        )
        self.status_label.pack(pady=(0, 10))
        
        # Главный лейбл - НОТА (огромный шрифт)
        self.note_label = ctk.CTkLabel(
            display_frame,
            text="—",
            font=ctk.CTkFont(size=100, weight="bold"),
            text_color=self.COLOR_TEXT_DIM
        )
        self.note_label.pack(pady=5)
        
        # Частота (средний шрифт)
        self.frequency_label = ctk.CTkLabel(
            display_frame,
            text="— Hz",
            font=ctk.CTkFont(size=18),
            text_color=self.COLOR_TEXT_DIM
        )
        self.frequency_label.pack(pady=3)
        
        # Отклонение в центах (крупный шрифт)
        self.cents_label = ctk.CTkLabel(
            display_frame,
            text="—",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.COLOR_TEXT_DIM
        )
        self.cents_label.pack(pady=5)
    
    def create_tuning_meter(self):
        """Создание визуальной шкалы настройки."""
        meter_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.COLOR_BG_MEDIUM,
            corner_radius=20,
            height=140
        )
        meter_frame.pack(pady=15, padx=40, fill="x")
        meter_frame.pack_propagate(False)
        
        # Заголовок
        meter_title = ctk.CTkLabel(
            meter_frame,
            text="TUNING METER",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.COLOR_TEXT_DIM
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
            text_color=self.COLOR_TEXT_DIM
        )
        left_mark.pack(side="left")
        
        center_mark = ctk.CTkLabel(
            marks_frame,
            text="0",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.COLOR_TEXT_NORMAL
        )
        center_mark.pack(side="left", expand=True)
        
        right_mark = ctk.CTkLabel(
            marks_frame,
            text="+50",
            font=ctk.CTkFont(size=10),
            text_color=self.COLOR_TEXT_DIM
        )
        right_mark.pack(side="right")
        
        # Создаем визуальную шкалу из сегментов
        self.meter_segments = []
        segments_frame = ctk.CTkFrame(scale_container, fg_color="transparent")
        segments_frame.pack(fill="x", pady=3)
        
        # 51 сегмент: от -50 до +50
        num_segments = 51
        for i in range(num_segments):
            segment = ctk.CTkFrame(
                segments_frame,
                width=10,
                height=25,
                fg_color=self.COLOR_BG_DARK,
                corner_radius=2
            )
            segment.pack(side="left", padx=1, expand=True, fill="both")
            self.meter_segments.append(segment)
        
        # Индикатор положения (стрелка/указатель)
        indicator_frame = ctk.CTkFrame(scale_container, fg_color="transparent", height=30)
        indicator_frame.pack(fill="x", pady=(3, 0))
        
        self.indicator_canvas_frame = ctk.CTkFrame(
            indicator_frame,
            fg_color="transparent"
        )
        self.indicator_canvas_frame.pack(fill="x")
        
        # Создаем индикатор (треугольник)
        self.indicator = ctk.CTkLabel(
            self.indicator_canvas_frame,
            text="▼",
            font=ctk.CTkFont(size=20),
            text_color=self.COLOR_ACCENT
        )
        self.indicator.place(relx=0.5, rely=0, anchor="n")
    
    def create_control_panel(self):
        """Создание панели управления."""
        control_frame = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )
        control_frame.pack(pady=15, padx=40, fill="x")
        
        # Кнопка запуска/остановки (большая, центральная)
        self.start_button = ctk.CTkButton(
            control_frame,
            text="START TUNING",
            command=self.toggle_tuner,
            font=ctk.CTkFont(size=16, weight="bold"),
            width=280,
            height=50,
            corner_radius=25,
            fg_color=self.COLOR_ACCENT,
            hover_color="#00b8dd",
            text_color="#000000"
        )
        self.start_button.pack(pady=10)
        
        # Индикатор уровня сигнала (минималистичный)
        self.signal_label = ctk.CTkLabel(
            control_frame,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=self.COLOR_TEXT_DIM
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
            text="STOP TUNING",
            fg_color=self.COLOR_RED,
            hover_color="#dd3333"
        )
        self.status_label.configure(
            text="LISTENING...",
            text_color=self.COLOR_ACCENT
        )
        
        # Запуск аудио-потока
        self.audio_engine.start(processing_callback=self.process_audio)
        
        # Запуск обработки очереди в GUI потоке
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
            text="START TUNING",
            fg_color=self.COLOR_ACCENT,
            hover_color="#00b8dd"
        )
        self.status_label.configure(
            text="READY",
            text_color=self.COLOR_TEXT_DIM
        )
        self.signal_label.configure(text="")
        
        # Сброс дисплея
        self.note_label.configure(text="—", text_color=self.COLOR_TEXT_DIM)
        self.frequency_label.configure(text="— Hz", text_color=self.COLOR_TEXT_DIM)
        self.cents_label.configure(text="—", text_color=self.COLOR_TEXT_DIM)
        
        # Сброс шкалы
        self.update_meter(0, self.COLOR_TEXT_DIM)
        self.indicator.configure(text_color=self.COLOR_TEXT_DIM)
    
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
                # Добавляем в буфер для сглаживания
                self.frequency_buffer.append(frequency)
                
                # Вычисляем среднюю частоту
                avg_frequency = np.mean(self.frequency_buffer)
                
                # Находим ближайшую ноту
                note_name, target_freq, cents = TuningConfig.find_closest_note(
                    avg_frequency,
                    self.current_tuning
                )
                
                # Добавляем центы в буфер для сглаживания
                self.cents_buffer.append(cents)
                smoothed_cents = np.mean(self.cents_buffer)
                
                # Отправляем данные в очередь для GUI
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
        """Обновление GUI из очереди (вызывается в главном потоке)."""
        if not self.is_running:
            return
        
        # Обрабатываем все данные из очереди
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
        
        # Повторяем через 30 мс (примерно 33 FPS)
        self.root.after(30, self.update_gui)
    
    def animate_indicator(self):
        """Плавная анимация перемещения индикатора."""
        # Интерполяция между текущим и целевым значением
        diff = self.target_cents - self.current_cents
        self.current_cents += diff * self.animation_speed
        
        # Обновляем позицию индикатора
        # Преобразуем центы (-50...+50) в relative position (0...1)
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
                text=f"Signal: too low • Play louder",
                text_color=self.COLOR_RED
            )
        elif rms < 0.01:
            self.signal_label.configure(
                text=f"Signal: weak • Play slightly louder",
                text_color=self.COLOR_ORANGE
            )
        else:
            self.signal_label.configure(
                text=f"Signal: good • Blocks: {blocks}",
                text_color=self.COLOR_GREEN
            )
    
    def display_tuning_info(self, note, current_freq, target_freq, cents):
        """
        Отображение информации о настройке с цветовой индикацией.
        
        Args:
            note: название ноты
            current_freq: текущая частота
            target_freq: целевая частота
            cents: отклонение в центах (уже сглаженное)
        """
        # Устанавливаем целевое значение для анимации
        self.target_cents = cents
        
        # Определяем цвет и статус на основе отклонения
        abs_cents = abs(cents)
        
        if abs_cents <= 5:
            # Идеально настроено
            color = self.COLOR_GREEN
            status = "IN TUNE"
            meter_color = self.COLOR_GREEN
        elif abs_cents <= 10:
            # Почти настроено
            color = self.COLOR_YELLOW
            status = "ALMOST" if cents > 0 else "ALMOST"
            meter_color = self.COLOR_YELLOW
        else:
            # Не настроено
            color = self.COLOR_ORANGE
            status = "TOO HIGH" if cents > 0 else "TOO LOW"
            meter_color = self.COLOR_ORANGE
        
        # Обновляем главную ноту
        self.note_label.configure(text=note, text_color=color)
        
        # Обновляем частоту
        freq_text = f"{current_freq:.1f} Hz"
        self.frequency_label.configure(text=freq_text, text_color=color)
        
        # Обновляем отклонение
        cents_text = f"{cents:+.1f} cents"
        self.cents_label.configure(text=cents_text, text_color=color)
        
        # Обновляем статус
        self.status_label.configure(text=status, text_color=color)
        
        # Обновляем визуальную шкалу
        self.update_meter(cents, meter_color)
        
        # Обновляем цвет индикатора
        self.indicator.configure(text_color=color)
    
    def update_meter(self, cents, color):
        """
        Обновление визуальной шкалы (сегментов).
        
        Args:
            cents: отклонение в центах
            color: цвет активных сегментов
        """
        # Преобразуем центы в индекс сегмента (0-50)
        cents_clamped = max(-50, min(50, cents))
        center_index = 25  # Центр шкалы
        current_index = int(center_index + cents_clamped / 2)
        
        # Обновляем цвет сегментов
        for i, segment in enumerate(self.meter_segments):
            if i == center_index:
                # Центральный сегмент всегда выделен
                segment.configure(fg_color=self.COLOR_TEXT_NORMAL)
            elif abs(i - center_index) <= 2:
                # Зона идеальной настройки (±5 центов)
                if abs(current_index - center_index) <= 2:
                    segment.configure(fg_color=self.COLOR_GREEN)
                else:
                    segment.configure(fg_color=self.COLOR_BG_DARK)
            else:
                # Остальные сегменты
                if (current_index < center_index and center_index <= i <= current_index) or \
                   (current_index > center_index and current_index <= i <= center_index) or \
                   (current_index < center_index and i <= center_index and i >= current_index) or \
                   (current_index > center_index and i >= center_index and i <= current_index):
                    # Активные сегменты
                    segment.configure(fg_color=color)
                else:
                    # Неактивные сегменты
                    segment.configure(fg_color=self.COLOR_BG_DARK)
    
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
