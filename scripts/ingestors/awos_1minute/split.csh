#!/bin/csh
# Split the AWOS file into smaller chunks
# Daryl Herzmann

foreach station (AXA IKV AIO ADU BNW CIN CNC CCY ICL CAV CWI CBF CSQ)
 grep ${station} ${1} > station/${station}.dat
end

foreach station (DEH DNS FFL FOD FSW HNR EOK OXV LRJ MXO MUT TNU OLZ ORC RDK)
 grep ${station} ${1} > station/${station}.dat
end

foreach station (SHL SDA SLB AWG EBS)
 grep ${station} ${1} > station/${station}.dat
end

foreach station (MPZ PEA VTI IIB CKP OOA GGI TVK IFA PRO FXY I75)
  grep ${station} ${1} > station/${station}.dat
end
