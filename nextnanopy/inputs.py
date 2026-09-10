import atexit
import concurrent.futures
import itertools
import os
import queue
import sys
import tempfile
import threading
import time
import warnings
from collections.abc import Callable, Iterable
from copy import deepcopy
from typing import Any

from nextnanopy import defaults
from nextnanopy.commands import execute as cmd_execute
from nextnanopy.utils.formatting import lines_to_text, text_to_lines
from nextnanopy.utils.misc import (
    get_file_extension,
    get_filename,
    get_folder,
    mkdir_even_if_exists,
    mkdir_if_not_exist,
    savetxt,
)
from nextnanopy.utils.mycollections import DictList


class InputFileTemplate:
    """
    This class stores and manipulates any kind of nextnano input files.

    For each nextnano product, the syntax is different but the core information
    is very similar like the variables that can be changed.
    This class contains useful methods such as to get a preview of the file or
    execute a simulation.

    The initialization of the class will execute the load method and setup the
    config file.

    Parameters
    ----------
    fullpath : str or pathlib.Path, default=None
        Path to the file. If given, the file is loaded, unless `text` is given as
        well: then `fullpath` only names the file and nothing is read from disk.
    configpath : str or pathlib.Path, default=None
        Path to the config file. If omitted, a copy of the process-wide
        configuration (`nextnanopy.config`) is taken instead of reading a file;
        see Notes.
    parse : bool, default=False
        Experimental feature to parse the input file into a structured object.
        Please refrain from using it.
    text : str, default=None
        Contents of the input file. If given, the file content is read from this
        string instead of from disk at `fullpath`.

    Attributes
    ----------
    fullpath : str or pathlib.Path
        Path to the file.
    configpath : str or pathlib.Path
        Path of the configuration file behind `.config`. Read-only; assign
        `.config` to point this file at a different configuration.
    variables : DictList of InputVariable
        Input variables defined in the file, keyed by name.
    raw_lines : list of str
        Each line of the file as it was loaded.
    raw_text : str
        The `.raw_lines` as one string, without the current input variable values
        applied. Read-only.
    text : str
        Text of the file with the current variable values applied. Assigning
        replaces `.raw_lines` and reloads `.variables`, but does not re-detect
        `.product`.
    lines : list of str
        The `.raw_lines` updated with the current input variable parameters.
    filename : str
        File name with the extension.
        Assigning changes `.fullpath` to the same folder with the new name.
    filename_only : str
        File name without the extension.
        Assigning changes `.fullpath` to the new name, keeping the folder and the extension.
    folder_input : str
        Folder containing the input file.
        Assigning changes `.fullpath` to the new folder, keeping the file name.
    product : str
        Detected nextnano product when the file is loaded.
        Defaults to 'not valid' if the product is not recognised.
    config : NNConfig
        The configuration this file runs on, bound at construction (see Notes).
    execute_info : dict
        Information about the last execution. Empty until `.execute()` has run.

    Notes
    -----
    The configuration is bound at construction and never re-read afterwards. With no
    ``configpath``, the file takes a *copy* of the process-wide configuration
    (``nextnanopy.config``) as it stands at that moment. Two things follow, both
    intended:

    - ``nextnanopy.config.set(...)`` reaches every input file built after it, and no
      ``save()`` is needed for that -- saving only matters for other processes. It
      reaches no file that already exists.
    - The copy is this file's own. Editing ``.config`` here changes neither
      ``nextnanopy.config`` nor any other input file, and later edits to
      ``nextnanopy.config`` do not reach this file.

    So configure first, then build the input files. To point a file that already
    exists at a different configuration, assign ``.config``; to build one on a config
    file of its own, pass ``configpath``.
    """

    _shared_temp_dir = None

    def __init__(self, fullpath=None, configpath=None, parse=False, text=None):
        self.raw_lines = []
        self.variables = DictList()
        self.content = None
        self.fullpath = fullpath
        self.product = "not valid"
        self.parse = parse
        self.__parallel__ = False
        # `text` alone is enough to load: load_raw() only opens fullpath when text is
        # None, so a caller who already has the contents needs no file on disk. Without
        # both, there is nothing to load and fullpath stays None.
        if fullpath is not None or text is not None:
            self.load(fullpath, text=text)
        if configpath is None:
            # A copy of the process-wide config, not the object itself and not a fresh
            # read of the file: the copy carries changes that were only set() on
            # nextnanopy.config, while leaving this file free to edit .config without
            # reaching nextnanopy.config or any other input file. See the class Notes.
            self.config = deepcopy(defaults.get_config())
        else:
            self.config = defaults.NNConfig(configpath)
        self.execute_info = {}

    @classmethod
    def _get_temp_dir(cls):
        if cls._shared_temp_dir is None:
            cls._shared_temp_dir = tempfile.TemporaryDirectory()
            atexit.register(cls._shared_temp_dir.cleanup)
        return cls._shared_temp_dir.name

    @property
    def text(self):
        return str(lines_to_text(*self.lines))

    @text.setter
    def text(self, text):
        self.raw_lines = list(text_to_lines(text))
        # self.find_product()
        self.validate()
        self.load_variables()
        self.load_content()

    @property
    def raw_text(self):
        return str(lines_to_text(*self.raw_lines))

    @property
    def lines(self):
        new_lines = list(self.raw_lines)
        for ivar in self.variables.values():
            text = ivar.text
            idx = ivar.metadata["line_idx"]
            new_lines[idx] = text
        return new_lines

    @property
    def default_command_args(self):
        return self.config.config[self.product]

    @property
    def configpath(self):
        return self.config.fullpath

    @property
    def filename_only(self):
        return get_filename(self.fullpath, ext=False)

    @filename_only.setter
    def filename_only(self, name):
        ext = get_file_extension(self.fullpath)
        self.filename = f"{name}{ext}"

    @property
    def filename(self):
        return get_filename(self.fullpath, ext=True)

    @filename.setter
    def filename(self, name):
        self.fullpath = os.path.join(self.folder_input, name)

    @property
    def folder_input(self):
        return get_folder(self.fullpath)

    @folder_input.setter
    def folder_input(self, folder):
        self.fullpath = os.path.join(folder, self.filename)

    @property
    def folder_output(self):
        """
        Folder where the simulated data is stored. Read-only.

        Returns
        -------
        pathlib.Path
            Output directory of the last execution, as chosen by `execute()`
            from `overwrite` and `create_subdirectory`.

        Raises
        ------
        KeyError
            If the input file has not been executed yet.
        """
        key = "outputdirectory"
        if key in self.execute_info.keys():
            return self.execute_info[key]
        else:
            raise KeyError("Input file has not been executed yet")

    def preview(self, nums=True):
        """
        Print the text of the file.

        Parameters
        ----------
        nums : bool, default=True
            If True, prefix each line with its index, starting at 0.
        """
        for i, line in enumerate(self.lines):
            if nums:
                print(f"{i} {line}")
            else:
                print(f"{line}")

    def load(self, fullpath, text=None):
        """
        Load the input file.

        The steps are the following:

        1. Clear `.raw_lines`, `.variables` and `.fullpath`.
        2. Load the raw text (updates `.fullpath` and `.raw_lines`).
        3. Find the nextnano product (updates `.product`).
        4. Validate the input file.
        5. Load the input variables (updates `.variables`).
        6. Load the content, when applicable.

        Parameters
        ----------
        fullpath : str or pathlib.Path
            Path to the file to be loaded.
        text : str, default=None
            Contents of `fullpath`, if the caller has already read them. Saves
            re-reading the file from disk. If omitted, the file is read here.

        Raises
        ------
        FileNotFoundError
            If `fullpath` does not exist and `text` is not given.
        """

        self.clear()
        self.fullpath = fullpath
        self.load_raw(text=text)
        self.find_product()
        self.validate()
        self.load_variables()
        self.load_content()

    def find_product(self):
        self.product = defaults.input_text_type(self.raw_text)
        return self.product

    def validate(self):
        if self.product not in defaults.products:
            self.product = "not valid"

    def save(self, fullpath=None, overwrite=False, automkdir=True, temp=False, content=False):
        """
        Save the current information into a file.

        `.fullpath` is updated to the path that was written.

        Parameters
        ----------
        fullpath : str or pathlib.Path, default=None
            Path including the file name where it will be saved. If None, the
            current `.fullpath` is used.
        overwrite : bool, default=False
            If False, an index is appended to the file name when it is already
            taken (`example.nnp`, then `example_0.nnp`, `example_1.nnp`, ...), so an
            existing file is never overwritten. If True, the file is written even
            if it exists and no index is appended.
        automkdir : bool, default=True
            If True, create the parent folder if it does not exist.
        temp : bool, default=False
            If True, save into a temporary folder that is removed when the process
            exits, keeping the current `.filename`. Ignored with a warning when
            `fullpath` is given.
        content : bool, default=False
            Experimental feature, refrain from using it.
            If True, save the parsed `.content` instead of `.text`. Comments are
            not preserved. It requires the file to be loaded with `parse=True`.

        Returns
        -------
        str
            Path of the file that was written. Not necessarily `fullpath`: with
            `overwrite=False` an index may have been appended.

        Raises
        ------
        ValueError
            If neither `fullpath` nor `.fullpath` is set, or if `content` is True
            and the file was not loaded with `parse=True`.
        FileNotFoundError
            If `automkdir` is False and the parent folder does not exist.
        """

        if temp and fullpath is not None:
            warnings.warn("Fullpath is specified, temp flag is ignored", stacklevel=2)
        if fullpath is None:
            if temp:
                folder = self._get_temp_dir()
                fullpath = os.path.join(folder, self.filename)
            elif self.fullpath is None:
                raise ValueError("Please, specify a fullpath")
            else:
                fullpath = self.fullpath

        if content:
            if self.content is None:
                raise ValueError(
                    "There is no parsed content to save. "
                    "Load the input file with parse=True to use content=True"
                )
            text = str(self.content)
        else:
            text = self.text

        self.fullpath = savetxt(
            fullpath=fullpath, text=text, overwrite=overwrite, automkdir=automkdir
        )
        return self.fullpath

    def execute(
        self,
        show_log=True,
        convergenceCheck=False,
        convergence_check_mode="pause",
        overwrite=False,
        create_subdirectory=True,
        **kwargs,
    ):
        """
        Execute the input file located at `.fullpath`.

        Individual kwargs can be passed like `license` or `database`; anything not
        given comes from `.config`.

        Parameters
        ----------
        show_log : bool, default=True
            If False, do not print the simulation log to the console. The log file
            is written either way.
        convergenceCheck : bool, default=False
            If True, check the log for convergence once the simulation has finished.
            Ignored when the file is executed in parallel, as a sweep or an
            execution queue does.
        convergence_check_mode : {'pause', 'terminate', 'continue'}
            What to do when the simulation did not converge. Only used when
            `convergenceCheck` is True.

            - 'pause': ask the user how to proceed. If no interactive terminal is
              attached (e.g. CI, cluster jobs), behaves like 'terminate' instead of
              blocking on input.
            - 'terminate': terminate the script.
            - 'continue': notify the user but continue the script. This is also the
              only mode that tolerates a missing log file.
        overwrite : bool, default=False
            If False, the output directory is created under an unused name: an index
            is appended (`example_0`, `example_1`, ...) when the name is already
            taken, so a run never writes into an earlier run's output. If True, an
            existing directory is used as it is - which means writing next to
            whatever the earlier run left there; nothing is deleted.
            Has no effect when `create_subdirectory` is False.
        create_subdirectory : bool, default=True
            If True, the simulation writes into
            `<outputdirectory>/<input file name>/`. If False, it writes into the
            `outputdirectory` itself.
        **kwargs : dict
            The nextnano product's own command line arguments, passed on as they
            are. Anything not given here comes from `.config`. `kwargs` may contain:

            exe : str, optional
                Path to the executable.
            license : str, optional
                Path to the license file.
            database : str, optional
                Path to the database file.
            outputdirectory : str, optional
                Path where to save the simulated data.

            and other parameters depending on the nextnano product. For example,
            'threads' is accepted by nextnano++. See the documentation of the
            command line arguments of each nextnano product on the online Manual
            (https://www.nextnano.com/docu/).

        Returns
        -------
        dict
            Information about the started simulation, also stored in
            `.execute_info`. Keys: 'process', 'outputdirectory', 'filename',
            'logfile', 'cmd', 'wdir', 'queue', 'tout', 'terr'.

        Raises
        ------
        ValueError
            If `.fullpath` is empty or is not an existing file, or if
            `convergence_check_mode` is not one of the values listed above.
        FileNotFoundError
            If the executable path in `.config` is empty or invalid.
        RuntimeError
            If `convergenceCheck` is True and the simulation was terminated or did
            not converge, unless `convergence_check_mode` is 'continue'.
        NotImplementedError
            If `convergenceCheck` is True and the product is nextnano.MSB.

        Notes
        -----
        The simulation is launched through the system shell, so
        `execute_info['process']` is the shell process, not the simulator
        itself. On Windows, calling `.kill()`/`.terminate()` on it stops only
        the shell wrapper; the running simulation is NOT stopped.

        Where the output goes is decided by `overwrite`/`create_subdirectory`, which
        are parameters rather than members of ``**kwargs``: they steer nextnanopy,
        not the simulator, so they are also not config options. `.folder_output`
        holds the directory that was chosen once the run has started.
        """

        cmd_kwargs = dict(self.default_command_args)
        cmd_kwargs.update(kwargs)
        cmd_kwargs["inputfile"] = self.fullpath
        info = cmd_execute(
            show_log=show_log,
            parallel=self.__parallel__,
            overwrite=overwrite,
            create_subdirectory=create_subdirectory,
            **cmd_kwargs,
        )
        self.execute_info = info
        if (
            convergenceCheck and not self.__parallel__
        ):  # - possible solution for later (delete comment if not)
            self.check_convergence(mode=convergence_check_mode)
        return info

    def check_convergence(self, mode="pause"):
        if self.product == "nextnano.MSB":
            raise NotImplementedError("Convergence check has not yet implemented for nextnano.MSB!")

        log = self.execute_info["logfile"]
        try:
            if self.product == "nextnano3":
                with open(log) as file:
                    for line in file:
                        if (
                            "Exiting iteration and terminating simulation" in line
                            or "Program was terminated using a soft kill" in line
                            or "Terminating immediately" in line
                        ):
                            raise RuntimeError(
                                f"\nSimulation got terminated! Check the log:\n{log}"
                            )
                        elif "Maximum number of iterations exceeded" in line:
                            raise RuntimeError(
                                f"\nSimulation did not converge! Check the log:\n{log}"
                            )
            elif self.product == "nextnano++":
                with open(log) as file:
                    for line in file:
                        if "Terminating program" in line:
                            raise RuntimeError(
                                f"\nSimulation got terminated! Check the log:\n{log}"
                            )
                        elif "Maximum number of iterations exceeded" in line:
                            raise RuntimeError(
                                f"\nSimulation did not converge! Check the log:\n{log}"
                            )
                        elif "Outdated numerics library (f95library) used" in line:
                            raise RuntimeError("\nOutdated numerics library (f95library) used.")
            elif (
                self.product == "nextnano.NEGF" or self.product == "nextnano.NEGF_classic"
            ):  # NEGF reports convergence at every voltage and temperature sweep.
                with open(log) as file:
                    for line in file:
                        if "Simulation has NOT CONVERGED" in line:
                            raise RuntimeError(f"\nSimulation has diverged! Check the log:\n{log}")
                        elif "Simulation has partially converged" in line:
                            print(
                                "\nWARNING: check_convergence(): Simulation did not fully converge."
                            )
                        elif "Terminating program!" in line:
                            raise RuntimeError(
                                f"\nSimulation got terminated! Check the log:\n{log}"
                            )
        except FileNotFoundError:
            print(f"Log file {log} not found!")
            if mode != "continue":
                raise
            else:
                pass
        except RuntimeError as e:
            print(e)
            if mode == "pause":
                if sys.stdin is None or not sys.stdin.isatty():
                    print(
                        "check_convergence: mode 'pause' needs an interactive terminal to ask"
                        " how to proceed, but none is attached - terminating instead."
                    )
                    raise RuntimeError("Nextnanopy terminated.") from e
                pause = True
                while pause:
                    answer = input("Do you nevertheless want to continue? [y/n]: ")
                    if answer == "y" or answer == "yes":
                        pause = False
                        return
                    elif answer == "n" or answer == "no":
                        pause = False
                        raise RuntimeError("Nextnanopy terminated.") from e
                    else:
                        print("Invalid input.")
                        continue
            elif mode == "terminate":
                raise RuntimeError("Nextnanopy terminated.") from e
            elif mode == "continue":
                return
            else:
                raise ValueError(f'Mode "{mode}" is not valid') from e
        else:
            return

    def clear(self):
        self.raw_lines = []
        self.variables = DictList()
        self.fullpath = None

    def remove(self):
        if os.path.exists(self.fullpath):
            os.remove(self.fullpath)

    def load_raw(self, text=None):
        if text is None:
            with open(self.fullpath) as f:
                text = f.read()
        self.raw_lines = list(text_to_lines(text))
        return self.raw_lines

    def load_variables(self):
        pass

    def load_content(self):
        pass

    def get_variable(self, name):
        """
        Return the input variable called `name`.

        Equivalent to `.variables[name]`, except that only lookup by name is
        supported: `.variables` also accepts an integer index, this method does
        not.

        Parameters
        ----------
        name : str
            Name of the input variable.

        Returns
        -------
        InputVariable
            The input variable stored under `name`.

        Raises
        ------
        KeyError
            If `name` is not a key of `.variables`.
        """
        if name not in self.variables.keys():
            raise KeyError(f"{name} is not a valid variable.")
        return self.variables[name]

    def set_variable(self, name, value=None, comment=None, unit=None):
        """
        Change the value, the comment and/or the unit of an input variable.

        Parameters
        ----------
        name : str
            Name of the input variable.
        value : int, float or str, default=None
            New value of the variable. If None, the value is left unchanged.
        comment : str, default=None
            New comment of the variable. If None, the comment is left unchanged.
        unit : str, default=None
            New unit of the variable. If None, the unit is left unchanged. The
            unit is not part of the input file text: it only feeds `.unit` and
            `.label` of the variable.

        Returns
        -------
        InputVariable
            The input variable that was changed.

        Raises
        ------
        KeyError
            If `name` is not a key of `.variables`.
        """

        var = self.get_variable(name)
        if value is not None:
            var.value = value
        if comment is not None:
            var.comment = comment
        if unit is not None:
            var.unit = unit
        return var

    def __getitem__(self, item):
        return self.variables[item]

    def __setitem__(self, item, value):
        self.variables[item] = value

    def __delitem__(self, item):
        del self.variables[item]

    def __repr__(self):
        out = []
        out.append(f"{self.__class__.__name__}")
        out.append(f"fullpath: {self.fullpath}")
        out.append(f"Input variables: {len(self.variables)} elements")
        for var in self.variables.values():
            out.append(f"\t{str(var)}")
        out = "\n".join(out)
        return out

    def __iter__(self):
        # Yields the input variables themselves, not their names (see DictList docstring).
        # Fresh iterator per call, so nested loops over the same file do not interfere.
        return iter(self.variables.values())


