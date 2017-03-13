"""
Arduino Uno - Raspberry Pi Weather Forecast

This Python script gathers weather data from the Internet using the
PyOWM API. This data is sent to the Arduino Uno through serial port,
then displayed on the LCD screen. This script also tells the Arduino Uno
which data to display. Command line is used as input.

Commands:
show [data] : Shows the specified data
  data : data to be shown
    city	City name
    cond	Weather condition
    temp	Temperature
    hum		Humidity
    wind	Wind speed and direction

get [city] : Gets forecast data from the specified city
  city : A city

update : Updates current city's weather forecast
exit : Exits program
help : Shows a list of commands

External modules required:
- PyOWM
- PySerial
"""

import pyowm, serial, time, sys, re
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
        
        # Stores forecast data in the following format:
        # [City, Condition, Temperature, Humidity, Wind]
        self._forecast_data = [] 

    def get_city(self):
        """
        Returns the city
        """
        return self._city

    def set_city(self, city=None):
        """
        Prompts the user for a new city
        
        Parameters:
        city: a city
        """
        if not city:
            self._city = input("Enter a city: ") + '\0'
        else:
            self._city = city + '\0'

        try:
            self._forecast=self._owm.weather_at_place(self._city).get_weather()
            print("City found")
        except:
            print("City not found")

    def download_forecast_data(self):
        """Downloads forecast data from PyOWM API"""
        print("Updating...")
        
        try:
            condition = self._forecast.get_status() + '\0'

            # temp in C and F
            temp = str(int(self._forecast.get_temperature("celsius")["temp"]))\
                + " C / " + \
                str(int(self._forecast.get_temperature("fahrenheit")["temp"]))\
                + " F\0"

            humidity = str(self._forecast.get_humidity()) + " %\0" 

            # wind direction and speed
            wind = str(int(self._forecast.get_wind()["deg"])) + " deg, " + \
                str(int(self._forecast.get_wind()["speed"]))[0:3] + " kmh\0"
            
            self._forecast_data = [self._city, condition, temp, humidity, wind]

        except: # Error gathering data
            print("Error")
            self._forecast_data = [self._city, "None", "None", "None", "None"]

    def get_forecast_data(self):
        """
        Returns forecast data
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
    # command regex
    SHOW = re.compile("^\s*show\s*(city|temp|cond|hum|wind|.*)\s*$")
    GET_CITY = re.compile("^\s*get\s*(.*)\s*$")
    UPDATE = re.compile("^\s*update\s*$")
    EXIT = re.compile("^\s*exit\s*$")
    HELP = re.compile("^\s*help\s*$")

    def __init__(self, weather_info, serial_port):
        """
        Parameters:
        weather_info: A WeatherInfo object. Stores weather info.
        serial_port: A WeatherSerialPort object. Serial port where the
                     Arduino Uno is connected
        """
        self._weather_info = weather_info
        self._serial_port = serial_port.get_serial_port()

    def command_input(self):
        """Asks the user for a command"""
        command = input("Enter a command (\"help\" for list of commands): ")

        if self.SHOW.match(command): # show
            if self._weather_info.get_city(): # City exists
                self.show(command)
            else: # City doesn't exist
                print("No specified city. Use \"get [city]\" command.")
                      
        elif self.GET_CITY.match(command): # get
            self.get(command)

        elif self.UPDATE.match(command): # update
            if self._weather_info.get_city(): # City exists
                self.update()
            else: # City doesn't exist
                print("No specified city. Use \"get [city]\" command.")

        elif self.EXIT.match(command): # exit
            self.terminate()

        elif self.HELP.match(command): # help
            self.help()

        else:
            print("Invalid command. Enter \"help\" for a list of commands")

    def show(self, command):
        """
        Parses the show command and shows the specified data

        Parameters:
        command: command entered by the user
        """
        if self.SHOW.match(command).group(1) == "city": # city
            self._serial_port.write([0])

        elif self.SHOW.match(command).group(1) == "cond": # condition
            self._serial_port.write([1])

        elif self.SHOW.match(command).group(1) == "temp": # temperature
            self._serial_port.write([2])

        elif self.SHOW.match(command).group(1) == "hum": # humidity
            self._serial_port.write([3])

        elif self.SHOW.match(command).group(1) == "wind": # wind
            self._serial_port.write([4])

        else:
            print("show [data]\n" +
                  "  data : city, cond, temp, hum, wind")

    def get(self, command):
        """
        Parses the get command and gets forecast data for the
        specified city

        Parameters:
        command: command entered by user
        """
        city = self.GET_CITY.match(command).group(1)
        if city:
            self._weather_info.set_city(city)
            self.update()
        else:
            print("get [city]\n" +
                  "  city : A city")

    def update(self):
        """Updates forecast data and sends it to the Arduino Uno"""
        self._weather_info.download_forecast_data()
        forecast_data = self._weather_info.get_forecast_data()

        # Tells Arduino Uno that update process is about to start
        self._serial_port.write([5])

        for data in forecast_data: # Sends data
            self._serial_port.write(data.encode())

        self._serial_port.write([0]) # Displays new city's name
        print("Update complete")

    def terminate(self):
        """Terminates the script and the sketch"""
        self._serial_port.write([6])
        print("Terminating")
        sys.exit(0)

    def help(self):
        """Displays commands"""
        print("\nArduino Pi Weather Forecast Commands\n\n" +
              "show [data] : Shows the specified data\n" +
              "  data : data to be shown\n" +
              "    city\tCity name\n" +
              "    cond\tWeather condition\n" +
              "    temp\tTemperature\n" +
              "    hum\t\tHumidity\n" +
              "    wind\tWind speed and direction\n\n" +
              "get [city] : Gets forecast data from the specified city\n" +
              "  city : A city\n\n" +
              "update : Updates current city's weather forecast\n" +
              "exit : Exits program\n" +
              "help : Shows a list of commands\n")


if __name__ == "__main__":
    serial_port = WeatherSerialPort()
    weather_info = WeatherInfo()
    controller = WeatherController(weather_info, serial_port)

    weather_info.set_city() # Asks the user for a city

    if weather_info.get_city():
        controller.update()
    else:
        print("No specified city. Use \"get [city]\" command.")

    while True:
        controller.command_input()
        
