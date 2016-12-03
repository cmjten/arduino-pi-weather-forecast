# Arduino Uno - Raspberry Pi Weather Forecast

The Raspberry Pi gathers weather data from the Internet through a Python script. This weather data is then sent
to the Arduino Uno and displayed on the 16x2 LCD screen. This project comes with two Python scripts: weather_commands.py
for command line input and weather_ps3.py for PS3 controller input.

###[Demo Video (PS3 Controller)](https://vid.me/Iex0)

### Components
- Raspberry Pi 3
- Arduino Uno
- 220 Ohm Resistor
- 16x2 LCD screen
- PS3 Controller (optional)

### Commands (weather_commands.py)
- show city : Shows city name
- show cond : Shows weather condition
- show temp : Shows temperature
- show hum : Shows humidity
- show wind : Shows wind speed and direction
- get [city] : Gets forecast data from the specified city
- update : Updates current city's weather forecast
- exit : Exits program
- help : Shows a list of commands

### Controls (weather_ps3.py)
- Left button : Scroll left
- Right button : Scroll right
- Circle button : Update data
- Square button : Get new city
- Playstation button : Exit

### Images

<img src=https://github.com/cmjten/arduino-pi-weather-forecast/blob/master/setup_images/arduino_pi_weather_forecast_setup.png width=600/>

<img src=https://github.com/cmjten/arduino-pi-weather-forecast/blob/master/setup_images/arduino_pi_weather_forecast.png width=600/>
