import xml.etree
import xml.etree.ElementTree
import pyvista as pv
import vtk
import Data
import Representation
import os
import dearpygui.dearpygui as dpg
import json
import xml
import trimesh as tm
import copy
from Graph import CreateGraphAndDraw

# Create a plotter window
# Bir çizim penceresi oluştur
plotter = pv.Plotter()
plotter.set_background([201, 205, 224])

ren_win: vtk.vtkRenderWindow = plotter.ren_win
renderer: vtk.vtkRenderer = ren_win.GetRenderers().GetFirstRenderer()
interactor = ren_win.GetInteractor()

# To adjust the font
# Yazı tipini ayarlamak için


def SetFont():
    with dpg.font_registry():
        font = dpg.add_font("GUI/Font/unifont-15.1.05.otf", 15)
        dpg.add_font_range(32, 7935, parent=font)
    dpg.bind_font(font)

# To adjust the theme
# Temayı ayarlamak için


def SetTheme():
    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text,
                                (24, 209, 219, 255), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg,
                                (42, 42, 42, 255), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_NavWindowingHighlight,
                                (42, 42, 42, 255), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive,
                                (60, 60, 60, 255), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg,
                                (42, 42, 42, 255), category=dpg.mvThemeCat_Core)

            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 12, 12)
    dpg.bind_theme(theme)


mode = "view"

# To set the mode
# Modu ayarlamak için


def SetMode(sender):
    global mode
    mode = dpg.get_value(sender)


if __name__ == "__main__":
    # To select a mode
    # Bir mod seçmek için
    dpg.create_context()
    dpg.create_viewport()
    dpg.setup_dearpygui()

    SetFont()
    SetTheme()

    win = dpg.add_window(label="Geopedia", width=500,
                         height=500, no_resize=True, no_move=True, no_close=True, no_collapse=True)

    dpg.add_text("Select a mode", parent=win)

    dpg.add_radio_button(items=["View", "Data Edit", "Relation Edit"],
                         callback=SetMode, parent=win)

    dpg.add_text("Close window to continue", parent=win)

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


