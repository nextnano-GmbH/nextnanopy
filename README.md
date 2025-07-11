# NEXTNANOPY README

[![BSD-3-Clause](https://img.shields.io/github/license/nextnanopy/nextnanopy)](https://opensource.org/licenses/BSD-3-Clause)
[![Downloads](https://img.shields.io/github/downloads/nextnanopy/nextnanopy/total)](https://github.com/nextnanopy/nextnanopy/releases)

nextnanopy is a Python module to interface the [nextnano](https://www.nextnano.com/) software. This package includes features for:

- **Output files**: User-friendly method to load the datafiles which allows easy and flexible post-processing.
- **Input files:** Load input files, set variables, save by finding unused name, execute the file, write input files, etc.
- **Configuration**: Setup default nextnano configuration (path to executables, databases, licenses, etc).
- **Import from GDS files**: Load polygons from GDS files and user-friendly methods to generate raw text of nextnano shapes (beta).

**Note:** A valid license for the nextnano software is not compulsory for the general use of nextnanopy, unless you would like to execute input files via Python.

## Future of nextnanopy

Currently, nextnanopy has basic features for [nextnano products](https://www.nextnano.com/products/products.php) nextnano++, nextnano³, nextnano.NEGF and nextnano.MSB.

In future releases, we would like to implement:

- **Common post-processing methods**: Like loading and plotting together bandedges, eigenenergies and eigenvalues, colormap of potential landscape with GDS polygons on top, etc.
- **User-friendly input file creation/modification**: The idea is to load any input file and it would detect all the different blocks so the user can easily modify parameters like 'boundary conditions' or 'region material'. Similarly, it should be user-friendly to create any input file from scratch via Python.
- **Feedback loops**: A routine that allows the user to optimize any figure of merit of a device with a given set of input variables. The user can set a post-processing routine to get the figure of merit from the simulated data and later, a new set of input variables will be generated and executed. This feedback loop will repeat until a set of conditions are satisfied.
- **Guidelines for contributors**: Set of rules if you want to contribute to the project.

## Installation

Nextnanopy can be installed on Linux / OS X / Windows.
For details, please refer to docs/How to install nextnanopy.md.

## Documentation

Basic features are documented in docs/examples.
Python scripts in templates/ will help you to start playing with nextnanopy.

## Support

Do you want to help nextnanopy? Please send an email to [python@nextnano.com](mailto:python@nextnano.com).

## History of changes

### Version 1.0.0 (Jul 11th, 2025)

- support of python3.13
- NEGF renamed to NEGF_classic (requires .nextnanopy-config update)
- NEGF++ renamed to NEGF (requires .nextnanopy-config update)

### Version 0.1.22 (May 7th, 2024)

- improved Dat loader

### Version 0.1.21 (Feb 28th, 2024)

- Added DataFile loader for total_charges.txt
- nextnanopy now supports python3.11

### Version 0.1.20 (Dec 13th, 2023)

- nextnanopy is aligned to be used with nextnanoevo. nextnanoevo will be released in 2024

### Version 0.1.19 (Jul 21st, 2023)

- new feature: saving DataFile: DataFile.save
- new feature: DataFolder.find_multiple - search files by multiple keywords
- new property DataFolder.name - return the basename of the folder

### Version 0.1.18 (Jul 04th, 2023)

- new product available: nextnano.NEGF++
- setting the text for InputFile is available again (but switching product when setting text os forbidden)
- interface with .gds files is extended

### Version 0.1.17 (Jun 07th, 2023)

- fixed a bug with nnp.shapes.GdsPolygons.get_obelisks
- get_obelisks can be used again. The usage is deprecated, nnp.shapes.GdsPolygons.get_polygonal_prisms is prefered way to convert gds to nextnano++ structure

### Version 0.1.16 (Apr 25th, 2023)

- nextnanopy now supports python 3.10!
- The execute_sweep function has been updated to include a new parameter, separate_sweep_dir, which allows the user to specify whether the output files should be saved in a separate directory or a common output directory.
  By default, execute_sweep will still create a separate output directory for each sweep. However, if the user sets separate_sweep_dir to False, the output files will be saved in a common output directory instead.
- ListDict now supports negative indexes (in the same way as a normal python list)
- nnpp assistant is updated
- shapely is no longer necessary to import geometry from gdsii file

### Version 0.1.15 (Aug 31st, 2022)

- input files now can be executed in parallel through nextnanopy.inputs.ExecutionQueue class
- Sweep uses ExecutionQueue and executes several simulations in parallel if parallel_limit>1 in Sweep.execute_sweep(parallel_limit = n)

### Version 0.1.14 (Jul 27th, 2022)

- nextnanopy.Sweep.save_sweep has parameter round_decimal to limit round of digits in the folder names. Deafault round_decimal = 8

### Version 0.1.13 (Jun 13th, 2022)

- Default .dat loader of nextnanopy.DataFile was changed. Before x,y,z and position were coordinates, anything else recognized as variables. Now first column of the '.dat' file is recognized as coordinate, all other columns are variables.
- Demo: parser of the whole input file for nextnano++. Raise error if file contains incorrect number and order of parentheses '{}'

### Version 0.1.12 (Mar 14th, 2022)

- added support of input variables for nextnanoNEGF. Note: after save all non-xml data (i.e. comments) is not preserved.

### Version 0.1.11 (Jan 10th, 2022)

- Feature: DataFile.plot() - make a preview plot. Graph for 1-dimensional data and a colormap for 2-dimensional data.
- Feature: New class DataFolder. Designed to simplify navigation in output directory.
- Beta feature: postprocess.simple_optimize. Runs simulation over given variables space and optimizes the desired output value.

### Version 0.1.10 (Oct 06th, 2021)

- Feature: Added new class Sweep allowing to create automatic sweeps over few variables

### Version 0.1.9 (Dec 16th, 2020)

- Feature: InputFile.execute has now show_log (True or False) to turn on/off the log. Note: the log file is always saved.
- Removed default messages when saving an input file

### Version 0.1.8 (Dec 14th, 2020)

- Buf fix: find unused name when saving input file

### Version 0.1.7 (Dec 3rd, 2020)

- docstring for inputs.py, outputs.py, config.py, mycollections.py, datasets.py
- Updated examples in docs/examples/

### Version 0.1.6 (Dec 2nd, 2020)

- Feature: [DataFile] access with index to coordinates and to variables

```python
df = nextnanopy.DataFile(...)
df['x'] # same as df.coords['x']
df['Gamma'] # same as df.variables['Gamma']
```

- Feature: [DataFile] is loopable as well as .coords and .variables
- Feature: [InputFile] access with index to input variables

```python
df = nextnanopy.InputFile(...)
df['xmax'] # same as df.variables['xmax']
```

- Feature: [InputFile] is loopable as well as .coords and .variables
- Feature: [InputFile] extra attributes

```python
df = nextnanopy.InputFile(...)
df.folder_output # returns the output folder if it was executed, otherwise it raises an error
df.filename      # settable
df.filename_only # settable
df.folder_input  # settable
```

- Feature: User-friendly information for DataFile, InputFile, Variable, Coord and InputVariable
- Bug fix: .vtr dataset reshape method

### Version 0.1.5 (Dec 2nd, 2020)

- Feature: Support of .vtr data files
- Feature: If unit is not found, default value is 'a.u.'.
- Bug fix: Better methods to find correctly name and unit from data file headers

### Version 0.1.4 (Nov 29th, 2020)

- Feature: Create an empty input file and set the raw text with the attribute text.

### Version 0.1.3 (Nov 28th, 2020)

- Bug fix: Find unused name when save input files.
- Feature: Default label for Variables and Coords. The attribute label returns "name (unit)".

### Version 0.1.2 (Nov 20th, 2020)

- Bug fix: Raw text of input variables without comment was generated incorrectly.

### Version 0.1.1 (Nov 18th, 2020)

- Bug fix: Find the home path for OSX and Linux.

### Version 0.1.0 (Nov 13th, 2020)

- Initial release
