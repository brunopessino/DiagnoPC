"""
INTERFACE WEB (EXTRA, opcional) - DiagnoPC
==========================================
A orientação da A4 não exige interface gráfica; esta tela é um extra.
Ela NÃO toma decisões: só envia os fatos ao MESMO motor (inferencia.py)
e mostra a conclusão e a explicação produzidas por ele.

Usa apenas a biblioteca padrão do Python.
Como rodar (a partir da pasta do projeto):   python src/interface_web.py
O navegador abre sozinho em http://localhost:8000  (Ctrl + C para desligar)
"""

import json
import os
import webbrowser
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from base_conhecimento import (AVISO_GERAL, CATEGORIAS, FATOS_ENTRADA, FONTES, REGRAS,
                               SAIDAS)
from executar import explicar, porque
from inferencia import inferir, proxima_pergunta

PASTA = os.path.dirname(os.path.abspath(__file__))
PASTA_WEB = os.path.join(PASTA, "web")
PASTA_RELATORIOS = os.path.join(os.path.dirname(PASTA), "relatorios")
REGRA_POR_ID = {r["id"]: r for r in REGRAS}


def limpar_fatos(fatos):
    """Aceita somente fatos de entrada conhecidos com valor true/false/null."""
    return {f: v for f, v in (fatos or {}).items()
            if f in FATOS_ENTRADA and v in (True, False, None)}


def api_inicio(_):
    return {"categorias": [{"id": k, "nome": v} for k, v in CATEGORIAS.items()],
            "aviso": AVISO_GERAL}


def api_proxima(dados):
    fato = proxima_pergunta(limpar_fatos(dados.get("fatos")), str(dados.get("categoria")))
    if fato is None:
        return {"fato": None}
    return {"fato": fato, "pergunta": FATOS_ENTRADA[fato]["pergunta"]}


def api_resultado(dados):
    r = inferir(limpar_fatos(dados.get("fatos")))
    grupos = []
    for saida, ids in r["saidas"].items():
        grupos.append({
            "saida": saida,
            "nome": SAIDAS[saida]["nome"],
            "descricao": SAIDAS[saida]["descricao"],
            "favoravel": SAIDAS[saida]["favoravel"],
            "principal": saida == r["principal"],
            "suspensa": saida in r["suspensas"],
            "regras": [{
                "id": rid,
                "hipotese": REGRA_POR_ID[rid]["hipotese"],
                "porque": porque(REGRA_POR_ID[rid], r["fatos_finais"]),
                "recomendacao": REGRA_POR_ID[rid]["recomendacao"],
                "alerta": REGRA_POR_ID[rid]["alerta"],
                "fonte": f"{REGRA_POR_ID[rid]['fonte']} - {FONTES[REGRA_POR_ID[rid]['fonte']]}",
            } for rid in ids],
        })
    return {
        "conclusao": r["conclusao"],
        "motivo": r["motivo"],
        "grupos": grupos,
        "derivados": r["derivados"],
        "em_aberto": r["em_aberto"],
        "avisos": r["avisos"],
        "trilha": explicar(r),
        "aviso": AVISO_GERAL,
    }


def api_salvar(dados):
    texto = explicar(inferir(limpar_fatos(dados.get("fatos"))))
    os.makedirs(PASTA_RELATORIOS, exist_ok=True)
    caminho = os.path.join(PASTA_RELATORIOS, f"consulta_{datetime.now():%Y%m%d_%H%M%S}.txt")
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto + "\n")
    return {"caminho": caminho}


ROTAS = {"/api/inicio": api_inicio, "/api/proxima": api_proxima,
         "/api/resultado": api_resultado, "/api/salvar": api_salvar}


class Manipulador(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PASTA_WEB, **kwargs)

    def _json(self, corpo, status=200):
        dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_POST(self):
        rota = ROTAS.get(self.path)
        if rota is None:
            self._json({"erro": "rota não encontrada"}, 404)
            return
        try:
            tamanho = int(self.headers.get("Content-Length", 0))
            self._json(rota(json.loads(self.rfile.read(tamanho) or b"{}")))
        except Exception as erro:
            self._json({"erro": str(erro)}, 500)

    def log_message(self, *args):
        pass


def iniciar(porta=8000):
    for tentativa in range(porta, porta + 10):
        try:
            servidor = ThreadingHTTPServer(("127.0.0.1", tentativa), Manipulador)
            break
        except OSError:
            continue
    else:
        raise SystemExit("Não encontrei uma porta livre entre 8000 e 8009.")
    endereco = f"http://localhost:{tentativa}"
    print("=" * 60)
    print("  DiagnoPC está no ar!")
    print(f"  Abra no navegador: {endereco}")
    print("  Pode minimizar esta janela. Para desligar: Ctrl + C (ou feche a janela).")
    print("=" * 60)
    webbrowser.open(endereco)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nDiagnoPC desligado. Até logo!")


if __name__ == "__main__":
    iniciar()
