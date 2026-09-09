import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from nextnanopy import commands
from nextnanopy.utils.formatting import _bool, _path

folder_nnp = Path("tests") / "datafiles" / "nextnano++"
folder_nn3 = Path("tests") / "datafiles" / "nextnano3"
folder_negf = Path("tests") / "datafiles" / "nextnano.NEGF"
folder_msb = Path("tests") / "datafiles" / "nextnano.MSB"


class TestCommands(unittest.TestCase):
    def test_commands_nnp(self):
        self.maxDiff = None
        inputfile = folder_nnp / "example.nnp"
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
        inputfile = folder_nn3 / "example.nn3"
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
        cmd = (
            f'"{exe}" "{inputfile}" "{outputdirectory}" "{database}" "{license}" -threads {threads}'
        )
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


class TestExecuteOutputDirectory(unittest.TestCase):
    """execute() decides which directory the simulation writes into.

    Two knobs, neither of which is a simulator command line argument:

    - create_subdirectory: <outputdirectory>/<input file name>/ (default), or
      <outputdirectory> itself
    - overwrite: claim a fresh directory under a unique name (default), or reuse
      one that is already there

    overwrite defaults to False, matching .save() and Sweep.execute_sweep(): a run
    never writes into another run's output unless it is asked to. Earlier versions
    always reused <outputdirectory>/<input file name>/, which is now overwrite=True.

    No nextnano executable is needed: send() and start_log() are patched out, so
    nothing is launched and no log is written - only the directory bookkeeping runs.
    The executable still has to exist, since execute() validates it, so the test
    passes the running interpreter.
    """

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.out = self.root / "out"
        # 'global{' is all input_text_type() needs to read this as a nextnano++ file,
        # which is what command() looks up to build the command line.
        self.inputfile = self.root / "example.in"
        self.inputfile.write_text("global{}\n")
        for name, value in [("send", None), ("start_log", (None, None, None))]:
            patch = unittest.mock.patch.object(commands, name, return_value=value)
            patch.start()
            self.addCleanup(patch.stop)

    def execute(self, **kwargs):
        """Run execute() on the temp input file and return its output directory."""
        info = commands.execute(
            inputfile=self.inputfile,
            exe=sys.executable,
            license="",
            database="",
            outputdirectory=self.out,
            show_log=False,
            **kwargs,
        )
        self.info = info
        return Path(info["outputdirectory"])

    def subdirectories(self, folder):
        return sorted(p.name for p in Path(folder).iterdir() if p.is_dir())

    def test_subdirectory_named_after_the_input_file_is_the_default(self):
        outputdirectory = self.execute()

        self.assertEqual(outputdirectory, self.out / "example")
        self.assertTrue(outputdirectory.is_dir())
        # nothing was in the way, so the name is used as it is - no index appended
        self.assertEqual(self.subdirectories(self.out), ["example"])

    def test_the_default_leaves_an_earlier_run_alone(self):
        # overwrite defaults to False, so a second run of the same input file gets
        # its own directory instead of writing over the first one's results.
        (self.out / "example").mkdir(parents=True)
        (self.out / "example" / "old_result.dat").write_text("from the previous run")

        outputdirectory = self.execute()

        self.assertEqual(outputdirectory, self.out / "example_0")
        self.assertTrue((self.out / "example" / "old_result.dat").is_file())

    def test_overwrite_true_reuses_the_existing_directory(self):
        # overwrite=True means 'write into it', not 'wipe it': what an earlier run
        # left behind is still there afterwards.
        (self.out / "example").mkdir(parents=True)
        (self.out / "example" / "old_result.dat").write_text("from the previous run")

        outputdirectory = self.execute(overwrite=True)

        self.assertEqual(outputdirectory, self.out / "example")
        self.assertTrue((outputdirectory / "old_result.dat").is_file())
        self.assertEqual(self.subdirectories(self.out), ["example"])

    def test_overwrite_false_claims_a_new_directory_each_run(self):
        (self.out / "example").mkdir(parents=True)
        (self.out / "example" / "old_result.dat").write_text("from the previous run")

        first = self.execute(overwrite=False)
        second = self.execute(overwrite=False)

        self.assertEqual(first, self.out / "example_0")
        self.assertEqual(second, self.out / "example_1")
        self.assertTrue(first.is_dir())
        self.assertTrue(second.is_dir())
        # the run that was already there is untouched
        self.assertTrue((self.out / "example" / "old_result.dat").is_file())

    def test_overwrite_true_creates_the_subdirectory_when_it_is_missing(self):
        # the fourth case of the grid: overwrite=True has nothing to reuse on a first
        # run, and must create the directory rather than expect one
        outputdirectory = self.execute(overwrite=True)

        self.assertEqual(outputdirectory, self.out / "example")
        self.assertTrue(outputdirectory.is_dir())

    def test_create_subdirectory_false_writes_into_the_outputdirectory(self):
        outputdirectory = self.execute(create_subdirectory=False)

        self.assertEqual(outputdirectory, self.out)
        self.assertTrue(self.out.is_dir())
        self.assertEqual(self.subdirectories(self.out), [])

    def test_create_subdirectory_false_ignores_overwrite(self):
        # With no subdirectory to name, there is nothing to make unique: the
        # configured outputdirectory is used as it is, and no sibling is invented.
        self.out.mkdir(parents=True)
        (self.out / "old_result.dat").write_text("from the previous run")

        outputdirectory = self.execute(create_subdirectory=False, overwrite=False)

        self.assertEqual(outputdirectory, self.out)
        self.assertEqual(self.subdirectories(self.root), ["out"])
        self.assertTrue((self.out / "old_result.dat").is_file())

    def test_logfile_lands_in_the_directory_that_was_chosen(self):
        (self.out / "example").mkdir(parents=True)

        outputdirectory = self.execute(overwrite=False)

        self.assertEqual(Path(self.info["logfile"]), outputdirectory / "example.log")

    def test_the_simulator_is_told_the_directory_that_was_resolved(self):
        # The resolved directory has to reach the command line too, not just the
        # returned info: everything else here would still pass if the simulation were
        # started on the outputdirectory as it came in.
        (self.out / "example").mkdir(parents=True)

        outputdirectory = self.execute(overwrite=False)

        self.assertIn(f'--outputdirectory "{outputdirectory}"', self.info["cmd"])


if __name__ == "__main__":
    unittest.main()
