# -*- coding: utf-8 -*-
from bg import BreakpointGraph, BGVertex, Multicolor

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"


class GRIMMReader(object):
    """ Class providing a staticmethod based implementation of reading GRIMM formatted data file-like object and obtain a :class:`BreakpointGraph` instance.

    There are no private methods implementations for all public methods so inheritance shall be performed with caution.
    For now GRIMM format is a bit simplified and straightened from the version provided at http://grimm.ucsd.edu/GRIMM/grimm_instr.html

    Supported GRIMM format:
    1) all strings are stripped from both sides for tabs, spaces, etc. Below when said "string", stripped string is assumed
    2) ``genome declaration`` is specified on a string that starts with ``>``
        2.1) ``genome name`` is everything, that follows ``>`` sign
    3) all input data before the next genome declaration (or EOF) will be attributed to this genome by its ``genome name``
    4) a data string (containing information about gene orders) is a string that is not a genome declaration, comment, empty string
        4.1) every new genomic fragments (chromosome/scaffold/contig/etc) must be specified on a new string
        4.2) every data string must contain a ``$`` (for linear case) or ``@`` (for circular case) gene order terminator, that indicates the end of current genomic fragment
        4.3) everything after the gene order terminator is ignored
        4.4) if no gene order before gene order terminator is specified an error would be raised
        4.5) gene order:
            4.5.1) gene order is a sequence of space separated block name strings with optional orientation declaration
            4.5.2) block can be described by a regular expression ``^((-|\+).+$)|([^-\+]+$)`` and viewed as follows:
                if the sign (``+`` or ``-``) is present as a first character, then it must be followed by a nonempty block name string
                if sign is not present, everything is assumed to be a block name, and ``+`` orientation is assigned to it automatically

    Main operations:

    *   :meth:`GRIMMReader.is_genome_declaration_string`: checks is supplied string after stripping corresponds to ``genome declaration``
    *   :meth:`GRIMMReader.parse_genome_declaration_string`: parses a string marked as ``genome declaration`` and returns a corresponding genome name
    *   :meth:`GRIMMReader.parse_data_string`: parses a string assumed to contain gene order data, retrieving information about fragment type, gene order, blocks names and their orientation
    *   :meth:`GRIMMReader.get_edges_from_parsed_data`: taking into account fragment type (circular|linear) and retrieved gene order information translates adjacencies between blocks into edges for addition to the :class:`BreakpointGraph`
    *   :meth:`GRIMMReader.get_breakpoint_graph`: taking a file-like object transforms supplied gene order data into the language of
    """
    @staticmethod
    def is_genome_declaration_string(data_string):
        data_string = data_string.strip()
        return data_string.startswith(">") and len(data_string) > 1

    @staticmethod
    def is_comment_string(data_string):
        return data_string.strip().startswith("#")

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
            raise ValueError("Invalid data string. No chromosome termination sign (+|-) found.")
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

    @staticmethod
    def get_breakpoint_graph(stream):
        result = BreakpointGraph()
        current_genome_name = None
        for line in stream:
            line = line.strip()
            if len(line) == 0:
                continue
            if GRIMMReader.is_genome_declaration_string(data_string=line):
                current_genome_name = GRIMMReader.parse_genome_declaration_string(data_string=line)
            elif GRIMMReader.is_comment_string(data_string=line):
                continue
            elif current_genome_name is not None:
                parsed_data = GRIMMReader.parse_data_string(data_string=line)
                edges = GRIMMReader.get_edges_from_parsed_data(parsed_data=parsed_data)
                for v1, v2 in edges:
                    result.add_edge(vertex1=BGVertex(v1), vertex2=BGVertex(v2),
                                    multicolor=Multicolor(current_genome_name))
        return result