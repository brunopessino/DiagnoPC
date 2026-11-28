"""
MOTOR DE INFERÊNCIA - encadeamento à frente (forward chaining)
=============================================================
Este arquivo contém SOMENTE o mecanismo. Ele não conhece nenhum sintoma
específico: recebe fatos e regras e devolve o que pode ser concluído.

Como funciona (em rodadas):
  1. Começa com os fatos informados (sim / não / não sei).
  2. Em cada rodada, testa todas as regras ainda não aplicadas usando os
     fatos conhecidos NO INÍCIO da rodada.
  3. Toda regra com TODAS as condições confirmadas é aplicada; se ela gera
     um fato derivado, ele entra na memória de trabalho (sem duplicar).
  4. Para quando uma rodada não aplica nenhuma regra nova.
     Como cada regra só pode ser aplicada uma vez, o número de rodadas é
     no máximo (quantidade de regras + 1): o processo sempre termina.

Estados possíveis de uma regra:
  APLICAVEL     todas as condições confirmadas
  NAO_APLICAVEL alguma condição foi respondida ao contrário (ou um fato
                derivado exigido não tem como ser concluído)
  EM_ABERTO     sem contradição, mas depende de resposta "não sei"
  AGUARDANDO    depende de fato ainda não informado
  AGUARDA_DERIVADO depende de um fato derivado que uma regra aplicável
                ainda vai concluir (aparece na rodada seguinte)
"""

from base_conhecimento import (
    REGRAS, FATOS_ENTRADA, CONTRADICOES, SAIDAS, PRIORIDADE_SAIDAS,
    SAIDAS_QUE_SUSPENDEM, SAIDA_INSUFICIENTE,
)

APLICAVEL = "aplicável"
NAO_APLICAVEL = "não aplicável"
EM_ABERTO = "em aberto"
AGUARDANDO = "aguardando informação"
AGUARDA_DERIVADO = "aguardando fato derivado"
JA_APLICADA = "já aplicada"

_ORDEM_GRAVIDADE = {NAO_APLICAVEL: 4, AGUARDANDO: 3, EM_ABERTO: 2, AGUARDA_DERIVADO: 1, APLICAVEL: 0}
_TEXTO = {True: "sim", False: "não", None: "não sei"}


def _produtoras(fato, regras):
    """Regras que concluem um fato derivado."""
    return [r for r in regras if r["entao"].get("fato") == fato]


def avaliar_regra(regra, fatos, regras=REGRAS, _visitadas=None):
    """
    Avalia UMA regra contra os fatos. Retorna (estado, motivo).
    Para fatos derivados ainda não concluídos, olha as regras que podem
    produzi-los (com proteção contra ciclos).
    """
    _visitadas = set(_visitadas or ()) | {regra["id"]}
    avaliacoes = []

    for fato, exigido in regra["se"].items():
        if fato in fatos and fatos[fato] is not None:
            if fatos[fato] == exigido:
                continue
            estado = NAO_APLICAVEL
            motivo = f"{fato} = {_TEXTO[fatos[fato]]} (exige {_TEXTO[exigido]})"
        elif fato in fatos:  # resposta "não sei"
            estado, motivo = EM_ABERTO, f"{fato} = não sei"
        elif fato in FATOS_ENTRADA:  # ainda não perguntado
            estado, motivo = AGUARDANDO, f"{fato} não informado"
        else:  # fato derivado ainda não concluído
            produtoras = [p for p in _produtoras(fato, regras) if p["id"] not in _visitadas]
            estados = [avaliar_regra(p, fatos, regras, _visitadas)[0] for p in produtoras]
            nomes = ", ".join(p["id"] for p in produtoras)
            if APLICAVEL in estados:
                estado, motivo = AGUARDA_DERIVADO, f"aguarda {fato}, que {nomes} vai concluir"
            elif AGUARDANDO in estados:
                estado, motivo = AGUARDANDO, f"{fato} depende de fatos não informados ({nomes})"
            elif EM_ABERTO in estados:
                estado, motivo = EM_ABERTO, f"{fato} não pôde ser concluído ({nomes} em aberto)"
            else:
                estado, motivo = NAO_APLICAVEL, f"fato derivado {fato} não foi concluído ({nomes} não se aplica)"
        avaliacoes.append((estado, motivo))

    if not avaliacoes:
        return APLICAVEL, "todas as condições confirmadas"
    pior = max((e for e, _ in avaliacoes), key=lambda e: _ORDEM_GRAVIDADE[e])
    return pior, "; ".join(m for e, m in avaliacoes if e == pior)


