# ICON [[(6.59, 7.4), (9.39, 4.6), (1.99, -2.8), (1.99, -12.0), (-2.01, -12.0), (-2.01, -1.2), (6.59, 7.4)], [(-0.01, 18.0), (-2.77, 17.82), (-5.22, 17.33), (-6.81, 16.84), (-9.0, 15.88), (-10.82, 14.83), (-12.37, 13.73), (-13.38, 12.88), (-14.8, 11.47), (-16.53, 9.28), (-17.71, 7.33), (-18.44, 5.84), (-18.93, 4.56), (-19.44, 2.82), (-19.69, 1.62), (-19.93, -0.24), (-19.98, -3.03), (-19.82, -4.82), (-19.36, -7.14), (-18.78, -8.99), (-18.18, -10.41), (-16.87, -12.77), (-15.61, -14.52), (-14.53, -15.77), (-13.03, -17.19), (-11.75, -18.19), (-9.49, -19.6), (-7.63, -20.48), (-5.31, -21.29), (-2.8, -21.81), (-1.17, -21.97), (0.56, -22.0), (2.17, -21.89), (4.17, -21.57), (5.78, -21.15), (6.98, -20.74), (8.54, -20.07), (10.61, -18.95), (12.5, -17.62), (14.56, -15.73), (15.71, -14.38), (16.82, -12.81), (18.11, -10.45), (18.75, -8.94), (19.3, -7.26), (19.84, -4.56), (19.98, -2.76), (19.98, -1.18), (19.8, 0.82), (19.39, 2.89), (18.67, 5.12), (17.97, 6.73), (16.56, 9.2), (15.45, 10.7), (13.58, 12.69), (11.88, 14.09), (10.45, 15.06), (9.16, 15.79), (6.7, 16.87), (5.01, 17.38), (2.25, 17.88), (0.04, 18.0)], [(-0.01, -2.0)], [(-0.01, 14.0), (1.87, 13.9), (3.1, 13.72), (4.92, 13.27), (6.57, 12.65), (7.85, 12.0), (9.95, 10.56), (11.26, 9.38), (12.07, 8.51), (13.65, 6.4), (14.66, 4.51), (15.18, 3.17), (15.75, 0.9), (15.93, -0.48), (15.99, -2.41), (15.75, -4.87), (15.46, -6.25), (14.87, -8.01), (14.31, -9.23), (13.28, -10.95), (12.42, -12.08), (11.05, -13.55), (9.91, -14.56), (8.05, -15.86), (6.45, -16.69), (4.54, -17.39), (3.36, -17.68), (1.71, -17.92), (0.44, -18.0), (-1.44, -17.94), (-2.97, -17.75), (-5.29, -17.16), (-6.71, -16.59), (-8.07, -15.88), (-10.05, -14.49), (-11.32, -13.34), (-12.48, -12.07), (-13.2, -11.12), (-14.1, -9.69), (-14.72, -8.44), (-15.33, -6.79), (-15.77, -4.91), (-15.98, -3.05), (-16.0, -1.85), (-15.9, -0.04), (-15.44, 2.39), (-14.95, 3.89), (-14.24, 5.45), (-13.24, 7.08), (-12.22, 8.41), (-11.39, 9.31), (-10.07, 10.49), (-8.57, 11.58), (-7.27, 12.32), (-5.83, 12.96), (-4.11, 13.51), (-1.72, 13.91), (-0.06, 14.0)]]
# NAME Analog Clock PaulskPt
# DESC Full resolution vector clock!
import presto
import time
import gc
import machine
import ntptime

from presto import Presto, Buzzer

from picovector import PicoVector, Polygon, Transform, ANTIALIAS_X16

# ----- Added by @PaulskPt -------------
tz_offset = 0
dt = None

# NTP update interval in minutes.
NTP_UPDATE_INTERVAL = 15 * 60 * 1000
print(f"ntp datetime refresh interval: {int(NTP_UPDATE_INTERVAL/60_000)} minutes")

try:
    from secrets import TIMEZONE_OFFSET 
    tz_offset = int(TIMEZONE_OFFSET)
except ImportError as exc:
    pass

wdDict = {0: "Mon",
          1: "Tue",
          2: "Wed",
          3: "Thu",
          4: "Fri",
          5: "Sat",
          6: "Sun"}

# --------------------------------------

