import time
from random import random

import usb_midi
import adafruit_midi
import busio
from board import SCL, SDA
from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis
from adafruit_midi.control_change import ControlChange
from adafruit_midi.program_change import ProgramChange


# -------------------------
#          SETUP
# -------------------------
# create the i2c object for the trellis
i2c_bus = busio.I2C(SCL, SDA)

trelli = [
    [NeoTrellis(i2c_bus, False, addr=0x2E),
     NeoTrellis(i2c_bus, False, addr=0x30)],
    [NeoTrellis(i2c_bus, False, addr=0x31),
     NeoTrellis(i2c_bus, False, addr=0x2F)]
]

trellis = MultiTrellis(trelli)

# some color definitions
OFF = (0, 0, 0)

# these are base 0
in_channels = (0,)  # listening on channel 1
out_channel = 1  # sending through channel 2

midi = adafruit_midi.MIDI(
    midi_in=usb_midi.ports[0],
    midi_out=usb_midi.ports[1],
    in_channel=in_channels,
    out_channel=out_channel,
    in_buf_size=64
)

PAGE = 'main'
FINE_PARAM_TYPE = 'drip'
FINE_PARAM = 'drip_modify'
BANK = 1
PSET = 0
HUE = None
BRIGHTNESS = None

CC_MAP = {
    'drip_time': 14,
    'mix': 15,
    'loop_length': 16,
    'drip_modify': 17,
    'clock': 18,
    'loop_modify': 19,
    'drip': 21,
    'routing': 22,
    'loop': 23,
    'exp': 100
}

params = {
    'drip_time': 64,
    'mix': 64,
    'loop_length': 64,
    'drip_modify': 64,
    'clock': 64,
    'loop_modify': 64,
    'drip': 2,
    'routing': 2,
    'loop': 2,
    'exp': 0,
    'pset': 0
}

psets = {}


