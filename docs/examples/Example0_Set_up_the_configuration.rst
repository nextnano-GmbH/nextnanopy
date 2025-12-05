Example 0: Set up the configuration
===================================

About this example: nextnano configuration
------------------------------------------

If you have a nextnano software license, the first thing you want to do
is to set up the configuration so you can execute input files easily.

On the other hand, most of the nextnanopy features can be used without
the need of a valid nextnano license, except you want to execute
nextnano input files via Python. We recommend to set up your
configuration at the beginning.

What is the configuration?
--------------------------

The configuration includes the paths to the executables, the license
files, the default output folder, etc.

This configuration is stored as a file called .nextnanopy-config and it
will be located at your home directory (usually C:/Users/Your_User/.nextnanopy-config)

When you import nextnanopy for the first time, it will automatically
generate the configuration file with a few default parameters. If a
configuration file already exists, it won’t modify it.

Once you have set up this configuration file, you do not need to worry
about it anymore, except when you renew your license or update the
nextnano software version.

Let’s import nextnanopy before setting up the configuration
-----------------------------------------------------------

In your Python console (e.g. in Spyder), type in:

.. code:: ipython3

    import nextnanopy as nn

This will generate a configuration file in your home directory.

How can I access the configuration?
-----------------------------------

The configuration can be accessed via:

.. code:: ipython3

    nn.config




.. parsed-literal::

    NNConfig(C:\Users\jun-liang.wang\.nextnanopy-config)
    [nextnano++]
    exe = 
    license = 
    database = 
    outputdirectory = 
    threads = 0
    [nextnano3]
    exe = 
    license = 
    database = 
    threads = 0
    outputdirectory = 
    debuglevel = 0
    cancel = -1
    softkill = -1
    [nextnano.NEGF]
    exe = 
    license = 
    database = 
    outputdirectory = 
    threads = 0
    [nextnano.MSB]
    exe = 
    license = 
    database = 
    outputdirectory = 
    debug = 0



To get an option from a section (nextnano++, nextnano3 or
nextnano.NEGF), you can use the get method:

.. code:: ipython3

    nn.config.get('nextnano++', 'exe')

To get all the options from a section, use:

.. code:: ipython3

    nn.config.get_options('nextnano++')




.. parsed-literal::

    {'exe': '', 'license': '', 'database': '', 'outputdirectory': '', 'threads': 0}



You can also get the location of the configuration file:

.. code:: ipython3

    nn.config.fullpath




.. parsed-literal::

    'C:\\Users\\jun-liang.wang\\.nextnanopy-config'



Config template
---------------

**Our template (nextnanopy/templates/config_nextnano.py in this GitHub
repository) helps you to set up the configuration.**

1. Save the file locally. If you have installed nextnanopy by
   downloading and building the source from GitHub, the template already
   exists in your local copy of the repository. We recommend to make a
   copy of this configuration template and save to another location to
   avoid your setting being overwritten by ‘git pull’.
2. Adjust the paths to your license folder, output folder and
   installation folder.
3. Run the script, then the file .nextnanopy-config gets updated.

Where do I find each path?
--------------------------

If you have activated your license via nextnanomat, the easiest way is
to go to the nextnanomat/Tools/Options. You can
find in the Simulation tab, the executable paths for each nextnano
software (nextnano++, nextnano3, nextnano.NEGF, nextnano.MSB).

Similarly, the database and license paths are in the Material database
and the Licenses tabs.

Side note: How can I set each option?
-------------------------------------

*Our config template does the following automatically. You do not have
to do it by yourself!*

The command

.. code:: python

   nextnanopy.config.set(section, option, value)

sets the option. Please use absolute paths to avoid any possible problem
and be aware of backslash or forwardslash depending on your OS. We
highly recommend to use ‘r’ in front of the path as shown below to avoid
any syntax conflict in python.

Note that after setting the options, you have to save the configuration
by running

.. code:: python

   nextnanopy.config.save()

You can also save the configuration elsewhere with a new name:

.. code:: python

   nextnanopy.config.save(r'C:\new_path\random_name.nextnanopy-config')

In the last case, nextnanopy will always look for the configuration file
in your HOME directory and NOT this one. Saving your own configuration
file can be useful in some cases that we will show later in this
Example.

