# DiagnoPC — Sistema especialista de triagem de computadores

## 1. Título e decisão apoiada

**DiagnoPC** é um protótipo de sistema especialista em Python, baseado em regras de produção (SE–ENTÃO).

> **Decisão apoiada:** qual é o **primeiro encaminhamento seguro** para um problema comum de computador relatado pelo usuário?

O sistema recebe sintomas observáveis (sim / não / não sei), aplica as regras e devolve um encaminhamento, com explicação, recomendação, alerta de segurança e fonte.

## 2. Escopo e limites

- **Usuário:** pessoa sem formação técnica, com computador de mesa ou notebook com Windows 10/11.
- **Situações cobertas:** não liga, liga sem imagem, lentidão, desligamentos e aquecimento, disco com alertas/ruídos, falta de internet/Wi-Fi.
- **Saídas:** `VERIFICACAO_BASICA`, `AJUSTE_DE_SOFTWARE`, `MELHORAR_VENTILACAO`, `VERIFICAR_REDE_EXTERNA` (o usuário pode agir), `ASSISTENCIA_TECNICA`, `BACKUP_E_INTERROMPER` e `DADOS_INSUFICIENTES`.
- **O sistema NÃO decide:** não confirma defeito de peça, não manda abrir o computador ou a fonte, não orienta medição elétrica, não recupera dados, não trata vírus, Mac/Linux, impressoras ou celulares.
- **Encaminha para análise humana:** sintomas que nenhuma regra cobre, falhas de energia e desligamentos que exigem técnico, disco com sinais de falha (após o backup) e informações que o usuário não consegue confirmar.

Detalhes em [`docs/escopo_e_fontes.md`](docs/escopo_e_fontes.md).

## 3. Estrutura das pastas

```text
A4_BrunoPessino/
├── README.md
├── Abrir DiagnoPC (web).bat     # extra: abre a interface web com dois cliques (Windows)
├── src/
│   ├── base_conhecimento.py     # fatos, 13 regras, fontes, saídas e prioridades (só dados)
│   ├── inferencia.py            # motor de encadeamento à frente (só mecanismo)
│   ├── executar.py              # recebe um caso, chama o motor e exibe a explicação
│   ├── casos.py                 # 16 casos fictícios usados nos testes e exemplos
│   ├── interface_web.py         # extra opcional: interface web (mesmo motor)
│   └── web/                     # extra opcional: HTML, CSS e JavaScript da interface
├── tests/
│   └── test_sistema.py          # 19 testes com assert + executor próprio
└── docs/
    ├── escopo_e_fontes.md
    ├── tabela_de_decisao.md
    ├── matriz_regra-caso-fonte.md
    ├── declaracao_uso_ia.md
    └── transcricao_video.md
```

## 4. Requisitos e instalação

- **Python 3.8 ou mais novo** (testado no 3.13).
- **Nenhuma biblioteca externa**: só a biblioteca padrão. Não é preciso `pip install` nem `requirements.txt`.
- Instalação: basta extrair o ZIP e abrir um terminal **dentro da pasta `A4_BrunoPessino`**.

Para conferir o Python:

```bash
python --version
```

(Em Linux/Mac, use `python3` no lugar de `python` em todos os comandos.)

## 5. Comandos para executar o sistema

```bash
# Modo interativo: escolha a categoria e responda s / n / ?
python src/executar.py

# As três execuções explicadas: favorável (C05), negativa (C06) e fronteira (C12)
python src/executar.py --exemplos

# Executar um caso fictício específico / listar os casos
python src/executar.py --caso C15
python src/executar.py --listar

# Extra opcional: interface web (abre o navegador em http://localhost:8000; Ctrl + C para sair)
python src/interface_web.py
```

## 6. Comando para executar os testes

```bash
python tests/test_sistema.py
```

Resultado esperado: `19 de 19 testes passaram.` (o comando termina com código 0; se algum teste falhar, mostra qual e termina com código 1).

## 7. Estratégia de inferência e justificativa

**Encadeamento à frente (forward chaining).**

