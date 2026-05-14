"""
Exports the Logseq graph into a GEXF file for Gephi and similar tools.
"""

from pathlib import Path
import networkx as nx

from src.regex_utils import LINK_RE, ASSET_LINK_RE
from src.config import PAGE_DIRS


def is_journal(file_path: Path):
    """
    Determines whether a file is a Logseq journal.
    """

    # Standard Logseq journal format: YYYY_MM_DD.md

    name = file_path.stem
    parts = name.split("_")

    if len(parts) != 3:
        return False

    return all(part.isdigit() for part in parts)


def add_weighted_edge(graph, source, target):
    """
    Adds or updates weighted edges.
    """

    if graph.has_edge(source, target):
        graph[source][target]["weight"] += 1
    else:
        graph.add_edge(
            source,
            target,
            weight=1
        )


def export_graph_to_gexf(output_path="logseq_graph.gexf"):
    """
    Builds a directed graph from Logseq pages and journals
    and exports it as a GEXF file suitable for Gephi.
    """

    graph = nx.DiGraph()

    total_links = 0
    asset_links = 0

    md_files = []

    for directory in PAGE_DIRS:

        if not directory.exists():
            continue

        md_files.extend(directory.glob("*.md"))

    node_types = {}

    for file_path in md_files:

        page_name = file_path.stem

        node_types[page_name] = (
            "journal"
            if is_journal(file_path)
            else "page"
        )

    for file_path in md_files:

        page_name = file_path.stem
        node_type = node_types[page_name]

        try:
            content = file_path.read_text(encoding="utf-8")

        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        word_count = len(content.split())

        graph.add_node(
            page_name,
            type=node_type,
            word_count=word_count,
            filename=file_path.name
        )

        links = LINK_RE.findall(content)

        for link in links:

            total_links += 1

            link = link.strip()

            if not link:
                continue

            linked_type = node_types.get(link, "page")

            graph.add_node(
                link,
                type=linked_type
            )

            add_weighted_edge(
                graph,
                page_name,
                link
            )

        assets = ASSET_LINK_RE.findall(content)

        for asset in assets:

            asset_links += 1

            asset_name = Path(asset).name

            graph.add_node(
                asset_name,
                type="asset",
                extension=Path(asset).suffix.lower()
            )

            add_weighted_edge(
                graph,
                page_name,
                asset_name
            )

    nx.write_gexf(graph, output_path)

    return (
        output_path,
        graph.number_of_nodes(),
        graph.number_of_edges(),
        total_links,
        asset_links
    )