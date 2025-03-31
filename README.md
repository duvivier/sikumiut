# Sikumiut
Classroom model activities for Sikumiut sea ice field school - April 2025


## Installing Python and Jupyter Hub on  your laptop

Open a terminal program (terminal, iterm, etc.)

1. Install miniconda: https://www.anaconda.com/docs/getting-started/miniconda/install

  -  MacOS instructions (assuming "Apple Silicon": click apple menu and "About this Mac"
      to verify the chip is made by Apple; if made by Intel, go to website and follow the
      Intel directions... should just be a different Miniconda3-latest file)
  - Say yes to prompts when asked during install

```
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
```
```
bash Miniconda3-latest-MacOSX-arm64.sh
```
```
conda config --set auto_activate_base true
```
```
conda config --add channels defaults
```
```
conda config --add channels conda-forge
```
```
conda config --set channel_priority strict
```
```
rm -f Miniconda3-latest-MacOSX-arm64.sh
```

  - Instructions for Windows and Linux are also available on the website

2. Quit your terminal program and reopen it. It should now open in the (base) environment.

3. In your (base) environment, install jupyter

```
conda install mamba jupyterlab
```

4. If you have not already, clone this GitHub repository to your desktop. Then go to the directory that holds the environment file
   
```
cd Desktop
```
```
git clone https://github.com/duvivier/sikumiut.git
```
```
cd sikumiut
```

5. Install the (alaska) environment within the (base) environment

```
mamba env create -f environment.yml
```

6. From the (base) environment, install (alaska) as an option for the kernel in your notebook.

```
conda activate alaska
```
It should now show (alaska) at the command line prompt instead of (base)
```
python -m ipykernel install --name  alaska --user
```

```
conda deactivate
```
It should now show (base) at the command line prompt instead of (alaska)


7. The file browser in jupyter will use whatever directory you ran "jupyter lab" from as
  the root directory. You should already be in the sikumiut directory and this should work fine.

```
cd sikumiut
```

8. Run jupyter by entering the following command. It should open a window in an internet browser.
   Make sure that your command line still says (base) at the start.

```
jupyter lab
```

NOTES:

* You can choose a better name for the environment by editing the first line of
  environment.yml before running mamba

* You may want to pin a specific version of python; when I created this environment it used
  python 3.13, but if you were testing your notebooks with an older version you may be in
  for surprises

* Since we added ipykernel to the (alaska) environment, it should be usable from jupyter
  even though jupyter was launched from the (base) environment


## How to Run A Jupyter Notebook

Once Jupyter opens in your internet browser it should look like the following screenshot. 
Note that there is an environment from the launcher called 'alaska', which is the environment
we set up above. There is also a navigation bar on the left with folders and the notebooks
are in these folders.

![Jupyter_home](https://github.com/user-attachments/assets/f6fdb21a-cd8e-4bbb-aca6-2f9c89524da0)

Double click on the 'cesm_activities' folder and then open a notebook (*.ipynb files are Jupyter
notebooks. Here we show one called 'Exercise_1_CESM1-LE.ipynb' as an example). 
When you open a notebook be sure that you select 'alaska' if asked 
to choose a kernel and that 'alaska' is shown in the upper right hand side of the notebook.
To run cells of code you can either push the 'play' button at the top when a cell is highlighted, 
or you can use the keys shift+enter to run the cell.

![Jupyter_notebook](https://github.com/user-attachments/assets/ed704862-47d8-4020-96c2-1532a460f56d)


Please let us know if you have questions!
