import sys, os
import subprocess
import queue
import threading
import warnings
from nextnanopy.utils.misc import get_filename, mkdir_if_not_exist
from nextnanopy import defaults

from nextnanopy.utils.formatting import generate_command


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
    tooLongPath = (product in ["nextnano3", "nextnano++"]) and len(
        outputdirectory
    ) + 80 > 260  # TODO: how long is the minimal path appended by nn3/nnp simulations?
    tooLongPathNEGF = (product in ["nextnano.NEGF", "nextnano.NEGF_classic"]) and len(
        outputdirectory
    ) + 80 > 260
    if tooLongPath or tooLongPathNEGF:
        warnings.warn(
            "The output path might be too long on Windows 10 (maximum 260 characters). Consider abbreviating your input file name and/or sweep variables..."
        )
    return cmd(**kwargs)


def send(cmd, cwd=os.getcwd()):
    PIPE = subprocess.PIPE
    return subprocess.Popen(
        cmd, stdout=PIPE, stderr=PIPE, close_fds=True, shell=True, cwd=cwd
    )


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
    tout = threading.Thread(
        target=read_output, args=(process.stdout, [q.put, out.append])
    )
    terr = threading.Thread(
        target=read_output, args=(process.stderr, [q.put, err.append])
    )
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
    **kwargs,
):
    filename = get_filename(inputfile, ext=False)
    inputfile = os.path.abspath(inputfile)
    outputdirectory = os.path.join(outputdirectory, filename)
    mkdir_if_not_exist(outputdirectory)
    logfile = os.path.join(outputdirectory, f"{filename}.log")
    cmd = command(inputfile, exe, license, database, outputdirectory, **kwargs)
    cwd = os.getcwd()
    wdir, executable = os.path.split(
        exe
    )  # nn3 assumes wdir at one folder upper than the executable

    # validate configuration of executable path
    if executable == "":
        raise FileNotFoundError(f"Executable path is empty! Check nextnanopy.config")

    if (not os.path.isfile(exe)) or (not os.path.isdir(wdir)):
        raise FileNotFoundError(
            f"Executable path is invalid: {exe}\nCheck nextnanopy.config"
        )
    process = send(cmd, cwd=wdir)
    queue, tout, terr = start_log(process, logfile, show_log, parallel=parallel)
    os.chdir(cwd)
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
    script: str
        path to the python script
    kwargs: dict
        optional parameters, {keyword:argument,keyword:argument}
        for a keyword without argument leave argument as an empty string ''

        EXAMPLE: {'-o': 'my_output_folder','-p':''} will be converted to '-o my_output_folder -p'
    show_log - bool
        show the log in console output, default is True

    Returns
    -------
    process: subprocess.POPEN
    """
    args = [[sys.executable, script]]
    if kwargs:
        for key in kwargs.keys():
            args.append([key, kwargs[key]])
    cmd = generate_command(args)
    process = send(cmd)
    logfile = os.path.join(os.getcwd(), f"{os.path.basename(script)}.log")
    start_log(process, logfile, show_log)
    return process
