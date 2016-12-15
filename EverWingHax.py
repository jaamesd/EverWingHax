#! /usr/bin/env python3

import sys
if sys.version_info[0] < 3:
    print('You need to run this with Python 3')
    sys.exit(1)

import HaxCore

if __name__ == "__main__":
    HaxCore.run()
