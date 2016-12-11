/*
Arduino Uno - Raspberry Pi Weather Forecast

An LCD screen is connected to the Arduino Uno, which will display 
the current weather forecast. This sketch will gather data from
the Raspberry Pi through the serial port. This data will be gathered
by the Raspberry Pi through the PyOWM Python script.
*/

#include <LiquidCrystal.h>

LiquidCrystal lcd(2, 3, 4, 5, 6, 7); // LCD

// The following string array will contain the data labels
String dataLabels[5] = {"City: ", "Condition: ", "Temp: ", 
                       "Humidity: ", "Wind: "};

// The following string array will contain the forecast data
String forecastData[5] = {"None", "None", "None", "None", "None"};

int command = 0; // If the value is 1, the Arduino Uno will
                 // update the forecast data. Otherwise, it
                 // will display the data associated with the
                 // value


void setup() {
  // Starts serial communication and the LCD
  Serial.begin(115200);
  Serial.setTimeout(10);
  lcd.begin(16, 2);
}

void loop() {
  if (Serial.available()) {
    // Reads the incoming byte. If the byte is 1, update the
    // forecast data. If the byte is 2-6, display the corresponding
    // forecast data.
    command = Serial.read();
    if (command == 5) {
      // Updates forecast data
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Updating...");
      update();
    }
    else if (command >= 0 && command <= 4) {
      // Displays data
      displayData(command);
    }
    else if (command == 6) {
      // Clears LCD
      lcd.clear();
    }
  }
}

void update() {
  // Updates the forecast data
  int index = 0;
  
  while (index < 5) {
    if (Serial.available()) {
      forecastData[index] = Serial.readString();
      index++;
    }
  }
}

void displayData(int command) {
  // Displays data corresponding to the byte sent by the
  // Raspberry Pi (0-4).
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(dataLabels[command]);
  lcd.setCursor(0, 1);
  lcd.print(forecastData[command]);
}
