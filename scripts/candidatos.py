# -*- coding: utf-8 -*-
"""Universo por tema e geração automática de chaves de TRIAGEM.

A triagem serve só para ranquear candidatas: são 1.262 matérias em economia,
saúde e segurança, e não há como escrever à mão uma chave de qualidade para
cada uma. A chave automática extrai da ementa a frase que descreve o objeto da
matéria; o Trends mede essas chaves em lote e as 50 primeiras de cada tema
passam por curadoria manual, que é de onde saem os números publicados.

Viés conhecido e declarado: a triagem favorece matérias cuja ementa contenha
palavras de busca popular, ainda que a matéria em si seja obscura.
"""

import csv
import os
import re

BASE = os.environ.get("SENADO_CSV", "dados/senado_aprovados.csv")

TEMAS = {
    "meio-ambiente": "Meio Ambiente",
    "economia": "Tributário e Economia",
    "saude": "Saúde",
    "seguranca": "Segurança e Justiça",
}

# citações de norma, datas e boilerplate que não descrevem o objeto
RUIDO = [
    r"Lei(?:\s+Complementar)?\s+n[ºo°]?\s*[\d.]+,?\s*de\s+\d+\s+de\s+\w+\s+de\s+\d{4}",
    r"Medida Provis[óo]ria\s+n[ºo°]?\s*[\d.\-]+,?\s*de\s+\d+\s+de\s+\w+\s+de\s+\d{4}",
    r"Decreto[- ]Lei\s+n[ºo°]?\s*[\d.]+,?\s*de\s+\d+\s+de\s+\w+\s+de\s+\d{4}",
    r"n[ºo°]?\s*[\d.]+,?\s*de\s+\d+\s+de\s+\w+\s+de\s+\d{4}",
    r"art\.?\s*[\d.\-ºA-Z]+", r"§\s*[\d.ºA-Z]+", r"inciso\s+[IVXLC]+",
    r"e d[áa] outras provid[êe]ncias\.?", r"\([^)]*\)",
]
ABERTURAS = r"^(Altera|Acrescenta|Modifica|Revoga|Aprova o texto d[aeo]|Aprova|Institui|Dispõe sobre|Estabelece|Cria|Regulamenta|Autoriza|Inscreve|Reconhece|Inclui|Torna|Prorroga|Amplia)\s+"
PARADAS = {"a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em",
           "no", "na", "nos", "nas", "para", "por", "que", "com", "ao", "à",
           "seus", "sua", "suas", "seu", "sobre"}


def frase_objeto(ementa):
    t = ementa
    for p in RUIDO:
        t = re.sub(p, " ", t, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip(" ,;.")
    # o objeto costuma estar na oração final "…, para <objeto>"
    m = re.search(r",\s*para\s+(.+)$", t, flags=re.I)
    if m and len(m.group(1).split()) >= 3:
        t = m.group(1)
    else:
        t = re.sub(ABERTURAS, "", t, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip(" ,;.")
    # o Trends exige TODAS as palavras da consulta: frase longa zera sempre.
    # Ficam 2-3 palavras de conteúdo, que é o que discrimina volume.
    palavras = [w.strip(" ,;.:") for w in t.split()]
    palavras = [w for w in palavras if w and w.lower() not in PARADAS and len(w) > 2]
    if palavras and re.search(r"(ar|er|ir)$", palavras[0], flags=re.I):
        palavras.pop(0)  # verbo no infinitivo que abre a oração "para <verbo>…"
    return " ".join(palavras[:2]).strip(" ,;.")


def numero_curto(identificacao):
    """'MPV 809/2017' -> ['MPV 809', 'MP 809']; 'PL 2159/2021' -> ['PL 2159']"""
    m = re.match(r"([A-Z]+)\s*(\d+)", identificacao)
    if not m:
        return []
    sigla, num = m.group(1), m.group(2)
    formas = [f"{sigla} {num}"]
    if sigla == "MPV":
        formas.append(f"MP {num}")
    return formas


def universo(tema_csv, base=BASE):
    with open(base, encoding="utf-8") as fh:
        return [x for x in csv.DictReader(fh) if x["tema"] == tema_csv]


def query_triagem(materia):
    """Bigrama de conteúdo da ementa. Sem o número da matéria: na triagem ele
    só somaria zero, e sem ele os bigramas repetidos entre matérias podem ser
    consultados uma vez só."""
    return frase_objeto(materia["ementa"])
