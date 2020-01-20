#!/usr/bin/env python

import binascii
import mmap
import os

class CSplitB(object):
    def __init__(self, spliton, infile, number, prefix, suffix):
        spliton_str = binascii.unhexlify(spliton)
        tmp = os.path.splitext(infile)
        if prefix is None:
            prefix = tmp[0] + "_"
        if suffix is None:
            suffix = tmp[1]
        self.spliton_str = spliton_str
        self.infile = infile
        self.number = number
        self.prefix = prefix
        self.suffix = suffix
        self.count = 0
        self.last_idx = -1
        self.indexes = []
    def run(self):
        with open(self.infile, "r+b") as f:
            self.mm = mmap.mmap(f.fileno(), 0)
            while True:
                idx = self.mm.find(self.spliton_str, self.last_idx + 1)
                if idx == -1:
                    self.write()
                    break
                else:
                    self.indexes.append(idx)
                    self.last_idx = idx

    def write(self):
        number = self.number
        if self.number is None:
            number=len(str(len(self.indexes)))
        number_fmt = "%%0%dd" % number

        count = len(self.indexes)
        if len(self.indexes):
            for i in range(count - 1):
                outfile = self.prefix + (number_fmt % (i+1) ) + self.suffix
                self.do_write(self.mm[self.indexes[i]:self.indexes[i+1]], outfile)
            outfile = self.prefix + (number_fmt % count ) + self.suffix
            self.do_write(self.mm[self.indexes[count-1]:], outfile)

    def do_write(self, data, outfile):
        with open(outfile, "w+b") as f:
            f.write(data)
