# -*- coding: utf-8 -*-

import networkx as nx


def get_all_cycles(breakpoint_graph):
    visited = set()
    cycles = []
    for vertex in breakpoint_graph.nodes():
        if vertex in visited:
            continue
        try:
            cycle = nx.find_cycle(breakpoint_graph.bg, vertex)
            new = False
            for v1, v2, dir in cycle:
                if v1 not in visited:
                    new = True
                visited.add(v1)
            if new:
                cycles.append(cycle)
        except:
            pass
    return cycles


def get_all_paths(breakpoint_graph):
    ccs = []
    for cc in breakpoint_graph.connected_components_subgraphs(copy=False):
        if any(map(lambda vertex: vertex.is_irregular_vertex, cc.nodes())):
            ccs.append(cc)
            continue
    return ccs


def scj(breakpoint_graph):
    number_of_genes = len([v for v in breakpoint_graph.nodes() if v.is_regular_vertex]) / 2
    cycles = get_all_cycles(breakpoint_graph=breakpoint_graph)
    two_cycles = [cycle for cycle in cycles if len(cycle) == 2]
    adjacency_graph_two_cycles = [cycle for cycle in two_cycles if all(map(lambda c_entry: c_entry[0].is_regular_vertex, cycle))]
    adjacency_graph_paths = get_all_paths(breakpoint_graph=breakpoint_graph)
    number_of_paths = len(adjacency_graph_paths)
    return int(2 * number_of_genes - 2 * len(adjacency_graph_two_cycles) - number_of_paths)


single_cut_and_join_distance = scj
