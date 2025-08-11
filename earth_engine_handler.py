import ee
import logging
import os
from typing import Dict, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class EarthEngineHandler:
    def __init__(self):
        self.initialized = False
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def initialize(self):
        try:
            service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
            
            if service_account_path and os.path.exists(service_account_path):
                credentials = ee.ServiceAccountCredentials(email=None, key_file=service_account_path)
                ee.Initialize(credentials, project=project_id)
            else:
                ee.Authenticate()
                ee.Initialize(project=project_id)
            
            self.initialized = True
            
            test_image = ee.Image('LANDSAT/LC08/C02/T1_L2/LC08_044034_20140318')
            test_image.getInfo()
            
        except Exception as e:
            logger.error(f"Failed to initialize Earth Engine: {e}")
            self.initialized = False
            raise e
    
    def is_initialized(self) -> bool:
        return self.initialized
    
    async def execute_query(self, earth_engine_code: str) -> Dict[str, Any]:
        if not self.initialized:
            return {
                'success': False, 
                'error': 'Earth Engine not initialized'
            }
        
        try:
            result = await self._parse_and_execute_code(earth_engine_code)
            
            return {
                'success': True,
                'description': result.get('description', 'Query executed successfully'),
                'map_data': result.get('map_data', {})
            }
            
        except Exception as e:
            logger.error(f"Error executing Earth Engine query: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _parse_and_execute_code(self, code: str) -> Dict[str, Any]:
        if 'NOAA/DMSP-OLS/NIGHTTIME_LIGHTS' in code:
            return await self._execute_nighttime_lights_query()
        elif 'LANDSAT' in code or 'deforestation' in code.lower():
            return await self._execute_landsat_query()
        elif 'COPERNICUS/S2' in code:
            return await self._execute_sentinel2_query()
        else:
            return await self._execute_generic_query(code)
    
    async def _execute_nighttime_lights_query(self) -> Dict[str, Any]:
        def run_query():
            try:
                collection = ee.ImageCollection('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS')
                
                def create_time_band(img):
                    year = ee.Date(img.get('system:time_start')).get('year').subtract(1991)
                    return ee.Image(year).byte().addBands(img)
                
                collection_with_time = collection.select('stable_lights').map(create_time_band)
                linear_fit = collection_with_time.reduce(ee.Reducer.linearFit())
                
                vis_params = {
                    'min': [0, -20], 
                    'max': [0.18, 20], 
                    'bands': ['scale', 'offset']
                }
                
                map_id = linear_fit.getMapId(vis_params)
                
                return {
                    'description': 'Night-time lights trend analysis showing changes from 1992-2013',
                    'map_data': {
                        'mapid': map_id['mapid'],
                        'token': map_id['token'],
                        'vis_params': vis_params,
                        'layer_name': 'stable lights trend'
                    }
                }
                
            except Exception as e:
                logger.error(f"Error in nighttime lights query: {e}")
                raise e
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, run_query)
    
    async def _execute_landsat_query(self) -> Dict[str, Any]:
        def run_query():
            try:
                image = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
                    .filterDate('2023-01-01', '2023-12-31') \
                    .median()
                
                ndvi = image.normalizedDifference(['SR_B5', 'SR_B4'])
                
                vis_params = {
                    'min': -0.2,
                    'max': 0.8,
                    'palette': ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163',
                              '99B718', '74A901', '66A000', '529400', '3E8601',
                              '207401', '056201', '004C00', '023B01', '012E01',
                              '011D01', '011301']
                }
                
                map_id = ndvi.getMapId(vis_params)
                
                return {
                    'description': 'NDVI analysis using Landsat 8 data for 2023',
                    'map_data': {
                        'mapid': map_id['mapid'],
                        'token': map_id['token'],
                        'vis_params': vis_params,
                        'layer_name': 'NDVI 2023'
                    }
                }
                
            except Exception as e:
                logger.error(f"Error in Landsat query: {e}")
                raise e
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, run_query)
    
    async def _execute_sentinel2_query(self) -> Dict[str, Any]:
        def run_query():
            try:
                collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                    .filterDate('2023-06-01', '2023-08-01') \
                    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                
                median = collection.median()
                
                vis_params = {
                    'min': 0.0,
                    'max': 3000,
                    'bands': ['B4', 'B3', 'B2']
                }
                
                map_id = median.getMapId(vis_params)
                
                return {
                    'description': 'Sentinel-2 RGB composite for summer 2023',
                    'map_data': {
                        'mapid': map_id['mapid'],
                        'token': map_id['token'],
                        'vis_params': vis_params,
                        'layer_name': 'Sentinel-2 RGB'
                    }
                }
                
            except Exception as e:
                logger.error(f"Error in Sentinel-2 query: {e}")
                raise e
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, run_query)
    
    async def _execute_generic_query(self, code: str) -> Dict[str, Any]:
        return {
            'description': f'Earth Engine code generated successfully. Code length: {len(code)} characters.',
            'map_data': {
                'note': 'This would require Earth Engine Code Editor API for full execution',
                'generated_code': code[:500] + '...' if len(code) > 500 else code
            }
        }