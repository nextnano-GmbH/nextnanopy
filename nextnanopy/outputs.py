import json
import os
from itertools import islice
import numpy as np
import struct
import warnings
import re

from nextnanopy.utils.datasets import Variable, Coord
from nextnanopy.utils.mycollections import DictList
from nextnanopy.utils.formatting import best_str_to_name_unit
from nextnanopy.utils.misc import get_filename, message_decorator, start_with_choice
from nextnanopy import defaults

import pyvista as pv


_msgs = defaults.messages["load_output"]
load_message = lambda method: message_decorator(
    method, init_msg=_msgs[0], end_msg=_msgs[1]
)


def displayname(data):
    """
    Parameters
    ----------
    data: DataFolder or filepath
    Returns
    -------
    str
    formatting filenames and folder names in datafolder to display DataFolder in tree structure
    """
    if isinstance(data, DataFolder):
        return os.path.basename(data.fullpath) + r"/"
    else:
        return os.path.basename(data)


class DataFolder(object):
    """
    This class stores information about output directory.
    The stored data contains files (.files) and folders (.folders)
    Navigation between folders could be done in 3 ways:
        1. DataFolder.folders['folder_name']
        2. DataFolder.go_to('subfolder1', 'subfolder2', 'subfolder3')
        3. DataFolder.subfolder1.subfolder2.subfolder3
    For each method see details below.

    The initialization of the class will execute load and create_navigation methods.


    Parameters:
    ----------------
    fullpath: str
        path to a file



    Attributes:
    ----------------
    fullpath: str
    path to a file

    folders: DictList
        subfolders of the DataFolder,
        keys: str
            names of subfolders
        values: DataFolder
            DataFolder objects of subfolders

    files: list
        paths to files in folder


    Methods:
    --------------
    load():
        load a DataFolder

    create_navigation:
        creates attributes for navigation like DataFolder.subfolder1.subfolder2.subfolder3
        if name of subfolder corresponds to existed attribute of DataFolder class, attribute will not be created!
        if name of subfolder constis spaces, dots or specials charecters, attribute will be created, but navigation
        to whis subfolder will not work  - attribute error.

    find(template, deep = False):
        searches for a files which names contain template.
        template shoud be string.
        if deep = True, searches in subfolders as well.

        return: list of files

    go_to(*args):
        goes to the location
        DataFolder_path\\arg1\\arg2\\arg3...

        if location is a file:
            return filepath
        if location is a folder:
            return DataFolder(location)

    filenames()
        return filenames of files in folder
    """

    def __init__(self, fullpath):
        if not os.path.isdir(fullpath):
            raise ValueError(f"{fullpath} is not a directory")
        self.fullpath = fullpath
        self.files = []
        self.folders = DictList()
        self.load()
        self.create_navigation()

    def load(self):
        list_of_nodes = sorted(os.listdir(self.fullpath))
        for node in list_of_nodes:
            node_path = os.path.join(self.fullpath, node)
            if os.path.isdir(node_path):
                new_folder = DataFolder(node_path)
                self.folders[node] = new_folder
            else:
                self.files.append(node_path)

    def create_navigation(self):
        check_list = dir(self)
        for key, folder in self.folders.items():
            if key in check_list:
                warnings.warn(
                    f"foldername '{key}' is not availabel for attribute navigation."
                    " Please, use DataFolder.go_to()"
                )
            else:
                setattr(self, key, folder)

    def find(self, template, deep=False):
        list_of_files = [
            file for file in self.files if template in os.path.basename(file)
        ]
        if not deep:
            return list_of_files
        if not self.folders:
            return list_of_files
        else:
            for folder in self.folders:
                list_of_files += folder.find(template=template, deep=deep)
            return list_of_files

    def find_multiple(self, templates, deep=False):
        list_of_files = []

        for file in self.files:
            if all(keyword in os.path.basename(file) for keyword in templates):
                list_of_files.append(file)

        if deep and self.folders:
            for folder in self.folders:
                list_of_files += folder.find_multiple(templates=templates, deep=deep)

        return list_of_files

    def file(self, filename):
        matched_files = self.find(template=filename, deep=False)
        if not matched_files:
            raise ValueError(
                f"No file with filename {filename} in directory {self.fullpath}"
            )
        elif len(matched_files) == 1:
            return matched_files[0]
        else:
            warnings.warn(
                f"More than one file match '{filename}' name match in directory {self.fullpath}. First match returned."
            )
            return matched_files[0]

    def go_to(self, *args):
        path = os.path.join(self.fullpath, *args)
        if os.path.isdir(path):
            data = DataFolder(path)
        elif os.path.isfile(path):
            data = path
        else:
            raise ValueError(f"No such file or directory {path}")
        return data

    def filenames(self):
        return [os.path.basename(file) for file in self.files]

    def __repr__(self):
        out = list()
        out.append(f"{self.__class__.__name__}")
        out.append(f"fullpath: {self.fullpath}")
        out.append(f"Folders: {len(self.folders)}")
        for key in self.folders.keys():
            out.append(key)
        out.append("Files:")
        out.append(str(self.filenames()))
        out = "\n".join(out)
        return out

    def make_tree(self, level=0, result=None, with_files=True, deep=True):
        if not result:
            result = []
        result.insert(level, level * "    " + displayname(self))
        if with_files:
            for file in reversed(self.files):
                result.insert(level + 1, (level + 1) * "    " + displayname(file))
        level = level + 1
        for i in reversed(range(len(self.folders))):
            folder = self.folders[i]
            if deep:
                result = folder.make_tree(level, result=result, with_files=with_files)
            else:
                result.insert(level, level * "    " + displayname(folder))
        return result

    def show_tree(self, with_files=True, deep=True):
        tree_list = self.make_tree(with_files=with_files, deep=deep)
        print("\n".join(tree_list))

    @property
    def name(self):
        # folder_path = os.path.dirname(self.fullpath)
        folder_name = os.path.basename(self.fullpath)
        return folder_name

    def read_sweep_infodict(self):
        infodict_path = os.path.join(self.fullpath, "sweep_infodict.json")

        if not os.path.isfile(infodict_path):
            raise FileNotFoundError(
                "Sweep infodict file not found. Make sure that the chosen folder is a sweep output folder."
            )

        with open(infodict_path, "r") as file:
            infodict = json.load(file)

        return infodict


