#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import gzip
import logging
import argparse


LOG = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "invicoun@foxmail.com"
__all__ = []



def read_csv(file):

    if file.endswith(".gz"):
        fc = gzip.open(file)
    else:
        fc = open(file)

    n = 0
    head = ""
    for line in fc:
        if isinstance(line, bytes):
            line = line.decode('utf-8')
        line = line.strip().replace('"', '')
        if not line:
            continue
        line  = line.split(',')
        if n == 0:
            head = line
        else:
            yield [head, line, n]
        n += 1
    fc.close()

    return 0


def modif_csv2list(file, cutseq, tigid="", start=1, end=1000):

    print("#refName\ttpl\tstrand\tbase\tipdRatio\tstrand\tbase\tipdRatio")
    for head, line, n in read_csv(file):
        seqid, tpl, strand, base = line[0], int(line[1]), int(line[2]), line[3]
        ipdratio, coverage = float(line[8]), int(line[9])

        if cutseq:
            if tigid != seqid:
                continue
            if tpl < start:
                continue
            if tpl > end:
                break
        if strand == 0:
            temp = [seqid, str(tpl), str(strand), base, '%.3f'%ipdratio]
            continue
        if strand == 1:
            temp += [str(strand), base, '%.3f'%ipdratio]
        print("\t".join(temp))

    return 0


def add_hlep_args(parser):

    parser.add_argument("input", metavar='FILE', type=str,
        help="Input files.")
    parser.add_argument("-id", "--tigid", metavar='STR', type=str, default='',
        help="Input sequence id, default=''.")
    parser.add_argument("-s", "--start", metavar='INT', type=int, default=0,
        help="Input start position, default=0.")
    parser.add_argument("-e", "--end", metavar='INT', type=int, default=1000,
        help="Input end position, default=1000.")
    parser.add_argument("--cutseq", action="store_true",
        help="Intercept part of the data.")

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
    modif_csv2list

attention:
    modif_csv2list WP3NRDnd1.modifications.csv.gz >WP3NRDnd1.modifications.tsv
    modif_csv2list WP3NRDnd1.modifications.csv.gz --tigid tig001 --start  10 --end 1000 --cutseq  >WP3NRDnd1.modifications.tsv
version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_hlep_args(parser).parse_args()

    modif_csv2list(args.input, args.cutseq, args.tigid, args.start, args.end)


if __name__ == "__main__":

    main()
