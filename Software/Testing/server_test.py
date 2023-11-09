from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.route('/hand')
    def helloHandler():
        return dict_to_string(create_actuator_dict())
    
    return app

def dict_to_string(d):
    s = ""
    for item in d:
        s = s + str(item) + " "
    return s

def create_actuator_dict():
    actuators = list()
    actuators.append(0.8) #index
    actuators.append(0.4) #left
    actuators.append(0.0) #wrist
    actuators.append(0.0) #right
    return actuators

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8090)