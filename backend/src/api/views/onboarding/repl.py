import os
import tempfile
import subprocess
import json
from typing import TypedDict, Dict, List, Optional

class REPLResult(TypedDict):
    status: str
    logs: List[str]
    error: Optional[str]
    output: Optional[str]

class MLBPythonREPL:
    def __init__(self, timeout: int = 8):
        self.timeout = timeout
        
    async def __call__(self, code: str) -> REPLResult:
        """
        Execute Python code and return structured result matching the MLB agent's expected format.
        
        Args:
            code (str): Python code to execute
            
        Returns:
            REPLResult containing:
                status: "success" or "error"
                logs: List of captured print/logging outputs
                error: Error message if execution failed
                output: Final expression result if execution succeeded
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create temp file for code execution
            code_file_path = os.path.join(temp_dir, "mlb_analysis.py")
            
            # Create wrapped code that handles execution and output capture
            wrapped_code = f"""
import sys
import io
import json

# Capture stdout
captured_output = io.StringIO()
sys.stdout = captured_output

try:
    # Execute the provided code
{code}

    # Get captured output
    sys.stdout = sys.__stdout__
    logs = captured_output.getvalue().strip().split('\\n')
    
    # The last print statement's output will be our result
    result = logs[-1] if logs else None
    logs = logs[:-1] if logs else []
    
    # Return success result
    print(json.dumps({{
        "status": "success",
        "logs": logs,
        "error": None,
        "output": result
    }}))

except Exception as e:
    # Get captured output up to error
    sys.stdout = sys.__stdout__
    logs = captured_output.getvalue().strip().split('\\n')
    
    # Return error result
    print(json.dumps({{
        "status": "error",
        "logs": logs,
        "error": str(e),
        "output": None
    }}))
"""
            # Write the wrapped code to temp file
            with open(code_file_path, "w", encoding="utf-8") as f:
                f.write(wrapped_code)
            
            try:
                # Execute the code
                result = subprocess.run(
                    ["python3", code_file_path],
                    capture_output=True,
                    check=False,
                    text=True,
                    timeout=self.timeout,
                )
                
                # Parse the JSON result
                if result.returncode == 0:
                    try:
                        return json.loads(result.stdout.strip())
                    except json.JSONDecodeError:
                        return {
                            "status": "error",
                            "logs": [],
                            "error": "Failed to parse execution result",
                            "output": None
                        }
                else:
                    # Clean up error message
                    error_lines = result.stderr.split("\n")
                    cleaned_errors = [
                        line.replace(code_file_path, "<analysis>")
                        for line in error_lines
                    ]
                    error_msg = "\n".join(cleaned_errors)
                    
                    return {
                        "status": "error",
                        "logs": [],
                        "error": error_msg,
                        "output": None
                    }
                    
            except subprocess.TimeoutExpired:
                return {
                    "status": "error",
                    "logs": [],
                    "error": f"Execution timed out after {self.timeout} seconds",
                    "output": None
                }