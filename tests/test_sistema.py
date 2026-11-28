"""
TESTES AUTOMATIZADOS - DiagnoPC
===============================
Somente Python + assert (sem bibliotecas externas).
Cada teste executa o sistema com um caso fictício (src/casos.py) e afirma a saída esperada.
A cobertura regra -> caso -> teste está em docs/matriz_regra-caso-fonte.md.

Como rodar (a partir da pasta do projeto):
    python tests/test_sistema.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from base_conhecimento import REGRAS, SAIDAS, FONTES  # noqa: E402
from casos import CASOS  # noqa: E402
from inferencia import inferir, proxima_pergunta, EM_ABERTO  # noqa: E402


def rodar(caso_id):
    return inferir(CASOS[caso_id]["fatos"])


# ---------------------------------------------------------------- regra a regra
def test_C01_R01_sem_energia_tomada_nao_verificada():
    r = rodar("C01")
    assert r["aplicadas"] == ["R01"]
    assert r["conclusao"] == "VERIFICACAO_BASICA"


def test_C02_R02_sem_energia_com_tomada_ok():
    r = rodar("C02")
    assert r["aplicadas"] == ["R02"]
    assert r["conclusao"] == "ASSISTENCIA_TECNICA"


def test_C03_R03_liga_sem_imagem():
    r = rodar("C03")
    assert r["aplicadas"] == ["R03"]
    assert r["conclusao"] == "VERIFICACAO_BASICA"


def test_C04_R04_inicializacao_lenta():
    r = rodar("C04")
    assert r["aplicadas"] == ["R04"]
    assert r["conclusao"] == "AJUSTE_DE_SOFTWARE"


def test_C05_R07_R12_caso_favoravel_duas_regras():
    r = rodar("C05")
    assert sorted(r["aplicadas"]) == ["R07", "R12"]
    assert r["conclusao"] == "AJUSTE_DE_SOFTWARE"
    assert r["saidas"]["AJUSTE_DE_SOFTWARE"] == ["R07", "R12"]


def test_C06_R05_R11_regra_encadeada_com_fato_derivado():
    r = rodar("C06")
    assert r["aplicadas"] == ["R05", "R11"]
    assert r["derivados"] == [{"fato": "suspeita_termica", "regra": "R05", "rodada": 1}]
    assert r["conclusao"] == "ASSISTENCIA_TECNICA"
    assert r["rodadas"][1]["aplicadas"] == ["R11"]  # R11 só dispara na 2ª rodada


def test_C07_R05_R13_desliga_sem_calor():
    r = rodar("C07")
    assert r["aplicadas"] == ["R05", "R13"]
    assert r["conclusao"] == "ASSISTENCIA_TECNICA"


def test_C08_R06_aquece_mas_nao_desliga():
    r = rodar("C08")
    assert r["aplicadas"] == ["R06"]
    assert r["conclusao"] == "MELHORAR_VENTILACAO"


def test_C09_R08_disco_com_ruido():
    r = rodar("C09")
    assert r["aplicadas"] == ["R08"]
    assert r["conclusao"] == "BACKUP_E_INTERROMPER"


def test_C10_R09_falha_so_no_wifi():
    r = rodar("C10")
    assert r["aplicadas"] == ["R09"]
    assert r["conclusao"] == "AJUSTE_DE_SOFTWARE"


def test_C11_R10_sem_internet_em_varios_aparelhos():
    r = rodar("C11")
    assert r["aplicadas"] == ["R10"]
    assert r["conclusao"] == "VERIFICAR_REDE_EXTERNA"


# ---------------------------------------------------------------- fronteira e negativos
def test_C12_fronteira_nao_sei_nao_vira_nao():
    r = rodar("C12")
    assert r["conclusao"] == "DADOS_INSUFICIENTES"
    assert "R13" not in r["aplicadas"]          # "não sei" NÃO foi tratado como "não"
    em_aberto = {e["regra"]: e["estado"] for e in r["em_aberto"]}
    assert em_aberto.get("R11") == EM_ABERTO and em_aberto.get("R13") == EM_ABERTO
    assert r["derivados"][0]["fato"] == "suspeita_termica"


def test_C13_negativo_nenhuma_regra_corresponde():
    r = rodar("C13")
    assert r["aplicadas"] == []
    assert r["conclusao"] == "DADOS_INSUFICIENTES"
    assert "análise humana" in r["motivo"]


def test_C14_fronteira_tomada_desconhecida():
    r = rodar("C14")
    assert r["aplicadas"] == []
    assert {e["regra"] for e in r["em_aberto"]} == {"R01", "R02"}
    assert r["conclusao"] == "DADOS_INSUFICIENTES"


def test_C15_politica_de_prioridade_backup_suspende_ajuste():
    r = rodar("C15")
    assert sorted(r["aplicadas"]) == ["R08", "R12"]
    assert r["principal"] == "BACKUP_E_INTERROMPER"
    assert r["suspensas"] == ["AJUSTE_DE_SOFTWARE"]


def test_C16_contradicao_nao_vira_fato_confirmado():
    r = rodar("C16")
    assert len(r["avisos"]) == 1
    assert "R02" not in r["aplicadas"] and "R03" not in r["aplicadas"]
    assert r["conclusao"] == "DADOS_INSUFICIENTES"


# ---------------------------------------------------------------- motor e base
def test_motor_termina_e_nao_duplica_fatos():
    r = rodar("C06")
    assert len(r["rodadas"]) <= len(REGRAS) + 1
    fatos_derivados = [d["fato"] for d in r["derivados"]]
    assert len(fatos_derivados) == len(set(fatos_derivados))
    assert r["rodadas"][-1]["aplicadas"] == []     # última rodada não aplicou nada novo


def test_modo_interativo_pula_pergunta_desnecessaria():
    # Se o PC TEM energia, não faz sentido perguntar sobre a tomada.
    assert proxima_pergunta({}, "1") == "sem_energia"
    assert proxima_pergunta({"sem_energia": False}, "1") is None
    # Desligou sob carga: a próxima pergunta é sobre calor (necessária para R11/R13).
    assert proxima_pergunta({"desliga_sozinho": True, "ocorre_durante_carga": True}, "4") \
        == "aquecimento_ou_ruido"


def test_base_integra_ids_fontes_e_cobertura():
    ids = [r["id"] for r in REGRAS]
    assert len(ids) == len(set(ids)) and len(ids) >= 12
    assert all(r["fonte"] in FONTES for r in REGRAS)
    assert len(SAIDAS) >= 4
    favoraveis = [r for r in REGRAS if SAIDAS.get(r["entao"].get("saida"), {}).get("favoravel")]
    assert len(favoraveis) >= 3
    acionadas = {rid for c in CASOS for rid in rodar(c)["aplicadas"]}
    assert acionadas == set(ids), f"regras sem caso: {set(ids) - acionadas}"


# ---------------------------------------------------------------- executor dos testes
if __name__ == "__main__":
    testes = [(nome, f) for nome, f in list(globals().items())
              if nome.startswith("test_") and callable(f)]
    falhas = 0
    for nome, funcao in testes:
        try:
            funcao()
            print(f"[PASSOU] {nome}")
        except AssertionError as erro:
            falhas += 1
            print(f"[FALHOU] {nome} {erro}")
        except Exception as erro:  # erro inesperado também conta como falha
            falhas += 1
            print(f"[ERRO]   {nome}: {type(erro).__name__}: {erro}")
    print("-" * 60)
    print(f"{len(testes) - falhas} de {len(testes)} testes passaram.")
    sys.exit(1 if falhas else 0)
