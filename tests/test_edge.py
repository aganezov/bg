# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

import unittest
from bg.edge import BGEdge


class BGEdgeTestCase(unittest.TestCase):
    def test_empty_initialization_incorrect(self):
        with self.assertRaises(TypeError):
            BGEdge()

if __name__ == '__main__':
    unittest.main()
