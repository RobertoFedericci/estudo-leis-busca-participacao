# -*- coding: utf-8 -*-
"""As 46 matérias ambientais do levantamento legislativo do Senado (2017-2026).

Universo: matérias substantivas aprovadas pelo Senado entre 2017 e 2026,
classificadas no tema "Meio Ambiente", a partir dos dados abertos da Casa
(legis.senado.leg.br/dadosabertos, endpoint /processo?ano=AAAA). Das 54 do
recorte, 8 foram descartadas por não terem objeto ambiental (ver DESCARTADAS).

Cada matéria vira UMA curva no Google Trends. A consulta une, pelo operador `+`
(OR do Trends), o número da matéria e a expressão que descreve o OBJETO da lei.

Regra das queries — o que aprendemos revisando a primeira rodada:
  * o termo temático tem de ser específico ao que a lei FAZ, não à instituição
    citada na ementa. "ICMBio" mede concurso público; "compensação ambiental
    ICMBio" mede a matéria. "energia solar" mede o mercado; "marco legal da
    geração distribuída" mede o PL.
  * cada termo separado por `+` é uma consulta independente: um termo largo no
    meio da união contamina a curva inteira, ainda que os outros sejam bons.
  * o Trends casa por conjunto de palavras, não por sequência exata: "MPV 809"
    já alcança quem buscou "MPV 809/2017". Por isso a forma curta basta — o que
    não é redundante é MP vs. MPV, formas realmente diferentes de escrever.
"""

