import xml.etree.ElementTree as ET
import json


def Convert(value, type: str):
    temp = str(value)
    match type:
        case "integer" | "int" | "integral":
            return int(temp.replace(",", "").replace(" ", ""))
        case "float" | "real":
            return float(temp.replace(",", "").replace(" ", ""))
        case "string" | "str":
            return temp


def GetRelationalData(name: str, lang: str = None) -> dict:

    # Get data from .xml
    # .xml dosyasından veri al
    tree = ET.parse(open("Relations\\"+name+".xml", encoding="utf-8"))
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

    # Get the data types to get
    # Alınacak veri tiplerini al
    toGet = [g.attrib["key"] for g in root.find("Data").findall("Get")]
    convert = {g.attrib["key"]: g.attrib["convert"]
               for g in root.find("Data").findall("Get") if "convert" in g.attrib}
    # If there are data types to get, filter the data
    # Alınacak veri tipleri varsa, veriyi filtrele
    if len(toGet) > 0:
        for entry in filteredData:
            for key in list(filteredData[entry]):
                if key not in toGet:
                    del filteredData[entry][key]
                if key in convert:
                    filteredData[entry][key] = Convert(
                        filteredData[entry][key], convert[key])

    # Add the filtered data to the dictionary
    # Filtrelenmiş veriyi sözlüğe ekle
    data["Data"] = filteredData

    representation = {
        "Colors": [[float(u) / 255.0 for u in t.text.split(" ")] for t in root.find("Representation").findall("Color")],
        "Value": root.find("Representation").attrib["value"],
        "Map": root.find("Representation").attrib["map"]
    }

    data["Representation"] = representation

    return data
