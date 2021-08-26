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

trelli = [
    [NeoTrellis(i2c_bus, False, addr=0x2E),
     NeoTrellis(i2c_bus, False, addr=0x30)],
    [NeoTrellis(i2c_bus, False, addr=0x31),
     NeoTrellis(i2c_bus, False, addr=0x2F)]
]

trellis = MultiTrellis(trelli)

UPPER_LEFT = 40

# some color definitions
OFF = (0, 0, 0)
V = 100  # default velocity (color "volume")

# Tell the device to act like a keyboard.
keyboard = Keyboard(usb_hid.devices)

# Send a keypress of ESCAPE
keyboard.send(Keycode.ESCAPE)

# Send CTRL-A (select all in most text editors)
keyboard.send(Keycode.CONTROL, Keycode.A)

# You can also control key press and release manually:
keyboard.press(Keycode.CONTROL, Keycode.A)
keyboard.release_all()

keyboard.press(Keycode.ESCAPE)
keyboard.release(Keycode.ESCAPE)


def type_keys(characters):
    character = {
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
        ' ': Keycode.SPACEBAR
    }

    for c in characters.lower():
        keyboard.send(character[c])
        # keyboard.press(character[c])


def get_grid(upper_left, quad=False):
    if quad:
        def get_quad(ul):
            return [list(range(n, n+4)) for n in range(ul, ul + 16, 4)]

        # If upper_left is 40, quad corners are [40, 56, 72, 88]
        quad_corners = list(range(upper_left, upper_left + 64, 16))
        quads = [get_quad(ul) for ul in quad_corners]

        quad_l = quads[0] + quads[2]
        quad_r = quads[1] + quads[3]

        grid = [l + r for l, r in zip(quad_l, quad_r)]

        # print(f"Using quad-grid with corners: {quad_corners}")

    # build normal grid
    else:
        grid = [list(range(n, n + 8)) for n in
                range(upper_left, upper_left + 64, 8)]

    return grid


def note_to_xy(note):
    assert note in flat_grid

    loc = flat_grid.index(note)
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
    '''
    if hue == 'yellow':
        h = 48
        s = .90
    else:
        h = 48
        s = .90

    r, g, b = hsv_to_rgb(h, s, v / 127)

    return int(r), int(g), int(b)


def button(x, y, edge, light=False):
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
        text = f"Pressing grid row {y} column {x}"
        type_keys(text)
        print(text)

        if light:
            trellis.color(x, y, pixel_on(V))

    # Recently released
    elif edge == NeoTrellis.EDGE_FALLING:

        if light:
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
#         RUNNING
# -------------------------
init()

while True:
    trellis.sync()
    time.sleep(0.02)  # try commenting this out if things are slow
