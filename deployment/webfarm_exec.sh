#!/bin/sh
# Exec a script over the webfarm nodes

MACHINES="iemvs100 iemvs101 iemvs102 iemvs103 iemvs104 iemvs105 iemvs106 iemvs107  iemvs108"
for MACH in $MACHINES
do
  ssh $MACH $1
done