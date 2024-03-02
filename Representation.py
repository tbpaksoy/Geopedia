import xml.etree.ElementTree as ET
import json
import trimesh as tm


def RepresentValueWithColor(meshes: dict, values: dict, interval: list = [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]) -> dict:
    # Normalize the values
    # Değerleri normalize et
    minaVal, maxVal = min(values.values()), max(values.values())
    normalized = {}
    for key in values.keys():
        normalized[key] = (values[key] - minaVal) / (maxVal - minaVal)

    # Create the color representation
    # Renk temsilini oluştur
    representation = {}

    # Create the color representation
    # Renk temsilini oluştur
    colorGap = [(interval[1][i] - interval[0][i]) for i in range(3)]
    for key in normalized.keys():
        print(key)
        if not key in meshes:
            continue
        color = [(normalized[key] - interval[0][i])/colorGap[i]
                 for i in range(3)]
        representation[key] = (meshes[key], color)

    # Return the representation
    # Temsili döndür
    return representation
