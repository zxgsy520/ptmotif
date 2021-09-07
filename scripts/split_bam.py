#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import pysam
import logging
import argparse

LOG = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "invicoun@foxmail.com"
__all__ = []


def split_bam(file, prefix="out", number=2000):

    n = 0
    lb = 0
    fh = pysam.AlignmentFile(file, "rb", check_sq=False)
    name = "%s_r%s.bam" % (prefix, lb)
    fo = pysam.AlignmentFile(name, "wb", template=fh)

    for line in fh:
        fo.write(line)
        n += 1
        if n >= number:
            lb += 1
            fo.close()
            name = "%s_r%s.bam" % (prefix, lb)
            fo = pysam.AlignmentFile(name, "wb", template=fh)
            n = 0
    fh.close()
    fo.close()


def add_hlep_args(parser):

    parser.add_argument('bam', metavar='FILE', type=str,
        help='Input reads file, format(bam).')
    parser.add_argument('-p','--prefix', metavar='STR', type=str, default='out',
        help='Split output file prefix, default=out.')
    parser.add_argument('-n','--number', metavar='INT', type=int, default=20000,
        help='Set the number of reads for each file, default=20000.')

    return parser


def main():

    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
name:
    split_bam.py Split bam according to the number of reads

attention:
    split_bam.py subreads.bam -p txt -n 20000
version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_hlep_args(parser).parse_args()

    split_bam(args.bam, args.prefix, args.number)


if __name__ == "__main__":

    main()
