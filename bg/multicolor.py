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
        return Multicolor.__left_merge(multicolor1, multicolor2)

    @staticmethod
    def merge(*multicolors):
        return Multicolor.__merge(*multicolors)

    def delete(self, multicolor):
        self.__delete(multicolor)

    def __delete(self, multicolor):
        if isinstance(multicolor, Multicolor):
            to_delete = multicolor.colors
        else:
            to_delete = set(multicolor)
        self.colors = self.colors - to_delete

    @staticmethod
    def __merge(*multicolors):
        return Multicolor(*{color for multicolor in multicolors for color in multicolor.colors})

    @staticmethod
    def __left_merge(multicolor1, multicolor2):
        multicolor1.colors.update(multicolor2.colors)
        return multicolor1

    def __sub__(self, other):
        if not isinstance(other, Multicolor):
            raise TypeError
        result = Multicolor(*self.colors)
        result.__delete(other)
        return result

    def __isub__(self, other):
        if not isinstance(other, Multicolor):
            raise TypeError
        self.colors = self.colors - other.colors
        return self

    def __add__(self, other):
        if not isinstance(other, Multicolor):
            raise TypeError
        return Multicolor.__merge(self, other)

    def __iadd__(self, other):
        if not isinstance(other, Multicolor):
            raise TypeError
        return Multicolor.__left_merge(self, other)

    def __eq__(self, other):
        if not isinstance(other, Multicolor):
            return False
        return self.colors == other.colors