class Output(object):

    def __init__(self, fullpath, **loader_kwargs):
        self.fullpath = fullpath
        self.metadata = {}
        self.coords = DictList()
        self.variables = DictList()

    @property
    def folder(self):
        return os.path.split(self.fullpath)[0]

    @property
    def filename_only(self):
        return get_filename(self.fullpath, ext=False)

    @property
    def filename(self):
        return get_filename(self.fullpath, ext=True)

    @property
    def extension(self):
        return os.path.splitext(self.fullpath)[-1]

    @property
    def data(self):
        dl = DictList()
        dl.update(self.coords)
        dl.update(self.variables)
        return dl

    @load_message
    def load(self):
        pass

    def get_coord(self, key):
        return self.coords[key]

    def get_variable(self, key):
        return self.variables[key]

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, item, value):
        if item in self.coords.keys():
            self.coords[item] = value
        if item in self.variables.keys():
            self.variables[item] = value

    def __delitem__(self, item):
        if item in self.coords.keys():
            del self.coords[item]
        if item in self.variables.keys():
            del self.variables[item]

    def __repr__(self):
        out = []
        out.append(f"{self.__class__.__name__}")
        out.append(f"fullpath: {self.fullpath}")
        out.append(f"Coordinates: {len(self.coords)} datasets")
        for key, coord in self.coords.items():
            out.append(f"\t{str(coord)}")
        out.append(f"Variables: {len(self.variables)} datasets")
        for key, var in self.variables.items():
            out.append(f"\t{str(var)}")
        out = "\n".join(out)
        return out

    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self):
        try:
            result = self.data.__getitem__(self._iter_index)
        except (IndexError, KeyError):
            raise StopIteration
        self._iter_index += 1
        return result


