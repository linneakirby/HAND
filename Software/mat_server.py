from flask import Flask
import pressure_mat_posture as pmp
import matplotlib.pyplot as plt

app = Flask(__name__)

# @app.route('/helloarduino')
# def helloHandler():
#     mat.get_matrix()
#     fig, ax = plt.subplots(figsize=(5,5))
#     plt.ion()
#     p_dict = pmp.execute_instructions(mat.Values, fig)
#     plt.show()
#     return p_dict.get("a")
#     # return create_actuator_dict()

# def create_actuator_dict():
#     actuators = list()
#     actuators.append((True, .8)) #index
#     actuators.append((True, .4)) #pinky
#     actuators.append((False, 0.0)) #wrist
#     actuators.append((False, 0.0)) #thumb
#     return actuators

# def main():
#     global mat
#     mat = pmp.Mat(pmp.get_port())
#     app.run(host='0.0.0.0', port=8090)

# if __name__ == '__main__':
#     main()

# ******************** juliette's nonsense **************************************

mat = pmp.Mat(pmp.get_port())

@app.route('/helloarduino')
def sendDataToArduino():
    mat.get_matrix()
    p_dict = pmp.execute_instructions(mat.Values, None)
    return p_dict.get("a")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)
