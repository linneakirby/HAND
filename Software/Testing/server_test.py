from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.route('/hand')
    def helloHandler():
        return create_actuator_dict()
    
    return app

def create_actuator_dict():
    actuators = list()
    actuators.append((True, .8)) #index
    actuators.append((True, .4)) #left
    actuators.append((False, 0.0)) #wrist
    actuators.append((False, 0.0)) #right
    return "hello"

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8090)