class DataFileTemplate(Output):
    """
    This class stores the data from any kind of nextnano data files with the
    same structure.
    The stored data contains coordinates (.coords) and dependent variables (.variables).
    Each coordinate or variable would contain attributes like name, unit and value.
    For more information, see their specific documentation.

    The initialization of the class will execute the load method.

    ...

    Parameters
    ----------
    fullpath : str
        path to the file.


    Attributes
    ----------
    fullpath : str
        path to the file (default: None)
    coords : DictList
        Coord objects (default: DictList())
    variables : DictList
        Variable objects (default: DictList())
    data : DictList
        coords and variables together
    metadata : dict
        extra information
    filename : str
        name with the file extension
    filename_only :
        name without the file extension
    extension : str
        file extension
    folder : str
        folder of the fullpath
    product : str
        flag about nextnano product to help to find the best loading routine


    Methods
    -------
    load(fullpath)
        load a data file

    get_coord(name)
        equivalent to self.coords[name]

    get_variable(name)
        equivalent to self.variables[name]

    """

    def __init__(self, fullpath, product=None, **loader_kwargs):
        super().__init__(fullpath)
        self.product = product
        self.load(**loader_kwargs)

    @load_message
    def load(self, **loader_kwargs):
        """
        Find the loader and update the stored information with the loaded data
        """
        loader = self.get_loader()
        df = loader(self.fullpath, **loader_kwargs)
        self.update_with_datafile(df)
        del df

    def update_with_datafile(self, datafile):
        """
        Copy .metadata, .coords and .variables of the specified datafile
        Copy other attributes like .vtk if there is any.

        Parameters
        ----------
        datafile : nextnano.outputs.DataFileTemplate object
        """

        self.metadata = datafile.metadata
        self.coords = datafile.coords
        self.variables = datafile.variables
        if hasattr(datafile, "vtk"):
            self.vtk = datafile.vtk

    def get_loader(self):
        pass

    def export(self, filename, format):
        raise NotImplementedError("Exporters are not implemented yet")


