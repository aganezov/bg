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
    for key, value in dict2.items():
        dict1_entry = dict1.get(key, {})
        if isinstance(value, collections.Mapping) and isinstance(dict1_entry, collections.Mapping):
            r = recursive_dict_update(dict1_entry, value)
            dict1[key] = r
        else:
            dict1[key] = dict2[key]
    return dict1


def add_to_dict_with_path(destination_dict, key, value, path=None):
    current_level = destination_dict
    if path is not None and len(path) > 0:
        for entry in path:
            if entry not in current_level or not isinstance(current_level[entry], dict):
                current_level[entry] = {}
            current_level = current_level[entry]
    if key != "" and value != "":
        current_level[key] = value
