# -*- coding: utf-8 -*-
__author__ = "aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"


class BGGenome(object):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, BGGenome):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    @property
    def json_id(self):
        return hash(self)