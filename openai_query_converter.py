import openai
import logging
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class OpenAIQueryConverter:
    def __init__(self):
        api_key = os.getenv('OPENAI_KEY')
        if not api_key:
            raise ValueError("OPENAI_KEY not found in environment variables")
        
        self.client = openai.OpenAI(api_key=api_key)
        
        self.system_prompt = """
You are an expert in Google Earth Engine API. Convert natural language queries into executable Earth Engine JavaScript code.

Key Earth Engine patterns:
1. Image collections: ee.ImageCollection('collection_name')
2. Filtering: .filterDate(), .filterBounds(), .filter()
3. Visualization: Map.addLayer(image, visParams, 'layer_name')
4. Analysis: .reduce(), .map(), .select()
5. Time series: createTimeBand functions for temporal analysis

Common datasets:
- Landsat: 'LANDSAT/LC08/C02/T1_L2'
- Sentinel-2: 'COPERNICUS/S2_SR_HARMONIZED'  
- MODIS: 'MODIS/006/MCD12Q1', 'MODIS/006/MOD13A1'
- Night lights: 'NOAA/DMSP-OLS/NIGHTTIME_LIGHTS'
- Population: 'WorldPop/GP/100m/pop'
- Climate: 'ECMWF/ERA5/MONTHLY'

Example conversions:

Query: "Show me night-time lights trend over time"
Code:
```javascript
function createTimeBand(img) {
  var year = ee.Date(img.get('system:time_start')).get('year').subtract(1991);
  return ee.Image(year).byte().addBands(img);
}

var collection = ee.ImageCollection('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS')
  .select('stable_lights')
  .map(createTimeBand);

Map.addLayer(
  collection.reduce(ee.Reducer.linearFit()),
  {min: 0, max: [0.18, 20, -0.18], bands: ['scale', 'offset', 'scale']},
  'stable lights trend'
);
```

Query: "Show deforestation in the Amazon from 2020-2023"
Code:
```javascript
var amazon = ee.FeatureCollection('WCMC/WDOECM/current/polygons')
  .filter(ee.Filter.eq('NAME', 'Amazon'));

var beforeImage = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
  .filterDate('2020-01-01', '2020-12-31')
  .filterBounds(amazon)
  .median()
  .select(['SR_B4', 'SR_B3', 'SR_B2']);

var afterImage = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
  .filterDate('2023-01-01', '2023-12-31')
  .filterBounds(amazon)
  .median()
  .select(['SR_B4', 'SR_B3', 'SR_B2']);

var ndvi_before = beforeImage.normalizedDifference(['SR_B5', 'SR_B4']);
var ndvi_after = afterImage.normalizedDifference(['SR_B5', 'SR_B4']);
var change = ndvi_after.subtract(ndvi_before);

Map.addLayer(change, {min: -0.5, max: 0.5, palette: ['red', 'white', 'green']}, 'NDVI Change');
Map.centerObject(amazon, 4);
```

Always include:
- Proper filtering (date, bounds if applicable)
- Map.addLayer() with appropriate visualization parameters
- Map.centerObject() if showing specific regions
- Descriptive layer names

Return only executable JavaScript code without explanations.
"""

    async def convert_query_to_code(self, query: str) -> Optional[str]:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Convert this to Earth Engine code: {query}"}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            generated_code = response.choices[0].message.content.strip()
            
            if generated_code.startswith('```javascript'):
                generated_code = generated_code[13:-3].strip()
            elif generated_code.startswith('```'):
                generated_code = generated_code[3:-3].strip()
            
            return generated_code
            
        except Exception as e:
            logger.error(f"Error converting query to code: {e}")
            return None

    def validate_earth_engine_code(self, code: str) -> bool:
        required_patterns = ['ee.', 'Map.']
        dangerous_patterns = ['import', 'require', 'eval', 'exec']
        
        has_required = any(pattern in code for pattern in required_patterns)
        has_dangerous = any(pattern in code for pattern in dangerous_patterns)
        
        return has_required and not has_dangerous