print("initializing...")
import numpy as np
import pydirectinput
from imagehandler import *
import mss
from pynput import keyboard
import threading
import time
from datetime import datetime
import cv2
import keyboard as kb
import cProfile
from random import randint
from enum import Enum, auto
from window_info import get_display_info
pydirectinput.PAUSE = 0

################## OPTIONS ##############################
# General options
PRINT_FRAME_TIME = False        # Print the delay between subsequent processing ticks (frames)
                                # A delay less than 300ms should be good enough

# Collection behavior
COLLECT_BANANAS = False         # Make the bot attempt to collect bananas
                                # Currently, the bot can mix up a lot of things as
                                # bananas. You should keep this disabled normally.
COLLECT_ENCOUNTERS = True       # Make the bot attempt to collect encounters
COLLECT_GOLD = True             # Make the bot attempt to collect gold

# Movement behavior
ENABLE_MOVEMENT = True          # Turn this off to disable movement altogether. Useful for testing.
AVOID_BLOONS = True             # Make the bot attempt to avoid getting hit by red & blue bloons.
                                # This is not necessary if you have a good healing build
                                # Turning this on will make it very hard for the bot to 
                                # move anywhere meaningful in dense stages as it will constantly
                                # be dodging bloons
DODGE_BULLETS = True            # Make the bot attempt to avoid purple attacks from the bosses
MAINTAIN_MOVEMENT = True        # Make the bot keep moving in the last moved direction instead of 
                                # standing still

# Upgrade behavior
USE_OCR = True                  # Disabling this cause the bot to choose random upgrades, 
                                # and skips initializing EasyOCR which massively improve initialization speed. 
                                # Useful for testing.
UPGRADE_FILE = 'boss_upgrades.txt'   # List of upgrades sorted by priority. Each upgrade should be on a separate line.


##################  POSITIONS  ###########################
play_area = {"left": 686, "top": 46, "width":(1228-686), "height":(1013-46)}

player_position = {"x": 956-686, "y": 462-46}

play_button = [
    {"x": 924, "y": 819, "color": 0xffef1d},
    {"x": 922, "y": 776, "color": 0xffef23},
    {"x": 1025, "y": 793, "color": 0xffffff},
    {"x": 1110, "y": 771, "color": 0xffef37},
    {"x": 1104, "y": 823, "color": 0xffeb10}
]

pause_button = [
    {"x": 712, "y": 62, "color": 0xfff34c},
    {"x": 714, "y": 78, "color": 0xffef1d},
    {"x": 739, "y": 75, "color": 0xffffff},
    {"x": 754, "y": 72, "color": 0xffef2f},
    {"x": 749, "y": 96, "color": 0xffbd1a}
]

upgrade_menu = [
    {"x": 786, "y": 192, "color": 0x08cf00},
    {"x": 875, "y": 178, "color": 0x2de12b},
    {"x": 1041, "y": 120, "color": 0xffee26},
    {"x": 1127, "y": 191, "color": 0x08cf00},
    {"x": 1064, "y": 197, "color": 0xffffff}
]

upgrade_text_regions = [
    [752, 520, 868, 573],
    [902,571, 1017, 629],
    [1055, 516, 1169, 573]
]

exp_region = [
    {"x": 689, "y": 209},
    {"x": 1222, "y": 759}
]

win_screen = [
    {"x": 800, "y": 869, "color": 0xffee16},
    {"x": 844, "y": 868, "color": 0xffef11},
    {"x": 898, "y": 868, "color": 0xffef17},
    {"x": 1028, "y": 905, "color": 0x52dfff},
    {"x": 1131, "y": 901, "color": 0x52dfff},
    {"x": 1109, "y": 901, "color": 0x52dfff}
]

rate_game_screen = [
    {"x": 820, "y": 633, "color": 0xffef21},
    {"x": 904, "y": 190, "color": 0xffffff},
    {"x": 996, "y": 638, "color": 0xffef25},
    {"x": 1095, "y": 624, "color": 0xffef16},
    {"x": 953, "y": 266, "color": 0xffffff}
]

