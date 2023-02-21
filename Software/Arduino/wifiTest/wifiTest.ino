#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  WiFi.begin("sri", "Rayan436");

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting...");
   
  }
  Serial.println("Connected to Wifi Network");

}

void loop() {
  // put your main code here, to run repeatedly:
  if (WiFi.status() == WL_CONNECTED) { //Check WiFi connection status
 
    HTTPClient http;  //Declare an object of class HTTPClient
    http.begin("192.168.1.54", 8082);
 
//    http.begin("http://192.168.1.88:8090/helloesp"); //Specify request destination
 
    int httpCode = http.GET(); //Send the request
 
    if (httpCode > 0) { //Check the returning code
 
      String payload = http.getString();   //Get the request response payload
      Serial.println(payload);             //Print the response payload
 
    }else Serial.println("An error ocurred");
 
    http.end();   //Close connection
 
  }
 
  delay(10000);    //Send a request every 10 seconds
 
  

}
