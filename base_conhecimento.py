"""
BASE DE CONHECIMENTO
====================
Aqui fica TODO o conhecimento do especialista, separado do motor de inferência
(seção 5.1 do relatório). Para mudar o diagnóstico, basta editar este arquivo:
o motor e a interface não precisam ser alterados (RNF04 - Manutenibilidade).

Conteúdo:
  - CATEGORIAS: grupos de problemas que o usuário pode escolher (RF01).
  - PERGUNTAS:  cada fato que o sistema pode perguntar, com o texto da pergunta
                e a frase usada na explicação (RF02, RF07).
  - REGRAS:     regras de produção SE-ENTÃO (seção 8 do relatório).
  - CONTRADICOES: pares de respostas que não podem ser verdade ao mesmo tempo (RNF05).
"""

# ---------------------------------------------------------------------------
# Categorias (Apêndice A do relatório)
# ---------------------------------------------------------------------------
CATEGORIAS = {
    "1": "Alimentação (o computador não liga)",
    "2": "Vídeo (liga, mas não aparece imagem)",
    "3": "Desempenho (lentidão)",
    "4": "Temperatura e estabilidade (desliga sozinho, esquenta, barulho)",
    "5": "Armazenamento (HD/SSD com erros ou ruídos)",
    "6": "Rede (internet / Wi-Fi)",
}

# ---------------------------------------------------------------------------
# Perguntas: fato -> texto da pergunta + frases usadas na explicação
# ---------------------------------------------------------------------------
PERGUNTAS = {
    # Alimentação
    "sem_energia": {
        "pergunta": "O computador não apresenta NENHUM sinal de energia "
                    "(nenhuma luz, ventoinha ou som ao apertar o botão)?",
        "sim": "o computador não apresenta nenhum sinal de energia",
        "nao": "o computador apresenta algum sinal de energia",
    },
    "tomada_cabo_verificados": {
        "pergunta": "Você já confirmou que a tomada funciona (testando outro aparelho nela) "
                    "e que o cabo de energia está bem conectado?",
        "sim": "a tomada funciona e o cabo de energia está conectado",
        "nao": "a tomada e o cabo de energia ainda não foram verificados",
    },
    # Vídeo
    "liga_com_ventoinhas": {
        "pergunta": "O computador liga e as ventoinhas (ventiladores) funcionam?",
        "sim": "o computador liga e as ventoinhas funcionam",
        "nao": "o computador não liga ou as ventoinhas não funcionam",
    },
    "sem_imagem": {
        "pergunta": "Mesmo ligado, a tela fica sem nenhuma imagem?",
        "sim": "não aparece imagem na tela",
        "nao": "aparece imagem na tela",
    },
    # Desempenho
    "inicializacao_lenta": {
        "pergunta": "Aparece imagem, mas o sistema operacional (ex.: Windows) "
                    "demora muito para iniciar?",
        "sim": "o sistema operacional demora muito para iniciar",
        "nao": "o sistema operacional inicia em tempo normal",
    },
    "lentidao_geral": {
        "pergunta": "O computador fica lento durante o uso normal?",
        "sim": "o computador fica lento durante o uso",
        "nao": "o computador não fica lento durante o uso",
    },
    "memoria_no_limite": {
        "pergunta": "No Gerenciador de Tarefas, o uso de memória (RAM) costuma ficar "
                    "perto de 100%?",
        "sim": "o uso de memória RAM fica frequentemente perto do limite",
        "nao": "o uso de memória RAM não fica perto do limite",
    },
    # Temperatura e estabilidade
    "desliga_sozinho": {
        "pergunta": "O computador desliga sozinho, sem você mandar?",
        "sim": "o computador desliga sozinho",
        "nao": "o computador não desliga sozinho",
    },
    "ocorre_durante_carga": {
        "pergunta": "Isso acontece durante jogos ou tarefas pesadas "
                    "(edição de vídeo, muitos programas abertos)?",
        "sim": "o desligamento acontece durante jogos ou tarefas pesadas",
        "nao": "o desligamento não está ligado a tarefas pesadas",
    },
    "aquecimento_ou_ruido": {
        "pergunta": "O computador esquenta muito ou as ventoinhas ficam muito barulhentas?",
        "sim": "o computador esquenta muito ou as ventoinhas ficam muito ruidosas",
        "nao": "não há aquecimento excessivo nem ruído forte de ventoinhas",
    },
    # Armazenamento
    "disco_alertas_ruidos": {
        "pergunta": "O HD/SSD mostra alertas, erros de leitura/gravação ou faz ruídos "
                    "estranhos (cliques, raspados)?",
        "sim": "o armazenamento apresenta alertas, erros ou ruídos anormais",
        "nao": "o armazenamento não apresenta alertas, erros ou ruídos",
    },
    # Rede
    "funciona_por_cabo": {
        "pergunta": "A internet funciona quando o computador está ligado por cabo de rede?",
        "sim": "a internet funciona por cabo",
        "nao": "a internet não funciona por cabo",
    },
    "falha_wifi": {
        "pergunta": "A internet NÃO funciona pelo Wi-Fi neste computador?",
        "sim": "a internet não funciona pelo Wi-Fi",
        "nao": "a internet funciona pelo Wi-Fi",
    },
    "falha_varios_dispositivos": {
        "pergunta": "A internet também não funciona em outros aparelhos "
                    "(celular, outro computador) na mesma rede?",
        "sim": "a internet também não funciona em outros dispositivos",
        "nao": "a internet funciona em outros dispositivos",
    },
}

