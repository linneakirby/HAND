/*
  HAND glove firmware
  Linnea Kirby
*/

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

ESP8266WiFiMulti WiFiMulti;

// if using home network
const String NETWORK = "THE DANGER ZONE";
const String PASSWORD = "all hailqueen nyxie";

// if using local network
//const String NETWORK = "ALTIMA_MESH-F19FC8";
//const String PASSWORD = "92f19fc8";

int *values = new int[8]; //4 char-int pairs

void setup() {
  // Initialize the LED_BUILTIN pins as an output
  pinMode(5, OUTPUT);  //INDEX   
  pinMode(4, OUTPUT); // RIGHT
  pinMode(14, OUTPUT); // LEFT
  pinMode(12, OUTPUT); // WRIST

  Serial.begin(115200);
  Serial.println();
  Serial.println();
  Serial.println();

  for (uint8_t t = 4; t > 0; t--) {
    Serial.printf("[SETUP] WAIT %d...\n", t);
    Serial.flush();
    delay(1000);
  }
  WiFi.mode(WIFI_STA);
  WiFiMulti.addAP(NETWORK, PASSWORD);
}

// the loop function runs over and over again forever
void loop() {
  // wait for WiFi connection
  getWifiConnection();

  delay(10000);

  // reset actuators
  turnActuatorsOff();

  // find actuators to activate
  values = splitInstructions(getInstructions(), values);

  for (int i=0; i<sizeof(values)-1; i+=2){
    activateActuator(values[i], HIGH);
    //activateActuator(values[i], values[i+1]); //TODO: uncomment this out to add intensities
  }

}

//TODO: add intensities
void activateActuator(int actuator, int intensity=HIGH){
  int a = convertSymbolToPin(char(actuator));
  digitalWrite(a, intensity);
}

// let's keep things human-readable!
int convertSymbolToPin(char symbol){
  if (symbol == 'i'){ //105
    return 5;
  }
  if (symbol == 'r'){ //114
    return 4;
  }
  if (symbol == 'l'){ //108
    return 14;
  }
  if (symbol == 'w'){ //119
    return 12;
  }
  return 0; //invalid symbol
}

void getWifiConnection(){
  if ((WiFiMulti.run() == WL_CONNECTED)) {

    WiFiClient client;

    HTTPClient http;

    Serial.print("[HTTP] begin...\n");
    if (http.begin(client, "http://192.168.11.2:8090/hand")) {  // HTTP


      Serial.print("[HTTP] GET...\n");
      // start connection and send HTTP header
      int httpCode = http.GET();

      // httpCode will be negative on error
      if (httpCode > 0) {
        // HTTP header has been send and Server response header has been handled
        Serial.printf("[HTTP] GET... code: %d\n", httpCode);

        // file found at server
        if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
          Serial.printf("Connection successful!")
          return; // successful!
        }
      } else {
        Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
      }

      http.end();
    } else {
      Serial.printf("[HTTP} Unable to connect\n");
    }
  }
}

String getInstructions(){
  String payload = http.getString(); //INSTRUCTIONS
  Serial.println("Payload: "+ payload);
  return payload;
}

// reset all acctuators
void turnActuatorsOff(){
  digitalWrite(5, LOW);  
  digitalWrite(4, LOW);
  digitalWrite(14, LOW);
  digitalWrite(12, LOW);
}

// turn specified actuator on
void turnActuatorOn(int actuator){
  digitalWrite(actuator, HIGH);
}

int *splitInstructions(String instructions, int values[8]){
  String str = instructions;
  int index = 0;
  // Split the string into substrings
  while (str.length() > 0)
  {
    int index = str.indexOf(' ');
    if (index == -1) // No space found
    {
      instructions.setCharAt(index++, str);
      break;
    }
    else
    {
      instructions.setCharAt(index++, str.substring(0, index);
      str = str.substring(index+1);
    }
  }
  return values;
}
