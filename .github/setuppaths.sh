# Only path setups here, adding data handled in setupdata.sh
sudo ln -s `pwd` /opt/iem
# Kind of hacky, but that is what daryl does
# needed by all kinds of things
sudo ln -s $HOME/micromamba /opt/miniconda3
mkdir _mesonet
sudo ln -s `pwd`/_mesonet /mesonet
mkdir -p /mesonet/ldmdata/gis/images/4326/USCOMP
mkdir -p /mesonet/share/pickup/yieldfx
mkdir -p /mesonet/share/features/2022/03

mkdir _webtmp
sudo ln -s `pwd`/_webtmp /var/webtmp
