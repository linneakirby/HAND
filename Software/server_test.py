from flask import Flask

app = Flask(__name__)

@app.route('/helloarduino')
def helloHandler():
    return create_actuator_dict()

def create_actuator_dict():
    actuators = list()
    actuators.append((True, .8)) #index
    actuators.append((True, .4)) #pinky
    actuators.append((False, 0.0)) #wrist
    actuators.append((False, 0.0)) #thumb
    return actuators


app.run(host='0.0.0.0', port=8090)