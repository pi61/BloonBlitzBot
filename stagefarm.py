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
pydirectinput.PAUSE = 0
##################  POSITIONS  ###########################
play_area = {"left": 686, "top": 46, "width":(1228-686), "height":(1013-46)}

player_position = {"x": 956, "y": 462}

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

boss_fight_screen = [
    {"x": 971, "y": 94, "color": 0xffffff}
    ,{"x": 1033, "y": 93, "color": 0xffffff}
    ,{"x": 1068, "y": 92, "color": 0xffffff}
]

mini_boss_screen = [
    {"x": 1012, "y": 92, "color": 0xffffff},
    {"x": 1020, "y": 65, "color": 0x0},
    {"x": 1021, "y": 93, "color": 0x0}
]

mode_completion = [
    [
        {"x": 834, "y": 317, "color": 0xffffff},
        {"x": 840, "y": 317, "color": 0xffffff},
        {"x": 848, "y": 309, "color": 0xffffff}
    ],
    [
        {"x": 902, "y": 316, "color": 0xffffff},
        {"x": 905, "y": 318, "color": 0xffffff},
        {"x": 916, "y": 310, "color": 0xffffff}
    ],
    [
        {"x": 970, "y": 315, "color": 0xffffff},
        {"x": 975, "y": 318, "color": 0xffffff},
        {"x": 985, "y": 309, "color": 0xffffff}
    ],
    [
        {"x": 1038, "y": 316, "color": 0xffffff},
        {"x": 1043, "y": 319, "color": 0xffffff},
        {"x": 1053, "y": 309, "color": 0xffffff}
    ],
    [
        {"x": 1106, "y": 316, "color": 0xffffff},
        {"x": 1110, "y": 319, "color": 0xffffff},
        {"x": 1120, "y": 309, "color": 0xffffff}
    ]
]

##################  COLORs  ###########################
blop_color = 0x70EFFD
purple_orb_attack = 0xFF4AFF
banana_outline_color = 0x985A15
bloon_color = {
    "red":0xFE2D38,
    "blue":0x16AAFF
}

################## SPRITES ############################
player_hp_sprite = cv2.imread('sprites/player_hp_scaled.png')

################## GAME DATA ##########################
upgrades = []

################## PROGRAM GLOBALS ####################
sct = mss.MSS()
stop_event = threading.Event()
running = True
latest_frame = None
objects = []
heart_location = None
last_heart_update = 0
frame_lock = threading.Lock()
quit_hotkey = None
pause_hotkey = None
listener = None
pausing = False

