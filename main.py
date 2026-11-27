"""
INTERFACE DO USUÁRIO (terminal)
===============================
Mostra o menu, faz as perguntas, recebe as respostas e exibe o resultado.
Toda a "inteligência" fica no motor e na base de conhecimento; este arquivo
só conversa com o usuário (arquitetura modular, seção 7 do relatório).

Como rodar:   python main.py
"""

import os
import sys
from datetime import datetime

from base_conhecimento import CATEGORIAS, PERGUNTAS, AVISO_GERAL
from motor_inferencia import MemoriaTrabalho, MotorInferencia, consultar, explicar, faltando

LINHA = "=" * 70
NOME_PRIORIDADE = {"alta": "ALTA", "media": "MÉDIA", "baixa": "BAIXA"}
RESPOSTAS_SIM = {"s", "sim", "y"}
RESPOSTAS_NAO = {"n", "nao", "não"}
RESPOSTAS_NAO_SEI = {"?", "ns", "nao sei", "não sei", "naosei"}


def ler(texto):
    """input() que também mostra a resposta quando a entrada vem de um arquivo
    (útil para gerar as evidências de teste automaticamente)."""
    valor = input(texto)
    if not sys.stdin.isatty():
        print(valor)
    return valor.strip()


def perguntar(fato):
    """Faz a pergunta do fato e devolve True (sim), False (não) ou None (não sei)."""
    texto = PERGUNTAS[fato]["pergunta"]
    while True:
        resposta = ler(f"\n> {texto}\n  [s] sim   [n] não   [?] não sei: ").lower()
        if resposta in RESPOSTAS_SIM:
            return True
        if resposta in RESPOSTAS_NAO:
            return False
        if resposta in RESPOSTAS_NAO_SEI:
            return None
        print("  Resposta inválida. Digite s, n ou ?")


def escolher_categoria():
    print("\nQual é o problema principal?")
    for chave, nome in CATEGORIAS.items():
        print(f"  [{chave}] {nome}")
    print("  [0] Encerrar")
    while True:
        opcao = ler("Escolha uma opção: ")
        if opcao == "0" or opcao in CATEGORIAS:
            return opcao
        print("  Opção inválida.")


def montar_resultado(memoria, motor):
    """Gera o texto final do diagnóstico (RF05, RF06, RF07, RF08, RF09)."""
    hipoteses, em_aberto = motor.inferir(memoria)
    avisos = motor.contradicoes(memoria)
    linhas = [LINHA, "RESULTADO DA TRIAGEM", LINHA]

    if avisos:
        linhas.append("\n[!] ATENÇÃO - respostas contraditórias:")
        for a in avisos:
            linhas.append(f"    - {a}")
        linhas.append("    Essas respostas não foram usadas como fatos confirmados. "
                      "Revise-as em uma nova consulta.")

    if hipoteses:
        linhas.append(f"\nHipóteses encontradas ({len(hipoteses)}), "
                      "da maior para a menor prioridade:")
        for i, regra in enumerate(hipoteses, 1):
            linhas.append(f"\n{i}. {regra['hipotese']}")
            linhas.append(f"   Prioridade: {NOME_PRIORIDADE[regra['prioridade']]}")
            linhas.append(f"   Por quê? {explicar(regra, memoria)}")
            linhas.append(f"   O que fazer: {regra['recomendacao']}")
            if regra["alerta"]:
                linhas.append(f"   Segurança: {regra['alerta']}")
    else:
        linhas.append("\nNão foi possível concluir com os dados informados.")
        linhas.append("Tente outra categoria ou procure um técnico de confiança.")

    if em_aberto:
        linhas.append("\nHipóteses EM ABERTO (faltou informação para confirmar):")
        for regra in em_aberto:
            linhas.append(f"  - {regra['id']}: {regra['hipotese']}")
            for p in faltando(regra, memoria):
                linhas.append(f"      Falta saber: {p}")
        linhas.append("  Se conseguir essas informações, faça uma nova consulta.")

    linhas.append(f"\nAviso: {AVISO_GERAL}")
    linhas.append(LINHA)
    return "\n".join(linhas)


def salvar_relatorio(texto, memoria):
    """Salva o resumo da consulta em um arquivo .txt (RF09). Não guarda dados pessoais."""
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "relatorios")
    os.makedirs(pasta, exist_ok=True)
    agora = datetime.now()
    caminho = os.path.join(pasta, f"consulta_{agora:%Y%m%d_%H%M%S}.txt")
    respostas = []
    for fato, valor in memoria.fatos.items():
        if fato in PERGUNTAS:
            texto_valor = {True: "sim", False: "não", None: "não sei"}[valor]
            respostas.append(f"  - {PERGUNTAS[fato]['pergunta']} -> {texto_valor}")
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(f"Consulta realizada em {agora:%d/%m/%Y %H:%M}\n\n")
        arquivo.write("Respostas informadas:\n" + "\n".join(respostas) + "\n\n")
        arquivo.write(texto + "\n")
    return caminho


def main():
    print(LINHA)
    print("  SISTEMA ESPECIALISTA DE DIAGNÓSTICO E MANUTENÇÃO DE COMPUTADORES")
    print(LINHA)
    print(AVISO_GERAL)

    memoria = MemoriaTrabalho()
    motor = MotorInferencia()

    while True:
        categoria = escolher_categoria()
        if categoria == "0":
            break
        print(f"\n--- Triagem: {CATEGORIAS[categoria]} ---")
        consultar(categoria, perguntar, memoria, motor)
        if ler("\nDeseja investigar outra categoria? [s/n]: ").lower() not in RESPOSTAS_SIM:
            break

    if not memoria.fatos:
        print("\nConsulta encerrada sem respostas. Até logo!")
        return

    resultado = montar_resultado(memoria, motor)
    print("\n" + resultado)
    if ler("\nDeseja salvar o resumo da consulta em arquivo? [s/n]: ").lower() in RESPOSTAS_SIM:
        print(f"Resumo salvo em: {salvar_relatorio(resultado, memoria)}")
    print("\nConsulta encerrada. Até logo!")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nConsulta interrompida.")
