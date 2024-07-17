import xml.etree.ElementTree as ET
import json
import csv
import math
from Graph import LinkFiles

currentXML: str = ""


# To convert values to the desired type
# Değerleri istenilen tipte çevirmek için


def Convert(value: str | dict | list, type: str):
    _value = str(value)
    if type == None or type == "":
        return value
    lambda caster: caster(value)
    match type:
        case "integer" | "int" | "integral":
            caster = int
            _value = _value.replace(",", "").replace(" ", "")
        case "float" | "real":
            caster = float
            _value = _value.replace(",", "").replace(" ", "")
        case "string" | "str":
            caster = str
    match value:
        case dict():
            result = {}
            for key in value:
                result[key] = caster(value[key])
            return result
        case list():
            result = []
            for item in value:
                result.append(caster(item))
            return result
    try:
        return caster(_value)
    except:
        return None


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


def GetRelationalData(root: ET.Element, lang: str = None) -> dict:
    processedData = {}
    # Create a dictionary to store the data
    # Veriyi saklamak için bir sözlük oluştur
    result = {"Type": "Relational"}
    default = root.attrib["default"]
    # If the language is not specified, get the default language
    # Dil belirtilmemişse, varsayılan dili al
    if lang == None:
        lang = default
    for i in root.find("Name").findall("Text"):
        if i.attrib["language"] == lang:
            result["Name"] = i.text
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

    global LinkFiles, currentXML

    LinkFiles(currentXML, sourceFile)

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

    for k in root.find("Data").findall("Key"):
        if "name" not in k.attrib:
            continue
        if "from" in k.attrib and "to" in k.attrib:
            pass
        else:
            for line in k.text.splitlines():
                t = line.strip().split(":")
                if len(t) == 2:
                    if t[0] in processedData:
                        processedData[t[1]] = processedData[t[0]]
                        del processedData[t[0]]
    representation = {
        "Colors": {se.attrib["key"]: [float(t) / 255.0 for t in se.text.split(" ")] for se in root.find("Representation").findall("Color") if "key" in se.attrib},
        "Value": root.find("Representation").attrib["value"],
        "Map": root.find("Representation").attrib["map"],
        "Interval": (min(realData), max(realData)),
        "Display": display,
        "Borders": [(b.attrib["source"], float(b.attrib["width"]), [int(c) for c in b.attrib["color"].split(" ")]) for b in root.find("Representation").findall("Borders") if "source" in b.attrib and "width" in b.attrib and "color" in b.attrib],
        "LocalNames": {ln.attrib["key"]: ln.text for ln in root.find("Representation").findall("LocalName") if "key" in ln.attrib and "lang" in ln.attrib and ln.attrib["lang"] == lang}
    }

    LinkFiles(currentXML, representation["Map"])

    result["Representation"] = representation

    # Add the filtered data to the dictionary
    # Filtrelenmiş veriyi sözlüğe ekle
    result["Data"] = processedData
    return result

# To get the data from the .xml file
# .xml dosyasından veri almak için


def GetMultiRelationalData(root: ET.Element, lang: str = None) -> dict:
    result = {"Type": "MultiRelational"}
    processedData = {}

    groupBy = root.find("Data").find("Group").attrib["by"]

    # Read the data and process it
    # Veriyi oku ve işle
    match root.find("Data").attrib["source"].split(".")[-1]:
        case "csv":
            c = csv.reader(
                open("Data\\"+root.find("Data").attrib["source"], encoding="utf-8"))
            keys = next(c)
            matches = {c.attrib["key"]: {"value": c.attrib["value"], "convert": c.attrib["convert"] if "convert" in c.attrib else None}
                       for c in root.find("Data").findall("Match") if "key" in c.attrib and "value" in c.attrib}
            if len(matches) > 0:
                for row in c:
                    index = keys.index(groupBy)
                    if row[index] not in processedData:
                        processedData[row[index]] = {}
                    for match in matches:
                        key = match
                        value = matches[match]["value"]
                        if "convert" in matches[match]:
                            processedData[row[index]][row[keys.index(key)]] = Convert(
                                row[keys.index(value)], matches[match]["convert"])
                        else:
                            processedData[row[index]][row[keys.index(
                                key)]] = row[keys.index(value)]
            else:
                for row in c:
                    index = keys.index(groupBy)
                    if row[index] not in processedData:
                        processedData[row[index]] = {}
                    for key in keys:
                        if key != groupBy:
                            processedData[row[index]
                                          ][key] = row[keys.index(key)]
            for c in root.find("Data").findall("Convert"):
                for entry in processedData:
                    processedData[entry][c.attrib["key"]] = Convert(
                        processedData[entry][c.attrib["key"]], c.attrib["to"])
    representation = {}
    representation["Colors"] = {se.attrib["key"]: [float(t) / 255.0 for t in se.text.split(
        " ")] for se in root.find("Representation").findall("Color") if "key" in se.attrib}
    representation["Map"] = {m.attrib["key"]: m.attrib["on"] for m in root.find("Representation").findall(
        "Map") if "key" in m.attrib and "on" in m.attrib}
    representation["Values"] = {e: processedData[e] for e in processedData}
    representation["Arrows"] = [(a.attrib["from"], a.attrib["to"]) for a in root.find(
        "Representation").findall("Arrow") if "from" in a.attrib and "to" in a.attrib]
    representation["LocalNames"] = {ln.attrib["key"]: ln.text for ln in root.find("Representation").findall(
        "LocalName") if "key" in ln.attrib and "lang" in ln.attrib and ln.attrib["lang"] == lang}
    result["Init"] = root.find("Representation").attrib["value"]
    result["Data"] = processedData
    result["Representation"] = representation

    return result

# To get the names of the units in the .geojson file
# .geojson dosyasındaki birimlerin adlarını almak için


def GetUnitNames(file: str) -> list[str]:
    if ".geojson" not in file:
        file += ".geojson"
    j = json.load(open("Countries\\"+file, encoding="utf-8"))
    return [i["properties"]["shapeName"] for i in j["features"]]

# To analyze the .xml file
# .xml dosyasını analiz etmek için


def AnalyzeXML(file: str, lang: str = None):
    if not file.startswith("Relations/"):
        file = "Relations/"+file
    if not file.endswith(".xml"):
        file += ".xml"
    xml = ET.parse(open(file, encoding="utf-8"))
    root = xml.getroot()
    global currentXML
    currentXML = file
    match root.tag:
        case "Relation":
            return GetRelationalData(root, lang)
        case "MultiRelation":
            return GetMultiRelationalData(root, lang)
