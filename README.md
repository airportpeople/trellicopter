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

[Bootloader](https://learn.adafruit.com/adafruit-feather-m4-express-atsamd51/update-the-uf2-bootloader). You'll have to double tap the reset button (pretty quick-ish). Load the file, and let it reset to show the BOOT drive again.

[CIRCUITPY](https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython#start-the-uf2-bootloader-2977081-13). Start the Bootloader, load this file into the BOOT drive, and let it install. You'll see the CIRCUITPY drive show up when it's done.

## Accessing the REPL Serial Console

In here, you can view the output of your `code.py` file. To open the console, we follow [these](https://www.bggofurther.com/2017/08/connect-to-serialconsole-terminal-with-macos-using-screen/) instructions:

```bash
$ ls /dev*/usb*
> ls: /dev*/usb*: No such file or directory
$ ls /dev/tty*usb*
> tty.usbserial (or something like it)
```

Copy paste the last line, and run

```bash
screen /dev/tty.usbserial 9600,cs8,ixon
```

To [leave](https://learn.adafruit.com/welcome-to-circuitpython/the-repl), press **Ctrl + D**. *Note: you may need to press **Ctrl + C** to stop whatever script is happening, if you like.*

# MIDI and Editing Workflow

The current `code.py` file works to create a simple MIDI grid which sends MIDI on channel 1, and receives from channels 2, 3, and 4. When a MIDI message is received (within range), the respective button will light up.

I like to have my code edited in PyCharm. I'll have the IDE up along with an open REPL console (above). I make updates to the trellicopter repo, which is meant to *emulate* what is on the Feather M4. Once I feel good about the code, I'll copy-paste the `code.py` file, and place it into the *CIRCUITPY* drive.

**Step 1:** Clone this repository (the *main* branch), and the [Adafruit Blinka](https://github.com/adafruit/Adafruit_Blinka) repo.

**Step 2:** Get the most recent [Adafruit library](https://circuitpython.org/libraries) **for both `.py` and `.mpy` files** (these are two separate links on the linked page). On my computer, I save the entirety of these in `adafruit_py` and `adafruit_mpy` folders (respectively), just to keep track.

**Step 3:** The folders in `trellicopter/lib` come from `adafruit_py`, so that editing in PyCharm is friendly (you can set this as a "Source" in the IDE). I'm not very diligent, so you'll probably want to replace these folders with the updated version of them in your most recent downloaded `adafruit_py` folder (note, these are **.py** files). This includes

- `adafruit_bus_device`
- `adafruit_midi`
- `adafruit_neotrellis`
- `adafruit_seesaw`

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