class DataFile(DataFileTemplate):
    def __init__(self, fullpath, product=None, **loader_kwargs):
        super().__init__(
            fullpath, product=product, **loader_kwargs
        )  # **loader_kwargs) #, FirstVarIsCoordFlag = False

    def get_loader(self):
        if self.product:
            loader = defaults.get_DataFile(self.product)
        else:
            print(
                "[Warning] nextnano product is not specified: nextnano++, nextnano3, nextnano.NEGF or nextnano.MSB"
            )
            print(
                "[Warning] Autosearching for the best loading method. Note: The result may not be correct"
            )
            loader = self.find_loader()
        return loader

    def find_loader(self):
        from nextnanopy.nnp.outputs import DataFile as DataFile_nnp
        from nextnanopy.nn3.outputs import DataFile as DataFile_nn3
        from nextnanopy.negf.outputs import DataFile as DataFile_negf
        from nextnanopy.msb.outputs import DataFile as DataFile_msb

        Dats = [DataFile_nn3, DataFile_nnp, DataFile_negf, DataFile_msb]
        for Dati in Dats:
            try:
                df = Dati(self.fullpath)
                if "" in df.variables.keys():
                    continue
                else:
                    break
            except:
                pass
        loader = Dati
        return loader

    def plot(self, legend=False, y_axis_name="", subplots=False):
        import matplotlib.pyplot as plt

        if len(self.coords) == 0:
            fig, ax = plt.subplots()
            if len(self.variables) > 1:
                plot_coord = self.variables[0]
                # plot_var = self.variables[1:]
                # for var in plot_var:
                for i in range(1, len(self.variables) - 1):
                    var = self.variables[i]
                    ax.plot(plot_coord.value, var.value, label=var.name)
                ax.set_xlabel(f"{plot_coord.name}[{plot_coord.unit}]")
            else:
                for var in self.variables:
                    ax.plot(var.value, label=var.name)
            ax.set_ylabel(f"{y_axis_name}[{var.unit}]")
        elif len(self.coords) == 1:
            fig, ax = plt.subplots()
            x_coord = self.coords[0]
            x_label_name = x_coord.name
            x_label_unit = x_coord.unit
            x_value = x_coord.value
            ax.set_xlabel(f"{x_label_name}[{x_label_unit}]")
            for var in self.variables:
                ax.plot(x_value, var.value, label=var.name)
            ax.set_ylabel(f"{y_axis_name}[{var.unit}]")
            if legend:
                plt.legend()
        elif len(self.coords) == 2:
            x = self.coords[0]
            y = self.coords[1]
            number_of_var = len(self.variables)
            if number_of_var < 2:
                fig, ax = plt.subplots()
                ax.set_xlabel(f"{x.name}[{x.unit}]")
                ax.set_ylabel(f"{y.name}[{y.unit}]")
                var = self.variables[0]
                im = ax.pcolormesh(
                    x.value,
                    y.value,
                    var.value,
                    shading="auto",
                    label=f"{var.name}[{var.unit}]",
                )
                ax.set_title(f"{var.name}[{var.unit}]")
                fig.colorbar(im, ax=ax)
            else:
                if subplots:
                    fig, ax = plt.subplots(len(self.variables))
                    for i, var in enumerate(self.variables):
                        im = ax[i].pcolormesh(
                            x.value,
                            y.value,
                            var.value,
                            shading="auto",
                            label=f"{var.name}[{var.unit}]",
                        )
                        ax[i].set_xlabel(f"{x.name}[{x.unit}]")
                        ax[i].set_ylabel(f"{y.name}[{y.unit}]")
                        ax[i].set_title(f"{var.name}[{var.unit}]")
                        fig.colorbar(im, ax=ax[i])
                else:
                    for i, var in enumerate(self.variables):
                        fig, ax = plt.subplots()
                        im = ax.pcolormesh(
                            x.value,
                            y.value,
                            var.value,
                            shading="auto",
                            label=f"{var.name}[{var.unit}]",
                        )
                        ax.set_xlabel(f"{x.name}[{x.unit}]")
                        ax.set_ylabel(f"{y.name}[{y.unit}]")
                        ax.set_title(f"{var.name}[{var.unit}]")
                        fig.colorbar(im, ax=ax)
        else:
            raise NotImplementedError(
                "Preview plot feature is implemented only for datafiles with 2 or less coordinates"
            )
        return fig, ax

    def save(self, filepath, format="dat"):
        """
        Save the data from the DataFile instance to a specified file in various formats.

        Parameters:
            filepath (str): The file path where the data will be saved.
            format (str, optional): The format in which the data should be saved. Default is 'dat'.
                Supported formats:
                - 'dat' (for 1D files): Data is saved in a plain text format (.dat) with whitespace-separated values.
                - 'VTKAscii' (for 2D/3D files): Data is saved in VTK ASCII format (.vtk) suitable for visualization tools.
                - 'AvsAscii_one_file' (for 2D/3D files): Data is saved in AVS/Express ASCII format (.fld) for AVS/Express software.

        Raises:
            NotImplementedError: If the provided 'format' is not supported for saving.

        Notes:
            - For the 'dat' format, the DataFile instance should be one-dimensional (ndim=1).
            - The 'VTKAscii' format requires 'nextnanopy.utils.formatting' module for creating the VTK header.
            - The 'AvsAscii_one_file' format requires the 'write_avsascii_one_file' function.

        Example:
            # Assuming `data_file` is an instance of the `DataFile` class
            data_file.save('data_file.dat', format='dat')  # Save data in .dat format
            data_file.save('data_file.vtk', format='VTKAscii')  # Save data in VTK ASCII format
            data_file.save('data_file.fld', format='AvsAscii_one_file')  # Save data in AVS/Express ASCII format
        """
        # TODO  and AvsBinary (.fld)
        accepted_format = ["dat", "VTKAscii", "AvsAscii_one_file"]
        if format not in accepted_format:
            raise NotImplementedError(f"{format} format is not supported for saving")
        if format == "dat":
            ndim = len(self.coords)
            if ndim > 1:
                raise ValueError(
                    f"The DataFile is {ndim}-dimensional. More than 1 dimension is not supported for .dat extension"
                )
            with open(filepath, "w") as f:
                # Write headers
                for header in self.metadata["headers"]:
                    f.write(header)

                # Write data
                combined_data = [coord.value for coord in self.coords] + [
                    variable.value for variable in self.variables
                ]

                data = np.column_stack(combined_data).transpose()
                np.savetxt(f, data.T)
        elif format == "VTKAscii":
            from nextnanopy.utils.formatting import create_vtk_header

            header = create_vtk_header(
                len(self.coords), [len(coord.value) for coord in self.coords]
            )
            with open(filepath, "w") as file:
                # Write the header
                file.write(header)

                # Write the coordinates
                file.write("<Coordinates>")
                for coord in self.coords:
                    file.write(
                        f'<DataArray type="Float64" Name="{coord.name.upper()}_COORDINATES" NumberOfComponents="1" format="ascii">\n'
                    )
                    np.savetxt(file, coord.value, fmt="%.6f", delimiter="\t")
                    file.write("</DataArray>\n")
                if len(self.coords) == 2:  # add Z coordinate
                    file.write(
                        """<DataArray type="Float64" Name ="Z_COORDINATES" NumberOfComponents ="1" format="ascii">
                                        0
                                    </DataArray>\n"""
                    )
                file.write("</Coordinates>\n")

                # Write the data
                file.write("<PointData>\n")
                for variable in self.variables:
                    if variable.unit:
                        name = variable.name + f"[{variable.unit}]"
                    else:
                        name = variable.name
                    file.write(
                        f'<DataArray type="Float64" Name="{name}" NumberOfComponents="1" format="ascii">\n'
                    )
                    flatten_array = variable.value.flatten("F")

                    np.savetxt(file, flatten_array, fmt="%.6f", delimiter="\t")
                    file.write("</DataArray>\n")

                # Write the footer
                footer = """</PointData>
                            </Piece>
                            </RectilinearGrid>
                            </VTKFile>"""
                file.write(footer)
        elif format == "AvsAscii_one_file":
            write_avsascii_one_file(
                coordinates=self.coords, variables=self.variables, filename=filepath
            )
        self.filepath = filepath


