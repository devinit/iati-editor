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
python3 diff.py "test_data/DIPR IATI data February 2018.xml" "test_data/DIPR IATI data June 2019.xml" "test_data/new_and_updated.xml"
python3 xml2csv.py "test_data/new_and_updated.xml"
python3 csv2xml.py "test_data/new_and_updated"
```
