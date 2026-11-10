# Pré-banca de 10/11: o que mostrar e falar

Grupo 7 — Masmorra Genética, Inteligência Artificial II.

## O compromisso de hoje

O cronograma da disciplina prevê, em 10/11, das 19h às 22h, uma pré-banca para todos os grupos: **10 minutos** para problema, dataset, técnica, principal experimento e protótipo funcionando; depois **5 minutos** para perguntas, teste não preparado e feedback. O documento não especifica o horário individual do grupo.

Hoje é também o marco de congelamento técnico: dataset e tratamento, baseline, algoritmo, experimentos, análise de erros e protótipo funcional devem existir. Depois, o foco é correção, refinamento, comunicação e ensaio. A entrega final comum é **17/11/2026 até as 17h**; a apresentação final do Grupo 7 está prevista para **01/12/2026**. Confiram eventuais mudanças diretamente com o professor.

Fontes: documentos 01 (Guia Geral, p. 3), 02 (Cronograma, pp. 1 e 3–4) e 07 (Mapa de Sorteio, p. 1) do ZIP recebido em 10/11.

## Preparar antes da aula

1. Na raiz do repositório, instale as dependências se necessário (`python -m pip install -r requirements.txt`) e execute `python -m streamlit run app.py`, ou abra `executar_prototipo.bat` no Windows. Deixe o navegador aberto e teste o equipamento/projetor.
2. Ensaie a demonstração indicada abaixo com a estratégia do algoritmo, uma semente e uma mudança no Laboratório. Guarde capturas ou o vídeo da pasta `ENTREGA_FINAL_GRUPO7/` como apoio. Teste em outro computador se possível.
3. Separe a tabela E3, o gráfico `results/experiments_v2/exp3_comparacao_baselines.png` e um exemplo de limite (E4). Não prometa que uma execução específica completará as 100 salas.
4. Divida as falas e cronometre. Preparem-se para explicar o projeto inteiro e responder a uma mudança pedida pelo professor.
5. Confiram o conteúdo dos slides e demais documentos com o código e os resultados; sua existência não comprova aprovação nem conformidade. Os roteiros anteriores em Markdown, DOCX e PDF têm erros técnicos e não devem ser lidos sem revisão.

## Divisão sugerida dos 10 minutos

Os nomes abaixo são apenas uma sugestão; o grupo pode trocar as falas.

### 0–2 min — Eduardo: problema

> Nosso projeto investiga como encontrar estratégias para um guerreiro avançar por uma masmorra de 100 salas. A estratégia decide como investir em atributos, aliados e equipamentos. Como há muitas combinações e encontros variados, usamos um algoritmo genético para buscar estratégias e comparamos o resultado com alternativas mais simples.

> O objetivo principal é maximizar a média de salas concluídas em várias masmorras. A taxa de conclusão das 100 salas é uma métrica separada.

### 2–4 min — Fernando: dados

> Usamos um conjunto externo de 334 criaturas da API D&D 5e SRD 2014. Guardamos uma cópia local, a origem, a atribuição, o tratamento e uma verificação de integridade. Os dados descrevem criaturas; as salas e os resultados são gerados pelo simulador criado pelo grupo.

> O combate é uma adaptação simplificada, não uma reprodução completa das regras de D&D. As sementes permitem repetir os cenários. Nos experimentos principais, treinamos nas sementes 101 a 105 e avaliamos nas sementes 201 a 210.

Mostre **Dados e fonte** ou **Bestiário** rapidamente.

### 4–6 min — Matheus: algoritmo

> Cada estratégia é um cromossomo com 16 valores. Eles representam prioridades dos atributos do guerreiro, contratação e evolução de aliados, equipamentos e decisões econômicas. Os valores têm limites diferentes; um gene é discreto e alguns pesos são normalizados.

> Criamos uma população, avaliamos cada estratégia nas masmorras de treino, selecionamos candidatas, combinamos seus genes e aplicamos mutações. O elitismo preserva boas soluções. A aptidão prioriza a média de salas concluídas, com pequenos bônus por vida e ouro restantes.

Analogia: é como testar vários planos, combinar partes de planos promissores e introduzir pequenas variações. O processo busca uma boa solução; não garante a melhor possível. Mostre **Como funciona** se o tempo permitir.

### 6–8 min — Reuel: comparação e limites

