# AI Assistant Project Configuration

## Build/Lint/Test Commands
* Build Command: python -m py_compile scripts/*.py ai_assistant.py
* Lint Command: python -m flake8 scripts/ tests/ *.py --max-line-length=100
* Test Command: python -m pytest tests/ -v

## Code Style Guidelines
* 4 space indentation (PEP 8)
* Use import statements at the top of files
* Use async/await for asynchronous operations
* Error handling: try/except blocks
* Naming conventions: snake_case for variables and functions, PascalCase for classes
* Follow PEP 8 style guide

## Project Architecture

### Core Components
* **ai_assistant.py** - Main AI assistant orchestrator with async operations
* **scripts/session_manager.py** - Session persistence and context restoration
* **scripts/opencode_manager.py** - OpenCode service control and consultation
* **sessions/** - Session storage (JSON + markdown formats)

### AI Assistant Capabilities
* **Session Management** - Automatic context restoration via `/start` and `/finish`
* **OpenCode Consultation** - On-demand AI code assistance via `consult_opencode()`
* **Script Orchestration** - Execute and manage child scripts via `execute_script()`
* **Memory Management** - Rolling cumulative recap system prevents bloat
* **Task Tracking** - Set/complete tasks with automatic session saving

### Session Management Commands
* `/finish` - Save session context and clear memory
* `/start` - Restore context and resume work
* `quick-finish` - Non-interactive session saving

### Project Structure
```
Assistant/
├── ai_assistant.py           # Main AI assistant
├── scripts/
│   ├── session_manager.py    # Session persistence
│   ├── opencode_manager.py   # OpenCode control
│   └── node_red_control.py   # NodeRED automation
├── sessions/                 # Session storage
├── tests/                   # Unit tests
├── .opencode/command/       # Command definitions
└── AGENTS.md               # This file
```

## Development Notes
* **AI-Powered Development** - Uses OpenCode for intelligent code assistance
* **Memory Persistence** - Session manager maintains context across restarts
* **Async Architecture** - All operations are asynchronous for performance
* **Service Integration** - Controls OpenCode service on-demand
* **Home Automation Context** - Designed for Kent's home automation needs
* **Security Constraints** - Never modify .node-red without explicit permission

## Environment Setup
* OpenCode service configured for `/home/kent/Assistant`
* All scripts executable with proper error handling
* Environment variables in `.env` (Kent's preference)
* Git repository with proper .gitignore for sensitive files

## Critical Safety Notes
* **Medication Refrigerator** - Plug safety is critical
* **NodeRED Protection** - Never modify .node-red without permission
* **API Keys** - All stored in .env file per Kent's preference
* **Direct Communication** - Kent prefers direct responses, not sycophancy