class InputFile(InputFileTemplate):
    """
    Load a nextnano input file as the product-specific class that fits it.

    ``InputFile(path)`` detects the product from the file's text and returns an instance of
    that product's class (``nextnanopy.nnp.inputs.InputFile``,
    ``nextnanopy.nn3.inputs.InputFile``, and so on), or a bare ``InputFileTemplate`` if the
    text matches no known product.

    Pass ``text`` to build from a string instead of from disk: ``InputFile(text=...)`` detects
    the product from that text and never opens a file. ``fullpath`` is then just the name to
    give the result (``InputFile(path, text=...)`` reads nothing, but the object saves back to
    ``path``). With neither, there is nothing to detect and nothing to load, so an empty
    ``InputFileTemplate`` comes back.

    Parameters are ``InputFileTemplate``'s; see it for what they mean and for the API of the
    object you get back.

    **Building from a string: use InputFile(text=...), not InputFile() + .text = ....**
    The latter cannot work: ``InputFile()`` has no text to detect from, so it returns a
    product-agnostic ``InputFileTemplate`` whose ``load_variables()`` is a no-op, and assigning
    ``.text`` afterwards cannot re-class the object it is called on. The text round-trips, but
    ``.variables`` stays empty and ``.product`` stays ``'not valid'``, silently. Dispatch
    happens in ``__new__`` or not at all, so the contents must be supplied at construction.
    (Assigning ``.text`` to a file loaded *from a path* is fine — that object is already a
    product class.)

    Two limitations follow from dispatching in ``__new__``, both deliberate:

    - **The result is not an InputFile.** The product classes are siblings of this class,
      not subclasses, so ``isinstance(InputFile(path), InputFile)`` is ``False``. Check against,
      annotate with, and subclass ``InputFileTemplate`` — the base every product class shares.
    - **This class cannot be subclassed.** ``__new__`` picks the class from the file's contents
      and ignores ``cls``, so a subclass would be silently discarded; it raises ``TypeError``
      instead. To extend one product, subclass that product's class; to extend all of them,
      subclass ``InputFileTemplate``.
    """

    # Takes exactly InputFileTemplate.__init__'s parameters, and must keep doing so:
    # changing either signature requires changing both.
    def __new__(cls, fullpath=None, configpath=None, parse=False, text=None):
        # `cls` is ignored below — the class to build is chosen from the text — so a subclass
        # would come back as the detected product class instead of itself, silently. Refuse
        # rather than hand back an object of the wrong type.
        if cls is not InputFile:
            raise TypeError(
                f"{cls.__name__} cannot subclass InputFile: InputFile.__new__ dispatches on "
                f"the file's contents and would return the product's class, not "
                f"{cls.__name__}. Subclass the product's InputFile, or InputFileTemplate."
            )
        if text is None:
            # With neither text nor fullpath there is nothing to detect and nothing to load:
            # dispatch on the 'not valid' sentinel, which lands on InputFileTemplate.
            if fullpath is None:
                return defaults.get_InputFile(defaults.NOT_VALID)(fullpath, configpath, parse=parse)
            # Read here to pick the product's class, then pass the text on so the chosen
            # class does not read the same file again.
            with open(fullpath) as f:
                text = f.read()
        _InputFileType = defaults.get_InputFile(defaults.input_text_type(text))
        return _InputFileType(fullpath, configpath, parse=parse, text=text)