.. code:: ipython3

    nn.config.set('nextnano++','exe',r'C:\Program Files\nextnano\2020_10_16\nextnano++\bin 64bit\nextnano++_Intel_64bit.exe')
    nn.config.set('nextnano++','license',r'C:\Users\jun-liang.wang\Documents\nextnano\License\License_nnp.lic')
    nn.config.set('nextnano++','database',r'C:\Program Files\nextnano\2020_10_16\nextnano++\Syntax\database_nnp.in')
    nn.config.set('nextnano++','outputdirectory',r'E:\junliang.wang\nextnano\Output')
    
    nn.config.set('nextnano3','exe',r'C:\Program Files\nextnano\2020_10_16\nextnano3\Intel 64bit\nextnano3_Intel_64bit.exe')
    nn.config.set('nextnano3','license',r'C:\Users\jun-liang.wang\Documents\nextnano\License\License_nnp.lic')
    nn.config.set('nextnano3','database',r'C:\Program Files\nextnano\2020_10_16\nextnano3\Syntax\database_nn3.in')
    nn.config.set('nextnano3','outputdirectory',r'E:\junliang.wang\nextnano\Output')
    
    nn.config.set('nextnano.NEGF','exe',r'C:\Program Files\nextnano\nextnanoNEGF_2020_06_22\nextnano.NEGF\nextnano.NEGF.exe')
    nn.config.set('nextnano.NEGF','license',r'C:\Program Files\nextnano\nextnanoNEGF_2020_06_22\License\License_nnQCL.lic')
    nn.config.set('nextnano.NEGF','database',r'C:\Program Files\nextnano\nextnanoNEGF_2020_06_22\nextnano.NEGF\Material_Database.xml')
    nn.config.set('nextnano.NEGF','outputdirectory',r'E:\junliang.wang\nextnano\Output')
    
    nn.config.set('nextnano.MSB','exe',r'C:\Program Files\nextnano\nextnano.MSB_2017_12_20\nextnano\2017_12_20\nextnano.MSB\x86\nextnano.MSB-intel.exe')
    nn.config.set('nextnano.MSB','license',r'C:\Users\jun-liang.wang\Documents\nextnano\License\License_nnMSB.lic')
    nn.config.set('nextnano.MSB','database',r'C:\Program Files\nextnano\nextnano.MSB_2017_12_20\nextnano\2017_12_20\nextnano.MSB\Materials.xml')
    nn.config.set('nextnano.MSB','outputdirectory',r'E:\junliang.wang\nextnano\Output')
    
    nn.config.save() #save permanently

.. code:: ipython3

    nn.config




.. parsed-literal::

    NNConfig(C:\Users\jun-liang.wang\.nextnanopy-config)
    [nextnano++]
    exe = C:\Program Files\nextnano\2020_10_16\nextnano++\bin 64bit\nextnano++_Intel_64bit.exe
    license = C:\Users\jun-liang.wang\Documents\nextnano\License\License_nnp.lic
    database = C:\Program Files\nextnano\2020_10_16\nextnano++\Syntax\database_nnp.in
    outputdirectory = E:\junliang.wang\nextnano\Output
    threads = 0
    [nextnano3]
    exe = C:\Program Files\nextnano\2020_10_16\nextnano3\Intel 64bit\nextnano3_Intel_64bit.exe
    license = C:\Users\jun-liang.wang\Documents\nextnano\License\License_nnp.lic
    database = C:\Program Files\nextnano\2020_10_16\nextnano3\Syntax\database_nn3.in
    threads = 0
    outputdirectory = E:\junliang.wang\nextnano\Output
    debuglevel = 0
    cancel = -1
    softkill = -1
    [nextnano.NEGF]
    exe = C:\Program Files\nextnano\nextnanoNEGF_2020_06_22\nextnano.NEGF\nextnano.NEGF.exe
    license = C:\Program Files\nextnano\nextnanoNEGF_2020_06_22\License\License_nnQCL.lic
    database = C:\Program Files\nextnano\nextnanoNEGF_2020_06_22\nextnano.NEGF\Material_Database.xml
    outputdirectory = E:\junliang.wang\nextnano\Output
    threads = 0
    [nextnano.MSB]
    exe = C:\Program Files\nextnano\nextnano.MSB_2017_12_20\nextnano\2017_12_20\nextnano.MSB\x86\nextnano.MSB-intel.exe
    license = C:\Users\jun-liang.wang\Documents\nextnano\License\License_nnMSB.lic
    database = C:\Program Files\nextnano\nextnano.MSB_2017_12_20\nextnano\2017_12_20\nextnano.MSB\Materials.xml
    outputdirectory = E:\junliang.wang\nextnano\Output
    debug = 0



Execute input file with the default configuration
-------------------------------------------------

By loading an input file with InputFile class (for more information, see
Example1), it will automatically load the configuration file as well.
You can access it via:

