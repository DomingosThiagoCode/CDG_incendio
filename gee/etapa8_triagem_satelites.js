// PROJETO FOGO — Etapa 8: TRIAGEM de cenas independentes (não validação concluída)
//
// Executar no Google Earth Engine Code Editor. Dispensa assets P1/P2 para localizar
// imagens: a AOI é apenas um retângulo que contém o evento 24340828.
// Para sobrepor P1/P2, usar no QGIS os GeoJSON versionados do projeto.
//
// OBJETIVO: inventariar cenas pré/pós, registrar aquisição/área válida e
// visualizar NBR/dNBR sem declarar que dNBR é verdade-terreno.
// Fontes: COPERNICUS/S2_SR_HARMONIZED (2020) e LANDSAT/LC08/C02/T1_L2.
// NBR = (NIR-SWIR2)/(NIR+SWIR2); dNBR = NBR_pre - NBR_pos.
// Imagens separadas podem ser adquiridas muitos dias antes/depois da transição.
// Não se pode inferir data exata de ignição ou fusão.

var CASO_ATIVO = 'incorporacao_p2';
var SENSOR = 'S2';                 // 'S2' ou 'L8' (comparar separadamente)
var JANELA_DIAS = 12;             // Antes de d0, depois de d1 (ver manifesto)
var MIN_FRACAO_VALIDA = 0.60;     // Apenas alerta de qualidade, não corte científico
var EXPORTAR_METADADOS = true;   // Cria uma tarefa CSV; executar em "Tasks"

// Recorte LAEA do resumo da Etapa 4 com margem geográfica aproximada.
var roi = ee.Geometry.Rectangle(
  [-58.02, -16.92, -57.46, -16.28], null, false
);

// Os controles foram pré-selecionados por hash dos intervalos no script Python.
// CONFIRMAR COM: resultados/etapa8/manifesto_cenas_24340828.csv.
var CASOS = {
  incorporacao_p2: {d0: '2020-09-10', d1: '2020-09-11', grupo: 'sentinela'},
  avanco_extremo_norte: {d0: '2020-08-31', d1: '2020-09-01', grupo: 'sentinela'},
  direcao_dispersiva: {d0: '2020-08-11', d1: '2020-08-12', grupo: 'sentinela'},
  controle_1: {d0: '2020-09-21', d1: '2020-09-22', grupo: 'controle'},
  controle_2: {d0: '2020-10-01', d1: '2020-10-02', grupo: 'controle'}
};

if (!CASOS[CASO_ATIVO]) throw new Error('CASO_ATIVO desconhecido');
if (SENSOR !== 'S2' && SENSOR !== 'L8') throw new Error('SENSOR deve ser S2 ou L8');

var caso = CASOS[CASO_ATIVO];
var preIni = ee.Date(caso.d0).advance(-JANELA_DIAS, 'day');
var preFim = ee.Date(caso.d0).advance(1, 'day');  // exclusivo
var posIni = ee.Date(caso.d1);
var posFim = ee.Date(caso.d1).advance(JANELA_DIAS + 1, 'day'); // exclusivo

Map.centerObject(roi, 10);
Map.addLayer(roi, {color: 'ffffff'}, 'Área de triagem', false);
print('Caso', CASO_ATIVO, caso, 'Sensor', SENSOR);
print('Pré: [início, fim exclusivo)', preIni.format('YYYY-MM-dd'),
  preFim.format('YYYY-MM-dd'));
print('Pós: [início, fim exclusivo)', posIni.format('YYYY-MM-dd'),
  posFim.format('YYYY-MM-dd'));

// SCL classe 2 (pixels escuros) é mantida para não excluir automaticamente
// cicatrizes escuras. Classes 0/1 sem dados ou saturação; 3 sombra de nuvem;
// 8/9/10 nuvens; 11 neve são excluídas. Classe 7 permanece incerta.
// QA60 NÃO é empregado.
function prepararS2(imagem) {
  var scl = imagem.select('SCL');
  var ok = scl.gte(2).and(scl.neq(3)).and(scl.lte(7)).rename('valido');
  var nir = imagem.select('B8A').multiply(0.0001);
  var swir = imagem.select('B12').multiply(0.0001);
  var nbr = nir.subtract(swir).divide(nir.add(swir))
    .rename('NBR').updateMask(ok);
  return imagem.addBands(nbr).addBands(ok);
}

// Landsat 8 Collection 2 L2: bits 0..5 do QA_PIXEL (fill,
// dilated cloud, cirrus, cloud, cloud shadow e snow); água é mantida.
function prepararL8(imagem) {
  var qa = imagem.select('QA_PIXEL');
  var ok = qa.bitwiseAnd(63).eq(0).rename('valido');
  var nir = imagem.select('SR_B5').multiply(0.0000275).add(-0.2);
  var swir = imagem.select('SR_B7').multiply(0.0000275).add(-0.2);
  var nbr = nir.subtract(swir).divide(nir.add(swir))
    .rename('NBR').updateMask(ok);
  return imagem.addBands(nbr).addBands(ok);
}

