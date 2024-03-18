import xml.etree.ElementTree as ET
import json
import math

# To perform operations
# İşlemleri gerçekleştirmek için


def Operate(a, b, operation: str):
    result = None
    try:
        match operation:
            case "add" | "addition" | "+":
                result = a + b
            case "subtract" | "subtraction" | "-":
                result = a - b
            case "multiply" | "multiplication" | "*" | "x":
                result = a * b
            case "divide" | "division" | "/" | "÷":
                result = a / b
            case "power" | "exponent" | "^":
                result = a ** b
            case "root" | "nthroot" | "√":
                result = a ** (1 / b)
            case "logarithm" | "log":
                result = math.log(a, b)
            case "modulus" | "mod" | "%":
                result = a % b
    except:
        print("An error occurred while performing the operation.")
    finally:
        return result

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
    if ".xml" not in name:
        name += ".xml"

    # Get data from .xml
    # .xml dosyasından veri al
    tree = ET.parse(open("Relations\\"+name, encoding="utf-8"))
    root = tree.getroot()

    # Create a dictionary to store the data
    # Veriyi saklamak için bir sözlük oluştur
    result = {}

    # Get the name and description of the relation
    # İlişkinin adını ve açıklamasını al

    # If the language is not specified, get the default language
    # Dil belirtilmemişse, varsayılan dili al
    if lang is None:
        default = root.find("Name").attrib["default"]
        for child in root.find("Name").findall("Text"):
            if child.attrib["language"] == default:
                result["Name"] = child.text
        default = root.find("Description").attrib["default"]
        for child in root.find("Description").findall("Text"):
            if child.attrib["language"] == default:
                result["Description"] = child.text

    # If the language is specified, get the data in that language
    # Dil belirtilmişse, o dildeki veriyi al
    else:
        for child in root.find("Name").findall("Text"):
            if child.attrib["language"] == lang:
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

    # Get the data source
    # Veri kaynağını al
    j = json.load(
        open("Data\\"+root.find("Data").attrib["source"], encoding="utf-8"))

    processedData = {}

    for entry in j:
        processedData[entry[root.find("Data").attrib["by"]]] = entry

    # Get the excluders and includers
    # Hariç tutucuları ve dahil edicileri al
    excluders = {e.attrib["key"]:
                 [t.replace(" ", "") for t in e.text.splitlines()
                  if not str.isspace(t) and t != ""]
                 for e in root.find("Data").findall(
        "Exclude") if "key" in e.attrib}
    includers = {e.attrib["key"]: [t.replace(" ", "") for t in e.text.splitlines() if not str.isspace(t) and t != ""] for e in root.find("Data").findall(
        "Include") if "key" in e.attrib}
    for ex_0 in excluders:
        for ex_1 in excluders[ex_0]:
            for datum in list(processedData.values()):
                if datum[ex_0] in ex_1:
                    del processedData[ex_1]
    for in_0 in includers:
        for in_1 in includers[in_0]:
            if in_1 not in processedData:
                for datum in list(j):
                    if datum[in_0] in in_1:
                        processedData[in_1] = datum

    # Get the data types to get
    # Alınacak veri tiplerini al
    toGet = [g.attrib["key"] for g in root.find("Data").findall("Get")]
    convert = {g.attrib["key"]: g.attrib["convert"]
               for g in root.find("Data").findall("Get") if "convert" in g.attrib}
    wanted = root.find("Representation").attrib["value"]
    realData = []

    # If there are data types to get, filter the data
    # Alınacak veri tipleri varsa, veriyi filtrele
    if len(toGet) > 0:
        for entry in processedData:
            for key in list(processedData[entry]):
                if key not in toGet:
                    del processedData[entry][key]
                    continue
                if key in convert:
                    processedData[entry][key] = Convert(
                        processedData[entry][key], convert[key])
                if key == wanted:
                    realData.append(processedData[entry][key])

    for filter in filters:
        processedData = FilterData(
            processedData, filter["key"], filter["filter"], filter["operation"] if "operation" in filter else None)

    # Add the filtered data to the dictionary
    # Filtrelenmiş veriyi sözlüğe ekle
    result["Data"] = processedData
    representation = {
        "Colors": [[float(u) / 255.0 for u in t.text.split(" ")] for t in root.find("Representation").findall("Color")],
        "Value": root.find("Representation").attrib["value"],
        "Map": root.find("Representation").attrib["map"],
        "Interval": (min(realData), max(realData))
    }

    result["Representation"] = representation

    return result

# To get the names of the units in the .geojson file
# .geojson dosyasındaki birimlerin adlarını almak için


def GetUnitNames(file: str) -> list[str]:
    if ".geojson" not in file:
        file += ".geojson"
    j = json.load(open("Countries\\"+file, encoding="utf-8"))
    return [i["properties"]["shapeName"] for i in j["features"]]
