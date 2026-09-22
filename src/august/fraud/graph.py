from __future__ import annotations

from collections.abc import Iterable

import networkx as nx


def build_entity_graph(edges: Iterable[tuple[str, str, str]]) -> nx.Graph:
    """Build user/device/card/address/IP/merchant relationship graph.

    Each edge is (left_entity, right_entity, relationship_type).
    """
    graph = nx.Graph()

    for left, right, relationship in edges:
        graph.add_edge(left, right, relationship=relationship)

    return graph


def suspicious_components(graph: nx.Graph, *, minimum_size: int = 4) -> list[dict]:
    components = []

    for nodes in nx.connected_components(graph):
        if len(nodes) < minimum_size:
            continue

        subgraph = graph.subgraph(nodes)
        components.append(
            {
                "nodes": sorted(nodes),
                "node_count": subgraph.number_of_nodes(),
                "edge_count": subgraph.number_of_edges(),
                "density": nx.density(subgraph),
                "degree_centrality": nx.degree_centrality(subgraph),
            }
        )

    return sorted(components, key=lambda item: (item["density"], item["node_count"]), reverse=True)
