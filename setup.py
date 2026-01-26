"""Setup для установки пакета."""

from setuptools import setup, find_packages

setup(
    name="facecrop",
    version="1.0.0",
    description="Автоматический кроп фотографий до квадрата с сохранением лица",
    author="FaceCrop",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "mediapipe>=0.10.0",
        "Pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "gradio>=4.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "facecrop=facecrop.main:main",
        ],
    },
)

