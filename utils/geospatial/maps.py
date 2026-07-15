"""
Funções para carregamento e consulta de mapas.
"""


import json

from numpy import array
from shapely.geometry import Point, Polygon

from utils.config import MAPAS


def verificar_insercao(valor_atual: str, coords: Point, mapa: dict) -> str:
    """Retorna os polígonos do mapa que contêm as coordenadas informadas."""
    novo_valor = ""
    for poligono in mapa:
        if mapa[poligono].contains(coords):
            novo_valor += f'{poligono},'

    if not novo_valor:
        return f'{valor_atual}F.A.A.,'

    return f'{valor_atual}{novo_valor}'


def gerar_mapas() -> dict[str, dict[str, Polygon]]:
    """Carrega os mapas configurados e suas geometrias em memória."""
    mapas: dict[str, dict[str, Polygon]] = {}
    for _mapa in MAPAS:
        with open(MAPAS[_mapa], 'r', encoding='utf-8') as file:
            file_data = ""
            mapa = {}
            for line in file.readlines():
                file_data += line
            features = json.loads(file_data)['features']
            for feature in features:
                geometry = feature['geometry']
                if geometry['type'] == 'Polygon':
                    name = feature['properties']['name']
                    coordinates = geometry['coordinates'][0]
                    trimmed_coordinates = []
                    for coordinate in coordinates:
                        trimmed_coordinates.append(
                            [coordinate[0], coordinate[1]]
                        )
                    mapa[name] = Polygon(array(trimmed_coordinates))

            mapas[_mapa] = mapa
    return mapas
