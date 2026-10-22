import time 
import mss
import numpy as np
import cv2
from pynput import mouse, keyboard

reader = None
play_area = {"left": 686, "top": 46, "width":(1228-686), "height":(1013-46)}

def init_ocr():
    global reader

    if reader is None:
        import easyocr
        reader = easyocr.Reader(['en'])

def hex_to_bgr(hex_color):
    r = (hex_color >> 16) & 0xFF
    g = (hex_color >> 8) & 0xFF
    b = hex_color & 0xFF
    return [b, g, r]

def bgr_to_hex(b, g, r):
    return ((int(r) << 16) + (int(g) << 8) + int(b))

def map_coordinate(x, y):
    x = x - play_area["left"]
    y = y - play_area["top"]
    return x, y

# Return pixel data in play area
def grabScreenshot(sct):
    sct_img = sct.grab(play_area)

    # Pixel data is in BGRA format
    return np.array(sct_img)

# Return color as BGRA
def getColor(x, y, img):
    if (img is None):
        return None
    x, y = map_coordinate(x, y)
    b,g,r,_ = img[y][x]
    return [int(b),int(g),int(r)]

def getColorDistance(color1, color2):
    sq_error = 0
    for i in range(0, 3):
        sq_error += (color1[i] - color2[i]) ** 2
    return sq_error

def checkColor(pixels, img, threshold = 1000):
    sq_error = 0;
    for pixel in pixels:
        color = getColor(pixel["x"], pixel["y"], img)
        if (color is None):
            return False, sq_error
        refcolor = hex_to_bgr(pixel["color"])
        sq_error += getColorDistance(color, refcolor)
    if (sq_error / len(pixels) > threshold):
        return False, sq_error
    return True, sq_error

exp_region = [
    {"x": 689, "y": 209},
    {"x": 1222, "y": 984}
]

#extract pixels that has a certain color 
def extract(img, color, threshold = 1000, is_play_area = True):
    diff = img[:, :, :3].astype(np.int32) - np.array(color, dtype=np.int32)
    sq_error = np.sum(diff * diff, axis=2)
    err = sq_error <= threshold
    if (is_play_area):
        top = exp_region[0]["y"] - play_area["top"]
        bottom = exp_region[1]["y"] - play_area["top"]
        err[:top,:] = False
        err[bottom:,:] = False
    return err

#extract pixels that has a certain group of color 
def extractGroup(img, color_group, threshold = 1000, is_play_area = True):
    img32 = img[:, :, :3].astype(np.int32)
    sq_error = np.full(img.shape[:2], 999999, dtype=np.int32)
    for color in color_group:
        diff_color = img32 - np.asarray(color, dtype=np.int32)
        dist = np.sum(diff_color * diff_color, axis=2)
        np.minimum(sq_error, dist, out=sq_error)
        
    err = sq_error <= threshold
    if (is_play_area):
        top = exp_region[0]["y"] - play_area["top"]
        bottom = exp_region[1]["y"] - play_area["top"]
        err[:top,:] = False
        err[bottom:,:] = False
    return err

region_split_x = [689,880,1030,1222]
region_split_y = [209,390,523,900]

def findColorCluster(img, color, min_area = 10, threshold = 1000, kernel_size = 15, label = "", verifier = None):
    err = extract(img, hex_to_bgr(color), threshold).astype(np.uint8)
    if (kernel_size > 1):
        kernel = cv2.getStructuringElement(
                cv2.MORPH_RECT,
                (kernel_size, kernel_size)
        )
        err = cv2.morphologyEx(err, cv2.MORPH_CLOSE, kernel)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(err, connectivity = 8)
    clusters = []
    objects = []
    new_err = np.zeros((*err.shape[:2], 3), dtype=np.uint8)
    new_err[err == True] = (255, 255, 255)
    for i in range(1, num_labels):  # Skip background (label 0)
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        if (area >= min_area and (verifier is None or (verifier(x,y,w,h,area) == True))):
            clusters.append([x,y,w,h])
            objects.append([x-10,y-10,x+w+10,y+h+10,hex_to_bgr(color), label + ": " + str(area)])

    return clusters, new_err, objects

def findColorClusterGroup(img, color_group, min_area = 10, threshold = 1000, kernel_size = 1, label = "", verifier = None):
    color_group = [hex_to_bgr(color) for color in color_group]
    err = extractGroup(img, color_group, threshold).astype(np.uint8)
    if (kernel_size > 1):
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (kernel_size, kernel_size)
        )
        err = cv2.morphologyEx(err, cv2.MORPH_CLOSE, kernel)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(err, connectivity = 8)
    clusters = []
    objects = []
    new_err = np.zeros((*err.shape[:2], 3), dtype=np.uint8)
    new_err[err == True] = (255, 255, 255)
    for i in range(1, num_labels):  # Skip background (label 0)
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        if (area >= min_area and (verifier is None or (verifier(x,y,w,h,area) == True))):
            clusters.append([x,y,w,h])
            objects.append([x-10,y-10,x+w+10,y+h+10,color_group[0], label + ": " + str(area)])

    return clusters, new_err, objects

