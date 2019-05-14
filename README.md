# sv2v Testing Tool
Tests used to verify `.sv` and their equivalent `.v` files. This tool is used to
help with the behavioral verification of files output by the
[`sv2v`](https://github.com/zachjs/sv2v) tool.

Intended for Python 2.7+.

## Dependencies
The script is run using Python, ver. 2.7+. The only other dependencies for the
script to work are:
- Synopsys's VCS tool, script ver. K-2015.09 and above
- the `diff` program, used in any major Unix system
Please ensure that these dependencies are installed and added to your `PATH`
before using the tool.

## Usage
Before running the testing script, ensure that the shebang `#!` points to
wherever your `python` install location is.
```
usage: sv2v_test.py [-h] [-v] [-m MODULE] [--check IN_FILE] file1 file2 testbench

testing tool for sv2v

positional arguments:
    file1                   path to the first Verilog file to compare
    file2                   path to the second Verilog file to compare
    testbench               path to the testbench

optional arguments:
    -h, --help              show this help message and exit
    -v, --verbose           verbose output
    --vcd VCD VCD           paths to two VCD files for comparison
    -m MODULE, --module MODULE
                            name of the (top) module to test for equivalence
    --check IN_FILE         check if IN_FILE can be processed without errors
    --ex-pass               run the tool to pass using the example files in 'examples'
    --ex-fail               run the tool to fail using the example files in 'examples'
    --version               show program's version number and exit
```

Note that failure to specify the correct module name may lead to a vacuous
success, so ensure that it is correct.

It is worth noting that **this tool relies on your ability to write
testbenches**. It merely checks the VCD (Value Change Dump) files and ensures
all signals in the top level have the same values. *This tool is only as
exhaustive as your testbench allows it to be.*

## Future Work
- get away from relying on Synopsys VCS for compilation
    - `iverilog` seems promising, but lack of support for SV may be problematic
- integrate testing script directly with `sv2v`
- add option to just compare VCD files, without having to compile
- allow arguments to be passed into VCS, and the generated `simv` executable
- more verbose runtime option
- add a minimum to the diff lines printed, for sanity's sake
