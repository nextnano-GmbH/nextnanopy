import os,sys
import threading
import time
import warnings
import itertools
import queue
import nextnanopy
from nextnanopy.utils.formatting import text_to_lines, lines_to_text
from nextnanopy.utils.mycollections import DictList
from nextnanopy.utils.misc import savetxt, get_filename, get_folder, get_file_extension, message_decorator, mkdir_even_if_exists, mkdir_if_not_exist
from nextnanopy.commands import execute as cmd_execute
from nextnanopy import defaults
from collections.abc import Iterable
import tempfile
import atexit


_msgs = defaults.messages['load_input']
load_message = lambda method: message_decorator(method, init_msg=_msgs[0], end_msg=_msgs[1])
_msgs = defaults.messages['save_input']
save_message = lambda method: message_decorator(method, init_msg=_msgs[0], end_msg=_msgs[1])
_msgs = defaults.messages['execute_input']
execute_message = lambda method: message_decorator(method, init_msg=_msgs[0], end_msg=_msgs[1])


class InputFileTemplate(object):
    """
        This class stores and manipulates any kind of nextnano input files.
        For each nextnano product, the syntax is different but the core information
        is very similar like the variables that can be changed.
        This class contains useful methods such as to get a preview of the file or
        execute a simulation.

        The initialization of the class will execute the load method and setup the
        config file.

        ...

        Parameters
        ----------
        fullpath : str
            path to the file.
            If it is not None, it will load the file (default: None)
        configpath : str
            path to the config file.
            If it is None, it will use the default configuration (default: None)


        Attributes
        ----------

        fullpath : str
            path to the file (default: None)
        configpath : str
            path to the config file (default: your home path)
        variables : DictList
            input variables defined in the file (default: DictList())
        raw_lines : list
            list of str of each line in the file
        text : str
            raw text of the file (settable)
        lines : list
            raw_lines updated with the current input variable parameters
        filename : str
            name with the file extension (settable)
        filename_only :
            name without the file extension (settable)
        folder_input : str
            folder of the fullpath (settable)
        folder_output : str
            folder where the simulated data is stored after execution
        product : str
            detected nextnano product when the file is loaded (default: 'not valid')
        config: nextnano.NNConfig
            config file object
        execute_info: dict
            information after executing the file

        Methods
        -------
        preview(nums=True)
            print the text of the file.

        load(fullpath)
            load an input file

        save(fullpath=None, overwrite=False, automkdir=True)
            save the current information into a file.

        execute(**kwargs)
            execute the input file located at .fullpath

        get_variable(name)
            equivalent to self.variables[name]

        set_variable(name, value=None, comment=None)
            change the value and/or the comment of self.variable[name]
            If value or comment is None, it won't change that parameter
    """
    _shared_temp_dir = None

    def __init__(self, fullpath=None, configpath=None):
        self.raw_lines = []
        self.variables = DictList()
        self.content = None
        self.fullpath = fullpath
        self.product = 'not valid'
        self.__parallel__ = False
        if fullpath is not None:
            self.load(fullpath)
        if configpath is None:
            self.config = defaults.NNConfig()
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
            idx = ivar.metadata['line_idx']
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
        self.filename = f'{name}{ext}'

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
        key = 'outputdirectory'
        if key in self.execute_info.keys():
            return self.execute_info[key]
        else:
            raise KeyError('Input file has not been executed yet')

    def preview(self, nums=True):
        """
        Print the text of the file.

        Parameters
        ----------
        nums : bool, optional
            If it is True, it will show the number of each line. (default is True)
        """
        for i, line in enumerate(self.lines):
            if nums:
                print(f'{i} {line}')
            else:
                print(f'{line}')

    @load_message
    def load(self, fullpath):
        """
        The steps are the following:
            1. clear the current information
            2. load the raw text (update .fullpath and .raw_lines)
            3. find the nextnano product (update .product)
            4. validate the input file
            5. load the input variables (update .variables)
            6. load content (when applicable)

        Parameters
        ----------
        fullpath : str
            path to the file to be loaded
        """
        self.clear()
        self.fullpath = fullpath
        self.load_raw()
        self.find_product()
        self.validate()
        self.load_variables()
        self.load_content()

    def find_product(self):
        self.product = defaults.input_text_type(self.raw_text)
        return self.product

    def validate(self):
        if self.product not in defaults.products:
            self.product = 'Not valid'
            #raise ValueError(f'Not valid input file')

    @save_message
    def save(self, fullpath=None, overwrite=False, automkdir=True, temp=False):
        """
        Save the current information into a file.

        Parameters
        ----------
        fullpath : str, optional
            path including the file name where it will be saved (default is None)
            If None, it will use the current .fullpath
        overwrite : bool, optional
            If it is False, it will find an unused name by adding an extra index like _1
            (default is False)
        automkdir : bool, optional
            If it is True, it will create the folder if it does not exist.
            (default is False)
        temp: bool, optional
            If it is True, it will save the file in a temporary location.
            (default is False)
        """
        if temp and fullpath is not None:
            warnings.warn('Fullpath is specified, temp flag is ignored')
        if fullpath is None:
            if temp:
                folder = self._get_temp_dir()
                fullpath = os.path.join(folder, self.filename)
            elif self.fullpath is None:
                raise ValueError('Please, specify a fullpath')
            else:
                fullpath = self.fullpath
        
        self.fullpath = savetxt(fullpath=fullpath, text=self.text, overwrite=overwrite, automkdir=automkdir)
        return self.fullpath

    @execute_message
    def execute(self, show_log = True, convergenceCheck = False, convergence_check_mode = 'pause',**kwargs):
        """
        Execute the input file located at .fullpath
        Individual kwargs can be passed like 'license' or 'database'
        If no kwargs is specified, it will use the default values in .config

        Parameters
        ----------
        show_log : bool, optional
            if False, suppress the simulation log
            (default is True)
        convergenceCheck : bool, optional
            if True, check convergence of the simulation
            (default is False)
        convergence_check_mode: string
            works only for convergenceCheck = True
            options:
                'pause': asks user how to proceed if simulation did not converge (default)
                'terminate': terminate the script if the simulation did not converge
                'continue': notify a user but continues execution of script
        kwargs may contain:
            exe : str, optional
                path to executable
            license : str, optional
                path to license file
            database : str, optional
                path to database file
            outputdirectory : str, optional
                path where to save the simulated data
        and other parameters depending on the nextnano product.
        For example, 'threads' is accepted by nextnano++.
        See the documentation of the command line arguments of each nextnano product
        on the online Manual (https://www.nextnano.de/manual/).
        """

        cmd_kwargs = dict(self.default_command_args)
        cmd_kwargs.update(kwargs)
        cmd_kwargs['inputfile'] = self.fullpath
        info = cmd_execute(show_log=show_log, parallel = self.__parallel__, **cmd_kwargs)
        self.execute_info = info
        if convergenceCheck and not self.__parallel__: #- possible solution for later (delete comment if not)
            self.check_convergence(mode= convergence_check_mode)
        return info

    def check_convergence(self, mode = 'pause'):
        if self.product == 'nextnano.MSB':
            raise NotImplementedError('Convergence check has not yet implemented for nextnano.MSB!')
            
        log = self.execute_info['logfile']
        try:
            if self.product == 'nextnano3':
                with open(log, 'r') as file:
                    for line in file:
                        if 'Exiting iteration and terminating simulation' in line or 'Program was terminated using a soft kill' in line or 'Terminating immediately' in line:
                            raise RuntimeError(f'\nSimulation got terminated! Check the log:\n{log}')
                        elif 'Maximum number of iterations exceeded' in line:
                            raise RuntimeError(f'\nSimulation did not converge! Check the log:\n{log}')
            elif self.product == 'nextnano++':
                with open(log, 'r') as file:
                    for line in file:
                        if 'Terminating program' in line:
                            raise RuntimeError(f'\nSimulation got terminated! Check the log:\n{log}')
                        elif 'Maximum number of iterations exceeded' in line:
                            raise RuntimeError(f'\nSimulation did not converge! Check the log:\n{log}')
                        elif 'Outdated numerics library (f95library) used' in line:
                            raise RuntimeError(f'\nOutdated numerics library (f95library) used.')
            elif self.product == 'nextnano.NEGF' or self.product == 'nextnano.NEGF++':   # NEGF reports convergence at every voltage and temperature sweep.
                with open(log, 'r') as file:
                    for line in file:
                        if 'Simulation has NOT CONVERGED' in line:
                            raise RuntimeError(f'\nSimulation has diverged! Check the log:\n{log}')
                        elif 'Simulation has partially converged' in line:
                            print(f'\nWARNING: check_convergence(): Simulation did not fully converge.')
                        elif 'Terminating program!' in line:
                            raise RuntimeError(f'\nSimulation got terminated! Check the log:\n{log}')
        except FileNotFoundError:
            print(f'Log file {log} not found!')
            if mode != 'continue':
                raise
            else:
                pass
        except RuntimeError as e:
            print(e)
            if mode == 'pause':
                pause = True
                while pause:
                    answer = input('Do you nevertheless want to continue? [y/n]: ')
                    if answer == 'y' or answer == 'yes':
                        pause = False
                        return
                    elif answer == 'n' or answer == 'no':
                        pause = False
                        raise RuntimeError('Nextnanopy terminated.')
                    else:
                        print('Invalid input.')
                        continue
            elif mode == 'terminate':
                raise RuntimeError('Nextnanopy terminated.')
            elif mode == 'continue':
                return
            else:
                raise ValueError(f'Mode "{mode}" is not valid')
        else:
            return

    def clear(self):
        self.raw_lines = []
        self.variables = DictList()
        self.fullpath = None

    def remove(self):
        if os.path.exists(self.fullpath):
            os.remove(self.fullpath)

    def load_raw(self):
        with open(self.fullpath, 'r') as f:
            text = f.read()
        self.raw_lines = list(text_to_lines(text))
        return self.raw_lines

    def load_variables(self):
        pass

    def load_content(self):
        pass

    def get_variable(self, name):
        """
        Equivalent to self.variables[name]

        Parameters
        ----------
        name : str
            key for self.variables

        Raises
        ------
        KeyError
            If name is not a key of self.variables
        """
        if name not in self.variables.keys():
            raise KeyError(f'{name} is not a valid variable.')
        return self.variables[name]

    def set_variable(self, name, value=None, comment=None, unit = None):
        """
        Change the value and/or the comment of self.variable[name]

        Parameters
        ----------
        name : str
            key for self.variables
        value : not defined, optional
            Equivalent to self.variables[name].value = value (default is None)
            If it is None, it won't change it
        comment : not defined, optional
            Equivalent to self.variables[name].comment = comment (default is None)
            If it is None, it won't change it
        unit : not defined, optional
            Equivalent to self.variables[name].unit = unit (default is None)
            If it is None, it won't change it
        """

        var = self.get_variable(name)
        if value is not None:
            var.value = value
        if comment is not None:
            var.comment = comment
        if unit is not None:
            var.unit  = unit
        return var

    def __getitem__(self, item):
        return self.variables[item]

    def __setitem__(self, item, value):
        self.variables[item] = value

    def __delitem__(self, item):
        del self.variables[item]

    def __repr__(self):
        out = []
        out.append(f'{self.__class__.__name__}')
        out.append(f'fullpath: {self.fullpath}')
        out.append(f'Input variables: {len(self.variables)} elements')
        for key, var in self.variables.items():
            out.append(f'\t{str(var)}')
        out = '\n'.join(out)
        return out

    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self):
        try:
            result = self.variables.__getitem__(self._iter_index)
        except (IndexError, KeyError):
            raise StopIteration
        self._iter_index += 1
        return result


