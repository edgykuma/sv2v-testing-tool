# sv2v Testing Tool
Tests used to verify `.sv` and their equivalent `.v` files.
Intended for Python 2.7.

## Usage
### TODO: formalize this
Before running the testing script, ensure that the shebang `#!` points to
wherever your `python` install location is.
```
sv2v_test.py [-c in_file] file1 file2 testbench

Usage:
    --check         checks to see if in_file can be run through our tool without
                    any errors. note that file1, file2, and testbench will be
                    ignored.
    file1, file2    path to the input .sv or .v files to compare
    testbench       path to the testbench to compare with
```

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
