#!/usr/bin/env python3
"""
FastAPI backend server for Deeper Seek with OpenAI integration.
Handles natural language to Earth Engine code conversion.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
import os
import json
import re

app = FastAPI(title="Deeper Seek API", description="AI-Powered Geospatial Analysis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
)

class QueryRequest(BaseModel):
    query: str
    type: str = "earth_engine"
    image_path: Optional[str] = None
    full_image_path: Optional[str] = None
    lobby_id: Optional[str] = None

class QueryResponse(BaseModel):
    success: bool
    earth_engine_code: Optional[str] = None
    response: Optional[str] = None
    error: Optional[str] = None
    query: Optional[str] = None
    type: Optional[str] = None

@app.get("/")
async def index():
    return FileResponse("frontend_old/geoguessr.html")

@app.get("/{filename:path}")
async def serve_static(filename: str):
    import os
    file_path = f"frontend_old/{filename}"
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.post("/submit_query", response_model=QueryResponse)
async def submit_query(request: QueryRequest):
    try:
        if request.type == 'earth_engine':
            return await handle_earth_engine_query(request.query)
        else:
            return await handle_location_query(request)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def handle_earth_engine_query(query: str) -> QueryResponse:
    """Convert natural language to Earth Engine JavaScript code using OpenAI"""
    
    system_prompt = """You are an expert Google Earth Engine JavaScript developer. Convert natural language queries into valid Earth Engine JavaScript code that can be executed in a web browser.

Rules:
1. Return ONLY executable JavaScript code, no explanations
2. Use ee.ImageCollection, ee.Image, ee.Geometry, etc. as needed
3. Always include Map.addLayer() to visualize results
4. Use appropriate visualization parameters (min, max, palette)
5. Handle common datasets like Landsat, Sentinel, MODIS, etc.
6. For trend analysis, use ee.Reducer.linearFit() like the example
7. Always end with Map.centerObject() if creating geometry
8. Use earthEngineMap instead of Map for adding layers
9. Clear existing layers first with earthEngineMap.layers().reset()

Example patterns:
- Night-time lights trend: Use NOAA/DMSP-OLS/NIGHTTIME_LIGHTS with linearFit
- Vegetation: Use MODIS/006/MOD13A2 NDVI
- Land cover: Use COPERNICUS/Landcover/100m/Proba-V-C3
- Water detection: Use JRC/GSW1_4/GlobalSurfaceWater
- Temperature: Use MODIS/006/MOD11A1 LST_Day_1km

Return code that will execute without errors."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        ee_code = response.choices[0].message.content.strip()
        
        ee_code = re.sub(r'^```javascript\s*', '', ee_code)
        ee_code = re.sub(r'^```\s*', '', ee_code)
        ee_code = re.sub(r'\s*```$', '', ee_code)
        
        return QueryResponse(
            success=True,
            earth_engine_code=ee_code,
            query=query
        )
        
    except Exception as e:
        return QueryResponse(
            success=False,
            error=f'OpenAI API error: {str(e)}'
        )

async def handle_location_query(request: QueryRequest) -> QueryResponse:
    """Handle location-based queries (existing functionality)"""
    return QueryResponse(
        success=True,
        response=f'Location query received: {request.query}',
        type='location'
    )

if __name__ == '__main__':
    import uvicorn
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key as an environment variable.")
        print("Contact the developer for the API key.")
        exit(1)
    
    client.api_key = os.getenv("OPENAI_API_KEY")
    uvicorn.run(app, host="0.0.0.0", port=5000)
