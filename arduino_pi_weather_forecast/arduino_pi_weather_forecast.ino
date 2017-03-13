/*
Arduino Uno Weather Forecast

This sketch displays weather forecast gathered by a computer
through the PyOWM module.
*/
#include <LiquidCrystal.h>

LiquidCrystal lcd(2, 3, 4, 5, 6, 7); // LCD
String dataLabels[5] = {"City: ", "Condition: ", "Temp: ", 
                        "Humidity: ", "Wind: "};
String forecastData[5] = {"None", "None", "None", "None", 
                          "None"};
                 
void setup() {
  Serial.begin(9600);
  lcd.begin(16, 2);
}

void loop() {
  if (Serial.available()) {
    // Reads the incoming byte. If the byte is 1, update the
    // forecast data. If the byte is 2-6, display the 
    // corresponding forecast data.
    int command = Serial.read();
    switch (command) {
      case 0:
      case 1:
      case 2:
      case 3:
      case 4: // Display data at indices 0-4
        displayData(command);
        break;
        
      case 5: // Update
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Updating...");
        updateData();
        break;

      case 6: // Clear lcd
        lcd.clear();
        break;
    }
  }
}

void updateData() {
  // Updates the forecast data
  int index = 0;
  while (index < 5) {
    if (Serial.available()) {
      forecastData[index] = Serial.readStringUntil('\0');
      index++;
    }
  }
}

void displayData(int command) {
  // Displays data corresponding to the byte received
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(dataLabels[command]);
  lcd.setCursor(0, 1);
  lcd.print(forecastData[command]);
}
