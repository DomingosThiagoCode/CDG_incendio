# Marcos do projeto — do protótipo aos testes

Este registro descreve o que foi efetivamente produzido até novembro de 2026,
sem tratar trabalhos exploratórios como resultados validados do estudo final.

## Histórico sucinto

1. **Exploração:** testes de métricas e trajetórias sobre outros fenômenos,
   incluindo furacão Beryl e conjuntos experimentais de formas/polígonos.
   Serviram para testar ferramentas, indicadores e métodos de região móvel.
2. **Recorte do estudo:** escolha do evento `24340828` do Pantanal de 2020,
   no GlobFire v2, em vez da análise de todos os IDs de incêndios do bioma.
3. **Pré-processamento no GEE:** separação temporal das componentes espaciais
   (P1) e rastreamento da região móvel principal (P2).
4. **Primeira conferência:** 57 datas, 978 feições em P1 e 57 em P2;
   consistência numérica e temporal verificada por script Python. Os dois
   GeoJSON originais usados nessa verificação foram guardados em
   `dados/estudo_caso_24340828/`.
5. **Auditoria espacial (Etapa 1):** verificação da validade geométrica após
   reprojeção LAEA, comparação P1/P2, detecção de sobreposições e candidatos
   a fusão, testes sintéticos e comparação de regularização. Os originais
   permaneceram intactos; o resultado está em
   [auditoria_espacial_24340828.md](auditoria_espacial_24340828.md).
6. **Métricas de paisagem (Etapa 2):** implementadas métricas vetoriais
   reproduzíveis por patch e data, além de uma análise de sensibilidade por
   contato de vértices. Foram observados 657 pares de contatos pontuais ao
   longo das datas, mostrando que a contagem de patches depende da
   interpretação topológica; os P1/P2 originais permanecem como base.
   Consulte [metricas_paisagem_24340828.md](metricas_paisagem_24340828.md).
7. **Relações temporais entre patches (Etapa 3):** reproduzida a associação
   entre datas por interseção de área, distinguindo correspondências 1→1,
   convergências N→1 e surgimentos sem predecessor. O caso apresentou 963
   vínculos, 72 convergências e 219 surgimentos sem sobreposição anterior;
   a transição 10→11/09 reúne um grupo de 21 patches anteriores para um
   posterior. Geradas quatro tabelas, um resumo JSON e GeoJSON de
   convergências para revisão no QGIS. Interpretação **geométrica**, não
   confirmação de fusões físicas; consultar
   [linhagens_patches_24340828.md](linhagens_patches_24340828.md).
8. **Etapa seguinte:** reproduzir a metodologia da Major de forma
   independente, implementar a do Coronel e comparar as regiões móveis,
   enquanto as questões de conectividade e causalidade são debatidas na
   orientação. Resultados científicos finais ainda estão em análise.

## O que significa “P1/P2 prontos”

Os arquivos existem e passaram em testes de estrutura, correspondência de
datas, contagens, áreas declaradas, ranks e relações espaciais. Todas as
geometrias passaram na verificação de validade após reprojeção para LAEA
local neste estudo de caso. Isso **não prova** exatidão cartográfica nem
garante que o algoritmo se comporte bem quando o ID é alterado.

P1 é um conjunto de **componentes por data**. A Etapa 3 acrescentou uma
**identificação temporal derivada e conservadora** a esses registros, sem
alterar o P1: linhagens são herdadas apenas em correspondências 1→1. P2
contém a **região móvel rastreada** em cada observação. Os polígonos
representam **área queimada acumulada**, não posição instantânea da frente
ativa de fogo.

## Próxima especificação de testes

| Nível | Cenário a testar | Resultado esperado |
| --- | --- | --- |
| Estrutural | Campos, IDs, datas e ranks | Integridade e coerência numérica |
| Geométrico | Polígonos inválidos, área e sistema de referência | Diagnóstico com tolerâncias explícitas |
| Temporal | Intervalos sem observação, crescimento e redução anômalos | Alertas sem interpolação silenciosa |
| Topológico | Surgimento, separação e fusão de patches sintéticos | Continuidade e eventos corretamente classificados |
| Rastreamento | Patch menor permanece dominante na continuidade espacial | P2 acompanha o mesmo fenômeno, não apenas o rank 1 |
| Generalização | Novo ID GlobFire com outras datas e números de patches | Execução sem condições especiais para o evento 24340828 |
| Reprodutibilidade | Nova exportação GEE com parâmetros e fonte fixados | Diferenças registradas e justificadas |

Esses testes representam uma **especificação incremental**. O validador
estrutural, a auditoria espacial e os testes sintéticos cobrem as primeiras
etapas, mas conectividade, rastreamento independente, generalização para
outros IDs e reexecução do GEE ainda não foram verificados integralmente.
Consulte [roteiro.md](roteiro.md) para a ordem das próximas etapas.
