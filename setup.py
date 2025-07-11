import setuptools
from packaging.version import Version, InvalidVersion
from importlib import import_module


VERSION = "1.0.0"

with open("README.md", "r") as fh:
    long_description = fh.read()

extras = {
    "gdspy": ("gdspy", "1.6", "pip"),
    "matplotlib": ("matplotlib", "3.2", "conda"),
    "cycler": ("cycler", "0.10", "conda"),
}
extras_require = {k: ">=".join(v[0:2]) for k, v in extras.items()}

install_requires = [
    "numpy>=1.18",
    "pyvista>=0.27",
]

setuptools.setup(
    name="nextnanopy",
    version=VERSION,
    author="nextnano GmbH",
    author_email="python@nextnano.com",
    license="BSD-3-Clause",
    description="Useful tools to interface the nextnano software (https://www.nextnano.com/)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="nextnano",
    url="https://github.com/nextnanopy/nextnanopy",
    packages=setuptools.find_packages(exclude=["tests"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Intended Audience :: Customer Service",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
)

# Code below adapted from QCoDeS (https://qcodes.github.io/)

version_template = """
*****
***** package {0} must be at least version {1}.
***** Please upgrade it (pip install -U {0} or conda install {0})
***** in order to use {2}
***** Recommended method: {3}
*****
"""

missing_template = """
*****
***** package {0} not found
***** Please install it (pip install {0} or conda install {0})
***** Recommended: {2} install {0}
***** in order to use {1}
*****
"""

valueerror_template = """
*****
***** package {0} version not understood
***** Please make sure the installed version ({1})
***** is compatible with the minimum required version ({2})
***** in order to use {3}
*****
"""

othererror_template = """
*****
***** could not import package {0}. Please try importing it from
***** the commandline to diagnose the issue.
*****
"""

# now test the versions of extras
for extra, (module_name, min_version, install_method) in extras.items():
    try:
        module = import_module(module_name.lower())
        try:
            if Version(module.__version__) < Version(min_version):
                print(
                    version_template.format(
                        module_name, min_version, extra, install_method
                    )
                )
        except InvalidVersion:
            print(
                valueerror_template.format(
                    module_name, module.__version__, min_version, extra
                )
            )
    except ImportError:
        print(missing_template.format(module_name, extra, install_method))
    except Exception:
        print(othererror_template.format(module_name))
