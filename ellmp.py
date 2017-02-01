#!/usr/bin/python

# Postprocessing module for lammps output averaging:
#   - Retrieves average properties computed by avlmpy.py
#   - Computes elastic constants in GPa
#
# Last modified: May  6  2015
#

import numpy as np 

def cs(avars, nsteps, T, path, pathT, split):
    """ Compute elastic constants, C11, C12 and C44. """
    # Read averaged properties for variables in avars
    # for chosen steps of simulations in nsteps.    
    if split == 'n':
        data = {}
        resC = []
        with open(pathT + 'av_res.txt', 'r') as fp:
            lines = fp.readlines()
            # Extract bottom nsteps lines as a dictionary
            data0 = dict.fromkeys(lines[-nsteps-1], [])
            data = dict.fromkeys(lines[-nsteps-1], [])
            tmp0 = np.array(lines[-nsteps].split(" "), ndmin=2)
            tmp = np.array(lines[-1].split(" "), ndmin=2)
            for jk in range(len(avars)):
                data0[avars[jk]] = tmp0[0][jk]
                data[avars[jk]] = tmp[0][jk]
        # Generate variables and compute the constants
		# Temperature, K
		T = float(data0['T'])
        resC.append(str(T) + ',') 
		# Average pressures pij [bar] and system dimensions lj
		# Initial dimensions: lj0, final: lj [Angstroms]
		pxx0 = float(data0['pxx'])
        pxx  = float(data['pxx'])
        lx0 = float(data0['lx'])
        lx = float(data['lx'])
        ly0 = float(data0['lx'])
        ly = float(data['lx'])
        pyz0 = float(data0['pxy'])
        pyz  = float(data['pxy'])
        yz0 = float(data0['xy'])
        yz = float(data['xy'])
        lz0 = float(data0['lx'])    

		# Elastic constants in GPa
		# Append to result list with temperatures
        # C11
        C11 =-(pxx-pxx0)/((lx-lx0)/lx0)*1.0e-4
        resC.append(str(C11) +',')
        # C12
        C12 = -(pxx-pxx0)/((ly-ly0)/ly0)*1.0e-4
        resC.append(str(C12) + ',')
        # C44
        C44 = -(pyz-pyz0)/((yz-yz0)/lz0)*1.0e-4
        resC.append(str(C44))
        
		# Save the results
        with open(path+'res_Cs.txt', 'a+') as fr:
            resC.append('\n') 
            fr.write(''.join(resC)) 
    elif split == '3n':
        subdir = ['x', 'y', 'yz']
        resC = []
        for sub in subdir:            
            pathsub = pathT + sub + '/'
            data = {} 
            with open(pathsub + 'av_res.txt', 'r') as fp:
                lines = fp.readlines()
                # Extract bottom nsteps lines as a dictionary
                data0 = dict.fromkeys(lines[-nsteps-1], [])
                data = dict.fromkeys(lines[-nsteps-1], [])
                tmp0 = np.array(lines[-nsteps].split(" "), ndmin=2)
                tmp = np.array(lines[-1].split(" "), ndmin=2)
                for jk in range(len(avars)):
                    data0[avars[jk]] = tmp0[0][jk]
                    data[avars[jk]] = tmp[0][jk]
            # Generate variables and compute the constants
        	# Temperature, K
			T = float(data0['T'])
			# Pressures, pij in [bar]
			# System dimensions, initial: lj0 and final: lj [Angstroms]
            if sub=='x':
                pxx0 = float(data0['pxx'])
                pxx  = float(data['pxx'])
                lx0 = float(data0['lx'])
                lx = float(data['lx'])
                # C11
                C11 =-(pxx-pxx0)/((lx-lx0)/lx0)*1.0e-4
                # Append the temperature and C11
                resC.append(str(T) + ',') 
                resC.append(str(C11) +',')
            elif sub=='y':
                pxx0 = float(data0['pxx'])
                pxx  = float(data['pxx'])
                ly0 = float(data0['ly'])
                ly = float(data['ly'])
                # C12
                C12 = -(pxx-pxx0)/((ly-ly0)/ly0)*1.0e-4
                resC.append(str(C12) + ',')
            elif sub=='yz':
                pyz0 = float(data0['pyz'])
                pyz  = float(data['pyz'])
                yz0 = float(data0['yz'])
                yz = float(data['yz'])
                lz0 = float(data0['lz'])    
                # C44
                C44 = -(pyz-pyz0)/((yz-yz0)/lz0)*1.0e-4
                resC.append(str(C44))
        with open(path+'res_Cs.txt', 'a+') as fr:
			# Write the result
            resC.append('\n') 
            fr.write(''.join(resC)) 

def elprops(path, filename):
    """ Compute elastic properties from elastic constants. """

    ## Load the data stored in path/filename
    data = np.loadtxt(path + filename, delimiter=',')
    T = data[0:,0]
    C11 = data[0:,1]
    C12 = data[0:,2]
    C44 = data[0:,3]

    ## Compute and save elastic properties, all in GPa
    # Bulk modulus
    B = (C11+2.0*C12)/3.0
    # Shear moduli
    GV = (C11-C12+3.0*C44)/5.0
    GR = 5.0*np.divide((np.multiply((C11-C12),C44)),(3.0*(C11-C12)+4.0*C44))
    # Young's modulus
    EV = 9.0*np.divide(np.multiply(B,GV),(3.0*B+GV)) 
    ER = 9.0*np.divide(np.multiply(B,GR),(3.0*B+GR))
    # Poisson ratio
    nuV = np.divide((3.0*B-GV),(2.0*(3.0*B+GV)))
    nuR = np.divide((3.0*B-GR),(2.0*(3.0*B+GR)))
    # Save
    np.savetxt(path+'resB.txt', np.dstack((T,B))[0][0:], delimiter=',')
    np.savetxt(path+'resGV.txt', np.dstack((T,GV))[0][0:], delimiter=',')
    np.savetxt(path+'resGR.txt', np.dstack((T,GR))[0][0:], delimiter=',')
    np.savetxt(path+'resEV.txt', np.dstack((T,EV))[0][0:], delimiter=',')
    np.savetxt(path+'resER.txt', np.dstack((T,ER))[0][0:], delimiter=',')
    np.savetxt(path+'resnuV.txt', np.dstack((T,nuV))[0][0:], delimiter=',')
    np.savetxt(path+'resnuR.txt', np.dstack((T,nuR))[0][0:], delimiter=',')

