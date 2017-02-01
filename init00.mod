# File with parameters for LAMMPS simulation
# metal units, elastic constants in GPa
# Last modified: May 6 2015

# --- Initial parameters
units       metal

# --- Minimization parameters
variable etol       equal   0.0
variable ftol       equal   1.0e-8
variable maxiter    equal   10000
variable maxeval    equal   100000
 
# --- Box properties and atom positions 
# Using a diamond lattice
boundary    p p p
dimension 	3
atom_style 	atomic
read_data 	data.Ni-unit
replicate 	10 10 10

# --- Other parameters
# Initial and final temperature
variable    Tf  equal   872.0
variable    T0  equal   872.0 

# Initial and final hydrostatic pressure
variable    Pf  equal   1.0
variable    P0  equal   1.0

# Box dimensions
variable af equal 1.0

# Time step
variable    dt          equal   0.5e-3
# Time of simulation stages
variable    HeatTime    equal   500
# Temperature and pressure drags for thermostat
# and barostat
variable    Tdrag       equal   100*${dt}
variable    Pdrag       equal   1000*${dt}
# Number of steps in each simulation stage
variable    NHeat       equal   ${HeatTime}/${dt}
# Set the LAMMPS timestep
timestep ${dt}

