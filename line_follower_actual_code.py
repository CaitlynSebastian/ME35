from machine import Pin, PWM, I2C, SoftI2C
from neopixel import NeoPixel
import time, json, math
import veml6040
import espnow
import network

# ---------- EFFECTS SETTINGS -----------
NEOPIXEL_PIN = 15    # change to the pin your strip's data wire is on
NUM_PIXELS = 2       # change to your pixel count
LIGHT_COLORS = {     # label -> (R, G, B); keep values low to limit current
    "floor": (4, 4, 4),
    "black": (40, 40, 40),
    "blue": (0, 0, 60),
    "green": (0, 60, 0),
    "red": (60, 0, 0),
}
OTHER_COLOR = (40, 0, 40)   # any label not listed above

ENABLED_EFFECTS = ("blue", "red", "green")   # add "green" here to turn the green flash back on
CONFIRM_ACTION = 4    # reads in a row a color must hold before its effect starts
FLASH_MS = 250        # length of each flash phase
FLASH_TOTAL_MS = 2500 # how long a flash effect lasts
_shown = [None]

# ---------- DRIVING SETTINGS -----------
DRIVE_SPEED = 0.25     # forward speed while on the line (0-1)
SWEEP_SPEED = 0.4     # duty of the driven wheel while pivoting
SPIN_SPEED = 0.3   # speed of each wheel while spinning in place

SAMPLE_MS = 80            # same as the sensor integration time
FINE_SWEEPS = 0           # how many small left-right cycles before widening

# ms to turn 90 degrees, from test_turn; put your measurements here
PIVOT_MS_90 = {1: 1250, -1: 1250}   # pivot right, pivot left
SPIN_MS_90  = {1: 940, -1: 940}   # spin right, spin left

FINE_DEG = 15              # small sweep, each side of center
WIDE_DEG = (35, 65, 100)   # wide sweeps, each done both ways

# -- other settings --
K = 5
CONFIRM_LINE = 2       # reads in a row before floor <-> black/color is believed

# --------------- init espnow --------------
# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.WLAN.IF_STA)  # Or network.WLAN.IF_AP
sta.active(True)
sta.disconnect()      # For ESP8266

e = espnow.ESPNow()
e.active(True)
peer = b'\x20\x50\x0d\x2a\x36\xf4'   # MAC address of peer's wifi interface
e.add_peer(peer)      # Must add_peer() before send()

# ------------------------------------------

# motor pins
left_fwd  = PWM(Pin(14), ht_rev = PWM(Pin(12), freq=20000, duty_u16=0)

# color sensor\, duty_u16=0)

# color sensor\, duty_u16=0)

# color sensor\, duty_u16=0)

# color sensor\, duty_u16=0)

# color sensor\, duty_u16=0)

# color sensor\, duty_u16=0)

# color sensor\, duty_u16=0)

# color sensor\, duty_u16=0)

# color sensor\, duty_u16=0)

# color sensor\, duty_u16=0)

# color sensor\, duty_u16=0)

# color sensor\, duty_u16=0)

# color sensor\, duty_u16=0)

# color sensor\, duty_u16=0)

# color sensor
INTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS nINTEGRATION = veml6040.IT_80MS   # IT_80MS matches training; 40 ms is faster
i2c_sensor = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)
print("center bus:", i2c_sensor.scan())  # both [16]
sensor = veml6040.VEML6040(i2c_sensor)
sensor.set_integration_time(INTEGRATION)   # your init never applied it; must match train_knn.py
time.sleep_ms(200)

pixels = NeoPixel(Pin(NEOPIXEL_PIN), NUM_PIXELS)

def set_light(color):
    if color == _shown[0]:
        return                  # skip redundant writes
    _shown[0] = color
    pixels[0] = color
    pixels.write()

# ----------- DRIVING FUNCS -----------
def _set(fwd, rev, speed):
    speed = max(-1.0, min(1.0, speed))
    if speed >= 0:
        rev.duty_u16(0)                      # turn the other side off first
        fwd.duty_u16(int(speed * 65535))
    else:
        fwd.duty_u16(0)
        rev.duty_u16(int(-speed * 65535))

def drive_signed(left, right):
    _set(left_fwd, left_rev, left)
    _set(right_fwd, right_rev, right)

def drive(left, right):                      # forward only, used by pivot() and following
    drive_signed(max(0.0, left), max(0.0, right))

def stop():
    for p in (left_fwd, left_rev, right_fwd, right_rev):
        p.duty_u16(0)

def pivot(direction):
    # +1 = turn right (left wheel drives), -1 = turn left (right wheel drives)
    if direction > 0:
        drive(SWEEP_SPEED, 0)
    else:
        drive(0, SWEEP_SPEED)

def spin(direction):
    # +1 = spin right (left forward, right back), -1 = spin left
    s = SPIN_SPEED if direction > 0 else -SPIN_SPEED
    drive_signed(s, -s)


# sensor init
_last = {}
_bad = [0]