tips_screen = [
    {"x": 823, "y": 469, "color": 0xffffff},
    {"x": 1043, "y": 691, "color": 0xffee18},
    {"x": 913, "y": 466, "color": 0x843800},
    {"x": 1013, "y": 692, "color": 0xffeb08},
    {"x": 891, "y": 734, "color": 0xffeb00},
    {"x": 849, "y": 228, "color": 0xf79f43}
]

health_shop_screen = [
    {"x": 798, "y": 288, "color": 0xffffff},
    {"x": 880, "y": 449, "color": 0xfe1c50},
    {"x": 921, "y": 507, "color": 0xffef2e},
    {"x": 999, "y": 518, "color": 0xffed1d},
    {"x": 1083, "y": 466, "color": 0xdf0a77},
    {"x": 1040, "y": 340, "color": 0xff1c51}
]

ad_screen = [
    {"x": 794, "y": 206, "color": 0xffffff},
    {"x": 897, "y": 702, "color": 0xffef23},
    {"x": 1105, "y": 703, "color": 0x9430e7},
    {"x": 813, "y": 704, "color": 0x9430e7},
    {"x": 1126, "y": 203, "color": 0xad0000}
]

daily_quests_screen = [
    {"x": 796, "y": 249, "color": 0xffffff},
    {"x": 909, "y": 232, "color": 0xe4f7ff},
    {"x": 785, "y": 507, "color": 0x843800},
    {"x": 1137, "y": 691, "color": 0x843800},
    {"x": 796, "y": 301, "color": 0xcbc0bb}
]

boss_fight_screen = [
    {"x": 971, "y": 94, "color": 0xffffff},
    {"x": 1064, "y": 66, "color": 0x120900},
    {"x": 1074, "y": 67, "color": 0x120700},
    {"x": 1068, "y": 92, "color": 0xffffff}
]

boss_victory_screen = [
    {"x": 1064, "y": 66, "color": 0xffffff},
    {"x": 1073, "y": 66, "color": 0xffffff},
    {"x": 1066, "y": 92, "color": 0xffffff}
]
mini_boss_screen = [
    {"x": 1012, "y": 92, "color": 0xffffff},
    {"x": 1020, "y": 65, "color": 0x0},
    {"x": 1021, "y": 93, "color": 0x0}
]

mini_boss_victory_screen = [
    {"x": 1012, "y": 92, "color": 0xffffff},
    {"x": 1020, "y": 65, "color": 0xffffff},
    {"x": 1021, "y": 93, "color": 0x0}
]
##################  COLORS  ###########################
blop_color = 0x70EFFD
purple_orb_attack_color = 0xFF4AFF
banana_outline_color = 0x985A15
bloon_color = [
    0xFE2D38, #RED
    0x16AAFF  #BLUE
]
encounter_color = [
    0x78C9A6
]

gold_color = [
    0xfff74b,
    0xffe70c,
    0xffdf04
]
################## SPRITES ############################
player_hp_sprite = cv2.imread('sprites/player_hp_scaled.png')


################## PROGRAM GLOBALS ####################
sct = mss.MSS()
stop_event = threading.Event()
running = True
starting = False
latest_frame = None
screen_objects = []
frame_lock = threading.Lock()
quit_hotkey = None
pause_hotkey = None
start_hotkey = None
info_hotkey = None
listener = None
pausing = False
playing = False 

upgrades = []
game_objects =  {
    "bananas": [], 
    "boss_bullets": [], 
    "heart_center": None, 
    "best_direction" : "", 
    "bloons": [],
    "encounters": [],
    "golds": []
}
heart_location = None
is_boss_fight = False

