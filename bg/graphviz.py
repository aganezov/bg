# -*- coding: utf-8 -*-
from collections import defaultdict
from collections import deque

from enum import Enum
from ete3 import TreeNode

from bg.edge import BGEdge
from bg.genome import BGGenome
from bg.multicolor import Multicolor
from bg.utils import get_from_dict_with_path
from bg.vertices import BGVertex, InfinityVertex, TaggedInfinityVertex


def vertex_as_a_sting(vertex, separator=" "):
    result = ""
    if isinstance(vertex, BGVertex):
        orientation = "t" if vertex.is_tail_vertex else "h"
        result += vertex.block_name + orientation
        if vertex.is_tagged_vertex and len(vertex.tags) > 0:
            result += separator + separator.join(map(lambda entry: "(" + entry + ")", vertex.get_tags_as_list_of_strings()))
    else:
        result = str(vertex)
    return "{string}".format(string=result)


def vertex_as_html(vertex, separator=" "):
    result = ""
    if isinstance(vertex, BGVertex):
        if vertex.is_block_vertex:
            orientation = "t" if vertex.is_tail_vertex else "h"
            result += vertex.block_name + "<SUP>" + orientation + "</SUP>"
        if vertex.is_tagged_vertex and len(vertex.tags) > 0:
            result += separator + separator.join(map(lambda entry: "(" + entry + ")", vertex.get_tags_as_list_of_strings()))
    else:
        result = str(vertex)
    return "<" + result + ">"


class LabelFormat(Enum):
    plain = "plain"
    html = "html"


class Colors(Enum):
    black = "black"
    blue = "blue"
    red = "red"
    green = "green"
    orange = "orange"
    aquamarine = "aquamarine"
    bisque = "bisque"
    cyan = "cyan"
    gold = "gold"
    gray = "gray"
    # 10
    khaki = "khaki"
    magenta = "magenta"
    maroon = "maroon"
    pink = "pink"
    orchid = "orchid"
    sandybrown = "sandybrown"
    cadetblue = "cadetblue"
    dimgrey = "dimgrey"
    plum = "plum"
    wheat = "wheat"
    # 20


def ids_generator(start=1, step=1):
    while True:
        yield start
        start += step


class ColorSource(object):
    def __init__(self):
        self.color_to_dot_color = {}
        self.unused_colors = deque([
            Colors.black,
            Colors.blue,
            Colors.red,
            Colors.green,
            Colors.orange,
            Colors.aquamarine,
            Colors.bisque,
            Colors.cyan,
            Colors.gold,
            Colors.gray,
            Colors.khaki,
            Colors.magenta,
            Colors.maroon,
            Colors.pink,
            Colors.orchid,
            Colors.sandybrown,
            Colors.cadetblue,
            Colors.dimgrey,
            Colors.plum,
            Colors.wheat,

        ])

    def get_unused_color(self, entry):
        if entry not in self.color_to_dot_color:
            self.color_to_dot_color[entry] = self.unused_colors.popleft()
        return self.color_to_dot_color[entry]

    def get_color_as_string(self, entry):
        return self.get_unused_color(entry=entry).value


class ShapeProcessor(object):
    def __init__(self, pen_width=1, style="solid", color=Colors.black, color_source=None):
        self.style_attrib_template = "style=\"{style}\""
        self.color_attrib_template = "color=\"{color}\""
        self.color_source = color_source if color_source is not None else ColorSource()
        self.pen_width = pen_width
        self.style = style
        self.color = color
        self.pen_width_attrib_template = "penwidth=\"{pen_width}\""

    def get_pen_width(self, entry=None):
        return self.pen_width

    def get_style(self, entry=None):
        return "solid"

    def get_color_as_string(self, entry):
        return self.color_source.get_color_as_string(entry=entry)

    def get_attributes_string_list(self, entry):
        return [
            self.color_attrib_template.format(color=self.get_color_as_string(entry=entry)),
            self.style_attrib_template.format(style=self.get_style(entry=entry)),
            self.pen_width_attrib_template.format(pen_width=self.get_pen_width(entry=entry))
        ]