class ExecutionQueue(threading.Thread):
    """
    This class take InputFiles and add them in the execution queue.

    Depending on limit_parallel, InputFiles are executed in parallel or sequentially.

    Parameters
    ----------
    limit_parallel : int
        number of InputFiles to be executed in parallel (default: 1)
    terminate_empty : bool
        If True, terminates once all added files are executed and logged.
        If you want to add more input files even after execution of all added in the beginning, use terminate_empty = False
        Then the ExecutionQueue has to be stopped manually later (ExecutionQueue.stop())
    convergenceCheck : bool
        see convergenceCheck in InputFile
    **execution_kwargs
        parameters to be taken by InputFile.execute()

    Attributes
    ----------
    waiting_queue : queue.Queue
        queue of InputFile objects to be executed
    started : list
        list of (simulation_info:dict, InputFile) currently executing
    finished : list
        list of simulation_infos for finished simulations
    stop_when_empty : bool
        see terminate_empty parameter
    daemon : bool
        see threading.Thread.daemon
    poll_interval : float
        seconds between checks for finished simulations while the queue is running
        (class attribute, default 0.1)

    Methods
    -------
    for user:

    ``add(*input_files)``
        adds InputFiles to queue
    start()
        start the thread (i.e. execution)
        see threading.Thread.start()
    stop()
        stop the thread (once all added files are executed)
        only necessary if terminate_empty = True

    internal (or for advanced users):

    all_done()
        return True if all execution and logging are finished
    add_execution()
        pop an InputFile from self.waiting_queue, execute and add to self.started
    log_finished()
        finish logging for finished execution in self.started
    run()
        commands to be run upon start():

            pop simulation from queue and execute
            log the simulation if some are finished from self.started

        see threading.Thread.run()
    """

    poll_interval = 0.1

    def __init__(
        self,
        limit_parallel: int = 1,
        maxsize: int = 0,
        terminate_empty: bool = True,
        convergenceCheck=False,
        **execution_kwargs,
    ):
        super().__init__()
        self.waiting_queue = queue.Queue()  # should be queue of InputFile objects
        self.started = []  # should be list of execution_infos
        self.finished = []  # should be list of execution_infos
        self.limit_parallel = limit_parallel
        self.execution_kwargs = execution_kwargs
        self.convergenceCheck = convergenceCheck
        self.stop_when_empty = terminate_empty
        self.daemon = False

    def all_done(self):
        return not bool(not self.waiting_queue.empty() or self.started)

    def add(self, *input_files: InputFileTemplate):
        for input_file in input_files:
            self.waiting_queue.put(input_file)

    def stop(self):
        self.stop_when_empty = True

    def add_execution(self):
        while (len(self.started) < self.limit_parallel) and not self.waiting_queue.empty():
            input_f = self.waiting_queue.get()
            if self.limit_parallel > 1:
                input_f.__parallel__ = True
            if "show_log" in self.execution_kwargs and not self.execution_kwargs["show_log"]:
                print("\nRemaining simulations in the queue: ", self.waiting_queue.qsize())
            info = input_f.execute(**self.execution_kwargs)
            self.started.append((info, input_f))

    def log_finished(self):
        if self.limit_parallel > 1:
            i = 0
            while i < len(self.started):
                poll = self.started[i][0]["process"].poll()
                if poll is None:
                    i += 1
                else:
                    # TODO check once again del
                    self.started[i][0]["process"].wait()
                    tout = self.started[i][0]["tout"]
                    terr = self.started[i][0]["terr"]
                    for t in (tout, terr):
                        t.join()
                    self.started[i][0]["queue"].put(None)
                    if self.convergenceCheck:
                        if "convergence_check_mode" in self.execution_kwargs:
                            convergence_check_mode = self.execution_kwargs["convergence_check_mode"]
                        else:
                            convergence_check_mode = "pause"
                        self.started[i][1].check_convergence(mode=convergence_check_mode)
                    self.finished.append(self.started[i][0])
                    del self.started[i]

        else:
            i = 0
            while i < len(self.started):
                poll = self.started[i][0]["process"].poll()
                if poll is None:
                    i += 1
                else:
                    self.finished.append(self.started[i][0])
                    del self.started[i]

    def run(self):
        while True:
            self.add_execution()
            self.log_finished()
            if self.all_done():
                print("\nWaiting queue is empty, all execution and logging are finished")

                if self.stop_when_empty:
                    break
                while self.all_done() and not self.stop_when_empty:
                    time.sleep(self.poll_interval)
            else:
                time.sleep(self.poll_interval)


