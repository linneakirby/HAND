# Standard libraries
import sys
import datetime

# Third-party libraries
import matplotlib.pyplot as plt
import numpy as np
import serial.tools.list_ports
np.set_printoptions(threshold=sys.maxsize)

# Default parameters
ROW_SIZE = 48  # Rows of the sensor
COL_SIZE = 48  # Columns of the sensor
DEFAULT_PORT = '/dev/cu.usbmodem104742601'
FIG_PATH = './Results/correction_'+datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")+'.png'

def get_port():
    # This is how serial ports are organized on macOS.
    # You may need to change it for other operating systems.
    print("Getting ports")
    ports = list(serial.tools.list_ports.grep("\/dev\/cu.usbmodem[0-9]{9}"))
    if (ports):
        print("Using port ")
        print(ports[0])
        return ports[0].device
    return None

def ndarray_to_2darray(nda, preserve_values=True, r=ROW_SIZE, c=COL_SIZE):
    two_d_array = np.zeros((r, c))
    for i in range(c):
        tmp = ""
        for j in range(r):
            if(preserve_values):
                tmp = int(nda[i][j])
                two_d_array[i][j] = tmp
            else:
                if(int(nda[i][j]) != 0):
                    two_d_array[i][j] = 1
    return two_d_array

# based off of http://hyperphysics.phy-astr.gsu.edu/hbase/cm.html
def calculate_cop(pv_dict):
    cop = [0,0]

    for k in pv_dict.keys():
        cop[0] = cop[0] + k[0]*pv_dict.get(k)
        cop[1] = cop[1] + k[1]*pv_dict.get(k)
        #print("MULTIPLIED BY: ", pv_dict.get(k))
        #print("COP IS NOW: ", cop[0], ",", cop[1])

    for i in range(2):
        s = sum(pv_dict.values())
        if s == 0:
            cop[i] = 0
        else:
            cop[i] = cop[i]/sum(pv_dict.values())

    #print("COP IS RETURNING AS: ", cop[0], ",", cop[1])
    return cop

def create_vector(start, end):
    return (end[0]-start[0], end[1]-start[1])

def get_filepath():
    return './Results/correction_'+datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")+'.png'

def get_palette(name):
    if(name == "color"):
        return {
            "label_edge": 'gray',
            "label0_color": '#cea2fd',
            "label1_color": '#ffb07c',
            "rcop_color": '#fc824a',
            "lcop_color": '#5d21d0',
            "icop_color": 'lime',
            "ccop_color": '#fedf08',
            "cop_edge": 'black',
            "vector_color": 'red',
            "vector_edge": 'black'
        }
    elif(name == "bw"):
        return {
            "label_edge": '#cccccc',
            "label0_color": '#dddddd',
            "label1_color": '#dddddd',
            "rcop_color": '#767676',
            "lcop_color": '#767676',
            "icop_color": '#767676',
            "ccop_color": '#767676',
            "cop_edge": '#474545',
            "vector_color": 'orangered',
            "vector_edge": 'orangered'
        }
    elif(name == "bwc"):
        return {
            "label_edge": '#cccccc',
            "label0_color": '#dddddd',
            "label1_color": '#dddddd',
            "rcop_color": '#767676',
            "lcop_color": '#767676',
            "icop_color": '#cea2fd',
            "ccop_color": '#ffb07c',
            "cop_edge": 'black',
            "vector_color": 'red',
            "vector_edge": 'darkorange'
        }
    else:
        return {
            "label_edge": 'gray',
            "label0_color": '#cea2fd',
            "label1_color": '#ffb07c',
            "rcop_color": '#fc824a',
            "lcop_color": '#5d21d0',
            "icop_color": 'lime',
            "ccop_color": '#fedf08',
            "cop_edge": 'black',
            "vector_color": 'red',
            "vector_edge": 'black'
        }

def generate_scatter_plot(kmeans, coords_only, rcop, lcop, ideal_cop, actual_cop, figure, ax, r=ROW_SIZE, c=COL_SIZE, fp=get_filepath(), p="color"):
    # ax.invert_yaxis()

    palette = get_palette(p)

    index = 0
    for x in range(c): #x
        for y in range(r): #y
            if [x, y] in coords_only:
                #print("looking at: "+str(col)+","+str(row))
                if kmeans.labels_[index] == 0:
                    plt.scatter(
                        x, y,
                        s=40, c=palette.get("label0_color"),
                        marker='.', edgecolor=palette.get("label_edge")
                    )
                if kmeans.labels_[index] == 1:
                    plt.scatter(
                        x, y,
                        s=40, c=palette.get("label1_color"),
                        marker='.', edgecolor=palette.get("label_edge")
                    )
                index+=1

    # add center of pressure markers
    plt.scatter(
        rcop[0], rcop[1],
        s=60, c=palette.get("rcop_color"),
        marker='>', edgecolor=palette.get("cop_edge"), label='right CoP'
        )
    plt.scatter(
        lcop[0], lcop[1],
        s=60, c=palette.get("lcop_color"),
        marker='<', edgecolor=palette.get("cop_edge"), label='left CoP'
        )
    plt.scatter(
        ideal_cop[0], ideal_cop[1],
        s=60, c=palette.get("icop_color"),
        marker='^', edgecolor=palette.get("cop_edge"), label='ideal CoP'
        )
    plt.scatter(
        actual_cop[0], actual_cop[1],
        s=60, c=palette.get("ccop_color"),
        marker='v', edgecolor=palette.get("cop_edge"), label='current CoP'
        )

    # add vector
    dx = ideal_cop[0] - actual_cop[0]
    dy = ideal_cop[1] - actual_cop[1]
    plt.arrow(actual_cop[0], actual_cop[1], dx, dy, facecolor=palette.get("vector_color"), edgecolor=palette.get("vector_edge"), length_includes_head=True, head_width = .9, width= .3)

    # add legend
    ax.legend()
    #plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=5)

    #plt.legend(scatterpoints=1)
    # plt.grid()
    plt.draw()
    plt.savefig(fp)
    #plt.show()
    figure.canvas.draw()
    figure.canvas.flush_events()