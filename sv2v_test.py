#!/usr/bin/python
from __future__ import print_function

import sys
import os
import time
import argparse
import subprocess
from subprocess import CalledProcessError
import shutil
import Verilog_VCD as vcd

# Global constants
##################
PROG = "sv2v_test.py"
VERSION = "1.0.0"
# Path to example files, if option --example is passed in
EX_DIR = "examples/"
EX_FILE1 = EX_DIR + "ham.sv"
EX_FILE2 = EX_DIR + "ham.v"
EX_TB    = EX_DIR + "ham_tb.sv"
EX_MOD   = "hamFix_test"
# Time to wait (seconds) before simulation times out
TIMEOUT = 10
# Error codes
# argparse errors
BAD_ARG_ERR = 1
# basic test errors
FAIL_BASIC = 20
# script runtime errors
NO_FILE_ERR = 10
VCS_COMP_ERR = 11
SIM_TIMEOUT_ERR = 12

# Exceptions for raising errors in script
#########################################
# TODO: define possible runtime errors
class NotEnoughArgError(Exception):
    pass
class BasicCheckError(Exception):
    pass
class NoFileError(Exception):
    pass
class VCSCompileError(Exception):
    pass
class SimTimeoutError(Exception):
    pass

def parse_args():
    usage = "%(prog)s [-h] [-m MODULE] [--check IN_FILE] [--example] "
    usage += "[--version] file1 file2 testbench"
    parser = argparse.ArgumentParser(description="testing tool for sv2v",
            usage=usage, prog=PROG)
    parser.add_argument("file1", nargs="?",
            help="path to the first Verilog file to compare")
    parser.add_argument("file2", nargs="?",
            help="path to the second Verilog file to compare")
    parser.add_argument("testbench", nargs="?", help="path to the testbench")
    parser.add_argument("-m", "--module",
            help="name of the (top) module to test for equivalence")
    parser.add_argument("--check", dest="in_file",
            help="check if IN_FILE can be processed without errors")
    parser.add_argument("--example", action="store_true", dest="use_example",
            help="run the script using the example files in 'examples'")
    ver_str = "%(prog)s " + VERSION
    parser.add_argument("--version", action="version", version=ver_str)

    args = parser.parse_args()
    # Checks to see if any positional arg is missing
    not_enough_args = None in [args.file1, args.file2, args.testbench]
    if (not args.use_example and args.in_file == None and not_enough_args):
        parser.print_usage(sys.stderr)
        raise NotEnoughArgError("{}: error: too few arguments".format(PROG))
    return args

def run_timeout(command):
    devnull = open(os.devnull, 'w')
    proc = subprocess.Popen(command, stdout=devnull, stderr=devnull,
            preexec_fn=os.setsid)
    # Time to wait until timeout, in seconds
    wait_remaining_sec = TIMEOUT;
    timedOut = False;

    # Wait for either simulation end or timeout
    while proc.poll() is None and wait_remaining_sec > 0:
        time.sleep(1)
        wait_remaining_sec -= 1

    if wait_remaining_sec <= 0:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        timedOut = True

    if(timedOut):
        devnull.close()
        raise SimTimeoutError("SimTimeoutError: simulation timed out")
    devnull.close()
    return

#TODO
def basic_check():
    print("basic check not currently supported :(")
    return

def generate_vcd(hdl_file, tb_file, vcd_name="dump.vcd"):
    hdl_base = os.path.basename(hdl_file)
    tb_base = os.path.basename(tb_file)
    dump_opt = "+vcs+dumpvars+" + vcd_name
    vcd_cmd = ["vcs", "-sverilog", "-q", "+v2k", hdl_file, tb_file, dump_opt]
    try:
        print("\tCompiling {}...".format(hdl_base), end="")
        sys.stdout.flush()
        subprocess.check_output(vcd_cmd)
        print("done")
        print("\tRunning sim for {}...".format(tb_base), end="")
        sys.stdout.flush()
        run_timeout(["./simv"])
        print("done")
    except CalledProcessError as e:
        exp_str = e.output + "\nVCSCompileError: "
        exp_str += "compilation failed with code {}. ".format(e.returncode)
        exp_str += "please check output for errors"
        raise VCSCompileError(exp_str)
    except SimTimeoutError:
        raise

