# -*- coding: utf-8 -*-
import collections


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


def recursive_dict_update(dict1, dict2):
    for key, value in dict2.iteritems():
        if isinstance(value, collections.Mapping):
            r = recursive_dict_update(dict1.get(key, {}), value)
            dict1[key] = r
        else:
            dict1[key] = dict2[key]
    return dict1
