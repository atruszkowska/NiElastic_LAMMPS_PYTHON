#!/usr/bin/python

# Delete running cluster jobs
# First run $ qstat | grep your_onid > jobs.out
# then run this script
# Last modified: May 28 2015
import subprocess
with open("jobs.out", 'r') as fp:
    lines = fp.readlines()
    for line in lines:
        line = line.split()
        #print line[0]
        subcom = 'qdel '+ line[0]
        subprocess.call([subcom], shell=True)
