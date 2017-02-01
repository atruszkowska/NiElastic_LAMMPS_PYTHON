#!/usr/bin/python

# Visualization module
# Last modified: May 6 2015
#

import matplotlib.pyplot as plt
import numpy

def vis_cs(path, filename):
    """ Plot elastic constants as a function of temperature. """
    # Experimental data
    Te = [0.0, 20.0, 320.0, 360.0, 420.0, 460.0, 520.0, 560.0, 620.0, 660.0, 760.0]
    C11e = [261.2, 261.2, 249.7, 247.7, 244.3, 241.9, 238.1, 235.2, 230.9, 228.2, 223.2]
    C12e = [150.8, 150.8, 149.9, 149.9, 149.5, 149.3, 148.7, 148.4, 147.9, 147.8, 146.4]
    C44e = [131.7, 131.7, 122.8, 121.3, 119.0, 117.5, 115.2, 113.5, 110.9, 109.3, 105.8]

    # Statics data
    Ts = [0.0]
    C11s = [246.55]
    C12s = [147.34]
    C44s = [104.51]

    # Load the data stored in path/res_Cs.txt
    data = numpy.loadtxt(path + filename, delimiter=',')    
    T = data[0:,0]
    C11 = data[0:,1]
    C12 = data[0:,2]
    C44 = data[0:,3]

    # C11 plot
    plt.figure(1)
    plt.plot(T,C11,'ro-', Te, C11e, 'bo', Ts, C11s, 'rs', markersize=10)
    plt.xlabel('T, K')
    plt.ylabel('C11, GPa')

    # C12 plot
    plt.figure(2)
    plt.plot(T, C12, 'bv-', Te, C12e, 'bo', Ts, C12s, 'rs', markersize=10)
    plt.xlabel('T, K')
    plt.ylabel('C12, GPa')

    # C44 plot
    plt.figure(3)
    plt.plot(T, C44, 'gs-', Te, C44e, 'bo', Ts, C44s, 'rs', markersize=10)
    plt.xlabel('T, K')
    plt.ylabel('C44, GPa')


    plt.show()

