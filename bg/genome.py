# -*- coding: utf-8 -*-
__author__ = "aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"


class BGGenome(object):
    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    @property
    def json_id(self):
        return hash(self)