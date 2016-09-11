"""
Arduino Uno - Raspberry Pi Weather Forecast

This Python script will gather weather data from the Internet through
the PyOWM module. This data will be sent to the Arduino Uno through the
serial port, then displayed on the LCD screen. This script will also
tell the Arduino Uno which data to display. A PS3 controller will be used
as input.
"""

import pygame, pyowm, serial, time
import serial.tools.list_ports as serial_list_ports

full_city_name = "Mississauga, CA"  # Name of the city. Default is Mississauga.
forecast_data = []  # This list will contain forecast data in the following
                    # order: [City, Condition, Temperature, Humidity, Wind,
                    # Precipitation]
data_index = 2  # Stores the index of the data to be shown on the LCD. 2 for
                # City, 3 for Condition, 4 for Temperature, 5 for Humidity,
                # 6 for Precipitation
                               
# Sets up serial port
ser_path = serial_list_ports.comports()[0].device  # Gets the first serial port
ser = serial.Serial(ser_path, 9600) 

# Sets up PyOWM
owm = pyowm.OWM("e2d8e6b2a2e79158b76f6d1873d2b145")

# Gets weather at a specified location
forecast = owm.weather_at_place(full_city_name).get_weather()

# Sets up the controller
pygame.init()
controller = pygame.joystick.Joystick(0)
controller.init()

# Pygame mappings for PS3 buttons
left_button = 7
right_button = 5
circle_button = 13
square_button = 15

current_button_state = False  # True if a button is pressed, False otherwise
previous_button_state = False  # Stores the previous button state to prevent
                               # sending multiple signals when the button is
                               # held down

def loop():
    """
    This body of the script. The code here is run in a loop.

    @rtype: None
    """
    for event in pygame.event.get():
        pass

    global circle_button, current_button_state, left_button, \
           previous_button_state, right_button, square_button

    # Gets the current button state and compares it to the previous
    # button state
    current_button_state = controller.get_button(left_button) or \
                           controller.get_button(right_button) or \
                           controller.get_button(circle_button) or \
                           controller.get_button(square_button)
    
    if current_button_state != previous_button_state:
        # Prevents the controller from sending multiple signals when held
        # down by only sending signal when the button switches from a low to
        # high state

        if controller.get_button(left_button):
            # Sends instructions to the Arduino Uno to scroll data to the left
            scroll("left")

        elif controller.get_button(right_button):
            # Sends instructions to the Arduino Uno to scroll data to the right
            scroll("right")

        elif controller.get_button(square_button):
            # Changes the city
            get_new_city()

        elif controller.get_button(circle_button):
            # Updates weather data then send to the Arduino Uno
            gather_data()             
            update()
            
    previous_button_state = current_button_state


def gather_data():
    """
    Gathers the city name, condition, temperature, humidity, and wind, and
    returns a list containing these data.

    @rtype: list[str]
    """
    global forecast, forecast_data, full_city_name
    print("Updating...")

    try:
        # Gathers the city, condition, temperature, humidity, and wind data
        city = full_city_name.split(',')[0]  # Removes the country
        condition = forecast.get_status()
        temp = str(int(forecast.get_temperature("celsius")["temp"])) + \
               " C / " + \
               str(int(forecast.get_temperature("fahrenheit")["temp"])) + \
               " F"
        humidity = str(forecast.get_humidity()) + " %"
        wind = str(int(forecast.get_wind()["deg"])) + " deg, " + \
               str(int(forecast.get_wind()["speed"]))[0:3] + " kmh"
        forecast_data = [city, condition, temp, humidity, wind]
        
    except:
        # When an error occurs, send "None" for every forecast entry
        print("Error")
        forecast_data = ["None", "None", "None", "None", "None"]


def get_new_city():
    """
    Prompts the user for a new city

    @rtype: None
    """
    global forecast, full_city_name
    
    full_city_name = input("Enter a new city: ")
    
    try:
        forecast = owm.weather_at_place(full_city_name).get_weather()
        print("City found")
        
    except:
        # Prints "City not found" when an error occurs
        print("City not found")


def scroll(direction):
    """
    Scrolls through the data in the specified direction

    @type direction: str
    @rtype: None
    """
    global data_index
    
    if direction == "left":
        # Scrolls to the left
        if data_index > 2:
            data_index -= 1

    elif direction == "right":
        # Scrolls to the right
        if data_index < 6:
            data_index += 1

    ser.write([data_index])  # Sends instruction to the Arduino Uno
        

def update():
    """
    Sends the forecast data to the Arduino Uno

    @rtype: None
    """
    global data_index, forecast_data, ser

    ser.write([1])  # Tells the Arduino Uno that update process is
                    # about to start
    
    for data in forecast_data:
        # Sends forecast data to Arduino Uno
        ser.write(data.encode())
        time.sleep(2)

    # Tells the Arduino Uno that the update process is over and to
    # display the new data
    data_index = 2  
    ser.write([data_index])  # Displays the city name after the update
    print("Update complete")


if __name__ == "__main__":
    while True:
        loop()
    


