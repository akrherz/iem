# Get conda in our $PATH
export PATH="$HOME/miniconda/bin:$PATH"

if [ ! -f $HOME/miniconda/envs/prod/bin/python ]; then
    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    bash miniconda.sh -f -b -p $HOME/miniconda
    . $HOME/miniconda/etc/profile.d/conda.sh
    conda config --set quiet True --set always_yes yes --set changeps1 no
    conda config --prepend channels conda-forge
    conda config --set channel_priority strict
    conda create -n prod python=$PYTHON_VERSION --file conda_requirements.txt
    conda activate prod
    conda clean -y --all -q
    pip install --upgrade -r pip_requirements.txt
    rm -rf $HOME/miniconda/pkgs/cache/*
fi
. $HOME/miniconda/etc/profile.d/conda.sh
conda activate prod
# Debug printout
conda list
