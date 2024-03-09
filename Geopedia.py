import pyvista as pv
import vtk
import Data
import Representation
import os

# Create a plotter window
# Bir çizim penceresi oluştur
plotter = pv.Plotter()
plotter.set_background([201, 205, 224])

# To keep the legend count
# Lejant sayısını tutmak için
currentLegendCount = 0

# To keep actors
# Aktörleri tutmak için
actors = {}


ren_win: vtk.vtkRenderWindow = plotter.ren_win
renderer: vtk.vtkRenderer = plotter.renderer
interactor = ren_win.GetInteractor()


def Pick(selfInteractor, event):
    mousePos = selfInteractor.GetEventPosition()
    picker = vtk.vtkCellPicker()
    picker.SetTolerance(0.0005)
    global renderer
    picker.Pick(mousePos[0], mousePos[1], 0, renderer)
    id = picker.GetCellId()
    if id == -1:
        return
    for actor in actors.values():
        if isinstance(actor, list):
            for subactor in actor:
                print(isinstance(subactor, vtk.vtkActor))
                if not isinstance(subactor, vtk.vtkActor):
                    print(type(subactor))


interactor.AddObserver(vtk.vtkCommand.MouseMoveEvent, Pick)

# Load a 3D model
# Bir 3B model yükle


def ShowData(file: str, lang: str = None):

    subactors = []

    # Get the relational data
    # İlişkisel veriyi al
    relation = Data.GetRelationalData(file, lang)
    units = list(relation["Data"].keys())
    representation = relation["Representation"]
    adm1s = Representation.BuildADM1(
        representation["Map"].split(".")[0], units)

    # Get the colors
    # Renkleri al
    colors = [color for color in representation["Colors"]]
    colorGap = [colors[1][i] - colors[0][i] for i in range(3)]

    # Represent the data with colors
    # Veriyi renklerle temsil et
    meshesAndColors = Representation.RepresentValueWithColor(
        adm1s, {item: relation["Data"][item][representation["Value"]] for item in relation["Data"].keys()}, colors)

    # Create a lookup table
    # Bir arama tablosu oluştur
    lu = vtk.vtkLookupTable()
    lu.SetNumberOfTableValues(256)
    lu.SetRange(representation["Interval"][0] /
                1e6, representation["Interval"][1] / 1e6)
    for items in range(256):
        lu.SetTableValue(items, colors[0][0] + colorGap[0] * items / 255.0,
                         colors[0][1] + colorGap[1] * items / 255.0,
                         colors[0][2] + colorGap[2] * items / 255.0)

    # Add the scalar bar as legend
    # Lejant olarak skaler çubuğu ekle
    sca = vtk.vtkScalarBarActor()
    sca.SetLookupTable(lu)
    sca.SetLabelFormat("%1.2fM")
    sca.SetUnconstrainedFontSize(True)

    # Set the text properties for titles
    # Başlıklar için metin özelliklerini ayarla
    ttp = vtk.vtkTextProperty()
    ttp.SetFontSize(10)
    ttp.SetColor(0.0, 0.0, 0.0)
    sca.SetTitleTextProperty(ttp)

    # Set orientation to horizontal
    # Yatay olarak yönlendirme ayarla
    sca.SetOrientationToHorizontal()

    # Set the text properties for labels
    # Etiketler için metin özelliklerini ayarla
    ltp = vtk.vtkTextProperty()
    ltp.SetFontSize(10)
    ltp.SetColor(0.0, 0.0, 0.0)
    sca.SetLabelTextProperty(ltp)

    global currentLegendCount
    sca.SetPosition(0.05 + 0.25 * (currentLegendCount %
                    3), int(currentLegendCount / 3) * 0.1)
    sca.SetWidth(0.2)
    sca.SetHeight(0.1)
    currentLegendCount += 1
    subactors.append(sca)
    plotter.add_actor(sca)

    # Add the meshes to the plotter
    # Ağları çizim penceresine ekle
    for items in meshesAndColors.values():
        # Add the mesh to the plotter
        # Meshi çizim penceresine ekle
        for mesh in items[0]:
            actor = plotter.add_mesh(mesh, color=items[1])
            subactors.append(actor)

    global actors
    actors[file] = subactors


answer = input("Do you want to see all the data? (y/n): ")
match answer:
    case "y":
        for file in os.listdir("Relations"):
            ShowData(file, "tr")
    case "n":
        for file in os.listdir("Relations"):
            if input("Do you want to see " + file + "? (y/n): ") == "y":
                ShowData(file, "tr")

# Show the plotter window
# Çizim penceresini göster
ren_win.MakeCurrent()
plotter.show()