# Setup for the Presto display
presto = Presto(full_res=True, ambient_light=False)
presto.auto_ambient_leds(False)
display = presto.display
WIDTH, HEIGHT = display.get_bounds()
MIDDLE = (int(WIDTH / 2), int(HEIGHT / 2))
HORI_MIDDLE = int(WIDTH / 2)
VERT_MIDDLE = int(HEIGHT / 2)

BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(200, 200, 200)
GRAY = display.create_pen(30, 30, 30)

# Touch tracking
touch_start_x = 0
touch_start_time = None
tap = False
NW = False # touch area 1
NE = False # touch area 2
SW = False # touch area 3
SE = False # touch area 4

# Ambient LEDs colour definitions:

ambLedsDict = {0: (255,   0,   0),  # Red
               1: (  0, 255,   0),  # Green
               2: (  0,   0, 255),  # Blue
               3: (255, 255, 255)}  # White

amb_leds_colour_idx = -1 
amb_leds_colour_idx_max = 3  # 0 ~ 3 = 4 colours

use_buzzer = False

# Setup the buzzer. The Presto piezo is on pin 43.
buzzer = Buzzer(43)

# How long the completion alert should be played (seconds)
alert_duration = 2
alert_start_time = 0

do_startwait = False

t_start = time.ticks_ms()
start_asp_t = t_start

rtc = machine.RTC()
# print(f"type(rtc) = {type(rtc)}")

vector = PicoVector(display)
t = Transform()
vector.set_transform(t)
vector.set_antialiasing(ANTIALIAS_X16)

last_second = None

use_inverse = False

aspect_minimum = 0
aspect_maximum = None
aspect_idx = 0  # Set for standard clock appearance

def show_message(text):
    display.set_pen(BLACK)
    display.clear()
    display.set_pen(WHITE)
    display.text(f"{text}", 5, 10, WIDTH, 2)
    presto.update()

show_message("Connecting...")

try:
    wifi = presto.connect()
except ValueError as e:
    while True:
        show_message(e)
except ImportError as e:
    while True:
        show_message(e)

    if not update_fm_ntp():
        while True:
            time.sleep(5)
            
leds_on = False

def touched(self, touch):
        x, y, w, h = self.bounds()
        return touch.x > x and touch.x < x + w and touch.y > y and touch.y < y + h
   
def update_fm_ntp():
    t1 = "Unable to get time from NTP server.\n\nCheck your network and try again."
    TAG = "update_fm_ntp(): "
    ret = False
    if presto.wifi.isconnected():
        print(f"connected to \"{presto.wifi._secrets()[0]}\"")
        print(f"IP address = {presto.wifi.ipv4()}")
        
        # Set the correct time using the NTP service.
        try:
            ntptime.settime()
            ret = True
            print(TAG + "rtc updated from NTP timestamp")
        except OSError:
            print(t1)
    
    else:
        print(t1)
    return ret


def pr_loc_time(tm):
    yy = tm[0]
    mo = tm[1]
    dd = tm[2]
    hh = tm[3]
    mm = tm[4]
    ss = tm[5]
    dt = "{:4d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(yy, mo, dd, hh, mm, ss)
    print(f"Starting with local datetime: {dt}")
    
def start_buzzer():
    global alert_start_time
    alert_start_time = time.time()
    buzzer.set_tone(150)

def stop_buzzer():
    global alert_start_time
    buzzer.set_tone(-1)
    alert_start_time = 0
    
