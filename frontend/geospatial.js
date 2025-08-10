const embeddings = ee.ImageCollection('GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL');
const s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED');
const csPlus = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED');

const YEAR = 2024;
const dateFilter = ee.Filter.date(YEAR + '-01-01', (YEAR + 1) + '-01-01');

const mosaic = embeddings.filter(dateFilter).mosaic();
const bandNames = mosaic.bandNames();

const PALETTE = ['000004', '2C105C', '711F81', 'B63679', 'EE605E', 'FDAE78', 'FCFDBF', 'FFFFFF'];
let PANELS_ADDED = false;

// Helper: color bar
function ColorBar(palette) {
  return ui.Thumbnail({
    image: ee.Image.pixelLonLat().select(0),
    params: {
      bbox: [0, 0, 1, 0.1],
      dimensions: '225x20',
      format: 'png',
      min: 0,
      max: 1,
      palette: palette,
    },
    style: { stretch: 'horizontal', margin: '2px 2px' },
  });
}

// Helper: legend panel
function makeLegend(palette) {
  const legendTitle = ui.Label({
    value: 'Similarity in embedding space',
    style: {
      fontWeight: 'bold',
      fontSize: '16px',
      margin: '0 0 2px 0',
      padding: '0',
      backgroundColor: 'rgba(255, 255, 255, 0)'
    }
  });

  const labelPanel = ui.Panel({
    widgets: [
      ui.Label('Less similar', { margin: '0px 0px', backgroundColor: 'rgba(255, 255, 255, 0)', fontSize: '14px' }),
      ui.Label(' ', { margin: '0px 0px', textAlign: 'center', stretch: 'horizontal', backgroundColor: 'rgba(255, 255, 255, 0)', fontSize: '12px' }),
      ui.Label('More similar', { margin: '0px 0px', backgroundColor: 'rgba(255, 255, 255, 0)', fontSize: '14px' })
    ],
    layout: ui.Panel.Layout.flow('horizontal'),
    style: { backgroundColor: 'rgba(255, 255, 255, 0)' }
  });

  return ui.Panel({
    widgets: [legendTitle, ColorBar(palette), labelPanel],
    style: {
      position: 'bottom-left',
      backgroundColor: 'rgba(255, 255, 255, 0.75)'
    }
  });
}

// Helper: simple contrast/brightness tweak
function magic(i, lo, hi, sat) {
  i = i.add(1).log().divide(10).subtract(lo).divide(hi - lo);
  const greyAxis = ee.Image(0.57735026919)
    .addBands(ee.Image(0.57735026919))
    .addBands(ee.Image(0.57735026919));
  const greyLevel = greyAxis.multiply(i.multiply(greyAxis).reduce('sum'));
  return i.subtract(greyLevel).multiply(sat).add(greyLevel);
}

// UI Panels
const legendPanel = ui.Panel({
  style: {
    width: '280px',
    position: 'bottom-left',
    backgroundColor: 'rgba(255, 255, 255, 0.85)'
  }
});

const legendSubpanel = ui.Panel({
  style: {
    width: '260px',
    position: 'top-left',
    backgroundColor: 'rgba(255, 255, 255, 0.5)'
  }
});

const thumbPanel = ui.Panel({
  style: {
    width: '280px',
    position: 'bottom-left',
    backgroundColor: 'rgba(255, 255, 255, 0.85)'
  }
});

// Add base panels
const introText = ui.Label({
  value: 'Click a point...',
  style: { fontWeight: 'bold', fontSize: '18px', backgroundColor: 'rgba(255, 255, 255, 0)' }
});
Map.add(legendPanel);
legendPanel.add(legendSubpanel.add(introText));

// Click handler: compute similarity and update UI
function handleMapClick(location) {
  // Clear distance layer.
  Map.layers().set(0, null);

  // Clicked point
  const point = ee.Geometry.Point([location.lon, location.lat]);
  const pointLayer = ui.Map.Layer(point, { color: 'black' }, 'clicked point');
  Map.layers().set(1, pointLayer);

  ui.url.set('lon', location.lon);
  ui.url.set('lat', location.lat);
  ui.url.set('clicked', true);

  // Cosine similarity via dot product with clicked pixel embedding
  const similarity = ee.ImageCollection(
    mosaic.sample({ region: point, scale: 10 }).map(function (f) {
      return ee.Image(f.toArray(bandNames))
        .arrayFlatten(ee.List([bandNames]))
        .multiply(mosaic)
        .reduce('sum');
    })
  );

  const similarityLayer = ui.Map.Layer(similarity, { palette: PALETTE, min: 0, max: 1 }, 'similarity layer');
  Map.layers().set(0, similarityLayer);

  // Sentinel-2 annual median composite with cloud score filtering
  let composite = s2
    .filterBounds(point)
    .filter(dateFilter)
    .linkCollection(csPlus, ['cs_cdf'])
    .map(function (img) { return img.updateMask(img.select('cs_cdf').gte(0.5)); })
    .median();

  // Enhance visualization
  composite = magic(composite.select(['B4', 'B3', 'B2']), 0.58, 0.9, 1.3)
    .visualize({ bands: ['B4', 'B3', 'B2'], min: 0, max: 1 });

  // Thumbnail centered on clicked point
  const parameters = {
    dimensions: [256, 256],
    region: point.buffer(1280 / 2).bounds(),
    crs: 'EPSG:3857',
    format: 'png'
  };

  const thumb = ui.Thumbnail({ image: composite, params: parameters });
  const thumbLabel = ui.Label({
    value: location.lon.toFixed(4) + ', ' + location.lat.toFixed(4),
    style: { margin: '2px', backgroundColor: 'rgba(255, 255, 255, 0)', fontSize: '14px' }
  });

  // One-time panel additions
  if (PANELS_ADDED === false) {
    legendPanel.clear();
    legendPanel.add(makeLegend(PALETTE));
    Map.add(thumbPanel);
    PANELS_ADDED = true;
  }

  // Update thumbnail
  thumbPanel.clear();
  thumbPanel.add(thumb).add(thumbLabel);
}

// Restore from URL state
if (ui.url.get('clicked') === true) {
  Map.setCenter(ui.url.get('lon'), ui.url.get('lat'), ui.url.get('zoom'));
  handleMapClick({ lon: ui.url.get('lon'), lat: ui.url.get('lat') });
}

// Event bindings
Map.onClick(handleMapClick);
Map.onChangeZoom(function (zoom) { return ui.url.set('zoom', zoom); });
Map.style().set({ cursor: 'crosshair' });
Map.setOptions('SATELLITE');