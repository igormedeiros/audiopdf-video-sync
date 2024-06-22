rm -r .\venv
python -m venv venv
.\venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt