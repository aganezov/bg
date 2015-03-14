# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"

version = "1.0.0"

__all__ = ["breakpoint_graph",
           "vertex",
           "multicolor",
           "edge",
           "bg_io"]

from bg.breakpoint_graph import BreakpointGraph
from bg.vertex import BGVertex
from bg.edge import BGEdge
from bg.multicolor import Multicolor
from bg.bg_io import GRIMMReader