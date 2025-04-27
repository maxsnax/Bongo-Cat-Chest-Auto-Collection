import os
import time
import pyautogui
from PIL import Image
import json
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # remove python console import message
import pygame

# ==================================================================
# Configuration & Globals
# ==================================================================
beep_count = 0
click_chest = False
check_interval = 15  # seconds
last_collection = 0

check_count = 0
collected_count = 0

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
    global beep_count, click_chest, _last_settings_mtime

    try:
        mtime = os.path.getmtime(SETTINGS_FILE)
        if mtime != _last_settings_mtime:
            _last_settings_mtime = mtime
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                beep_count = data.get('beep_count', beep_count)
                click_chest = data.get('click_chest', click_chest)
            settings_text = f"[ Settings: beep_count={beep_count} click_chest={str(bool(click_chest)):<5} ]"
            print('-' * len(settings_text))
            print(settings_text)
            print('-' * len(settings_text))

    except Exception as e:
        print(f"[Settings Error] {e}")


def take_screenshot() -> Image.Image:
    return pyautogui.screenshot()


def find_chest(screenshot):
    global check_count
    global beep_count

    check_count += 1
    found_box = pyautogui.locate(CHEST_IMAGE, screenshot, grayscale=True, confidence=0.85)

    log_status(bool(found_box))

    if found_box:  # return the coordinates of the center of the image
        play_beep(beep_count)
        center_x = found_box.left + found_box.width // 2
        center_y = found_box.top + found_box.height // 2
        return center_x, center_y

    return None


def play_beep(n):
    for x in range(n):  # play beep sound n times
        pygame.mixer.Sound(SOUND_PATH).play()
        time.sleep(0.5)  # wait for sound to finish playing


def log_status(found: bool):
    timestamp = time.strftime("%H:%M:%S")
    status = "Found" if found else "No chest"

    # format the print statement with specific width for each part
    print(f"[ Check #{check_count:<7} {timestamp:<14} {status:<10} ]")


def process_chest():
    global collected_count
    global beep_count
    global check_interval
    global click_chest
    global last_collection

    screenshot = take_screenshot()
    match = find_chest(screenshot)

    if match:

        if click_chest:
            play_beep(beep_count)
            pyautogui.moveTo(match, duration=0.2)  # duration helps with click detection on chest
            pyautogui.click()

            # check to make sure the chest is collected
            time.sleep(1)
            screenshot = take_screenshot()
            match = find_chest(screenshot)

            # match indicates unsuccessful chest collection
            if match:
                check_interval = 5  # give 5s between next click attempt
            # no match means chest collected
            else:
                last_collection = time.time()
                collected_count += 1
                check_interval = 1800  # check again for next chest in 30 minutes
                print(f"[ Chest Collected: #{collected_count:<22} ]")

        return True

    # if chest hasn't collected >30mins then reset check interval
    elif time.time() - last_collection > 1800:
        check_interval = 15

    return False


# ==================================================================
# Main Loop
# ==================================================================
def main():
    global check_count
    global last_collection

    # set the last collection to now for 30min interval checks later
    last_collection = time.time()

    pygame.mixer.init()
    play_beep(3)

    while True:
        load_settings()
        process_chest()
        time.sleep(check_interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Exit]")
