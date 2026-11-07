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
5. **Etapa atual:** passar da geração de produtos para uma **especificação
   verificável de testes espaciais e automações**. Resultados científicos dos
   métodos de região móvel e das métricas de paisagem ainda estão em análise.

## O que significa “P1/P2 prontos”

Os arquivos existem e passaram em testes de estrutura, correspondência de
datas, contagens, áreas declaradas e ranks. Isso **não prova** que todas as
geometrias são válidas, que a associação espacial entre datas é correta, nem
que o algoritmo se comporta bem quando o ID do incêndio é alterado.

P1 é um conjunto de **componentes por data**, não um cadastro de patches com
identidade temporal persistente. P2 contém a **região móvel rastreada** em cada
observação. Os polígonos representam **área queimada acumulada**, não posição
instantânea da frente ativa de fogo.

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

Esses testes são **requisitos propostos**, ainda não implementados integralmente.
O script atual cobre apenas a primeira linha e parte do diagnóstico temporal.
Consulte [roteiro.md](roteiro.md) para a ordem das próximas etapas.
