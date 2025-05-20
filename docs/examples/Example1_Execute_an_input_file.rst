Example 1 - Execute an input file
=================================

About this example: load and execute an input file
--------------------------------------------------

To work with an input file, instantiate an InputFile class object:

.. code:: ipython3

    import nextnanopy as nn
    
    my_input = nn.InputFile(r'..\..\tests\datafiles\nextnano++\example.in')
    print(my_input)


.. parsed-literal::

    InputFile
    fullpath: ..\..\tests\datafiles\nextnano++\example.in
    Input variables: 8 elements
    	$BIAS = 0.0 # Gate voltage(V)
    	$ALLOY = 0.3 # Al content of AlGaAs layer
    	$SIZE = 80 # size of AlGaAs layer (nm)
    	$DOPECONC = 3e+18 # donor concentration of 10nm doping layer (cm^-3)
    	$DOPEPOS = 65 # distance between AlGaAs-GaAs interface and delta doping position (nm)
    	$MINGRID = 0.1 # minimum grid spacing (nm)
    	$NUMEV = 10 # number of eigenvalues to be calculated
    	$BARRIER = 0.7 # height of left Schottky barrier (eV)
    

This object contains all the relevant information of the input file such
as the raw text, the variables and the configuration for the execution
(see Example 0).

When you create ``my_input``, the class will first check automatically
the type of the input file (nextnano++, nextnano3, nextnano.NEGF or
nexntano.MSB). It will then get the raw text and extract all variables
defined in the file:

::

   $my_var = 3    # in nextnano++
   %my_var = 3    ! in nextnano3
   $my_var = 3    # in nextnano.NEGF

What information does it contain?
---------------------------------

``my_input`` has the following relevant attributes:

- fullpath (str): path to the input file including the name
- text (str): return raw text
- variables (list): list of InputVariable objects
- config: nextnano configuration (see Example 0)

.. code:: ipython3

    print(my_input.fullpath)


.. parsed-literal::

    ..\..\tests\datafiles\nextnano++\example.in
    

.. code:: ipython3

    my_input.preview()


.. parsed-literal::

    0 # 1D sample for solving quantum-poisson
    1 
    2 #Begin NextnanoWizard parameter section
    3 $BIAS = 0.0 # Gate voltage(V)
    4 $ALLOY = 0.3 # Al content of AlGaAs layer
    5 $SIZE = 80 # size of AlGaAs layer (nm)
    6 $DOPECONC = 3e+18 # donor concentration of 10nm doping layer (cm^-3)
    7 $DOPEPOS = 65 # distance between AlGaAs-GaAs interface and delta doping position (nm)
    8 $MINGRID = 0.1 # minimum grid spacing (nm)
    9 $NUMEV = 10 # number of eigenvalues to be calculated
    10 $BARRIER = 0.7 # height of left Schottky barrier (eV)
    11 #End NextnanoWizard parameter section
    12 
    13 
    14 global{
    15    simulate1D{}
    16    
    17    temperature = 4
    18 
    19    substrate{ name = "GaAs" }
    20 
    21    crystal_zb{ x_hkl = [1, 0, 0] y_hkl = [0, 1, 0] }
    22 }
    23 
    24 
    25 grid{
    26    xgrid{
    27       line{ pos = 0                   spacing = 0.5 }
    28       line{ pos = 10                  spacing = 0.5 }
    29       line{ pos = 10+$SIZE-$DOPEPOS-5 spacing = 0.5 }
    30       line{ pos = 10+$SIZE-$DOPEPOS+5 spacing = 0.5 }
    31       line{ pos = 10+$SIZE            spacing = $MINGRID }
    32       line{ pos = 400                 spacing = 5 }
    33    }
    34 }
    35 
    36 
    37 impurities{
    38    donor{ name = "Si" energy = -10 degeneracy = 2 } # fully ionized
    39 }
    40 
    41 
    42 contacts{
    43    schottky{ 
    44       name = "gate"
    45       bias = 0
    46       barrier = $BARRIER
    47    }
    48 
    49    fermi{ 
    50       name = "backgate"
    51       bias = -$BIAS
    52    }
    53 }
    54 
    55 
    56 structure{
    57    output_material_index{}
    58    output_contact_index{}
    59    output_impurities{}
    60 
    61    # AlGaAs layer
    62    region{
    63       everywhere{} # default material
    64       ternary_constant{ name = "Al(x)Ga(1-x)As" alloy_x = $ALLOY }
    65    }
    66 
    67    # GaAs cap layer
    68    region{
    69       line{ x = [0, 10] }
    70       binary{ name = "GaAs" }
    71    }
    72 
    73    # doping layer
    74    region{
    75       line{ x = [10+$SIZE-$DOPEPOS-5, 10+$SIZE-$DOPEPOS+5] }
    76       doping{ constant{ name = "Si" conc = $DOPECONC} }
    77    }
    78 
    79    # GaAs substrate
    80    region{
    81       line{ x = [10+$SIZE, 4000] }
    82       binary{ name = "GaAs" }
    83    }
    84 
    85    #  Top gate (Schottky contact)
    86    region{ 
    87       line{ x = [0, 1] }
    88       contact{ name = "gate" }
    89    }
    90 
    91    # Back gate (Ohmic contact)
    92    region{ 
    93       line{ x = [390, 400] }
    94       contact{ name = "backgate" }
    95    }
    96 }
    97 
    98 
    99 classical{
    100    Gamma{}
    101    HH{}
    102 
    103    output_bandedges{}
    104    output_carrier_densities{}
    105    output_ionized_dopant_densities{}
    106 }
    107 
    108 
    109 quantum {
    110    region{
    111       name = "2DEG"
    112       x = [10+$SIZE-5, 250]
    113       Gamma{ num_ev = $NUMEV }
    114       output_wavefunctions{ probabilities = yes  max_num = $NUMEV }
    115    }
    116 }
    117 
    118 
    119 poisson{
    120    output_potential{}
    121 }
    122 
    123 
    124 currents{
    125    recombination_model{
    126       SRH         = no
    127       Auger       = no
    128       radiative   = no
    129    }
    130    insulator_bandgap = 0.05 # guarantees that fermi level drops in barrier region without solving current equation
    131    output_fermi_levels{}
    132 }
    133 
    134 
    135 run{
    136    solve_poisson{}
    137    solve_quantum{}
    138    outer_iteration{} # solve coupled Schrödinger-Poisson equations
    139 }
    140 
    