class AvsAscii(Output):
    def __init__(self, fullpath, **loader_kwargs):
        super().__init__(fullpath)
        self.load()

    @property
    def fld(self):
        filename = self.filename_only + ".fld"
        return os.path.join(self.folder, filename)

    def load(self):
        self.load_raw_metadata()
        self.load_metadata()
        self.load_variables()
        self.load_coords()

    def load_raw_metadata(self):
        possible_keys = [
            "ndim",
            "dim",
            "nspace",
            "veclen",
            "data",
            "field",
            "label",
            "variable",
            "coord",
        ]
        info = []
        try:
            with open(self.fld, "r") as f:
                for line in f:
                    line = line.replace("\n", "")
                    line = line.strip()
                    try:
                        float(line)
                        break
                    except:
                        if line == "":
                            continue
                        # if line[0] != '#':
                        #     info.append(line)
                        if start_with_choice(line, *possible_keys):
                            info.append(line)
        except UnicodeDecodeError:
            with open(self.fld, "rb") as f:
                for line in f:
                    try:
                        line = line.decode("ascii")
                    except:
                        break
                    line = line.replace("\n", "")
                    line = line.strip()
                    if line == "":
                        continue
                    # if line[0] != '#':
                    #     info.append(line)
                    if start_with_choice(line, *possible_keys):
                        info.append(line)
        return info

    def load_metadata(self):
        info = self.load_raw_metadata()
        key_int = ["ndim", "dim1", "dim2", "dim3", "nspace", "veclen"]
        key_str = ["data", "field"]
        metadata = {}
        metadata["labels"] = []
        metadata["units"] = []
        metadata["variables"] = []
        metadata["coords"] = []
        metadata["dims"] = []
        for line in info:
            key, value = line.split(maxsplit=1)
            if value[0] == "=":
                value = value.replace("=", "")
                value = value.strip()
                if key in key_int:
                    value = int(value)
                    metadata[key] = value
                elif key == "label":
                    labels = value.split()
                    for label in labels:
                        label, unit = best_str_to_name_unit(label, default_unit=None)
                        metadata["labels"].append(label)
                        metadata["units"].append(unit)
                else:
                    value = str(value)
                    metadata[key] = value

                if key[:3] == "dim":
                    metadata["dims"].append(metadata[key])

            else:
                if key == "variable":
                    vm = values_metadata(line)
                    vm["file"] = os.path.join(self.folder, vm["file"])
                    vm["size"] = np.prod(metadata["dims"])
                    metadata["variables"].append(vm)
                elif key == "coord":
                    vm = values_metadata(line)
                    vm["file"] = os.path.join(self.folder, vm["file"])
                    num = vm["num"]
                    vm["size"] = metadata[f"dim{num}"]
                    metadata["coords"].append(vm)

        self.metadata = metadata
        return metadata

    def load_variables(self):
        meta = self.metadata
        variables = DictList()
        for vmeta, label, unit in zip(meta["variables"], meta["labels"], meta["units"]):
            values = load_values(
                file=vmeta["file"],
                filetype=vmeta["filetype"],
                datatype=meta["data"],
                skip=vmeta["skip"],
                offset=vmeta["offset"],
                stride=vmeta["stride"],
                size=vmeta["size"],
            )
            values = reshape_values(values, *meta["dims"])
            var = Variable(name=label, value=values, unit=unit, metadata=vmeta)
            variables[var.name] = var
        self.variables = variables
        return variables

    def load_coords(self):
        meta = self.metadata
        coords = DictList()
        for vmeta in meta["coords"]:
            values = load_values(
                file=vmeta["file"],
                filetype=vmeta["filetype"],
                datatype=meta["data"],
                skip=vmeta["skip"],
                offset=vmeta["offset"],
                stride=vmeta["stride"],
                size=vmeta["size"],
            )
            ax = coord_axis(vmeta["num"])
            unit = "nm"
            var = Coord(
                name=ax, value=values, unit=unit, dim=vmeta["num"] - 1, metadata=vmeta
            )
            coords[var.name] = var
        self.coords = coords
        return coords


