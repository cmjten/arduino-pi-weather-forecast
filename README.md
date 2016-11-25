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
- city : shows city name
- condition : shows weather condition
- temperature : shows temperature
- humidity : shows humidity
- wind : shows wind speed and direction
- new : asks user for a new city
- update : updates weather information ands sends data to Arduino Uno
- help : command list

### Controls (weather_ps3.py)
- Left and right buttons to scroll through forecast data
- Circle button to send data from Raspberry Pi to the Arduino Uno
- Square button to prompt user for a new city

### Images

<img src=https://github.com/cmjten/arduino-pi-weather-forecast/blob/master/setup_images/arduino_pi_weather_forecast_setup.png width=600/>

<img src=https://github.com/cmjten/arduino-pi-weather-forecast/blob/master/setup_images/arduino_pi_weather_forecast.png width=600/>