.. code:: ipython3

    my_input = nn.InputFile(r'..\..\tests\datafiles\nextnano++\example.in')
    my_input.config




.. parsed-literal::

    NNConfig(C:\Users\jun-liang.wang\.nextnanopy-config)
    [nextnano++]
    exe = C:\Program Files\nextnano\2020_10_16\nextnano++\bin 64bit\nextnano++_Intel_64bit.exe
    license = C:\Users\jun-liang.wang\Documents\nextnano\License\License_nnp.lic
    database = C:\Program Files\nextnano\2020_10_16\nextnano++\Syntax\database_nnp.in
    outputdirectory = E:\junliang.wang\nextnano\Output
    threads = 0
    [nextnano3]
    exe = C:\Program Files\nextnano\2020_10_16\nextnano3\Intel 64bit\nextnano3_Intel_64bit.exe
    license = C:\Users\jun-liang.wang\Documents\nextnano\License\License_nnp.lic
    database = C:\Program Files\nextnano\2020_10_16\nextnano3\Syntax\database_nn3.in
    threads = 0
    outputdirectory = E:\junliang.wang\nextnano\Output
    debuglevel = 0
    cancel = -1
    softkill = -1
    [nextnano.NEGF]
    exe = C:\Program Files\nextnano\nextnanoNEGF_2020_06_22\nextnano.NEGF\nextnano.NEGF.exe
    license = C:\Program Files\nextnano\nextnanoNEGF_2020_06_22\License\License_nnQCL.lic
    database = C:\Program Files\nextnano\nextnanoNEGF_2020_06_22\nextnano.NEGF\Material_Database.xml
    outputdirectory = E:\junliang.wang\nextnano\Output
    threads = 0
    [nextnano.MSB]
    exe = C:\Program Files\nextnano\nextnano.MSB_2017_12_20\nextnano\2017_12_20\nextnano.MSB\x86\nextnano.MSB-intel.exe
    license = C:\Users\jun-liang.wang\Documents\nextnano\License\License_nnMSB.lic
    database = C:\Program Files\nextnano\nextnano.MSB_2017_12_20\nextnano\2017_12_20\nextnano.MSB\Materials.xml
    outputdirectory = E:\junliang.wang\nextnano\Output
    debug = 0



The execute() method runs the input file.

It will automatically detect the nextnano product (nextnano++, nextnano3
or nextnano.NEGF) and will load the corresponding configuration
parameters.

.. code:: ipython3

    my_input.execute()


