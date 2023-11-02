# Install

The examples for this series have been tested on python 3.8 and 3.9 but should work on earlier versions of python 3 as well.

The external libraries needed are in the [requirements.txt](requirements.txt) file and can be installed with pip. Ideally in a virtual environement
using [venv](https://docs.python.org/3.8/library/venv.html) for example as shown below.

On Linux or MacOS

```sh
git clone git@github.com:jessicakoubi/talk_introduction_to_qt.git
cd talk_introduction_to_qt

python -m venv env
source env/bin/activate

pip install -r requirements.txt
```

On Windows

```sh
git clone git@github.com:jessicakoubi/talk_introduction_to_qt.git
cd talk_introduction_to_qt

python -m venv env
.env/Scripts/activate

pip install -r requirements.txt
```

## Mac Silicon Note

The **requirements.txt** file above does not work on a Mac using a silicon chip (tested on an M1Pro). You will need to either compile PySide2, install it using homebrew
or, preferabley, switch to PySide6.

**2023.11.01:** An update of this repository working with PySide6 is available on the [pyside6_version](https://github.com/jessicakoubi/talk_introduction_to_qt/tree/pyside6_version) branch.
