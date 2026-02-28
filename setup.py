"""
Setup скрипт для Гитарного Тюнера Pro.
"""

from setuptools import setup, find_packages
import os

# Читаем README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Читаем requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="guitar-tuner-pro",
    version="1.0.0",
    author="Guitar Tuner Team",
    description="Профессиональное приложение для настройки гитары в реальном времени",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/guitar-tuner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "guitar-tuner=src.ui.guitar_tuner_gui:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md"],
    },
)
