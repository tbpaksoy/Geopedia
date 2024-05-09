import xml.etree.ElementTree as ET
import json
import csv
import math

# To convert values to the desired type
# Değerleri istenilen tipte çevirmek için


def Convert(value, type: str):
    temp = str(value)
    match type:
        case "integer" | "int" | "integral":
            try:
                return int(temp.replace(",", "").replace(" ", ""))
            except:
                return 0
        case "float" | "real":
            try:
                return float(temp.replace(",", "").replace(" ", ""))
            except:
                return 0.0
        case "string" | "str":
            return temp


evaluators = {"sin": math.sin, "log": math.log, "exp": math.exp, "sqrt": math.sqrt,
              "abs": abs, "ceil": math.ceil, "floor": math.floor, "round": round}

# To filter the data
# Veriyi filtrelemek için


def FilterData(data: dict, key: str, filter: str | int | float | list[str], operation: str = None) -> dict:
    try:
        filter = Convert(filter, "float")
    except:
        pass
    result = {}
    match operation:
        case None | "equal" | "equals" | "=" | "==":
            if isinstance(filter, list[str]):
                for entry in data:
                    if data[entry][key] in filter:
                        result[entry] = data[entry]
            else:
                for entry in data:
                    if data[entry][key] == filter:
                        result[entry] = data[entry]
        case "not equal" | "not equals" | "!=" | "≠" | "!=":
            if isinstance(filter, list[str]):
                for entry in data:
                    if data[entry][key] not in filter:
                        result[entry] = data[entry]
            else:
                for entry in data:
                    if data[entry][key] != filter:
                        result[entry] = data[entry]
        case "greater" | "greater than" | ">":
            for entry in data:
                value = Convert(data[entry][key], "float")
                if value > filter:
                    result[entry] = data[entry]
        case "less" | "less than" | "<":
            for entry in data:
                value = Convert(data[entry][key], "float")
                if value < filter:
                    result[entry] = data[entry]
        case "greater or equal" | "greater than or equal" | "≥" | ">=":
            for entry in data:
                value = Convert(data[entry][key], "float")
                if value >= filter:
                    result[entry] = data[entry]
        case "less or equal" | "less than or equal" | "≤" | "<=":
            for entry in data:
                value = Convert(data[entry][key], "float")
                if value <= filter:
                    result[entry] = data[entry]
    return result

# To get the data from the .xml file
# .xml dosyasından veri almak için