class TextProcessor(object):
    def __init__(self, color=Colors.black, size=12, font_name="Arial", color_source=None):
        self.color_source = color_source if color_source is not None else ColorSource()
        self.color = color
        self.text_size = size
        self.text_font_name = font_name

        self.color_attrib_template = "fontcolor=\"{color}\""
        self.size_attrib_template = "fontsize=\"{size}\""
        self.font_attrib_template = "fontname=\"{font}\""
        self.label_attrib_template = "label={label}"

    def get_text_font(self, entry=None):
        return self.text_font_name

    def get_text_size(self, entry=None):
        return self.text_size

    def get_text_color(self, entry=None):
        return self.color.value if self.color in Colors else str(self.color)

    def get_text(self, entry=None, label_format=LabelFormat.plain):
        if label_format == LabelFormat.html.value or label_format == LabelFormat.html:
            return "<>"
        return "\"\""

    def get_attributes_string_list(self, entry, label_format=LabelFormat.plain):
        return [self.label_attrib_template.format(label=self.get_text(entry=entry, label_format=label_format)),
                self.font_attrib_template.format(font=self.text_font_name),
                self.size_attrib_template.format(size=self.text_size),
                self.color_attrib_template.format(color=self.get_text_color(entry=entry))]


class VertexShapeProcessor(ShapeProcessor):
    def __init__(self, pen_width=1, style="solid", color=Colors.black, shape="oval", color_source=None):
        super(VertexShapeProcessor, self).__init__(pen_width=pen_width, style=style, color=color, color_source=color_source)
        self.shape_attrib_template = "shape=\"{shape}\""
        self.shape = shape

    def get_shape(self, entry=None):
        return self.shape

    def get_attributes_string_list(self, entry):
        return [self.shape_attrib_template.format(shape=self.get_shape(entry=entry)),
                self.pen_width_attrib_template.format(pen_width=self.get_pen_width(entry=entry)),
                self.style_attrib_template.format(style=self.get_style(entry=entry)),
                self.color_attrib_template.format(color=self.get_color_as_string(entry=entry))]


class BGVertexShapeProcessor(VertexShapeProcessor):
    def __init__(self, pen_width=1, style="solid", color=Colors.black, color_source=None,
                 regular_vertex_shape="oval", irregular_vertex_shape="point", non_bg_vertex_shape="oval"):
        super(BGVertexShapeProcessor, self).__init__(pen_width=pen_width, style=style, color=color, shape=non_bg_vertex_shape, color_source=color_source)
        self.regular_vertex_shape = regular_vertex_shape
        self.irregular_vertex_shape = irregular_vertex_shape

    def get_shape(self, entry=None):
        if isinstance(entry, BGVertex):
            return self.regular_vertex_shape if entry.is_regular_vertex else self.irregular_vertex_shape
        return super(BGVertexShapeProcessor, self).get_shape(entry=entry)

    def get_attributes_string_list(self, entry):
        return [self.shape_attrib_template.format(shape=self.get_shape(entry=entry)),
                self.pen_width_attrib_template.format(pen_width=self.get_pen_width())]


class BGVertexTextProcessor(TextProcessor):
    def __init__(self, color=Colors.black, size=12, font_name="Arial", color_source=None):
        super(BGVertexTextProcessor, self).__init__(color=color, size=size, font_name=font_name, color_source=color_source)

    def get_text(self, entry=None, label_format=LabelFormat.plain, separator="\n"):
        if entry is None:
            return super(BGVertexTextProcessor, self).get_text(entry=entry, label_format=label_format)
        if label_format == LabelFormat.plain.value or label_format == LabelFormat.plain:
            return "\"" + vertex_as_a_sting(vertex=entry, separator=separator) + "\""
        elif label_format == LabelFormat.html.value or label_format == LabelFormat.html:
            return vertex_as_html(vertex=entry, separator=separator)


