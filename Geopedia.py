import trimesh as tm
import numpy as np
import pyvista as pv
import json
import random
import vtk
import vtkmodules.all as vtkm
import xml.etree.ElementTree as ET


def BuildADM1(country: str, id: int | str) -> list:

    # Get data from .json
    # .json dosyasından veri al
    data = json.load(open("Countries\\ADM1\\"+country +
                     ".geojson", encoding="utf-8"))

    index = -1
    if isinstance(id, str):
        for i in range(len(data["features"])):
            if data["features"][i]["properties"]["shapeName"] == id:
                index = int(i)
                break
    if isinstance(id, int):
        index = id

    borders = data["features"][index]["geometry"]["coordinates"]

    adm1 = [data["features"][index]["properties"]
            ["shapeName"]]

    # Check if the borders are multipart
    # Sınırların çok parçalı olup olmadığını kontrol et
    multipart = isinstance(borders[0][0][0], list)
    parts = []
    if multipart:
        for border in borders:
            polygon = tm.creation.Polygon(border[0])
            parts.append(tm.creation.extrude_polygon(polygon, 0.1))
    # If multipart, create a polygon for each part
    # Çok parçalı ise, her parça için bir çokgen oluştur
    else:
        polygon = tm.creation.Polygon(borders[0])
        parts.append(tm.creation.extrude_polygon(polygon, 0.1))
    # Return the name of the province and its parts
    # İlin adını ve parçalarını döndür
    adm1.append(parts)
    return adm1


def BuildRelation(relation: str):
    pass


# Create a plotter window
# Bir çizim penceresi oluştur
plotter = pv.Plotter()


colorInterval = [[205 / 255, 221 / 255, 221 / 255], [
    87 / 255, 74 / 255, 226 / 255]]

data = json.load(open("Data\\Turkey Population.json", encoding="utf-8"))
population = {}
year = input("Enter the year: ")
for province in data:
    population[province["name"]] = int(province[year].replace(" ", ""))
minPop = min(population.values())
maxPop = max(population.values())

for province in population.keys():
    ratio = (population[province]-minPop)/(maxPop-minPop)
    color = [colorInterval[0][i] *
             (1 - ratio) + colorInterval[1][i] * ratio for i in range(3)]
    provinceElements = BuildADM1("Turkey", province)
    for element in provinceElements[1]:
        plotter.add_mesh(element, color=color)

picker = vtk.vtkPointPicker()


renwin = plotter.ren_win


def test(_widget, _event):
    print("test")
    print(renwin.GetInteractor().GetEventPosition())


interactor = renwin.GetInteractor()
interactor.AddObserver("LeftButtonPressEvent", test)
interactor.AddObserver("RightButtonPressEvent", test)
interactor.Initialize()


# Show the plotter window
# Çizim penceresini göster
plotter.show()
