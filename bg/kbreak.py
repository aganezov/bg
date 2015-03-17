# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"


class KBreak(object):
    def __init__(self, edge1, edge2, *edges):
        self.edges = [edge1, edge2] + list(edges)
        if len(edges) % 2 != 0:
            raise ValueError("Even number of edges for a k-break is expected. Odd number ({cnt}) received."
                             "".format(cnt=len(self.edges)))
        multicolor = self.edges[0].multicolor
        for edge in self.edges[1:]:
            if edge.multicolor != multicolor:
                raise ValueError("All edged for a k-break are expected to have same multicolors.")