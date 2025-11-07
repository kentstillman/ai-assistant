#!/usr/bin/env python3
"""
Session Manager for OpenCode
Handles session persistence and context restoration
"""

import os
import json
from datetime import datetime
from pathlib import Path

class SessionManager:
    def __init__(self):
        self.sessions_dir = Path("/home/kent/Assistant/sessions")
        self.current_session_file = self.sessions_dir / "current_session.json"
        self.env_file = Path("/home/kent/Assistant/.env")
        
        # Ensure sessions directory exists
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def get_current_session_info(self):
        """Get current session information"""
        return {
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": datetime.now().isoformat(),
            "working_directory": os.getcwd(),
            "git_status": self._get_git_status(),
            "opencode_service_status": self._get_opencode_status()
        }
    
    def _get_git_status(self):
        """Get git repository status"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd="/home/kent/Assistant"
            )
            return {
                "has_changes": bool(result.stdout.strip()),
                "status_output": result.stdout.strip()
            }
        except:
            return {"has_changes": False, "status_output": "Git not available"}
    
    def _get_opencode_status(self):
        """Get OpenCode service status"""
        try:
            import subprocess
            result = subprocess.run(
                ["python3", "/home/kent/Assistant/scripts/opencode_manager.py", "status"],
                capture_output=True,
                text=True
            )
            return {
                "running": "active (running)" in result.stdout,
                "status_output": result.stdout.strip()
            }
        except:
            return {"running": False, "status_output": "Status check failed"}
    
    def save_session_finish(self, accomplishments, current_state, next_steps, notes=""):
        """Save session completion data"""
        session_info = self.get_current_session_info()
        session_info.update({
            "end_time": datetime.now().isoformat(),
            "accomplishments": accomplishments,
            "current_state": current_state,
            "next_steps": next_steps,
            "notes": notes,
            "session_type": "finish"
        })
        
        # Save to current session file
        with open(self.current_session_file, 'w') as f:
            json.dump(session_info, f, indent=2)
        
        # Create markdown session file
        self._create_session_markdown(session_info)
        
        return session_info["session_id"]
    
    def load_latest_session(self):
        """Load the most recent session for context restoration"""
        if not self.current_session_file.exists():
            return None
        
        try:
            with open(self.current_session_file, 'r') as f:
                return json.load(f)
        except:
            return None
    
    def _create_session_markdown(self, session_info):
        """Create markdown session file for easy reading"""
        session_id = session_info["session_id"]
        md_file = self.sessions_dir / f"session_{session_id}.md"
        
        content = f"""# Session {session_id}

**Start Time:** {session_info["start_time"]}
**End Time:** {session_info["end_time"]}
**Working Directory:** {session_info["working_directory"]}

## 🎯 Accomplishments
{session_info["accomplishments"]}

## 📊 Current State
{session_info["current_state"]}

## 🚀 Next Steps
{session_info["next_steps"]}

## 📝 Notes
{session_info["notes"]}

---
## Technical Details

### Git Status
```json
{json.dumps(session_info["git_status"], indent=2)}
```

### OpenCode Service Status
```json
{json.dumps(session_info["opencode_service_status"], indent=2)}
```

### Session Metadata
- Session ID: {session_id}
- Session Type: {session_info["session_type"]}
- Working Directory: {session_info["working_directory"]}

---
*Session saved by SessionManager*
"""
        
        with open(md_file, 'w') as f:
            f.write(content)
        
        return md_file
    
    def start_new_session(self):
        """Start a new session and restore context"""
        latest_session = self.load_latest_session()
        
        if latest_session:
            return self._create_session_start_context(latest_session)
        else:
            return "# No previous session found\n\nStarting fresh session."
    
    def _create_session_start_context(self, session_info):
        """Create context for starting new session"""
        content = f"""# Session Context Restored

**Previous Session:** {session_info["session_id"]}
**Previous End Time:** {session_info["end_time"]}

## 🔄 Where We Left Off

### Last Accomplishments
{session_info["accomplishments"]}

### Current State
{session_info["current_state"]}

### Planned Next Steps
{session_info["next_steps"]}

## 🎯 Immediate Priorities for This Session

Based on the previous session, here's what we should focus on:

{session_info["next_steps"]}

## 📋 Technical Context

- **Working Directory:** {session_info["working_directory"]}
- **Git Status:** {"Has uncommitted changes" if session_info["git_status"]["has_changes"] else "Clean"}
- **OpenCode Service:** {"Running" if session_info["opencode_service_status"]["running"] else "Stopped"}

---
*Context restored by SessionManager*
"""
        return content

def main():
    """Command line interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python session_manager.py <command>")
        print("Commands:")
        print("  start                    Load and display previous session context")
        print("  finish                   Interactive session finish")
        print("  quick-finish <args>     Quick finish with command line args")
        sys.exit(1)
    
    manager = SessionManager()
    command = sys.argv[1].lower()
    
    if command == "start":
        context = manager.start_new_session()
        print(context)
        
    elif command == "finish":
        print("Session Finish - Interactive Mode")
        print("Enter details for session completion:")
        
        accomplishments = input("🎯 What did we accomplish? ")
        current_state = input("📊 What's the current state? ")
        next_steps = input("🚀 What are the next steps? ")
        notes = input("📝 Any additional notes? ")
        
        session_id = manager.save_session_finish(
            accomplishments, current_state, next_steps, notes
        )
        
        print(f"\n✅ Session {session_id} saved successfully!")
        print("📁 Session files created in /Assistant/sessions/")
        
    elif command == "quick-finish":
        if len(sys.argv) < 5:
            print("Usage: python session_manager.py quick-finish <accomplishments> <current_state> <next_steps> [notes]")
            sys.exit(1)
        
        accomplishments = sys.argv[2]
        current_state = sys.argv[3]
        next_steps = sys.argv[4]
        notes = sys.argv[5] if len(sys.argv) > 5 else ""
        
        session_id = manager.save_session_finish(
            accomplishments, current_state, next_steps, notes
        )
        
        print(f"✅ Session {session_id} saved!")
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()