class Vtk(Output):
    def __init__(self, fullpath, **loader_kwargs):
        super().__init__(fullpath)
        self.load()

    def load(self):
        self.vtk = pv.read(self.fullpath)
        self.load_coords()
        self.load_variables()

    def load_coords(self):
        for i, coord in enumerate(["x", "y", "z"]):
            if not hasattr(self.vtk, coord):
                continue
            value = getattr(self.vtk, coord)
            if value.size == 1:
                continue
            self.coords[coord] = Coord(name=coord, value=value, unit=None, dim=i)

    def load_variables(self):
        for _name in self.vtk.array_names:
            name, unit = best_str_to_name_unit(_name, default_unit=None)
            value = (
                np.array(self.vtk[_name])
                .reshape(self.vtk.dimensions, order="F")
                .squeeze()
            )
            self.variables[name] = Variable(name=name, value=value, unit=unit)


class Dat(Output):
    def __init__(self, fullpath, **loader_kwargs):
        super().__init__(fullpath)
        self.load(**loader_kwargs)

    def load(self, **loader_kwargs):
        self.load_metadata(**loader_kwargs)
        self.load_data()

    def _get_headers(self):
        headers = []
        with open(self.fullpath, "r") as f:
            for line in f:
                try:
                    float(line.split()[0])
                    break
                except:
                    headers.append(line)
        return headers

    def _get_nb_columns(self):
        meta = self.metadata
        with open(self.fullpath, "r") as f:
            for i, line in enumerate(f):
                if i < meta["skip_rows"]:
                    continue
                line = line.replace("\n", "").strip().split()
                arr = np.array(line)
                break
        return arr.size

    def load_metadata(self, FirstVarIsCoordFlag=True):
        headers = self._get_headers()
        self.metadata["headers"] = headers
        self.metadata["skip_rows"] = len(headers)
        nb = self._get_nb_columns()
        self.metadata["nb_columns"] = nb

        if len(headers) == 0:
            raise NotImplementedError(".dat file without header")
        else:
            header = headers[-1]  # take the last one by default

        header = self._split_into_columns(header, nb)
        if header is None:
            raise RuntimeError(
                f"Can not load the datafile {self.fullpath}. The number of columns is not consistent"
            )

        columns_and_units = [self._extract_name_and_unit(column) for column in header]

        # diff = len(columns) - len(units)
        # if len(columns) > nb:
        #     columns = columns[0:nb]
        # elif diff > 0:
        #     empty = [""] * diff
        #     units.extend(empty)
        ndim = 0
        dkeys = []

        for i, (column, unit) in enumerate(columns_and_units):
            self.metadata[i] = {"name": column, "unit": unit}
            if FirstVarIsCoordFlag:
                ndim += 1
                dkeys.append(i)
                FirstVarIsCoordFlag = False
        self.metadata["ndim"] = ndim
        self.metadata["dkeys"] = dkeys
        return self.metadata

    def load_data(self):
        data = []
        meta = self.metadata
        # with open(self.fullpath, 'r') as f:
        #     for i, line in enumerate(f):
        #         if i < meta['skip_rows']:
        #             continue
        #         line = line.replace('\n', '').strip().split()
        #         if line:
        #             data.append(line)
        data = np.loadtxt(self.fullpath, skiprows=meta["skip_rows"])
        data = np.array(data, dtype=float).T  # columns 1st index
        coords, variables = DictList(), DictList()
        dims = []
        for i, values in enumerate(data):
            vm = meta[i]
            if i in meta["dkeys"]:
                # values = np.unique(values)
                dims.append(values.size)
                var = Coord(name=vm["name"], unit=vm["unit"], dim=i, value=values)
                coords[var.name] = var
            else:
                if dims:
                    values = values.reshape(*dims)
                var = Variable(name=vm["name"], unit=vm["unit"], value=values)
                variables[var.name] = var
        self.coords = coords
        self.variables = variables
        return coords, variables

    @staticmethod
    def _split_into_columns(header, expected_num_columns):
        # First try to split by any number of spaces
        columns = re.split(r"\s+", header.strip())

        # Check if the number of columns matches the expected number
        if len(columns) == expected_num_columns:
            return columns

        # If not matching, try splitting by two or more spaces or tabs
        columns = re.split(r"\s{2,}|\t+", header)

        # Final check to ensure we have the right number of columns (optional)
        if len(columns) != expected_num_columns:
            None
        return columns

    @staticmethod
    def _extract_name_and_unit(column):
        # Check if there is a unit in brackets
        match = re.search(r"\[(.*?)\]", column)
        if match:
            # Extract unit and remove it along with brackets from the column
            unit = match.group(1)
            name = column.replace(f"[{unit}]", "").strip()
        else:
            name, unit = column.strip(), ""
        return name, unit


