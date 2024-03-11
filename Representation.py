import xml.etree.ElementTree as ET
import json
import trimesh as tm

# Get administrative division 1 data
# İdari bölüm 1 verisini al


def BuildADM(country: str, id: int | str | list) -> dict:

    # Get data from .json
    # .json dosyasından veri al
    data = json.load(open("Countries\\"+country +
                     ".geojson", encoding="utf-8"))
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

    # Create a dictionary to store the data
    # Veriyi saklamak için bir sözlük oluştur
    data = {}

    # Get the name and description of the relation
    # İlişkinin adını ve açıklamasını al
    for item in query:
        # Get the coordinates
        # Koordinatları al
        coordinates = item["geometry"]["coordinates"]
        meshes = []
        # Check if the borders are multipart
        # Sınırların çok parçalı olup olmadığını kontrol et
        if isinstance(coordinates[0][0][0], list):
            for border in coordinates:
                polygon = tm.creation.Polygon(border[0])
                meshes.append(tm.creation.extrude_polygon(polygon, 0.1))
        else:
            polygon = tm.creation.Polygon(coordinates[0])
            meshes.append(tm.creation.extrude_polygon(polygon, 0.1))
        data[item["properties"]["shapeName"]] = meshes

    return data

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
