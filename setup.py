# setup.py
from setuptools import setup, find_packages

setup(
    name="proyecto_ocr",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'easyocr==1.7.1',
        'streamlit==1.32.1',
        'opencv-python==4.8.1.78',
        'numpy==1.26.4',
        'pandas==2.2.1',
        'Pillow==10.2.0',
        'python-dotenv==1.0.0',
        'pytest==8.0.2'
    ],
)