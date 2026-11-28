# Escopo e fontes — DiagnoPC

## 1. Decisão apoiada (em uma frase)

> **Qual é o primeiro encaminhamento seguro para um problema comum de computador relatado pelo usuário?**

O DiagnoPC faz uma **triagem**: a partir de sintomas observáveis, indica se o próprio usuário pode fazer uma ação simples e segura ou se o caso deve ir para backup imediato ou assistência técnica.

## 2. Escopo

| Item | Descrição |
|---|---|
| **Usuário primário** | Pessoa sem formação técnica (estudante, usuário doméstico ou de escritório) que usa um computador de mesa ou notebook com Windows 10/11. |
| **Situação** | O computador apresenta um problema comum (não liga, sem imagem, lentidão, desligamentos, aquecimento, disco com ruído, falta de internet) e o usuário quer saber o que fazer primeiro, antes de chamar alguém ou mexer no equipamento. |
| **Entradas (fatos observáveis)** | 15 perguntas de resposta **sim / não / não sei**, por exemplo: "o computador não apresenta nenhum sinal de energia?", "a tomada e o cabo já foram verificados?", "desliga durante jogos?", "esquenta muito?". Lista completa em `tabela_de_decisao.md`. |
| **Saídas possíveis** | `VERIFICACAO_BASICA`, `AJUSTE_DE_SOFTWARE`, `MELHORAR_VENTILACAO`, `VERIFICAR_REDE_EXTERNA` (favoráveis: o usuário pode agir), `ASSISTENCIA_TECNICA`, `BACKUP_E_INTERROMPER` (encaminhamentos de proteção/humano) e `DADOS_INSUFICIENTES` (produzida pelo motor quando não é possível concluir). |
| **Limite (o que o sistema NÃO decide)** | Não confirma defeito de peça, não manda abrir o computador ou a fonte, não orienta medições elétricas, não recupera dados, não instala nada automaticamente, não trata Mac/Linux, impressoras, celulares nem vírus/malware. |
| **Encaminhamento para análise humana** | (a) Sintomas que nenhuma regra cobre; (b) falha de energia com tomada e cabo já confirmados (R02); (c) desligamentos sob carga (R11, R13); (d) disco com sinais de falha, após o backup (R08); (e) informação insuficiente que o usuário não consegue confirmar. |

Todos os casos usados no projeto são **fictícios** (`src/casos.py`). O sistema não coleta nenhum dado pessoal.

## 3. Fontes

Data de acesso de todas as fontes on-line: **26/11/2026**.

### F1 — Dell: problemas de energia
- **Título:** Computer Won't Turn On: Troubleshoot Power Issues
- **Autor/órgão:** Dell Technologies — Dell Support Knowledge Base
- **Versão/data:** página on-line consultada em 26/11/2026
- **Link:** https://www.dell.com/support/contents/us-en/article/product-support/self-support-knowledgebase/fix-common-issues/no-power
- **Síntese usada:** "No power" é quando não há luzes, ventoinhas nem sons. Antes de suspeitar de peça interna, verificar a tomada (testando outro aparelho) e o cabo/adaptador. Se mesmo assim não ligar, a fonte pode estar com defeito e o caso deve ir ao suporte técnico. Desligamentos inesperados também aparecem como sintoma de problema de alimentação ("intermittent power").
- **Sustenta:** R01, R02 e parte de R13.
- **Limite conhecido:** escrito para equipamentos Dell; os passos externos são genéricos, mas testes internos da fonte (autoteste do PSU) são específicos de alguns modelos e ficaram fora da base.

### F2 — Dell: computador liga, mas sem imagem
- **Título:** Computer Turns On But No Display: Troubleshoot Display Problems
- **Autor/órgão:** Dell Technologies — Dell Support
- **Versão/data:** página on-line consultada em 26/11/2026
- **Link:** https://www.dell.com/support/monitors
- **Síntese usada:** quando o computador liga mas não há imagem, verificar primeiro se o monitor está ligado, se o cabo de vídeo está firme e se a entrada correta (HDMI, DisplayPort etc.) está selecionada.
- **Sustenta:** R03.
- **Limite conhecido:** passos seguintes (diagnóstico de placa de vídeo/memória) exigem técnico e não viraram regra.

### F3 — Microsoft: desempenho do PC
- **Título:** Tips to improve PC performance in Windows
- **Autor/órgão:** Microsoft Support
- **Versão/data:** aplica-se a Windows 10 e 11; página consultada em 26/11/2026
- **Link:** https://support.microsoft.com/help/4002019
- **Síntese usada:** lentidão pode vir de muitos aplicativos de inicialização, de pouca memória para os programas abertos e de pouco espaço em disco. Recomenda desativar aplicativos de inicialização no Gerenciador de Tarefas, fechar aplicativos/abas sem uso e reiniciar; em hardware antigo, o upgrade pode ser a solução.
- **Sustenta:** R04, R07.
- **Limite conhecido:** não define um valor exato de "memória alta"; o sistema usa a observação do usuário ("perto de 100%").

