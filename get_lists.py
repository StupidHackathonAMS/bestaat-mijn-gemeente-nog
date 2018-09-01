#!/usr/bin/env python

import os
import sys
import re
from pprint import pprint
import json

import requests
from lxml import etree


def get_possible_lists():
    html = etree.HTML(
        requests.get('https://dataderden.cbs.nl/ODataFeed/').content)
    return html.xpath('//a/@href')


def get_gemeenten(link):
    resp = requests.get('https://dataderden.cbs.nl%s/Gemeenten?$format=json' % (link,))
    if resp.status_code >= 200 and resp.status_code < 300:
        return resp.json()


def get_year(link):
    # https://dataderden.cbs.nl/ODataFeed/OData/45001NED/TableInfos?$format=json
    resp = requests.get('https://dataderden.cbs.nl%s/TableInfos?$format=json' % (link,))
    if resp.status_code >= 200 and resp.status_code < 300:
        return resp.json()['value'][0]['Period']


def main(argv):
    yearly = {}
    links = get_possible_lists()
    for link in links:
        result = get_gemeenten(link)
        if result is not None:
            year_str = get_year(link)
            try:
                year = int(year_str)
            except ValueError:
                year = None
            if year is not None:
                yearly[year] = result

    for year in sorted(yearly.keys()):
        print(year)
        with open('cache/%s.json' % (year,), 'w') as out_file:
            json.dump(yearly[year], out_file)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
