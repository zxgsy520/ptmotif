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

__version__ = "v1.2.0"
__author__ = ("Xingguo Zhang",)
__email__ = "113178210@qq.com"
__all__ = []


class gff_record(object):

    #__slots__ = ["seqid", "source", "type", "start", "end", "score", strand, phase, attrs]
    def __init__(self, seqid, source, type, start, end, score, strand, phase, attrs):
        try:
            assert '\n' not in seqid
            assert '\n' not in source
            assert '\n' not in type
            assert '\n' not in start
            assert '\n' not in end
            assert '\n' not in score
            assert '\n' not in strand
            assert '\n' not in phase
            assert '\n' not in attrs
        except AssertionError:
            raise ValueError('Invalid GFF record data')

        self.seqid = seqid
        self.source = source
        self._type = type
        self.start = int(start)
        self.end = int(end)
        assert self.start <= self.end, '%s %s %s' % (self.seqid, self.start, self.end)
        #self.length = self.end-self.start+1
        self.score = score
        self.strand = strand
        self.phase = phase
        self._attrs = attrs
        self.attributes = self._split_attr(attrs)

    @property
    def length(self):
        return self.end - self.start + 1


    def _split_attr(self, attributes):
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


    def to_string(self):
        attr = []
        for key, value in self.attributes.items():
            if key in "ID":
                attr.insert(0, '%s=%s' % (key, value))
            else:
                attr.append('%s=%s' % (key, value))
        r = '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (self.seqid, self.source, self._type, self.start, self.end, self.score, self.strand, self.phase, ';'.join(attr))
        return r


    @property
    def type(self):
        return self._type


    @type.setter
    def type(self, s):
        self._type = s


    @classmethod
    def from_string(cls,s):
        try:
            assert '\n' not in s
            parts = s.split('\t')
            assert len(parts) == 9
            seqid, source, type, start, end, score, strand, phase, attributes = parts
           # assert strand in "+-"
        except AssertionError:
            raise ValueError('%r not recognized as a valid GFF record' % s)

        return gff_record(seqid, source, type, start, end, score, strand, phase, attributes)


def read_gff(file):

    if file.endswith('.gz'):
        fp = gzip.open(file)
    else:
        fp = open(file)

    for line in fp:
        if type(line) == type(b''):
            line = line.decode('utf-8')
        line = line.strip()

        if not line or line.startswith('#'):
            continue
        yield gff_record.from_string(line)

    fp.close()


def match_motif(context, ptbase, ptsite=1):

    nbase = False
    length = len(context)
    start = length//2-ptsite+1
    end = length//2+len(ptbase)+1-ptsite

    if context[start:end]==ptbase:
        nbase = context[start-1:end+1]

    return nbase


def motifs2pt(file, ptbase, ptsite=1, coverage=10, ipdratio=1):

    data = {}

    for line in read_gff(file):
        if line.type=='.' or 'context' not in line.attributes:
            continue
        if 'motif' in line.attributes:
            continue
        if float(line.attributes['coverage']) < coverage or float(line.attributes['IPDRatio']) < ipdratio:
            continue

        context = line.attributes['context']
        around = match_motif(context, ptbase, ptsite)

        if around:
            print(gff_record.to_string(line))
            if around not in data:
                data[around] = 0
            data[around] +=  1

    total = 0
    fp = open('stat_pt_around.tsv' , 'w')
    fp.write('##Statistics of base distribution before and after modification\n')
    fp.write('#Dase\tNumber\n')
    for i in data:
        fp.write('%s\t%s\n' % (i, data[i]))
        total += data[i]
    fp.write('#Total modif\t%s\n' % total)
    fp.close()


def add_help_args(parser):

    parser.add_argument('gff', 
        help='Input the methylation modification result file (gff).')
    parser.add_argument('-ptb', '--ptbase',  metavar='SRT', type=str, required=True,
        help='Input PT modified base type.')
    parser.add_argument('-pts', '--ptsite',  metavar='INT', type=int, default=2,
        help='Input the position of the PT modification on the modified base (starting from 1); default=2.')
    parser.add_argument('--coverage',  metavar='INT', type=int, default=10,
        help='Modified base coverage; default=10.')
    parser.add_argument('-ipd', '--ipdratio',  metavar='FLOAT', type=float, default=1,
        help='Modified base IPDRatio; default=1.')

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
     motifs2pt.py Extraction of PT modifications from base modification results

attention:
     motifs2pt.py motif.gff --ptbase GATC --ptsite 1 --coverage 5 --ipdratio 0.5 >pt.gff

version: %s
contact:  %s <%s>\
    """ % (__version__, " ".join(__author__), __email__))

    args = add_help_args(parser).parse_args()

    motifs2pt(args.gff, args.ptbase, args.ptsite, args.coverage, args.ipdratio)


if __name__ == "__main__":

    main()
