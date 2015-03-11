# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"


class GRIMMReader(object):

    @staticmethod
    def is_genome_declaration_string(data_string):
        data_string = data_string.strip()
        return data_string.startswith(">")