import os
import logging
import subprocess
from typing import Annotated
from langchain_core.tools import tool
from logger import setup_logger
from load_cfg import WORKING_DIRECTORY

# Initialize logger
logger = setup_logger()

# Ensure the storage directory exists
if not os.path.exists(WORKING_DIRECTORY):
    os.makedirs(WORKING_DIRECTORY)
    logger.info(f"Created storage directory: {WORKING_DIRECTORY}")

@tool
def execute_code(
    input_code: Annotated[str, "The Python code to execute."],
    codefile_name: Annotated[str, "The Python code file name or full path."] = 'code.py'
):
    """
    Execute Python code and return the result.

    This function writes the given Python code to a file, executes it using the
    system-installed Python interpreter, and returns the output or any errors encountered.

    Args:
    input_code (str): The Python code to be executed.
    codefile_name (str): The name of the file to save the code in, or the full path.

    Returns:
    dict: A dictionary containing the execution result, output, and file path.
    """
    try:
        # Ensure WORKING_DIRECTORY exists
        os.makedirs(WORKING_DIRECTORY, exist_ok=True)
        
        # Handle codefile_name, ensuring it's a valid path
        if os.path.isabs(codefile_name):
            code_file_path = codefile_name
        else:
            code_file_path = os.path.join(WORKING_DIRECTORY, codefile_name)

        # Normalize the path for the current platform
        code_file_path = os.path.normpath(code_file_path)

        logger.info(f"Code will be written to file: {code_file_path}")
        
        # Write the code to the file with UTF-8 encoding
        with open(code_file_path, 'w', encoding='utf-8') as code_file:
            code_file.write(input_code)
        
        logger.info(f"Code has been written to file: {code_file_path}")
        
        # Execute the code using Python
        command = f"python {code_file_path}"
        logger.info(f"Executing command: {command}")
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=WORKING_DIRECTORY
        )
        
        # Capture standard output and error output
        output = result.stdout
        error_output = result.stderr
        
        if result.returncode == 0:
            logger.info("Code executed successfully")
            return {
                "result": "Code executed successfully",
                "output": output + "\n\nIf you have completed all tasks, respond with FINAL ANSWER.",
                "file_path": code_file_path
            }
        else:
            logger.error(f"Code execution failed: {error_output}")
            return {
                "result": "Failed to execute",
                "error": error_output,
                "file_path": code_file_path
            }
    except Exception as e:
        logger.exception("An error occurred while executing code")
        return {
            "result": "Error occurred",
            "error": str(e),
            "file_path": code_file_path if 'code_file_path' in locals() else "Unknown"
        }

@tool
def execute_command(
    command: Annotated[str, "Command to be executed."]
) -> Annotated[str, "Output of the command."]:
    """
    Execute a command and return its output.

    This function runs the provided command in the default system shell and returns the output.

    Args:
    command (str): The command to be executed.

    Returns:
    str: The output of the command or an error message.
    """
    try:
        logger.info(f"Executing command: {command}")
        
        # Execute the command and capture the output
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=WORKING_DIRECTORY
        )
        
        logger.info("Command executed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing command: {e.stderr}")
        return f"Error: {e.stderr}"

logger.info("Module initialized successfully")
