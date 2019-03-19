# Verilog\_VCD - Parse a Verilog VCD text file
This document refers to Verilog::VCD version 1.10.

Credit goes to: https://github.com/zylin/Verilog_VCD

## Usage
```python
from Verilog_VCD import parse_vcd
vcd = parse_vcd('/path/to/some.vcd')
```

## Description
Verilog is a Hardware Description Language (HDL) used to model digital logic.
While simulating logic circuits, the values of signals can be written out to
a Value Change Dump (VCD) file.  This module can be used to parse a VCD file
so that further analysis can be performed on the simulation data.  The entire
VCD file can be stored in a Python data structure and manipulated using
standard hash and array operations.  This module is also a good helper for
parsing fsdb files, since you can run fsd2vcd(part of the novas installation)
to convert them to the vcd format and then use this module.

### Input File Syntax
The syntax of the VCD text file is described in the documentation of
the IEEE standard for Verilog.  Only the four-state VCD format is supported.
The extended VCD format (with strength information) is not supported.
Since the input file is assumed to be legal VCD syntax, only minimal
validation is performed.

## Subroutines
### `parse_vcd(file, $opt_ref)`
Parse a VCD file and return a reference to a data structure which
includes hierarchical signal definitions and time-value data for all
the specified signals.  A file name is required.  By default, all
signals in the VCD file are included, and times are in units
specified by the `$timescale` VCD keyword.

```python
vcd = parse_vcd('/path/to/some.vcd')
```

It returns a reference to a nested data structure.  The top of the
structure is a Hash-of-Hashes.  The keys to the top hash are the VCD
identifier codes for each signal.  The following is an example
representation of a very simple VCD file.  It shows one signal named
`chip.cpu.alu.clk`, whose VCD code is `+`.  The time-value pairs
are stored as an Array-of-Tuples, referenced by the `tv` key.  The
time is always the first number in the pair, and the times are stored in
increasing order in the array.

```
{
    '+' : {
        'tv' : [
            (0, '1'),
            (12, '0')
        ],
        'nets' : [
            {
                'hier' : 'chip.cpu.alu.',
                'name' : 'clk',
                'type' : 'reg',
                'size' : '1'
            }
        ]
    }
}
```

Since each code could have multiple hierarchical signal names, the names are
stored as an Array-of-Hashes, referenced by the `nets` key.  The example above
only shows one signal name for the code.

#### Options
Options to `parse_vcd` should be passed as a hash reference.

##### timescale
It is possible to scale all times in the VCD file to a desired timescale.
To specify a certain timescale, such as nanoseconds:

```python
vcd = parse_vcd(file, opt_timescale='ns'})
```

Valid timescales are: `s ms us ns ps fs`

##### siglist
If only a subset of the signals included in the VCD file are needed,
they can be specified by a signal list passed as an array reference.
The signals should be full hierarchical paths separated by the dot
character.  For example:

```python
signals = [
    'top.chip.clk',
    'top.chip.cpu.alu.status',
    'top.chip.cpu.alu.sum[15:0]',
]
vcd = parse_vcd(file, siglist=signals)
```

Limiting the number of signals can substantially reduce memory usage of the
returned data structure because only the time-value data for the selected
signals is loaded into the data structure.

##### use\_stdout
It is possible to print time-value pairs directly to STDOUT for a
single signal using the `use_stdout` option.  If the VCD file has
more than one signal, the `siglist` option must also be used, and there
must only be one signal specified.  For example:

```python
vcd = parse_vcd(file,
                use_stdout=1,
                siglist=['top.clk']
)
```

The time-value pairs are output as space-separated tokens, one per line.
For example:

```
0 x
15 0
277 1
500 0
```

Times are listed in the first column.
Times units can be controlled by the `timescale` option.

##### only\_sigs

Parse a VCD file and return a reference to a data structure which
includes only the hierarchical signal definitions.  Parsing stops once
all signals have been found.  Therefore, no time-value data are
included in the returned data structure.  This is useful for
analyzing signals and hierarchies.

```python
vcd = parse_vcd(file, only_sigs=1)
```


### `list_sigs(file)`
Parse a VCD file and return a list of all signals in the VCD file.
Parsing stops once all signals have been found.  This is
helpful for deciding how to limit what signals are parsed.

Here is an example:

```python
signals = list_sigs('input.vcd')
```

The signals are full hierarchical paths separated by the dot character

```
top.chip.cpu.alu.status
top.chip.cpu.alu.sum[15:0]
```

### `get_timescale()`
This returns a string corresponding to the timescale as specified
by the `$timescale` VCD keyword.  It returns the timescale for
the last VCD file parsed.  If called before a file is parsed, it
returns an undefined value.  If the `parse_vcd` `timescale` option
was used to specify a timescale, the specified value will be returned
instead of what is in the VCD file.

```
vcd = parse_vcd(file); # Parse a file first
ts  = get_timescale();  # Then query the timescale
```

### `get_endtime()`
This returns the last time found in the VCD file, scaled
appropriately.  It returns the last time for the last VCD file parsed.
If called before a file is parsed, it returns an undefined value.

```python
vcd = parse_vcd(file); # Parse a file first
et  = get_endtime();    # Then query the endtime
```

## Export
Nothing is exported by default.  Functions may be exported individually, or
all functions may be exported at once, using the special tag `:all`.

## Diagnostics
Error conditions cause the program to raise an Exception.

## Limitations
Only the following VCD keywords are parsed:

    $end                $scope
    $enddefinitions     $upscope
    $timescale          $var

The extended VCD format (with strength information) is not supported.

The default mode of `parse_vcd` is to load the entire VCD file into the
data structure.  This could be a problem for huge VCD files.  The best solution
to any memory problem is to plan ahead and keep VCD files as small as possible.
When simulating, dump fewer signals and scopes, and use shorter dumping
time ranges.  Another technique is to parse only a small list of signals
using the `siglist` option; this method only loads the desired signals into
the data structure.  Finally, the `use_stdout` option will parse the input VCD
file line-by-line, instead of loading it into the data structure, and directly
prints time-value data to STDOUT.  The drawback is that this only applies to
one signal.

## Bugs
There are no known bugs in this module.

## See also
Refer to the following Verilog documentation:

```
IEEE Standard for Verilog (c) Hardware Description Language
IEEE Std 1364-2005
Section 18.2, "Format of four-state VCD file"
```

## Author
Originally written in Perl by Gene Sullivan (gsullivan@cpan.org)
Translated into Python by Sameer Gauria (sgauria+python@gmail.com)

Plus the following patches :
 - Scott Chin : Handle upper-case values in VCD file.
 - Sylvain Guilley : Fixed bugs in list_sigs.
 - Bogdan Tabacaru : Fix bugs in globalness of timescale and endtime
 - Andrew Becker : Fix bug in list_sigs
 - Pablo Madoery : Found bugs in siglist and opt_timescale features.
 - Matthew Clapp itsayellow+dev@gmail.com : Performance speedup, Exception, print, open, etc cleanup to make the code more robust.
Thanks!

## Copyright and License
Copyright (c) 2012 Gene Sullivan, Sameer Gauria.  All rights reserved.

This module is free software; you can redistribute it and/or modify
it under the same terms as Perl itself.
