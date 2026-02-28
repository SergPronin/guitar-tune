# Установка Гитарного Тюнера Pro

## Быстрая установка

### Вариант 1: Запуск из исходников (рекомендуется)

```bash
# 1. Клонируйте репозиторий
git clone <repo-url>
cd guitar-tune

# 2. Установите зависимости
pip install -r requirements.txt

# 3. Запустите приложение
python guitar_tuner.py
```

### Вариант 2: Установка как пакет

```bash
# 1. Клонируйте репозиторий
git clone <repo-url>
cd guitar-tune

# 2. Установите пакет
pip install -e .

# 3. Запустите из любого места
guitar-tuner
```

### Вариант 3: Установка через pip (если опубликован)

```bash
pip install guitar-tuner-pro
guitar-tuner
```

## Требования

- Python 3.10 или выше
- Микрофон (встроенный или внешний)
- macOS, Linux или Windows

## Зависимости

Все зависимости устанавливаются автоматически:

- numpy >= 1.24.0
- scipy >= 1.10.0
- sounddevice >= 0.4.6
- customtkinter >= 5.2.0

## Первый запуск

### macOS

1. **Дайте разрешение на микрофон:**
   ```
   Системные настройки → Конфиденциальность и безопасность → Микрофон
   ```
   Разрешите доступ для Terminal или Python

2. **Перезапустите Terminal**

3. **Запустите приложение:**
   ```bash
   python guitar_tuner.py
   ```

### Windows

1. **Дайте разрешение на микрофон:**
   ```
   Параметры → Конфиденциальность → Микрофон
   ```
   Разрешите доступ приложениям

2. **Запустите приложение:**
   ```bash
   python guitar_tuner.py
   ```

### Linux

1. **Убедитесь, что установлен PortAudio:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install portaudio19-dev
   
   # Fedora
   sudo dnf install portaudio-devel
   
   # Arch
   sudo pacman -S portaudio
   ```

2. **Запустите приложение:**
   ```bash
   python guitar_tuner.py
   ```

## Проверка установки

```bash
# Проверьте версию Python
python --version  # Должно быть >= 3.10

# Проверьте установку зависимостей
python -c "import numpy, scipy, sounddevice, customtkinter; print('OK')"

# Запустите тест микрофона
python tests/test_microphone.py
```

## Устранение проблем

### "ModuleNotFoundError"

```bash
# Переустановите зависимости
pip install -r requirements.txt --force-reinstall
```

### "No module named 'src'"

```bash
# Запускайте из корневой директории проекта
cd guitar-tune
python guitar_tuner.py
```

### Микрофон не работает

```bash
# Запустите диагностику
python tests/diagnose_audio.py
```

## Удаление

```bash
# Если установлен как пакет
pip uninstall guitar-tuner-pro

# Удалите директорию
rm -rf guitar-tune
```

## Разработка

### Установка для разработки

```bash
# Клонируйте репозиторий
git clone <repo-url>
cd guitar-tune

# Установите в режиме разработки
pip install -e ".[dev]"

# Запустите тесты
pytest tests/
```

### Структура проекта

```
guitar-tune/
├── guitar_tuner.py      # Главный файл
├── setup.py            # Setup скрипт
├── requirements.txt    # Зависимости
├── README.md          # Документация
├── LICENSE           # Лицензия
│
├── src/              # Исходный код
│   ├── core/        # Ядро
│   └── ui/          # Интерфейс
│
├── tests/           # Тесты
└── docs/            # Документация
```

---

Подробнее: [README.md](README.md)
