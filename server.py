from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import logging
from typing import Optional
from dotenv import load_dotenv

from openai_query_converter import OpenAIQueryConverter
from earth_engine_handler import EarthEngineHandler

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Earth Engine Query API", version="1.0.0")

openai_converter = OpenAIQueryConverter()
ee_handler = EarthEngineHandler()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    earth_engine_code: Optional[str] = None
    map_data: Optional[dict] = None

@app.on_event("startup")
async def startup_event():
    try:
        await ee_handler.initialize()
        logger.info("Earth Engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Earth Engine: {e}")

@app.post("/submit_query", response_model=QueryResponse)
async def submit_query(query_request: QueryRequest):
    try:
        logger.info(f"Processing query: {query_request.query}")
        
        ee_code = await openai_converter.convert_query_to_code(query_request.query)
        
        if not ee_code:
            return QueryResponse(
                success=False,
                error="Failed to generate Earth Engine code from query"
            )
        
        logger.info(f"Generated Earth Engine code: {ee_code[:200]}...")
        
        result = await ee_handler.execute_query(ee_code)
        
        if not result.get('success'):
            return QueryResponse(
                success=False,
                error=f"Earth Engine execution failed: {result.get('error')}",
                earth_engine_code=ee_code
            )
        
        return QueryResponse(
            success=True,
            response=result.get('description', 'Query executed successfully'),
            earth_engine_code=ee_code,
            map_data=result.get('map_data')
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return QueryResponse(
            success=False,
            error=f"Internal server error: {str(e)}"
        )

@app.get("/")
async def root():
    return FileResponse("/Users/Yifan/deeper-seek/frontend/index.html")

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "earth_engine": ee_handler.is_initialized()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")