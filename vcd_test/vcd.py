#!/usr/bin/python

import Verilog_VCD as vcd
import pprint

#file1 = "ham_dump1.vcd"
#file2 = "ham_dump2.vcd"

file1 = "test1.vcd"
file2 = "test2.vcd"

parsed1 = vcd.parse_vcd(file1)
parsed2 = vcd.parse_vcd(file2)

correct = parsed1 == parsed2
print(correct)
if not correct:
    pprint.pprint("file1:")
    pprint.pprint(parsed1)
    pprint.pprint("file2:")
    pprint.pprint(parsed2)
