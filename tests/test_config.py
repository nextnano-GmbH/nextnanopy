from pathlib import Path
from nextnanopy.defaults import NNConfig
import unittest
import warnings


default_config_path = Path.home() / ".nextnanopy-config"


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
            self.assertTrue(option in config.validators["nextnano3"].keys())
            self.assertTrue(option in config.defaults["nextnano3"].keys())
            self.assertTrue(option in config.config["nextnano3"].keys())
        self.assertTrue(Path(config.fullpath).is_file())

    def test_default_nnp(self):
        config = NNConfig()
        self.assertEqual(Path(config.fullpath), default_config_path)
        self.assertTrue("nextnano++" in config.validators.keys())
        self.assertTrue("nextnano++" in config.defaults.keys())
        self.assertTrue("nextnano++" in config.config.keys())
        options = ["exe", "license", "database", "threads", "outputdirectory"]
        for option in options:
            self.assertTrue(option in config.validators["nextnano++"].keys())
            self.assertTrue(option in config.defaults["nextnano++"].keys())
            self.assertTrue(option in config.config["nextnano++"].keys())
        self.assertTrue(Path(config.fullpath).is_file())

    def test_default_negf(self):
        config = NNConfig()
        self.assertEqual(Path(config.fullpath), default_config_path)
        self.assertTrue("nextnano.NEGF" in config.validators.keys())
        self.assertTrue("nextnano.NEGF" in config.defaults.keys())
        self.assertTrue("nextnano.NEGF" in config.config.keys())
        options = ["exe", "license", "database", "threads", "outputdirectory"]
        for option in options:
            self.assertTrue(option in config.validators["nextnano.NEGF"].keys())
            self.assertTrue(option in config.defaults["nextnano.NEGF"].keys())
            self.assertTrue(option in config.config["nextnano.NEGF"].keys())
        self.assertTrue(Path(config.fullpath).is_file())

    def test_default_nnevo(self):
        config = NNConfig()
        self.assertEqual(Path(config.fullpath), default_config_path)
        self.assertTrue("nextnanoevo" in config.validators.keys())
        self.assertTrue("nextnanoevo" in config.defaults.keys())
        self.assertTrue("nextnanoevo" in config.config.keys())
        options = ["license"]
        for option in options:
            self.assertTrue(option in config.validators["nextnanoevo"].keys())
            self.assertTrue(option in config.defaults["nextnanoevo"].keys())
            self.assertTrue(option in config.config["nextnanoevo"].keys())
        option = "exe"  # no exe for nnevo
        self.assertFalse(option in config.validators["nextnanoevo"].keys())
        self.assertFalse(option in config.defaults["nextnanoevo"].keys())
        self.assertFalse(option in config.config["nextnanoevo"].keys())
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
            self.assertTrue(option in config.validators["nextnano3"].keys())
            self.assertTrue(option in config.defaults["nextnano3"].keys())
            self.assertTrue(option in config.config["nextnano3"].keys())
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
            self.assertTrue(option in config.validators["nextnano++"].keys())
            self.assertTrue(option in config.defaults["nextnano++"].keys())
            self.assertTrue(option in config.config["nextnano++"].keys())
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
            self.assertTrue(option in config.validators["nextnano.NEGF"].keys())
            self.assertTrue(option in config.defaults["nextnano.NEGF"].keys())
            self.assertTrue(option in config.config["nextnano.NEGF"].keys())
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
            {"nextnano.NEGF++", "nextnano_nonexistent"},
        )


if __name__ == "__main__":
    unittest.main()
