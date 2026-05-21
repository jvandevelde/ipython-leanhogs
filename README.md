# Getting Started
## Windows

* Install miniconda from http://conda.pydata.org/miniconda.html
    * Add conda & scripts directory to Windows PATH
    * ex: C:\Anaconda3;C:\Anaconda3\Scripts\
* Install nbformat
   * `conda install nbformat`
* Create a new environment using the environment file at ./conda/environment.yml
   * `conda env create -f ./conda/environment.yml`

1. Launch
   * `jupyter notebook`

1. conda create --name hogs python=3.5
1. conda activate hogs
   - pip install --upgrade pip
   - pip install PyQt5
   - pip install jupyter==1.0.0
   - pip install matplotlib==3.0.3
   - pip install numpy==1.14.2
   - pip install quandl==2.8.9
   - pip install requests
   - pip install pandas==0.18.1
   - pip install seaborn==0.7.1
   - pip install xlsxwriter==0.9.4

### Windows Tips

1. You may get an untrusted kernel error combined with missing module `win32api`
   https://github.com/jupyter/notebook/issues/4909
   pip install --upgrade jupyter_client

### Installation on Windows

1. Install conda/MiniConda
1. Add conda & scripts directory to Windows PATH
    * ex: C:\Anaconda3;C:\Anaconda3\Scripts\
1. Create new py3.5 env
   * `conda create --name hogs python=3.5`
1. Activate new env
   * `conda activate hogs`
1. Upgrade pip in new environment
   * `python -m pip install --upgrade pip`
1. Install environment via pip
   * `pip install -r ./conda/requirements.txt`

## Linux

Install for Ubuntu 20.04
https://itslinuxfoss.com/how-to-install-and-use-miniconda-on-ubuntu-20-04/

## Create Conda environment & install requirements

1. Activate conda if not automatic
   * `eval "$(/home/jvandevelde/miniconda3/bin/conda shell.bash hook)"`
1. Create new py3.5 env
   * `conda create --name hogs python=3.5`
1. Activate new env
   * `conda activate hogs`
1. Upgrade pip in new environment
   * `python -m pip install --upgrade pip`
1. Install environment via pip
   * `pip install -r ./conda/requirements.txt`

# Launch Application

1. Launch Jupyter Notebook
   * `jupyter notebook`