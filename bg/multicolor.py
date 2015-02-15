# -*- coding: utf-8 -*-
from collections import Counter

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"


class Multicolor(object):
    def __init__(self, *args):
        self.multicolors = Counter(arg for arg in args)

    def update(self, *args):
        self.multicolors = self.multicolors + Counter(arg for arg in args)

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
            to_delete = multicolor.multicolors
        else:
            to_delete = Counter(color for color in multicolor)
        self.multicolors = self.multicolors - to_delete

    @staticmethod
    def __merge(*multicolors):
        result = Multicolor()
        for multicolor in multicolors:
            result.multicolors = result.multicolors + multicolor.multicolors
        return result

    @staticmethod
    def __left_merge(multicolor1, multicolor2):
        multicolor1.multicolors = multicolor1.multicolors + multicolor2.multicolors
        return multicolor1

    @staticmethod
    def similarity_score(multicolor1, multicolor2):
        result = 0
        for key, value in multicolor1.multicolors.items():
            if key in multicolor2.multicolors:
                result += min(value, multicolor2.multicolors[key])
        return result

    @staticmethod
    def split_colors(multicolor, guidance=None):
        if guidance is None:
            guidance = [(color, ) for color in multicolor.colors]
        guidance = sorted([set(subset) for subset in guidance], key=lambda subset: len(subset), reverse=True)
        first_run_result = []
        second_run_result = []
        colors = multicolor.colors
        for color_set in guidance:
            if color_set.issubset(colors):
                first_run_result.append(color_set)
                colors -= color_set
        for color_set in guidance:
            if len(color_set.intersection(colors)) > 0:
                second_run_result.append(color_set.intersection(colors))
                colors -= color_set.intersection(colors)
        appendix = colors
        preliminary_result = first_run_result + second_run_result + ([appendix] if len(appendix) > 0 else [])
        result = []
        for color_set in preliminary_result:
            colors = []
            for color in color_set:
                colors.extend([color for _ in range(multicolor.multicolors[color])])
            result.append(Multicolor(*colors))
        return result

    def __sub__(self, other):
        if not isinstance(other, Multicolor):
            raise TypeError
        result = Multicolor(*(color for color in self.multicolors.elements()))
        result.__delete(other)
        return result

    def __isub__(self, other):
        if not isinstance(other, Multicolor):
            raise TypeError
        self.multicolors = self.multicolors - other.multicolors
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
        return self.multicolors == other.multicolors

    def __lt__(self, other):
        if not isinstance(other, Multicolor):
            return False
        self_keys = set(self.multicolors.keys())
        other_keys = set(other.multicolors.keys())
        return any(self.multicolors[key] < other.multicolors[key] for key in self_keys) and self_keys <= other_keys

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    @property
    def colors(self):
        return set(self.multicolors.keys())