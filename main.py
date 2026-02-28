"""
Гитарный тюнер с графическим интерфейсом (CustomTkinter).
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
import threading
import queue
import numpy as np
from config import TuningConfig
from pitch_detector import PitchDetector
from audio_engine import AudioEngine


class GuitarTunerGUI:
    """Графический интерфейс гитарного тюнера."""
    
    def __init__(self):
        """Инициализация GUI."""
        
        # Настройка темы
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Создание главного окна
        self.root = ctk.CTk()
        self.root.title("Гитарный Тюнер 🎸")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
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
        
        # Буфер сглаживания
        self.frequency_buffer = []
        self.buffer_size = 3
        
        # Флаг работы
        self.is_running = False
        
        # Создание UI
        self.create_ui()
        
        # Обработчик закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_ui(self):
        """Создание элементов интерфейса."""
        
        # Заголовок
        title_label = ctk.CTkLabel(
            self.root,
            text="🎸 Гитарный Тюнер",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Выбор строя
        tuning_frame = ctk.CTkFrame(self.root)
        tuning_frame.pack(pady=10, padx=20, fill="x")
        
        tuning_label = ctk.CTkLabel(
            tuning_frame,
            text="Строй:",
            font=ctk.CTkFont(size=16)
        )
        tuning_label.pack(side="left", padx=10)
        
        self.tuning_var = ctk.StringVar(value="Standard")
        tuning_menu = ctk.CTkOptionMenu(
            tuning_frame,
            variable=self.tuning_var,
            values=TuningConfig.get_tuning_names(),
            command=self.on_tuning_change,
            font=ctk.CTkFont(size=14),
            width=200
        )
        tuning_menu.pack(side="left", padx=10)
        
        # Отображение нот строя
        self.tuning_notes_label = ctk.CTkLabel(
            tuning_frame,
            text=self.get_tuning_notes_text("Standard"),
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.tuning_notes_label.pack(side="left", padx=10)
        
        # Основная область - текущая нота
        note_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        note_frame.pack(pady=30)
        
        self.note_label = ctk.CTkLabel(
            note_frame,
            text="—",
            font=ctk.CTkFont(size=120, weight="bold"),
            text_color="gray"
        )
        self.note_label.pack()
        
        # Частота
        self.frequency_label = ctk.CTkLabel(
            note_frame,
            text="Играйте на гитаре",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.frequency_label.pack(pady=5)
        
        # Индикатор отклонения (Progressbar)
        tuning_indicator_frame = ctk.CTkFrame(self.root)
        tuning_indicator_frame.pack(pady=20, padx=40, fill="x")
        
        # Метки шкалы
        scale_frame = ctk.CTkFrame(tuning_indicator_frame, fg_color="transparent")
        scale_frame.pack(fill="x")
        
        left_label = ctk.CTkLabel(
            scale_frame,
            text="Слабее (-50)",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        left_label.pack(side="left")
        
        center_label = ctk.CTkLabel(
            scale_frame,
            text="ИДЕАЛЬНО (0)",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="gray"
        )
        center_label.pack(side="left", expand=True)
        
        right_label = ctk.CTkLabel(
            scale_frame,
            text="Сильнее (+50)",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        right_label.pack(side="right")
        
        # Прогресс-бар (от 0 до 100, где 50 = идеально настроено)
        self.tuning_progressbar = ctk.CTkProgressBar(
            tuning_indicator_frame,
            width=500,
            height=20,
            progress_color="gray"
        )
        self.tuning_progressbar.pack(pady=10)
        self.tuning_progressbar.set(0.5)  # Центр
        
        # Текст отклонения
        self.cents_label = ctk.CTkLabel(
            tuning_indicator_frame,
            text="0 центов",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="gray"
        )
        self.cents_label.pack(pady=5)
        
        # Статус
        self.status_label = ctk.CTkLabel(
            self.root,
            text="",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.status_label.pack(pady=10)
        
        # Кнопка запуска/остановки
        self.start_button = ctk.CTkButton(
            self.root,
            text="▶ Начать настройку",
            command=self.toggle_tuner,
            font=ctk.CTkFont(size=16, weight="bold"),
            width=200,
            height=40,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.start_button.pack(pady=20)
    
    def get_tuning_notes_text(self, tuning_name):
        """Возвращает строку с нотами выбранного строя."""
        notes = [note for note, _ in TuningConfig.get_tuning(tuning_name)]
        return f"({', '.join(notes)})"
    
    def on_tuning_change(self, choice):
        """Обработчик изменения строя."""
        self.current_tuning = choice
        self.tuning_notes_label.configure(
            text=self.get_tuning_notes_text(choice)
        )
    
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
            text="⏸ Остановить",
            fg_color="red",
            hover_color="darkred"
        )
        self.status_label.configure(
            text="🎤 Слушаю микрофон...",
            text_color="green"
        )
        
        # Запуск аудио-потока
        self.audio_engine.start(processing_callback=self.process_audio)
        
        # Запуск обработки очереди в GUI потоке
        self.update_gui()
    
    def stop_tuner(self):
        """Остановка тюнера."""
        self.is_running = False
        self.audio_engine.stop()
        
        self.start_button.configure(
            text="▶ Начать настройку",
            fg_color="green",
            hover_color="darkgreen"
        )
        self.status_label.configure(
            text="Тюнер остановлен",
            text_color="gray"
        )
        
        # Сброс дисплея
        self.note_label.configure(text="—", text_color="gray")
        self.frequency_label.configure(
            text="Нажмите 'Начать настройку'",
            text_color="gray"
        )
        self.cents_label.configure(text="0 центов", text_color="gray")
        self.tuning_progressbar.set(0.5)
        self.tuning_progressbar.configure(progress_color="gray")
    
    def process_audio(self, audio_data: np.ndarray):
        """
        Обработка аудиоданных (вызывается из отдельного потока).
        
        Args:
            audio_data: массив аудиоданных
        """
        # Определяем частоту
        frequency = self.pitch_detector.detect_pitch(audio_data)
        
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
            self.current_tuning
        )
        
        # Отправляем данные в очередь для GUI
        try:
            self.data_queue.put_nowait({
                'note': note_name,
                'frequency': avg_frequency,
                'target_frequency': target_freq,
                'cents': cents
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
                self.display_tuning_info(
                    data['note'],
                    data['frequency'],
                    data['target_frequency'],
                    data['cents']
                )
        except queue.Empty:
            pass
        
        # Повторяем через 50 мс
        self.root.after(50, self.update_gui)
    
    def display_tuning_info(self, note, current_freq, target_freq, cents):
        """
        Отображение информации о настройке.
        
        Args:
            note: название ноты
            current_freq: текущая частота
            target_freq: целевая частота
            cents: отклонение в центах
        """
        # Определяем цвет и статус
        if abs(cents) <= 5:
            color = "green"
            status = "✅ НАСТРОЕНА"
        elif cents > 0:
            color = "#FFA500"  # оранжевый
            status = "↑ ПЕРЕТЯНУТА"
        else:
            color = "#FFA500"  # оранжевый
            status = "↓ НЕДОТЯНУТА"
        
        # Обновляем ноту
        self.note_label.configure(text=note, text_color=color)
        
        # Обновляем частоту
        freq_text = f"{current_freq:.2f} Гц (цель: {target_freq:.2f} Гц)"
        self.frequency_label.configure(text=freq_text, text_color=color)
        
        # Обновляем отклонение
        cents_text = f"{cents:+.1f} центов"
        self.cents_label.configure(text=cents_text, text_color=color)
        
        # Обновляем прогресс-бар
        # Преобразуем центы (-50...+50) в прогресс (0...1)
        # -50 центов = 0, 0 центов = 0.5, +50 центов = 1.0
        cents_clamped = max(-50, min(50, cents))
        progress = (cents_clamped + 50) / 100.0
        self.tuning_progressbar.set(progress)
        
        # Цвет прогресс-бара
        if abs(cents) <= 5:
            self.tuning_progressbar.configure(progress_color="green")
        else:
            self.tuning_progressbar.configure(progress_color="#FFA500")
        
        # Обновляем статус
        self.status_label.configure(text=status, text_color=color)
    
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
