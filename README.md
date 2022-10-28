# Haptics-Assisted iNversions Device (HAND)
Schematics and firmware for haptics-embedded palmless, fingerless gloves and software for SensingTex pressure mats 

## The Gloves
### Schematics
Schematics for the gloves can be found in the "Technical Docs" folder under "Gloves_battery_schem.png" and "Gloves_battery_bb.png".

<img alt="glove schematics" src="Technical\ Docs/Gloves_battery_schem.png" width="auto" height="auto"/>

### Firmware
Firmware for the gloves can be found in the "Software/Arduino" folder.

## Mat Software
The mat software is written in Python3 and can be found in the "Software" folder as "pressure_mat_posture.py". A list of dependencies can be found in the "requirements.txt" file in the same folder.

### Testing
The mat software can be tested by running the "start" shell script, which allows the user to interact with a preloaded snapshot of the mat output.
