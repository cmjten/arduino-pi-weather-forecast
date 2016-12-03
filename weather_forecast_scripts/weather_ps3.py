"""
Arduino Uno - Raspberry Pi Weather Forecast

This Python script gathers weather data from the Internet using the
PyOWM API. This data is sent to the Arduino Uno through serial port,
then displayed on the LCD screen. This script also tells the Arduino Uno
which data to display. For this version of the script, a PS3 controller
is used as input. This script also depends on the weather_commands script.

External modules required:
- Pygame
- PyOWM
- PySerial
"""

import pygame
from weather_commands import WeatherInfo, WeatherSerialPort, WeatherController


class WeatherControllerPS3(WeatherController):
    """
    Takes input from the PS3 controller and sends data to the Arduino Uno.
    Inherits WeatherController class from the weather_keyboard script.

    Instance variables:
    _data_index: index + 2 of the current data being displayed
    _controller: Controller being used
    _current_button_state: Current button state
    _previous_button_state: Button state from previous loop iteration
    """
    # Pygame mappings for the PS3 buttons
    LEFT = 7
    RIGHT = 5
    CIRCLE = 13
    SQUARE = 15

    def __init__(self, weather_info, serial_port):
        super(WeatherControllerPS3, self).__init__(weather_info, serial_port)
        self._data_index = 2

        # Sets up pygame
        pygame.init()
        self._controller = pygame.joystick.Joystick(0)
        self._controller.init()

        # True is a button is pressed, false otherwise
        # Previous button state for detecting a change in state and
        # preventing multiple signals to be sent when button is held
        # down
        self._current_button_state = False
        self._previous_button_state = True

    def scroll_left(self):
        """Scrolls to the left"""
        if self._data_index > 2:
            self._data_index -= 1
        self._serial_port.write([self._data_index])

    def scroll_right(self):
        """Scrolls to the right"""
        if self._data_index < 6:
            self._data_index += 1
        self._serial_port.write([self._data_index])

    def controller_listener(self):
        """Processes input from the PS3 controller"""
        for event in pygame.event.get():
            pass

        # Gets the current state of the controller (if any buttons have
        # been pressed or not). Detects state change
        self._current_button_state = self._controller.get_button(self.LEFT) or\
                                    self._controller.get_button(self.RIGHT) or\
                                    self._controller.get_button(self.CIRCLE) or\
                                    self._controller.get_button(self.SQUARE)

        if self._current_button_state != self._previous_button_state:
            # Change in state
            if self._controller.get_button(self.LEFT):
                # Scroll left
                self.scroll_left()

            elif self._controller.get_button(self.RIGHT):
                # Scroll right
                self.scroll_right()

            elif self._controller.get_button(self.CIRCLE):
                # Update
                self.update()

            elif self._controller.get_button(self.SQUARE):
                # New city
                self._weather_info.set_city()

        self._previous_button_state = self._current_button_state


if __name__ == "__main__":
    weather_info = WeatherInfo()
    serial_port = WeatherSerialPort()
    controller = WeatherControllerPS3(weather_info, serial_port)
    
    while True:
        controller.controller_listener()