.. parsed-literal::

    C:\Program Files\nextnano\2020_10_16\nextnano++\bin 64bit
    ================================================================================
    STARTING...
    ================================================================================
    Starting execution as:
    C:\Program Files\nextnano\2020_10_16\nextnano++\bin 64bit\nextnano++_Intel_64bit.exe --license C:\Users\jun-liang.wang\Documents\nextnano\License\License_nnp.lic --database C:\Program Files\nextnano\2020_10_16\nextnano++\Syntax\database_nnp.in --threads 0 --outputdirectory E:\junliang.wang\nextnano\Output\example --noautooutdir ..\..\tests\datafiles\nextnano++\example.in 
    
    nextnano++ (1.6.79 - 2020.092201) Oct 16 2020
    =============================================================================
    COPYRIGHT NOTICE                                                             
    =============================================================================
    Please read the file 'copyright_nextnano++.txt' in your installation folder  
    for further information about the terms of copyright of the nextnano++ code  
    and of third party source codes and libraries used in the nextnano++ code.   
                                                                                 
    In case this file is missing or seems incomplete or corrupted, please contact
    nextnano GmbH, Germany by submitting a support request on www.nextnano.de or 
    by contacting us at https://nextnano.com/goto/support/ in order to receive a new copy.  
                                                                                 
    ANY USE OF THE NEXTNANO++ CODE CONSTITUTES ACCEPTANCE OF THE TERMS OF THE    
    COPYRIGHT NOTICE.                                                            
    =============================================================================
    
    
    =============================================================================
     PROCESSING FILE: ..\..\tests\datafiles\nextnano++\example.in
    =============================================================================
    
    Start time: Fri 2020-11-13, 16:31:06 (+0100)
    
    Simulation process uses 4 of 4 available OpenMP threads (system default).
    
    BLAS and LAPACK libraries use 4 of 4 available threads (system default).
    
    Preparing input validator...
    Reading input file (..\..\tests\datafiles\nextnano++\example.in)...
    
    
    WARNING: Using database specified in command line.
    
    Preparing database validator...
    Reading database file (C:\Program Files\nextnano\2020_10_16\nextnano++\Syntax\database_nnp.in)...
    
    Checking license:
    	 Valid From: 2020-10-8 To: 2021-12-31
    	 Licensed to: E-mail: jun-liang.wang@nextnano.com-2021-12-31-m4t6
    
    ********* SETUP SIMULATION *****************************************************
    
    NOTE: Using output directory specified from command line (nextnanomat), 
    
    NOTE: Setting output directory to: E:\junliang.wang\nextnano\Output\example\
    
    ********* Simulation Grid *********
    
    Creating grid 1 using:
        pos = 0     	spacing = 0.5
        pos = 10     	spacing = 0.5
        pos = 20     	spacing = 0.5
        pos = 30     	spacing = 0.5
        pos = 90     	spacing = 0.1
        pos = 400     	spacing = 5
    
    Grid dimension: 548 * 1 * 1 
    Number of unique grid points: 548
    Range in 1-direction:   0 , ... , 400
    
    
    ********* Rotation Matrix *********
     1.0000000,  0.0000000,  0.0000000
     0.0000000,  1.0000000,  0.0000000
     0.0000000,  0.0000000,  1.0000000
    
    ********* Periodicity *************
      0-direction:  not periodic
    
    Start initializing structure.
    Finished initializing structure.
    Structure initialization time: 0[s]
    
    Setting reference vacuum level to 6.3 eV.
    
    NOTE: Electron minimum density is 1e+10 cm^-3.
    NOTE: Hole minimum density is 1e+10 cm^-3.
    
    NOTE: Electron maximum density is 1e+30 cm^-3.
    NOTE: Hole maximum density is 1e+30 cm^-3.
    
    NOTE: Minimal recombination is DISABLED.
    
    ***** Quantum Subgrid (2DEG) ******     
    Gridsize: 
    Grid dimension: 249 * 1 * 1 
    Number of unique grid points: 249
    Range in 1-direction:   85.0319539 , ... , 248.032375
    
    Calculating quantum density of states ... (2DEG_Gamma)
    
    ********* STRUCTURE OUTPUT *****************************************************
    Writing material indices...
    Writing contact indices...
    Writing donor density...
    Writing fixed charge density...
    
    ********* START CALCULATION ****************************************************
    
    Determine dirichlet points for contacts...
    Intrinsic charge time: 0.001[s]
    
    Discretizing Poisson equation...
    
    
    
    
    ========= STARTING CALCULATION FOR BIAS POINT ==================================
    gate 0 V   backgate -0 V   
    
    Determine electron Fermi level dirichlet values in contacts...
    Determine hole Fermi level dirichlet values in contacts...
    Initialize Fermi levels...
    Fermi level initialization time: 0[s]
    Initialize contacts as charge neutral...
    Determine potential Dirichlet values in Schottky and ohmic contacts...
    Update contact discretization in Poisson equation...
    
    Initialize electrostatic potential...
    Charge Neutrality time: 0.002[s]
    
    Solving nonlinear Poisson equation...
      Newton step: 1	99.70915169962517
      Newton step: 2	7.481685423403909
      Newton step: 3	1.439844607244896
      Newton step: 4	0.2775619229531272
      Newton step: 5	0.05442436986948125
      Newton step: 6	0.01203158025139562
      Newton step: 7	0.003954477372347387
      Newton step: 8	0.002006649927482974
      Newton step: 9	0.0001530601137746094
      Newton step: 10	4.972988069251226e-05
      Newton step: 11	1.477642000260307e-05
      Newton step: 12	2.813911755971973e-06
      Newton step: 13	1.46512611284872e-07
      Newton step: 14	4.335619798520064e-10
      Newton achieved/desired residual: 5.29119376e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51800187
      conduction band minimum: -0.0278041201
    
     Solving 1 exact 1-band Schroedinger equation(s)...
        Tridiagonal real symmetric eigenvalue solver:           1          10
    
    Computing densities...
    
    ******  SOLVING QUANTUM-POISSON EQUATIONS *----------------------------
    *----  Terminates after:   max_iter = 30
                            residual =       1.000000000e+05
    
    QUANTUM-POISSON:  iteration = 1 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	0.003564354209361633
      Newton step: 2	0.0006444409481719048
      Newton step: 3	1.274691077816259e-05
      Newton step: 4	5.110232646041035e-09
      Newton achieved/desired residual: 4.9951182e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51791479
      conduction band minimum: -0.0384996935
    
     Solving 1 approximate subspace 1-band Schroedinger equation(s)...
       Solving dense hermitian eigenvalue problem (standard solver)...
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 1.261862807e+11   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 1.070368955e-02
    
    QUANTUM-POISSON:  iteration = 2 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	0.0008901366968905123
      Newton step: 2	7.916418306169971e-06
      Newton step: 3	2.726403765988829e-08
      Newton achieved/desired residual: 7.74929396e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51788994
      conduction band minimum: -0.0392992043
    
     Solving 1 exact 1-band Schroedinger equation(s)...
        Tridiagonal real symmetric eigenvalue solver:           1          10
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 2.568348129e+10   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 7.995351601e-04
    
    QUANTUM-POISSON:  iteration = 3 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	0.0002802969751370559
      Newton step: 2	1.14809884149047e-06
      Newton achieved/desired residual: 5.68206556e-11 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51789207
      conduction band minimum: -0.0388850626
    
     Solving 1 approximate subspace 1-band Schroedinger equation(s)...
       Solving dense hermitian eigenvalue problem (standard solver)...
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 5.877166311e+09   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 4.146481048e-04
    
    QUANTUM-POISSON:  iteration = 4 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	5.20829174171011e-05
      Newton step: 2	1.100093411432588e-08
      Newton achieved/desired residual: 5.93076426e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51789137
      conduction band minimum: -0.0388561529
    
     Solving 1 exact 1-band Schroedinger equation(s)...
        Tridiagonal real symmetric eigenvalue solver:           1          10
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 1.197851016e+09   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 3.103745753e-05
    
    QUANTUM-POISSON:  iteration = 5 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	1.199739305429823e-05
      Newton step: 2	4.211340614545428e-10
      Newton achieved/desired residual: 5.55815013e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51789157
      conduction band minimum: -0.0388646175
    
     Solving 1 approximate subspace 1-band Schroedinger equation(s)...
       Solving dense hermitian eigenvalue problem (standard solver)...
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 7.522644017e+07   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 8.464641899e-06
    
    QUANTUM-POISSON:  iteration = 6 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	2.159780727963887e-06
      Newton achieved/desired residual: 1.58739637e-11 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51789156
      conduction band minimum: -0.0388660521
    
     Solving 1 exact 1-band Schroedinger equation(s)...
        Tridiagonal real symmetric eigenvalue solver:           1          10
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 4.844156492e+07   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 1.434902214e-06
    
    QUANTUM-POISSON:  iteration = 7 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	4.841511952243991e-07
      Newton achieved/desired residual: 8.67957336e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51789155
      conduction band minimum: -0.0388656864
    
     Solving 1 approximate subspace 1-band Schroedinger equation(s)...
       Solving dense hermitian eigenvalue problem (standard solver)...
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 3.253110567e+06   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 3.656992953e-07
    
    QUANTUM-POISSON:  iteration = 8 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	8.880327249267377e-08
      Newton achieved/desired residual: 5.53995026e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51789155
      conduction band minimum: -0.0388656276
    
     Solving 1 exact 1-band Schroedinger equation(s)...
        Tridiagonal real symmetric eigenvalue solver:           1          10
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 1.978813726e+06   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 5.880264675e-08
    
    QUANTUM-POISSON:  iteration = 9 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	1.954208097513615e-08
      Newton achieved/desired residual: 5.47215604e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51789155
      conduction band minimum: -0.0388656425
    
     Solving 1 approximate subspace 1-band Schroedinger equation(s)...
       Solving dense hermitian eigenvalue problem (standard solver)...
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 1.225399191e+05   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 1.489577128e-08
    
    QUANTUM-POISSON:  iteration = 10 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	3.606404752604288e-09
      Newton achieved/desired residual: 5.15124056e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51789155
      conduction band minimum: -0.0388656449
    
     Solving 1 exact 1-band Schroedinger equation(s)...
        Tridiagonal real symmetric eigenvalue solver:           1          10
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 7.945884163e+04   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 2.426685963e-09
    
    *----  SOLVING QUANTUM-POISSON FINISHED ----------------------------
    
    Solving Quantum Mechanics ---- (quantum regions without density only)
    
    
    Solving Quantum Mechanics ---- (determine k-dispersion only)
    
    
    ********* OUTPUT ***************************************************************
    
    Writing characteristics data(1)...
    Writing characteristics data(2)...
    
    Writing electrostatic potential...
    
    Writing band edges...
    
    Writing Fermi levels...
    
    Writing results from quantum calculations...
    
    Writing carrier densities...
    Writing ionized dopant densities...
    
    ********* FINISHED CALCULATION *************************************************
    
    End time: Fri 2020-11-13, 16:31:06 (+0100)
    Total Poisson Solver Time: 0.011[s]
    Total Quantum Solver Time: 0.008[s]
    Simulator Run Time: 0.302[s]
    
    ================================================================================
    DONE.
    ================================================================================
    



