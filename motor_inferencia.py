"""
MOTOR DE INFERÊNCIA (encadeamento para frente / forward chaining)
=================================================================
Contém três peças do relatório:
  - MemoriaTrabalho  -> guarda as respostas da sessão como fatos (seção 5.2, RF03)
  - MotorInferencia  -> compara os fatos com as regras e dispara as aplicáveis (seção 9)
  - explicações      -> diz quais respostas sustentaram cada hipótese (seção 9.2, RF07)

Cada fato pode ter TRÊS estados (seção 8.2):
    True  = "sim"
    False = "não"
    None  = "não sei"  (desconhecido -> NUNCA é tratado como "não")
Um fato que ainda não foi perguntado simplesmente não existe na memória.
"""

from base_conhecimento import REGRAS, PERGUNTAS, CONTRADICOES

PESO_PRIORIDADE = {"alta": 3, "media": 2, "baixa": 1}

# Situação de uma regra em relação aos fatos atuais
DISPARADA = "disparada"        # todas as condições confirmadas
IMPOSSIVEL = "impossivel"      # alguma condição foi respondida ao contrário
EM_ABERTO = "em_aberto"        # nenhuma contradição, mas há condição com "não sei"
AGUARDANDO = "aguardando"      # ainda faltam perguntas a fazer


class MemoriaTrabalho:
    """Guarda os fatos informados pelo usuário durante UMA consulta."""

    def __init__(self):
        self.fatos = {}          # fato -> True / False / None

    def registrar(self, fato, valor):
        self.fatos[fato] = valor

    def foi_perguntado(self, fato):
        return fato in self.fatos

    def valor(self, fato):
        return self.fatos.get(fato)


def situacao_da_regra(regra, memoria):
    """Diz se a regra está disparada, impossível, em aberto ou aguardando."""
    tem_desconhecido = False
    tem_pendente = False
    for fato, esperado in regra["condicoes"].items():
        if not memoria.foi_perguntado(fato):
            tem_pendente = True
        elif memoria.valor(fato) is None:          # "não sei"
            tem_desconhecido = True
        elif memoria.valor(fato) != esperado:      # respondeu o contrário
            return IMPOSSIVEL
    if tem_pendente:
        return AGUARDANDO
    if tem_desconhecido:
        return EM_ABERTO
    return DISPARADA


class MotorInferencia:
    def __init__(self, regras=None):
        self.regras = regras if regras is not None else REGRAS

    # ---------------- escolha da próxima pergunta (RF02) ----------------
    def proxima_pergunta(self, memoria, categoria):
        """
        Devolve o próximo fato a perguntar, ou None se não há mais nada útil.
        Só pergunta o que ainda pode levar a alguma regra da categoria:
        se uma regra já ficou impossível, as perguntas dela são puladas.
        """
        for regra in self.regras:
            if regra["categoria"] != categoria:
                continue
            if situacao_da_regra(regra, memoria) != AGUARDANDO:
                continue
            for fato in regra["condicoes"]:
                if not memoria.foi_perguntado(fato):
                    return fato
        return None

    # ---------------- encadeamento para frente (seção 9.1) ----------------
    def inferir(self, memoria):
        """
        Percorre a base de regras repetidamente. Cada regra cujas condições
        estão todas confirmadas é disparada e sua conclusão entra na memória
        de trabalho como um novo fato ("hipotese_R05", por exemplo).
        O ciclo termina quando uma volta inteira não dispara nenhuma regra nova.
        """
        # Fatos envolvidos em contradição são tratados como "não sei" (RNF05):
        # assim nenhuma regra é disparada com base em respostas incompatíveis.
        memoria = self._memoria_sem_contradicoes(memoria)

        disparadas = []
        houve_novidade = True
        while houve_novidade:
            houve_novidade = False
            for regra in self.regras:
                if regra in disparadas:
                    continue
                if situacao_da_regra(regra, memoria) == DISPARADA:
                    disparadas.append(regra)
                    memoria.registrar("hipotese_" + regra["id"], True)
                    houve_novidade = True

        # Ordena: prioridade maior primeiro; empate -> mais condições confirmadas
        disparadas.sort(
            key=lambda r: (PESO_PRIORIDADE[r["prioridade"]], len(r["condicoes"])),
            reverse=True,
        )
        em_aberto = [r for r in self.regras if situacao_da_regra(r, memoria) == EM_ABERTO]
        return disparadas, em_aberto

    # ---------------- contradições (RNF05) ----------------
    def _memoria_sem_contradicoes(self, memoria):
        suspeitos = set()
        for (f1, v1), (f2, v2), _ in CONTRADICOES:
            if memoria.foi_perguntado(f1) and memoria.foi_perguntado(f2) \
                    and memoria.valor(f1) == v1 and memoria.valor(f2) == v2:
                suspeitos.update([f1, f2])
        if not suspeitos:
            return memoria
        copia = MemoriaTrabalho()
        copia.fatos = dict(memoria.fatos)
        for fato in suspeitos:
            copia.fatos[fato] = None
        return copia

    def contradicoes(self, memoria):
        avisos = []
        for (f1, v1), (f2, v2), mensagem in CONTRADICOES:
            if memoria.foi_perguntado(f1) and memoria.foi_perguntado(f2) \
                    and memoria.valor(f1) == v1 and memoria.valor(f2) == v2:
                avisos.append(mensagem)
        return avisos


# ---------------- módulo de explicação (seção 9.2, RF07) ----------------
def explicar(regra, memoria):
    """Monta a frase 'foi sugerida porque você informou que ...'."""
    partes = []
    for fato, esperado in regra["condicoes"].items():
        chave = "sim" if memoria.valor(fato) else "nao"
        partes.append(PERGUNTAS[fato][chave])
    if len(partes) == 1:
        texto = partes[0]
    else:
        texto = ", ".join(partes[:-1]) + " e " + partes[-1]
    return f"Regra {regra['id']} acionada porque você informou que {texto}."


def faltando(regra, memoria):
    """Lista o que ficou como 'não sei' numa regra em aberto."""
    return [PERGUNTAS[f]["pergunta"] for f in regra["condicoes"] if memoria.valor(f) is None
            and memoria.foi_perguntado(f)]


# ---------------- consulta completa (usada pela interface e pelos testes) ----------------
def consultar(categoria, responder, memoria=None, motor=None):
    """
    Executa uma consulta de ponta a ponta.
      categoria: chave de CATEGORIAS (ex.: "4")
      responder: função que recebe o nome do fato e devolve True/False/None
    Retorna um dicionário com memória, hipóteses, regras em aberto e contradições.
    """
    memoria = memoria or MemoriaTrabalho()
    motor = motor or MotorInferencia()

    while True:
        fato = motor.proxima_pergunta(memoria, categoria)
        if fato is None:
            break
        memoria.registrar(fato, responder(fato))

    disparadas, em_aberto = motor.inferir(memoria)
    return {
        "memoria": memoria,
        "hipoteses": disparadas,
        "em_aberto": em_aberto,
        "contradicoes": motor.contradicoes(memoria),
    }
