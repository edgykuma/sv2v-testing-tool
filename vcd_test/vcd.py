#!/usr/bin/python

import Verilog_VCD as vcd

#file1 = "ham_dump1.vcd"
#file2 = "ham_dump2.vcd"

file1 = "test1.vcd"
file2 = "test2.vcd"

tb_name = "hamFix_test"

parsed1 = vcd.parse_vcd(file1, siglist=[tb_name])
parsed2 = vcd.parse_vcd(file2, siglist=[tb_name])

correct = parsed1 == parsed2
print(correct)
exit(0)
