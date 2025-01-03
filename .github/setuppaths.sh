# Only path setups here, adding data handled in setupdata.sh
sudo ln -s `pwd` /opt/iem
sudo ln -s $HOME/micromamba /opt/miniconda3
mkdir _mesonet
sudo ln -s `pwd`/_mesonet /mesonet
mkdir -p /mesonet/ldmdata/gis/images/4326/USCOMP
mkdir -p /mesonet/share/pickup/yieldfx

mkdir _webtmp
sudo ln -s `pwd`/_webtmp /var/webtmp
