#!/usr/bin/python

# Module for setting up and performing lammps simulations
#   - Modifies the input scripts
#   - Modifies and sets up runs on the computer cluster
#    
# Notes:
#   - init.mod modification needs a template init00.mod 
#
# Last modified: April 21 2015
#

import re, os, zipfile, shutil, subprocess

# Functions for modification of init.mod
#
def mod_init(parameters, pathT):
    """ Include new parameter set in init.mod file. """
    with open(pathT + 'init0.mod', 'r') as fp:
       with open(pathT + 'init.mod', 'w') as fpo:
            lines = fp.readlines()
            linesOUT = ['\n', '\n']
            # Substitute parameters in each line
            for line in lines:
                linesOUT = sub_input(fp, line, linesOUT, parameters)
            fpo.write(''.join(linesOUT))
           
    
def sub_input(fp, line, linesOUT, parameters):
    """ Substitute new parameter values into init.mod file. """
  	# Find parameters that are to be changed
    for key in parameters:
        match = re.search(key, line)
        if match:
            # Find if match is a parameter declaration 
			# this prevents from substituting expressions   
            mnd = match.end()
            matchv = re.search('equal', line[mnd:])
			# If a declaration -- substitute new value                    
            if matchv:
                line0 = line[:mnd]
                line = re.sub("[0-9.]|e-|e[0-9]|e+[0-9]|\n", ' ', line[mnd:])
                line = line0 + line + parameters[key] + '\n'
    linesOUT.append(line)
    return linesOUT		    

def num_atoms(n, pathT):
    """ Change number of atoms to use in the simulation. """
    with open(pathT + 'init00.mod', 'r') as fp:
        with open(pathT + 'init0.mod', 'w') as fpo: 
            lines = fp.readlines()
            for line in lines:
                fpo.write('replicate\t'+ (n + ' ')*3 if 'replicate' in line else line)

def make_main(files, newdir, ensemble, split):
    """ Create main directory for LAMMPS simulations of ensemble with type split. """
    # Remove old (if exists) and create new zipfile of type ensebmble for given split choice
    if split == 'n': 
        inname = 'in.' + 'elastic_' + ensemble
        zipname = ensemble+'.zip'
        files.append(inname)
    elif split == '3n':
        inname_x = 'in.' + 'elastic_' + ensemble +'_x'
        inname_y = 'in.' + 'elastic_' + ensemble +'_y'
        inname_yz = 'in.' + 'elastic_' + ensemble +'_yz'
        zipname = ensemble+'.zip'
        files.append(inname_x)
        files.append(inname_y)
        files.append(inname_yz)
    try:
        os.remove(zipname)
    except OSError:
        pass
    zf = zipfile.ZipFile(zipname, 'a') 
    try:
        for file in files:
            zf.write(file)
    finally:
        zf.close()
    # Make main directory for current results set
    os.mkdir(newdir)
    # Copy zip file to the main directory    
    shutil.copy(zipname,newdir)    
    return zipname

def make_dirs(path, newdir, T, zipname, ensemble, split):
    """ Create a directory for simulation at temperature T and subdirs if split is 3n. """
    # Create the T directory
    dirname = 'T_'+ T
    pathT = path + newdir + '/' + dirname + '/'
    os.mkdir(pathT)
    # Unzip the zip file with scripts in the T directory
    zippath = path + newdir + '/' + zipname
    zf = zipfile.ZipFile(zippath)
    zf.extractall(pathT)
    # Modify according to split - create 3 directories and mv appropriate in. files into them 
    if split == '3n':
        subdir = ['x', 'y', 'yz']
        for sub in subdir:
            pathsub = pathT + sub + '/'
            os.mkdir(pathsub)
            fname = 'in.' + 'elastic_' + ensemble + '_' + sub
            shutil.move(pathT + fname, pathsub)

def lmp_sub(p, T, pathT, split, ensemble):
    """ Submit the cluster submission script. """
    if split == 'n': 
        # Name and submit job in T_ directory
        # Make files executable
        subprocess.call(['chmod -R 700 *'], shell=True, cwd=pathT)
        fname = 'in.' + 'elastic_' + ensemble 
        jobname = 'jobT' + T      
        sub_command = 'submit_lammps_parallel.pl' + ' ' + fname + ' ' + p + ' '  + jobname + ' ' + '| qsub'
        subprocess.call([sub_command], shell=True, cwd=pathT)
    elif split == '3n':
        # Copy all files from /.../Ti/ to each subdirectory
        #   appropriate in. files are mv there in make_dirs
        # Name and submit the jobs in each subdirectory
        # Make files executable
        subdir = ['x', 'y', 'yz']
        for sub in subdir:
            pathsub = pathT + sub + '/'
            fname = 'in.' + 'elastic_' + ensemble + '_' + sub 
            jobname = 'jobT' + T + '_' + sub     
            sub_command = 'submit_lammps_parallel.pl' + ' ' + fname + ' ' + p + ' '  + jobname + ' ' + '| qsub'
            subprocess.call(['cp *.* '+ pathsub], shell=True, cwd=pathT)
            subprocess.call(['chmod -R 700 */'], shell=True, cwd=pathT)
            subprocess.call([sub_command], shell=True, cwd=pathsub)


