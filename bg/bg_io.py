# -*- coding: utf-8 -*-
from copy import deepcopy

from bg import BreakpointGraph, Multicolor, BGEdge
from bg.genome import BGGenome
from bg.utils import add_to_dict_with_path
from bg.vertices import BlockVertex, TaggedVertex, TaggedBlockVertex, TaggedInfinityVertex, BGVertex

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"


class GRIMMReader(object):
    """ Class providing a staticmethod based implementation of reading GRIMM formatted data file-like object and obtain a :class:`bg.breakpoint_graph.BreakpointGraph` instance.

    There are no private methods implementations for all public methods so inheritance shall be performed with caution.
    For now GRIMM format is a bit simplified and straightened from the version provided at http://grimm.ucsd.edu/GRIMM/grimm_instr.html

    Supported GRIMM format:

    #) all strings are stripped from both sides for tabs, spaces, etc. Below when said "string", stripped string is assumed
    #) ``genome declaration`` is specified on a string that starts with ``>``

       #) ``genome name`` is everything, that follows ``>`` sign

    #) all input data before the next genome declaration (or EOF) will be attributed to this genome by its ``genome name``
    #) a data string (containing information about gene orders) is a string that is not a genome declaration, comment, empty string

        #) every new genomic fragments (chromosome/scaffold/contig/etc) must be specified on a new string
        #) every data string must contain a ``$`` (for linear case) or ``@`` (for circular case) gene order terminator, that indicates the end of current genomic fragment
        #) everything after the gene order terminator is ignored
        #) if no gene order before gene order terminator is specified an error would be raised
        #) gene order:
            #) gene order is a sequence of space separated block name strings with optional orientation declaration
            #) block can be described by a regular expression ``^((-|\+).+$)|([^-\+]+$)`` and viewed as follows:
                if the sign (``+`` or ``-``) is present as a first character, then it must be followed by a nonempty block name string
                if sign is not present, everything is assumed to be a block name, and ``+`` orientation is assigned to it automatically

    #) comment string starts with ``#`` sign and is ignored during data processing

    Main operations:

    *   :meth:`GRIMMReader.is_genome_declaration_string`: checks if supplied string after stripping corresponds to ``genome declaration``
    *   :meth:`GRIMMReader.is_comment_string`: checks if supplied string after stripping corresponds to comment and shall thus be ignored in data processing
    *   :meth:`GRIMMReader.parse_genome_declaration_string`: parses a string marked as ``genome declaration`` and returns a corresponding genome name
    *   :meth:`GRIMMReader.parse_data_string`: parses a string assumed to contain gene order data, retrieving information about fragment type, gene order, blocks names and their orientation
    *   :meth:`GRIMMReader.get_edges_from_parsed_data`: taking into account fragment type (circular|linear) and retrieved gene order information translates adjacencies between blocks into edges for addition to the :class:`bg.breakpoint_graph.BreakpointGraph`
    *   :meth:`GRIMMReader.get_breakpoint_graph`: taking a file-like object transforms supplied gene order data into the language of BreakpointGraph
    """

    COMMENT_DATA_STRING_SEPARATOR = "::"
    PATH_SEPARATOR_STRING = ":"

    @staticmethod
    def is_genome_declaration_string(data_string):
        """ Checks if supplied string after stripping corresponds to ``genome declaration``

        :param data_string: a string to check genome name declaration in
        :type data_string: ``str``
        :return: a flag indicating if supplied string corresponds to genome name declaration
        :rtype: ``Boolean``
        """
        data_string = data_string.strip()
        return data_string.startswith(">") and len(data_string) > 1

    @staticmethod
    def is_comment_string(data_string):
        """ Checks if supplied string after stripping corresponds to comment and shall thus be ignored in data processing

        :param data_string: a string to check if it is a pure comment string
        :type data_string: ``str``
        :return: a flag indicating if supplied string is a pure comment string
        :rtype: ``Boolean``
        """
        return data_string.strip().startswith("#")

    @staticmethod
    def parse_genome_declaration_string(data_string):
        """ Parses a string marked as ``genome declaration`` and returns a corresponding :class:`bg.genome.BGGenome`

        :param data_string: a string to retrieve genome name from
        :type data_string: ``str``
        :return: genome name from supplied genome declaration string
        :rtype: :class:`bg.genome.BGGenome`
        """
        data_string = data_string.strip()
        return BGGenome(data_string[1:])

    @staticmethod
    def parse_data_string(data_string):
        """ Parses a string assumed to contain gene order data, retrieving information about fragment type, gene order, blocks names and their orientation

        First checks if gene order termination signs are present.
        Selects the earliest one.
        Checks that information preceding is not empty and contains gene order.
        Generates results structure by retrieving information about fragment type, blocks names and orientations.

        **NOTE:** comment signs do not work in data strings. Rather use the fact that after first gene order termination sign everything is ignored for processing

        :param data_string: a string to retrieve gene order information from
        :type data_string: ``str``
        :return: (``$`` | ``@``, [(``+`` | ``-``, block_name),...]) formatted structure corresponding to gene order in supplied data string and containing fragments type
        :rtype: ``tuple(str, list((str, str), ...))``
        """
        data_string = data_string.strip()
        linear_terminator_index = data_string.index("$") if "$" in data_string else -1
        circular_terminator_index = data_string.index("@") if "@" in data_string else -1
        if linear_terminator_index < 0 and circular_terminator_index < 0:
            raise ValueError("Invalid data string. No chromosome termination sign ($|@) found.")
        if linear_terminator_index == 0 or circular_terminator_index == 0:
            raise ValueError("Invalid data string. No data found before chromosome was terminated.")
        if linear_terminator_index < 0 or 0 < circular_terminator_index < linear_terminator_index:
            ###############################################################################################
            #
            # we either encountered only a circular chromosome termination sign
            # or we have encountered it before we've encountered the circular chromosome termination sign first
            #
            ###############################################################################################
            chr_type = "@"
            terminator_index = circular_terminator_index
        else:
            chr_type = "$"
            terminator_index = linear_terminator_index
        ###############################################################################################
        #
        # everything after first fragment termination sign is omitted
        #
        ###############################################################################################
        data = data_string[:terminator_index].strip()
        ###############################################################################################
        #
        # genomic blocks are separated between each other by the space character
        #
        ###############################################################################################
        split_data = data.split()
        blocks = []
        for block in split_data:
            ###############################################################################################
            #
            # since positively oriented blocks can be denoted both as "+block" as well as "block"
            # we need to figure out where "block" name starts
            #
            ###############################################################################################
            cut_index = 1 if block.startswith("-") or block.startswith("+") else 0
            if cut_index == 1 and len(block) == 1:
                ###############################################################################################
                #
                # block can not be empty
                # from this one can derive the fact, that names "+" and "-" for blocks are forbidden
                #
                ###############################################################################################
                raise ValueError("Empty block name definition")
            blocks.append(("-" if block.startswith("-") else "+", block[cut_index:]))
        return chr_type, blocks

    @staticmethod
    def __assign_vertex_pair(block):
        """ Assigns usual BreakpointGraph type vertices to supplied block.

        Vertices are labeled as "block_name" + "h" and "block_name" + "t" according to blocks orientation.

        :param block: information about a genomic block to create a pair of vertices for in a format of ( ``+`` | ``-``, block_name)
        :type block: ``(str, str)``
        :return: a pair of vertices labeled according to supplied blocks name (respecting blocks orientation)
        :rtype: ``(str, str)``
        """
        sign, name = block
        root_name, *data = name.split(BlockVertex.NAME_SEPARATOR)
        tags = [entry.split(TaggedVertex.TAG_SEPARATOR) for entry in data]
        for tag_entry in tags:
            if len(tag_entry) == 1:
                tag_entry.append(None)
            elif len(tag_entry) > 2:
                tag_entry[1:] = [TaggedVertex.TAG_SEPARATOR.join(tag_entry[1:])]
        tail, head = root_name + "t", root_name + "h"
        tail, head = TaggedBlockVertex(tail), TaggedBlockVertex(head)
        tail.mate_vertex = head
        head.mate_vertex = tail
        for tag, value in tags:
            head.add_tag(tag, value)
            tail.add_tag(tag, value)
        return (tail, head) if sign == "+" else (head, tail)

    @staticmethod
    def get_edges_from_parsed_data(parsed_data):
        """ Taking into account fragment type (circular|linear) and retrieved gene order information translates adjacencies between blocks into edges for addition to the :class:`bg.breakpoint_graph.BreakpointGraph`

        In case supplied fragment is linear (``$``) special artificial vertices (with ``__infinity`` suffix) are introduced to denote fragment extremities

        :param parsed_data: (``$`` | ``@``, [(``+`` | ``-``, block_name),...]) formatted data about fragment type and ordered list of oriented blocks
        :type parsed_data: ``tuple(str, list((str, str), ...))``
        :return: a list of vertices pairs that would correspond to edges in :class:`bg.breakpoint_graph.BreakpointGraph`
        :rtype: ``list((str, str), ...)``
        """
        chr_type, blocks = parsed_data
        vertices = []
        for block in blocks:
            ###############################################################################################
            #
            # each block is represented as a pair of vertices (that correspond to block extremities)
            #
            ###############################################################################################
            v1, v2 = GRIMMReader.__assign_vertex_pair(block)
            vertices.append(v1)
            vertices.append(v2)
        if chr_type == "@":
            ###############################################################################################
            #
            # if we parse a circular genomic fragment we must introduce an additional pair of vertices (edge)
            # that would connect two outer most vertices in the vertex list, thus connecting fragment extremities
            #
            ###############################################################################################
            vertex = vertices.pop()
            vertices.insert(0, vertex)
        elif chr_type == "$":
            ###############################################################################################
            #
            # if we parse linear genomic fragment, we introduce two artificial (infinity) vertices
            # that correspond to fragments ends, and introduce edges between them and respective outermost block vertices
            #
            # if outermost vertices at this moment are repeat vertices, the outermost pair shall be discarded and the innermost
            # vertex info shall be utilized in the infinity vertex, that is introduced for the fragment extremity
            #
            ###############################################################################################
            if vertices[0].is_repeat_vertex:
                left_iv_tags = sorted([(tag, value) if tag != "repeat" else (tag, BGVertex.get_vertex_name_root(vertices[1].name))
                                       for tag, value in vertices[1].tags])
                left_iv_root_name = BGVertex.get_vertex_name_root(vertices[2].name)
                vertices = vertices[2:]
            else:
                left_iv_tags = []
                left_iv_root_name = vertices[0].name
            if vertices[-1].is_repeat_vertex:
                right_iv_tags = sorted(
                        [(tag, value) if tag != "repeat" else (tag, BGVertex.get_vertex_name_root(vertices[-2].name))
                         for tag, value in vertices[-2].tags])
                right_iv_root_name = BGVertex.get_vertex_name_root(vertices[-3].name)
                vertices = vertices[:-2]
            else:
                right_iv_tags = []
                right_iv_root_name = BGVertex.get_vertex_name_root(vertices[-1].name)
            left_iv, right_iv = TaggedInfinityVertex(left_iv_root_name), TaggedInfinityVertex(right_iv_root_name)
            left_iv.tags = left_iv_tags
            right_iv.tags = right_iv_tags
            vertices.insert(0, left_iv)
            vertices.append(right_iv)
        return [(v1, v2) for v1, v2 in zip(vertices[::2], vertices[1::2])]

    @staticmethod
    def get_breakpoint_graph(stream, merge_edges=True):
        """ Taking a file-like object transforms supplied gene order data into the language of

        :param merge_edges: a flag that indicates if parallel edges in produced breakpoint graph shall be merged or not
        :type merge_edges: ``bool``
        :param stream: any iterable object where each iteration produces a ``str`` object
        :type stream: ``iterable`` ver ``str``
        :return: an instance of a BreakpointGraph that contains information about adjacencies in genome specified in GRIMM formatted input
        :rtype: :class:`bg.breakpoint_graph.BreakpointGraph`
        """
        result = BreakpointGraph()
        current_genome = None
        fragment_data = {}
        for line in stream:
            line = line.strip()
            if len(line) == 0:
                ###############################################################################################
                #
                # empty lines are omitted
                #
                ###############################################################################################
                continue
            if GRIMMReader.is_genome_declaration_string(data_string=line):
                ###############################################################################################
                #
                # is we have a genome declaration, we must update current genome
                # all following gene order data (before EOF or next genome declaration) will be attributed to current genome
                #
                ###############################################################################################
                current_genome = GRIMMReader.parse_genome_declaration_string(data_string=line)
                fragment_data = {}
            elif GRIMMReader.is_comment_string(data_string=line):
                if GRIMMReader.is_comment_data_string(string=line):
                    path, (key, value) = GRIMMReader.parse_comment_data_string(comment_data_string=line)
                    if len(path) > 0 and path[0] == "fragment":
                        add_to_dict_with_path(destination_dict=fragment_data, key=key, value=value, path=path)
                else:
                    continue
            elif current_genome is not None:
                ###############################################################################################
                #
                # gene order information that is specified before the first genome is specified can not be attributed to anything
                # and thus omitted
                #
                ###############################################################################################
                parsed_data = GRIMMReader.parse_data_string(data_string=line)
                edges = GRIMMReader.get_edges_from_parsed_data(parsed_data=parsed_data)
                for v1, v2 in edges:
                    edge_specific_data = {
                        "fragment": {
                            "forward_orientation": (v1, v2)
                        }
                    }
                    edge = BGEdge(vertex1=v1, vertex2=v2, multicolor=Multicolor(current_genome), data=deepcopy(fragment_data))
                    edge.update_data(source=edge_specific_data)
                    result.add_bgedge(bgedge=edge,
                                      merge=merge_edges)
        return result

    @classmethod
    def is_comment_data_string(cls, string):
        s = string.strip()
        comment_string = cls.is_comment_string(data_string=s)
        s = s[1:]  # removing # from beginning
        split_result = s.split(cls.COMMENT_DATA_STRING_SEPARATOR)
        if len(split_result) < 2:
            return False
        specification, *_ = split_result
        return comment_string & ("data" == specification.strip())

    @classmethod
    def parse_comment_data_string(cls, comment_data_string):
        _, *entries = map(lambda string: string.strip(), comment_data_string.split(cls.COMMENT_DATA_STRING_SEPARATOR))
        *path, key_value_entry = map(lambda string: string.strip(), entries[0].split(cls.PATH_SEPARATOR_STRING))
        key_value_entry_split = list(map(lambda string: string.strip(), key_value_entry.split("=")))
        if len(key_value_entry_split) < 2:
            key = ""
            value = ""
        else:
            key, value = key_value_entry_split
        return path, (key, value)


