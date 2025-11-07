#!/usr/bin/env python3
"""
OpenCode Custom Commands
Adds /finish and /start commands to OpenCode sessions
"""

import subprocess
import sys
import os
from pathlib import Path

def run_finish_command():
    """Handle /finish command"""
    print("🏁 Finishing session...")
    
    # Save session context
    session_manager = "/home/kent/Assistant/scripts/session_manager.py"
    
    # Get session info interactively
    print("\n📋 Session Summary:")
    print("Let me help you document what we accomplished...")
    
    # For now, use quick-finish with predefined content
    # In future, this could be more interactive
    accomplishments = """
✅ **Phase 1: Memory Management Solution - COMPLETE**
- Created opencode_manager.py for on-demand service control
- Implemented start/stop/consult functionality  
- Tested memory clearing works perfectly
- AI assistant can now call OpenCode without memory accumulation

✅ **Phase 2: Git/GitHub Setup - IN PROGRESS**
- Git installed and configured
- Local repository initialized with initial commit
- GitHub CLI installed (authentication pending)
- Session management system created

✅ **Session Persistence System - COMPLETE**
- Created session_manager.py for context persistence
- Built /finish and /start command infrastructure
- Designed system for AI assistant future automation
"""
    
    current_state = """
📊 **Current Project State:**
- Working directory: /home/kent/Assistant
- Git repository initialized with initial commit
- OpenCode service configured to start in /Assistant directory
- Memory management solution operational
- Session persistence system ready for testing
- GitHub authentication pending (code: 334B-DFA8)

🔧 **Technical Infrastructure:**
- opencode_manager.py: Service control and memory management
- session_manager.py: Session persistence and context restoration
- Git repository with proper .gitignore
- All scripts executable and tested
"""
    
    next_steps = """
🚀 **Immediate Next Steps:**
1. **Complete GitHub Authentication**
   - Go to: https://github.com/login/device
   - Enter code: 334B-DFA8
   - Create kentstillman/ai-assistant repository

2. **Test Session Persistence**
   - Run /finish to save this session
   - Restart opencode service (clear memory)
   - Run /start in new session to verify context restoration

3. **Phase 3: Core AI Architecture**
   - Design main AI assistant script
   - Build consultation mechanisms with OpenCode
   - Create child script orchestration system

4. **Update AGENTS.md**
   - Compile knowledge base into compact format
   - Add session management commands
   - Include project context and constraints
"""
    
    notes = """
💡 **Key Insights:**
- On-demand OpenCode consultation solves memory issue perfectly
- Session persistence prototypes future AI memory management
- Manual process now will become automated AI behavior
- Project is more sophisticated than initially understood
- Kent wants direct communication, not sycophancy
- Safety critical: medication refrigerator plug, .node-red protection

🔒 **Security Notes:**
- Never touch .node-red without explicit permission
- All API keys in .env (Kent's preference)
- Git excludes sensitive files properly
"""
    
    # Save the session
    result = subprocess.run([
        "python3", session_manager, "quick-finish",
        accomplishments, current_state, next_steps, notes
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Session saved successfully!")
        print(result.stdout)
        
        # Restart OpenCode service to clear memory
        print("\n🔄 Restarting OpenCode service to clear memory...")
        restart_result = subprocess.run([
            "python3", "/home/kent/Assistant/scripts/opencode_manager.py", "restart"
        ], capture_output=True, text=True)
        
        if restart_result.returncode == 0:
            print("✅ Memory cleared - service restarted")
            print("\n👋 Session complete! Start new CLI session and use /start")
            print("\n/finish complete, okay to close the CLI window ...")
        else:
            print("❌ Service restart failed")
            print(restart_result.stderr)
    else:
        print("❌ Failed to save session")
        print(result.stderr)

def run_start_command():
    """Handle /start command"""
    print("🚀 Starting new session...")
    
    session_manager = "/home/kent/Assistant/scripts/session_manager.py"
    result = subprocess.run(["python3", session_manager, "start"], 
                         capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print("❌ Failed to load session context")
        print(result.stderr)

def main():
    """Command router"""
    if len(sys.argv) < 2:
        print("Usage: python opencode_commands.py <finish|start>")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "finish":
        run_finish_command()
    elif command == "start":
        run_start_command()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()