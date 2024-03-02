import trimesh as tm
import numpy as np
import pyvista as pv
import json
import random
import vtk
import vtkmodules.all as vtkm
import xml.etree.ElementTree as ET
import Data
import Representation
import os

# Create a plotter window
# Bir çizim penceresi oluştur
plotter = pv.Plotter()


def ShowData(file: str, lang: str = None):
    relation = Data.GetRelationalData(file, lang)
    units = list(relation["Data"].keys())
    representation = relation["Representation"]
    adm1s = Representation.BuildADM1(
        representation["Map"].split(".")[0], units)
    meshesAndColors = Representation.RepresentValueWithColor(
        adm1s, {item: relation["Data"][item][representation["Value"]] for item in relation["Data"].keys()}, [color for color in representation["Colors"]])
    for i in meshesAndColors.values():
        for j in i[0]:
            plotter.add_mesh(j, color=i[1])


for file in os.listdir("Relations"):
    if file.endswith(".xml"):
        ShowData(file.split(".")[0])


# Show the plotter window
# Çizim penceresini göster
plotter.show()
