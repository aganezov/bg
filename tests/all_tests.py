# -*- coding: utf-8 -*-
import glob
import os

__author__ = "aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "development"

import unittest
from teamcity import is_running_under_teamcity
from teamcity.unittestpy import TeamcityTestRunner
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from bg import version

if __name__ == '__main__':
    all_tests = unittest.TestLoader().discover('./', pattern='test_*.py')
    if is_running_under_teamcity():
        runner = TeamcityTestRunner()
        print("###teamcity[setParameter name='env.FullVersion' value='{version}']".format(version=version))
    else:
        runner = unittest.TextTestRunner()
    runner.run(all_tests)
