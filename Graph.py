import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image


file_colors: dict[str:str] = {
    "xml": "orange",
    "json": "yellow",
    "geojson": "yellow",
    "csv": "green"
}

files: list[tuple] = []


def LinkFiles(file1: str, file2: str) -> None:
    global files
    if file1 != "" and file2 != "":
        files.append((file1, file2))


node_colors: list[str] = []


G = nx.DiGraph()


def DefineColors() -> None:
    global node_colors, G, file_colors
    for file in G.nodes:
        file: str
        print(file)
        if file.split(".")[-1] in file_colors:
            node_colors.append(file_colors[file.split(".")[-1]])


def CreateGraphAndDraw() -> None:
    global files, G, node_colors
    print(files)
    G.add_edges_from(files)
    pos = nx.circular_layout(G)
    DefineColors()

    plt.figure(figsize=(10, 10))
    nx.draw(G, pos, node_color=node_colors, with_labels=True,
            node_size=3000, font_size=7, font_weight='bold')

    plt.show()
