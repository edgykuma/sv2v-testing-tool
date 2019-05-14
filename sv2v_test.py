#!/usr/bin/python
from __future__ import print_function

import sys
import os
import time
import tempfile
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
EX_FILE1        = EX_DIR + "ham.sv"
EX_FILE1_BAD    = EX_DIR + "ham_bad.sv"
EX_FILE2        = EX_DIR + "ham.v"
EX_TB           = EX_DIR + "ham_tb.sv"
EX_MOD          = "hamFix_test"
# Time to wait (seconds) before simulation times out
TIMEOUT = 10
# Error codes
# argparse errors
BAD_ARG_ERR     = 1
# basic test errors
FAIL_BASIC      = 20
# script runtime errors
NO_FILE_ERR     = 10
VCS_COMP_ERR    = 11
SIM_TIMEOUT_ERR = 12
# wtf happened here
UNKNOWN_ERR     = 255

# Exceptions for raising errors in script
#########################################
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

# Function for raising error exceptions
#######################################
def raise_err(err_code, err_params=[]):
    if (err_code == BAD_ARG_ERR):
        if (len(err_params)):
            msg = "{}: error: too few arguments".format(err_params[0])
        else:
            msg = "error: too few arguments"
        raise NotEnoughArgError(msg)
    elif (err_code == SIM_TIMEOUT_ERR):
        raise SimTimeoutError("SimTimeoutError: simulation timed out")
    elif (err_code == VCS_COMP_ERR):
        msg = ""
        if (len(err_params) > 0):
            msg += "{}\n".format(err_params[0])
        msg += "VCSCompileError: compilation failed"
        if (len(err_params) > 1):
            msg += " with code {}".format(err_params[1])
        if (len(err_params) > 0):
            msg += ". Please check output for errors"
        raise VCSCompileError(msg)
    elif (err_code == NO_FILE_ERR):
        msg = "NoFileError: no file found"
        if (len(err_params)):
            msg += " in {}".format(err_params[0])
        raise NoFileError(msg)

def parse_args():
    """Parses the command line for arguments via argparse.
    Will error out if arguments are insufficient.

    Args:
        None

    Returns:
        None
    """
    usage = "%(prog)s [-h] [-v] [-m MODULE] [--check IN_FILE] "
    usage += "file1 file2 testbench"
    parser = argparse.ArgumentParser(description="testing tool for sv2v",
            usage=usage, prog=PROG)
    parser.add_argument("-v", "--verbose", action="store_true",
            help="verbose output")
    parser.add_argument("file1", nargs="?",
            help="path to the first Verilog file to compare")
    parser.add_argument("file2", nargs="?",
            help="path to the second Verilog file to compare")
    parser.add_argument("testbench", nargs="?", help="path to the testbench")
    parser.add_argument("--vcd", nargs=2, help="paths to two VCD files for comparison")
    parser.add_argument("-m", "--module",
            help="name of the (top) module to test for equivalence")
    parser.add_argument("--check", dest="in_file",
            help="check if IN_FILE can be processed without errors")
    parser.add_argument("--ex-pass", action="store_true", dest="use_good",
            help="run the tool to pass using the example files in 'examples'")
    parser.add_argument("--ex-fail", action="store_true", dest="use_bad",
            help="run the tool to fail using the example files in 'examples'")
    ver_str = "%(prog)s " + VERSION
    parser.add_argument("--version", action="version", version=ver_str)

    args = parser.parse_args()
    # Checks to see if any positional arg is missing and not just comparing VCD
    not_enough_args = (args.vcd == None) and \
                      (None in [args.file1, args.file2, args.testbench])
    use_example = args.use_good or args.use_bad
    if (not use_example and args.in_file == None and not_enough_args):
        parser.print_usage(sys.stderr)
        raise_err(BAD_ARG_ERR, (PROG,))
    return args

