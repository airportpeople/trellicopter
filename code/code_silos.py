'''
Keyboard commands to adjust gridxy on silos script

(https://norns.community/authors/justmat/silos)

Some Notes for Trellis Keyboard library:

# Send a keypress of ESCAPE
keyboard.send(Keycode.ESCAPE)

# Send CTRL-A (select all in most text editors)
keyboard.send(Keycode.CONTROL, Keycode.A)

# You can also control key press and release manually:
keyboard.press(Keycode.CONTROL, Keycode.A)
keyboard.release_all()

keyboard.press(Keycode.ESCAPE)
keyboard.release(Keycode.ESCAPE)
'''

import time
import usb_hid
import busio
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from board import SCL, SDA
from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis


# -------------------------
#          SETUP
# -------------------------
# create the i2c object for the trellis
i2c_bus = busio.I2C(SCL, SDA)

trellis = [
    [NeoTrellis(i2c_bus, False, addr=0x2E),
     NeoTrellis(i2c_bus, False, addr=0x30)],
    [NeoTrellis(i2c_bus, False, addr=0x31),
     NeoTrellis(i2c_bus, False, addr=0x2F)]
]

trellis = MultiTrellis(trellis)

# some color definitions
OFF = (0, 0, 0)

# Keyboard characters
KEY = {
    'a': Keycode.A,
    'b': Keycode.B,
    'c': Keycode.C,
    'd': Keycode.D,
    'e': Keycode.E,
    'f': Keycode.F,
    'g': Keycode.G,
    'h': Keycode.H,
    'i': Keycode.I,
    'j': Keycode.J,
    'k': Keycode.K,
    'l': Keycode.L,
    'm': Keycode.M,
    'n': Keycode.N,
    'o': Keycode.O,
    'p': Keycode.P,
    'q': Keycode.Q,
    'r': Keycode.R,
    's': Keycode.S,
    't': Keycode.T,
    'u': Keycode.U,
    'v': Keycode.V,
    'w': Keycode.W,
    'x': Keycode.X,
    'y': Keycode.Y,
    'z': Keycode.Z,
    '0': Keycode.ZERO,
    '1': Keycode.ONE,
    '2': Keycode.TWO,
    '3': Keycode.THREE,
    '4': Keycode.FOUR,
    '5': Keycode.FIVE,
    '6': Keycode.SIX,
    '7': Keycode.SEVEN,
    '8': Keycode.EIGHT,
    '9': Keycode.NINE,
    ' ': Keycode.SPACEBAR,
    '-': Keycode.ESCAPE,
    '@': Keycode.CONTROL,
    '#': Keycode.COMMAND,
    '>': Keycode.RIGHT_ARROW,
    '<': Keycode.LEFT_ARROW,
    '!': Keycode.RETURN
}

# params
SELECT = None
CONTROL = None
CONTROLLER = None
MACRO = None
MACRO_MULT = 1
MACRO_CLEAR = False
RANDOM = False
GRID_MODE = 1
N_GRID_MODES = 2

# for each controller (y = row) assign a control 
assignments = {
    'gridx1': None,
    'gridy1': None,
    'gridx2': None,
    'gridy2': None,
    'enc1': None,
    'enc2': None,
    'enc3': None
}

# number of controls for each track/fx assigned to each encoder (macro)
macros = {
    '1': [0, 0, 0, 0, 0],
    '2': [0, 0, 0, 0, 0],
    '3': [0, 0, 0, 0, 0]
}

# Tell the device to act like a keyboard.
keyboard = Keyboard(usb_hid.devices)


def type_keys(characters, press=False, wait=0.04):
    """
    Type the keys in `characters` in sequence, with `wait` seconds in between.

    Parameters
    ----------
    characters : str
        Characters to type
    press : bool, optional
        Send `keyboard.send` instead of `keyboard.press`, by default False
    wait : float
        Time between key presses/sends
    """
    for c in characters.lower():
        time.sleep(wait)
        if press:
            keyboard.press(KEY[c])
        else:
            keyboard.send(KEY[c])


def release_keys(characters, release_all=True, wait=0.04):
    '''
    Release either all keys (with `release_all`), or all keys in `characters` in sequence, with `wait` seconds in between each release.
    '''
    if release_all:
        keyboard.release_all()
    else:
        for c in characters.lower():
            time.sleep(wait)
            keyboard.release(KEY[c])


