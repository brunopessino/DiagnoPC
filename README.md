# DiagnoPC · Sistema Especialista de Diagnóstico e Manutenção de Computadores

Protótipo acadêmico. Disciplina **Programação de Sistemas Especialistas** (UVA), Prof. Paulo Marcos.
Aluno: Bruno Pessino.

Sistema baseado em regras de produção (SE–ENTÃO) com **encadeamento para frente**.
Ele faz uma triagem de problemas comuns de computador a partir de respostas
**sim / não / não sei** e mostra hipóteses, explicações, recomendações e alertas de segurança.

> É uma ferramenta de triagem: as hipóteses são "possíveis causas", não defeitos confirmados.

---

## Estrutura do projeto

| Arquivo | O que faz | Seção do relatório |
|---|---|---|
| `base_conhecimento.py` | Categorias, perguntas, regras R01–R10, contradições e avisos | 8 e Apêndice A |
| `motor_inferencia.py` | Memória de trabalho, motor de inferência (forward chaining) e explicação | 5.2, 9, 9.1, 9.2 |
| `main.py` | Interface no terminal: menu, perguntas, resultado e resumo em arquivo | 7, 10 |
| `servidor_web.py` | Servidor da interface web: usa o MESMO motor do terminal | 7.2 |
| `web/` | Tela do DiagnoPC (HTML, CSS e JavaScript) | 7.2 |
| `Abrir DiagnoPC.bat` | Atalho para abrir a versão web com clique duplo (Windows) | — |
| `testes/test_cenarios.py` | Testes automatizados T01–T07 (+ T08 e um teste extra) | 12 |
| `evidencias/` | Saída real do programa em cada cenário de teste | 12 |

---

## Como rodar (passo a passo)

**1. Instale o Python 3** (versão 3.8 ou mais nova).
Não precisa instalar nenhuma biblioteca extra.

**2. Abra o terminal dentro da pasta do projeto.**
No Windows: abra a pasta no Explorador, clique na barra de endereço, digite `cmd` e aperte Enter.

**3. Rode o sistema:**
```
python main.py
```
(em Linux/Mac pode ser `python3 main.py`)

**4. Use o sistema:**
- Escolha a categoria do problema digitando o número (1 a 6).
- Responda cada pergunta com `s` (sim), `n` (não) ou `?` (não sei).
- No final, o sistema mostra as hipóteses e pergunta se você quer salvar o resumo.
  O resumo vai para a pasta `relatorios/`.

**4b. Versão com tela (web):**
```
python servidor_web.py
```
O navegador abre sozinho em `http://localhost:8000`. No Windows, também dá para dar
**clique duplo** em `Abrir DiagnoPC.bat`. Para desligar, volte à janela preta e aperte `Ctrl + C`.

A tela não toma nenhuma decisão de diagnóstico: ela só envia as respostas ao motor em Python
e mostra o que ele devolve. Assim, o motor de inferência continua separado da camada visual.

**5. Rode os testes automatizados:**
```
python -m unittest discover -s testes -v
```
Todos devem aparecer como `ok`.

---

## Como funciona o motor de inferência

1. Cada resposta vira um **fato** na memória de trabalho: `True` (sim), `False` (não) ou `None` (não sei).
2. O sistema só faz perguntas que ainda podem levar a alguma regra. Se uma resposta já descarta
   a regra, as perguntas seguintes dela são puladas.
3. No final, o motor percorre as regras em ciclo: toda regra com **todas** as condições confirmadas
   é disparada, e a conclusão entra na memória como novo fato. O ciclo para quando nenhuma regra nova dispara.
4. As hipóteses são ordenadas por prioridade (alta > média > baixa) e depois pelo número de condições confirmadas.
5. Regras com alguma resposta "não sei" ficam **em aberto**: não viram conclusão, e o sistema diz o que faltou saber.
6. Respostas contraditórias geram um aviso e **não** são usadas como fatos confirmados.

---

## Mapa dos requisitos

| Requisito | Onde foi atendido |
|---|---|
| RF01 Selecionar categoria | `main.py` → `escolher_categoria()` |
| RF02 Perguntas compatíveis com respostas anteriores | `motor_inferencia.py` → `proxima_pergunta()` |
| RF03 Registrar respostas como fatos | `MemoriaTrabalho.registrar()` |
| RF04 Comparar fatos com regras | `MotorInferencia.inferir()` |
| RF05 Apresentar hipóteses | `main.py` → `montar_resultado()` |
| RF06 Recomendações e cuidados de segurança | campos `recomendacao` e `alerta` de cada regra |
| RF07 Explicar a conclusão | `explicar()` |
| RF08 Avisar quando os dados são insuficientes | mensagem "Não foi possível concluir" + hipóteses em aberto |
| RF09 Resumo da consulta | `salvar_relatorio()` |
| RF10 Manutenção da base | versão futura (hoje: editar `base_conhecimento.py`) |
| RNF03 Segurança | nenhuma regra manda abrir a fonte ou fazer medição elétrica |
| RNF05 Confiabilidade | "não sei" ≠ "não"; contradições não viram fatos |
| RNF07 Privacidade | não pede nem guarda nenhum dado pessoal |

---

## Resultado dos testes

| Teste | Cenário | Resultado |
|---|---|---|
| T01 | Sem energia, tomada não verificada | R01: verificações externas ✔ |
| T02 | Tomada ok, continua sem ligar | R02: avaliação técnica, sem abrir a fonte ✔ |
| T03 | Liga, mas sem imagem | R03: monitor, cabo, entrada, vídeo ✔ |
| T04 | Desliga em jogo com aquecimento | R05 (alta) + avaliação técnica ✔ |
| T05 | "Não sei" sobre temperatura | R06 fica em aberto, não é descartada ✔ |
| T06 | Sintomas sem regra | "Não foi possível concluir" ✔ |
| T07 | Duas regras aplicáveis | R05 e R06, cada uma com explicação ✔ |
| T08 (extra) | Respostas contraditórias | Aviso e nenhuma conclusão falsa ✔ |
