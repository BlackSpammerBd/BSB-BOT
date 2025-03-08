# bsb/cli.py
import argparse
import threading
import os
from .monitor import BSBMonitor

def main():
    parser = argparse.ArgumentParser(
        description="BSB - Device Monitoring via Telegram Bot",
        usage="black -t <telegram_bot_token> --c <telegram_chat_id> | black -stop"
    )
    parser.add_argument("-t", "--token", help="Telegram bot token")
    parser.add_argument("-c", "--chatid", help="Telegram chat ID")
    parser.add_argument("-stop", action="store_true", help="Stop the monitoring process")
    args = parser.parse_args()

    if args.stop:
        # Issue stop signal by creating the stop.signal file
        with open("stop.signal", "w") as f:
            f.write("stop")
        print("Stop signal issued. Monitoring will be stopped soon.")
        return

    if not args.token or not args.chatid:
        parser.error("Both --token and --chatid are required to start monitoring.")
    
    monitor = BSBMonitor(args.token, args.chatid)
    # Start Telegram bot polling in a separate thread
    poll_thread = threading.Thread(target=monitor.bot.polling, kwargs={"non_stop": True})
    poll_thread.daemon = True
    poll_thread.start()
    # Start monitoring
    monitor.start_monitoring()
    # Keep the main thread alive
    try:
        while True:
            pass
    except KeyboardInterrupt:
        monitor.stop_monitoring()

if __name__ == "__main__":
    main()
