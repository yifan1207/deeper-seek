# Deeper Seek
## Semantic File Search and Enhanced Geospatial Query Interface

Deeper Seek now features an enhanced **Google Earth Engine integration** that converts natural language queries into executable Earth Engine code using OpenAI, with real-time visualization capabilities.

## ✨ New Features

### 🌍 Earth Engine Query Interface
- **Natural Language to Code**: Convert queries like "Show me deforestation in the Amazon from 2020-2023" into executable Earth Engine JavaScript
- **Real-time Visualization**: Generated Earth Engine maps and analysis results
- **Interactive Examples**: Pre-built query templates for common use cases
- **Code Generation**: View the generated Earth Engine code for learning and customization

### 🗺️ Enhanced Mapping
- **Dynamic Layer Management**: Add/remove Earth Engine layers dynamically
- **Multi-source Integration**: Supports Landsat, Sentinel-2, MODIS, and more
- **Visualization Controls**: Custom styling and visualization parameters
- **Regional Focus**: Automatic map centering for specific regions (Amazon, Brazil, USA, Global)

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- OpenAI API Key
- Google Earth Engine Account (for full functionality)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/deeper-seek.git
   cd deeper-seek
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Set up environment variables:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/ee-service-account.json"
   ```

4. Start the FastAPI server:
   ```bash
   source .venv/bin/activate
   python server.py
   ```

5. Open your browser to `http://localhost:8000`

## 🎯 Example Queries

Try these natural language queries in the interface:

- **"Show me night-time lights trend over time"** → Generates DMSP-OLS time series analysis
- **"Deforestation in the Amazon from 2020-2023"** → Creates NDVI change detection using Landsat
- **"NDVI analysis using Landsat data for 2023"** → Builds vegetation health visualization  
- **"Sentinel-2 RGB composite for summer 2023"** → Creates cloud-free satellite imagery

## 🏗️ Architecture

### Backend Components
- **`server.py`**: FastAPI server with Earth Engine endpoints
- **`openai_query_converter.py`**: Natural language to Earth Engine code conversion
- **`earth_engine_handler.py`**: Earth Engine API integration and execution
- **`test_server.py`**: Test suite for API functionality

### Frontend Components  
- **`frontend_old/geoguessr.html`**: Enhanced web interface with Earth Engine query panel
- **`frontend_old/geospatial.js`**: Extended Earth Engine visualization and layer management

## 📊 API Reference

### POST `/submit_query`
Converts natural language to Earth Engine code and executes analysis.

**Request:**
```json
{
  "query": "Show me deforestation in Brazil from 2020-2023"
}
```

**Response:**
```json
{
  "success": true,
  "response": "NDVI analysis using Landsat 8 data for 2023",
  "earth_engine_code": "var collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')...",
  "map_data": {
    "mapid": "...",
    "token": "...",
    "layer_name": "NDVI 2023",
    "vis_params": {...}
  }
}
```

## 🔧 Configuration

### Google Earth Engine Setup
1. Create a [Google Earth Engine](https://earthengine.google.com/) account
2. Set up a [service account](https://developers.google.com/earth-engine/guides/service_account)
3. Download the JSON key file
4. Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

### OpenAI Setup
1. Get an [OpenAI API key](https://platform.openai.com/api-keys)
2. Set `OPENAI_API_KEY` environment variable
3. Configure model settings in `openai_query_converter.py`

## 🧪 Testing

Run the test suite:
```bash
source .venv/bin/activate
python test_server.py
```

This tests:
- OpenAI query conversion
- Earth Engine handler initialization  
- API response formatting

## 🗺️ Data Sources

The system supports these Earth Engine datasets:
- **Landsat**: `LANDSAT/LC08/C02/T1_L2` (Surface Reflectance)
- **Sentinel-2**: `COPERNICUS/S2_SR_HARMONIZED`
- **MODIS**: `MODIS/006/MCD12Q1`, `MODIS/006/MOD13A1`
- **Night Lights**: `NOAA/DMSP-OLS/NIGHTTIME_LIGHTS`
- **Population**: `WorldPop/GP/100m/pop`
- **Climate**: `ECMWF/ERA5/MONTHLY`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Earth Engine** - Geospatial analysis platform
- **OpenAI** - Natural language processing
- **FastAPI** - Modern web framework
- **Leaflet** - Interactive mapping library
