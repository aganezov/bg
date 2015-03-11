# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"


class GRIMMReader(object):
    @staticmethod
    def is_genome_declaration_string(data_string):
        data_string = data_string.strip()
        return data_string.startswith(">") and len(data_string) > 1

    @staticmethod
    def parse_genome_declaration_string(data_string):
        data_string = data_string.strip()
        return data_string[1:]

    @staticmethod
    def parse_data_string(data_string):
        data_string = data_string.strip()
        linear_terminator_index = data_string.index("$") if "$" in data_string else -1
        circular_terminator_index = data_string.index("@") if "@" in data_string else -1
        if linear_terminator_index < 0 and circular_terminator_index < 0:
            raise ValueError("Invalid data string. No chromosome termination sign (+|-_ found.")
        if linear_terminator_index == 0 or circular_terminator_index == 0:
            raise ValueError("Invalid data string. No data found before chromosome was terminated.")
        if linear_terminator_index < 0 or 0 < circular_terminator_index < linear_terminator_index:
            chr_type = "@"
            terminator_index = circular_terminator_index
        else:
            chr_type = "$"
            terminator_index = linear_terminator_index
        data = data_string[:terminator_index].strip()
        split_data = data.split()
        blocks = []
        for block in split_data:
            cut_index = 1 if block.startswith("-") or block.startswith("+") else 0
            blocks.append(("-" if block.startswith("-") else "+", block[cut_index:]))
        return chr_type, blocks

    @staticmethod
    def __assign_vertex_pair(block):
        sign, name = block
        tail, head = name + "t", name + "h"
        return (tail, head) if sign == "+" else (head, tail)

    @staticmethod
    def get_edges_from_parsed_data(parsed_data):
        chr_type, blocks = parsed_data
        vertices = []
        for block in blocks:
            v1, v2 = GRIMMReader.__assign_vertex_pair(block)
            vertices.append(v1)
            vertices.append(v2)
        if chr_type == "@":
            vertex = vertices.pop()
            vertices.insert(0, vertex)
        else:
            infty_vertex1, infty_vertex2 = vertices[0] + "__infinity", vertices[-1] + "__infinity"
            vertices.insert(0, infty_vertex1)
            vertices.append(infty_vertex2)
        return [(v1, v2) for v1, v2 in zip(vertices[::2], vertices[1::2])]