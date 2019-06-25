# iati-editor
A user-friendly IATI editor

## To install:
```
python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## To run:
```
source venv/bin/activate
python3 diff.py
python3 xml2csv.py
python3 csv2xml.py
```

## To bundle:
```
pyinstaller -w --onefile xml2csv.py
pyinstaller -w --onefile csv2xml.py
pyinstaller -w --onefile diff.py
cp -R iati dist/
```
