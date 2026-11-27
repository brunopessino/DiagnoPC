"""
TESTES AUTOMATIZADOS - Plano de testes da seção 12 do relatório (T01 a T07)
+ T08 adicional para respostas contraditórias (RNF05).

Como rodar (dentro da pasta do projeto):
    python -m unittest discover -s testes -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from motor_inferencia import (MemoriaTrabalho, MotorInferencia, consultar,  # noqa: E402
                              explicar)


def respostas(dicionario):
    """Cria um 'usuário de mentira' que responde de acordo com o dicionário."""
    def responder(fato):
        if fato not in dicionario:
            raise AssertionError(f"O sistema fez uma pergunta inesperada: {fato}")
        return dicionario[fato]
    return responder


def ids(lista_regras):
    return [r["id"] for r in lista_regras]


class TestCenarios(unittest.TestCase):

    def test_T01_sem_energia_tomada_nao_verificada(self):
        """T01: orientar verificações externas antes de levantar falha interna."""
        r = consultar("1", respostas({"sem_energia": True, "tomada_cabo_verificados": False}))
        self.assertEqual(ids(r["hipoteses"]), ["R01"])
        self.assertIn("tomada", r["hipoteses"][0]["recomendacao"].lower())
        self.assertNotIn("R02", ids(r["hipoteses"]))

    def test_T02_tomada_ok_continua_sem_ligar(self):
        """T02: sugerir fonte/botão/placa-mãe SEM instruir abertura da fonte."""
        r = consultar("1", respostas({"sem_energia": True, "tomada_cabo_verificados": True}))
        self.assertEqual(ids(r["hipoteses"]), ["R02"])
        regra = r["hipoteses"][0]
        self.assertIn("avaliação técnica", regra["recomendacao"])
        self.assertIn("NÃO abra a fonte", regra["alerta"])

    def test_T03_liga_mas_sem_imagem(self):
        """T03: investigar monitor, cabo, entrada e componentes de vídeo."""
        r = consultar("2", respostas({"liga_com_ventoinhas": True, "sem_imagem": True}))
        self.assertEqual(ids(r["hipoteses"]), ["R03"])
        texto = r["hipoteses"][0]["recomendacao"].lower()
        for palavra in ("monitor", "cabo", "entrada", "placa de vídeo"):
            self.assertIn(palavra, texto)

    def test_T04_desliga_em_jogo_com_aquecimento(self):
        """T04: apresentar superaquecimento como hipótese e recomendar avaliação."""
        r = consultar("4", respostas({"desliga_sozinho": True, "ocorre_durante_carga": True,
                                      "aquecimento_ou_ruido": True}))
        self.assertIn("R05", ids(r["hipoteses"]))
        r05 = r["hipoteses"][0]
        self.assertEqual(r05["id"], "R05")            # prioridade alta vem primeiro
        self.assertIn("superaquecimento", r05["hipotese"].lower())
        self.assertIn("avaliação técnica", r05["recomendacao"])

    def test_T05_nao_sei_sobre_temperatura(self):
        """T05: 'não sei' NÃO pode ser tratado como 'não'; hipótese fica em aberto."""
        r = consultar("4", respostas({"desliga_sozinho": False,
                                      "aquecimento_ou_ruido": None}))
        self.assertEqual(r["hipoteses"], [])
        self.assertIn("R06", ids(r["em_aberto"]))
        self.assertIsNone(r["memoria"].valor("aquecimento_ou_ruido"))  # guardado como desconhecido

    def test_T06_sintomas_sem_regra(self):
        """T06: nenhum sintoma bate -> sem hipóteses, nada em aberto."""
        r = consultar("6", respostas({"funciona_por_cabo": False,
                                      "falha_varios_dispositivos": False}))
        self.assertEqual(r["hipoteses"], [])
        self.assertEqual(r["em_aberto"], [])

    def test_T07_duas_regras_aplicaveis(self):
        """T07: apresentar hipóteses múltiplas e explicar os indícios de cada uma."""
        r = consultar("4", respostas({"desliga_sozinho": True, "ocorre_durante_carga": True,
                                      "aquecimento_ou_ruido": True}))
        self.assertEqual(ids(r["hipoteses"]), ["R05", "R06"])
        for regra in r["hipoteses"]:
            explicacao = explicar(regra, r["memoria"])
            self.assertTrue(explicacao.startswith(f"Regra {regra['id']} acionada porque"))

    def test_T08_respostas_contraditorias(self):
        """T08 (adicional): respostas contraditórias não viram fatos confirmados."""
        memoria = MemoriaTrabalho()
        motor = MotorInferencia()
        consultar("1", respostas({"sem_energia": True, "tomada_cabo_verificados": True}),
                  memoria, motor)
        consultar("2", respostas({"liga_com_ventoinhas": True, "sem_imagem": True}),
                  memoria, motor)
        hipoteses, em_aberto = motor.inferir(memoria)
        self.assertEqual(len(motor.contradicoes(memoria)), 1)
        self.assertNotIn("R02", ids(hipoteses))
        self.assertNotIn("R03", ids(hipoteses))
        self.assertIn("R02", ids(em_aberto))

    def test_pergunta_desnecessaria_e_pulada(self):
        """RF02: se a primeira resposta já descarta a regra, a próxima pergunta é pulada."""
        r = consultar("1", respostas({"sem_energia": False}))   # não pergunta sobre tomada
        self.assertEqual(r["hipoteses"], [])
        self.assertFalse(r["memoria"].foi_perguntado("tomada_cabo_verificados"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
