#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import gzip
import logging
import argparse

from collections import OrderedDict

LOG = logging.getLogger(__name__)

__version__ = "1.1.0"
__author__ = ("Xingguo Zhang",)
__email__ = "invicoun@foxmail.com"
__all__ = []


def read_modif_csv(file):

    if file.endswith(".gz"):
        fc = gzip.open(file)
    else:
        fc = open(file)

    r = {}
    head = []
    for line in fc:
        if isinstance(line, bytes):
            line = line.decode('utf-8')
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        line = line.replace('"', '').split(',')
        if line[0] == "refName":
            head = line
            continue
        if line[0] not in r:
            r[line[0]] = OrderedDict()
        if line[1] not in r[line[0]]:
            r[line[0]][line[1]] = {}
        r[line[0]][line[1]][line[2]] = line
    fc.close()

    return head, r


def read_fasta(file):

    '''Read fasta file'''
    if file.endswith(".gz"):
        fp = gzip.open(file)
    elif file.endswith(".fasta") or file.endswith(".fa"):
        fp = open(file)
    else:
        raise Exception("%r file format error" % file)

    seq = []
    for line in fp:
        if isinstance(line, bytes):
            line = line.decode('utf-8')
        line = line.strip()

        if not line:
            continue
        if line.startswith(">"):
            line = line.strip(">")
            if len(seq) == 2:
                yield seq
            seq = []
            seq.append(line.split()[0])
            continue
        if len(seq) == 2:
            seq[1] += line
        else:
            seq.append(line)

    if len(seq) == 2:
        yield seq
    fp.close()


def complement(seq):

    seq = seq.lower()
    seq = seq.replace("a", "T")
    seq = seq.replace("t", "A")
    seq = seq.replace("c", "G")
    seq = seq.replace("g", "C")

    return seq


def add_modif(seqid, site, base, modif):

    site = str(site)
    p = [seqid, site, "0", base, "0", "0", "0", "0", "0", "1"]
    r = [seqid, site, "1", complement(base), "0", "0", "0", "0", "0", "1"]

    if seqid not in modif:
        pass
    elif site not in modif[seqid]:
        pass
    else:
        if "0" in modif[seqid][site]:
            p = modif[seqid][site]["0"]
        if "1" in modif[seqid][site]:
            r = modif[seqid][site]["1"]

    return p, r


def modif_csv2list(genome, modif_csv, outfile, cutseq, tigid="", start=1, end=1000):

    head, dr = read_modif_csv(modif_csv)
    fo = open(outfile, "w")

    fo.write("#refName\ttpl\tstrand\tbase\tipdRatio\tstrand\tbase\tipdRatio\n")
    print(",".join(head))
    for seqid, seq in read_fasta(genome):
        n = 0
        for i in seq:
            n += 1
            p, r = add_modif(seqid, n, i, dr)
            print(",".join(p))
            print(",".join(r))
            if cutseq:
                if tigid != seqid:
                    continue
                if tpl < start:
                    continue
                if tpl > end:
                    continue
            fo.write("{seqid}\t{tpl}\t{ps}\t{pbase}\t{pipd}\t{rs}\t{rbase}\t{ripd}\n".format(
                seqid=seqid,
                tpl=n,
                ps=p[2],
                pbase=p[3],
                pipd=p[8],
                rs=r[2],
                rbase=r[3],
                ripd=r[8])
            )

    return 0


def add_hlep_args(parser):

    parser.add_argument("input", metavar='FILE', type=str,
        help="Input files.")
    parser.add_argument("-g", "--genome", metavar='FILE', type=str, required=True,
        help="Input genome file(fasta).")
    parser.add_argument("-o", "--outfile", metavar='FILE', type=str, default="modifications.tsv",
        help="The name of the output file.")
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
    modif_csv2list　Completion and conversion of output file format

attention:
    modif_csv2list modifications.csv.gz -g genome.fasta -o modifications.tsv >modifications_new.csv
    modif_csv2list modifications.csv.gz -g genome.fasta -o modifications.tsv --tigid tig001 --start  10 --end 1000 --cutseq >modifications_new.csv
version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_hlep_args(parser).parse_args()

    modif_csv2list(args.genome, args.input, args.outfile, args.cutseq, args.tigid, args.start, args.end)


if __name__ == "__main__":

    main()
