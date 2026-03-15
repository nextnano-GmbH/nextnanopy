import unittest
from pathlib import Path
from nextnanopy import commands
from nextnanopy.utils.formatting import _path, _bool

folder_nnp = Path("tests") / "datafiles" / "nextnano++"
folder_nn3 = Path("tests") / "datafiles" / "nextnano3"
folder_negf = Path("tests") / "datafiles" / "nextnano.NEGF"
folder_msb = Path("tests") / "datafiles" / "nextnano.MSB"


class TestCommands(unittest.TestCase):

    def test_commands_nnp(self):
        self.maxDiff = None
        inputfile = folder_nnp / "example.in"
        exe = Path("nextnano++") / "bin 64bit" / "nextnano++_Intel_64bit.exe"
        runmode = "--resume"
        no_file_options = "--autosave --logfile"
        license = Path("nextnanopy") / "License" / "License_nnp.lic"
        database = Path("nextnano++") / "Syntax" / "database_nnp.in"
        outputdirectory = Path("tests") / "datafiles"
        threads = 4
        cmd = f'"{exe}" {runmode} --license "{license}" --database "{database}" --threads {threads} --outputdirectory "{outputdirectory}" --noautooutdir {no_file_options} "{inputfile}"'
        kwargs = dict(
            inputfile=inputfile,
            runmode=runmode,
            exe=exe,
            license=license,
            database=database,
            outputdirectory=outputdirectory,
            threads=threads,
            no_file_options=no_file_options,
        )
        from nextnanopy.nnp.defaults import command_nnp

        self.assertEqual(command_nnp(**kwargs), cmd)
        self.assertEqual(commands.command(**kwargs), cmd)

    def test_commands_nn3(self):
        self.maxDiff = None
        inputfile = folder_nn3 / "example.in"
        exe = Path("nextnano++") / "bin 64bit" / "nextnano++_Intel_64bit.exe"
        license = Path("nextnanopy") / "License" / "License_nnp.lic"
        database = Path("nextnano++") / "Syntax" / "database_nnp.in"
        outputdirectory = Path("tests") / "datafiles"
        threads = 4
        debuglevel = 0
        cancel = -1
        softkill = -1
        no_file_options = "-log -parse"
        cmd = f'"{exe}" -license "{license}" -inputfile "{inputfile}" -database "{database}" -threads {threads} -outputdirectory "{outputdirectory}" -debuglevel {debuglevel} -cancel {cancel} -softkill {softkill} {no_file_options}'
        kwargs = dict(
            inputfile=inputfile,
            exe=exe,
            license=license,
            database=database,
            outputdirectory=outputdirectory,
            threads=threads,
            debuglevel=debuglevel,
            cancel=cancel,
            softkill=softkill,
            no_file_options=no_file_options,
        )
        from nextnanopy.nn3.defaults import command_nn3

        self.assertEqual(command_nn3(**kwargs), cmd)
        self.assertEqual(commands.command(**kwargs), cmd)

    def test_commands_negf_classic(self):
        self.maxDiff = None
        inputfile = folder_negf / "example.xml"
        exe = Path("nextnano.NEGF") / "nextnano.NEGF.exe"
        license = Path("License") / "License_nnQCL.lic"
        database = Path("nextnano.NEGF") / "Material_Database.xml"
        outputdirectory = Path("tests") / "datafiles"
        threads = 4
        cmd = f'"{exe}" "{inputfile}" "{outputdirectory}" "{database}" "{license}" -threads {threads}'
        kwargs = dict(
            inputfile=inputfile,
            exe=exe,
            license=license,
            database=database,
            outputdirectory=outputdirectory,
            threads=threads,
        )
        from nextnanopy.negf.defaults import command_negf_classic

        self.assertEqual(command_negf_classic(**kwargs), cmd)
        self.assertEqual(commands.command(**kwargs), cmd)

    # TODO: add test_commands_negf

    def test_commands_msb(self):
        from nextnanopy.msb.defaults import command_msb

        self.maxDiff = None
        inputfile = folder_msb / "example.msb"
        exe = Path("nextnano.MSB") / "nextnano.MSB.exe"
        license = Path("License") / "License_nnMSB.lic"
        database = Path("nextnano.MSB") / "Materials.xml"
        outputdirectory = Path("tests") / "datafiles"
        threads = 1

        cmd = f'"{exe}" --license "{license}" --database "{database}" --threads {threads} --outputdirectory "{outputdirectory}" --noautooutdir "{inputfile}"'
        kwargs = dict(
            inputfile=inputfile,
            exe=exe,
            license=license,
            database=database,
            outputdirectory=outputdirectory,
            threads=threads,
        )
        self.assertEqual(command_msb(**kwargs), cmd)
        self.assertEqual(commands.command(**kwargs), cmd)

    def test_path(self):
        self.assertEqual(_path("aa\nb.test"), '"aa\nb.test"')
        self.assertEqual(_path("aa\nb"), '"aa\nb"')
        self.assertEqual(_path(""), "")
        self.assertEqual(_path(2), '"2"')
        self.assertEqual(_path(None), None)

    def test_execute(self):
        self.assertRaises(
            ValueError,
            commands.execute,
            inputfile="",
            exe="",
            license="",
            database="",
            outputdirectory="",
        )
        self.assertRaises(
            ValueError,
            commands.execute,
            inputfile=Path("test") / "datafiles",
            exe="",
            license="",
            database="",
            outputdirectory="",
        )

    def test_bool(self):
        self.assertEqual(_bool(""), False)
        self.assertEqual(_bool(None), False)
        self.assertEqual(_bool("1"), True)
        self.assertEqual(_bool("0"), True)
        self.assertEqual(_bool(0), True)
        self.assertEqual(_bool(1), True)


if __name__ == "__main__":
    unittest.main()
