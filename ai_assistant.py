#!/usr/bin/env python3
"""
Main AI Assistant
Core orchestration system for AI-powered development assistance
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import manager classes using importlib to avoid path issues
import importlib.util

def load_manager_class(script_name: str, class_name: str):
    """Load a class from a script file"""
    script_path = Path(__file__).parent / "scripts" / script_name
    spec = importlib.util.spec_from_file_location(class_name, script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {script_name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)

# Load the manager classes
try:
    SessionManager = load_manager_class("session_manager.py", "SessionManager")
    OpenCodeManager = load_manager_class("opencode_manager.py", "OpenCodeManager")
except Exception as e:
    print(f"Failed to load manager classes: {e}")
    sys.exit(1)


class AIAssistant:
    """Main AI Assistant orchestrator"""
    
    def __init__(self):
        self.base_dir = Path("/home/kent/Assistant")
        self.scripts_dir = self.base_dir / "scripts"
        self.sessions_dir = self.base_dir / "sessions"
        
        # Initialize managers
        self.session_manager = SessionManager()
        self.opencode_manager = OpenCodeManager()
        
        # Setup logging
        self._setup_logging()
        
        # AI Assistant state
        self.current_task = None
        self.context = {}
        self.child_processes = {}
        
    def _setup_logging(self):
        """Setup logging configuration"""
        log_file = self.base_dir / "ai_assistant.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("AIAssistant")
    
    async def start_session(self) -> Dict[str, Any]:
        """Start new AI assistant session with context restoration"""
        self.logger.info("Starting AI Assistant session")
        
        # Restore context from session manager
        context_output = self.session_manager.start_new_session()
        if isinstance(context_output, str):
            # Parse the markdown context to extract structured information
            self.context = {
                "session_context": context_output,
                "restored_at": datetime.now().isoformat(),
                "has_previous_sessions": "No previous session found" not in context_output
            }
        else:
            self.context = context_output
        
        # Ensure OpenCode is running
        if not self.opencode_manager.is_service_running():
            self.opencode_manager.start()
        
        return {
            "status": "ready",
            "context": self.context,
            "timestamp": datetime.now().isoformat()
        }
    
    async def consult_opencode(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Consult OpenCode for development assistance"""
        self.logger.info(f"Consulting OpenCode: {prompt[:100]}...")
        
        try:
            # Prepare consultation context
            consultation_context = {
                "prompt": prompt,
                "current_task": self.current_task,
                "session_context": context or self.context,
                "working_directory": str(self.base_dir)
            }
            
            # Use opencode_manager to get consultation
            result = self.opencode_manager.consult_opencode(prompt, timeout_minutes=10)
            
            return {
                "status": "success",
                "response": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"OpenCode consultation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def execute_script(self, script_name: str, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute a child script with proper error handling"""
        self.logger.info(f"Executing script: {script_name}")
        
        script_path = self.scripts_dir / script_name
        if not script_path.exists():
            return {
                "status": "error",
                "error": f"Script not found: {script_name}",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Prepare command
            cmd = ["python3", str(script_path)]
            if args:
                cmd.extend(args)
            
            # Execute script
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.base_dir
            )
            
            self.child_processes[script_name] = process
            
            stdout, stderr = await process.communicate()
            
            # Clean up process tracking
            if script_name in self.child_processes:
                del self.child_processes[script_name]
            
            return {
                "status": "success" if process.returncode == 0 else "error",
                "returncode": process.returncode,
                "stdout": stdout.decode().strip(),
                "stderr": stderr.decode().strip(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Script execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def set_task(self, task_description: str) -> Dict[str, Any]:
        """Set current task and update context"""
        self.current_task = task_description
        self.context["current_task"] = task_description
        self.context["task_start_time"] = datetime.now().isoformat()
        
        self.logger.info(f"Task set: {task_description}")
        
        return {
            "status": "success",
            "task": task_description,
            "timestamp": datetime.now().isoformat()
        }
    
    async def complete_task(self, accomplishments: str, next_steps: str = "") -> Dict[str, Any]:
        """Complete current task and update session"""
        if not self.current_task:
            return {
                "status": "error",
                "error": "No active task to complete",
                "timestamp": datetime.now().isoformat()
            }
        
        # Save session completion
        session_id = self.session_manager.save_session_finish(
            accomplishments=accomplishments,
            current_state=f"Completed task: {self.current_task}",
            next_steps=next_steps,
            notes=f"Task completed at {datetime.now().isoformat()}"
        )
        
        # Clear current task
        completed_task = self.current_task
        self.current_task = None
        
        self.logger.info(f"Task completed: {completed_task}")
        
        return {
            "status": "success",
            "completed_task": completed_task,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current AI assistant status"""
        return {
            "status": "active",
            "current_task": self.current_task,
            "opencode_running": self.opencode_manager.is_service_running(),
            "active_processes": list(self.child_processes.keys()),
            "context_keys": list(self.context.keys()),
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self) -> Dict[str, Any]:
        """Gracefully shutdown AI assistant"""
        self.logger.info("Shutting down AI Assistant")
        
        # Terminate child processes
        for name, process in self.child_processes.items():
            try:
                process.terminate()
                await process.wait()
                self.logger.info(f"Terminated process: {name}")
            except Exception as e:
                self.logger.error(f"Failed to terminate process {name}: {e}")
        
        # Save final session if there's an active task
        if self.current_task:
            await self.complete_task(
                "AI Assistant shutdown",
                "Resume task on next startup"
            )
        
        return {
            "status": "shutdown",
            "timestamp": datetime.now().isoformat()
        }


async def main():
    """Main entry point for AI Assistant"""
    assistant = AIAssistant()
    
    try:
        # Start session
        await assistant.start_session()
        
        # Example usage - this would be replaced with actual interaction logic
        print("AI Assistant started successfully")
        status = await assistant.get_status()
        print(f"Status: {json.dumps(status, indent=2)}")
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        await assistant.shutdown()
    except Exception as e:
        print(f"Error: {e}")
        await assistant.shutdown()


if __name__ == "__main__":
    asyncio.run(main())