################# FUNCTION DEFINITIONS ################
def time_ms():
    return (time.time_ns() // 1000000)

def text_distance(str1, str2):
    dp = arr = [[0] * len(str2) for _ in range(len(str1))]
    dp[0][0] = 0
    if str1[0] != str2[0]:
        dp[0][0] = 1
    
    for i in range(0, len(str1)):
        for j in range(0, len(str2)):
            dist = max(i, j) + 1
            if i > 0:
                dist = min(dist, dp[i-1][j] + 1)
            if j > 0:
                dist = min(dist, dp[i][j-1] + 1)
            if i > 0 and j > 0 and str1[i] == str2[j]:
                dist = min(dist, dp[i-1][j-1])
            if i > 0 and j > 0 and str1[i] != str2[j]:
                dist = min(dist, dp[i-1][j-1] + 1)
            if i > 0 or j > 0:
                dp[i][j] = dist

    return dp[len(str1) - 1][len(str2) - 1]

def init():
    if USE_OCR:
        init_ocr()
    
    #fix upgrade location
    for index, region in enumerate(upgrade_text_regions):
        x1, y1, x2, y2 = region
        x1 -= play_area['left']
        x2 -= play_area['left']
        y1 -= play_area['top']
        y2 -= play_area['top']
        upgrade_text_regions[index] = [x1,y1,x2,y2]

    #port upgrades
    content = ""
    try:
        with open(UPGRADE_FILE, "r", encoding="utf-8") as f:
                content = f.readlines()
    except FileNotFoundError:
        print("File does not exist.")
        exit(0)
    except PermissionError:
        print("Permission denied.")
        exit(0)
    except OSError as e:
        print(f"Failed to read file: {e}")
        exit(0)
    for line in content:
        cur = line.strip()
        if (len(cur)):
            upgrades.append(cur)

    #init hotkey functions
    global pause_hotkey, quit_hotkey, start_hotkey, info_hotkey, listener
    quit_hotkey = keyboard.HotKey(
        keyboard.HotKey.parse('<ctrl>+q'),
        quit_program
    )

    pause_hotkey = keyboard.HotKey(
        keyboard.HotKey.parse('<ctrl>+p'),
        pause_bot
    )

    start_hotkey = keyboard.HotKey(
        keyboard.HotKey.parse('<ctrl>+w'),
        start_bot
    )

    info_hotkey = keyboard.HotKey(
        keyboard.HotKey.parse('<ctrl>+i'),
        print_display_info
    )
    
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )

    listener.start()

def quit_program():
    print("Ctrl+Q detected!")
    stop_event.set()

def pause_bot():
    global pausing
    if (pausing):
        print("Unpaused")
    else:
        print("Paused")
    pausing = not pausing

def start_bot():
    global starting
    print("Starting bot")
    starting = True 

def print_display_info():
    try:
        info = get_display_info()
    except (LookupError, OSError) as error:
        print(f"Unable to inspect the game window: {error}")
        return

    print(f"Game window: {info.game_window_title}")
    print(
        "Primary screen resolution: "
        f"{info.primary_screen_resolution[0]}x{info.primary_screen_resolution[1]}"
    )
    print(
        "Game monitor resolution: "
        f"{info.game_monitor_resolution[0]}x{info.game_monitor_resolution[1]}"
    )
    print(
        f"Game resolution (client area): "
        f"{info.game_resolution[0]}x{info.game_resolution[1]}"
    )
    print(
        f"Game window position (outer, screen): "
        f"x={info.window_position[0]}, y={info.window_position[1]}"
    )
    print(
        f"Game window size (outer): "
        f"{info.window_size[0]}x{info.window_size[1]}"
    )
    print(
        f"Game client position (screen): "
        f"x={info.client_position[0]}, y={info.client_position[1]}"
    )

def on_press(key):
    quit_hotkey.press(listener.canonical(key))
    pause_hotkey.press(listener.canonical(key))
    start_hotkey.press(listener.canonical(key))
    info_hotkey.press(listener.canonical(key))

def on_release(key):
    quit_hotkey.release(listener.canonical(key))
    pause_hotkey.release(listener.canonical(key))
    start_hotkey.release(listener.canonical(key))
    info_hotkey.release(listener.canonical(key))

def stopMovement():
    pydirectinput.keyUp('a')
    pydirectinput.keyUp('w')
    pydirectinput.keyUp('s')
    pydirectinput.keyUp('d')