################# FUNCTION DEFINITIONS ################
def init():
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
        with open("upgrades.txt", "r", encoding="utf-8") as f:
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
    global pause_hotkey, quit_hotkey, listener
    quit_hotkey = keyboard.HotKey(
        keyboard.HotKey.parse('<ctrl>+q'),
        quit_program
    )

    pause_hotkey = keyboard.HotKey(
        keyboard.HotKey.parse('p'),
        pause_bot
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
        print("Unpaused!")
    else:
        print("Paused!")
    pausing = not pausing

def on_press(key):
    quit_hotkey.press(listener.canonical(key))
    pause_hotkey.press(listener.canonical(key))

def on_release(key):
    quit_hotkey.release(listener.canonical(key))
    pause_hotkey.release(listener.canonical(key))

def moveTo(heart_center, location):
    heartx, hearty = heart_center
    posx, posy = location 
    inp = ""
    if (heartx < posx):
        inp += "d"
    else:
        inp += "a"

    if (hearty < posy):
        inp += "s"
    else:
        inp += "w"

    print(inp)
    for chr in inp:
        pydirectinput.keyDown(chr)

def sq_distance(first, second):
    return (first[0] - second[0])**2 + (first[1] - second[1])**2

def getDodgePosition(heart_center, bullets):
    closest = None
    secondClosest = None
    for bullet in bullets:
        x,y,w,h = bullet
        x += w/2
        y += h/2
        cur = (x, y)
        if closest is None or sq_distance(closest, heart_center) > sq_distance(cur, heart_center):
            closest = cur
            secondClosest = closest 
        elif secondClosest is None or sq_distance(secondClosest, heart_center) > sq_distance(cur, heart_center):
            secondClosest = cur
    heart_center = np.array(heart_center)
    v1 = np.array(closest) - heart_center
    v2 = np.array(secondClosest) - heart_center 
    final_position = heart_center - v1 - v2 
    return final_position 

def pickUpgrade(img):
    current_upgrades = []
    for x1,y1,x2,y2 in upgrade_text_regions:
        text, conf = getText(img, x1,y1,x2,y2)
        if (conf > 0):
            current_upgrades.append(text.lower())
        else:
            current_upgrades.append("unknown")
        print(current_upgrades[-1])
    best = upgrade_text_regions[0]
    text = "unknown"
    for ref in upgrades:
        if (text != "unknown"):
            break
        for index, upgrade in enumerate(current_upgrades):
            if ref.find(upgrade) != -1 or upgrade.find(ref) != -1:
                best, text = upgrade_text_regions[index], upgrade

    x1,y1,x2,y2 = best
    x1 += play_area["left"]
    x2 += play_area["left"]
    y1 += play_area["top"]
    y2 += play_area["top"]
    best = [x1,y1,x2,y2]
    return best, text

def banana_verifier(w,h,area):
    return (w/h < 1.3 and h/w < 1.3)

mode_selector = [
    (851, 298),
    (960, 299),
    (1064, 303),
    (964, 453),
    (957, 627)
]

def goToMode(index):
    mode_button = (841, 803)
    x, y = mode_button
    pydirectinput.click(x, y)
    time.sleep(1)
    x, y = mode_selector[index]
    pydirectinput.click(x,y)
    time.sleep(1)
    pydirectinput.leftClick(
        play_button[0]["x"],
        play_button[0]["y"]
    )

stage_selection_sequence = [
    (1141, 925),
    (1113, 813),
    (948, 926)
]

def getNextStage():
    for x, y in stage_selection_sequence:
        pydirectinput.click(x, y)
        time.sleep(1)
##################### MAIN LOOP #############################
init()
print("Finished bot initialization. Press 'W' to start playing. Press Ctrl + Q to exit.")
while not stop_event.is_set() and not kb.is_pressed('w') :
    continue

def bot_loop():
    global running, heart_location
    last_direction = ""
    game_timer = time.time_ns() // 1000000
    while not stop_event.is_set():
        while (pausing):
            time.sleep(1)
        if checkColor(play_button, latest_frame)[0]:
            print("menu")
            
            # time.sleep(1)
            # x1,y1,x2,y2 = [828, 211 , 1108, 256]
            # x1 -= play_area['left']
            # x2 -= play_area['left']
            # y1 -= play_area['top']
            # y2 -= play_area['top']
            # stage_name, _ = getText(latest_frame, x1, y1, x2 ,y2)
            # stage_name = stage_name.lower()
            # print(stage_name)
         
            # cur_mode = None
            # for index, stage in enumerate(mode_completion):
            #     if not checkColor(stage, latest_frame)[0]:
            #         cur_mode = index
            #         break

            # if stage_name.find("stage 50") != -1:
            #     cur_mode = 0

            # if (cur_mode is None):
            #     getNextStage()
            # else:
            #     goToMode(cur_mode)
            pydirectinput.leftClick(
                play_button[0]["x"],
                play_button[0]["y"]
            )


        if checkColor(pause_button, latest_frame)[0]:
            print("playing")
            is_boss_fight = False
            frame_counter = 0
            timer = time.time_ns() // 1000000
            while not checkColor(win_screen, latest_frame)[0] and not stop_event.is_set():
                while (pausing):
                    time.sleep(1)
                time.sleep(0.2)
                if checkColor(upgrade_menu, latest_frame)[0]:
                    print("upgrading")
                    time.sleep(0.2) #Sleep to make sure everything loads up first
                    (x1,y1,x2,y2), text = pickUpgrade(latest_frame)
                    print("upgrade:"+text)
                    objects.append([x1,y1,x2,y2,(0,0,255),text])
                    x = (x1+x2)//2
                    y = (y1+y2)//2
                    pydirectinput.leftClick(x, y)

                # elif checkColor(mini_boss_screen, latest_frame)[0]:
                #     pydirectinput.keyUp('a')
                #     pydirectinput.keyUp('w')
                #     pydirectinput.keyUp('s')
                #     pydirectinput.keyUp('d')
                #     print("mini_boss")
                #     while checkColor(mini_boss_screen, latest_frame)[0]:
                #         while (pausing):
                #             time.sleep(1)
                #         time.sleep(0.2)
                #         if checkColor(upgrade_menu, latest_frame)[0]:
                #             print("upgrading")
                #             time.sleep(0.2) #Sleep to make sure everything loads up first
                #             (x1,y1,x2,y2), text = pickUpgrade(latest_frame)
                #             print("upgrade:"+text)
                #             objects.append([x1,y1,x2,y2,(0,0,255),text])
                #             x = (x1+x2)//2
                #             y = (y1+y2)//2
                #             pydirectinput.leftClick(x, y)

                # elif checkColor(boss_fight_screen, latest_frame)[0]:
                #     pydirectinput.keyUp('a')
                #     pydirectinput.keyUp('w')
                #     pydirectinput.keyUp('s')
                #     pydirectinput.keyUp('d')
                #     print("boss")
                #     while checkColor(boss_fight_screen, latest_frame)[0]:
                #         while (pausing):
                #             time.sleep(1)
                #         time.sleep(0.2)
                #         if checkColor(upgrade_menu, latest_frame)[0]:
                #             print("upgrading")
                #             time.sleep(0.2) #Sleep to make sure everything loads up first
                #             (x1,y1,x2,y2), text = pickUpgrade(latest_frame)
                #             print("upgrade:"+text)
                #             objects.append([x1,y1,x2,y2,(0,0,255),text])
                #             x = (x1+x2)//2
                #             y = (y1+y2)//2
                #             pydirectinput.leftClick(x, y)

                # else:
                #     keys = ['w','a','s','d']
                #     best_direction, _, blop_regions = findMaxColorRegion(latest_frame, blop_color, 20)

                #     if len(best_direction) == 0:
                #         if len(last_direction) == 0:
                #             last_direction = keys[randint(0,3)]
                #         best_direction = last_direction
                #     else:
                #         last_direction = best_direction

                #     pydirectinput.keyUp('a')
                #     pydirectinput.keyUp('w')
                #     pydirectinput.keyUp('s')
                #     pydirectinput.keyUp('d')
                #     time.sleep(0.1)
                #     for char in best_direction:
                #         pydirectinput.keyDown(char)
                #     time.sleep(0.1)

            print("done")
            pydirectinput.keyUp('a')
            pydirectinput.keyUp('w')
            pydirectinput.keyUp('s')
            pydirectinput.keyUp('d')
            with open("log.txt", "a") as file:
                new_timer = time.time_ns() // 1000000
                file.write("Finished in: " + str(new_timer - game_timer)+"ms at:" + str(datetime.now()) + "\n")
                game_timer = new_timer
                file.close()
            
            pydirectinput.keyUp('a')
            pydirectinput.keyUp('w')
            pydirectinput.keyUp('s')
            pydirectinput.keyUp('d')

        if checkColor(win_screen, latest_frame)[0]:
            print("won")
            pydirectinput.leftClick(win_screen[0]["x"], win_screen[0]["y"])
            # time.sleep(10)

        if checkColor(rate_game_screen, latest_frame)[0]:
            print("rate")
            pydirectinput.leftClick(rate_game_screen[0]["x"], rate_game_screen[0]["y"])

        if checkColor(tips_screen, latest_frame)[0]:
            print("tips")
            pydirectinput.leftClick(tips_screen[0]["x"], tips_screen[0]["y"])

        if checkColor(health_shop_screen, latest_frame)[0]:
            print("health shop")
            pydirectinput.leftClick(health_shop_screen[0]["x"], health_shop_screen[0]["y"])

        if checkColor(ad_screen, latest_frame)[0]:
            print("ad")
            pydirectinput.leftClick(ad_screen[0]["x"], ad_screen[0]["y"])

        if checkColor(upgrade_menu, latest_frame)[0]:
            print("upgrading")
            time.sleep(0.2) #Sleep to make sure everything loads up first
            (x1,y1,x2,y2), text = pickUpgrade(latest_frame)
            print("upgrade:"+text)
            objects.append([x1,y1,x2,y2,(0,0,255),text])
            x = (x1+x2)//2
            y = (y1+y2)//2
            pydirectinput.leftClick(x, y)
        time.sleep(1)

    running = False

def profilerThread():
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        bot_loop()
    finally:
        profiler.disable()
        profiler.dump_stats("thread_profile.prof")

#profiler_thread = threading.Thread(target=profilerThread, daemon=True)
#profiler_thread.start()

bot_thread = threading.Thread(target=bot_loop, daemon=True)
bot_thread.start()

def display_loop():
    global latest_frame, objects
    img = grabScreenshot(sct)
    with frame_lock:
        latest_frame = img.copy()
    img = addObjects(img, objects)
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