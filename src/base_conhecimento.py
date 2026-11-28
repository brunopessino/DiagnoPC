"""
BASE DE CONHECIMENTO - DiagnoPC
===============================
Somente DADOS e CONHECIMENTO. Nenhuma lógica de execução fica aqui
(o motor está em inferencia.py e a apresentação em executar.py).
Mudar, incluir ou remover uma regra NÃO exige alterar o motor.

Decisão apoiada:
    "Qual é o primeiro encaminhamento SEGURO para um problema comum
     de computador relatado pelo usuário?"

Conteúdo deste arquivo:
    FONTES             - fontes identificáveis que sustentam as regras
    CATEGORIAS         - grupos de sintomas (para o modo interativo)
    FATOS_ENTRADA      - fatos observáveis perguntados ao usuário
    FATOS_DERIVADOS    - fatos que só podem ser concluídos por regras
    SAIDAS             - conclusões finais possíveis (encaminhamentos)
    PRIORIDADE_SAIDAS  - política escrita de prioridade
    REGRAS             - regras de produção SE-ENTÃO (R01 a R13)
    CONTRADICOES       - pares de respostas incompatíveis

Valores dos fatos de entrada:
    True  = sim | False = não | None = não sei
    Fato ausente = ainda não informado. "Não sei" e "ausente" NUNCA viram "não".
"""

# ---------------------------------------------------------------------------
# FONTES (detalhes completos em docs/escopo_e_fontes.md)
# ---------------------------------------------------------------------------
FONTES = {
    "F1": "Dell Support - Computer Won't Turn On: Troubleshoot Power Issues",
    "F2": "Dell Support - Computer Turns On But No Display: Troubleshoot Display Problems",
    "F3": "Microsoft Support - Tips to improve PC performance in Windows",
    "F4": "Microsoft Support - Free up drive space in Windows",
    "F5": "Intel Support - Overheating Symptoms and Troubleshooting (art. 000005791)",
    "F6": "Seagate Support - Identifying Hard Drive Sounds and Determining What They Mean",
    "F7": "Microsoft Support - Fix Wi-Fi connection issues in Windows",
    "F8": "Política de segurança do projeto (Relatório de proposta DiagnoPC, nov/2026, seção 13)",
}

