"""
INTERFACE WEB - DiagnoPC
========================
Evolução prevista na seção 7.2 do relatório: interface web (HTML, CSS e JavaScript)
mantendo o motor de inferência SEPARADO da camada visual.

Este arquivo é um pequeno servidor feito só com a biblioteca padrão do Python
(não precisa instalar nada). Ele:
  - entrega as páginas da pasta "web/" (HTML, CSS, JS);
  - oferece uma API que usa o MESMO motor_inferencia.py do terminal.

Como rodar:   python servidor_web.py
O navegador abre sozinho em http://localhost:8000
"""

import json
import os
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from base_conhecimento import CATEGORIAS, PERGUNTAS, AVISO_GERAL
from motor_inferencia import MemoriaTrabalho, MotorInferencia, explicar, faltando
from main import montar_resultado, salvar_relatorio

PASTA_WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
motor = MotorInferencia()


def memoria_a_partir_de(fatos):
    """Recria a memória de trabalho com os fatos enviados pela tela (true/false/null)."""
    memoria = MemoriaTrabalho()
    for fato, valor in (fatos or {}).items():
        if fato in PERGUNTAS and valor in (True, False, None):
            memoria.registrar(fato, valor)
    return memoria


def api_inicio(_dados):
    return {
        "categorias": [{"id": k, "nome": v} for k, v in CATEGORIAS.items()],
        "aviso": AVISO_GERAL,
    }


def api_proxima(dados):
    memoria = memoria_a_partir_de(dados.get("fatos"))
    fato = motor.proxima_pergunta(memoria, str(dados.get("categoria")))
    if fato is None:
        return {"fato": None}
    return {"fato": fato, "pergunta": PERGUNTAS[fato]["pergunta"]}


def api_resultado(dados):
    memoria = memoria_a_partir_de(dados.get("fatos"))
    hipoteses, em_aberto = motor.inferir(memoria)
    return {
        "hipoteses": [{
            "id": r["id"],
            "hipotese": r["hipotese"],
            "prioridade": r["prioridade"],
            "explicacao": explicar(r, memoria),
            "recomendacao": r["recomendacao"],
            "alerta": r["alerta"],
        } for r in hipoteses],
        "em_aberto": [{
            "id": r["id"],
            "hipotese": r["hipotese"],
            "faltando": faltando(r, memoria),
        } for r in em_aberto],
        "contradicoes": motor.contradicoes(memoria),
        "aviso": AVISO_GERAL,
    }


def api_salvar(dados):
    memoria = memoria_a_partir_de(dados.get("fatos"))
    texto = montar_resultado(memoria, motor)
    caminho = salvar_relatorio(texto, memoria)
    return {"caminho": caminho, "texto": texto}


ROTAS = {
    "/api/inicio": api_inicio,
    "/api/proxima": api_proxima,
    "/api/resultado": api_resultado,
    "/api/salvar": api_salvar,
}


class Manipulador(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PASTA_WEB, **kwargs)

    def _responder_json(self, corpo, status=200):
        dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_POST(self):
        rota = ROTAS.get(self.path)
        if rota is None:
            self._responder_json({"erro": "rota não encontrada"}, 404)
            return
        try:
            tamanho = int(self.headers.get("Content-Length", 0))
            dados = json.loads(self.rfile.read(tamanho) or b"{}")
            self._responder_json(rota(dados))
        except Exception as erro:  # mostra o erro em vez de derrubar o servidor
            self._responder_json({"erro": str(erro)}, 500)

    def log_message(self, formato, *args):
        pass  # deixa o terminal limpo


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
    print("  Para desligar, volte aqui e aperte Ctrl + C")
    print("=" * 60)
    webbrowser.open(endereco)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nDiagnoPC desligado. Até logo!")


if __name__ == "__main__":
    iniciar()
