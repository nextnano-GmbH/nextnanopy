"""Command line access to the nextnano configuration file.

Installed as the ``nextnanopy-config`` command.
"""

import argparse

from nextnanopy.defaults import config_default_path, get_config

_NEXT_STEPS = (
    "Fill in 'exe', 'license', 'database' and 'outputdirectory' for the products you have "
    "installed, either by editing that file or from Python with nextnanopy.config.set(...) "
    "followed by nextnanopy.config.save()."
)


def main(argv=None):
    """Create the configuration file if it is missing and report where it is.

    Parameters
    ----------
    argv : list of str, default=None
        Command line arguments. ``sys.argv[1:]`` is used when omitted.

    Returns
    -------
    int
        Exit status, ``0`` on success. It is returned rather than raised so that the
        console-script wrapper can hand it to `sys.exit`.

    Notes
    -----
    The first line of the output is the path to the configuration file and nothing else,
    so a shell script can read it with ``nextnanopy-config | head -1``.

    Creating a missing file is what first use of `nextnanopy.config` does anyway; this
    only makes it an explicit step for a user who has yet to write any Python. An
    existing file is left untouched unless ``--reset`` is given, which overwrites every
    option with the shipped defaults and so discards the paths configured there.
    """
    parser = argparse.ArgumentParser(
        prog="nextnanopy-config",
        description=(
            "Create the nextnanopy configuration file with the default values if it does "
            "not exist yet, and print where it is."
        ),
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="print every section with its options and their values",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="overwrite every option with the shipped defaults, discarding configured paths",
    )
    args = parser.parse_args(argv)

    # Asked before get_config(), which is what writes the file when it is missing.
    existed = config_default_path.is_file()
    config = get_config()
    if args.reset:
        config.reset()

    print(config.fullpath)
    if args.reset:
        print("reset to the defaults nextnanopy ships.")
    elif existed:
        print("already exists, left as it is.")
    else:
        print("created with the defaults nextnanopy ships.")
    if args.reset or not existed:
        print(_NEXT_STEPS)

    if args.show:
        print()
        config.preview()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