> No experimento principal E3, a estratégia fixa concluiu em média 69 salas. A busca aleatória obteve 92,27 e o algoritmo genético 91,27. Nas sete repetições, a taxa média de conclusão foi 25,71% para a busca aleatória e 28,57% para o genético. As duas buscas tiveram o mesmo orçamento de 240 avaliações por repetição; a regra fixa é uma única estratégia, não uma busca de 240 candidatas.

> Nesse experimento não encontramos evidência estatística suficiente de diferença entre o algoritmo genético e a busca aleatória. Isso não prova que os métodos sejam equivalentes. O resultado mostra que o algoritmo genético não foi claramente superior nessa configuração.

> Também testamos mudanças no cenário. A melhor estratégia selecionada no E3 teve média de 96,9 salas na validação padrão, mas 73,4 com dificuldade 15% maior. Esses números são de uma estratégia individual, não a média das sete repetições.

Se perguntarem sobre E5: com 20 outras sementes e dez repetições, as médias foram 90,385 salas para AG com mutação de 10%, 92,495 para 25% e 94,56 para busca aleatória. A diferença entre as duas mutações não foi conclusiva (p = 0,241; intervalo inclui zero). O resultado por si só não demonstra por que um método foi melhor. Consulte `data/experiments/extra_mutation_e5_v1.json` e o pré-registro.

### 8–10 min — Rogério: demonstração

1. Em **Aventura**, escolha **Estratégia do algoritmo**, mantenha ou altere **Número da masmorra** e clique em **Iniciar com esta estratégia**. Mostre algumas salas, decisões e resultado. Explique que um resultado individual depende do cenário.
2. Em **Resultados**, aponte a comparação entre métodos. Se houver tempo, mostre **Como funciona** e a explicação dos genes.
3. Para um teste novo, abra **Laboratório**, altere **Número da masmorra**, força dos inimigos ou baús e clique em **Comparar neste cenário**. A comparação é uma tentativa por estratégia, não uma conclusão geral. As duas usam a mesma masmorra, mas decisões diferentes podem consumir a sequência aleatória de maneira diferente.

Se a busca automática for mostrada, avise que a masmorra escolhida participa da busca; vencer nela não é uma avaliação independente.

## Perguntas prováveis

- **Por que usar um AG?** Porque há várias decisões interdependentes e não temos um gabarito de estratégia ótima. O AG é uma forma de procurar boas combinações, mas a comparação com métodos simples é necessária.
- **Por que comparar com busca aleatória?** Para verificar se a evolução agrega valor quando ambos têm o mesmo orçamento. Nos nossos testes ela foi competitiva; o AG não venceu claramente no E3.
- **A IA sempre vence?** Não. O resultado depende da semente, das regras e da estratégia. Até a melhor estratégia escolhida falhou em cenários de validação.
- **O que os dados representam?** Criaturas de uma fonte externa. Salas, regras simplificadas e partidas são simulações do grupo; não são partidas reais.
- **A semente garante comparação perfeita?** Ela permite repetir a configuração, mas estratégias diferentes podem consumir a sequência aleatória de maneiras diferentes; não significa que todos os eventos sejam idênticos.

## Organização para o GitHub

- `app.py`, `src/`, `config/`: aplicação e implementação.
- `data/`: snapshot bruto e tratado, metadados e resultados de experimentos.
- `scripts/`: coleta, experimentos e geração de materiais.
- `tests/`: testes automatizados.
- `results/`: gráficos e resumos; `experiments_v2/` contém a comparação corrigida, enquanto `experiments/` preserva o histórico anterior.
- `docs/`: documentação do projeto; `docs/FINALIZACAO/` reúne guias e pré-registro.
- `ENTREGA_FINAL_GRUPO7/`: pacote organizado por documentação, divulgação, apresentação, evidências e instruções. Ele contém cópias de alguns dados e gráficos para consulta; os arquivos de origem continuam no repositório.

Antes de publicar: revise o `git status`, os nomes dos integrantes, dados pessoais e o diário de IA; verifique o conteúdo dos PDFs, vídeo, slides e QR Code; confira as exigências e o formato do resumo. Há materiais com afirmações exageradas ou incorretas: o checklist de 100% pronto e os roteiros antigos não são prova de conformidade. A URL pública do protótipo não foi confirmada. O GitHub é apenas uma parte da entrega exigida.

Nesta verificação, `python -m pytest tests -q` concluiu com **53 testes aprovados** em 10/11/2026. Isso não substitui ensaio, avaliação visual dos materiais ou publicação do aplicativo.