def findMaxColorRegion(img, color, min_area = 50, threshold = 1000):
    err = extract(img, hex_to_bgr(color), threshold)

    counts = {}
    rects = {}
    objects = []
    for row, name_y in enumerate(("w", "", "s")):
        for col, name_x in enumerate(("a", "", "d")):
            top = region_split_y[row] - play_area["top"]
            bot = region_split_y[row+1] - play_area["top"]
            left = region_split_x[col]- play_area["left"]
            right =  region_split_x[col+1] - play_area["left"]
            region = err[
                top:bot,
                left:right
            ]
            objects.append([left,top,right,bot,(255,0,0), ""])
            counts[name_y + name_x] = cv2.countNonZero(region)
            rects[name_y + name_x] = [left,top,right,bot]

    best_direction = max(counts, key=counts.get)
    if counts[best_direction] < min_area:
        return "", err, objects
    x1,y1,x2,y2 = rects[best_direction]
    objects.append([x1,y1,x2,y2,(0,255,0),""])
    return best_direction, err, objects

def addObjects(img, objects):
    for x1,y1,x2,y2,color,label in objects:
        cv2.rectangle(img, (x1,y1),(x2,y2),color,2)
        cv2.putText(
            img,
            label,
            (x1, y2 + 20),           # Text baseline below rectangle
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,                        # Font scale
            color,
            2,                          # Thickness
            cv2.LINE_AA
        )
    return img

MAX_CONFIDENCE = 0
FIRST_APPEARANCE = 1
def searchSprite(img, sprite, label, type = MAX_CONFIDENCE):
    h, w = sprite.shape[:2]
    
    screen = img[:,:,:3]

    mask = extract(sprite, hex_to_bgr(0), 10, False)
    mask = (mask == False).astype(np.uint8)*255
    result = cv2.matchTemplate(screen, sprite, cv2.TM_CCOEFF_NORMED, mask)
    top = exp_region[0]["y"] - play_area["top"]
    bottom = exp_region[1]["y"] - play_area["top"]
    x, y, confidence = 0, 0, 0
    if (type == MAX_CONFIDENCE):
        _, confidence, _, max_loc = cv2.minMaxLoc(result[top:bottom])
        x,y = max_loc
        y += top
        if (confidence < 0.7):
                return [], None
    else:
        matches = np.argwhere(result[top:bottom] >= 0.7)
        if len(matches):
            y, x = matches[0]
            y += top
            confidence = result[y][x]
        else:
            return [], None
    #print(x, y)
    #print("Confidence:" + str(confidence))
    objects = []
    objects.append([x-10,y-10,x+w+10,y+h+10,(0,255,255),label])
    center = (x + w/2, y + h/2)
    return objects, center

def getText(img, x1, y1, x2, y2):
    init_ocr()
    result = reader.readtext(img[y1:y2,x1:x2])
    full_text = ""
    full_confidence = 0
    if (len(result) == 0):
        return "", -1
    for _, text, confidence in result:
        if (len(full_text)):
            full_text += " "
        full_text += text
        full_confidence += confidence
    full_confidence /= len(result)
    return full_text, full_confidence

def bloon_verifier(x,y,w,h,area):
    return (area > 50)

if __name__ == "__main__":
    #Main function primarily for testing purposes
    mini_boss_screen = [
        {"x": 1012, "y": 92, "color": 0xffffff},
        {"x": 1020, "y": 65, "color": 0x0},
        {"x": 1021, "y": 93, "color": 0x0}
    ]
    bloon_color = [
    0xFE2D38, #RED
    0x16AAFF  #BLUE
    ]

    player_hp_sprite = cv2.imread('sprites/player_hp_scaled.png')
    sct = mss.MSS()
    def on_press(key):
        if hasattr(key, 'char') and key.char == 'w':
            x, y = mouse.Controller().position
            img = grabScreenshot(sct)
            print("{\"x\": %d, \"y\": %d, \"color\": %s}" % (x, y, hex(bgr_to_hex(*getColor(x, y, img)))))
            cwolor = getColor(x, y, img)

        elif hasattr(key, 'char') and key.char == 'q':
            return False

    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()
    gold_color = [
        0xffcaa1,
        0xfff74b,
        0xffe70c,
        0xffdf04
    ]
    bloon_color = [
        0xFE2D38, #RED
        0x16AAFF  #BLUE
    ]
    while True:
        img = grabScreenshot(sct)
        #clusters, err, objects =  findColorCluster(img, 0xFF4AFF, 30, 1000, 99, label = "boss_bullets")
        #clusters, err, objects = findColorCluster(img, 0x78C9A6, 250, 1000, 5, "encounters")
        clusters, err, objects = findColorClusterGroup(img, gold_color, 60, 150, 7, "gold")
        #clusters, err, objects = findColorCluster(img, 0x70EFFD, 30, 1000, 10, "blop")
        #clusters, err, objects = findColorClusterGroup(img, bloon_color, 50, 500, 3, label = "bloons", verifier=bloon_verifier)
                
        # objects, _= searchSprite(img, player_hp_sprite, "health", FIRST_APPEARANCE)
        # objects.extend(bananas)
        # img = addObjects(img, objects)
        # err = err.astype(np.uint8)*255
        err = addObjects(err, objects)
        cv2.imshow("img", err)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

    keyboard_listener.join()

    sct.close()