# ---------------------------------------------------------------------------
# Regras de produção (tabela da seção 8 do relatório)
#   condicoes: {fato: valor_esperado}  -> todas precisam ser confirmadas
#   prioridade: "alta", "media" ou "baixa"
# ---------------------------------------------------------------------------
REGRAS = [
    {
        "id": "R01",
        "categoria": "1",
        "condicoes": {"sem_energia": True, "tomada_cabo_verificados": False},
        "hipotese": "Possível problema na alimentação externa (tomada, filtro de linha ou cabo).",
        "recomendacao": "Confira a tomada, o filtro de linha, o cabo de energia e a chave "
                        "traseira da fonte (se houver). Teste outro cabo ou outra tomada.",
        "alerta": "NÃO abra a fonte de alimentação: ela guarda energia mesmo desligada.",
        "prioridade": "media",
    },
    {
        "id": "R02",
        "categoria": "1",
        "condicoes": {"sem_energia": True, "tomada_cabo_verificados": True},
        "hipotese": "Possível falha na fonte de alimentação, no botão de energia ou na placa-mãe.",
        "recomendacao": "Procure avaliação técnica para testar fonte, botão e placa-mãe.",
        "alerta": "NÃO abra a fonte nem faça medições elétricas sem qualificação.",
        "prioridade": "alta",
    },
    {
        "id": "R03",
        "categoria": "2",
        "condicoes": {"liga_com_ventoinhas": True, "sem_imagem": True},
        "hipotese": "Possível problema de vídeo (monitor, cabo, entrada, memória RAM ou placa de vídeo).",
        "recomendacao": "Confira se o monitor está ligado, se o cabo de vídeo está firme e se a "
                        "entrada correta (HDMI, DisplayPort...) está selecionada. Se continuar, "
                        "procure avaliação técnica para memória RAM e placa de vídeo.",
        "alerta": "Desligue o computador da tomada antes de mexer em qualquer cabo interno.",
        "prioridade": "media",
    },
    {
        "id": "R04",
        "categoria": "3",
        "condicoes": {"inicializacao_lenta": True},
        "hipotese": "Possível lentidão no armazenamento, excesso de programas na inicialização, "
                    "pouco espaço livre ou memória insuficiente.",
        "recomendacao": "Verifique o espaço livre no disco, desative programas desnecessários "
                        "na inicialização (Gerenciador de Tarefas > Inicializar) e observe o uso de memória.",
        "alerta": "",
        "prioridade": "baixa",
    },
    {
        "id": "R05",
        "categoria": "4",
        "condicoes": {"desliga_sozinho": True, "ocorre_durante_carga": True},
        "hipotese": "Possível superaquecimento ou instabilidade de alimentação.",
        "recomendacao": "Interrompa as tarefas que provocam o desligamento, mantenha as entradas "
                        "de ar livres e procure avaliação técnica para medir temperaturas e "
                        "verificar a alimentação.",
        "alerta": "Desligamentos repetidos podem causar perda de dados: faça backup se possível.",
        "prioridade": "alta",
    },
    {
        "id": "R06",
        "categoria": "4",
        "condicoes": {"aquecimento_ou_ruido": True},
        "hipotese": "Possível problema de refrigeração (poeira, entradas de ar obstruídas ou "
                    "ventoinha com defeito).",
        "recomendacao": "Verifique se as entradas de ar estão livres e se há acúmulo de poeira. "
                        "Recomenda-se limpeza adequada, de preferência por um técnico.",
        "alerta": "Não use aspirador nem objetos metálicos dentro do computador.",
        "prioridade": "media",
    },
    {
        "id": "R07",
        "categoria": "3",
        "condicoes": {"lentidao_geral": True, "memoria_no_limite": True},
        "hipotese": "Possível falta de memória RAM para o uso atual.",
        "recomendacao": "Feche aplicativos que não está usando e avalie um upgrade de RAM "
                        "compatível com o seu computador.",
        "alerta": "",
        "prioridade": "media",
    },
    {
        "id": "R08",
        "categoria": "5",
        "condicoes": {"disco_alertas_ruidos": True},
        "hipotese": "Possível falha no armazenamento (HD/SSD).",
        "recomendacao": "PRIORIDADE: faça uma cópia de segurança (backup) dos seus arquivos "
                        "agora, se ainda for possível, e procure assistência técnica.",
        "alerta": "Se houver ruído de falha (cliques), PARE de usar o disco para não perder dados.",
        "prioridade": "alta",
    },
    {
        "id": "R09",
        "categoria": "6",
        "condicoes": {"funciona_por_cabo": True, "falha_wifi": True},
        "hipotese": "Possível problema no Wi-Fi do computador (adaptador sem fio, modo avião ou driver).",
        "recomendacao": "Verifique se o modo avião está desligado e se o Wi-Fi está ativado. "
                        "Reinicie o roteador e confira o driver do adaptador sem fio.",
        "alerta": "",
        "prioridade": "baixa",
    },
    {
        "id": "R10",
        "categoria": "6",
        "condicoes": {"falha_varios_dispositivos": True},
        "hipotese": "Possível problema no roteador/modem ou no serviço do provedor de internet.",
        "recomendacao": "Reinicie o roteador e o modem. Se continuar, entre em contato com o "
                        "provedor para verificar instabilidade externa.",
        "alerta": "",
        "prioridade": "media",
    },
]

# ---------------------------------------------------------------------------
# Contradições (RNF05): respostas que não podem ser verdade juntas.
# Se aparecerem, o sistema avisa e não trata o caso como confirmado.
# ---------------------------------------------------------------------------
CONTRADICOES = [
    (("sem_energia", True), ("liga_com_ventoinhas", True),
     "Você disse que o computador não tem sinal de energia, mas também que ele liga."),
    (("funciona_por_cabo", True), ("falha_varios_dispositivos", True),
     "Você disse que a internet funciona por cabo, mas também que não funciona em nenhum aparelho."),
]

# Aviso geral de segurança mostrado em toda consulta (RNF03, seção 13)
AVISO_GERAL = (
    "Este sistema faz apenas uma TRIAGEM. As hipóteses são 'possíveis causas', não defeitos "
    "confirmados. Ele não substitui o manual do fabricante nem a avaliação de um técnico."
)
