# -*- coding: utf-8 -*-
from unittest.mock import Mock
from bg import BGEdge, BGVertex, Multicolor
from bg.kbreak import KBreak

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

import unittest


class KBreakTestCase(unittest.TestCase):
    def test_initialization_incorrect_argument_number(self):
        # required
        # initial set of edges in terms of pairs of vertices
        # desired set of edges in terms of pairs of vertices
        # a multicolor to perform such operation on
        mock_vertex = Mock(spec=BGVertex)
        mock_multicolor = Mock(spec=Multicolor)
        with self.assertRaises(ValueError):
            KBreak(start_edges=[(mock_vertex, ), (mock_vertex, mock_vertex)],
                   result_edges=[(mock_vertex, mock_vertex), (mock_vertex, mock_vertex)],
                   multicolor=mock_multicolor)
        with self.assertRaises(ValueError):
            KBreak(start_edges=[(mock_vertex, mock_vertex), (mock_vertex, mock_vertex)],
                   result_edges=[(mock_vertex, ), (mock_vertex, mock_vertex)],
                   multicolor=mock_multicolor)
        with self.assertRaises(ValueError):
            KBreak(start_edges=[(mock_vertex, mock_vertex), (mock_vertex, )],
                   result_edges=[(mock_vertex, ), (mock_vertex, mock_vertex)],
                   multicolor=mock_multicolor)

if __name__ == '__main__':
    unittest.main()
