# ENERGY'S LOAD FORECASTING USING STREAMLIT
Energy's Load Forecasting (Machine Learning model) using Streamlit to deploy

## Install Python and update pip
> PowerShell
* Install [Python](https://www.tutorialsteacher.com/python/install-python#:~:text=You%20can%20install%20Python%20by,to%20start%20the%20installation%20wizard.)
* Check Python version: `python --version`
* Install and upgrade pip: `python -m pip install --upgrade pip`

## Configure the virtualenv
> PowerShell
* Access inside of the root folder: `cd energy-load-forecasting-en`
* Allow execute scripts to activate virtualenv: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
* Install virtualenv: `pip install virtualenv`
* Create a virtualenv inside the root folder: `python -m virtualenv venv`
* Activate the virtualenv: `.\venv\Scripts\activate`
* Install all libraries required: `pip install -r requirements.txt`

## How to run
> PowerShell
* Access inside of the root folder.
* Activate virtual env: `.\venv\Scripts\activate`
* Run the web app: `streamlit run .\app.py`

## PEP8 and Pylint
> PowerShell
* Check code style: `pycodestyle [filename].py`
* Static code analyzer: `pylint [filename].py` 

## Deactivate the virtualenv
> PowerShell
* Run the visualizator: `deactivate`
