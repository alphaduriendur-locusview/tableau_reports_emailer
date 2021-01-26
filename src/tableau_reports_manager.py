import argparse
import os

__version__ = "1.0"


def get_parser():
    parser = argparse.ArgumentParser(description="This is tableau one stop report manager",
                                     prog='Tableau Reports Manager')
    parser.add_argument('--version', '-v', action='version', version='%(prog)s - {0}'.format(__version__))
    parser.add_argument('--list', '-l', help='list all workbooks from the server')
    return parser

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
