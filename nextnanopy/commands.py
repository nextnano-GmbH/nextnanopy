import queue
import subprocess
import sys
import threading
import warnings
from pathlib import Path

from nextnanopy import defaults
from nextnanopy.utils.formatting import generate_command
from nextnanopy.utils.misc import mkdir_even_if_exists, mkdir_if_not_exist


def command(
    inputfile,
    exe,
    license,
    database,
    outputdirectory,
    **opt_kwargs,
):
    kwargs = dict(
        inputfile=inputfile,
        exe=exe,
        license=license,
        database=database,
        outputdirectory=outputdirectory,
    )
    kwargs.update(opt_kwargs)
    product = defaults.input_file_type(inputfile)
    cmd = defaults.get_command(product)

    # warn if output path might be too long
    outdir_len = len(str(outputdirectory))
    tooLongPath = (
        (product in ["nextnano3", "nextnano++"]) and outdir_len + 80 > 260
    )  # TODO: how long is the minimal path appended by nn3/nnp simulations?
    tooLongPathNEGF = (
        product in ["nextnano.NEGF", "nextnano.NEGF_classic"]
    ) and outdir_len + 80 > 260
    if tooLongPath or tooLongPathNEGF:
        # stacklevel=4 blames the caller of InputFile.execute(), the usual route here:
        # command() <- execute() <- InputFile.execute() <- user.
        warnings.warn(
            "The output path might be too long on Windows 10 (maximum 260 characters). Consider abbreviating your input file name and/or sweep variables...",
            stacklevel=4,
        )
    return cmd(**kwargs)


def send(cmd, cwd=None):
    """
    Launch ``cmd`` through the system shell (``shell=True``).

    Note: because the command runs via the shell, the returned Popen object is
    the shell process (cmd.exe on Windows), not the simulator itself. On
    Windows, calling .kill()/.terminate() on it stops only the shell wrapper;
    the running simulation is NOT stopped.
    """
    PIPE = subprocess.PIPE
    return subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, close_fds=True, shell=True, cwd=cwd)


def read_output(pipe, funcs):
    for line in iter(pipe.readline, b""):
        for func in funcs:
            func(line)
    pipe.close()


def write_output(get, filepath, show=True):
    with open(filepath, "w", newline="") as f:
        for line in iter(get, None):
            line = str(line, "utf-8", errors="ignore")
            if show:
                sys.stdout.write(line)
            f.write(line)


def start_log(process, filepath, show=True, parallel=False):
    q = queue.Queue()
    out, err = [], []
    tout = threading.Thread(target=read_output, args=(process.stdout, [q.put, out.append]))
    terr = threading.Thread(target=read_output, args=(process.stderr, [q.put, err.append]))
    twrite = threading.Thread(target=write_output, args=(q.get, filepath, show))
    for t in (tout, terr, twrite):
        t.daemon = False
        t.start()

    if parallel:
        return q, tout, terr
    else:
        process.wait()
        for t in (tout, terr):
            t.join()
        q.put(None)
        return q, tout, terr


def execute(
    inputfile,
    exe,
    license,
    database,
    outputdirectory,
    show_log=True,
    parallel=False,
    overwrite=False,
    create_subdirectory=True,
    **kwargs,
):
    """
    Run one input file and return a dict describing the started simulation.

    ``**kwargs`` are the simulator's own command line arguments and are passed on to
    the product's command builder as they are. ``overwrite`` and
    ``create_subdirectory`` are not among them: they only decide which directory the
    simulation is started on, which is nextnanopy's own bookkeeping.

    Parameters
    ----------
    overwrite : bool, optional
        If False (default), the output directory is created under an unused name: an
        index is appended (``example_0``, ``example_1``, ...) when the name is already
        taken, so a run never writes into an earlier run's output. If True, an
        existing directory is used as it is - which means writing next to whatever
        the earlier run left there; nothing is deleted.
        Has no effect when create_subdirectory is False.
    create_subdirectory : bool, optional
        If True (default), the simulation writes into
        ``<outputdirectory>/<input file name>/``. If False, it writes into
        ``outputdirectory`` itself.
    """
    # validate the input file
    if not str(inputfile):
        raise ValueError("Input file path is empty")
    inputfile = Path(inputfile).resolve()
    if not inputfile.is_file():
        raise ValueError(f"Input file is not an existing file: {inputfile}")

    if not Path(exe).is_file():
        raise FileNotFoundError(f"Executable path is invalid: '{exe}'\nCheck nextnanopy.config")

    exe = Path(exe)
    wdir = inputfile.parent

    filename = inputfile.stem
    if not create_subdirectory:
        # everything below (the log file, the command line, the returned info) follows
        # outputdirectory, so switching the subdirectory off is only this branch
        outputdirectory = Path(mkdir_if_not_exist(Path(outputdirectory)))
    elif overwrite:
        outputdirectory = Path(mkdir_if_not_exist(Path(outputdirectory) / filename))
    else:
        outputdirectory = Path(mkdir_even_if_exists(outputdirectory, filename))
    logfile = outputdirectory / f"{filename}.log"
    cmd = command(inputfile, exe, license, database, outputdirectory, **kwargs)
    process = send(cmd, cwd=wdir)
    queue, tout, terr = start_log(process, logfile, show_log, parallel=parallel)
    info = {
        "process": process,
        "outputdirectory": outputdirectory,
        "filename": filename,
        "logfile": logfile,
        "cmd": cmd,
        "wdir": wdir,
        "queue": queue,
        "tout": tout,
        "terr": terr,
    }
    return info


def run_script(script, kwargs=None, show_log=True):
    """
    The function runs a python script with given arguments. Output is stored in the file script_name.log

    Parameters
    ----------
    script : str
        path to the python script
    kwargs : dict
        optional parameters, {keyword:argument,keyword:argument}
        for a keyword without argument leave argument as an empty string ''

        EXAMPLE: {'-o': 'my_output_folder','-p':''} will be converted to '-o my_output_folder -p'
    show_log : bool
        show the log in console output, default is True

    Returns
    -------
    process : subprocess.POPEN
    """
    args = [[sys.executable, script]]
    if kwargs:
        for key in kwargs.keys():
            args.append([key, kwargs[key]])
    cmd = generate_command(args)
    process = send(cmd)
    logfile = Path.cwd() / f"{Path(script).name}.log"
    start_log(process, logfile, show_log)
    return process