### F4 — Microsoft: liberar espaço em disco
- **Título:** Free up drive space in Windows (e artigo relacionado "Manage drive space with Storage Sense")
- **Autor/órgão:** Microsoft Support
- **Versão/data:** página consultada em 26/11/2026
- **Link:** https://support.microsoft.com/help/12425
- **Síntese usada:** com pouco espaço, o PC pode ficar mais lento; a barra de armazenamento fica vermelha em estado de pouco espaço. Recomenda Lixeira, Limpeza de Disco e Sensor de Armazenamento.
- **Sustenta:** R12.
- **Limite conhecido:** o limite de "pouco espaço" varia com o tamanho do disco; o sistema usa o indicador visual do Windows.

### F5 — Intel: superaquecimento
- **Título:** Overheating Symptoms and Troubleshooting for Intel® Boxed Processors (Artigo 000005791); complementar: Processor Turns On for a Few Minutes Then Turns Off (Artigo 000037333)
- **Autor/órgão:** Intel Corporation — Intel Support
- **Versão/data:** artigo 000005791 com última revisão em 17/12/2025; consultado em 26/11/2026
- **Link:** https://www.intel.com/content/www/us/en/support/articles/000005791.html e https://www.intel.com/content/www/us/en/support/articles/000037333.html
- **Síntese usada:** sintomas de superaquecimento incluem o sistema desligar sozinho, lentidão e ruído excessivo das ventoinhas; o processador tem proteção térmica que desliga o sistema. Recomenda verificar ventoinhas e poeira e, em computadores de fabricante (Dell, HP, Lenovo...), procurar o fabricante. O artigo 000037333 lembra que o desligamento também pode ter **outras causas**.
- **Sustenta:** R05, R06, R11, R13.
- **Limite conhecido:** voltado a processadores Intel; o sintoma é genérico, mas o sistema não mede temperatura real.

### F6 — Seagate: ruídos de disco rígido
- **Título:** Identifying Hard Drive Sounds and Determining What They Mean
- **Autor/órgão:** Seagate Technology — Seagate Support
- **Versão/data:** página consultada em 26/11/2026
- **Link:** https://www.seagate.com/support/kb/identifying-hard-drive-sounds-and-determining-what-they-mean/
- **Síntese usada:** sons anormais (raspados, cliques fortes) podem indicar problema; ao ouvi-los, verificar imediatamente se existe backup completo dos dados importantes; o uso contínuo pode causar mais danos.
- **Sustenta:** R08 e a política de prioridade (backup antes de qualquer outra ação).
- **Limite conhecido:** trata de HDs mecânicos; SSDs não fazem ruído, por isso a regra também aceita "alertas ou erros" informados pelo sistema.

### F7 — Microsoft: problemas de Wi-Fi
- **Título:** Fix Wi-Fi connection issues in Windows
- **Autor/órgão:** Microsoft Support
- **Versão/data:** aplica-se a Windows 10 e 11; página consultada em 26/11/2026
- **Link:** https://support.microsoft.com/help/10741
- **Síntese usada:** verificar se o Wi-Fi está ligado e o modo avião desligado; reinstalar o driver do adaptador de rede; reiniciar modem e roteador; testar outro aparelho na mesma rede — se ele conecta, o problema provavelmente está no seu dispositivo (e, se nenhum conecta, está na rede).
- **Sustenta:** R09, R10.
- **Limite conhecido:** não cobre redes corporativas, VPN ou configurações avançadas.

### F8 — Política de segurança do projeto (documento do autor)
- **Título:** Relatório de proposta do Sistema Especialista de Diagnóstico e Manutenção de Computadores, seção 13 (Segurança, ética e limitações)
- **Autor/órgão:** autor do projeto (documento de proposta entregue à disciplina)
- **Versão/data:** novembro de 2026
- **Local de acesso:** documento de proposta entregue ao professor
- **Síntese usada:** o sistema prioriza verificações externas e não orienta abrir a fonte, tocar em circuitos energizados ou fazer medições elétricas; recomenda backup quando há risco para os dados; usa linguagem de "possível causa".
- **Sustenta:** os **alertas de segurança** exibidos junto às regras (não cria regra sozinha).
- **Limite conhecido:** é uma política interna, não uma norma técnica.

## 4. Pendências (fora da base de regras)

Critérios citados nas fontes que **não** viraram regra, por falta de dado observável seguro para o usuário leigo:
- autoteste interno da fonte e reset do RTC (F1) — exige abrir o equipamento;
- diagnóstico de memória RAM e placa de vídeo quando não há imagem (F2) — exige técnico;
- pasta térmica, overclock e BIOS (F5) — exige técnico;
- verificação de malware (F3) — fora do escopo declarado.
