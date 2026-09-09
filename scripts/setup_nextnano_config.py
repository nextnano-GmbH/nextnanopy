"""
Write the nextnanopy config for the extracted nextnano++ portable build.

The portable build unpacks into a folder whose name is the release date (e.g.
``2026_07_03``), so it changes with every release and cannot be hardcoded. This
locates the install by globbing for the ``nextnano++`` subfolder under the
extraction directory, then points the nextnanopy config at its executable,
database and license. Only the nextnano++ product is configured.

**Environment**

NEXTNANO_PORTABLE_DIR
    Directory the portable build was extracted into (default: ``nextnano``).
NEXTNANO_OUTPUT_DIR
    Directory for simulation output (default: ``nextnano_output``). Created if
    absent.
"""

import os
from pathlib import Path

import nextnanopy as nn


def find_one(root: Path, pattern: str, what: str) -> Path:
    """
    Return the single glob match for `pattern` under `root`, newest last.

    Raises SystemExit with a readable message if nothing matches, so the CI
    step fails loudly instead of writing an empty path into the config.
    """
    matches = sorted(root.glob(pattern))
    if not matches:
        raise SystemExit(f"no {what} matching {pattern!r} under {root}")
    return matches[-1]


base = Path(os.environ.get("NEXTNANO_PORTABLE_DIR", "nextnano")).resolve()

# Discover the versioned install by its nextnano++ subfolder rather than naming
# the release-date directory. sorted()[-1] picks the newest if several coexist:
# the date is in the path and YYYY_MM_DD sorts chronologically.
nnp_dir = find_one(base, "**/nextnano++", "nextnano++ folder")
path_exe = find_one(nnp_dir, "bin 32bit/nextnano++*.exe", "nextnano++ executable")
path_database = find_one(nnp_dir, "database/database_free.nnp", "nextnano++ database")
# The license is not under nextnano++/, so search the whole extraction tree.
path_license = find_one(base, "**/License_free.lic", "nextnano++ license")

path_output = Path(os.environ.get("NEXTNANO_OUTPUT_DIR", "nextnano_output")).resolve()
path_output.mkdir(parents=True, exist_ok=True)

nn.config.to_default()  # start from the defaults, then override nextnano++

nn.config.set("nextnano++", "exe", str(path_exe))
nn.config.set("nextnano++", "database", str(path_database))
nn.config.set("nextnano++", "license", str(path_license))
nn.config.set("nextnano++", "outputdirectory", str(path_output))

nn.config.save()

print(f"nextnano++ exe:      {path_exe}")
print(f"nextnano++ database: {path_database}")
print(f"nextnano++ license:  {path_license}")
print(f"output directory:    {path_output}")
print(f"config saved to:     {nn.config.fullpath}")
