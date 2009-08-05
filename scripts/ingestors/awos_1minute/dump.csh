#!/bin/csh

# Dump DB files into DB...

cd DB
foreach file (`ls -1 *.db`)
  echo "Do: ${file}"
#  grep -v "None" ${file} > ${file}.cln
  cat ${file} | sed -e "s/None/Null/g" > ${file}.cln
  psql -h iemdb awos -f ${file}.cln
end