def coord_axis(dim):
    dim = str(dim)
    axes = {"1": "x", "2": "y", "3": "z"}
    return axes[dim]


def values_metadata(line):
    """Return a dict for: kind, num, file, filetype, skip, offset, stride"""
    metadata = {}
    kind, num, rest = line.split(maxsplit=2)
    metadata["kind"] = kind
    metadata["num"] = int(num)
    raw_rest = rest.split("=")
    raw_rest = [r.strip().split() for r in raw_rest]
    rest = []
    for ri in raw_rest:
        rest.extend(ri)
    keys = rest[0::2]
    values = rest[1::2]
    for key, value in zip(keys, values):
        key = key.strip()
        value = value.strip()
        if key in ["num", "skip", "offset", "stride"]:
            value = int(value)
        metadata[key] = value
    return metadata


def load_values(
    file, filetype="ascii", datatype="double", skip=0, offset=0, stride=1, size=None
):
    """Return flat array of floating values"""
    if filetype == "ascii":

        stop = skip + size if size != None else None
        with open(file, "rb") as f:
            lines = islice(f, skip, stop, 1)
            values = [line.decode("ascii").replace("\n", "").strip().split()[offset] for line in lines]
    elif filetype == "binary":
        datatypes = {"double": "d"}
        datatype_sizes = {"double": 8}
        datatype_size = datatype_sizes[datatype]
        with open(file, "rb") as datafile:
            datafile.seek(skip)
            data = datafile.read(size * datatype_size)
            values = []
            iteration = struct.iter_unpack(datatypes[datatype], data)
            for i in iteration:
                values.append(i[0])

    else:
        raise ValueError("filetype is not recognized or implemented")
    return np.array(values, dtype=float)


