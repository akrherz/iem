#!/bin/bash

bash createGrids.sh
bash SDMESONET_plot.sh
bash MW_mesonet.sh
bash TEMPS_plot.sh
bash DEWPS_plot.sh
bash NEXRAD_overlay.sh DMX
bash NEXRAD_overlay.sh OAX
bash NEXRAD_overlay.sh DVN
bash NEXRAD_overlay.sh FSD
bash NEXRAD_overlay.sh ARX
bash NEXRAD_overlay.sh EAX
bash NEXRAD_overlay.sh MPX
bash HEAT_plot.sh
bash WCHT_plot.sh
bash RELH_plot.sh
bash ASOS_plot.sh

cd black && bash surfaceContours.sh
