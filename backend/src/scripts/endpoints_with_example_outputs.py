from pathlib import Path
import aiohttp
import asyncio
import json
import time
from typing import Dict, List, Any, Union
from datetime import datetime
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CONSTANTS_DIR = SCRIPT_DIR.parent / "core" / "constants"


class EndpointResponse:
    def __init__(
        self, status: int, content_type: str, data: Union[Dict, bytes, str], url: str
    ):
        self.status = status
        self.content_type = (
            content_type or "application/octet-stream"
        )  # Default content type if none provided
        self.data = data
        self.url = url

    def is_success(self) -> bool:
        return 200 <= self.status < 300

    def is_json(self) -> bool:
        return "application/json" in self.content_type.lower()

    def is_image(self) -> bool:
        return "image" in self.content_type.lower()

    def to_schema(self) -> Dict:
        try:
            if self.is_json():
                return {
                    "type": "json",
                    "schema": SchemaExtractor.extract_schema(self.data),
                    "content_type": self.content_type,
                }
            elif self.is_image():
                return {
                    "type": "image",
                    "content_type": self.content_type,
                    "size_bytes": len(self.data)
                    if isinstance(self.data, bytes)
                    else len(str(self.data)),
                }
            else:
                return {
                    "type": "raw",
                    "content_type": self.content_type,
                    "sample": str(self.data)[:100] if self.data else None,
                }
        except Exception as e:
            logger.error(f"Error in to_schema: {str(e)}")
            return {"type": "error", "error": str(e), "content_type": self.content_type}


class SchemaExtractor:
    @staticmethod
    def extract_schema(data: Any, max_depth: int = 3) -> Dict:
        try:
            if max_depth <= 0:
                return {"type": type(data).__name__}

            if isinstance(data, dict):
                schema = {}
                for key, value in data.items():
                    schema[key] = SchemaExtractor.extract_schema(value, max_depth - 1)
                return {"type": "object", "properties": schema}

            elif isinstance(data, list):
                if data:
                    # Handle multiple items in array to capture variations
                    item_schemas = [
                        SchemaExtractor.extract_schema(item, max_depth - 1)
                        for item in data[:3]
                    ]  # Sample first 3 items
                    return {
                        "type": "array",
                        "items": item_schemas[0]
                        if len(item_schemas) == 1
                        else item_schemas,
                        "example_length": len(data),
                    }
                return {"type": "array", "items": {}}

            else:
                return {
                    "type": type(data).__name__,
                    "example": str(data)[:100] if data is not None else None,
                }
        except Exception as e:
            logger.error(f"Error in extract_schema: {str(e)}")
            return {"type": "error", "error": str(e)}


