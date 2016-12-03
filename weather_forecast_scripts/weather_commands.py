"""
Arduino Uno - Raspberry Pi Weather Forecast

This Python script gathers weather data from the Internet using the
PyOWM API. This data is sent to the Arduino Uno through serial port,
then displayed on the LCD screen. This script also tells the Arduino Uno
which data to display. Command line is used as input.

Commands:
city - shows city name
condition - shows weather condition
temperature - shows temperature
humidity - shows humidity
wind - shows wind
new - gets new city
update - updates weather information
help - command list

External modules required:
- PyOWM
- PySerial
"""

import pyowm, serial, time
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
        # Setting up PyOWM
        self._owm = pyowm.OWM("5ec1a1baebeabb32f92cec56a6682dfb")
        self._forecast = None
        
        self._city = None
        self.set_city() # Asks the user for a city
        
        # Stores forecast data in the following format:
        # [City, Condition, Temperature, Humidity, Wind]
        self._forecast_data = [] 

    def get_city(self):
        """
        Returns the city

        return: self._city
        """
        return self._city

    def set_city(self):
        """Prompts the user for a new city"""
        self._city = input("Enter a new city: ")

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
    Controller for the script, Takes input from command line and sends
    data to the Arduino Uno

    Instance variables:
    _weather_info: WeatherInfo object
    _serial_port: Serial port where the Arduino Uno is connected
    """
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
        self._serial_port.write([2])
        print("Update complete")

    def help(self):
        """Displays commands"""
        print("\nArduino Pi Weather Forecast Commands\n" +
              "city: shows city name\n" +
              "condition: shows weather condition\n" +
              "temperature: shows temperature\n" +
              "humidity: shows humidity\n" +
              "wind: shows wind\n" +
              "new: asks user for a new city\n" +
              "update: updates weather information\n")

    def command_input(self):
        """Asks the user for a command"""
        command = input("Enter a command ('help' to show list of commands): ")

        if command == "city":
            self._serial_port.write([2])

        elif command == "condition":
            self._serial_port.write([3])

        elif command == "temperature":
            self._serial_port.write([4])

        elif command == "humidity":
            self._serial_port.write([5])

        elif command == "wind":
            self._serial_port.write([6])

        elif command == "new":
            self._weather_info.set_city()

        elif command == "update":
            self.update()

        elif command == "help":
            self.help()

        else:
            print("Invalid command")


if __name__ == "__main__":
    weather_info = WeatherInfo()
    serial_port = WeatherSerialPort()
    controller = WeatherController(weather_info, serial_port)
    
    while True:
        controller.command_input()
