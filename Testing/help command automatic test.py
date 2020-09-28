import time
from pynput.keyboard import Key, Controller

keyboard = Controller()

command_list = ["8ball", "choose", "flip", "coinflip", "flipcoin", "roll", "rolldie", "dieroll", "say", "help", "google", "googleit", "googlesearch", "language", "detect", "morsecode", "morse", "ping", "translate", "wikipedia", "ban", "clear", "kick", "prefix", "unban", ""]

time.sleep(5)

for com in command_list:
	keyboard.type(f"g!help {com}")
	keyboard.press(Key.enter)
	keyboard.release(Key.enter)
	time.sleep(3)
