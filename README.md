# Masmorra Genética

Um guerreiro precisa atravessar uma masmorra de 100 salas. Qual estratégia ajuda mais: distribuir os pontos de forma equilibrada, experimentar escolhas aleatórias ou usar um algoritmo genético para procurar boas combinações?

O projeto do Grupo 7, da disciplina Inteligência Artificial II da FIB, investiga essa pergunta usando um simulador de combates e dados de criaturas do D&D 5e SRD. A aplicação permite treinar e jogar automaticamente, montar uma estratégia própria, acompanhar a jornada e comparar os resultados.

![Tela inicial da Masmorra Genética com o atlas das 100 salas](docs/images/inicio.jpg)

## Como usar

1. Na tela inicial, escolha **Treinar e iniciar automaticamente** para procurar uma estratégia e acompanhar sua jornada. Ou abra **Aventura** para escolher o foco do guerreiro, um aliado preferido e a prioridade no mercado.
2. Os combates e as decisões de compra são automáticos; a tela apresenta o registro da simulação, que pode ser revisto sala por sala.
3. Após a busca automática, abra **Ver tentativas anteriores e evolução** para comparar estratégias que falharam, ver em que sala pararam e reproduzir o combate final de uma delas. O histórico é mantido durante a sessão e nas continuações da mesma busca.
4. Compare a tentativa com a estratégia do algoritmo. Em **Como funciona**, é possível executar um treinamento pequeno e usar a estratégia gerada na aventura.
5. Explore **Resultados**, **Bestiário**, **Dados e fonte** e **Laboratório** para conhecer os dados, os experimentos e testar outras condições. O Bestiário filtra por nome, tipo e nível de desafio; o recorte pode ser baixado em CSV.
6. Na jornada, use **Mapa da expedição** para rever uma sala e **Salvar relatório da jornada** para baixar as regras, a semente, os genes e os resultados. O histórico da busca também pode ser baixado em CSV.

Cada sessão é independente. A comparação interativa usa a mesma masmorra e semente para os dois métodos, mas as decisões podem fazer com que eles consumam a sequência aleatória de maneiras diferentes.

No modo automático, a aplicação cria e evolui estratégias até encontrar uma que vença as 100 salas da masmorra escolhida, 201 por padrão. A busca também avalia as sementes 101–105 e usa a média de salas como fitness. Quando disponível, a estratégia salva nos experimentos integra a população inicial e é reavaliada. Cada rodada testa até 400 estratégias, com população de 16; se não encontrar uma vencedora nesse limite, a tela oferece **Continuar procurando** a partir da melhor tentativa encontrada.

Como a masmorra escolhida participa da busca, a vitória nela é um resultado de treino, não um teste independente. Vencer as 100 salas nesse cenário também não prova que a estratégia seja ótima ou vença outras masmorras. Os experimentos científicos continuam com sementes de treino e validação separadas.

## Executar localmente

É necessário ter Python instalado. Na pasta do projeto:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

O Streamlit informa o endereço local no terminal. O dataset e os resultados já estão no repositório; a aplicação não precisa consultar a API a cada visita.

Para executar os testes:

```bash
python -m pytest tests -q
```

Para validar o snapshot e gerar novamente a análise exploratória:

```bash
python scripts/run_etl_and_eda.py
```

Por padrão, esse comando usa a cópia local. Para tentar uma nova coleta da API, acrescente `--refresh`. Uma nova coleta pode alterar os dados e não deve substituir o snapshot usado para reproduzir os resultados sem registrar a mudança.

Para repetir os quatro experimentos científicos:

```bash
python scripts/run_scientific_experiments.py
```

O processamento completo pode levar vários minutos. Ele grava os resultados em `data/experiments/scientific_experiments_v2.json` e os gráficos em `results/experiments_v2/`. O arquivo `v1` foi preservado como histórico, mas suas comparações não devem ser apresentadas como tendo orçamentos iguais: o AG realizou 218 avaliações onde a busca aleatória realizou 240. A versão `v2` corrige a comparação e também torna a composição alternativa reproduzível entre processos.

## Dados e regras

**Dataset** é o conjunto de dados; **fonte** é a origem desses dados. Neste projeto, usamos os registros de criaturas da API D&D 5e SRD. As salas e os resultados de combate são gerados pelo simulador do grupo. A explicação e um texto para preencher o Canvas estão em [docs/dados_e_fonte.md](docs/dados_e_fonte.md); os arquivos podem ser baixados na tela **Dados e fonte**.

