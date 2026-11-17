"""unittest adapter for plain test_* functions (the Foot IK tests were written for pytest)."""
import unittest


def load_functions(module):
    def load_tests(loader, tests, pattern):
        suite = unittest.TestSuite()
        for name in sorted(n for n in dir(module) if n.startswith("test_") and callable(getattr(module, n))):
            suite.addTest(unittest.FunctionTestCase(getattr(module, name), description=module.__name__ + "." + name))
        return suite
    return load_tests
