# Transcrição do vídeo — DiagnoPC

**Link do vídeo (não listado no YouTube):** *[colar aqui o link depois de publicar]*

**Duração prevista:** cerca de 7 minutos. A transcrição segue os mesmos blocos do vídeo.

---

## Bloco 1 (0:00–0:45) — Decisão, usuário, escopo e limite

*Na tela: README.md aberto na seção 1 e 2.*

"Olá! Este é o DiagnoPC, um protótipo de sistema especialista em Python para a disciplina de Programação de Sistemas Especialistas.
A decisão que ele apoia é: qual é o primeiro encaminhamento seguro para um problema comum de computador.
O usuário é uma pessoa sem formação técnica, com um computador Windows que não liga, está sem imagem, lento, desligando sozinho, com disco fazendo barulho ou sem internet.
O sistema faz só uma triagem: ele não confirma defeito de peça, não manda abrir o computador e não faz medição elétrica. Quando não dá para concluir, ou quando o caso é sério, ele encaminha para backup ou para um técnico."

## Bloco 2 (0:45–1:30) — Fontes e como sustentam as regras

*Na tela: docs/escopo_e_fontes.md.*

"As regras vêm de oito fontes identificadas. Sete são páginas oficiais de suporte: Dell, para computador que não liga e sem imagem; Microsoft, para desempenho, espaço em disco e Wi-Fi; Intel, para superaquecimento; e Seagate, para ruídos de disco. A oitava é a política de segurança do meu relatório de proposta, que gera os alertas, como 'não abra a fonte'.
Cada fonte tem link, data de acesso, a síntese usada e o limite conhecido. E cada regra aponta para a fonte que a sustenta. Por exemplo, a R08, disco com ruído, vem da Seagate, que orienta verificar o backup imediatamente."

## Bloco 3 (1:30–2:30) — Estrutura do código, base e inferência

*Na tela: árvore de pastas e depois src/base_conhecimento.py e src/inferencia.py.*

"O código está separado em três partes. Em base_conhecimento.py ficam só os dados: os fatos de entrada, as 13 regras, as fontes, as saídas e a política de prioridade. Em inferencia.py fica só o motor. E executar.py recebe o caso, chama o motor e mostra a explicação. Se eu mudar uma regra, não preciso mexer no motor.
Escolhi encadeamento à frente, porque o usuário começa descrevendo sintomas, ou seja, fatos, e o sistema precisa descobrir o que esses fatos permitem concluir. O motor trabalha em rodadas: testa as regras, aplica as que têm todas as condições confirmadas, adiciona os fatos derivados sem duplicar e para quando uma rodada não aplica nada novo.
As respostas têm três valores: sim, não e não sei. 'Não sei' nunca é tratado como 'não'."

## Bloco 4 (2:30–3:45) — Caso favorável e trilha explicada

*Na tela: terminal executando `python src/executar.py --exemplos` (primeiro caso, C05).*

"Primeiro, um caso favorável, o C05: o computador está lento, a memória fica perto de 100% e o disco está quase cheio.
Na seção 1 aparecem os fatos iniciais. Na seção 2, as regras testadas na rodada 1: a R04 não se aplica porque a inicialização não é lenta, e as regras R07 e R12 são aplicadas. Na rodada 2, nada novo é aplicado, então o encadeamento termina.
A conclusão é AJUSTE_DE_SOFTWARE: o próprio usuário pode resolver. Para cada regra aparece o porquê, o que fazer e a fonte, por exemplo, liberar espaço com a Limpeza de Disco, segundo a Microsoft."

## Bloco 5 (3:45–4:45) — Caso negativo e caso de fronteira

*Na tela: mesma execução, casos C06 e C12.*

"Agora um caso negativo com regra encadeada, o C06: o computador desliga sozinho durante jogos e esquenta muito. Na rodada 1, a R05 conclui o fato derivado 'suspeita_termica'. A R11 fica aguardando esse fato e é aplicada na rodada 2. A conclusão é ASSISTENCIA_TECNICA, sustentada por R05 e R11.
E o caso de fronteira, o C12: é a mesma situação, mas o usuário responde 'não sei' sobre o aquecimento. O sistema não chuta: R11 e R13 ficam em aberto, e a conclusão é DADOS_INSUFICIENTES, com o motivo explicando exatamente o que falta saber."

## Bloco 6 (4:45–5:45) — Testes e matriz de cobertura

*Na tela: terminal executando `python tests/test_sistema.py` e depois docs/matriz_regra-caso-fonte.md.*

"Os testes usam só Python e assert. Rodando python tests/test_sistema.py, os 19 testes passam.
Na matriz de cobertura, cada uma das 13 regras aponta para a fonte, para o caso fictício e para o teste que a aciona. Há também testes para 'não sei', para respostas contraditórias, para o término do motor e para a política de prioridade: no caso C15, o disco com ruído suspende os ajustes de software, porque proteger os dados vem primeiro. Um teste ainda confere automaticamente que nenhuma regra ficou sem caso."

## Bloco 7 (5:45–6:30) — Limitações e uso de IA

*Na tela: README.md, seções 10 e 11.*

"As limitações: o sistema depende do que o usuário consegue observar, não mede temperatura nem testa peças, cobre só alguns problemas comuns do Windows e as fontes são de fabricantes específicos.
Sobre o uso de IA: usei ferramentas de IA como apoio, para lapidar o texto da minha proposta e no desenvolvimento, e está tudo registrado em docs/declaracao_uso_ia.md. O tema, as regras e a validação são meus: rodei os testes e os casos no meu computador e conferi as fontes."

## Extra (6:30–7:00, opcional) — Interface web

*Na tela: `python src/interface_web.py` e o DiagnoPC no navegador.*

"Por fim, como extra, o DiagnoPC também tem uma interface web, que usa exatamente o mesmo motor. Ela mostra o encaminhamento principal, as regras com as fontes e a trilha completa do motor. Obrigado!"