def reshape_values(values, *dims):
    dims = np.flip(dims)
    shape = tuple([dim for dim in dims])
    values = np.reshape(values, shape)
    return np.transpose(values)


def write_avsascii_one_file(coordinates, variables, filename, binary=False):
    if binary:
        filetype = "binary"
        numpy_encoding = "bytes"
    else:
        filetype = "ascii"
        numpy_encoding = "bytes"
    # Validate input
    if len(coordinates) < 2 or len(coordinates) > 3:
        raise ValueError("Coordinates array must have exactly 2 or 3 objects.")

    num_coords = len(coordinates)
    num_variables = len(variables)

    # Calculate skip values
    # TODO calculate skip values (in bytes?) for binary output
    header_up_to_first_label = 9
    header_lines = (
        header_up_to_first_label + num_variables + 1 + num_variables + num_coords + 1
    )  # each 1 is skipped line
    coord_skip_values = [header_lines]
    for i in range(num_coords - 1):
        coord_skip_values.append(
            coord_skip_values[-1] + coordinates[i].value.size + 1
        )  # 1 for empty line after each coord

    data_skip = coord_skip_values[-1] + coordinates[-1].value.size + 1

    # Calculate the number of lines each variable takes
    number_of_lines_for_var = np.prod([coord.value.size for coord in coordinates])

    # Open file for writing
    with open(filename, "w") as file:
        # Write header
        file.write("# AVS/Express field file\n")
        file.write("#\n")
        file.write(f"ndim = {num_coords}\n")

        for i in range(num_coords):
            file.write(f"dim{i+1} = {coordinates[i].value.size}\n")

        file.write("nspace = {}\n".format(num_coords))
        file.write(f"veclen = {num_variables}\n")
        file.write("data = double\n")
        file.write("field = rectilinear\n")

        # Write variable labels and units
        for i in range(num_variables):
            file.write(f"label = {variables[i].name}[{variables[i].unit}]\n")

        # Write an empty line after the last label
        file.write("\n")

        # Write variable file paths
        for i, var in enumerate(variables):
            file.write(
                f"variable {i + 1} file={filename} filetype={filetype} skip={data_skip + i * number_of_lines_for_var} offset=0 stride=1\n"
            )

        # Write coordinate file paths
        for coord, skip_value, i in zip(
            coordinates, coord_skip_values, range(num_coords)
        ):
            file.write(
                f"coord {i+1} file={filename} filetype={filetype} skip={skip_value} offset=0 stride=1\n"
            )

        # Write an empty line after the last coord line
        file.write("\n")

        # Write data for coordinates
        for coord in coordinates:
            np.savetxt(
                file, coord.value.flatten("F"), fmt="%.8f", encoding=numpy_encoding
            )
            file.write("\n")

        # Write data for variables
        for var in variables:
            np.savetxt(
                file, var.value.flatten("F"), fmt="%.8f", encoding=numpy_encoding
            )
