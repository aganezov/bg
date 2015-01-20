# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"


class BGVertex(object):
    def __init__(self, name, info=None):
        self.name = name
        self.info = {}
        if info is None:
            info = {}
        self.info = info