class MLBAPIExecutor:
    def __init__(
        self,
        batch_size: int = 5,
        timeout: int = 30,
        delay: float = 1.0,
        max_retries: int = 3,
    ):
        self.batch_size = batch_size
        self.timeout = timeout
        self.delay = delay
        self.max_retries = max_retries
        self.default_params = {
            "playerId": "671096",
            "teamId": "137",
            "sportId": "1",
            "season": "2023",
            "leagueId": "103",
            "gamePk": "715705",
            "personId": "671096",
            "fields": "people,id,fullName",
            "group": "hitting",
            "stats": "season",
            "leaderCategories": "homeRuns",
            "venueIds": "1",
            "divisionId": "200",
        }
        self.session = None
        self.results = defaultdict(dict)
        self.status_counts = defaultdict(int)
        self.failed_endpoints = []

    async def init_session(self):
        if not self.session:
            timeout = aiohttp.ClientTimeout(
                total=self.timeout, connect=10, sock_connect=10, sock_read=10
            )
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={"User-Agent": "MLBAPIExplorer/1.0", "Accept": "*/*"},
            )

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    def prepare_url(self, endpoint_data: Dict[str, Any]) -> str:
        url = endpoint_data["url"]
        try:
            # Handle placeholder parameters in URL
            for param, value in self.default_params.items():
                placeholder = f"{{{param}}}"
                if placeholder in url:
                    url = url.replace(placeholder, str(value))
            return url
        except Exception as e:
            logger.error(f"Error preparing URL: {str(e)}")
            raise

    def prepare_params(self, endpoint_data: Dict[str, Any]) -> Dict[str, str]:
        params = {}
        try:
            if "required_params" in endpoint_data:
                for param in endpoint_data["required_params"]:
                    if param in self.default_params:
                        params[param] = self.default_params[param]
            return params
        except Exception as e:
            logger.error(f"Error preparing parameters: {str(e)}")
            return {}

    async def fetch_endpoint(
        self, url: str, params: Dict[str, str], retries: int = 0
    ) -> EndpointResponse:
        try:
            async with self.session.get(url, params=params) as response:
                content_type = response.headers.get("Content-Type", "")
                self.status_counts[response.status] += 1

                if response.status == 200:
                    try:
                        if "json" in content_type.lower():
                            data = await response.json()
                        elif "image" in content_type.lower():
                            data = await response.read()
                        else:
                            data = await response.text()
                    except Exception as e:
                        logger.error(f"Error processing response data: {str(e)}")
                        data = await response.text()
                else:
                    data = await response.text()
                    if response.status >= 500 and retries < self.max_retries:
                        await asyncio.sleep(self.delay * (retries + 1))
                        return await self.fetch_endpoint(url, params, retries + 1)

                return EndpointResponse(
                    status=response.status,
                    content_type=content_type,
                    data=data,
                    url=str(response.url),
                )

        except asyncio.TimeoutError:
            logger.error(f"Timeout error for URL: {url}")
            if retries < self.max_retries:
                await asyncio.sleep(self.delay * (retries + 1))
                return await self.fetch_endpoint(url, params, retries + 1)
            raise

        except Exception as e:
            logger.error(f"Error fetching endpoint {url}: {str(e)}")
            if retries < self.max_retries:
                await asyncio.sleep(self.delay * (retries + 1))
                return await self.fetch_endpoint(url, params, retries + 1)
            raise

    async def execute_endpoint(
        self, name: str, endpoint_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            url = self.prepare_url(endpoint_data)
            params = self.prepare_params(endpoint_data)

            response = await self.fetch_endpoint(url, params)

            if response.is_success():
                schema = response.to_schema()
                if "error" not in schema:
                    return schema
                else:
                    logger.error(
                        f"Schema extraction error for {name}: {schema['error']}"
                    )
                    return {"error": f"Schema extraction failed: {schema['error']}"}
            else:
                error_result = {
                    "error": f"HTTP {response.status}",
                    "url": response.url,
                    "content_type": response.content_type,
                }
                return error_result

        except Exception as e:
            error_msg = f"Error executing {name}: {str(e)}"
            logger.error(error_msg)
            error_result = {"error": error_msg}
            self.failed_endpoints.append((name, error_result))
            return error_result

    async def process_batch(self, batch: List[tuple]) -> None:
        tasks = []
        for name, endpoint_data in batch:
            task = asyncio.create_task(self.execute_endpoint(name, endpoint_data))
            tasks.append((name, task))
            await asyncio.sleep(self.delay)

        for name, task in tasks:
            try:
                result = await task
                if "error" not in result:  # Only add successful responses
                    self.results[name] = {
                        "timestamp": datetime.now().isoformat(),
                        "endpoint": {
                            "url": endpoint_data.get("url"),
                            "description": endpoint_data.get("description"),
                            "required_params": endpoint_data.get("required_params", []),
                            "optional_params": endpoint_data.get("optional_params", []),
                        },
                        "response": result,
                    }
                else:
                    logger.warning(
                        f"Skipping endpoint {name} due to error: {result['error']}"
                    )
                    self.failed_endpoints.append((name, result))
            except Exception as e:
                logger.error(f"Error processing {name}: {str(e)}")
                self.failed_endpoints.append((name, {"error": str(e)}))

    async def execute_all(self, endpoints_file: str) -> Dict[str, Any]:
        start_time = time.time()

        try:
            # Load endpoints
            endpoints_path = CONSTANTS_DIR / endpoints_file
            logger.info(f"Loading endpoints from: {endpoints_path}")

            with open(endpoints_path, "r") as f:
                data = json.load(f)
                endpoints = data["endpoints"]

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

            # Process remaining endpoints
            if batch:
                await self.process_batch(batch)
                processed += len(batch)
                logger.info(f"Processed {processed}/{total_endpoints} endpoints")

            # Log failed endpoints
            if self.failed_endpoints:
                logger.warning(f"Failed endpoints ({len(self.failed_endpoints)}):")
                for name, error in self.failed_endpoints:
                    logger.warning(f"- {name}: {error}")

            await self.close_session()

            # Prepare output
            output = {
                "metadata": {
                    "execution_time": time.time() - start_time,
                    "total_endpoints": total_endpoints,
                    "successful_endpoints": total_endpoints
                    - len(self.failed_endpoints),
                    "failed_endpoints": len(self.failed_endpoints),
                    "status_counts": dict(self.status_counts),
                },
                "endpoints": dict(self.results),
            }

            # Save results
            output_path = CONSTANTS_DIR / "mlb_api_responses.json"
            with open(output_path, "w") as f:
                json.dump(output, f, indent=2)

            logger.info(f"Results saved to: {output_path}")

            return output

        except Exception as e:
            logger.error(f"Error in execute_all: {str(e)}")
            raise


async def main():
    executor = MLBAPIExecutor(batch_size=5, timeout=30, delay=1.0, max_retries=3)
    await executor.execute_all(CONSTANTS_DIR / "endpoints.json")


if __name__ == "__main__":
    asyncio.run(main())