def get_grid(top_left, height=8, length=8, bottom_right=127, integer=True):
    """
    Get a grid of integer vales from `top-left` to `bottom_right`, with the given dimensions.
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
#        MAIN PAGE
# -------------------------
def main_page(x=None, y=None):
    '''
    If `x` and `y` are None (default), then return the main page key and value grids, respectively. Otherwise, return the information encapsulated in the main page at (`x`, `y`). The latter returns the (key, value) tuple.
    '''
    grid_1x8 = get_grid(0, 1, 8, bottom_right=127)[0]
    grid_1x6_ = get_grid(0, 1, 6, bottom_right=127 // 2)[0]
    grid_1x5_ = get_grid(76, 1, 5, bottom_right=127)[0]
    grid_2x4 = get_grid(0, 2, 4, bottom_right=127)
    
    grid_k = [['mix'] * 8,
              ['drip'] + ['clock'] * 6 + ['loop'],
              ['drip'] + ['clock'] * 6 + ['loop'],
              ['drip_time'] * 4 + ['loop_length'] * 4,
              ['drip_time'] * 4 + ['loop_length'] * 4,
              ['drip_modify'] * 4 + ['loop_modify'] * 4,
              ['drip_modify'] * 4 + ['loop_modify'] * 4,
              ['routing', 'routing', 'pset', 'pset', 'page', 'page', 'page', 'page']]

    grid_v = [grid_1x8,
              [1] + grid_1x6_ + [1],
              [3] + grid_1x5_ + [int(random() * 127)] + [3],
              grid_2x4[0] + grid_2x4[0],
              grid_2x4[1] + grid_2x4[1],
              grid_2x4[0] + grid_2x4[0],
              grid_2x4[1] + grid_2x4[1],
              [1, 3, 1, 2, 'main', 'fine', 'exp', 'psets']]
    
    if x is None or y is None:
        return grid_k, grid_v
    else:
        return grid_k[y][x], grid_v[y][x]


def redraw_main():
    grid_k, grid_v = main_page()

    for y in range(8):
        for x in range(8):
            k = grid_k[y][x]
            v = grid_v[y][x]

            if k in ['mix', 'clock', 'drip_time', 'loop_length', 
                     'drip_modify', 'loop_modify']:
                if v <= params[k]:
                    trellis.color(x, y, v_to_rgb())
                else:
                    trellis.color(x, y, OFF)

            elif k in ['drip', 'loop', 'routing', 'pset']:
                if v == params[k]:
                    trellis.color(x, y, v_to_rgb())
                else:
                    trellis.color(x, y, OFF)
                    
            elif k == 'page':
                if v == PAGE:
                    trellis.color(x, y, v_to_rgb())
                else:
                    trellis.color(x, y, OFF)


def pad_main(x, y):
    global PAGE
    k, v = main_page(x, y)
        
    if k == 'page':
        PAGE = v
        print(f"page --> {v}")

    elif k == 'pset':
        params[k] = v
        midi.send(ProgramChange(v))
        print(f"pset (pc) --> {v}\n")
        print(params)

    else:
        k_trios = ['drip', 'loop', 'routing']
        if (k in k_trios) and (v == params[k]):
            v = 2
        
        params[k] = v
        cc = CC_MAP[k]
        midi.send(ControlChange(cc, v))
        print(f"{k} ({cc}) --> {v}")


# -------------------------
#     FINE TUNING PAGE
# -------------------------
def fine_page(x=None, y=None):
    grid_k = [['*'] * 8] * 7 + \
        [['param_type'] * 2 + ['param'] * 2 + ['page'] * 4]

    grid_v = get_grid(0, 7) + \
            [['drip', 'loop', 'drip_time/loop_length', 
            'drip_modify/loop_modify', 'main', 'fine', 'exp', 'psets']]

    if x is None or y is None:
        return grid_k, grid_v
    else:
        return grid_k[y][x], grid_v[y][x]


def redraw_fine():
    grid_k, grid_v = fine_page()

    for y in range(8):
        for x in range(8):
            k = grid_k[y][x]
            v = grid_v[y][x]

            if k == '*':
                if v <= params[FINE_PARAM]:
                    trellis.color(x, y, v_to_rgb())
                else:
                    trellis.color(x, y, OFF)
            
            elif k == 'param_type':
                if v == FINE_PARAM_TYPE:
                    trellis.color(x, y, v_to_rgb())
                else:
                    trellis.color(x, y, OFF)

            elif k == 'param':
                if FINE_PARAM in v:
                    trellis.color(x, y, v_to_rgb())
                else:
                    trellis.color(x, y, OFF)
            
            elif k == 'page':
                if v == PAGE:
                    trellis.color(x, y, v_to_rgb())
                else:
                    trellis.color(x, y, OFF)


def pad_fine(x, y):
    global PAGE
    global FINE_PARAM
    global FINE_PARAM_TYPE

    k, v = fine_page(x, y)

    if k == '*':
        params[FINE_PARAM] = v
        cc = CC_MAP[FINE_PARAM]
        midi.send(ControlChange(cc, v))
        print(f"{FINE_PARAM} ({cc}) --> {v}")
    
    elif k == 'param_type':
        FINE_PARAM_TYPE = 'mix' if FINE_PARAM_TYPE == v else v

        if FINE_PARAM_TYPE == 'mix':
            FINE_PARAM = 'mix'
        else:
            FINE_PARAM = FINE_PARAM_TYPE + '_modify'

    elif k == 'param':
        if FINE_PARAM_TYPE != 'mix':
            v = v.split('/')
            FINE_PARAM = [e for e in v if FINE_PARAM_TYPE in e][0]

    else:
        PAGE = v
        print(f"page --> {v}")


# -------------------------
#     EXPRESSION PAGE
# -------------------------
def exp_page(x=None, y=None):
    grid_k = [['*'] * 8] * 7 + \
             [['tbd'] * 4 + ['page'] * 4]

    grid_v = get_grid(0, 7) + \
             [['tbd'] * 4 + ['main', 'fine', 'exp', 'psets']]

    if x is None or y is None:
        return grid_k, grid_v
    else:
        return grid_k[y][x], grid_v[y][x]


def redraw_exp():
    grid_k, grid_v = exp_page()

    for y in range(8):
        for x in range(8):
            k = grid_k[y][x]
            v = grid_v[y][x]

            if k == '*':
                if v == params['exp']:
                    trellis.color(x, y, v_to_rgb())
                else:
                    trellis.color(x, y, OFF)
            
            elif k == 'page':
                if v == PAGE:
                    trellis.color(x, y, v_to_rgb())
                else:
                    trellis.color(x, y, OFF)

            elif k == 'tbd':
                trellis.color(x, y, OFF)


def pad_exp(x, y):
    global PAGE
    k, v = exp_page(x, y)

    if k == '*':
        params['exp'] = v
        cc = CC_MAP['exp']
        midi.send(ControlChange(cc, v))
        print(f"exp ({cc}) --> {v}")
    
    elif k == 'tbd':
        print('tbd ...')

    else:
        PAGE = v
        print(f"page --> {v}")


# -------------------------
#       PRESET PAGE
# -------------------------
def preset_page(x=None, y=None, bank=1):
    grid_k = [['*'] * 8] * 5 + \
            [['hue'] * 8] + \
            [['v'] * 8] + \
            [['bank'] * 3 + ['live'] + ['page'] * 4]

    # start with 3, and up
    grid_v = get_grid(
            top_left=(bank - 1) * 5 * 8 + 3, 
            height=5, 
            bottom_right=bank * 5 * 8 + 2) + \
            [['r', 'o', 'y', 'g', 'b', 'i', 'v', 'w']] + \
            [[0, 2, 6, 18, 30, 40, 60, 100]] + \
            [[1, 2, 3, 0] + ['main', 'fine', 'exp', 'psets']]

    if x is None or y is None:
        return grid_k, grid_v
    else:
        return grid_k[y][x], grid_v[y][x]


def redraw_preset():
    grid_k, grid_v = preset_page(bank=BANK)

    for y in range(8):
        for x in range(8):
            k = grid_k[y][x]
            v = grid_v[y][x]

            if k == '*':
                if v in psets.keys():
                    hue_ = psets[v][0]
                    v_ = psets[v][1]
                    
                    if v == PSET: 
                        v_ = min(v_ * 1.5, 100)

                    trellis.color(x, y, v_to_rgb(v_, hue_))

                else:
                    trellis.color(x, y, OFF)
            
            elif k == 'hue':
                trellis.color(x, y, v_to_rgb(hue=v))

            elif k == 'v':
                trellis.color(x, y, v_to_rgb(v=v))
            
            elif k == 'bank':
                if v == BANK:
                    trellis.color(x, y, v_to_rgb())
                else:
                    trellis.color(x, y, OFF)
            
            elif k == 'live':
                if PSET == v:
                    trellis.color(x, y, v_to_rgb())
                else:
                    trellis.color(x, y, OFF)
            
            elif k == 'page':
                if PAGE == v:
                    trellis.color(x, y, v_to_rgb())
                else:
                    trellis.color(x, y, OFF)


def pad_preset(x, y):
    global PAGE
    global BANK
    global HUE
    global BRIGHTNESS
    global PSET
    global psets

    k, v = preset_page(x, y, BANK)

    if k == '*':          
        # if a hue and brightness were just selected
        if (HUE is not None) and (BRIGHTNESS is not None):
            if (v in psets.keys()) and \
                (HUE == psets[v][0]) and \
                (BRIGHTNESS == 0):
                # remove preset
                _ = psets.pop(v)
            elif BRIGHTNESS > 0:
                psets[v] = (HUE, BRIGHTNESS)
                
            HUE = None
            BRIGHTNESS = None

        if v in psets.keys():
            PSET = v
            midi.send(ProgramChange(v))
            print(f"pset (pc) --> {v}")
        
    elif k == 'hue':
        HUE = v
    
    elif k == 'v':
        BRIGHTNESS = v
    
    elif k == 'bank':
        BANK = v

    elif k == 'live':
        PSET = 0
        midi.send(ProgramChange(v))
        print(f"pset (pc) --> {v}\n")
        print(psets)
    
    elif k == 'page':
        PAGE = v
        print(f"page --> {v}")


# -------------------------
#         CALLBACK
# -------------------------
def pad(x, y):
    '''
    Activate the pad at (`x`, `y`).
    '''
    if PAGE == 'main':
        pad_main(x, y)

    elif PAGE == 'fine':
        pad_fine(x, y)
    
    elif PAGE == 'exp':
        pad_exp(x, y)

    elif PAGE == 'psets':
        pad_preset(x, y)

    if PAGE == 'main':
        redraw_main()

    elif PAGE == 'fine':
        redraw_fine()
    
    elif PAGE == 'exp':
        redraw_exp()

    elif PAGE == 'psets':
        redraw_preset()
    

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
    light : bool
        activate pixel light on edge events
    '''
    # Recently pressed
    if edge == NeoTrellis.EDGE_RISING:
        pad(x, y)

    # Recently released
    # elif edge == NeoTrellis.EDGE_FALLING:
    #     trellis.color(x, y, OFF)

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
            trellis.color(x, y, v_to_rgb())
            time.sleep(0.05)
            trellis.color(x, y, OFF)

    redraw_main()

# -------------------------
#           INIT
# -------------------------
init()
print("Output Channel:", midi.out_channel + 1)  # DAWs start at 1
# print("Input Channels:", [c + 1 for c in midi.in_channel])

# -------------------------
#         RUNNING
# -------------------------
while True:
    trellis.sync()
    time.sleep(0.02)  # try commenting this out if things are slow
