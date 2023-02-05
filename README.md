# trellicopter

Helicopters really just shouldn't fly. Ask any engineer, and they'll tell you it's a wonder that they work.

Whatever is going on with helicopters is apparently happening with this NeoTrellis I put together. Hence, the name.

# Overview

These are instructions on running the [Adafruit 8x8 NeoTrellis Feather M4 Kit Pack](https://www.adafruit.com/product/1929?gclid=CjwKCAiAyc2BBhAaEiwA44-wW63PYCkAl9Zfi6kaksNPi9xqDzJIXK7--h8ihcQyx7eMPXnjFNWXXRoC15sQAvD_BwE) with Python:

1. First, I go through the initial setup of CIRCUITPY.
2. Then, I go through instructions to set this up as MIDI controller. This includes steps to make editing your CIRCUITPY code friendly.
3. Finally, a quick walkthrough to set this up to emulate a [monome grid](https://monome.org/docs/grid/) (i.e., an 8x8, 64-grid) for the [Norns](https://monome.org/norns/).

# CIRCUITPY Setup

For development purposes, these are the steps to take with a new NeoTrellis grid, or for user-defined updates.

## Update and Install

[Bootloader](https://learn.adafruit.com/adafruit-feather-m4-express-atsamd51/update-the-uf2-bootloader). Double tap the device's reset button (pretty quick-ish) to enter "boot mode". Load (drag and drop) the most recent version of the bootloader into the disk, and let it reset to show the BOOT drive again.

[CIRCUITPY](https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython#download-the-latest-version-2977908-4). Download the most recent version of CIRCUITPY for your chip (Feather M4 Express, likely). Start the Bootloader (above), then load the UF2 file into the BOOT drive, and let it install. You'll see the CIRCUITPY drive show up when it's done.

## Accessing the REPL Serial Console

In here, you can view the output of your `code.py` file. To open the console, we follow [these](https://www.bggofurther.com/2017/08/connect-to-serialconsole-terminal-with-macos-using-screen/) instructions:

*(One of the following should work.)*

```bash
$ ls /dev*/usb*
> ls: /dev*/usb*: No such file or directory
$ ls /dev/tty*usb*
> tty.usbserial (or something like it)
```

Copy (to paste) the output that works, and run

```bash
screen /dev/tty.usbserial 9600,cs8,ixon
```

*(I.e., everything in between `screen` and `9600` is in your copy/paste clipboard.)*

To [leave](https://learn.adafruit.com/welcome-to-circuitpython/the-repl), press **Ctrl + D**. *Note: you may need to press **Ctrl + C** to stop whatever script is happening, if you like.*

# Setup Workflow

**This repository is meant to emulate what is loaded on the trellicopter.**

I like to have my code edited in VS Code. I'll have the IDE up along with an open REPL console (above). I make updates to the trellicopter repo, which is meant to *emulate* what is on the Feather M4. Once I feel good about the code, I'll copy-paste the `code.py` file, and place it into the *CIRCUITPY* drive.

**Step 1:** Clone this repository (the *main* branch), and the [Adafruit Blinka](https://github.com/adafruit/Adafruit_Blinka) repo.

**Step 2:** Get the most recent [Adafruit library](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/latest) **for both `.py` and `.mpy` files** (these will be two separate links). On my computer, I save the entirety of these in `adafruit_py` and `adafruit_mpy` folders (respectively), just to keep track.

**Step 3:** The folders in `trellicopter/lib` come from `adafruit_py`, so that editing in PyCharm is friendly (you can set this as a "Source" in the IDE). I'm not very diligent, so you'll probably want to replace these folders with the updated version of them in your most recent downloaded `adafruit_py` folder (note, these are **.py** files). This includes

- `adafruit_bus_device`
- `adafruit_midi`
- `adafruit_neotrellis`
- `adafruit_seesaw`

*You'll need to add whatever folders are required for the project you're working on.*

**Step 4:** The folders in `trellicopter/src` come from the `Adafruit_Blinka` repo, i.e., the most recent mirror of the Trellis firmware. Copy-paste the contents of `Adafruit_Blinka/src` into `trellicopter/src`. Again, this will make editing in PyCharm kinda nice.

**Step 5:** In your CIRCUITPY drive (on the NeoTrellis), copy paste the `.mpy` version of the folders from Step 3. So, you'll have something like:

```
CIRCUITPY/
    /lib
        /adafruit_bus_device
        /adafruit_midi
        /adafruit_neotrellis
        /adafruit_seesaw
    ...
    code.py
```

where `code.py` is exactly the same file as what's in `trellicopter`, and the folders in `lib` are the **`.mpy`** version of the folders from `adafruit_mpy`.

**Step 6 - infinity:** Editing. My workflow goes like this:

1. Open PyCharm, and open a REPL console.
2. Edit the `trellicopter/code.py` file. *(For one, make sure the [grid addresses](https://learn.adafruit.com/adafruit-neotrellis/tiling) match your own.)*
3. Copy-paste the `code.py` file into the *CIRCUITPY* drive (the trellicopter should update).
4. Watch the output on REPL.
5. Rinse, Repeate, Smile :)

# Monome Grid Setup

The credit for this really goes to [Jeremy Arnold](https://github.com/jaggednz) and [miker2049](https://github.com/miker2049).

**Step 1:** Clone [my fork of the midigrid repository](https://github.com/airportpeople/midigrid) into your Norns's `dust/code` folder.

**Step 2:** Notice on [line 13](https://github.com/airportpeople/midigrid/blob/master/lib/supported_devices.lua#L13), I reference the (lowercase) `'feather m4 express'`. After getting the MIDI set up from the above section, this title should match the name that comes up in your Norns when you plug it in.

**Step 3:** Also, notice that the [grid notes](https://github.com/airportpeople/midigrid/blob/master/lib/devices/generic_device.lua#L4) in `midigrid` match the outcome of the [grid calculation](https://github.com/airportpeople/trellicopter/blob/main/code.py#L46) in `trellicopter`. **THESE NEED TO MATCH!**

**Step 4:** Open [Maiden](https://monome.org/docs/norns/maiden/), and update whatever script you plan on running (except those that have built in support, e.g., Cheat Codes 2 — check the docs). At the top of the script, [add](https://github.com/airportpeople/midigrid#instructions) `include('midigrid/lib/midigrid')`.

**Step 5:** Go to `PARAMETERS -> EDIT -> GRID` and make sure to set the following:

- `grid size = 64`
- `vert rotation = usb on bottom`
- `midigrid? = yes`

**Step 6:** Enjoy. Have fun. Smile :)

# Alternative (Serial Port)

Alternatively, you could use Steve's (okyeron's) [solution](https://github.com/okyeron/neotrellis-monome):

*Note: This solution only works if you have a 64-grid, 8x8, with [grid addresses](https://learn.adafruit.com/adafruit-neotrellis/tiling) below:*

```
[
    [0x2E, 0x30],
    [0x31, 0x2F]
]
```
*If your addresses are different, reach out to Steve and follow the rest of the instructions accordingly. He is incredibly helpful!*

1. Download the [UF2 file](./neotrellis_f_m4_8x8.UF2) (or whichever one matches your addresses), and install it onto your system using the [bootloader](#update-and-install).
2. Access your norns via WiFi using [SSH](https://monome.org/docs/norns/wifi-files/#ssh).
3. Complete this fairly benign Norns hack, [here](https://github.com/okyeron/neotrellis-monome#norns-shield) (roughly, to allow Norns to recognize this device's serial number). **This needs to be done after every Norns Update.**
4. Restart your Norns.
5. Make sure that you've uninstalled *midigrid* in [maiden](https://monome.org/docs/norns/maiden/) (if you don't need it anymore), and that you've removed references to *'feather m4 express'* as a MIDI controller. `MAIN -> SYSTEM -> DEVICES -> MIDI -> select-and-change-to-"none"`.
6. Also, make sure that your Norns is seeking out the right grid: `MAIN -> SYSTEM -> DEVICES -> GRID -> select-and-change-to-"neo-monome m4216124"`.
7. (optional) If you're running something like Cheat Codes 2, you'll need to update the grid parameters there, and make sure `midigrid? = no`: `PARAMS -> GRID -> midigrid? = no`.
8. Do music.

# HID Keyboard

* [Keycodes](https://github.com/adafruit/Adafruit_CircuitPython_HID/blob/master/adafruit_hid/keycode.py)

