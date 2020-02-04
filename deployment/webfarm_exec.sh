#!/bin/sh
# Exec a script over the webfarm nodes

MACHINES="iem14 iemvs100 iemvs101 iemvs102 iemvs103 iemvs104 iemvs105 iemvs106 iemvs107 iemvs108 iemvs109"
for MACH in $MACHINES
do
	echo "--------------------- $MACH -----------------------------"
	ssh root@${MACH}.local $1
	echo
done