def run_timeout(command, suppress=True):
    """Run a command with timeout. Suppresses command output by default.

    Args:
        command (str | [str]): command to be passed into subprocess.Popen()

    Returns:
        None
    """
    devnull = open(os.devnull, 'w')
    if (suppress):
        dest = devnull
    else:
        dest = None
    proc = subprocess.Popen(command, stdout=dest, stderr=dest,
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
        raise_err(SIM_TIMEOUT_ERR)
    devnull.close()
    return

def path_make_absolute(file_path, ori_path):
    if (len(file_path) == 0):
        print("ERROR: file path is empty")
        sys.exit(1)
    return "{}/{}".format(ori_path, file_path) if (file_path[0] != '/') else file_path

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
        raise_err(VCS_COMP_ERR, (e.output, e.returncode))
    except SimTimeoutError:
        raise

def generate_vcds(path1, path2, tb_path):
    # Check to see if the files exist
    if not (os.path.isfile(path1)):
        raise_err(NO_FILE_ERR, (path1,))
    if not (os.path.isfile(path2)):
        raise_err(NO_FILE_ERR, (path2,))
    if not (os.path.isfile(tb_path)):
        raise_err(NO_FILE_ERR, (tb_path,))

    try:
        print("Generating VCD files:")
        generate_vcd(path1, tb_path, vcd_name="out1.vcd")
        generate_vcd(path2, tb_path, vcd_name="out2.vcd")
    except (SimTimeoutError, VCSCompileError, KeyboardInterrupt):
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

def get_diff(str1, str2):
    tf1 = tempfile.NamedTemporaryFile()
    tf2 = tempfile.NamedTemporaryFile()
    tf1.write(str1)
    tf1.seek(0)
    tf2.write(str2)
    tf2.seek(0)

    diff_cmd = ["diff", "-y", "--suppress-common-lines", tf1.name, tf2.name]
    try:
        subprocess.check_output(diff_cmd)
        return None     # returncode of 0 means no diffs
    except subprocess.CalledProcessError as e:
        if (e.returncode != 1): # retcode of 1 means there is a diff
            raise
        else:
            return e.output
    finally:
        tf1.close()
        tf2.close()

def compare_vcd(vcd1, vcd2, module, file1, file2):
    col_offset = 10
    # Get size of terminal for pretty printing
    (trow, tcol) = subprocess.check_output(["stty", "size"]).split()
    tcol = int(tcol)
    trow = int(trow)
    cwidth = (tcol - col_offset) // 2       # -4 for column separator
    vcd_dict1 = filter_vcd(vcd.parse_vcd(vcd1), module)
    vcd_dict2 = filter_vcd(vcd.parse_vcd(vcd2), module)
    out_str = ""

    # Check if any signal isn't in both dicts
    diff_keys = set(vcd_dict1.keys()) ^ set(vcd_dict2.keys())
    for key in diff_keys:
        msg = "Warning: "
        if (key in vcd_dict1):      # not in dict2
            msg += "{} is in {}, but not in {}".format(key, file1, file2)
        else:                       # not in dict1
            msg += "{} is in {}, but not in {}".format(key, file2, file1)
        print(msg)
    if (len(diff_keys)):
        print("Netlists cannot be equivalent. Please check your testbench.")
        return (False, out_str)

    is_equivalent = vcd_dict1 == vcd_dict2

    # Feedback on what signals differ
    if (not is_equivalent):
        out_str += "\nSignal value changes not equivalent\n"
        diff_list = []
        # Keys in 1 should be same as keys in 2
        for key in vcd_dict1.keys():
            if (set(vcd_dict1[key]) != set(vcd_dict2[key])):
                diff_list.append(key)
        diff_list = sorted(diff_list)
        out_str += "Inconsistent signals: {}\n\n".format(diff_list)
        if (VERBOSE):
            for key in diff_list:
                out_str += "===== {}: <{}, {}> =====\n".format(key, file1, file2)
                tv1 = ""
                tv2 = ""
                for tv in vcd_dict1[key]:
                    tv1 += "{}\n".format(tv)
                for tv in vcd_dict2[key]:
                    tv2 += "{}\n".format(tv)
                diff_str = get_diff(tv1, tv2)
                if (diff_str != None):
                    out_str += diff_str
                out_str += "\n"
            out_str += "Verbose output may be very long. Recommend outputting "
            out_str += "to a file.\n"
        else:
            out_str += "Run tool with '-v' to see value change dumps\n"
    return (is_equivalent, out_str)

def equiv_check(vcd1, vcd2, module, hdl1, hdl2):
    print("Comparing VCD files...", end="")
    sys.stdout.flush()
    if (hdl1 != None):
        file1 = os.path.basename(hdl1)
    else:
        file1 = vcd1
    if (hdl2 != None):
        file2 = os.path.basename(hdl2)
    else:
        file2 = vcd2
    (is_equivalent, out_str) = compare_vcd(vcd1, vcd2, module, file1, file2)
    print("done")
    return (is_equivalent, out_str)

def main():
    # Grab args from the command line
    try:
        args = parse_args()
    except NotEnoughArgError as e:
        print(e)
        return BAD_ARG_ERR

    global VERBOSE
    VERBOSE = args.verbose
    no_compile = (args.vcd != None)
    vcd_files = args.vcd
    if (args.use_good or args.use_bad):
        file1_path = EX_FILE1 if args.use_good else EX_FILE1_BAD
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
            # Suppress traceback
            sys.exit(1)

    # Create a temp directory for our compilation/simulation
    tempdir = tempfile.mkdtemp()
    ori_dir = os.getcwd()
    os.chdir(tempdir)
    try:
        if (no_compile):
            # Prepend path since we are in the tempdir, only if paths are not absolute
            vcd1 = path_make_absolute(vcd_files[0], ori_dir)
            vcd2 = path_make_absolute(vcd_files[1], ori_dir)
            path1 = None
            path2 = None
            if (module == None):
                print("No top module specified. Defaulting to 'top'.")
                module = "top"
        else:
            path1 = path_make_absolute(file1_path, ori_dir)
            path2 = path_make_absolute(file2_path, ori_dir)
            tb_path = path_make_absolute(tb_path, ori_dir)
            generate_vcds(path1, path2, tb_path)
            vcd1 = "out1.vcd"
            vcd2 = "out2.vcd"
            # Module name is name of tb file, unless otherwise specified
            if (module == None):
                base = os.path.basename(tb_path)
                module = os.path.splitext(base)[0]
                print("No top module specified. Defaulting to '{}'".format(module))

        (is_equiv, out_str) = equiv_check(vcd1, vcd2, module, path1, path2)
        if (is_equiv):
            print("\nDescriptions are equivalent!")
        else:
            print(out_str)
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
    except Exception as e:
        print("an unknown error has occurred:")
        print(e)
        return UNKNOWN_ERR
    finally:
        # Cleanup
        os.chdir(ori_dir)
        shutil.rmtree(tempdir)

sys.exit(main())