class ExecutionPool:
    """
    Run added InputFiles concurrently, at most parallel_limit at a time.

    Candidate replacement for ExecutionQueue, built on
    concurrent.futures.ThreadPoolExecutor instead of a hand-rolled scheduler
    thread. Each worker thread runs one simulation at a time through the
    blocking execution path (InputFile.execute() with __parallel__ = False):
    commands.start_log() itself waits for the simulator process, joins the
    log-pump threads and finishes the log file, and the convergence check runs
    inline in InputFile.execute(). Completion is therefore event-driven — no
    polling loop, no poll_interval — and an exception in a worker cannot kill
    a scheduler thread: it is captured in the corresponding future and
    re-raised by join().

    Unlike ExecutionQueue there is no terminate_empty flag: the pool accepts
    add() at any point — before or after start(), even after join() — until
    stop() shuts it down. Idle worker threads cost nothing and exit with the
    interpreter, so calling stop() is optional.

    Parameters
    ----------
    parallel_limit : int
        maximum number of simulations running simultaneously (default: 1).
        Same spelling as Sweep.execute_sweep(parallel_limit=...); note that
        ExecutionQueue calls this limit_parallel.
    **execution_kwargs
        forwarded to InputFile.execute() of every added file: outputdirectory,
        show_log, convergenceCheck, convergence_check_mode, exe, license,
        database, ... With parallel_limit > 1 and show_log=True the console
        logs of concurrent simulations interleave (the per-simulation .log
        files are unaffected). convergenceCheck with mode 'pause' can prompt
        for several finished simulations at once (unlike ExecutionQueue,
        which serialized the prompts through its manager thread); with
        parallel_limit > 1 prefer mode 'terminate' or 'continue'.

    Attributes
    ----------
    finished : list
        info dicts (as returned by InputFile.execute()) of the completed
        simulations, in completion order.
    errors : list
        exceptions raised by workers; filled by join() once all work is done.

    Methods
    -------
    ``add(*input_files)``
        hand InputFiles to the pool. Buffered before start(), submitted to the
        workers immediately after it.
    start()
        create the worker threads and submit everything buffered so far.
    join(timeout=None)
        wait until the work submitted so far is done, or timeout (in seconds)
        elapses — check is_alive() to tell which. Once everything is done,
        re-raises the first worker exception, if any (all of them are kept in
        .errors; successful runs are in .finished either way).
    is_alive()
        True while at least one added simulation has not finished.
    stop()
        wait for outstanding work and shut the pool down; add() raises
        afterwards.
    """

    def __init__(self, parallel_limit: int = 1, **execution_kwargs):
        self.parallel_limit = parallel_limit
        self.execution_kwargs = execution_kwargs
        self.finished = []
        self.errors = []
        self._executor = None
        self._futures = []
        self._buffer = []
        self._lock = threading.Lock()

    def add(self, *input_files: InputFileTemplate):
        with self._lock:
            if self._executor is None:
                self._buffer.extend(input_files)
                return
            executor = self._executor
        futures = [executor.submit(self._execute_one, f) for f in input_files]
        with self._lock:
            self._futures.extend(futures)

    def start(self):
        with self._lock:
            if self._executor is not None:
                raise RuntimeError("ExecutionPool can only be started once")
            self._executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.parallel_limit,
                thread_name_prefix="ExecutionPool",
            )
            buffer, self._buffer = self._buffer, []
        self.add(*buffer)

    def _execute_one(self, input_file):
        # The blocking path on purpose: start_log(parallel=False) waits for the
        # process and tears down the log threads, InputFile.execute() runs the
        # convergence check — nothing is left to supervise from here.
        input_file.__parallel__ = False
        info = input_file.execute(**self.execution_kwargs)
        with self._lock:
            self.finished.append(info)
            n_done, n_known = len(self.finished), len(self._futures)
        if not self.execution_kwargs.get("show_log", True):
            print(f"\nSimulations finished: {n_done} of {n_known} submitted")
        return info

    def join(self, timeout=None):
        with self._lock:
            if self._executor is None:
                raise RuntimeError("cannot join ExecutionPool before it is started")
            futures = list(self._futures)
        _, not_done = concurrent.futures.wait(futures, timeout=timeout)
        if not_done:
            return
        with self._lock:
            all_futures = list(self._futures)
        if len(all_futures) > len(futures):
            # work was added while waiting; the caller sees is_alive() True
            return
        self.errors = [f.exception() for f in all_futures if f.exception() is not None]
        if self.errors:
            raise self.errors[0]

    def is_alive(self):
        with self._lock:
            if self._buffer:
                return True
            futures = list(self._futures)
        return any(not f.done() for f in futures)

    def stop(self):
        with self._lock:
            if self._executor is None:
                raise RuntimeError("cannot stop ExecutionPool before it is started")
            executor = self._executor
        executor.shutdown(wait=True)