def get_grid(top_left=0, height=8, length=8, bottom_right=63, integer=True):
    """
    Get a grid of integer vales from `top-left` to `bottom_right` (inclusive), with the given dimensions.
    """
    num_vals = length * height
    
    if bottom_right is None:
        bottom_right = top_left + num_vals - 1
        
    delta = (bottom_right - top_left) / (num_vals - 1)
    
    if integer:
        values = [round(top_left + i * delta) for i in range(num_vals)]
    else:
        values = [top_left + i * delta for i in range(num_vals)]
        
    grid = [values[i:i + length] for i in range(0, num_vals, length)]

    return grid


def v_to_xy(v, grid):
    '''
    Given a value, `v`, inside of the `grid`, return the (x, y) coordinates.
    '''
    flat_grid = [i for row in grid for i in row]
    
    assert v in flat_grid

    loc = flat_grid.index(v)
    x = loc % 8
    y = loc // 8
    
    return x, y


def hsv_to_rgb(h, s, v):
    '''
    HSV to RGB. (`h` is in degrees).
    E.g., hsv_to_rgb(50, .53, .98) = (249.9, 227, 117)

    Parameters
    ----------
    h : int
        hue
    s : float
        saturation
    v : float
        brightness

    Returns
    -------
    (tuple) r, g, b
    '''
    h /= 360
    if s == 0.0:
        v *= 255
        return v, v, v

    i = int(h * 6.)
    f = (h * 6.) - i

    p = int(255 * (v * (1. - s)))
    q = int(255 * (v * (1. - s * f)))
    t = int(255 * (v * (1. - s * (1. - f))))
    v *= 255
    i %= 6

    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q


def v_to_rgb(v=30, hue='o'):
    '''
    Get RGB color for a `hue` given some brightness value, `v`, between 0 and 100. `hue` should be in {r, o, y, g, b, i, v, w}, where 'w' is white.
    '''
    colors = {
        'r': (0, 1),
        'o': (28, 1.0),
        'y': (58, 1.0),
        'g': (100, 1.0),
        'b': (225, 1.0),
        'i': (290, 1.0),
        'v': (324, 0.98),
        'w': (0, 0.0)
    }

    h, s = colors[hue]
    r, g, b = hsv_to_rgb(h, s, v / 100)

    return int(r), int(g), int(b)

# -------------------------
#       SILOS CONFIG
# -------------------------

# max control numbers for:
#             *track*     *fx*
MAX_CONTROLS = [13] * 4 + [11]

# color levels
colors = {
    'select_off': v_to_rgb(7),
    'select_on': v_to_rgb(40),
    'control_off': v_to_rgb(2),
    'control_on': v_to_rgb(20),
    'controller': v_to_rgb(20),
    'macro_off': v_to_rgb(0.5, 'b'),
    'macro_on': v_to_rgb(2, 'b'),
    'macro_mult': v_to_rgb(2, 'b'),
    'macro_clear': v_to_rgb(1, 'r'),
    'macro': v_to_rgb(1, 'b'),
    'assignment': v_to_rgb(2),
    'mode': v_to_rgb(1, 'w'),
    'mode_set': v_to_rgb(7, 'w'),
    'assign_off': v_to_rgb(2),
    'assign_on': v_to_rgb(40)
}


def assign_control():
    global CONTROLLER
    global CONTROL

    controller_ = CONTROLLER[:-3]
    id_ = str(CONTROLLER[-3])
    a = int(CONTROLLER[-1])
    track_fx_ = 'fx' if a == 4 else str(a + 1)
    control_number_ = int(CONTROL)

    # to be typed using `type_keys`
    print(f"** PROMPT **\n{controller_} {id_} {track_fx_} {control_number_}")


# -------------------------
#        GRID
# -------------------------
def grid(x=None, y=None):
    '''
    If `x` and `y` are None (default), then return the main page key and value grids, respectively. Otherwise, return the information encapsulated in the main page at (`x`, `y`). The latter returns the (key, value) tuple.
    '''
    g = [[f'track {i}' for i in range(1, 5)] + ['fx '] + 
            [f'control_number {i}' for i in range(1, 4)],
        ['gridx 1'] * 5 + [f'control_number {i}' for i in range(4, 7)],
        ['gridy 1'] * 5 + [f'control_number {i}' for i in range(7, 10)],
        ['gridx 2'] * 5 + [f'control_number {i}' for i in range(10, 13)],
        ['gridy 2'] * 5 + [f'control_number {i}' for i in range(13, 16)],
        ['enc 1'] * 5 + ['macro 1', 'macro_mult .5', 'random '],
        ['enc 2'] * 5 + ['macro 2', 'macro_mult -1', 'grid_mode '],
        ['enc 3'] * 5 + ['macro 3', 'macro_clear ', 'assign ']]
    
    if x is None or y is None:
        return g
    else:
        return g[y][x].split(' ')