class VertexProcessor(object):
    def __init__(self, shape_processor=None, text_processor=None):
        self.vertices_id_generator = ids_generator()
        self.vertices_ids_storage = {}
        self.shape_processor = shape_processor
        self.text_processor = text_processor
        self.template = "\"{v_id}\" [{attributes}];"

    def get_vertex_id(self, vertex):
        if vertex not in self.vertices_ids_storage:
            self.vertices_ids_storage[vertex] = next(self.vertices_id_generator)
        return self.vertices_ids_storage[vertex]

    def export_vertex_as_dot(self, vertex, label_format=LabelFormat.plain):
        """

        :type label_format: Union[str, LabelFormat]
        """
        vertex_id = self.get_vertex_id(vertex=vertex)
        attributes = []
        attributes.extend(self.text_processor.get_attributes_string_list(entry=vertex, label_format=label_format))
        attributes.extend(self.shape_processor.get_attributes_string_list(entry=vertex))
        return self.template.format(v_id=vertex_id, attributes=", ".join(attributes))


class BGVertexProcessor(VertexProcessor):
    def __init__(self, shape_processor=None, text_processor=None, color_source=None):
        super(BGVertexProcessor, self).__init__(shape_processor=shape_processor, text_processor=text_processor)
        if color_source is None:
            color_source = ColorSource()
        if self.shape_processor is None:
            self.shape_processor = BGVertexShapeProcessor(color_source=color_source)
        if self.text_processor is None:
            self.text_processor = BGVertexTextProcessor(color_source=color_source)

    def get_vertex_id(self, vertex):
        if isinstance(vertex, InfinityVertex):
            vertex = BGVertex.get_vertex_name_root(vertex.name)
        return super(BGVertexProcessor, self).get_vertex_id(vertex=vertex)

    def export_vertex_as_dot(self, vertex, label_format=LabelFormat.plain):
        """

        :type label_format: Union[str, LabelFormat]
        """
        vertex_id = self.get_vertex_id(vertex=vertex)
        attributes = []
        if not isinstance(vertex, InfinityVertex):
            attributes.extend(self.text_processor.get_attributes_string_list(entry=vertex, label_format=label_format))
        attributes.extend(self.shape_processor.get_attributes_string_list(entry=vertex))
        return self.template.format(v_id=vertex_id, attributes=", ".join(attributes))


class BGEdgeShapeProcessor(ShapeProcessor):
    def __init__(self, pen_width=1, style="solid", color=Colors.black, color_source=None):
        super(BGEdgeShapeProcessor, self).__init__(pen_width=pen_width, style=style, color=color, color_source=color_source)
        self.regular_edge_style = "solid"
        self.irregular_edge_style = "dotted"
        self.repeat_edge_style = "dashed"
        self.regular_edge_pen_width = 1
        self.irregular_edge_pen_with = .7
        self.repeat_edge_pen_width = .7

    def get_style(self, entry=None):
        if entry is None or not isinstance(entry, BGEdge):
            return self.regular_edge_style
        if entry.is_repeat_edge:
            return self.repeat_edge_style
        if entry.is_irregular_edge:
            return self.irregular_edge_style
        if entry.is_regular_edge:
            return self.regular_edge_style

    def get_pen_width(self, entry=None):
        if entry is None or not isinstance(entry, BGEdge):
            return self.regular_edge_pen_width
        if entry.is_repeat_edge:
            return self.repeat_edge_pen_width
        if entry.is_irregular_edge:
            return self.irregular_edge_pen_with
        if entry.is_regular_edge:
            return self.regular_edge_pen_width

    def get_dot_colors(self, multicolor):
        return [self.color_source.get_unused_color(entry=color) for color in multicolor.multicolors.elements()]

    def get_attributes_string_list(self, entry):
        if len(list(entry.multicolor.multicolors.elements())) != 1:
            raise ValueError(
                "Graphviz edge shape attributes can not be created only for multi-colored edge, but rather an edge with a single-colored edge")
        color = self.get_dot_colors(multicolor=entry.multicolor)[0].value
        return [
            self.color_attrib_template.format(color=color),
            self.style_attrib_template.format(style=self.get_style(entry=entry)),
            self.pen_width_attrib_template.format(pen_width=self.get_pen_width(entry=entry))]