def read_safe(sensor):
    """Retry a failed read; reuse the last good one for a brief glitch."""
    for _ in range(4):
        try:
            _last[id(sensor)], _bad[0] = sensor.read_rgbw(), 0
            return _last[id(sensor)]
        except OSError:
            time.sleep_ms(3)
    _bad[0] += 1
    if _bad[0] > 25 or id(sensor) not in _last:
        raise OSError("sensor stopped answering: check cable and battery")
    return _last[id(sensor)]


with open("knn.json") as f:
    KNN = json.load(f)          # [[r/w, g/w, b/w], label] ...

def classify(rgbw):
    r, g, b, w = rgbw
    if w <= 0:
        return "black"          # no light at all: treat as dark
    x, y, z = r / w, g / w, b / w
    best = []                   # K nearest as (dist, label)
    for (px, py, pz), lab in KNN:
        d = (px - x) ** 2 + (py - y) ** 2 + (pz - z) ** 2
        if len(best) < K or d < best[-1][0]:
            best.append((d, lab))
            best.sort()
            if len(best) > K:
                best.pop()
    votes = {}
    for _, lab in best:
        votes[lab] = votes.get(lab, 0) + 1
    return max(votes, key=votes.get)

def flash(label):
    """Stop and flash the tape's color, then restore the sensor light."""
    stop()
    color = LIGHT_COLORS.get(label, OTHER_COLOR)
    e.send(peer, label)

    t0 = time.ticks_ms()
    on = True
    while time.ticks_diff(time.ticks_ms(), t0) < FLASH_TOTAL_MS:
        set_light(color if on else (0, 0, 0))
        on = not on
        time.sleep_ms(FLASH_MS)
    set_light(color)            # was set_light(ILLUM)
    time.sleep_ms(150)          # let the sensor see the steady light again

def leg_time(delta, is_spin):
    d = 1 if delta > 0 else -1
    ms90 = (SPIN_MS_90 if is_spin else PIVOT_MS_90)[d]
    return abs(delta) / 90 * ms90

# ---- build the sweep schedule once ----
def build_legs():
    steps = []
    for _ in range(FINE_SWEEPS):
        steps += [(FINE_DEG, False), (-FINE_DEG, False), (0, False)]
    for a in WIDE_DEG:
        steps += [(a, True), (-a, True), (0, True)]
    legs, t, pos = [], 0.0, 0
    for tgt, is_spin in steps:
        delta = tgt - pos
        t += leg_time(delta, is_spin)
        legs.append((t, 1 if delta > 0 else -1, is_spin))
        pos = tgt
    return legs

LEGS = build_legs()

def run():
    set_light(LIGHT_COLORS["floor"])
    time.sleep_ms(300)
    state = "floor"
    cand, n = None, 0
    lost_at = time.ticks_ms()
    last_read = time.ticks_add(lost_at, -SAMPLE_MS)
    first_dir = cur_dir = 1
    was_on = False
    last_flashed = None
    try:
        while True:
            now = time.ticks_ms()

            # sense: once per new sensor measurement
            if time.ticks_diff(now, last_read) >= SAMPLE_MS:
                last_read = now
                lab = classify(read_safe(sensor))
                if lab == cand:
                    n += 1
                else:
                    cand, n = lab, 1
                need = CONFIRM_ACTION if lab in ENABLED_EFFECTS else (1 if lab != "floor" else CONFIRM_LINE)
                if n >= need:
                    state = lab
                set_light(LIGHT_COLORS.get(state, OTHER_COLOR))

                on_line = state != "floor"
                if on_line and not was_on:
                    first_dir = -cur_dir     # entered turning cur_dir, expect to exit the other way
                elif was_on and not on_line:
                    lost_at = now
                was_on = on_line

                if state in ENABLED_EFFECTS:
                    if state != last_flashed:
                        flash(state)
                        last_flashed = state
                        last_read = time.ticks_ms()
                        continue
                elif state in ("floor", "black"):
                    last_flashed = None

            # act: every loop, so sweep legs are timed to about 10 ms
            if state != "floor":
                drive(DRIVE_SPEED, DRIVE_SPEED)
            else:
                elapsed = time.ticks_diff(time.ticks_ms(), lost_at)
                for end, d, is_spin in LEGS:
                    if elapsed < end:
                        cur_dir = d * first_dir
                        if is_spin:
                            spin(cur_dir)
                        else:
                            pivot(cur_dir)
                        break
                else:
                    print("lost the line")
                    break
            time.sleep_ms(10)
    finally:
        stop()
        set_light((0, 0, 0))

btn = Pin(34, Pin.IN, Pin.PULL_UP)
DEBOUNCE_MS = 200
last_press = 0
pressed_flag = False

def button_handler(pin):
    global last_press
    global pressed_flag
    now = time.ticks_ms()
    if time.ticks_diff(now, last_press) > DEBOUNCE_MS:
        if (pin.value() == 0):
            last_press = now
            pressed_flag = True

btn.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)

while True:
    if pressed_flag:
        print("running")
        run()
        pressed_flag = False