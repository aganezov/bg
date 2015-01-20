# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

import unittest
from bg.vertex import BGVertex


class BGVertexTestCase(unittest.TestCase):
    def test_empty_initialization(self):
        with self.assertRaises(TypeError):
            BGVertex()


if __name__ == '__main__':
    unittest.main()