def redraw_grid():
    global SELECT
    global CONTROL
    global CONTROLLER
    global MACRO
    global MACRO_MULT
    global MACRO_CLEAR
    global RANDOM
    global assignments
    global colors
    global macros
    
    for y in range(8):
        for x in range(8):
            k, v = grid(x, y)

            # top track/fx row
            if k in ['track', 'fx']:
                if x == SELECT:
                    trellis.color(x, y, colors['select_on'])
                else:
                    trellis.color(x, y, colors['select_off'])

            elif k == 'assign':
                trellis.color(x, y, colors['assign_off'])

            elif k == 'control_number':
                if CONTROL == v:
                    trellis.color(x, y, colors['control_on'])
                else:
                    trellis.color(x, y, colors['control_off'])
            
            elif (k == 'macro'):
                if MACRO == v:
                    trellis.color(x, y, colors['macro_on'])
                else:
                    trellis.color(x, y, colors['macro_off'])

            elif k == 'macro_mult':
                # selected macro_mult only one activated
                if MACRO_MULT / float(v) == 1:
                    trellis.color(x, y, colors['macro_mult'])
                # both macro_mult values activated
                elif MACRO_MULT == -0.5:
                    trellis.color(x, y, colors['macro_mult'])
                # this macro_mult is not activated
                else:
                    trellis.color(x, y, OFF)
            
            elif k in ['gridx', 'gridy', 'enc']:
                # controller selected for a given track/fx
                if CONTROLLER == k + v + f'-{x}':
                    trellis.color(x, y, colors['controller'])
                # controller has macro assigned to it
                elif k == 'enc' and macros[v][x] > 0:
                    trellis.color(x, y, colors['macro'])
                # controller already assigned to a track/fx
                elif x == assignments[k + v]:
                    trellis.color(x, y, colors['assignment'])
                # controller not assigned or selected
                else:
                    trellis.color(x, y, OFF)
            
            elif k == 'macro_clear':
                if MACRO_CLEAR:
                    trellis.color(x, y, colors['macro_clear'])
                else:
                    trellis.color(x, y, OFF)

            elif k == 'random':
                if RANDOM:
                    trellis.color(x, y, colors['mode_set'])
                else:
                    trellis.color(x, y, colors['mode'])

            elif k == 'grid_mode':
                trellis.color(x, y, colors['mode'])
   

