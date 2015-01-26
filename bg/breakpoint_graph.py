# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"
from networkx import MultiGraph


class BreakpointGraph(object):
    def __init__(self):
        self.bg = MultiGraph()