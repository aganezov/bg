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


def get_from_dict_with_path(source_dict, key, path=None, default=None):
    current_level = source_dict
    if path is not None and len(path) > 0:
        for entry in path:
            if not isinstance(current_level, collections.Mapping) or entry not in current_level:
                return default
            current_level = current_level[entry]
    if not isinstance(current_level, collections.Mapping):
        return default
    return current_level.get(key, default)


def merge_fragment_edge_data(fragment_data_1, fragment_data_2):
    result = {"name": [fragment_data_1["name"] if fragment_data_1 is not None else None,
                       fragment_data_2["name"] if fragment_data_2 is not None else None],
              "forward_orientation": [fragment_data_1["forward_orientation"] if fragment_data_1 is not None else None,
                                      fragment_data_2["forward_orientation"] if fragment_data_2 is not None else None]}
    return result
