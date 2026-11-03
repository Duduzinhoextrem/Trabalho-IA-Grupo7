# Roteiros de divulgação e apresentação

Este arquivo reúne conteúdo inicial. Ele não substitui o folder diagramado, o carrossel, o vídeo gravado, os slides ou o teste da aplicação publicada.

## Folder de uma página com dobra

- **Capa:** “Até onde sua estratégia consegue chegar?” e identificação do Grupo 7.
- **O problema:** preparar um guerreiro para atravessar 100 salas de uma masmorra simulada.
- **Os dados:** criaturas do D&D 5e SRD, com regras de combate adaptadas pelo grupo.
- **Como funciona:** várias estratégias são testadas; as melhores são combinadas e alteradas para gerar novas opções.
- **Resultado e limite:** no experimento `v2`, o AG e a busca aleatória alcançaram médias próximas; os resultados dependem das regras e das sementes.
- **Convite:** endereço e QR Code da aplicação, quando houver uma URL pública verificada; nomes dos integrantes e disciplina.

## Carrossel sugerido

1. “Uma estratégia consegue atravessar 100 salas?”
2. Apresentar o guerreiro, os aliados e o desafio.
3. Explicar que os registros de criaturas vêm do SRD e que os combates são simulados.
4. Mostrar, com uma analogia simples, seleção, cruzamento e mutação.
5. Comparar a média de salas do AG, da busca aleatória e da regra fixa, identificando as condições do teste.
6. Mostrar uma limitação e convidar o público a testar a aplicação quando a URL estiver disponível.

## Vídeo demonstrativo — 1 a 3 minutos

- Abertura: apresentar a pergunta e a masmorra.
- Demonstração: iniciar a busca automática até vencer a masmorra escolhida, rever algumas salas e comparar o resultado; se houver tempo, testar uma estratégia escolhida pela plateia. Explicar que a masmorra escolhida participa do treino e que os experimentos usam validação separada.
- Explicação: mostrar rapidamente como uma geração de estratégias é testada.
- Encerramento: apresentar um resultado real, uma limitação e o endereço verificado da aplicação.

O roteiro precisa ser gravado e revisado pelo grupo. Não há vídeo final ou link verificado neste repositório.

## Apresentação — núcleo de aproximadamente 40 minutos

| Bloco | Tempo sugerido |
| --- | ---: |
| Abertura e pergunta | 3 min |
| Problema e público | 4 min |
| Analogia e funcionamento técnico do AG | 9 min |
| Dados, tratamento e descobertas | 6 min |
| Experimentos e comparação | 8 min |
| Falhas e limitações | 4 min |
| Demonstração com entrada da plateia | 5 min |
| Conclusão | 1 min |

Preparar respostas para os critérios da disciplina: por que usar o AG, qual é a alternativa simples, quais foram os problemas dos dados, como treino e validação foram separados, por que a métrica foi escolhida e onde a estratégia falhou. Todos os integrantes devem conhecer o projeto completo.

## Publicação e plano alternativo

1. Conferir os arquivos, resultados e testes; publicar o repositório em uma conta do grupo.
2. No Streamlit Community Cloud, conectar o repositório e selecionar `app.py`. A criação da aplicação depende do acesso à conta do grupo.
3. Abrir a URL resultante em outro navegador e celular, executar uma jornada e o laboratório e verificar os links de fonte. Só então criar os QR Codes.
4. Ter uma cópia local funcional, os dados congelados e os resultados disponíveis para a apresentação sem depender da API. Testar essa alternativa antes do dia.

Não há URL pública verificada neste repositório. O teste de presença de arquivos de deploy não substitui o teste da aplicação online.

## Datas indicadas nos materiais da disciplina

- 03/11/2026: experimentos, métricas, comparação e análise de casos inesperados.
- 10/11/2026: pré-banca com protótipo funcional e demonstração com entrada não preparada.
- 17/11/2026, até 17h: entrega final comum a todos os grupos.
- 01/12/2026: apresentação do Grupo 7, conforme o mapa de sorteio.
