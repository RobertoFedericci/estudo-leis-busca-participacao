# -*- coding: utf-8 -*-
"""Coleta o Google Trends (BR) dos tópicos legislativos ambientais e põe todas
as curvas numa escala comum, para poder empilhá-las num único gráfico.

O problema: o Trends normaliza cada consulta de 0 a 100 DENTRO da requisição.
Duas curvas de requisições diferentes não são comparáveis. Solução em 3 passos:

  1. ÂNCORAS  – uma requisição com três termos de magnitudes muito diferentes
                fixa a régua global (âncora forte = 100).
  2. NÍVEIS   – cada grupo de 4 tópicos é consultado junto de uma âncora; o
                máximo do tópico dividido pelo da âncora dá seu nível global.
                Se o grupo inteiro zerar contra a âncora forte, repete com uma
                mais fraca (ganho de resolução na cauda).
  3. FORMATO  – cada tópico também é consultado sozinho, o que devolve a curva
                em resolução cheia (0-100). A série final é
                    solo(t) / 100 * nivel_global.

Saída: dados.json, consumido por gerar_html.py.
"""

import json
import os
import sys

from trends_client import TrendsClient, TrendsError
from topicos import TOPICOS

TIMEFRAME = os.environ.get("TIMEFRAME", "2016-01-01 2026-08-16")
OUT = os.environ.get("OUT", "dados/dados.json")

# âncoras em ordem decrescente de volume. Cada uma é medida contra a anterior
# (não contra a primeira), senão as fracas zeram e a régua se perde.
ANCORAS = [
    "meio ambiente",
    "licenciamento ambiental",
    "manejo integrado do fogo",
    "cota de reserva ambiental",
]

# abaixo deste valor bruto (0-100) o tópico tem pouca resolução e é remedido
# contra a próxima âncora, mais fraca
LIMIAR_RESOLUCAO = 20
# âncora fraca demais dentro do lote: a razão fica instável, descarta a medida
MIN_ANCORA = 5


def serie_max(pontos):
    return max((p["value"] for p in pontos), default=0)


def main():
    cli = TrendsClient(cache_dir="dados/cache_trends", min_interval=2.0)

    # ---------- 1. régua das âncoras (em cadeia) ----------
    print("[1/3] calibrando âncoras…")
    nivel_ancora = {ANCORAS[0]: 100.0}
    for anterior, atual in zip(ANCORAS, ANCORAS[1:]):
        d = cli.interest_over_time([anterior, atual], TIMEFRAME)
        ma = serie_max(d[anterior])
        nivel_ancora[atual] = (
            nivel_ancora[anterior] * serie_max(d[atual]) / ma if ma else 0.0
        )
    for a in ANCORAS:
        print(f"      {a}: nível {nivel_ancora[a]:.4f}")

    # ---------- 2. nível global de cada tópico ----------
    # Cascata: mede todos contra a âncora forte; quem sai com valor bruto baixo
    # (pouca resolução) é remedido contra a âncora seguinte, mais fraca.
    print("[2/3] medindo nível de cada tópico contra as âncoras…")
    niveis = {t[4]: 0.0 for t in TOPICOS}
    melhor_bruto = {t[4]: -1 for t in TOPICOS}
    pendentes = [t[4] for t in TOPICOS]

    for ancora in ANCORAS:
        if not pendentes or nivel_ancora[ancora] <= 0:
            continue
        print(f"  -- âncora '{ancora}' (nível {nivel_ancora[ancora]:.4f}), "
              f"{len(pendentes)} tópicos")
        proximos = []
        grupos = [pendentes[i:i + 4] for i in range(0, len(pendentes), 4)]
        for gi, queries in enumerate(grupos, 1):
            try:
                d = cli.interest_over_time([ancora] + queries, TIMEFRAME)
            except TrendsError as exc:
                print(f"     grupo {gi}: falhou ({exc})")
                proximos.extend(queries)
                continue
            ma = serie_max(d[ancora])
            if ma < MIN_ANCORA:
                print(f"     grupo {gi}: âncora fraca no lote (max {ma}), adiando")
                proximos.extend(queries)
                continue
            fator = nivel_ancora[ancora] / ma
            saida = []
            for q in queries:
                bruto = serie_max(d[q])
                if bruto > melhor_bruto[q]:
                    melhor_bruto[q] = bruto
                    niveis[q] = bruto * fator
                if bruto < LIMIAR_RESOLUCAO:
                    proximos.append(q)
                saida.append(f"{bruto:3d}->{niveis[q]:.4f}")
            print(f"     grupo {gi}/{len(grupos)}: " + " | ".join(saida))
        pendentes = proximos

    # ---------- 3. formato de cada curva ----------
    print("[3/3] baixando a curva individual de cada tópico…")
    series = {}
    eixo = None
    for i, t in enumerate(TOPICOS, 1):
        q = t[4]
        try:
            d = cli.interest_over_time([q], TIMEFRAME)
            pontos = d[q]
        except TrendsError as exc:
            print(f"  {i:2d}/{len(TOPICOS)} {t[0]:<14} sem dados ({exc})")
            pontos = []
        if pontos and eixo is None:
            eixo = [p["label"] for p in pontos]
        series[q] = pontos
        print(f"  {i:2d}/{len(TOPICOS)} {t[0]:<14} nível {niveis.get(q, 0):7.3f}  "
              f"pontos {len(pontos)}")

    if eixo is None:
        sys.exit("nenhuma série retornou dados")
    n = len(eixo)

    saida = {"timeframe": TIMEFRAME, "eixo": eixo, "topicos": []}
    for ident, ano, virou_norma, ementa, q in TOPICOS:
        pontos = series.get(q) or []
        nivel = niveis.get(q, 0.0)
        if len(pontos) == n:
            valores = [round(p["value"] / 100.0 * nivel, 4) for p in pontos]
        else:  # série vazia ou de tamanho divergente
            valores = [0.0] * n
        saida["topicos"].append({
            "id": ident,
            "ano": ano,
            "virou_norma": virou_norma,
            "ementa": ementa,
            "query": q,
            "nivel": round(nivel, 4),
            "valores": valores,
        })

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(saida, fh, ensure_ascii=False)
    print(f"ok -> {OUT} ({n} pontos, {len(saida['topicos'])} tópicos)")


if __name__ == "__main__":
    main()
