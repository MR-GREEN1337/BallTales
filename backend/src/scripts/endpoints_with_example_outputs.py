"""MLB API Response Schema Extractor

This script executes MLB API endpoints and extracts response schemas for documentation
and analysis purposes. It handles multiple response types (JSON, images, raw data) and
provides detailed execution metrics.
"""
from pathlib import Path
import aiohttp
import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CONSTANTS_DIR = SCRIPT_DIR.parent / 'core' / 'constants'

class EndpointResponse:
    def __init__(self, 
                 status: int,
                 content_type: str,
                 data: Union[Dict, bytes, str],
                 url: str):
        self.status = status
        self.content_type = content_type
        self.data = data
        self.url = url

    def is_success(self) -> bool:
        return 200 <= self.status < 300

    def is_json(self) -> bool:
        return 'application/json' in self.content_type.lower()

    def is_image(self) -> bool:
        return 'image' in self.content_type.lower()

    def to_schema(self) -> Dict:
        if self.is_json():
            return {
                "type": "json",
                "schema": SchemaExtractor.extract_schema(self.data),
                "content_type": self.content_type
            }
        elif self.is_image():
            return {
                "type": "image",
                "content_type": self.content_type,
                "size_bytes": len(self.data) if isinstance(self.data, bytes) else len(str(self.data))
            }
        else:
            return {
                "type": "raw",
                "content_type": self.content_type,
                "sample": str(self.data)[:100] if self.data else None
            }

class SchemaExtractor:
    @staticmethod
    def extract_schema(data: Any, max_depth: int = 3) -> Dict:
        if max_depth <= 0:
            return {"type": type(data).__name__}
            
        if isinstance(data, dict):
            schema = {}
            for key, value in data.items():
                schema[key] = SchemaExtractor.extract_schema(value, max_depth - 1)
            return {"type": "object", "properties": schema}
            
        elif isinstance(data, list):
            if data:
                item_schema = SchemaExtractor.extract_schema(data[0], max_depth - 1)
                return {
                    "type": "array",
                    "items": item_schema,
                    "example_length": len(data)
                }
            return {"type": "array", "items": {}}
            
        else:
            return {
                "type": type(data).__name__,
                "example": str(data)[:100] if data is not None else None
            }

class MLBAPIExecutor:
    def __init__(self, batch_size: int = 5, timeout: int = 10, delay: float = 0.5):
        self.batch_size = batch_size
        self.timeout = timeout
        self.delay = delay
        self.default_params = {
            'playerId': '671096',
            'teamId': '137',
            'sportId': '1',
            'season': '2023',
            'leagueId': '103',
            'gamePk': '715705',
            'personId': '671096',
            'fields': 'people,id,fullName',
            'group': 'hitting',
            'stats': 'season',
            'leaderCategories': 'homeRuns',
            'venueIds': '1',
            'divisionId': '200'
        }
        self.session = None
        self.results = defaultdict(dict)
        self.status_counts = defaultdict(int)

    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={'User-Agent': 'MLBAPIExplorer/1.0'}
            )

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    def prepare_url(self, endpoint_data: Dict[str, Any]) -> str:
        url = endpoint_data['url']
        # Handle placeholder parameters in URL
        for param, value in self.default_params.items():
            placeholder = f"{{{param}}}"
            if placeholder in url:
                url = url.replace(placeholder, str(value))
        return url

    def prepare_params(self, endpoint_data: Dict[str, Any]) -> Dict[str, str]:
        params = {}
        if 'required_params' in endpoint_data:
            for param in endpoint_data['required_params']:
                if param in self.default_params:
                    params[param] = self.default_params[param]
        return params

    async def fetch_endpoint(self, url: str, params: Dict[str, str]) -> EndpointResponse:
        async with self.session.get(url, params=params) as response:
            content_type = response.headers.get('Content-Type', '')
            self.status_counts[response.status] += 1

            if response.status == 200:
                if 'json' in content_type.lower():
                    data = await response.json()
                elif 'image' in content_type.lower():
                    data = await response.read()
                else:
                    data = await response.text()
            else:
                data = await response.text()

            return EndpointResponse(
                status=response.status,
                content_type=content_type,
                data=data,
                url=str(response.url)
            )

    async def execute_endpoint(self, name: str, endpoint_data: Dict[str, Any]) -> Dict[str, Any]:
        url = self.prepare_url(endpoint_data)
        params = self.prepare_params(endpoint_data)
        
        try:
            response = await self.fetch_endpoint(url, params)
            
            if response.is_success():
                return response.to_schema()
            else:
                return {
                    "error": f"HTTP {response.status}",
                    "url": response.url,
                    "content_type": response.content_type
                }
                
        except Exception as e:
            logger.error(f"Error executing {name}: {str(e)}")
            return {"error": str(e)}

    async def process_batch(self, batch: List[tuple]) -> None:
        tasks = []
        for name, endpoint_data in batch:
            task = asyncio.create_task(self.execute_endpoint(name, endpoint_data))
            tasks.append((name, task))
            await asyncio.sleep(self.delay)

        for name, task in tasks:
            try:
                result = await task
                self.results[name] = {
                    "timestamp": datetime.now().isoformat(),
                    "endpoint": {
                        "url": endpoint_data.get('url'),
                        "description": endpoint_data.get('description'),
                        "required_params": endpoint_data.get('required_params', []),
                        "optional_params": endpoint_data.get('optional_params', [])
                    },
                    "response": result
                }
            except Exception as e:
                logger.error(f"Error processing {name}: {str(e)}")
                self.results[name] = {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }

    async def execute_all(self, endpoints_file: str) -> Dict[str, Any]:
        start_time = time.time()
        
        # Load endpoints
        endpoints_path = CONSTANTS_DIR / endpoints_file
        logger.info(f"Loading endpoints from: {endpoints_path}")
        
        with open(endpoints_path, 'r') as f:
            data = json.load(f)
            endpoints = data['endpoints']

        await self.init_session()
        
        # Process in batches
        batch = []
        total_endpoints = len(endpoints)
        processed = 0
        
        for name, endpoint_data in endpoints.items():
            batch.append((name, endpoint_data))
            
            if len(batch) >= self.batch_size:
                await self.process_batch(batch)
                processed += len(batch)
                logger.info(f"Processed {processed}/{total_endpoints} endpoints")
                batch = []
        
        if batch:
            await self.process_batch(batch)
            processed += len(batch)
            logger.info(f"Processed {processed}/{total_endpoints} endpoints")

        await self.close_session()
        
        # Prepare output
        output = {
            "metadata": {
                "execution_time": time.time() - start_time,
                "total_endpoints": total_endpoints,
                "status_counts": dict(self.status_counts)
            },
            "endpoints": dict(self.results)
        }
        
        # Save results
        output_path = CONSTANTS_DIR / 'mlb_api_responses.json'
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
            
        logger.info(f"Results saved to: {output_path}")
        
        return output

async def main():
    executor = MLBAPIExecutor(
        batch_size=5,
        timeout=10,
        delay=0.5
    )
    await executor.execute_all('endpoints.json')

if __name__ == "__main__":
    asyncio.run(main())