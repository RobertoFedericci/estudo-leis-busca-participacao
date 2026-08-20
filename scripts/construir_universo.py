# -*- coding: utf-8 -*-
"""Constrói o universo do estudo a partir dos dados abertos do Senado.

Entra: dados/senado/processo_AAAA.json (baixados por scripts/baixar_senado.py)
Sai:   dados/senado_aprovados.csv

Recorte: proposições SUBSTANTIVAS (exclui requerimentos, indicações, mensagens
e ofícios) cuja situação atual indica aprovação pelo Senado. O tema vem de
palavras-chave da ementa, com a ordem das regras importando — as específicas
primeiro, para que "acordo internacional sobre meio ambiente" caia em relações
exteriores e não em meio ambiente.
"""

import csv
import glob
import json
import os
import re
import unicodedata

ENTRADA = os.environ.get("BASE_SENADO", "dados/senado")
SAIDA = os.environ.get("SAIDA_CSV", "dados/senado_aprovados.csv")

SUBSTANTIVAS = {
    "Projeto de Lei Ordinária", "Projeto de Lei Complementar",
    "Proposta de Emenda à Constituição", "Projeto de Decreto Legislativo",
    "Medida Provisória", "Projeto de Resolução", "Projeto de Lei de Conversão",
}
APROVA = ("APROVAD", "TRANSFORMAD", "NORMA JUR", "REMETIDA À CÂMARA",
          "ENVIADA À SANÇÃO", "ENVIADA À CÂMARA", "SANCIONAD", "PROMULGAD")
NORMA = ("NORMA JUR", "TRANSFORMAD", "SANCIONAD", "PROMULGAD")

TEMAS = [
    ("Relações Exteriores (tratados)", ["aprova o texto do acordo", "aprova o acordo", "acordo entre", "tratado", "convencao internacional", " protocolo", "cooperacao tecnica entre", "cooperacao cultural", "facilitacao de investimentos", "emenda ao acordo", "acordo-quadro"]),
    ("Comunicações (rádio/TV)", ["radiodifusao", "retransmissao", "radio comunitaria", " tv ", " radio ", " radiofusao", "servico de radio", "executa servico", "outorga"]),
    ("Homenagens/Denominações", ["denomina", "passa a denominar", "institui o dia", "data comemorativa", "titulo de cidad", "utilidade publica", "congratul", "capital nacional", "comenda", "merito", "dia do", "dia nacional", "semana nacional", "ano nacional"]),
    ("Saúde", ["saude", "sus", "medic", "hospital", "doenca", "cancer", "vacina", "sanitar", "farmac", "enferm", "autismo", "saude mental"]),
    ("Educação", ["educac", "escola", "ensino", "universidad", "professor", "estudante", "creche", "pronatec", "fies", "alfabetiz"]),
    ("Segurança e Justiça", ["seguranca publica", "crime", "penal", "pena", "violencia", "policia", "armas", "feminicidio", "drogas", "penitenci", "codigo penal"]),
    ("Trabalho e Previdência", ["trabalh", "emprego", "clt", "sindical", "previdenc", "aposentad", "salario", "fgts", "estagi"]),
    ("Tributário e Economia", ["tribut", "imposto", "icms", "fiscal", "credito", "financ", "economi", "empresa", "microempres", "setor produtivo", "contribuic"]),
    ("Assistência e Direitos", ["assistencia social", "bolsa", "idoso", "crianca", "adolescente", "deficienc", "igualdade", "direitos", "mulher", "racial", "lgbt", "indigena", "quilombol", "refugiado"]),
    ("Meio Ambiente", ["ambient", "clima", "floresta", "agua", "residuos", "sustentab", "amazonia", "poluic", "biodivers", "energia renovavel"]),
    ("Agropecuária", ["agropecuar", "agricultura", "rural", "agronegoci", "pesca", "produtor rural", "defensivos"]),
    ("Infraestrutura e Transporte", ["transporte", "rodovi", "transito", "mobilidade", "saneamento", "energia", "portuari", "aeroport", "habitac", "telecomunic"]),
    ("Administração Pública", ["servidor", "administracao publica", "carreira", "orgao", "autarqui", "licitac", "concurso publico"]),
    ("Defesa do Consumidor", ["consumidor", "cobranca", "tarifa", "plano de saude", "cadastro", "superendivid"]),
]
COLUNAS = ["ano", "identificacao", "tipo", "autoria", "casa", "data_apresentacao",
           "situacao", "virou_norma", "tema", "ementa", "codigo_materia", "url"]


def sem_acento(t):
    return unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()


def tema(ementa):
    e = sem_acento(ementa)
    for nome, chaves in TEMAS:
        if any(k in e for k in chaves):
            return nome
    return "Outros"


def main():
    arquivos = sorted(glob.glob(os.path.join(ENTRADA, "processo_*.json")))
    if not arquivos:
        raise SystemExit(f"nada em {ENTRADA}/ — rode antes scripts/baixar_senado.py")
    linhas = []
    for fp in arquivos:
        ano = int(re.search(r"(\d{4})", os.path.basename(fp)).group(1))
        with open(fp, encoding="utf-8") as fh:
            for x in json.load(fh):
                if x.get("tipoDocumento") not in SUBSTANTIVAS:
                    continue
                sit = (x.get("situacaoAtual") or "").upper()
                if not any(k in sit for k in APROVA):
                    continue
                linhas.append({
                    "ano": ano,
                    "identificacao": x.get("identificacao"),
                    "tipo": x.get("tipoDocumento"),
                    "autoria": x.get("autoria"),
                    "casa": x.get("casaIdentificadora"),
                    "data_apresentacao": x.get("dataApresentacao"),
                    "situacao": x.get("situacaoAtual"),
                    "virou_norma": any(k in sit for k in NORMA),
                    "tema": tema(x.get("ementa")),
                    "ementa": (x.get("ementa") or "").replace("\n", " ").strip(),
                    "codigo_materia": x.get("codigoMateria"),
                    "url": x.get("urlDocumento"),
                })
    os.makedirs(os.path.dirname(SAIDA) or ".", exist_ok=True)
    with open(SAIDA, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUNAS)
        w.writeheader()
        w.writerows(linhas)
    import collections
    print(f"{len(linhas)} matérias substantivas aprovadas -> {SAIDA}")
    for t, n in collections.Counter(x["tema"] for x in linhas).most_common():
        print(f"  {n:>5}  {t}")


if __name__ == "__main__":
    main()
