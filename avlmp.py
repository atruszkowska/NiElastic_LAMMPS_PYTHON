#!/usr/bin/python

# Postprocessing module for lammps output averaging:
#   - Retrieves the data from log.lammps and stores as txt 
#   - Performs data averaging using selected approach
#
# Last modified: May  6  2015
#
import subprocess, os, numpy
from scipy import stats

class ChangeDir:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def prc_log(pathT, split):
    """ Process log.lammps data in each subdirectory of pathT. """
    # Saves the data in data_out.txt and info on simulation stages from log.lammps in log.out
    if split == 'n':
        subprocess.call(['log2txt.py log.lammps data_out.txt > log.out'], shell=True, cwd=pathT)
    elif split == '3n':
        subdir = ['x', 'y', 'yz']
        for sub in subdir:
            pathsub = pathT + sub + '/'
            subprocess.call(['log2txt.py log.lammps data_out.txt > log.out'], shell=True, cwd=pathsub)

def imp_data(avars, thermo):
    """ Import data_out.txt as a numeric array and lammps steps in log.out. 

        Process the data and return numeric arrays with target variables."""

    # Load thermo output from data_out.txt
    data = numpy.loadtxt('data_out.txt')
    # Load log info, delete the second row and convert first to int         
    log =[] #numpy.genfromtxt('log.out')        
    #log = map(int, log[0])
    
    # Find indices of avars in thermo
    find = lambda searchlist, elem: [[i for i, x in enumerate(searchlist) if x==e] for e in elem]
    ind = find(thermo, avars)
    # Change 'data' into an array
    data = numpy.array(data)
    # Generate variables from thermo data and return them along with log
    newvars = {}
    for jk in ind:
        newvars[thermo[jk[0]]] = data[:,jk[0]]         
    return newvars, log

def simpav(avars, thermo):
    """ Compute average of all values for each simulation step. """
    # Import thermo data with target variables and log info
    [data, logL] = imp_data(avars, thermo)
    nd = len(data)
    nl = len(logL)
    # Initialize array with results
    meanvar = numpy.zeros((nl-1,nd))
    # Compute mean of variables listed in avars for each simulation step and save them to file
    for ik in range(nl-1):    
        t0 = logL[ik] + 1
        tf = logL[ik+1]
        for jk in range(nd):
            temp = data[avars[jk]]
            meanvar[ik,jk] = numpy.mean(temp[t0-1:tf], axis=0, dtype=numpy.float128)
    # Save to file (.npy binary also an option)
    with open("av_res.txt", "a") as resfile:
        hstr = ' '*30
        resfile.write(hstr.join(avars))
        resfile.write('\n')
        numpy.savetxt(resfile, meanvar)

def moveav(avars, thermo, window):
    """ Moving average averaging. Saves mean over averages. """
    # NOTE: numpy.convolve() option 'valid' makes sure that the
    # average will always be computed from number of datapoints 
    # specified by 'window' - otherwise it will patch missing 
    # entries at the far ends of the data with 0 
    # E.g. - first point (e.g.=1, window=3) average will be 1+0+0=0.333  

    # Import thermo data with target variables and log info
    [data, logL] = imp_data(avars, thermo)
    nd = len(data)
    nl = len(logL)
    # Initialize array with results
    mvavar = numpy.zeros((nl-1,nd))
    # Compute mean of variables listed in avars for each simulation step 
    # and save them to file 
    for ik in range(nl-1):    
        t0 = logL[ik] + 1
        tf = logL[ik+1]
        for jk in range(nd):
            temp = data[avars[jk]]
            weights = numpy.repeat(1.0, window)/window
            mvavar[ik,jk] = numpy.mean(numpy.convolve(temp[t0-1:tf], weights, 'valid'))
    # Save to file (.npy binary also an option)
    with open("av_res.txt", "a") as resfile:
        hstr = ' '*30
        resfile.write(hstr.join(avars))
        resfile.write('\n')
        numpy.savetxt(resfile, mvavar)