# Parameter asp has to be equal to one of the values of aspect_lst2
def chg_aspect(idx):
    
    global use_inverse, RED, BLACK, DARKGREY, GREY, WHITE, BLUE, aspect_maximum, aspect_minimum
    
    aspect_lst =  ["Normal", "Blue", "Reversed", "Grey", "Dark"]
    aspect_maximum = len(aspect_lst)-1
    
    if idx < 0 or idx > len(aspect_lst)-1:
        print(f"Param idx: {idx} not in aspect_lst2. Exiting function")
        return

    #----- FLAG FOR INVERSE COLORS CLOCK ----------+
    if idx == 1:                                 # |
        use_inverse = True                       # |
    else:                                        # |
        use_inverse = False                      # |
    #----------------------------------------------+

    # print(f"Clock aspect index: {idx}, ")
    print(f"Changing clock aspect to \"{aspect_lst[idx]}\"")

    if idx == 0:
        # Redefine colours for a normal (standard) clock
        RED      = display.create_pen(200,   0,   0)
        BLACK    = display.create_pen(  0,   0,   0) # This make the middle more dark.
        DARKGREY = display.create_pen(100, 100, 100)
        GREY     = display.create_pen(200, 200, 200)
        WHITE    = display.create_pen(255, 255, 255)
        return
    
    if idx == 1:
        # Redefine colours for a Blue clock
        RED   = display.create_pen(200,   0,   0)
        BLACK = display.create_pen(135, 159, 169) #  This controls the (middle big circle)
        GREY  = display.create_pen( 10,  40,  50)
        WHITE = display.create_pen( 14,  60,  76)
        BLUE  = display.create_pen(100,   0, 255)
        return

    if idx == 2:
        # Redefine colours for a Reversed clock
        RED   = display.create_pen(200,   0,   0)
        BLACK = display.create_pen(135, 159, 169)
        GREY  = display.create_pen( 10,  40,  50)
        WHITE = display.create_pen( 14,  60,  76)
        return

    if idx == 3:
        # Redefine colours for a Dark clock
        RED   = display.create_pen(200,  0,  0)
        BLACK = display.create_pen( 65, 80, 84)
        GREY  = display.create_pen(  5, 20, 25)
        WHITE = display.create_pen( 14, 60, 76)
        return

    if idx == 4: # aspect_minimum
        # Redefine colours for a Dark clock
        RED   = display.create_pen(200,  0,   0)
        BLACK = display.create_pen( 65, 80,  84)
        GREY  = display.create_pen(  5, 20,  25)
        WHITE = display.create_pen(100,  0, 255)

dt_shown = False

def pr_dt():
    global dt
    TAG = "pr_dt(): "
    if isinstance(dt, tuple) and len(dt) == 8:
        print("datetime received from NTP server: ", end = '\n')
        # print(f"weekday = {dt[6]}", end = '')
        if dt[6] in wdDict.keys():
            wday = wdDict[dt[6]]
        else:
            wday = str(dt[6])
        if int(TIMEZONE_OFFSET) >= 0: # in case timezone(s) UTC or EAST of UTC
            n = TIMEZONE_OFFSET.find('+')
            if n == -1: # not found
                tz = "+" + TIMEZONE_OFFSET
            else:
                tz = TIMEZONE_OFFSET
        else: # in case timezone(s) WEST of UTC
            n = TIMEZONE_OFFSET.find('-')
            if n == -1: # not found
                tz = "-" + TIMEZONE_OFFSET
            else:
                tz = TIMEZONE_OFFSET

    
        print("{:4d}-{:02d}-{:02d} T {:02d}:{:02d}:{:02d}, {:s}, yearday: {:3d}, timezone: UTC{:s}".format( \
            dt[0], dt[1], dt[2], dt[3], dt[4], dt[5],  wday, dt[7], tz))
        #   year, month, day, hours, minutes, seconds, wday, yearday))
    else:
        print(TAG + f"expected global variable dt being a tuple,\n\thowever received a type \"{type(dt)}\". Check your code!")

def update_fm_ntp():
    global dt
    ret = False
    t1 = "Unable to get time from NTP server.\n\nCheck your network and try again."
    
    if presto.wifi.isconnected():
        # print(f"connected to \"{presto.wifi._secrets()[0]}\"")
        # print(f"IP address = {presto.wifi.ipv4()}")
        
        # grab the current time from the ntp server and update the Pico RTC
        try:
            sec = ntptime.time()
            timezone_sec = tz_offset * 3600
            sec = int(sec + timezone_sec)
            dt = time.localtime(sec)
            (year, month, day, hours, minutes, seconds, weekday, yearday) = time.localtime(sec)
            # set the rtc
            rtc.datetime((year, month, day, 0, hours, minutes, seconds, 0))
            ret = True
            print("rtc updated from NTP timestamp")
            # ntptime.settime()  # original code
    
        except OSError:
            print(t1)
    else:
        print(t1)
    
    return ret

