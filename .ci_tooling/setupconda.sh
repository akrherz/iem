. $HOME/miniconda/etc/profile.d/conda.sh

conda config --set quiet True --set always_yes yes --set changeps1 no
conda config --prepend channels conda-forge
conda config --set channel_priority strict
