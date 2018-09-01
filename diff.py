#!/usr/bin/env python

import os
import sys
import re
from glob import glob
import json

from pprint import pprint
import json

from lxml import etree
import shapely
from shapely.geometry import asShape, Polygon, LinearRing


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_gml_shapes(gml_file):
    ns = {
        'kad': "http://www.kadaster.nl/kad/pdok",
        'gml': 'http://www.opengis.net/gml/3.2'
    }
    xml = etree.parse(gml_file)
    shapes = []
    for gem in xml.xpath('//kad:Gemeenten', namespaces=ns):
        info = {
            'code': 'GM' + ''.join(
                gem.xpath('./kad:Code/text()', namespaces=ns)),
            'naam': ''.join(
                gem.xpath('./kad:Gemeentenaam/text()', namespaces=ns))
        }
        points_txt = ''.join(
            gem.xpath('.//gml:LinearRing//text()', namespaces=ns))
        points = [
            float(x) for x in
            points_txt.split()]
        shape = asShape(Polygon(LinearRing(
            chunks(points, 2)
        )))
        shapes.append((info, shape))
    return shapes


def compare(older_year, newer_year, older, newer):
    # print("Comparing %s vs %s" % (older_year, newer_year,))
    older_keys = {r['Key'].strip() for r in older['value']}
    newer_keys = {r['Key'].strip() for r in newer['value']}
    disappeared = older_keys - newer_keys
    added = newer_keys - older_keys
    return (
        [o for o in older['value'] if o['Key'].strip() in disappeared],
        [n for n in newer['value'] if n['Key'].strip() in added],)


def merge(older_year, newer_year, gone, created, new_shapes, old_shapes):
    # print("Merging %s and %s" % (newer_year, older_year,))
    gone_keys = [g['Key'].strip() for g in gone]
    created_keys = [c['Key'].strip() for c in created]
    merges = {}
    for old, old_shape in old_shapes:
        if old['code'] not in gone_keys:
            continue
        was_found = False
        for new, new_shape in new_shapes:
            if was_found:
                continue
            # if new['code'] not in created_keys:
            #     continue
            if new_shape.contains(old_shape.representative_point()):
                was_found = True
                # print("%s -> %s" % (old, new,))
                merges[old['code']] = new['code']
        # if not was_found:
        #     print("%s went to unknown" % (old,))
    return merges


def main(argv):
    yearly = {}
    for f in glob('cache/*.json'):
        year = int(os.path.basename(f).replace('.json', ''))
        with open(f, 'r') as in_file:
            yearly[year] = json.load(in_file)

    all = {}
    for year in sorted(yearly.keys()):
        for gem in yearly[year]['value']:
            if gem['Key'].strip() not in all:
                all[gem['Key'].strip()] = gem
        if (year - 1) in yearly:
            gone, created = compare(
                year - 1, year, yearly[year - 1], yearly[year])
            # print("Disappeared:")
            # pprint(gone)
            # print("New:")
            # pprint(created)
            old_shapes = []
            new_shapes = []
            gg_path = 'grenzen/%s/Gemeentegrenzen.gml' % (year,)
            if os.path.exists(gg_path):
                new_shapes = get_gml_shapes(gg_path)
            gg_path = 'grenzen/%s/Gemeentegrenzen.gml' % (year - 1,)
            if os.path.exists(gg_path):
                old_shapes = get_gml_shapes(gg_path)
            if len(new_shapes) > 0 and len(old_shapes) > 0:
                merges = merge(
                    year - 1, year, gone, created, new_shapes,
                    old_shapes)
                for old, new in merges.items():
                    try:
                        all[old]['merges'] += {'code': new, 'year': year}
                    except LookupError:
                        all[old]['merges'] = [{'code': new, 'year': year}]
    print(json.dumps({v['Key'].strip(): v for v in all.values()}))
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
