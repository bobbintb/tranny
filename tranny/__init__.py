# -*- coding: utf-8 -*-
import argparse

__author__ = "Leigh MacDonald <leigh.macdonald@gmail.com>"
__license__ = "BSD 3-Clause"
__copyright__ = "Copyright (c) 2013-2014 Leigh MacDonald"

import logging
from docopt import docopt


__version__ = '0.0.1'

def parse_args():
    parser = argparse.ArgumentParser(description="Tranny torrent management system")
    parser.add_argument('command', metavar='CMD', nargs=1, help="")
    args = parser.parse_args()
    return args

def main():

    arguments = parse_args()
    print(arguments)
    from tranny.manager import ServiceManager

    logging.basicConfig(level=logging.INFO)

    application = ServiceManager()
    application.start()

if __name__ == '__main__':
    main()