O snapshot `srd-2014-v1.0.0`, coletado em 29/10/2026, contém **334 registros** de criaturas fictícias da [D&D 5e SRD API](https://docs.dnd5eapi.co/), mantida pela comunidade 5e-bits. A versão bruta, os dados tratados, o manifesto e a validação estão em `data/`.

Os registros do SRD são dados externos; as salas, equipamentos, fórmulas de combate e resultados das partidas são criações ou simulações do grupo. Cada inimigo da masmorra mantém um link para o registro de origem. O combate é uma adaptação simplificada, não uma implementação completa das regras de D&D.

O SRD 5.1 é disponibilizado pela Wizards of the Coast sob CC BY 4.0 e OGL 1.0a. A atribuição escolhida para o conteúdo do SRD consta em `data/metadata/collection_manifest.json`; consulte também o [SRD 5.1 e suas condições](https://www.dndbeyond.com/srd). A API e seu código são projetos separados do conteúdo do SRD. O antigo [repositório da base](https://github.com/5e-bits/5e-database) foi arquivado e aponta para o repositório atual da API.

A exploração dos dados, os valores ausentes e as transformações estão em [docs/eda_report.md](docs/eda_report.md). A configuração de combate está em `config/balance.json`.

## Algoritmo e experimentos

Cada estratégia é representada por 16 valores que orientam a distribuição de atributos, as prioridades de aliados e as compras. O algoritmo cria uma população, testa os candidatos, seleciona estratégias, combina seus genes e aplica mutações. A principal métrica é a média de salas concluídas; a taxa de conclusão das 100 salas é apresentada separadamente.

O conjunto de treino usa as sementes 101–105. O conjunto de validação usa 201–210, e a composição alternativa usa 301–310. As configurações comparam:

- três taxas de mutação;
- três tamanhos de população com o mesmo orçamento efetivo;
- estratégia fixa, busca aleatória e algoritmo genético;
- a estratégia selecionada no treino em novos cenários, com mudanças de composição, dificuldade e baús.

Na comparação `v2`, busca aleatória e AG fizeram **240 avaliações efetivas por repetição**, em sete repetições. O elitismo preserva indivíduos já avaliados; por isso, a última geração pode ser parcial. As avaliações, sementes, configurações e resultados estão no JSON. A estratégia fixa é uma única regra, não uma busca com 240 candidatos.

| Método | Média de salas na validação | Conclusão das 100 salas |
| --- | ---: | ---: |
| Estratégia fixa | 69,00 | 0,00% |
| Busca aleatória | 92,27 | 25,71% |
| Algoritmo genético | 91,27 | 28,57% |

A tabela mostra a média das sete repetições para busca aleatória e AG, avaliadas nas mesmas dez sementes; a regra fixa foi avaliada uma vez nessas sementes. Nesta execução, a busca aleatória teve média maior de salas, e o AG teve taxa média de conclusão maior. Essas diferenças não demonstram superioridade geral de um método.

A estratégia individual selecionada pelo desempenho no treino alcançou média de **96,9 salas** e concluiu as 100 salas em **4 das 10** sementes de validação. Não confunda esse resultado de um indivíduo com a média das sete repetições. A ficha em [docs/ficha_experimentos.md](docs/ficha_experimentos.md) apresenta a metodologia, outros cenários e casos de falha.

## Limitações

- As batalhas são simulações e dependem das fórmulas de balanceamento escolhidas pelo grupo. Não são dados de partidas reais.
- Cinco masmorras de treino são uma amostra pequena. O mesmo conjunto de validação aparece em vários experimentos, portanto não deve ser tratado como uma prova de desempenho em qualquer masmorra ou como um teste independente adicional após decisões baseadas nele.
- Os dados de monstros são adaptados e resumidos; ações especiais e resistência não reproduzem integralmente as regras do SRD.
- O algoritmo não garante a melhor estratégia possível e pode perder para uma alternativa mais simples em uma execução ou cenário.
- O teste automatizado dos arquivos de deploy não comprova que há uma URL pública disponível.

## Materiais e entrega

A [revisão de melhorias e pendências](docs/revisao_e_melhorias.md) registra o que mudou na interface e no motor da jornada, além dos ajustes restantes nos materiais.

O repositório contém o [Canvas](docs/canvas_projeto.md), a [ficha de experimentos](docs/ficha_experimentos.md), o [Model Card](docs/model_card.md), um [rascunho de resumo](docs/resumo_expandido.md), a [análise exploratória](docs/eda_report.md) e um [roteiro de divulgação e apresentação](docs/materiais_divulgacao_e_apresentacao.md). Os roteiros não são o vídeo, o folder, o carrossel nem os slides finalizados. O resumo ainda precisa ser formatado no modelo vigente da Jornada Científica da FIB.

O formulário em PDF fornecido anteriormente ao grupo descreve uma proposta de rotas; ele deve ser atualizado ou substituído pelo Canvas da masmorra antes da entrega, se ainda for usado.

A aplicação está preparada para execução em Streamlit, mas **uma publicação e uma URL pública ainda não foram verificadas**. O prazo comum de entrega indicado nos materiais da disciplina é 17/11/2026 às 17h; a apresentação do Grupo 7 está indicada para 01/12/2026. É necessário testar o protótipo em outro computador ou navegador, preparar um plano sem internet e conferir os materiais e QR Codes após a publicação.

## Integrantes

Eduardo Coque Corrêa de Lima · Fernando Eduardo Motta Mendes · Matheus Alcântara Pereira · Reuel Vitor Lanzetti · Rogério Tiritan Marcone.
