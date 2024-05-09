import xml.etree.ElementTree as ET
import json
import trimesh as tm
import pyvista as pv


def BuildADM(file: str, id: int | str | list | None = None) -> dict:
    if not file.endswith(".geojson"):
        file += ".geojson"

    # Get data from .json
    # .json dosyasından veri al
    data = json.load(open("Countries\\"+file, encoding="utf-8"))
    # Get the features
    # Özellikleri al
    features = data["features"]
    query = []

    match id:
        case int():
            query.append(features[id])
        case str():
            for feature in features:
                if feature["properties"]["shapeName"] == id:
                    query.append(feature)
        case list():
            for i in id:
                match i:
                    case int():

                        query.append(features[i])
                    case str():
                        for feature in features:
                            if feature["properties"]["shapeName"] == i:
                                query.append(feature)
        case None:
            for feature in features:
                query.append(feature)
    polygons = {}

    # Get the name and description of the relation
    # İlişkinin adını ve açıklamasını al
    for item in query:
        name = item["properties"]["shapeName"]
        coordinates = item["geometry"]["coordinates"]
        polygons[name] = []
        if isinstance(coordinates[0][0][0], list):
            for border in coordinates:
                polygon = tm.creation.Polygon(border[0])
                polygons[name].append(polygon)
        else:
            polygon = tm.creation.Polygon(coordinates[0])
            polygons[name].append(polygon)

    for key1 in polygons.keys():
        for key2 in polygons.keys():
            if key1 == key2:
                continue

            for i in range(len(polygons[key1])):
                for j in range(len(polygons[key2])):
                    if polygons[key1][i].contains(polygons[key2][j]):
                        polygons[key1][i] = polygons[key1][i].difference(
                            polygons[key2][j])
    return {key: [tm.creation.extrude_polygon(poly, 0.1) for poly in polygons[key]] for key in polygons.keys()}


def BuildADMBorders(file: str, id: int | str | list | None = None) -> dict:
    if not file.endswith(".geojson"):
        file += ".geojson"

    # Get data from .json
    # .json dosyasından veri al
    data = json.load(open("Countries\\"+file, encoding="utf-8"))
    # Get the features
    # Özellikleri al
    features = data["features"]
    query = []

    match id:
        case int():
            query.append(features[id])
        case str():
            for feature in features:
                if feature["properties"]["shapeName"] == id:
                    query.append(feature)
        case list():
            for i in id:
                match i:
                    case int():

                        query.append(features[i])
                    case str():
                        for feature in features:
                            if feature["properties"]["shapeName"] == i:
                                query.append(feature)
        case None:
            for feature in features:
                query.append(feature)

    polyDatas = {}

    # Get the name and description of the relation
    # İlişkinin adını ve açıklamasını al
    for item in query:
        name = item["properties"]["shapeName"]
        coordinates = item["geometry"]["coordinates"]
        polyDatas[name] = []
        if isinstance(coordinates[0][0][0], list):
            for border in coordinates:
                temp = [[point[0], point[1], 0.1] for point in border[0]]
                polyData = pv.lines_from_points(temp, True)
                polyDatas[name].append(polyData)
        else:
            temp = [[point[0], point[1], 0.1] for point in coordinates[0]]
            polyData = pv.lines_from_points(temp, True)
            polyDatas[name].append(polyData)

    return polyDatas

# Represent the values with color
# Değerleri renk ile temsil et


def RepresentValueWithColor(meshes: dict, values: dict, interval: list = [[1.0, 1.0, 1.0], [0.0, 0.0, 0.0]]) -> dict:
    # Normalize the values
    # Değerleri normalize et
    minVal, maxVal = min(values.values()), max(values.values())
    normalized = {}
    if len(values) > 1 and maxVal != minVal:
        for key in values.keys():
            normalized[key] = (values[key] - minVal) / (maxVal - minVal)
    else:
        normalized = {list(values.keys())[0]: 1.0}

    # Create the color representation
    # Renk temsilini oluştur
    representation = {}

    # Create the color representation
    # Renk temsilini oluştur
    colorGap = [(interval[1][i] - interval[0][i]) for i in range(3)]
    for key in normalized.keys():
        if not key in meshes:
            continue
        color = [interval[0][i] + normalized[key] * colorGap[i]
                 for i in range(3)]
        representation[key] = (meshes[key], color)

    # Return the representation
    # Temsili döndür
    return representation


def RepresentValuesWithColors(meshes: dict, values: dict, colors: dict = {0.0: [1.0, 1.0, 1.0], 1.0: [0.0, 0.0, 0.0]}) -> dict:

    # Create the color representation
    # Renk temsilini oluştur
    temp = ColorRamp(values, colors)
    return {key: (meshes[key], temp[key]) for key in values.keys() if key in meshes.keys() and key in temp.keys()}


def ColorRamp(values: dict, colors: dict) -> dict[str: list]:
    maxVal, minVal = max(values.values()), min(values.values())
    for key in list(colors.keys()):
        if isinstance(key, int):
            colors[(key - minVal) / (maxVal - minVal)] = colors[key]
            del colors[key]
    normalized = {key: (values[key] - minVal) / (maxVal - minVal)
                  for key in values.keys()}
    colors = dict(sorted(colors.items()))
    result = {}

    colorKeys = list(colors.keys())
    colorValues = list(colors.values())

    for key in normalized:
        for i in range(len(colors) - 1):
            if normalized[key] >= colorKeys[i] and normalized[key] <= colorKeys[i+1]:
                x, y, z = colorValues[i], colorValues[i+1], normalized[key]
                z = (z - colorKeys[i]) / (colorKeys[i+1] - colorKeys[i])
                result[key] = [x[i] + (z) * (y[i] - x[i])
                               for i in range(3)]
                break
    return result


def ColorRampSample(colorRamp: dict[str: list], value: float) -> list:
    minBound, maxBound = 0, len(colorRamp)-1
    keys = list(colorRamp.keys())
    for i in range(int(len(keys))):
        if value == keys[i]:
            return colorRamp[keys[i]]
        if value > keys[i]:
            minBound = i
        if value < keys[i]:
            maxBound = i
    value = (value - keys[minBound]) / (keys[maxBound] - keys[minBound])
    colors = list(colorRamp.values())
    begin, end = colors[minBound], colors[maxBound]
    result = [begin[j] + value *
              (end[j] - begin[j]) for j in range(3)]
    return result