class BGEdgeTextProcessor(TextProcessor):
    def __init__(self, size=7, font_name="Arial", color=Colors.black, color_source=None):
        super(BGEdgeTextProcessor, self).__init__(size=size, font_name=font_name, color=color, color_source=color_source)

    def get_text(self, entry=None, label_format=LabelFormat.plain,
                 edge_attributes_to_be_displayed=None,
                 tag_key_processor=None, tag_value_processor=None,
                 edge_key_value_separator=":",
                 entries_separator="\n"):
        """

        :type label_format: Union[str, LabelFormat]
        """
        if entry is None or not isinstance(entry, BGEdge):
            return super(BGEdgeTextProcessor, self).get_text(entry=entry, label_format=label_format)
        if tag_key_processor is None:
            tag_key_processor = self._tag_key_processor
        if tag_value_processor is None:
            tag_value_processor = self._tag_value_processor
        if edge_attributes_to_be_displayed is None:
            edge_attributes_to_be_displayed = []
        text = ""
        entries = []
        for path, key in edge_attributes_to_be_displayed:
            value = get_from_dict_with_path(source_dict=entry.data, key=key, path=path)
            if value is None:
                continue
            entries.append(tag_key_processor(key=key, label_format=label_format) + \
                           edge_key_value_separator + \
                           tag_value_processor(value=value, label_format=label_format))
        text += entries_separator.join(entries)
        if isinstance(entry.vertex1, TaggedInfinityVertex):
            entries = []
            starting = "" if len(text) == 0 else entries_separator
            for tag, value in entry.vertex1.tags:
                entries.append(tag_key_processor(tag, label_format=label_format) + \
                               entry.vertex1.TAG_SEPARATOR + \
                               tag_value_processor(value, label_format=label_format))
            text += starting + entries_separator.join(entries)
        if isinstance(entry.vertex2, TaggedInfinityVertex):
            entries = []
            starting = "" if len(text) == 0 else entries_separator
            for tag, value in entry.vertex2.tags:
                entries.append(tag_key_processor(tag, label_format=label_format) + \
                               entry.vertex1.TAG_SEPARATOR + \
                               tag_value_processor(value, label_format=label_format))
            text += starting + entries_separator.join(entries)
        if label_format == LabelFormat.plain.value or label_format == LabelFormat.plain:
            return "\"" + text + "\""
        elif label_format == LabelFormat.html.value or label_format == LabelFormat.html:
            return "<" + text + ">"
        return "\"\""

    def _tag_key_processor(self, key, label_format):
        if key == "repeat":
            return "r"
        else:
            return str(key)

    def _tag_value_processor(self, value, label_format):
        if str(value).endswith(("h", "t")) and (label_format == LabelFormat.html.value or label_format == LabelFormat.html):
            return str(value)[:-1] + "<SUP>" + str(value)[-1] + "</SUP>"
        return str(value)

    def get_attributes_string_list(self, entry, label_format=LabelFormat.plain, edge_attributes_to_be_displayed=None,
                                   tag_key_processor=None, tag_value_processor=None, edge_key_value_separator=":",
                                   entries_separator="\n"):
        return [self.label_attrib_template.format(label=self.get_text(entry=entry, label_format=label_format,
                                                                      edge_attributes_to_be_displayed=edge_attributes_to_be_displayed,
                                                                      tag_key_processor=tag_key_processor,
                                                                      tag_value_processor=tag_value_processor,
                                                                      edge_key_value_separator=edge_key_value_separator,
                                                                      entries_separator=entries_separator)),
                self.font_attrib_template.format(font=self.text_font_name),
                self.size_attrib_template.format(size=self.text_size),
                self.color_attrib_template.format(color=self.get_text_color(entry=entry))]


class EdgeProcessor(object):
    def __init__(self, vertex_processor, edge_shape_processor=None, edge_text_processor=None):
        self.shape_processor = edge_shape_processor
        self.text_processor = edge_text_processor
        self.vertex_processor = vertex_processor
        self.template = "\"{v1_id}\" -- \"{v2_id}\" [{attributes}];"

    def export_edge_as_dot(self, edge, label_format=LabelFormat.plain):
        """

        :type label_format: Union[str, LabelFormat]
        """
        v1_id = self.vertex_processor.get_vertex_id(vertex=self.get_vertex_1(edge))
        v2_id = self.vertex_processor.get_vertex_id(vertex=self.get_vertex_2(edge))
        attributes = self.shape_processor.get_attributes_string_list(entry=edge)
        if len(self.text_processor.get_text(entry=edge)) > 2:
            attributes.extend(self.text_processor.get_attributes_string_list(entry=edge, label_format=label_format))
        return [self.template.format(v1_id=v1_id, v2_id=v2_id, attributes=", ".join(attributes))]

    def get_vertex_1(self, edge):
        return edge[0]

    def get_vertex_2(self, edge):
        return edge[1]


