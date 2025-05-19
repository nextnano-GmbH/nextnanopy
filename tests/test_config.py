import os
from nextnanopy.defaults import NNConfig
import unittest
import platform
import warnings

system = platform.system()


class Test_NNConfig(unittest.TestCase):
    def test_default_nn3(self):
        config = NNConfig()

        if system == "Windows":
            default_fullpath = os.path.join(
                os.environ["HOMEDRIVE"], os.environ["HOMEPATH"], ".nextnanopy-config"
            )
        else:
            default_fullpath = os.path.join(os.environ["HOME"], ".nextnanopy-config")

        self.assertEqual(config.fullpath, default_fullpath)
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
        self.assertTrue(os.path.isfile(config.fullpath))

    def test_default_nnp(self):
        config = NNConfig()
        if system == "Windows":
            default_fullpath = os.path.join(
                os.environ["HOMEDRIVE"], os.environ["HOMEPATH"], ".nextnanopy-config"
            )
        else:
            default_fullpath = os.path.join(os.environ["HOME"], ".nextnanopy-config")
        self.assertEqual(config.fullpath, default_fullpath)
        self.assertTrue("nextnano++" in config.validators.keys())
        self.assertTrue("nextnano++" in config.defaults.keys())
        self.assertTrue("nextnano++" in config.config.keys())
        options = ["exe", "license", "database", "threads", "outputdirectory"]
        for option in options:
            self.assertTrue(option in config.validators["nextnano++"].keys())
            self.assertTrue(option in config.defaults["nextnano++"].keys())
            self.assertTrue(option in config.config["nextnano++"].keys())
        self.assertTrue(os.path.isfile(config.fullpath))

    def test_default_negf(self):
        config = NNConfig()
        if system == "Windows":
            default_fullpath = os.path.join(
                os.environ["HOMEDRIVE"], os.environ["HOMEPATH"], ".nextnanopy-config"
            )
        else:
            default_fullpath = os.path.join(os.environ["HOME"], ".nextnanopy-config")

        self.assertEqual(config.fullpath, default_fullpath)
        self.assertTrue("nextnano.NEGF" in config.validators.keys())
        self.assertTrue("nextnano.NEGF" in config.defaults.keys())
        self.assertTrue("nextnano.NEGF" in config.config.keys())
        options = ["exe", "license", "database", "threads", "outputdirectory"]
        for option in options:
            self.assertTrue(option in config.validators["nextnano.NEGF"].keys())
            self.assertTrue(option in config.defaults["nextnano.NEGF"].keys())
            self.assertTrue(option in config.config["nextnano.NEGF"].keys())
        self.assertTrue(os.path.isfile(config.fullpath))

    def test_default_nnevo(self):
        config = NNConfig()
        if system == "Windows":
            default_fullpath = os.path.join(
                os.environ["HOMEDRIVE"], os.environ["HOMEPATH"], ".nextnanopy-config"
            )
        else:
            default_fullpath = os.path.join(os.environ["HOME"], ".nextnanopy-config")

        self.assertEqual(config.fullpath, default_fullpath)
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
        self.assertTrue(os.path.isfile(config.fullpath))

    def test_load_nn3(self):
        fullpath = os.path.join("tests", ".nextnanopy-config")
        config = NNConfig(fullpath)

        self.assertEqual(config.fullpath, fullpath)
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
        self.assertTrue(os.path.isfile(config.fullpath))
        if os.path.isfile(config.fullpath):
            os.remove(config.fullpath)

        self.assertEqual(config.config["nextnano3"]["exe"], "")
        config.set("nextnano3", "exe", "some_path")
        self.assertEqual(config.config["nextnano3"]["exe"], "some_path")
        config.to_default()
        self.assertEqual(config.config["nextnano3"]["exe"], "")
        if os.path.isfile(config.fullpath):
            os.remove(config.fullpath)
        fullpath_new = os.path.join("tests", "test.nnconfig")
        self.assertFalse(os.path.isfile(fullpath_new))
        config.save(fullpath_new)
        self.assertTrue(os.path.isfile(fullpath_new))
        self.assertEqual(config.fullpath, fullpath_new)
        if os.path.isfile(config.fullpath):
            os.remove(config.fullpath)

    def test_load_nnp(self):
        fullpath = os.path.join("tests", ".nextnanopy-config")
        config = NNConfig(fullpath)

        self.assertEqual(config.fullpath, fullpath)
        self.assertTrue("nextnano++" in config.validators.keys())
        self.assertTrue("nextnano++" in config.defaults.keys())
        self.assertTrue("nextnano++" in config.config.keys())
        options = ["exe", "license", "database", "threads", "outputdirectory"]
        for option in options:
            self.assertTrue(option in config.validators["nextnano++"].keys())
            self.assertTrue(option in config.defaults["nextnano++"].keys())
            self.assertTrue(option in config.config["nextnano++"].keys())
        self.assertTrue(os.path.isfile(config.fullpath))
        if os.path.isfile(config.fullpath):
            os.remove(config.fullpath)

        self.assertEqual(config.config["nextnano++"]["exe"], "")
        config.set("nextnano++", "exe", "some_path")
        self.assertEqual(config.config["nextnano++"]["exe"], "some_path")
        config.to_default()
        self.assertEqual(config.config["nextnano++"]["exe"], "")
        if os.path.isfile(config.fullpath):
            os.remove(config.fullpath)
        fullpath_new = os.path.join("tests", "test.nnconfig")
        self.assertFalse(os.path.isfile(fullpath_new))
        config.save(fullpath_new)
        self.assertTrue(os.path.isfile(fullpath_new))
        self.assertEqual(config.fullpath, fullpath_new)
        if os.path.isfile(config.fullpath):
            os.remove(config.fullpath)

    def test_load_negf(self):
        fullpath = os.path.join("tests", ".nextnanopy-config")
        config = NNConfig(fullpath)

        self.assertEqual(config.fullpath, fullpath)
        self.assertTrue("nextnano.NEGF" in config.validators.keys())
        self.assertTrue("nextnano.NEGF" in config.defaults.keys())
        self.assertTrue("nextnano.NEGF" in config.config.keys())
        options = ["exe", "license", "database", "threads", "outputdirectory"]
        for option in options:
            self.assertTrue(option in config.validators["nextnano.NEGF"].keys())
            self.assertTrue(option in config.defaults["nextnano.NEGF"].keys())
            self.assertTrue(option in config.config["nextnano.NEGF"].keys())
        self.assertTrue(os.path.isfile(config.fullpath))
        if os.path.isfile(config.fullpath):
            os.remove(config.fullpath)

        self.assertEqual(config.config["nextnano.NEGF"]["exe"], "")
        config.set("nextnano.NEGF", "exe", "some_path")
        self.assertEqual(config.config["nextnano.NEGF"]["exe"], "some_path")
        config.to_default()
        self.assertEqual(config.config["nextnano.NEGF"]["exe"], "")
        if os.path.isfile(config.fullpath):
            os.remove(config.fullpath)
        fullpath_new = os.path.join("tests", "test.nnconfig")
        self.assertFalse(os.path.isfile(fullpath_new))
        config.save(fullpath_new)
        self.assertTrue(os.path.isfile(fullpath_new))
        self.assertEqual(config.fullpath, fullpath_new)
        if os.path.isfile(config.fullpath):
            os.remove(config.fullpath)

    def test_get_unsupported_products(self):
        filepath = os.path.join("tests", "configs", ".nnconfig_unsupported")
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
