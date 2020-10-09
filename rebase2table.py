#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import argparse
import logging

LOG = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "1131978210@qq.com"
__all__ = []


def read_tsv(file):

    for line in open(file):
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        yield line.split("\t")


def rebase2table(file):

    print('#Gene_ID\tRebase_ID\tEnzyme_Type\tEvalue\tScore')
    for line in read_tsv(file):
        types = re.search(r'EnzType:([^;]+)', line[4]).group(1)
        print('{0}\t{1}\t{2}\t{3}\t{4}'.format(line[0], line[1], types, line[-2], line[-1]))


def set_args():

    args = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
Processing rebase database annotation results.

version: %s
contact:  %s <%s>\
    """ % (__version__, " ".join(__author__), __email__))

    args.add_argument("rebase",
        help="Input the rebase database comment result")

    return args.parse_args()


def main():

    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )

    args = set_args()

    rebase2table(args.rebase)


if __name__ == "__main__":
    main()
