#!/bin/sh
# Exec a script over all the IEM nodes

MACHINES="iem-director0 iem-director1 iemfe iem12 iem19 iem21 iem22 iem23 iem30 iem50 iemvs100 iemvs101 iemvs102 iemvs103 iemvs104 iemvs105 iemvs106 iemvs107 iemvs108"
for MACH in $MACHINES
do
ssh root@$MACH $1
done