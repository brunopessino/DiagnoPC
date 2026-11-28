# Declaração de uso de Inteligência Artificial — DiagnoPC

O tema, o escopo, as decisões de projeto, a revisão e a validação do DiagnoPC são do autor.
Ferramentas de IA foram usadas como **apoio**, conforme registrado abaixo. O autor responde integralmente
por cada regra, linha de código, teste e afirmação deste trabalho.

## Ferramenta 1 — apoio no desenvolvimento do protótipo

| Campo | Registro |
|---|---|
| **Nome da ferramenta** | Claude (Anthropic) |
| **Finalidade** | Auxílio na programação em Python, na escrita dos testes e da documentação, na adequação do projeto às orientações da A4 e na pesquisa de fontes oficiais. |
| **Arquivos ou trechos afetados** | `src/`, `tests/test_sistema.py`, `README.md` e os arquivos de `docs/`. |
| **O que o autor revisou ou alterou** | O autor definiu o tema, o escopo e as regras a partir do seu relatório de proposta; decidiu pela interface web e pelo nome DiagnoPC; revisou as regras, os casos de teste e as explicações geradas pelo sistema; publicou o projeto no GitHub. |
| **Como o resultado foi validado** | O autor executou no próprio computador (Windows, Python 3.13.5) `python tests/test_sistema.py` (19 de 19 testes aprovados) e `python src/executar.py --exemplos`, comparando a saída com `docs/tabela_de_decisao.md`; usou o modo interativo e a interface web; conferiu os links das sete fontes on-line em 28/11/2026. |

## Ferramenta 2 — revisão do texto do relatório de proposta

| Campo | Registro |
|---|---|
| **Nome da ferramenta** | ChatGPT (OpenAI) e Claude (Anthropic) |
| **Finalidade** | Revisão e lapidação do texto do relatório de proposta, escrito pelo autor. |
| **Arquivos ou trechos afetados** | Relatório de proposta (fora do ZIP), citado como fonte F8. |
| **O que o autor revisou ou alterou** | O autor escreveu a proposta, usou a IA para melhorar a redação, revisou a versão final e a entregou ao professor. |
| **Como o resultado foi validado** | As regras da proposta foram conferidas com fontes oficiais (F1 a F7) durante o desenvolvimento. |

Nenhum dado pessoal, senha, chave de acesso ou dado real de terceiros foi usado. Todos os casos de teste são fictícios.
