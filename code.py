import time
import usb_midi
import adafruit_midi
from board import SCL, SDA
import busio
from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis

# TimingClock is worth importing first if present
# from adafruit_midi.timing_clock import TimingClock
# from adafruit_midi.channel_pressure import ChannelPressure
# from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
# from adafruit_midi.pitch_bend import PitchBend
# from adafruit_midi.polyphonic_key_pressure import PolyphonicKeyPressure
# from adafruit_midi.program_change import ProgramChange
# from adafruit_midi.start import Start
# from adafruit_midi.stop import Stop
# from adafruit_midi.system_exclusive import SystemExclusive
from adafruit_midi.midi_message import MIDIUnknownEvent


# create the i2c object for the trellis
i2c_bus = busio.I2C(SCL, SDA)

trelli = [
    [NeoTrellis(i2c_bus, False, addr=0x2E), NeoTrellis(i2c_bus, False, addr=0x30)],
    [NeoTrellis(i2c_bus, False, addr=0x31), NeoTrellis(i2c_bus, False, addr=0x2F)]
]

trellis = MultiTrellis(trelli)

# some color definitions
OFF = (0, 0, 0)

midi = adafruit_midi.MIDI(
    midi_in=usb_midi.ports[0],
    midi_out=usb_midi.ports[1],
    in_channel=(1, 2, 3),
    out_channel=0,
)

UPPER_LEFT = 40
grid = [list(range(n, n+8)) for n in
        range(UPPER_LEFT, UPPER_LEFT + 64, 8)]
V = 100  # default velocity
major_chord = [0, 4, 10]  # for debugging


def hsv_to_rgb(h, s, v):
    '''
    HSV to RGB. (`h` is in degrees).

    E.g., hsv_to_rgb(50, .53, .98) = (249.9, 227, 117)
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


def pixel_on(v):
    '''
    slightly yellow. v is velocity, between 0 and 127
    '''
    r, g, b = hsv_to_rgb(50, .53, v / 127)
    return int(r), int(g), int(b)


def note_on():
    print(
        "Playing major chord with root",
        msg_in.note,
        "from channel",
        msg_in.channel + 1,
    )
    for offset in major_chord:
        new_note = msg_in.note + offset
        if 0 <= new_note <= 127:
            midi.send(NoteOn(new_note, msg_in.velocity))
            trellis.color(3, 3, pixel_on(30))


def note_off():
    for offset in major_chord:
        new_note = msg_in.note + offset
        if 0 <= new_note <= 127:
            midi.send(NoteOff(new_note, 0x00))
            trellis.color(3, 3, OFF)


def button(x, y, edge):
    '''
    Actions to take for each edge event on the grid

    Parameters
    ----------
    x : int
        column
    y : int
        row
    edge : NeoTrellis EDGE event
        event
    '''
    # Recently pressed
    if edge == NeoTrellis.EDGE_RISING:
        midi.send(NoteOn(grid[y][x], V))
        print(f"Sending note {grid[y][x]} at velocity {V}")
        trellis.color(x, y, pixel_on(30))
    # Recently released
    elif edge == NeoTrellis.EDGE_FALLING:
        midi.send(NoteOff(grid[y][x], 0x00))
        trellis.color(x, y, OFF)


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
            trellis.color(x, y, pixel_on(30))
            time.sleep(0.05)
            trellis.color(x, y, OFF)


# -------------------------
#           INIT
# -------------------------
init()
print("Midi in and out")
print("Default output channel:", midi.out_channel + 1)  # DAWs start at 1
print("Listening on input channels:", tuple([c + 1 for c in midi.in_channel]))

# -------------------------
#         RUNNING
# -------------------------
while True:
    msg_in = midi.receive()  # non-blocking read

    # MIDI IN: Note On
    if isinstance(msg_in, NoteOn) and msg_in.velocity != 0:
        note_on()

    # MIDI IN: Note Off
    elif (
        isinstance(msg_in, NoteOff)
        or isinstance(msg_in, NoteOn)
        and msg_in.velocity == 0
    ):
        note_off()

    # MIDI IN: Unknown MIDI Event
    elif isinstance(msg_in, MIDIUnknownEvent):
        print("Unknown MIDI event status ", msg_in.status)

    # MIDI IN: Any other MIDI Event
    elif msg_in is not None:
        midi.send(msg_in)

    # Sync (the trellis can only be read every 17 milliseconds or so)
    trellis.sync()
    time.sleep(0.02)