def moveTo(player_position, location):
    if not ENABLE_MOVEMENT:
        return 
    playerx, playery = player_position
    posx, posy = location 
    slope = abs((posy-playery)/(posx-playerx))
    inp = ""
    if (slope < 1.732):
        if (playerx < posx):
            inp += "d"
        else:
            inp += "a"

    if (slope > 0.577):
        if (playery < posy):
            inp += "s"
        else:
            inp += "w"

    for chr in inp:
        pydirectinput.keyDown(chr)
    return inp

def moveAway(player_position, location):
    if not ENABLE_MOVEMENT:
        return 
    
    playerx, playery = player_position
    posx, posy = location 
    slope = abs((posy-playery)/(posx-playerx))
    inp = ""
    if (slope < 1.732):
        if (playerx < posx):
            inp += "a"
        else:
            inp += "d"

    if (slope > 0.577):
        if (playery < posy):
            inp += "w"
        else:
            inp += "s"

    for chr in inp:
        pydirectinput.keyDown(chr)
    return inp

# Moves to the right of the previous direction. Call repeatedly to get the bot to move in circle.
def moveCircle(last_direction):
    if not ENABLE_MOVEMENT:
        return 
    
    cycle = ['a','aw','w','wd','d','sd','s','as']
    index = cycle.index(last_direction) if last_direction in cycle else -1
    index = (index + 1) % len(cycle)
    last_direction = cycle[index]
    for char in last_direction:
        pydirectinput.keyDown(char)
    return last_direction

# Press the movement keys specified in the input string
def moveToDirection(best_direction):
    if not ENABLE_MOVEMENT:
        return
    
    for char in best_direction:
        pydirectinput.keyDown(char)

def sq_distance(first, second):
    x1,y1 = first
    x2,y2 = second
    return (x1 - x2)**2 + (y1 - y2)**2

def getDodgePosition(heart_center, bullets):
    closest = None
    secondClosest = None
    for bullet in bullets:
        x,y,w,h = bullet
        x += w/2
        y += h/2
        cur = (x, y)
        if closest is None or sq_distance(closest, heart_center) > sq_distance(cur, heart_center):
            secondClosest = closest 
            closest = cur
        elif secondClosest is None or sq_distance(secondClosest, heart_center) > sq_distance(cur, heart_center):
            secondClosest = cur
    heart_center = np.array(heart_center)
    v = np.array(heart_center) - np.array(closest)
    if secondClosest is not None:
        v = np.array(closest) - np.array(secondClosest)
    final_position = heart_center + v
    x, y = final_position
    x = round(x)
    y = round(y)
    screen_objects.append([x-10,y-10, x+10,y+10, (255,255,255), "dodge"])
    return final_position 

def getNearest(bloons, player_position):
    playerx, playery = player_position
    nearest = None
    minDist = 999999999
    for bloon in bloons:
        x,y,w,h = bloon
        centerx, centery = (x+w/2), (y+h/2)
        dist = (centerx - playerx)**2 + (centery - playery)**2
        if (dist < minDist):
            minDist = dist
            nearest = bloon
    return nearest, dist
    
def pickUpgrade(img):
    if not USE_OCR:
        x1,y1,x2,y2 = upgrade_text_regions[0]
        x1 += play_area["left"]
        x2 += play_area["left"]
        y1 += play_area["top"]
        y2 += play_area["top"]
        return (x1,y1,x2,y2), 'random'
    
    current_upgrades = []
    for x1,y1,x2,y2 in upgrade_text_regions:
        text, conf = getText(img, x1,y1,x2,y2)
        if (conf > 0):
            current_upgrades.append(text.lower())
        else:
            x1,y1,x2,y2 = upgrade_text_regions[0]
            x1 += play_area["left"]
            x2 += play_area["left"]
            y1 += play_area["top"]
            y2 += play_area["top"]
            return (x1,y1,x2,y2), 'unknown'
        print(current_upgrades[-1])
    best = upgrade_text_regions[0]
    text = 'unknown'
    for ref in upgrades:
        if (text != 'unknown'):
            break
        for index, upgrade in enumerate(current_upgrades):
            dist = text_distance(ref, upgrade)
            if dist <= 3:
                best, text = upgrade_text_regions[index], (ref + "/" + upgrade)

    x1,y1,x2,y2 = best
    x1 += play_area["left"]
    x2 += play_area["left"]
    y1 += play_area["top"]
    y2 += play_area["top"]
    best = [x1,y1,x2,y2]
    return best, text

