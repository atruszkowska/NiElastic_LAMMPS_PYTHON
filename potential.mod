# LAMMPS potential  and output settings module
# Last modified: April 21 2015
 
# Choose potential
pair_style eam/alloy
pair_coeff  * * FeNiCr.eam.alloy Fe Ni Cr

# Setup neighbor style
neighbor 0.3 bin
neigh_modify delay 10

# Setup output
thermo          1
thermo_style    custom step temp press ke pe pxx pyy pzz pxy pxz pyz lx ly lz xy xz yz
 
