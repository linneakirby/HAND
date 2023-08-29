# Haptics-Assisted iNversions Device (HAND)
Schematics and firmware for haptics-embedded palmless, fingerless gloves and software for SensingTex pressure mats 

## The Gloves
### Schematics
Schematics for the gloves can be found in the "Technical Docs" folder under "Gloves_battery_schem.png" and "Gloves_battery_bb.png".

<img alt="glove schematics" src="Technical Docs/Gloves_battery_schem.png" width="auto" height="300px"/> <img alt="glove breadboard setup" src="Technical Docs/Gloves_battery_bb.png" width="auto" height="300px"/>

### Firmware
Firmware for the gloves can be found in the "Software/Arduino" folder. In Arduino, the board is considered a "Generic ESP8266 Module" and is part of the "ESP8266 Boards" library.

## Mat Software
The mat software is written in Python3 and can be found in the "Software" folder as "pressure_mat_posture.py". A list of dependencies can be found in the "requirements.txt" file in the same folder.

The software is broken down into several files to create a HAND library:

- Mat.py
  - contains a Mat class which sets up and processes data from the SensingTex mat
- Hands.py
  - contains a Hand and a Hands class which process mat data to find and separate the two hands, determine centers of pressure, create a correction vector, and determine which actuators to activate
- Actuators.py
  - contains an Actuator and an Actuator_manager class which allow for easy actuator setup and interaction
- hand_utils.py
  - contains useful general functions used by other files in the library
- haptic_assisted_inversions_device.py
  - executable file to run the HAND software

### Testing
The mat software can be tested by running the "start" shell script, which allows the user to interact with a preloaded snapshot of the mat output.
