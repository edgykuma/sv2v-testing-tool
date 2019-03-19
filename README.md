# sv2v Testing Tool
Tests used to verify `.sv` and their equivalent `.v` files.
Intended for Python 2.7.

## Usage
### TODO: formalize this
Before running the testing script, ensure that the shebang `#!` points to
wherever your `python` install location is.
```
sv2v_test.py [-h] [-v] [-m MODULE] [--check IN_FILE] [--ex-pass] [--ex-fail] [--version] file1 file2 testbench

testing tool for sv2v

positional arguments:
  file1                 path to the first Verilog file to compare
  file2                 path to the second Verilog file to compare
  testbench             path to the testbench

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose output
  -m MODULE, --module MODULE
                        name of the (top) module to test for equivalence
  --check IN_FILE       check if IN_FILE can be processed without errors
  --ex-pass             run the tool to pass using the example files in
                        'examples'
  --ex-fail             run the tool to fail using the example files in
                        'examples'
  --version             show program's version number and exit

sv2v_test.py [-c in_file] file1 file2 testbench
```

Note that failure to specify the correct module name may lead to a vacuous
success, so ensure that it is correct.

It is worth noting that **this tool relies on your ability to write
testbenches**. It merely checks the VCD (Value Change Dump) files and ensures
all signals in the top level have the same values. This tool is only as
exhaustive as your testbench allows it to be.

## Specification
List is informal, and will need to be refined later on.
- test if tool can parse file with no errors
- verify functionality for `.sv` file, then with equivalent `.v` file, then
  compare their TB outputs to check for equivalent behavior
    - process to do this: `vcs` with `.sv`, `vcs` with `.v`, then compare
