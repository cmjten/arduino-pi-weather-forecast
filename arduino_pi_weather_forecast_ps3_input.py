"""
Arduino Uno - Raspberry Pi Weather Forecast

This Python script will gather weather data from the Internet through
the PyOWM module. This data will be sent to the Arduino Uno through the
serial port, then displayed on the LCD screen. This script will also
tell the Arduino Uno which data to display. A PS3 controller will be 
used as input.

External modules required:
- Pygame
- PyOWM
- PySerial
"""

import pygame, pyowm, serial, time
import serial.tools.list_ports as list_ports

class WeatherInfo:
    """
    Stores the weather information

    Instance variables:
    _city: City for which the forecast will be displayed
    _forecast_data: List that stores forecast data in format
                    [City, Condition, Temperature, Humidity, Wind]
    _owm: Allows access to PyOWM API
    _forecast: Stores all weather data from OWM
    """
    def __init__(self):
        """Constructor for WeatherInfo class"""
        self._city = "Mississauga, CA" # Default city is Mississauga
        
        # Stores forecast data in the following format:
        # [City, Condition, Temperature, Humidity, Wind]
        self._forecast_data = [] 

        # Setting up PyOWM
        self._owm = pyowm.OWM("5ec1a1baebeabb32f92cec56a6682dfb")
        self._forecast = self._owm.weather_at_place(self._city).get_weather()


    def get_city(self):
        """
        Returns the city

        return: self._city
        """
        return self._city


    def set_city(self):
        """Prompts the user for a new city"""
        self._city = input("Enter a new city: ")
        print(self._city)
        try:
            self._forecast = self._owm.weather_at_place(self._city).get_weather()
            print("City found")
        except:
            print("City not found")


    def download_forecast_data(self):
        """Downloads forecast data from PyOWM API"""
        print("Updating...")
        city = self._city.split(",")[0] # City name only
        
        try:
            condition = self._forecast.get_status()

            # temp in C and F
            temp = str(int(self._forecast.get_temperature("celsius")["temp"]))\
                   + " C / " + \
                   str(int(self._forecast.get_temperature("fahrenheit")["temp"]))\
                   + " F"

            humidity = str(self._forecast.get_humidity()) + " %"

            # wind direction and speed
            wind = str(int(self._forecast.get_wind()["deg"])) + " deg, " + \
                   str(int(self._forecast.get_wind()["speed"]))[0:3] + " kmh"
            
            self._forecast_data = [city, condition, temp, humidity, wind]

        except:
            # Error gathering data
            print("Error")
            self._forecast_data = [city, "None", "None", "None", "None"]
            

    def get_forecast_data(self):
        """
        Returns forecast data

        return: self._forecast_data
        """
        return self._forecast_data


class WeatherSerialPort:
    """
    Stores serial port data

    Instance variable:
    _serial_port: Serial port where the Arduino Uno is connected
    """
    def __init__(self):
        """
        Gets the first serial port connected. Assumes that Arduino Uno is
        the only device connected to a serial port
        """
        self._serial_port = serial.Serial(list_ports.comports()[0].device, 9600)


    def get_serial_port(self):
        """
        Returns the serial port

        return: self._serial_port
        """
        return self._serial_port


class WeatherController:
    """
    Controller for the script, Takes input from the PS3 controller and sends
    data to the Arduino Uno
    """
    #Pygame mappings for the PS3 buttons
    LEFT = 7
    RIGHT = 5
    CIRCLE = 13
    SQUARE = 15

    def __init__(self, weather_info, serial_port):
        """
        Constructor

        Parameters:
        weather_info: A WeatherInfo object. Stores weather info.
        serial_port: A WeatherSerialPort object. Serial port where the
                     Arduino Uno is connected
        """
        self._weather_info = weather_info
        self._serial_port = serial_port.get_serial_port()

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

        self._data_index = 2 # index + 2 of data to be shown


    def update(self):
        """Updates forecast data and sends it to the Arduino Uno"""
        self._weather_info.download_forecast_data()
        forecast_data = self._weather_info.get_forecast_data()

        # Tells Arduino Uno that update process is about to start
        self._serial_port.write([1])

        for data in forecast_data:
            # Sends data
            self._serial_port.write(data.encode())
            time.sleep(2)

        # Displays new city's name
        self._data_index = 2
        self._serial_port.write([self._data_index])
        print("Update complete")


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
        self._current_button_state = self._controller.get_button(self.LEFT) or \
                                     self._controller.get_button(self.RIGHT) or \
                                     self._controller.get_button(self.CIRCLE) or \
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
    controller = WeatherController(weather_info, serial_port)
    
    while True:
        controller.controller_listener()