# def decor(func):
#     def inner(*args,**kwargs):
#
#         args = list(args)
#         initial_object = args[0]
#         if hasattr(initial_object, '_helper_input_file'):
#             helper =  initial_object._helper_input_file
#         else:
#             func(*args,**kwargs)
#             return
#
#         helper_func = getattr(helper, func.__name__)
#
#
#         args = args[1:]
#
#
#         # print(kwargs)
#         #print('Start of decor message')
#         helper_func(*args, **kwargs)
#
#         for key in helper.__dict__:
#             setattr(initial_object, key, helper.__dict__[key])
#         #print('End of decor message')
#     return inner
#
# def class_decorator(cls):
#     for attr_name in dir(cls):
#         attr_value = getattr(cls, attr_name)
#         if hasattr(attr_value, '__call__') and not attr_name.startswith('__') and attr_name !='load': # check if attr is a function
#             setattr(cls, attr_name, decor(attr_value))
#     return cls



#@class_decorator
class InputFile(InputFileTemplate):
    # def __init__(self,fullpath = None, configpath = None):
    #
    #     self.raw_lines = []
    #     self.variables = DictList()
    #     self.content = None
    #     self.fullpath = fullpath
    #     self.product = 'not valid'
    #     self.__parallel__ = False
    #     if fullpath is not None:
    #         self.clear()
    #         self.fullpath = fullpath
    #         self.load_raw()
    #         self.find_product()
    #         self.validate()
    #     if configpath is None:
    #         self.config = defaults.NNConfig()
    #     else:
    #         self.config = defaults.NNConfig(configpath)
    #     self.execute_info = {}
    #
    #
    #     _helper_input_file_type = defaults.get_InputFile(self.product)
    #     self._helper_input_file = _helper_input_file_type(fullpath = fullpath, configpath = configpath)
    #
    #     for key in self._helper_input_file.__dict__:
    #         setattr(self, key, self._helper_input_file.__dict__[key])

    def __new__(cls, fullpath=None, configpath=None, *args, **kwargs):
        preInputFile = InputFileTemplate(fullpath,configpath)
        _InputFileType = defaults.get_InputFile(preInputFile.product)
        return _InputFileType(fullpath, configpath)

    # def load_variables(self):
    #     """
    #     Convenient method to find the best loading method for each nextnano product.
    #     self.variables will be updated
    #     """
    #     _InputFile = defaults.get_InputFile(self.product)
    #     file = _InputFile()
    #     file.text = self.text
    #     self.variables = file.variables
    #
    # def load_content(self):
    #     _InputFile = defaults.get_InputFile(self.product)
    #     file = _InputFile()
    #     file.text = self.text
    #     file.load_content()
    #     self.content = file.content
    #
    # @property
    # def lines(self):
    #     """
    #     update method to support NEGF input
    #     """
    #     try:
    #         _InputFile = defaults.get_InputFile(self.product)
    #     except ValueError:
    #         _InputFile = InputFileTemplate
    #
    #
    #     file = _InputFile()
    #     #file.product = self.product
    #     #file.text = self.raw_text
    #     #file.variables = self.variables
    #     #print(file.product)
    #     #print(type(file))
    #     file.variables = self.variables
    #     file.raw_lines = self.raw_lines
    #     return file.lines