class BGEdgeProcessor(EdgeProcessor):
    def __init__(self, vertex_processor, edge_shape_processor=None, edge_text_processor=None, color_source=None):
        super(BGEdgeProcessor, self).__init__(vertex_processor=vertex_processor, edge_shape_processor=edge_shape_processor,
                                              edge_text_processor=edge_text_processor)
        if color_source is None:
            color_source = ColorSource()
        if self.shape_processor is None:
            self.shape_processor = BGEdgeShapeProcessor(color_source=color_source)
        if self.text_processor is None:
            self.text_processor = BGEdgeTextProcessor(color_source=color_source)

    def export_edge_as_dot(self, edge, label_format=LabelFormat.plain):
        """

        :type label_format: Union[str, LabelFormat]
        """
        v1_id = self.vertex_processor.get_vertex_id(vertex=self.get_vertex_1(edge))
        v2_id = self.vertex_processor.get_vertex_id(vertex=self.get_vertex_2(edge))
        result = []
        for color in edge.multicolor.multicolors.elements():
            tmp_edge = BGEdge(vertex1=self.get_vertex_1(edge=edge), vertex2=self.get_vertex_2(edge=edge), multicolor=Multicolor(color),
                              data=edge.data)
            attributes = self.shape_processor.get_attributes_string_list(entry=tmp_edge)
            if len(self.text_processor.get_text(entry=tmp_edge)) > 2:
                attributes.extend(self.text_processor.get_attributes_string_list(entry=tmp_edge, label_format=label_format))
            result.append(self.template.format(v1_id=v1_id, v2_id=v2_id, attributes=", ".join(attributes)))
        return result

    def get_vertex_1(self, edge):
        return edge.vertex1

    def get_vertex_2(self, edge):
        return edge.vertex2


class GraphProcessor(object):
    def __init__(self, vertex_processor=None, edge_processor=None):
        self.vertex_processor = vertex_processor
        self.edge_processor = edge_processor
        self.template = "graph {{\n{edges}\n{vertices}\n}}"

    def export_vertices_as_dot(self, graph, label_format=LabelFormat.plain):
        result = []
        for vertex in graph.nodes():
            result.append(self.vertex_processor.export_vertex_as_dot(vertex=vertex, label_format=label_format))
        return result

    def export_edges_as_dot(self, graph, label_format=LabelFormat.plain):
        result = []
        for edge in graph.edges():
            result.extend(self.edge_processor.export_edge_as_dot(edge=edge, label_format=label_format))
        return result

    def export_graph_as_dot(self, graph, label_format=LabelFormat.plain):
        vertices_entries = self.export_vertices_as_dot(graph=graph, label_format=label_format)
        edges_entries = self.export_edges_as_dot(graph=graph, label_format=label_format)
        return self.template.format(edges="\n".join(edges_entries), vertices="\n".join(vertices_entries))


