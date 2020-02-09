#!/usr/bin/env python

import binascii
import mmap
import os

class CSplitB(object):
    def __init__(self, spliton, infile, splitend, start_offset, end_offset, number, prefix, suffix):
        if spliton[0:1] == "/" and spliton[-1] == "/":
            spliton_str=spliton[1:-1]
        else:
            spliton_str = binascii.unhexlify(spliton)
        splitend_str = ""
        if splitend is not None:
            if splitend[0:1] == "/" and splitend[-1] == "/":
                splitend_str=splitend[1:-1]
            else:
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
        self.start_offset = start_offset
        self.end_offset = end_offset
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

        file_written_count = 0
        count = len(self.indexes)
        if len(self.indexes):
            end_index = -1
            for i in range(count - 1):
                outfile = self.prefix + (number_fmt % (file_written_count+1) ) + self.suffix
                if self.indexes[i] + self.start_offset < 0 or self.indexes[i] + self.start_offset > len(self.mm):
                    continue
                if self.splitend_str:
                    if self.indexes[i] + self.start_offset < end_index:
                        continue
                    end_index = self.mm.find(self.splitend_str,self.indexes[i] + len(self.spliton_str))
                    if end_index < 0:
                        continue
                    end_index += len(self.splitend_str) + self.end_offset
                else:
                    end_index=self.indexes[i+1] + self.end_offset

                if end_index < 0 or end_index > len(self.mm):
                    continue
                self.do_write(self.mm[self.indexes[i] + self.start_offset:end_index], outfile)
                file_written_count += 1
            outfile = self.prefix + (number_fmt % (file_written_count + 1) ) + self.suffix
            i = count - 1
            if self.indexes[i] + self.start_offset < 0 or self.indexes[i] + self.start_offset > len(self.mm):
                return file_written_count
            if self.splitend_str:
                if self.indexes[i] + self.start_offset < end_index:
                    return file_written_count
                end_index = self.mm.find(self.splitend_str,self.indexes[i] + len(self.spliton_str))
                if end_index < 0:
                    return file_written_count
                end_index += len(self.splitend_str) + self.end_offset
            else:
                end_index=len(self.mm) # Intentionally ignore self.end_offset for last match

            if end_index < 0 or end_index > len(self.mm):
                return file_written_count
            self.do_write(self.mm[self.indexes[i] + self.start_offset:end_index], outfile)
            file_written_count += 1
        return file_written_count

    def do_write(self, data, outfile):
        with open(outfile, "w+b") as f:
            f.write(data)
