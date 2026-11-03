# Análise dos dados de criaturas

O projeto usa o snapshot `srd-2014-v1.0.0`, coletado em 29/10/2026 da [D&D 5e SRD API](https://docs.dnd5eapi.co/). Ele contém 334 registros de criaturas fictícias. Os arquivos brutos, tratados, o manifesto da coleta e o relatório de validação estão em `data/`; os gráficos e os números calculados estão em `results/eda/`.

A fonte da API é o projeto 5e-bits. O conteúdo do SRD 5.1 é da Wizards of the Coast; a atribuição e o endereço da licença estão no manifesto. O [antigo repositório da base](https://github.com/5e-bits/5e-database) foi arquivado e aponta para o repositório atual. As fórmulas e instâncias de combate são adaptações do grupo, não valores originais da API.

## Qualidade e preparação

- A listagem indicou 334 registros; a coleta registrou 334 recebidos, sem falhas HTTP ou índices duplicados.
- Os campos obrigatórios verificados, como nome, tipo, vida e nível de desafio, estão preenchidos nos 334 registros. Isso não significa que todos os campos opcionais estejam completos: `subtype` está ausente em 258 registros, por exemplo.
- A classe de armadura e as ações foram normalizadas a partir de estruturas aninhadas. O dano esperado das ações que usam dados é estimado por uma fórmula, quando a expressão pode ser interpretada.
- A análise identificou cinco registros sem dano direto reconhecido nas ações. Quatro formas passivas ou alternativas (`frog`, `sea-horse`, `shrieker` e `vampire-mist`) são excluídas da seleção de encontros. O `rug-of-smothering` permanece elegível e recebe o tratamento de dano estimado quando necessário.
- Quando não há dano de ação suficiente para a conversão, o simulador usa uma estimativa baseada em desafio e atributos. Essa estimativa é uma regra criada pelo grupo e pode não representar as habilidades reais da criatura.

## Descobertas do snapshot

1. **Vida e desafio:** a vida original tem mediana de 45 e varia de 1 a 676. A correlação de Pearson entre vida e nível de desafio é 0,9404 neste conjunto. É uma associação geral, não uma previsão exata para cada criatura.
2. **Experiência é assimétrica:** a mediana é 450 XP, enquanto o máximo é 155.000. Como os valores mais altos são muito distantes dos mais comuns, a recompensa do simulador usa uma transformação sublinear em vez de somar o XP original diretamente.
3. **Destreza e desafio:** a correlação de Pearson entre as duas variáveis é -0,0100. A análise não encontrou relação linear relevante no conjunto; isso não permite concluir que todos os grupos de criaturas tenham a mesma destreza.
4. **Resistências:** 85 registros têm resistência ou imunidade física identificada e 133 têm resistência ou imunidade elemental/mágica identificada. Esses indicadores são simplificações das listas originais, não uma medida de quantas batalhas uma estratégia vencerá.

Os gráficos de distribuição de desafio, vida, tipos, atributos ofensivos, relações entre variáveis e matriz de correlação estão em `results/eda/`. As estatísticas completas e a contagem de campos ausentes estão em `results/eda/eda_summary.json`.

## Uso no simulador

O gerador usa o nível de desafio para selecionar encontros e mantém o identificador e a URL da criatura. Vida, classe de armadura, atributos, ações, dano e resistências entram nas fórmulas de adaptação em `src/game/monsters.py`; desafio e experiência também influenciam as recompensas. Os parâmetros das fórmulas estão em `config/balance.json`.

O simulador simplifica as ações e os efeitos. Campos como idiomas, alinhamento e deslocamento não determinam o combate. Os dados tratados e os resultados das simulações não devem ser apresentados como dados de partidas observadas.
