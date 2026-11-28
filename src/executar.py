"""
EXECUTAR - DiagnoPC
===================
Recebe um caso, chama o motor de inferência e exibe a conclusão e a explicação.

Modos de uso (rode a partir da pasta do projeto):
    python src/executar.py                 -> modo interativo (perguntas no terminal)
    python src/executar.py --exemplos      -> as 3 execuções explicadas (favorável,
                                              negativo e fronteira)
    python src/executar.py --caso C06      -> executa um caso fictício de src/casos.py
    python src/executar.py --listar        -> lista os casos disponíveis
"""

import os
import sys
from datetime import datetime

from base_conhecimento import (AVISO_GERAL, CATEGORIAS, FATOS_DERIVADOS, FATOS_ENTRADA,
                               FONTES, REGRAS, SAIDAS, SAIDA_INSUFICIENTE)
from casos import CASOS, EXEMPLOS_EXPLICADOS
from inferencia import (APLICAVEL, AGUARDANDO, AGUARDA_DERIVADO, EM_ABERTO, JA_APLICADA, NAO_APLICAVEL,
                        inferir, proxima_pergunta)

try:  # acentos corretos no terminal do Windows e em arquivos redirecionados
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

LINHA = "=" * 72
REGRA_POR_ID = {r["id"]: r for r in REGRAS}
TEXTO_VALOR = {True: "sim", False: "não", None: "não sei"}


# ----------------------------------------------------------------------------
# Explicação
# ----------------------------------------------------------------------------
def frase_do_fato(fato, valor):
    if fato in FATOS_ENTRADA:
        return FATOS_ENTRADA[fato]["sim" if valor else "nao"]
    return FATOS_DERIVADOS[fato]["sim"]


def porque(regra, fatos):
    partes = [frase_do_fato(f, fatos[f]) for f in regra["se"]]
    texto = partes[0] if len(partes) == 1 else ", ".join(partes[:-1]) + " e " + partes[-1]
    return f"{regra['id']} foi aplicada porque {texto}."


def explicar(resultado, titulo=None):
    """Monta a explicação completa da execução (itens 1 a 5 da orientação, seção 3.3)."""
    r = resultado
    linhas = [LINHA, titulo or "RESULTADO DA TRIAGEM - DiagnoPC", LINHA]

    linhas.append("\n1) FATOS INICIAIS")
    if r["fatos_iniciais"]:
        for fato, valor in r["fatos_iniciais"].items():
            linhas.append(f"   - {fato} = {TEXTO_VALOR[valor]}")
    else:
        linhas.append("   (nenhum fato informado)")
    for aviso in r["avisos"]:
        linhas.append(f"   [!] Contradição: {aviso} Esses fatos passaram a valer 'não sei'.")

    linhas.append("\n2) REGRAS TESTADAS E APLICADAS (encadeamento à frente, por rodada)")
    for rodada in r["rodadas"]:
        linhas.append(f"   Rodada {rodada['numero']}:")
        aguardando = []
        for rid, estado, motivo in rodada["testes"]:
            if estado == APLICAVEL:
                linhas.append(f"     [APLICADA]      {rid}: {motivo}")
            elif estado == EM_ABERTO:
                linhas.append(f"     [EM ABERTO]     {rid}: {motivo}")
            elif estado == NAO_APLICAVEL:
                linhas.append(f"     [NÃO APLICÁVEL] {rid}: {motivo}")
            elif estado == AGUARDA_DERIVADO:
                linhas.append(f"     [AGUARDA]       {rid}: {motivo}")
            elif estado == AGUARDANDO:
                aguardando.append(rid)
            elif estado == JA_APLICADA:
                linhas.append(f"     [JÁ APLICADA]   {rid}")
        if aguardando:
            linhas.append(f"     [SEM DADOS]     {', '.join(aguardando)}: dependem de fatos não informados")
        if not rodada["aplicadas"]:
            linhas.append("     -> Nenhuma regra nova aplicada: fim do encadeamento.")

    linhas.append("\n3) FATOS DERIVADOS")
    if r["derivados"]:
        for d in r["derivados"]:
            linhas.append(f"   - {d['fato']} = sim (concluído por {d['regra']} na rodada {d['rodada']})")
    else:
        linhas.append("   (nenhum fato derivado)")

    linhas.append("\n4) CONCLUSÃO")
    if r["conclusao"] == SAIDA_INSUFICIENTE:
        linhas.append(f"   {SAIDA_INSUFICIENTE}: não foi possível concluir.")
        linhas.append(f"   Motivo: {r['motivo']}")
        if r["em_aberto"]:
            linhas.append("   Encaminhamento: confirme as informações que faltam e consulte de novo;")
            linhas.append("   se não for possível confirmar, procure um técnico.")
        else:
            linhas.append("   Encaminhamento: análise humana (procure um técnico de confiança).")
    else:
        principal = SAIDAS[r["principal"]]
        linhas.append(f"   Encaminhamento principal: {r['principal']} - {principal['nome']}")
        linhas.append(f"   ({principal['descricao']})")
        for saida, ids in r["saidas"].items():
            marca = "  [SUSPENSA pela política de prioridade]" if saida in r["suspensas"] else ""
            linhas.append(f"\n   >> {saida} (regras {', '.join(ids)}){marca}")
            for rid in ids:
                regra = REGRA_POR_ID[rid]
                linhas.append(f"      {rid} | {regra['hipotese']}")
                linhas.append(f"          Por quê: {porque(regra, r['fatos_finais'])}")
                linhas.append(f"          O que fazer: {regra['recomendacao']}")
                if regra["alerta"]:
                    linhas.append(f"          Segurança: {regra['alerta']}")
                linhas.append(f"          Fonte: {regra['fonte']} - {FONTES[regra['fonte']]}")
        if r["suspensas"]:
            linhas.append("\n   Política de prioridade: com risco de perda de dados, ações do usuário que "
                          "gravam no disco ficam suspensas até o backup ser feito.")
        if r["em_aberto"]:
            linhas.append("\n   Também ficaram em aberto (faltou informação): "
                          + "; ".join(f"{e['regra']} ({e['motivo']})" for e in r["em_aberto"]))

    linhas.append("\n5) REGRAS QUE SUSTENTAM A SAÍDA")
    sustentam = [rid for ids in r["saidas"].values() for rid in ids]
    cadeia = [d["regra"] for d in r["derivados"]
              if any(d["fato"] in REGRA_POR_ID[s]["se"] for s in sustentam)]
    if sustentam:
        linhas.append(f"   {', '.join(cadeia + sustentam)}")
    else:
        linhas.append("   Nenhuma (a saída DADOS_INSUFICIENTES é produzida pelo próprio motor).")

    linhas.append(f"\nAviso: {AVISO_GERAL}")
    linhas.append(LINHA)
    return "\n".join(linhas)


