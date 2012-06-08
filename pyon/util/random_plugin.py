"""
This plugin randomizes the order of tests within a unittest.TestCase class
"""
__test__ = False

import logging
import os
import sys
from nose.plugins import Plugin
from nose import loader
from inspect import isfunction, ismethod
from nose.case import FunctionTestCase, MethodTestCase
from nose.failure import Failure
from nose.config import Config
from nose.importer import Importer, add_path, remove_path
from nose.selector import defaultSelector, TestAddress
from nose.util import isclass, isgenerator, \
    transplant_func, transplant_class
from nose.suite import ContextSuiteFactory, ContextList, LazySuite
import random
import unittest
import collections

log = logging.getLogger(__name__)

class MyLoader(loader.TestLoader):
    def loadTestsFromTestCase(self, testCaseClass):
        tsts = super(MyLoader, self).loadTestsFromTestCase(testCaseClass)
        print >>sys.stderr, "I AM", tsts
        return tsts

class Randomize(Plugin):
    """
    Randomize the order of the tests within a unittest.TestCase class
    """
    name = 'randomize'
    # Generate a seed for deterministic behaviour
    # Could use getstate  and setstate, but that would involve
    # pickling the state and storing it somewhere. too lazy.
    seed = random.getrandbits(32)

    def options(self, parser, env):
        """Register commandline options.
        """
        Plugin.options(self, parser, env)
        parser.add_option('--randomize', action='store_true', dest='randomize',
                          help="Randomize the order of the tests within a unittest.TestCase class")
        parser.add_option('--seed', action='store', dest='seed', default=None, type = long,
                          help="Initialize the seed for deterministic behavior in reproducing failed tests")

    def configure(self, options, conf):
        """
        Configure plugin.
        """
        Plugin.configure(self, options, conf)
        if options.randomize:
            self.enabled = True
            if options.seed is not None:
                self.seed = options.seed
            random.seed(self.seed)
            print("Using %d as seed" % (self.seed,))



    def prepareTestLoader(self, loader):
        return MyLoader()

    def XXXprepareTest(self, test):

        def goof(o):
            print >>sys.stderr, o.__class__
            lst = []
            for x in o:
                if isinstance(x, collections.Iterable):
                    lst.append(goof(x))
                else:
                    lst.append(x)
            return lst


        tests = goof(test._tests)
        test._tests = tests
        return test

    def XXloadTestsFromTestCase(self, cls):
        """
        Return tests in this test case class. Return None if you are not able to load any tests, or an iterable if you are. May be a generator.
        """
        #tl = super(Randomize, self).loadTestsFromTestCase(cls)
        #tl = Plugin.loadTestsFromTestCase(self, cls)
        l = loader.TestLoader()
        tl = l.loadTestsFromTestCase(cls)

        print >>sys.stderr, "WHAT", cls
        print >>sys.stderr, dir(self)
        print >>sys.stderr, "HELLO I AM", tl
        #if hasattr(cls, 'test_start_stop'):
        #    return [getattr(cls, 'test_start_stop')]
        return tl

    def NOmakeTest(self, obj, parent=None):
        
        """Given a test object and its parent, return a test case
        or test suite.
        """
        ldr = loader.TestLoader()
        if isinstance(obj, unittest.TestCase):
            return obj
        elif isclass(obj):
            if parent and obj.__module__ != parent.__name__:
                obj = transplant_class(obj, parent.__name__)
            if issubclass(obj, unittest.TestCase):
                # Randomize the order of the tests in the TestCase
                return self.Randomized_loadTestsFromTestCase(obj)
            else:
                return ldr.loadTestsFromTestClass(obj)
        elif ismethod(obj):
            if parent is None:
                parent = obj.__class__
            if issubclass(parent, unittest.TestCase):
                return parent(obj.__name__)
            else:
                if isgenerator(obj):
                    return ldr.loadTestsFromGeneratorMethod(obj, parent)
                else:
                    return MethodTestCase(obj)
        elif isfunction(obj):
            if parent and obj.__module__ != parent.__name__:
                obj = transplant_func(obj, parent.__name__)
            if isgenerator(obj):
                return ldr.loadTestsFromGenerator(obj, parent)
            else:
                return FunctionTestCase(obj)
        else:
            return Failure(TypeError,
                           "Can't make a test from %s" % obj)

    def Randomized_loadTestsFromTestCase(self, testCaseClass):
        l = loader.TestLoader()
        tmp = l.loadTestsFromTestCase(testCaseClass)
        randomized_tests = []
        for t in tmp._tests:
            randomized_tests.append(t)
        random.shuffle(randomized_tests)
        tmp._tests = (t for t in randomized_tests)
        return tmp

