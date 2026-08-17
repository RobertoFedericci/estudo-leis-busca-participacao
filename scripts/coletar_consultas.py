# -*- coding: utf-8 -*-
"""Coleta a consulta pública do e-Cidadania (Sim/Não) de cada matéria.

Toda proposição que tramita no Senado fica aberta a opinião pelo e-Cidadania
(Resolução 26/2013). Os totais são renderizados no servidor na página
`visualizacaomateria`, nos spans .contabilizacao-favor / .contabilizacao-contra
— não há API pública para isso, então lemos a página.

Saída: consultas.json  {identificacao: {codigo, sim, nao, total, pct_sim, url}}
"""

import glob
import json
import os
import re
import sys
import time

import requests

from topicos import TOPICOS

# JSONs do endpoint /dadosabertos/processo?ano=AAAA da API do Senado Federal
# (legis.senado.leg.br/dadosabertos), um arquivo por ano: processo_2017.json …
BASE_SENADO = os.environ.get("BASE_SENADO", "dados/senado")
URL = "https://www12.senado.leg.br/ecidadania/visualizacaomateria?id={}"
OUT = os.environ.get("OUT", "dados/consultas.json")

RE_FAVOR = re.compile(r'class="contabilizacao-favor"[^>]*>([\d.]+)<')
RE_CONTRA = re.compile(r'class="contabilizacao-contra"[^>]*>([\d.]+)<')


def num(txt):
    return int(txt.replace(".", ""))


def mapa_codigos():
    """identificacao -> codigoMateria, a partir dos JSONs já baixados do Senado."""
    m = {}
    for f in sorted(glob.glob(os.path.join(BASE_SENADO, "processo_*.json"))):
        with open(f, encoding="utf-8") as fh:
            for o in json.load(fh):
                ident = o.get("identificacao")
                cod = o.get("codigoMateria")
                if ident and cod:
                    m.setdefault(ident, cod)
    return m


def main():
    codigos = mapa_codigos()
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9",
    })

    saida = {}
    if os.path.exists(OUT):  # retomável
        with open(OUT, encoding="utf-8") as fh:
            saida = json.load(fh)

    for i, t in enumerate(TOPICOS, 1):
        ident = t[0]
        if ident in saida:
            continue
        cod = codigos.get(ident)
        if not cod:
            print(f"  {i:2d}/{len(TOPICOS)} {ident:<14} sem codigoMateria na base")
            saida[ident] = None
            continue
        url = URL.format(cod)
        try:
            r = s.get(url, timeout=40)
            r.raise_for_status()
        except requests.RequestException as exc:
            print(f"  {i:2d}/{len(TOPICOS)} {ident:<14} erro: {exc}")
            continue
        mf, mc = RE_FAVOR.search(r.text), RE_CONTRA.search(r.text)
        if not (mf and mc):
            print(f"  {i:2d}/{len(TOPICOS)} {ident:<14} sem bloco de votos")
            saida[ident] = {"codigo": cod, "sim": None, "nao": None, "url": url}
        else:
            sim, nao = num(mf.group(1)), num(mc.group(1))
            total = sim + nao
            saida[ident] = {
                "codigo": cod,
                "sim": sim,
                "nao": nao,
                "total": total,
                "pct_sim": round(100 * sim / total, 1) if total else None,
                "url": url,
            }
            print(f"  {i:2d}/{len(TOPICOS)} {ident:<14} sim {sim:>7,} | "
                  f"não {nao:>7,} | total {total:>7,}")
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump(saida, fh, ensure_ascii=False, indent=1)
        time.sleep(1.2)

    com = [v for v in saida.values() if v and v.get("total")]
    print(f"ok -> {OUT} ({len(com)} matérias com consulta, "
          f"{sum(v['total'] for v in com):,} votos no total)")


if __name__ == "__main__":
    sys.exit(main())
