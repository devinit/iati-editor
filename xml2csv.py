import sys
from utils import xml_to_csv


if __name__ == "__main__":
    try:
        outpath = sys.argv[2]
    except IndexError:
        outpath = None
    xml_to_csv(sys.argv[1], outpath)