match mode.lower():

    case "view":

        def View():
            # To keep the selected files
            # Seçilen dosyaları tutmak için
            selectedFiles: list[str] = []
            # To keep temporary selected file
            # Geçici seçilen dosyayı tutmak için
            selectedFile: str
            # To keep the selected language
            # Seçilen dili tutmak için
            lang: str = "en"

            def SelectionWindow():

                dpg.create_context()
                dpg.create_viewport(width=400, height=800)
                dpg.setup_dearpygui()

                SetFont()
                SetTheme()

                # Get the files
                # Dosyaları al
                files = os.listdir("Relations")

                files_listbox: int | str
                selectedFiles_listbox: int | str

                window = dpg.add_window(width=400, height=800, pos=[
                                        0, 0], no_collapse=True, no_close=True, no_move=True)

                def SelectFile(sender):
                    nonlocal selectedFile
                    selectedFile = dpg.get_value(sender)

                def AddFile():
                    nonlocal selectedFiles, files_listbox
                    if selectedFile not in selectedFiles:
                        selectedFiles.append(selectedFile)
                        files.remove(selectedFile)
                        dpg.configure_item(files_listbox, items=files)
                        dpg.configure_item(selectedFiles_listbox,
                                           items=selectedFiles)

                def RemoveFile():
                    nonlocal selectedFiles, selectedFiles_listbox, files_listbox
                    item = dpg.get_value(selectedFiles_listbox)
                    selectedFiles.remove(item)
                    dpg.configure_item(selectedFiles_listbox,
                                       items=selectedFiles)
                    files.append(item)
                    files.sort()
                    dpg.configure_item(files_listbox, items=files)

                def SelectLang(sender):
                    nonlocal lang
                    lang = dpg.get_value(sender)

                files_listbox = dpg.add_listbox(parent=window, items=files,
                                                callback=SelectFile, num_items=10)

                dpg.add_button(label="Add File",
                               callback=lambda: AddFile(), parent=window)

                selectedFiles_listbox = dpg.add_listbox(
                    parent=window, items=selectedFiles)

                dpg.add_button(label="Remove File",
                               callback=lambda: RemoveFile(), parent=window)

                dpg.add_listbox(parent=window, items=[
                                "en", "tr", "de"], callback=SelectLang)

                dpg.show_viewport()
                dpg.start_dearpygui()
                dpg.destroy_context()

            SelectionWindow()

            data = {}

            # To keep the legend count
            # Lejant sayısını tutmak için
            currentLegendCount = 0

            # To keep actors
            # Aktörleri tutmak için
            actors = {}

            # To keep the values
            # Değerleri tutmak için
            displayValues = {}

            # To keep the local names
            # Yerel adları tutmak için
            localNames = {}

            # Create a picker
            # Bir seçici oluştur
            picker = vtk.vtkCellPicker()
            picker.SetTolerance(0.0005)

            nameTextActor = vtk.vtkTextActor()
            nameTextActor.SetInput("Please select a administrative unit\n")
            textProperty = nameTextActor.GetTextProperty()
            textProperty.SetJustificationToCentered()
            textProperty.SetFontSize(24)
            textProperty.SetColor(0, 0, 0)
            textProperty.SetVerticalJustificationToTop()
            plotter.add_actor(nameTextActor)

            valueTextActor = vtk.vtkTextActor()
            textProperty = valueTextActor.GetTextProperty()
            textProperty.SetJustificationToLeft()
            textProperty.SetFontSize(18)
            textProperty.SetColor(0, 0, 0)
            textProperty.SetVerticalJustificationToTop()
            plotter.add_actor(valueTextActor)

            # Reposition the text
            # Metni yeniden konumlandır

            def RepositionText(selfInteractor, event):
                size = renderer.GetSize()
                nonlocal nameTextActor, valueTextActor
                global ren_win
                nameTextActor.SetPosition(size[0] / 2, size[1])
                valueTextActor.SetDisplayPosition(0, size[1])
                ren_win.Render()

            RepositionText(None, None)

            # Add an observer to the window resize event
            # Pencereyi yeniden boyutlandırma olayına bir gözlemci ekle
            interactor.AddObserver(
                vtk.vtkCommand.MouseMoveEvent, RepositionText)

            # Pick an actor
            # Bir aktör seç

            def Pick(selfInteractor, event):
                global ren_win
                mousePos = interactor.GetEventPosition()
                global renderer
                nonlocal picker, actors
                picker.Pick(mousePos[0], mousePos[1], 0, renderer)
                id = picker.GetCellId()
                if id == -1:
                    return
                actor: vtk.vtkActor = picker.GetActor()
                adm1 = " "
                for key in actors.keys():
                    if isinstance(actors[key], list) and actor in actors[key]:
                        adm1 = key
                        break
                nonlocal nameTextActor, valueTextActor, displayValues
                if adm1 in localNames.keys():
                    nameTextActor.SetInput(localNames[adm1])
                else:
                    nameTextActor.SetInput(adm1)
                valueText = ""
                if adm1 in displayValues.keys():
                    for key in data[adm1].keys():
                        valueText += key + " : " + str(data[adm1][key]) + "\n"
                valueTextActor.SetInput(valueText)

            interactor.AddObserver(vtk.vtkCommand.MouseMoveEvent, Pick)

            # Load a 3D model
            # Bir 3B model yükle

            def ShowData(file: str, lang: str = None):

                # Get the relational data
                # İlişkisel veriyi al
                relation = Data.AnalyzeXML("Relations/" + file, lang)
                units = []

                match relation["Type"]:
                    case "Relational":

                        units = list(relation["Data"].keys())

                        # Store the data
                        # Veriyi sakla
                        nonlocal data
                        for unit in units:
                            data[unit] = relation["Data"][unit]

                        representation = relation["Representation"]
                        adm1s = Representation.BuildADM(
                            representation["Map"].split(".")[0], units)

                        colors = representation["Colors"]

                        # Represent the data with colors
                        # Veriyi renklerle temsil et
                        meshesAndColors = Representation.RepresentValuesWithColors(
                            adm1s, {item: relation["Data"][item][representation["Value"]] for item in relation["Data"].keys()}, colors)

                        borders = representation["Borders"]

                        for border in borders:
                            lines = Representation.BuildADMBorders(border[0])
                            for key in lines.keys():
                                for line in lines[key]:
                                    _line: pv.PolyData = line
                                    plotter.add_lines(
                                        _line.points, color=border[2], width=border[1], connected=True)

                        # Create a lookup table
                        # Bir arama tablosu oluştur
                        lu = vtk.vtkLookupTable()
                        lu.SetNumberOfTableValues(256)
                        lu.SetRange(representation["Interval"][0] /
                                    1e6, representation["Interval"][1] / 1e6)
                        for key in range(256):
                            color = Representation.ColorRampSample(
                                colors, key / 255.0)
                            lu.SetTableValue(key, color[0], color[1], color[2])

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

                        nonlocal currentLegendCount
                        sca.SetPosition(0.05 + 0.2 * (currentLegendCount %
                                        3), int(currentLegendCount / 3) * 0.1)
                        sca.SetWidth(0.175)
                        sca.SetHeight(0.125)
                        currentLegendCount += 1
                        actors[file] = sca
                        plotter.add_actor(sca)

                        display = representation["Display"]

                        # Store the values
                        # Değerleri sakla
                        nonlocal displayValues, localNames
                        for adm1 in adm1s.keys():
                            displayValues[adm1] = relation["Data"][adm1]

                        for name in representation["LocalNames"]:
                            localNames[name] = representation["LocalNames"][name]

                        for key in display:
                            for adm1 in adm1s.keys():
                                if key in display:
                                    displayValues[adm1][display[key]
                                                        ] = displayValues[adm1][key]
                                    del displayValues[adm1][key]

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
                    case "MultiRelational":

                        representation = relation["Representation"]
                        meshes = {}
                        for key in representation["Map"]:
                            val = Representation.BuildADM(
                                representation["Map"][key])
                            for a in val:
                                temp = []
                                for b in val[a]:
                                    temp += b
                                meshes[key] = temp
                        initKey = relation["Init"]
                        _data = relation["Data"]
                        centers = {}
                        meshesAndColors = Representation.RepresentValuesWithColors(
                            meshes, {key: _data[key][initKey] for key in _data if initKey in _data[key]}, representation["Colors"])
                        for key in meshesAndColors:
                            subactors = []
                            _temp = []
                            for mesh in meshesAndColors[key]:
                                actor = plotter.add_mesh(
                                    meshesAndColors[key][0], color=meshesAndColors[key][1])
                                subactors.append(actor)
                                for v in meshesAndColors[key][0].vertices:
                                    _temp.append(v)
                                centers[key] = list(sum(_temp) / len(_temp))
                            actors[key] = subactors
                        for c in centers.values():
                            sphere = tm.creation.icosphere(
                                radius=0.15)
                            sphere.apply_translation(c)
                            sphere.apply_translation([0, 0, 0.4])
                            plotter.add_mesh(sphere, color=[0, 0, 0])

                        for key in representation["LocalNames"]:
                            localNames[key] = representation["LocalNames"][key]
                        arrows: list = representation["Arrows"]
                        for arrow in arrows:
                            start, end = copy.deepcopy(centers[arrow[0]]), copy.deepcopy(
                                centers[arrow[1]])
                            start[2] += 0.4
                            end[2] += 0.4
                            arrow_shape = vtk.vtkLineSource()
                            arrow_shape.SetPoint1(start)
                            arrow_shape.SetPoint2(end)

                            mapper = vtk.vtkPolyDataMapper()
                            mapper.SetInputConnection(
                                arrow_shape.GetOutputPort())

                            actor = vtk.vtkActor()
                            actor.SetMapper(mapper)

                            renderer.AddActor(actor)

            for file in selectedFiles:
                ShowData(file, lang=lang)
            # Show the plotter window
            # Çizim penceresini göster
            ren_win.MakeCurrent()

            plotter.show()

            CreateGraphAndDraw()

        View()

    case "data edit":

        # To keep the counter
        # Sayaç tutmak için
        counter = 0

        # To keep the selected file
        # Seçilen dosyayı tutmak için
        files = os.listdir("Countries")
        selectedFile = ""
        selectedColor = ""

        # To keep the save unit as
        # Kaydedilecek birimi tutmak için
        saveUnitAs = ""

        # To keep the windows
        # Pencereleri tutmak için
        mainWindow = None
        dataWindow = None

        # To keep the input data
        # Giriş verisini tutmak için
        inputData: list[dict] = []

        # To keep the keys
        # Anahtarları tutmak için
        keyUI: dict[str: []] = {}

        # Callbacks
        # Geri çağrılar
        def SetSaveUnitAs(sender):
            global saveUnitAs
            saveUnitAs = dpg.get_value(sender)

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
                label="key", parent=mainWindow), dpg.add_combo(label="type", items=["int", "float", "str", "date"], parent=mainWindow),
                dpg.add_button(label="Remove", callback=lambda: RemoveKey(key), parent=mainWindow)]
            counter += 1

        def RunDataEditScreen():
            global dataWindow, inputData
            dpg.delete_item(dataWindow)
            inputData = []
            pos = dpg.get_item_rect_size(mainWindow)
            dataWindow = dpg.add_window(
                label="Data", width=500, height=500, pos=(pos[0], 0), no_resize=True, no_move=True)
            units = Data.GetUnitNames(selectedFile)
            valid = 0
            for unit in units:
                dpg.add_button(label=unit, parent=dataWindow)

                temp = {saveUnitAs: unit}
                for i in range(counter):
                    key = str(i)
                    if key in keyUI:
                        name = dpg.get_value(keyUI[key][0])
                        match dpg.get_value(keyUI[key][1]):
                            case "int":
                                dpg.add_input_int(
                                    label=name, parent=dataWindow, callback=InputData, user_data=(valid, name))
                            case "float":
                                dpg.add_input_float(
                                    label=name, parent=dataWindow, callback=InputData, user_data=(valid, name))
                            case "str":
                                dpg.add_input_text(
                                    label=name, parent=dataWindow, callback=InputData, user_data=(valid, name), multiline=True)
                        temp[name] = None
                valid += 1
                inputData.append(temp)
            dpg.add_button(label="Save", callback=lambda: SaveData(),
                           parent=dataWindow, width=100, height=30)

        def InputData(sender, app_data, user_data: tuple):
            global inputData
            inputData[user_data[0]][user_data[1]] = dpg.get_value(sender)

        def RemoveKey(index):
            global keyUI
            for ui in keyUI[str(index)]:
                dpg.delete_item(ui)
            del keyUI[str(index)]

        def RunKeyEditScreen():
            dpg.create_context()
            dpg.create_viewport()
            dpg.setup_dearpygui()

            SetFont()

            global mainWindow, files, saveUnitAs

            mainWindow = dpg.add_window(
                label="Geopedia", width=500, height=500, no_resize=True, no_move=True)

            dpg.add_text("Save unit as :", parent=mainWindow)
            dpg.add_same_line(parent=mainWindow)
            dpg.add_input_text(callback=SetSaveUnitAs,
                               parent=mainWindow)

            dpg.add_text("Select a file :", parent=mainWindow)
            dpg.add_same_line(parent=mainWindow)
            dpg.add_combo(items=files, callback=SelectFile,
                          parent=mainWindow)

            dpg.add_button(label="Generate data", callback=lambda: RunDataEditScreen(),
                           parent=mainWindow, width=100, height=30)
            dpg.add_same_line(parent=mainWindow)
            dpg.add_button(label="Add key", callback=lambda: AddKey(),
                           parent=mainWindow, width=100, height=30)

            dpg.show_viewport()
            dpg.start_dearpygui()
            dpg.destroy_context()

        def SaveData():
            global saveUnitAs, inputData
            with open("Data/test.json", "w") as file:
                json.dump(inputData, file)

        RunKeyEditScreen()
    case "relation edit":

        # dearpygui related
        # dearpygui ile ilgili
        mainWindow: int
        nameSection: int
        descriptionSection: int

        def RunRelationEditWindow():
            dpg.create_context()
            dpg.create_viewport()
            dpg.setup_dearpygui()

            SetFont()

            global mainWindow, nameSection, descriptionSection

            mainWindow = dpg.add_window(
                label="Relation Edit", width=500, height=500)

            dpg.add_button(label="Save", callback=lambda: SaveRelation(
            ), parent=mainWindow)

            def ToggleNameSection():
                shown = dpg.is_item_shown(nameSection)
                if shown:
                    dpg.hide_item(nameSection)
                else:
                    dpg.show_item(nameSection)

            dpg.add_button(
                label="Names", callback=lambda: ToggleNameSection(), parent=mainWindow)

            nameSection = dpg.add_group(label="Name", parent=mainWindow)
            dpg.add_button(label="Add Name", callback=lambda: AddName(),
                           parent=nameSection)

            group = dpg.add_group(parent=nameSection, horizontal=True)
            dpg.add_text(default_value="Default", parent=group)
            dpg.add_input_text(parent=group, callback=SetNameDefault)

            dpg.show_viewport()
            dpg.start_dearpygui()
            dpg.destroy_context()

        # XML related
        # XML ile ilgili
        relation = xml.etree.ElementTree.Element("Relation")

        def SaveRelation():
            tree = xml.etree.ElementTree.ElementTree(relation)
            tree.write("Relations/test.xml")

        name = xml.etree.ElementTree.SubElement(relation, "Name")
        name.attrib["default"] = ""

        def SetNameDefault(sender):
            global name
            name.attrib["default"] = dpg.get_value(sender)

        def AddName():
            global nameSection, name
            se = xml.etree.ElementTree.SubElement(name, "Text")

            def SetValue(sender):
                se.text = dpg.get_value(sender)

            def SetLang(sender):
                se.attrib["lang"] = dpg.get_value(sender)

            group = dpg.add_group(parent=nameSection, horizontal=True)
            dpg.add_text(default_value="lang", parent=group)
            dpg.add_input_text(parent=group,
                               callback=SetLang, width=50)
            dpg.add_text(default_value="text", parent=group)
            dpg.add_input_text(parent=group,
                               callback=SetValue, height=200)

            def RemoveName():
                dpg.delete_item(item=group)
                name.remove(se)

            dpg.add_button(
                label="Remove", callback=lambda: RemoveName(), parent=group)

        description = xml.etree.ElementTree.SubElement(relation, "Description")
        description.attrib["default"] = ""

        provider = xml.etree.ElementTree.SubElement(relation, "Provider")

        data = xml.etree.ElementTree.SubElement(relation, "Data")

        representation = xml.etree.ElementTree.SubElement(
            relation, "Representation")

        RunRelationEditWindow()
