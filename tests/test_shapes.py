import unittest
from pathlib import Path
from nextnanopy.shapes import GdsPolygonsRaw, units_factor, validate_unit
import numpy as np

np_equal = np.testing.assert_almost_equal

folder = Path('tests') / 'gds'


class TestShapes(unittest.TestCase):
    def test_unit(self):
        self.assertEqual(units_factor['nm'], 1e-9)
        self.assertEqual(units_factor['um'], 1e-6)
        self.assertEqual(units_factor['mm'], 1e-3)
        self.assertEqual(units_factor['m'], 1)
        self.assertEqual(units_factor['si'], 1)
        self.assertRaises(KeyError, validate_unit, 'none')
        self.assertTrue(validate_unit('NM'))

    def test_example0(self):
        fullpath = folder / "example0.gds"
        gpols = GdsPolygonsRaw(fullpath, unit='nm')
        self.assertEqual(gpols.fullpath, fullpath)
        np_equal(gpols.labels, [0])
        self.assertEqual(gpols.unit, 'nm')
        self.assertEqual(gpols.nb_polygons, 1)
        np_equal(gpols.xy[0][0], np.array([-500, -500, 500, 500]))
        np_equal(gpols.xy[0][1], np.array([-500, 500, 500, -500]))

        gpols.unit = 'm'
        self.assertEqual(gpols.unit, 'm')
        self.assertEqual(gpols.nb_polygons, 1)
        np_equal(gpols.xy[0][0], np.array([-500, -500, 500, 500]) * 1e-9)
        np_equal(gpols.xy[0][1], np.array([-500, 500, 500, -500]) * 1e-9)

        gpols.labels = [2]
        np_equal(gpols.labels, [2])

        gpols.labels = ['2']
        self.assertEqual(gpols.labels, ['2'])

    def test_example1(self):
        fullpath = folder / "example1.gds"
        gpols = GdsPolygonsRaw(fullpath, unit='nm')
        np_equal(gpols.labels, [0, 1, 2, 3])
        self.assertEqual(gpols.nb_polygons, 4)
        np_equal(gpols.xy[0][0], np.array([1500., 1500., 1975., 1975., 2025., 2025., 2500., 2500.]))

    def test_example2(self):
        fullpath = folder / "example2.gds"
        gpols = GdsPolygonsRaw(fullpath, unit='nm')
        np_equal(gpols.labels, [0, 1])
        self.assertEqual(gpols.nb_polygons, 2)


if __name__ == '__main__':
    unittest.main()