def ck_corners():
    global touch, NW, NE, SW, SE
    x = touch.x
    y = touch.y
    
    # check upper left (corner 1)
    if x >= 0 and x <= HORI_MIDDLE-10 and y >= 0 and y <= VERT_MIDDLE-10:
        NW = True
    
    # check upper right (corner 2)
    elif x >= HORI_MIDDLE+10 and x <= WIDTH-10 and y >= 0 and y <= VERT_MIDDLE-10:
        NE = True
    
    # check lower left (corner 3)
    elif x >= 0 and x <= HORI_MIDDLE-10 and y >= VERT_MIDDLE+10 and y <= HEIGHT-10:
        SW = True
    
    # check lower right (corner 4)
    elif x >= HORI_MIDDLE+10 and x <= HEIGHT-10 and y >= VERT_MIDDLE+10 and y <= HEIGHT-10:
        SE = True

hub = Polygon()
hub.circle(int(WIDTH / 2), int(HEIGHT / 2), 0) # was: ,5) # this change maked the outer small "ring" more small

face = Polygon()
# NOTE: the 3rd param of next line determines the length at N, E, S, W (cardinal? points). The higher the value, the shorter the drawn part is.
#       the 2nd param              determines the length at S (6 o'clock)
#       the 1st param              appears to move the inner circle to the left
#corr = -2
face.circle(int(WIDTH / 2), int(HEIGHT / 2), int(HEIGHT / 2))
#face.circle(int(WIDTH / 2)+corr, int(HEIGHT / 2)+corr, int(HEIGHT / 2)+corr) # TRIED TO GET RID OF SMALL OUTER WHITE CIRCLE

tick_mark = Polygon()
tick_mark.rectangle(int(WIDTH / 2) - 3, 10, 6, int(HEIGHT / 48))

hour_mark = Polygon()
hour_mark.rectangle(int(WIDTH / 2) - 5, 10, 10, int(HEIGHT / 10))

minute_hand_length = int(HEIGHT / 2) - int(HEIGHT / 24)
minute_hand = Polygon()
minute_hand.path((-5, -minute_hand_length), (-10, int(HEIGHT / 16)), (10, int(HEIGHT / 16)), (5, -minute_hand_length))

hour_hand_length = int(HEIGHT / 2) - int(HEIGHT / 8)
hour_hand = Polygon()
hour_hand.path((-5, -hour_hand_length), (-10, int(HEIGHT / 16)), (10, int(HEIGHT / 16)), (5, -hour_hand_length))

second_hand_length = int(HEIGHT / 2) - int(HEIGHT / 8)
second_hand = Polygon()
second_hand.path((-2, -second_hand_length), (-2, int(HEIGHT / 8)), (2, int(HEIGHT / 8)), (2, -second_hand_length))

# Sync datetime from ntp server
if not update_fm_ntp():
    pass
else:
    pr_dt()
#------------- WAIT TO REACH 0 SECONDS --------------------
if do_startwait:
    # Try to sync Start_asp_t with time.localtime() seconds
    print("Waiting for the localtime to reach 0 seconds ", end='')
    t_ticks = time.localtime()[5] # get seconds
    my_ticks_old = 0
    while t_ticks % 60 != 0:
        t_ticks = time.localtime()[5]
        my_ticks = int(time.ticks_ms() / 1_000)
        if my_ticks != my_ticks_old:
            my_ticks_old = my_ticks
            print('. ', end='')
    print("\nDone! Starting Clock.")
#----------------------------------------------------------

tm = time.localtime()
start_asp_t = time.time() # epoch timeserial

hh = tm[3]

pr_loc_time(tm)

last_second = None

# print(f"value of hh = {hh}.")
if (hh >= 22 and hh <= 24) or (hh >= 0 and hh < 7): # during night hours show a more dimmed clock face
    print("Changing to nighttime clock.")
    aspect_minimum = 1
    use_inverse = True
else:
    print("Changing to daytime clock.")
    aspect_minimum = 0
    use_inverse = False

aspect_idx = aspect_minimum
chg_aspect(aspect_idx)
if use_inverse:
    print("Inverse active")
#else:
#    print("Inverse not active")
#display.set_pen(WHITE if use_inverse else BLACK)  # was: BLACK
display.set_pen(WHITE)
display.clear()
#display.set_pen(BLACK if use_inverse else WHITE)  # was WHITE
display.set_pen(BLACK)
vector.draw(face)

print("\nVector Clock Full for Pimoroni Presto\n")

start_t = time.ticks_ms()
curr_t = 0
elapsed_t = 0

# Take a local reference to touch for a tiny performance boost
touch = presto.touch

# ToDo: using Buzzer

