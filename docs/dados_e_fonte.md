# Dataset e fonte da Masmorra Genética

**Dataset** é o conjunto de dados usado no projeto. **Fonte** é a origem desses dados.

Aqui, o dataset contém 334 registros de criaturas fictícias do D&D 5e SRD 2014, coletados em 29/10/2026. A fonte é a API D&D 5e SRD, mantida pela comunidade 5e-bits. Cada registro tem nome, tipo, tamanho, vida, classe de armadura, nível de desafio, atributos e ações. O endereço do registro original acompanha os dados tratados e os inimigos do simulador.

O algoritmo genético não aprende com exemplos de jogadores. Ele propõe estratégias, executa o simulador e recebe uma pontuação baseada na média de salas concluídas. Os registros das criaturas fornecem os adversários desses testes.

## Texto para o campo “Dataset/fonte” do Canvas

> Snapshot local de 334 criaturas da D&D 5e SRD API, edição 2014, coletado em 29/10/2026 e identificado como srd-2014-v1.0.0. Os registros externos fornecem os atributos dos inimigos; as masmorras, as adaptações de combate e os resultados são gerados pelo simulador do grupo. Fonte: https://www.dnd5eapi.co/api/2014/monsters. Origem, data, atribuição e hash do arquivo bruto constam no manifesto da coleta.

O PDF preenchido com a proposta de rotas ainda informa “APIs do Waze/GPS”. Esse campo descreve a proposta anterior e precisa ser substituído se a entrega for a Masmorra Genética. O PDF original foi mantido intacto.

## Onde conferir

| Etapa | Arquivo | O que contém |
| --- | --- | --- |
| Coleta | `data/raw/monsters_raw_srd2014.json` | Registros originais e origem de cada consulta. |
| Tratamento | `data/processed/monsters_srd2014_processed.csv` | Tabela com os campos organizados, tipos e medidas derivadas. |
| Tratamento | `data/processed/monsters_srd2014_processed.parquet` | Mesma tabela em formato binário, usada preferencialmente pela aplicação. |
| Proveniência | `data/metadata/collection_manifest.json` | Fonte, versão, data, contagens, atribuição e SHA-256 do JSON bruto. |
| Validação | `data/metadata/validation_report.json` | Verificações feitas durante a preparação dos registros. |
| Análise | `docs/eda_report.md` | Distribuições, campos ausentes, casos especiais e transformações. |
| Regras próprias | `config/balance.json` | Parâmetros de combate e de adaptação das criaturas. |
| Experimentos | `data/experiments/scientific_experiments_v2.json` | Resultados das simulações e configurações das comparações. |

A tela **Dados e fonte** permite baixar o CSV, o JSON bruto e o manifesto. A conferência calcula o SHA-256 do arquivo bruto e compara quantidade e IDs com a tabela carregada. Ela não certifica, sozinha, a correção de todas as transformações. A tela **Bestiário** filtra os registros por nome, tipo e desafio e permite baixar o recorte.

## O que é externo e o que foi criado pelo grupo

Os atributos originais das criaturas são dados publicados por terceiros. As criaturas são fictícias, mas os registros e a coleta estão documentados.

O grupo definiu a progressão de dificuldade, as fórmulas de adaptação, o guerreiro, a economia, as estratégias e o gerador de salas. Os combates, as vitórias e as derrotas são resultados simulados. Eles não representam partidas humanas nem reproduzem integralmente as regras do D&D.

Uma estratégia vencer a masmorra usada na busca interativa é um resultado de treino. Os experimentos científicos usam conjuntos de sementes distintos para treino e validação; a comparação completa está na ficha de experimentos.

## Referências

- [D&D 5e SRD API: documentação](https://docs.dnd5eapi.co/)
- [Lista de criaturas da edição 2014](https://www.dnd5eapi.co/api/2014/monsters)
- [Exemplo de registro: Goblin](https://www.dnd5eapi.co/api/2014/monsters/goblin)
- [SRD e condições de uso](https://www.dndbeyond.com/srd)

A atribuição escolhida para o conteúdo do SRD está no manifesto e aparece também na aplicação.