def pad_grid(x, y):
    global SELECT
    global CONTROL
    global CONTROLLER
    global GRID_MODE
    global N_GRID_MODES
    global MACRO
    global MACRO_MULT
    global MACRO_CLEAR
    global RANDOM
    global assignments
    global colors
    global macros

    g = grid()
    k, v = g[y][x].split(' ')
        
    if k in ['track', 'fx']:
        SELECT = x
        print(f"select --> {x}")

    # controller pad section
    elif (x < 5) and (y > 0):
        # macro is already selected
        if MACRO is not None:
            trellis.color(x, y, OFF)
            print(f"controller error --> macro selected")

        # controller is already selected for a track/fx
        elif CONTROLLER == k + v + f'-{x}':
            CONTROLLER = None
            # it has an assignment
            if x == assignments[k + v]:
                trellis.color(x, y, colors['assignment'])
            # it doesn't have an assignment yet
            else:
                trellis.color(x, y, OFF)
            print(f"controller --> None")
        
        # controller not selected yet
        else:
            CONTROLLER = k + v + f'-{x}'
            trellis.color(x, y, colors['controller'])
            print(f"controller --> {k + v}-{x}")
    
    # control number section
    elif (x > 4) and (y < 5):
        if CONTROL == v:
            CONTROL = None
            trellis.color(x, y, colors['control_off'])
            print(f"control --> None")
        else:
            CONTROL = v
            trellis.color(x, y, colors['control_on'])
            print(f"control --> {v}")

    # macro section
    elif k == 'macro':
        # controller is already selected
        if CONTROLLER is not None:
            trellis.color(x, y, colors['macro_off'])
            print(f"macro error --> controller selected")

        # macro already selected
        elif MACRO == v:
            MACRO = None
            trellis.color(x, y, colors['macro_off'])
            print(f"macro --> None")

        # macro not selected yet
        elif v in '123':
            MACRO = v
            trellis.color(x, y, colors['macro_on'])
            print(f"macro --> {v}")

    # macro_mult section
    elif k == 'macro_mult':
        # selected macro_mult only one (already) activated
        if MACRO_MULT / float(v) == 1:
            MACRO_MULT /= float(v)
            trellis.color(x, y, OFF)

        # both macro_mult values (already) activated
        elif MACRO_MULT == -0.5:
            MACRO_MULT /= float(v)
            trellis.color(x, y, OFF)

        # this macro_mult is not yet activated
        else:
            MACRO_MULT *= float(v)
            MACRO_CLEAR = False  # macro_mult voids macro_clear
            trellis.color(x, y, colors['macro_mult'])
            
        print(f"macro_mult --> {MACRO_MULT} (no macro_clear)")

    elif k == 'macro_clear':
        if MACRO_CLEAR:
            MACRO_CLEAR = False
            trellis.color(x, y, OFF)

        else:
            MACRO_CLEAR = True
            MACRO_MULT = 1  # macro_clear voids macro_mult
            trellis.color(x, y, colors['macro_clear'])

        print(f'macro_clear --> {MACRO_CLEAR} (macro_mult = 1)')

    elif k == 'random':
        # already selected (de-select)
        if RANDOM:
            RANDOM = False
            trellis.color(x, y, colors['mode'])
        else:
            RANDOM = True
            trellis.color(x, y, colors['mode_set'])

        print(f"random --> {RANDOM}")

    elif k == 'grid_mode':
        GRID_MODE = GRID_MODE % N_GRID_MODES + 1
        trellis.color(x, y, colors['mode_set'])  # temporary light
        print(f'grid_mode --> {GRID_MODE}')

    elif k == 'assign':
        # assigning control to controller (if available)
        if (None not in [CONTROL, CONTROLLER]) and \
            (int(CONTROL) <= MAX_CONTROLS[int(CONTROLLER[-1])]):
            # assign given SELECT value (e.g., 1 for track2) to controller
            assignments[CONTROLLER[:-2]] = int(CONTROLLER[-1])
            trellis.color(x, y, colors['assign_on'])  # temporary light
            assign_control()
            print(f"control {CONTROL} --> {CONTROLLER}")
            CONTROL = None
            CONTROLLER = None
            print(":: assignments ::")
            for k_ in ["".join(g[i][0].split(' ')) for i in range(1, 8)]:
                print(f"{k_:<9}{assignments[k_]}")

        # clear all assignments for a macro
        elif MACRO is not None and MACRO_CLEAR:
            macros[MACRO] = [0, 0, 0, 0, 0]
            trellis.color(x, y, colors['assign_on'])
            print(f"macro {MACRO} cleared (unselect pads)")
            MACRO = None
            MACRO_CLEAR = False
            MACRO_MULT = 1
            CONTROL = None
            CONTROLLER = None

        # assigning macro to controller (for selected track)
        elif (None not in [SELECT, CONTROL, MACRO]) and \
            (int(CONTROL) <= MAX_CONTROLS[SELECT]):
            macros[MACRO][SELECT] += 1
            trellis.color(x, y, colors['assign_on'])
            print(f"control {CONTROL} for track/fx {SELECT} --> {MACRO}")
            CONTROL = None
            MACRO = None
            MACRO_MULT = 1
            RANDOM = False
            print(":: macros ::")
            for i in range(1, 4):
                print(f'enc {i}', macros[str(i)])

        # assign random value to a control for SELECTed track/fx
        elif (None not in [SELECT, CONTROL]) and RANDOM and \
            (int(CONTROL) <= MAX_CONTROLS[SELECT]):
            trellis.color(x, y, colors['assign_on'])
            print(f"random control {CONTROL} to track/fx {SELECT}")
            CONTROL = None
            RANDOM = False
            MACRO_MULT = 1

# -------------------------
#         CALLBACK
# -------------------------
def pad(x, y):
    '''
    Utility function after button [x, y] is pressed.

    Note: x and y are zero-based (i.e., 0, 1, ..., etc.)
    '''
    pad_grid(x, y)
    redraw_grid()


def button(x, y, edge):
    '''
    Actions to take for each edge event on the grid

    Parameters
    ----------
    x : int
        grid column
    y : int
        grid row
    edge : NeoTrellis EDGE event
        event
    '''
    # Recently pressed
    if edge == NeoTrellis.EDGE_RISING:
        pad(x, y)

        # TESTING
        # type_keys(f"row {y} column {x}")

    # Recently released
    # elif edge == NeoTrellis.EDGE_FALLING:
    #     pass

    return None


def init():
    for y in range(8):
        for x in range(8):
            # activate rising edge events
            trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
            # activate falling edge events
            trellis.activate_key(x, y, NeoTrellis.EDGE_FALLING)
            # set callback for rising/falling edge events
            trellis.set_callback(x, y, button)

            # fanciness
            if y == x:
                trellis.color(x, y, v_to_rgb())
                time.sleep(0.05)
                trellis.color(x, y, OFF)

    redraw_grid()


# -------------------------
#         RUNNING
# -------------------------
init()

while True:
    trellis.sync()
    time.sleep(0.01)  # try commenting this out if things are slow
