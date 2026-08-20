# -*- coding: utf-8 -*-
"""Lista as N candidatas de cada tema, ordenadas pela triagem, para curadoria.

Entra: dados/triagem.json (scripts/triagem.py) e dados/senado_aprovados.csv
Sai:   imprime identificação, score, situação e ementa — o material a partir do
       qual as chaves finais são escritas à mão em scripts/topicos_<tema>.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import candidatos as C

TRIAGEM = os.environ.get("TRIAGEM", "dados/triagem.json")
TOPO = int(os.environ.get("TOPO", "50"))


def ranking(slug, scores, topo=TOPO):
    materias = C.universo(C.TEMAS[slug])
    pontuadas = []
    for m in materias:
        q = C.query_triagem(m)
        pontuadas.append((scores.get(q, 0.0), q, m))
    pontuadas.sort(key=lambda x: (-x[0], x[2]["identificacao"]))
    return pontuadas[:topo]


def main():
    with open(TRIAGEM, encoding="utf-8") as fh:
        scores = json.load(fh)
    alvo = sys.argv[1:] or ["economia", "saude", "seguranca"]
    for slug in alvo:
        print(f"\n{'='*78}\n{C.TEMAS[slug]} — {TOPO} candidatas por volume de busca\n{'='*78}")
        for score, q, m in ranking(slug, scores):
            norma = "norma" if m["virou_norma"] == "True" else "tramita"
            print(f"{score:7.3f} | {m['identificacao']:<14} | {norma} | [{q}]")
            print(f"          {m['ementa'][:200]}")


if __name__ == "__main__":
    main()
