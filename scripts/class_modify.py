#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import gzip
import logging
import argparse

from collections import OrderedDict

LOG = logging.getLogger(__name__)

__version__ = "v1.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "113178210@qq.com"
__all__ = []


def read_file(file, step='\t'):

    if file.endswith('.gz'):
        ft = gzip.open(file)
    else:
        ft = open(file)

    for line in ft:
        if type(line) == type(b''):
            line = line.decode('utf-8')
        line = line.strip()

        if not line or line.startswith('#'):
            continue
        yield line.split(step)

    ft.close()


def split_attr(attributes):

    r = OrderedDict()

    for content in attributes.split(';'):
        if not content:
            continue
        if '=' not in content:
            print('%r is not a good formated attribute: no tag!')
            continue
        tag, value = content.split('=', 1)
        r[tag] = value

    return r


def recover_modify(context, site=2, mlen=4):

    msite = len(context)//2
    start = msite-(site-1)
    end = msite-(site-1)+mlen

    return context[start:end]


def class_modify(file, prefix, site=2, mlen=4):

    odict = {}
    r = {}

    for line in read_file(file):
        if line[2]==".":
            mtype = "other"
        else:
            mtype = line[2]
        fo = "%s.%s_motifs.gff" % (prefix, mtype)
        if fo not in odict:
            odict[fo] = open(fo, 'w')
        odict[fo].write("%s\n" % '\t'.join(line))

        attr = split_attr(line[-1])
        mstr = recover_modify(attr["context"], site, mlen)
        if mtype not in r:
            r[mtype] = {}
        if mstr not in r[mtype]:
            r[mtype][mstr] = [[],[],[]]
        r[mtype][mstr][0].append(int(attr["coverage"]))
        r[mtype][mstr][1].append(float(attr["IPDRatio"]))
        if "identificationQv" in attr:
            r[mtype][mstr][2].append(int(attr["identificationQv"]))

    for i in odict:
        odict[i].close()

    return r


def add_help_args(parser):

    parser.add_argument('gff', metavar='FILE', type=str,
        help='Input the methylation modification result file (gff).')
    parser.add_argument('--mlen',  metavar='INT', type=int, default=4,
        help='Input the length of the modified base, default=4')
    parser.add_argument('--site',  metavar='INT', type=int, default=2,
        help='Input the site of the modified base, default=2')
    parser.add_argument('-p', '--prefix', metavar='STR', type=str, default='out',
        help='Input sample name.')

    return parser


def main():

    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
name:
     class_modify.py Statistics modification results

attention:
     class_modify.py motif.gff >stat.motif.tsv

version: %s
contact:  %s <%s>\
    """ % (__version__, " ".join(__author__), __email__))

    args = add_help_args(parser).parse_args()
    r = class_modify(args.gff, args.prefix, args.site, args.mlen)

    print("#Type\tMotif Base\tModified Position\tNumber\tAverage Covearge\tAverage IPDRatio\tAverage Quality")
    for i in r:
        for j in r[i]:
            c, ip, qv = r[i][j]
            mnumber = len(c)
            if len(qv)==mnumber:
                aqv = "{:,.2f}".format(sum(qv)*1.0/mnumber)
            else:
                aqv = "-"
            print("{0}\t{1}\t{2}\t{3:,}\t{4:,.2f}\t{5:,.2f}\t{6}".format(
                i, j, args.site, mnumber, sum(c)*1.0/mnumber, sum(ip)*1.0/mnumber, aqv)
            )


if __name__ == "__main__":

    main()
