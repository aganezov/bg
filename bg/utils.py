# -*- coding: utf-8 -*-


def dicts_are_equal(dict1, dict2):
    if len(set(dict1.keys()).symmetric_difference(set(dict2.keys()))) > 0:
        return False
    result = True
    for key in dict1.keys():
        if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            result &= dicts_are_equal(dict1[key], dict2[key])
        else:
            result &= dict1[key] == dict2[key]
    return result
