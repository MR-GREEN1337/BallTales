import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mlb_docs_parser.log'),
        logging.StreamHandler()
    ]
)

class MLBDocsParser:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    async def parse_function_doc(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Parse a single function documentation file using Gemini."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logging.info(f"Processing file: {filepath}")
            
            # Split content into chunks if too large
            prompt = f"""
            Parse this MLB StatsAPI function documentation and return a structured JSON object.
            
            Documentation content:
            {content}
            
            Return a valid JSON object with this exact structure:
            {{
                "name": "function_name",
                "description": "main description",
                "signature": "full function signature if present, otherwise null",
                "parameters": [
                    {{
                        "name": "param_name",
                        "type": "param_type (e.g. str, int, List[str], Optional[int], etc)",
                        "default": "default_value if any, otherwise null",
                        "description": "parameter description if found, otherwise null"
                    }}
                ],
                "return_value": {{
                    "type": "return type (e.g. List[Dict], str, etc)",
                    "description": "description of what the function returns"
                }},
                "notes": ["note1", "note2"]
            }}
            
            IMPORTANT:
            - Return VALID JSON only
            - If a field is not found in the documentation, use null
            - Use Python type hints format for types
            - Include all notes found in the documentation
            """

            result = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    response_mime_type="application/json"
                )
            )
            
            try:
                parsed = json.loads(result.text)
                logging.info(f"Successfully parsed {filepath}")
                return parsed
            except json.JSONDecodeError as e:
                logging.error(f"Invalid JSON from model for {filepath}: {str(e)}")
                logging.error(f"Model output: {result.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error processing {filepath}: {str(e)}", exc_info=True)
            return None

    async def process_all_docs(self, docs_dir: str) -> Dict[str, Any]:
        """Process all markdown files in the directory."""
        md_files = sorted(Path(docs_dir).glob("Function:-*.md"))
        total_files = len(list(md_files))
        
        logging.info(f"Found {total_files} markdown files to process")
        
        all_functions = []
        failed_files = []
        
        for file_path in sorted(Path(docs_dir).glob("Function:-*.md")):
            try:
                function_info = await self.parse_function_doc(str(file_path))
                if function_info:
                    all_functions.append(function_info)
                    logging.info(f"✓ Processed {file_path.name}")
                else:
                    failed_files.append(file_path.name)
                    logging.warning(f"✗ Failed to process {file_path.name}")
            except Exception as e:
                failed_files.append(file_path.name)
                logging.error(f"Error processing {file_path.name}: {str(e)}", exc_info=True)
        
        result = {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "total_files_found": total_files,
            "successfully_processed": len(all_functions),
            "failed_files": failed_files,
            "functions": all_functions,
            "type_mappings": {
                "common_types": {
                    "GameID": "str",
                    "PlayerID": "int",
                    "TeamID": "int",
                    "Date": "str (YYYY-MM-DD)",
                    "Season": "int",
                    "LeagueID": "int"
                }
            }
        }
        
        return result

async def main():
    try:
        # Set your Gemini API key
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Please set GEMINI_API_KEY environment variable")
        
        # Initialize parser
        parser = MLBDocsParser(api_key)
        
        # Path to your function docs
        docs_dir = "backend/src/core/constants/functions-wiki"
        
        # Make sure directory exists
        if not os.path.exists(docs_dir):
            raise ValueError(f"Documentation directory not found: {docs_dir}")
        
        # Process all documentation
        result = await parser.process_all_docs(docs_dir)
        
        # Save output
        output_path = "backend/src/core/constants/mlb_functions.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        print("\nProcessing Summary:")
        print(f"Total files found: {result['total_files_found']}")
        print(f"Successfully processed: {result['successfully_processed']}")
        print(f"Failed files: {len(result['failed_files'])}")
        if result['failed_files']:
            print("\nFailed files:")
            for file in result['failed_files']:
                print(f"  - {file}")
        print(f"\nOutput saved to: {output_path}")
        print("Check mlb_docs_parser.log for detailed processing information")

    except Exception as e:
        logging.error("Fatal error in main:", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())