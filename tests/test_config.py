import os
import subprocess
import sys
import tempfile
import unittest
import warnings
from importlib import metadata
from pathlib import Path
from unittest import mock

import nextnanopy
from nextnanopy.defaults import NNConfig, products
from nextnanopy.utils.config import Config

default_config_path = Path.home() / ".nextnanopy-config"


def _run_in_home(args, home):
    """Run the interpreter with `args` in a subprocess whose home directory is `home`.

    Returns the completed process and the names of the files `home` holds afterwards.
    """
    env = dict(os.environ, HOME=home, USERPROFILE=home)
    proc = subprocess.run(
        [sys.executable, *args],
        env=env,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    return proc, sorted(p.name for p in Path(home).iterdir())


def _run_in_fake_home(args):
    """Run the interpreter with `args` in a subprocess whose home is an empty temp folder.

    A fresh interpreter is the only honest way to test import-time behaviour, and a fake
    home is the only way to see the first-run bootstrap: this machine already has a
    ~/.nextnanopy-config, which is the case that does NOT write.
    """
    with tempfile.TemporaryDirectory() as home:
        return _run_in_home(args, home)


# The body of the console script pip generates from the entry point, as source to hand to
# `python -c`: the wrapper is nothing more than this call.
_CLI_SOURCE = "import sys\nfrom nextnanopy.utils.config_cli import main\nsys.exit(main())\n"


class Test_NNConfig(unittest.TestCase):
    def test_default_nn3(self):
        config = NNConfig()

        self.assertEqual(Path(config.fullpath), default_config_path)
        self.assertTrue("nextnano3" in config.validators.keys())
        self.assertTrue("nextnano3" in config.defaults.keys())
        self.assertTrue("nextnano3" in config.config.keys())
        options = [
            "exe",
            "license",
            "database",
            "threads",
            "outputdirectory",
            "debuglevel",
            "cancel",
            "softkill",
        ]
        for option in options:
            self.assertTrue(option in config.defaults["nextnano3"].keys())
            self.assertTrue(option in config.config["nextnano3"].keys())
        # Only options that need type conversion carry a validator; path options do not.
        for option in ["threads", "debuglevel", "cancel", "softkill"]:
            self.assertTrue(option in config.validators["nextnano3"].keys())
        self.assertTrue(Path(config.fullpath).is_file())

    def test_default_nnp(self):
        config = NNConfig()
        self.assertEqual(Path(config.fullpath), default_config_path)
        self.assertTrue("nextnano++" in config.validators.keys())
        self.assertTrue("nextnano++" in config.defaults.keys())
        self.assertTrue("nextnano++" in config.config.keys())
        options = ["exe", "license", "database", "threads", "outputdirectory"]
        for option in options:
            self.assertTrue(option in config.defaults["nextnano++"].keys())
            self.assertTrue(option in config.config["nextnano++"].keys())
        # Only options that need type conversion carry a validator; path options do not.
        self.assertTrue("threads" in config.validators["nextnano++"].keys())
        self.assertTrue(Path(config.fullpath).is_file())

    def test_default_negf(self):
        config = NNConfig()
        self.assertEqual(Path(config.fullpath), default_config_path)
        self.assertTrue("nextnano.NEGF" in config.validators.keys())
        self.assertTrue("nextnano.NEGF" in config.defaults.keys())
        self.assertTrue("nextnano.NEGF" in config.config.keys())
        options = ["exe", "license", "database", "threads", "outputdirectory"]
        for option in options:
            self.assertTrue(option in config.defaults["nextnano.NEGF"].keys())
            self.assertTrue(option in config.config["nextnano.NEGF"].keys())
        # Only options that need type conversion carry a validator; path options do not.
        self.assertTrue("threads" in config.validators["nextnano.NEGF"].keys())
        self.assertTrue(Path(config.fullpath).is_file())

    def test_default_nnopti(self):
        config = NNConfig()
        self.assertEqual(Path(config.fullpath), default_config_path)
        self.assertTrue("nextnano optimizers" in config.validators.keys())
        self.assertTrue("nextnano optimizers" in config.defaults.keys())
        self.assertTrue("nextnano optimizers" in config.config.keys())
        options = ["license"]
        for option in options:
            self.assertTrue(option in config.defaults["nextnano optimizers"].keys())
            self.assertTrue(option in config.config["nextnano optimizers"].keys())
        # nnopti has no option needing type conversion, so its validator dict is empty;
        # 'license' is a path kept verbatim.
        self.assertFalse("license" in config.validators["nextnano optimizers"].keys())
        option = "exe"  # no exe for nnopti
        self.assertFalse(option in config.validators["nextnano optimizers"].keys())
        self.assertFalse(option in config.defaults["nextnano optimizers"].keys())
        self.assertFalse(option in config.config["nextnano optimizers"].keys())
        self.assertTrue(Path(config.fullpath).is_file())

    def test_load_nn3(self):
        fullpath = Path("tests") / ".nextnanopy-config"
        config = NNConfig(fullpath)

        self.assertEqual(Path(config.fullpath), fullpath)
        self.assertTrue("nextnano3" in config.validators.keys())
        self.assertTrue("nextnano3" in config.defaults.keys())
        self.assertTrue("nextnano3" in config.config.keys())
        options = [
            "exe",
            "license",
            "database",
            "threads",
            "outputdirectory",
            "debuglevel",
            "cancel",
            "softkill",
        ]
        for option in options:
            self.assertTrue(option in config.defaults["nextnano3"].keys())
            self.assertTrue(option in config.config["nextnano3"].keys())
        # Only options that need type conversion carry a validator; path options do not.
        for option in ["threads", "debuglevel", "cancel", "softkill"]:
            self.assertTrue(option in config.validators["nextnano3"].keys())
        self.assertTrue(Path(config.fullpath).is_file())
        if Path(config.fullpath).is_file():
            Path(config.fullpath).unlink()

        self.assertEqual(config.config["nextnano3"]["exe"], "")
        config.set("nextnano3", "exe", "some_path")
        self.assertEqual(config.config["nextnano3"]["exe"], "some_path")
        config.to_default()
        self.assertEqual(config.config["nextnano3"]["exe"], "")
        if Path(config.fullpath).is_file():
            Path(config.fullpath).unlink()
        fullpath_new = Path("tests") / "test.nnconfig"
        self.assertFalse(fullpath_new.is_file())
        config.save(fullpath_new)
        self.assertTrue(fullpath_new.is_file())
        self.assertEqual(Path(config.fullpath), fullpath_new)
        if Path(config.fullpath).is_file():
            Path(config.fullpath).unlink()

    def test_load_nnp(self):
        fullpath = Path("tests") / ".nextnanopy-config"
        config = NNConfig(fullpath)

        self.assertEqual(Path(config.fullpath), fullpath)
        self.assertTrue("nextnano++" in config.validators.keys())
        self.assertTrue("nextnano++" in config.defaults.keys())
        self.assertTrue("nextnano++" in config.config.keys())
        options = ["exe", "license", "database", "threads", "outputdirectory"]
        for option in options:
            self.assertTrue(option in config.defaults["nextnano++"].keys())
            self.assertTrue(option in config.config["nextnano++"].keys())
        # Only options that need type conversion carry a validator; path options do not.
        self.assertTrue("threads" in config.validators["nextnano++"].keys())
        self.assertTrue(Path(config.fullpath).is_file())
        if Path(config.fullpath).is_file():
            Path(config.fullpath).unlink()

        self.assertEqual(config.config["nextnano++"]["exe"], "")
        config.set("nextnano++", "exe", "some_path")
        self.assertEqual(config.config["nextnano++"]["exe"], "some_path")
        config.to_default()
        self.assertEqual(config.config["nextnano++"]["exe"], "")
        if Path(config.fullpath).is_file():
            Path(config.fullpath).unlink()
        fullpath_new = Path("tests") / "test.nnconfig"
        self.assertFalse(fullpath_new.is_file())
        config.save(fullpath_new)
        self.assertTrue(fullpath_new.is_file())
        self.assertEqual(Path(config.fullpath), fullpath_new)
        if Path(config.fullpath).is_file():
            Path(config.fullpath).unlink()

    def test_load_negf(self):
        fullpath = Path("tests") / ".nextnanopy-config"
        config = NNConfig(fullpath)

        self.assertEqual(Path(config.fullpath), fullpath)
        self.assertTrue("nextnano.NEGF" in config.validators.keys())
        self.assertTrue("nextnano.NEGF" in config.defaults.keys())
        self.assertTrue("nextnano.NEGF" in config.config.keys())
        options = ["exe", "license", "database", "threads", "outputdirectory"]
        for option in options:
            self.assertTrue(option in config.defaults["nextnano.NEGF"].keys())
            self.assertTrue(option in config.config["nextnano.NEGF"].keys())
        # Only options that need type conversion carry a validator; path options do not.
        self.assertTrue("threads" in config.validators["nextnano.NEGF"].keys())
        self.assertTrue(Path(config.fullpath).is_file())
        if Path(config.fullpath).is_file():
            Path(config.fullpath).unlink()

        self.assertEqual(config.config["nextnano.NEGF"]["exe"], "")
        config.set("nextnano.NEGF", "exe", "some_path")
        self.assertEqual(config.config["nextnano.NEGF"]["exe"], "some_path")
        config.to_default()
        self.assertEqual(config.config["nextnano.NEGF"]["exe"], "")
        if Path(config.fullpath).is_file():
            Path(config.fullpath).unlink()
        fullpath_new = Path("tests") / "test.nnconfig"
        self.assertFalse(fullpath_new.is_file())
        config.save(fullpath_new)
        self.assertTrue(fullpath_new.is_file())
        self.assertEqual(Path(config.fullpath), fullpath_new)
        if Path(config.fullpath).is_file():
            Path(config.fullpath).unlink()

    def test_get_unsupported_products(self):
        filepath = Path("tests") / "configs" / ".nnconfig_unsupported"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            config = NNConfig(filepath)
        unsupported_products = set(config.get_unsupported_products())
        self.assertEqual(
            unsupported_products,
            {"nextnano.NEGF++", "nextnano_nonexistent", "nextnanoevo"},
        )


class Test_LazyConfig(unittest.TestCase):
    def _run_in_fake_home(self, code):
        proc, created = _run_in_fake_home(["-c", code])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout.strip(), created

    def test_import_does_not_create_config_file(self):
        stdout, created = self._run_in_fake_home("import nextnanopy; print('imported')")

        self.assertEqual(stdout, "imported")
        self.assertEqual(created, [])

    def test_accessing_config_creates_config_file(self):
        # The bootstrap still happens, just on first access rather than on import.
        stdout, created = self._run_in_fake_home(
            "import nextnanopy; print(nextnanopy.config.fullpath)"
        )

        self.assertEqual(created, [".nextnanopy-config"])
        self.assertEqual(Path(stdout).name, ".nextnanopy-config")

    def test_config_is_cached_and_supports_set_then_save(self):
        # The documented workflow (templates/config_nextnano.py): set on one access,
        # save on another. It only works if both see the same object.
        code = (
            "import nextnanopy as nn\n"
            "nn.config.set('nextnano++', 'exe', 'some_path')\n"
            "nn.config.save()\n"
            "print(nn.config is nn.config)\n"
            "print(nn.NNConfig().get('nextnano++', 'exe'))\n"
        )
        stdout, created = self._run_in_fake_home(code)

        self.assertEqual(created, [".nextnanopy-config"])
        self.assertEqual(stdout.splitlines(), ["True", "some_path"])

    def test_from_import_still_works(self):
        stdout, _ = self._run_in_fake_home(
            "from nextnanopy import config; print(type(config).__name__)"
        )

        self.assertEqual(stdout, "NNConfig")

    def test_unknown_attribute_raises_attribute_error(self):
        # Defining a module __getattr__ takes over the missing-attribute path: without
        # the trailing raise, every unknown name would silently evaluate to None.
        with self.assertRaises(AttributeError):
            _ = nextnanopy.does_not_exist


class Test_CLI(unittest.TestCase):
    """Tests for the nextnanopy-config command.

    The command is run in a subprocess with a fake home, so the real
    ~/.nextnanopy-config of the machine running the tests is never read or written.
    """

    def _run_cli(self, *args, home=None):
        """Run the command in a subprocess whose home directory is `home`.

        An empty temp folder is used when `home` is omitted. The command is driven
        through its entry-point function rather than the installed `nextnanopy-config`
        wrapper, so that the tests hold for a source checkout as well; that the wrapper
        points at that function is what test_console_script_is_declared asserts.
        """
        argv = ["-c", _CLI_SOURCE, *args]
        if home is None:
            return _run_in_fake_home(argv)
        return _run_in_home(argv, home)

    def _configure(self, home, value):
        """Set nextnano++ `exe` to `value` in the config file of `home` and save it."""
        fullpath = Path(home) / ".nextnanopy-config"
        config = NNConfig(fullpath)
        config.set("nextnano++", "exe", value)
        config.save()
        return fullpath

    def test_creates_config_file_in_empty_home(self):
        proc, created = self._run_cli()

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(created, [".nextnanopy-config"])
        # The path is the first line on its own, so a script can read it with `head -1`.
        first_line = proc.stdout.splitlines()[0]
        self.assertEqual(Path(first_line).name, ".nextnanopy-config")

    def test_second_run_keeps_the_configured_paths(self):
        with tempfile.TemporaryDirectory() as home:
            proc, _ = self._run_cli(home=home)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            fullpath = self._configure(home, "some_path")

            proc, _ = self._run_cli(home=home)

            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(NNConfig(fullpath).get("nextnano++", "exe"), "some_path")

    def test_reset_restores_the_defaults(self):
        with tempfile.TemporaryDirectory() as home:
            proc, _ = self._run_cli(home=home)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            fullpath = self._configure(home, "some_path")

            proc, _ = self._run_cli("--reset", home=home)

            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(NNConfig(fullpath).get("nextnano++", "exe"), "")

    def test_show_prints_every_product_section(self):
        proc, _ = self._run_cli("--show")

        self.assertEqual(proc.returncode, 0, proc.stderr)
        for product in products:
            self.assertIn(f"[{product}]", proc.stdout)

    def test_module_invocation_runs_main(self):
        # `python -m nextnanopy.utils.config_cli` is a PATH-independent way to reach the
        # command, so the module runs main() when executed as __main__.
        proc, created = _run_in_fake_home(["-m", "nextnanopy.utils.config_cli"])

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(created, [".nextnanopy-config"])
        first_line = proc.stdout.splitlines()[0]
        self.assertEqual(Path(first_line).name, ".nextnanopy-config")

    def test_console_script_is_declared(self):
        # The entry point is the whole reason `nextnanopy-config` exists as a command.
        # Nothing else fails if it is dropped from pyproject.toml: the package still
        # imports and `python -m nextnanopy` still works.
        try:
            dist = metadata.distribution("nextnanopy")
        except metadata.PackageNotFoundError:
            self.skipTest("nextnanopy is not installed, so there is no metadata to read")
        scripts = {ep.name: ep.value for ep in dist.entry_points if ep.group == "console_scripts"}
        self.assertEqual(
            scripts.get("nextnanopy-config"),
            "nextnanopy.utils.config_cli:main",
            "console script metadata is missing or stale; reinstall with `pip install -e .`",
        )


class Test_Config(unittest.TestCase):
    def test_falsy_fullpath_raises(self):
        for fullpath in ["", None]:
            with self.assertRaises(ValueError):
                Config(fullpath)

    def test_missing_file_yields_empty_config(self):
        with tempfile.TemporaryDirectory() as folder:
            fullpath = Path(folder) / "missing.nnconfig"
            config = Config(str(fullpath))

            self.assertEqual(list(config.sections), [])
            self.assertEqual(Path(config.fullpath), fullpath)

    def test_save_creates_missing_file(self):
        with tempfile.TemporaryDirectory() as folder:
            fullpath = Path(folder) / "new.nnconfig"
            config = Config(str(fullpath))
            config.add_section("nextnano++")
            config.set("nextnano++", "exe", "some_path")
            config.save()

            self.assertTrue(fullpath.is_file())
            self.assertEqual(Config(str(fullpath)).get("nextnano++", "exe"), "some_path")

    def test_set_without_save_does_not_create_file(self):
        with tempfile.TemporaryDirectory() as folder:
            fullpath = Path(folder) / "unsaved.nnconfig"
            config = Config(str(fullpath))
            config.add_section("nextnano++")
            config.set("nextnano++", "exe", "some_path")

            self.assertEqual(config.get("nextnano++", "exe"), "some_path")
            self.assertFalse(fullpath.is_file())

    def test_set_without_save_does_not_change_file(self):
        with tempfile.TemporaryDirectory() as folder:
            fullpath = Path(folder) / "existing.nnconfig"
            config = Config(str(fullpath))
            config.add_section("nextnano++")
            config.set("nextnano++", "exe", "original")
            config.save()

            config.set("nextnano++", "exe", "modified")

            self.assertEqual(config.get("nextnano++", "exe"), "modified")
            self.assertEqual(Config(str(fullpath)).get("nextnano++", "exe"), "original")

    def test_empty_fullpath_raises_for_nnconfig(self):
        # None means 'use the default path', but an empty path is a caller bug
        # and must not be silently treated as the default.
        with self.assertRaises(ValueError):
            NNConfig("")

    def test_save_to_new_path_leaves_no_temp_file(self):
        with tempfile.TemporaryDirectory() as folder:
            fullpath = Path(folder) / "first.nnconfig"
            config = Config(str(fullpath))
            config.add_section("nextnano++")
            config.set("nextnano++", "exe", "some_path")
            config.save()

            new_fullpath = Path(folder) / "second.nnconfig"
            config.save(str(new_fullpath))

            self.assertEqual(Path(config.fullpath), new_fullpath)
            self.assertEqual(Config(str(new_fullpath)).get("nextnano++", "exe"), "some_path")
            self.assertEqual(
                sorted(p.name for p in Path(folder).iterdir()),
                ["first.nnconfig", "second.nnconfig"],
            )

    def test_failed_save_keeps_previous_file_and_leaves_no_temp_file(self):
        # save() writes a temp file and swaps it in with os.replace, so a write that
        # blows up half way must not truncate the config that is already on disk.
        with tempfile.TemporaryDirectory() as folder:
            fullpath = Path(folder) / "existing.nnconfig"
            config = Config(str(fullpath))
            config.add_section("nextnano++")
            config.set("nextnano++", "exe", "original")
            config.save()

            config.set("nextnano++", "exe", "modified")
            with mock.patch.object(config.configparser, "write", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    config.save()

            self.assertEqual(Config(str(fullpath)).get("nextnano++", "exe"), "original")
            self.assertEqual([p.name for p in Path(folder).iterdir()], ["existing.nnconfig"])


if __name__ == "__main__":
    unittest.main()
