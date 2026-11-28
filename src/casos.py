"""
CASOS FICTÍCIOS DE TESTE E DEMONSTRAÇÃO
=======================================
Todos os casos são inventados (não há dados pessoais nem equipamentos reais).
Valores: True = sim | False = não | None = não sei | fato ausente = não informado.
Cada caso indica as regras que ele exercita (ver docs/matriz_regra-caso-fonte.md).
"""

CASOS = {
    "C01": {
        "descricao": "PC sem nenhum sinal de energia; tomada e cabo ainda não verificados.",
        "tipo": "favorável",
        "fatos": {"sem_energia": True, "tomada_cabo_verificados": False},
    },
    "C02": {
        "descricao": "PC sem energia mesmo com tomada e cabo confirmados.",
        "tipo": "negativo",
        "fatos": {"sem_energia": True, "tomada_cabo_verificados": True},
    },
    "C03": {
        "descricao": "PC liga, ventoinhas giram, mas a tela fica preta.",
        "tipo": "favorável",
        "fatos": {"liga_com_ventoinhas": True, "sem_imagem": True},
    },
    "C04": {
        "descricao": "Windows demora muito para iniciar.",
        "tipo": "favorável",
        "fatos": {"inicializacao_lenta": True},
    },
    "C05": {
        "descricao": "PC lento no uso, memória perto de 100% e disco C: quase cheio.",
        "tipo": "favorável",
        "fatos": {"inicializacao_lenta": False, "lentidao_geral": True,
                  "memoria_no_limite": True, "disco_quase_cheio": True},
    },
    "C06": {
        "descricao": "PC desliga sozinho durante jogos e esquenta muito (regra encadeada).",
        "tipo": "negativo",
        "fatos": {"desliga_sozinho": True, "ocorre_durante_carga": True,
                  "aquecimento_ou_ruido": True},
    },
    "C07": {
        "descricao": "PC desliga durante jogos, mas sem calor nem ruído forte (regra encadeada).",
        "tipo": "negativo",
        "fatos": {"desliga_sozinho": True, "ocorre_durante_carga": True,
                  "aquecimento_ou_ruido": False},
    },
    "C08": {
        "descricao": "Notebook esquenta e faz barulho, mas não desliga sozinho.",
        "tipo": "favorável",
        "fatos": {"desliga_sozinho": False, "aquecimento_ou_ruido": True},
    },
    "C09": {
        "descricao": "HD faz cliques fortes e o Windows mostra erro de leitura.",
        "tipo": "negativo",
        "fatos": {"disco_alertas_ruidos": True},
    },
    "C10": {
        "descricao": "Internet funciona no cabo, mas não no Wi-Fi do notebook.",
        "tipo": "favorável",
        "fatos": {"funciona_por_cabo": True, "falha_wifi": True},
    },
    "C11": {
        "descricao": "Sem internet no PC e também no celular, na mesma rede.",
        "tipo": "favorável",
        "fatos": {"funciona_por_cabo": False, "falha_varios_dispositivos": True},
    },
    "C12": {
        "descricao": "PC desliga durante jogos; usuário NÃO SABE se esquenta (fronteira).",
        "tipo": "fronteira",
        "fatos": {"desliga_sozinho": True, "ocorre_durante_carga": True,
                  "aquecimento_ou_ruido": None},
    },
    "C13": {
        "descricao": "Usuário diz que o Windows inicia normal e não fica lento (nenhuma regra).",
        "tipo": "negativo",
        "fatos": {"inicializacao_lenta": False, "lentidao_geral": False},
    },
    "C14": {
        "descricao": "PC sem energia; usuário NÃO SABE se a tomada foi verificada (fronteira).",
        "tipo": "fronteira",
        "fatos": {"sem_energia": True, "tomada_cabo_verificados": None},
    },
    "C15": {
        "descricao": "Disco com cliques E PC lento com disco cheio (conflito resolvido pela prioridade).",
        "tipo": "negativo",
        "fatos": {"disco_alertas_ruidos": True, "lentidao_geral": True,
                  "disco_quase_cheio": True, "memoria_no_limite": False},
    },
    "C16": {
        "descricao": "Respostas contraditórias: 'sem energia' e 'liga com ventoinhas'.",
        "tipo": "fronteira",
        "fatos": {"sem_energia": True, "tomada_cabo_verificados": True,
                  "liga_com_ventoinhas": True, "sem_imagem": True},
    },
}

# As três execuções explicadas exigidas pela orientação (item 3.3)
EXEMPLOS_EXPLICADOS = ["C05", "C06", "C12"]
