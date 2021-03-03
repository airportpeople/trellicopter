# CIRCUITPY Setup

## Update and Install

[Bootloader](https://learn.adafruit.com/adafruit-feather-m4-express-atsamd51/update-the-uf2-bootloader). You'll have to double tap the reset button (pretty quick-ish). Load the file, and let it reset to show the BOOT drive again.

[Circuitpy](https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython#start-the-uf2-bootloader-2977081-13). Start the Bootloader, load this file into the BOOT drive, and let it install. You'll see the CIRCUITPY drive show up when it's done.

## Accessing the REPL Serial Console

(Using [these](https://www.bggofurther.com/2017/08/connect-to-serialconsole-terminal-with-macos-using-screen/) instructions.)

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

To [leave](https://learn.adafruit.com/welcome-to-circuitpython/the-repl), press **Ctrl + D**.

## Editing

**ONLY EDIT THE TRELLICOPTER REPO.**

1. Edit the `trellicopter/code.py` file. 
2. Copy-paste into the *CIRCUITPY* drive (the trellicopter should update).

Use the `Adafruit_Blinka` repo for the most recent mirror of the Trellis firmware (for writing code in `trellicopter`). (Copy/Paste `Adafruit_Blinka/src` into `trellicopter/src`).

### Important:
- In `trellicopter/lib`, use the `.py` files from `Adafruit_/adafruit_py`
- In `CIRCUITPY/lib`, use the `.mpy` files from `Adafruit_/adafruit_mpy`

These `adafruit` packages come from the most recent [Adafruit library update](https://circuitpython.org/libraries).

## Extra Stuff

- [Grid Addresses](https://learn.adafruit.com/adafruit-neotrellis/tiling)