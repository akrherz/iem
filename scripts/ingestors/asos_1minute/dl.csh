# Download the 1 minute data from NCDC

cd data/

foreach station (MCW BRL MIW SPW AMW OTM CID DVN EST IOW SUX DBQ ALO DSM LWD OMA MLI FSD)
#foreach station (HUT)
  mkdir -p ${station}
  foreach yr (${1})
    #foreach mo (01 02 03 04 05 06 07 08 09 10 11 12)
    foreach mo (${2})
      foreach report (6405 6406)
        echo "$station $yr $mo $report"
        wget -q -O ${station}/${report}0K${station}${yr}${mo}.dat "ftp://ftp.ncdc.noaa.gov/pub/data/asos-onemin/${report}-${yr}/${report}0K${station}${yr}${mo}.dat"
        ls -l ${station}/${report}0K${station}${yr}${mo}.dat
      end
    end
  end
end
