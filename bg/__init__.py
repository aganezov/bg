# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

version = "1.0.0a"

__all__ = ["breakpoint_graph",
           "vertex",
           "multicolor",
           "edge"]

from bg.breakpoint_graph import BreakpointGraph
from bg.vertex import BGVertex
from bg.edge import BGEdge
from bg.multicolor import Multicolor