while True:
    # time.sleep(60 * NTP_UPDATE_INTERVAL)
    curr_t = time.ticks_ms()
    elapsed_t = curr_t - start_t
    if elapsed_t >= NTP_UPDATE_INTERVAL:
        start_t = curr_t
        if not update_fm_ntp():
            pass
        else:
            pr_dt()
    
    tm = time.localtime()
    year, month, day, hour, minute, second, _, _ = tm
    
    touch.poll()

    if touch.state: #and touch_start_time is None:
        ck_corners()
        touch.state = False
        
        if NW:
            aspect_idx -= 1
            if aspect_idx < aspect_minimum:
                aspect_idx = aspect_maximum
            chg_aspect(aspect_idx)
            NW = False
        elif NE:
            aspect_idx += 1
            if aspect_idx > aspect_maximum:
                aspect_idx = aspect_minimum
            chg_aspect(aspect_idx)
            NE = False
        elif SW:
            amb_leds_colour_idx += 1
            if amb_leds_colour_idx > amb_leds_colour_idx_max:
                amb_leds_colour_idx = -1
                
                    
            leds_on = True
            SW = False
        elif SE:
            leds_on = False
            SE = False

    if leds_on:
        # Cycle the hue of the backlight LEDs to match the icon colours
        hue = 1.0 # - (move_angle % (2 * math.pi)) / (2 * math.pi)
        if amb_leds_colour_idx in ambLedsDict.keys():
            clr = ambLedsDict[amb_leds_colour_idx]
            for i in range(7):
                #presto.set_led_hsv(i, hue, 1.0, 0.5)
                presto.set_led_rgb(i, clr[0], clr[1], clr[2])
    else:
        hue = 0.0 # - (move_angle % (2 * math.pi)) / (2 * math.pi)
        for i in range(7):
            #presto.set_led_hsv(i, hue, 0.0, 0.0)
            presto.set_led_rgb(i, 0, 0, 0)
    presto.update()
    time.sleep(0.05) # prevent touch bounce (50 mSecs)
        
    
    if last_second == second:
        time.sleep_ms(10)
        continue

    last_second = second
    
    t.reset()

    display.set_pen(BLACK if use_inverse else WHITE)  # was: WHITE
    
    display.circle(int(WIDTH / 2), int(HEIGHT / 2), int(HEIGHT / 2) - 4)

    display.set_pen(GREY)

    for a in range(60):
        t.rotate(360 / 60.0 * a, MIDDLE)
        t.translate(0, 2)
        vector.draw(tick_mark)
        t.reset()

    for a in range(12):
        t.rotate(360 / 12.0 * a, MIDDLE)
        t.translate(0, 2)
        vector.draw(hour_mark)
        t.reset()

    display.set_pen(GREY)

    x, y = MIDDLE
    y += 5

    angle_minute = minute * 6
    angle_minute += second / 10.0
    t.rotate(angle_minute, MIDDLE)
    t.translate(x, y)
    vector.draw(minute_hand)
    t.reset()

    angle_hour = (hour % 12) * 30
    angle_hour += minute / 2
    t.rotate(angle_hour, MIDDLE)
    t.translate(x, y)
    vector.draw(hour_hand)
    t.reset()

    angle_second = second * 6
    t.rotate(angle_second, MIDDLE)
    t.translate(x, y)
    vector.draw(second_hand)
    t.reset()

    display.set_pen(WHITE if use_inverse else BLACK) # was: BLACK

    for a in range(60):
        t.rotate(360 / 60.0 * a, MIDDLE)
        vector.draw(tick_mark)
        t.reset()

    for a in range(12):
        t.rotate(360 / 12.0 * a, MIDDLE)
        vector.draw(hour_mark)
        t.reset()

    x, y = MIDDLE

    t.rotate(angle_minute, MIDDLE)
    t.translate(x, y)
    vector.draw(minute_hand)
    t.reset()

    t.rotate(angle_hour, MIDDLE)
    t.translate(x, y)
    vector.draw(hour_hand)
    t.reset()

    display.set_pen(RED)
    t.rotate(angle_second, MIDDLE)
    t.translate(x, y)
    vector.draw(second_hand)

    t.reset()
    vector.draw(hub)

    presto.update()
    gc.collect()

    t_end = time.ticks_ms()
    show_took = False
    
    if show_took:
        print(f"Took {t_end - t_start}ms")

