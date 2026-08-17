# -*- coding: utf-8 -*-
"""Baixa a base de processos legislativos do Senado Federal (2017-2026).

Fonte oficial: legis.senado.leg.br/dadosabertos, endpoint /processo?ano=AAAA.
São ~4 MB por ano; os arquivos ficam em dados/senado/ e não vão para o
repositório (ver .gitignore) — o que se versiona são os resultados derivados,
em dados/dados.json e dados/consultas.json.

É deste conjunto que sai o universo do estudo: as matérias substantivas
aprovadas pelo Senado, das quais as de tema ambiental estão em scripts/topicos.py.

Uso, a partir da raiz do repositório:
    python scripts/baixar_senado.py
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

ANOS = range(2017, 2027)
DESTINO = os.environ.get("BASE_SENADO", "dados/senado")
URL = "https://legis.senado.leg.br/dadosabertos/processo?ano={}"


def baixar(ano, destino):
    caminho = os.path.join(destino, f"processo_{ano}.json")
    if os.path.exists(caminho):
        print(f"  {ano}: já existe, pulando")
        return True
    req = urllib.request.Request(
        URL.format(ano),
        headers={"Accept": "application/json", "User-Agent": "estudo-leis-ambientais"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            dados = json.load(r)
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        print(f"  {ano}: falhou ({exc})")
        return False
    with open(caminho, "w", encoding="utf-8") as fh:
        json.dump(dados, fh, ensure_ascii=False)
    print(f"  {ano}: {len(dados):>5} processos, "
          f"{os.path.getsize(caminho) / 1e6:.1f} MB")
    return True


def main():
    os.makedirs(DESTINO, exist_ok=True)
    print(f"baixando processos do Senado em {DESTINO}/")
    falhas = []
    for ano in ANOS:
        if not baixar(ano, DESTINO):
            falhas.append(ano)
        time.sleep(1)
    if falhas:
        sys.exit(f"anos não baixados: {falhas}")
    print("ok")


if __name__ == "__main__":
    main()
