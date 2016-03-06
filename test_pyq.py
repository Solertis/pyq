from pyq.astmatch import ASTMatchEngine

import unittest
import os.path
import ast


class TestASTMatchEngine(unittest.TestCase):
    def setUp(self):
        self.m = ASTMatchEngine()

    def filepath(self, filename):
        return os.path.join(os.path.dirname(__file__), 'testfiles', filename)

    def test_classes(self):
        matches = list(self.m.match('class', self.filepath('classes.py')))
        self.assertEqual(len(matches), 4)

        # check instances
        self.assertIsInstance(matches[0][0], ast.ClassDef)
        self.assertIsInstance(matches[1][0], ast.ClassDef)
        self.assertIsInstance(matches[2][0], ast.ClassDef)
        self.assertIsInstance(matches[3][0], ast.ClassDef)

        # check lines
        self.assertEqual(matches[0][1], 1)
        self.assertEqual(matches[1][1], 9)
        self.assertEqual(matches[2][1], 13)
        self.assertEqual(matches[3][1], 14)

    def test_classes_with_specific_method(self):
        matches1 = list(self.m.match('class:not(:has(def))',
                        self.filepath('classes.py')))

        matches2 = list(self.m.match('class:has(def[name=bar])',
                        self.filepath('classes.py')))

        matches3 = list(self.m.match('class:has(> def)',
                        self.filepath('classes.py')))

        self.assertEqual(len(matches1), 1)
        self.assertIsInstance(matches1[0][0], ast.ClassDef)

        self.assertEqual(len(matches2), 3)
        self.assertIsInstance(matches2[0][0], ast.ClassDef)
        self.assertIsInstance(matches2[1][0], ast.ClassDef)
        self.assertIsInstance(matches2[2][0], ast.ClassDef)

        self.assertEqual(len(matches3), 2)
        self.assertIsInstance(matches3[0][0], ast.ClassDef)
        self.assertIsInstance(matches3[1][0], ast.ClassDef)
        self.assertEqual(matches3[0][1], 1)
        self.assertEqual(matches3[1][1], 14)

    def test_methods(self):
        matches = list(self.m.match('class def', self.filepath('classes.py')))
        self.assertEqual(len(matches), 3)

        # check instances
        self.assertIsInstance(matches[0][0], ast.FunctionDef)
        self.assertIsInstance(matches[1][0], ast.FunctionDef)
        self.assertIsInstance(matches[2][0], ast.FunctionDef)

        # check lines
        self.assertEqual(matches[0][1], 2)
        self.assertEqual(matches[1][1], 5)
        self.assertEqual(matches[2][1], 15)

    def test_methods_by_name(self):
        matches1 = list(self.m.match('class def[name=baz]',
                        self.filepath('classes.py')))
        matches2 = list(self.m.match('class def[name!=baz]',
                        self.filepath('classes.py')))

        self.assertEqual(len(matches1), 1)
        self.assertEqual(matches1[0][1], 5)

        self.assertEqual(len(matches2), 2)
        self.assertEqual(matches2[0][1], 2)
        self.assertEqual(matches2[1][1], 15)

    def test_import(self):
        matches = list(self.m.match('import', self.filepath('imports.py')))

        self.assertEqual(len(matches), 6)

        # check instances
        self.assertIsInstance(matches[0][0], ast.ImportFrom)
        self.assertIsInstance(matches[1][0], ast.ImportFrom)
        self.assertIsInstance(matches[2][0], ast.ImportFrom)
        self.assertIsInstance(matches[3][0], ast.ImportFrom)
        self.assertIsInstance(matches[4][0], ast.Import)
        self.assertIsInstance(matches[5][0], ast.Import)

    def test_import_from(self):
        matches = list(self.m.match('import[from=foo]',
                       self.filepath('imports.py')))

        self.assertEqual(len(matches), 2)

        # check instances
        self.assertIsInstance(matches[0][0], ast.ImportFrom)
        self.assertIsInstance(matches[1][0], ast.ImportFrom)

        # check lines
        self.assertEqual(matches[0][1], 1)
        self.assertEqual(matches[1][1], 2)

    def test_import_not_from(self):
        matches = list(self.m.match('import:not([from^=foo])',
                       self.filepath('imports.py')))

        self.assertEqual(len(matches), 3)

        # check instances
        self.assertIsInstance(matches[0][0], ast.ImportFrom)
        self.assertIsInstance(matches[1][0], ast.Import)
        self.assertIsInstance(matches[2][0], ast.Import)

    def test_import_name(self):
        matches = list(self.m.match('import[name=example2]',
                       self.filepath('imports.py')))

        self.assertEqual(len(matches), 1)

        matches = list(self.m.match('import[name=bar], import[name=bar2]',
                       self.filepath('imports.py')))

        self.assertEqual(len(matches), 2)

    def test_import_multiple(self):
        matches1 = list(self.m.match('import[name=xyz]',
                        self.filepath('imports.py')))

        matches2 = list(self.m.match('import[name=xyz][name=bar2]',
                        self.filepath('imports.py')))

        matches3 = list(self.m.match('import[name=foo.baz]',
                        self.filepath('imports.py')))

        matches4 = list(self.m.match('import[name^=foo]',
                        self.filepath('imports.py')))

        matches5 = list(self.m.match('import[from^=foo]',
                        self.filepath('imports.py')))

        self.assertEqual(len(matches1), 1)
        self.assertEqual(len(matches2), 1)
        self.assertEqual(len(matches3), 1)
        self.assertEqual(len(matches4), 1)
        self.assertEqual(len(matches5), 3)

    def test_import_special_attr(self):
        matches1 = list(self.m.match('import[full=foo.bar2]',
                        self.filepath('imports.py')))

        matches2 = list(self.m.match('import[full=foo.xyz]',
                        self.filepath('imports.py')))

        self.assertEqual(len(matches1), 1)
        self.assertEqual(len(matches2), 1)

    def test_match_id(self):
        matches = list(self.m.match('#foo,#bar', self.filepath('ids.py')))

        self.assertEqual(len(matches), 5)

    def test_assign(self):
        matches1 = list(self.m.match('assign', self.filepath('assign.py')))
        matches2 = list(self.m.match('assign#foo', self.filepath('assign.py')))
        matches3 = list(
            self.m.match('assign[name=bar]', self.filepath('assign.py')))
        matches4 = list(self.m.match('assign#b', self.filepath('assign.py')))
        matches5 = list(
            self.m.match('#abc,[name=abc]', self.filepath('assign.py')))

        self.assertEqual(len(matches1), 6)

        self.assertEqual(len(matches2), 1)
        self.assertEqual(matches2[0][1], 1)

        self.assertEqual(len(matches3), 1)
        self.assertEqual(matches3[0][1], 2)

        self.assertEqual(len(matches4), 1)
        self.assertEqual(matches4[0][1], 4)

        self.assertEqual(len(matches5), 1)
        self.assertEqual(matches5[0][1], 5)

    def test_calls(self):
        matches1 = list(
            self.m.match('[name=print]', self.filepath('calls.py')))
        matches2 = list(self.m.match('call#foo', self.filepath('calls.py')))
        matches3 = list(self.m.match('call', self.filepath('calls.py')))
        matches4 = list(self.m.match('[name=foo]', self.filepath('calls.py')))

        self.assertEqual(len(matches1), 1)
        self.assertEqual(len(matches2), 2)
        self.assertEqual(len(matches3), 5)
        self.assertEqual(len(matches4), 2)

    def test_call_arg_kwarg(self):
        matches1 = list(self.m.match('call[kwarg=a]',
                        self.filepath('calls.py')))
        matches2 = list(self.m.match('call[kwarg=x]',
                        self.filepath('calls.py')))
        matches3 = list(self.m.match('call[arg=bar]',
                        self.filepath('calls.py')))
        matches4 = list(self.m.match('[arg=bang]', self.filepath('calls.py')))

        self.assertEqual(len(matches1), 1)
        self.assertEqual(len(matches2), 2)
        self.assertEqual(len(matches3), 2)
        self.assertEqual(len(matches4), 2)

        self.assertIsInstance(matches1[0][0], ast.Call)
        self.assertIsInstance(matches2[0][0], ast.Call)
        self.assertIsInstance(matches2[1][0], ast.Call)
        self.assertIsInstance(matches3[0][0], ast.Call)
        self.assertIsInstance(matches3[1][0], ast.Call)
        self.assertIsInstance(matches4[0][0], ast.Call)

    def test_attrs(self):
        matches1 = list(self.m.match('#bang', self.filepath('attrs.py')))
        matches2 = list(self.m.match('attr#z', self.filepath('attrs.py')))
        matches3 = list(self.m.match('attr', self.filepath('attrs.py')))
        matches4 = list(self.m.match('#y', self.filepath('attrs.py')))

        self.assertEqual(len(matches1), 1)
        self.assertEqual(len(matches2), 1)
        self.assertEqual(len(matches3), 4)
        self.assertEqual(len(matches4), 1)

        self.assertEqual(matches3[0][0].attr, 'bar')
        self.assertEqual(matches3[1][0].attr, 'bang')
        self.assertEqual(matches3[2][0].attr, 'y')
        self.assertEqual(matches3[3][0].attr, 'z')

    def test_pseudo_extends(self):
        matches1 = list(self.m.match(':extends(#object)',
                        self.filepath('classes.py')))

        matches2 = list(self.m.match(':extends()',
                        self.filepath('classes.py')))

        matches3 = list(self.m.match(':extends(#Unknown)',
                        self.filepath('classes.py')))

        matches4 = list(self.m.match(':extends(#object, #X)',
                        self.filepath('classes.py')))

        matches5 = list(self.m.match(':extends(#X):extends(#Y)',
                        self.filepath('classes.py')))

        matches6 = list(self.m.match(':extends(#foo)',
                        self.filepath('classes.py')))

        matches7 = list(self.m.match(':extends(attr#B)',
                        self.filepath('classes.py')))

        matches8 = list(self.m.match(':extends(#A):extends(attr#B)',
                        self.filepath('classes.py')))

        self.assertEqual(len(matches1), 3)
        self.assertEqual(len(matches2), 1)
        self.assertEqual(len(matches3), 0)
        self.assertEqual(len(matches4), 3)
        self.assertEqual(len(matches5), 1)
        self.assertEqual(len(matches6), 1)
        self.assertEqual(len(matches7), 1)
        self.assertEqual(len(matches8), 1)


unittest.main(failfast=True)
