# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"


class Multicolor(object):
    def __init__(self, *args):
        self.colors = set(args)

    def update(self, *args):
        self.colors.update(args)

    @staticmethod
    def left_merge(multicolor1, multicolor2):
        multicolor1.colors.update(multicolor2.colors)
        return multicolor1

    def __eq__(self, other):
        if not isinstance(other, Multicolor):
            return False
        return self.colors == other.colors