def GetRelationalData(name: str, lang: str = None) -> dict:
    # If the file name does not contain ".xml", add it
    # Dosya adı ".xml" içermiyorsa, ekle
    if not name.endswith(".xml"):
        name += ".xml"

    processedData = {}

    # Get data from .xml
    # .xml dosyasından veri al
    tree = ET.parse(open("Relations\\"+name, encoding="utf-8"))
    root = tree.getroot()

    # Create a dictionary to store the data
    # Veriyi saklamak için bir sözlük oluştur
    result = {}
    default = root.attrib["default"]
    # If the language is not specified, get the default language
    # Dil belirtilmemişse, varsayılan dili al
    if lang is None:
        lang = default
        for child in root.find("Name").findall("Text"):
            if ("language" in child.attrib and child.attrib["language"] == default) or ("lang" in child.attrib and child.attrib["lang"] == default):
                result["Name"] = child.text
        lang = default = root.find("Description").attrib["default"]
        for child in root.find("Description").findall("Text"):
            if ("language" in child.attrib and child.attrib["language"] == default) or ("lang" in child.attrib and child.attrib["lang"] == default):
                result["Description"] = child.text

    # If the language is specified, get the data in that language
    # Dil belirtilmişse, o dildeki veriyi al
    else:
        for child in root.find("Name").findall("Text"):
            if ("language" in child.attrib and child.attrib["language"] == default) or ("lang" in child.attrib and child.attrib["lang"] == default):
                result["Name"] = child.text
        for child in root.find("Description").findall("Text"):
            if child.attrib["language"] == lang:
                result["Description"] = child.text

    # Get the filters
    # Filtreleri al
    filters = []
    for child in root.find("Data").findall("Filter"):
        filters.append(
            {
                "key": child.attrib["key"],
                "filter": child.text,
                "operation": child.attrib["operation"] if "operation" in child.attrib else None
            })

    sourceFile = "Data\\"+root.find("Data").attrib["source"]

    # Get the excluders and includers
    # Hariç tutucuları ve dahil edicileri al
    excluders = {e.attrib["key"]:
                         [t.replace(" ", "") for t in e.text.splitlines()
                          if not str.isspace(t) and t != ""]
                 for e in root.find("Data").findall(
        "Exclude") if "key" in e.attrib}
    includers = {e.attrib["key"]: [t.replace(" ", "") for t in e.text.splitlines() if not str.isspace(t) and t != ""] for e in root.find("Data").findall(
        "Include") if "key" in e.attrib}

    # Get the data types to get
    # Alınacak veri tiplerini al
    toGet = [g.attrib["key"] for g in root.find("Data").findall("Get")]
    convert = {g.attrib["key"]: g.attrib["convert"]
               for g in root.find("Data").findall("Get") if "convert" in g.attrib}

    # Get the wanted data type
    # İstenen veri tipini al
    realData = []

    match sourceFile.split(".")[1]:
        # If the source file is a .json file
        # Kaynak dosyası .json dosyasıysa
        case "json":
            # Get the data source
            # Veri kaynağını al
            j = json.load(
                open(sourceFile, encoding="utf-8"))

            for entry in j:
                processedData[entry[root.find("Data").attrib["by"]]] = entry

        # If the source file is a .csv file
        # Kaynak dosyası .csv dosyasıysa
        case "csv":
            c = csv.reader(open(sourceFile, encoding="utf-8"))

            keys = next(c)
            keyIndices = {key: keys.index(key) for key in keys}
            toGet = [g.attrib["key"] for g in root.find("Data").findall("Get")]
            for indices in keyIndices:
                if indices not in toGet:
                    keys.remove(indices)
            for row in c:

                temp = {}
                for key in keys:
                    if key in keyIndices.keys():
                        temp[key] = row[keyIndices[key]]
                processedData[row[0]] = temp

    # Convert the data to the desired type
    # Veriyi istenilen tipte çevir
    for c in convert:
        for entry in processedData:
            processedData[entry][c] = Convert(
                processedData[entry][c], convert[c])

    # Exclude the data that should not be included
    # Dahil edilmemesi gereken verileri hariç tut
    for ex_0 in excluders:
        for ex_1 in excluders[ex_0]:
            for datum in list(processedData.values()):
                if datum[ex_0] in ex_1:
                    del processedData[ex_1]

    # Include the data that should be included
    # Dahil edilmesi gereken verileri dahil et
    for in_0 in includers:
        for in_1 in includers[in_0]:
            if in_1 not in processedData:
                for datum in list(j):
                    if datum[in_0] in in_1:
                        processedData[in_1] = datum

    # Filter the data
    # Veriyi filtrele
    for filter in filters:
        processedData = FilterData(
            processedData, filter["key"], filter["filter"], filter["operation"] if "operation" in filter else None)

    # Get the wanted data type
    # İstenen veri tipini al
    wanted = root.find("Representation").attrib["value"]

    # To calculate custom values
    # Özel değerleri hesaplamak için
    for calc in [o for o in root.find("Data").findall("Calculate") if "key" in o.attrib]:
        calcText = calc.text
        split = calcText.split("%")
        for key in processedData:
            toCalc = ""
            for i in range(len(split)):
                if i % 2 == 0:
                    toCalc += split[i]
                else:
                    if split[i] in processedData[key]:
                        toCalc += str(processedData[key][split[i]])
                    else:
                        toCalc += split[i]
            processedData[key][calc.attrib["key"]] = eval(toCalc)

    # To display keys in regular and in different language texts.
    # Anahtarları düzgün ve farklı dilde ki metinler ile görüntülemek için.
    display = {}
    for d in [o for o in root.find("Data").findall("Display") if "key" in o.attrib]:
        if ("lang" in d.attrib and d.attrib["lang"] == lang) or ("language" in d.attrib and d.attrib["language"] == lang):
            display[d.attrib["key"]] = d.text

    # If there are data types to get, filter the data
    # Alınacak veri tipleri varsa, veriyi filtrele
    if len(toGet) > 0:
        for entry in processedData:
            for key in list(processedData[entry]):
                if key not in toGet and key not in [o.attrib["key"] for o in root.find("Data").findall("Calculate") if "key" in o.attrib]:
                    del processedData[entry][key]
                    continue
                if key in convert:
                    processedData[entry][key] = Convert(
                        processedData[entry][key], convert[key])
                if key == wanted:
                    realData.append(processedData[entry][key])

    representation = {
        "Colors": {float(se.attrib["key"]) if "." in se.attrib["key"] else int(se.attrib["key"]): [float(u) if "." in u else float(u) / 255.0 for u in se.text.split(" ")] for se in root.find("Representation").findall("Color")},
        "Value": root.find("Representation").attrib["value"],
        "Map": root.find("Representation").attrib["map"],
        "Interval": (min(realData), max(realData)),
        "Display": display,
        "Borders": [(b.attrib["source"], float(b.attrib["width"]), [int(c) for c in b.attrib["color"].split(" ")]) for b in root.find("Representation").findall("Borders") if "source" in b.attrib and "width" in b.attrib and "color" in b.attrib]
    }
    result["Representation"] = representation

    # Add the filtered data to the dictionary
    # Filtrelenmiş veriyi sözlüğe ekle
    result["Data"] = processedData
    return result

# To get the names of the units in the .geojson file
# .geojson dosyasındaki birimlerin adlarını almak için


def GetUnitNames(file: str) -> list[str]:
    if ".geojson" not in file:
        file += ".geojson"
    j = json.load(open("Countries\\"+file, encoding="utf-8"))
    return [i["properties"]["shapeName"] for i in j["features"]]
