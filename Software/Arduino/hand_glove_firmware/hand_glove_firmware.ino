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

//USER-CHANGEABLE VARIABLES
const bool LEFT_HAND = false;
const bool LOCAL_NETWORK = true;
const bool TWO_ACTUATORS = true;

const char* NETWORK;
const char* PASSWORD;
const char* HTTP_LEFT;
const char* HTTP_RIGHT;

float *values = new float[4]; //4 ints representing actuators in the order {INDEX, LEFT, WRIST, RIGHT}
HTTPClient http;
int httpCode;

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

  setupWifi();
}

void setupWifi(){
  //if using local network
  if(LOCAL_NETWORK == true) {
    NETWORK = "ALTIMA_MESH-F19FC8";
    PASSWORD = "92f19fc8";
    HTTP_LEFT = "http://192.168.11.2:8090/lhand";
    HTTP_RIGHT = "http://192.168.11.2:8090/rhand";
  }
  else{ //// if using home network
    NETWORK = "THE DANGER ZONE";
    PASSWORD = "allhailqueennyxie";
    HTTP_LEFT = "http://192.168.11.2:8090/lhand";
    HTTP_RIGHT = "http://192.168.11.2:8090/rhand";
  }
  
  WiFi.mode(WIFI_STA);
  WiFiMulti.addAP(NETWORK, PASSWORD);
}

void getWifiConnection(){
  const char* httpHand;
  if(LEFT_HAND == true){ //left hand
    httpHand = HTTP_LEFT;
  }
  else { //right hand
    httpHand = HTTP_RIGHT;
  }

  if (WiFiMulti.run() == WL_CONNECTED) {

    WiFiClient client;

    Serial.print("[HTTP] begin...\n");
    if (http.begin(client, httpHand)) {

      for (size_t i = 0; i < 3; i++) {
        Serial.printf("[HTTP] GET (%d)...\n", i+1);
        // start connection and send HTTP header
        httpCode = http.GET();
  
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
  Serial.println("symbol is: " + symbol);
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

//pulse target actuator on and off
void pulseActuator(int actuator){
  digitalWrite(actuator, HIGH);
  delay(100);
  digitalWrite(actuator, LOW);
  delay(200);
}

//pulse an actuator according to intensity
void activateActuator(int actuator, float intensity=HIGH){
  //Serial.println("activating pin " + String(actuator));
  // if(intensity > 0.66){ //highest intensity
  //   pulseActuator(actuator);
  //   pulseActuator(actuator);
  //   pulseActuator(actuator);
  // }
  // else if(intensity > 0.33){ //mid intensity
  //   pulseActuator(actuator);
  //   pulseActuator(actuator);
  // }
  // else{ //low intensity
  //   pulseActuator(actuator);
  // }
  pulseActuator(actuator);
  pulseActuator(actuator);
  pulseActuator(actuator);
}

//2 actuators
void activate2Actuators(float *v){
  if (values[0] > 0){// index
    activateActuator(convertSymbolToPin('i'), values[0]);
  }
  if (values[2] > 0){// wrist
    activateActuator(convertSymbolToPin('w'), values[2]);
  }
}

//4 actuators
//activate desired actuators in series
void activate4Actuators(float *v){
  if (values[0] > 0){
    if (values[1] > 0){ // index/left pair
      if(values[0] > values[1]){ //more index
        activateActuator(convertSymbolToPin('i'), values[0]);
        activateActuator(convertSymbolToPin('l'), values[1]);
      }
      else{ //more left
        activateActuator(convertSymbolToPin('l'), values[1]);
        activateActuator(convertSymbolToPin('i'), values[0]);
      }
    }
    else{ //index/right pair
      if(values[0] > values[3]){ //more index
        activateActuator(convertSymbolToPin('i'), values[0]);
        activateActuator(convertSymbolToPin('r'), values[3]);
      }
      else{ //more right
        activateActuator(convertSymbolToPin('r'), values[3]);
        activateActuator(convertSymbolToPin('i'), values[0]);
      }
    }
  }
  else{
    if(values[1] > 0){ //wrist/left pair
      if(values[2] > values[1]){ //more wrist
        activateActuator(convertSymbolToPin('w'), values[2]);
        activateActuator(convertSymbolToPin('l'), values[1]);
      }
      else{ //more left
        activateActuator(convertSymbolToPin('l'), values[1]);
        activateActuator(convertSymbolToPin('w'), values[2]);
      }
    }
    else{ //wrist/right pair
      if(values[2] > values[3]){ //more wrist
        activateActuator(convertSymbolToPin('w'), values[2]);
        activateActuator(convertSymbolToPin('r'), values[3]);
      }
      else{ //more right
        activateActuator(convertSymbolToPin('r'), values[3]);
        activateActuator(convertSymbolToPin('w'), values[2]);
      }
    }
  }
}

// the loop function runs over and over again forever
void loop() {
  // wait for WiFi connection
  getWifiConnection();

  delay(250);

  // reset actuators
  turnActuatorsOff();

  // find actuators to activate
  if (httpCode == HTTP_CODE_OK) {
    values = splitInstructions(getInstructions(), values);
  
    //order is always {INDEX, LEFT, WRIST, RIGHT}
    if(TWO_ACTUATORS){
      activate2Actuators(values);
    }
    else {
      activate4Actuators(values);
    }
    
  }
}
