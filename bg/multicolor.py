# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"


class Multicolor(object):
    def __init__(self, *args):
        self.colors = set(args)

    def update(self, *args):
        self.colors.update(args)

    def __eq__(self, other):
        if not isinstance(other, Multicolor):
            return False
        return self.colors == other.colors