# Deeper Seek - AI-Powered Earth Engine Setup

## Quick Start

1. **Set your OpenAI API Key:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Start the server:**
   ```bash
   python server.py
   ```

4. **Open your browser:**
   Navigate to `http://localhost:5000`

## Features

- **AI-Powered Earth Engine Queries**: Convert natural language to Earth Engine JavaScript code
- **Real-time Code Generation**: See the generated Earth Engine code before execution
- **Map Visualization**: Execute and visualize Earth Engine results on the map
- **Existing Functionality**: Preserves all existing similarity heatmap features

## Example Queries

- "Show night-time lights trend over the last decade"
- "Display vegetation changes using NDVI"
- "Find areas with water detection"
- "Show land cover classification"
- "Display temperature anomalies"

The AI will convert these natural language queries into proper Google Earth Engine JavaScript code and execute them on the map.

## Configuration

The application requires an OpenAI API key to function. Contact the developer for access to the API key.
