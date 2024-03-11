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

# To get the data from the .xml file
# .xml dosyasından veri almak için


def GetRelationalData(name: str, lang: str = None) -> dict:
    if ".xml" not in name:
        name += ".xml"

    # Get data from .xml
    # .xml dosyasından veri al
    tree = ET.parse(open("Relations\\"+name, encoding="utf-8"))
    root = tree.getroot()

    # Create a dictionary to store the data
    # Veriyi saklamak için bir sözlük oluştur
    data = {}

    # Get the name and description of the relation
    # İlişkinin adını ve açıklamasını al

    # If the language is not specified, get the default language
    # Dil belirtilmemişse, varsayılan dili al
    if lang is None:
        default = root.find("Name").attrib["default"]
        for child in root.find("Name").findall("Text"):
            if child.attrib["language"] == default:
                data["Name"] = child.text
        default = root.find("Description").attrib["default"]
        for child in root.find("Description").findall("Text"):
            if child.attrib["language"] == default:
                data["Description"] = child.text

    # If the language is specified, get the data in that language
    # Dil belirtilmişse, o dildeki veriyi al
    else:
        for child in root.find("Name").findall("Text"):
            if child.attrib["language"] == lang:
                data["Name"] = child.text
        for child in root.find("Description").findall("Text"):
            if child.attrib["language"] == lang:
                data["Description"] = child.text

    # Get the filters
    # Filtreleri al
    filters = {}
    for child in root.find("Data").findall("Filter"):
        filters[child.attrib["key"]] = [
            s.replace(" ", "") for s in child.text.splitlines() if not s.isspace() and s != ""]

    # Get the data source
    # Veri kaynağını al
    j = json.load(
        open("Data\\"+root.find("Data").attrib["source"], encoding="utf-8"))

    filteredData = {}

    # If there are no filters, get all the data
    # Filtre yoksa, tüm veriyi al
    if len(filters) == 0:
        for entry in j:
            filteredData[entry[root.find("Data").attrib["by"]]] = entry

    # Filter the data
    # Veriyi filtrele
    else:
        for filter in filters:
            for key in filters[filter]:
                for entry in j:
                    if entry[filter] == key:
                        filteredData[key] = entry
                        break

    excluders = {e.attrib["key"]:
                 [t.replace(" ", "") for t in e.text.splitlines()
                  if not str.isspace(t) and t != ""]
                 for e in root.find("Data").findall(
        "Exclude") if "key" in e.attrib}

    for ex_0 in excluders:
        for ex_1 in excluders[ex_0]:
            for datum in list(filteredData.values()):
                if datum[ex_0] in ex_1:
                    del filteredData[ex_1]

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
        for entry in filteredData:
            for key in list(filteredData[entry]):
                if key not in toGet:
                    del filteredData[entry][key]
                    continue
                if key in convert:
                    filteredData[entry][key] = Convert(
                        filteredData[entry][key], convert[key])
                if key == wanted:
                    realData.append(filteredData[entry][key])

    (realData)

    # Add the filtered data to the dictionary
    # Filtrelenmiş veriyi sözlüğe ekle
    data["Data"] = filteredData
    representation = {
        "Colors": [[float(u) / 255.0 for u in t.text.split(" ")] for t in root.find("Representation").findall("Color")],
        "Value": root.find("Representation").attrib["value"],
        "Map": root.find("Representation").attrib["map"],
        "Interval": (min(realData), max(realData))
    }

    data["Representation"] = representation

    return data
