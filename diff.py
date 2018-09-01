#!/usr/bin/env python

import os
import sys
import re
from glob import glob
import json

from pprint import pprint
import json


def compare(older_year, newer_year, older, newer):
    print("Comparing %s vs %s" % (older_year, newer_year,))
    older_keys = {r['Key'].strip() for r in older['value']}
    newer_keys = {r['Key'].strip() for r in newer['value']}
    print("Disappeared:")
    print(older_keys - newer_keys)
    print("New:")
    print(newer_keys - older_keys)


def main(argv):
    yearly = {}
    for f in glob('cache/*.json'):
        year = int(os.path.basename(f).replace('.json', ''))
        with open(f, 'r') as in_file:
            yearly[year] = json.load(in_file)

    for year in sorted(yearly.keys()):
        if (year - 1) in yearly:
            compare(year - 1, year, yearly[year - 1], yearly[year])
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
