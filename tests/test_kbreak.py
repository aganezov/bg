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
        # even number of BGEdges is expected
        # two at least
        mock_bgedge = Mock(spec=BGEdge)
        with self.assertRaises(TypeError):
            KBreak()
        with self.assertRaises(TypeError):
            KBreak(mock_bgedge)
        with self.assertRaises(ValueError):
            KBreak(mock_bgedge, mock_bgedge, mock_bgedge)

    def test_initialization_incorrect_multicolor(self):
        mock_bgedge1 = Mock(spec=BGEdge)
        mock_bgedge1.multicolor = Multicolor("green")
        mock_bgedge2 = Mock(spec=BGEdge)
        mock_bgedge2.multicolor = Multicolor("black")
        # multicolors of bgedges to be changed have to equal to each other
        with self.assertRaises(ValueError):
            KBreak(mock_bgedge1, mock_bgedge2)

    def test_initialization(self):
        m = Multicolor("green")
        mock_bgedge1 = Mock(spec=BGEdge)
        mock_bgedge2 = Mock(spec=BGEdge)
        mock_bgedge3 = Mock(spec=BGEdge)
        mock_bgedge4 = Mock(spec=BGEdge)
        mock_vertex1 = Mock(spec=BGVertex)
        mock_vertex1.name = "v1"
        mock_vertex2 = Mock(spec=BGVertex)
        mock_vertex2.name = "v2"
        mock_vertex3 = Mock(spec=BGVertex)
        mock_vertex3.name = "v3"
        mock_vertex4 = Mock(spec=BGVertex)
        mock_vertex4.name = "v4"
        mock_bgedge1.vertex1, mock_bgedge1.vertex2 = mock_vertex1, mock_vertex2
        mock_bgedge2.vertex1, mock_bgedge2.vertex2 = mock_vertex2, mock_vertex3
        mock_bgedge3.vertex1, mock_bgedge3.vertex2 = mock_vertex3, mock_vertex4
        mock_bgedge4.vertex1, mock_bgedge4.vertex2 = mock_vertex4, mock_vertex1
        mock_bgedge1.multicolor = m
        mock_bgedge2.multicolor = m
        mock_bgedge3.multicolor = m
        mock_bgedge4.multicolor = m
        kbreak = KBreak(mock_bgedge1, mock_bgedge2, mock_bgedge3, mock_bgedge4)
        self.assertEqual(len(kbreak.edges) % 2, 0)
        self.assertEqual(len(kbreak.edges), 4)
        res_first_vertices = [edge.vertex1 for edge in kbreak.edges]
        ref_first_vertices = [mock_vertex1, mock_vertex2, mock_vertex3, mock_vertex4]
        self.assertListEqual(res_first_vertices, ref_first_vertices)
        res_second_vertices = [edge.vertex2 for edge in kbreak.edges]
        ref_second_vertices = [mock_vertex2, mock_vertex3, mock_vertex4, mock_vertex1]
        self.assertListEqual(res_second_vertices, ref_second_vertices)


if __name__ == '__main__':
    unittest.main()
