#!/usr/bin/env python

import binascii
import mmap
import os

class CSplitB(object):
    def __init__(self, spliton, infile, splitend, number, prefix, suffix):
        spliton_str = binascii.unhexlify(spliton)
        splitend_str = ""
        if splitend is not None:
            splitend_str = binascii.unhexlify(splitend)
        tmp = os.path.splitext(infile)
        if prefix is None:
            prefix = tmp[0] + "_"
        if suffix is None:
            suffix = tmp[1]
        self.spliton_str = spliton_str
        self.splitend_str = splitend_str
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
                    return self.write()
                    break
                else:
                    self.indexes.append(idx)
                    self.last_idx = idx
        return 0
    def write(self):
        number = self.number
        if self.number is None:
            number=len(str(len(self.indexes)))
        number_fmt = "%%0%dd" % number

        count = len(self.indexes)
        if len(self.indexes):
            end_index = -1
            file_written_count = 0
            for i in range(count - 1):
                outfile = self.prefix + (number_fmt % (file_written_count+1) ) + self.suffix
                if self.splitend_str:
                    if self.indexes[i] < end_index:
                        continue
                    end_index=self.mm.find(self.splitend_str,self.indexes[i] + len(self.spliton_str) ) + len(self.splitend_str)
                else:
                    end_index=self.indexes[i+1]
                if end_index > 0:
                    print(self.indexes[i], end_index)
                    self.do_write(self.mm[self.indexes[i]:end_index], outfile)
                    file_written_count += 1
            outfile = self.prefix + (number_fmt % (file_written_count + 1) ) + self.suffix
            if self.splitend_str:
                if self.indexes[count-1] < end_index:
                    return file_written_count
                end_index=self.mm.find(self.splitend_str, self.indexes[count-1] + len(self.spliton_str) ) + len(self.splitend_str)
            else:
                end_index=len(self.mm)
            if end_index > 0:
                self.do_write(self.mm[self.indexes[count-1]:end_index], outfile)
                file_written_count += 1
            return file_written_count

    def do_write(self, data, outfile):
        with open(outfile, "w+b") as f:
            f.write(data)
