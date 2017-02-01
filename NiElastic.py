#!/usr/bin/python
#
# SCRIPT FOR MD SIMULATIONS OF Ni ELASTIC PROPERTIES ON COE COMPUTER CLUSTER
# 
# Last modified: May 28 2015
#
# Python version: 2.6.6
#
# To run this script LAMMPS and python files need to be present in the directory 
#   where the script is run - this is a batch script, it creates directories for
#   every requested parameter set and runs MD in them
#
#  Script is split into 6 parts:
#		I.   	Input parameters
#		II.  	Modification and submission of LAMMPS scripts
#		III. 	Collection of LAMMPS results
#		IV.  	Averaging of LAMMPS results
#		V.		Computation of elastic constants
#		VI.		Basic visualization of the results
# NOTE: uncomment all the script parts that are not part of the current stage
#   besides parameter selection (I.) when running any of the script parts II.-VI.
#
# NOTE:init00.mod is the modified script for LAMMPS runs and it cannot have
#   inline comments (only in separate lines)
#
# NOTE: part III. uses multithreading, requesting a thread per temperature used 
#
# NOTE: assumes log2txt.py is present in a directory which path is included in 
#		the shell configuration settings i.e. it can be called directly
#
# User Input: 
# -------------
# LAMMPS simulation programs (in. file, LAMMPS modules, potential files)
# Current package: in.elastic_nvt, init00.mod, potential.mod, data.Ni-unit
#					FeNiCr.eam.alloy
# submit_lammps_parallel.pl: COE cluster submission script modified to 
#								generate and incorporate variable MD seed 
#
# Output: 
# -------------
# resCsFit.txt 	- average temperatures [K] and corresponding elastic constants [GPa]
# log.out 		- average properties from log.lammps file
# movie.xyz		- data for atom/simulation visualization
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #  

# -- MODULES
# PYTHON MODULES
import os, datetime, threading, subprocess, numpy
# OPTIONAL MODULES 
# Modification and submission of LAMMPS scripts
#import runlmp
# Collection and averaging of Lammps output
#import avlmp
# Computation of elastic properties
#import ellmp
# Data visualisation
import vislmp

# # # # # # # # # # # # # # # # # # # # # # 
# 
# I. INPUT PARAMETERS
#
# # # # # # # # # # # # # # # # # # # # # # 

# --- Temperature range, K
# To run an entire T range
# Note: it will run until last T value - step
# so use one extra at the end of the range
Ttemp = numpy.arange(323.15,923.15,50) 
arr = numpy.array(Ttemp)
arr.tolist()
T=[str(i) for i in arr]
T.insert(0, '0.5')
#
# Uncoment to run only selected, previously 
# incomplete jobs 
# List of temperatures not to run
#T1 = ['0.5','473.15','673.15']
#T0=T 
#T = [x for x in T0 if x not in T1]

# --- Box dimensions for each temperature, Angstroms  
af = ['28.1448', '28.1598', '28.1652', '28.1715', '28.1787', '28.1867', '28.1955', '28.2051', '28.2156',
       '28.2270', '28.2391', '28.2521', '28.2659']

# --- LAMMPS simulation parameters 
# names to appear exactly as in init.mod script
parameters = {'dt': '0.5e-3', 'Pf': '1.0', 'P0': '1.0', 'DP': '10.0', 'HeatTime': '100.0'}
# Number of atom replications in each direction
# Total number of atoms is then (#unit cell)*Nat^3
Nat = '8'

# --- Other simulation parameters
# 
# Ensemble - NPT or NVT
ensemble = 'nvt'
# Cluster job split
# 'n' - run a single job for each T (in. script which has all the deformation cases)
# '3n' - run a 3 jobs per T - each job being a different deformation (x, y, and yz)
#			separate in. scripts for each deformation
split = 'n'
# Number of processors for each job
p = '20'
# Files other than in.- needed for the run or to be modified
files = ['data.Ni-unit', 'init00.mod', 'FeNiCr.eam.alloy', 'potential.mod', 'submit_lammps_parallel.pl']
#
# Path to current folder 
path = os.getcwd()+ '/' 
# Make new main directory for current runs with date in its name
# Uncomment if needed the name to be offset by a day
today = datetime.date.today()# + datetime.timedelta(days=1)
newdir = 'RES_' + str(today)  
# Comment the above two lines, uncomment the following 
# and use a different name if the results directory has
# a different naming convention
#newdir = 

