import time
from random import random

import usb_midi
import adafruit_midi
import busio
from board import SCL, SDA
from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.control_change import ControlChange
from adafruit_midi.midi_message import MIDIUnknownEvent


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

UPPER_LEFT = 0
V = 100  # default color value
PAGE = 'main'

CC_MAP = {
    'time': 14,
    'mix': 15,
    'length': 16,
    'drip_modify': 17,
    'clock': 18,
    'loop_modify': 19,
    'drip': 21,
    'routing': 22,
    'loop': 23,
    'exp': 100
}

params = {
    'time': 64,
    'mix': 64,
    'length': 64,
    'drip_modify': 64,
    'clock': 64,
    'loop_modify': 64,
    'drip': 2,
    'routing': 2,
    'loop': 2,
    'exp': 0,
    'pset': 0
}


def get_grid(top_left, height=8, length=8, bottom_right=127, integer=True):
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


def pixel_on(v, hue='yellow'):
    '''
    slightly yellow. v is velocity, between 0 and 127

    color map: https://www.rapidtables.com/convert/color/rgb-to-hsv.html
    '''
    if hue == 'yellow':
        h = 48
        s = .90
    else:
        # white
        h = 180
        s = 1

    r, g, b = hsv_to_rgb(h, s, v / 127)

    return int(r), int(g), int(b)


def main_page(x, y):
    grid_1x8 = get_grid(0, 1, 8, bottom_right=127)[0]
    grid_1x6_ = get_grid(0, 1, 6, bottom_right=127 // 2)[0]
    grid_1x5_ = get_grid(76, 1, 5, bottom_right=127)[0]
    grid_2x4 = get_grid(0, 2, 4, bottom_right=127)
    
    grid_k = [['mix'] * 8,
              ['drip'] + ['clock'] * 6 + ['loop'],
              ['drip'] + ['clock'] * 6 + ['loop'],
              ['time'] * 4 + ['length'] * 4,
              ['time'] * 4 + ['length'] * 4,
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
    
    return grid_k[y][x], grid_v[y][x]


def pad(x, y):
    if PAGE == 'main':
        k, v = main_page(x, y)
        
        if k == 'page':
            # PAGE = v
            print(f"page -> {v}")

        elif k == 'pset':
            params[k] = v
            # TODO: do the update preset thing
            print(f"OUT (pc) -- "
                  f"C: {out_channel + 1}\t"
                  f"p: {v} (pset)\t")

        else:
            cc = CC_MAP[k]
            midi.send(ControlChange(cc, v))
            print(f"OUT (cc) -- "
                  f"C: {out_channel + 1}\t"
                  f"#: {cc} ({k})\t"
                  f"v: {v}\t")


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
        trellis.color(x, y, pixel_on(V, 'white'))

    # Recently released
    elif edge == NeoTrellis.EDGE_FALLING:
        trellis.color(x, y, OFF)


def init():
    global grid
    global flat_grid

    grid = get_grid(UPPER_LEFT)
    flat_grid = [i for row in grid for i in row]

    for y in range(8):
        for x in range(8):
            # activate rising edge events
            trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
            # activate falling edge events
            trellis.activate_key(x, y, NeoTrellis.EDGE_FALLING)
            # set callback for rising/falling edge events
            trellis.set_callback(x, y, button)

            # fanciness
            trellis.color(x, y, pixel_on(V))
            time.sleep(0.05)
            trellis.color(x, y, OFF)


# -------------------------
#           INIT
# -------------------------
init()
# print("Output Channel:", midi.out_channel + 1)  # DAWs start at 1
# print("Input Channels:", [c + 1 for c in midi.in_channel])

# -------------------------
#         RUNNING
# -------------------------
while True:
    trellis.sync()
    time.sleep(0.02)  # try commenting this out if things are slow
