#!/bin/ksh
# -- script to handle incoming mail messages, 
# -- strip off extra text distrib to arhdata 
# -- and on to juneau
# -- pap, 6/2000

SrcDir=/var/mail
Usr=erosa
RawDir=/raw/erosa
TRUE=1
FALSE=0
SleepTime=60

while (true)
do
  printf "%s: %s  ------ " $0 "$(date -u +"%x %X")"
  TS=$(date -u +"%j%H%M%S")
  FName=erosa.${TS}

  InMsg=0
  FCtr=1

  if [[ -s ${SrcDir}/${Usr} ]]
  then
    printf "\n-----------------------------------\n"
    date -u +"%x %X" 

    # -- give sendmail time to finish saving file
    sleep 2

    ll ${SrcDir}/${Usr}

    # -- debug saving of input file
    #cp ${SrcDir}/${Usr} /tmp/${Usr}.${TS}

    cat ${SrcDir}/${Usr} |
      while read Line
        do
          echo "$Line" | egrep -e "------------------------" > /dev/null
          status=$?
          if [[ $status = 0 ]]
          then
            if [[ $InMsg = TRUE ]] 
            then 
              InMsg=FALSE
              (( FCtr = $FCtr + 1 ))
            else 
              InMsg=TRUE
            fi
          fi
    
          if [[ $InMsg = TRUE && "$Line" != "" && $status != 0 ]]
          then
            echo ${FName}.$FCtr : "$Line"
            echo "$Line" >> ${RawDir}/${FName}.$FCtr
          fi 
        done
  
    # -- find and distribute the erosa files
    cd $RawDir
    for f in ${FName}.*
    do
      echo /apps/dd/DistribMsq 160.0.2.11 1 EROSA ${RawDir}/$f
           /apps/dd/DistribMsq 160.0.2.11 1 EROSA ${RawDir}/$f
    done
    
    set -x
    cat /dev/null > ${SrcDir}/${Usr}
    set +x

    date -u +"%x %X" 
    printf "-----------------------------------\n"
  
    # -- restore source file for debugging, but check above 
    #cp /tmp/${Usr} ${SrcDir}/${Usr} 
  else 
    echo No new files
  fi
  sleep $SleepTime
done

exit 0

