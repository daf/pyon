#!/usr/bin/env python

"""
Nose plugin for objgraph.

@author Dave Foster <dfoster@asascience.com>
"""

import time

import nose
from nose.plugins.base import Plugin
import objgraph
from cStringIO import StringIO
import sys
import gc

class ObjGraph(Plugin):

    name    = 'objgraph'
    score   = 1
    enabled = False

    def options(self, parser, env):
        super(ObjGraph, self).options(parser, env)

    def configure(self, options, config):
        super(ObjGraph, self).configure(options, config)
        self.config = config
        self._growth = []

    def _cap_growth(self):
        ostd = sys.stdout
        sys.stdout = c = StringIO()

        objgraph.show_growth()
        sys.stdout = ostd

        return c.getvalue()

    def begin(self):
        self._cap_growth()      # initialize cap

    def _add_growth(self, test):
        self._growth.append((test.id(), self._cap_growth()))

    def addError(self, test, err, capt=None):
        self._add_growth(test)

    def addFailure(self, test, err, capt=None, tb_info=None):
        self._add_growth(test)

    def addSuccess(self, test, capt=None):
        self._add_growth(test)

    def report(self, stream):
        if not self.enabled:
            return

        for x in self._growth:
            stream.writeln("%s:\n%s\n\n" % (x[0], x[1]))

def main():
    nose.main(addplugins=[ObjGraph()])

if __name__ == '__main__':
    main()