def getObjects():
    global latest_frame, screen_objects, game_objects, is_boss_fight
    newObjects = []

    bananas = []
    encounters = []
    boss_bullets = []
    golds = []
    bloons = []
    heart_center = None
    best_direction = ""

    if not is_boss_fight:
        if COLLECT_BANANAS:
            bananas, _, banana_objects = findColorCluster(latest_frame, banana_outline_color, 100, 1000, 1, "bananas", banana_verifier)    
            newObjects.extend(banana_objects)

        if COLLECT_ENCOUNTERS:
            encounters, _, encounter_objects = findColorCluster(latest_frame, encounter_color, 250, 1000, 5, "encounters")
            newObjects.extend(encounter_objects)

        if COLLECT_GOLD:
            golds, _, gold_objects = findColorCluster(latest_frame, gold_color, 60, 300, 9, "gold", gold_verifier)
            newObjects.extend(gold_objects)
    
    if DODGE_BULLETS and is_boss_fight:
        boss_bullets, _, bullet_objects = findColorCluster(latest_frame, purple_orb_attack_color, 40, 1000, 9, "boss_bullets", bullet_verifier)
        newObjects.extend(bullet_objects)

    if AVOID_BLOONS and not is_boss_fight:
        bloons, _, bloons_objects = findColorCluster(latest_frame, bloon_color, 50, 500, 3,"bloons", bloon_verifier)
        newObjects.extend(bloons_objects)

    if is_boss_fight:
        hearts, heart_center= searchSprite(latest_frame, player_hp_sprite, "heart", FIRST_APPEARANCE)
        newObjects.extend(hearts)

    best_direction, _, blop_regions = findMaxColorRegion(latest_frame, blop_color, 150)
    newObjects.extend(blop_regions)

    screen_objects = newObjects
    game_objects = {
        "bananas": bananas, 
        "boss_bullets": boss_bullets, 
        "heart_center": heart_center, 
        "best_direction" : best_direction, 
        "bloons": bloons,
        "encounters": encounters,
        "golds": golds
    }

def banana_verifier(x,y,w,h,area):
    return w/h < 1.3 and h/w < 1.3

def bloon_verifier(x,y,w,h,area):
    x += w/2
    y += h/2
    return sq_distance((x,y), player_position.values()) < 25000

def gold_verifier(x,y,w,h,area):
    x += w/2
    y += h/2
    return w/h < 2 and h/w < 2 and area < 250 and sq_distance((x,y), player_position.values()) > 10000

def bullet_verifier(x,y,w,h,area):
    if (heart_location is None):
        return True 
    return sq_distance((x,y), heart_location) < 20000

##################### MAIN LOOP #############################
init()
print("Finished bot initialization.\n" 
    + "Ctrl + W: Start playing\n"
    + "Ctrl + P: Pause\n"
    + "Ctrl + I: Show display and game window information\n"
    + "Ctrl + Q: Quit program\n")

while not stop_event.is_set() and not starting:
    time.sleep(0.5)


class BotState(Enum):
    MENU = auto()
    PLAYING = auto()
    BOSS_FIGHT = auto()