def distav(avars, thermo):
    """ Mean of the distribution. Currently using t student distribution. """
    # Import thermo data with target variables and log info
    [data, logL] = imp_data(avars, thermo)
    nd = len(data)
    nl = len(logL)
    # Initialize array with results
    dstavar = numpy.zeros((nl-1,nd))
    # Fit the data for each step to t-student distribution and save the distribution mean    
    for ik in range(nl-1):    
        t0 = logL[ik] + 1
        tf = logL[ik+1]
        for jk in range(nd):
            temp = data[avars[jk]]
            # prm[0] - unknown; prm[1] - mu/mean; prm[2] - sigma/std  
            prm = stats.t.fit(temp[t0-1:tf])
            dstavar[ik,jk] = prm[1]
    # Save to file (.npy binary also an option)
    with open("av_res.txt", "a") as resfile:
        hstr = ' '*30
        resfile.write(hstr.join(avars))
        resfile.write('\n')
        numpy.savetxt(resfile, dstavar)
    
def fitstr(avars, thermo, path, t00, t0, tf0, tf, dirC44, split, sub):
    """ Obtain elastic constants from linear fit of stress/strain curve. """
    # Input:
    # t00, t0 - initial time span
    # tf0, tf - final time span    
    # dirC44 - direction of straining for C44 computation 
    #
	# Comment/uncomment sections of this code for different
	# deformation strategies - currently x and xy
	#
    # Import thermo data with target variables and log info
    [data, logL] = imp_data(avars, thermo)
    nd = len(data)
    # Initial box dimensions
    for jk in range(nd):
        if avars[jk]=='lx':
            temp = data[avars[jk]]
            # prm[0] - unknown; prm[1] - mu/mean; prm[2] - sigma/std  
            prm = stats.t.fit(temp[t00:t0])
            lx0 = prm[1]
#        elif avars[jk]=='ly':
#            temp = data[avars[jk]]
#            # prm[0] - unknown; prm[1] - mu/mean; prm[2] - sigma/std  
#            prm = stats.t.fit(temp[t00:t0])
#            ly0 = prm[1]
        else:
            pass
    # Compute the average temperature during the deformation part
    # saves only the x component for now (in 3n)
    temp = data['T']
    prm = stats.t.fit(temp[tf0:tf])
    T = prm[1]
    # Compute strain
    eta11 = (data['lx']-lx0)/lx0
    #eta12 = (data['lx']-lx0)/lx0
    #eta44 = (data[dirC44]-lx0)/lx0
    # Collect only the deformation part
    eta11 = eta11[tf0:tf]
    #eta12 = eta12[tf0:tf]
    #eta44 = eta44[tf0:tf]
    # Collect the stresses
    p11 = data['pxx']
    p11 = p11[tf0:tf]
    p12 = data['pyy']
    p12 = p12[tf0:tf]
    p44 = data['p'+dirC44]
    p44 = p44[tf0:tf]
    # Fit - collect the slopes (elastic constants)
    if split == 'n':
        coefs = numpy.polyfit(eta11, -p11, 1)
        C11 = coefs[0]*1.0e-4
        coefs = numpy.polyfit(eta11, -p12, 1)
        C12 = coefs[0]*1.0e-4
        coefs = numpy.polyfit(0.5*eta11, -p44, 1)
        C44 = coefs[0]*1.0e-4
        with open(path+'res_CsFit.txt','a+') as fr:
            fr.write(str(T)+','+str(C11)+','+str(C12)+','+str(C44)+'\n')
    elif split == '3n':
        if sub == 'x':
            coefs = numpy.polyfit(eta11, -p11, 1)
            C11 = coefs[0]*1.0e-4
            with open(path+'res_CsFit.txt','a+') as fr:
                fr.write(str(T)+','+str(C11)+',')  
        elif sub == 'y':
            coefs = numpy.polyfit(eta12, -p11, 1)
            C12 = coefs[0]*1.0e-4
            with open(path+'res_CsFit.txt','a+') as fr:
                fr.write(str(C12)+ ',') 
        elif sub == dirC44:
            coefs = numpy.polyfit(eta44, -p44, 1)
            C44 = coefs[0]*1.0e-4
            with open(path+'res_CsFit.txt','a+') as fr:
                fr.write(str(C44)+'\n') 

