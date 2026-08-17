# O que o Brasil procura das leis ambientais

Quanta atenção pública receberam, na busca do Google e na consulta popular do
Senado, as **46 matérias de tema ambiental aprovadas pelo Senado Federal entre
2017 e 2026**. Uma década de legislação ambiental, medida pelo que o cidadão
procurou e pelo que ele opinou.

**Página:** https://robertofedericci.github.io/estudo-leis-ambientais-busca/

Estudo de Roberto Federicci. Trabalho independente, sem vínculo com partido,
campanha ou candidatura.

## O que é medido

Duas medidas independentes, para as mesmas 46 matérias:

| Medida | Fonte | O que é |
|---|---|---|
| **Busca** | Google Trends (Brasil, 2016–2026, mensal) | Volume relativo de procura pelo número da proposição e pelo tópico que descreve seu objeto |
| **Participação** | Portal e-Cidadania do Senado | Votos Sim/Não na consulta pública aberta a toda proposição em tramitação (Resolução 26/2013) |

## As chaves de busca

Cada matéria vira **uma** curva. A consulta une, pelo operador `+` (OR do
Trends), o número da proposição e a expressão que descreve o objeto da lei:

```
PL 2159 + lei geral do licenciamento ambiental + PL da devastação
```

A expressão temática é escolhida para colar no objeto da matéria, **nunca na
instituição citada na ementa nem no assunto amplo em volta dela**. A diferença
não é cosmética: em versões anteriores deste levantamento, `ICMBio` media
concurso público, `energia solar` media o mercado solar e `Fundo Clima` media
notícia do BNDES. Trocados pelos termos específicos, os três tópicos caíram
entre 92% e 99,9%, e o índice consolidado encolheu 98%. O que a primeira
versão media era, em quase tudo, o tema em volta da lei — não a lei.

Duas propriedades do Trends explicam a armadilha, e valem para qualquer
levantamento assim:

- **Casa por conjunto de palavras, não por sequência.** `Fundo Clima` alcança
  qualquer busca que contenha "fundo" e "clima", em qualquer ordem.
- **Cada termo do `+` é uma consulta independente.** Um termo largo no meio da
  união contamina a curva inteira, ainda que os outros sejam precisos.

Todas as 46 chaves estão em [`scripts/topicos.py`](scripts/topicos.py), uma por
matéria, com o motivo de cada escolha registrado em comentário.

## A régua comum

O Trends normaliza cada consulta de 0 a 100 **dentro da requisição**, então
curvas de requisições diferentes não são somáveis. Para empilhar as 46 numa só
linha, o estudo reconstrói a escala em três passos:

1. **Âncoras.** Quatro buscas de referência de magnitudes muito diferentes
   (`meio ambiente` → `licenciamento ambiental` → `manejo integrado do fogo` →
   `cota de reserva ambiental`), medidas em cadeia, cada uma contra a anterior.
   Isso dá uma régua com amplitude de ~2.200×, indispensável porque os tópicos
   variam de 1,92 a 0,003.
2. **Níveis.** Cada tópico é medido junto de uma âncora. Quem sai com valor
   bruto baixo — pouca resolução, já que o Trends devolve inteiros — é remedido
   contra a âncora seguinte, mais fraca.
3. **Formato.** Cada tópico é consultado também sozinho, o que devolve a curva
   em resolução cheia. A série final é `solo(t) / 100 × nível_global`.

A referência `meio ambiente` **não faz parte do índice**: é só a régua. Seu pico
na década vale 100, o que dá a leitura do resultado — no melhor mês, jul/2025,
a atenção somada a todas as 46 leis chegou a 2,19, cerca de 2% do que os
brasileiros procuram ao digitar simplesmente "meio ambiente".

## O que o estudo encontra

- **A atenção pública a legislação ambiental é pequena e concentrada.** Três
  temas respondem por 62% de toda a busca; 10 das 46 matérias não registram
  volume mensurável.
- **Um único evento se destaca na década:** julho de 2025, a aprovação do
  PL 2159/2021, a Lei Geral do Licenciamento Ambiental. Ele lidera a busca com
  1,92 contra 0,47 do segundo colocado.
- **O mesmo PL 2159 concentra 63% de todos os votos da consulta pública** das
  46 matérias, e foi rejeitado por 94% (342 Sim × 4.976 Não).
- **As três matérias de flexibilização do licenciamento são as três mais
  rejeitadas** — PL 2776/2020 (3% Sim), PL 2159/2021 (6%) e MPV 1308/2025
  (13%). Não é dispersão: é a mesma direção nas três.

## Como reproduzir

```bash
pip install -r requirements.txt

python scripts/baixar_senado.py       # base de processos, API do Senado (~40 MB)
python scripts/coletar_consultas.py   # votos Sim/Não do e-Cidadania
python scripts/coletar.py             # Google Trends, com cache em disco
python scripts/gerar_html.py          # gera index.html
```

Rode sempre da raiz do repositório. `coletar.py` tem cache em disco e backoff
para o rate limit do Trends: uma execução completa leva de 20 a 40 minutos na
primeira vez, e segundos depois disso. Alterar uma chave em `topicos.py` só
manda à rede os lotes afetados.

Os dados derivados já estão versionados em [`dados/`](dados/), então
`gerar_html.py` roda sozinho, sem nenhuma coleta.

## Limites

- **Isto mede tema, não proposição.** Ninguém busca "PL 182/2024"; busca o
  assunto da lei. As chaves foram apertadas para reduzir isso ao mínimo, mas
  onde o objeto da matéria é ele próprio um tema de imprensa — `Fundo Amazônia`,
  `estado de calamidade no Rio Grande do Sul` — a curva ainda capta mais do que
  a tramitação.
- **Granularidade mensal.** Janelas acima de cinco anos vêm em meses no Trends;
  picos de poucos dias desaparecem dentro do mês.
- **O voto do e-Cidadania é autosselecionado.** Vota quem foi mobilizado a
  votar. Serve para ler direção e intensidade de mobilização, nunca como
  pesquisa de opinião.
- **O recorte são as matérias aprovadas pelo Senado.** Projetos ambientais
  rejeitados ou parados na Câmara não estão aqui, inclusive alguns de alta
  relevância.
- **A classificação temática do Senado é por palavra-chave da ementa.** Das 54
  matérias que caíram em "Meio Ambiente" no período, 8 não têm objeto ambiental
  (praticagem, designer de interiores, doação de viaturas) e foram descartadas.

## Fontes

- Google Trends — Brasil, todas as categorias, jan/2016 a ago/2026.
- Portal e-Cidadania do Senado Federal, consultado em agosto de 2026.
- Dados abertos do Senado Federal, `legis.senado.leg.br/dadosabertos`.

## Licença

MIT, ver [LICENSE](LICENSE).
