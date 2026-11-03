# Revisão do protótipo e próximos ajustes

Revisão de 03/11/2026. O escopo foi o protótipo local da Masmorra Genética, seu código e a comparação dos materiais existentes com o guia e os checklists fornecidos. Os documentos da disciplina foram tratados como referência da entrega.

## Implementado nesta revisão

- Identidade de atlas de expedição: papel, tinta, detalhes em vermelho e gravuras vetoriais locais. A navegação aparece em capítulos, e a abertura apresenta uma planta esquemática das 100 salas.
- Ficha de estratégia com distribuição de atributos, aliado e prioridade de compra.
- Encontro atual antes do histórico de treinamento. O mapa do replay permite escolher diretamente uma sala registrada.
- Bestiário com fichas por família, busca literal por nome, filtro por tipo e faixa de desafio, além de exportação do recorte.
- Tela Dados e fonte com explicação da proveniência, amostra, arquivos para download e conferência do snapshot.
- Busca e simulação separadas da renderização do Streamlit em `src/services/journey.py`.
- Continuação de busca recusa juntar tentativas quando dados, regras, semente ou opção de baús mudaram.
- Progresso de busca baseado em avaliações reais, sem atraso artificial de reprodução ao final.
- Relatório JSON de jornada com genes, regras, semente, resultados, comparadores e histórico; CSV das tentativas também pode ser baixado.
- Validação de parâmetros inválidos do algoritmo com mensagens antes da execução.

Os arquivos de experimentos existentes e as regras de combate foram mantidos nesta revisão. A identidade visual e as novas funções não são uma nova execução dos experimentos científicos.

## Validação realizada

- `python -m pytest tests -q`: **48 testes passaram**. A suíte cobre orçamento, parada da busca, continuação, reprodução, integridade, navegação e resultados registrados.
- Navegador: jornada manual, avanço de sala, busca automática, histórico, consulta à fonte e filtro do Bestiário. Na busca interativa da masmorra 201, a vitória ocorreu após 59 estratégias avaliadas; esse cenário participa do treino.
- O relatório de uma jornada manual foi baixado pela interface e reproduzido com os genes, regras e semente exportados. O novo processamento coincidiu com as 69 salas concluídas e a sala de derrota registrada.
- Tela inicial conferida na largura normal e em 390 × 844 px; a medida de largura do documento não excedeu os 390 px no teste móvel. A captura real da tela inicial está em `docs/images/inicio.jpg`.
- Sintaxe Python e diferenças de formatação conferidas. Não houve nova execução dos experimentos científicos completos, publicação, commit ou push.

## Pendências observadas para a entrega

| Prioridade | Pendência | Ação concreta |
| --- | --- | --- |
| Alta | Canvas do PDF ainda apresenta a ideia de rotas e Waze/GPS. | Usar `docs/canvas_projeto.md` e o texto de `docs/dados_e_fonte.md` para preencher o material definitivo. |
| Alta | URL pública não verificada. | Publicar o protótipo, testar o acesso fora da máquina e depois conferir os QR Codes. |
| Alta | Resumo ainda é um rascunho em Markdown. | Formatar no modelo vigente da Jornada Científica da FIB e conferir o limite de duas páginas. |
| Alta | Folder, carrossel, vídeo e apresentação têm roteiro, mas não foram comprovados como peças finais. | Produzir os arquivos finais usando capturas reais, resultados conferidos e links publicados. |
| Média | Falta comprovar uso em outro computador e uma demonstração sem internet. | Testar instalação com o snapshot local e guardar um vídeo curto de reserva. |
| Média | A demonstração precisa receber uma entrada da plateia. | Sortear uma semente no Laboratório e interpretar o resultado sem prometer vitória do AG. |
| Média | Poucas sementes e reutilização da validação limitam as conclusões. | Se ampliar a investigação, reservar um novo conjunto de sementes antes de observar seus resultados e comparar orçamentos iguais. |

O checklist do PDF informa entrega final em 17/11/2026 às 17h. A publicação, a criação das peças finais e a alteração do PDF não fizeram parte desta revisão do código.
