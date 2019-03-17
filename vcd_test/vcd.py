#!/usr/bin/python

import Verilog_VCD as vcd

file1 = "ham_dump1.vcd"
file2 = "ham_dump2.vcd"

parsed1 = vcd.parse_vcd(file1)
parsed2 = vcd.parse_vcd(file2)

correct = parsed1 == parsed2
print(correct)
#if not correct:
#    print("file1:")
#    print(parsed1)
#    print("file2:")
#    print(parsed2)
