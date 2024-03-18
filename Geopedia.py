import pyvista as pv
import vtk
import Data
import Representation
import os
import random
import dearpygui.dearpygui as dpg
from multiprocessing import Process

# Create a plotter window
# Bir çizim penceresi oluştur
plotter = pv.Plotter()
plotter.set_background([201, 205, 224])

ren_win: vtk.vtkRenderWindow = plotter.ren_win
renderer: vtk.vtkRenderer = ren_win.GetRenderers().GetFirstRenderer()
interactor = ren_win.GetInteractor()

mode = "edit"

match mode.lower():
    case "view":

        # To keep the legend count
        # Lejant sayısını tutmak için
        currentLegendCount = 0

        # To keep actors
        # Aktörleri tutmak için
        actors = {}

        # To keep the values
        # Değerleri tutmak için
        values = {}

        # Create a picker
        # Bir seçici oluştur
        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.0005)

        textActor = vtk.vtkTextActor()
        textActor.SetInput("Please select a administrative unit\n")
        textProperty = textActor.GetTextProperty()
        textProperty.SetFontSize(24)
        textProperty.SetColor(0, 0, 0)
        textProperty.SetVerticalJustificationToTop()
        plotter.add_actor(textActor)

        # Reposition the text
        # Metni yeniden konumlandır

        def RepositionText(selfInteractor, event):
            size = renderer.GetSize()
            global textActor, ren_win
            textActor.SetPosition(size[0] / 2, size[1])
            ren_win.Render()

        RepositionText(None, None)

        # Add an observer to the window resize event
        # Pencereyi yeniden boyutlandırma olayına bir gözlemci ekle
        interactor.AddObserver(
            vtk.vtkCommand.WindowResizeEvent, RepositionText)

        # Pick an actor
        # Bir aktör seç

        def Pick(selfInteractor, event):
            mousePos = selfInteractor.GetEventPosition()
            global renderer, picker, actors
            picker.Pick(mousePos[0], mousePos[1], 0, renderer)
            id = picker.GetCellId()
            if id == -1:
                return
            actor: vtk.vtkActor = picker.GetActor()
            adm1 = ""
            for key in actors.keys():
                if isinstance(actors[key], list) and actor in actors[key]:
                    adm1 = key
                    break
            global textActor
            textActor.SetInput(adm1 + "\n" + str(values[adm1]))

        interactor.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, Pick)

        # Load a 3D model
        # Bir 3B model yükle

        def ShowData(file: str, lang: str = None):

            # Get the relational data
            # İlişkisel veriyi al
            relation = Data.GetRelationalData(file, lang)
            units = list(relation["Data"].keys())
            representation = relation["Representation"]
            adm1s = Representation.BuildADM(
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
            for key in range(256):
                lu.SetTableValue(key, colors[0][0] + colorGap[0] * key / 255.0,
                                 colors[0][1] + colorGap[1] * key / 255.0,
                                 colors[0][2] + colorGap[2] * key / 255.0)

            # Add the scalar bar as legend
            # Lejant olarak skaler çubuğu ekle
            sca = vtk.vtkScalarBarActor()

            sca.SetTitle(file.split(".")[0] + "\n")
            sca.SetLookupTable(lu)
            sca.SetLabelFormat("%1.2fM")
            sca.SetUnconstrainedFontSize(True)

            # Set the text properties for titles
            # Başlıklar için metin özelliklerini ayarla
            ttp = vtk.vtkTextProperty()
            ttp.SetFontSize(12)
            ttp.SetColor(0.0, 0.0, 0.0)
            sca.SetTitleTextProperty(ttp)

            # Set orientation to horizontal
            # Yatay olarak yönlendirme ayarla
            sca.SetOrientationToHorizontal()

            # Set the text properties for labels
            # Etiketler için metin özelliklerini ayarla
            ltp = vtk.vtkTextProperty()
            ltp.SetFontSize(8)
            ltp.SetColor(0.0, 0.0, 0.0)
            sca.SetLabelTextProperty(ltp)

            global currentLegendCount
            sca.SetPosition(0.05 + 0.2 * (currentLegendCount %
                            3), int(currentLegendCount / 3) * 0.1)
            sca.SetWidth(0.175)
            sca.SetHeight(0.125)
            currentLegendCount += 1
            actors[file] = sca
            plotter.add_actor(sca)

            # Store the values
            # Değerleri sakla
            global values
            for adm1 in adm1s.keys():
                values[adm1] = relation["Data"][adm1][representation["Value"]]

            # Add the meshes to the plotter
            # Ağları çizim penceresine ekle
            for key in meshesAndColors.keys():
                # Add the mesh to the plotter
                # Meshi çizim penceresine ekle
                subactors = []
                for mesh in meshesAndColors[key][0]:
                    actor = plotter.add_mesh(
                        mesh, color=meshesAndColors[key][1])
                    subactors.append(actor)
                actors[key] = subactors

        files = os.listdir("Relations")

        for i in range(3):
            chosen = random.choice(files)
            del files[files.index(chosen)]
            ShowData(chosen)
        # Show the plotter window
        # Çizim penceresini göster
        ren_win.MakeCurrent()

        plotter.show()

    case "edit":
        counter = 0

        files = os.listdir("Countries")
        selectedFile = ""
        selectedColor = ""

        mainWindow = None
        dataWindow = None

        keyUI: dict[str: []] = {}

        p2: Process

        def SelectFile(sender):
            global selectedFile
            selectedFile = dpg.get_value(sender)

        def SelectColor(sender):
            global selectedColor
            selectedColor = dpg.get_value(sender)
            selectedColor = [int(c) for c in selectedColor]

        def GenerateMap():
            global selectedFile, selectedColor, plotter
            plotter.close()
            plotter = pv.Plotter()
            meshes = Representation.BuildADM(selectedFile)
            for key in meshes.keys():
                for mesh in meshes[key]:
                    plotter.add_mesh(mesh, color=selectedColor)
            plotter.show()

        def AddKey():
            global keyUI, counter
            key = counter
            keyUI[str(counter)] = [dpg.add_input_text(
                label="key", parent=mainWindow), dpg.add_combo(label="type", items=["int", "float", "str"], parent=mainWindow),
                dpg.add_button(label="Remove", callback=lambda: RemoveKey(key), parent=mainWindow)]
            counter += 1

        def RunDataEditScreen():
            global dataWindow
            dataWindow = dpg.add_window(label="Data", width=500, height=500)
            units = Data.GetUnitNames(selectedFile)
            for unit in units:
                dpg.add_text(default_value=unit, parent=dataWindow)
                for i in range(counter):
                    key = str(i)
                    if key in keyUI:
                        name = dpg.get_value(keyUI[key][0])
                        match dpg.get_value(keyUI[key][1]):
                            case "int":
                                dpg.add_input_int(
                                    label=name, parent=dataWindow)
                            case "float":
                                dpg.add_input_float(
                                    label=name, parent=dataWindow)
                            case "str":
                                dpg.add_input_text(
                                    label=name, parent=dataWindow)

        def RemoveKey(index):
            global keyUI
            for ui in keyUI[str(index)]:
                dpg.delete_item(ui)
            del keyUI[str(index)]

        def RunKeyEditScreen():
            dpg.create_context()
            dpg.create_viewport()
            dpg.setup_dearpygui()

            global mainWindow, files

            mainWindow = dpg.add_window(
                label="Geopedia", width=500, height=500)

            dpg.add_combo(label="File", items=files, callback=SelectFile,
                          parent=mainWindow, width=100)

            dpg.add_button(label="Generate data", callback=lambda: RunDataEditScreen(),
                           parent=mainWindow, width=100, height=30)

            dpg.add_button(label="Add key", callback=lambda: AddKey(),
                           parent=mainWindow, width=100, height=30)

            dpg.show_viewport()
            dpg.start_dearpygui()
            dpg.destroy_context()

        if __name__ == "__main__":
            p1 = Process(target=RunKeyEditScreen)
            p1.start()
            p1.join()
