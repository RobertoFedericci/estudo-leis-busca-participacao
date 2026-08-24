# -*- coding: utf-8 -*-
"""Interesse de busca por unidade da federação, tema a tema.

O Trends devolve, para cada consulta, um valor de 0 a 100 por estado. Esse
valor é a FRAÇÃO das buscas do estado dedicada àquele termo, não o volume
absoluto — já vem corrigido pelo tamanho do estado, de modo que São Paulo não
lidera por ser grande.

Para chegar a um índice geográfico do tema, cada matéria é ponderada pelo seu
índice de busca nacional (o `nivel` da coleta principal), senão uma matéria
minúscula pesaria tanto quanto a maior do tema.

Saída: dados/<tema>/geo.json
"""

import importlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trends_client import TrendsClient, TrendsError

TIMEFRAME = os.environ.get("TIMEFRAME", "2016-01-01 2026-08-16")
TEMAS = {
    "meio-ambiente": "topicos_meio_ambiente",
    "economia": "topicos_economia",
    "saude": "topicos_saude",
    "seguranca": "topicos_seguranca",
}


def main():
    cli = TrendsClient(cache_dir="dados/cache_trends", min_interval=2.0)
    for slug, modulo in TEMAS.items():
        caminho = f"dados/{slug}/dados.json"
        if not os.path.exists(caminho):
            print(f"{slug}: sem dados.json, pulando")
            continue
        with open(caminho, encoding="utf-8") as fh:
            dados = json.load(fh)
        saida_path = f"dados/{slug}/geo.json"
        saida = {}
        if os.path.exists(saida_path):
            with open(saida_path, encoding="utf-8") as fh:
                saida = json.load(fh)

        com_sinal = [t for t in dados["topicos"] if t["nivel"] > 0]
        print(f"\n=== {slug}: {len(com_sinal)} matérias com sinal")
        for i, t in enumerate(com_sinal, 1):
            if t["id"] in saida:
                continue
            try:
                regioes = cli.interest_by_region(t["query"], TIMEFRAME)
            except TrendsError as exc:
                print(f"  {i:2d}/{len(com_sinal)} {t['id']:<14} falhou ({exc})")
                continue
            if not any(regioes.values()):
                print(f"  {i:2d}/{len(com_sinal)} {t['id']:<14} sem sinal regional")
                saida[t["id"]] = None
            else:
                topo = max(regioes.items(), key=lambda kv: kv[1])
                saida[t["id"]] = {"nivel": t["nivel"], "regioes": regioes}
                print(f"  {i:2d}/{len(com_sinal)} {t['id']:<14} lidera {topo[0][3:]}")
            with open(saida_path, "w", encoding="utf-8") as fh:
                json.dump(saida, fh, ensure_ascii=False)
        medidos = sum(1 for v in saida.values() if v)
        print(f"  -> {saida_path} ({medidos} matérias com perfil regional)")


if __name__ == "__main__":
    main()