class GRIMMWriter(object):
    @staticmethod
    def get_blocks_in_grimm_from_breakpoint_graph(bg):
        """
        :param bg: a breakpoint graph, that contians all the information
        :type bg: ``bg.breakpoint_graph.BreakpointGraph``
        :return: list of strings, which represent genomes present in breakpoint graph as orders of blocks and is compatible with GRIMM format
        """
        result = []
        genomes = bg.get_overall_set_of_colors()
        for genome in genomes:
            genome_graph = bg.get_genome_graph(color=genome)
            genome_blocks_orders = genome_graph.get_blocks_order()
            blocks_orders = genome_blocks_orders[genome]
            if len(blocks_orders) > 0:
                result.append(">{genome_name}".format(genome_name=genome.name))
            for chr_type, blocks_order in blocks_orders:
                string = " ".join(value if sign == "+" else sign + value for sign, value in blocks_order)
                string += " {chr_type}".format(chr_type=chr_type)
                result.append(string)
        return result

    @classmethod
    def print_genomes_as_grimm_blocks_orders(cls, bg, file_name):
        with open(file_name, "wt") as destination:
            for grimm_string in cls.get_blocks_in_grimm_from_breakpoint_graph(bg=bg):
                print(grimm_string, file=destination)

    @staticmethod
    def get_fragments_in_grimm_from_breakpoint_graph(bg):
        result = []
        genomes = bg.get_overall_set_of_colors()
        for genome in genomes:
            genome_graph = bg.get_genome_graph(color=genome)
            fragments_orders = genome_graph.get_fragments_orders()
            fragments_orders = fragments_orders[genome]
            if len(fragments_orders) > 0 and any(map(lambda entry: len(entry[1]) > 0, fragments_orders)):
                result.append(">{genome_name}".format(genome_name=genome.name))
            for chr_type, fragments_order in fragments_orders:
                string = " ".join(value if sign == "+" else (sign + value) for sign, value in fragments_order)
                string += " {chr_type}".format(chr_type=chr_type)
                result.append(string)
        return result