class BreakpointGraphProcessor(GraphProcessor):
    def __init__(self, vertex_processor=None, edge_processor=None, color_source=None, cc_filters=None):
        super(BreakpointGraphProcessor, self).__init__(vertex_processor=vertex_processor, edge_processor=edge_processor)
        if color_source is None:
            color_source = ColorSource()
        if self.vertex_processor is None:
            self.vertex_processor = BGVertexProcessor(color_source=color_source)
        if self.edge_processor is None:
            self.edge_processor = BGEdgeProcessor(vertex_processor=self.vertex_processor, color_source=color_source)
        if cc_filters is None:
            cc_filters = []
        self.cc_filters = cc_filters
        self.cc_filter_template = "{filter_name}: {filtered_cnt}"
        self.cc_filters_template = "\"cc_filters\" [shape=\"square\", penwidth=\"5\"," \
                                   " fontname=\"Arial\", fontsize=\"15\", " \
                                   "label=\"{overall_filters_info}\"];"

    def export_graph_as_dot(self, graph, label_format=LabelFormat.plain):
        vertices_entries = []
        edges_entries = []
        filters_results = defaultdict(int)
        for cc in graph.connected_components_subgraphs(copy=False):
            for cc_filter in self.cc_filters:
                if not cc_filter.accept_connected_component(cc=cc, breakpoint_graph=graph):
                    filters_results[cc_filter.name] += 1
                    break
            else:
                vertices_entries.extend(self.export_vertices_as_dot(graph=cc, label_format=label_format))
                edges_entries.extend(self.export_edges_as_dot(graph=cc, label_format=label_format))
        invoked_filters = {key: value for key, value in filters_results.items() if value > 0}
        if len(invoked_filters) > 0:
            entries = []
            for key, value in invoked_filters.items():
                entries.append(self.cc_filter_template.format(filter_name=key, filtered_cnt=value))
            label = "\n".join(entries)
            vertices_entries.append(self.cc_filters_template.format(overall_filters_info=label))
        return self.template.format(edges="\n".join(edges_entries), vertices="\n".join(vertices_entries))


class BGTreeVertexShapeProcessor(VertexShapeProcessor):
    def __init__(self, color=Colors.black, style="solid", internal_node_pen_width=1, leaf_node_pen_width=3, shape="oval", color_source=None,
                 vertex_data_wrapper=BGGenome, leaf_wrapper=None):
        super(BGTreeVertexShapeProcessor, self).__init__(color=color, style=style, pen_width=internal_node_pen_width, shape=shape, color_source=color_source)
        self.leaf_node_pen_width = leaf_node_pen_width
        self.__leaf_wrapper = lambda node: BGGenome(node.name) if leaf_wrapper is None else leaf_wrapper
        self.internal_node_pen_width = internal_node_pen_width
        self.vertex_data_wrapper = vertex_data_wrapper

    def get_pen_width(self, entry=None):
        if not isinstance(entry, TreeNode):
            return super(BGTreeVertexShapeProcessor, self).get_pen_width(entry=entry)
        if entry.is_leaf():
            return self.leaf_node_pen_width
        else:
            return self.internal_node_pen_width

    def get_color_as_string(self, entry, leaf_wrapper=None):
        if leaf_wrapper is None:
            self.__leaf_wrapper = self.__leaf_wrapper
        if not isinstance(entry, TreeNode):
            return super(BGTreeVertexShapeProcessor, self).get_color_as_string(entry=entry)
        if entry.is_leaf():
            entry = self.__leaf_wrapper(entry)
        else:
            entry = "non_leaf_tree_node"
        return super(BGTreeVertexShapeProcessor, self).get_color_as_string(entry=entry)


class BGTreeVertexTextProcessor(TextProcessor):
    def __init__(self, color=Colors.black, size=12, font_name="Arial", color_source=None, leaf_wrapper=None):
        super(BGTreeVertexTextProcessor, self).__init__(color=color, size=size, font_name=font_name, color_source=color_source)
        self.__leaf_wrapper = lambda node: BGGenome(node.name) if leaf_wrapper is None else leaf_wrapper

    def get_text_color(self, entry=None, leaf_wrapper=None):
        if leaf_wrapper is None:
            leaf_wrapper = self.__leaf_wrapper
        if entry is None or not isinstance(entry, TreeNode):
            return super(BGTreeVertexTextProcessor, self).get_text_color(entry=entry)
        if entry.is_leaf():
            entry = leaf_wrapper(entry)
        else:
            entry = "non_leaf_tree_node"
        return self.color_source.get_color_as_string(entry=entry)

    def get_text(self, entry=None, label_format=LabelFormat.plain):
        if entry is None or not isinstance(entry, TreeNode):
            return super(BGTreeVertexTextProcessor, self).get_text(entry=entry, label_format=label_format)
        text = ""
        if entry.is_leaf():
            text += entry.name
        if label_format == LabelFormat.html or label_format == LabelFormat.html.value:
            return "<" + text + ">"
        return "\"" + text + "\""