class Sweep:
    """
    This class give a user possibility to run multiple simulations (sweep) over defined variables in the input file.

    Parameters
    ----------
    variables_to_sweep : dict
        Dict of variables to sweep in the form of {name1:values1,name2:values2...}
        values should be an iterable object (ideally list)
    fullpath : str
        defined as for InputFile
    configpath : str
        defined as for input files

    Attributes
    ----------
    input_file : InputFile
        the parsed prototype input file whose variables are swept

    Methods
    -------
    save_sweep()
        creates an output folder
        creates input files for all combinations of sweep variables
    execute_sweep()
        execute created input files and saves information to output folder
    """

    def __init__(self, variables_to_sweep, fullpath=None, configpath=None):
        # Keep the argument, not the resolved .configpath: the latter is a real path
        # even when configpath is None, so handing it to the generated input files
        # would make them read the config file from disk and miss anything that was
        # only set() on nextnanopy.config -- which the prototype below, built with
        # configpath=None, does pick up. A sweep's files must run on the same config
        # as the sweep itself.
        self._configpath = configpath
        # Parse the prototype exactly once. Everything the sweep needs from an
        # input file (variables to validate against, fullpath, config, product)
        # comes from this single object instead of a throwaway plus a base-class
        # re-parse.
        self.input_file = InputFile(fullpath=fullpath, configpath=configpath)
        if set(variables_to_sweep.keys()).issubset(self.input_file.variables.keys()):
            self.var_sweep = variables_to_sweep
        else:
            raise ValueError("Defined variables are not variables of input file")
        for value in self.var_sweep.values():
            if not isinstance(value, Iterable):
                raise TypeError("Values of variables_to_sweep should be iterable objects")
        self.sweep_output_directory = None
        self.input_files = []
        self.sweep_infodict = DictList()
        self.sweep_output_infodict = DictList()

    @property
    def fullpath(self):
        return self.input_file.fullpath

    @property
    def config(self):
        return self.input_file.config

    @config.setter
    def config(self, value):
        self.input_file.config = value

    @property
    def configpath(self):
        return self.input_file.configpath

    @property
    def product(self):
        return self.input_file.product

    @property
    def filename_only(self):
        return self.input_file.filename_only

    def save_sweep(
        self,
        delete_old_files=True,
        round_decimal=8,
        integer_only_in_name=False,
        temp=False,
        variables_comb_screen_fn: Callable[..., Any] = None,
    ):
        """
        Parameters
        ----------
        delete_old_files
            if True, deletes files created in previous sweeps
        round_decimal
            number of digits to round in the output folder names
        integer_only_in_name
            if True, only integer values are used in the output folder names
        temp
            if True, input files are saved in temporary directory

        Returns
        -------
        None
        """
        if delete_old_files:
            for inputfile in self.input_files:
                inputfile.remove()
        self.input_files = []
        if temp:
            input_file = InputFile(fullpath=self.fullpath, configpath=self._configpath)
            input_file.save(temp=True, overwrite=True)
            path = input_file.fullpath
        else:
            path = self.fullpath

        self.create_input_files(
            path,
            round_decimal,
            integer_only_in_name=integer_only_in_name,
            variables_comb_screen_fn=variables_comb_screen_fn,
        )

    def save(self, *args, **kwargs):
        """
        Save the sweep input files. See :meth:`save_sweep` for the parameters.

        Notes
        -----
        This is the preferred name. For now it simply forwards to
        :meth:`save_sweep`. In a future patch the two will swap: ``save`` will
        hold the implementation and ``save_sweep`` will become the mirror,
        emitting a deprecation warning.
        """
        return self.save_sweep(*args, **kwargs)

    def prepare_output(self, overwrite=False, output_directory=None):
        self.sweep_output_directory = self.mk_dir(
            overwrite=overwrite, output_directory=output_directory
        )
        self.create_info()

    def _screen_variables_comb(self, iteration_combinations, var_comb_screen_fn):
        return [comb_ for comb_ in iteration_combinations if var_comb_screen_fn(comb_)]

    def create_input_files(
        self,
        input_file_path,
        round_decimal,
        integer_only_in_name=False,
        variables_comb_screen_fn: Callable[..., Any] = None,
    ):
        iteration_combinations = list(itertools.product(*self.var_sweep.values()))
        if variables_comb_screen_fn is not None:
            iteration_combinations = self._screen_variables_comb(
                iteration_combinations, variables_comb_screen_fn
            )

        filename_path, filename_extension = os.path.splitext(input_file_path)
        for combination in iteration_combinations:
            filename_end = "__"
            inputfile = InputFile(fullpath=input_file_path, configpath=self._configpath)
            for var_name, var_value in zip(self.var_sweep.keys(), combination, strict=True):
                inputfile.set_variable(var_name, var_value, comment="THIS VARIABLE IS UNDER SWEEP")
                if isinstance(var_value, str):
                    var_value_string = var_value
                else:
                    var_value_string = round(var_value, round_decimal)
                filename_end += f"{var_name}_{var_value_string}_"
            if integer_only_in_name:
                inputfile.save(overwrite=False)
            else:
                inputfile.save(filename_path + filename_end + filename_extension, overwrite=True)
            variable_combination = dict(zip(self.var_sweep.keys(), combination, strict=True))
            self.input_files.append(inputfile)
            self.sweep_infodict[inputfile.fullpath] = variable_combination

    def execute_sweep(
        self,
        delete_input_files=False,
        overwrite=False,
        show_log=True,
        convergenceCheck=False,
        convergence_check_mode="pause",
        parallel_limit=1,
        separate_sweep_dir=True,
        **kwargs,
    ):
        """
        Execute created input files and saves information to output folder.

        Parameters
        ----------
        delete_input_files : bool, optional
            if True, input_files are deleted after execution. Default is False.
        overwrite : bool, optional
            if True, the output overwrites the old output data. If False, execution will create a new output folder
            (with the unique name, created by adding an integer to the foldername). Default is False.
            It applies to the sweep folder and to the folder of every simulation in
            it, so a sweep run with overwrite=False writes over no earlier output at
            either level. The per-file subfolder itself is always created: it is what
            keeps the sweep points apart.
        show_log : bool, optional
            if True, the simulation log is displayed in the console. If False, the count of current simulation is displayed without log.
            Default is True.
            Note that the log file is always saved in the output folders regardless of this option.
        convergenceCheck : bool, optional
            if True, nextnanopy scans the log file of the simulation performed and check whether the solution has converged.
            If it did not converge, nextnanopy warns you and ask if you want to proceed with postprocessing.
            Note that non-converged solutions are not reliable and further calculation and/or visualization from them do not make much sense.
            Default is False.
        convergence_check_mode : str, optional
            works only for convergenceCheck = True
            options:

            - 'pause': asks user how to proceed if simulation did not converge (default);
              if no interactive terminal is attached (e.g. CI, cluster jobs),
              behaves like 'terminate' instead of blocking on input
            - 'terminate': terminate the script if the simulation did not converge
            - 'continue': notify a user but continues execution of script
        parallel_limit : int, optional
            number of simulations to run simultaneously. Especially useful for simple simulations which might be more efficiently run in parallel. Be aware that
            some nextnano solvers parallelize computations internally in threads (controlled by --threads in nextnanopy config). To avoid unexpected behaviour and
            not desirable decrease of simulation speed use the rule: parallel_limit*threads<= number of physical cores of the machine
            default 1
        separate_sweep_dir : bool, optional
            if True, creates separate directory to store subdirectories of the sweep simulation. If False, stores all directories without separate directory.
            default True
        **kwargs
            see ``**kwargs`` of InputFile.execute()
        """
        try:
            output_directory = kwargs["outputdirectory"]
            del kwargs["outputdirectory"]
        except KeyError:
            output_directory = self.config.get(section=self.product, option="outputdirectory")
        if separate_sweep_dir:
            self.prepare_output(overwrite, output_directory)
            output_directory = self.sweep_output_directory
        else:
            self.sweep_output_directory = output_directory

        if not self.input_files:
            warnings.warn(
                "Nothing was executed in sweep! Input files to execute were not created.",
                stacklevel=2,
            )
            return

        # TODO: delete if statement (use execution_queue for both cases)
        if parallel_limit > 1:
            execution_queue = ExecutionQueue(
                limit_parallel=parallel_limit,
                terminate_empty=True,
                outputdirectory=output_directory,
                show_log=show_log,
                convergenceCheck=convergenceCheck,
                convergence_check_mode=convergence_check_mode,
                overwrite=overwrite,
                **kwargs,
            )
            execution_queue.add(*self.input_files)
            execution_queue.start()

            execution_queue.join()
        else:
            for i, inputfile in enumerate(self.input_files):
                if not show_log:
                    print(f"\nExecuting simulations [{i + 1}/{len(self.input_files)}]...")
                inputfile.execute(
                    outputdirectory=output_directory,
                    show_log=show_log,
                    convergenceCheck=convergenceCheck,
                    convergence_check_mode=convergence_check_mode,
                    overwrite=overwrite,
                    **kwargs,
                )
        if delete_input_files:
            for inputfile in self.input_files:
                inputfile.remove()

        # part where the info is stored
        for inputfile, variable_combination in zip(
            self.input_files, self.sweep_infodict.values(), strict=True
        ):
            self.sweep_output_infodict[str(inputfile.folder_output)] = variable_combination
        # TODO create files with info in output_directories
        if True:  # TODO
            # self.create_infodict_files()
            self.create_infodict_json()

    def execute(self, *args, **kwargs):
        """
        Execute the sweep. See :meth:`execute_sweep` for the parameters.

        Notes
        -----
        This is the preferred name. For now it simply forwards to
        :meth:`execute_sweep`. In a future patch the two will swap: ``execute``
        will hold the implementation and ``execute_sweep`` will become the
        mirror, emitting a deprecation warning.
        """
        return self.execute_sweep(*args, **kwargs)

    def create_infodict_files(self):
        """Creates files with variables under sweep in output directories"""
        raise NotImplementedError

    def create_infodict_json(self):
        """Creates json file to store infodict"""
        import json

        filepath = os.path.join(self.sweep_output_directory, "sweep_infodict.json")
        with open(filepath, "w") as file:
            # default conversion for numpy types
            json.dump(
                self.sweep_output_infodict,
                file,
                indent=4,
                default=lambda o: o.item() if hasattr(o, "item") else o,
            )

    def mk_dir(self, overwrite=False, output_directory=None):
        vars = ""
        for i in self.var_sweep.keys():
            vars += "__" + i
        name_of_file = self.filename_only
        if not output_directory:
            output_directory = self.config.get(section=self.product, option="outputdirectory")
        name = name_of_file + "_sweep" + vars
        if overwrite:
            directory = mkdir_if_not_exist(os.path.join(output_directory, name))
        else:
            directory = mkdir_even_if_exists(output_directory, name)
        return directory

    def create_info(self):
        file_location = os.path.join(self.sweep_output_directory, "sweep_info.txt")
        with open(file_location, "w") as file:
            file.write(f"Input file: '{self.fullpath}' \n")
            file.write("Sweep variables: \n")
            for i in self.var_sweep:
                file.write(f"{i} = {self.var_sweep[i]} \n")
