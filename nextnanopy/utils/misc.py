import itertools
import os
from pathlib import Path

import numpy as np


def get_filename(fullpath, ext=True):
    filename = os.path.basename(fullpath)
    return filename if ext else os.path.splitext(filename)[0]


def get_file_extension(fullpath):
    return os.path.splitext(fullpath)[1]


def get_folder(fullpath):
    return os.path.dirname(fullpath)


def get_path_files(path):
    if path == "":
        path = "."
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files


def mkdir_if_not_exist(path):
    from pathlib import Path

    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def candidate_names(path):
    """
    Names to try, in order: the requested one first, then name_0, name_1, ...

    Whether any of them is free is not decided here - see savetxt. An index already on the
    name is dropped before counting, so 'ex_0.in' falls back to 'ex_1.in' rather than to
    'ex_0_0.in'.
    """
    yield path
    stem = get_file_prefix(path.name)
    for idx in itertools.count():
        yield path.with_name(f"{stem}_{idx}{path.suffix}")


def savetxt(fullpath, text, overwrite=False, automkdir=True):
    """
    Write text to a file without clobbering an existing one.

    If fullpath is free, it is used as-is. If it is taken, an index is appended to the file
    name and the first free one wins: ex.in, then ex_0.in, ex_1.in, ... Gaps are reused, so a
    folder holding ex.in and ex_1.in gets ex_0.in next.

    Parameters
    ----------
    fullpath : str or Path
        path including the file name where the text should be saved
    text : str
        the content to write
    overwrite : bool, optional
        If True, fullpath is written even if it already exists, and no index is appended
        (default is False)
    automkdir : bool, optional
        If True, the parent folder is created if it does not exist. If False, a missing parent
        raises FileNotFoundError (default is True)

    Returns
    -------
    str
        path of the file that was actually written - not necessarily fullpath, since an index
        may have been appended

    Notes
    -----
    The name is claimed by creating the file, not by checking whether it exists and writing
    afterwards, so two processes saving to the same folder at the same time cannot be handed
    the same name.
    """
    path = Path(fullpath)
    if automkdir:
        path.parent.mkdir(parents=True, exist_ok=True)
    if overwrite:
        path.write_text(text)
        return str(path)
    for candidate in candidate_names(path):
        try:
            # "x" creates the file only if it does not exist, in one atomic step: it is both
            # the existence check and the guard against a racing writer taking the same name.
            with open(candidate, "x") as file:
                file.write(text)
        except FileExistsError:
            continue
        return str(candidate)


def get_file_prefix(file):
    prefix, ext = os.path.splitext(file)
    idx = get_file_idx(prefix)
    if idx > -1:
        prefix = "_".join(prefix.split("_")[0:-1])
    return prefix


def get_file_idx(file):
    prefix, ext = os.path.splitext(file)
    idx = -1
    if "_" in prefix:
        end = prefix.split("_")[-1]
        try:
            idx = int(end)
        except ValueError:
            pass
    return idx


def mkdir_even_if_exists(path, name):
    """
    creates a directory under path with a given name.

    If exists, adds integer number to directory name.
    returns directory full path

    The name is claimed by creating the directory, not by checking whether it exists and creating
    afterwards, so two processes making directories in the same folder at the same time cannot be
    handed the same name.
    """
    directory = os.path.join(path, name)
    for i in itertools.count(-1):
        # -1 yields the bare name first, then name_0, name_1, ...
        if i > 2147483646:
            raise RuntimeError("too many folders with the same name")
        candidate = directory if i < 0 else f"{directory}_{i}"
        try:
            # os.makedirs is atomic: it creates the directory only if it does not exist and
            # raises otherwise, in one step - both the existence check and the guard against a
            # racing process taking the same name.
            os.makedirs(candidate)
        except FileExistsError:
            continue
        return candidate


def combinations(*args):
    n = len(args)
    array_of_combinations = np.array(np.meshgrid(*args)).T.reshape(-1, n)
    return array_of_combinations