class BGTreeVertexProcessor(VertexProcessor):
    def __init__(self, shape_processor=None, text_processor=None, color_source=None):
        super(BGTreeVertexProcessor, self).__init__(shape_processor=shape_processor, text_processor=text_processor)
        if color_source is None:
            color_source = ColorSource()
        if self.shape_processor is None:
            self.shape_processor = BGTreeVertexShapeProcessor(color_source=color_source)
        if self.text_processor is None:
            self.text_processor = BGTreeVertexTextProcessor(color_source=color_source)

    def get_vertex_id(self, vertex, leaf_wrapper=BGGenome):
        if isinstance(vertex, TreeNode) and vertex.is_leaf():
            vertex_for_id = leaf_wrapper(vertex.name)
        else:
            vertex_for_id = vertex
        return super(BGTreeVertexProcessor, self).get_vertex_id(vertex=vertex_for_id)

    def export_vertex_as_dot(self, vertex, label_format=LabelFormat.plain, leaf_wrapper=BGGenome):
        vertex_id = self.get_vertex_id(vertex=vertex, leaf_wrapper=leaf_wrapper)
        attributes = []
        attributes.extend(self.text_processor.get_attributes_string_list(entry=vertex, label_format=label_format))
        attributes.extend(self.shape_processor.get_attributes_string_list(entry=vertex))
        return self.template.format(v_id=vertex_id, attributes=", ".join(attributes))


class BGTreeEdgeShapeProcessor(ShapeProcessor):
    def __init__(self, non_leaf_pen_width=1, leaf_pen_width=3, color=Colors.black, color_source=None, style="solid"):
        super(BGTreeEdgeShapeProcessor, self).__init__(pen_width=non_leaf_pen_width, color=color, color_source=color_source, style=style)
        self.leaf_branch_pen_width = leaf_pen_width
        self.non_leaf_branch_pen_width = non_leaf_pen_width

    def _is_leaf_branch(self, edge):
        return not (isinstance(edge[0], TreeNode) and isinstance(edge[1], TreeNode))

    def get_color_as_string(self, entry):
        if not isinstance(entry, tuple):
            return super(BGTreeEdgeShapeProcessor, self).get_attributes_string_list(entry=entry)
        if not self._is_leaf_branch(edge=entry):
            entry = None
        else:
            non_tree_node_instance = entry[0] if not isinstance(entry[0], TreeNode) else entry[1]
            entry = non_tree_node_instance
        return super(BGTreeEdgeShapeProcessor, self).get_color_as_string(entry=entry)

    def get_pen_width(self, entry=None):
        if self._is_leaf_branch(edge=entry):
            return self.leaf_branch_pen_width
        else:
            return self.non_leaf_branch_pen_width


class BGTreeEdgeTextProcessor(TextProcessor):
    def __init__(self, font_name="Arial", size=7, color=Colors.black, color_source=None):
        super(BGTreeEdgeTextProcessor, self).__init__(color=color, size=size, font_name=font_name, color_source=color_source)


class BGTreeEdgeProcessor(EdgeProcessor):
    def __init__(self, vertex_processor, edge_shape_processor=None, edge_text_processor=None, color_source=None):
        super(BGTreeEdgeProcessor, self).__init__(vertex_processor=vertex_processor, edge_shape_processor=edge_shape_processor,
                                                  edge_text_processor=edge_text_processor)
        self.vertex_processor = vertex_processor
        if color_source is None:
            color_source = ColorSource()
        if self.shape_processor is None:
            self.shape_processor = BGTreeEdgeShapeProcessor(color_source=color_source)
        if self.text_processor is None:
            self.text_processor = BGTreeEdgeTextProcessor(color_source=color_source)


class BGTreeProcessor(GraphProcessor):
    def __init__(self, vertex_processor=None, edge_processor=None, color_source=None):
        super(BGTreeProcessor, self).__init__(vertex_processor=vertex_processor, edge_processor=edge_processor)
        if color_source is None:
            color_source = ColorSource()
        if self.vertex_processor is None:
            self.vertex_processor = BGTreeVertexProcessor(color_source=color_source)
        if self.edge_processor is None:
            self.edge_processor = BGTreeEdgeProcessor(vertex_processor=self.vertex_processor, color_source=color_source)
