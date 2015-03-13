#!/bin/sh
# Exec a script over all the IEM nodes

# Run iem21 first as it may need to be aware of changes in hostnames
MACHINES="iem21 iem-director0 iem-director1 iemfe iem6 iem12 iem21 iem22 iem30 iem50 iemvs100 iemvs101 iemvs102 iemvs103 iemvs104 iemvs105 iemvs106 iemvs107 iemvs108"
for MACH in $MACHINES
do
ssh root@$MACH $1
done