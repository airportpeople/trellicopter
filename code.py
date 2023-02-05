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
V = 100  # default velocity (color "volume")

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
SELECT = '1'
CONTROL = '1'
MACRO = None

# Tell the device to act like a keyboard.
keyboard = Keyboard(usb_hid.devices)


def type_keys(characters, press=False, wait=0.04):
    """
    Type the keys in `characters` in sequence, with `wait` seconds in between

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
#        GRID
# -------------------------
def grid(x=None, y=None):
    '''
    If `x` and `y` are None (default), then return the main page key and value grids, respectively. Otherwise, return the information encapsulated in the main page at (`x`, `y`). The latter returns the (key, value) tuple.
    '''
    g = [[f'track_{i}' for i in range(1, 5)] + ['fx'] + 
            [f'control_number_{i}' for i in range(1, 4)],
        ['gridx_1'] * 5 + [f'control_number_{i}' for i in range(4, 7)],
        ['gridy_1'] * 5 + [f'control_number_{i}' for i in range(7, 10)],
        ['gridx_2'] * 5 + [f'control_number_{i}' for i in range(10, 13)],
        ['gridy_2'] * 5 + [f'control_number_{i}' for i in range(13, 16)],
        ['enc_1'] * 5 + ['macro_1', 'macro_2', 'macro_3'],
        ['enc_2'] * 5 + ['macro_.5', 'macro_-1', 'macro_clear'],
        ['enc_3'] * 5 + ['random', 'grid_mode', 'assign']]
    
    if x is None or y is None:
        return g
    else:
        if '_' in g[y][x]:
            return g[y][x].split('_')[0], g[y][x].split('_')[1]
        else:
            return g[y][x], ""


def redraw_grid():
    global SELECT
    
    for y in range(8):
        for x in range(8):
            k, v = grid(x, y)

            # top track/fx row
            if ('track' in k) or (k == 'fx'):
                if k + v == SELECT:
                    trellis.color(x, y, v_to_rgb(40))
                else:
                    trellis.color(x, y, v_to_rgb(10))

            elif k == 'assign':
                trellis.color(x, y, v_to_rgb(40))

            elif 'control_number' in k:
                trellis.color(x, y, v_to_rgb(2 * int(v)))


def pad_grid(x, y):
    global SELECT
    k, v = grid(x, y)
        
    if ('track' in k) or (k == 'fx'):
        SELECT = k + v
        print(f"select --> {k + v}")

    # elif k == 'pset':
    #     params[k] = v
    #     midi.send(ProgramChange(v))
    #     print(f"pset (pc) --> {v}\n")
    #     print(params)

    # else:
    #     k_trios = ['drip', 'loop', 'routing']
    #     if (k in k_trios) and (v == params[k]):
    #         v = 2
        
    #     params[k] = v
    #     cc = CC_MAP[k]
    #     midi.send(ControlChange(cc, v))
    #     print(f"{k} ({cc}) --> {v}")


# -------------------------
#         CALLBACK
# -------------------------
def pad(x, y):
    pad_grid(x, y)
    redraw_grid()


def button(x, y, edge, light=True):
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
    light : bool
        activate pixel light on edge events
    '''
    # Recently pressed
    if edge == NeoTrellis.EDGE_RISING:
        if light:
            trellis.color(x, y, v_to_rgb())

        # TESTING
        type_keys(f"row {y} column {x}")

        pad(x, y)

    # Recently released
    # elif edge == NeoTrellis.EDGE_FALLING:
    #     if light:
    #         trellis.color(x, y, OFF)

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
    time.sleep(0.02)  # try commenting this out if things are slow