.. parsed-literal::

    <subprocess.Popen at 0x2c128bae190>



Execute with different parameters
---------------------------------

Method 1: use another configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to execute a specific input file with user-defined
configuration file, you can do

.. code:: python

   my_input = nextnanopy.InputFile('example.in', configpath=r'C:\new_path\random_name.nextnanopy-config')
   my_input.config

This feature can be useful if you have different versions of nextnano
installed and you want to use a given version for a set of input files.

Method 2: without any configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can pass one or more specific arguments such as outputdirectoy or
threads:

.. code:: ipython3

    my_input.execute(outputdirectory=r'C:\Users\jun-liang.wang\Downloads', threads=4)


.. parsed-literal::

    C:\Program Files\nextnano\2020_10_16\nextnano++\bin 64bit
    ================================================================================
    STARTING...
    ================================================================================
    Starting execution as:
    C:\Program Files\nextnano\2020_10_16\nextnano++\bin 64bit\nextnano++_Intel_64bit.exe --license C:\Users\jun-liang.wang\Documents\nextnano\License\License_nnp.lic --database C:\Program Files\nextnano\2020_10_16\nextnano++\Syntax\database_nnp.in --threads 4 --outputdirectory C:\Users\jun-liang.wang\Downloads\example --noautooutdir ..\..\tests\datafiles\nextnano++\example.in 
    
    nextnano++ (1.6.79 - 2020.092201) Oct 16 2020
    =============================================================================
    COPYRIGHT NOTICE                                                             
    =============================================================================
    Please read the file 'copyright_nextnano++.txt' in your installation folder  
    for further information about the terms of copyright of the nextnano++ code  
    and of third party source codes and libraries used in the nextnano++ code.   
                                                                                 
    In case this file is missing or seems incomplete or corrupted, please contact
    nextnano GmbH, Germany by submitting a support request on www.nextnano.de or 
    by contacting us at https://nextnano.com/goto/support/ in order to receive a new copy.  
                                                                                 
    ANY USE OF THE NEXTNANO++ CODE CONSTITUTES ACCEPTANCE OF THE TERMS OF THE    
    COPYRIGHT NOTICE.                                                            
    =============================================================================
    
    
    =============================================================================
     PROCESSING FILE: ..\..\tests\datafiles\nextnano++\example.in
    =============================================================================
    
    Start time: Fri 2020-11-13, 16:31:09 (+0100)
    
    Simulation process uses 4 of 4 available OpenMP threads (specified via command line).
    
    BLAS and LAPACK libraries use 4 of 4 available threads (specified via command line).
    
    Preparing input validator...
    Reading input file (..\..\tests\datafiles\nextnano++\example.in)...
    
    
    WARNING: Using database specified in command line.
    
    Preparing database validator...
    Reading database file (C:\Program Files\nextnano\2020_10_16\nextnano++\Syntax\database_nnp.in)...
    
    Checking license:
    	 Valid From: 2020-10-8 To: 2021-12-31
    	 Licensed to: E-mail: jun-liang.wang@nextnano.com-2021-12-31-m4t6
    
    ********* SETUP SIMULATION *****************************************************
    
    NOTE: Using output directory specified from command line (nextnanomat), 
    
    NOTE: Setting output directory to: C:\Users\jun-liang.wang\Downloads\example\
    
    ********* Simulation Grid *********
    
    Creating grid 1 using:
        pos = 0     	spacing = 0.5
        pos = 10     	spacing = 0.5
        pos = 20     	spacing = 0.5
        pos = 30     	spacing = 0.5
        pos = 90     	spacing = 0.1
        pos = 400     	spacing = 5
    
    Grid dimension: 548 * 1 * 1 
    Number of unique grid points: 548
    Range in 1-direction:   0 , ... , 400
    
    
    ********* Rotation Matrix *********
     1.0000000,  0.0000000,  0.0000000
     0.0000000,  1.0000000,  0.0000000
     0.0000000,  0.0000000,  1.0000000
    
    ********* Periodicity *************
      0-direction:  not periodic
    
    Start initializing structure.
    Finished initializing structure.
    Structure initialization time: 0[s]
    
    Setting reference vacuum level to 6.3 eV.
    
    NOTE: Electron minimum density is 1e+10 cm^-3.
    NOTE: Hole minimum density is 1e+10 cm^-3.
    
    NOTE: Electron maximum density is 1e+30 cm^-3.
    NOTE: Hole maximum density is 1e+30 cm^-3.
    
    NOTE: Minimal recombination is DISABLED.
    
    ***** Quantum Subgrid (2DEG) ******     
    Gridsize: 
    Grid dimension: 249 * 1 * 1 
    Number of unique grid points: 249
    Range in 1-direction:   85.0319539 , ... , 248.032375
    
    Calculating quantum density of states ... (2DEG_Gamma)
    
    ********* STRUCTURE OUTPUT *****************************************************
    Writing material indices...
    Writing contact indices...
    Writing donor density...
    Writing fixed charge density...
    
    ********* START CALCULATION ****************************************************
    
    Determine dirichlet points for contacts...
    Intrinsic charge time: 0.001[s]
    
    Discretizing Poisson equation...
    
    
    
    
    ========= STARTING CALCULATION FOR BIAS POINT ==================================
    gate 0 V   backgate -0 V   
    
    Determine electron Fermi level dirichlet values in contacts...
    Determine hole Fermi level dirichlet values in contacts...
    Initialize Fermi levels...
    Fermi level initialization time: 0[s]
    Initialize contacts as charge neutral...
    Determine potential Dirichlet values in Schottky and ohmic contacts...
    Update contact discretization in Poisson equation...
    
    Initialize electrostatic potential...
    Charge Neutrality time: 0.002[s]
    
    Solving nonlinear Poisson equation...
      Newton step: 1	99.70915169962517
      Newton step: 2	7.481685423403909
      Newton step: 3	1.439844607244896
      Newton step: 4	0.2775619229531272
      Newton step: 5	0.05442436986948125
      Newton step: 6	0.01203158025139562
      Newton step: 7	0.003954477372347387
      Newton step: 8	0.002006649927482974
      Newton step: 9	0.0001530601137746094
      Newton step: 10	4.972988069251226e-05
      Newton step: 11	1.477642000260307e-05
      Newton step: 12	2.813911755971973e-06
      Newton step: 13	1.46512611284872e-07
      Newton step: 14	4.335619798520064e-10
      Newton achieved/desired residual: 5.29119376e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51800187
      conduction band minimum: -0.0278041201
    
     Solving 1 exact 1-band Schroedinger equation(s)...
        Tridiagonal real symmetric eigenvalue solver:           1          10
    
    Computing densities...
    
    ******  SOLVING QUANTUM-POISSON EQUATIONS *----------------------------
    *----  Terminates after:   max_iter = 30
                            residual =       1.000000000e+05
    
    QUANTUM-POISSON:  iteration = 1 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	0.003564354209361633
      Newton step: 2	0.0006444409481719048
      Newton step: 3	1.274691077816259e-05
      Newton step: 4	5.110232646041035e-09
      Newton achieved/desired residual: 4.9951182e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51791479
      conduction band minimum: -0.0384996935
    
     Solving 1 approximate subspace 1-band Schroedinger equation(s)...
       Solving dense hermitian eigenvalue problem (standard solver)...
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 1.261862807e+11   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 1.070368955e-02
    
    QUANTUM-POISSON:  iteration = 2 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	0.0008901366968905123
      Newton step: 2	7.916418306169971e-06
      Newton step: 3	2.726403765988829e-08
      Newton achieved/desired residual: 7.74929396e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51788994
      conduction band minimum: -0.0392992043
    
     Solving 1 exact 1-band Schroedinger equation(s)...
        Tridiagonal real symmetric eigenvalue solver:           1          10
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 2.568348129e+10   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 7.995351601e-04
    
    QUANTUM-POISSON:  iteration = 3 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	0.0002802969751370559
      Newton step: 2	1.14809884149047e-06
      Newton achieved/desired residual: 5.68206556e-11 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51789207
      conduction band minimum: -0.0388850626
    
     Solving 1 approximate subspace 1-band Schroedinger equation(s)...
       Solving dense hermitian eigenvalue problem (standard solver)...
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 5.877166311e+09   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 4.146481048e-04
    
    QUANTUM-POISSON:  iteration = 4 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	5.20829174171011e-05
      Newton step: 2	1.100093411432588e-08
      Newton achieved/desired residual: 5.93076426e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51789137
      conduction band minimum: -0.0388561529
    
     Solving 1 exact 1-band Schroedinger equation(s)...
        Tridiagonal real symmetric eigenvalue solver:           1          10
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 1.197851016e+09   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 3.103745753e-05
    
    QUANTUM-POISSON:  iteration = 5 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	1.199739305429823e-05
      Newton step: 2	4.211340614545428e-10
      Newton achieved/desired residual: 5.55815013e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51789157
      conduction band minimum: -0.0388646175
    
     Solving 1 approximate subspace 1-band Schroedinger equation(s)...
       Solving dense hermitian eigenvalue problem (standard solver)...
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 7.522644017e+07   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 8.464641899e-06
    
    QUANTUM-POISSON:  iteration = 6 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	2.159780727963887e-06
      Newton achieved/desired residual: 1.58739637e-11 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51789156
      conduction band minimum: -0.0388660521
    
     Solving 1 exact 1-band Schroedinger equation(s)...
        Tridiagonal real symmetric eigenvalue solver:           1          10
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 4.844156492e+07   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 1.434902214e-06
    
    QUANTUM-POISSON:  iteration = 7 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	4.841511952243991e-07
      Newton achieved/desired residual: 8.67957336e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51789155
      conduction band minimum: -0.0388656864
    
     Solving 1 approximate subspace 1-band Schroedinger equation(s)...
       Solving dense hermitian eigenvalue problem (standard solver)...
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 3.253110567e+06   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 3.656992953e-07
    
    QUANTUM-POISSON:  iteration = 8 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	8.880327249267377e-08
      Newton achieved/desired residual: 5.53995026e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51789155
      conduction band minimum: -0.0388656276
    
     Solving 1 exact 1-band Schroedinger equation(s)...
        Tridiagonal real symmetric eigenvalue solver:           1          10
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 1.978813726e+06   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 5.880264675e-08
    
    QUANTUM-POISSON:  iteration = 9 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	1.954208097513615e-08
      Newton achieved/desired residual: 5.47215604e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51789155
      conduction band minimum: -0.0388656425
    
     Solving 1 approximate subspace 1-band Schroedinger equation(s)...
       Solving dense hermitian eigenvalue problem (standard solver)...
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 1.225399191e+05   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 1.489577128e-08
    
    QUANTUM-POISSON:  iteration = 10 of 30 ----------------------------
    
    Solving nonlinear Poisson equation...
      Newton step: 1	3.606404752604288e-09
      Newton achieved/desired residual: 5.15124056e-13 1.80951265e-10
    
    Solving Quantum Mechanics ---- (and calculate density)
    
      valence band maximum: -1.51789155
      conduction band minimum: -0.0388656449
    
     Solving 1 exact 1-band Schroedinger equation(s)...
        Tridiagonal real symmetric eigenvalue solver:           1          10
    
    Computing densities...
    
    QUANTUM-POISSON:   Residual_EDensity = 7.945884163e+04   Residual_HDensity = 0.000000000e+00
    QUANTUM-POISSON:   Residual_potential = 2.426685963e-09
    
    *----  SOLVING QUANTUM-POISSON FINISHED ----------------------------
    
    Solving Quantum Mechanics ---- (quantum regions without density only)
    
    
    Solving Quantum Mechanics ---- (determine k-dispersion only)
    
    
    ********* OUTPUT ***************************************************************
    
    Writing characteristics data(1)...
    Writing characteristics data(2)...
    
    Writing electrostatic potential...
    
    Writing band edges...
    
    Writing Fermi levels...
    
    Writing results from quantum calculations...
    
    Writing carrier densities...
    Writing ionized dopant densities...
    
    ********* FINISHED CALCULATION *************************************************
    
    End time: Fri 2020-11-13, 16:31:10 (+0100)
    Total Poisson Solver Time: 0.012[s]
    Total Quantum Solver Time: 0.006[s]
    Simulator Run Time: 0.288[s]
    
    ================================================================================
    DONE.
    ================================================================================
    



.. parsed-literal::

    <subprocess.Popen at 0x2c1287240d0>



Reset the configuration to default
----------------------------------

You can reset the configuration to the default one.

Note that you need to save the file after the modification.

.. code:: ipython3

    nn.config.to_default() # not saved automatically
    nn.config.save() # save the default values
    print(nn.config)


.. parsed-literal::

    NNConfig(C:\Users\jun-liang.wang\.nextnanopy-config)
    [nextnano++]
    exe = 
    license = 
    database = 
    outputdirectory = 
    threads = 0
    [nextnano3]
    exe = 
    license = 
    database = 
    threads = 0
    outputdirectory = 
    debuglevel = 0
    cancel = -1
    softkill = -1
    [nextnano.NEGF]
    exe = 
    license = 
    database = 
    outputdirectory = 
    threads = 0
    [nextnano.MSB]
    exe = 
    license = 
    database = 
    outputdirectory = 
    debug = 0
    

Please contact python@nextnano.com for any issues with this document.
