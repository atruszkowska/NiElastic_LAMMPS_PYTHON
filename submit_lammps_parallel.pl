#!/usr/bin/perl -w
#
# Script to generate submit script for running parallel LAMMPS simulations
#	modified to include different random seeds in each simulation
#
# Usage: submit_lammps_parallel.pl in.file-name number-of-processors job-name | qsub
#
# Last modified: submit_lammps_parallel.pl
#

unless (@ARGV >= 3){die "Error: Need 3 arguments -- sugested usage\nsubmit_lammps_parallel.pl in.file-name number-of-processors job-name | qsub\n";}

$in    = shift(@ARGV);
$nproc = shift(@ARGV);
$name  = shift(@ARGV);

# Random seed
use Time::HiRes qw/ time sleep /;
my $datestring = int(time*1000000);
my $datestring2 = "$datestring";
@datestring3 = split(//, $datestring2);
my $tme = int(join("", @datestring3[-6..-1]));

print "\#!/bin/csh

\#\$ -N $name

\#\$ -cwd

\# send output to job.log (STDOUT + STDERR)
\#\$ -o $in\.out
\#\$ -j y

\# specify the mpich parallel environment and request 4
\# processors from the available hosts
\#\$ -pe mpich2 $nproc

\# specify the hardware platform to run the job on.
\#\$ -q mime


echo \"------------------------------------------------------------------------\"
date
echo \"Got \$NSLOTS slots.\"

\# command to run.  ONLY CHANGE THE NAME OF YOUR MPI APPLICATION  

date >! TIMING
/scratch/a1/sge/mpich2/bin/mpiexec -np \$NSLOTS -machinefile \$TMPDIR/machines /nfs/matsci-fserv/share/\$USER/bin/lmp_parallel -var seed $tme < $in
date >> TIMING

echo \" ALL DONE \"
date
echo \"------------------------------------------------------------------------\"
exit 0";
