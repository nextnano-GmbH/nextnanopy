#!/usr/bin/env python
# coding: utf-8

# # Example 1 - Execute an input file
# 
# ## About this example: load and execute an input file
# 
# To work with an input file, instantiate an InputFile class object:

# In[1]:


import nextnanopy as nn

my_input = nn.InputFile(r'..\..\tests\datafiles\nextnano++\example.in')
print(my_input)


# This object contains all the relevant information of the input file such as the raw text, the variables and the configuration for the execution (see Example 0).
# 
# When you create ```my_input```, the class will first check automatically the type of the input file (nextnano++, nextnano3, nextnano.NEGF or nexntano.MSB). It will then get the raw text and extract all variables defined in the file:
# 
# ```
# $my_var = 3    # in nextnano++
# %my_var = 3    ! in nextnano3
# $my_var = 3    # in nextnano.NEGF
# 
# ```

# ## What information does it contain?
# 
# ```my_input``` has the following relevant attributes:
# 
# - fullpath (str): path to the input file including the name
# - text (str): return raw text
# - variables (list): list of InputVariable objects
# - config: nextnano configuration (see Example 0)
# 

# In[2]:


print(my_input.fullpath)


# In[3]:


my_input.preview()


# ## Input variables
# 
# The input variables are stored in ```my_input.variables``` as a list of ```InputVariable``` objects.
# 
# These objects have the following attributes:
# 
# - name (str)
# - value (undefined)
# - unit (str, optional)
# - comment (str, optional)
# - metadata (dict, optional)
# - text (str): raw text in the input file for a given variable

# In[4]:


print(f"List of variables: {my_input.variables}")


# ### Get a variables
# 
# There are several methods to do so:
# 
# ```python
# my_input.get_variable(name) # method 1 (recommended)
# my_input.variables[name] # method 2 (recommended)
# my_input[name] # method 3
# my_input.variables[index] # method 4
# ```

# ### Let's have a quick look of the variables in this file

# In[5]:


for var in my_input.variables:
    print(var.text)


# ### Variable line number
# 
# You can also check the line number in the input file where the variable is defined:

# In[6]:


my_input.variables['BIAS'].metadata


# ### Modify the variable
# 
# To modify the value of a given variable, you can do:
# 
# ```python
# my_input.set_variable('BIAS', value=3)
# ```
# 
# You can also change the comment:
# ```python
# my_input.set_variable('BIAS', comment='this is a new comment')
# ```
# 
# You can change both at the same time:
# ```python
# my_input.set_variable('BIAS', value=3, comment='this is a new comment')
# ```

# In[7]:


print(f"Old variable: {my_input.get_variable('BIAS').text}")
my_input.set_variable('BIAS', value=3, comment='this is a new comment')
print(f"New variable: {my_input.get_variable('BIAS').text}")


# ## Save the current file
# 
# ```my_input``` has a method ```save``` which saves the current input file.
# 
# ```python
# my_input.save()
# ```
# 
# By default, it does not overwrite the current file and save it with an unused name (like example_1.in).
# 
# You can overwrite the current file with the option:
# 
# ```python
# my_input.save(overwrite=True)
# ```
# 
# You can save it in another location with a new name:
# 
# ```python
# my_input.save('new_path\new_input.in')
# ```
# 
# Automatically, ```my_input.fullpath``` is updated if the saving was successful.
# 
# By default, if the new location does not exist, it will create the folder automatically. To turn this option off, use:
# 
# ```python
# my_input.save('new_path\new_input.in', automkdir=False)
# ```

# You can get help for these options from Command prompt:

# In[8]:


help(my_input.save)


# ## Execute the input file
# 
# To execute the input file, run:
# 
# ```python
# my_input.execute()
# ```
# 
# Make sure you have saved the file before execution, otherwise your modification to the input file does not take effect.
# 
# The ```execute``` method without any arguments will use the configuration stored in ```my_input.config```. As explained in Example 0, it will automatically detect the nextnano product (nextnano++, nextnano3, nextnano.NEGF or nextnano.MSB) and will load the corresponding configuration parameters prior to the execution.
# 
# To suppress the simulation log in the Python console, use
# ```python
# my_input.execute(show_log=False)
# ```
# (Default is `True`). Note that the log file is always saved in the output folder regardless of this option.
# 
# From 2022-03-22, a new option 
# ```python
# my_input.execute(convergenceCheck=True)
# ```
# is available (default is `False`). If `True`, nextnanopy scans the log file of the simulation performed and check whether the solution has converged. If it did not converge, nextnanopy warns you and ask if you want to proceed with postprocessing. Note that non-converged solutions are not reliable and further calculation and/or visualization from them do not make much sense.

# You can get help for these options from Command prompt:

# In[9]:


help(my_input.execute)


# ## Get information after executing the file
# 
# The output folder of the simulation is stored at:
# ```python
# my_input.folder_output
# ```
# 
# You can access all the relevant information from the execution, e.g., the log file location, the command line arguments, via:
# ```python
# my_input.execute_info
# ```
# 

# In[11]:


my_input.folder_output


# ## Sweep an input variable
# 
# __Automatic sweep is now supported. Please refer to Example 4.__
# 
# You can sweep its value and execute the input file in a simple loop. Manual sweep might look like:
# 
# ```python
# for value in [0, 1, 2]:
#     my_input.set_variable('BIAS', value=value)
#     my_input.save() # remember that by default, overwrite is False.
#     my_input.execute() 
# ```

# ## Change filename and input folder
# 
# If you want to change the current filename or the current input folder, you can do the following:
# ```python
# my_input.filename = 'new_file.in'
# my_input.filename_only = 'new_file' # it will use the original file extension
# my_input.folder_input = 'new_folder'
# ```

# 
# 
# Please contact python@nextnano.com for any issues with this document.
