import serial
import time
import requests
import json
import argparse

DEBUG = False

"""
Project:PicoKeypadSoundboard
Date: 8/7/2022
Author: Ian Sodersjerna
Description: 
"""


class KeypadManager:
    class ColorManager:

        color_dict = {
            "green": 0,
            "yellow": 1,
            "red": 2,
            "magenta": 3,
            "blue": 4,
            "cyan": 5,
            "white": 6,
            "off": 7
        }

        def __init__(self, serial_connection, default_color_matrix=None, rainbow_mode=False):
            self.serial_connection = serial_connection
            if default_color_matrix is None:
                self.color_matrix = [[0, 1, 2, 3],
                                     [4, 5, 6, 0],
                                     [1, 2, 3, 4],
                                     [5, 6, 0, 1]]
            else:
                self.color_matrix = default_color_matrix
            self.rainbow_mode = rainbow_mode

        def step(self):
            self.send_color_matrix()
            if self.rainbow_mode:
                self.rainbow_cycle()
            if DEBUG:
                print("Color matrix: " + str(self.color_matrix))

        def set_rainbow_mode(self, rainbow_mode):
            self.rainbow_mode = rainbow_mode

        def page_to_color_matrix(self, page):
            color_matrix = []
            for row in page:
                color_matrix.append([])
                for col in row:
                    color_matrix[-1].append(self.color_dict[col[1]])
            self.color_matrix = color_matrix

        def get_color_matrix(self):
            return self.color_matrix

        def set_color_matrix(self, color_matrix):
            self.color_matrix = color_matrix

        def send_color_matrix(self):
            for row in self.color_matrix:
                for col in row:
                    self.serial_connection.write(bytes(str(col), 'utf-8'))
                    self.serial_connection.write(bytes(b" "))
            self.serial_connection.write(b'\r\n')
            self.serial_connection.flush()

        def rainbow_cycle(self):
            for i in range(len(self.color_matrix)):
                self.color_matrix[i] = list(map(self.iterate_color, self.color_matrix[i]))

        @staticmethod
        def iterate_color(n):
            return (n + 1) % 6

    def __init__(self, config: str):
        self.config = json.load(open(config))
        self.username = self.config['username']
        self.avatar_url = self.config['avatar_url']
        if self.config['parity'] == 'PARITY_NONE':
            parity = serial.PARITY_NONE
        self.ser = serial.Serial(self.config["com"],
                                 self.config["baudrate"],
                                 timeout=self.config["timeout"],
                                 parity=parity,
                                 rtscts=self.config["rtscts"])
        self.address = self.config['address']
        self.cm = self.ColorManager(self.ser)
        self.prev_buttons = 0
        self.pages = self.config['pages']
        self.current_page = self.pages["home"]

    def run(self):
        self.cm.page_to_color_matrix(self.current_page)
        while True:
            self.cm.step()
            data = self.ser.readline().strip()
            if DEBUG:
                print("received: ", data)
            if data:
                if int(data) > self.prev_buttons:
                    new_buttons = int(data) ^ self.prev_buttons
                    self.decode_button(new_buttons)
                self.prev_buttons = int(data)
            if DEBUG:
                print("current page: ", self.current_page)
            time.sleep(0.1)
            self.ser.flushInput()
            self.ser.flushOutput()

    def bot_play_sound(self, sound):
        r = requests.post(self.address, json={'username': self.username,
                                              'avatar_url': self.avatar_url,
                                              'content': "www.sodersjerna.com:" + self.username + ":play:" + sound})
        if DEBUG:
            print(sound)
            print(r.status_code)
            print(r.text)

    def bot_command(self, command):
        r = requests.post(self.address, json={'username': self.username,
                                              'avatar_url': self.avatar_url,
                                              'content': "www.sodersjerna.com:" + self.username + ":" + command})
        if DEBUG:
            print(r.status_code)
            print(r.text)

    def interpret_command(self, command: str):
        if command.startswith("%"):
            if command.endswith("pause"):
                print("pause")
                self.bot_command("pause")

            elif command.endswith("resume"):
                print("resume")
                self.bot_command("resume")

            elif command.endswith("stop"):
                print("stop")
                self.bot_command("stop")

            elif command.endswith("leave"):
                print("leave")
                self.bot_command("leave")

            elif command.endswith("reset"):
                print("reset")
                self.cm.set_rainbow_mode(False)
                self.cm.page_to_color_matrix(self.current_page)

            elif command.endswith("rainbowon"):
                print("rainbowon")
                self.cm.set_rainbow_mode(True)

            elif command.endswith("rainbowoff"):
                print("rainbowoff")
                self.cm.set_rainbow_mode(False)

            else:
                page_names = list(self.pages.keys())
                print(page_names)
                for name in page_names:
                    if command.endswith(name):
                        self.current_page = self.pages[name]
                        self.cm.page_to_color_matrix(self.current_page)
                        return
                if DEBUG:
                    print("Unknown command: " + command)
        else:
            self.bot_play_sound(command)

    def decode_button(self, buttons):
        if buttons & 1:
            self.interpret_command(self.current_page[0][0][0])
        if buttons & 2:
            self.interpret_command(self.current_page[0][1][0])
        if buttons & 4:
            self.interpret_command(self.current_page[0][2][0])
        if buttons & 8:
            self.interpret_command(self.current_page[0][3][0])
        if buttons & 16:
            self.interpret_command(self.current_page[1][0][0])
        if buttons & 32:
            self.interpret_command(self.current_page[1][1][0])
        if buttons & 64:
            self.interpret_command(self.current_page[1][2][0])
        if buttons & 128:
            self.interpret_command(self.current_page[1][3][0])
        if buttons & 256:
            self.interpret_command(self.current_page[2][0][0])
        if buttons & 512:
            self.interpret_command(self.current_page[2][1][0])
        if buttons & 1024:
            self.interpret_command(self.current_page[2][2][0])
        if buttons & 2048:
            self.interpret_command(self.current_page[2][3][0])
        if buttons & 4096:
            self.interpret_command(self.current_page[3][0][0])
        if buttons & 8192:
            self.interpret_command(self.current_page[3][1][0])
        if buttons & 16384:
            self.interpret_command(self.current_page[3][2][0])
        if buttons & 32768:
            self.interpret_command(self.current_page[3][3][0])


if __name__ == "__main__":
    """
    This is the main method. It starts the program.
    """
    params = argparse.ArgumentParser()
    params.add_argument("--config", help="Config file", default="config.json")
    params.add_argument("--debug", action="store_true")
    arguments = params.parse_args()
    if arguments.debug:
        DEBUG = True
    print("Starting...")

    manager = KeypadManager(arguments.config)
    manager.run()
