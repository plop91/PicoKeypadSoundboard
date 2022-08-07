import time
import picokeypad as keypad
import sys
import _thread


def set_colour(color, index):
    if color == 0:
        keypad.illuminate(index, 0x00, 0x20, 0x00)
    elif color == 1:
        keypad.illuminate(index, 0x20, 0x20, 0x00)
    elif color == 2:
        keypad.illuminate(index, 0x20, 0x00, 0x00)
    elif color == 3:
        keypad.illuminate(index, 0x20, 0x00, 0x20)
    elif color == 4:
        keypad.illuminate(index, 0x00, 0x00, 0x20)
    elif color == 5:
        keypad.illuminate(index, 0x00, 0x20, 0x20)
    elif color == 6:
        keypad.illuminate(index, 0x05, 0x05, 0x05)
    else:
        keypad.illuminate(index, 0x00, 0x00, 0x00)


def read_color_matrix():
    data = sys.stdin.readline().strip()
    data_array = data.split()
    if len(data_array) != 16:
        return
    for i in range(0, 16):
        set_colour(int(data_array[i]), i)


def second_thread():
    while True:
        read_color_matrix()
        time.sleep(0.1)


if __name__ == "__main__":
    keypad.init()
    keypad.set_brightness(1.0)
    NUM_PADS = keypad.get_num_pads()
    _thread.start_new_thread(second_thread, ())
    while True:
        button_states = keypad.get_button_states()
        print(button_states)
        # read_color_matrix()
        keypad.update()
        time.sleep(0.1)