# ----------------------------------------------------------------------------
# Modos de execução
# ----------------------------------------------------------------------------
def executar_caso(cid):
    caso = CASOS[cid]
    titulo = f"CASO {cid} ({caso['tipo']}): {caso['descricao']}"
    print(explicar(inferir(caso["fatos"]), titulo))


def ler(texto):
    valor = input(texto)
    if not sys.stdin.isatty():  # mostra a resposta quando a entrada vem de arquivo
        print(valor)
    return valor.strip().lower()


def perguntar(fato):
    while True:
        resposta = ler(f"\n> {FATOS_ENTRADA[fato]['pergunta']}\n  [s] sim   [n] não   [?] não sei: ")
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        if resposta in ("?", "ns", "nao sei", "não sei"):
            return None
        print("  Resposta inválida. Digite s, n ou ?")


def modo_interativo():
    print(LINHA)
    print("  DiagnoPC - Sistema especialista de triagem de computadores")
    print(LINHA)
    print(AVISO_GERAL)
    fatos = {}
    while True:
        print("\nQual é o problema principal?")
        for chave, nome in CATEGORIAS.items():
            print(f"  [{chave}] {nome}")
        print("  [0] Encerrar")
        opcao = ler("Escolha uma opção: ")
        if opcao == "0":
            break
        if opcao not in CATEGORIAS:
            print("  Opção inválida.")
            continue
        while (fato := proxima_pergunta(fatos, opcao)) is not None:
            fatos[fato] = perguntar(fato)
        if ler("\nDeseja investigar outra categoria? [s/n]: ") not in ("s", "sim"):
            break

    if not fatos:
        print("\nConsulta encerrada sem respostas.")
        return
    texto = explicar(inferir(fatos))
    print("\n" + texto)
    if ler("\nDeseja salvar este resultado em arquivo? [s/n]: ") in ("s", "sim"):
        pasta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "relatorios")
        os.makedirs(pasta, exist_ok=True)
        caminho = os.path.join(pasta, f"consulta_{datetime.now():%Y%m%d_%H%M%S}.txt")
        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write(texto + "\n")
        print(f"Resultado salvo em: {caminho}")


def main(argumentos):
    if not argumentos:
        modo_interativo()
    elif argumentos[0] == "--exemplos":
        for cid in EXEMPLOS_EXPLICADOS:
            executar_caso(cid)
            print()
    elif argumentos[0] == "--caso" and len(argumentos) > 1 and argumentos[1].upper() in CASOS:
        executar_caso(argumentos[1].upper())
    elif argumentos[0] == "--listar":
        for cid, caso in CASOS.items():
            print(f"{cid} [{caso['tipo']}] {caso['descricao']}")
    else:
        print(__doc__)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except (KeyboardInterrupt, EOFError):
        print("\n\nExecução interrompida.")