class ExecutionQueue(threading.Thread):
    """
        This class take InputFiles and add them in the execution queue.
        Depending on limit_parallel, InputFiles are executed in parallel or sequentially.


        Parameters
        ----------
        limit_parallel: int
            number of InputFiles to be executed in parallel (default: 1)
        terminate_empty : bool
            If True, terminates once all added files are executed and logged.
            If you want to add more input files even after execution of all added in the beginning, use termanate_empy = False
            Then the ExecutionQueue has to be stopped manually later (ExecutionQueue.stop())
        convergenceCheck: bool
            see convergenceCheck in InputFile

        **execution_kwargs: parameters to be taken by InputFile.execute()




        Attributes
        ----------
        waiting_queue: queue.Queue
            queue of InputFile objects to be executed
        started: list
            list of (simulation_info:dict, InputFile) currently executing

        finished: list
            list of simulation_infos for finished simulations

        stop_when_empty: bool
            see terminate_empty parameter
        daemon: bool
            see threading.Thread.daemon

        Methods
        ----------- for user
        add(*input_files)
            adds InputFiles to queue

        start()
            start the thread (i.e. execution)
            see threading.Thread.start()

        stop()
            stop the thread (once all added files are executed)
            only necessary if termanate_empty = True


        -------internal (or for advanced users)
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
    def __init__(self, limit_parallel : int = 1 , maxsize : int = 0, terminate_empty : bool = True, convergenceCheck = False, **execution_kwargs):
        super(ExecutionQueue, self).__init__()
        self.waiting_queue = queue.Queue()#should be queue of InputFile objects
        self.started = []#should be list of execution_infos
        self.finished = []#should be list of execution_infos
        self.limit_parallel = limit_parallel
        self.execution_kwargs = execution_kwargs
        self.convergenceCheck = convergenceCheck
        self.stop_when_empty = terminate_empty
        self.daemon = False
    def all_done(self):
        return not bool(not self.waiting_queue.empty() or self.started)

    def add(self,*input_files: InputFileTemplate):
        for input_file in input_files:
            self.waiting_queue.put(input_file)

    def stop(self):
        self.stop_when_empty = True


    def add_execution(self):
        if (len(self.started) < self.limit_parallel) and not self.waiting_queue.empty():
            input_f = self.waiting_queue.get()
            if self.limit_parallel>1:
                input_f.__parallel__ = True
            if 'show_log' in self.execution_kwargs and not self.execution_kwargs['show_log']:
                print(f"\nRemaining simulations in the queue: ", self.waiting_queue.qsize())
            info = input_f.execute(**self.execution_kwargs)
            self.started.append((info,input_f))

    def log_finished(self):
        if self.limit_parallel>1:
            i = 0
            while i < len(self.started):
                poll = self.started[i][0]['process'].poll()
                if poll is None:
                    i+=1
                else:
                    #TODO check once again del
                    self.started[i][0]['process'].wait()
                    tout = self.started[i][0]['tout']
                    terr = self.started[i][0]['terr']
                    for t in (tout, terr):
                        t.join()
                    self.started[i][0]['queue'].put(None)
                    if self.convergenceCheck:
                        if 'convergence_check_mode' in self.execution_kwargs:
                            convergence_check_mode = self.execution_kwargs['convergence_check_mode']
                        else:
                            convergence_check_mode = 'pause'
                        self.started[i][1].check_convergence(mode = convergence_check_mode)
                    self.finished.append(self.started[i][0])
                    del self.started[i]


        else:
            i = 0
            while i < len(self.started):
                poll = self.started[i][0]['process'].poll()
                if poll is None:
                    i+=1
                else:
                    self.finished.append(self.started[i][0])
                    del self.started[i]

    def run(self):
        while True:
            self.add_execution()
            self.log_finished()
            if self.all_done():
                print('\nWaiting queue is empty, all execution and logging are finished')

                if self.stop_when_empty:
                    break
                while self.all_done() and not self.stop_when_empty:
                    time.sleep(0.1) #to ensure switch to main thread
                    pass



class Sweep(InputFileTemplate):
    """
        This class give a user possibility to run multiple simulations (sweep) over defined variables in the input file.


        Parameters:
        -------------------
        variables_to_sweep: dict
            Dict of variables to sweep in the form of {name1:values1,name2:values2...}
            values should be an iterable object (ideally list)
        fullpath: str
            defined as for InputFile
        configpath: str
            defined as for input files


        Methods:
        --------
        save_sweep()
            creates an output folder
            creates input files for all combinations of sweep variables
        execute_sweep():
            execute created input files and saves information to output folder

    """
    def __init__(self,variables_to_sweep,fullpath=None, configpath=None):
        testInputFile = InputFile(fullpath = fullpath, configpath = configpath)
        super().__init__(fullpath, configpath)
        if set(variables_to_sweep.keys()).issubset(testInputFile.variables.keys()):
            self.var_sweep = variables_to_sweep
        else:
            raise ValueError('Defined variables are not variables of input file')
        for value in self.var_sweep.values():
            if not isinstance(value, Iterable):
                raise TypeError('Values of variables_to_sweep should be iterable objects')
        self.sweep_output_directory = None
        self.input_files = []
        self.sweep_infodict = DictList()
        self.sweep_output_infodict = DictList()

    def save_sweep(self, delete_old_files = True, round_decimal = 8, integer_only_in_name = False):
        """

        Parameters
        ----------
        delete_old_files: if True, deletes files created in previous sweeps
        round: number of digits to round in the output folder names

        Returns
        -------
        None
        """
        if delete_old_files == True:
            for inputfile in self.input_files:
                inputfile.remove()
        self.input_files = []
        self.create_input_files(round_decimal, integer_only_in_name = integer_only_in_name)

    def prepare_output(self, overwrite = False, output_directory = None):
        self.sweep_output_directory = self.mk_dir(overwrite=overwrite, output_directory = output_directory)
        self.create_info()

    def create_input_files(self, round_decimal, integer_only_in_name = False):
        iteration_combinations = list(itertools.product(*self.var_sweep.values()))
        filename_path, filename_extension = os.path.splitext(self.fullpath)
        for combination in iteration_combinations:
            filename_end = '__'
            inputfile = InputFile(fullpath = self.fullpath, configpath = self.configpath)
            for var_name, var_value in zip(self.var_sweep.keys(), combination):
                inputfile.set_variable(var_name, var_value, comment='THIS VARIABLE IS UNDER SWEEP')
                if isinstance(var_value,str):
                    var_value_string = var_value
                else:
                    var_value_string = round(var_value, round_decimal)
                filename_end += '{}_{}_'.format(var_name, var_value_string)
            if integer_only_in_name:
                inputfile.save(overwrite = False)
            else:
                inputfile.save(filename_path + filename_end + filename_extension, overwrite = True)
            variable_combination =  dict(zip(self.var_sweep.keys(), combination))
            self.input_files.append(inputfile)
            self.sweep_infodict[inputfile.fullpath] = variable_combination


    def execute_sweep(self, delete_input_files = False, overwrite = False, show_log = True, convergenceCheck = False, convergence_check_mode = 'pause', parallel_limit = 1, separate_sweep_dir = True, **kwargs):
        """
        Execute created input files and saves information to output folder.

        Parameters
        ----------
        delete_input_files : bool, optional
            if True, input_files are deleted after execution. Default is False.
        overwrite : bool, optional
            if True, the output overwrites the old output data. If False, execution will create a new output folder
            (with the unique name, created by adding an integer to the foldername). Default is False.
        show_log : bool, optional
            if True, the simulation log is displayed in the console. If False, the count of current simulation is displayed without log. 
            Default is True.
            Note that the log file is always saved in the output folders regardless of this option.
        convergenceCheck : bool, optional
            if True, nextnanopy scans the log file of the simulation performed and check whether the solution has converged. 
            If it did not converge, nextnanopy warns you and ask if you want to proceed with postprocessing. 
            Note that non-converged solutions are not reliable and further calculation and/or visualization from them do not make much sense. 
            Default is False.
        parallel_limit: int, optional
            number of simulation to run simultaniously. Espicially usefull for simple simulations which migh be more efficiently rn in parallel. Be aware that
            some nextnano solvers parallelize computations internally in threads (controlled by --threads in nextnanopy config). To avoid unexpected behaviour and
            not desirable decrease of simulation speed use the rule: parallel_limit*threads<= number of physical cores of the mahcine
            default 1
        separate_sweep_dir: bool, optional
            if True, creates separate directory to store subdirectories of the sweep simulation. If False, stores all directories without separate directory.
            default True
        **kwargs:
            see **kwargs of InputFile.execute()
        """
        try:
            output_directory = kwargs['outputdirectory']
            del kwargs['outputdirectory']
        except KeyError:
            output_directory = self.config.get(section = self.product,option = 'outputdirectory')
        if separate_sweep_dir:
            self.prepare_output(overwrite, output_directory)
            output_directory = self.sweep_output_directory
        else:
            self.sweep_output_directory = output_directory

        if not self.input_files:
            warnings.warn('Nothing was executed in sweep! Input files to execute were not created.')
            return

        #TODO: delete if statement (use execution_queue for both cases)
        if parallel_limit>1:
            execution_queue = ExecutionQueue(limit_parallel=parallel_limit, terminate_empty=True, outputdirectory = output_directory, show_log = show_log, convergenceCheck = convergenceCheck, convergence_check_mode = convergence_check_mode, **kwargs)
            execution_queue.add(*self.input_files)
            execution_queue.start()

            execution_queue.join()
        else:
            for i, inputfile in enumerate(self.input_files):
                if not show_log:
                    print(f"\nExecuting simulations [{i+1}/{len(self.input_files)}]...")
                info = inputfile.execute(outputdirectory = output_directory, show_log = show_log, convergenceCheck = convergenceCheck, convergence_check_mode = convergence_check_mode,**kwargs)
        if delete_input_files:
            for inputfile in self.input_files:
                inputfile.remove()

        #part where the info is stored
        for inputfile, variable_combination in zip(self.input_files, self.sweep_infodict.values()):
            self.sweep_output_infodict[inputfile.folder_output] = variable_combination
        # TODO create files with info in output_directories
        if True:# TODO
            # self.create_infodict_files()
            self.create_infodict_json()

    def create_infodict_files(self):
        """
        Creates files with variables under sweep in output directories

        """
        raise NotImplementedError

    def create_infodict_json(self):
        """
        Creates json file to store infodict
        """
        import json
        filepath = os.path.join(self.sweep_output_directory, 'sweep_infodict.json')
        with open(filepath, "w") as file:
            json.dump(self.sweep_output_infodict, file, indent=4)

    def mk_dir(self,overwrite = False, output_directory = None):
        vars = ''
        for i in self.var_sweep.keys():
            vars+=('__'+i)
        name_of_file = self.filename_only
        if not output_directory:
            output_directory = self.config.get(section = self.product,option = 'outputdirectory')
        name = (name_of_file+'_sweep'+vars)
        if overwrite:
            directory = mkdir_if_not_exist(os.path.join(output_directory,name))
        else:
            directory = mkdir_even_if_exists(output_directory,name)
        return directory

    def create_info(self):
        file_location = os.path.join(self.sweep_output_directory,'sweep_info.txt')
        with open(file_location,'w') as file:
            file.write("Input file: '{}' \n".format(self.fullpath))
            file.write("Sweep variables: \n")
            for i in self.var_sweep:
                file.write("{} = {} \n".format(i,self.var_sweep[i]))




