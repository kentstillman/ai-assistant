# Assistant Project Configuration

## Build/Lint/Test Commands
* Build Command: python -m py_compile scripts/*.py
* Lint Command: python -m flake8 scripts/ tests/ --max-line-length=100
* Test Command: python -m pytest tests/ -v

## Code Style Guidelines
* 4 space indentation (PEP 8)
* Use import statements at the top of files
* Use async/await for asynchronous operations
* Error handling: try/except blocks
* Naming conventions: snake_case for variables and functions, PascalCase for classes
* Follow PEP 8 style guide

## Project Structure
* scripts/ - Python scripts for automation and functionality
* tests/ - Unit tests using pytest
* requirements.txt - Python dependencies
* .env - Environment variables (not committed)

## Development Notes
* This is a Python-based home automation project
* Uses Flask for web functionality
* Scripts should be executable and include proper error handling
* Environment variables should be used for configuration