// Fração de pixels válidos no retângulo, amostrada em 120 m para triagem.
// O cálculo é aproximado e NÃO representa acurácia cartográfica.
function pontuar(imagem) {
  var frac = imagem.select('valido').unmask(0, false)
    .reduceRegion({
      reducer: ee.Reducer.mean(),
      geometry: roi,
      scale: 120,
      maxPixels: 10000000,
      bestEffort: true
    }).get('valido');
  return imagem.set('fracao_valida_roi', ee.Number(
    ee.Algorithms.If(frac, frac, 0)
  ));
}

function buscar(inicio, fim) {
  var colecao = (SENSOR === 'S2')
    ? ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterBounds(roi).filterDate(inicio, fim).map(prepararS2)
    : ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        .filterBounds(roi).filterDate(inicio, fim)
        .filter(ee.Filter.eq('PROCESSING_LEVEL', 'L2SP'))
        .map(prepararL8);
  return colecao.map(pontuar).sort('fracao_valida_roi', false);
}

function tabelaDeCenas(colecao, periodo) {
  var candidatos = colecao.toList(150);
  return ee.FeatureCollection(candidatos.map(function(x) {
    var im = ee.Image(x);
    return ee.Feature(null, {
      id_incendio: 24340828,
      caso: CASO_ATIVO,
      grupo: caso.grupo,
      periodo: periodo,
      sensor: SENSOR,
      imagem_id: im.id(),
      data_aquisicao: ee.Date(im.get('system:time_start')).format('YYYY-MM-dd HH:mm'),
      fracao_valida_roi: im.get('fracao_valida_roi'),
      fonte_colecao: SENSOR === 'S2'
        ? 'COPERNICUS/S2_SR_HARMONIZED'
        : 'LANDSAT/LC08/C02/T1_L2',
      nota: 'triagem; nao validacao independente concluida'
    });
  }));
}

var pre = buscar(preIni, preFim);
var pos = buscar(posIni, posFim);
var registrosPre = tabelaDeCenas(pre, 'pre');
var registrosPos = tabelaDeCenas(pos, 'pos');

print('Quantidade de cenas pré:', pre.size());
print('Quantidade de cenas pós:', pos.size());
print('Cenas pré (ordenadas por fração válida na AOI):', registrosPre);
print('Cenas pós (ordenadas por fração válida na AOI):', registrosPos);

// A ausência de cenas deve gerar aviso, e não uma "imagem" de validação.
var vazia = ee.Image.constant(0).rename('NBR')
  .updateMask(ee.Image.constant(0)).clip(roi);
var melhorPre = ee.Image(ee.Algorithms.If(pre.size().gt(0), pre.first(), vazia));
var melhorPos = ee.Image(ee.Algorithms.If(pos.size().gt(0), pos.first(), vazia));

print('Pré selecionada (maior cobertura utilizável na AOI):',
  ee.Algorithms.If(pre.size().gt(0), melhorPre.id(), 'SEM_CENA'));
print('Pós selecionada (maior cobertura utilizável na AOI):',
  ee.Algorithms.If(pos.size().gt(0), melhorPos.id(), 'SEM_CENA'));

var nbrPre = melhorPre.select('NBR');
var nbrPos = melhorPos.select('NBR');
var dNbr = nbrPre.subtract(nbrPos).rename('dNBR').clip(roi);
var parValido = nbrPre.mask().and(nbrPos.mask())
  .unmask(0, false).rename('par_valido');
var coberturaPar = parValido.reduceRegion({
  reducer: ee.Reducer.mean(),
  geometry: roi,
  scale: 120,
  bestEffort: true,
  maxPixels: 10000000
}).get('par_valido');
print('Fração aproximada de pixels claros nas DUAS cenas:',
  coberturaPar);
print('Cobertura mínima para revisão:',
  MIN_FRACAO_VALIDA,
  '(valor operacional; conferir também geometria da cobertura e nuvens)');
print('AVISO: dNBR NÃO indica sozinho a data física de queima.');
print('AVISO: cenas em janelas largas podem incluir queimadas de outras datas.');

Map.addLayer(nbrPre.clip(roi),
  {min: -0.5, max: 0.9, palette: ['#8c2d04', '#fdd49e', '#006d2c']},
  'NBR pré (cena isolada)', false);
Map.addLayer(nbrPos.clip(roi),
  {min: -0.5, max: 0.9, palette: ['#8c2d04', '#fdd49e', '#006d2c']},
  'NBR pós (cena isolada)', false);
Map.addLayer(dNbr,
  {min: -0.5, max: 0.8,
   palette: ['#2166ac', '#f7f7f7', '#f4a582', '#b2182b']},
  'dNBR exploratório, sem limiar de queimado', true);
Map.addLayer(parValido.selfMask().clip(roi),
  {palette: ['#00bfc4']},
  'Cobertura observada em ambas as cenas', false);

// Exportação MANUAL em Tasks, sem enviar geometrias nem dados sensíveis.
if (EXPORTAR_METADADOS) {
  Export.table.toDrive({
    collection: registrosPre.merge(registrosPos),
    description: 'fogo_etapa8_cenas_' + CASO_ATIVO + '_' + SENSOR,
    folder: 'Projeto_Fogo_Validacao',
    fileFormat: 'CSV'
  });
}