def remover_contradicoes(fatos):
    """Fatos envolvidos em contradição passam a valer 'não sei' (não viram fatos confirmados)."""
    fatos = dict(fatos)
    avisos = []
    for (f1, v1), (f2, v2), mensagem in CONTRADICOES:
        if fatos.get(f1) is v1 and fatos.get(f2) is v2:
            fatos[f1] = None
            fatos[f2] = None
            avisos.append(mensagem)
    return fatos, avisos


def inferir(fatos_iniciais, regras=REGRAS):
    """
    Executa o encadeamento à frente e devolve um dicionário com a trilha completa:
      fatos_iniciais, avisos, rodadas, aplicadas, derivados, em_aberto,
      saidas, principal, suspensas, conclusao, motivo
    """
    fatos, avisos = remover_contradicoes(fatos_iniciais)
    aplicadas, derivados, rodadas = [], [], []

    for numero in range(1, len(regras) + 2):
        conhecidos = dict(fatos)  # fatos no início da rodada
        testes, novas = [], []
        for regra in regras:
            if regra["id"] in aplicadas:
                testes.append((regra["id"], JA_APLICADA, ""))
                continue
            estado, motivo = avaliar_regra(regra, conhecidos, regras)
            testes.append((regra["id"], estado, motivo))
            if estado == APLICAVEL:
                novas.append(regra)

        novos_fatos = []
        for regra in novas:
            aplicadas.append(regra["id"])
            fato = regra["entao"].get("fato")
            if fato and fatos.get(fato) is not True:  # impede fato duplicado
                fatos[fato] = True
                derivados.append({"fato": fato, "regra": regra["id"], "rodada": numero})
                novos_fatos.append(fato)

        rodadas.append({"numero": numero, "testes": testes,
                        "aplicadas": [r["id"] for r in novas], "novos_fatos": novos_fatos})
        if not novas:
            break

    # Regras que ficaram pela metade: nada contradiz e ao menos uma condição foi confirmada
    em_aberto = []
    for regra in regras:
        if regra["id"] in aplicadas:
            continue
        estado, motivo = avaliar_regra(regra, fatos, regras)
        confirmou_algo = any(fatos.get(f) == v for f, v in regra["se"].items())
        if estado in (EM_ABERTO, AGUARDANDO) and (confirmou_algo or estado == EM_ABERTO):
            em_aberto.append({"regra": regra["id"], "estado": estado, "motivo": motivo})

    # Saídas finais e política de prioridade
    saidas = {}
    for regra in regras:
        if regra["id"] in aplicadas and "saida" in regra["entao"]:
            saidas.setdefault(regra["entao"]["saida"], []).append(regra["id"])

    if saidas:
        ordem = sorted(saidas, key=lambda s: (PRIORIDADE_SAIDAS[s], list(SAIDAS).index(s)))
        principal = ordem[0]
        suspensas = []
        if principal in SAIDAS_QUE_SUSPENDEM:
            suspensas = [s for s in ordem if SAIDAS[s]["favoravel"]]
        conclusao, motivo = principal, ""
    else:
        ordem, principal, suspensas = [], None, []
        conclusao = SAIDA_INSUFICIENTE
        if em_aberto:
            motivo = ("Faltam informações para concluir: "
                      + "; ".join(f"{e['regra']} ({e['motivo']})" for e in em_aberto))
        else:
            motivo = ("Nenhuma regra da base corresponde aos fatos informados. "
                      "O caso está fora do escopo e deve ir para análise humana.")

    return {
        "fatos_iniciais": dict(fatos_iniciais),
        "fatos_finais": fatos,
        "avisos": avisos,
        "rodadas": rodadas,
        "aplicadas": aplicadas,
        "derivados": derivados,
        "em_aberto": em_aberto,
        "saidas": {s: saidas[s] for s in ordem},
        "principal": principal,
        "suspensas": suspensas,
        "conclusao": conclusao,
        "motivo": motivo,
    }


def proxima_pergunta(fatos, categoria, regras=REGRAS):
    """
    Modo interativo: escolhe o próximo fato de entrada a perguntar.
    Só pergunta o que ainda pode levar a alguma regra da categoria;
    perguntas de regras já descartadas são puladas.
    """
    fatos = inferir(fatos, regras)["fatos_finais"]  # inclui fatos derivados até agora
    for regra in regras:
        if regra["categoria"] != categoria:
            continue
        if avaliar_regra(regra, fatos, regras)[0] not in (AGUARDANDO, AGUARDA_DERIVADO):
            continue
        for fato in regra["se"]:
            if fato in FATOS_ENTRADA and fato not in fatos:
                return fato
    return None
