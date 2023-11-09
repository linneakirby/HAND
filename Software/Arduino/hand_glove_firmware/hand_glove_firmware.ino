/*
  HAND glove firmware
  Linnea Kirby
*/

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <tuple>

ESP8266WiFiMulti WiFiMulti;

// if using home network
const char* NETWORK = "THE DANGER ZONE";
const char* PASSWORD = "allhailqueennyxie";
const char* HTTP = "http://192.168.0.15:8090/hand";


// if using local network
//const char* NETWORK = "ALTIMA_MESH-F19FC8";
//const char* PASSWORD = "92f19fc8";
//const char* HTTP = "http://192.168.11.3:8090/hand";

float *values = new float[4]; //4 ints representing actuators in the order {INDEX, LEFT, WRIST, RIGHT}
HTTPClient http;

void setup() {
  // Initialize the LED_BUILTIN pins as an output
  pinMode(5, OUTPUT);  //INDEX
  pinMode(14, OUTPUT); // LEFT
  pinMode(12, OUTPUT); // WRIST   
  pinMode(4, OUTPUT); // RIGHT

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

void getWifiConnection(){
  if ((WiFiMulti.run() == WL_CONNECTED)) {

    WiFiClient client;

    Serial.print("[HTTP] begin...\n");
    if (http.begin(client, HTTP)) {  // HTTP


      Serial.print("[HTTP] GET...\n");
      // start connection and send HTTP header
      int httpCode = http.GET();

      // httpCode will be negative on error
      if (httpCode > 0) {
        // HTTP header has been send and Server response header has been handled
        Serial.printf("[HTTP] GET... code: %d\n", httpCode);

        // file found at server
        if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
          Serial.printf("Connection successful!");
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

// get actuator activation instructions from Flask server
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

int findNextSpace(String s){
  int index = s.indexOf(' ');
  //Serial.println("Looking at: " + s);
  if (index == -1){ // no spaces!
    return 0;
  }
  Serial.println("Returning: " + String(index));
  return index;
}

//parse the first int from a String of unknown length
float getFloat(String target){
  int index = findNextSpace(target);
  if (index == 0){ // must only be an int
    //Serial.println("Adding to values: " + target);
    return target.toFloat();
  }
  else{ //otherwise you've found the end of the int
    //Serial.println("Adding to values: " + target.substring(0, index));
    return target.substring(0, index).toFloat();
  }
}

// split instructions from payload into 4 floats (representing intensity for each actuator)
float *splitInstructions(String instructions, float values[4]){
  int r=0;
  int t=0;

  for(int i=0; i<instructions.length(); i++){
    if(instructions.charAt(i) == ' '){
      values[t] = instructions.substring(r,i).toFloat();
      r = (i+1);
      t++;
     }
  }
//  for(int k=0; k<t; k++){
//  Serial.println(values[k]);
//  }
  
  return values;
}

// let's keep things human-readable!
int convertSymbolToPin(char symbol){
  if (symbol == 'i'){ //105
    return 5;
  }
  if (symbol == 'l'){ //108
    return 14;
  }
  if (symbol == 'w'){ //119
    return 12;
  }
  if (symbol == 'r'){ //114
    return 4;
  }
  return 0; //invalid symbol
}

void activateActuator(int actuator, float intensity=HIGH){
  int a = convertSymbolToPin(char(actuator));
  if(intensity > 0){
    digitalWrite(a, HIGH);
  }
}

// the loop function runs over and over again forever
void loop() {
  // wait for WiFi connection
  getWifiConnection();

  delay(5000);

  // reset actuators
  turnActuatorsOff();

  // find actuators to activate
  values = splitInstructions(getInstructions(), values);
  Serial.println(String(values[0]));
  Serial.println(String(values[1]));
  Serial.println(String(values[2]));
  Serial.println(String(values[3]));

  //order is always {INDEX, LEFT, WRIST, RIGHT}
  activateActuator(convertSymbolToPin('i'), values[0]);
  activateActuator(convertSymbolToPin('l'), values[1]);
  activateActuator(convertSymbolToPin('w'), values[2]);
  activateActuator(convertSymbolToPin('r'), values[3]);

}
