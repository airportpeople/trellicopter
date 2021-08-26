import time
import usb_midi
import adafruit_midi
from board import SCL, SDA
import busio
from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis

# TimingClock is worth importing first, if present
# from adafruit_midi.timing_clock import TimingClock
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
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

UPPER_LEFT = 40
V = 100  # default velocity


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


def note_on(light=True):
    # print(f"IN (on) -- "
    #       f"C: {msg_in.channel + 1}\t"
    #       f"N: {msg_in.note}\t"
    #       f"V: {msg_in.velocity}")

    # square light on
    if (msg_in.note in flat_grid) and light:
        x, y = note_to_xy(msg_in.note)
        trellis.color(x, y, pixel_on(msg_in.velocity))


def note_off(light=True):
    # print(f"IN (off) -- "
    #       f"C: {msg_in.channel + 1}\t"
    #       f"N: {msg_in.note}\t"
    #       f"V: {msg_in.velocity}")

    # square light off
    if (msg_in.note in flat_grid) and light:
        x, y = note_to_xy(msg_in.note)
        trellis.color(x, y, OFF)


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
        midi.send(NoteOn(grid[y][x], V))
        # print(f"OUT (on) -- "
        #       f"C: {out_channel + 1}\t"
        #       f"N: {grid[y][x]}\t"
        #       f"V: {V}")

        if light:
            trellis.color(x, y, pixel_on(V))

    # Recently released
    elif edge == NeoTrellis.EDGE_FALLING:
        midi.send(NoteOff(grid[y][x]))
        # print(f"OUT (off) -- "
        #       f"C: {out_channel + 1}\t"
        #       f"N: {grid[y][x]}\t"
        #       f"V: 0")

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
#           INIT
# -------------------------
init()
# print("Output Channel:", midi.out_channel + 1)  # DAWs start at 1
# print("Input Channels:", [c + 1 for c in midi.in_channel])

# -------------------------
#         RUNNING
# -------------------------
while True:
    msg_in = midi.receive()  # non-blocking read

    # MIDI IN: Note On
    if isinstance(msg_in, NoteOn) and (msg_in.velocity not in [0, None]):
        note_on()

    # MIDI IN: Note Off
    elif (
        isinstance(msg_in, NoteOff)
        or (isinstance(msg_in, NoteOn) and (msg_in.velocity in [0, None]))
    ):
        note_off()

    # MIDI IN: Unknown MIDI Event
    # elif isinstance(msg_in, MIDIUnknownEvent):
        # print("Unknown MIDI event status ", msg_in.status)

    # MIDI IN: Any other MIDI Event
    # elif msg_in is not None:
        # print("MIDI Message ", msg_in)

    trellis.sync()
    time.sleep(0.02)  # try commenting this out if things are slow