def handle_upgrade():
    if USE_OCR:
        time.sleep(0.3)  # Sleep to make sure everything loads up first
    current_time = time_ms()
    (x1, y1, x2, y2), text = pickUpgrade(latest_frame)
    while text == "unknown" and time_ms() - current_time < 1000:
        (x1, y1, x2, y2), text = pickUpgrade(latest_frame)
    print("upgrade:" + text)
    screen_objects.append([x1, y1, x2, y2, (0, 0, 255), text])
    pydirectinput.leftClick((x1 + x2) // 2, (y1 + y2) // 2)


def handle_normal_play(last_direction):
    stopMovement()

    bananas = game_objects["bananas"]
    if COLLECT_BANANAS and len(bananas):
        x, y, w, h = bananas[0]
        center = (x + w / 2, y + h / 2)
        return moveTo(player_position.values(), center)

    bloons = game_objects["bloons"]
    if AVOID_BLOONS and len(bloons):
        (x, y, w, h), _ = getNearest(bloons, player_position.values())
        center = (x + w / 2, y + h / 2)
        moveAway(player_position.values(), center)
        return last_direction

    golds = game_objects["golds"]
    if COLLECT_GOLD and len(golds):
        (x, y, w, h), _ = getNearest(golds, player_position.values())
        center = (x + w / 2, y + h / 2)
        return moveTo(player_position.values(), center)

    encounters = game_objects["encounters"]
    if COLLECT_ENCOUNTERS and len(encounters):
        x, y, w, h = encounters[0]
        center = (x + w / 2, y + h / 2)
        return moveTo(player_position.values(), center)

    best_direction = game_objects["best_direction"]
    if len(best_direction) == 0 and MAINTAIN_MOVEMENT:
        if len(last_direction) == 0:
            last_direction = ["w", "a", "s", "d"][randint(0, 3)]
        best_direction = last_direction
    else:
        last_direction = best_direction

    moveToDirection(best_direction)
    return last_direction


def finish_round(game_timer):
    print("done")
    new_timer = time_ms()
    with open("log.txt", "a") as file:
        file.write(
            "Finished in: "
            + str(new_timer - game_timer)
            + "ms at:"
            + str(datetime.now())
            + "\n"
        )
    stopMovement()
    return new_timer


def handle_menu_state():
    if checkColor(play_button, latest_frame)[0]:
        print("menu")
        pydirectinput.leftClick(
            play_button[0]["x"],
            play_button[0]["y"],
        )

    if checkColor(pause_button, latest_frame)[0]:
        global playing, is_boss_fight
        print("playing")
        playing = True
        is_boss_fight = False
        return BotState.PLAYING

    handle_menu_screens()
    return BotState.MENU


def handle_menu_screens():
    screens = (
        (win_screen, "won"),
        (rate_game_screen, "rate"),
        (tips_screen, "tips"),
        (health_shop_screen, "health shop"),
        (ad_screen, "ad"),
        (daily_quests_screen, "daily quest"),
    )
    for screen, label in screens:
        if checkColor(screen, latest_frame)[0]:
            print(label)
            pydirectinput.leftClick(screen[0]["x"], screen[0]["y"])


def transition_to_menu(last_direction, game_timer, boss_action_timer):
    global playing, is_boss_fight

    playing = False
    is_boss_fight = False
    game_timer = finish_round(game_timer)
    return BotState.MENU, last_direction, game_timer, boss_action_timer


def handle_playing_state(last_direction, game_timer, boss_action_timer):
    global playing, is_boss_fight

    if checkColor(play_button, latest_frame)[0]:
        return transition_to_menu(last_direction, game_timer, boss_action_timer)

    if checkColor(win_screen, latest_frame)[0]:
        playing = False
        game_timer = finish_round(game_timer)
        handle_menu_screens()
        return BotState.MENU, last_direction, game_timer, boss_action_timer

    if checkColor(upgrade_menu, latest_frame)[0]:
        print("upgrading")
        handle_upgrade()
        return BotState.PLAYING, last_direction, game_timer, boss_action_timer

    if (
        checkColor(boss_fight_screen, latest_frame)[0]
        or checkColor(mini_boss_screen, latest_frame)[0]
    ):
        print("boss fight")
        is_boss_fight = True
        boss_action_timer = time_ms()
        return BotState.BOSS_FIGHT, last_direction, game_timer, boss_action_timer

    last_direction = handle_normal_play(last_direction)
    return BotState.PLAYING, last_direction, game_timer, boss_action_timer


def handle_boss_fight_state(last_direction, game_timer, boss_action_timer):
    global heart_location, playing, is_boss_fight

    if checkColor(play_button, latest_frame)[0]:
        return transition_to_menu(last_direction, game_timer, boss_action_timer)

    if checkColor(win_screen, latest_frame)[0]:
        playing = False
        game_timer = finish_round(game_timer)
        handle_menu_screens()
        return BotState.MENU, last_direction, game_timer, boss_action_timer

    if checkColor(upgrade_menu, latest_frame)[0]:
        print("upgrading")
        handle_upgrade()
        return BotState.BOSS_FIGHT, last_direction, game_timer, boss_action_timer

    if checkColor(mini_boss_victory_screen, latest_frame)[0]:
        print("miniboss killed")
        is_boss_fight = False
        return BotState.PLAYING, last_direction, game_timer, boss_action_timer

    if checkColor(boss_victory_screen, latest_frame)[0]:
        print("boss killed")
        is_boss_fight = False
        pydirectinput.leftClick(
            pause_button[0]["x"],
            pause_button[0]["y"],
        )
        return BotState.PLAYING, last_direction, game_timer, boss_action_timer

    heart_center = game_objects["heart_center"]
    if heart_center is not None:
        heart_location = heart_center

    boss_bullets = game_objects["boss_bullets"]
    if heart_location is not None and DODGE_BULLETS and len(boss_bullets):
        stopMovement()
        x, y = getDodgePosition(heart_location, boss_bullets)
        print(x, y)
        moveTo(heart_location, (x, y))
        boss_action_timer = time_ms()
    elif time_ms() - boss_action_timer >= 1500:
        stopMovement()
        time.sleep(0.1)
        last_direction = moveCircle(last_direction)
        boss_action_timer = time_ms()

    return BotState.BOSS_FIGHT, last_direction, game_timer, boss_action_timer


def bot_loop():
    global running, playing
    state = BotState.MENU
    last_direction = ''
    game_timer = time_ms()
    boss_action_timer = game_timer

    while not stop_event.is_set():
        if pausing:
            time.sleep(1)
            continue

        if state is BotState.MENU:
            state = handle_menu_state()
        elif state is BotState.PLAYING:
            state, last_direction, game_timer, boss_action_timer = handle_playing_state(
                last_direction,
                game_timer,
                boss_action_timer,
            )
        else:
            state, last_direction, game_timer, boss_action_timer = handle_boss_fight_state(
                last_direction,
                game_timer,
                boss_action_timer,
            )

        if state in (BotState.PLAYING, BotState.BOSS_FIGHT):
            time.sleep(0.1)
        else:
            time.sleep(1)

    if playing:
        playing = False
        game_timer = finish_round(game_timer)

    running = False

def profilerThread():
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        bot_loop()
    finally:
        profiler.disable()
        profiler.dump_stats("thread_profile.prof")

def visionThread():
    frame_counter = 0
    frame_timer = time_ms()
    while bot_thread.is_alive():
        if playing:
            while (pausing):
                time.sleep(1)
            frame_counter += 1
            new_frame_timer = time_ms()
            if (PRINT_FRAME_TIME):
                print("frame:"+str(frame_counter)+" timer:" + str(new_frame_timer - frame_timer)) 
            frame_timer = new_frame_timer
            getObjects()

#profiler_thread = threading.Thread(target=profilerThread, daemon=True)
#profiler_thread.start()

bot_thread = threading.Thread(target=bot_loop, daemon=True)
bot_thread.start()

vision_thread = threading.Thread(target=visionThread, daemon=True)
vision_thread.start()

def display_loop():
    global latest_frame, screen_objects
    img = grabScreenshot(sct)
    with frame_lock:
        latest_frame = img.copy()
    img = addObjects(img, screen_objects)
    cv2.imshow("Live View", img)
    cv2.waitKey(1)

try:
    while bot_thread.is_alive():
        display_loop()
finally:
    cv2.destroyAllWindows()
    listener.stop()
    listener.join()
    sct.close()
    print("Exited cleanly.")