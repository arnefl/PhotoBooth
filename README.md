# Photobooth
A simple photobooth app.


## Install instrunctions

1. Install miniconda or anaconda
2. Install libghoto2 from source
```
    brew install libgphoto2
```
3. Create new conda environment and install some packages
```
    conda create --name photobooth python=3.7 pillow pyyaml
    conda activate photobooth
    pip install -v gphoto2
```
4. Update `config.yml`.
5. Update shebang in main.py to your python path
6. Give more priveliges to main.py.
```
    chmod +x main.py
```
7. Update shebang in main.py.
