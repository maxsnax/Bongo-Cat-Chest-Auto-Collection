import os
import time
import pygame
import pyautogui
import argparse
import json

# ==================================================================
# Configuration & Globals
# ==================================================================
play_sound = False
click_chest = False
check_interval = 60  # seconds

count = 0
collected = 0

BASE_DIR = os.path.dirname(__file__)
CHEST_IMAGE = os.path.join(BASE_DIR, 'images', 'bongo_chest.png')
SCREENSHOT_PATH = os.path.join(BASE_DIR, 'images', 'bongo_screenshot.png')
SOUND_PATH = os.path.join(BASE_DIR, 'sounds', 'adjusted_beep.wav')
SETTINGS_FILE = os.path.join(BASE_DIR, 'settings.json')
_last_settings_mtime = None


# ==================================================================
# Helper Functions
# ==================================================================
def load_settings():
    global play_sound, click_chest, _last_settings_mtime

    try:
        mtime = os.path.getmtime(SETTINGS_FILE)
        if mtime != _last_settings_mtime:
            _last_settings_mtime = mtime
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                play_sound = data.get('play_sound', play_sound)
                click_chest = data.get('click_chest', click_chest)
            print(f"[Settings Reloaded] play_sound={play_sound}, click_chest={click_chest}")
    except Exception as e:
        print(f"[Settings Error] {e}")


def take_screenshot(path: str):
    screenshot = pyautogui.screenshot()
    screenshot.save(path)
    return screenshot


def find_chest(screenshot_path: str):
    return pyautogui.locate(CHEST_IMAGE, screenshot_path, grayscale=True, confidence=0.85)


def play_beep():
    pygame.mixer.init()  # Initialize the mixer
    for x in range(3):
        pygame.mixer.Sound(SOUND_PATH).play()
        time.sleep(0.5)  # Wait for the sound to finish playing


def log_status(found: bool):
    timestamp = time.strftime("%H:%M:%S")
    print(f"#{collected}/{count} {timestamp}:", end=" ")
    print("Found chest" if found else "No chest")


def process_chest():
    global collected
    take_screenshot(SCREENSHOT_PATH)
    match = find_chest(SCREENSHOT_PATH)

    log_status(bool(match))

    if match:
        collected += 1
        center_x = match.left + 10
        center_y = match.top + 10

        if play_sound:
            play_beep()

        if click_chest:
            pyautogui.moveTo(center_x, center_y)
            pyautogui.click()


# ==================================================================
# Main Loop
# ==================================================================
def main():
    global count

    play_beep()

    while True:
        load_settings()
        count += 1
        process_chest()
        time.sleep(check_interval)


if __name__ == "__main__":
    main()