TOPICOS = [
    # (identificação, ano, virou_norma, ementa curta, QUERY DO TRENDS)
    #   só o 5º campo vai para o Google. Os outros são rótulos do relatório.

    ("MPV 809/2017", 2017, True,
     "Gestão dos recursos de compensação ambiental pelo ICMBio",
     "MP 809 + MPV 809 + compensação ambiental ICMBio"),

    ("PLS 251/2018", 2018, False,
     "Registro das Cotas de Reserva Ambiental no Código Florestal",
     # "registro de CRA" saiu: CRA também é Certificado de Recebíveis do
     # Agronegócio, sigla de volume muito maior no mercado financeiro
     "PLS 251 + Cota de Reserva Ambiental"),

    ("PLS 317/2018", 2018, False,
     "Incentivo à redução de perdas na distribuição de água tratada",
     "PLS 317 + perdas na distribuição de água tratada"),

    ("PLS 458/2018", 2018, False,
     "Reaproveitamento de estudos de impacto anteriores no licenciamento",
     "PLS 458 + reaproveitamento de estudo de impacto ambiental"),

    ("PLC 128/2018", 2018, True,
     "Eliminação controlada de equipamentos com PCB (ascarel)",
     "PLC 128 + bifenilas policloradas + descarte de ascarel"),

    ("PL 724/2019", 2019, False,
     "Água de reúso obrigatória em indústrias de região de baixa chuva",
     "PL 724 + água de reúso na indústria"),

    ("PL 754/2019", 2019, False,
     "Amplia beneficiários do Programa de Apoio à Conservação Ambiental",
     # "Bolsa Verde" saiu: pega o programa federal e os estaduais homônimos,
     # mesmo problema institucional de "ICMBio"
     "PL 754 + Programa de Apoio à Conservação Ambiental"),

    ("PL 1452/2019", 2019, False,
     "Reaproveitamento e redução de rejeitos na segurança de barragens",
     "PL 1452 + segurança de barragens + reaproveitamento de rejeitos"),

    ("PL 2920/2019", 2019, False,
     "Repasse de 20% do Fundo Nacional de Meio Ambiente a municípios",
     "PL 2920 + Fundo Nacional de Meio Ambiente"),

    ("PRS 52/2019", 2019, False,
     "Campanha Junho Verde de conscientização ambiental",
     "PRS 52 + campanha Junho Verde"),

    ("PL 3253/2019", 2019, False,
     "Regulamenta a profissão de agente de coleta de resíduos",
     "PL 3253 + profissão de agente de coleta de resíduos + profissão de gari"),

    ("PL 4731/2019", 2019, False,
     "Codevasf na bacia do Araguari e demais bacias do AP e PA",
     "PL 4731 + Codevasf no Amapá + bacia do rio Araguari"),

    ("PRS 85/2019", 2019, False,
     "Prêmio Chico Mendes do Senado para jornalismo ambiental",
     "PRS 85 + Prêmio Chico Mendes do Senado"),

    ("PL 5028/2019", 2019, True,
     "Política Nacional de Pagamento por Serviços Ambientais",
     "PL 5028 + Política Nacional de Pagamento por Serviços Ambientais"),

    ("PL 5098/2019", 2019, False,
     "Fundo Clima para desmatamento, queimadas e desastres",
     # "Fundo Clima" saiu: casa qualquer busca com "fundo"+"clima" (notícia do
     # BNDES, fundos de investimento). O nome formal já é específico
     "PL 5098 + Fundo Nacional sobre Mudança do Clima"),

    ("PL 6046/2019", 2019, False,
     "Telhados verdes e reservatórios de chuva no plano diretor",
     "PL 6046 + telhado verde no plano diretor + cobertura vegetada"),

    ("PL 6044/2019", 2019, False,
     "Capacitação do consumidor no acondicionamento de resíduos",
     "PL 6044 + acondicionamento de resíduos sólidos"),

    ("PL 6539/2019", 2019, False,
     "PNMC atualizada ao contexto do Acordo de Paris",
     "PL 6539 + PNMC Acordo de Paris"),

    ("PL 5829/2019", 2019, True,
     "Marco legal da microgeração e minigeração distribuída",
     "PL 5829 + marco legal da geração distribuída + minigeração distribuída"),

    ("PL 2510/2019", 2019, True,
     "APPs no entorno de cursos d'água em área urbana consolidada",
     "PL 2510 + área de preservação permanente urbana"),

    ("PDL 696/2019", 2019, True,
     "Emenda de Banimento à Convenção de Basileia",
     "PDL 696 + Emenda de Banimento + Convenção de Basileia"),

    ("PL 2673/2019", 2019, True,
     "Prorroga benefícios das Áreas de Livre Comércio da Amazônia Ocidental",
     "PL 2673 + Área de Livre Comércio da Amazônia Ocidental"),

    ("PL 175/2020", 2020, True,
     "Aproveitamento de águas pluviais e reúso de águas servidas",
     "PL 175 + aproveitamento de águas pluviais + reúso de água servida"),

    ("PL 415/2020", 2020, False,
     "Institui o Fundo Amazônia em lei",
     "PL 415 + Fundo Amazônia"),

    ("PL 4379/2020", 2020, False,
     "Altera a Flona de Brasília e a Reserva Biológica da Contagem",
     "PL 4379 + Reserva Biológica da Contagem"),

    ("PL 2776/2020", 2020, True,
     "Altera os limites da Floresta Nacional de Brasília",
     "PL 2776 + limites da Floresta Nacional de Brasília"),

    ("PL 1539/2021", 2021, False,
     "Nova meta de compromisso nacional voluntário na PNMC",
     "PL 1539 + meta brasileira de redução de emissões + NDC do Brasil"),

    ("PL 2159/2021", 2021, True,
     "Lei Geral do Licenciamento Ambiental",
     "PL 2159 + lei geral do licenciamento ambiental + PL da devastação"),

    ("PL 3475/2021", 2021, False,
     "Parcelamento de dívidas de produtores rurais no Ibama",
     "PL 3475 + parcelamento de multas do Ibama + dívida com o Ibama"),

    ("PL 3639/2021", 2021, True,
     "Caminhada da Água como evento do Dia Mundial da Água",
     "PL 3639 + Caminhada da Água"),

    ("PL 4129/2021", 2021, True,
     "Diretrizes para planos de adaptação à mudança do clima",
     "PL 4129 + plano de adaptação à mudança do clima"),

    ("PL 1818/2022", 2022, True,
     "Política Nacional de Manejo Integrado do Fogo",
     "PL 1818 + Política Nacional de Manejo Integrado do Fogo"),

    ("PL 1944/2023", 2023, False,
     "Tratamento ambientalmente adequado do esgoto em áreas rurais",
     "PL 1944 + tratamento de esgoto em área rural + saneamento rural"),

    ("PL 2088/2023", 2023, True,
     "Padrões ambientais brasileiros exigidos de bens importados",
     "PL 2088 + padrão ambiental para produto importado"),

    ("PL 4364/2023", 2023, False,
     "Mitigação e remoção de gases de efeito estufa na PNMC",
     "PL 4364 + remoção de gases de efeito estufa"),

    ("PDL 321/2023", 2023, True,
     "Estado de calamidade no RS pelas chuvas intensas",
     "PDL 321 + estado de calamidade no Rio Grande do Sul"),

    ("PL 5569/2023", 2023, False,
     "Acesso a água potável em estabelecimentos e eventos",
     "PL 5569 + água potável gratuita em estabelecimento"),

    ("PL 380/2023", 2023, False,
     "Cidades resilientes às mudanças climáticas na política urbana",
     "PL 380 + cidade resiliente à mudança do clima"),

    ("PL 182/2024", 2024, True,
     "Sistema Brasileiro de Comércio de Emissões (SBCE)",
     # "SBCE" sozinha é sigla ambígua; exigindo "carbono" junto ela só casa
     # com o sistema criado pela lei
     "PL 182 + SBCE carbono + lei do mercado de carbono"),

    ("PL 4096/2024", 2024, True,
     "Recompra de cotas do Finam e do Finor",
     "PL 4096 + recompra de cotas do Finam + Finor"),

    ("PL 4199/2024", 2024, False,
     "Plano Rios Livres da Amazônia",
     "PL 4199 + Plano Rios Livres da Amazônia"),

    ("PL 3944/2024", 2024, True,
     "Proíbe a importação de resíduos sólidos",
     "PL 3944 + proibição da importação de resíduos sólidos + importação de lixo"),

    ("PL 3347/2025", 2025, False,
     "Programa Luz na Amazônia como cultura nacional",
     "PL 3347 + Programa Luz na Amazônia"),

    ("PL 3761/2025", 2025, False,
     "Cria o Selo Verde Café Amazônia",
     "PL 3761 + Selo Verde Café Amazônia"),

    ("MPV 1308/2025", 2025, True,
     "Licenciamento ambiental especial para obras estratégicas",
     "MP 1308 + MPV 1308 + licenciamento ambiental especial"),

    ("PL 358/2025", 2025, True,
     "Sede do Governo Federal em Belém durante a COP30",
     "PL 358 + transferência da sede do governo para Belém"),
]

# Classificadas como "Meio Ambiente" pelo levantamento (que usa palavra-chave da
# ementa) sem terem objeto ambiental. Removidas do índice; ficam registradas
# aqui e na nota de limitações do relatório.
DESCARTADAS = [
    ("PLS 430/2018", "Banheiro familiar e fraldário", "'ambientes coletivos'"),
    ("PL 1397/2019", "Nísia Floresta no Livro dos Heróis", "'Floresta'"),
    ("PLP 262/2019", "Cooperativas no FDNE, FDA e FDCO", "fundos regionais"),
    ("PL 296/2022", "Doação de viaturas ao Paraguai", "sem termo ambiental"),
    ("PL 877/2022", "Preço dos serviços de praticagem", "'águas sob jurisdição'"),
    ("PL 2375/2022", "Profissão de designer de interiores", "'ambientes'"),
    ("PL 757/2022", "Regulação da praticagem", "'águas sob jurisdição'"),
    ("PL 2911/2022", "Material militar ao Paraguai", "sem termo ambiental"),
]

assert len({t[0] for t in TOPICOS}) == len(TOPICOS)
assert len({t[4] for t in TOPICOS}) == len(TOPICOS)
assert all(len(t[4]) <= 100 for t in TOPICOS)