# ---------------------------------------------------------------------------
# CATEGORIAS (o usuário escolhe uma no modo interativo)
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
# FATOS DE ENTRADA: fato -> pergunta + frases usadas na explicação
# ---------------------------------------------------------------------------
FATOS_ENTRADA = {
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
    "inicializacao_lenta": {
        "pergunta": "Aparece imagem, mas o Windows demora muito para iniciar?",
        "sim": "o Windows demora muito para iniciar",
        "nao": "o Windows inicia em tempo normal",
    },
    "lentidao_geral": {
        "pergunta": "O computador fica lento durante o uso normal?",
        "sim": "o computador fica lento durante o uso",
        "nao": "o computador não fica lento durante o uso",
    },
    "memoria_no_limite": {
        "pergunta": "No Gerenciador de Tarefas, o uso de memória (RAM) costuma ficar perto de 100%?",
        "sim": "o uso de memória RAM fica perto do limite",
        "nao": "o uso de memória RAM não fica perto do limite",
    },
    "disco_quase_cheio": {
        "pergunta": "O disco principal (C:) está quase cheio? (Configurações > Sistema > "
                    "Armazenamento mostra a barra vermelha ou pouco espaço livre)",
        "sim": "o disco principal está quase cheio",
        "nao": "o disco principal tem espaço livre suficiente",
    },
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
    "disco_alertas_ruidos": {
        "pergunta": "O HD/SSD mostra alertas, erros de leitura/gravação ou faz ruídos "
                    "estranhos (cliques fortes, raspados)?",
        "sim": "o armazenamento apresenta alertas, erros ou ruídos anormais",
        "nao": "o armazenamento não apresenta alertas, erros ou ruídos",
    },
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
# FATOS DERIVADOS: só existem se uma regra os concluir (nunca são perguntados)
# ---------------------------------------------------------------------------
FATOS_DERIVADOS = {
    "suspeita_termica": {
        "sim": "há suspeita de desligamento por proteção térmica (conclusão da regra R05)",
    },
}

# ---------------------------------------------------------------------------
# SAÍDAS (conclusões finais). "favoravel" = ação permitida/recomendada ao usuário.
# ---------------------------------------------------------------------------
SAIDAS = {
    "VERIFICACAO_BASICA": {
        "nome": "Verificação básica segura",
        "descricao": "O próprio usuário pode fazer verificações externas simples e seguras.",
        "favoravel": True,
    },
    "AJUSTE_DE_SOFTWARE": {
        "nome": "Ajuste de software pelo usuário",
        "descricao": "O usuário pode ajustar configurações do Windows por conta própria.",
        "favoravel": True,
    },
    "MELHORAR_VENTILACAO": {
        "nome": "Melhorar a ventilação",
        "descricao": "O usuário pode desobstruir as entradas de ar e reduzir o calor.",
        "favoravel": True,
    },
    "VERIFICAR_REDE_EXTERNA": {
        "nome": "Verificar a rede externa",
        "descricao": "Reiniciar modem/roteador; se persistir, acionar o provedor de internet.",
        "favoravel": True,
    },
    "ASSISTENCIA_TECNICA": {
        "nome": "Encaminhar para assistência técnica",
        "descricao": "O caso precisa de avaliação humana especializada.",
        "favoravel": False,
    },
    "BACKUP_E_INTERROMPER": {
        "nome": "Fazer backup e interromper o uso",
        "descricao": "Proteger os dados antes de qualquer outra ação e procurar assistência.",
        "favoravel": False,
    },
}

# Saída do sistema (não é regra) quando nenhuma regra pode concluir
SAIDA_INSUFICIENTE = "DADOS_INSUFICIENTES"

# ---------------------------------------------------------------------------
# POLÍTICA DE PRIORIDADE (conflito real do domínio)
# Um disco com sinais de falha NÃO deve receber limpezas, desfragmentação ou
# outras ações que gravem dados: proteger os dados vem primeiro (fonte F6).
#   1) BACKUP_E_INTERROMPER  suspende as saídas favoráveis do usuário
#   2) ASSISTENCIA_TECNICA
#   3) demais saídas (favoráveis), na ordem desta lista
# Número menor = mais prioritário.
# ---------------------------------------------------------------------------
PRIORIDADE_SAIDAS = {
    "BACKUP_E_INTERROMPER": 1,
    "ASSISTENCIA_TECNICA": 2,
    "VERIFICACAO_BASICA": 3,
    "MELHORAR_VENTILACAO": 3,
    "VERIFICAR_REDE_EXTERNA": 3,
    "AJUSTE_DE_SOFTWARE": 3,
}
# Saídas que bloqueiam (suspendem) as ações favoráveis do usuário
SAIDAS_QUE_SUSPENDEM = {"BACKUP_E_INTERROMPER"}

# ---------------------------------------------------------------------------
# REGRAS DE PRODUÇÃO
#   se:     {fato: valor_exigido}   (todas precisam ser confirmadas)
#   entao:  "fato" (fato derivado) e/ou "saida" (conclusão final)
# ---------------------------------------------------------------------------
REGRAS = [
    {
        "id": "R01", "categoria": "1", "fonte": "F1",
        "se": {"sem_energia": True, "tomada_cabo_verificados": False},
        "entao": {"saida": "VERIFICACAO_BASICA"},
        "hipotese": "Possível problema na alimentação externa (tomada, filtro de linha ou cabo).",
        "recomendacao": "Teste a tomada com outro aparelho, confira o filtro de linha, o cabo de "
                        "energia e a chave traseira da fonte (se houver).",
        "alerta": "Não abra a fonte de alimentação: ela pode guardar energia mesmo desligada. (F8)",
    },
    {
        "id": "R02", "categoria": "1", "fonte": "F1",
        "se": {"sem_energia": True, "tomada_cabo_verificados": True},
        "entao": {"saida": "ASSISTENCIA_TECNICA"},
        "hipotese": "Possível falha na fonte de alimentação, no botão de energia ou na placa-mãe.",
        "recomendacao": "Com tomada e cabo confirmados, procure assistência técnica para avaliar "
                        "fonte, botão e placa-mãe.",
        "alerta": "Não abra a fonte nem faça medições elétricas sem qualificação. (F8)",
    },
    {
        "id": "R03", "categoria": "2", "fonte": "F2",
        "se": {"liga_com_ventoinhas": True, "sem_imagem": True},
        "entao": {"saida": "VERIFICACAO_BASICA"},
        "hipotese": "Possível problema de conexão ou configuração do vídeo.",
        "recomendacao": "Confira se o monitor está ligado, se o cabo de vídeo está firme nas duas "
                        "pontas e se a entrada correta (HDMI, DisplayPort...) está selecionada.",
        "alerta": "",
    },
    {
        "id": "R04", "categoria": "3", "fonte": "F3",
        "se": {"inicializacao_lenta": True},
        "entao": {"saida": "AJUSTE_DE_SOFTWARE"},
        "hipotese": "Possível excesso de programas iniciando junto com o Windows.",
        "recomendacao": "Abra o Gerenciador de Tarefas (Ctrl + Shift + Esc) > Aplicativos de "
                        "inicialização e desative os que não precisam iniciar sozinhos.",
        "alerta": "",
    },
    {
        "id": "R05", "categoria": "4", "fonte": "F5",
        "se": {"desliga_sozinho": True, "ocorre_durante_carga": True},
        "entao": {"fato": "suspeita_termica"},
        "hipotese": "Desligamento sob carga é sintoma típico de proteção térmica do processador.",
        "recomendacao": "",
        "alerta": "",
    },
    {
        "id": "R06", "categoria": "4", "fonte": "F5",
        "se": {"aquecimento_ou_ruido": True, "desliga_sozinho": False},
        "entao": {"saida": "MELHORAR_VENTILACAO"},
        "hipotese": "Possível ventilação insuficiente (entradas de ar obstruídas ou poeira).",
        "recomendacao": "Deixe as entradas e saídas de ar livres, use o computador em superfície "
                        "firme e observe se o ruído diminui.",
        "alerta": "Não use aspirador nem objetos metálicos dentro do computador. (F8)",
    },
    {
        "id": "R07", "categoria": "3", "fonte": "F3",
        "se": {"lentidao_geral": True, "memoria_no_limite": True},
        "entao": {"saida": "AJUSTE_DE_SOFTWARE"},
        "hipotese": "Possível falta de memória RAM para a quantidade de programas abertos.",
        "recomendacao": "Feche aplicativos e abas que não está usando e reinicie o computador. "
                        "Se continuar, avalie um upgrade de RAM compatível.",
        "alerta": "",
    },
    {
        "id": "R08", "categoria": "5", "fonte": "F6",
        "se": {"disco_alertas_ruidos": True},
        "entao": {"saida": "BACKUP_E_INTERROMPER"},
        "hipotese": "Possível falha no armazenamento (HD/SSD), com risco para os dados.",
        "recomendacao": "Copie AGORA os arquivos importantes para outro local, evite usar o disco "
                        "e procure assistência técnica.",
        "alerta": "Não faça limpezas, desfragmentação nem formatação no disco suspeito. (F6)",
    },
    {
        "id": "R09", "categoria": "6", "fonte": "F7",
        "se": {"funciona_por_cabo": True, "falha_wifi": True},
        "entao": {"saida": "AJUSTE_DE_SOFTWARE"},
        "hipotese": "Possível problema no Wi-Fi do próprio computador (modo avião ou driver).",
        "recomendacao": "Verifique se o Wi-Fi está ligado e o modo avião desligado (Configurações > "
                        "Rede e Internet). Se continuar, reinstale o driver do adaptador sem fio.",
        "alerta": "",
    },
    {
        "id": "R10", "categoria": "6", "fonte": "F7",
        "se": {"falha_varios_dispositivos": True},
        "entao": {"saida": "VERIFICAR_REDE_EXTERNA"},
        "hipotese": "Possível problema no modem/roteador ou no serviço do provedor.",
        "recomendacao": "Desligue modem e roteador da tomada, aguarde 30 segundos e ligue de novo. "
                        "Se continuar sem internet, entre em contato com o provedor.",
        "alerta": "",
    },
    {
        "id": "R11", "categoria": "4", "fonte": "F5",
        "se": {"suspeita_termica": True, "aquecimento_ou_ruido": True},
        "entao": {"saida": "ASSISTENCIA_TECNICA"},
        "hipotese": "Superaquecimento provável: desliga sob carga E apresenta calor/ruído forte.",
        "recomendacao": "Interrompa jogos e tarefas pesadas e procure assistência técnica para "
                        "limpeza interna e verificação das ventoinhas e da pasta térmica.",
        "alerta": "Desligamentos repetidos podem causar perda de dados: faça backup. (F8)",
    },
    {
        "id": "R12", "categoria": "3", "fonte": "F4",
        "se": {"lentidao_geral": True, "disco_quase_cheio": True},
        "entao": {"saida": "AJUSTE_DE_SOFTWARE"},
        "hipotese": "Possível lentidão causada por pouco espaço livre no disco.",
        "recomendacao": "Libere espaço: esvazie a Lixeira, use a Limpeza de Disco ou ative o "
                        "Sensor de Armazenamento (Configurações > Sistema > Armazenamento).",
        "alerta": "",
    },
    {
        "id": "R13", "categoria": "4", "fonte": "F5",
        "se": {"suspeita_termica": True, "aquecimento_ou_ruido": False},
        "entao": {"saida": "ASSISTENCIA_TECNICA"},
        "hipotese": "Desliga sob carga SEM sinais de calor: a causa pode ser outra "
                    "(ex.: alimentação elétrica).",
        "recomendacao": "Procure assistência técnica para testar a fonte e os demais componentes.",
        "alerta": "Não abra a fonte de alimentação. (F8)",
    },
]

# ---------------------------------------------------------------------------
# CONTRADIÇÕES: respostas que não podem ser verdade ao mesmo tempo.
# Os fatos envolvidos passam a ser tratados como "não sei".
# ---------------------------------------------------------------------------
CONTRADICOES = [
    (("sem_energia", True), ("liga_com_ventoinhas", True),
     "Você disse que o computador não tem sinal de energia, mas também que ele liga."),
    (("funciona_por_cabo", True), ("falha_varios_dispositivos", True),
     "Você disse que a internet funciona por cabo, mas também que não funciona em nenhum aparelho."),
]

AVISO_GERAL = (
    "O DiagnoPC faz apenas uma TRIAGEM. As hipóteses são 'possíveis causas', não defeitos "
    "confirmados. Ele não substitui o manual do fabricante nem a avaliação de um técnico."
)