Input variables
---------------

The input variables are stored in ``my_input.variables`` as a list of
``InputVariable`` objects.

These objects have the following attributes:

- name (str)
- value (undefined)
- unit (str, optional)
- comment (str, optional)
- metadata (dict, optional)
- text (str): raw text in the input file for a given variable

.. code:: ipython3

    print(f"List of variables: {my_input.variables}")


.. parsed-literal::

    List of variables: DictList([
    (index: 0 - key: 'BIAS' - $BIAS = 0.0 # Gate voltage(V)),
    (index: 1 - key: 'ALLOY' - $ALLOY = 0.3 # Al content of AlGaAs layer),
    (index: 2 - key: 'SIZE' - $SIZE = 80 # size of AlGaAs layer (nm)),
    (index: 3 - key: 'DOPECONC' - $DOPECONC = 3e+18 # donor concentration of 10nm doping layer (cm^-3)),
    (index: 4 - key: 'DOPEPOS' - $DOPEPOS = 65 # distance between AlGaAs-GaAs interface and delta doping position (nm)),
    (index: 5 - key: 'MINGRID' - $MINGRID = 0.1 # minimum grid spacing (nm)),
    (index: 6 - key: 'NUMEV' - $NUMEV = 10 # number of eigenvalues to be calculated),
    (index: 7 - key: 'BARRIER' - $BARRIER = 0.7 # height of left Schottky barrier (eV))
    ])
    

Get a variables
~~~~~~~~~~~~~~~

There are several methods to do so:

.. code:: python

   my_input.get_variable(name) # method 1 (recommended)
   my_input.variables[name] # method 2 (recommended)
   my_input[name] # method 3
   my_input.variables[index] # method 4

Let’s have a quick look of the variables in this file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    for var in my_input.variables:
        print(var.text)


.. parsed-literal::

    $BIAS = 0.0 # Gate voltage(V)
    $ALLOY = 0.3 # Al content of AlGaAs layer
    $SIZE = 80 # size of AlGaAs layer (nm)
    $DOPECONC = 3e+18 # donor concentration of 10nm doping layer (cm^-3)
    $DOPEPOS = 65 # distance between AlGaAs-GaAs interface and delta doping position (nm)
    $MINGRID = 0.1 # minimum grid spacing (nm)
    $NUMEV = 10 # number of eigenvalues to be calculated
    $BARRIER = 0.7 # height of left Schottky barrier (eV)
    

Variable line number
~~~~~~~~~~~~~~~~~~~~

You can also check the line number in the input file where the variable
is defined:

.. code:: ipython3

    my_input.variables['BIAS'].metadata




.. parsed-literal::

    {'line_idx': 3}



Modify the variable
~~~~~~~~~~~~~~~~~~~

To modify the value of a given variable, you can do:

.. code:: python

   my_input.set_variable('BIAS', value=3)

You can also change the comment:

.. code:: python

   my_input.set_variable('BIAS', comment='this is a new comment')

You can change both at the same time:

.. code:: python

   my_input.set_variable('BIAS', value=3, comment='this is a new comment')

.. code:: ipython3

    print(f"Old variable: {my_input.get_variable('BIAS').text}")
    my_input.set_variable('BIAS', value=3, comment='this is a new comment')
    print(f"New variable: {my_input.get_variable('BIAS').text}")


.. parsed-literal::

    Old variable: $BIAS = 0.0 # Gate voltage(V)
    New variable: $BIAS = 3 # this is a new comment
    

Save the current file
---------------------

``my_input`` has a method ``save`` which saves the current input file.

.. code:: python

   my_input.save()

By default, it does not overwrite the current file and save it with an
unused name (like example_1.in).

You can overwrite the current file with the option:

.. code:: python

   my_input.save(overwrite=True)

You can save it in another location with a new name:

.. code:: python

   my_input.save('new_path\new_input.in')

Automatically, ``my_input.fullpath`` is updated if the saving was
successful.

By default, if the new location does not exist, it will create the
folder automatically. To turn this option off, use:

.. code:: python

   my_input.save('new_path\new_input.in', automkdir=False)

You can get help for these options from Command prompt:

.. code:: ipython3

    help(my_input.save)


.. parsed-literal::

    Help on method save in module nextnanopy.inputs:
    
    save(fullpath=None, overwrite=False, automkdir=True) method of nextnanopy.inputs.InputFile instance
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
    
    

Execute the input file
----------------------

To execute the input file, run:

.. code:: python

   my_input.execute()

Make sure you have saved the file before execution, otherwise your
modification to the input file does not take effect.

The ``execute`` method without any arguments will use the configuration
stored in ``my_input.config``. As explained in Example 0, it will
automatically detect the nextnano product (nextnano++, nextnano3,
nextnano.NEGF or nextnano.MSB) and will load the corresponding
configuration parameters prior to the execution.

To suppress the simulation log in the Python console, use

.. code:: python

   my_input.execute(show_log=False)

(Default is ``True``). Note that the log file is always saved in the
output folder regardless of this option.

From 2022-03-22, a new option

.. code:: python

   my_input.execute(convergenceCheck=True)

is available (default is ``False``). If ``True``, nextnanopy scans the
log file of the simulation performed and check whether the solution has
converged. If it did not converge, nextnanopy warns you and ask if you
want to proceed with postprocessing. Note that non-converged solutions
are not reliable and further calculation and/or visualization from them
do not make much sense.

You can get help for these options from Command prompt:

.. code:: ipython3

    help(my_input.execute)


.. parsed-literal::

    Help on method execute in module nextnanopy.inputs:
    
    execute(**kwargs) method of nextnanopy.inputs.InputFile instance
        Execute the input file located at .fullpath
        Individual kwargs can be passed like 'license' or 'database'
        If no kwargs is specified, it will use the default values in .config
        
        Parameters
        ----------
        exe : str, optional
            path to executable
        license : str, optional
            path to license file
        database : str, optional
            path to database file
        outputdirectory : str, optional
            path where to save the simulated data
        
        Other parameters can be used depending on the nextnano product.
        For example, 'threads' is accepted for nextnano++.
        Please, see the documentation of the command line arguments for each nextnano product
        in the website (https://www.nextnano.com/)
    
    

Get information after executing the file
----------------------------------------

The output folder of the simulation is stored at:

.. code:: python

   my_input.folder_output

You can access all the relevant information from the execution, e.g.,
the log file location, the command line arguments, via:

.. code:: python

   my_input.execute_info

.. code:: ipython3

    my_input.folder_output




.. parsed-literal::

    'E:\\junliang.wang\\nextnano\\Output\\example'



Sweep an input variable
-----------------------

**Automatic sweep is now supported. Please refer to Example 4.**

You can sweep its value and execute the input file in a simple loop.
Manual sweep might look like:

.. code:: python

   for value in [0, 1, 2]:
       my_input.set_variable('BIAS', value=value)
       my_input.save() # remember that by default, overwrite is False.
       my_input.execute() 

Change filename and input folder
--------------------------------

If you want to change the current filename or the current input folder,
you can do the following:

.. code:: python

   my_input.filename = 'new_file.in'
   my_input.filename_only = 'new_file' # it will use the original file extension
   my_input.folder_input = 'new_folder'

Please contact python@nextnano.com for any issues with this document.
