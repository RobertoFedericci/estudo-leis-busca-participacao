# -*- coding: utf-8 -*-
"""Baixa a malha das UFs no IBGE e pré-calcula os caminhos SVG do mapa.

Embutir o GeoJSON cru custaria 251 KB no HTML. Aqui a geometria é projetada,
simplificada e convertida em `path` uma vez só, no servidor: o que vai para a
página é um dicionário {sigla: "M…L…Z"} de poucos KB.

Projeção: equirretangular com correção de longitude por cos(latitude média).
Para a faixa do Brasil a distorção é de ~3%, invisível num mapa deste tamanho,
e evita depender de biblioteca de projeção.

Saída: dados/uf_paths.json
"""

import gzip
import json
import math
import os
import urllib.request

URL = ("https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR"
       "?formato=application/vnd.geo+json&intrarregiao=UF&qualidade=intermediaria")
SAIDA = os.environ.get("SAIDA", "dados/uf_paths.json")
LARGURA, ALTURA = 620.0, 620.0
PRECISAO = 1          # 0,1 px: abaixo do que a tela resolve
DIST_MIN = 1.4        # px: descarta pontos que cairiam quase em cima do anterior
MIN_PONTOS = 5        # descarta ilhotas que virariam um pixel

UF = {
    "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP",
    "17": "TO", "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB",
    "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES",
    "33": "RJ", "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS",
    "51": "MT", "52": "GO", "53": "DF",
}


def aneis(geom):
    if geom["type"] == "Polygon":
        return geom["coordinates"]
    return [anel for poly in geom["coordinates"] for anel in poly]


def main():
    # o IBGE responde gzipado mesmo pedindo identity, e urllib não descomprime
    with urllib.request.urlopen(URL, timeout=120) as r:
        bruto = r.read()
    if bruto[:2] == b"\x1f\x8b":
        bruto = gzip.decompress(bruto)
    malha = json.loads(bruto.decode("utf-8"))

    lons = [c[0] for f in malha["features"] for a in aneis(f["geometry"]) for c in a]
    lats = [c[1] for f in malha["features"] for a in aneis(f["geometry"]) for c in a]
    lat_media = (min(lats) + max(lats)) / 2
    k = math.cos(math.radians(lat_media))

    x0, x1 = min(lons) * k, max(lons) * k
    y0, y1 = -max(lats), -min(lats)
    escala = min(LARGURA / (x1 - x0), ALTURA / (y1 - y0))
    dx = (LARGURA - (x1 - x0) * escala) / 2
    dy = (ALTURA - (y1 - y0) * escala) / 2

    def proj(lon, lat):
        return ((lon * k - x0) * escala + dx, (-lat - y0) * escala + dy)

    paths = {}
    for f in malha["features"]:
        sigla = UF.get(str(f["properties"]["codarea"]))
        if not sigla:
            continue
        partes = []
        for anel in aneis(f["geometry"]):
            pontos, anterior = [], None
            bruto = [proj(lon, lat) for lon, lat in anel]
            for j, (x, y) in enumerate(bruto):
                par = (round(x, PRECISAO), round(y, PRECISAO))
                ultimo = j == len(bruto) - 1
                # mantém o ponto se ele se afasta o bastante do anterior; o
                # último do anel entra sempre, para o contorno fechar
                if anterior is None or ultimo or \
                        abs(par[0] - anterior[0]) + abs(par[1] - anterior[1]) >= DIST_MIN:
                    if par != anterior:
                        pontos.append(par)
                        anterior = par
            if len(pontos) < MIN_PONTOS:
                continue
            partes.append("M" + "L".join(f"{x} {y}" for x, y in pontos) + "Z")
        paths[sigla] = "".join(partes)

    os.makedirs(os.path.dirname(SAIDA) or ".", exist_ok=True)
    with open(SAIDA, "w", encoding="utf-8") as fh:
        json.dump({"largura": LARGURA, "altura": ALTURA, "paths": paths}, fh,
                  ensure_ascii=False)
    print(f"{len(paths)} UFs -> {SAIDA} ({os.path.getsize(SAIDA)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
