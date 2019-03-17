#!/usr/bin/python
import sys
import argparse
import subprocess

# Global constants
VERSION = "0.1.1"
TIMEOUT = 10

def parse_args():
    parser = argparse.ArgumentParser(description="testing tool for sv2v")
    parser.add_argument("file1",
            help="path to the first Verilog file to compare")
    parser.add_argument("file2",
            help="path to the second Verilog file to compare")
    parser.add_argument("testbench", help="path to the testbench")
    parser.add_argument("--check", dest="in_file",
            help="check if in_file can be processed without errors")
    ver_str = "%(prog)s " + VERSION
    parser.add_argument("--version", action="version", version=ver_str)

    return parser.parse_args()

def runTimeout(command):
    outFile =  tempfile.SpooledTemporaryFile()
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

    # read temp streams from start
    outFile.seek(0)
    out = outFile.read()
    outFile.close()
    if(timedOut):
        out = "ERROR: simulation timed out\n\n" + out
    return out

def main():
    args = parse_args()
    # TODO: write functionality with sv2v tool
    return 0

sys.exit(main())
