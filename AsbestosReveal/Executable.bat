@ECHO OFF
ECHO Congratulations! Your file executed successfully.
python -m pip install --upgrade pip
pip install pillow
pip install rdflib
pip install requests
pip install unidecode
pip install owlready2
pip install joblib
python main.py py2exe
PAUSE