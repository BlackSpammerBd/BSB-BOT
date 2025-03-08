# setup.py
from setuptools import setup, find_packages

setup(
    name="bsb-bot-sp",
    version="1.0.0",
    author="Shawpon Sp",
    author_email="shawponsp6@gmail.com",
    description="A Python package to monitor device events (call logs, SMS, new media) and send logs via Telegram bot.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/BlackSpammerBd/BSB-BOT/",
    packages=find_packages(),
    install_requires=[
        "pyTelegramBotAPI>=4.0.0",
        "psutil",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "black=bsb.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
