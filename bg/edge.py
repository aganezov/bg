# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"


class BGEdge(object):
    def __init__(self, vertex1, vertex2, multicolor):
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.multicolor = multicolor