def filter_vcd(vcd_dict, top):
    new_vcd = dict()
    for key in vcd_dict:
        tv = vcd_dict[key]["tv"]
        for net in vcd_dict[key]["nets"]:
            if (net["hier"] == top):    # If it is a signal we care about
                sig_name = "{}.{}".format(net["hier"], net["name"])
                new_vcd[sig_name] = tv
    return new_vcd

def compare_vcd(vcd1, vcd2, module):
    vcd_dict1 = filter_vcd(vcd.parse_vcd(vcd1), module)
    vcd_dict2 = filter_vcd(vcd.parse_vcd(vcd2), module)
    out_str = ""

    is_equivalent = vcd_dict1 == vcd_dict2
    # TODO: ability to print out which values are different, and when
    return (is_equivalent, out_str)

def equiv_check(path1, path2, tb_path, module):
    # Check to see if the files exist
    if not (os.path.isfile(path1)):
        raise NoFileError("NoFileError: no file found in {}".format(path1))
    if not (os.path.isfile(path2)):
        raise NoFileError("NoFileError: no file found in {}".format(path2))
    if not (os.path.isfile(tb_path)):
        raise NoFileError("NoFileError: no file found in {}".format(tb_path))
    # Create a temp directory for our compilation/simulation
    # Remove previous temp dir, just in case it still exists
    tempdir = "__sv2v_temp"
    shutil.rmtree(tempdir, ignore_errors=True)
    os.mkdir(tempdir)
    os.chdir(tempdir)
    # Prepend "../" since we are in the tempdir, only if paths are not absolute
    path1 = "../" + path1 if (path1[0] != '/') else path1
    path2 = "../" + path2 if (path2[0] != '/') else path2
    tb_path = "../" + tb_path if (tb_path[0] != '/') else tb_path

    # Module name is name of tb file, unless otherwise specified
    if (module == None):
        base = os.path.basename(tb_path)
        module = os.path.splitext(base)[0]

    try:
        print("Generating VCD files:")
        generate_vcd(path1, tb_path, vcd_name="out1.vcd")
        generate_vcd(path2, tb_path, vcd_name="out2.vcd")
        print("Comparing VCD files...", end="")
        sys.stdout.flush()
        (is_equivalent, out_str) = compare_vcd("out1.vcd", "out2.vcd", module)
        print("done")
        return is_equivalent
    except (SimTimeoutError, VCSCompileError, KeyboardInterrupt):
        raise
    finally:
        # Cleanup
        os.chdir("..")
        shutil.rmtree(tempdir)

def main():
    # Grab args from the command line
    try:
        args = parse_args()
    except NotEnoughArgError as e:
        print(e)
        return BAD_ARG_ERR
    use_example = args.use_example
    if (use_example):
        file1_path = EX_FILE1
        file2_path = EX_FILE2
        tb_path = EX_TB
        module = EX_MOD
    else:
        file1_path = args.file1
        file2_path = args.file2
        tb_path = args.testbench
        module = args.module
    # TODO: write functionality with sv2v tool
    checkfile_path = args.in_file
    if (checkfile_path != None):
        try:
            basic_check()
            return 0
        except BasicCheckError as e:
            print(e)
            return FAIL_BASIC
        except KeyboardInterrupt:
            sys.exit(1)

    try:
        is_equiv = equiv_check(file1_path, file2_path, tb_path, module)
        if (is_equiv):
            print("\nDescriptions are equivalent!")
        else:
            print("\nDescriptions are not equivalent.")
        return 0
    except NoFileError as e:
        print(e)
        return NO_FILE_ERR
    except VCSCompileError as e:
        print(e)
        return VCS_COMP_ERR
    except SimTimeoutError as e:
        print(e)
        return SIM_TIMEOUT_ERR
    except KeyboardInterrupt:
        sys.exit(1)

sys.exit(main())
