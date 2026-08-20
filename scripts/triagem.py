# -*- coding: utf-8 -*-
"""Triagem: ranqueia as matérias de cada tema por volume aproximado de busca.

Economia, saúde e segurança somam 1.262 matérias aprovadas — não há como
escrever à mão uma chave de qualidade para cada uma, nem consultar todas com a
precisão da coleta final. A triagem mede um bigrama extraído da ementa e serve
apenas para escolher as 50 candidatas de cada tema, que depois passam por
curadoria manual. Os números publicados vêm da coleta final, nunca daqui.

Âncora fraca ('licenciamento ambiental') porque termos fortes zeram a cauda:
contra 'diário oficial', 100% dos bigramas testados voltaram zero.

Saída: dados/triagem.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import candidatos as C
from trends_client import TrendsClient, TrendsError

TIMEFRAME = os.environ.get("TIMEFRAME", "2016-01-01 2026-08-16")
OUT = os.environ.get("OUT", "dados/triagem.json")
ANCORA = "licenciamento ambiental"
MIN_ANCORA = 1  # só ranqueia: aceita âncora baixa, ao contrário da coleta final


def main():
    bigramas, por_tema = set(), {}
    for slug, tema in C.TEMAS.items():
        if slug == "meio-ambiente":
            continue
        materias = C.universo(tema)
        por_tema[slug] = len(materias)
        for m in materias:
            q = C.query_triagem(m)
            if len(q) > 4:
                bigramas.add(q)
    bigramas = sorted(bigramas)
    print(f"{sum(por_tema.values())} matérias -> {len(bigramas)} bigramas únicos")

    scores = {}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as fh:
            scores = json.load(fh)
        print(f"retomando: {len(scores)} já medidos")

    cli = TrendsClient(cache_dir="dados/cache_trends", min_interval=2.0)
    pendentes = [b for b in bigramas if b not in scores]
    lotes = [pendentes[i:i + 4] for i in range(0, len(pendentes), 4)]
    for i, lote in enumerate(lotes, 1):
        try:
            d = cli.interest_over_time([ANCORA] + lote, TIMEFRAME)
        except TrendsError as exc:
            print(f"  lote {i}/{len(lotes)}: falhou ({exc})")
            continue
        ma = max((p["value"] for p in d[ANCORA]), default=0)
        if ma < MIN_ANCORA:
            print(f"  lote {i}/{len(lotes)}: âncora zerada, marcando como saturado")
            ma = 1
        for q in lote:
            bruto = max((p["value"] for p in d[q]), default=0)
            scores[q] = round(bruto / ma, 4)
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump(scores, fh, ensure_ascii=False)
        if i % 10 == 0 or i == len(lotes):
            print(f"  lote {i}/{len(lotes)} ({len(scores)}/{len(bigramas)} medidos)")
    print(f"ok -> {OUT}")


if __name__ == "__main__":
    main()
