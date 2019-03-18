#!/usr/bin/python
import sys
import os
import time
import argparse
import subprocess
import shutil
import Verilog_VCD as vcd

# Global constants
##################
VERSION = "1.0.0.2"
# Path to example files, if option --example is passed in
EX_DIR = "examples/"
EX_FILE1 = EX_DIR + "ham.sv"
EX_FILE2 = EX_DIR + "ham.v"
EX_TB    = EX_DIR + "ham_tb.sv"
EX_MOD   = "hamFix_test"
# Time to wait (seconds) before simulation times out
TIMEOUT = 10
# Error codes
NO_FILE_ERR = 1
VCS_COMP_ERR = 2
SIM_TIMEOUT_ER = 3

# Exceptions for raising errors in script
#########################################
# TODO: define possible runtime errors
class NoFileError(Exception):
    pass
class VCSCompileError(Exception):
    pass
class SimTimeoutError(Exception):
    pass

def parse_args():
    parser = argparse.ArgumentParser(description="testing tool for sv2v")
    parser.add_argument("file1",
            help="path to the first Verilog file to compare")
    parser.add_argument("file2",
            help="path to the second Verilog file to compare")
    parser.add_argument("testbench", help="path to the testbench")
    parser.add_argument("-m", "--module",
            help="name of the (top) module to test for equivalence")
    parser.add_argument("--check", dest="in_file",
            help="check if IN_FILE can be processed without errors")
    parser.add_argument("--example", action="store_true", dest="use_example",
            help="run the script using the example files in 'examples'")
    ver_str = "%(prog)s " + VERSION
    parser.add_argument("--version", action="version", version=ver_str)

    return parser.parse_args()

def run_timeout(command):
    proc = subprocess.Popen(command, stdout=outFile, stderr=outFile,
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
        raise SimTimeoutError("simulation timed out")
    return

#TODO
def basic_check():
    return

#TODO
def generate_vcd(hdl_file, tb_file, vcd_name="dump.vcd"):
    dump_opt = "+vcs+dumpvars+test.vcd"
    vcd_cmd = ["vcs", "-sverilog", "-q", "+v2k", hdl_file, tb_file, dump_opt]
    try:
        subprocess.check_call(vcd_cmd)
        subprocess.check_call(["./simv"])
    except CalledProcessError as e:
        exp_str = "compilation failed with code {}. ".format(e.returncode)
        exp_str += "please check output for errors"
        raise VCSCompileError(exp_str)
    except SimTimeoutError:
        raise

#TODO
def compare_vcd(vcd1, vcd2, module):
    # List of the signal hierarchy level that we care about
    siglist = [module]
    vcd_dict1 = vcd.parse_vcd(vcd1, siglist=siglist)
    vcd_dict2 = vcd.parse_vcd(vcd2, siglist=siglist)
    out_str = ""

    is_equivalent = vcd_dict1 == vcd_dict2
    # TODO: ability to print out which values are different, and when
    return (is_equivalent, out_str)

def equiv_check(path1, path2, tb_path, module):
    # Check to see if the files exist
    if not (os.path.isfile(path1)):
        raise NoFileError("no file found in {}".format(path1))
    if not (os.path.isfile(path2)):
        raise NoFileError("no file found in {}".format(path2))
    if not (os.path.isfile(tb_path)):
        raise NoFileError("no file found in {}".format(tb_path))
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
        generate_vcd(path1, tb_path, vcd_name="out1.vcd")
        generate_vcd(path2, tb_path, vcd_name="out2.vcd")
        (is_equivalent, out_str) = compare_vcd("out1.vcd", "out2.vcd", module)
        return is_equivalent
    except (SimTimeoutError, VCSCompileError, KeyboardInterrupt):
        raise
    finally:
        # Cleanup
        os.chdir("..")
        shutil.rmtree(tempdir)

def main():
    # Grab args from the command line
    args = parse_args()
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
        basic_check()

    try:
        is_equiv = equiv_check(file1_path, file2_path, tb_path, module)
        if (is_equiv):
            print("Descriptions are equivalent!")
        else:
            print("Descriptions are not equivalent.")
        return 0
    except NoFileError as e:
        #TODO
        print("NoFileError: " + e)
        return NO_FILE_ERR
    except VCSCompileError as e:
        #TODO
        print("VCSCompileError: " + e)
        return VCS_COMP_ERR
    except SimTimeoutError as e:
        #TODO
        print("SimTimeoutError: " + e)
        return SIM_TIMEOUT_ERR

sys.exit(main())
