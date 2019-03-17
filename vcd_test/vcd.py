#!/usr/bin/python

import Verilog_VCD as vcd
import pprint

def remove_inner_signals(dump, module_name):
    keys = set()
    # Search all signals if it is part of the top of the specified module
    for key in dump:
        is_bad_key = True   # True if key is not necessary
        for net in dump[key]["nets"]:
            if net["hier"] == module_name:
                is_bad_key = False
        if is_bad_key:
            keys.add(key)

    for key in keys:
        dump.pop(key)
    return None

#file1 = "ham_dump1.vcd"
#file2 = "ham_dump2.vcd"

file1 = "test1.vcd"
file2 = "test2.vcd"

tb_name = "hamFix_test"
verbose = False

parsed1 = vcd.parse_vcd(file1)
parsed1_ori = dict(parsed1)
parsed2 = vcd.parse_vcd(file2)
parsed2_ori = dict(parsed2)

remove_inner_signals(parsed1, tb_name)
remove_inner_signals(parsed2, tb_name)

if verbose:
    print("original parsed1:")
    pprint.pprint(parsed1_ori)
    print("clean parsed1:")
    pprint.pprint(parsed1)

    print("original parsed2:")
    pprint.pprint(parsed2_ori)
    print("clean parsed2:")
    pprint.pprint(parsed2)

correct = parsed1 == parsed2
print(correct)
exit(0)
