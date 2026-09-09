# NEXTNANOPY README

[![BSD-3-Clause](https://img.shields.io/github/license/nextnano-GmbH/nextnanopy)](https://opensource.org/licenses/BSD-3-Clause)
[![Downloads](https://img.shields.io/github/downloads/nextnano-GmbH/nextnanopy/total)](https://github.com/nextnano-GmbH/nextnanopy/releases)

nextnanopy is a Python module to interface the [nextnano](https://www.nextnano.com/) software. This package includes features for:

- **Output files**: User-friendly method to load the datafiles which allows easy and flexible post-processing.
- **Input files:** Load input files, set variables, save by finding unused name, execute the file, write input files, etc.
- **Configuration**: Setup default nextnano configuration (path to executables, databases, licenses, etc).
- **Import from GDS files**: Load polygons from GDS files and user-friendly methods to generate raw text of nextnano shapes (beta).

**Note:** A valid license for the nextnano software is not compulsory for the general use of nextnanopy, unless you would like to execute input files via Python.

## Installation

nextnanopy can be installed on Linux / macOS / Windows. It requires Python >= 3.10.

To install the latest release the standard way, run the following in your Python environment of choice:

```bash
pip install nextnanopy
```

Alternatively, if you want the development version (for Python experts only), clone the GitHub repository into a directory of your choice and install it from there:

```bash
git clone https://github.com/nextnano-GmbH/nextnanopy.git
cd nextnanopy
pip install -e .
```

For details — optional features, a development install from source, and dependencies — see the [installation guide in the nextnanopy documentation](https://www.nextnano.com/docu/nextnanopy/user_guide/index.html#installation).

## Documentation

The basic features are documented as Jupyter notebooks in [docs/examples](docs/examples), best read in order. We recommend every new nextnanopy user to go through Examples 0–2. A short description of what each example covers is on the [tutorials page of the nextnanopy documentation](https://www.nextnano.com/docu/nextnanopy/tutorials/index.html).

Python scripts in [templates/](templates) will help you to start playing with nextnanopy.
More advanced scripts for postprocessing/plotting results of nextnano++ simulations are located in the examples folder of the nextnano++ distribution.

## Support

Do you want to help nextnanopy? Please send an email to [python@nextnano.com](mailto:python@nextnano.com).

## History of changes

Release notes for all published versions are in the [nextnanopy documentation](https://www.nextnano.com/docu/nextnanopy/release_notes/index.html). The section below tracks changes for the next, not-yet-released version; on release, these entries move to the documentation.

## Unreleased changes
