# Tabela de decisão — DiagnoPC

Converte o conhecimento das fontes (`escopo_e_fontes.md`) em fatos, condições, regras e conclusões.
A implementação está em `src/base_conhecimento.py`.

## 1. Fatos de entrada (perguntados ao usuário)

Valores: **sim** (True), **não** (False), **não sei** (None). Um fato não perguntado fica **ausente**.
"Não sei" e "ausente" **nunca** são tratados como "não".

| Fato | Pergunta (resumo) | Categoria |
|---|---|---|
| `sem_energia` | Nenhum sinal de energia (luz, ventoinha, som)? | 1 Alimentação |
| `tomada_cabo_verificados` | Tomada testada e cabo conectado? | 1 Alimentação |
| `liga_com_ventoinhas` | Liga e as ventoinhas funcionam? | 2 Vídeo |
| `sem_imagem` | Ligado, mas a tela fica sem imagem? | 2 Vídeo |
| `inicializacao_lenta` | O Windows demora muito para iniciar? | 3 Desempenho |
| `lentidao_geral` | Fica lento durante o uso? | 3 Desempenho |
| `memoria_no_limite` | Memória perto de 100% no Gerenciador de Tarefas? | 3 Desempenho |
| `disco_quase_cheio` | Disco C: quase cheio (barra vermelha)? | 3 Desempenho |
| `desliga_sozinho` | Desliga sozinho? | 4 Temperatura |
| `ocorre_durante_carga` | Acontece em jogos/tarefas pesadas? | 4 Temperatura |
| `aquecimento_ou_ruido` | Esquenta muito ou ventoinhas muito ruidosas? | 4 Temperatura |
| `disco_alertas_ruidos` | HD/SSD com alertas, erros ou ruídos estranhos? | 5 Armazenamento |
| `funciona_por_cabo` | A internet funciona por cabo? | 6 Rede |
| `falha_wifi` | A internet NÃO funciona pelo Wi-Fi? | 6 Rede |
| `falha_varios_dispositivos` | Também falha em outros aparelhos da rede? | 6 Rede |

## 2. Fato derivado (concluído por regra, nunca perguntado)

| Fato | Produzido por | Usado por |
|---|---|---|
| `suspeita_termica` | R05 | R11, R13 |

## 3. Saídas (conclusões finais)

| Saída | Significado | Favorável? | Prioridade |
|---|---|---|---|
| `BACKUP_E_INTERROMPER` | Proteger dados antes de tudo e procurar assistência | Não | 1 (maior) |
| `ASSISTENCIA_TECNICA` | Caso precisa de avaliação humana | Não | 2 |
| `VERIFICACAO_BASICA` | Usuário faz verificações externas seguras | **Sim** | 3 |
| `MELHORAR_VENTILACAO` | Usuário desobstrui as entradas de ar | **Sim** | 3 |
| `VERIFICAR_REDE_EXTERNA` | Reiniciar modem/roteador; depois provedor | **Sim** | 3 |
| `AJUSTE_DE_SOFTWARE` | Usuário ajusta configurações do Windows | **Sim** | 3 |
| `DADOS_INSUFICIENTES` | Motor não conseguiu concluir (não é regra) | — | — |

## 4. Regras

| ID | SE (condições) | ENTÃO | Fonte |
|---|---|---|---|
| R01 | `sem_energia` = sim **E** `tomada_cabo_verificados` = não | `VERIFICACAO_BASICA` | F1 |
| R02 | `sem_energia` = sim **E** `tomada_cabo_verificados` = sim | `ASSISTENCIA_TECNICA` | F1 |
| R03 | `liga_com_ventoinhas` = sim **E** `sem_imagem` = sim | `VERIFICACAO_BASICA` | F2 |
| R04 | `inicializacao_lenta` = sim | `AJUSTE_DE_SOFTWARE` | F3 |
| R05 | `desliga_sozinho` = sim **E** `ocorre_durante_carga` = sim | fato derivado `suspeita_termica` | F5 |
| R06 | `aquecimento_ou_ruido` = sim **E** `desliga_sozinho` = não | `MELHORAR_VENTILACAO` | F5 |
| R07 | `lentidao_geral` = sim **E** `memoria_no_limite` = sim | `AJUSTE_DE_SOFTWARE` | F3 |
| R08 | `disco_alertas_ruidos` = sim | `BACKUP_E_INTERROMPER` | F6 |
| R09 | `funciona_por_cabo` = sim **E** `falha_wifi` = sim | `AJUSTE_DE_SOFTWARE` | F7 |
| R10 | `falha_varios_dispositivos` = sim | `VERIFICAR_REDE_EXTERNA` | F7 |
| R11 | `suspeita_termica` = sim **E** `aquecimento_ou_ruido` = sim | `ASSISTENCIA_TECNICA` | F5 |
| R12 | `lentidao_geral` = sim **E** `disco_quase_cheio` = sim | `AJUSTE_DE_SOFTWARE` | F4 |
| R13 | `suspeita_termica` = sim **E** `aquecimento_ou_ruido` = não | `ASSISTENCIA_TECNICA` | F5 (+F1) |

**Resumo:** 13 regras ativas · 6 saídas finais distintas (+ `DADOS_INSUFICIENTES`) ·
8 regras com encaminhamento favorável (R01, R03, R04, R06, R07, R09, R10, R12) ·
1 cadeia de regras (R05 → R11 / R13).

## 5. Política de prioridade

O domínio tem um conflito real: um disco com sinais de falha (R08) **não deve** receber limpezas, desfragmentação
ou formatação, que são justamente ações recomendadas por R12 ou R04 para lentidão. Fonte: F6 (verificar o backup
imediatamente; uso contínuo pode causar dano).

1. Quando várias saídas aparecem juntas, o **encaminhamento principal** é o de menor número de prioridade (tabela da seção 3).
2. Se `BACKUP_E_INTERROMPER` estiver presente, todas as saídas **favoráveis** ficam **suspensas** até o backup ser feito.
3. As demais saídas continuam sendo mostradas, com a explicação, para o técnico ou para depois do backup.

Esse comportamento é testado no caso **C15** (`test_C15_politica_de_prioridade_backup_suspende_ajuste`).

## 6. Verificações feitas antes de programar

- **Cada saída é possível:** todas as 6 saídas são produzidas por pelo menos um caso de teste (ver matriz).
- **Sem redundância:** nenhuma regra tem as mesmas condições de outra. R04, R07, R09 e R12 levam à mesma saída, mas por motivos e recomendações diferentes.
- **Sem conflito oculto:** R06 exige `desliga_sozinho = não` e R11/R13 dependem de `suspeita_termica`, por isso nunca disparam juntas. R11 e R13 são mutuamente exclusivas (`aquecimento_ou_ruido` sim × não). O único conflito real está documentado na seção 5.
- **Caso incompleto ≠ negativo:** "não sei" deixa a regra **em aberto** (casos C12 e C14) e o motor responde `DADOS_INSUFICIENTES`, informando o que falta.
- **Contradição:** respostas incompatíveis (ex.: "sem energia" e "liga com ventoinhas") passam a valer "não sei" (caso C16).