# --- Parameters for averaging
# NOTE: Choose the averaging method in the averaging section
# Name of the main folder with results
resdir = newdir
# Thermo output - variables for collection - type and order
thermo = ['Step', 'T', 'p', 'ke', 'pe', 'pxx', 'pyy', 'pzz', 'pxy', 'pxz', 'pyz', 'lx', 'ly', 'lz', 'xy', 'xz', 'yz']
# Variables to be averaged
avars = ['T', 'pxx', 'pyy', 'pxy', 'lx', 'ly', 'xy']
# Window for movig average
window = 2000.0 
# Number of simulation steps
nsteps = 2
# Initial time span (LAMMPS sample preparation)
t00 = 2
t0 = 200000
# Final time span (LAMMPS elastic deformation)
tf0 = 200000
tf  = 400000
# Deformation direction for C44
dirC44 = 'xy'

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
# II. MODIFICATION AND SUBMISSION OF LAMMPS SCRIPTS
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Make main directory for all results from this batch run
#zipname = runlmp.make_main(files, newdir, ensemble, split)
# --- Main processes for each temperature  
#for Ti in T:
#    # Add or update temperature in the parameter list
#    parameters['Tf'] = Ti
#    parameters['T0'] = Ti
#    # Add or update box dimensions
#    i = T.index(Ti)
#    parameters['af'] = af[i]
#    # Make sub-and subsub directories for each temperature T
#    #   and each deformation if split = 3n
#    runlmp.make_dirs(path, newdir, Ti, zipname, ensemble, split)
#    # Path to path/Ti/ directory 
#    pathT = path + newdir + '/T_' + Ti + '/'    
#    # Modify init.mod
#    runlmp.num_atoms(Nat, pathT) 
#    runlmp.mod_init(parameters, pathT)
#    # Collect all files in proper subdirs, construct the commands and submit the jobs 
#    runlmp.lmp_sub(p, Ti, pathT, split, ensemble)   
#

# # # # # # # # # # # # # # # # # # # # # # 
# 
# III. COLLECTION OF LAMMPS RESULTS
#
# # # # # # # # # # # # # # # # # # # # # # 
#
# NOTE: this is imperfect but it speeds the program up considerably
#
# Process lammps log into text in each subdirectory
# Starts the process for each Ti as a different thread
# Results are stored in data_out.txt and log info in log.out   
#for Ti in T:
#    # Path to path/Ti/ directory 
#    pathT = path + resdir + '/T_' + Ti + '/'    
#    thread = threading.Thread(target=avlmp.prc_log, args=(pathT, split))        
#    thread.start() 

# # # # # # # # # # # # # # # # # # # # # # 
# 
# IV. AVERAGING OF LAMMPS RESULTS
#
# # # # # # # # # # # # # # # # # # # # # # 
# Choose an averaging approach - details in avlmp.py
# Check the avlmp module for exact input.   
# Current list and usage examples:
#
# 1) Moving average
#   Not yet checked numpy moving average from the web.
#   avlmp.moveav(avars, thermo, window) 
#   
# 2) Average of the distributions
#   avlmp.distav(avars, thermo)
#
# 3) Fit the stress/strain data and get the elastic constants from
#       the slopes - no need for part V but may be less accurate 
#   avlmp.fitstr(avars, thermo, path, t00, t0, tf0, tf, dirC44, split, sub)               
#
# 4) Simple average
#   avlmp.simpav(avars, thermo)

#for Ti in T:
#    # Path to path/Ti/ directory 
#    pathT = path + resdir + '/T_' + Ti + '/'
#    # Change directory, perform averaging 
#    # and change back to current directory        
#    if split == '3n':
#        subdir = ['x', 'y', 'yz']
#        for sub in subdir:
#            pathsub = pathT + sub + '/'
#            with avlmp.ChangeDir(pathsub):
#                # Change the averaging approach here
#                avlmp.fitstr(avars, thermo, path+resdir+'/', t00, t0, tf0, tf, dirC44, split, sub)               
#    elif split == 'n':
#            with avlmp.ChangeDir(pathT):
#                # Change the averaging approach here
#                avlmp.fitstr(avars, thermo, path+resdir+'/', t00, t0, tf0, tf, dirC44, split, None)               

# # # # # # # # # # # # # # # # # # # # # # 
# 
# V. COMPUTATION OF ELASTIC CONSTANTS 
#
# # # # # # # # # # # # # # # # # # # # # # 

#for Ti in T:
#    # Path to path/Ti/ directory 
#    pathT = path + resdir + '/T_' + Ti + '/'
#    # Compute elastic constants
#    ellmp.cs(avars, nsteps, Ti, path + resdir + '/', pathT, split)     

# Compute other elastic properties - under development
#pathMain = path + resdir + '/'
#ellmp.elprops(pathMain, 'res_CsFit.txt')

# # # # # # # # # # # # # # # # # # # # # # 
# 
# VI. BASIC VISUALIZATION OF THE RESULTS 
#
# # # # # # # # # # # # # # # # # # # # # # 
# Plot elastic constants as a function of temperature
vislmp.vis_cs(path+resdir+'/', 'res_CsFit.txt')

