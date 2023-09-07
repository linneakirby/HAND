/*
  HAND glove firmware
*/

int button = 12;
int b2 = 14;
int switchState = 0;
int s2 = 0;
void setup() {
  pinMode(5, OUTPUT);     // Initialize the LED_BUILTIN pin as an output
  pinMode(4, OUTPUT);
}

// the loop function runs over and over again forever
void loop() {
  digitalWrite(5, LOW);   // Turn the LED on (Note that LOW is the voltage level
  digitalWrite(4, LOW);
  switchState = digitalRead(button);
  s2 = digitalRead(b2);
  if (switchState == HIGH) { //pressed
    digitalWrite(5, HIGH);
  } else {
    digitalWrite(5, LOW);
  }
  if (s2 == HIGH){
    digitalWrite(4, HIGH);
  } else {
    digitalWrite(4, LOW);
  }

}

// Struct definition.
struct Array4 {
    int array[4];
};

Array4 splitInstructions(String instructions){
  Array4 values;
  String str = instructions;
  int index = 0;
  // Split the string into substrings
  while (str.length() > 0)
  {
    int index = str.indexOf(' ');
    if (index == -1) // No space found
    {
      instructions[index++] = str;
      break;
    }
    else
    {
      instructions[index++] = str.substring(0, index);
      str = str.substring(index+1);
    }
  }
  return values;
}
