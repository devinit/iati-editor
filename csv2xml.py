import sys
from utils import csv_to_xml


if __name__ == "__main__":
    try:
        outpath = sys.argv[2]
    except IndexError:
        outpath = None
    csv_to_xml(sys.argv[1], outpath)