- **Por quê:** numa triagem, o usuário começa relatando **sintomas** (fatos) e não sabe qual é o problema. Por isso, o caminho natural é partir dos fatos para as conclusões. Encadeamento para trás exigiria escolher antes uma conclusão-alvo, o que o usuário leigo não consegue fazer.
- **Como funciona:** em cada **rodada**, o motor testa todas as regras ainda não aplicadas com os fatos conhecidos no início da rodada. Aplica as que têm **todas** as condições confirmadas e adiciona os fatos derivados **sem duplicar**. O processo para quando uma rodada não aplica nenhuma regra nova. Como cada regra só é aplicada uma vez, há no máximo *(nº de regras + 1)* rodadas, então o processo sempre termina.
- **Três valores:** sim, não e **não sei**. "Não sei" ou fato não informado **nunca** vira "não": a regra fica **em aberto** e o motor responde `DADOS_INSUFICIENTES`, dizendo o que falta.
- **Regra encadeada:** R05 conclui o fato derivado `suspeita_termica`, que é usado por R11 e R13 na rodada seguinte.
- **Prioridade:** quando há várias saídas, o motor escolhe o encaminhamento principal pela política de prioridade (`docs/tabela_de_decisao.md`, seção 5). Disco com sinais de falha (`BACKUP_E_INTERROMPER`) **suspende** as ações do usuário que gravam no disco.
- **Contradições:** respostas incompatíveis passam a valer "não sei" e geram um aviso.

## 8. Exemplos de casos e explicações

Cada explicação mostra: (1) fatos iniciais, (2) regras testadas e aplicadas por rodada, (3) fatos derivados, (4) conclusão ou motivo para não concluir e (5) regras que sustentam a saída.

**Caso favorável — C05** (lento, memória perto de 100%, disco quase cheio):

```text
Rodada 1: [NÃO APLICÁVEL] R04: inicializacao_lenta = não (exige sim)
          [APLICADA] R07   [APLICADA] R12
Rodada 2: nenhuma regra nova -> fim
Conclusão: AJUSTE_DE_SOFTWARE (R07, R12) - o próprio usuário pode resolver
```

**Caso negativo com regra encadeada — C06** (desliga em jogos e esquenta):

```text
Rodada 1: [APLICADA] R05 -> fato derivado suspeita_termica
          [AGUARDA]  R11: aguarda suspeita_termica, que R05 vai concluir
Rodada 2: [APLICADA] R11
Conclusão: ASSISTENCIA_TECNICA - regras que sustentam: R05, R11
```

**Caso de fronteira — C12** (desliga em jogos, "não sei" se esquenta):

```text
Rodada 2: [EM ABERTO] R11: aquecimento_ou_ruido = não sei
          [EM ABERTO] R13: aquecimento_ou_ruido = não sei
Conclusão: DADOS_INSUFICIENTES - faltam informações para concluir (R11, R13)
```

A saída completa é gerada por `python src/executar.py --exemplos`.

## 9. Vínculo entre fontes, regras e testes

| Fonte | Regras | Casos / testes |
|---|---|---|
| F1 Dell (energia) | R01, R02 (e R13) | C01, C02, C07 |
| F2 Dell (sem imagem) | R03 | C03 |
| F3 Microsoft (desempenho) | R04, R07 | C04, C05 |
| F4 Microsoft (espaço em disco) | R12 | C05, C15 |
| F5 Intel (superaquecimento) | R05, R06, R11, R13 | C06, C07, C08, C12 |
| F6 Seagate (ruídos de disco) | R08 + política de prioridade | C09, C15 |
| F7 Microsoft (Wi-Fi) | R09, R10 | C10, C11 |
| F8 Política de segurança do projeto | alertas de segurança | todos |

A matriz completa (regra → fonte → caso → teste → resultado esperado) está em [`docs/matriz_regra-caso-fonte.md`](docs/matriz_regra-caso-fonte.md).
Todas as 13 regras são acionadas por pelo menos um teste, e o teste `test_base_integra_ids_fontes_e_cobertura` confere isso automaticamente.

## 10. Limitações conhecidas

- Depende do que o usuário **consegue observar e responder**; respostas erradas levam a encaminhamentos errados.
- Não mede temperatura, tensão ou saúde do disco: as hipóteses são **possíveis causas**, não defeitos confirmados.
- Cobre um conjunto pequeno de problemas comuns em Windows 10/11.
- As fontes são de fabricantes específicos (Dell, Microsoft, Intel, Seagate); os passos usados são genéricos, mas podem não valer para todo modelo.
- Algumas combinações de sintomas não têm regra (ex.: desliga sozinho fora de tarefas pesadas): nesses casos, o sistema encaminha para análise humana em vez de inventar uma conclusão.
- O modo interativo pergunta por categoria; sintomas de categorias diferentes precisam ser investigados um de cada vez.

## 11. Declaração resumida de uso de IA

O projeto foi desenvolvido pelo autor com **apoio** de ferramentas de IA (Claude, da Anthropic, no desenvolvimento; e ChatGPT e Claude na revisão do texto do relatório de proposta). O tema, as regras, a revisão e a validação são do autor, que responde integralmente pelo conteúdo. Detalhes em [`docs/declaracao_uso_ia.md`](docs/declaracao_uso_ia.md).
