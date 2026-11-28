# Matriz regra – caso – fonte — DiagnoPC

Casos em `src/casos.py` (todos fictícios). Testes em `tests/test_sistema.py`.
Comando: `python tests/test_sistema.py` → **19 de 19 testes passaram**.

## 1. Cobertura de cada regra ativa

| Regra | Fonte | Condição → conclusão (resumo) | Caso | Teste | Resultado esperado |
|---|---|---|---|---|---|
| R01 | F1 | sem energia + tomada/cabo **não** verificados → verificação básica | C01 | `test_C01_R01_sem_energia_tomada_nao_verificada` | aplica só R01; saída `VERIFICACAO_BASICA` |
| R02 | F1 | sem energia + tomada/cabo **verificados** → assistência | C02 | `test_C02_R02_sem_energia_com_tomada_ok` | aplica só R02; saída `ASSISTENCIA_TECNICA` |
| R03 | F2 | liga com ventoinhas + sem imagem → verificação básica | C03 | `test_C03_R03_liga_sem_imagem` | aplica só R03; saída `VERIFICACAO_BASICA` |
| R04 | F3 | inicialização lenta → ajuste de software | C04 | `test_C04_R04_inicializacao_lenta` | aplica só R04; saída `AJUSTE_DE_SOFTWARE` |
| R05 | F5 | desliga sozinho + sob carga → fato `suspeita_termica` | C06, C07, C12 | `test_C06_R05_R11_regra_encadeada_com_fato_derivado` | `suspeita_termica` derivado na rodada 1 |
| R06 | F5 | aquecimento/ruído + **não** desliga → melhorar ventilação | C08 | `test_C08_R06_aquece_mas_nao_desliga` | aplica só R06; saída `MELHORAR_VENTILACAO` |
| R07 | F3 | lentidão + memória no limite → ajuste de software | C05 | `test_C05_R07_R12_caso_favoravel_duas_regras` | aplica R07 e R12; saída `AJUSTE_DE_SOFTWARE` |
| R08 | F6 | disco com alertas/ruídos → backup e interromper | C09, C15 | `test_C09_R08_disco_com_ruido` | aplica só R08; saída `BACKUP_E_INTERROMPER` |
| R09 | F7 | internet no cabo + falha no Wi-Fi → ajuste de software | C10 | `test_C10_R09_falha_so_no_wifi` | aplica só R09; saída `AJUSTE_DE_SOFTWARE` |
| R10 | F7 | falha em vários dispositivos → verificar rede externa | C11 | `test_C11_R10_sem_internet_em_varios_aparelhos` | aplica só R10; saída `VERIFICAR_REDE_EXTERNA` |
| R11 | F5 | `suspeita_termica` + aquecimento/ruído → assistência | C06 | `test_C06_R05_R11_regra_encadeada_com_fato_derivado` | R05 na rodada 1, R11 na rodada 2; saída `ASSISTENCIA_TECNICA` |
| R12 | F4 | lentidão + disco quase cheio → ajuste de software | C05, C15 | `test_C05_R07_R12_caso_favoravel_duas_regras` | aplica R07 e R12; saída `AJUSTE_DE_SOFTWARE` |
| R13 | F5 (+F1) | `suspeita_termica` + **sem** aquecimento → assistência | C07 | `test_C07_R05_R13_desliga_sem_calor` | aplica R05 e R13; saída `ASSISTENCIA_TECNICA` |

Todas as 13 regras são acionadas por pelo menos um caso. Isso também é verificado automaticamente por
`test_base_integra_ids_fontes_e_cobertura`, que falha se alguma regra ficar sem caso.

## 2. Casos de fronteira, negativos e de comportamento do motor

| Caso | Tipo | Situação | Teste | Resultado esperado |
|---|---|---|---|---|
| C12 | fronteira | desliga sob carga, **não sei** se esquenta | `test_C12_fronteira_nao_sei_nao_vira_nao` | `DADOS_INSUFICIENTES`; R11 e R13 em aberto; R13 **não** dispara ("não sei" ≠ "não") |
| C13 | negativo | inicia normal e não fica lento | `test_C13_negativo_nenhuma_regra_corresponde` | nenhuma regra; `DADOS_INSUFICIENTES` com encaminhamento para análise humana |
| C14 | fronteira | sem energia, **não sei** se a tomada foi verificada | `test_C14_fronteira_tomada_desconhecida` | R01 e R02 em aberto; `DADOS_INSUFICIENTES` |
| C15 | prioridade | disco com ruído **e** lento com disco cheio | `test_C15_politica_de_prioridade_backup_suspende_ajuste` | principal `BACKUP_E_INTERROMPER`; `AJUSTE_DE_SOFTWARE` suspensa |
| C16 | fronteira | "sem energia" **e** "liga com ventoinhas" | `test_C16_contradicao_nao_vira_fato_confirmado` | aviso de contradição; R02 e R03 não disparam |
| C06 | motor | encadeamento com fato derivado | `test_motor_termina_e_nao_duplica_fatos` | rodadas ≤ regras + 1; sem fato duplicado; última rodada sem regra nova |
| — | interativo | perguntas desnecessárias são puladas | `test_modo_interativo_pula_pergunta_desnecessaria` | com energia, não pergunta da tomada; após R05, pergunta do calor |
| — | base | integridade da base | `test_base_integra_ids_fontes_e_cobertura` | IDs únicos, ≥ 12 regras, fontes válidas, ≥ 4 saídas, ≥ 3 favoráveis, todas as regras cobertas |

## 3. Três execuções explicadas (item 3.3 da orientação)

Geradas por `python src/executar.py --exemplos`:

| Execução | Caso | Conclusão | Regras que sustentam |
|---|---|---|---|
| Favorável | C05 | `AJUSTE_DE_SOFTWARE` | R07, R12 |
| Negativa | C06 | `ASSISTENCIA_TECNICA` (com fato derivado) | R05 → R11 |
| Fronteira | C12 | `DADOS_INSUFICIENTES` (R11/R13 em aberto) | nenhuma (motivo explicado) |
