import sys
from utils import xml_differencer


if __name__ == "__main__":
    xml_differencer(sys.argv[1], sys.argv[2], sys.argv[3])
